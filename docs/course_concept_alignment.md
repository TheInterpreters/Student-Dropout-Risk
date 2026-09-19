# Course-concept alignment

This matrix records where concepts from the course slides are operationalised. A concept
is marked implemented only when code or a fixed protocol exists; final test and human
results remain deliberately unavailable.

| Course concept | Project implementation | Evidence |
|---|---|---|
| Stakeholder-centred explanations | Student-support officer prioritising voluntary outreach under limited capacity | Proposal Section 2; interface specification |
| Interpretability–accuracy trade-off | TabICL is compared on identical splits with logistic regression, a depth-3 tree, XGBoost, and a native main-effects EBM; its 0.006 validation ROC-AUC margin over EBM is reported as modest | `src/modeling.py`; validation tables |
| Intrinsic versus post-hoc interpretability | EBM provides exact additive shape functions/local terms; permutation SHAP explains non-decomposable TabICL | EBM tables and exactness artifact; SHAP integration artifact |
| Global versus local explanation | Local permutation SHAP plus global grouped permutation importance and ALE | `src/explanations.py`; `scripts/run_validation_audits.py` |
| Model-agnostic explanation | Permutation SHAP wraps TabICL dropout probability | `permutation_shap_values` |
| Faithfulness versus plausibility | Signed SHAP values are summed within semantic groups before absolute ranking; matched grouped deletion is compared with random orders | `aggregate_shap_by_group`; `deletion_curve` |
| Interpretable model as XAI ground truth | Synthetic additive white-box attribution rank check | `scripts/validate_explanation_pipeline.py` |
| Background/reference dependence | Seed variation and training-background variation are evaluated separately | Frozen protocol JSON |
| Correlated/off-manifold inputs | Semantic grouping, derived-feature recomputation, and ALE instead of relying on PDP | `semantic_feature_groups`; `accumulated_local_effect` |
| Stability | Label-free risk-stratified case selection, top-five overlap, rank correlation and clipped 1%-of-training-SD perturbations | Frozen protocol JSON; explanation helpers |
| Mental-model alignment | Blinded explanation/no-explanation forward simulation | Human-study instrument |
| Actionable recourse | Historical/immutable separation and capacity-ranking-consistent administrative changes | `constrained_binary_counterfactuals`; proposal Section 5.5 |
| Fairness and bias | Flag rate, TPR, FPR, precision, predicted-risk and calibration-gap diagnostics; proxy association checks | `src/auditing.py` |
| Correlation is not causation | SHAP, ALE and counterfactuals are described as model behaviour, not interventions | Proposal Sections 2, 5 and 6 |
| Explanation lifecycle | Validation freeze, one final test evaluation, model card, interface safeguards and human evidence | `config/evaluation_protocol.json`; handoff |

LIME, PDP, ICE and risk scores are not added merely to maximize method count. The
selected methods answer complementary questions: SHAP explains individual predictions,
grouped permutation importance measures global reliance, ALE examines global effects in
observed regions, and the GAM-like EBM plus transparent baselines test whether black-box
complexity is justified.
