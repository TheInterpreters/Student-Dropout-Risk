"""Regenerate every current validation-only core result with one command."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.modeling import run_baseline_validation, run_tfm_validation  # noqa: E402


if __name__ == "__main__":
    print("Baselines (validation only)")
    print(run_baseline_validation().to_string(index=False))
    print("\nSelected TFM feasibility (validation only)")
    print(run_tfm_validation(candidates=("tabicl",), n_estimators=4).to_string(index=False))
