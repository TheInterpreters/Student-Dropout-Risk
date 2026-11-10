# Find the project and inspect the restored checkpoint

Open `START_HERE.md` at the `Data-Science` repository root. The current code is in `Student Dropout Project/Code/Student-Dropout-Risk`.

**Restored checkpoint, 9 November: 1/544 explanation cases complete.** The previous process stopped when the environment was replaced; the files are preserved and it has not been restarted by this folder-navigation task. To resume later, run `--run --inference-cache` without a case cap, as documented below. Do not infer that an old process ID is still running in a new environment.

---

# 9 November continuation update

The real model comparison has now completed on all 544 validation rows using a refit and a verified checkpoint. The full 544-case explanation run has been started, without a case cap. Earlier 4 November blocker notes below are historical.

The current full-cohort runtime uses `--run --inference-cache`. This records a separate cache identity and verifies bounded numerical agreement with uncached outputs plus exact outreach-flag agreement. Do not resume a cached manifest using the uncached command or mix case outputs. Check whether the existing process is active before starting another. The environment must remain active for the current process to continue.

See `Reports/Actual Validation/FINDINGS_2026-11-09.md` at the grouped project root and the local `outputs/cases/progress.json` for a later count. The final-test lock remains excluded from this supplementary evaluation and unchanged.

---

# Continue the actual W1 audit

## Correct scope

The final clarification is **every one of the 544 held-out validation observations**.
The 3,085 development rows include 2,541 training observations; those are used only
for model fitting and training-based explanation references. Training rows must not
be counted as independent audit/evaluation cases. The 545 locked final-test rows
remain excluded. No final-test runner or proposed team-document patch is applied.

## Current evidence, 4 November 2026

- The original source repository was retrieved at commit
  `5cad40f531b9980f0250fb8e171632cdbdd39bdc`.
- The data-quality checks ran on all 544 actual validation observations and 33
  eligible first-semester model features: 213 Dropout, 331 Graduate.
- No nonfinite/missing model features, duplicate feature profiles, negative
  enrolled/approved counts, approved counts exceeding enrolled counts, or grades
  outside 0–20 were flagged. These are limited data checks, not a certification.
- Actual-versus-model scoring was attempted but the official checkpoint request
  failed with proxy HTTP 403. No predictive metrics or SHAP results are claimed.
- The private original fitted-model/freeze bundle is not included in the uploaded
  ZIP or source clone. The provided runner **refits** TabICL on the original saved
  training split using the recorded configuration. It does not load the original
  saved fitted model or establish identical predictions to that private bundle.
- The complete explanation audit remains **0/544 cases**. No full W1 findings or
  completed-audit conclusion should be written until genuine cases finish.

## What was added

`actual_data_audit.py` checks every actual validation row. `development_population.py`
checks exact original split membership and prevents training/test IDs from entering
validation. The main runner now supports `--compare`, saves actual outcomes beside
real model predictions, and checks/records checkpoint identity and package versions.
It continues to use all 544 cases for `--run` and to refuse incomplete full reports.

## Run in the original project root

Use Python 3.12 and the project's pinned `requirements.txt`. On the prepared cloud
machine the interpreter is `/workspace/.venvs/w1/bin/python`; on Windows use
`.\.venv-core\Scripts\python.exe` in place of `python` below.

```sh
python -m unittest discover -s W1_Noey_Enhanced/tests -v
python W1_Noey_Enhanced/scripts/actual_data_audit.py --run
python W1_Noey_Enhanced/scripts/run_enhanced_audit.py --check
python W1_Noey_Enhanced/scripts/run_enhanced_audit.py --compare
python W1_Noey_Enhanced/scripts/run_enhanced_audit.py --run --max-new-cases 1
# After checking that the genuine first case is valid, resume ALL remaining cases:
python W1_Noey_Enhanced/scripts/run_enhanced_audit.py --run
python W1_Noey_Enhanced/scripts/run_enhanced_audit.py --report
```

`--compare` reports ROC-AUC, Brier score, calibration error, balanced accuracy,
confusion matrix, capacity precision/recall and a row-by-row prediction/error table
for all 544 validation observations. Outreach flags follow the frozen top-20%
cohort rule, not a universal 0.5 threshold. Predictive performance is distinct from
SHAP/deletion/stability/surrogate fidelity and from causal benefit.

Use `--checkpoint /path/to/tabicl-classifier-v2-20260212.ckpt` on both model commands
to use an existing checkpoint. Otherwise the named official checkpoint is downloaded.
The runner enforces the expected SHA256 from the supplied package's installer and
does not disable verification or silently use a different checkpoint.

The single-case command is only an execution check. It cannot stand in for auditing
all observations. The remaining run can be costly; batch resumption preserves each
completed case and checks input, checkpoint, runtime and probability identities.

## Current external blocker

The cloud network policy currently blocks `huggingface.co`. Its domain addition was
saved to the environment configuration draft. Review and save that change in
environment settings, then publish the environment. Saving a draft alone does not
activate access. Official download redirects may identify additional required
hosts; allow only the destinations actually needed. Alternatively, use an existing
matching checkpoint in this environment.

For comparison against the **exact already-trained team model**, the original
private fitted-model/freeze artifact and its provenance are needed. A verified refit
must remain labelled as a refit. Do not copy that model into public Git history.

## Output locations

`outputs/actual_validation/ACTUAL_DATA_AUDIT.md` and its JSON/CSV files contain the
completed actual-data checks. After successful model scoring, the same directory
will contain `actual_vs_model_validation.csv`, `actual_vs_model_summary.json` and
`model_provenance.json`. `outputs/cases/` and `outputs/tables/` are reserved for
genuine explanation evidence; no synthetic case results were put there.

The supplied `TASK_SPLIT_PROPOSED.md` and handoff remain historical proposals;
they were not automatically applied, sent or approved.
