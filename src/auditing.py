"""Fairness and subgroup diagnostics for the frozen operating threshold."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from sklearn.metrics import precision_score, recall_score


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
    threshold: float,
    min_group_size: int = 30,
) -> pd.DataFrame:
    """Report descriptive operating-point metrics without declaring fairness."""
    truth = np.asarray(y_true, dtype=int)
    scores = np.asarray(probabilities, dtype=float)
    labels = pd.Series(groups).astype(str).to_numpy()
    predictions = (scores >= threshold).astype(int)
    rows: list[dict[str, object]] = []
    for level in sorted(np.unique(labels)):
        mask = labels == level
        n = int(mask.sum())
        if n < min_group_size:
            continue
        subgroup_truth = truth[mask]
        subgroup_predictions = predictions[mask]
        negatives = subgroup_truth == 0
        false_positive_rate = (
            float(np.mean(subgroup_predictions[negatives] == 1)) if negatives.any() else np.nan
        )
        rows.append(
            {
                "group": level,
                "n": n,
                "outcome_rate": float(np.mean(subgroup_truth)),
                "flag_rate": float(np.mean(subgroup_predictions)),
                "true_positive_rate": recall_score(
                    subgroup_truth, subgroup_predictions, pos_label=1, zero_division=0
                ),
                "false_positive_rate": false_positive_rate,
                "precision": precision_score(
                    subgroup_truth, subgroup_predictions, pos_label=1, zero_division=0
                ),
                "mean_predicted_risk": float(np.mean(scores[mask])),
                "calibration_gap": float(
                    np.mean(scores[mask]) - np.mean(subgroup_truth)
                ),
            }
        )
    return pd.DataFrame(rows)
