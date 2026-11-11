# Project Handoff — Single Source of Truth

Updated: 2026-11-11. This file replaces the former `MODEL_CARD.md`, `human_study_instrument.md`,
`interface_spec.md`, `course_concept_alignment.md`, `proposal_final_audit.md` and `tasks.md`
(all still recoverable from git history). `README.md` is the public overview;
`docs/TASK_SPLIT.md` assigns the remaining work to five workstreams.

**Contents:** 1 Status · 2 Scope · 3 Completed work and results · 4 Methodology ·
5 Next actions (task list) · 6 Human-study protocol · 7 Study instrument (Google Forms) ·
8 Model card · 9 Course-criteria alignment · 10 Proposal audit · 11 Repository, commands, hygiene ·
12 Current handover, amendments and evidence

**Completion attribution:** "Completed by Yolanda" identifies work she performed.
"Integrated and verified by Yolanda" identifies her integration/checking of teammates' existing
implementations, preserving original authorship. Partial tasks name the completed component;
neither label certifies omitted analyses or independent review. Current remaining work is in
TASK_SPLIT §4.

---

## 1. Status — what to show the professor and team

- Final project report deadline: **Mon 16 Nov 2026**; the report schedule in
  `docs/TASK_SPLIT.md` supersedes earlier project dates and lists task owners.
- Final title: **Trustworthy Explanations for Student Dropout Risk: Comparing Black-Box and
  Interpretable Models**.
- Submission files: `The-Interpreters-ProjectProposal-XDS-125970-126729-127419-127305-127366.docx`
  and the matching `.pdf` (re-exported from the DOCX on 2026-10-27).
- The proposal body is four pages with references alone on page 5 (verified in Word). Re-export
  the PDF after any further DOCX change and re-check the page count.
- The repository contains only the UCI predictive dataset. The unrelated OfS background-data
  branch has been removed from version control.
- **94 unit tests pass** in the pinned Python 3.12 environment; separate form checks pass.
  Run `python -m unittest discover -s tests` and `python forms/test_spec.py`.
- The **single final evaluation is completed** on 545 cases. Preserve the completed
  `artifacts/final_test.lock`; never rerun the final test. Results are in section 8.
- The planned pre-final explanation audit was stopped and replaced by an exploratory one-case/two-seed
  execution check. A separate validation-only W1 audit later completed all 544 validation cases;
  it does not retroactively change the original gate or final test.
- The real 11-case pack, 11 charts and locally sealed canonical assignment exist privately.
  The team reports real-form build, live privacy/acceptance checks, exports and pilot complete
  (4 Nov); pre-collection coordination and private assignment handover are reported complete.
- Human-response collection and quantitative analysis are complete: 50 participants, 25 per group,
  500 scored case responses and no exclusions. Qualitative coding completed in one coding pass on 11 Nov (independent 20% double-coding not done; agreement not measured).

For an honest status update: model evaluation, the later W1 validation audit, private case/chart
export, live form/privacy/pilot gates, collection and quantitative study analysis are complete.
Independent human review of report claims and a second coder for 20% of the written answers remain. Historical schedules and
pre-final full-audit requirements below are superseded by the timeline recorded in section 12.

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
  linked by pseudonymous participant and case IDs. Participants are adult volunteers
  recruited by team members, assessing UCI cases; no AIT student records are collected.

There is **no external review corpus and no second predictive dataset**. The old
`final.csv`/BERTopic branch is archived and must not supply claims, figures or findings.

**Ethics:** this is a class project, so basic research-ethics practice applies (voluntary
informed consent, minimal data, no identifiers, restricted access, stated withdrawal and
retention rules). No formal ethics approval is recorded. The absence of AIT student records
does not itself establish an exemption: the coordinator should confirm the applicable
course/institutional requirements before recruitment.

## 3. Completed work and results

- UCI EDA: 4,424 rows, 36 predictors, no missing values or duplicates (verified 2026-10-27).
- Temporal policy: second-semester variables excluded. Fixed stratified 70/15/15 split, seed 42,
  saved source-row IDs (3,630 rows after excluding Enrolled; 544 validation rows).
- Validation-only baselines and TabICL feasibility run.
- Protocol 1.3 frozen before test access: 1.1 added EBM; 1.2 froze semantic-group SHAP
  aggregation, label-free case selection, perturbation scaling, capacity-consistent recourse,
  subgroup suppression, proxy checks and paired uncertainty; 1.3 made the validation-split audit
  cases and the Google Forms study-instrument rules (replacing the planned custom interface) explicit. None
  changed the split, seed, target, feature windows, models or test data.
- EBM exact additive reconstruction on all 544 validation cases: maximum error 3.3e-16.
- TabICL/permutation-SHAP integration passed on two validation cases (artifact maximum local-
  accuracy error 3.2e-8, bounded by 4.1e-8); synthetic white-box rank check 1.0.
- Capacity-based top-20% policy implemented (an earlier recall-plus-capacity formulation was
  rejected as mathematically infeasible). Semantic grouping, derived-feature recomputation,
  grouped permutation importance, ALE, subgroup suppression and all-feature proxy tables built.
- Admission-time sensitivity: TabICL ROC-AUC 0.874 vs 0.952 post-semester-one; capacity recall
  0.469 vs 0.507.
- **Exploratory eligibility-proxy check (4 Nov; validation only):** applied the saved fitted model
  to the existing 544 validation rows; its bundle hash matches `artifacts/final_test.lock`, and
  the original validation confusion matrix was reproduced. The top-20% rule flagged 108 records;
  all 108 had Dropout labels. Of the 49 validation records with zero first-semester evaluations
  (36 Dropout, 13 Graduate), 25 were flagged (all Dropout); 83 flagged records had at least one
  evaluation. Among the 495 records with at least one evaluation (177 Dropout), recomputing the
  top-20% capacity within this subset flagged 99: TN=318, FP=0, FN=78, TP=99; recall 0.559,
  precision 1.000, ROC-AUC 0.9486. This is post-hoc validation sensitivity analysis, not a new
  confirmatory result. Evaluation presence is only a proxy and does not establish enrollment,
  availability to support, or reachability at the decision point. Enrolled outcomes remain excluded;
  this analysis provides no performance evidence for them. The final-test lock was not rerun or changed.

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
is modest and does not establish operational superiority. The subsequent once-only final results
are in section 8; the final evaluation is complete and must not be repeated.

**Validation eligibility sensitivity (exploratory, 4 Nov).** Of 108 records flagged under the
original validation-cohort ranking, 25 (23.1%) had no first-semester evaluations and 83 had at
least one. There were 49 such zero-evaluation records in validation, of which 36 were Dropouts.
Restricting to records with one or more evaluations (495 total; 177 Dropouts) and recalculating the
same 20% within-subset capacity flagged 99; all 99 had Dropout labels (recall 0.559, precision
1.000, ROC-AUC 0.9486; TN=318, FP=0, FN=78, TP=99). This post-hoc sensitivity does not replace
the primary result, prove actual eligibility, or establish that a support officer could reach those
students. It does not evaluate Enrolled students, which remain excluded. “100% precision” here means
only that the selected top-20% flags in these particular validation subsets had Dropout labels; it
does not mean all Dropouts were found, that the model generalises perfectly, or that outreach would
benefit flagged students. On the full validation cohort, 105 of 213 Dropouts were not flagged.

## 4. Methodology (frozen in `config/evaluation_protocol.json`, v1.3.0)

The faithfulness/stability/actionability paragraphs below describe the **original planned
full-audit methods**, not completed analyses. Under the accelerated amendment those empirical
audits were omitted. The actual smoke evidence and once-only final results are in sections 8/12.

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

## 5. Next actions (ownership in TASK_SPLIT; implementation handover in section 12)

Current checklist under the accelerated amendment (section 12):

- [x] **Exploratory explanation execution check**: one validation case, two seeds.
  Full faithfulness/stability/recourse audits were omitted, not passed.
