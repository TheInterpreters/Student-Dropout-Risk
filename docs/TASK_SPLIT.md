# Task Split and Timeline — Five Workstreams plus a Shared Report/Slides Track

Draft for the team meeting on Tue 27 Oct 2026. Workstreams are roles, not names: agree who takes
which one and record it in the tracker (§10); the decisions are already settled in §1. Methodology and
protocol live in `docs/HANDOFF.md`; this file says **who does what, by when, in what order, and when
each task counts as done**.

**What changed on 27 Oct:** participants answer a **Google Form** instead of a custom-built interface
(decision D8). The study itself is unchanged: same two groups, same 10 cases, same questions, same
consent and privacy rules. §8 lists the few deviations to disclose.

**Fairness:** every workstream is real technical or operational work, and **writing the report and
making the slides is shared by all five** (§5). §7 shows the estimated hours per person; they are
within about ±1.5% of each other. Hours are estimates, so adjust at the meeting if someone knows better.

> **Deadline (settled):** "3rd week of November" = **Mon 16 – Fri 20 Nov 2026**. The plan finishes
> everything by **Thu 19 Nov**; **Fri 20 Nov is buffer** and the hard stop.

**How to read a task:** `[I]` = **independent** (can start now). `[D: W1.2]` = **depends on** that
task finishing first. **Deadline** is the latest day the task may finish; a dependent task can start
only after what it depends on is done. **Done when** is the check the reviewer uses.

## 0. Rules for everyone

1. **Test-split gate.** The test split is the 15% of students the models have never seen; it is how
   the final result is measured. Nobody opens, scores or tunes on it until **all three** are true:
   (a) the validation audit (W1) is finished, (b) the study-form acceptance checks pass (W2.6), and
   (c) the protocol is frozen and tagged (W3.4). Then W3 runs it **once**. No re-tuning after.
2. **One owner and one different reviewer per workstream.** The reviewer checks code and claims before
   anything is reported.
3. **Who edits what.** Only the **report editor** (one appointed member, §10) edits the proposal and
   final-report DOCX/PDF, because Word files cannot be merged in git. Everyone else writes text in the
   shared Google Doc drafts (rule 4) and the editor pastes it in. Anyone may edit `docs/HANDOFF.md`,
   but `git pull` first and commit small.
4. **Where data lives.** Raw participant responses are never in git and never in the open team Drive
   folder. Form responses go to **one restricted Google Sheet** shared only with the W4 owner and
   reviewer (no email collection, no sign-in). The analysis-ready copy `data/human_study/responses.csv`
   is git-ignored (`data/**`) and stays on the analysis laptop; the only backup is in a **restricted**
   Drive subfolder with the same two people. The team Drive may hold report and slide drafts, figures,
   aggregate or coded results, recruitment counts and the public UCI data. Never store participant
   contact details next to participant codes. Commit only aggregate or coded summaries, and keep the
   Drive and Form URLs out of the repo.
5. **Day-1 setup (everyone, due Wed 28 Oct):** clone the repo, create the pinned `.venv-core` from
   `requirements.txt`, run `python -m unittest tests.test_modeling tests.test_explanations
   tests.test_auditing -v` and confirm 26 tests pass. Also run `python -c "import tabicl, xgboost,
   interpret, shap"` (the audit and final-test scripts need `tabicl` and `xgboost`; the tests do not).
   Report any failure in the group chat.
6. **Every new script gets a small test** and writes outputs only under `tables/`, `artifacts/` or
   `figures/`, so results reproduce from one command.
7. After any DOCX change, the report editor re-exports the PDF. For the proposal, re-check the page
   count (body 4 pages, references on page 5).
8. **Weekends are buffer, not plan.** If a deadline slips, tell the group the same day. (Participant
   sessions may use Sat 14 / Sun 15 Nov if participants prefer.)
9. **Git workflow.** Work on your own branch (`w1-audit`, `w2-forms`, ...), commit small, `git pull
   --rebase origin main` before pushing, merge to `main` only after your reviewer has looked at it, and
   never force-push. Review time is part of the plan (§7).

## 1. Settled decisions (D1–D8)

Decided on 27 Oct 2026 to protect the Thu 19 Nov finish, so nothing waits for the meeting. Change one
only if the whole team agrees **and** tells W3 before the freeze (Mon 9 Nov).

