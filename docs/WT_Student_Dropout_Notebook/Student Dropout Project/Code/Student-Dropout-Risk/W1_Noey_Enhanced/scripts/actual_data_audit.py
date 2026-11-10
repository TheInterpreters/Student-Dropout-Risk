"""Audit all 544 actual validation rows and compare outcomes with model outputs.

Training and validation are separate. Training accuracy is in-sample evidence.
No final-test scoring, model tuning, label invention or row sampling occurs.
"""
import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from development_population import ROOT, EXPECTED_COUNTS, load_population
from run_enhanced_audit import atomic_json

EXPECTED_TOTAL = EXPECTED_COUNTS["validation"]


def require_validation_only(frames):
    if set(frames) != {"validation"}:
        raise ValueError("Audit/evaluation must include validation only; training is for fitting/reference values")
    if len(frames["validation"]) != EXPECTED_TOTAL:
        raise ValueError("Audit must include all 544 validation observations")


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def data_audit(frames, columns, output, root=ROOT):
    require_validation_only(frames)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    quality, class_rows, partition_summary = [], [], {}
    for split, frame in frames.items():
        numeric = frame[columns].apply(pd.to_numeric, errors="coerce")
        finite = np.isfinite(numeric.to_numpy(dtype=float))
        for i, col in enumerate(columns):
            quality.append({
                "source_split": split, "feature": col, "n_rows": len(frame),
                "missing_count": int(frame[col].isna().sum()),
                "nonfinite_or_nonnumeric_count": int((~finite[:, i]).sum()),
                "distinct_values": int(frame[col].nunique(dropna=False)),
                "minimum": float(numeric[col].min()), "maximum": float(numeric[col].max()),
            })
        enrolled = frame.curricular_units_1st_sem_enrolled
        approved = frame.curricular_units_1st_sem_approved
        grade = frame.curricular_units_1st_sem_grade
        checks = pd.DataFrame({
            "source_row_id": frame.source_row_id,
            "source_split": split,
            "actual_dropout": frame.target,
            "has_nonfinite_model_feature": ~finite.all(axis=1),
            "approved_exceeds_enrolled": approved > enrolled,
            "negative_enrolled_or_approved": (enrolled < 0) | (approved < 0),
            "grade_outside_0_20": ~grade.between(0, 20),
            "duplicate_feature_profile": frame.duplicated(subset=columns, keep=False),
        })
        checks.to_csv(output / f"row_checks_{split}.csv", index=False)
        partition_summary[split] = {
            "n_rows": len(frame),
            "actual_dropouts": int(frame.target.sum()),
            "actual_graduates": int((frame.target == 0).sum()),
            **{c: int(checks[c].sum()) for c in checks if c not in ("source_row_id", "source_split", "actual_dropout")},
        }
        class_rows.extend({"source_split": split, "actual_outcome": name, "n": int((frame.target == label).sum())}
                          for label, name in [(0, "Graduate"), (1, "Dropout")])
    pd.DataFrame(quality).to_csv(output / "feature_quality_by_split.csv", index=False)
    pd.DataFrame(class_rows).to_csv(output / "actual_outcome_counts_by_split.csv", index=False)
    summary = {
        "scope": "all_validation_rows", "n_rows": sum(len(f) for f in frames.values()),
        "expected_rows": EXPECTED_TOTAL, "n_model_features": len(columns),
        "all_observations_checked": len(frames["validation"]) == EXPECTED_TOTAL,
        "partitions": partition_summary, "test_evaluated": False,
        "data_sha256": file_hash(root / "eda_uci_data/data/dropout_data.csv"),
        "split_sha256": file_hash(root / "artifacts/split_ids.csv"),
        "note": "Data checks use actual records. Flagged inconsistencies are reported without deleting or modifying records. This is not a model or explanation audit completion claim.",
    }
    atomic_json(output / "data_audit_summary.json", summary)
    actual = partition_summary["validation"]
    checks = "\n".join(f"| {name.replace('_', ' ')} | {actual[name]} |" for name in (
        "has_nonfinite_model_feature", "approved_exceeds_enrolled", "negative_enrolled_or_approved",
        "grade_outside_0_20", "duplicate_feature_profile"))
    (output / "ACTUAL_DATA_AUDIT.md").write_text(f"""# Actual validation-data audit

**Data checks completed: {summary['n_rows']}/{EXPECTED_TOTAL} validation observations, {len(columns)} model features.**
Actual recorded outcomes: {actual['actual_dropouts']} Dropout and {actual['actual_graduates']} Graduate.

The 2,541 training rows are fitting/reference data, not audit cases. The 545 locked test rows are excluded from this analysis. The original saved split IDs are used; no sampling or re-splitting occurs.

| Data check | Rows flagged |
| --- | ---: |
{checks}

These checks establish only the listed data properties. Zero flags do not certify the entire data-generating process, feature validity, model accuracy, explanation quality or intervention efficacy. Rows are checked without deleting or changing source records.

**Next:** compare the trained model's predictions with the 544 recorded outcomes (`--compare`), then run/resume all 544 explanation cases (`--run`). This data report alone does not mean either model stage has run. Their evidence is stored separately.

Provenance: source data SHA256 `{summary['data_sha256']}`; saved split SHA256 `{summary['split_sha256']}`. See `data_audit_summary.json`, `feature_quality_by_split.csv`, `actual_outcome_counts_by_split.csv` and `row_checks_validation.csv`.
""", encoding="utf-8")
    return summary


