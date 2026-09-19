# Project Handoff — Canonical Current State

Updated: 2026-09-19

## 0. What to show the professor and team

- Final title: **Trustworthy Explanations for Student Dropout Risk: Comparing
  Black-Box and Interpretable Models**.
- Submission files: `The-Interpreters-ProjectProposal-XDS-125970-126729-127419-127305-127366.docx`
  and the matching `.pdf`.
- The assessed proposal body is four pages; references occupy a separate fifth page.
- The repository contains only the UCI predictive dataset used by the project. The
  unrelated OfS background-data branch has been removed from version control.
- All 26 tracked, in-scope automated tests pass in the pinned `.venv-core`
  environment. Three additional ignored tests belong to the local archived text branch
  and are not part of the submitted repository.
- Reported model numbers are validation-only. The final test remains untouched and no
  human-study result is claimed before data collection.

The proposal is ready to show. For an honest status update, describe the methodology,
validation evidence and frozen protocol as complete, while describing the explanation
audit, interface, one-time final-test run and human study as planned next work.

## 1. Final scope decision

The project predicts first-year student dropout risk from the UCI **Predict Students’
Dropout and Academic Success** dataset and evaluates whether local explanations of a
tabular foundation model are faithful, stable, actionable, fair, and useful to a
university student-support officer.

- Primary model: TabICL 2.2.0 with four estimators.
- Baselines: logistic regression, depth-3 decision tree, XGBoost, and a native
  main-effects Explainable Boosting Machine (EBM).
- Primary task: Dropout (1) versus Graduate (0).
- Decision point: after first-semester results and before second-semester support.
- Explanation method: model-agnostic SHAP on dropout probability.
- Evidence: deletion faithfulness, repeated-run and perturbation stability, constrained
  counterfactuals, subgroup/proxy diagnostics, and a two-group forward-simulation study.
- Unstructured data: only the consented, anonymised written responses collected during
  the human study. Participants will be voluntarily recruited from the AIT community;
  they will assess pseudonymised UCI cases, and no AIT student records will be collected.

There is **no external university-review corpus and no second predictive dataset** in
the current scope. The old `final.csv`/BERTopic branch is archived and must not supply
claims, figures, or findings for the submitted project.

## 2. Completed work

- UCI EDA completed: 4,424 rows, 36 predictors, no missing values, no duplicate rows.
- Temporal feature policy implemented: second-semester variables are excluded.
- Fixed stratified 70/15/15 split implemented with seed 42 and source-row identifiers.
- Validation-only baselines and TabICL feasibility run completed.
- Protocol amended to 1.2 before test access: 1.1 added EBM; 1.2 froze semantic-group
  SHAP aggregation, label-free case selection, perturbation scaling, capacity-consistent
  recourse, explicit subgroup suppression, proxy checks and paired uncertainty without
  changing the split, seed, target, feature windows, or test data.
- EBM exact additive reconstruction passed on all 544 validation cases with maximum
  probability error 3.4e-16; global and fixed local term tables are exported.
- TabICL runs locally and reproducibly.
- Explanation-evaluation primitives and unit tests implemented.
- Capacity-based top-20% operating policy implemented; the earlier recall-plus-capacity
  formulation was rejected as mathematically infeasible.
- TabICL/permutation-SHAP integration passed on validation cases with maximum local-
  accuracy error below 4.1e-8; the synthetic white-box rank check achieved 1.0.
- Semantic feature grouping, derived-feature recomputation, grouped permutation
  importance, ALE, subgroup suppression and all-feature proxy tables implemented.
- Admission-time sensitivity completed: TabICL validation ROC-AUC 0.874 versus 0.952
  post-semester-one, with capacity-policy recall 0.469 versus 0.507.
- Human-study instrument, response schema, model-card template, and proposal prepared.
- The final test partition has not been used for reported model selection.

### Validation-only feasibility results

