# Trustworthy Explanations for Student Dropout Risk: Comparing Black-Box and Interpretable Models

## The Interpreters

## Group Members

Aye Khin Khin Hpone (Yolanda) - 125970, Nguyen Liem Son (Lucas) - 126729, Witchayda Theppithuk (Noey) - 127419, Han Htoo Zaw - 127305, Pyae Sone Han - 127366

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

**Human study:** collection is complete for all 50 assigned main participants: 25 saw profiles
only and 25 saw profiles plus explanation charts. All 50 consented, confirmed adult status,
completed all 10 scored cases, and matched their sealed form variants; no response was excluded.
Mean participant accuracy was 0.916 for profiles only and 0.900 with explanations. The exploratory
between-group difference (explanations minus profiles only) was -0.016, with a stratified-bootstrap
95% interval [-0.060, 0.032] and permutation p=0.612. This does not show an accuracy benefit from
the explanation charts. Mean confidence was 0.208 points higher with explanations (exploratory
95% interval [0.016, 0.416]); completion time differed by -3.2 minutes [−8.72, 2.04]. Group B's
practice chart checks were both correct for 21/25 participants. Aggregate, privacy-safe outputs are
in `tables/human_study/` and `figures/human_study/`. The 1,500 written answers were coded in one pass
(themes plus proposal 5.7 intervention ratings; aggregate tables in `tables/report_ready/`). The planned
independent double-coding of 20% was not done, so inter-coder agreement was not measured.

