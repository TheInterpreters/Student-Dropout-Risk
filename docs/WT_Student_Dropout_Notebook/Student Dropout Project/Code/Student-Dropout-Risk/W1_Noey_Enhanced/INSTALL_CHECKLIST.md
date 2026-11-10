# Noey enhanced W1 — installation / review checklist

No GitHub main changes were made: GitHub branch creation failed with HTTP 403 (integration cannot create refs). This ZIP is a **local** package, not a repository commit.

1. Place `W1_Noey_Enhanced/` under the team repository root. Original Yolanda files stay unchanged.
2. Review the new full 544-validation-student analysis methods, tests, original EDA, and code with a different reviewer.
3. If agreed, replace repo `docs/TASK_SPLIT.md` with `W1_Noey_Enhanced/docs/TASK_SPLIT_PROPOSED.md`, or apply `TASK_SPLIT_W1_ENHANCEMENT.patch`. **Do not mistake this proposed copy for a committed change.**
4. In pinned Python 3.12 env: `python -m unittest discover -s W1_Noey_Enhanced/tests -v`; `python W1_Noey_Enhanced/scripts/run_enhanced_audit.py --check`; `--run`; then `--report`.
5. Review all 544 validation cases and aggregate outputs; fill `docs/FINDINGS_TEMPLATE.md` only with genuine results; send `docs/HANDOFF_TO_YOLANDA.md` with aggregate tables.
6. Preserve `artifacts/final_test.lock` and all earlier final-test/model/split artifacts; never rerun the final test for explanation weakness alone.

The raw CSV was inspected via GitHub and includes 4,424 records. The EDA notebook URL is known; full notebook output was not independently ingested. Real full-audit model computations were **not executed here**. Synthetic unit tests do not replace that evidence.