| # | Decision | Settled as | Why |
|---|---|---|---|
| D1 | Final deadline and extra deliverables | **Fri 20 Nov 2026** hard stop (3rd week of November), team finish Thu 19 Nov. Deliverables: final report (DOCX and PDF) and the slide deck; if the instructor asks for more, tell the report editor at once and it uses the buffer day | Fixed date for every task deadline |
| D2 | Optional narrative condition (B2) | **Dropped.** Not built; removed from the DOCX, HANDOFF and protocol (ID W5.4 unused) | Adds build and checking time to a 24-day plan; the core study is unaffected |
| D3 | How sessions run | **In person on a team laptop**: the session runner opens the participant's pre-filled Google Form link. A remote link is only a fallback to reach the minimum of 20, and is disclosed as a limitation | Keeps the controlled, no-sharing conditions we planned; minimal deviation |
| D4 | Subgroup and proxy diagnostics on the test split too | **Yes**, descriptive, same code, run once inside the final-test script | One extra call; recorded in the protocol before the freeze |
| D5 | Decision-support demonstration (formerly "Mode A") | **Static example case card** (screenshots from validation fixtures) in the report and slides; no software | The form replaces the app; the example still shows what an officer would see |
| D6 | Pilot participants count toward the 25 | **No.** The pilot is one extra person | Keeps the 25 clean and the groups approximately balanced (12/13) |
| D7 | Withdrawal window and anonymity | **Current plan:** responses are pseudonymised (random participant code); withdrawal is possible until de-identification; then the code link is deleted. Never call the data "anonymous" in the consent text before de-identification | Pseudonymised is not fully anonymous; withdrawal needs a link |
| D8 | Study instrument | **Google Forms, not a custom interface.** Two forms (Group A, Group B), each with three seeded case-order versions (six variants); explanation images made in Python; responses to a restricted Sheet | Saves about 30–40 hours in a 24-day plan; the study design is unchanged |

## 2. Participants — everyone recruits and runs their own sessions (W4 coordinates)

- **Target: 25 participants in total. Every team member recruits at least 5** voluntary adults from the
  AIT community, **books them into slots and runs those 5 sessions** from the W4 session sheet. Each
  recruiter has **5 confirmed session slots by Fri 6 Nov** and sends reminders.
- **Recruiters do not choose groups.** Each participant gets the **next unused pre-filled link** from a
  seeded assignment list (task W5.8), held by the W4 coordinator. The link carries the participant code
  and the form variant; a recruiter cannot pick or swap it. 25 is odd, so groups will be 12 and 13;
  report the imbalance.
- W4 keeps a count per recruiter only (no names or IDs in the repo). People consent only inside the
  form, at the session.
- **Minimum: 20 completed sessions with at least 9 in each group** (so 9/11 is acceptable, 8/12 is
  not). If fewer than 25 attend by Tue 17 Nov, proceed once the minimum is met and report the achieved
  sample honestly; below the minimum, describe the study as pilot-scale.
- **Replacements keep the groups balanced.** The seeded list holds 2 spare slots (one Group A, one
  Group B). If a participant does not complete (no-show, withdrawal, incomplete session), the next
  recruited participant **inherits that empty slot's group and variant**; a spare is used only when a
  slot is empty, choosing the group that keeps the totals closest to balanced. Incomplete sessions are
  logged and excluded. The older documents say "minimum 4" (see §8).

## 3. Timeline at a glance (2026)

| Phase | Dates | What | Who |
|---|---|---|---|
| **P0** Setup | Tue 27 – Wed 28 Oct | Owners and editor appointed (decisions D1–D8 already settled), environment and tests | all |
| **P1** Build (validation only) | Thu 29 Oct – Fri 6 Nov | Audit, form generator, images, final-test script, session kit, assignment lists, report methods drafts | W1–W5 + everyone (R) |
| **P2** Gate | Mon 9 Nov | Freeze and tag; go/no-go for the test run | W1, W2, W3 |
| **P3** Final test and study cases | Tue 10 – Thu 12 Nov | One test run, export cases, build real forms, model card | W3, W2, W5 |
| **P4** Study | Fri 13 – Wed 18 Nov | Pilot, 25 sessions, scoring, coding | W4 coordinates; everyone runs own sessions |
| **P5** Wrap-up | Mon 16 – Thu 19 Nov | Report sections, cross-review, slides, merge, final check | **everyone** |
| **Buffer** | Fri 20 Nov | Final export and submission | all |

**Checkpoints (everyone reports status at each):**

| Date | Checkpoint | Must be true |
|---|---|---|
| Fri 30 Oct | Foundations | Form spec and case-pack contract agreed, ethics note done, 20-case script selects cases, report/slide outline and Google Docs created |
| Fri 6 Nov | Build complete | Audit tables done, form acceptance passed on validation fixtures, final-test script dry-run OK, 25 slots booked, every section has a methods draft |
| **Mon 9 Nov** | **Gate / go-no-go** | Freeze tag created; if not ready, escalate the same day |
| Fri 13 Nov | Study start | Real forms built, pilot passed, sessions begin |
| Tue 17 Nov | Sessions done | 25 sessions complete (minimum 20, at least 9 per group); slide drafts in |
| Thu 19 Nov | Finish line | Report, slides, PDF, model card, README and HANDOFF final |

