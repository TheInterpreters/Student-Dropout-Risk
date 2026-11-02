"""W1: validation-only faithfulness, stability and constrained-recourse audit."""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from src.evaluation import development_frames, load_protocol, selected_model
from src.explanations import (
    aggregate_shap_by_group, constrained_binary_counterfactuals, deletion_curve,
    permutation_shap_values, prediction_preserving_perturbations, recompute_first_semester_features,
    select_risk_stratified_positions, semantic_feature_groups, top_k_overlap, training_reference_values,
)
from src.modeling import CATEGORICAL_COLUMNS, capacity_predictions, prepare_tfm_frame


def area_interval(values, seed=42):
    values = np.asarray(values, dtype=float)
    if not len(values) or not np.isfinite(values).all():
        raise ValueError("case-level areas must be nonempty and finite")
    rng = np.random.default_rng(seed)
    means = values[rng.integers(0, len(values), size=(2000, len(values)))].mean(axis=1)
    return {"n_cases": len(values), "mean_area": float(values.mean()),
            "ci_lower_95": float(np.quantile(means, .025)), "ci_upper_95": float(np.quantile(means, .975))}


def run_audit(train, validation, columns, model, protocol, timing_only=False):
    xtrain = prepare_tfm_frame(train, columns)
    xval = prepare_tfm_frame(validation, columns)
    # Restore category dtypes after masking/perturbation without refitting the model.
    def predict(frame):
        return model.predict_proba(prepare_tfm_frame(recompute_first_semester_features(frame), columns))
    probability = predict(xval)[:, 1]
    flags, _ = capacity_predictions(probability)
    positions = select_risk_stratified_positions(
        probability, n_cases=protocol["faithfulness"]["cases"], n_strata=5)
    groups = semantic_feature_groups(columns)
    settings = protocol["shap"]
    background = xtrain.sample(n=settings["background_size"], random_state=42)
    references = training_reference_values(train, columns)
    continuous = [c for c in columns if c not in CATEGORICAL_COLUMNS and not c.startswith("first_semester_")]

    def ranking(case, bg, seed):
        explanation = permutation_shap_values(predict, bg, case.to_frame().T,
                                             max_evals=settings["max_evals"], seed=seed)
        grouped = aggregate_shap_by_group(explanation.values[0], columns, groups)
        return grouped["feature_group"].tolist()

    start = perf_counter()
    initial = ranking(xval.iloc[positions[0]], background, 42)
    seconds = perf_counter() - start
    timing = {"split": "validation", "test_evaluated": False, "one_explanation_seconds": seconds,
              "selected_source_row_ids": validation.iloc[positions]["source_row_id"].astype(int).tolist(),
              "estimated_seed_background_explanations": len(positions) * 21,
              "estimated_seed_background_seconds": seconds * len(positions) * 21,
              "note": "Perturbation explanations and deletion predictions add runtime."}
    if timing_only:
        return {}, timing
    areas, curves, stability, recourse, perturbation_rows = [], [], [], [], []
    runs = protocol["stability"]["runs_per_case"]
    for selected_index, position in enumerate(positions):
        case = xval.iloc[position]
        source_id = int(validation.iloc[position]["source_row_id"])
        baseline = initial if selected_index == 0 else ranking(case, background, 42)
        curve = deletion_curve(
            predict, case, baseline[:settings["display_top_k"]], references,
            random_repetitions=protocol["faithfulness"]["random_deletion_repetitions"],
            seed=42, feature_groups=groups)
        areas.append({"source_row_id": source_id, "area_between_curves": curve.attrs["area_between_curves"]})
        curve.insert(0, "source_row_id", source_id)
        curves.append(curve)
        perturbations = prediction_preserving_perturbations(
            predict, case, train, continuous,
            fraction_of_training_sd=protocol["stability"]["continuous_perturbation_fraction"],
            probability_tolerance=protocol["stability"]["prediction_tolerance_absolute_probability"])
        perturbations.insert(0, "source_row_id", source_id)
        perturbation_rows.append(perturbations)
        accepted = perturbations.loc[perturbations["accepted"]].head(runs)
        for mode in ("seed", "background", "perturbation"):
            rankings = []
            for run in range(runs):
                bg, changed, shap_seed = background, case, 42
                if mode == "seed":
                    shap_seed = 42 + run
                elif mode == "background":
                    bg = xtrain.sample(n=settings["background_size"], random_state=42 + run)
                else:
                    if run >= len(accepted):
                        break
                    perturbation = accepted.iloc[run]
                    changed = case.copy()
                    changed[perturbation["feature"]] = perturbation["perturbed_value"]
                    changed = recompute_first_semester_features(changed.to_frame().T).iloc[0]
                rankings.append(ranking(changed, bg, shap_seed))
            overlap = top_k_overlap(rankings, k=5) if len(rankings) >= 2 else np.nan
            correlations = []
            for left, right in combinations(rankings, 2):
                correlations.append(spearmanr(
                    [left.index(g) for g in baseline], [right.index(g) for g in baseline]).statistic)
            stability.append({
                "source_row_id": source_id, "variation": mode, "valid_runs": len(rankings),
                "top_5_overlap": overlap,
                "rank_spearman": float(np.mean(correlations)) if correlations else np.nan,
                "low_stability": bool(overlap < .80) if np.isfinite(overlap) else "",
                "status": "ok" if len(rankings) >= 2 else "insufficient accepted perturbations",
            })
        if flags[position] == 1:
            candidates = constrained_binary_counterfactuals(predict, case, probability, int(position))
            if candidates.empty:
                recourse.append({"source_row_id": source_id, "status": "no_recourse",
                                 "n_changes": "", "changed_features": "", "dropout_probability": ""})
            else:
                for row in candidates.to_dict("records"):
                    recourse.append({"source_row_id": source_id, "status": "recourse_found",
                                     "n_changes": row["n_changes"], "changed_features": row["changed_features"],
                                     "dropout_probability": row["dropout_probability"]})
        else:
            recourse.append({"source_row_id": source_id, "status": "not_flagged",
                             "n_changes": "", "changed_features": "", "dropout_probability": ""})
    tables = {
        "faithfulness_validation": pd.DataFrame(areas),
        "faithfulness_curves_validation": pd.concat(curves, ignore_index=True),
        "faithfulness_summary_validation": pd.DataFrame([area_interval([r["area_between_curves"] for r in areas])]),
        "stability_validation": pd.DataFrame(stability),
        "recourse_validation": pd.DataFrame(recourse),
        "perturbations_validation": pd.concat(perturbation_rows, ignore_index=True),
    }
    return tables, timing


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timing-only", action="store_true", help="time one real validation SHAP explanation")
    args = parser.parse_args(argv)
    train, validation, columns = development_frames("validation")
    model = selected_model(train, columns)
    tables, timing = run_audit(train, validation, columns, model, load_protocol(), args.timing_only)
    for name, frame in tables.items():
        path = ROOT / "tables" / (name + ".csv")
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)
    path = ROOT / "artifacts" / "audit_runtime_validation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(timing, indent=2), encoding="utf-8")
    if tables:
        save_figures(tables)
    print(json.dumps(timing, indent=2))
    print("Validation only; write the descriptive findings note after reviewing the tables.")
    return 0


def save_figures(tables):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out = ROOT / "figures"
    out.mkdir(exist_ok=True)
    curve = tables["faithfulness_curves_validation"].groupby("features_deleted").mean(numeric_only=True)
    fig, ax = plt.subplots()
    ax.plot(curve.index, curve["ranked_absolute_probability_change"], label="Ranked")
    ax.plot(curve.index, curve["random_absolute_probability_change_mean"], label="Random mean")
    ax.set(xlabel="Semantic groups masked", ylabel="Absolute model probability change")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "faithfulness_validation.png")
    plt.close(fig)
    stability = tables["stability_validation"]
    fig, ax = plt.subplots()
    for mode, sample in stability.groupby("variation"):
        ax.scatter(sample["source_row_id"], sample["top_5_overlap"], label=mode)
    ax.axhline(.8, color="gray", linestyle="--")
    ax.set(xlabel="Validation source row", ylabel="Mean pairwise top-five overlap", ylim=(0, 1.05))
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "stability_validation.png")
    plt.close(fig)


if __name__ == "__main__":
    raise SystemExit(main())
