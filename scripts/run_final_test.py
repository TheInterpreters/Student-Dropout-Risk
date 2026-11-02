"""W3.2: validation dry-run or a gated, once-only frozen-model test evaluation."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.auditing import paired_bootstrap_model_differences
from src.evaluation import (
    development_frames, evaluate_frozen_models, fairness_outputs, load_protocol,
    reliability_table, save_reliability_figure,
)
from src.modeling import capacity_predictions

LOCK = ROOT / "artifacts" / "final_test.lock"
TAG = "protocol-1.3-frozen"


def verify_environment():
    if sys.version_info[:2] != (3, 12):
        raise ValueError("final test requires the documented Python 3.12 environment")
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        pin = line.split("#", 1)[0].strip()
        if "==" not in pin:
            continue
        package, version = pin.split("==", 1)
        actual = importlib.metadata.version(package)
        if actual != version:
            raise ValueError(f"{package}: installed {actual}, frozen requirement is {version}")


def acquire_lock(path, metadata):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        json.dump({"status": "started", **metadata}, f, indent=2)


def check_gate(approval_path):
    verify_environment()
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    if git("status", "--porcelain"):
        raise ValueError("final test requires a clean working tree")
    head = git("rev-parse", "HEAD")
    if git("rev-parse", TAG + "^{commit}") != head:
        raise ValueError("HEAD must be the frozen tag; check out the approved frozen revision")
    remote = git("ls-remote", "--tags", "origin", "refs/tags/" + TAG, "refs/tags/" + TAG + "^{}")
    if head not in {line.split()[0] for line in remote.splitlines()}:
        raise ValueError("frozen tag has not been pushed to origin")
    approval_path = Path(approval_path).resolve()
    relative = approval_path.relative_to(ROOT)
    git("ls-files", "--error-unmatch", str(relative))
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    required = ("validation_audit_passed", "form_acceptance_passed",
                "final_runner_dry_run_passed", "participant_plan_verified")
    if any(approval.get(key) is not True for key in required):
        raise ValueError("all four reviewed freeze gates must be explicitly true")
    if not approval.get("owner") or not approval.get("reviewer") or approval["owner"] == approval["reviewer"]:
        raise ValueError("gate approval requires a named owner and a different reviewer")
    digest = hashlib.sha256((ROOT / "config" / "evaluation_protocol.json").read_bytes()).hexdigest()
    if approval.get("protocol_sha256") != digest:
        raise ValueError("approval does not match the protocol SHA-256")
    return {"frozen_commit": head, "protocol_sha256": digest,
            "approval": str(relative), "started_at": datetime.now(timezone.utc).isoformat(),
            "command": sys.argv}


def execute(split, out, bootstrap_resamples=None):
    import joblib
    import numpy as np
    import pandas as pd
    protocol = load_protocol()
    train, evaluation, columns = development_frames(split)
    metrics, predictions, fitted = evaluate_frozen_models(train, evaluation, columns)
    out.mkdir(parents=True, exist_ok=True)
    metrics.insert(0, "split", split)
    metrics.to_csv(out / "metrics.csv", index=False)
    comparison = []
    for name in predictions:
        if name == "tabicl":
            continue
        result = paired_bootstrap_model_differences(
            evaluation["target"], predictions["tabicl"], predictions[name],
            resamples=bootstrap_resamples or protocol["final_test_inference"]["paired_bootstrap_resamples"],
            seed=protocol["final_test_inference"]["bootstrap_seed"])
        result.insert(0, "comparison", "tabicl minus " + name)
        comparison.append(result)
    pd.concat(comparison, ignore_index=True).to_csv(out / "paired_comparisons.csv", index=False)
    for name, probability in predictions.items():
        reliability = reliability_table(evaluation["target"], probability)
        reliability.to_csv(out / (name + "_reliability.csv"), index=False)
        save_reliability_figure(reliability, out / (name + "_reliability.png"))
        flags, _ = capacity_predictions(probability)
        subgroups, proxies = fairness_outputs(evaluation, probability, flags, columns)
        subgroups.to_csv(out / (name + "_subgroups.csv"), index=False)
        proxies.to_csv(out / (name + "_proxies.csv"), index=False)
    if split == "test":
        private_dir = ROOT / "data" / "final_evaluation"
        private_dir.mkdir(parents=True, exist_ok=True)
        # Preserve the fitted selected model for W3.9: no refit or test rerun is necessary.
        joblib.dump({"model": fitted["tabicl"], "columns": columns,
                     "source_row_ids": evaluation["source_row_id"].to_numpy(),
                     "probabilities": np.asarray(predictions["tabicl"]),
                     "frozen_commit": subprocess.check_output(
                         ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()},
                    private_dir / "selected_model.joblib")
    manifest = {
        "split": split, "protocol_sha256": hashlib.sha256(
            (ROOT / "config" / "evaluation_protocol.json").read_bytes()).hexdigest(),
        "files_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted(out.iterdir()) if p.is_file() and p.name != "manifest.json"},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"split": split, "evaluation_cases": len(evaluation), "models": list(predictions)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=["validation", "test"], default="validation")
    parser.add_argument("--approval", help="tracked freeze approval JSON; required for test")
    parser.add_argument("--confirm-final-test", action="store_true")
    args = parser.parse_args(argv)
    if args.split == "test":
        if not args.confirm_final_test or not args.approval:
            parser.error("test access needs --approval and --confirm-final-test; do not run before freeze")
        if LOCK.exists():
            raise FileExistsError("final-test lock exists; never rerun or clear without a recorded team decision")
        metadata = check_gate(args.approval)
        acquire_lock(LOCK, metadata)
        # Never clear the lock on failure: a partial run still used the test split.
        result = execute("test", ROOT / "tables" / "final_test")
        LOCK.write_text(json.dumps({**metadata, **result, "status": "completed"}, indent=2), encoding="utf-8")
        print("Final test complete. Commit artifacts/final_test.lock immediately; never rerun.")
    else:
        result = execute("validation", ROOT / "tables" / "final_test_dry_run")
        print("VALIDATION DRY RUN ONLY:", json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
