# LAYOUT — Where Noey should run, check, and review W1

**Read this first.** The ZIP contains ONE folder named `W1_Noey_Enhanced/`. Extract that folder directly into the existing `Student-Dropout-Risk` repository root. **Do not replace** the team's `src/`, `scripts/`, `config/`, `artifacts/`, `docs/HANDOFF.md`, `docs/TASK_SPLIT.md` or final-test lock.

## A. Exact target directory

```text
Student-Dropout-Risk/                         # existing team clone, NOT supplied in ZIP
├── .venv-core/                              # your already-installed Python 3.12 / TabICL environment
├── artifacts/
│   ├── final_test.lock                      # MUST REMAIN UNCHANGED
│   └── split_ids.csv                        # source train/validation/test assignments
├── config/evaluation_protocol.json          # frozen team protocol; do not edit
├── src/                                     # original code; do not edit
├── eda_uci_data/data/dropout_data.csv       # original 4,424-student CSV; not duplicated
├── eda_uci_data/eda_dropout.ipynb           # original EDA; not modified
├── docs/TASK_SPLIT.md                       # original; no automatic overwrite
└── W1_Noey_Enhanced/                        # NEW independent folder from this ZIP
    ├── LAYOUT.md                            # THIS FILE, output/verification guide
    ├── README.md                            # methods and interpretation
    ├── INSTALL_CHECKLIST.md                  # quick local setup checks
    ├── config/
    │   └── full_cohort_protocol.json        # records expansion from 20 to ALL 544 validation cases
    ├── scripts/
    │   ├── run_enhanced_audit.py             # MAIN 544-case SHAP/pair/stability/recourse + report
    │   ├── surrogate_comparison.py           # OLS/Ridge/Lasso x main/pairs
    │   ├── student_improvement_simulation.py # one-student REAL TabICL scenario example (optional)
    │   ├── validation_descriptive_audit.py   # observed outcome patterns in TRAIN & VALIDATION only
    │   └── install_tabicl_checkpoint.ps1     # OPTIONAL; skip if your TabICL already runs
    ├── tests/                                # synthetic code tests, not empirical model findings
    ├── docs/
    │   ├── HANDOFF_TO_YOLANDA.md             # new review handoff; does not replace hers
    │   ├── FINDINGS_TEMPLATE.md              # report structure: fill with real outputs only
    │   ├── TASK_SPLIT_PROPOSED.md            # full proposed team task-file update
    │   ├── TASK_SPLIT_W1_ENHANCEMENT.patch   # reviewable changes to team task file
    │   ├── NUMERICAL_SIMULATION_EXPLAINED.md
    │   └── TABICL_CHECKPOINT_INSTALL.md
    └── outputs/                              # initially empty except README; generated on YOUR PC
        └── README.md
```

## B. Run in this order — copy/paste into VS Code PowerShell at repository root

```powershell
# 1. Confirm the existing interpreter and checkpoint works
.\.venv-core\Scripts\python.exe -c "import tabicl, shap, sklearn; print('Imports OK')"

# 2. Test supplementary audit code (NO genuine model run)
.\.venv-core\Scripts\python.exe -m unittest discover -s W1_Noey_Enhanced\tests -v

# 3. Preflight check: frozen files + lock + expected full-cohort configuration
.\.venv-core\Scripts\python.exe W1_Noey_Enhanced\scripts\run_enhanced_audit.py --check

# 4. Actual observed data patterns; no fitting or test-label use
.\.venv-core\Scripts\python.exe W1_Noey_Enhanced\scripts\validation_descriptive_audit.py --run

# 5. Recommended first REAL TabICL batch: just one case; report not yet complete
.\.venv-core\Scripts\python.exe W1_Noey_Enhanced\scripts\run_enhanced_audit.py --run --max-new-cases 1

# 6. Continue in batches of five or run all remaining cases with no --max-new-cases
.\.venv-core\Scripts\python.exe W1_Noey_Enhanced\scripts\run_enhanced_audit.py --run --max-new-cases 5

# 7. Repeat step 6 until 544/544 case files; then compile genuine report
.\.venv-core\Scripts\python.exe W1_Noey_Enhanced\scripts\run_enhanced_audit.py --report
```

`--run` fits the specified original TabICL **on training only**, scores validation, and resumes from complete case JSON files only when all input/lock/model-probability checks match. Each batch refits training-only TabICL once. The 544-case experiment is very compute-intensive: 10 SHAP seeds + 10 backgrounds + up to 10 perturbation SHAP explanations per student, plus deletion/pairs/surrogates. Depending on CPU and checkpoint, the full job may require many hours or longer. **Do not close a running batch expecting work to continue in the background.** An interrupted run resumes only after you run the command again.

If you have no results yet, `--report` **should fail** rather than invent findings. For a *clearly labeled incomplete preview* after at least one case, use `--report-partial`. Do not show partial figures as complete W1 results.

## C. After running: Which files do I check?

