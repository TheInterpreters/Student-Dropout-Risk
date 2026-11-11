# Student Dropout Project — W1_analysis

This guide locates the main W1 analysis and its supporting documents.

The completed audit covers **544 validation students**. Training data supplies model context; the locked final test is excluded.

## Start here: W1_analysis

| File | Purpose |
| --- | --- |
| [W1_Topic_Analysis.ipynb](Reports/Full_Audit/W1_Topic_Analysis.ipynb) | Main executed notebook: feature contributions, changed predictions, single-versus-pair comparisons, robustness and human support |
| [W1_Topic_Analysis.html](Reports/Full_Audit/W1_Topic_Analysis.html) | Browser-readable version; download and open locally |
| [W1_SUMMARY.md](Code/Student-Dropout-Risk/W1_Noey_Enhanced/topics/W1_SUMMARY.md) | Short findings, selected explanatory groups/pairs and limitations |
| [Topic code and navigation](Code/Student-Dropout-Risk/W1_Noey_Enhanced/topics/README.md) | Guide to the analysis code and generated results |

### Recommended reading order

1. Understand each feature and its signed contribution.
2. Inspect predicted probabilities before and after recorded feature changes.
3. Compare single features with paired explanations.
4. Review explanation stability and the selected explanatory panel.
5. Consider practical support actions after confirming the student's needs.

### Code and results by topic

All topic folders are inside:

`Code/Student-Dropout-Risk/W1_Noey_Enhanced/topics/`

Each topic keeps its `analysis.py`, `README.md` and `results/` together.

| Topic folder | Analysis | Main result files |
| --- | --- | --- |
| `w1_1_local_explanations/` | Feature definitions and contribution strength/direction | `all_33_feature_definitions.csv`, `feature_importance.csv`, `selected_case_contributions.png` |
| `w1_2_single_vs_pairs/` | Single/joint masking responses and six local surrogates | `single_vs_pair_summary.csv`, `matched_main_vs_pairs.csv`, `six_variants.csv`, `main_vs_pairs.png` |
| `w1_3_robustness/` | Sensitivity to explanation seeds, backgrounds and accepted perturbations | `stability_summary.csv`, `conditional_feature_retention.csv`, `selected_feature_retention.png` |
| `w1_4_human_support/` | Recorded feature-change results and proposed retention support | `recorded_scenario_summary.csv`, `support_catalogue.csv`, `future_retention_follow_up_template.csv`, `selected_case_scenarios.png` |
| `w1_5_feature_selection/` | Provisional explanatory groups and pairs | `selected_explanatory_panel.json`, `selected_main_groups.csv`, `selected_pairs.csv`, `selected_group_stability.csv` |

Additional code:

- `w1_1_local_explanations/feature_guide.py`: defines all 33 inputs and explains a selected student's signed contributions.
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
| Complete audit overview — executed notebook | [Read_Completed_Audit.ipynb](Reports/Full_Audit/Read_Completed_Audit.ipynb) |
| Complete audit overview — HTML | [Read_Completed_Audit.html](Reports/Full_Audit/Read_Completed_Audit.html) |
| Complete downloadable evidence package | [Student_Dropout_Full_Audit.zip](Downloads/Student_Dropout_Full_Audit.zip) |
| ZIP contents and extraction guide | [Student_Dropout_Full_Audit_Contents.md](Downloads/Student_Dropout_Full_Audit_Contents.md) |
| Original project source, model code and audit scripts | [Code/Student-Dropout-Risk/](Code/Student-Dropout-Risk/) |
| Audit setup and methodology documentation | [W1_Noey_Enhanced/](Code/Student-Dropout-Risk/W1_Noey_Enhanced/) |
| Verification tests | [W1_Noey_Enhanced/tests/](Code/Student-Dropout-Risk/W1_Noey_Enhanced/tests/) |
| Earlier actual-data reports and progress snapshots | [Reports/Actual Validation/](Reports/Actual%20Validation/) |
| Local input requirements | [LOCAL_DATA_REQUIREMENTS.md](LOCAL_DATA_REQUIREMENTS.md) |

Earlier dated reports describe the status when they were written. Use the completed audit package and W1 analysis for the latest completed evidence.

### Locate every file in the full package

After extracting the ZIP, open `Student_Dropout_Full_Audit/`.

| Package folder/file | Contents |
| --- | --- |
| `START_HERE.md` | Package navigation |
| `01_Data_Audit/` | Data-check code and reports |
| `02_Model_Evaluation/` | Model evaluation code and reports |
| `03_Full_Audit/Code/topics/` | W1 topic code and derived results |
| `03_Full_Audit/Cases/` | All 544 completed student-case records |
| `03_Full_Audit/Reports/` | Original full-audit report |
| `03_Full_Audit/Tables/` | Original and derived audit tables |
| `03_Full_Audit/Figures/` | Audit figures |
| `04_View_Results/` | Executed notebooks and HTML reports |
| `05_Provenance/` | Execution logs, manifests and verification evidence |
| `06_Reproduce/` | Preserved original notebook and reproduction source |
| `FILE_INDEX.csv` | Complete file-by-file location index |
| `PACKAGE_MANIFEST.json` | File hashes and package metadata |
| `VERIFY_PACKAGE.py` | Package integrity verification |

To rerun the W1 results notebook, extract the complete ZIP so the code and saved case inputs are available. Reading its saved outputs requires no model training or full audit rerun.