- [x] **Local hashed freeze and once-only final evaluation**: five models, 545 cases;
  completed lock retained. No mandatory publication tag or independent approval is claimed.
- [x] **Generate real cases/charts and final model card**: one practice plus ten scored cases,
  genuine contributions, 11 charts and aggregate final subgroup/calibration/comparison evidence.
- [x] **Private handover and assignment (team-reported complete 4 Nov)**: the pack/charts and
  sealed assignment were handed over through restricted storage; the private lookup is limited to
  the designated scorer. Keep codes, seed and lookup out of Git.
- [x] **Real study form build and pilot (team-reported complete 4 Nov)**: the team reports the
  real forms, privacy/consent checks, live acceptance/export checks and pilot complete. Individual
  acceptance outcomes are not recorded here; this is not an independent live audit.
- [x] **Pre-collection arrangements (team-reported complete 4 Nov)**: the team reports the form,
  consent/privacy, response-access/export and pilot gates complete.
- [x] **Main human-study collection and quantitative analysis (11 Nov)**: all 50 assigned main
  participants completed (25/25 groups), with 500 scored case responses and no exclusions.
  Aggregate scoring, bootstrap/permutation comparisons, case/flag summaries and privacy-safe figures
  are complete in `tables/human_study/`, `figures/human_study/` and `docs/HUMAN_STUDY_RESULTS.md`.
- [x] **Qualitative coding (single pass, 11 Nov)**: all three free-text fields coded with the codebook
  plus the section 5.7 intervention ratings; aggregate tables in `tables/report_ready/human_study_theme_*`
  and `human_study_intervention_flags_by_group.csv`; results in `docs/HUMAN_STUDY_RESULTS.md`.
- [ ] **Second coder (optional) and retention**: independent 20% double-coding was not done, so agreement
  is not measured (deviation); private data must still be deleted on the retention date.
- [x] **Clean-clone/evidence verification (4 Nov)**: 62 unit tests, four form variants and all
  22 saved final-evidence hashes passed; protocol hash matched the manifest and lock. The
  once-only final evaluation was not rerun. This clean-clone run preceded the later tag-mode
  bundle-hash, workbook, privacy and demo-card regressions; the current local suite has 97 passing tests (11 Nov, after coding, report-tooling, interface, what-if and TA-feedback tests).
- [x] **Optional sensitivity checks (11 Nov; exploratory, validation-only, not used for model
  selection).** Admission-time window: `tables/temporal_window_validation_metrics.csv`.
  TA feedback checks: `python scripts/run_ta_feedback_checks.py` (saved cases, no model run) and
  `python scripts/run_no_protected_sensitivity.py` (refit without protected attributes: ROC-AUC
  0.9521 → 0.9503, 103/108 flags unchanged, gender recall gap 0.19 → 0.10); summary and report
  wording in `docs/report_notes/TA_FEEDBACK_FINAL_REPORT_NOTES.md`.
  Enrolled handling: `python scripts/run_enrolled_sensitivity.py` → `tables/sensitivity/`.
  Enrolled rows (794, never in `split_ids.csv`) were split 70/15/15 with seed 42; only the 70% and
  15% shares were used, and the test split was not touched. (A) The frozen model scored the
  119-student Enrolled validation share at median 0.354 (graduates 0.064, dropouts 0.990). If those
  students share the validation cohort, the 20% rule flags 7 of 132 of them (5%, although they are
  18% of the cohort). With the slot count held at 108, 3 slots move to Enrolled students and
  validation dropout recall falls from 0.507 to 0.493. (B) Grouping Enrolled with non-dropout:
  the frozen model's ROC-AUC on the grouped validation set is 0.924 (0.952 on binary validation);
  a TabICL refit on the grouped target reaches 0.929 with Brier 0.085 (frozen 0.111), and logistic
  regression 0.925. Enrolled flags are neither right nor wrong (outcomes unresolved), and grouping
  them as non-dropout is an assumption. Three-class modelling was not run.
- [x] **W5.1 static demo card (11 Nov):** `python scripts/build_demo_card.py` →
  `figures/demo_card/`. One validation student (row 916; middle-ranked flagged case, excluding the
  practice case), frozen model, frozen SHAP settings; the script refuses study cases and shows no
  recourse advice.
- [x] **W1 reproducibility (11 Nov):** `W1_analysis/03_Full_Audit/Code/topics/run_all.py` reruns
  from the saved 544 cases in seconds and regenerates every topic table byte-identically (UTF-8
  fix applied for Windows). The heavy audit scripts are archived (original `W1_Noey_Enhanced/`
  layout). W1 explains a **refit** with the frozen settings, not the frozen model bundle. That refit
  reproduces the frozen model on all 544 validation students (max probability difference 0.00001;
  108/108 flags identical; `artifacts/w1_refit_identity.json`). See `W1_analysis/README.md`.
- [x] **Qualitative-coding tooling (11 Nov):** `assign_human_coding.py` now has `reconcile`
  (agreed codes, adjudication sheet for disagreements) and a by-group/by-flag `summary`; dry-run on
  synthetic data passed. Real coding is blocked only on the private `data/human_study/send_log.csv`.
- [x] Hygiene: the raw workbook and row-level responses remain outside version control; the final
  test was not rerun; current unit/form checks and aggregate manifests are verified. Keep the final
  report, README and this file synchronized when report preparation begins.

## 6. Human-study protocol

The three free-text fields collected here are the project's only unstructured data (criterion 5:
explanation vs no explanation, forward simulation). Participants are adult volunteers recruited
by team members, assessing pseudonymised UCI cases; unless they are support professionals they are
intended-user proxies, so the study evaluates comprehensibility, not model validity or
effectiveness at AIT.

**Design**
- 50 participants (10 recruited by each team member; minimum 40 with at least 18 per group),
  allocated 25/25 by a recorded seed before they see any case; participants and recruiters do not
  choose the group (each participant gets a pre-assigned link to the Group A or Group B form). If a
  participant does not complete, the next recruit inherits that slot's group (4 spare slots, two per
  group). Report shortfalls, unequal groups,
  sample size and role category. Collect no names or IDs. Claim no statistical significance.
- **Group A (control):** profile only. **Group B (explanation):** profile plus feature-contribution
  display that suppresses the base value, final score, probability, capacity boundary and
  predicted class. Neither group ever sees the model output before answering.
- Task per case: "What do you think the model predicts — will it flag this student as at-risk
  (yes/no)?" Same 10 cases (five flagged, five unflagged), in one of two orders per
  group (a seeded order or its exact reverse). One unscored
  practice case with standardised instructions; Group B also gets a contribution-direction
  legend and comprehension check.
