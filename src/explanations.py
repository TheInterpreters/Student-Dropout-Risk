"""Reusable explanation-evaluation primitives for the frozen classifier.

The functions here do not open the final test set or manufacture study results. They
implement the pre-specified mechanics that can be applied after the model is frozen.
"""

from __future__ import annotations

from itertools import combinations
from typing import Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from src.modeling import CATEGORICAL_COLUMNS, SEED


ProbabilityFunction = Callable[[pd.DataFrame], np.ndarray]


FIRST_SEMESTER_GROUPS: dict[str, tuple[str, ...]] = {
    "first_semester_participation": (
        "curricular_units_1st_sem_enrolled",
        "curricular_units_1st_sem_evaluations",
        "curricular_units_1st_sem_without_evaluations",
        "first_semester_no_enrollment",
        "first_semester_no_evaluations",
    ),
    "first_semester_progress": (
        "curricular_units_1st_sem_approved",
        "curricular_units_1st_sem_grade",
        "first_semester_pass_rate",
    ),
}


def recompute_first_semester_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Restore deterministic relationships after a grouped perturbation."""
    result = frame.copy()
    enrolled_name = "curricular_units_1st_sem_enrolled"
    approved_name = "curricular_units_1st_sem_approved"
    evaluations_name = "curricular_units_1st_sem_evaluations"
    if enrolled_name in result and approved_name in result:
        enrolled = pd.to_numeric(result[enrolled_name])
        approved = pd.to_numeric(result[approved_name])
        result["first_semester_pass_rate"] = np.divide(
            approved,
            enrolled,
            out=np.zeros(len(result), dtype=float),
            where=enrolled.to_numpy() > 0,
        )
        result["first_semester_no_enrollment"] = (enrolled == 0).astype(int)
    if evaluations_name in result:
        evaluations = pd.to_numeric(result[evaluations_name])
        result["first_semester_no_evaluations"] = (evaluations == 0).astype(int)
    return result


def semantic_feature_groups(columns: Sequence[str]) -> dict[str, tuple[str, ...]]:
    """Return non-overlapping source-feature groups for perturbation audits."""
    available = set(columns)
    groups: dict[str, tuple[str, ...]] = {}
    assigned: set[str] = set()
    for name, members in FIRST_SEMESTER_GROUPS.items():
        present = tuple(member for member in members if member in available)
        if present:
            groups[name] = present
            assigned.update(present)
    for column in columns:
        if column not in assigned:
            groups[column] = (column,)
    return groups


def training_reference_values(train: pd.DataFrame, columns: Sequence[str]) -> pd.Series:
    """Return train-only masking values: mode for categorical, median otherwise."""
    values: dict[str, object] = {}
    for column in columns:
        series = train[column]
        if column in CATEGORICAL_COLUMNS:
            modes = series.mode(dropna=True)
            if modes.empty:
                raise ValueError(f"categorical feature {column!r} has no training mode")
            values[column] = modes.iloc[0]
        else:
            values[column] = float(series.median())
    return pd.Series(values)


def dropout_probability(predict_proba: ProbabilityFunction, frame: pd.DataFrame) -> np.ndarray:
    probabilities = np.asarray(predict_proba(frame))
    if probabilities.ndim == 2:
        probabilities = probabilities[:, 1]
    if probabilities.ndim != 1 or len(probabilities) != len(frame):
        raise ValueError("predict_proba must return n probabilities or an n x 2 matrix")
    return probabilities.astype(float)


def deletion_curve(
    predict_proba: ProbabilityFunction,
    case: pd.Series,
    ranking: Sequence[str],
    references: pd.Series,
    random_repetitions: int = 50,
    seed: int = SEED,
    random_pool: Sequence[str] | None = None,
    feature_groups: Mapping[str, Sequence[str]] | None = None,
) -> pd.DataFrame:
    """Compare ranked feature deletion with repeated random deletion.

    Deletion means replacement by a training-only reference. It is a reliance test,
    not a feasible intervention or causal counterfactual.
    """
    groups = dict(feature_groups or {column: (column,) for column in case.index})
    ranking = list(dict.fromkeys(ranking))
    if not ranking:
        raise ValueError("ranking must contain at least one feature")
    missing = set(ranking).difference(groups)
    if missing:
        raise KeyError(f"feature groups missing from mapping: {sorted(missing)}")

    def mask_group(row: pd.Series, group_name: str) -> pd.Series:
        masked = row.copy()
        members = groups[group_name]
        absent = set(members).difference(case.index) | set(members).difference(references.index)
        if absent:
            raise KeyError(f"features missing from case/references: {sorted(absent)}")
        for feature in members:
            masked[feature] = references[feature]
        restored = recompute_first_semester_features(masked.to_frame().T)
        return restored.iloc[0]

    columns = list(case.index)
    ranked_scores = []
    ranked_case = case.copy()
    for step in range(len(ranking) + 1):
        if step:
            ranked_case = mask_group(ranked_case, ranking[step - 1])
        ranked_scores.append(float(dropout_probability(predict_proba, ranked_case.to_frame().T)[0]))

    random_pool = list(dict.fromkeys(random_pool or groups.keys()))
    random_missing = set(random_pool).difference(groups)
    if random_missing:
        raise KeyError(f"random-pool features missing from case/references: {sorted(random_missing)}")
    if len(random_pool) < len(ranking):
        raise ValueError("random_pool must contain at least as many features as ranking")

    rng = np.random.default_rng(seed)
    random_scores = np.zeros((random_repetitions, len(ranking) + 1), dtype=float)
    for repetition in range(random_repetitions):
        random_order = list(rng.choice(random_pool, size=len(ranking), replace=False))
        random_case = case.copy()
        random_scores[repetition, 0] = dropout_probability(
            predict_proba, random_case.to_frame().T
        )[0]
        for step, feature in enumerate(random_order, start=1):
            random_case = mask_group(random_case, feature)
            random_scores[repetition, step] = dropout_probability(
                predict_proba, random_case.to_frame().T
            )[0]

    original_probability = ranked_scores[0]
    ranked_absolute_change = np.abs(np.asarray(ranked_scores) - original_probability)
    random_absolute_change = np.abs(random_scores - original_probability)
    result = pd.DataFrame(
        {
            "features_deleted": np.arange(len(ranking) + 1),
            "ranked_dropout_probability": ranked_scores,
            "random_dropout_probability_mean": random_scores.mean(axis=0),
            "random_dropout_probability_sd": random_scores.std(axis=0, ddof=0),
            "ranked_absolute_probability_change": ranked_absolute_change,
            "random_absolute_probability_change_mean": random_absolute_change.mean(axis=0),
            "random_absolute_probability_change_sd": random_absolute_change.std(axis=0, ddof=0),
        }
    )
    result.attrs["area_between_curves"] = float(
        np.trapezoid(
            result["ranked_absolute_probability_change"]
            - result["random_absolute_probability_change_mean"],
            result["features_deleted"],
        )
    )
    result.attrs["area_definition"] = (
        "ranked minus random cumulative absolute probability change"
    )
    return result


def grouped_permutation_importance(
    predict_proba: ProbabilityFunction,
    frame: pd.DataFrame,
    target: Sequence[int],
    groups: Mapping[str, Sequence[str]],
    repeats: int = 30,
    seed: int = SEED,
) -> pd.DataFrame:
    """Measure validation ROC-AUC loss after jointly permuting semantic groups."""
    from sklearn.metrics import roc_auc_score

    truth = np.asarray(target, dtype=int)
    baseline = roc_auc_score(truth, dropout_probability(predict_proba, frame))
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    for group_name, members in groups.items():
        members = [member for member in members if member in frame.columns]
        if not members:
            continue
        losses = []
        for _ in range(repeats):
            permutation = rng.permutation(len(frame))
            perturbed = frame.copy()
            perturbed.loc[:, members] = frame.iloc[permutation][members].to_numpy()
            perturbed = recompute_first_semester_features(perturbed)
            score = roc_auc_score(truth, dropout_probability(predict_proba, perturbed))
            losses.append(baseline - score)
        rows.append(
            {
                "feature_group": group_name,
                "members": ", ".join(members),
                "baseline_roc_auc": baseline,
                "importance_mean": float(np.mean(losses)),
                "importance_sd": float(np.std(losses, ddof=1)),
                "repeats": repeats,
            }
        )
    return pd.DataFrame(rows).sort_values("importance_mean", ascending=False, ignore_index=True)


def accumulated_local_effect(
    predict_proba: ProbabilityFunction,
    frame: pd.DataFrame,
    feature: str,
    bins: int = 10,
) -> pd.DataFrame:
    """Compute first-order ALE for one numerical feature on observed intervals."""
    values = pd.to_numeric(frame[feature], errors="raise").to_numpy(dtype=float)
    edges = np.unique(np.quantile(values, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        raise ValueError(f"feature {feature!r} has too few distinct values for ALE")
    interval = np.clip(np.digitize(values, edges[1:-1]), 0, len(edges) - 2)
    effects = np.zeros(len(edges) - 1, dtype=float)
    counts = np.zeros(len(edges) - 1, dtype=int)
    lower_frame = frame.copy()
    upper_frame = frame.copy()
    lower_frame[feature] = edges[interval]
    upper_frame[feature] = edges[interval + 1]
    lower_frame = recompute_first_semester_features(lower_frame)
    upper_frame = recompute_first_semester_features(upper_frame)
    row_effects = dropout_probability(
        predict_proba, upper_frame
    ) - dropout_probability(predict_proba, lower_frame)
    for index in range(len(effects)):
        mask = interval == index
        counts[index] = int(mask.sum())
        if not mask.any():
            continue
        effects[index] = np.mean(row_effects[mask])
    accumulated = np.cumsum(effects)
    centered = accumulated - np.average(accumulated, weights=np.maximum(counts, 1))
    return pd.DataFrame(
        {
            "feature": feature,
            "lower": edges[:-1],
            "upper": edges[1:],
            "midpoint": (edges[:-1] + edges[1:]) / 2,
            "n": counts,
            "local_effect": effects,
            "ale": centered,
        }
    )


def top_k_overlap(rankings: Sequence[Sequence[str]], k: int = 5) -> float:
    """Return the rubric's mean pairwise top-k agreement: |intersection| / k."""
    if k < 1:
        raise ValueError("k must be positive")
    if len(rankings) < 2:
        raise ValueError("at least two rankings are required")
    sets = []
    for ranking in rankings:
        top_features = set(ranking[:k])
        if len(top_features) != k:
            raise ValueError(f"each ranking must contain at least {k} unique features")
        sets.append(top_features)
    values = []
    for left, right in combinations(sets, 2):
        values.append(len(left & right) / k)
    return float(np.mean(values))


