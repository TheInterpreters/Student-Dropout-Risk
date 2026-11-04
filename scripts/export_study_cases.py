"""W3.9: export restricted study cases from the saved final model, without refitting or retuning."""
from __future__ import annotations

import argparse
import csv
import json
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from forms import case_pack as cp
from src.evaluation import development_frames, load_protocol
from src.explanations import (
    aggregate_shap_by_group, permutation_shap_values, select_forward_simulation_positions,
    semantic_feature_groups,
)
from src.modeling import capacity_predictions, prepare_tfm_frame
from src.freeze import file_hash, verify_snapshot


def main(argv=None):
    import joblib
    import numpy as np
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="data/study_cases")
    args = parser.parse_args(argv)
    lock = json.loads((ROOT / "artifacts" / "final_test.lock").read_text(encoding="utf-8"))
    if lock.get("status") != "completed":
        raise ValueError("study export requires a completed final-test lock")
    if hashlib.sha256((ROOT / "config" / "evaluation_protocol.json").read_bytes()).hexdigest() != lock["protocol_sha256"]:
        raise ValueError("protocol changed after the final test")
    bundle_path = ROOT / "data" / "final_evaluation" / "selected_model.joblib"
    expected_bundle_hash = lock.get("model_bundle_sha256")
    if not isinstance(expected_bundle_hash, str):
        raise ValueError("final-test lock has no saved model-bundle SHA-256")
    if file_hash(bundle_path) != expected_bundle_hash:
        raise ValueError("saved model bundle changed after final evaluation")
    if lock.get("freeze_mode") == "local_snapshot":
        manifest_path = Path(lock["local_freeze"])
        if file_hash(manifest_path) != lock["local_freeze_sha256"]:
            raise ValueError("local-freeze manifest changed after final evaluation")
        verify_snapshot(ROOT, manifest_path)
        bundle = joblib.load(bundle_path)
        if bundle.get("local_freeze_sha256") != lock["local_freeze_sha256"]:
            raise ValueError("saved model does not match local freeze")
        frozen = "local-sha256:" + lock["local_freeze_sha256"]
    else:
        bundle = joblib.load(bundle_path)
        frozen = subprocess.check_output(
            ["git", "rev-parse", "protocol-1.3-frozen^{commit}"], cwd=ROOT, text=True).strip()
        if bundle["frozen_commit"] != frozen or lock["frozen_commit"] != frozen:
            raise ValueError("saved model/lock do not match the frozen tag")
    train, test, columns = development_frames("test")
    _, validation, _ = development_frames("validation")
    if list(columns) != bundle["columns"] or not np.array_equal(test["source_row_id"], bundle["source_row_ids"]):
        raise ValueError("saved test rows/features do not match")
    probability = bundle["probabilities"]
    flags, _ = capacity_predictions(probability)
    positions = select_forward_simulation_positions(probability)
    chosen = sorted(positions, key=lambda p: int(test.iloc[p]["source_row_id"]))
    practice = validation.iloc[[0]].copy()
    cases = [("PR", practice.iloc[0], None)] + [
        (f"C{i:02d}", test.iloc[pos], int(flags[pos])) for i, pos in enumerate(chosen, 1)]
    with open(ROOT / "eda_uci_data" / "data" / "dropout_data.csv", newline="", encoding="utf-8") as f:
        raw = [{k.strip(): v.strip() for k, v in r.items()} for r in csv.DictReader(f)]
    protocol = load_protocol()
    bg = prepare_tfm_frame(train, columns).sample(n=25, random_state=42)
    labels = cp.bar_labels()
    profiles = cp.profile_field_labels()
    pack_cases, lookup = [], {}
    for cid, row, flag in cases:
        frame = prepare_tfm_frame(row.to_frame().T, columns)
        explanation = permutation_shap_values(
            bundle["model"].predict_proba, bg, frame, max_evals=protocol["shap"]["max_evals"], seed=42)
        groups = aggregate_shap_by_group(explanation.values[0], columns, semantic_feature_groups(columns)).head(5)
        contributions = [
            {"bar_id": r.feature_group, "label": labels[r.feature_group], "value": float(r.signed_shap)}
            for r in groups.itertuples()]
        source_id = int(row["source_row_id"])
        pack_cases.append({
            "case_id": cid, "role": "practice" if cid == "PR" else "scored",
            "profile": [{"field": f, "value": raw[source_id][f]} for f in profiles],
            "chart_file": cp.chart_file(cid), "contributions": contributions,
        })
        if cid == "PR":
            # Practice is validation-only; its flag remains private and is never scored.
            vp = bundle["model"].predict_proba(prepare_tfm_frame(validation, columns))[:, 1]
            vf, _ = capacity_predictions(vp)
            flag = int(vf[0])
        lookup[cid] = {"source_row_id": source_id, "model_flag": flag}
    pack = {"contract_version": "1.0", "protocol_version": "1.3", "pack_kind": "study",
            "source": "Post-final-test, prediction-only balanced panel; validation-only practice",
            "model_ref": frozen, "contributions_placeholder": False, "cases": pack_cases}
    problems = cp.validate_pack(pack) + cp.validate_private(lookup, "study")
    if not problems:
        problems += cp.validate_provenance(pack, lookup)
    if problems:
        raise ValueError("; ".join(problems))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if any((out / name).exists() for name in ("case_pack_study.json", "private_lookup_study.json")):
        raise FileExistsError("study export exists; do not silently replace released cases")
    for name, value in (("case_pack_study.json", pack), ("private_lookup_study.json", lookup)):
        with (out / name).open("x", encoding="utf-8") as f:
            json.dump(value, f, indent=2)
    print("PASS: restricted study pack and private lookup exported; do not commit or show lookup.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
