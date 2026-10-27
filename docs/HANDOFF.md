# Project Handoff — Single Source of Truth

Updated: 2026-10-27. This file replaces the former `MODEL_CARD.md`, `human_study_instrument.md`,
`interface_spec.md`, `course_concept_alignment.md`, `proposal_final_audit.md` and `tasks.md`
(all still recoverable from git history). `README.md` is the public overview.

**Contents:** 1 Status · 2 Scope · 3 Completed work and results · 4 Methodology ·
5 Next actions (task list) · 6 Human-study protocol · 7 Interface specification ·
8 Model card · 9 Course-criteria alignment · 10 Proposal audit · 11 Repository, commands, hygiene

---

## 1. Status — what to show the professor and team

- Final title: **Trustworthy Explanations for Student Dropout Risk: Comparing Black-Box and
  Interpretable Models**.
- Submission files: `The-Interpreters-ProjectProposal-XDS-125970-126729-127419-127305-127366.docx`
  and the matching `.pdf` (re-exported from the DOCX on 2026-10-27).
- The proposal body is four pages with references alone on page 5 (verified in Word). Re-export
  the PDF after any further DOCX change and re-check the page count.
- The repository contains only the UCI predictive dataset. The unrelated OfS background-data
  branch has been removed from version control.
- 26 tracked, in-scope tests exist. On 2026-10-27, 25 passed in a partial environment; the
  26th (`test_ebm_uses_raw_named_features_and_main_effects_only`) errored only because the
  `interpret` package was not installed there. Run all 26 in the pinned `.venv-core` environment
  before submission. Three ignored tests belong to the local archived text branch and are not
  part of the repository.
- All reported model numbers are validation-only. The final test is untouched and no
  human-study result is claimed before data collection.

For an honest status update: methodology, validation evidence and the frozen protocol are
complete; the explanation audit, interface, one-time final-test run and human study are planned.

## 2. Scope decision

The project predicts first-year dropout risk from the UCI **Predict Students' Dropout and
Academic Success** dataset and evaluates whether local explanations of a tabular foundation
model are faithful, stable, actionable, fair and useful to a university student-support officer.

- Primary model: TabICL 2.2.0, four estimators.
- Baselines: logistic regression, depth-3 decision tree, XGBoost, native main-effects EBM.
- Primary task: Dropout (1) versus Graduate (0); decision point after first-semester results
  and before second-semester support.
- Explanation method: model-agnostic permutation SHAP on dropout probability.
- Evidence: deletion faithfulness, repeated-run and perturbation stability, constrained
  counterfactuals, subgroup/proxy diagnostics, two-group forward-simulation study.
- Unstructured data: only the consented, pseudonymised written responses from the human study,
  linked by pseudonymous participant and case IDs. Participants are voluntary AIT community
  members assessing UCI cases; no AIT student records are collected.

There is **no external review corpus and no second predictive dataset**. The old
`final.csv`/BERTopic branch is archived and must not supply claims, figures or findings.

**Ethics:** this is a class project, so basic research-ethics practice applies (voluntary
informed consent, minimal data, no identifiers, restricted access, stated withdrawal and
retention rules). No AIT ethics-board approval is sought because no AIT student records are
collected.

## 3. Completed work and results

- UCI EDA: 4,424 rows, 36 predictors, no missing values or duplicates (verified 2026-10-27).
- Temporal policy: second-semester variables excluded. Fixed stratified 70/15/15 split, seed 42,
  saved source-row IDs (3,630 rows after excluding Enrolled; 544 validation rows).
- Validation-only baselines and TabICL feasibility run.
- Protocol 1.3 frozen before test access: 1.1 added EBM; 1.2 froze semantic-group SHAP
  aggregation, label-free case selection, perturbation scaling, capacity-consistent recourse,
  subgroup suppression, proxy checks and paired uncertainty; 1.3 made the validation-split audit
  cases, optional narrative condition and precomputed-output interface rules explicit. None
  changed the split, seed, target, feature windows, models or test data.
- EBM exact additive reconstruction on all 544 validation cases: maximum error 3.3e-16.
- TabICL/permutation-SHAP integration passed on two validation cases (artifact maximum local-
  accuracy error 3.2e-8, bounded by 4.1e-8); synthetic white-box rank check 1.0.
