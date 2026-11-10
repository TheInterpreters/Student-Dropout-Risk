"""W1 supplementary surrogate comparison, validation cases only.

For five SHAP-selected semantic groups, enumerate 2^5 reference-masking
patterns, obtain FROZEN TabICL probabilities and compare six small, post-hoc
local surrogates for descriptive fidelity on an internally held-out set of
masking patterns. Does not fit, alter or retest the selected classifier.

Methods are: ordinary least squares (OLS), Ridge and Lasso, each with
main-effects only or main + ten pairwise interactions. Never interpret
coefficients as effects of real student support or as SHAP interactions.
"""
from __future__ import annotations

from itertools import combinations, product
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RIDGE_ALPHAS = (0.0001, 0.001, 0.01, 0.1, 1.0, 10.0)
LASSO_ALPHAS = (0.000001, 0.00001, 0.0001, 0.001, 0.01)
SEED = 42


def make_binary_design(mask_patterns: np.ndarray, group_names: list[str], with_pairs: bool):
    """1 = masked to training reference; 0 = left at observed value."""
    m = np.asarray(mask_patterns, dtype=float)
    if m.ndim != 2 or m.shape[1] != len(group_names):
        raise ValueError("Mask design columns must align with selected group names")
    names = [f"mask::{name}" for name in group_names]
    values = [m]
    if with_pairs:
        pairs = list(combinations(range(len(group_names)), 2))
        values.append(np.column_stack([m[:, i] * m[:, j] for i, j in pairs]))
        names.extend(f"joint_mask::{group_names[i]} + {group_names[j]}" for i, j in pairs)
    return np.column_stack(values), names


def fixed_mask_holdout(group_count: int = 5, seed: int = SEED):
    """All original, single- and pair-masked rows are in train.

    8 of the remaining 16 higher-order (3-5 mask) patterns are held out,
    so the evaluation asks whether learned low-order surrogates extrapolate
    to more extensive joint masking. This is *not* general model accuracy.
    """
    if group_count != 5:
        raise ValueError("Protocol fixes five top-ranked semantic groups")
    masks = np.array(list(product((0, 1), repeat=group_count)), dtype=int)
    complex_idx = np.flatnonzero(masks.sum(axis=1) >= 3)
    rng = np.random.default_rng(seed)
    holdout = np.sort(rng.choice(complex_idx, size=8, replace=False))
    train = np.array([i for i in range(len(masks)) if i not in set(holdout)], dtype=int)
    assert len(train) == 24 and len(holdout) == 8
    return masks, train, holdout


def _model(method: str, alpha: float | None):
    if method == "OLS":
        regressor = LinearRegression()
    elif method == "Ridge":
        regressor = Ridge(alpha=float(alpha))
    elif method == "Lasso":
        regressor = Lasso(alpha=float(alpha), max_iter=30000, tol=1e-7, selection="cyclic")
    else:
        raise ValueError("Unknown comparison method " + method)
    # Scaling is fit separately within each CV fold and again on training rows.
    return Pipeline([("scale", StandardScaler()), ("reg", regressor)])


def fit_six_surrogates(mask_patterns: np.ndarray, probabilities: np.ndarray,
                       group_names: list[str], seed: int = SEED):
    """Compare six candidates using *only* separate masked-pattern holdouts.

    Penalty hyperparameters are chosen in 3-fold CV on the 24 training rows;
    the 8 held-out rows never influence the fit or alpha choice. All metrics
    are computed on original, unclipped surrogate predictions.
    """
    masks = np.asarray(mask_patterns, dtype=int)
    y = np.asarray(probabilities, dtype=float)
    if masks.shape != (32, 5) or y.shape != (32,):
        raise ValueError("Expected 32 complete factorial masks and 32 probabilities")
    expected, train_idx, hold_idx = fixed_mask_holdout(seed=seed)
    if not np.array_equal(masks, expected):
        raise ValueError("Mask patterns are not in the deterministic factorial order")
    if not np.isfinite(y).all() or np.any((y < 0) | (y > 1)):
        raise ValueError("Invalid target model probabilities")
    comparisons = []
    predictions = []
    for with_pairs in (False, True):
        design, columns = make_binary_design(masks, group_names, with_pairs)
        xtrain, xhold = design[train_idx], design[hold_idx]
        ytrain, yhold = y[train_idx], y[hold_idx]
        for method in ("OLS", "Ridge", "Lasso"):
            if method == "OLS":
                alpha = None
                cv_mae = None
            else:
                alphas = RIDGE_ALPHAS if method == "Ridge" else LASSO_ALPHAS
                folds = KFold(n_splits=3, shuffle=True, random_state=seed)
                checked = []
                for candidate in alphas:
                    maes = []
                    for inner_train, inner_valid in folds.split(xtrain):
                        fitted = _model(method, candidate).fit(xtrain[inner_train], ytrain[inner_train])
                        estimated = fitted.predict(xtrain[inner_valid])
                        maes.append(float(np.mean(np.abs(estimated - ytrain[inner_valid]))))
                    checked.append((float(np.mean(maes)), candidate))
                cv_mae, alpha = min(checked, key=lambda t: (t[0], t[1]))
            fitted = _model(method, alpha).fit(xtrain, ytrain)
            forecast = fitted.predict(xhold)
            residual = forecast - yhold
            mae = float(np.mean(np.abs(residual)))
            rmse = float(np.sqrt(np.mean(residual**2)))
            variance = float(np.sum((yhold - yhold.mean()) ** 2))
            r2 = float(1 - np.sum(residual**2) / variance) if variance > 1e-12 else None
            coefs = np.asarray(fitted.named_steps["reg"].coef_, dtype=float)
            n_nonzero = int(np.count_nonzero(np.abs(coefs) > 1e-5))
            method_label = method + ("+pairs" if with_pairs else "+main")
            comparisons.append({
                "variant": method_label, "method": method, "include_pair_terms": with_pairs,
                "alpha": alpha, "inner_cv_mae": cv_mae, "holdout_mae": mae,
                "holdout_rmse": rmse, "holdout_r2": r2,
                "nonzero_terms": n_nonzero, "total_terms": len(columns),
                "fraction_outside_probability_range": float(np.mean((forecast < 0) | (forecast > 1))),
                "design_note": "train=24; holdout=8 higher-order masking patterns; predictions not clipped",
            })
            predictions.extend({
                "variant": method_label, "pattern_index": int(row_ix),
                "n_masked_groups": int(masks[row_ix].sum()),
                "tabicl_probability": float(y[row_ix]),
                "surrogate_probability": float(p),
                "absolute_error": float(abs(p - y[row_ix])),
            } for row_ix, p in zip(hold_idx, forecast))
    # No single 'winner' based on one student: aggregate across the full panel.
    return comparisons, predictions


