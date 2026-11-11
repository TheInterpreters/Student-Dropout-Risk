# W1.1–W1.5: analysis of the completed audit

This code reuses all **544 saved validation case records**. It does not fit TabICL, download a checkpoint, rerun SHAP or change the original 33 model inputs. The original audit runner and recorded case files remain unchanged.

| Topic | Code | Reports beside the code |
| --- | --- | --- |
| W1.1 — Local explanations | `w1_1_local_explanations/analysis.py` | `results/feature_importance.csv` |
| W1.2 — Single versus paired groups | `w1_2_single_vs_pairs/analysis.py` | `results/single_vs_pair_summary.csv`, `matched_main_vs_pairs.csv`, `six_variants.csv` |
| W1.3 — Robustness | `w1_3_robustness/analysis.py` | `results/stability_summary.csv`, `conditional_feature_retention.csv` |
| W1.4 — Human retention support | `w1_4_human_support/analysis.py` | `results/support_catalogue.csv`, future follow-up template, support-plan guide |
| W1.5 — Explanatory selection | `w1_5_feature_selection/analysis.py` | `results/selected_explanatory_panel.json`, selected groups and pairs |

## Run from saved files

Use Python 3.12 with NumPy and pandas. From this folder:

```sh
python run_all.py --cases "/path/to/Student_Dropout_Full_Audit/03_Full_Audit/Cases"
```

Extract the whole full-audit ZIP so its saved model-prediction CSV is available for identity checks. The code validates all 544 IDs, the model-probability hash, all ten pair probes and the six variants on matching holdout patterns before analysis. Without an explicit path it searches the complete extracted package or the saved cloud run.

`policy.json` exposes the new reporting defaults: five main groups, up to three pairs, at least 30 observed cases per pair, 2,000 student-level bootstrap resamples and a numerical tolerance at the 0.80 stability boundary. These are post-hoc reporting choices, not changes to the original frozen protocol.

The selected panel is for explaining the existing model. It is **not validated predictor input selection** and is not the exact nonzero Lasso coefficient list, which the original case format did not save. Changing a predictive model's features requires separate training/validation and its own evaluation; old explanation results would then describe the old model.

Case-level CSV exports and case fingerprints remain local by default. Aggregate topic tables, code and documentation are shareable project outputs.

Start with `W1_SUMMARY.md` after running. Open the executed W1 topic notebook/HTML in `Student Dropout Project/Reports/Full_Audit/` to read results without another model run.

## How TabICL is audited

1. The official pretrained checkpoint and original 2,541 training rows define the recorded refit/context. The private original saved fitted-model bundle was not supplied.
2. Its probabilities and capacity flags are compared with actual outcomes for all 544 validation students.
3. SHAP, ranked-versus-random deletion, all ten top-five group pairs per student and saved scenario responses probe that unchanged model.
4. Repeated seeds, training backgrounds and eligible grade changes test explanation robustness.
5. Six local surrogates approximate TabICL on recorded held-out masks. Their fidelity is separate from TabICL’s outcome accuracy and from human support effectiveness.

This is an audit of recorded model behavior on this dataset, not proof of every internal weight or a causal retention effect. This topic code performs only post-processing of the completed evidence.

## Read in this order

1. `w1_1_local_explanations/feature_guide.py` defines all 33 model inputs; `results/all_33_feature_definitions.csv` lists meanings and action context. `explain_case(record)` shows all 27 signed contributions for a selected student. Positive means a higher model probability relative to the SHAP background; negative means a lower probability. The two academic groups have only group totals saved, so separate contributions for their members are unavailable.
2. `w1_4_human_support/scenarios.py` validates saved before/after probabilities and exports `results/recorded_scenario_summary.csv`. All 2,508 broad rows and 590 administrative rows remain in the case exports inside the full ZIP. Original/no-change rows are not effect experiments. The scenario cohorts differ; this is not an intervention-efficacy ranking.
3. `make_support_plan(record)` proposes human review and practical support; use confirmed needs to choose single or combined assistance. Historical grade/credit edits are not prospective actions. Monitor future enrollment and progress rather than treating a flag change as success.

The executed W1 notebook provides the full sequence, a named-case example and an optional prediction-only wrapper for new four-input edits. The optional function needs an already-fitted model, does not fit/download anything and never overwrites audit evidence. Other feature edits were not exhaustively simulated in the recorded scenarios; their SHAP/masking contributions are not substitutes for a new prediction.