def permutation_shap_values(
    predict_proba: ProbabilityFunction,
    background: pd.DataFrame,
    cases: pd.DataFrame,
    max_evals: int | None = None,
    seed: int = SEED,
):
    """Run model-agnostic permutation SHAP with an explicitly supplied background."""
    import shap

    if max_evals is None:
        max_evals = 2 * background.shape[1] + 1
    background = background.copy()
    cases = cases.copy()
    categorical_dtypes = {
        column: background[column].dtype
        for column in background.columns
        if isinstance(background[column].dtype, pd.CategoricalDtype)
    }

    def restore_frame(values) -> pd.DataFrame:
        restored = pd.DataFrame(values, columns=background.columns)
        for column, dtype in categorical_dtypes.items():
            restored[column] = pd.Categorical(
                restored[column], categories=dtype.categories, ordered=dtype.ordered
            )
        return recompute_first_semester_features(restored)

    masker = shap.maskers.Independent(background, max_samples=len(background))
    explainer = shap.PermutationExplainer(
        lambda values: dropout_probability(predict_proba, restore_frame(values)),
        masker,
        seed=seed,
    )
    return explainer(cases, max_evals=max_evals)


def constrained_binary_counterfactuals(
    predict_proba: ProbabilityFunction,
    case: pd.Series,
    allowed_resolutions: dict[str, int] | None = None,
    threshold: float = 0.5,
) -> pd.DataFrame:
    """Enumerate defensible binary administrative changes, smallest changes first.

    The defaults are potentially resolvable statuses, not guaranteed student-controlled
    actions. Historical grades and demographic attributes are never changed here.
    """
    if allowed_resolutions is None:
        allowed_resolutions = {"debtor": 0, "tuition_fees_up_to_date": 1}
    mutable = [
        feature
        for feature, resolved_value in allowed_resolutions.items()
        if feature in case.index and int(case[feature]) != resolved_value
    ]
    candidates: list[dict[str, object]] = []
    for size in range(1, len(mutable) + 1):
        for changed in combinations(mutable, size):
            candidate = case.copy()
            for feature in changed:
                candidate[feature] = allowed_resolutions[feature]
            probability = float(
                dropout_probability(predict_proba, candidate.to_frame().T)[0]
            )
            if probability < threshold:
                candidates.append(
                    {
                        "n_changes": size,
                        "changed_features": ", ".join(changed),
                        "dropout_probability": probability,
                    }
                )
        if candidates:
            break
    return pd.DataFrame(candidates).sort_values(
        "dropout_probability", ignore_index=True
    ) if candidates else pd.DataFrame(
        columns=["n_changes", "changed_features", "dropout_probability"]
    )