| Priority | Generated file (inside `W1_Noey_Enhanced/outputs/`) | Your manual check | What a valid result would look like |
|---|---|---|---|
| **1** | `cases/manifest.json` | `split=validation`, `selected_source_row_ids` length **544**, `test_evaluated=false`, lock hash present | No IDs lost/duplicated; saved probability SHA consistent across batches |
| **2** | `cases/case_*.json` | Exactly **544 files** when finished. Open several examples including flagged and unflagged | Each case has local signed SHAP, top five, 10 pairs, faithfulness, stability, six surrogates and hypothetical scenarios |
| **3** | `tables/summary.json` | `n_cases=544`, `full_audit_completed=true`, `test_evaluated=false` | If false or absent, the full audit is **not complete** |
| **4** | `tables/w1_local_shap_summary_validation.csv` | Mean absolute signed-group contributions and top-five frequency | Which groups commonly influence predictions; *not* action effectiveness |
| **5** | `tables/w1_local_shap_by_case_validation.csv` | Positive/negative SHAP sign for individual cases | Check signs against raw student values; compare selected risk cases |
| **6** | `tables/faithfulness_summary` **is in** `tables/summary.json` + `tables/faithfulness_validation.csv` | Positive/negative area and case-level 95% bootstrap interval | Ranked-vs-random reference-masking reliance, not causal faithfulness |
| **7** | `tables/stability_validation.csv` | Separate seed, background, perturbation results; >=2 valid perturbations | Cases below overlap 0.80 flagged for caution, not automatic universal failure |
| **8** | `tables/pairwise_reference_masking_summary_validation.csv` | Top feature-group **pairs**, effect magnitude and number of students where each pair appears | Strong pair nonadditivity is a model masking response, not SHAP interaction or cause |
| **9** | `tables/surrogate_six_variants_overall_validation.csv` | Compare **OLS / Ridge / Lasso** × **main-only / main+pairs**; holdout MAE | Lower MAE mimics TabICL on unseen mask patterns better; consider simplicity and out-of-range predictions too |
| **10** | `tables/individual_and_combined_improvement_scenarios_validation.csv` | Original and scenario probability, change in **percentage points**, flag and cohort rank | Academic grade/approved units = **historical sensitivity only**; debt/tuition = hypothetical administrative change |
| **11** | `tables/recourse_all_scenarios_validation.csv` and `tables/recourse_validation.csv` | Flagged students with a tested successful status combination; no-change cases | Never call a no-recourse result “no support available” |
| **12** | `figures/*.png` | Review all five plots; cross-check numbers with tables | Genuine charts only after sufficient case data |
| **13** | `tables/W1_COMPLETE_REPORT.md` | Confirm all claims against `summary.json`; supply to Yolanda | Only generated after **544/544** successfully audited; reviewer sign-off still pending |

**Separate descriptive files:** `outputs/observed_validation/actual_training_subgroups.csv`, `actual_validation_subgroups.csv` and `provenance.json`. They describe observed outcomes and do **not** represent SHAP or TabICL probabilities.

**Optional single-student figures:** `outputs/improvement_scenarios/<source_row_id>/` when executing `student_improvement_simulation.py --run`. Do not confuse the `--demo` invented logistic percentages with genuine TabICL.

## D. Noey's final audit acceptance checklist

- [ ] Correct repository and Python 3.12 TabICL version/checkpoint verified
- [ ] No modifications to team's `artifacts/final_test.lock` or held-out final results
- [ ] `python -m unittest ...` passes (synthetic tests only)
- [ ] `--check` passes, no source/protocol hash drift
- [ ] `observed_validation` outputs generated using **training + validation** only
- [ ] Exactly **544 distinct source-row cases** successfully saved
- [ ] No truncated, missing, nonfinite SHAP or model probabilities
- [ ] Local and global feature importance clearly separated
- [ ] Pairs reported as *reference-masking nonadditivity*, never causal interactions
- [ ] Stability results include seed/background/accepted perturbations + failures
- [ ] All **six** surrogate variants compared with same held-out mask patterns, Ridge/Lasso tuned only on training masks
- [ ] Counterfactual scenarios for **all flagged validation students** reviewed for feasibility
- [ ] Grade improvements disclosed as *retrospective simulations*, not interventions available after first semester
- [ ] `summary.json`: `n_cases == 544` and `full_audit_completed == true`
- [ ] Generated report and charts match output CSV/JSON
- [ ] Independent reviewer (Yolanda or another agreed member) signs off; no retroactive claim that 2 Nov full audit was passed
- [ ] Updated `docs/TASK_SPLIT.md` proposed text/patch reviewed before merging

## E. If you get an error

- `ModuleNotFoundError: tabicl`: VS Code is using a different Python interpreter; call `.venv-core\Scripts\python.exe` explicitly.
- `Missing required files`: extracted `W1_Noey_Enhanced/` into the wrong directory; it must be directly under the team repository root.
- `Final-test lock changed`: STOP; preserve the current evidence, ask Yolanda to reconcile. **Never delete the lock or rerun final_test.py**.
- `Repo inputs/script changed since earlier audit`: STOP; the saved cases belong to an older code/data version. Archive results under a different project snapshot; never blend incompatible batches.
- `Validation probabilities differ on resume`: STOP; confirm checkpoint and environment identity with Yolanda. The result may be nondeterministic or the wrong model; do not silently mix cases.
- `Only 1/544 cases saved`: expected after a small `--max-new-cases` run. Continue with `--run`.
- Lasso convergence warning during synthetic testing: investigate if persistent in real runs; inspect relative MAE and convergence rather than treating unstable coefficients as strong evidence.
- No eligible perturbations: report **insufficient stability evidence**, not a pass.

## F. Handoff

Send `docs/HANDOFF_TO_YOLANDA.md` plus **aggregate outputs**, `summary.json`, figures and run/verification record for review. Case-level JSON and any private model/checkpoint files must remain in restricted storage. If the audit finds weak explanations, revise interpretation and support advice—**do not rerun the completed locked final-test evaluation** without an independently documented fundamental-methodology issue and team authorization.
