# Final Proposal Audit

Audited: 2026-09-19

## Outcome

The submission-ready proposal is aligned with every criterion in the supplied grading
guideline. Microsoft Word renders the assessed body as four pages, followed by a
one-page reference appendix. The final test remains locked; all numerical results in
the proposal are validation-only and are labelled accordingly.

The guideline is internally inconsistent: its summary allocates Complexity 5 marks and
Ethics 5 marks, while the detailed text omits a separate complexity subsection and
labels Ethics as 10 marks. The proposal covers both interpretations through dedicated
Sections 6 and 7.

## Criterion-by-criterion check

| Criterion | Proposal evidence | Audit status |
|---|---|---|
| Audience and decision | Section 2 names one student-support officer, one outreach-prioritisation decision, timing, and both error costs | Complete |
| Model and baseline | Section 5.1 compares TabICL with logistic regression, a depth-3 tree, XGBoost, and native main-effects EBM on the same frozen validation split; it promises one same-test-set comparison | Complete for proposal; final test intentionally pending |
| Faithfulness | Section 5.2 freezes signed semantic-group SHAP aggregation, matched grouped deletion, 50 random orders, area-between-curves, local accuracy, and a white-box rank check | Complete design with integration evidence |
| Stability | Section 5.3 freezes label-free five-stratum case selection, 10 runs, seed/background variation, top-five overlap, 1%-of-training-SD perturbations, and a 0.80 warning rule | Complete design |
| Human evidence | Section 5.4 specifies a blinded two-group study, one practice case, 10 scored cases, participant-level accuracy, time, confidence, comments, and no feedback until completion | Complete design; recruitment pending |
| Actionability | Section 5.5 separates immutable/historical from feasible changes and defines success by leaving the top-20% set after exact cohort reranking | Complete design and implementation |
| Complexity | Section 7 contrasts non-decomposable TabICL with exactly additive EBM and refuses to presume that a 0.006 validation ROC-AUC margin justifies complexity | Complete and unusually strong |
| Ethics and data handling | Section 6 covers source/licence, consent, protected attributes, explicit small-group suppression, all-feature proxy screening, and non-causal/non-denial safeguards | Complete |
| Documentation and reproducibility | Section 8 records the fixed split/seed, pinned environment, protocol 1.2, 26 in-scope tests, exported evidence, model card, and planned regeneration command | Complete for proposal |

## Numerical and methodological consistency

- Dataset: 4,424 original records; 3,630 remain after excluding unresolved Enrolled
  outcomes. No second-semester feature is eligible.
- Split: fixed stratified 70/15/15 with seed 42 and saved source-row IDs.
- Capacity policy: stable top-20% cohort ranking; validation flag rate is 108/544 =
  0.198529.
- With 213 validation dropouts and 108 available flags, the maximum possible recall is
  108/213 = 0.507042; TabICL reaches this validation ceiling with precision 1.0.
- First-semester validation ROC-AUC: TabICL 0.952144, EBM 0.946102, XGBoost
  0.945165, logistic regression 0.945066, depth-3 tree 0.923117.
- TabICL capacity results: recall 0.507042, precision 1.000000, Brier 0.070795,
  10-bin ECE 0.018628.
- EBM capacity results: recall 0.502347, precision 0.990741, Brier 0.075681,
  10-bin ECE 0.032495.
- Admission-time ROC-AUC: EBM 0.875296, XGBoost 0.875197, TabICL 0.873949.
- EBM validation probabilities reconstruct from the intercept and main-effect terms
  with maximum error 3.33e-16. Interactions are fixed to zero.
- TabICL permutation-SHAP local accuracy and the synthetic white-box check remain
  distinct evidence: maximum reconstruction error 4.1e-8 and rank correlation 1.0.

## Remaining work after proposal approval

These are not proposal defects; they are deliberately identified future-project tasks:

1. Run the frozen label-free 20-case, 10-run faithfulness and stability audit.
2. Build and pilot the blinded study interface without leaking the model answer.
3. Confirm the required AIT ethics/administrative approval before recruitment.
4. Evaluate every model once on the untouched test split and report paired 2,000-resample
   intervals without further selection.
5. Conduct the human study, report actual group accuracy/time/sample sizes and comments,
   and avoid significance claims.
6. Complete the final model card and the one-command raw-data-to-figures runner.

No accuracy, faithfulness, stability, fairness, human-benefit, or deployment claim
should be upgraded beyond the proposal's present wording until the corresponding task
is complete.
