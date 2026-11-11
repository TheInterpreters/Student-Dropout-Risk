# Student Dropout Project — W1_analysis

This guide locates the main W1 analysis and its supporting documents.

The completed audit covers **544 validation students**. Training data supplies model context; the locked final test is excluded.

## Start here: W1_analysis

| File | Purpose |
| --- | --- |
| [W1_Topic_Analysis.ipynb](04_View_Results/W1_Topic_Analysis.ipynb) | Main executed notebook: feature contributions, changed predictions, single-versus-pair comparisons, robustness and human support |
| [W1_Topic_Analysis.html](04_View_Results/W1_Topic_Analysis.html) | Browser-readable version; download and open locally |
| [W1_SUMMARY.md](03_Full_Audit/Code/topics/W1_SUMMARY.md) | Short findings, selected explanatory groups/pairs and limitations |
| [Topic code and navigation](03_Full_Audit/Code/topics/README.md) | Guide to the analysis code and generated results |

### Recommended reading order

1. Understand each feature and its signed contribution.
2. Inspect predicted probabilities before and after recorded feature changes.
3. Compare single features with paired explanations.
4. Review explanation stability and the selected explanatory panel.
5. Consider practical support actions after confirming the student's needs.

### Code and results by topic

All topic folders are inside:

`03_Full_Audit/Code/topics/`

Each topic keeps its `analysis.py`, `README.md` and `results/` together.

| Topic folder | Analysis | Main result files |
| --- | --- | --- |
| `w1_1_local_explanations/` | Feature definitions and contribution strength/direction | `all_33_feature_definitions.csv`, `feature_importance.csv`, `selected_case_contributions.png` |
| `w1_2_single_vs_pairs/` | Single/joint masking responses and six local surrogates | `single_vs_pair_summary.csv`, `matched_main_vs_pairs.csv`, `six_variants.csv`, `main_vs_pairs.png` |
| `w1_3_robustness/` | Sensitivity to explanation seeds, backgrounds and accepted perturbations | `stability_summary.csv`, `conditional_feature_retention.csv`, `selected_feature_retention.png` |
| `w1_4_human_support/` | Recorded feature-change results and proposed retention support | `recorded_scenario_summary.csv`, `support_catalogue.csv`, `future_retention_follow_up_template.csv`, `selected_case_scenarios.png` |
| `w1_5_feature_selection/` | Provisional explanatory groups and pairs | `selected_explanatory_panel.json`, `selected_main_groups.csv`, `selected_pairs.csv`, `selected_group_stability.csv` |

Additional code:

- `w1_4_human_support/scenarios.py`: validates saved scenarios and provides optional prediction-only feature edits.
- `run_all.py`: generates all topic tables from completed cases.
- `common.py`: loads and validates saved evidence.
- `policy.json`: reporting and selection settings.
- `analysis_provenance.json`: records the source evidence and analysis scope.

### Interpretation

- Positive signed SHAP raises the student's predicted probability relative to the explanation background; negative SHAP lowers it.
- The saved explanations contain **27 groups covering 33 inputs**. Individual member contributions were not retained for the two multi-input academic groups.
- Feature-change scenarios describe model responses. They do not establish actual dropout prevention.
- Historical grade changes are retrospective sensitivity tests.
- Human support should address confirmed barriers and monitor future enrollment and progress.
- Selected explanatory groups/pairs do not change TabICL's original inputs.

## Supporting documents

| Supporting material | Location |
| --- | --- |
| Complete audit overview — executed notebook | [Read_Completed_Audit.ipynb](04_View_Results/Read_Completed_Audit.ipynb) |
| Complete audit overview — HTML | [Read_Completed_Audit.html](04_View_Results/Read_Completed_Audit.html) |
| Complete computational report | [W1_COMPLETE_REPORT.md](03_Full_Audit/Reports/W1_COMPLETE_REPORT.md) |
| Topic analysis code | [topics/](03_Full_Audit/Code/topics/) |
| Audit setup and methodology documentation | [Full audit README](03_Full_Audit/README.md) |
| Execution and integrity evidence | [Provenance README](05_Provenance/README.md) |
| Earlier actual-data reports | [Data audit](01_Data_Audit/Reports/) and [model evaluation](02_Model_Evaluation/Reports/) |

