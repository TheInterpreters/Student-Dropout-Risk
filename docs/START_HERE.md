# Student Dropout Project — Completed full audit

**Status: 544/544 validation students audited.** The original cloud run finished on 11 November 2026 at about 08:00 Thailand time. No case computations were restarted for this package.

## Open the completed results

Open `04_View_Results/Read_Completed_Audit.html` in a browser, or open `04_View_Results/Read_Completed_Audit.ipynb` in Jupyter/VS Code. Both contain the saved full-cohort results and five figures. The viewer reads saved files and does not train a model, download weights or start an audit.

## Folders grouped by task

| Folder | Contents |
| --- | --- |
| `01_Data_Audit/` | Data-audit code beside data-quality reports and row/feature checks. |
| `02_Model_Evaluation/` | Model-comparison code beside actual-versus-model predictions, metrics and provenance. |
| `03_Full_Audit/` | Explanation-audit code, complete report, original 17 CSV tables, five figures and 544 case records. An additional derived CSV combines reversed pair orders. |
| `04_View_Results/` | Executed results-viewer notebook and standalone HTML. |
| `05_Provenance/` | Execution log, source/checkpoint manifests, completion checks and warning records. |
| `06_Reproduce/` | Your original uploaded notebook and the complete runnable source/input/result layout. |

Each task has a README with its code and report locations. The task `Code` folders are exact source exports for inspection. For executing audit code, use the intact project in `06_Reproduce`.

## Important distinctions

- All 544 validation students are included; 2,541 training rows supplied fitting/reference context. Final-test execution is outside this audit.
- Completion means all case computations and reports are saved. Background/seed SHAP instability and surrogate convergence warnings remain findings; read `03_Full_Audit/Reports/REVIEW_NOTES.md`.
- Pair-order aggregation is corrected in a separate derived table. Original reports, original CSVs and original case JSON files are unchanged.
- Your original notebook is byte-for-byte preserved, including 23 saved outputs and its interrupted local-run output. It is not the completed-results viewer. Its last cell starts a full audit if deliberately run; review the saved results instead of starting another run.
- Case records and reports appear twice: task-organized exports in `03_Full_Audit` and matching files in the intact reproduction project. These are the same 544 students, not additional cases. Verification checks that both copies match.
- Checkpoint weights, Python environments and the original private fitted-model bundle are not included. The recorded model was a refit from the verified official checkpoint. Reading this package does not need those weights.
- Paths in the original run logs refer to the cloud workspace. The relative folder paths in this guide apply to the extracted package.

Extract to a short path such as `C:/Student_Dropout_Full_Audit` on Windows. `PACKAGE_MANIFEST.json` records checksums; `FILE_INDEX.csv` lists every packaged file.

Two presentation figures are in `03_Full_Audit/Figures/Presentation/` (package-relative path). They use saved tables, readable labels and, for pairs, the derived unordered summary restricted to n >= 30 for display. All five original PNGs are retained unchanged in `03_Full_Audit/Figures/`. No SHAP/model/case computation was repeated.

## New W1.1–W1.5 topic analysis

Open `04_View_Results/W1_Topic_Analysis.html` or the executed notebook beside it for single-versus-pair comparisons, explanatory feature selection and human-support proposals. The code and derived results are grouped by topic under `03_Full_Audit/Code/topics/`. `topics/run_all.py` uses all 544 saved cases; it does not fit TabICL or rerun SHAP. The original model still uses its 33 inputs. The explanatory panel is not a new predictive feature set or a causal intervention ranking.

## Feature contribution, changed prediction, then action

Open `04_View_Results/W1_Topic_Analysis.html` or its executed notebook. It defines all 33 inputs, shows signed contributions for a selectable student, presents recorded before/after feature-change probabilities, then proposes human support and follow-up. The two academic groups have only group totals retained (27 contribution groups cover 33 inputs).

Code and reports stay together: `03_Full_Audit/Code/topics/w1_1_local_explanations/` contains the feature guide and explanations; `w1_4_human_support/` contains scenario validation, optional prediction-only edits, practical support and a prospective follow-up template. No original case or fitted-model setting was changed.