| Model | Balanced accuracy | Macro-F1 | ROC-AUC | Recall | Precision |
|---|---:|---:|---:|---:|---:|
| Logistic regression | 0.754 | 0.768 | 0.945 | 0.507 | 1.000 |
| Depth-3 decision tree | 0.746 | 0.759 | 0.923 | 0.498 | 0.981 |
| XGBoost | 0.750 | 0.764 | 0.945 | 0.502 | 0.991 |
| Main-effects EBM | 0.750 | 0.764 | 0.946 | 0.502 | 0.991 |
| TabICL (four estimators) | 0.754 | 0.768 | 0.952 | 0.507 | 1.000 |

All rows use the same validation cohort and top-20% capacity policy. Interpretation:
TabICL is feasible and competitive, but its ROC-AUC margin over EBM is only 0.006 and
validation does not establish operational superiority. That honest comparison is part
of the model-complexity analysis. The untouched test set will be evaluated once after
all choices are frozen.

## 3. Pre-specified methodology

### Data and target

Exclude Enrolled records from the primary binary task because their final outcome is
unresolved. Document that this restriction may introduce selection bias and limits
applicability. If time and class support permit, run a sensitivity analysis that treats
Enrolled as a third class or groups it with non-dropout. A second bounded sensitivity
check, subject to time, will compare an admission-time feature window with the primary
post-first-semester window to quantify the value of waiting for semester-one results.

### Faithfulness

Use a training-only SHAP background. Replace numerical features with training medians
and categorical features with training modes. Compare ranked deletion curves with
repeated random deletion and report the area between curves with uncertainty. These
deletions measure model reliance, not realistic intervention.

### Stability

Select four deterministic cases from each of five predicted-risk strata without labels.
Run the explainer 10 times
per case with controlled seeds/background samples. The primary metric is mean pairwise
top-five overlap: `number of shared top-five features / 5`. Rank correlation is
secondary. Perturb continuous features using Gaussian noise at 1% of training-set
standard deviation, clip to training bounds, recompute dependencies, and retain only
perturbations with absolute probability change at most 0.01. Warn below 0.80 overlap.

### Human evidence and qualitative responses

Aim to recruit 8–10 participants, require at least four, and allocate the achieved sample
as evenly as practicable across two groups using the recorded seed. Recruitment will use a voluntary convenience
sample from the AIT community. Both groups predict the concealed model output on the
same 10 pseudonymised UCI test profiles. Group A sees the profile; Group B sees the profile plus an
explanation that suppresses the output, probability, capacity boundary, and predicted class.
Use one unscored practice case and reveal no feedback until all 10 scored cases are locked.
Compare accuracy and time descriptively. Code brief written rationales, support actions,
and missing-information comments using a pre-defined guide. If participants are not
student-support professionals, identify them as intended-user proxies and limit the
claim to explanation comprehensibility. Do not claim statistical significance from the
small sample or deployment validity at AIT.

### Actionability, fairness, and ethics

Constrain counterfactuals to changes that are feasible at the stated decision point;
keep immutable and historical fields fixed. Distinguish institution-controlled support
from student-controlled action. A successful result must leave the top-20% flagged set
after recomputing rank with every other cohort score fixed; do not use a universal 0.5
threshold or describe counterfactuals as causal promises.
Retain all subgroup counts, suppress metrics below n=30, state unavailable comparisons,
and screen every non-protected feature as a potential proxy. Frame the system as outreach support rather than an autonomous decision.
Human participation must be voluntary and consented; collect no names, keep raw free
text outside version control, and report only aggregate or paraphrased evidence. Before
recruitment, confirm with the course instructor whether AIT approval is required and
obtain it where applicable.

## 4. Next actions, in order

1. Run the pre-specified 20-case explanation faithfulness/stability audit on validation.
2. Build and pilot the two-mode browser interface defined in `docs/interface_spec.md`:
   a decision-support demonstration view and a blinded A/B study view. Verify that study mode
   reveals no answer or feedback until all 10 scored cases are complete.
