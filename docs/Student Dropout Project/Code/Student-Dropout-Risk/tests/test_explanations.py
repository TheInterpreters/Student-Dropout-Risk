import unittest

import numpy as np
import pandas as pd

from src.explanations import (
    accumulated_local_effect,
    aggregate_shap_by_group,
    constrained_binary_counterfactuals,
    deletion_curve,
    grouped_permutation_importance,
    prediction_preserving_perturbations,
    recompute_first_semester_features,
    semantic_feature_groups,
    select_risk_stratified_positions,
    select_forward_simulation_positions,
    top_k_overlap,
    training_reference_values,
)


def toy_predict_proba(frame: pd.DataFrame) -> np.ndarray:
    probability = np.clip(
        0.15 + 0.45 * frame["debtor"].astype(float) + 0.25 * frame["grade"].astype(float),
        0,
        1,
    ).to_numpy()
    return np.column_stack([1 - probability, probability])


class ExplanationTests(unittest.TestCase):
    def setUp(self):
        self.train = pd.DataFrame(
            {"debtor": [0, 0, 0, 1], "grade": [0.0, 0.2, 0.4, 1.0]}
        )
        self.case = pd.Series({"debtor": 1.0, "grade": 1.0})

    def test_training_references_use_mode_and_median(self):
        references = training_reference_values(self.train, ["debtor", "grade"])
        self.assertEqual(references["debtor"], 0)
        self.assertAlmostEqual(references["grade"], 0.3)

    def test_ranked_deletion_is_stronger_than_random_for_top_feature(self):
        references = training_reference_values(self.train, ["debtor", "grade"])
        curve = deletion_curve(
            toy_predict_proba,
            self.case,
            ["debtor", "grade"],
            references,
            random_repetitions=100,
        )
        self.assertLess(
            curve.loc[1, "ranked_dropout_probability"],
            curve.loc[1, "random_dropout_probability_mean"],
        )
        self.assertGreater(curve.attrs["area_between_curves"], 0)

    def test_deletion_score_is_sign_aware_for_protective_feature(self):
        def protective_predict(frame):
            probability = 0.9 - 0.5 * frame["protective"] - 0.2 * frame["other"]
            probability = probability.to_numpy(dtype=float)
            return np.column_stack([1 - probability, probability])

        case = pd.Series({"protective": 1.0, "other": 1.0})
        references = pd.Series({"protective": 0.0, "other": 0.0})
        curve = deletion_curve(
            protective_predict,
            case,
            ["protective", "other"],
            references,
            random_repetitions=200,
        )
        self.assertGreater(curve.attrs["area_between_curves"], 0)
        self.assertGreater(curve.loc[1, "ranked_dropout_probability"], curve.loc[0, "ranked_dropout_probability"])

    def test_semantic_groups_do_not_duplicate_derived_features(self):
        columns = [
            "curricular_units_1st_sem_enrolled",
            "curricular_units_1st_sem_approved",
            "curricular_units_1st_sem_evaluations",
            "first_semester_pass_rate",
            "first_semester_no_enrollment",
            "first_semester_no_evaluations",
            "debtor",
        ]
        groups = semantic_feature_groups(columns)
        members = [feature for group in groups.values() for feature in group]
        self.assertCountEqual(members, columns)
        self.assertEqual(len(members), len(set(members)))

    def test_grouped_shap_sums_signed_members_before_ranking(self):
        grouped = aggregate_shap_by_group(
            [0.6, -0.4, 0.1],
            ["raw", "derived", "other"],
            {"semantic": ("raw", "derived"), "other": ("other",)},
        )
        self.assertEqual(grouped.iloc[0]["feature_group"], "semantic")
        self.assertAlmostEqual(grouped.iloc[0]["signed_shap"], 0.2)

    def test_recompute_restores_pass_rate_and_indicators(self):
        frame = pd.DataFrame(
            {
                "curricular_units_1st_sem_enrolled": [4, 0],
                "curricular_units_1st_sem_approved": [2, 0],
                "curricular_units_1st_sem_evaluations": [3, 0],
                "first_semester_pass_rate": [99.0, 99.0],
            }
        )
        result = recompute_first_semester_features(frame)
        self.assertEqual(result["first_semester_pass_rate"].tolist(), [0.5, 0.0])
        self.assertEqual(result["first_semester_no_enrollment"].tolist(), [0, 1])
        self.assertEqual(result["first_semester_no_evaluations"].tolist(), [0, 1])

    def test_grouped_pfi_and_ale_detect_numeric_signal(self):
        frame = pd.DataFrame({"signal": np.linspace(0, 1, 60), "noise": np.tile([0, 1], 30)})
        target = (frame["signal"] > 0.5).astype(int)

        def predictor(values):
            probability = 0.05 + 0.9 * values["signal"].astype(float).to_numpy()
            return np.column_stack([1 - probability, probability])

        importance = grouped_permutation_importance(
            predictor,
            frame,
            target,
            {"signal": ("signal",), "noise": ("noise",)},
            repeats=10,
        )
        self.assertEqual(importance.iloc[0]["feature_group"], "signal")
        ale = accumulated_local_effect(predictor, frame, "signal", bins=5)
        self.assertGreater(ale.iloc[-1]["ale"], ale.iloc[0]["ale"])

    def test_top_k_overlap_uses_fixed_k_denominator(self):
        value = top_k_overlap([["a", "b", "c"], ["a", "b", "d"]], k=3)
        self.assertAlmostEqual(value, 2 / 3)

    def test_top_k_overlap_rejects_short_rankings(self):
        with self.assertRaises(ValueError):
            top_k_overlap([["a", "b"], ["a", "b", "c"]], k=3)

    def test_risk_stratified_selection_is_deterministic_and_label_free(self):
        selected = select_risk_stratified_positions(np.arange(100), n_cases=20, n_strata=5)
        self.assertEqual(len(selected), 20)
        self.assertEqual(len(set(selected)), 20)
        self.assertEqual([sum((selected >= low) & (selected < low + 20)) for low in range(0, 100, 20)], [4] * 5)

    def test_forward_simulation_panel_balances_model_outputs(self):
        probability = np.linspace(0, 1, 100)
        selected = select_forward_simulation_positions(probability)
        from src.modeling import capacity_predictions

        labels, _ = capacity_predictions(probability)
        self.assertEqual(int(labels[selected].sum()), 5)
        self.assertEqual(int((labels[selected] == 0).sum()), 5)

    def test_perturbations_use_training_scale_and_probability_filter(self):
        result = prediction_preserving_perturbations(
            toy_predict_proba,
            self.case,
            self.train,
            ["grade"],
            fraction_of_training_sd=0.01,
            probability_tolerance=0.01,
        )
        self.assertEqual(result.loc[0, "feature"], "grade")
        self.assertTrue(bool(result.loc[0, "accepted"]))

    def test_counterfactual_changes_only_allowed_feature(self):
        result = constrained_binary_counterfactuals(
            toy_predict_proba,
            self.case,
            cohort_probabilities=[0.85, 0.80, 0.70, 0.20, 0.10],
            case_position=0,
            allowed_resolutions={"debtor": 0},
            capacity=0.4,
        )
        self.assertEqual(result.loc[0, "changed_features"], "debtor")
        self.assertEqual(result.loc[0, "n_changes"], 1)
        self.assertFalse(bool(result.loc[0, "flagged_after_change"]))


if __name__ == "__main__":
    unittest.main()
