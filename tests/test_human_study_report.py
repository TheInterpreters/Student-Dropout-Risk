import unittest
import tempfile
from pathlib import Path

import pandas as pd

from scripts.build_human_study_report import build_tables
from scripts.audit_human_study_privacy import audit


class HumanStudyReportTests(unittest.TestCase):
    def test_privacy_audit_reports_counts_without_text(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "responses.csv"
            pd.DataFrame([{
                "participant_id": "P-0001", "rationale_freetext": "Because of the grades",
                "intervention_freetext": "Offer tutoring", "missing_info_freetext": "Attendance",
            }]).to_csv(path, index=False)
            result = audit(path)
            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["pattern_match_rows"], {
                "email": 0, "url": 0, "phone_like": 0, "self_identification_phrase": 0})
            self.assertNotIn("Because", str(result))

    def test_report_tables_use_participants_as_primary_unit(self):
        people, participants, scored = [], [], []
        lookup = {f"C{i:02d}": {"model_flag": int(i > 5)} for i in range(1, 11)}
        for index in range(50):
            group = "A" if index < 25 else "B"
            pid = f"P-{index:04d}"
            people.append({"participant_id": pid, "group": group, "accuracy": 0.8 if group == "A" else 0.9,
                           "mean_confidence": 4.0, "self_reported_minutes": 30})
            participants.append({
                "participant_id": pid, "variant_id": group + ("1" if index % 2 else "2"),
                "role": "Student", "chart_check_b1": "" if group == "A" else "More worried about this student",
                "chart_check_b2": "" if group == "A" else "A bigger effect",
                "chart_check_ok": "" if group == "A" else "1",
            })
            for case in range(1, 11):
                scored.append({"participant_id": pid, "group": group, "case_id": f"C{case:02d}",
                               "correct": int(case <= (8 if group == "A" else 9)), "confidence": 4})
        tables, merged_people, merged_scored = build_tables(
            pd.DataFrame(scored), pd.DataFrame(people), pd.DataFrame(participants), lookup,
            seed=42, resamples=100)
        comparison = tables["group_comparisons"].query("metric == 'accuracy'").iloc[0]
        self.assertAlmostEqual(comparison["difference"], 0.1)
        self.assertEqual(len(merged_people), 50)
        self.assertEqual(len(merged_scored), 500)
        self.assertEqual(len(tables["case_summary"]), 20)
        self.assertEqual(tables["practice_checks"]["n_correct"].tolist(), [25, 25, 25])


if __name__ == "__main__":
    unittest.main()