- Both groups' instructions state the at-most-top-20% full-cohort policy and explicitly distinguish it
  from the selected 10-case sample; the sample's actual flag mix is not disclosed to participants
  (Yolanda's authorised review, 2 Nov).
- Record and report Group B practice-chart answers without correction or automatic exclusion for wrong
  answers. Report correct counts and denominators per item and for both items together.
- No correctness feedback until all 10 scored responses are locked; debrief afterwards.
- Primary measure: participant-level accuracy across 10 cases; group means descriptive. Also
  confidence (1–5), self-reported total time (online; Google Forms cannot time cases), and written
  responses. Never treat ~500 case responses as independent people.
- Accuracy measures agreement with the model's hidden flag, not correctness about actual dropout.
  The ten cases form a deliberately balanced, fixed panel; results do not estimate real-cohort
  performance or generalise to unseen cases. With the base value, full score and cohort boundary
  hidden, even faithful contribution bars cannot uniquely determine the outreach flag. Interpret
  group differences as task-specific forward-simulation evidence, not proof of explanation quality.
- Case selection: after the one-time test run, pick five flagged and five unflagged cases
  deterministically across each group's risk range, outcome labels unused; never choose cases
  because the explanation looks persuasive.
- Exclusions: only withdrawn consent, incomplete task, or accidental exposure to the hidden
  output; log every exclusion with its reason.
- The optional plain-language narrative condition was considered and **dropped** (time budget);
  Group B sees the contribution display only.

**Consent text (original template; the live wording is `CONSENT_TEXT` in `forms/build_spec.py`).** On 30 Oct
the team removed the withdrawal deadline, named contact and retention date from the consent text to keep it
flexible; participants contact the person who sent them the form. W4 still records the course retention date
privately for deletion (W4.10).

> You are invited to take part in a short class research activity about understanding an AI
> model's predictions. It takes about 30–40 minutes. You will look at 11 student
> profiles (one practice and ten scored), guess whether the model flags each student as at-risk, rate
> your confidence, and write three short answers per profile. We record your answers, confidence and
> how long you say it took, under a random participant code. We do not ask for your name or any identifying
> information, so please do not enter any in your answers. Participation is voluntary, you must be 18
> or older, and you may stop at any time without penalty. Your responses are kept in access-restricted
> storage available only to the research team and reported only in aggregate or as paraphrased
> comments. To withdraw, give your participant code to the person who sent you the form; once
> responses are de-identified and combined into aggregate results, they can no longer be separated
> out. The risks are no greater than
> everyday computer use and there is no direct benefit. By ticking "I agree" and confirming that you
> are 18 or older, you confirm that you understand this information and consent to take part.

Participation or refusal must not affect grades, standing, employment or services. Basic research
ethics applies; confirm the applicable course/institutional requirements before recruitment.
Collect nothing beyond what the
consent text describes. Pseudonymous is not fully anonymous: restrict raw-response access to the
research team. Use responses only for the course project. Record `consent = yes/no`; a "no" must
not proceed.

**Per-case response form** (schema: `docs/human_study_response_template.csv`)

| Field | Type | Purpose |
|---|---|---|
| `case_id` | string | pseudonymous ID (C01…); private lookup to the UCI source row |
| `participant_id` | string | pseudonymous code (P1…P10) |
| `group` | A / B | A control; B explanation |
| `case_order` | integer | position in that participant's sequence (set by the form variant) |
| `predicted_output` | at-risk / not-at-risk | guess at the model's output |
| `confidence` | 1–5 | self-reported confidence |
| `correct` | bool | scored afterwards by the researcher; hidden from participants |
| `time_seconds` | number | self-reported total time in seconds (the form's last question in minutes × 60; same value on each of a participant's rows); per-case time is not recorded |
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
unsupported causal assumptions), missing-information themes. Coding is shared: each member codes
about 10 participants' responses (not their own recruits), blinded to group where practical, and a
random 20% is coded again by a second member; report raw agreement, resolve
disagreements, no formal reliability statistic unless the sample supports it. Report theme counts
by group descriptively.

**Rules.** No direct identifiers. Form responses live in one restricted Google Sheet (no email
collection, no sign-in); the analysis-ready long CSV `data/human_study/responses.csv` is
git-ignored via `data/**`; commit only coded/theme summaries. Keep a backup only in the
restricted (not link-shared) Drive subfolder described in `docs/TASK_SPLIT.md` rule 4, never in the
open team folder, and delete it everywhere (Forms, Sheet, CSV, Drive trash) at the retention deadline.
Total time is self-reported in the form (sessions are online, with no observer); take no
think-aloud notes, interviews or recordings. Report both group accuracies and sample size.
No subgroup comparisons with fewer than five participants.

**Status.** Done: officer role and decision, response schema, local model freeze, once-only final
evaluation, ten real scored cases plus practice, Group B chart images and locally sealed assignment.
Team-reported complete (4 Nov): real Google Forms (§7), live privacy/consent/routing and export
checks, and one-person pilot. Open: send and exclusion log, actual recruitment, response collection and coding. Disclose the omitted
explanation audits.

## 7. Study instrument — Google Forms (replaces the planned custom interface)

**Decision (27 Oct 2026, D8).** Participants answer Google Forms instead of a custom browser
interface, to protect the project schedule. The study design, cases, questions, consent and privacy
rules are unchanged. The decision-support demonstration (formerly "Mode A") becomes a static example
card (screenshots from a validation fixture) in the report and slides. It accepts no real AIT student
records. Deviations are listed in `docs/TASK_SPLIT.md` §8 and must be disclosed in the final report.

**How it is built.** Case packs follow one JSON contract (task W2.2). Python renders the explanation
images: a profile card per case and, for Group B only, a contribution chart (direction and magnitude)
that shows **no** base value, score, probability, capacity boundary or class. A script (Apps Script or
Forms API) builds **four forms**: Group A and Group B, each in two case orders (a seeded order and its reverse). A seeded
list assigns each participant slot a code and a variant; the participant's link is pre-filled with the
code. Forms are built on validation fixtures first; the 10 study cases and the practice case are added
only after the single final evaluation, then a parity check runs without retuning.

**Form content.** Required consent and 18+ confirmation; participant code; instructions; one unscored
practice case (Group B also gets the neutral contribution-direction legend and a comprehension check);
the 10 scored cases, each with the profile (A) or profile plus chart (B), a yes/no "will the model flag
this student as at-risk?", confidence 1–5 and the three free-text prompts; a thank-you page. No quiz
mode, no answers or feedback shown.

**Settings and sessions.** No email collection, no sign-in, response editing off, summary charts hidden,
form not publicly listed; responses go to one restricted Sheet. Sessions are online and
unsupervised: each participant opens their own pre-filled link on their own device (changed 31 Oct;
disclosed as a limitation). W4 gives each recruiter the next unused link, nobody chooses the group,
and W4's send log records each code's recruiter, send date, submission and any exclusion (no names, no times).

**Data handling.** No names, AIT IDs or administrative records. Raw responses and free text stay out of
version control; model outputs used for scoring stay private. Only aggregate results and paraphrased
comments enter the report. A transform script (W2.8) turns the wide Sheet export into the long CSV in
`docs/human_study_response_template.csv`.

**Acceptance checks (W2.6).** (1) All four forms build and displayed values match the exports
(validation fixtures before test; exported study cases after). (2) Group B sees nothing that reveals the
output, and no feedback appears anywhere. (3) Groups see identical profiles and differ only in
explanation. (4) Assignment and case order reproduce from the seed. (5) Privacy settings are correct
(no emails, no sign-in, summary hidden, Sheet restricted). (6) Form text matches the model card and
consent text. (7) A dry-run export transforms into the right long CSV.

**Current gate.** Final evaluation, real cases/charts and local assignment sealing are complete.
Build the real forms closed; privacy and all seven acceptance checks plus one pilot must pass
before participant links are sent. The old pre-final fixture gate was waived for evaluation,
not marked passed; no further model evaluation is needed.

## 8. Model card — student dropout early-warning model

**Status (updated 11 Nov).** The five frozen models were evaluated once on 545 held-out cases
under the owner-authorized local hashed freeze (2 Nov); the completed final-test lock prevents
reruns. That evaluation was an accelerated protocol deviation without independent approval: the
pre-final explanation audit was replaced by a one-case smoke check and live form acceptance was
incomplete at the time. Since then, a full 544-case validation explanation audit (11 Nov, post-final,
on a refit verified to match the frozen model), the 50-participant human study, an Enrolled-handling
sensitivity check and a validation-only demo card have been completed. The written answers were coded in a single pass (agreement not measured). The policy ranks each cohort and flags at most the top 20%.

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

**Final held-out results (545 cases; one run).**

| Model | ROC-AUC | Brier | Recall at 20% capacity | Precision at 20% capacity |
|---|---|---|---|---|
| Logistic regression | 0.9525 | 0.0822 | 0.5070 | 0.9908 |
| Depth-3 tree | 0.9099 | 0.0999 | 0.5023 | 0.9817 |
| XGBoost | 0.9557 | 0.0711 | 0.5070 | 0.9908 |
| Main-effects EBM | 0.9539 | 0.0768 | 0.5117 | 1.0000 |
| TabICL | 0.9566 | 0.0740 | 0.5070 | 0.9908 |

