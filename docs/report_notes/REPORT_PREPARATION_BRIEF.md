# Report preparation brief

This repository is prepared for later report writing. Use saved aggregate evidence; do not rerun
the locked final test and do not expose raw participant responses.

## Central sources

- Headline machine-readable numbers: `tables/report_ready/project_numbers.json`
- Formatted aggregate tables: `tables/report_ready/`
- Report figures and diagrams: `figures/report_ready/`
- Human-study methods/results: `docs/HUMAN_STUDY_RESULTS.md`
- W1 explanation audit: `W1_analysis/03_Full_Audit/Reports/W1_COMPLETE_REPORT.md`
- Reproducibility boundary: `docs/REPRODUCIBILITY.md`
- Automated evidence audit: `artifacts/release_readiness.json`

## Suggested results order

1. Cohort and temporal design: 4,424 source records; 3,630 Dropout/Graduate records; fixed
   2,541/544/545 train/validation/test split; second-semester fields excluded.
2. Locked final test: compare all five models at the same top-20% outreach capacity. TabICL
   ROC-AUC 0.9566, Brier 0.0740, recall 0.507 and precision 0.991. Do not call TabICL
   significantly superior to XGBoost or EBM.
3. Fairness/proxy diagnostics: report descriptive group differences, suppression for n<30 and the
   strongest proxy associations. Do not claim fairness certification or causal discrimination.
4. Later W1 validation audit: explain that it used a frozen-settings refit and did not alter the
   final test. Report faithfulness together with the weaker background/seed stability and limited
   constrained recourse.
5. Human study: 50 complete participants, 25 per group, no exclusions. Profiles-only accuracy was
   0.916 and profiles-plus-explanations accuracy was 0.900; B-minus-A difference -0.016
   [-0.060, 0.032]. Discuss C01 and the leave-one-case-out result transparently.
6. Limitations: single dataset, Enrolled excluded, no external validation, capacity-limited recall,
   refitted W1 model, explanation/reference dependence, selected study cases, self-reported time,
   small study, no causal intervention evidence, and single-pass qualitative coding without measured agreement.

## Available figures

| Figure | Intended use |
| --- | --- |
| `project_pipeline.png` | End-to-end methods overview |
| `final_test_model_performance.png` | ROC-AUC and Brier comparison |
| `final_test_outreach_metrics.png` | Capacity recall and precision |
| `top_explanation_groups.png` | Validation grouped-SHAP overview |
| `explanation_stability.png` | Seed/background/perturbation contrast |
| `human_study_design.png` | Two-group study design |
| `figures/demo_card/demo_card_validation.png` | Validation-only static adviser-card demonstration |
| `interface/student_support_demo.html` (screenshot) | Local research interface; run `python scripts/launch_interface.py`, open a student with `#student=<id>` |
| `figures/human_study/human_accuracy_by_group.png` | Participant accuracy distribution |
| `figures/human_study/human_accuracy_by_case.png` | Case-level comprehension and C01 |
| `figures/human_study/human_confidence_vs_accuracy.png` | Confidence/accuracy relationship |
| `figures/human_study/human_completion_time.png` | Self-reported time distribution |

## Claims that are not supported

- “TabICL is significantly better than all baselines.”
- “The model identifies nearly all students who will drop out.”
- “SHAP features cause dropout or prescribe effective interventions.”
- “The system is fair or ready for institutional deployment.”
- “Explanation charts improved flag-identification accuracy.”
- “The human study validates real adviser decisions or student outcomes.”
- “Support officers used or evaluated the interface” (it was built after the study, never user-tested).
- What-if results as evidence that changing grades or paying fees would reduce a student's dropout risk.
- Any inter-coder agreement figure, or that two reviewers coded the answers (one coding pass only).

## Remaining non-report work

1. Done 11 Nov: all written answers coded once; aggregate themes and 5.7 ratings exported.
2. Optional: a team member blind-codes the 20% subset in `assignments_study.csv` and runs `agreement`
   so agreement can be reported; otherwise disclose it as not measured.
3. Report the response-quality caveat in `docs/HUMAN_STUDY_RESULTS.md` (generic/repeated answers).
4. Have an independent member verify the human-study and W1 claims against aggregate tables.
5. Execute the agreed private-data retention/deletion action after review.

After those steps, rerun:

```powershell
python -m unittest discover -s tests -v
python forms/test_spec.py
python scripts/build_report_assets.py
python scripts/verify_release_readiness.py
```