- Capacity-based top-20% policy implemented (an earlier recall-plus-capacity formulation was
  rejected as mathematically infeasible). Semantic grouping, derived-feature recomputation,
  grouped permutation importance, ALE, subgroup suppression and all-feature proxy tables built.
- Admission-time sensitivity: TabICL ROC-AUC 0.874 vs 0.952 post-semester-one; capacity recall
  0.469 vs 0.507.

### Validation-only results (same cohort, top-20% capacity policy)

| Model | Balanced acc. | Macro-F1 | ROC-AUC | Recall | Precision |
|---|---:|---:|---:|---:|---:|
| Logistic regression | 0.754 | 0.768 | 0.945 | 0.507 | 1.000 |
| Depth-3 decision tree | 0.746 | 0.759 | 0.923 | 0.498 | 0.981 |
| XGBoost | 0.750 | 0.764 | 0.945 | 0.502 | 0.991 |
| Main-effects EBM | 0.750 | 0.764 | 0.946 | 0.502 | 0.991 |
| TabICL (four estimators) | 0.754 | 0.768 | 0.952 | 0.507 | 1.000 |

With 213 validation dropouts and 108 available flags (108/544 = 0.1985), maximum possible recall is
108/213 = 0.507; TabICL reaches it. TabICL Brier 0.0708, ECE 0.0186; EBM Brier 0.0757, ECE 0.0325.
Admission-time ROC-AUC: EBM 0.8753, XGBoost 0.8752, TabICL 0.8739. TabICL's 0.006 margin over EBM
is modest and does not establish operational superiority; the untouched test set is evaluated once
after all choices are frozen.

## 4. Methodology (frozen in `config/evaluation_protocol.json`, v1.3.0)

**Data and target.** Exclude Enrolled from the primary task (unresolved outcome; possible
selection bias). 17.3% of Dropout vs 3.4% of Graduate records have no first-semester
evaluations, so some dropouts may have left before the decision point; report this as an
eligibility limitation. Time-permitting sensitivity checks: Enrolled as a third class or grouped
with non-dropout; admission-time vs post-first-semester feature window.

**Faithfulness.** Training-only SHAP background (25 rows, 67 evaluations). Signed values are
summed within semantic groups before ranking by absolute total. Replace numerical features with
training medians and categoricals with training modes; compare ranked deletion with 50 random
orders; report area between curves with case-level uncertainty. This measures model reliance, not
intervention.

**Stability.** 20 cases from the **validation split**: four deterministic cases from each of five
predicted-risk strata, predictions only, labels unused, test split unopened. 10 runs per case
varying seed and background separately. Primary metric: mean pairwise top-five overlap
(`shared / 5`); rank correlation secondary. Perturb continuous features with Gaussian noise at 1%
of training SD, clip, recompute dependencies, keep perturbations changing probability by at most
0.01. Warn below 0.80 overlap.

**Actionability.** Keep immutable/historical fields fixed; only realistic tuition/debt-status
resolutions may change, distinguishing institutional support from student action. Success means
leaving the top-20% set after exact cohort reranking with other scores fixed; report no-recourse
cases; no universal 0.5 threshold; no causal promises.

**Fairness.** Retain all subgroup counts, suppress metrics below n=30 and state unavailable
comparisons. Report flag rate, TPR, FPR, precision, mean risk and calibration gap. Screen every
non-protected feature as a proxy with Cramér's V or correlation-ratio eta. Diagnostics do not
establish fairness. The system supports outreach prioritisation, not denial of services, and must
not frame financial disadvantage as a personal obligation.

**Separate reporting.** Real-data model results, explanation audits and human-study findings are
reported separately. Explanations describe model associations, not causes.

**Final test.** One same-test-set evaluation: discrimination, classification summaries, capacity
recall/precision, calibration (raw probabilities, no recalibration), runtime, and paired
2,000-resample bootstrap intervals. No tuning after test access.

## 5. Next actions (task list; none assigned yet)

Do not open or report final-test performance until the protocol is frozen and acceptance checks pass.

- [ ] **Faithfulness and stability audit** on the validation split (deletion curves, 10 reruns per
  case, top-5 overlap, perturbation test).
- [ ] **Interface build and pilot** (§7), using validation fixtures; the 10 study cases are loaded
  only after the final test run. Verify study mode reveals no answer or feedback until all 10
  scored cases are complete.
