# Model Card — Student Dropout Early-Warning Model

## Status

Development model and protocol selected; final test evaluation remains locked. TabICL
2.2.0 with four estimators passed the validation-only feasibility and SHAP integration
gates. The operating policy ranks each cohort and flags at most the top 20% by risk.

## Intended use

Decision support for a university student-support officer prioritizing voluntary outreach and
support meetings after first-semester results. It is not an autonomous decision system
and must not be used to deny enrollment, financial support, or academic services.

## Prediction target and time

- Target: Dropout=1 versus Graduate=0.
- Enrolled records: excluded from the primary task because the outcome is unresolved.
- Prediction time: immediately after first-semester results.
- Prohibited leakage: all second-semester curricular variables.

## Data

UCI “Predict Students' Dropout and Academic Success,” 4,424 students before target
filtering and 3,630 after excluding unresolved Enrolled outcomes, Portuguese
higher-education context, CC BY 4.0. The primary feature frame adds first-semester pass
rate plus explicit no-enrolment/no-evaluation indicators and excludes every
second-semester curricular field.

## Splitting and selection

Stratified 70/15/15 train/validation/test split with seed 42 and saved source-row IDs.
TFM feasibility and all model choices use train/validation only. The test set is used
once after the model and explanation protocol are frozen.

## Models and results

Selected development model: TabICL 2.2.0, four estimators, CPU, seed 42. Validation
ROC-AUC is 0.9521. Under the frozen top-20% capacity policy, validation dropout recall is
0.5070, precision is 1.0000, flag rate is 0.1985, Brier score is 0.0708 and 10-bin ECE is
0.0186. The admission-time sensitivity model achieved ROC-AUC 0.8739 and capacity-policy
recall 0.4695, showing added predictive information after semester one but not resolving
the eligibility-timing limitation. These are validation—not final—metrics.

## Explanation evidence

Permutation SHAP uses 25 training-only background rows and 67 evaluations. Validation
integration reconstructed probabilities within 4.1e-8; a synthetic white-box check
achieved absolute-rank Spearman 1.0. Complete the pre-specified deletion, top-five,
perturbation and human forward-simulation results before final reporting.

## Fairness and limitations

Report subgroup sample sizes and error rates where groups are large enough, plus proxy
checks. The data come from one institution and may not transfer to another country or
time period. Predictive associations are not causal diagnoses. A feasible counterfactual
may not exist for every student.
