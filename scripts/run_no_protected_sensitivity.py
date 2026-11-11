"""TA feedback: sensitivity run without the protected attributes (validation only, exploratory).

The research model uses every UCI feature, including the protocol's protected attributes
(gender, nationality, age, international, displaced, special educational needs). The TA asked
whether these should help decide who gets an outreach meeting. This script gives evidence for
that argument without touching the test split, the final-test lock or the selected model:

- control: TabICL refitted on the training rows with all 33 features (frozen settings);
- no_protected: the same refit with the six protected attributes removed (27 features).

Both are scored on the 544 validation students with the same top-20% capacity rule. It reports
overall metrics, how many of the 108 flags change, and descriptive flag rates by protected group
(metrics suppressed below n=30, as in the protocol). Removing a column does not remove
information that other features carry about it (proxies; see the proxy screen in tables/final_test/).

Usage (repo root, .venv-core):  python scripts/run_no_protected_sensitivity.py
Outputs: tables/sensitivity/no_protected_metrics.csv, no_protected_flag_rates.csv,
         no_protected_summary.json (aggregates only).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation import development_frames, load_protocol, protected_attributes  # noqa: E402
from src.modeling import build_tfm, capacity_predictions, evaluate_predictions, prepare_tfm_frame  # noqa: E402

OUT = ROOT / "tables" / "sensitivity"
PROTECTED_COLUMNS = ("gender", "nacionality", "age_at_enrollment", "international", "displaced",
                     "educational_special_needs")
MIN_GROUP = 30


def fit_and_score(train, validation, columns, protocol):
    model = build_tfm(protocol["model"]["name"], columns, n_estimators=protocol["model"]["n_estimators"])
    start = perf_counter()
    model.fit(prepare_tfm_frame(train, columns), train["target"])
    probability = model.predict_proba(prepare_tfm_frame(validation, columns))[:, 1]
    return probability, perf_counter() - start


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    protocol = load_protocol()
    train, validation, columns = development_frames("validation")
    missing = [c for c in PROTECTED_COLUMNS if c not in columns]
    if missing:
        raise ValueError(f"protected columns not in the model features: {missing}")
    reduced = [c for c in columns if c not in PROTECTED_COLUMNS]
    y = validation["target"].astype(int).to_numpy()

    results, flags = [], {}
    for name, cols in (("control_all_features", list(columns)), ("no_protected", reduced)):
        probability, seconds = fit_and_score(train, validation, cols, protocol)
        flag, boundary = capacity_predictions(probability)
        metrics = evaluate_predictions(y, flag, probability)
        metrics.pop("confusion_matrix", None)
        results.append({"model": name, "n_features": len(cols), "n": len(y),
                        **{k: round(float(v), 4) for k, v in metrics.items()},
                        "n_flagged": int(flag.sum()), "capacity_boundary": round(float(boundary), 4),
                        "seconds": round(seconds, 1)})
        flags[name] = np.asarray(flag, bool)
    pd.DataFrame(results).to_csv(OUT / "no_protected_metrics.csv", index=False)

    rates = []
    for attribute, values in protected_attributes(validation).items():
        values = pd.Series(values).astype(str).reset_index(drop=True)
        for level, idx in values.groupby(values).groups.items():
            idx = np.asarray(list(idx))
            row = {"attribute": attribute, "group": level, "n": len(idx)}
            if len(idx) < MIN_GROUP:
                row.update({"suppressed": True})
            else:
                row["suppressed"] = False
                for name, flag in flags.items():
                    row[f"flag_rate_{name}"] = round(float(flag[idx].mean()), 4)
                    dropouts = idx[y[idx] == 1]
                    row[f"dropout_recall_{name}"] = (round(float(flag[dropouts].mean()), 4)
                                                     if len(dropouts) >= MIN_GROUP else None)
            rates.append(row)
    pd.DataFrame(rates).to_csv(OUT / "no_protected_flag_rates.csv", index=False)

    a, b = flags["control_all_features"], flags["no_protected"]
    summary = {
        "analysis": "Sensitivity without protected attributes (TA feedback; exploratory, validation only)",
        "test_split_accessed": False, "final_model_changed": False,
        "protected_columns_removed": list(PROTECTED_COLUMNS),
        "flags_in_both": int((a & b).sum()), "flags_only_control": int((a & ~b).sum()),
        "flags_only_no_protected": int((~a & b).sum()),
        "dropouts_among_changed_flags": {"only_control": int(y[a & ~b].sum()),
                                         "only_no_protected": int(y[~a & b].sum())},
        "metrics": results,
        "note": "Descriptive only. Removing protected columns does not remove proxy information, "
                "and similar validation performance does not establish fairness.",
    }
    (OUT / "no_protected_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
