"""W3.3: run checks and optionally regenerate validation-only results; never rerun the final test.

Default (fast, no model fitting): tests, form checks, fixture charts, W1 topic tables from the saved
544 cases (written to a temporary folder and compared byte-for-byte with the committed tables),
the TA-feedback checks from the same saved cases, the training-split EDA table, report assets, the local research interface page and the release-readiness check.

--validation-results (slow): additionally refits validation models and regenerates the validation
audits, the W1-refit identity check, the W5.1 demo card, the W3.7 Enrolled sensitivity and the
no-protected-attributes refit. All use
train/validation data only; run_final_test.py runs its validation dry run and the completed lock
blocks any repeat of the final test.

--human-study: additionally rebuilds the aggregate human-study tables from the private scored
files, if those restricted files are present on this machine.
"""
import argparse
import filecmp
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
W1_TOPICS = ROOT / "W1_analysis" / "03_Full_Audit" / "Code" / "topics"
HUMAN_PRIVATE = {
    "--scored": ROOT / "data" / "human_study" / "analysis" / "scored_study.csv",
    "--people": ROOT / "data" / "human_study" / "analysis" / "participants_study.csv",
    "--participants": ROOT / "data" / "human_study" / "analysis" / "responses_participants_study.csv",
    "--private": ROOT / "data" / "human_study" / "scoring_private" / "private_lookup_study.json",
}


def run(args_, cwd=ROOT):
    subprocess.run([sys.executable, *args_], cwd=cwd, check=True)


def check_w1_topics():
    """Regenerate W1 topic tables into a temp folder and require identical results."""
    with tempfile.TemporaryDirectory() as folder:
        run(["run_all.py", "--output-root", folder], cwd=W1_TOPICS)
        out = Path(folder)
        compared = 0
        for path in out.rglob("*"):
            if path.is_dir() or path.name == "analysis_provenance.json" or "_by_case" in path.name:
                continue
            committed = W1_TOPICS / path.relative_to(out)
            if not committed.is_file() or not filecmp.cmp(path, committed, shallow=False):
                raise SystemExit(f"W1 topic output differs from committed file: {committed}")
            compared += 1
    print(f"PASS: {compared} W1 topic outputs regenerated identically from saved cases")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--validation-results", action="store_true",
                        help="slow: refit validation models and regenerate validation-only evidence")
    parser.add_argument("--human-study", action="store_true",
                        help="rebuild aggregate human-study tables from restricted private inputs")
    args = parser.parse_args(argv)

    for step in (["forms/build_spec.py"],
                 ["-m", "unittest", "discover", "-s", "tests", "-v"],
                 ["forms/test_spec.py"],
                 ["forms/render_images.py", "forms/out/case_pack_fixture.json", "--profiles"]):
        run(step)
    check_w1_topics()
    run(["scripts/run_ta_feedback_checks.py"])
    run(["scripts/build_eda_profile.py"])

    if args.validation_results:
        for name in ("scripts/run_validation.py", "scripts/validate_explanation_pipeline.py",
                     "scripts/run_validation_audits.py", "scripts/run_temporal_sensitivity.py",
                     "scripts/run_explanation_audit.py", "scripts/run_final_test.py",
                     "scripts/check_w1_refit_identity.py", "scripts/build_demo_card.py",
                     "scripts/run_enrolled_sensitivity.py",
                     "scripts/run_no_protected_sensitivity.py"):
            run([name])

    if args.human_study:
        missing = [str(path.relative_to(ROOT)) for path in HUMAN_PRIVATE.values() if not path.is_file()]
        if missing:
            raise SystemExit("restricted human-study inputs not present: " + ", ".join(missing))
        run(["scripts/build_human_study_report.py",
             *[part for flag, path in HUMAN_PRIVATE.items() for part in (flag, str(path))]])

    run(["scripts/build_report_assets.py"])
    run(["scripts/launch_interface.py", "--no-open"])
    run(["scripts/verify_release_readiness.py"])
    print("PASS: checks complete. Final test was not opened or rerun.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
