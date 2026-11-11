# W1 Noey — Full Validation Explanation Audit (COMPLETE)

**Evidence date:** 2026-11-11 01:00 UTC  
**Validation cases:** 544/544; **test partition:** not evaluated.  
**Final-test lock:** unchanged and checked against the audit manifest.  
**Important:** These are validation-only explanation-quality diagnostics. They do not change final-test results or the frozen predictive model.

## Actual observations and predictive comparison

The audit cases are all 544 held-out validation observations. The 2,541 training rows supply fitting and explanation references only; they are excluded from audit-case counts and predictive evaluation. Actual-versus-model predictions, confusion matrix, ROC-AUC, Brier score, calibration error, capacity precision/recall and balanced accuracy are saved separately in `outputs/actual_validation/`. Outreach flags follow the fixed top-20% policy; they are not a universal 0.5 classification rule. Predictive accuracy and explanation fidelity answer different questions.

Model origin: `refit_on_original_training_rows_with_frozen_settings`. The original private fitted-model/freeze bundle was not supplied. A refit using the recorded settings and verified checkpoint must not be described as loading that original serialized model.

## W1.1 — Case selection and local explanations

This completed audit includes 544 of the 544 eligible validation cases. The configured full run selects every case rather than a 20-case sample. Original feature values, SHAP values and group summaries are saved at case level. Signed grouped SHAP indicates direction of the model's probability contribution relative to the SHAP background, not the cause of dropout.

## W1.2 — Which features influence predictions? (local SHAP and deletion check)

**Mean absolute grouped SHAP on the full 544-case validation cohort (not a causal claim):**

- **first_semester_progress**: mean |grouped SHAP| = 0.2769; in top five for 97% of audited cases.
- **first_semester_participation**: mean |grouped SHAP| = 0.0525; in top five for 68% of audited cases.
- **tuition_fees_up_to_date**: mean |grouped SHAP| = 0.0513; in top five for 87% of audited cases.
- **course**: mean |grouped SHAP| = 0.0418; in top five for 75% of audited cases.
- **scholarship_holder**: mean |grouped SHAP| = 0.0193; in top five for 32% of audited cases.

The repository also has a *separate* global permutation-importance result on 100 sampled validation rows (`tables/grouped_permutation_importance_validation.csv`). Do not conflate that ROC-AUC-loss metric with grouped SHAP values (probability units). Use both to triangulate model reliance and inspect disagreements.

**Faithfulness: SHAP-ranked vs. random feature deletion**

Mean ranked-minus-random area = 1.55712; 95% bootstrap interval [1.47570, 1.64266].

The mean area is positive and its case-level bootstrap interval excludes zero; this supports reliance on the ranked groups under this masking test. Positive areas among cases: 536/544. The conclusion concerns reliance under training-reference masking, not causality or actual student interventions.

**Exploratory pairwise feature-group masking (not SHAP interaction values)**

For each case, the 10 pairs among its local top-five groups are masked jointly and separately. The nonadditive model response is `p(mask A+B) - p(mask A) - p(mask B) + p(original)`; a nonzero value indicates that joint masking differs from the sum of single masking effects under the selected reference values. It does **not** prove a causal interaction. It can depend on correlated features and off-manifold combinations.

- **first_semester_progress + first_semester_participation**: mean absolute nonadditivity 0.1972, across 320 audited cases.
- **debtor + mothers_occupation**: mean absolute nonadditivity 0.1729, across 1 audited cases.
- **first_semester_progress + scholarship_holder**: mean absolute nonadditivity 0.1180, across 163 audited cases.
- **first_semester_participation + first_semester_progress**: mean absolute nonadditivity 0.0954, across 40 audited cases.
- **fathers_occupation + debtor**: mean absolute nonadditivity 0.0788, across 1 audited cases.

Among the audited cases, mean absolute nonadditive response is 0.0358 probability units. These are descriptive exploratory findings, not pre-specified confirmatory outcomes. Joint change magnitude and signed direction are also saved case by case.

**Exploratory six-surrogate comparison: with/without pair terms and with/without regularization**

For each student, 32 patterns of masking the locally top-five groups are scored using the *unchanged* TabICL model. Six surrogate variants (ordinary least squares, Ridge, Lasso; main effects only or main + 10 pair terms) approximate these 32 model outputs. The fit uses 24 patterns and independently scores eight held-out higher-order masks. Ridge/Lasso penalty selection uses three-fold CV **inside** the 24 fitting patterns. Coefficient regularization is not performed on or used to change TabICL.