Earlier dated reports describe the status when they were written. Use the completed audit package and W1 analysis for the latest completed evidence.

### Locate every file in this checked-out audit

| Package folder/file | Contents |
| --- | --- |
| `01_Data_Audit/` | Data-check code and reports |
| `02_Model_Evaluation/` | Model evaluation code and reports |
| `03_Full_Audit/Code/topics/` | W1 topic code and derived results |
| `03_Full_Audit/Cases/` | All 544 completed student-case records |
| `03_Full_Audit/Reports/` | Original full-audit report |
| `03_Full_Audit/Tables/` | Original and derived audit tables |
| `03_Full_Audit/Figures/` | Audit figures |
| `04_View_Results/` | Executed notebooks and HTML reports |
| `05_Provenance/` | Execution logs, manifests and verification evidence |

The checked-out tree contains all 544 case records, aggregate tables, figures, notebooks, and
execution-integrity records. Reading the saved outputs requires no model training or full audit rerun.

## Which model this audit explains (read before citing numbers)

The W1 audit did **not** load the frozen final model (`data/final_evaluation/selected_model.joblib`,
bound to `artifacts/final_test.lock`). It **refitted** TabICL on the same 2,541 training rows with
the frozen settings and the same checkpoint (`Reports/summary.json`:
`original_saved_fitted_model_loaded: false`). Consequences for the report:

- **Checked 11 Nov: the refit reproduces the frozen model on validation.** On all 544 validation
  students the largest probability difference is 0.00001 (mean 0.0000009), and all 108
  20%-capacity flags are identical (`python scripts/check_w1_refit_identity.py` →
  `artifacts/w1_refit_identity.json`; also enforced by `scripts/verify_release_readiness.py`).
  W1's results can therefore be read as describing the frozen model's validation behaviour. The
  report should still say a refit was used and that the audit ran after the final test.
- SHAP values depend on random seeds and the background sample, so the human-study charts and the
  W5.1 demo card (computed separately from the frozen bundle) can still differ slightly from W1's
  bars for the same student.
- W1 used validation rows only; the test split was not evaluated (`test_evaluated: false`).

## What can be rerun from this checkout

| Code | Rerunnable here? | Notes |
| --- | --- | --- |
| `03_Full_Audit/Code/topics/run_all.py` | **Yes** (seconds; no model or SHAP) | Finds `03_Full_Audit/Cases/` automatically. Verified 11 Nov: every topic CSV, `selected_explanatory_panel.json` and `W1_SUMMARY.md` regenerate byte-identically; only `analysis_provenance.json` changes its `source_cases` path. Use `--output-root <tmp>` to compare without overwriting. |
| `03_Full_Audit/Code/run_enhanced_audit.py`, `student_improvement_simulation.py`, `surrogate_comparison.py` | **No, archived** | Hours of TabICL/SHAP compute; they expect the original `W1_Noey_Enhanced/` folder layout at the repo root. Their outputs are preserved in `Cases/`, `Tables/`, `Figures/` and `05_Provenance/`. |
| `01_Data_Audit/Code/*.py`, `02_Model_Evaluation/Code/actual_data_audit.py` | **No, archived** | Same `W1_Noey_Enhanced/` layout; outputs preserved in each `Reports/` folder. |
| `02_Model_Evaluation/Code/modeling.py`, `evaluation.py`, `03_Full_Audit/Code/explanations.py` | Snapshot copies | Byte-identical to `src/modeling.py`, `src/evaluation.py`, `src/explanations.py` as of 11 Nov. `src/` is canonical; do not edit these copies. |

```powershell
cd W1_analysis/03_Full_Audit/Code/topics
..\..\..\..\.venv-core\Scripts\python.exe run_all.py --output-root $env:TEMP\w1_check
```