Every model flags 109/545 cases (20%). TabICL balanced accuracy is 0.7520, macro-F1 0.7664,
10-bin ECE 0.0323, and confusion matrix TN=331, FP=1, FN=105, TP=108. Its ROC-AUC advantage
over EBM is 0.0027 (paired 95% bootstrap interval -0.0071 to 0.0138); over XGBoost it is
0.0009 (-0.0061 to 0.0086). These do not establish superiority over either comparator.
XGBoost has the lowest point-estimate Brier score; EBM has the highest capacity recall/precision.
Do not select or tune a different model after seeing the held-out results. Full tables, 2,000-resample
paired intervals, reliability plots and descriptive subgroup/proxy screens are in `tables/final_test/`.

**Explanation evidence (integration checks, pre-final).** Permutation SHAP (25 background rows,
67 evaluations) reconstructed probabilities within 4.1e-8 on two validation cases (artifact max
3.2e-8); synthetic white-box rank Spearman 1.0. EBM intercept plus main effects reconstruct
validation probabilities within 3.3e-16 (intrinsic reference). There are 33 input features;
`max_evals=67` is `2 x 33 + 1`, the explainer's evaluation budget per case, not 67 cases. For shap's
PermutationExplainer this is exactly one forward-and-backward permutation, the minimum allowed, so seed
instability may partly reflect the budget; a larger-budget rerun was not done (see
`docs/report_notes/TA_FEEDBACK_FINAL_REPORT_NOTES.md`). Grouped
permutation importance and ALE are in `tables/`.

**Explanation audit (W1, post-final, validation only; `W1_analysis/`).** Run after the final test on
all 544 validation students (the proposal planned 20) with a TabICL refit using the frozen settings.
The refit reproduces the frozen model on validation: largest probability difference 0.00001 and
108/108 identical flags (`artifacts/w1_refit_identity.json`). Report it as post-hoc evidence, not a
pre-final gate that passed.
- *Faithfulness:* SHAP-ranked deletion vs 50 random group orders; mean ranked-minus-random area 1.557
  (95% bootstrap interval 1.476 to 1.643), positive in 536/544 cases. This shows model reliance on the
  ranked groups under training-reference masking, not causal effects.
- *Stability (mean top-five overlap; 0.80 warning level):* seed 0.818 (213/544 cases below 0.80),
  background sample **0.745 (411/544 below; below the warning level)**, small grade perturbations
  0.996 (0 below). Background choice is the main source of instability; show this, do not hide it.
- *Most influential groups (mean absolute grouped SHAP):* first-semester progress 0.277,
  first-semester participation 0.053, tuition fees up to date 0.051, course 0.042, scholarship 0.019.
- *Recourse (debtor/tuition only, rank-based):* 17 of 108 flagged students have a feasible
  administrative change that moves them out of the top 20%; 91 have none.
- *Surrogates:* six local surrogates approximate TabICL on held-out masked inputs; the lowest pooled
  holdout MAE is 0.0224 (Lasso with pairs). This measures approximation of TabICL, not outcome
  accuracy. The log records 579 convergence warnings across 342 cases' surrogate fits.

**Fairness and limitations.** Retain subgroup counts, suppress metrics below n=30, report the
all-feature proxy screen. Single institution; may not transfer across countries or time.
Associations are not causal diagnoses; a feasible counterfactual may not exist for every student.
Final descriptive gender-group flag rates were 0.1224 and 0.3238, with recalls 0.4100 and
0.5929 respectively (coded groups 0/1). These differences do not demonstrate fairness or causation.
Protected attributes were retained in this research model to reflect the available dataset and
permit descriptive subgroup/proxy audits, not because they are established as appropriate outreach
criteria. These analyses do not authorize prioritising real students by protected status; that
would require a separate, justified and governed decision and further evaluation. Small-group
performance metrics are suppressed in the tables; cross-country/generalisation claims remain
unsupported. Clean-clone/evidence verification completed 4 Nov without rerunning the final test.

**Enrolled sensitivity (W3.7, 11 Nov; exploratory, validation only, not used for model selection;
`tables/sensitivity/`).** The frozen model scores Enrolled students between the two labelled groups
(median 0.354 vs graduates 0.064 and dropouts 0.990). If an Enrolled share joins the validation
cohort, it receives 7 of 132 flags (5%) despite being 18% of the cohort; with slots fixed at 108,
3 move to Enrolled students and dropout recall falls from 0.507 to 0.493. Grouping Enrolled with
non-dropout lowers the frozen model's ROC-AUC from 0.952 to 0.924; a grouped-target refit reaches
0.929 (Brier 0.085 vs 0.111). Enrolled flags are neither right nor wrong (outcomes unresolved). A
three-class model was not run.

**Decision-support demonstration (W5.1).** `figures/demo_card/demo_card_validation.png`: one
validation student (not a study case), frozen model and SHAP settings, labelled estimate, five
largest contributions and limitations, deliberately without recourse advice.

**Local research interface (reduced section 5.6, added 11 Nov).** `python scripts/launch_interface.py`
builds and opens `interface/student_support_demo.html`: a self-contained page for 543 validation
students (practice/study cases refused, test split never read) showing outreach status and cohort rank
(with a risk-curve chart marking the top-20% cut-off, the student and any fee/debt rank changes), a
stability chart against the 0.80 warning line,
the five largest grouped SHAP contributions, that student's W1 stability warning (below 0.80), the
debtor/tuition recourse check labelled as model behaviour rather than advice, adviser topics and an audit
panel (model hash, protocol 1.3.0, split, refit identity). Invalid saved cases are rejected, not repaired.
Scores come from the W1 refit (frozen model within 0.00001, 108/108 identical flags). The saved page has
no live inference (the optional what-if mode below runs the frozen model locally) and no blinded-study mode, was built after the study and was not evaluated with users
(deviations D5/D8 narrowed accordingly).

**What-if mode** (`python scripts/launch_interface.py --what-if`): a local server on 127.0.0.1 loads the frozen model (hash-checked against the lock) and re-predicts a validation student after edits to first-semester results or fee/debt/scholarship status only; demographic and family fields are fixed. Inputs must be consistent and within the train/validation range or are rejected; rank is recomputed against the other 543 frozen scores; an optional fresh explanation takes a few seconds. Speed: TabICL has no weights trained on this data, so each uncached prediction re-reads all training students as context (about 9 s on CPU even for one student). At startup the server builds TabICL's own in-memory key-value cache of that context (the model file is unchanged) and uses it only if it reproduces the frozen cohort (largest gap 0.000011, identical ranking); a prediction then takes about 0.05 s. Re-audit with the cache (11 Nov): all 104 saved fee/debt scenario predictions match (largest gap 0.0000041, same ranks) and recomputed explanations for students 174 and 916 match the saved ones within 0.000001. Nothing is saved, nothing is retrained and the test split is never read. What-if results have no stability audit or fee/debt check and describe model responses, not effects on students. Audit (11 Nov): all 27 saved fee/debt recourse scenarios reproduce through the what-if mode (largest probability difference 0.0000034, same ranks), 16 unchanged students (including ranks 107-110) return their saved rank, flag and score, and recomputed explanations for students 174 and 916 equal the saved ones. Live inference goes beyond proposal section 5.6, which planned precomputed outputs only; report it as an added local demonstration feature. Page features for first-time readers: a how-to panel, numbered question headings, example and previous/next navigation, hover tooltips (curve, bars, stability, field help) and per-field units, recorded values and input checks.

