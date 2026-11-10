# Noey → Yolanda: independent full-cohort W1 evidence handoff

**Prepared 4 November 2026; status = code and synthetic verification complete, genuine 544-case TabICL audit not yet run.** This is a *new supplementary* validation exercise; it does **not** rewrite Yolanda's 2 November work or retroactively satisfy an omitted audit gate.

## Why the enhanced work exists

The earlier one-case/two-seed execution check could not establish explanation faithfulness, stability, important feature combinations, or actionable model recourse. This independent investigation now targets **all 544 validation students** rather than 20, adds local SHAP + group/pair effects, checks robustness, compares six post-hoc OLS/Ridge/Lasso surrogate variants, and simulates individual/combined academic-financial input changes.

The raw dataset remains the original UCI CSV, with **4,424** raw rows, **3,630** Dropout/Graduate binary rows (**2,541 train, 544 validation, 545 locked final test**). The final 545-case test must never be opened or rerun as part of W1.

## Repository isolation and files

All new code, configuration and evidence belong under **`W1_Noey_Enhanced/`** only. The existing `src/`, `scripts/run_explanation_audit.py`, `config/evaluation_protocol.json`, `docs/HANDOFF.md`, `artifacts/final_test.lock` and original final-test tables are read-only. The proposed change to team `docs/TASK_SPLIT.md` is supplied in `docs/TASK_SPLIT_PROPOSED.md` and `docs/TASK_SPLIT_W1_ENHANCEMENT.patch`; it is **not already applied or merged**.

See `../LAYOUT.md` for full directory tree, commands and acceptance checks. User's TabICL environment/checkpoint is already installed according to the user's report; verify exact model/inputs on the run machine.

## Run and review (Windows / cloned project)

```powershell
.\.venv-core\Scripts\python.exe -m unittest discover -s W1_Noey_Enhanced\tests -v
.\.venv-core\Scripts\python.exe W1_Noey_Enhanced\scripts\run_enhanced_audit.py --check
.\.venv-core\Scripts\python.exe W1_Noey_Enhanced\scripts\validation_descriptive_audit.py --run
.\.venv-core\Scripts\python.exe W1_Noey_Enhanced\scripts\run_enhanced_audit.py --run --max-new-cases 1
# Review first case, then continue the complete 544 validation rows
.\.venv-core\Scripts\python.exe W1_Noey_Enhanced\scripts\run_enhanced_audit.py --run
.\.venv-core\Scripts\python.exe W1_Noey_Enhanced\scripts\run_enhanced_audit.py --report
```

The `--run` command saves cases individually; if stopped, re-run the same command and it verifies data/script/lock and validation probability hashes before skipping already completed cases. Because each resumed run must reconstruct training-only TabICL, hundreds of 1-case batches are inefficient. The full 544-case SHAP calculation may be computationally extensive. **Do not treat a partial run as a completed audit**.

## What to verify with Noey after execution

| Aspect | Evidence to check | Acceptance criterion |
|---|---|---|
| Population and leakage | `outputs/cases/manifest.json` | 544 distinct validation IDs; original train/validation mapping; no held-out test; final lock unchanged |
| W1.1 Local SHAP | 544 case JSONs and `tables/w1_local_shap_by_case_validation.csv` | Finite SHAP, proper signed semantic groups, clear positive/negative contributions; no 20-case sample substitution |
| W1.2 Influence/faithfulness | `tables/w1_local_shap_summary_validation.csv`, `faithfulness_validation.csv`, `summary.json` | Do not conflate average SHAP with global permutation importance; interpret ranked-minus-random masking area and uncertainty |
| W1.2 Pairs | `tables/pairwise_reference_masking_summary_validation.csv` | 10 tested pairs per student; signed/magnitude effect; reported as reference-masking nonadditivity **not SHAP interaction values** |
| W1.2 Surrogates | `tables/surrogate_six_variants_overall_validation.csv` | OLS, Ridge, Lasso × main/pairs (6); 24 training/8 withheld mask patterns per student; Ridge/Lasso CV training-only; consider MAE, sparsity and out-of-range forecasts |
| W1.3 Stability | `tables/stability_validation.csv` and `pair_rank_stability_validation.csv` | 10 seeds, 10 backgrounds, up to 10 accepted grade perturbations; report insufficiency separately from failures; 0.80 warning only |
| W1.4 Recourse | `tables/recourse_all_scenarios_validation.csv` | Every *flagged validation student* represented, including no change/no recourse; 20% capacity reranking with other scores fixed |
| W1.4 Simulations | `tables/individual_and_combined_improvement_scenarios_validation.csv` | Every validation student represented; original/new probability, Δ percentage points, flag/rank; grade/credit edits **retrospective sensitivity**; debt/tuition hypotheses require feasibility checking |
| W1.5 Conclusion | `tables/summary.json`, `tables/W1_COMPLETE_REPORT.md`, five figures | 544/544 complete and cross-verified; no causal, human benefit, intervention effect or fairness-certification claims |

Please independently review a sample of individual case JSONs against raw data and CSVs (e.g. one clearly flagged, one unflagged, one with overdue tuition and one with no allowable debt/tuition change), then record agreement/disagreement. **Reviewer acceptance is not claimed by generation or passing synthetic tests.**

## Final-test rerun decision

- Weak W1 explanations, unstable groups, large pair effects, low recourse success, or Ridge/Lasso outperforming OLS: **DO NOT RERUN final test.** These are explanation-layer findings and limitations; retain final predictive metrics and lock.
- Defect only in new W1 scripts: **fix W1 on a new run/version**, preserve original incomplete evidence, then re-audit validation; do not rerun the final test.
- Demonstrated defect in original frozen model identity, data leakage, split/evaluation scoring or final-test protocol: **escalate to team and reviewer with hashes and exact affected claims**; preserve original test results/lock. Any new evaluation requires a documented independent authorization and ideally fresh untouched data, not casual reuse of the locked test.

## Scientific interpretation

The comparison is explanatory, not causal: SHAP and grouped scores identify model dependence, masking pairs reveal nonadditivity under an artificial reference intervention, and six surrogate variants approximate frozen TabICL responses on withheld mask configurations. Post-first-semester grades and approved credits cannot be rewritten, so “improve grade to 12” can be an advising target but *not* a demonstrated model-supported recourse or causal dropout prevention effect. Real institutional support effectiveness and human understanding require longitudinal or human-study evidence beyond W1.

**Current preparation evidence:** 20 synthetic unit tests passed, and a separate end-to-end report-generator test with 544 **synthetic** records produced 17 CSV tables and five figures. These are implementation checks only. No actual 544-student TabICL audit output has been represented as completed in this package.
