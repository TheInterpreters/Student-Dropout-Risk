"""Fairness, suppression, and proxy diagnostics for the frozen capacity policy."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from sklearn.metrics import brier_score_loss, precision_score, recall_score, roc_auc_score

from src.modeling import capacity_predictions


def cramers_v(left: Sequence[object], right: Sequence[object]) -> float:
    """Bias-corrected Cramer's V for two categorical variables."""
    table = pd.crosstab(pd.Series(left, name="left"), pd.Series(right, name="right"))
    if table.empty or min(table.shape) < 2:
        return 0.0
    chi2 = chi2_contingency(table, correction=False)[0]
    n = table.to_numpy().sum()
    phi2 = chi2 / n
    rows, columns = table.shape
    corrected = max(0.0, phi2 - ((columns - 1) * (rows - 1)) / (n - 1))
    corrected_rows = rows - ((rows - 1) ** 2) / (n - 1)
    corrected_columns = columns - ((columns - 1) ** 2) / (n - 1)
    denominator = min(corrected_columns - 1, corrected_rows - 1)
    return float(np.sqrt(corrected / denominator)) if denominator > 0 else 0.0


def correlation_ratio(categories: Sequence[object], values: Sequence[float]) -> float:
    """Return eta for a categorical protected attribute and continuous feature."""
    groups = pd.Series(categories, dtype="category")
    numeric = np.asarray(values, dtype=float)
    grand_mean = float(np.mean(numeric))
    denominator = float(np.sum((numeric - grand_mean) ** 2))
    if denominator == 0:
        return 0.0
    numerator = 0.0
    for level in groups.cat.categories:
        group_values = numeric[(groups == level).to_numpy()]
        if len(group_values):
            numerator += len(group_values) * (float(np.mean(group_values)) - grand_mean) ** 2
    return float(np.sqrt(numerator / denominator))


def subgroup_diagnostics(
    y_true: Sequence[int],
    probabilities: Sequence[float],
    groups: Sequence[object],
    predictions: Sequence[int],
    min_group_size: int = 30,
) -> pd.DataFrame:
    """Report metrics for eligible groups and explicit rows for suppressed groups."""
    truth = np.asarray(y_true, dtype=int)
    scores = np.asarray(probabilities, dtype=float)
    predicted = np.asarray(predictions, dtype=int)
    if not (truth.shape == scores.shape == predicted.shape):
        raise ValueError("truth, probabilities, and predictions must align")
    labels = pd.Series(groups).astype(str).to_numpy()
    rows: list[dict[str, object]] = []
    for level in sorted(np.unique(labels)):
        mask = labels == level
        n = int(mask.sum())
        eligible = n >= min_group_size
        subgroup_truth = truth[mask]
        subgroup_predictions = predicted[mask]
        negatives = subgroup_truth == 0
        false_positive_rate = (
            float(np.mean(subgroup_predictions[negatives] == 1)) if negatives.any() else np.nan
        )
        rows.append(
            {
                "group": level,
                "n": n,
                "eligible": eligible,
                "suppression_reason": "" if eligible else f"n < {min_group_size}",
                "outcome_rate": float(np.mean(subgroup_truth)),
                "flag_rate": float(np.mean(subgroup_predictions)) if eligible else np.nan,
                "true_positive_rate": recall_score(
                    subgroup_truth, subgroup_predictions, pos_label=1, zero_division=0
                ) if eligible else np.nan,
                "false_positive_rate": false_positive_rate if eligible else np.nan,
                "precision": precision_score(
                    subgroup_truth, subgroup_predictions, pos_label=1, zero_division=0
                ) if eligible else np.nan,
                "mean_predicted_risk": float(np.mean(scores[mask])) if eligible else np.nan,
                "calibration_gap": float(
                    np.mean(scores[mask]) - np.mean(subgroup_truth)
                ) if eligible else np.nan,
            }
        )
    return pd.DataFrame(rows)


def proxy_association_table(
    frame: pd.DataFrame,
    protected_attributes: dict[str, Sequence[object]],
    features: Sequence[str],
    categorical_features: Sequence[str],
) -> pd.DataFrame:
    """Measure every candidate feature's association with protected attributes."""
    categorical = set(categorical_features)
    rows: list[dict[str, object]] = []
    for attribute, protected_values in protected_attributes.items():
        protected_series = pd.Series(protected_values).reset_index(drop=True)
        counts = protected_series.astype(str).value_counts()
        for feature in features:
            if feature not in frame or feature == attribute:
                continue
            values = frame[feature].reset_index(drop=True)
            if feature in categorical:
                metric = "cramers_v"
                association = cramers_v(protected_series, values)
            else:
                metric = "correlation_ratio_eta"
                association = correlation_ratio(protected_series, values)
            rows.append(
                {
                    "protected_attribute": attribute,
                    "feature": feature,
                    "feature_type": "categorical" if feature in categorical else "continuous",
                    "metric": metric,
                    "association": association,
                    "n": len(frame),
                    "protected_levels": int(len(counts)),
                    "smallest_protected_group_n": int(counts.min()),
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["protected_attribute", "association"],
        ascending=[True, False],
        ignore_index=True,
    )


def paired_bootstrap_model_differences(
    y_true: Sequence[int],
    left_probabilities: Sequence[float],
    right_probabilities: Sequence[float],
    resamples: int = 2000,
    seed: int = 42,
    capacity: float = 0.20,
) -> pd.DataFrame:
    """Return paired percentile intervals for final same-case model differences."""
    truth = np.asarray(y_true, dtype=int)
    left = np.asarray(left_probabilities, dtype=float)
    right = np.asarray(right_probabilities, dtype=float)
    if not (truth.shape == left.shape == right.shape) or truth.ndim != 1:
        raise ValueError("truth and both probability vectors must be aligned")
    if resamples < 2:
        raise ValueError("resamples must be at least two")

    def metrics(labels: np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
        predictions, _ = capacity_predictions(probabilities, capacity=capacity)
        return {
            "roc_auc": roc_auc_score(labels, probabilities),
            "brier_score": brier_score_loss(labels, probabilities),
            "capacity_recall": recall_score(labels, predictions, zero_division=0),
            "capacity_precision": precision_score(labels, predictions, zero_division=0),
        }

    point_left = metrics(truth, left)
    point_right = metrics(truth, right)
    draws: dict[str, list[float]] = {name: [] for name in point_left}
    rng = np.random.default_rng(seed)
    for _ in range(resamples):
        indices = rng.integers(0, len(truth), size=len(truth))
        sampled_truth = truth[indices]
        if len(np.unique(sampled_truth)) < 2:
            continue
        sampled_left = metrics(sampled_truth, left[indices])
        sampled_right = metrics(sampled_truth, right[indices])
        for name in draws:
            draws[name].append(sampled_left[name] - sampled_right[name])
    rows = []
    for name, values in draws.items():
        rows.append(
            {
                "metric": name,
                "difference_definition": "left minus right",
                "point_difference": point_left[name] - point_right[name],
                "ci_lower_95": float(np.quantile(values, 0.025)),
                "ci_upper_95": float(np.quantile(values, 0.975)),
                "valid_resamples": len(values),
                "seed": seed,
            }
        )
    return pd.DataFrame(rows)
