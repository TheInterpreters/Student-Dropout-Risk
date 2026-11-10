# W1_Noey_Enhanced — Independent full-validation-cohort explanation audit

**Continuation update (4 November 2026):** Start with [`CONTINUE_HERE.md`](CONTINUE_HERE.md).
Actual data-quality checks have now run on **all 544 held-out validation rows**.
The 2,541 training rows are fitting/reference data only. The new `--compare` command
compares real model predictions with recorded validation outcomes before the full
explanation audit. Model scoring is currently blocked by checkpoint download access;
no model metrics or completed SHAP cases are claimed. The runner explicitly records
that it refits from the recorded settings rather than loads the private original
fitted-model bundle. Earlier preparation status below is historical.

**Status:** runnable **audit implementation**, synthetic checks passed; **the actual 544-student TabICL audit has not been executed in this preparation environment**. Outputs will be populated after running on the original team project with the installed TabICL checkpoint. No empirical explanation-quality conclusion or best Ridge/Lasso variant is claimed yet.

**Start with [`LAYOUT.md`](LAYOUT.md)**: complete folder structure, Windows commands, outputs and manual review checklist. This package stays fully separate from Yolanda's original files.

## Research question

Can the frozen TabICL model's dropout predictions be explained consistently at individual and feature-pair levels, and what changes to student attributes could alter the *model's* predicted risk or top-20% outreach flag? How do six local explanatory surrogates compare for reproducing frozen TabICL responses to structured masked-feature probes? What is **not** causally or operationally knowable from the available data?

## Coverage

The original raw data has **4,424** students, including 1,421 Dropout, 2,209 Graduate and 794 Enrolled records. The fixed binary evaluation uses **3,630** eligible Dropout/Graduate records with **2,541 training / 544 validation / 545 locked final test**. This supplementary full audit explains **ALL 544 validation students** rather than 20 selected cases. Separate descriptive subgroup analyses cover training and validation, with no test outcome analysis. The prior final-test lock and model settings are left intact.

| Workstream | Full audit | Output |
|---|---|---|
| **W1.1 — Student selection and local SHAP** | 544/544 validation students; 25-row training-only SHAP background, 67 evaluations; signed semantic-group SHAP | One case JSON per student; local SHAP table and summary |
| **W1.2 — Influence, faithfulness, combinations** | Top-five grouped SHAP; ranked deletion vs 50 random orders; all 10 top-five group pairs per student; reference-masking joint effects; six surrogates | Faithfulness curves and bootstrap area, pair tables, OLS/Ridge/Lasso comparisons |
| **W1.3 — Robustness** | 10 seeds, 10 backgrounds and up to 10 eligible grade-only small input perturbations per student; analyze top-five overlap and pair ranks | Stability tables and plots, insufficient-case counts |
| **W1.4 — Student-support scenarios** | One and combined tuition/debt status resolutions for **all flagged validation students**; individual and combined grade/approved-unit hypothetical input sensitivity for all 544 | Scenario probabilities, percentage-point differences, recourse flags/ranks, review prompts |
| **W1.5 — Trustworthiness conclusion** | Aggregate all findings with limitations and evidence status | `summary.json`, 17 CSV tables, 5 charts and complete Markdown report |

### Understanding the equations

Local signed grouped SHAP:

\[\Phi_G(x)=\sum_{j\in G}\phi_j(x).\]

Pairwise masking nonadditivity for semantic groups A and B:

\[I_{AB}=p(x_{AB})-p(x_A)-p(x_B)+p(x).\]

This is **not** a SHAP interaction value and is sensitive to reference-mask choices. It is not a causal estimate.

Six local surrogates fit unchanged TabICL responses on 32 combinations of masked top-five groups:

\[\widetilde p(m)=\beta_0+\sum_{i=1}^{5}\beta_i m_i+\sum_{i<j}\gamma_{ij}m_im_j.\]

Run OLS (no penalty), Ridge (\(L_2\) penalty) and Lasso (\(L_1\) penalty), each with and without the ten pair terms. **24** patterns are used for fitting/tuning, **8** different higher-order masks for fidelity scoring. Ridge/Lasso hyperparameters are tuned using only the training-mask patterns. Report held-out MAE, RMSE, sparsity and predictions outside [0,1]. The best surrogate *approximates the model under the masking experiment*; it does not necessarily provide the best true explanation or student-outcome predictor.

### Academic improvement vs feasible recourse

- **Historical first-semester grades/approved credits:** changing these values after the first-semester prediction point is *retrospective model sensitivity*, not actionable recourse. A target such as future 12/20 grade is a student-support goal but cannot be validated by this model as a causal intervention.
- **Debt and tuition status:** possible administrative-resolution probes, conditional on actual feasibility and institutional verification. The code recalculates the frozen top-20% cohort flag with all other students' scores fixed.
- **No feasible model recourse:** does NOT mean no university support is possible. Advising, tutoring and financial support remain topics for human review.

### Reproduction boundaries and computing cost

This analysis was added **after** the 2 November accelerated scope decision and the completed held-out final evaluation. It is a separate supplementary validation audit, not a retroactive pre-freeze approval. It must never run `scripts/run_final_test.py` or remove `artifacts/final_test.lock`.

The full 544-case SHAP audit can be **extremely slow on CPU** because it performs repeated SHAP computations and many counterfactual model calls. Use `--max-new-cases 1` first, check results, then resume in batches. A batch refits the training-only TabICL model before resuming, so many tiny batches increase overhead. `--report` refuses incomplete studies; `--report-partial` produces clearly labeled incomplete evidence.

**Current verification:** 20 synthetic unit tests passed and a separate *synthetic* 544-case report-generation smoke test successfully produced the expected 17 CSV tables and five plots. No real TabICL/SHAP empirical audit was executed in this environment.

**Sources:** the project's `eda_uci_data/data/dropout_data.csv`, `artifacts/split_ids.csv`, `config/evaluation_protocol.json`, `src/` and `scripts/` from the main branch at the point of preparation. See [`docs/HANDOFF_TO_YOLANDA.md`](docs/HANDOFF_TO_YOLANDA.md) for a peer-review and final-test rerun decision protocol.