def run_masking_surrogates(predict, case: pd.Series, groups: dict,
                           references: pd.Series, top_five: list[str],
                           mask_group_union):
    """Get the actual frozen model's response for 32 deterministic probes.

    No labels are used; only the selected *validation* case and training-only
    references enter the 32 prediction calls. The masks can be off-manifold.
    """
    names = list(top_five)
    if len(names) != 5 or len(set(names)) != 5:
        raise ValueError("Exactly five distinct SHAP groups required")
    masks, _, _ = fixed_mask_holdout()
    probs = []
    for flags in masks:
        selected = [name for name, enabled in zip(names, flags) if enabled]
        masked = mask_group_union(case, selected, groups, references)
        pred = np.asarray(predict(masked.to_frame().T), dtype=float)
        if pred.shape != (1, 2) or not np.isfinite(pred).all():
            raise ValueError("Invalid frozen-model probability for masking context")
        probs.append(float(pred[0, 1]))
    summaries, holdout_details = fit_six_surrogates(masks, np.asarray(probs), names)
    return {
        "top_five_groups": names,
        "masking_pattern_count": int(len(masks)),
        "train_pattern_count": 24,
        "holdout_pattern_count": 8,
        "summary": summaries,
        "holdout_predictions": holdout_details,
        "comparability_note": "Surrogates fit TabICL responses to masking interventions only. Good fidelity does not prove genuine/cause/actionability or global explanation quality.",
    }


def aggregate_surrogate_comparisons(cases: list[dict]):
    """Score only when *every* case has all six variants and all heldouts."""
    summaries = []
    details = []
    for case in cases:
        sr = case.get("surrogate_comparison")
        if not sr or len(sr.get("summary", [])) != 6 or len(sr.get("holdout_predictions", [])) != 48:
            raise ValueError("Missing/incomplete per-case six-surrogate comparison")
        sid = int(case["source_row_id"])
        summaries.extend({"source_row_id": sid, **r} for r in sr["summary"])
        details.extend({"source_row_id": sid, **r} for r in sr["holdout_predictions"])
    df = pd.DataFrame(summaries)
    holdout = pd.DataFrame(details)
    if df.groupby("source_row_id")["variant"].nunique().ne(6).any():
        raise ValueError("Duplicate/missing surrogate variants")
    pooled = holdout.groupby("variant", as_index=False).agg(
        pooled_holdout_mae=("absolute_error", "mean"),
        pooled_n_holdout=("absolute_error", "size"),
    )
    case_summaries = df.groupby("variant", as_index=False).agg(
        mean_case_mae=("holdout_mae", "mean"),
        median_case_mae=("holdout_mae", "median"),
        mean_case_rmse=("holdout_rmse", "mean"),
        mean_nonzero_terms=("nonzero_terms", "mean"),
        mean_out_of_range_fraction=("fraction_outside_probability_range", "mean"),
        n_cases=("source_row_id", "nunique"),
    )
    totals = case_summaries.merge(pooled, on="variant", validate="one_to_one")
    # Primary comparison: lowest pooled masked-scenario MAE, with complexity
    # and out-of-range predictions still separately reported. No significance claim.
    totals = totals.sort_values(["pooled_holdout_mae", "mean_nonzero_terms", "variant"], ignore_index=True)
    return df, holdout, totals
