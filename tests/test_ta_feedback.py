import unittest

import numpy as np

from scripts import run_ta_feedback_checks as ta


class TaFeedbackHelperTests(unittest.TestCase):
    def test_rule_metrics(self):
        result = ta.rule_metrics([1, 1, 0, 0], [1, 0, 1, 0])
        self.assertEqual(result["n_selected"], 2)
        self.assertAlmostEqual(result["precision"], 0.5)
        self.assertAlmostEqual(result["recall"], 0.5)

    def test_top_k_hits_breaks_ties_by_position(self):
        self.assertEqual(ta.top_k_hits(np.array([0.9, 0.5, 0.5, 0.1]), np.array([1, 0, 1, 0]), 2), 1)
        self.assertEqual(ta.top_k_hits(np.array([0.9, 0.5, 0.5, 0.1]), np.array([1, 1, 0, 0]), 2), 2)

    def test_eligibility_subset_reranks_without_no_evaluation_students(self):
        import pandas as pd
        probability = np.array([0.99, 0.95, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05])
        y = np.array([1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0], bool)
        no_eval = np.array([1, 1] + [0] * 10, bool)  # the two highest scorers sat no evaluations
        result = ta.eligibility_subset(pd.DataFrame({"probability": probability}), y, no_eval)
        self.assertEqual((result["n"], result["flagged"]), (10, 2))
        self.assertEqual((result["tp"], result["fp"]), (2, 0))
        self.assertEqual(result["excluded_no_evaluation_dropout"], 2)
        self.assertAlmostEqual(result["recall"], round(2 / 3, 4))

    def test_saved_cases_cover_validation(self):
        table = ta.load_case_table()
        self.assertEqual(len(table), 544)
        self.assertEqual(int(table["flagged"].sum()), 108)


if __name__ == "__main__":
    unittest.main()
