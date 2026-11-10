"""Reproduce the validation-only result for the selected TabICL model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.modeling import run_tfm_validation  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        choices=("tabicl",),
        default="tabicl",
        help="Frozen TFM choice; retained as an explicit audit field.",
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=4,
        help="Small feasibility ensemble; record any later change before final fitting.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(
        run_tfm_validation(
            candidates=(args.model,), n_estimators=args.n_estimators
        ).to_string(index=False)
    )
