# Project Handoff — Canonical Current State

Updated: 2026-09-19

## 1. Final scope decision

The project predicts first-year student dropout risk from the UCI **Predict Students’
Dropout and Academic Success** dataset and evaluates whether local explanations of a
tabular foundation model are faithful, stable, actionable, fair, and useful to a
university student-support officer.

- Primary model: TabICL 2.2.0 with four estimators.
- Baselines: logistic regression, depth-3 decision tree, and XGBoost.
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
- TabICL runs locally and reproducibly.
- Explanation-evaluation primitives and unit tests implemented.
- Capacity-based top-20% operating policy implemented; the earlier recall-plus-capacity
  formulation was rejected as mathematically infeasible.
- TabICL/permutation-SHAP integration passed on validation cases with maximum local-
  accuracy error below 4.1e-8; the synthetic white-box rank check achieved 1.0.
- Semantic feature grouping, derived-feature recomputation, grouped permutation
  importance, ALE, subgroup diagnostics and association measures implemented.
- Admission-time sensitivity completed: TabICL validation ROC-AUC 0.874 versus 0.952
  post-semester-one, with capacity-policy recall 0.469 versus 0.507.
- Human-study instrument, response schema, model-card template, and proposal prepared.
- The final test partition has not been used for reported model selection.

### Validation-only feasibility results

| Model | Balanced accuracy | Macro-F1 | ROC-AUC | Dropout recall |
|---|---:|---:|---:|---:|
| Logistic regression | 0.882 | 0.879 | 0.945 | 0.873 |
| Depth-3 decision tree | 0.885 | 0.881 | 0.923 | 0.878 |
| XGBoost | 0.894 | 0.897 | 0.945 | 0.854 |
| TabICL (four estimators; 0.5 threshold legacy comparison) | 0.892 | 0.897 | 0.952 | 0.845 |

Interpretation: TabICL is feasible and competitive, but validation does not establish
clear superiority over XGBoost or the simpler baselines. That honest comparison is part
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

Pre-select 20 held-out cases across predicted-risk levels. Run the explainer 10 times
per case with controlled seeds/background samples. The primary metric is mean pairwise
top-five overlap: `number of shared top-five features / 5`. Rank correlation is
secondary. Also test small valid perturbations only when the model prediction remains
within a pre-specified tolerance. Freeze tolerances on validation cases before test
evaluation.

### Human evidence and qualitative responses

Target 8–10 participants, while preserving the rubric-compliant minimum of 4–5 split as
evenly as possible across two groups. Recruitment will use a voluntary convenience
sample from the AIT community. Both groups predict the concealed model output on the
same 10 pseudonymised UCI test profiles. Group A sees the profile; Group B sees the profile plus an
explanation that suppresses the output, probability, threshold, and predicted class.
Compare accuracy and time descriptively. Code brief written rationales, support actions,
and missing-information comments using a pre-defined guide. If participants are not
student-support professionals, identify them as intended-user proxies and limit the
claim to explanation comprehensibility. Do not claim statistical significance from the
small sample or deployment validity at AIT.

### Actionability, fairness, and ethics

Constrain counterfactuals to changes that are feasible at the stated decision point;
keep immutable and historical fields fixed. Distinguish institution-controlled support
from student-controlled action and do not describe counterfactuals as causal promises.
Report subgroup/error diagnostics only where group sizes are adequate, inspect plausible
proxies, and frame the system as outreach support rather than an autonomous decision.
Human participation must be voluntary and consented; collect no names, keep raw free
text outside version control, and report only aggregate or paraphrased evidence. Before
recruitment, confirm with the course instructor whether AIT approval is required and
obtain it where applicable.

## 4. Next actions, in order

1. Complete and review the validation-only grouped-PFI, ALE and subgroup audit tables.
2. Run the pre-specified 20-case explanation faithfulness/stability audit on validation.
3. Build and pilot the two-mode browser interface defined in `docs/interface_spec.md`:
   a decision-support demonstration view and a blinded A/B study view. Verify that study mode
   does not reveal the answer before submission.
4. After all acceptance checks pass, evaluate all frozen models once on the untouched test split.
5. Generate explanations, faithfulness/stability results, constrained counterfactuals,
   subgroup diagnostics, and the 10 pre-specified study cases.
6. Obtain consent and conduct the human study; code responses using two reviewers for
   the agreed subset.
7. Complete the model card and provide one clean-clone command that regenerates all
   reported tables and figures.

## 5. Repository map

- `XDS_Project_Proposal_Submission_Ready.docx` — submission candidate.
- `README.md` — public project overview and reproduction entry point.
- `eda_uci_data/eda_dropout.ipynb` — completed UCI EDA.
- `notebooks/uci_tfm_baseline.ipynb` — split and modelling overview.
- `src/modeling.py` — target, temporal policy, split, and model helpers.
- `src/explanations.py` — faithfulness, stability, and recourse primitives.
- `scripts/run_validation.py` — validation-only baseline and TFM runner.
- `tables/baseline_validation_metrics.csv` and `tables/tfm_validation_metrics.csv` —
  current feasibility evidence.
- `docs/human_study_instrument.md` — criterion-5 protocol.
- `docs/interface_spec.md` — decision-support demonstration and blinded-study prototype specification.
- `docs/MODEL_CARD.md` — living model card.
- `text_analysis/`, `data/text/`, `requirements-text.txt` — archived, out of scope.

## 6. Rubric alignment

| Criterion | Planned evidence |
|---|---|
| 1. Audience and decision | Student-support officer, post-semester-one outreach decision, asymmetric error costs |
| 2. Interesting model | TabICL with same-split logistic, tree, and XGBoost baselines |
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
python -m unittest discover -s tests -v
python scripts/run_validation.py
```

Do not open or report final-test performance until the model and explanation protocol
are frozen.
