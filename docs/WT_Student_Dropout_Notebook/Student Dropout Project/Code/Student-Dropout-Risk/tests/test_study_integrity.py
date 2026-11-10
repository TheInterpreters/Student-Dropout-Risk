import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
from forms import build_spec as b, case_pack as cp, transform_responses as tr
from scripts.analyze_human_study import main as analyze, score_responses, write_csv, read_csv
from scripts.assign_human_coding import assign_coding, raw_agreement


def dummy_rows(n=50):
    rows = []
    for p in range(n):
        for i in range(1, 11):
            rows.append({
                "participant_id": f"DUMMY-{p:03d}", "case_id": f"C{i:02d}", "case_order": str(i),
                "group": "A" if p % 2 == 0 else "B", "consent": "yes", "complete": "1",
                "exclude_reason": "", "predicted_output": str(int(i <= 5)), "confidence": "4",
                "time_seconds": "1200", "rationale_freetext": "fake rationale",
                "intervention_freetext": "fake intervention", "missing_info_freetext": "fake gap",
            })
    return rows


def dummy_people(n=50):
    return [
        {"participant_id": f"DUMMY-{i:03d}", "group": "A" if i % 2 == 0 else "B",
         "chart_check_b1": "" if i % 2 == 0 else "More worried about this student",
         "chart_check_b2": "" if i % 2 == 0 else "A bigger effect",
         "chart_check_ok": "" if i % 2 == 0 else "1"}
        for i in range(n)
    ]


