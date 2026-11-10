"""Regression checks for scope exclusion and actual-outcome comparisons.

Invented fixtures here are software tests, never empirical audit results.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import actual_data_audit as actual
from development_population import validate_population


class ActualDataAuditTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame({
            "source_row_id": np.arange(544),
            "target": np.tile([0, 1], 272),
            "curricular_units_1st_sem_enrolled": 6,
            "curricular_units_1st_sem_approved": 4,
            "curricular_units_1st_sem_grade": 12.,
        })
        self.columns = self.frame.columns[2:].tolist()

    def test_training_and_test_cannot_be_counted_as_audit_cases(self):
        for name in ("train", "test"):
            with self.assertRaises(ValueError):
                actual.require_validation_only({"validation": self.frame, name: self.frame})

    def test_sampling_cannot_be_reported_as_all_observations(self):
        with self.assertRaises(ValueError):
            actual.require_validation_only({"validation": self.frame.head(20)})

    def test_actual_data_flags_are_reported_without_modifying_rows(self):
        self.frame.loc[0, "curricular_units_1st_sem_approved"] = 9
        before = self.frame.copy(deep=True)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "eda_uci_data/data").mkdir(parents=True)
            (root / "eda_uci_data/data/dropout_data.csv").write_text("fixture")
            (root / "artifacts").mkdir()
            (root / "artifacts/split_ids.csv").write_text("fixture")
            out = root / "outputs"
            result = actual.data_audit({"validation": self.frame}, self.columns, out, root=root)
            self.assertEqual(result["n_rows"], 544)
            self.assertEqual(result["partitions"]["validation"]["approved_exceeds_enrolled"], 1)
            self.assertEqual(len(pd.read_csv(out / "row_checks_validation.csv")), 544)
        pd.testing.assert_frame_equal(self.frame, before)

    @unittest.skipUnless((SCRIPTS.parents[1] / "src/modeling.py").is_file(), "Original project required for metric integration")
    def test_actual_vs_model_uses_all_rows_and_capacity_policy(self):
        sys.path.insert(0, str(SCRIPTS.parents[1]))
        # Even with perfectly separated scores, only 108/544 are flagged.
        p = np.where(self.frame.target.to_numpy() == 1, .9, .1)
        with tempfile.TemporaryDirectory() as tmp:
            result = actual.compare_actual_outcomes({"validation": self.frame}, {"validation": p}, tmp)
            rows = pd.read_csv(Path(tmp) / "actual_vs_model_validation.csv")
            self.assertEqual(len(rows), 544)
            self.assertEqual(int(rows.predicted_outreach_flag.sum()), 108)
            metrics = result["partitions"]["validation"]
            self.assertEqual(metrics["roc_auc"], 1.)
            self.assertEqual(metrics["confusion_matrix"], [[272, 0], [164, 108]])
            self.assertAlmostEqual(metrics["brier_score"], .01)
            self.assertEqual(metrics["evidence_type"], "held_out_validation")
            self.assertFalse(result["test_evaluated"])

    def test_population_requires_exact_saved_ids_not_just_counts(self):
        train = pd.DataFrame({"source_row_id": np.arange(2541), "target": 0, "grade": 12.})
        validation = pd.DataFrame({"source_row_id": np.arange(2541, 3085), "target": 1, "grade": 12.})
        splits = pd.DataFrame({"source_row_id": np.arange(3630),
                               "split": ["train"] * 2541 + ["validation"] * 544 + ["test"] * 545})
        self.assertEqual(len(validate_population(train, validation, ["grade"], splits)["validation"]), 544)
        # A single test ID must fail even though the row count is still 544.
        validation.loc[0, "source_row_id"] = 3085
        with self.assertRaises(ValueError):
            validate_population(train, validation, ["grade"], splits)


if __name__ == "__main__":
    unittest.main()