**Final deliverables checklist (all done by Thu 19 Nov):**
- [ ] Final report DOCX and PDF, in the repo root next to the proposal
- [ ] Slide deck (PPTX or Google Slides export), rehearsed once, timed
- [ ] Repo on `main`: tag `protocol-1.3-frozen` pushed, tests passing (26/26), final-test outputs under `tables/`
- [ ] Completed model card (`docs/HANDOFF.md` §8) and README/HANDOFF updated with results
- [ ] Raw participant data deleted everywhere (Forms, Sheet, exports, Drive trash) on the confirmed retention date, after the human-results review (R7), or the date and plan recorded; aggregates only kept
- [ ] Drive folder Restricted, no Drive or Form URL in the repo
- [ ] Final report discloses the deviations in §8

**If behind:** (1) drop W3.7 (optional sensitivity); (2) cut the demo-card polish (W5.1) before cutting
any study or audit task; (3) shorten the slide deck before shortening the report; (4) never move the
test run earlier than the freeze.

## 4. Workstreams (technical and operational)

### W1 — Explanation audit (core code) — also the suggested report editor

| ID | Task | Depends | Deadline | Done when |
|---|---|---|---|---|
| W1.1 | Write `scripts/run_explanation_audit.py`: select 20 audit cases from the **validation** split with `select_risk_stratified_positions` (4 per risk stratum, predictions only, labels unused). Also **time one SHAP explanation** and estimate the total runtime of W1.2/W1.3 (about 400 explanations). | [I] | Fri 30 Oct | Same 20 case IDs on every run; script never reads test labels; runtime estimate posted so the team can plan compute time. |
| W1.2 | Deletion faithfulness with `deletion_curve`: ranked vs 50 random orders per case; area between curves with case-level uncertainty. | [D: W1.1] | Wed 4 Nov | `tables/faithfulness_validation.csv` plus figure; reviewer re-runs and gets identical numbers. |
| W1.3 | Stability: 10 runs per case varying seed and training background separately; `top_k_overlap` (top 5), rank correlation, `prediction_preserving_perturbations` (1% of training SD, probability change ≤ 0.01); flag overlap < 0.80. | [D: W1.1] | Wed 4 Nov | `tables/stability_validation.csv`, seed and background reported separately. |
| W1.4 | Constrained counterfactuals with `constrained_binary_counterfactuals` (only tuition/debt status may change; success = leaves the top-20% set). | [D: W1.1] | Wed 4 Nov | Table with successes and explicit no-recourse rows. |
| W1.5 | Audit results note (½ page): descriptive findings, no causal claims. Becomes the base of W1's report section (R3). | [D: W1.2, W1.3, W1.4] | Thu 5 Nov | Reviewer signs off; numbers match the tables. |

The W1 owner is busy only until Thu 5 Nov, so they are the suggested **report editor** (R1 and R8).
ID W1.6 moved to W2.2.

### W2 — Study instrument: Google Forms (build and test)

