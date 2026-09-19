# Student Retention and Dropout Analysis

## The Interpreters

Catching Students Before They Leave: Faithful, Stable, and Actionable Early-Warning Explanations for First-Semester Academic Risk

## Group Members

Aye Khin Khin Hpone (Yolanda) - 125970, Nguyen Liem Son (Lucas) - 126729, Witchayda Theppithuk (Noey) - 127419, Han Htoo Zaw - st127305, Pyae Sone Han - st127366

## Current Development

EDA, validation-only model selection, and the explanation integration gate are complete.
The frozen development configuration uses TabICL 2.2.0 with four estimators, a top-20%
cohort-capacity outreach policy, grouped perturbations, and model-agnostic permutation
SHAP with 25 training-background rows and 67 evaluations. The real TabICL/SHAP check and
synthetic white-box check pass. The untouched test split remains unopened until every
validation audit and interface acceptance check is complete.

## Final Project Scope

The primary project predicts student dropout risk using structured UCI administrative
data and a tabular foundation model (TFM), compared with conventional baselines
(logistic regression, depth-3 decision tree, XGBoost). The project evaluates whether the
model's explanations are faithful, stable, actionable, fair, and useful to a university
student-support officer.

The primary task is **Dropout (1) versus Graduate (0)**. Students labelled Enrolled are
excluded because their final outcome is unresolved; retaining Enrolled as a separate
class or grouping it with non-dropout is reserved for sensitivity analysis. This
restriction may introduce selection bias and limits the target population. The primary
prediction point is immediately after first-semester results, so second-semester
curricular variables are excluded as temporal leakage.

Short, consented written responses collected during the human study are the project's
only unstructured data. They are linked to study case IDs and support a small qualitative
analysis of comprehension, actionability, and missing information. Participants will be
voluntarily recruited from the AIT community to assess pseudonymised UCI cases; no AIT
student records will be collected, and the study will not validate deployment at AIT.
No external review corpus and no second predictive dataset are part of the current project.

## Datasets

- **Primary (modeling):** UCI "Predict Students' Dropout and Academic Success"
  https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success
  — 4,424 students × 36 features, individual-level, CC-BY 4.0.
- **Prospective qualitative data:** consented, anonymised responses from the human
  evaluation. These responses are not model inputs and are reported only in aggregate
  or through paraphrased examples.
- **Background context only:** OfS outcomes statistics (`EDA/`) — group-level, not used
  for modeling.

## Repository guide

- `docs/HANDOFF.md` — current status, decisions, and next actions (start here)
- `eda_uci_data/eda_dropout.ipynb` — completed UCI EDA (run in the `.venv-core` env)
- `notebooks/uci_tfm_baseline.ipynb` — executable modeling/split overview
- `scripts/run_core.py` — regenerate validation-only baseline metrics
- `scripts/run_tfm_feasibility.py` — rerun the TFM feasibility gate
- `tables/baseline_validation_metrics.csv` and `tables/tfm_validation_metrics.csv` — current evidence
- `docs/MODEL_CARD.md` — living model card
- `config/evaluation_protocol.json` — frozen validation/test evaluation protocol
- `XDS_Project_Proposal_Submission_Ready.docx` — synchronized proposal submission candidate
- `requirements.txt` — pinned core modeling environment
- `docs/human_study_instrument.md` — the human-evidence (criterion 5) study design
- `docs/interface_spec.md` — decision-support demo and blinded-study interface requirements
- `docs/course_concept_alignment.md` — mapping from lecture concepts to project evidence

The `text_analysis/`, `requirements-text.txt`, and `data/text/` materials are retained
only as an archived exploratory branch. They are outside the approved proposal scope and
must not be included in project findings.

## Reproduce the current checks

From the repository root after activating `.venv-core`:

```powershell
python -m unittest discover -s tests -v
python scripts/run_validation.py
python scripts/validate_explanation_pipeline.py
python scripts/run_validation_audits.py
python scripts/run_temporal_sensitivity.py
```

These commands use validation data only. Do not evaluate on the test split until the
frozen protocol's remaining explanation and interface acceptance checks pass.