- [ ] **Final test evaluation**: run all frozen models exactly once on the untouched test split.
- [ ] **Generate study artifacts**: explanations, faithfulness/stability results, constrained
  counterfactuals, subgroup diagnostics, the 10 pre-specified study cases.
- [ ] **Human study** (§6): finalise class-level ethics basics (consent text, withdrawal deadline,
  course retention deadline, restricted raw-response access); recruit 8–10 (minimum 4); consent;
  run 1 practice + 10 scored cases; code responses (two reviewers on the agreed subset);
  analyse accuracy/time descriptively. Optional: narrative condition if at least 12 recruited.
- [ ] **Model card and reproducibility**: complete §8 with final results; provide one clean-clone
  command regenerating all tables and figures.
- [ ] Optional sensitivity checks (Enrolled handling; admission-time window).
- [ ] Hygiene: keep test set untouched; keep raw responses out of version control; verify the 26
  tests in `.venv-core`; keep repo scope clean (no OfS/text-analysis material); keep DOCX, README
  and this file in sync and re-export the PDF after every DOCX change.

## 6. Human-study protocol

The three free-text fields collected here are the project's only unstructured data (criterion 5:
explanation vs no explanation, forward simulation). Participants are voluntary AIT community
members assessing pseudonymised UCI cases; unless they are support professionals they are
intended-user proxies, so the study evaluates comprehensibility, not model validity or
effectiveness at AIT.

**Design**
- 8–10 participants (minimum 4), allocated as evenly as practicable by a recorded seed before
  they see any case; participants do not choose their group. Report shortfalls, unequal groups,
  sample size and role category. Collect no names or IDs. Claim no statistical significance.
- **Group A (control):** profile only. **Group B (explanation):** profile plus feature-contribution
  display that suppresses the base value, final score, probability, capacity boundary and
  predicted class. Neither group ever sees the model output before answering.
- Task per case: "What do you think the model predicts — will it flag this student as at-risk
  (yes/no)?" Same 10 cases (five flagged, five unflagged, randomised order). One unscored
  practice case with standardised instructions; Group B also gets a contribution-direction
  legend and comprehension check.
- No correctness feedback until all 10 scored responses are locked; debrief afterwards.
- Primary measure: participant-level accuracy across 10 cases; group means descriptive. Also
  confidence (1–5), integer seconds per case, and written responses. Never treat ~100 case
  responses as independent people.
- Case selection: after the one-time test run, pick five flagged and five unflagged cases
  deterministically across each group's risk range, outcome labels unused; never choose cases
  because the explanation looks persuasive.
- Exclusions: only withdrawn consent, incomplete task, or accidental exposure to the hidden
  output; log every exclusion with its reason.
- **Optional exploratory narrative condition** (only if at least 12 participants): split Group B
  into B1 (chart only) and B2 (chart plus plain-language narrative rendered by a verified local
  template from the same contributions; no free-form generated text, no output/probability/class).
  Seeded assignment; descriptive and separate from model results; with fewer than 12, omit B2.

**Consent text**

> You are invited to take part in a short class research activity about understanding an AI
> model. Participation is voluntary. You may stop at any time without penalty. Do not enter your
> name or other identifying information in free-text answers. Your responses will be stored under
> a random participant ID and reported only in aggregate or as paraphrased comments. You may
> withdraw until your responses are de-identified and combined into aggregate results; raw
> responses will be deleted at the course retention deadline. By selecting "I agree," you confirm
> that you understand this information and consent to participate.

Participation or refusal must not affect grades, standing, employment or services. Basic research
ethics applies (class project; no formal ethics-board process); collect nothing beyond what the
consent text describes. Pseudonymous is not fully anonymous: restrict raw-response access to the
research team. Use responses only for the course project. Record `consent = yes/no`; a "no" must
not proceed.

**Per-case response form** (schema: `docs/human_study_response_template.csv`)

| Field | Type | Purpose |
|---|---|---|
| `case_id` | string | pseudonymous ID (C01…); private lookup to the UCI source row |
| `participant_id` | string | pseudonymous code (P1…P10) |
| `group` | A / B (B1/B2) | A control; B explanation |
| `case_order` | integer | position in that participant's randomised sequence |
| `predicted_output` | at-risk / not-at-risk | guess at the model's output |
| `confidence` | 1–5 | self-reported confidence |
| `correct` | bool | scored afterwards by the researcher; hidden from participants |
| `time_seconds` | number | time on case |
| `rationale_freetext` | text | "Why do you think the model predicts that?" |
| `intervention_freetext` | text | "What would you tell this student to do?" |
| `missing_info_freetext` | text | "What extra info would help you decide?" |
| `consent` | yes / no | consent screen result; "no" must not proceed |
| `complete` | bool | whether the participant finished all 10 scored cases |
| `exclude_reason` | text | permitted exclusion reason, if any (withdrawal, incomplete, exposed output) |