def compare_actual_outcomes(frames, probabilities, output):
    require_validation_only(frames)
    from src.modeling import capacity_predictions, evaluate_predictions
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    results = {}
    for split, frame in frames.items():
        p = np.asarray(probabilities[split], dtype=float)
        if p.shape != (len(frame),) or not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
            raise ValueError(f"{split}: invalid model predictions")
        flags, boundary = capacity_predictions(p, capacity=.20)
        truth = frame.target.to_numpy(dtype=int)
        rows = pd.DataFrame({
            "source_row_id": frame.source_row_id, "source_split": split,
            "actual_dropout": truth, "predicted_dropout_probability": p,
            "predicted_outreach_flag": flags, "flag_matches_actual_dropout": flags == truth,
            "error_type": np.select([(flags == 1) & (truth == 1), (flags == 1) & (truth == 0),
                                     (flags == 0) & (truth == 1)], ["TP", "FP", "FN"], default="TN"),
        })
        rows.to_csv(output / f"actual_vs_model_{split}.csv", index=False)
        results[split] = {
            "n_rows": len(frame), "evidence_type": "in_sample" if split == "train" else "held_out_validation",
            "operating_rule": "top 20% of this original split; stable source-row tie break",
            "capacity_boundary": boundary, **evaluate_predictions(truth, flags, p),
            "accuracy_of_capacity_flags": float((flags == truth).mean()),
            "interpretation": "Outreach flags are a capacity policy, not a universal 0.5 probability classification rule.",
        }
    summary = {"scope": "all_validation_rows", "test_evaluated": False,
               "n_rows_scored": sum(len(f) for f in frames.values()), "partitions": results,
               "warning": "Training fit is in-sample. Only validation measures held-out performance; neither is the locked final test. Predictive performance does not validate explanation fidelity or causal benefit."}
    atomic_json(output / "actual_vs_model_summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", required=True)
    args = parser.parse_args()
    frames, columns = load_population()
    summary = data_audit({"validation": frames["validation"]}, columns,
                         ROOT / "W1_Noey_Enhanced/outputs/actual_validation")
    print(f"Actual data audit: {summary['n_rows']}/{EXPECTED_TOTAL} rows checked; no model scoring yet.")


if __name__ == "__main__":
    main()