class StudyIntegrityTests(unittest.TestCase):
    def test_same_group_wrong_variant_is_dropped(self):
        _, _, spec, assignment = b.build_all()
        variant = next(v for v in spec["variants"] if v["variant_id"] == "A2")
        code = next(r["participant_code"] for r in assignment if r["variant_id"] == "A1")
        values = {"S1.1": "I agree", "S1.2": "Yes", "S2.1": code}
        export = [["Timestamp"] + [i["title"] for i in tr.answer_items(variant)],
                  ["fake"] + [values.get(i["id"], "fake") for i in tr.answer_items(variant)]]
        rows, people, report = tr.transform(
            [("export.csv", export)], assignment, spec, source_variants={"export.csv": "A2"})
        self.assertEqual((rows, people, report["wrong_form"]), ([], [], [code]))
        with self.assertRaises(ValueError):
            tr.transform([("export.csv", export)], assignment, spec)

    def test_duration_validation(self):
        for value in ("inf", "nan", "301", "0", "0.001", "bad", "-2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                tr.minutes_to_seconds(value)
        self.assertEqual(tr.minutes_to_seconds("1"), 60)
        self.assertEqual(tr.minutes_to_seconds("300"), 18000)
        self.assertEqual(tr.minutes_to_seconds(""), "")

    def test_provenance_and_profile_parity(self):
        pack, lookup, _, _ = b.build_all()
        self.assertEqual(cp.validate_provenance(pack, lookup), [])
        duplicate = copy.deepcopy(lookup)
        duplicate["C01"]["source_row_id"] = duplicate["PR"]["source_row_id"]
        self.assertTrue(cp.validate_private(duplicate, "fixture"))
        changed = copy.deepcopy(pack)
        changed["cases"][0]["profile"][0]["value"] = "999999"
        self.assertTrue(cp.validate_provenance(changed, lookup))
        relabelled = copy.deepcopy(pack)
        relabelled["pack_kind"] = "study"
        self.assertTrue(cp.validate_provenance(relabelled, lookup))

    def test_study_charts_preflight_before_form_creation(self):
        harness = r"""
const vm = require('vm'), fs = require('fs'), assert = require('assert');
const context = {FormApp: {create: () => { throw Error('FORM CREATED TOO EARLY'); }}};
vm.createContext(context);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), context);
context.readDriveText_ = () => JSON.stringify({pack_kind:'study', variants:[]});
assert.throws(() => context.renderAll(), /requires a chart folder/);
vm.runInContext("CONFIG.CHART_FOLDER_ID = 'mock';", context);
context.readDriveText_ = () => JSON.stringify({pack_kind:'study', variants:[
  {sections:[{items:[{image:'chart_C01.png'}]}]}]});
context.chartBlob_ = () => null;
assert.throws(() => context.renderAll(), /Missing study chart/);
"""
        import shutil
        if not shutil.which("node"):
            self.skipTest("Node required for Apps Script mock")
        result = subprocess.run(
            ["node", "-e", harness, str(ROOT / "forms" / "render_forms.gs")],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_scoring_and_exclusions(self):
        lookup = {cid: {"source_row_id": i, "model_flag": int(1 <= i <= 5)}
                  for i, cid in enumerate(cp.CASE_IDS)}
        rows = dummy_rows()
        for row in rows[:10]:
            row["exclude_reason"] = "withdrawal"
        scored, people, summaries, exclusions = score_responses(rows, lookup, "dummy")
        self.assertEqual((len(scored), len(people), len(exclusions)), (490, 49, 1))
        self.assertTrue(all(p["accuracy"] == 1 for p in people))
        self.assertTrue(all(s["overall_minimum_met"] for s in summaries))
        with self.assertRaises(ValueError):
            score_responses(dummy_rows(1)[:-1], lookup, "dummy")

    def test_forms_close_before_settings_and_rollback_partial_opening(self):
        harness = r"""
const vm = require('vm'), fs = require('fs'), assert = require('assert');
let accepting = true;
const form = {
  setAcceptingResponses(value) { accepting = value; return this; },
  setCollectEmail() { assert.strictEqual(accepting, false); throw Error('setting failed'); }
};
const context = {FormApp: {create: () => form}};
vm.createContext(context);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), context);
assert.throws(() => context.buildForm_({form_title:'dummy'}, {form_label:'Form 1'}), /setting failed/);
assert.strictEqual(accepting, false);
const states = {A1:false, A2:false};
context.readDriveText_ = () => JSON.stringify({pack_kind:'fixture', variants:[
  {variant_id:'A1'}, {variant_id:'A2'}]});
context.buildForm_ = (spec, v) => ({
  setAcceptingResponses(value) {
    states[v.variant_id] = value;
    if (value && v.variant_id === 'A2') throw Error('opening failed');
  }
});
context.writeLinks_ = () => {};
vm.runInContext("CONFIG.ACCEPTING_RESPONSES = true;", context);
assert.throws(() => context.renderAll(), /opening failed/);
assert.deepStrictEqual(states, {A1:false, A2:false});
context.buildForm_ = (spec, v) => ({
  setAcceptingResponses(value) {
    if (value) throw Error('opening failed');
    throw Error('closing failed');
  }
});
assert.throws(() => context.renderAll(), /closing failed/);
"""
        import shutil
        if not shutil.which("node"):
            self.skipTest("Node required for Apps Script mock")
        result = subprocess.run(
            ["node", "-e", harness, str(ROOT / "forms" / "render_forms.gs")],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_analysis_rejects_inconsistent_or_missing_practice_export(self):
        lookup = {cid: {"source_row_id": i, "model_flag": int(1 <= i <= 5)}
                  for i, cid in enumerate(cp.CASE_IDS)}
        for changes in ({"chart_check_b1": "Cannot tell"},
                        {"chart_check_b2": "Cannot tell"},
                        {"chart_check_ok": "0"},
                        {"chart_check_b1": "", "chart_check_ok": "0"},
                        {"chart_check_b2": "", "chart_check_ok": "0"},
                        {"group": "A"}):
            with self.subTest(changes=changes), tempfile.TemporaryDirectory() as folder:
                out = Path(folder)
                write_csv(out / "responses.csv", dummy_rows(2))
                (out / "private.json").write_text(json.dumps(lookup))
                participants = dummy_people(2)
                participants[1].update(changes)
                write_csv(out / "people.csv", participants)
                with self.assertRaises(ValueError):
                    analyze([str(out / "responses.csv"), "--private", str(out / "private.json"),
                             "--participants", str(out / "people.csv"), "--label", "dummy",
                             "--out", str(out / "results")])
                self.assertFalse((out / "results").exists())

    def test_analysis_retains_consistently_wrong_practice_answers(self):
        lookup = {cid: {"source_row_id": i, "model_flag": int(1 <= i <= 5)}
                  for i, cid in enumerate(cp.CASE_IDS)}
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            write_csv(out / "responses.csv", dummy_rows(2))
            (out / "private.json").write_text(json.dumps(lookup))
            participants = dummy_people(2)
            participants[1].update(chart_check_b1="Cannot tell", chart_check_ok="0")
            write_csv(out / "people.csv", participants)
            analyze([str(out / "responses.csv"), "--private", str(out / "private.json"),
                     "--participants", str(out / "people.csv"), "--label", "dummy",
                     "--out", folder])
            self.assertEqual(len(read_csv(out / "participants_dummy.csv")), 2)
            checks = read_csv(out / "chart_checks_dummy.csv")
            self.assertEqual([r["n_correct"] for r in checks], ["0", "1", "0"])
            self.assertTrue(all(r["n_participants"] == "1" for r in checks))

    def test_coding_and_agreement(self):
        rows = dummy_rows()
        members = ["M1", "M2", "M3", "M4", "M5"]
        recruiters = {f"DUMMY-{i:03d}": members[i % 5] for i in range(50)}
        assignments, tasks = assign_coding(rows, recruiters, members)
        self.assertEqual(sum(bool(a["secondary_coder"]) for a in assignments), 10)
        self.assertEqual((assignments, tasks), assign_coding(rows, recruiters, members))
        for a in assignments:
            self.assertNotEqual(a["primary_coder"], recruiters[a["participant_id"]])
            self.assertNotEqual(a["secondary_coder"], recruiters[a["participant_id"]])
            self.assertNotEqual(a["primary_coder"], a["secondary_coder"])
        self.assertTrue(all("group" not in t and "recruiter" not in t for t in tasks))
        for t in tasks:
            t["code"] = "comprehension"
        agreement = raw_agreement(assignments, tasks)
        self.assertEqual([r["raw_agreement"] for r in agreement], [1, 1, 1])
        self.assertEqual([r["n_items"] for r in agreement], [100, 100, 100])
        doubled = next(a["participant_id"] for a in assignments if a["secondary_coder"])
        missing = [t for t in tasks if not (t["participant_id"] == doubled and t["case_id"] == "C01")]
        with self.assertRaises(ValueError):
            raw_agreement(assignments, missing)

    def test_analysis_and_coding_cli_end_to_end(self):
        lookup = {cid: {"source_row_id": i, "model_flag": int(1 <= i <= 5)}
                  for i, cid in enumerate(cp.CASE_IDS)}
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            write_csv(out / "responses.csv", dummy_rows())
            (out / "private.json").write_text(json.dumps(lookup), encoding="utf-8")
            write_csv(out / "people.csv", dummy_people())
            write_csv(out / "log.csv", [
                {"participant_code": f"DUMMY-{i:03d}", "recruiter": f"M{i % 5 + 1}"} for i in range(50)])
            commands = [
                ["scripts/analyze_human_study.py", str(out / "responses.csv"),
                 "--private", str(out / "private.json"), "--participants", str(out / "people.csv"),
                 "--label", "dummy", "--out", folder],
                ["scripts/assign_human_coding.py", "assign", str(out / "responses.csv"),
                 "--send-log", str(out / "log.csv"), "--members", "M1", "M2", "M3", "M4", "M5",
                 "--label", "dummy", "--out", folder],
            ]
            for command in commands:
                result = subprocess.run([sys.executable, *command], cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(read_csv(out / "participants_dummy.csv")), 50)
            self.assertTrue(all(r["mean_accuracy"] == "1.0" for r in read_csv(out / "group_summary_dummy.csv")))
            tasks = [r for p in out.glob("coder_*_dummy.csv") for r in read_csv(p)]
            for row in tasks:
                row["code"] = "comprehension"
            write_csv(out / "completed.csv", tasks)
            result = subprocess.run([
                sys.executable, "scripts/assign_human_coding.py", "agreement",
                "--assignments", str(out / "assignments_dummy.csv"), "--coded", str(out / "completed.csv"),
                "--label", "dummy", "--out", folder], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(all(r["raw_agreement"] == "1.0" for r in read_csv(out / "agreement_dummy.csv")))


if __name__ == "__main__":
    unittest.main()