**Analysis.** Light qualitative coding with a codebook written before comparing groups (definition
plus one paraphrased example per code, with an `other/unclear` code). Rationale themes (do
Group B cite the highlighted features?), intervention themes (compare with the counterfactuals;
code concreteness, feasibility before semester two, student- vs institution-controlled action,
unsupported causal assumptions), missing-information themes. Two members independently code at
least 20% of responses, blinded to group where practical; report raw agreement, resolve
disagreements, no formal reliability statistic unless the sample supports it. Report theme counts
by group descriptively.

**Rules.** No direct identifiers. Store responses in `data/human_study/responses.csv`
(git-ignored via `data/**`); commit only coded/theme summaries. Record time-on-task; take no
think-aloud notes, interviews or recordings. Report both group accuracies and sample size.
No subgroup comparisons with fewer than five participants.

**Status.** Done: officer role and decision; development model frozen on validation; response
schema. Open: 10 study cases (after final test); Group B rendering; per-participant randomisation;
interface (§7); consent screen, assignment, exclusion log, timer; codebook and two-coder subset;
one-person pilot (check nobody can see the answer); recruitment; coding. Do not collect responses
before the validation audits pass, the study cases are selected after the single final
evaluation, and Group B's view is rendered and piloted.

## 7. Interface specification

A lightweight browser research interface runs locally or in a controlled course environment,
demonstrates the frozen model and administers the study. It is not a production AIT service and
accepts no real AIT student records. It is not publicly deployed.

**Technical pipeline.** Both modes render versioned, precomputed Python outputs (no live
inference; model weights stay in Python): feature schema and temporal window; predictions under
the frozen preprocessing; frozen TabICL configuration and top-20% policy; precomputed explanations
and feature-group mapping; model-card version and limitation text. Case packs and response
submissions are validated on load: missing, extra, invalid or out-of-range fields are rejected,
never silently changed. An audit panel shows model, data-split and interface versions. Before
final-test access, parity is checked with training/validation fixtures; the 10 study cases are
loaded only after the single final evaluation, then an export-parity check runs without retuning.

**Mode A — decision support** (pre-approved, pseudonymised UCI test cases only): profile and
prediction time; frozen class and probability labelled "estimated model risk, not a causal or
guaranteed individual probability" with its calibration summary; local feature contributions;
faithfulness/stability summaries or a clear weak-evidence warning; immutable/historical factors
separated from changeable ones; a feasible counterfactual or explicit no-recourse result;
intended-use, non-causality and non-deployment warnings. It must not phrase a prediction as a
diagnosis, guarantee or automated decision.

**Mode B — blinded forward-simulation study:** consent screen before any case; pseudonymous
participant ID and seeded random A/B group; the same label-free panel in randomised order;
profile only for A; contributions for B with output, probability, capacity boundary, base value
and class hidden throughout; one practice case with a comprehension check; record predicted
output, confidence, integer seconds and the three free-text fields; B2 narrative only if enabled;
no feedback until all 10 are submitted; support withdrawal and record only permitted exclusion
reasons.

**Data handling.** No names, AIT IDs or administrative records. Raw responses and free text stay
outside version control and frontend bundles; model weights and credentials never enter frontend
code. Only aggregate results and paraphrased comments enter the report.

**Acceptance checks.** (1) Displayed probabilities match the pipeline (validation fixtures before
test; exported study cases after). (2) Group B cannot see anything revealing the output, and no
group gets feedback before all 10 scored cases. (3) Groups see identical profiles and differ only
in explanation visibility. (4) Case order, seed, timer and exclusion log are reproducible.
(5) Invalid fields are rejected and no real-person data are persisted. (6) Displayed model version,
explanation settings and limitations match the model card (§8).

**Gate.** Implementation starts after the model, capacity policy and explanation protocol are
frozen, using validation fixtures; study data collection starts after the study cases are loaded
and piloted.

## 8. Model card — student dropout early-warning model

