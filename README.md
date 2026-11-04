# Trustworthy Explanations for Student Dropout Risk: Comparing Black-Box and Interpretable Models

## The Interpreters

## Group Members

Aye Khin Khin Hpone (Yolanda) - 125970, Nguyen Liem Son (Lucas) - 126729, Witchayda Theppithuk (Noey) - 127419, Han Htoo Zaw - st127305, Pyae Sone Han - st127366

## Current Development

**Model evaluation:** the single final evaluation is complete on 545 held-out cases under the
authorized local hashed freeze; preserve `artifacts/final_test.lock` and never rerun it.
Final metrics/intervals/reliability/subgroup outputs are in `tables/final_test/`. TabICL
ROC-AUC is 0.9566 and Brier 0.0740; paired intervals do not establish superiority over XGBoost
or EBM. At the 20% flag limit, test recall was 0.507 and precision was 0.991; this does not mean
all dropouts are identified or that outreach benefits flagged students.

**Validation eligibility sensitivity (exploratory, 4 Nov; distinct from the locked final test):**
of 108 flagged validation records, 25 had no first-semester evaluations and 83 had at least one.
Within the 495-record at-least-one-evaluation proxy subset, recomputing the 20% capacity flagged
99 records (all with Dropout labels; recall 0.559, ROC-AUC 0.9486). Evaluation presence does not
prove enrollment or reachability at the decision point; Enrolled outcomes remain excluded. See
`docs/HANDOFF.md` for the full counts and limitations.

Real study cases, 11 charts, and the canonical private assignment (50 main slots, 4 spares,
1 pilot) are prepared. The team reports that real-form build, privacy/export checks and pilot
are complete (4 Nov); **human-response collection and analysis remain pending**. The final-test
lock must not be rerun. See HANDOFF sections 8 and 12 and TASK_SPLIT for evidence, deviations,
pending independent review and next steps. Earlier unopened-test statements below describe the
pre-final workflow, not current status.

**2 Nov accelerated amendment:** the full explanation audit was stopped at the owner's request.
The default `python scripts/run_explanation_audit.py` now runs a one-case/two-seed validation
smoke check (47.37 seconds in the recorded run, single-case top-five overlap 0.8). It checks
execution, not explanation quality; faithfulness, background/perturbation stability and recourse
auditing are omitted and must be disclosed. `--full-audit` explicitly opts into the old workload.
The local hashed-freeze alternative and live-study status are documented in HANDOFF section 12.
These amendments supersede the original full-audit/tag prerequisites described below; genuine
study charts, consent/privacy, consistent assignments and the once-only test lock are retained.

EDA, validation-only model selection, and the explanation integration gate are complete.
The frozen development configuration uses TabICL 2.2.0 with four estimators, a top-20%
cohort-capacity outreach policy, grouped perturbations, and model-agnostic permutation
SHAP with 25 training-background rows and 67 evaluations. The real TabICL/SHAP check and
synthetic white-box check pass. Protocol 1.3 fixes signed semantic-group aggregation,
label-free risk-stratified validation audit cases, capacity-consistent recourse, suppression/proxy rules,
and paired final-test uncertainty. The single final evaluation is now complete under the
documented accelerated amendment; do not rerun it. Full explanation-quality auditing was omitted.

## Project Scope

In real-world educational settings, universities face challenges in identifying students who may be at risk of dropping out before it is too late to provide appropriate support. Students may discontinue their studies due to various factors, including academic difficulties, financial constraints, personal circumstances, and insufficient academic engagement. Although universities collect substantial amounts of student information, such as academic performance, enrolment records, and demographic characteristics, identifying potential dropout risks often requires considerable time and effort from academic advisors and student-support officers. As a result, students who need assistance may not always be identified early enough to receive effective intervention.

The primary project predicts student dropout risk using structured UCI administrative
data and a tabular foundation model (TFM), compared with conventional baselines
(logistic regression, depth-3 decision tree, XGBoost) and a native main-effects
Explainable Boosting Machine (EBM). The project evaluates whether the
model's explanations are faithful, stable, actionable, fair, and useful to a university
student-support officer.

