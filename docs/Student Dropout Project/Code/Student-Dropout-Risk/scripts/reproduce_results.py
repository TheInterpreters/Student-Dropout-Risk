"""W3.3: run checks and optionally regenerate validation-only results; never rerun the final test."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation-results", action="store_true",
                        help="expensive: refit models and regenerate validation results and audit figures")
    args = parser.parse_args(argv)
    commands = [
        ["forms/build_spec.py"],
        ["-m", "unittest", "discover", "-s", "tests", "-v"],
        ["forms/test_spec.py"],
        ["forms/render_images.py", "forms/out/case_pack_fixture.json", "--profiles"],
    ]
    if args.validation_results:
        commands += [[name] for name in (
            "scripts/run_validation.py", "scripts/validate_explanation_pipeline.py",
            "scripts/run_validation_audits.py", "scripts/run_temporal_sensitivity.py",
            "scripts/run_explanation_audit.py", "scripts/run_final_test.py")]
    for args_ in commands:
        subprocess.run([sys.executable, *args_], cwd=ROOT, check=True)
    print("PASS: checks complete. Final test was not opened or rerun.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