3. After all acceptance checks pass, evaluate all frozen models once on the untouched test split.
4. Generate explanations, faithfulness/stability results, constrained counterfactuals,
   subgroup diagnostics, and the 10 pre-specified study cases.
5. Obtain consent and conduct the human study; code responses using two reviewers for
   the agreed subset.
6. Complete the model card and provide one clean-clone command that regenerates all
   reported tables and figures.

## 5. Repository map

- `The-Interpreters-ProjectProposal-XDS-125970-126729-127419-127305-127366.docx` — editable submission candidate.
- `The-Interpreters-ProjectProposal-XDS-125970-126729-127419-127305-127366.pdf` — rendered submission candidate.
- `docs/proposal_source.docx` — tracked canonical source used by the proposal builder.
- `scripts/finalize_proposal_docx.py` — regenerate the submission candidate from that
  source.
- `README.md` — public project overview and reproduction entry point.
- `eda_uci_data/eda_dropout.ipynb` — completed UCI EDA.
- `notebooks/uci_tfm_baseline.ipynb` — split and modelling overview.
- `src/modeling.py` — target, temporal policy, split, and model helpers.
- `src/explanations.py` — faithfulness, stability, and recourse primitives.
- `scripts/run_validation.py` — validation-only baseline and TFM runner.
- `tables/baseline_validation_metrics.csv` and `tables/tfm_validation_metrics.csv` —
  current feasibility evidence.
- `docs/human_study_instrument.md` — criterion-5 protocol.
- `docs/interface_spec.md` — decision-support demonstration and blinded-study interface specification.
- `docs/MODEL_CARD.md` — living model card.
- Local `text_analysis/`, `data/text/`, `requirements-text.txt`, and `EDA/` materials —
  ignored exploratory work, out of scope and not to be recommitted.

## 6. Rubric alignment

| Criterion | Planned evidence |
|---|---|
| 1. Audience and decision | Student-support officer, post-semester-one outreach decision, asymmetric error costs |
| 2. Model and baseline | TabICL with same-split logistic, tree, XGBoost, and main-effects EBM baselines |
| 3. Faithfulness | Ranked-versus-random deletion curves and area between curves |
| 4. Stability | 20 cases × 10 runs, top-five overlap, rank correlation, perturbation test |
| 5. Human evidence | Two-group forward simulation plus time and qualitative responses |
| 6. Actionability | Feasibility-constrained counterfactuals and explicit no-recourse cases |
| 7. Complexity | Architecture/configuration disclosure and honest baseline comparison |
| 8. Ethics | Consent, data minimisation, protected-group and proxy diagnostics |
| 9. Reproducibility | Fixed split/seeds, pinned environment, tests, model card, regeneration command |

## 7. Commands

From the repository root in `.venv-core`:

```powershell
python -m unittest tests.test_modeling tests.test_explanations tests.test_auditing -v
python scripts/run_validation.py
python scripts/validate_explanation_pipeline.py
python scripts/run_validation_audits.py
python scripts/run_temporal_sensitivity.py
```

Do not open or report final-test performance until the model and explanation protocol
are frozen.

## 8. Git and data hygiene

- Delete a tracked file from both Git and the working folder with
  `git rm -- <path>`, then commit and push.
- Keep a file locally but stop tracking it with `git rm --cached -- <path>`, add the
  path to `.gitignore`, then commit and push.
- Before either command, use `git ls-files -- <path>` to verify that Git tracks the
  exact target.
- Ordinary deletion does not erase earlier commits. Use history-rewriting tools only
  for exposed secrets or a serious repository-size problem, and only after coordinating
  a force-push and fresh clones with every collaborator.

The removed OfS ZIP remains recoverable from earlier commits. It contains no secret and
is below GitHub's per-file limit, so rewriting shared history is unnecessary.
