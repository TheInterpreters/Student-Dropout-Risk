# W1.1 — Student coverage and local explanations

`analysis.py` aggregates every saved signed grouped SHAP contribution. All groups must cover every selected validation student exactly once. `results/feature_importance.csv` ranks mean absolute grouped SHAP over all 544 students and retains group members, signed means and top-five frequency. This is descriptive model attribution, not causal feature importance. Per-student SHAP exports remain local.

## Read in this order

1. `w1_1_local_explanations/feature_guide.py` defines all 33 model inputs; `results/all_33_feature_definitions.csv` lists meanings and action context. `explain_case(record)` shows all 27 signed contributions for a selected student. Positive means a higher model probability relative to the SHAP background; negative means a lower probability. The two academic groups have only group totals saved, so separate contributions for their members are unavailable.
2. `w1_4_human_support/scenarios.py` validates saved before/after probabilities and exports `results/recorded_scenario_summary.csv`. All 2,508 broad rows and 590 administrative rows remain in the case exports inside the full ZIP. Original/no-change rows are not effect experiments. The scenario cohorts differ; this is not an intervention-efficacy ranking.
3. `make_support_plan(record)` proposes human review and practical support; use confirmed needs to choose single or combined assistance. Historical grade/credit edits are not prospective actions. Monitor future enrollment and progress rather than treating a flag change as success.

The executed W1 notebook provides the full sequence, a named-case example and an optional prediction-only wrapper for new four-input edits. The optional function needs an already-fitted model, does not fit/download anything and never overwrites audit evidence. Other feature edits were not exhaustively simulated in the recorded scenarios; their SHAP/masking contributions are not substitutes for a new prediction.