**Status.** Development model and protocol selected; final test locked. Protocol 1.3 freezes the
EBM baseline plus validation-split audit cases, explanation, uncertainty, suppression, recourse
and human-study rules. The policy ranks each cohort and flags at most the top 20%.

**Intended use.** Decision support for a student-support officer prioritising voluntary outreach
after first-semester results. Not an autonomous decision system; must not be used to deny
enrolment, financial support or academic services.

**Target and time.** Dropout=1 vs Graduate=0; Enrolled excluded (unresolved); prediction
immediately after first-semester results; all second-semester curricular variables prohibited.

**Data.** UCI dataset 697, 4,424 students (3,630 after excluding Enrolled), Portuguese higher
education, CC BY 4.0. Features add first-semester pass rate and explicit no-enrolment/
no-evaluation indicators and exclude every second-semester curricular field.

**Splitting.** Stratified 70/15/15, seed 42, saved source-row IDs. Feasibility and all model
choices use train/validation only; test is used once after protocol freeze.

**Models and results (validation, not final).** TabICL 2.2.0, four estimators, CPU, seed 42:
ROC-AUC 0.9521, recall 0.5070, precision 1.0000, flag rate 0.1985, Brier 0.0708, ECE 0.0186.
Admission-time model: ROC-AUC 0.8739, recall 0.4695. EBM: ROC-AUC 0.9461, recall 0.5023,
precision 0.9907, Brier 0.0757, ECE 0.0325. The 0.0060 gap to TabICL is modest; the final
same-test-set comparison decides whether complexity is justified. Raw probabilities are evaluated
with Brier, 10-bin ECE and a reliability curve; no recalibration after test access.

**Explanation evidence.** Permutation SHAP (25 background rows, 67 evaluations) reconstructed
probabilities within 4.1e-8 on two validation cases (artifact max 3.2e-8); synthetic white-box
rank Spearman 1.0. EBM intercept plus main effects reconstruct validation probabilities within
3.3e-16 (intrinsic reference). Deletion, top-five, perturbation and human results are pending.

**Fairness and limitations.** Retain subgroup counts, suppress metrics below n=30, report the
all-feature proxy screen. Single institution; may not transfer across countries or time.
Associations are not causal diagnoses; a feasible counterfactual may not exist for every student.

## 9. Course-criteria alignment

| Criterion | Planned evidence |
|---|---|
| 1. Audience and decision | Student-support officer, post-semester-one outreach, asymmetric error costs |
| 2. Model and baseline | TabICL vs logistic, tree, XGBoost, main-effects EBM on one split |
| 3. Faithfulness | Ranked-vs-random deletion curves, area between curves |
| 4. Stability | 20 cases × 10 runs, top-five overlap, rank correlation, perturbation test |
| 5. Human evidence | Two-group forward simulation, time, qualitative responses |
| 6. Actionability | Feasibility-constrained counterfactuals, explicit no-recourse cases |
| 7. Complexity | Architecture disclosure and honest baseline comparison |
| 8. Ethics | Consent, data minimisation, protected-group and proxy diagnostics |
| 9. Reproducibility | Fixed split/seeds, pinned environment, tests, model card, regeneration command |

| Course concept | Implementation | Evidence |
|---|---|---|
| Stakeholder-centred explanations | Officer prioritising outreach under limited capacity | Proposal §2; §7 |
| Interpretability–accuracy trade-off | TabICL vs LR, tree, XGBoost, EBM; 0.006 margin reported as modest | `src/modeling.py`; tables |
| Intrinsic vs post-hoc | EBM exact additive terms; permutation SHAP for TabICL | EBM tables; SHAP artifact |
| Global vs local | Local SHAP plus grouped permutation importance and ALE | `src/explanations.py`; `scripts/run_validation_audits.py` |
| Model-agnostic explanation | Permutation SHAP wraps TabICL probability | `permutation_shap_values` |
| Faithfulness vs plausibility | Group-summed SHAP, matched grouped deletion vs random | `aggregate_shap_by_group`; `deletion_curve` |
| Interpretable model as ground truth | Synthetic additive white-box rank check | `scripts/validate_explanation_pipeline.py` |
| Background dependence | Seed and background variation evaluated separately | Protocol JSON |
| Correlated/off-manifold inputs | Semantic grouping, derived-feature recomputation, ALE over PDP | `semantic_feature_groups`; `accumulated_local_effect` |
| Stability | Label-free stratified cases, top-five overlap, clipped 1% perturbations | Protocol JSON |
| Mental-model alignment | Blinded forward simulation | §6 |
| Actionable recourse | Immutable/historical separation; capacity-consistent changes | `constrained_binary_counterfactuals` |
| Fairness and bias | Flag rate, TPR, FPR, precision, risk, calibration gap; proxy checks | `src/auditing.py` |
| Correlation is not causation | SHAP, ALE, counterfactuals described as model behaviour | Proposal §2, §5, §6 |
| Explanation lifecycle | Validation freeze, one final test, model card, interface safeguards | Protocol JSON; this file |

