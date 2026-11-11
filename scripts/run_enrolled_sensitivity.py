"""W3.7 (optional): Enrolled-handling sensitivity, validation-only.

The primary task excludes students whose outcome is "Enrolled" (unresolved). At a real decision
point those students are in the cohort, so this script asks two questions without touching the
test split, the final-test lock, or model selection:

A. Frozen model, no refit: how does the saved final model score Enrolled students, and how many
   20%-capacity outreach slots would they take if they shared the validation cohort?
B. Grouped refit: Dropout (1) versus Not-dropout (Graduate + Enrolled = 0). TabICL with the frozen
   settings and the logistic-regression baseline are refitted on training rows plus a training
   share of Enrolled rows and evaluated on validation rows plus a validation share of Enrolled
   rows (labelled 0). The frozen primary model is scored on the same grouped validation set.

Enrolled rows are never in artifacts/split_ids.csv, so they are split here 70/15/15 with the
project seed; only the 70% and 15% shares are used. The remaining 15% share is not touched.
This is a labelled sensitivity analysis: it is not used to select or change the final model.

Usage (repo root, .venv-core):  python scripts/run_enrolled_sensitivity.py
Outputs: tables/sensitivity/enrolled_*.csv and enrolled_summary.json (aggregates only).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation import development_frames, load_protocol  # noqa: E402
from src.freeze import file_hash  # noqa: E402
from src.modeling import (  # noqa: E402
    DATA_PATH, SEED, add_first_semester_features, build_baselines, build_tfm,
    capacity_predictions, clean_column_name, evaluate_predictions, prepare_tfm_frame,
)

OUT = ROOT / "tables" / "sensitivity"


def enrolled_shares():
    """Enrolled rows split 70/15/15 by the project seed; returns (train_share, validation_share)."""
    frame = pd.read_csv(DATA_PATH).rename(columns=clean_column_name)
    frame.insert(0, "source_row_id", np.arange(len(frame), dtype=int))
    enrolled = add_first_semester_features(frame[frame["target"] == "Enrolled"].copy())
    enrolled["target"] = 0
    split_ids = set(pd.read_csv(ROOT / "artifacts" / "split_ids.csv")["source_row_id"])
    if split_ids & set(enrolled["source_row_id"]):
        raise ValueError("Enrolled rows overlap the saved binary split")
    train, rest = train_test_split(enrolled, train_size=0.70, random_state=SEED)
    validation, _held_back = train_test_split(rest, train_size=0.5, random_state=SEED)
    return (train.sort_values("source_row_id").reset_index(drop=True),
            validation.sort_values("source_row_id").reset_index(drop=True), len(enrolled))


def load_frozen():
    import joblib
    lock = json.loads((ROOT / "artifacts" / "final_test.lock").read_text(encoding="utf-8"))
    path = ROOT / "data" / "final_evaluation" / "selected_model.joblib"
    if lock.get("status") != "completed" or file_hash(path) != lock.get("model_bundle_sha256"):
        raise ValueError("saved model bundle does not match the completed final-test lock")
    return joblib.load(path)


def metric_row(name, y, probability, **extra):
    flags, boundary = capacity_predictions(probability)
    metrics = evaluate_predictions(y, flags, probability)
    metrics.pop("confusion_matrix")
    return {"model": name, **extra, "n": int(len(y)), "n_dropout": int(np.sum(y)),
            **{k: float(v) for k, v in metrics.items()}, "capacity_boundary": float(boundary)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bundle = load_frozen()
    model = bundle["model"]
    train, validation, columns = development_frames("validation")
    if list(columns) != bundle["columns"]:
        raise ValueError("feature columns differ from the saved model")
    enrolled_train, enrolled_val, n_enrolled_total = enrolled_shares()

    # A. Frozen model on Enrolled students (no refit).
    p_val = model.predict_proba(prepare_tfm_frame(validation, columns))[:, 1]
    p_enr_val = model.predict_proba(prepare_tfm_frame(enrolled_val, columns))[:, 1]
    _, val_boundary = capacity_predictions(p_val)
    y_val = validation["target"].to_numpy(int)

    distribution = []
    for label, values in (("validation_dropout", p_val[y_val == 1]),
                          ("validation_graduate", p_val[y_val == 0]),
                          ("enrolled_validation_share", p_enr_val)):
        q = np.quantile(values, [0.1, 0.25, 0.5, 0.75, 0.9])
        distribution.append({
            "group": label, "n": int(len(values)), "mean": float(values.mean()),
            "p10": q[0], "q1": q[1], "median": q[2], "q3": q[3], "p90": q[4],
            "share_at_or_above_validation_capacity_boundary": float(np.mean(values >= val_boundary)),
        })
    pd.DataFrame(distribution).to_csv(OUT / "enrolled_frozen_score_distribution.csv",
                                      index=False, float_format="%.4f")

    combined_p = np.concatenate([p_val, p_enr_val])
    is_enrolled = np.r_[np.zeros(len(p_val), bool), np.ones(len(p_enr_val), bool)]
    flags_combined, combined_boundary = capacity_predictions(combined_p)
    flags_val_only, _ = capacity_predictions(p_val)
    labelled_flags = flags_combined[~is_enrolled]
    # Same number of slots as the validation-only cohort, so displacement is not hidden by a
    # larger cohort getting more 20% slots.
    fixed_slots = int(flags_val_only.sum())
    fixed_flags, _ = capacity_predictions(combined_p, capacity=fixed_slots / len(combined_p) + 1e-9)
    fixed_labelled = fixed_flags[~is_enrolled]
    displacement = {
        "cohort_validation_only": int(len(p_val)),
        "cohort_with_enrolled": int(len(combined_p)),
        "enrolled_in_cohort": int(is_enrolled.sum()),
        "flags_validation_only": int(flags_val_only.sum()),
        "flags_with_enrolled": int(flags_combined.sum()),
        "flags_given_to_enrolled": int(flags_combined[is_enrolled].sum()),
        "flags_given_to_validation_dropout": int(labelled_flags[y_val == 1].sum()),
        "flags_given_to_validation_graduate": int(labelled_flags[y_val == 0].sum()),
        "dropout_recall_validation_only": float(flags_val_only[y_val == 1].mean()),
        "dropout_recall_with_enrolled_in_cohort": float(labelled_flags[y_val == 1].mean()),
        "fixed_slots": fixed_slots,
        "fixed_slots_given_to_enrolled": int(fixed_flags[is_enrolled].sum()),
        "dropout_recall_fixed_slots_with_enrolled": float(fixed_labelled[y_val == 1].mean()),
        "capacity_boundary_validation_only": float(val_boundary),
        "capacity_boundary_with_enrolled": float(combined_boundary),
    }
    pd.DataFrame([displacement]).to_csv(OUT / "enrolled_capacity_displacement.csv",
                                        index=False, float_format="%.4f")

    # B. Grouped target: Dropout vs Not-dropout (Graduate + Enrolled).
    grouped_train = pd.concat([train, enrolled_train], ignore_index=True)
    grouped_val = pd.concat([validation, enrolled_val], ignore_index=True)
    y_grouped = grouped_val["target"].to_numpy(int)
    rows = [
        metric_row("tabicl_frozen_primary (no refit)", y_val, p_val,
                   evaluation_set="validation (binary)", refit=False),
        metric_row("tabicl_frozen_primary (no refit)", y_grouped, combined_p,
                   evaluation_set="validation + Enrolled share (grouped)", refit=False),
    ]
    protocol = load_protocol()
    tabicl = build_tfm(protocol["model"]["name"], columns,
                       n_estimators=protocol["model"]["n_estimators"])
    start = perf_counter()
    tabicl.fit(prepare_tfm_frame(grouped_train, columns), grouped_train["target"])
    p_tabicl = tabicl.predict_proba(prepare_tfm_frame(grouped_val, columns))[:, 1]
    rows.append(metric_row("tabicl_grouped_refit", y_grouped, p_tabicl,
                           evaluation_set="validation + Enrolled share (grouped)", refit=True,
                           seconds=perf_counter() - start))
    for name in ("logistic_regression",):
        for target_set, fit_frame in (("binary", train), ("grouped", grouped_train)):
            baseline = build_baselines(columns)[name]
            baseline.fit(fit_frame[columns], fit_frame["target"])
            p = baseline.predict_proba(grouped_val[columns])[:, 1]
            rows.append(metric_row(f"{name}_{target_set}_fit", y_grouped, p,
                                   evaluation_set="validation + Enrolled share (grouped)",
                                   refit=True))
    grouped = pd.DataFrame(rows)
    grouped.to_csv(OUT / "enrolled_grouped_validation_metrics.csv", index=False, float_format="%.4f")

    summary = {
        "analysis": "W3.7 Enrolled-handling sensitivity (optional, exploratory)",
        "splits_used": ["train", "validation", "Enrolled 70% and 15% shares"],
        "test_split_accessed": False,
        "final_model_changed": False,
        "enrolled_total": n_enrolled_total,
        "enrolled_train_share": int(len(enrolled_train)),
        "enrolled_validation_share": int(len(enrolled_val)),
        "capacity_displacement": displacement,
        "note": "Enrolled outcomes are unresolved: flags given to Enrolled students are neither "
                "correct nor incorrect. Grouping Enrolled as not-dropout is an assumption.",
    }
    (OUT / "enrolled_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(displacement, indent=2))
    print(grouped[["model", "evaluation_set", "roc_auc", "brier_score",
                   "dropout_recall", "dropout_precision"]].to_string(index=False))


if __name__ == "__main__":
    main()
