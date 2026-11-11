"""Compare the W1 audit's refit predictions with the frozen final model on the validation split.

W1 refitted TabICL with the frozen settings because the frozen bundle was not available to it.
This read-only check scores the 544 validation students with the frozen bundle (bound to
artifacts/final_test.lock) and compares probabilities and 20%-capacity flags with the values saved
in W1_analysis/03_Full_Audit/Cases. No test data, no refit, no final-test rerun.

Usage (repo root, .venv-core):  python scripts/check_w1_refit_identity.py
Output: artifacts/w1_refit_identity.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation import development_frames  # noqa: E402
from src.freeze import file_hash  # noqa: E402
from src.modeling import capacity_predictions, prepare_tfm_frame  # noqa: E402

CASES = ROOT / "W1_analysis" / "03_Full_Audit" / "Cases"
OUT = ROOT / "artifacts" / "w1_refit_identity.json"
TOLERANCE = 1e-4


def compare(frozen_probability, refit_probability, refit_flags):
    frozen_probability = np.asarray(frozen_probability, float)
    refit_probability = np.asarray(refit_probability, float)
    frozen_flags, _ = capacity_predictions(frozen_probability)
    difference = np.abs(frozen_probability - refit_probability)
    agree = frozen_flags == np.asarray(refit_flags, int)
    return {
        "n_cases": int(len(difference)),
        "max_abs_probability_difference": float(difference.max()),
        "mean_abs_probability_difference": float(difference.mean()),
        "cases_above_tolerance": int((difference > TOLERANCE).sum()),
        "tolerance": TOLERANCE,
        "frozen_flags": int(frozen_flags.sum()),
        "refit_flags": int(np.sum(refit_flags)),
        "flag_disagreements": int((~agree).sum()),
        "identical_within_tolerance": bool((difference <= TOLERANCE).all() and agree.all()),
    }


def main():
    import joblib
    lock = json.loads((ROOT / "artifacts" / "final_test.lock").read_text(encoding="utf-8"))
    bundle_path = ROOT / "data" / "final_evaluation" / "selected_model.joblib"
    if lock.get("status") != "completed" or file_hash(bundle_path) != lock.get("model_bundle_sha256"):
        raise ValueError("saved model bundle does not match the completed final-test lock")
    bundle = joblib.load(bundle_path)
    _, validation, columns = development_frames("validation")
    if list(columns) != bundle["columns"]:
        raise ValueError("validation features do not match the saved model")
    frozen = bundle["model"].predict_proba(prepare_tfm_frame(validation, columns))[:, 1]
    saved = {}
    for path in CASES.glob("case_*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        saved[int(record["source_row_id"])] = (record["predicted_probability"], record["flagged"])
    ids = validation["source_row_id"].astype(int).tolist()
    if set(ids) != set(saved):
        raise ValueError("W1 cases do not cover exactly the validation split")
    result = compare(frozen, [saved[i][0] for i in ids], [saved[i][1] for i in ids])
    result.update({"split": "validation", "test_split_accessed": False,
                   "model_bundle_sha256": lock["model_bundle_sha256"]})
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
