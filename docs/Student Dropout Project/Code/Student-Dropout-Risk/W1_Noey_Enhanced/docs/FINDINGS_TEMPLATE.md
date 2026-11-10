# Noey W1 enhanced analysis — review-ready report template

**Status as prepared 4 November 2026:** Proposed analyses and code; real 544-case TabICL run pending. Any bracketed value below must be filled from **generated validation evidence** only.

## W1.1 — Case selection and individual explanations
- Model: frozen TabICL 2.2.0 (four estimators); first-semester data, fixed saved train/validation split; no final test access.
- Twenty deterministic validation cases across five predicted-risk strata. Verify sample IDs in `outputs/cases/manifest.json`.
- State each student's dropout-risk prediction and signed top-five semantic SHAP contributions without disclosing private profile data.
- **Finding:** [once available: leading groups and illustrative differences among model-risk strata].

## W1.2 — Individual, grouped and paired feature evidence
- Local group summary: [top five by mean absolute SHAP; probability units; all 544 validation cases].
- Existing separate global evidence: first-semester progress ROC-AUC permutation drop 0.2547 (100-case validation sample), tuition-status 0.0375, participation 0.0245. These are **not local SHAP**.
- Deletion faithfulness: [ranked-minus-random area, case-level 95% bootstrap interval, positive cases/20].
- Pair masking: [largest mean |nonadditive effect| pairs; per-pair counts; distinguish 10 pairs of local top five from a full feature search].
- Surrogate comparison: Six variants (`OLS`, `Ridge`, `Lasso` each with main-only vs +10 pair terms). [MAE, RMSE, R², nonzero terms, out-of-range probabilities, alpha]. Best **local mimic by held-out MAE**: [value, not determined until real run]. Do not equate this with the most trustworthy explanation.

## W1.3 — Stability and robustness
- Ten seeds: [overlap, rank correlation, count under 0.80].
- Ten training backgrounds: [same].
- Up to ten effective and prediction-preserving grade perturbations: [eligible count, overlap, rank correlation, insufficiencies].
- Pair robustness among accepted perturbations: [top-three pair overlap, eligible cases].
- Note: SHAP value **magnitudes** and **signs** are not fully certified by top-five overlap alone.

## W1.4 — Conditional model recourse and support topics
- Only debtor -> 0 and tuition-paid -> 1 are mechanically tested, individually and together, for flagged cases; unflagged cases are not considered recourse targets.
- [number flagged, number with successful single or combined scenario, number without feasible/successful scenario].
- The top-20% **whole-cohort** ranking must be recalculated after hypothetical model-score changes. State when a scenario changes probability without changing a flag.
- Academic tutoring, counselling, payment support and advisor outreach are potential human discussion topics, **not intervention effects measured by the model**.

## W1.5 — Conclusion and limitations
- **Prior recorded evidence**: one middle-risk validation case / two SHAP seeds / 0.80 overlap / 47.37 seconds. Execution check only; not a general pass.
- **Current empirical status:** [pending/completed and independently checked].
- **Conclude:** [what the actual 544-case outputs support about model reliance, stability, pair masking and feasible recorded-status scenarios].
- **Limitations:** correlational data, no causal inference, reference-masking off-manifold possibility, one fixed 544-case validation partition (no external validation), nonrepresentative perturbation design, SHAP background dependence, pairwise search selection, proxy/fairness concerns, unverified impact of student-support referrals and unknown generalisation to other institutions.
- **Do not repeat the final evaluation:** the historical locked test result remains unchanged; supplementary validation evidence adds to limitations and interpretation, not the held-out score.

## Discussion bullets for team report
1. Feature importance should be examined at both local and semantic-group levels; grouped contribution alone does not reveal interactions.
2. Joint masking effects and Ridge/Lasso surrogate fidelity can expose nonadditive model behavior but cannot establish causal student-support actions.
3. Even a technically stable prediction explanation must be independently verified for relevance, fairness and human usefulness before real deployment.