| ID | Task | Depends | Deadline | Done when |
|---|---|---|---|---|
| W2.1 | **Form spec:** sections (the **W4.1 consent form** with required **18+ confirmation**, pre-filled participant code, instructions, practice case, 10 cases), per-case questions (yes/no, confidence 1–5, three free-text prompts), no quiz mode, no feedback or answers shown, six variants (A/B × three seeded orders). Uses the W4.1 consent text and the W4.2 instruction text. | [I] | Thu 29 Oct | One-page spec agreed by W2, W4 and W5 owners. |
| W2.2 | **Case-pack data contract:** JSON fields per case (case id, profile fields, Group B contribution values, image file names; the model output is kept **private** for scoring only). Agreed with W1, W3 and W5. | [I] | Thu 29 Oct | Schema file in the repo agreed by the four owners. |
| W2.3 | **Form generator** (Google Apps Script or Forms API) that builds all six variants from the case packs and images, including consent, 18+, pre-filled code and the practice case. First run on **validation fixtures** as dummy cases. | [D: W2.1, W2.2, W5.8, W4.1, W4.2] | Wed 4 Nov | Six test forms build from one command; reviewer can rebuild them identically. |
| W2.4 | **Privacy settings and response Sheet:** no email collection, no sign-in, response editing off, summary charts hidden, form not publicly listed; one **restricted** Sheet shared only with the W4 owner and reviewer. | [D: W2.1] | Wed 4 Nov | Settings checklist signed by the reviewer; Sheet permissions show only the two people. |
| W2.8 | **Response transform script:** form export (wide Sheet) → long CSV with the template columns in `docs/human_study_response_template.csv` (participant, group, case order from the variant, case id, answers, free text, session time from the log, complete flag). Tested with dummy rows marked fake. | [D: W2.1] | Wed 4 Nov | Dummy export becomes the right long CSV; output labelled "dummy". |
| W2.5 | **Dry run:** submit dummy responses to the test forms, export them and run W2.8; then delete the test responses. | [D: W2.3, W2.4, W2.8] | Thu 5 Nov | Export and transform give correct rows; test data deleted from Forms and Sheet. |
| W2.6 | **Acceptance checks** (HANDOFF §7): (1) all six variants build and displayed values match the exports; (2) Group B sees nothing that reveals the output and no feedback appears anywhere; (3) groups see identical profiles and differ only in explanation; (4) assignment and case order reproduce from the seed; (5) privacy settings correct; (6) form text matches the model card and consent text; (7) dry-run export transforms correctly. | [D: W5.3, W2.3, W2.4, W2.5, W2.8] | Fri 6 Nov | All seven checks recorded as passed by the reviewer. **Gate condition (b).** |
| W2.7 | **Real forms:** after the test run, build the six variants from the 10 study cases and the practice case (running W5.3's image renderer), repeat the parity check without retuning, and prepare the pre-filled links per the assignment list for W4. | [D: W3.9, W5.8] | Thu 12 Nov | Displayed values equal the exported frozen outputs; links tested by opening each variant once. |

### W3 — Final evaluation, study cases and reproducibility

| ID | Task | Depends | Deadline | Done when |
|---|---|---|---|---|
| W3.1 | Confirm the pinned `.venv-core` works and all **26** tests pass (the EBM test needs `interpret`). | [I] | Wed 28 Oct | Test log shows 26/26 OK. |
| W3.2 | Write `scripts/run_final_test.py`: refit frozen models on train and evaluate once on test (discrimination, capacity recall/precision, Brier, 10-bin ECE, reliability curve, runtime, `paired_bootstrap_model_differences` 2,000 resamples seed 42, and subgroup/proxy tables per D4). **One-run guard:** a separate lock file (`artifacts/final_test.lock`) is written **before** the run starts and committed right after it, so deleting the output tables cannot allow a second run; the script refuses to run while the lock exists, and clearing it needs a recorded team decision. | [I] | Fri 6 Nov | Dry-run on the **validation** split gives the right columns; guard test passes, including "output deleted, lock still blocks". |
| W3.3 | One-command clean-clone script that regenerates every reported table and figure. Note in the README that TabICL downloads its model weights on first use and needs internet. | [I] | Fri 13 Nov | Script written and runs on the author's machine. |
| W3.4 | **Freeze:** confirm protocol 1.3 values, the settled decisions D1–D8 and the participant plan, create the git tag `protocol-1.3-frozen` and **push it** (`git push origin protocol-1.3-frozen`). | [D: W1.5, W2.6, W3.2, W4.12] | Mon 9 Nov | Tag exists on GitHub; reviewer confirms no model, split or setting changed since. **Gate condition (c).** |
| W3.5 | **Run the final test once.** Save outputs and the exact command. | [D: W3.4] | Tue 10 Nov | Result files exist and the lock file is committed; nothing re-run or re-tuned afterwards. |
| W3.9 | **After the test run:** select the 10 study cases (5 flagged, 5 unflagged, predictions only) with `select_forward_simulation_positions`; compute explanations; export pseudonymised case packs (C01–C10) in the W2.2 format. Also pick the **unscored practice case from the validation split** (never a test case) with its explanation. Private case lookup stays outside git. | [D: W3.5] | Wed 11 Nov | Packs validate against the schema; practice case is not one of the 10; lookup is not in git. |
| W3.6 | Complete the model card (HANDOFF §8) with final numbers, and make the final-test figures (reliability curve, subgroup table). | [D: W3.5] | Thu 12 Nov | Every "pending" in §8 replaced by a number or a stated limitation; figures regenerate from scripts. |
| W3.7 | *Optional:* sensitivity checks (Enrolled as third class or grouped). | [I] | Fri 13 Nov (drop if behind) | Labelled as sensitivity; not used for model selection. |
| W3.8 | **Clean-clone verification** by the **W5 owner** (a different person than the author). | [D: W3.3, W3.5, W3.6] | Wed 18 Nov | Fresh clone reproduces identical tables; any difference fixed. |

### W4 — Human-study operations and analysis

| ID | Task | Depends | Deadline | Done when |
|---|---|---|---|---|
| W4.1 | **Consent form and information sheet** (the first section of every form): take the template in HANDOFF §6 and fill every placeholder: purpose, about how long it takes, what is recorded, voluntary, 18+, **withdrawal deadline and the contact person**, how data are stored, **confirmed retention and deletion date (find the real course date)**. Also set who may see raw responses and the deletion plan. **Lock the team Drive first (rule 4):** change the shared folder from "Anyone with the link" to Restricted, and create the restricted raw-data subfolder. | [I] | Fri 30 Oct (Drive lock: Wed 28 Oct) | Drive set to Restricted; consent form has no placeholder left and is read by all five owners; the same text is what the form shows. |
| W4.5 | Recruitment plan, per-recruiter count and tentative session calendar (sessions Fri 13 – Tue 17 Nov, weekend allowed). Also book a **quiet room and laptop(s)** for those days. | [I] | Fri 30 Oct | Calendar, room and laptop booked; counts shared; **25 slots booked by Fri 6 Nov**. |
| W4.2 | Session materials: **standardised instruction text first (the form needs it)**, then practice-case script, debrief script, a **participant card** (their code, the contact person and the withdrawal deadline, handed out at the session), and an "if something goes wrong" sheet (laptop charged, spare slot, no-show rule). | [D: W4.1] | Tue 3 Nov | Instruction text delivered to W2 by Tue 3 Nov; any member can run a session from the sheet alone. |
| W4.3 | Codebook (comprehension, actionability, information gaps, `other/unclear`) with one paraphrased example per code. | [I] | Fri 6 Nov | Written **before** any group comparison. |
| W4.12 | Align the participant numbers (target 25, minimum 20 with at least 9 per group) and the replacement rule (§2) in `config/evaluation_protocol.json` and `docs/HANDOFF.md` §6 **before the freeze**. The proposal DOCX stays as submitted; the final report states the achieved numbers. | [I] | Fri 6 Nov | No "8–10" or "minimum 4" left in the protocol JSON or HANDOFF; replacement rule written down. |
| W4.6 | One-person pilot on the real forms (check nobody can see the answer early, the link and code work, and the sheet receives the row); fix issues. | [D: W2.7] | Fri 13 Nov (morning) | Pilot finds no leakage; fixes logged; pilot row deleted. |
| W4.7 | Coordinate the study: hand each recruiter the next pre-filled links, keep the **session log** (start and end time per participant code, exclusions with reasons), check daily that the Sheet has the right rows. (Each member runs their own 5 sessions, §2.) | [D: W4.6, W4.5] | Tue 17 Nov | 25 complete sessions (minimum 20, at least 9 per group) logged; replacements follow §2; response Sheet backed up each day to the restricted W4 Drive subfolder (not git, not the open team folder). |
| W4.8 | **Rolling task:** coding starts as soon as the first sessions finish (not before the codebook W4.3) and is complete only after the last session (W4.7). **W4 owner** codes; the **W5 owner** is the independent second coder on ≥ 20% (about 50 of roughly 250 per field); raw agreement; W4 owner finishes the rest. | [D: W4.7 (last session), W4.3] | Wed 18 Nov (rolling from Fri 13 Nov) | Theme counts by group plus agreement figure. |
| W4.11 | Run W2.8 on the real export, then the scoring/analysis script (W5.6). | [D: W4.7, W5.6] | Wed 18 Nov | Group accuracy, session time and sample sizes tabulated; no significance claims. |
| W4.10 | Delete raw responses and any case-link files **on the confirmed retention date from W4.1**, and only after the human-results review (R7); keep aggregates only. If that date is after submission, keep the data in the restricted store until then and record the plan; if it is before Thu 19 Nov, W4.1 raises it at once and the verification chain moves earlier. | [D: W4.8, W4.11, R7] | Thu 19 Nov at the earliest (after R7); otherwise the confirmed retention date | Deletion done everywhere (Forms, Sheet, laptop CSV, restricted Drive subfolder **and its Drive trash**, any export) and noted in the private governance note. |

ID W4.9 moved to W5.8.

### W5 — Explanation images, assignment lists, demo card and scoring script (code-heavy)

| ID | Task | Depends | Deadline | Done when |
|---|---|---|---|---|
| W5.8 | Generate the **seeded assignment list:** 25 participant slots plus 2 spares (one Group A, one Group B), groups 12/13, each slot assigned a participant code and one of the six form variants; record the seed; write the replacement rule (§2) on the sealed list; give it to the W4 owner. | [I] | Mon 2 Nov | List reproduces from the seed; recruiters never see or choose a participant's group; replacement rule is on the list. |
| W5.3 | **Image renderer in Python:** a profile card for each case and, for Group B, the contribution chart (direction and magnitude only), plus the neutral legend and the comprehension-check question for the practice case. Runs on the W2.2 case packs. | [D: W2.2] | Thu 5 Nov | Images for validation fixtures built; reviewer confirms **no** base value, score, probability, capacity boundary or class appears anywhere. |
| W5.6 | Scoring and analysis script: `correct` against the frozen output, participant-level accuracy, group means, confidence and session time; descriptive only, no significance tests. Reads the long CSV from W2.8. Test with **dummy rows marked fake**. | [I] (schema in `docs/human_study_response_template.csv`) | Fri 6 Nov | Runs on dummy data; output labelled "dummy" and never committed as a result. |
| W5.1 | **Static demo card** (replaces Mode A): one example case with profile, prediction labelled "estimated model risk", contributions, warnings, counterfactual or no-recourse, intended-use and non-causality notes, as an image from a **validation fixture** for the report and slides. | [D: W2.2] | Wed 11 Nov | Image reviewed; no test case shown. |
| W5.5 | Audit figures for the report: deletion curves and stability plots. | [D: W1.2, W1.3] | Wed 11 Nov | Figures regenerate from scripts. |

W5 also does **W3.8** (clean-clone verification) and is the independent second coder in **W4.8**.
IDs W5.2, W5.4 and W5.7 are unused: those tasks moved to W3.9, dropped (D2) and W4.11.

## 5. Report and slides — everyone (shared track)

**One appointed report editor** assembles the Word report and the slide deck. They do **not** write
everyone's text. Each workstream owner writes the section and slides for their own part, and each
section is cross-reviewed by a different workstream.

| Report section | Written by | Draft source |
|---|---|---|
| Introduction, data and EDA, limitations | W3 owner | HANDOFF §2–§4 |
| Predictive results and model comparison (final test), model card, reproducibility | W3 owner | W3.5, W3.6 |
| Explanation audit (faithfulness, stability, recourse, subgroup/proxy) | W1 owner | W1.5 and tables |
| Study instrument (Google Forms), form screenshots, acceptance results, disclosed deviations | W2 owner | W2.6, HANDOFF §7 |
| Explanation images, demo card, audit figures | W5 owner | W5.3, W5.1, W5.5 |
| Human study: methods, ethics, results, qualitative findings | W4 owner | W4.7, W4.8, W4.11 |
| Discussion and conclusion | **everyone**: each owner contributes 3 bullet points; the editor merges them | R3 |

| ID | Task | Depends | Deadline | Done when |
|---|---|---|---|---|
| R1 | Report and slide setup: outline, section and slide owners, shared Google Doc and Slides in the team Drive (drafts only, no raw data), template, and the **report editor appointed** (§10). | [I] | Fri 30 Oct | Outline and owner list shared; empty Doc and Slides exist. |
| R2 | **Methods drafts:** each owner writes what their part built and how (no results yet), matching HANDOFF. | [D: R1] | Fri 6 Nov | Every section has a methods draft; each owner's reviewer has read it. |
| R3 | **Results sections** (all but human study): each owner adds results and limitations for the rows in the table above, plus their 3 discussion bullets. Form screenshots and the demo card use **validation fixtures**, never the 10 test cases, until after the last session. | [D: W1.5, W2.6, W3.6, W5.5, W5.1, R2] | Mon 16 Nov | Sections complete in the Google Doc; every number matches the tables. |
| R4 | **Cross-review:** each owner reads and comments on a different workstream's section (W1→W2, W2→W3, W3→W4, W4→W5, W5→W1), checking numbers against tables and claims against HANDOFF. | [D: R3] | Wed 18 Nov | Comments resolved by the writers; no claim beyond the evidence. |
| R5 | **Slides:** each owner makes 2–3 slides for their own part (W4's human-results slide is filled in at R6). One shared look, one message per slide. | [D: R1, R3] | Tue 17 Nov | Draft deck complete with placeholders only for human results. |
| R6 | **Human-study results section and slide** by the W4 owner (using the W4.11 analysis), including limitations and sample size. | [D: W4.8, W4.11, R4] | Thu 19 Nov (12:00) | Section and slide in the shared files; sample size, group counts, accuracy, session time and themes match the analysis. |
| R7 | **Review of the human-results section:** the **W3 owner** (not the author) checks it against the analysis outputs: sample size and group counts, accuracy, session time, themes, deviations disclosed, and that no significance or causal claim is made. | [D: R6] | Thu 19 Nov (15:00) | Comments resolved by the W4 owner before the merge. |
| R8 | **Merge and export:** the report editor assembles the final report DOCX, adds references and figures, exports the PDF, and merges the deck. | [D: R4, R5, R7, W3.8] | Thu 19 Nov (17:00) | Report DOCX and PDF and the deck are complete and consistent. |
| R9 | **Final read and rehearsal:** two members who are not the editor read the PDF and deck end to end; one timed rehearsal; README and HANDOFF updated with results. | [D: R8] | Thu 19 Nov (evening); Fri 20 Nov = buffer | No inconsistency left; rehearsal done; PDF is current. |

## 6. Critical path

```
Tue 27-Wed 28 Oct   P0   owners + report editor (D1-D8 settled) · env/tests (W3.1) · Drive lock (W4.1)
Thu 29-Fri 30 Oct   W2.1 form spec · W2.2 case-pack contract · W1.1 case script · W4.1/W4.5 · R1 report+slides setup
Mon 2 Nov           W5.8 seeded assignment list ─> W2.3
Mon 2-Wed 4 Nov     W1.2/1.3/1.4 audit ─> W1.5 (Thu 5)  |  W2.3 generator · W2.4 privacy · W2.8 transform (Wed 4)
Tue 3 Nov           W4.2 instruction text ─> W2.3
Thu 5 Nov           W1.5 audit note · W2.5 dry run · W5.3 image renderer
Fri 6 Nov           W2.6 acceptance ✔ · W3.2 dry-run ✔ · W4.12 numbers aligned · W4.3 · W5.6 · R2 · 25 slots
Mon 9 Nov           W3.4 FREEZE + TAG   (needs W1.5 + W2.6 + W3.2 + W4.12)
Tue 10 Nov          W3.5 FINAL TEST (once)
Wed 11 Nov          W3.9 export 10 study cases · W5.5 audit figures · W5.1 demo card
Thu 12 Nov          W2.7 build real forms · W3.6 model card + final-test figures
Fri 13 Nov          W4.6 pilot (morning) ─> sessions start (afternoon)  [each member runs own 5]
Fri 13-Tue 17 Nov   W4.7 sessions  ·  W4.8 coding starts as sessions finish
Mon 16 Nov          R3 results sections written by every owner
Tue 17 Nov          R5 slide drafts
Wed 18 Nov          W4.8 coding done (rolling since Fri 13) · W4.11 transform + analysis · W3.8 clean-clone check · R4 cross-review
After R7            W4.10 delete raw data on the confirmed retention date (not automatic on 19 Nov)
Thu 19 Nov          R6 human results (12:00) ─> R7 review (15:00) ─> R8 merge + PDF (17:00) ─> R9 final read + rehearsal
Fri 20 Nov          buffer / submission
```

**Blocking rules.** (1) W3.5 cannot start until W1.5, W2.6 and W3.4 are done. (2) No participant
session until W2.7 is built and W4.6 passes. (3) After W3.5, no retuning and no model selection.

## 7. Fair-share check (estimated hours per person)

Hours are estimates (build, run, check and write), used only to compare people. Counted as one person
per workstream.

| Person (workstream) | Technical / operational work | Shared work (all five) | Total |
|---|---|---|---|
| W1 owner (+ report editor) | 30 audit (incl. timing test) + 9 editor (R1 3, R8 6) = **39** | 26.5 | **65.5** |
| W2 owner | 4 + 2 + 12 + 3 + 6 + 4 + 5 + 4 = **40** | 26.5 | **66.5** |
| W3 owner | 8 + 6 + 2 + 3 + 9 + 7 = 35, + 3 intro/data section + 1.5 (R7 review) = **39.5** | 26.5 | **66** |
| W4 owner | 4 + 3 + 5 + 3 + 2 (W4.12) + 3 + 5 (W4.7 incl. session log) + 7 (coding) + 3 + 1 + 4 (R6) = **40** | 26.5 | **66.5** |
| W5 owner | 3 + 12 + 6 + 4 + 4 + 4 (W3.8) + 5 (second coder) = **38** | 26.5 | **64.5** |

**Shared work per person (about 26.5 h):** day-1 setup 2 · recruiting 5 participants 3 · running their
own 5 sessions 4 · methods draft (R2) 3 · results section (R3) 5 · cross-review (R4) 2 · slides (R5) 3 ·
final read and rehearsal (R9) 1.5 · reviewing their partner's work and PRs 3.

**Result:** totals range from 64.5 to 66.5 hours (about ±1.5%); the W3 owner's R7 review is included. The Google Form saved roughly 30–40 hours
of interface work, which is why the totals are lower than in the earlier plan. Optional W3.7 (about 6 h)
is excluded; the W3 owner takes it if time allows. If the meeting finds someone with a lighter or
heavier load, move a whole task and update the table.

## 8. Participant numbers and disclosed deviations

**Participant numbers.** `config/evaluation_protocol.json` and `docs/HANDOFF.md` §6 still say "target
8–10, minimum 4". This file uses 25 (minimum 20). **Task W4.12 aligns them before the freeze (Fri 6
Nov).** The submitted proposal DOCX/PDF stays as it was submitted; the final report states the achieved
numbers.

**Deviations from the proposal and the original plan (state these plainly in the final report):**
1. **Google Forms replace the custom browser interface** (D8): a deliberate scope decision to protect the
   3-week deadline. The study design, cases, questions and privacy rules are unchanged.
2. **Case order:** three pre-shuffled seeded orders per form instead of a fresh random order per person.
3. **Timing:** per-case time is not recorded; only total session time (from the session log).
4. **Decision-support demonstration:** a static example card instead of a working screen (D5).
5. **Withdrawal and exclusions** are handled by hand through the participant code and the session log.
6. **Remote link** is a fallback only (D3); if used, disclose it as less controlled.
7. The optional narrative condition was dropped (D2), and think-aloud notes were dropped earlier.

## 9. Risks and what to do

| Risk | Early warning | Response |
|---|---|---|
| Form generator not ready by Fri 6 Nov | W2.3 slips past Wed 4 Nov | W2 escalates immediately; build the six variants by hand from the spec (copy-paste) as a fallback; the W5 owner helps |
| Fewer than 25 recruited | Fewer than 25 booked slots on Fri 6 Nov | Everyone recruits more that week; the minimum is 20 |
| Test run reveals a problem | Odd numbers on Tue 10 Nov | Report honestly; **no tuning and no re-run**; document as a limitation |
| Retention date earlier than Thu 19 Nov, or later than submission | Found in W4.1 | Earlier: move the verification chain (R6, R7, W4.8) earlier. Later: keep the data in the restricted store until that date; never delete before R7 |
| Someone deletes the final-test output and re-runs the test | Missing output tables | The committed `final_test.lock` blocks the second run; report honestly if it happened (W3.2) |
| A participant does not complete | Empty slot in the session log | The next recruit inherits that slot's group and variant (§2); log the exclusion |
| Session no-shows | Empty slots on Fri 13 – Tue 17 Nov | Keep two spare slots; recruiters reschedule |
| DOCX edit conflicts | Two people edit the DOCX | Only the report editor edits it (rule 3) |
| Writing left to the last days | R2 methods drafts missing on Fri 6 Nov | Owner writes it that weekend; editor reports the gap at the checkpoint |
| SHAP/TabICL runs too slowly on laptops | The W1.1 timing test shows hours per run | Split the 20 cases across several members' machines; never reduce the cases or runs (the protocol is frozen) |
| A Group B image reveals the output | Reviewer finds a probability, base value or class in an image | Fix W5.3 and rebuild; rerun the W2.6 check before the pilot |
| A participant gets the wrong form or the link is shared | Session log shows a mismatch, or a code appears twice | Each link is single-use by convention and tied to a code; discard and replace the duplicate row |
| Google Form settings expose data | Summary charts, email collection or public listing found | W2.4 checklist; re-check before the pilot and before every batch of sessions |
| `tabicl` or `xgboost` missing on someone's machine | Day-1 import check fails | Fix on Wed 28 Oct; the audit and final-test scripts need them |
| Merge conflicts in shared files | Rebase errors | Per-workstream branches (rule 9); only the editor touches the DOCX |

## 10. Tracker (fill in at the meeting)

| Workstream | Owner | Reviewer | First deadline | Status |
|---|---|---|---|---|
| W1 Explanation audit | | suggested: W2 owner | Fri 30 Oct | |
| W2 Study instrument: Google Forms | | suggested: W3 owner | Thu 29 Oct | |
| W3 Final evaluation, study cases, reproducibility | | suggested: W4 owner | Wed 28 Oct | |
| W4 Human-study operations and analysis | | suggested: W5 owner | Fri 30 Oct | |
| W5 Images, assignment lists, demo card, scoring script | | suggested: W1 owner | Mon 2 Nov | |
| **Report and slides editor** (assembles only; suggested: W1 owner) | | — | Fri 30 Oct (R1) | |

**Suggested reviewers** form a ring (each owner reviews the next workstream), so everyone reviews exactly
one other person's work (3 h, already counted in §7). Change it if a pair works poorly together.

**Open items only the team can fill in:** owner and reviewer names above; who is the report editor; the
real course deadline and any required deliverable beyond the report and deck (for example a presentation
date); the course retention deadline (task W4.1); each person's real availability on Fri 13 – Tue 17 Nov.

| Recruiter | Participants recruited (target ≥ 5 each) | Slots booked by Fri 6 Nov |
|---|---|---|
| Member 1 | | |
| Member 2 | | |
| Member 3 | | |
| Member 4 | | |
| Member 5 | | |
| **Total (target 25)** | | |