**Interface (research demonstration, added 11 Nov):** a local page shows the saved model results for
543 validation students: flag status and rank, the five main reasons, how stable those reasons are, and
whether clearing fees or debt would change the flag. An optional what-if mode re-scores an edited
student with the frozen model on your own computer. It was built after the human study, was not
tested with users and is not deployed. See [Run the interface](#run-the-interface).

**Explanation-audit timeline:** on 2 Nov the planned pre-final full explanation audit was stopped
at the owner's request.
The default `python scripts/run_explanation_audit.py` now runs a one-case/two-seed validation
smoke check (47.37 seconds in the recorded run, single-case top-five overlap 0.8). It checks
execution, not explanation quality; faithfulness, background/perturbation stability and recourse
auditing are omitted and must be disclosed. `--full-audit` explicitly opts into the old workload.
The local hashed-freeze alternative and live-study status are documented in HANDOFF section 12.
These amendments superseded the original pre-final full-audit/tag prerequisite. A separate,
subsequent validation-only W1 audit was completed on 11 Nov across all 544 validation cases. It
records faithfulness, seed/background/perturbation stability, pair-masking and constrained-recourse
diagnostics. It used a reproducible refit with the frozen settings because the original serialized
fitted model was not supplied; it does not retroactively change the 2 Nov gate status or test result.

EDA, validation-only model selection, and the explanation integration gate are complete.
The frozen development configuration uses TabICL 2.2.0 with four estimators, a top-20%
cohort-capacity outreach policy, grouped perturbations, and model-agnostic permutation
SHAP with 25 training-background rows and 67 evaluations. The real TabICL/SHAP check and
synthetic white-box check pass. Protocol 1.3 fixes signed semantic-group aggregation,
label-free risk-stratified validation audit cases, capacity-consistent recourse, suppression/proxy rules,
and paired final-test uncertainty. The single final evaluation is complete under the documented
accelerated amendment; do not rerun it. The later supplementary W1 audit is under `W1_analysis/`.

## Project Scope

In real-world educational settings, universities face challenges in identifying students who may be at risk of dropping out before it is too late to provide appropriate support. Students may discontinue their studies due to various factors, including academic difficulties, financial constraints, personal circumstances, and insufficient academic engagement. Although universities collect substantial amounts of student information, such as academic performance, enrolment records, and demographic characteristics, identifying potential dropout risks often requires considerable time and effort from academic advisors and student-support officers. As a result, students who need assistance may not always be identified early enough to receive effective intervention.

The primary project predicts student dropout risk using structured UCI administrative
data and a tabular foundation model (TFM), compared with conventional baselines
(logistic regression, depth-3 decision tree, XGBoost) and a native main-effects
Explainable Boosting Machine (EBM). The project evaluates whether the
model's explanations are faithful, stable, actionable, fair, and useful to a university
student-support officer.

That is the original research scope, not a claim that every property has been established.
The project now contains final predictive diagnostics, a later validation-only explanation audit,
and a completed 50-participant comprehension study. It still does not establish causal recourse,
intervention benefit, fairness in deployment, or external validity.

The primary task is **Dropout (1) versus Graduate (0)**. Students labelled Enrolled are
excluded because their final outcome is unresolved; retaining Enrolled as a separate
class or grouping it with non-dropout is reserved for sensitivity analysis (grouped
sensitivity completed 11 Nov on validation only: `tables/sensitivity/`, HANDOFF §5). This
restriction may introduce selection bias and limits the target population. The primary
prediction point is immediately after first-semester results, so second-semester
curricular variables are excluded as temporal leakage.

Short, consented written responses collected during the human study are the project's
only unstructured data. They are linked to pseudonymous participant and study case IDs
and support a small qualitative analysis of comprehension, actionability, and missing
information. Participants were adult volunteers (a convenience sample, about ten recruited by each
team member) who assessed pseudonymised UCI cases; no AIT student records were collected, and the
study does not validate deployment at AIT.
No external review corpus and no second predictive dataset are part of the current project.

## Datasets

- **Primary (modeling):** UCI "Predict Students' Dropout and Academic Success"
  https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success
  — 4,424 students × 36 features, individual-level, CC-BY 4.0.
- **Qualitative data (collected 11 Nov):** consented, pseudonymised responses from the human
  evaluation (50 participants, 1,500 written answers; git-ignored). These responses are not model inputs and are reported only in aggregate
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
- `tables/human_study/` and `figures/human_study/` — aggregate completed-study results
- `tables/report_ready/` and `figures/report_ready/` — centralized later-report assets
- `docs/REPORT_PREPARATION_BRIEF.md` — report claims, asset map and remaining non-report work
- `docs/QUALITATIVE_CODEBOOK.md` — finalized primary-theme codes and coding workflow
- `scripts/build_human_study_report.py` — privacy-safe quantitative study analysis
- `scripts/build_report_assets.py` — regenerate aggregate report tables and figures without model inference
- `scripts/build_demo_card.py` — validation-only static adviser-card demonstration; never a study/test case
  (output in `figures/demo_card/`)
- `scripts/run_enrolled_sensitivity.py` — optional W3.7 Enrolled-handling sensitivity, validation only
  (output in `tables/sensitivity/`)
- `scripts/run_ta_feedback_checks.py` — TA feedback numbers from the saved W1 validation cases (who the
  108 flags are, a "passed zero units" rule, top reasons, adding up the bars); no model run
- `scripts/run_no_protected_sensitivity.py` — TA feedback: validation-only refit without the six protected
  attributes, against an all-feature refit control (output in `tables/sensitivity/no_protected_*`)
- `docs/TA_FEEDBACK_FINAL_REPORT_NOTES.md` — each TA point marked [DOC] or [CODE], with the numbers
  to use in the final report
- `scripts/check_w1_refit_identity.py` — confirms W1's refit matches the frozen model on validation
  (`artifacts/w1_refit_identity.json`: max difference 0.00001, 108/108 flags identical)
- `scripts/launch_interface.py` — builds and opens the local research interface (see [Run the interface](#run-the-interface))
  (`interface/student_support_demo.html`; validation students only, saved results,
  not used in the study); add `--what-if` to edit a validation student's first-semester results or
  fee status and re-predict locally with the frozen model
- `scripts/whatif_server.py` — local what-if server used by `launch_interface.py --what-if`
- `W1_analysis/` — later 544-case validation explanation audit (a refit with the frozen settings,
  not the frozen bundle); see its README for what is rerunnable
- `scripts/inspect_proposal_docx.py` — print the proposal DOCX's structure and word count
  (the submission DOCX is edited directly; there is no builder script)


## Run the interface

The interface is a research demonstration of how the model could support decisions about whom to
offer a support contact. It is not a deployed service and must not be used for real students.

**Prerequisites:** from the repository root, activate the pinned environment (`.venv-core`, Python 3.12,
`pip install -r requirements.txt`). The saved page needs only files already in Git. What-if mode also
needs the private frozen model `data/final_evaluation/selected_model.joblib` (git-ignored, about 2 MB;
obtain it from the model owner and never commit it).

**1. Saved page (no model, works offline):**

```powershell
python scripts/launch_interface.py            # builds interface/student_support_demo.html and opens it
python scripts/launch_interface.py --no-open  # build only; open the HTML file yourself later
```

The HTML file is self-contained: double-click it, or send it to someone, to view it in any browser.
Section 5 (what-if) shows as unavailable in this mode.

**2. What-if mode (frozen model, local only):**

```powershell
python scripts/launch_interface.py --what-if              # opens http://127.0.0.1:8765/
python scripts/launch_interface.py --what-if --port 8766  # if port 8765 is busy
```

Startup takes about 20 seconds (it hash-checks the model against `artifacts/final_test.lock`, scores
the 544 validation students and builds the context cache described below). Keep the terminal open while you use the page; press Ctrl+C to stop.
The server listens only on your own computer (127.0.0.1).

**Using the page:**
1. Choose a student with the **Student** list, **◀ Previous / Next ▶**, the ← → keys, the **Example**
   menu, by clicking the risk curve, or with `#student=<record id>` in the address (e.g. `#student=174`).
2. Read sections 1–4: whether the student is flagged (top 108 of 544 = 20%), the five main reasons,
   how stable those reasons are, and whether clearing fees or debt would change the flag. Hover over
   the curve, bars, stability rows and **i** icons for explanations.
3. In section 5 (what-if mode only), change first-semester results or fee/debt/scholarship status, or
   use a quick example, then press **Predict** (under 1 second; a few seconds if "also recompute
   the reasons" is ticked). Startup takes about 20 seconds: the server scores all 544 students, then
   stores the training context in TabICL's in-memory cache and checks that it reproduces the frozen
   scores and ranking exactly before using it (otherwise it falls back to about 10 seconds per
   prediction). The result shows the new estimate, rank and flag, and a purple diamond on
   the section 1 curve. **Reset to recorded values** restores the student.

**What what-if mode allows:** only validation students, and only first-semester units, evaluations,
grade, fees, debt and scholarship can change; age, gender, nationality, family and background fields are
fixed. Impossible combinations (for example more units passed than enrolled) are rejected with a reason.
Other students' scores stay fixed. Nothing is saved or retrained and the test split is never read.
Results show how the model responds, not what would happen to a student or what they should do.

**Troubleshooting:**
- *Section 5 says "not available":* you opened the saved HTML file; start with `--what-if` and use the
  `http://127.0.0.1:8765/` address instead.
- *Blank or outdated page:* an older server may still hold the port. Close its terminal (or stop the
  Python process) and start again, or use `--port 8766`; then reload with Ctrl+F5. The server now
  refuses to start if the port is taken.
- *"needs the private frozen model file":* the model file is missing; the saved page still works.

**Checked (11 Nov, with the context cache on):** what-if reproduces all 104 saved fee/debt scenario
predictions, including the 27 that move a student out of the top 20% (largest probability difference
0.0000041, same ranks); an unedited student returns their saved rank, flag and score exactly; and
recomputed reasons for students 174 and 916 match the saved ones within 0.000001. Tests: `tests/test_interface.py`, `tests/test_whatif.py`.

## Reproduce the current checks

From the repository root after activating `.venv-core`:

```powershell
python -m unittest tests.test_modeling tests.test_explanations tests.test_auditing -v
python scripts/run_validation.py
python scripts/validate_explanation_pipeline.py
python scripts/run_validation_audits.py
python scripts/run_temporal_sensitivity.py
python scripts/run_enrolled_sensitivity.py
python scripts/run_ta_feedback_checks.py
python scripts/run_no_protected_sensitivity.py
python scripts/build_report_assets.py
```

These commands use validation data only. For the complete current unit suite, run
`python -m unittest discover -s tests`, then `python forms/test_spec.py`.
The final test has already run: verify its saved evidence rather than evaluating it again.
The private raw survey workbook and row-level free text are intentionally not committed. The
aggregate human-study tables and figures are reproducible with the commands documented in
`docs/HUMAN_STUDY_RESULTS.md` when the authorized private inputs are present.

## Team handover (2 Nov 2026)

See [HANDOFF section 12](docs/HANDOFF.md#12-member-handover-and-remaining-gates-2-nov-2026)
for per-member actions, the W1 audit runner, validation dry run, once-only final-test lock,
private study-case export, W5 scoring/coding commands and the remaining human-study steps.
Run `python scripts/reproduce_results.py` to regenerate every report artefact from saved evidence:
tests, form checks, fixture charts, W1 topic tables (checked byte-identical against the committed
ones), report-ready tables/figures, the local interface page and the release-readiness check. It never opens the final test.
`--validation-results` adds the slow validation refits, W1-refit identity check, demo card and
Enrolled sensitivity; `--human-study` rebuilds the aggregate human-study tables when the restricted
private files are present.

The study uses W5's sealed assignment CSV throughout; form exports require explicit source
variants to prevent same-group case-order mislabelling. The team reports live form/privacy/pilot
acceptance complete; collection (50 participants) and analysis were completed on 11 Nov.
Private fitted models, study lookups, case packs and chart handover files are intentionally
excluded from Git.
