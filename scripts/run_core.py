"""One-command core baseline workflow; does not touch the final test set."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.modeling import run_baseline_validation  # noqa: E402


if __name__ == "__main__":
    print(run_baseline_validation().to_string(index=False))
