import unittest

import numpy as np

from src.auditing import (
    correlation_ratio,
    cramers_v,
    paired_bootstrap_model_differences,
    proxy_association_table,
    subgroup_diagnostics,
)
from src.modeling import capacity_predictions, capacity_threshold, evaluate_predictions


class AuditingTests(unittest.TestCase):
    def test_capacity_threshold_never_exceeds_capacity_with_ties(self):
        probabilities = np.array([0.9, 0.8, 0.8, 0.8, 0.1])
        threshold = capacity_threshold(probabilities, capacity=0.4)
        self.assertLessEqual(np.mean(probabilities >= threshold), 0.4)

    def test_capacity_policy_uses_stable_tie_breaking(self):
        probabilities = np.array([0.9, 0.8, 0.8, 0.8, 0.1])
        predictions, boundary = capacity_predictions(probabilities, capacity=0.4)
        self.assertEqual(predictions.tolist(), [1, 1, 0, 0, 0])
        self.assertEqual(boundary, 0.8)

    def test_evaluation_includes_decision_and_calibration_metrics(self):
        truth = np.array([0, 0, 1, 1])
        probability = np.array([0.1, 0.4, 0.6, 0.9])
        metrics = evaluate_predictions(truth, probability >= 0.5, probability)
        for name in (
            "dropout_precision",
            "flag_rate",
            "brier_score",
            "expected_calibration_error_10bin",
        ):
            self.assertIn(name, metrics)

    def test_association_and_subgroup_metrics(self):
        category = ["a", "a", "b", "b"] * 20
        paired = ["x", "x", "y", "y"] * 20
        values = [0.0, 0.1, 0.9, 1.0] * 20
        self.assertGreater(cramers_v(category, paired), 0.9)
        self.assertGreater(correlation_ratio(category, values), 0.8)
        truth = np.array([0, 1, 0, 1] * 20)
        scores = np.array([0.1, 0.9, 0.2, 0.8] * 20)
        predictions = (scores >= 0.5).astype(int)
        report = subgroup_diagnostics(
            truth, scores, category, predictions, min_group_size=10
        )
        self.assertEqual(set(report["group"]), {"a", "b"})
        self.assertIn("true_positive_rate", report.columns)

    def test_small_groups_are_reported_as_suppressed(self):
        report = subgroup_diagnostics(
            [0, 1, 0], [0.1, 0.9, 0.2], ["large", "rare", "large"], [0, 1, 0], min_group_size=2
        )
        rare = report.loc[report["group"].eq("rare")].iloc[0]
        self.assertFalse(bool(rare["eligible"]))
        self.assertEqual(rare["suppression_reason"], "n < 2")
        self.assertTrue(np.isnan(rare["flag_rate"]))

    def test_proxy_table_uses_metric_by_feature_type(self):
        import pandas as pd

        frame = pd.DataFrame({"coded": [0, 0, 1, 1], "numeric": [0.0, 0.1, 0.9, 1.0]})
        table = proxy_association_table(
            frame,
            {"protected": ["a", "a", "b", "b"]},
            ["coded", "numeric"],
            ["coded"],
        )
        self.assertEqual(set(table["metric"]), {"cramers_v", "correlation_ratio_eta"})

    def test_paired_bootstrap_reports_same_case_differences(self):
        truth = np.array([0, 0, 0, 1, 1, 1] * 10)
        left = np.where(truth == 1, 0.9, 0.1)
        right = np.where(truth == 1, 0.7, 0.3)
        result = paired_bootstrap_model_differences(
            truth, left, right, resamples=100, capacity=0.5
        )
        self.assertEqual(
            set(result["metric"]),
            {"roc_auc", "brier_score", "capacity_recall", "capacity_precision"},
        )
        brier_difference = result.loc[
            result["metric"].eq("brier_score"), "point_difference"
        ].iloc[0]
        self.assertLess(brier_difference, 0)


if __name__ == "__main__":
    unittest.main()
