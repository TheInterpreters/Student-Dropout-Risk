import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.analyze_human_study import read_csv, write_csv
from scripts.assign_human_coding import (
    ALLOWED_CODES, assign_coding, intervention_flag_summary, reconcile, theme_by_group,
)

ROOT = Path(__file__).resolve().parents[1]
MEMBERS = ["M1", "M2", "M3", "M4", "M5"]


def responses(n=50):
    rows = []
    for p in range(n):
        for c in range(1, 11):
            rows.append({"participant_id": f"D-{p:03d}", "consent": "yes", "group": "A" if p < n // 2 else "B",
                         "case_id": f"C{c:02d}", "complete": "1", "exclude_reason": "",
                         "rationale_freetext": "r", "intervention_freetext": "i",
                         "missing_info_freetext": "m"})
    return rows


def coded_tasks(rows):
    recruiters = {f"D-{p:03d}": MEMBERS[p % 5] for p in range(50)}
    assignments, tasks = assign_coding(rows, recruiters, MEMBERS)
    for task in tasks:
        task["code"] = sorted(ALLOWED_CODES[task["field"]])[0]
    return assignments, tasks


class ReconcileTests(unittest.TestCase):
    def test_agreement_only_reconciles_every_item_once(self):
        assignments, tasks = coded_tasks(responses())
        reconciled, open_items = reconcile(assignments, tasks)
        self.assertEqual(open_items, [])
        self.assertEqual(len(reconciled), 50 * 10 * 3)
        self.assertEqual(sum(r["source"] == "agreed" for r in reconciled), 10 * 10 * 3)
        keys = {(r["participant_id"], r["case_id"], r["field"]) for r in reconciled}
        self.assertEqual(len(keys), len(reconciled))

    def test_disagreement_needs_decision_then_uses_it(self):
        assignments, tasks = coded_tasks(responses())
        doubled = next(a for a in assignments if a["secondary_coder"])
        target = next(t for t in tasks if t["participant_id"] == doubled["participant_id"]
                      and t["coder"] == doubled["secondary_coder"] and t["field"] == "rationale_freetext")
        target["code"] = "explanation_chart"
        reconciled, open_items = reconcile(assignments, tasks)
        self.assertEqual(len(open_items), 1)
        decision = dict(open_items[0], resolved_code="explanation_chart")
        reconciled, open_items = reconcile(assignments, tasks, [decision])
        self.assertEqual(open_items, [])
        chosen = [r for r in reconciled if r["source"] == "adjudicated"]
        self.assertEqual([r["code"] for r in chosen], ["explanation_chart"])

    def test_rejects_missing_invalid_and_stale_inputs(self):
        assignments, tasks = coded_tasks(responses())
        with self.assertRaises(ValueError):
            reconcile(assignments, tasks[1:])
        bad = [dict(t) for t in tasks]
        bad[0]["code"] = "not_a_code"
        with self.assertRaises(ValueError):
            reconcile(assignments, bad)
        stale = {"participant_id": tasks[0]["participant_id"], "case_id": tasks[0]["case_id"],
                 "field": tasks[0]["field"], "resolved_code": tasks[0]["code"]}
        with self.assertRaises(ValueError):
            reconcile(assignments, tasks, [stale])

    def test_theme_by_group_splits_groups_and_flags(self):
        rows = responses()
        assignments, tasks = coded_tasks(rows)
        reconciled, _ = reconcile(assignments, tasks)
        lookup = {f"C{i:02d}": {"source_row_id": i, "model_flag": int(i <= 5)} for i in range(1, 11)}
        table = theme_by_group(reconciled, rows, lookup)
        totals = {(r["field"], r["group"], r["model_flag"]): r["n_field_items"] for r in table}
        self.assertEqual(totals[("rationale_freetext", "A", "all")], 250)
        self.assertEqual(totals[("rationale_freetext", "B", "1")], 125)
        for key in {(r["field"], r["group"], r["model_flag"]) for r in table}:
            shares = sum(r["share_within_stratum"] for r in table
                         if (r["field"], r["group"], r["model_flag"]) == key)
            self.assertAlmostEqual(shares, 1.0)

    def test_cli_disagreement_loop(self):
        rows = responses()
        assignments, tasks = coded_tasks(rows)
        doubled = next(a for a in assignments if a["secondary_coder"])
        for t in tasks:
            if (t["participant_id"] == doubled["participant_id"] and t["coder"] == doubled["secondary_coder"]
                    and t["case_id"] == "C01" and t["field"] == "intervention_freetext"):
                t["code"] = "unclear_other"
        lookup = {f"C{i:02d}": {"source_row_id": i, "model_flag": int(i <= 5)} for i in range(1, 11)}
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            write_csv(out / "assignments.csv", assignments)
            write_csv(out / "completed.csv", tasks)
            write_csv(out / "responses.csv", rows)
            (out / "lookup.json").write_text(json.dumps(lookup), encoding="utf-8")
            base = [sys.executable, "scripts/assign_human_coding.py"]
            first = subprocess.run(base + ["reconcile", "--assignments", str(out / "assignments.csv"),
                                           "--coded", str(out / "completed.csv"), "--label", "dummy",
                                           "--out", folder], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(first.returncode, 2, first.stderr)
            self.assertFalse((out / "reconciled_dummy.csv").exists())
            sheet = read_csv(out / "disagreements_dummy.csv")
            self.assertEqual(len(sheet), 1)
            sheet[0]["resolved_code"] = "unclear_other"
            write_csv(out / "decisions.csv", sheet)
            second = subprocess.run(base + ["reconcile", "--assignments", str(out / "assignments.csv"),
                                            "--coded", str(out / "completed.csv"),
                                            "--decisions", str(out / "decisions.csv"),
                                            "--label", "dummy", "--out", folder],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            third = subprocess.run(base + ["summary", "--coded", str(out / "reconciled_dummy.csv"),
                                           "--responses", str(out / "responses.csv"),
                                           "--private", str(out / "lookup.json"),
                                           "--label", "dummy", "--out", folder],
                                   cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(third.returncode, 0, third.stderr)
            by_group = read_csv(out / "theme_by_group_dummy.csv")
            self.assertTrue(by_group)
            self.assertNotIn("participant_id", by_group[0])
            self.assertNotIn("text", by_group[0])


class InterventionFlagTests(unittest.TestCase):
    def rating(self, pid, case, concrete="1", actor="student"):
        return {"participant_id": pid, "case_id": case, "concrete_next_step": concrete,
                "feasible_before_second_semester": "1", "responsible_actor": actor,
                "unsupported_causal_assumption": "0"}

    def test_shares_by_group_and_model_flag(self):
        rows = responses(2)
        flags = [self.rating("D-000", "C01", "1"), self.rating("D-000", "C02", "0", "none"),
                 self.rating("D-001", "C01", "1", "both")]
        lookup = {"C01": {"model_flag": 1}, "C02": {"model_flag": 0}}
        result = {(r["group"], r["model_flag"]): r for r in intervention_flag_summary(flags, rows, lookup)}
        self.assertEqual(result[("A", "all")]["share_concrete_next_step"], 0.5)
        self.assertEqual(result[("all", "all")]["n_items"], 3)
        self.assertEqual(result[("A", "1")]["share_actor_student"], 1.0)
        self.assertEqual(result[("B", "all")]["share_actor_both"], 1.0)
        self.assertNotIn("participant_id", result[("A", "all")])

    def test_rejects_invalid_and_duplicate_ratings(self):
        rows = responses(2)
        with self.assertRaises(ValueError):
            intervention_flag_summary([self.rating("D-000", "C01", "2")], rows)
        with self.assertRaises(ValueError):
            intervention_flag_summary([self.rating("D-000", "C01")] * 2, rows)


if __name__ == "__main__":
    unittest.main()
