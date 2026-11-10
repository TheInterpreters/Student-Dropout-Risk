"""W5.8 tests and CSV-to-W2-response integration, using dummy data only."""
import csv
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "make_assignment_list.py"
_SPEC = importlib.util.spec_from_file_location("make_assignment_list", SCRIPT)
mal = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(mal)
sys.path.insert(0, str(ROOT / "forms"))
import build_spec as builder
import transform_responses as transform

DUMMY_SEED = 12345


class AssignmentListTests(unittest.TestCase):
    def test_counts_and_validation(self):
        rows = mal.build_assignment(DUMMY_SEED)
        mal.validate(rows)
        self.assertEqual(len(rows), 55)
        self.assertEqual(rows[-1]["participant_code"], "PILOT-01")
        self.assertEqual(rows[-1]["variant_id"], "B1")

    def test_reproducible_from_seed(self):
        self.assertEqual(mal.build_assignment(DUMMY_SEED), mal.build_assignment(DUMMY_SEED))
        self.assertNotEqual(mal.build_assignment(DUMMY_SEED), mal.build_assignment(DUMMY_SEED + 1))

    def test_prefix_stays_balanced(self):
        main = [r for r in mal.build_assignment(DUMMY_SEED) if r["role"] == "main"]
        diff = 0
        for row in main:
            diff += 1 if row["group"] == "A" else -1
            self.assertLessEqual(abs(diff), 2)

    def test_one_spare_per_form(self):
        spare = [r for r in mal.build_assignment(DUMMY_SEED) if r["role"] == "spare"]
        self.assertEqual(sorted(r["variant_id"] for r in spare), ["A1", "A2", "B1", "B2"])

    def test_validate_rejects_tampering(self):
        for field, value in (("role", "unknown"), ("variant_id", "A3"), ("group", "wrong"),
                             ("slot", 99), ("participant_code", "")):
            with self.subTest(field=field):
                rows = mal.build_assignment(DUMMY_SEED)
                rows[0][field] = value
                with self.assertRaises(ValueError):
                    mal.validate(rows)
        rows = mal.build_assignment(DUMMY_SEED)
        rows[0]["participant_code"] = rows[1]["participant_code"]
        with self.assertRaises(ValueError):
            mal.validate(rows)
        rows = mal.build_assignment(DUMMY_SEED)
        rows[-1]["variant_id"], rows[-1]["group"] = "A1", "A"
        with self.assertRaises(ValueError):
            mal.validate(rows)

    def test_cli_and_files_written_and_hash_stable(self):
        check = subprocess.run(
            [sys.executable, str(SCRIPT), "--seed", str(DUMMY_SEED), "--check"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stderr)
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            for folder in (d1, d2):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), "--seed", str(DUMMY_SEED), "--out", folder],
                    cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            data = (Path(d1) / "assignment_list.csv").read_bytes()
            self.assertEqual(data, (Path(d2) / "assignment_list.csv").read_bytes())
            rules = (Path(d1) / "assignment_list_RULES.txt").read_text(encoding="utf-8")
            self.assertIn(hashlib.sha256(data).hexdigest(), rules)
            self.assertIn("PILOT-01", rules)

    @unittest.skipUnless(shutil.which("node"), "Node.js needed for the Apps Script mock")
    def test_assignment_csv_to_prefilled_links(self):
        harness = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
let output;
const context = {
  Utilities: {parseCsv: JSON.parse},
  FormApp: {ItemType: {TEXT: 'TEXT'}},
  SpreadsheetApp: {create: () => ({
    getSheets: () => [{getRange: () => ({setValues: rows => { output = rows; }})}],
    getUrl: () => 'mock://links'
  })},
  Logger: {log: () => {}}
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(payload.renderer, 'utf8'), context);
context.readDriveText_ = () => JSON.stringify(payload.csv);
const forms = {};
for (const variant of ['A1', 'A2', 'B1', 'B2']) {
  forms[variant] = {
    getItems: () => [{
      getTitle: () => 'Your participant code',
      asTextItem: () => ({createResponse: code => code})
    }],
    createResponse: () => ({
      withItemResponse: code => ({toPrefilledUrl: () => `mock://${variant}/${code}`})
    })
  };
}
context.writeLinks_(forms, {pack_kind: 'fixture'});
assert.strictEqual(output.length, 56);
assert.strictEqual(output[0][5], 'prefilled_link');
for (let i = 1; i < output.length; i++) {
  assert.strictEqual(output[i][5], `mock://${output[i][2]}/${output[i][1]}`);
}
assert.strictEqual(output[55][5], 'mock://B1/PILOT-01');
"""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "assignment.csv"
            mal.write_csv(mal.build_assignment(DUMMY_SEED), path)
            with path.open(newline="", encoding="utf-8") as f:
                csv_rows = list(csv.reader(f))
        payload = {"renderer": str(ROOT / "forms" / "render_forms.gs"), "csv": csv_rows}
        result = subprocess.run(
            ["node", "-e", harness], input=json.dumps(payload),
            capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_assignment_csv_to_response_csv(self):
        _, _, spec, default_assignment = builder.build_all()
        variants = {v["variant_id"]: v for v in spec["variants"]}
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            self.assertEqual(mal.main(["--seed", str(DUMMY_SEED), "--out", folder]), 0)
            assignment_path = out / "assignment_list.csv"
            with assignment_path.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.assertEqual(reader.fieldnames, list(default_assignment[0]))
                assignment = list(reader)
            exports = {}
            for row in assignment:
                variant = variants[row["variant_id"]]
                code = row["participant_code"]
                values = {
                    "S1.1": "I agree", "S1.2": "Yes", "S2.1": code,
                    "S6.1": "Student", "S6.2": "25",
                }
                answers = []
                for item in transform.answer_items(variant):
                    iid = item["id"]
                    value = values.get(iid, transform.CHART_CHECK.get(iid))
                    if value is None:
                        value = ("Yes" if iid.endswith(".Q1") else
                                 "3" if iid.endswith(".Q2") else "fake " + iid)
                    answers.append(value)
                export = exports.setdefault(variant["variant_id"], [
                    ["Timestamp"] + [i["title"] for i in transform.answer_items(variant)]])
                export.append(["dummy timestamp"] + answers)
            paths = []
            for variant_id, export in exports.items():
                path = out / (variant_id + ".csv")
                with path.open("w", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerows(export)
                paths.append(str(path))
            spec_path = out / "form_spec.json"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            self.assertEqual(transform.main(
                paths + ["--assignment", str(assignment_path), "--spec", str(spec_path),
                         "--label", "dummy", "--out-dir", folder,
                         "--variants", *exports]), 0)
            with (out / "responses_long_dummy.csv").open(newline="", encoding="utf-8") as f:
                long_rows = list(csv.DictReader(f))
            with (out / "responses_participants_dummy.csv").open(newline="", encoding="utf-8") as f:
                people = list(csv.DictReader(f))
            self.assertEqual(len(people), 54)
            self.assertEqual(len(long_rows), 540)
            slots = {r["participant_code"]: r for r in assignment}
            self.assertNotIn("PILOT-01", {p["participant_id"] for p in people})
            for row in long_rows:
                variant = variants[slots[row["participant_id"]]["variant_id"]]
                case_id = variant["scored_order"][int(row["case_order"]) - 1]
                self.assertEqual(row["case_id"], case_id)
                self.assertEqual(row["group"], variant["group"])
                self.assertEqual(row["rationale_freetext"], "fake " + case_id + ".Q3")
                self.assertEqual(row["exclude_reason"], "")


if __name__ == "__main__":
    unittest.main()
