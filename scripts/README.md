# Scripts index

Run every script from the repository root with the core environment, for example
`.venv-core/Scripts/python.exe scripts/run_validation.py` (Windows) or
`.venv-core/bin/python scripts/run_validation.py`. No script reruns the locked final test:
`run_final_test.py` refuses once `artifacts/final_test.lock` exists.

**One command for everything:** `python scripts/reproduce_results.py` runs the tests, form checks,
TA-feedback numbers and EDA profile without fitting models; add `--validation-results` to also
regenerate the validation-only model results listed below (slower, fits models).

## 1. Data, models and the final test

| Script | Purpose |
|---|---|
| `run_core.py` | Validation-only baseline metrics (logistic regression, tree, XGBoost, EBM) |
| `run_tfm_feasibility.py` | Validation-only TabICL result |
| `run_validation.py` | All current validation-only core results in one command |
| `run_final_test.py` | Validation dry run, or the once-only locked final test (already done; refuses to rerun) |
| `build_eda_profile.py` | Training-split profile by outcome (report Table 3) |

## 2. Explanations and audits (validation only)

| Script | Purpose |
|---|---|
| `validate_explanation_pipeline.py` | SHAP integration checks (additivity, white-box recovery) |
| `run_validation_audits.py` | Global explanations (permutation importance, ALE) and fairness/proxy tables |
| `run_explanation_audit.py` | Explanation smoke check (the full 544-case audit lives in `W1_analysis/`) |
| `check_w1_refit_identity.py` | Confirms the W1 audit refit matches the frozen model |

## 3. Sensitivity analyses (validation only)

| Script | Purpose |
|---|---|
| `run_temporal_sensitivity.py` | Admission-time vs. after-first-semester feature windows |
| `run_enrolled_sensitivity.py` | How the model treats still-enrolled students |
| `run_no_protected_sensitivity.py` | Refit without the six protected attributes |
| `run_ta_feedback_checks.py` | TA questions: who is flagged, bar sums, eligibility re-ranking (no model run) |

## 4. Human study

| Script | Purpose |
|---|---|
| `export_study_cases.py` | Exports the restricted study cases from the saved final model |
| `make_assignment_list.py` | Seeded participant-to-form assignment list |
| `analyze_human_study.py` | Scores private response exports (output stays private) |
| `audit_human_study_privacy.py` | Scans private responses for identifier patterns; reports counts only |
| `assign_human_coding.py` | Blinded qualitative-coding assignments and agreement tooling |
| `build_human_study_report.py` | Privacy-safe aggregate tables and figures |

The Google Forms tooling is in `forms/` (see `forms/README.md`).

## 5. Report assets and verification

| Script | Purpose |
|---|---|
| `build_report_assets.py` | Regenerates aggregate report tables and figures without model inference |
| `build_demo_card.py` | Static adviser card for one validation student (report Figure 4) |
| `verify_release_readiness.py` | Checks saved evidence and report numbers without fitting models |
| `reproduce_results.py` | Runs the checks above in order (see top) |

## 6. Local research interface

| Script | Purpose |
|---|---|
| `launch_interface.py` | Builds and opens the interface for validation students; `--what-if` enables re-scoring |
| `whatif_server.py` | Local server used by `launch_interface.py --what-if` |

## Other

| Script | Purpose |
|---|---|
| `inspect_proposal_docx.py` | Prints the proposal DOCX text for checking (not part of the pipeline) |