- **Lasso+pairs**: held-out MAE = 0.02239; mean nonzero terms = 9.9; out-of-range forecast share = 3.2%.
- **Ridge+pairs**: held-out MAE = 0.02514; mean nonzero terms = 13.5; out-of-range forecast share = 4.5%.
- **OLS+pairs**: held-out MAE = 0.02586; mean nonzero terms = 13.2; out-of-range forecast share = 4.9%.
- **OLS+main**: held-out MAE = 0.07153; mean nonzero terms = 4.9; out-of-range forecast share = 4.7%.
- **Ridge+main**: held-out MAE = 0.07276; mean nonzero terms = 4.9; out-of-range forecast share = 3.6%.
- **Lasso+main**: held-out MAE = 0.07313; mean nonzero terms = 3.7; out-of-range forecast share = 3.8%.

**Lowest held-out masking-pattern MAE on this completed cohort:** Lasso+pairs. This means it most faithfully approximated TabICL *for this particular masking test*, NOT that it is the best human explanation, a causal model, or a superior student-dropout predictor. Evaluate parsimony, out-of-range values and stability of pair importance as well. The comparison is exploratory and was added after the original final evaluation; it cannot retroactively establish the initial protocol gate.

## W1.3 — Explanation stability

- seed: mean overlap 0.818; 213 below 0.80; 0 insufficient.
- background: mean overlap 0.745; 411 below 0.80; 0 insufficient.
- perturbation: mean overlap 0.996; 0 below 0.80; 0 insufficient.

The 0.80 threshold is a pre-specified warning heuristic, not proof of explanation validity. Seed, background and perturbation results must be discussed separately; cases with fewer than two accepted perturbation explanations are insufficient, not passes.

**Exploratory pair-rank robustness:** 544/544 cases had at least one accepted grade perturbation to compare their top-three joint-masking rankings. Mean overlap across eligible cases: 0.9955709051297286. This is NOT full interaction-SHAP stability and must not be generalized to all perturbations or settings.

## W1.4 — Model-level recourse and possible support

Flagged validation cases: 108; cases with at least one model-level recourse candidate: 17; flagged cases with no candidate under the allowed changes: 91.

Only administrative debt/tuition-status resolutions are examined, individually and together where applicable, with the top-20% cohort ranking recalculated. Across all selected cases, 23 combined-status scenarios were evaluated; 8 resulted in leaving the flagged set in this model. This is a hypothetical model response, not a promise that a real student can make the change or avoid dropping out. Every scenario (including unsuccessful ones) is saved and identified explicitly.

**Permissible support interpretation:** If the model identifies debt or overdue tuition status, a student-support officer could *verify the record* and offer financial aid advice, payment-plan information or a referral to the appropriate service. If the explanation highlights academic progress, the officer can consider tutoring/advising, but this is **not a tested counterfactual** here: recorded grades are historical, not mutable. SHAP is not a causal intervention selector. Do not advise a student to manipulate records merely to avoid a model flag.

## W1.5 — Can we trust the explanations? Limitations and reviewer follow-up

- The OLS/Ridge/Lasso comparison uses locally approximated TabICL probabilities for masked variants of the **same validation case**. Good surrogate fidelity does not validate feature causality, true outcome accuracy or human comprehension.
- Lasso may drop correlated/interacting terms while Ridge distributes weight across them; coefficients are scale- and masking-dependent. Compare the no-penalty OLS baseline explicitly, and do not use Lasso to delete model features.
- Interaction analysis is a reference-masking test, not formal SHAP interaction values, causal identification or an intervention effect. The trained model is unchanged and the pairwise investigation was added after the original final evaluation.
- Pairs are conditionally selected from each student's baseline top five; all possible feature pairs are NOT tested, and importance of an unselected pair cannot be ruled out.
- Deleting feature groups using median/mode replacements may produce implausible combinations.
- Grade-only perturbations may generate small fractional grade values; these are range-clipped numerical sensitivity probes, not feasible student actions. The original broad count perturbations are not repeated under this add-on.
- Top-five overlap does not measure direction, size or causality of SHAP contributions.
- Local SHAP contributions are relative to 25 sampled training-background rows; changes in reference distribution, correlations, semantic grouping or model calibration may change them.
- This supplementary validation-only audit followed the 2 Nov amendment and the completed final test. Do not describe it as an earlier passed freeze gate.
- The 544 validation cases are the entire validation partition, but the study is still from one source dataset and not externally validated.
- W1 does not assess real human comprehension, usefulness, causal interventions or deployment safety.
- The original full audit was omitted in the 2 November accelerated workflow. This file records a **separate subsequent validation-only analysis**, not retroactive evidence that the earlier audit passed.

## Review status

Complete computational outputs generated; independent human/team review still needed.

## Source files

All audit outputs reside only in `W1_Noey_Enhanced/outputs/`: `tables/` has local SHAP, deletion, stability, pairwise reference-masking, all recourse scenarios and summary JSON; `figures/` has five charts; `cases/` has the provenance manifest and 544 case-level JSON records. Original Yolanda-produced source/results files are unchanged.
