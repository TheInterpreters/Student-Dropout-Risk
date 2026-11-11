# W1 topic analysis from saved full-audit evidence

**544/544 students covered. No TabICL, SHAP or case audit was rerun.**

Lowest recorded local surrogate MAE: Lasso+pairs, 0.02239.

## Matched main-only versus pair-augmented surrogates

| Family | Main MAE | Pair MAE | Mean MAE reduction | 95% student-bootstrap interval | Pair win fraction |
| --- | ---: | ---: | ---: | --- | ---: |
| OLS | 0.07153 | 0.02586 | 0.04567 | [0.04137, 0.05010] | 90.6% |
| Ridge | 0.07276 | 0.02514 | 0.04762 | [0.04338, 0.05206] | 91.7% |
| Lasso | 0.07313 | 0.02239 | 0.05073 | [0.04664, 0.05500] | 95.2% |

Resampling is by student, keeping that student’s eight masking tests together. Intervals are descriptive per-family intervals; selection is exploratory and is not a new independent predictive test.

## Selected explanatory panel

Main groups: first_semester_progress, first_semester_participation, tuition_fees_up_to_date, course, scholarship_holder.

Pairs: first_semester_participation + first_semester_progress; first_semester_progress + scholarship_holder; first_semester_progress + tuition_fees_up_to_date.

These are a report shortlist. The original predictor still uses all its original inputs. Exact nonzero Lasso coefficient identities were not saved in the old case format; this output does not invent them.

## Feature contribution → change in model output → human action

The feature guide defines all 33 inputs. Signed SHAP is saved for 27 groups: positive raises the local probability relative to the training background; negative lowers it. Individual member values were not retained for the two multi-input academic groups. No global monotonic or causal direction is inferred.

All 2508 broad scenario rows (including 544 original profiles) and 590 administrative rows are preserved in derived case exports. Scenario summaries exclude baselines and not-applicable/no-change placeholders. Compare before/after within each student: scenario populations differ.

Grade/credit edits are retrospective input sensitivity. Verified financial assistance and practical tutoring/access support target real barriers and future study, with no estimated local causal effect on dropout. A separate optional callback can score new permitted edits using an already-fitted model; it does not fit or rerun this audit.

## Robustness and human action

The robustness topic preserves original warning counts and also reports a 1e-12 numerical tolerance at the 0.80 boundary. Original case JSON is unchanged.

Academic, financial and combined support are proposed human-reviewed actions. Ask students about current barriers, target future course engagement and assistance, and monitor actual continued enrollment/completion. Model masking responses do not estimate programme benefits.

The human-support topic includes an empty prospective follow-up template. There are no future intervention outcome records in this audit.

## Evidence limits

The 24/8 local masking design and its six saved variants are reused. Pair effects are conditional on each student’s SHAP-selected top five groups. Rare pairs remain in the summary with their counts but are excluded from the reporting panel below the declared support threshold.

Convergence warnings, background/seed instability, off-manifold masking and the absent original private fitted-model bundle remain limitations. No retention improvement or causal effect is inferred from these files.