That is the original research scope, not a claim that every property has been established.
The accelerated workflow provides model-performance diagnostics and limited explanation
execution evidence; full faithfulness/stability/recourse audits were omitted and the human
study remains pending.

The primary task is **Dropout (1) versus Graduate (0)**. Students labelled Enrolled are
excluded because their final outcome is unresolved; retaining Enrolled as a separate
class or grouping it with non-dropout is reserved for sensitivity analysis. This
restriction may introduce selection bias and limits the target population. The primary
prediction point is immediately after first-semester results, so second-semester
curricular variables are excluded as temporal leakage.

Short, consented written responses collected during the human study are the project's
only unstructured data. They are linked to pseudonymous participant and study case IDs
and support a small qualitative analysis of comprehension, actionability, and missing
information. Participants will be voluntarily recruited from the AIT community to assess
pseudonymised UCI cases; no AIT student records will be collected, and the study will not
validate deployment at AIT.
No external review corpus and no second predictive dataset are part of the current project.

## Datasets

- **Primary (modeling):** UCI "Predict Students' Dropout and Academic Success"
  https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success
  — 4,424 students × 36 features, individual-level, CC-BY 4.0.
- **Prospective qualitative data:** consented, pseudonymised responses from the human
  evaluation. These responses are not model inputs and are reported only in aggregate
  or through paraphrased examples.

## Repository guide

- `docs/HANDOFF.md` — the single internal document (start here): status, methodology,
  task list, human-study protocol, study instrument (Google Forms), model card, criteria alignment, audit
- `docs/TASK_SPLIT.md` — current report plan to 16 Nov: five workstreams, shared report/slides track, dependencies, fair-share hours, recruitment
- `eda_uci_data/eda_dropout.ipynb` — completed UCI EDA (run in the `.venv-core` env)
- `notebooks/uci_tfm_baseline.ipynb` — executable modeling/split overview
- `scripts/run_core.py` — regenerate validation-only baseline metrics
- `scripts/run_tfm_feasibility.py` — rerun the TFM feasibility gate
- `tables/baseline_validation_metrics.csv` and `tables/tfm_validation_metrics.csv` — current evidence
- `tables/ebm_global_terms_validation.csv` and `tables/ebm_local_contributions_validation.csv` — exact EBM explanation evidence
- `config/evaluation_protocol.json` — frozen validation/test evaluation protocol
- `The-Interpreters-ProjectProposal-XDS-125970-126729-127419-127305-127366.docx` — editable proposal submission candidate
- `The-Interpreters-ProjectProposal-XDS-125970-126729-127419-127305-127366.pdf` — rendered proposal submission candidate
- `requirements.txt` — pinned core modeling environment
- `docs/human_study_response_template.csv` — ratings/response schema for the human study
- `scripts/inspect_proposal_docx.py` — print the proposal DOCX's structure and word count
  (the submission DOCX is edited directly; there is no builder script)


## Reproduce the current checks

From the repository root after activating `.venv-core`:

```powershell
python -m unittest tests.test_modeling tests.test_explanations tests.test_auditing -v
python scripts/run_validation.py
python scripts/validate_explanation_pipeline.py
python scripts/run_validation_audits.py
python scripts/run_temporal_sensitivity.py
```

These commands use validation data only. For the complete current unit suite, run
`python -m unittest discover -s tests`, then `python forms/test_spec.py`.
The final test has already run: verify its saved evidence rather than evaluating it again.

## Team handover (2 Nov 2026)

See [HANDOFF section 12](docs/HANDOFF.md#12-member-handover-and-remaining-gates-2-nov-2026)
for per-member actions, the W1 audit runner, validation dry run, once-only final-test lock,
private study-case export, W5 scoring/coding commands and the remaining human-study steps.
Run `python scripts/reproduce_results.py` for tests and fixture-only checks; it never opens the
final test. Real-model validation regeneration is an explicit, expensive option.

The study uses W5's sealed assignment CSV throughout; form exports require explicit source
variants to prevent same-group case-order mislabelling. The team reports live form/privacy/pilot
acceptance complete; record the human-study findings only after actual collection and analysis.
Private fitted models, study lookups, case packs and chart handover files are intentionally
excluded from Git.