**Recourse and human-study interpretation for reporting.** Fee/debtor status is an administrative
feature that can reflect financial circumstances. The dataset's association between fee status and a
later Dropout label does not establish causal direction: financial difficulty may affect fee status,
fee status may be a marker of other circumstances, and the label records a later outcome. A change
to a model score after changing this feature is not evidence that paying fees prevents dropout, is
feasible for a student, or should be recommended.

**Human study (forward simulation; completed 11 Nov; `docs/HUMAN_STUDY_RESULTS.md`).** 50 adult
volunteers (25 profiles only, 25 profiles plus contribution charts), all consented and completed;
no exclusions. Participants guessed the model's hidden flag for 10 cases (5 flagged, 5 not); Group B
also saw bar directions and relative sizes, never probabilities or labels.
- *Accuracy (agreement with the model's flag):* 0.916 profiles only vs 0.900 with charts; difference
  -0.016 (95% bootstrap interval -0.060 to 0.032; exploratory permutation p = 0.61). No accuracy
  benefit from the charts was shown.
- *Confidence:* 0.208 points higher with charts (interval 0.016 to 0.416, exploratory).
- *Time (self-reported total):* -3.2 minutes with charts (interval -8.72 to 2.04).
- *Case C01* (not flagged): 0.20 accuracy with charts vs 0.60 without. Leaving C01 out changes the
  difference to +0.027 (interval -0.013 to 0.076), still inconclusive. On unflagged cases overall,
  accuracy was 0.808 with charts vs 0.864 without.
- *Chart comprehension:* 21/25 Group B participants answered both practice chart checks correctly.
- *Written answers (single coding pass; agreement not measured):* with charts, 72% of rationales cited
  the chart; without, answers cited academic results or several factors. Suggestions were mostly academic
  support, financial/fee help (flagged cases) or no action (unflagged); 76% named a concrete step and
  2.8% asserted an unsupported cause. Participants most wanted attendance/enrolment status and work or
  family circumstances.

The study measures whether proxy users can anticipate the model's output. It does not establish
support-officer effectiveness, better interventions, student outcomes or deployment suitability.

**Final-report framing (notes, not the final report).** Start with the practical question in plain
language: whether a model can help prioritise a limited number of voluntary support contacts after
first-semester results. Define the cohort and outcome (Dropout versus Graduate; Enrolled excluded),
explain that the 20% rule means selecting up to one fifth of a cohort for outreach, then state the
central results: (1) TabICL is not shown to beat simpler models, and the interpretable EBM is
statistically indistinguishable; (2) explanations rely on the ranked features but vary with the
background sample; (3) charts raised confidence without raising accuracy. Keep model, audit and
human-study evidence separate (proposal section 9), and disclose the deviations in TASK_SPLIT
section 8. Avoid protocol jargon on page one; do not imply that retrospective metrics certify
real-world use.

## 9. Course-criteria alignment

The tables below retain the original evidence plan, not a list of completed findings.
Full faithfulness, multi-case stability and constrained-recourse audits were omitted under
the accelerated amendment (a later post-final 544-case validation audit is reported in section 8).
The human study is complete (section 8; `docs/HUMAN_STUDY_RESULTS.md`); subgroup/proxy screens
are descriptive and do not certify fairness. Do not present implemented helpers or planned
analyses as empirical evidence.

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
| Background dependence | Seed/background variation planned separately; full audit omitted | Protocol JSON; section 12 deviation |
| Correlated/off-manifold inputs | Semantic grouping, derived-feature recomputation, ALE over PDP | `semantic_feature_groups`; `accumulated_local_effect` |
| Stability | Label-free stratified cases, top-five overlap, clipped 1% perturbations | Protocol JSON |
| Mental-model alignment | Blinded forward simulation | §6 |
| Actionable recourse | Immutable/historical separation; capacity-consistent changes | `constrained_binary_counterfactuals` |
| Fairness and bias | Flag rate, TPR, FPR, precision, risk, calibration gap; proxy checks | `src/auditing.py` |
| Correlation is not causation | SHAP, ALE, counterfactuals described as model behaviour | Proposal §2, §5, §6 |
| Explanation lifecycle | Validation freeze, one final test, model card, study-form safeguards | Protocol JSON; this file |

LIME, PDP, ICE and risk scores are not added merely to maximise method count: SHAP explains
individual predictions, grouped permutation importance measures global reliance, ALE examines
global effects in observed regions, and the EBM plus transparent baselines test whether black-box
complexity is justified.

## 10. Proposal audit (2026-09-19, revised 2026-10-27)

After the first audit the submission DOCX was edited directly: audit cases moved to the
validation split; separate-reporting, non-causal and fairness wording sharpened; interface text
uses precomputed outputs and validation fixtures (later replaced by Google Forms, see §7); class-level ethics wording added (the optional
narrative condition was considered and dropped); think-aloud notes dropped; protocol 1.3 recorded; EBM error stated as
3.3e-16. Word renders five pages (four body, references on page 5, about 3,190 words including
references); the PDF was re-exported. A numerical check against the tables, artifacts and UCI
data confirmed every quoted figure.

| Criterion | Proposal evidence | Status |
|---|---|---|
| Audience and decision | §2: one officer, one decision, timing, both error costs | Complete |
| Model and baseline | §5.1: five models, one frozen split, one final same-test-set comparison | Complete; single final test completed and locked |
| Faithfulness | §5.2: signed group SHAP, grouped deletion, 50 random orders, white-box check | Complete design; integration evidence |
| Stability | §5.3: label-free five-stratum validation cases, 10 runs, 0.80 warning | Complete design |
| Human evidence | §5.4, §5.7: blinded two-group study, practice case, 10 cases, coding | Completed 11 Nov: 50 participants (25/25), single-pass coding (agreement not measured) |
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
`notebooks/eda_dropout.ipynb` and `notebooks/uci_tfm_baseline.ipynb` ·
`docs/human_study_response_template.csv` · the proposal DOCX and PDF.
The submission DOCX is edited directly (only the appointed report editor; every workstream writes its own section and slides, see `docs/TASK_SPLIT.md` §5). The old
builder `scripts/finalize_proposal_docx.py` and `docs/proposal_source.docx` were removed on
2026-10-27 because re-running them would have overwritten the current DOCX; both remain in git
history. `scripts/inspect_proposal_docx.py` prints the DOCX structure and word count.

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

## 12. Member handover and remaining gates (2 Nov 2026)

### Latest W3 completion record (2 Nov, evening; supersedes earlier pending-status notes)

The owner authorized completing W3 and committing the combined work directly on `main`.
The local freeze and **single final evaluation are completed**, with lock status `completed`.
The final evaluation was not repeated when a later explanation-export process was interrupted:
only the unfinished export was restarted from the saved model, before any study pack existed.
No scientific code/configuration was changed after creating the snapshot.

- Frozen manifest SHA-256: `37a021d34d722e7dfec9e72481f41b1c28655b20d412cfc506abc244b99422b3`.
- Protocol SHA-256: `ae7bfe66294cec154622e6828862f575a02413a7e32099b1a53e3e1a0c1c44ac`.
- Five-model evaluation: **545 held-out cases**, completed lock `artifacts/final_test.lock`;
  final aggregates/plots and 22-file hash manifest under `tables/final_test/`. Do not rerun it.
- Private fitted model: `data/final_evaluation/selected_model.joblib`; its SHA-256 is bound in
  the completed lock. Preserve it and `data/local_freeze/` privately; a Git clone alone does not
  contain these assets and must not trigger another final evaluation.
- Real export: `data/study_cases/case_pack_study.json` and
  `data/study_cases/private_lookup_study.json`: **one validation practice plus ten test cases**,
  genuine signed grouped SHAP contributions, five flagged/five unflagged scored cases selected
  from saved predictions without using outcome labels. Format/provenance checks pass.
- Chart handover: **11 genuine chart PNGs** under `forms/out/images_study/`; the renderer's
  forbidden-text check passes. The team reports live insertion and acceptance complete (4 Nov);
  detailed parity results are not reproduced here.
- Validation dry-run tables were generated before the accelerated amendment. Their manifest
  deliberately records that earlier protocol hash; they are historical dry-run evidence, not the
  final frozen protocol. The smoke artifact records the reduced explanation evidence.

**W3 deliverable handover:** use the real case pack and chart PNGs only through restricted study
storage. Give the private lookup only to the designated scorer/coordinator; never upload it to
participant-facing Forms/Drive assets or Git. The canonical private assignment is generated and
locally sealed; its CSV, seed/rules and `assignment_seal.json` stay in ignored
`data/human_study/`. The team reports the real forms, privacy/consent checks, acceptance/export
checks and pilot complete (4 Nov). Keep their detailed records with the study materials; do not
infer undocumented per-check results from this summary. Private assignment acknowledgement and
main response collection remain outstanding. Clean-clone/evidence verification was completed
4 Nov without rerunning the final test.

### Latest local consistency audit (2 Nov, after assignment sealing)

**Local verification completed by Yolanda; not independent or live acceptance.**

The live-form observations in the historical audit below describe the earlier forms and response
Sheet as inspected on 2 Nov. They are superseded as a current status by the team's 4 Nov report
that the real build, privacy/consent checks, acceptance/export checks and pilot are complete.
Per-check evidence for the current build is retained with the study materials, not reproduced here.

- All **62 unit tests** and separate four-variant form checks pass. The test runner's guard
  rejection messages and mocked "Final test complete" output are expected synthetic test paths,
  not new final-model runs.
- Snapshot/current scientific inputs and exact checkpoint match; saved model digest and completed
  final-test lock remain intact. All **44 aggregate-file hashes** across final and validation
  manifests verify. Final confusion counts, capacity recall/precision, balanced accuracy and ECE
  arithmetic agree with saved tables; this does not independently recompute ROC-AUC/bootstrap draws.
- Real pack/profile/split provenance, deterministic ten-case selection and hidden flags verify
  against saved predictions. Eleven PNGs validate; one genuine chart was visually inspected.
  This local audit did not independently inspect all charts or verify live profile/order parity;
  that is distinct from the team's reported completion of live acceptance checks.
- Canonical assignment validates and reproduces byte-for-byte from its private seed: 50 main,
  25/group, A1/A2/B1/B2 counts 13/12/12/13; four spares, one B1 pilot. CSV matches its local seal.
  No codes or seed were put in public documentation.
- Real pack builds into four compatible form variants **in memory only**; seed-11 order is shared
  across groups and reversed for A2/B2. This check wrote no real spec/links and deployed no Forms.
- Private model/pack/lookup/charts/assignment/seed/seal remain Git-ignored. Documentation changes
  pass `git diff --check`; scientific source/configuration were not changed.

**Corrections/improvements applied:** task-level completion/remaining-work attribution, omitted
audit disclosure, prospective rather than fabricated completed human methods, current no-rerun
instructions, canonical-assignment overwrite warnings and explicit approval for instrument changes.
The current builder records nine settled design decisions and fails validation if unresolved TBD or
placeholder text enters the form specification. Study builds require every chart image before any
form is created. The original pre-final frozen snapshot remains unchanged under `data/local_freeze/`.

**Next:** collection and quantitative analysis are complete. Remaining work is independent claim
review, optional second coding of 20% of written answers, the final report/slides and retention-date deletion.
This local audit did not independently
reverify live sharing/settings.

### Historical execution notes (superseded by the completion record above)

The following notes preserve the sequence of earlier checks, test counts and pre-final commands.
They are not current pending work. In particular, "no final-test lock", "not evaluated" and
"deferred" below refer to those earlier checkpoints only. Current completed work includes the
final evaluation/export and local assignment seal; full explanation audits are omitted.

**Amendment recorded 2 Nov, 21:00:** at Yolanda's request, the hours-long validation audit was
stopped and replaced by an **exploratory smoke check**, now the default command. This supersedes
the full-audit requirements and running/deferred status in earlier notes below and earlier sections.
Those notes/settings retain historical context; do not report the full audit as completed.
Local hashed freeze remains the alternative to mandatory Git publication. Privacy, truthful consent,
genuine study contributions, consistent assignment and once-only final-test locking remain unchanged.

The real smoke run completed in **47.37 seconds** (excluding startup/model preparation):
one middle-risk validation case, two SHAP explanations with seeds 42/43, finite probabilities,
correct contribution shapes and finite grouped values. Single-case top-five overlap was **0.8**.
This is execution evidence, **not an explanation-quality pass or multi-case stability estimate**.
Evidence: `artifacts/explanation_smoke_validation.json`.
After this amendment, all **62 unit tests** and separate form checks pass, including a regression
that proves the default CLI does not invoke the full audit. No final-test lock was created.
Omitted: deletion faithfulness/uncertainty, multi-case seed stability, background stability,
prediction-preserving perturbation stability and constrained-recourse auditing.

```powershell
.\.venv-core\Scripts\python.exe scripts\run_explanation_audit.py
```

The superseded full audit runs only with explicit `--full-audit`; its original settings are retained
for reproducibility, not an accelerated-workflow requirement. The stopped run is incomplete and is
not resumed automatically. Do not mix earlier timing estimates or partial output with smoke results.
The report must disclose the reduced explanation evaluation; no faithfulness/recourse findings are
established by this change. The final test has not been run by the smoke check.

**Status:** implementation and synthetic regression checks are not a signed operational acceptance.
The test split has not been evaluated by this handover work. Do not invent review results, mark the
blank W2.6 acceptance table passed, or run the final test early. A different reviewer must check new
code and claims. Follow-up verification on 2 Nov installed Python 3.12.10 alongside the existing
3.13 interpreter and restored every exact requirement into ignored `.venv-core/`. The environment
verifier and `pip check` pass. All five models completed a validation-only dry run; the full
explanation audit remains deferred, not passed.
Verification on this machine: **58 unit tests pass**, the separate form-spec checks pass, and
the fixture build renders 11 charts plus 11 optional profile images. Synthetic tests cover scoring,
coding, final-run locks, validation-output structure and source-form/provenance errors; they are
not evidence of final model performance or successful live Google Forms configuration.
The follow-up regressions cover closure before settings, rollback after partially opening forms,
and missing/contradictory practice exports. Rebuild live forms with the updated renderer; any failure
to close is reported for manual action. Never distribute links after a renderer error.

### Follow-up environment, validation and live checks (2 Nov)

Run commands with `.\.venv-core\Scripts\python.exe` on this Windows machine. The exact pinned
environment passes all 58 tests, separate form checks and rendering of 22 fixture images.
`scripts/run_final_test.py --split validation` completed on **544 validation cases**, fitting
logistic regression, the depth-3 tree, XGBoost, main-effects EBM and TabICL. The 22 output-file
hashes in `tables/final_test_dry_run/manifest.json` match. Each model's ten reliability bins
cover all 544 cases, flag rates stay at or below 20%, and the six specified performance metrics
are suppressed for subgroups below 30. These are dry-run checks, not final results or freeze approval.
TabICL downloaded `tabicl-classifier-v2-20260212.ckpt` on first use. Record the exact checkpoint
revision/hash before freeze as well as package versions; do not assume "latest" will stay unchanged.

One real validation SHAP explanation completed in **20.88 seconds**.
`artifacts/audit_runtime_validation.json` records its 20 selected validation IDs and estimates
**8,769 seconds (2.44 hours)** for 420 seed/background explanations alone. Perturbation explanations
and deletion predictions add runtime. The full audit was explicitly deferred after this estimate;
faithfulness, stability and recourse results still require the complete run and independent review.
The final test was not evaluated and no final-test lock was created.

Live checks are **partial and not accepted**:

- All four supplied respondent pages were reachable without cookies in an anonymous HTTP check.
  This does not certify every anonymous submission path.
- A routing-only decline check reached the thank-you/decline page without submitting. Its synthetic
  draft was cleared; no participant-code link or response was submitted.
- Google initially displayed "Draft saved", contradicting the consent's pre-Submit promise.
  With Yolanda's approval, **Settings > Presentation > Disable autosave for all respondents**
  was enabled in all four existing forms. Changes were saved to Drive and all four respondent
  pages subsequently displayed **"Saving disabled"**. Repeat this manual setting and live check
  after every rebuild; the Apps Script renderer does not configure it.
- The inspected Group B Form 4 still contains **11 chart placeholders** and lacks the agreed
  top-20%-of-full-cohort instruction. Its editor showed quiz mode, response editing,
  one-response/sign-in enforcement, question shuffling, another-response link and results
  summary off, and email collection set to "Do not collect"; these observations do not sign off
  the other forms or actual submission behaviour.
- The supplied response Sheet's general access allows **institution-wide link editing**.
  This fails the restricted-storage requirement. Permissions were deliberately left unchanged
  at Yolanda's request; the owner must restrict access and explicitly add the designated W4
  coordinator and reviewer before any real collection.
- The supplied live Apps Script is older than the repository renderer and still uses manual
  settings/routing fallbacks. It was inspected, not replaced or executed. Rebuild with the
  reviewed repository version, fixture charts and the agreed assignment; repeat acceptance.
- Respondent pages were available during the checks. Closing the test forms afterwards could
  not be verified because the editor's controls timed out. The owner must close test responses
  outside supervised checks; no link distribution or real collection is authorised.

No public Form/Drive URLs, file IDs, assignment codes or raw answers belong in this log or Git.
Private downloaded assignment workbooks are ignored; keep them in restricted storage.

### Local-freeze amendment and accelerated preparation (2 Nov, evening)

Yolanda explicitly selected a local hashed freeze in place of a mandatory commit, clean checkout
and pushed tag. This is a workflow deviation, **not independent approval**. The original tagged
path remains available. The once-only final-test lock, pinned environment and explicit final-test
confirmation remain mandatory for both paths. Do not clear the lock after a failure.

The full validation explanation audit is now running; the earlier deferral is superseded by this
request. Do not start a duplicate. Inspect its actual outputs when complete; no pass is assumed.
After the local-freeze implementation, **61 tests pass**, including synthetic tampering,
checkpoint-binding and repeat-run tests; the separate form checks pass. Mocked test messages saying
"Final test complete" are synthetic tests, not evidence that the actual holdout was evaluated.

The local mode copies scientific source/configuration, requirements, original dataset, split IDs
and the selected cached TabICL checkpoint into ignored `data/local_freeze/`. It hashes the copied
files and verifies both copies and current inputs before final evaluation. It rejects added,
deleted or changed input files and changed checkpoint bytes. Model fitting uses that exact copied
checkpoint with auto-download disabled. Preserve the entire snapshot privately.

Create the snapshot only after the intended inputs are settled. Example (replace the checkpoint
path and note with actual values; this command creates evidence only, not a final-test run):

```powershell
.\.venv-core\Scripts\python.exe scripts\run_final_test.py --create-local-freeze data\local_freeze --checkpoint "<actual cached checkpoint path>" --deviation-note "<actual completed, incomplete and skipped checks; no invented sign-offs>"
```

Final evaluation under the local workflow, **after inspecting the audit**, uses:

```powershell
.\.venv-core\Scripts\python.exe scripts\run_final_test.py --split test --local-freeze data\local_freeze\manifest.json --acknowledge-incomplete-checks --confirm-final-test
```

The lock records the snapshot digest and honest deviation note, not a fictitious reviewer.
Successful evaluation also binds the saved model bundle by SHA-256. Study export verifies the
snapshot, current inputs and model digest without requiring a Git tag for local mode. If inputs
change afterwards, stop and investigate rather than silently refitting or re-running the test.
No actual local snapshot or final evaluation is claimed merely by documenting these commands.

The requested priority is preparing the human study without another fixture-only rebuild.
No new approval is asserted by this note, no response collection has been started by this work,
and the existing final-test guard has not been changed. The earlier preparation notes were local
at that checkpoint; completed W3 implementation/evidence is now in commit `a7fbbb5`, with the
current documentation update following it. No push or live deployment is claimed.

Ready locally: the four-form generator with updated instructions, chart renderer, assignment
generator, response transformer, scoring/coding tools, pinned environment and successful
validation dry-run outputs. Existing live forms have autosave disabled.

Current material status (supersedes the earlier preparation check): the real pack, saved fitted
model, completed final-test lock and 11 genuine charts now exist and verify. The team reports the
real forms, privacy/export acceptance checks and one-person pilot complete (4 Nov). Clean-clone/
evidence verification was completed separately on 4 Nov. Human-response collection and quantitative
analysis completed on 11 Nov; qualitative coding completed in one coding pass on 11 Nov (independent 20% double-coding not done; agreement not measured). The canonical private
`data/human_study/assignment_list.csv` now exists with private seed/rules and local seal.
Do not rename fixtures as study
material or repeat the final evaluation.

**Live-form, pilot, collection and quantitative-analysis gates are complete.** Preserve
the exact sealed assignment for links and transformation; do not regenerate or switch lists. Keep
the private lookup restricted to the designated scorer and maintain the response-sheet access
controls. The full audit was omitted under the amendment, not deferred as a mandatory launch gate.

### What each member takes next

| Member | Code ready for review | Next real action |
|---|---|---|
| Noey (W1) | Later 544-case validation audit and report package complete | Independently review W1 claims and ensure the report distinguishes the later refit audit from the pre-final gate |
| Han (W2) | Provenance, source-tab identity, workbook ingestion, duration and closed-form safeguards in `forms/` | Review the completed instrument and C01 interface finding for the methods/limitations section |
| Yolanda (W3) | Final evaluation, pack/charts, model card and local verification completed | Hand over pack/charts privately and lookup only to scorer; support independent review. Preserve freeze/model/lock; never repeat final evaluation |
| Harry (W4) | Completed private transformation/scoring plus coding interfaces below | Maintain restricted storage; coordinate codebook training, qualitative coding/agreement and retention/deletion |
| Lucas (W5) | Aggregate human-study analysis, report assets and assignment/coding tools | Independently review quantitative results and assist with qualitative coding/agreement; never rerun the final test |

### Safe checks and optional validation regeneration (not a new freeze)

From the repository root in the verified environment:

```powershell
python scripts/reproduce_results.py
python scripts/run_explanation_audit.py --timing-only
python scripts/run_explanation_audit.py
python scripts/run_final_test.py --split validation
```

These commands are optional verification/regeneration, not remaining study-build requirements.
Fixture reproduction overwrites generated fixture outputs in `forms/out/`; keep real build assets
separate and rebuild the real spec from the genuine pack afterwards if needed.
The first command runs all unit tests, fixture builds, form checks and fixture images. Add
`--validation-results` only when prepared for lengthy model fits/SHAP. TabICL may download its
weights on first use and needs internet then. Only explicit `--full-audit` produces the original
full audit outputs such as `tables/faithfulness_validation.csv`,
case-level bootstrap uncertainty, deletion curves, separate seed/background/perturbation stability
tables and explicit recourse/no-recourse rows. Figures go under `figures/`; timing/selected validation
IDs go to `artifacts/audit_runtime_validation.json`. No completed full-audit result is claimed.
The default smoke result is in `artifacts/explanation_smoke_validation.json`. Perturbation
stability is part of the omitted full workload; the original runtime estimate is not a guarantee.

The final runner defaults to validation. It refits the existing frozen TabICL and four baseline
configurations on train only, evaluates the selected split, and writes metrics, 2,000 paired
bootstrap comparisons, reliability curves, runtime, subgroup suppression and proxy tables under
`tables/final_test_dry_run/`. Existing dry-run files are historical validation evidence, not
final-test results; verify their manifest rather than overwriting them unnecessarily.

### Original tagged freeze and once-only final test (alternative to local amendment above)

**Historical reference only for this completed study. Do not execute the final-test command
below, create a replacement freeze or manufacture retroactive gate approval.** The chosen local
freeze and completed lock already exist.

After W1.5, all seven W2.6 checks, the validation dry run, and W4.12 pass, the W3 owner and a
different reviewer create and commit `config/freeze_approval.json`:

```json
{
  "owner": "<W3 owner>",
  "reviewer": "<different reviewer>",
  "validation_audit_passed": true,
  "form_acceptance_passed": true,
  "final_runner_dry_run_passed": true,
  "participant_plan_verified": true,
  "protocol_sha256": "<SHA-256 of config/evaluation_protocol.json>"
}
```

This is a schema example, **not an approval**. Replace all placeholders only after actual checks.
Use `(Get-FileHash config\evaluation_protocol.json -Algorithm SHA256).Hash.ToLower()` for the digest.
Commit the approved code/protocol/approval, create and push `protocol-1.3-frozen`, and start from that
clean tagged revision. Do not change any model, split or setting after it.

```powershell
python scripts/run_final_test.py --split test --approval config/freeze_approval.json --confirm-final-test
```

The original tagged mode requires a clean checkout at the pushed freeze tag and matching tracked approval. It
also rejects Python versions other than 3.12 and any installed version that differs from a pin
in `requirements.txt`; resolve environment problems before attempting a final run. It
creates `artifacts/final_test.lock` exclusively **before loading/evaluating the test split**.
Any failure leaves the lock in place. Deleting result tables never permits another run; clearing a
lock requires a recorded team decision, not an automatic retry. Commit the lock immediately after
the run, including failed runs, and record any failure honestly.

Final tables/figures and their SHA-256 manifest go to `tables/final_test/`. The selected fitted
model and ordered test predictions stay private in ignored `data/final_evaluation/selected_model.joblib`.
W3.9 uses those predictions without refitting or re-running test metrics:

```powershell
python scripts/export_study_cases.py --out data/study_cases
python forms/case_pack.py data/study_cases/case_pack_study.json data/study_cases/private_lookup_study.json
python forms/render_images.py data/study_cases/case_pack_study.json
python forms/build_spec.py --case-pack data/study_cases/case_pack_study.json --private data/study_cases/private_lookup_study.json --assignment data/human_study/assignment_list.csv
```

The practice case is the lowest source-row-ID validation case; scored cases use the existing
prediction-only balanced selection, numbered by ascending original source row. Practice is never
scored. This rule was used in the completed export; verify its saved provenance rather than
reselecting cases. Private outputs are not in Git.
Export refuses existing study filenames to avoid silently replacing released material.

### One assignment, actual source forms, private analysis

The study handoff uses W5's block-randomised assignment, with A1/A2/B1/B2 main counts **13/12/12/13**.
The canonical CSV and private seed/rules were generated once and locally hash-sealed under the
owner's authorization on 2 Nov; `data/human_study/assignment_seal.json` records the digest and
honest review status. The team reports Harry/Lucas's restricted handover acknowledgement complete
(4 Nov); this does not claim independent sign-off. Keep all three files private and use the exact
CSV unchanged.
The W2 allocation seed 2026 is fixture-only. The separate case-order seed 11 is already in the
frozen builder; record/review the resulting real-build order during acceptance without changing
scientific inputs or creating another freeze.

Pass `--assignment data/human_study/assignment_list.csv` when rebuilding test forms too. Upload
that same CSV for the Apps Script links and use it for all later response exports. Do not switch
lists after links are distributed. See `forms/README.md` for chart/settings preflight and cleanup.

Each response Sheet tab must be identified from its actual form, **not the participant code**.
The completed study used the original workbook with explicit sheet-to-variant mapping:

```powershell
python forms/transform_responses.py --workbook data/human_study/scoring_private/exports/response_sheet_study.xlsx --sheets "Form Responses 1" "Form Responses 2" "Form Responses 3" "Form Responses 4" --variants A1 A2 B1 B2 --assignment data/human_study/assignment_list.csv --spec data/human_study/scoring_private/form_spec.json --label study --out-dir data/human_study/analysis
python scripts/analyze_human_study.py data/human_study/analysis/responses_long_study.csv --participants data/human_study/analysis/responses_participants_study.csv --private data/human_study/scoring_private/private_lookup_study.json --label study --out data/human_study/analysis
python scripts/build_human_study_report.py --scored data/human_study/analysis/scored_study.csv --people data/human_study/analysis/participants_study.csv --participants data/human_study/analysis/responses_participants_study.csv --private data/human_study/scoring_private/private_lookup_study.json
python scripts/build_report_assets.py
python scripts/assign_human_coding.py assign forms/out/responses_long_dummy.csv --send-log data/human_study/send_log.csv --members M1 M2 M3 M4 M5 --label dummy
python scripts/assign_human_coding.py agreement --assignments data/human_study/coding/assignments_dummy.csv --coded data/human_study/coding/completed_dummy.csv --label dummy
```

For **pre-freeze dummy scoring**, supply a made-up private lookup with unique nonnegative source
IDs, five flagged and five unflagged scored cases; do not access the real study/test data to create
dummy answers. The study lookup in the example exists only after the final test; before then replace
that path with the synthetic lookup. Use `--label study` only for real consented post-pilot data.

The send log needs `participant_code,recruiter` (M1-M5, never names/contact details). Coding worksheets
omit group and recruiter; distribute only each coder's own file, through restricted storage.
Combine completed worksheets privately into `completed_<label>.csv`; preserve each row's coder,
participant, case and field. One agreed code per text item is compared exactly for raw agreement.
The primary/secondary coders cannot be the recruiter or each other. Train coders on W4's codebook first.

Scoring excludes consent withdrawals, incomplete cases and logged exclusions, retains wrong practice
answers, and computes accuracy per participant before group means. `chart_checks_<label>.csv`
reports correct counts and denominators. Private scored rows, participant summaries, coding text and
exclusion logs remain under ignored `data/human_study/`. Only reviewed aggregate summaries may be
copied into report tables; no participant codes/free text or fake results in Git.
Scoring requires the matching participant export: included participants' groups must agree, Group B
practice answers must be present, and the imported combined-correct flag must match those answers.
Invalid exports stop analysis before outputs are written; regenerate them with the transformer rather
than hand-editing flags. Consistently wrong answers remain included and are reported as wrong.

### Remaining non-code and independent-review work (status updated 4 Nov)

- The team reports the pre-collection coordination and required private handover acknowledgements
  complete (4 Nov). Keep the genuine pack/charts and locally sealed assignment in restricted
  storage; the lookup goes only to the designated scorer. Do not regenerate the assignment.
- The team reports the closed real-form build, privacy/access controls, consent/routing, live
  acceptance checks, exports and one-person pilot complete (4 Nov). Keep their evidence with the
  study materials.
- The team reports applicable course/ethics arrangements, retention/deletion/withdrawal plan,
  recruitment preparation and codebook/training agreed (4 Nov). Record actual recruitment and
  exclusion events as they occur; do not infer participant counts before collection.
- The pilot is reported complete; proceed with approved participant recruitment and response
  collection only under the confirmed consent/retention/access arrangements, then perform analysis/coding.
- Clean-clone tests and saved-result hash verification completed 4 Nov; preserve the saved evidence
  and never repeat the final evaluation. Full explanation audits remain omitted; review the limitation note
  rather than treating those audits as a launch prerequisite.
- Finish W5's validation-only static demo, final report/slides, reviewed human results after
  collection and rehearsal. Existing DOCX/PDF proposal/question-bank files are historical drafts,
  not certification of the current form build; the appointed report editor handles binary updates
  and matching PDF export.