LIME, PDP, ICE and risk scores are not added merely to maximise method count: SHAP explains
individual predictions, grouped permutation importance measures global reliance, ALE examines
global effects in observed regions, and the EBM plus transparent baselines test whether black-box
complexity is justified.

## 10. Proposal audit (2026-09-19, revised 2026-10-27)

After the first audit the submission DOCX was edited directly: audit cases moved to the
validation split; separate-reporting, non-causal and fairness wording sharpened; interface text
uses precomputed outputs and validation fixtures; optional narrative condition and class-level
ethics wording added; think-aloud notes dropped; protocol 1.3 recorded; EBM error stated as
3.3e-16. Word renders five pages (four body, references on page 5, about 3,250 words including
references); the PDF was re-exported. A numerical check against the tables, artifacts and UCI
data confirmed every quoted figure.

| Criterion | Proposal evidence | Status |
|---|---|---|
| Audience and decision | §2: one officer, one decision, timing, both error costs | Complete |
| Model and baseline | §5.1: five models, one frozen split, one final same-test-set comparison | Complete; final test pending |
| Faithfulness | §5.2: signed group SHAP, grouped deletion, 50 random orders, white-box check | Complete design; integration evidence |
| Stability | §5.3: label-free five-stratum validation cases, 10 runs, 0.80 warning | Complete design |
| Human evidence | §5.4, §5.7: blinded two-group study, practice case, 10 cases, coding | Complete design; recruitment pending |
| Actionability | §5.5: immutable vs feasible; exact cohort reranking | Complete design and implementation |
| Complexity | §7: non-decomposable TabICL vs exactly additive EBM | Complete |
| Ethics and data handling | §6: licence, consent, class-level ethics, suppression, proxies, safeguards | Complete |
| Documentation | §8: split/seed, pinned environment, protocol 1.3, 26 tests, model card | Complete for proposal |

The course guideline is internally inconsistent about Complexity (5 marks) and Ethics (5 vs 10
marks); Sections 6 and 7 cover both readings. No accuracy, faithfulness, stability, fairness,
human-benefit or deployment claim may be upgraded beyond the proposal wording until the matching
task in §5 is complete.

## 11. Repository, commands, hygiene

**Map.** `README.md` (public overview) · this file · `config/evaluation_protocol.json` (frozen
protocol) · `src/` (`modeling.py`, `explanations.py`, `auditing.py`) · `scripts/` (validation and
audit runners) · `tests/` · `tables/` and `artifacts/` (validation evidence) ·
`eda_uci_data/eda_dropout.ipynb` and `notebooks/uci_tfm_baseline.ipynb` ·
`docs/human_study_response_template.csv` · the proposal DOCX and PDF.
`scripts/finalize_proposal_docx.py` and `docs/proposal_source.docx` are **superseded**: the
submission DOCX has been edited directly, so running the builder would overwrite those edits.

**Commands** (repository root, `.venv-core`):

```powershell
python -m unittest tests.test_modeling tests.test_explanations tests.test_auditing -v
python scripts/run_validation.py
python scripts/validate_explanation_pipeline.py
python scripts/run_validation_audits.py
python scripts/run_temporal_sensitivity.py
```

**Git and data hygiene.** Delete a tracked file from Git and disk with `git rm -- <path>`; stop
tracking but keep locally with `git rm --cached -- <path>` plus a `.gitignore` entry; check with
`git ls-files -- <path>` first. Ordinary deletion does not erase history; rewrite history only for
exposed secrets or serious size problems, after coordinating a force-push with all collaborators.
The removed OfS ZIP remains recoverable from earlier commits and contains no secret.
Ignored local text-branch material (`text_analysis/`, `data/text/`, `requirements-text.txt`,
`EDA/`) is out of scope and must not be recommitted.
