# Task Split and Timeline — Five Workstreams plus a Shared Report/Slides Track

**Latest project status (updated 11 Nov):** local hashed freeze and once-only five-model final evaluation
completed (545 test cases); real case pack and 11 genuine charts exported and validated. Final
aggregates/plots and completed lock are retained; model, snapshot and case lookup stay private.
Model card/results and member handover are in HANDOFF sections 8/12. W3's implementation and
local execution are complete. The canonical assignment is now locally sealed under owner
authorization; private assignment handover and pre-collection coordination are reported complete
by the team (4 Nov). Independent W5 clean-clone verification is complete. The main human study is
complete: 50/50 assigned participants, 25 per group, 500 scored case responses and no exclusions.
Quantitative aggregate analysis and report-ready assets are complete; qualitative coding was
completed in one pass (agreement not measured). The team reports the real-form build, restricted response
storage, live acceptance/export checks and pilot complete (4 Nov); clean-clone/evidence verification
was completed on 4 Nov.
Earlier "test not run" notes below are historical and superseded; never rerun the final evaluation.

Updated 2 Nov 2026 from the original 27 Oct team plan. Workstream owners are recorded in §10;
reviewer acceptance and the report editor still need team confirmation. Methodology and
protocol live in `docs/HANDOFF.md`; this file says **who does what, by when, in what order, and when
each task counts as done**.

**Accelerated amendment (2 Nov, evening; takes precedence over the original schedule/gates below):**
Yolanda replaced W1's full audit with one validation-case/two-seed exploratory smoke check.
W1.1-W1.4's original large audit outputs are omitted, not passed; W1.5 becomes a limitation note
describing the smoke result and missing evidence. The smoke check completed in 47.37 seconds,
with top-five overlap 0.8 on that single case. Default `scripts/run_explanation_audit.py` runs
the short check; only `--full-audit` opts back into the old workload. Local hashed freeze replaces
mandatory committed/tagged publication when selected; record incomplete gates without fake approvals.
Consent/privacy, genuine chart values, consistent assignment and the once-only final-test lock remain.
See HANDOFF section 12 and `config/evaluation_protocol.json`; historical requirements below do not
override this amendment. That statement describes the 2 Nov gate: a later supplementary W1 audit
completed all 544 validation cases, and collection subsequently completed.
The current full unit suite contains **97 passing tests**, with separate form checks passing.

## Current task status and launch order (updated 4 Nov)

This table is the current operational tracker. Detailed task descriptions and dates below are
the original plan unless explicitly amended here. "Implemented" does not mean independently
reviewed or accepted live. **"Completed by Yolanda"** identifies work she performed.
**"Integrated and verified by Yolanda"** identifies her integration/checking of teammates'
existing implementations, preserving original authorship. Neither label claims that member's
approval. Mixed tasks name completed and remaining components; omitted analyses are not completed.

| Workstream / task IDs | Completed or available | Still needed |
|---|---|---|
| W1 Noey: W1.1–W1.5 | Completed by Yolanda: accelerated runner, real smoke check (47.37 seconds, overlap 0.8) and limitation note in HANDOFF §8/§12. **11 Nov:** Noey completed the full 544-case validation audit (faithfulness, seed/background/perturbation stability, pair masking, recourse) in `W1_analysis/`; topic analysis reruns byte-identically | Independent review; report must say the audit used a refit with the frozen settings, ran after the final test, and was not a pre-final gate |
| W2 Han: W2.1–W2.3, W2.8 | Han's implementation integrated and verified by Yolanda; authorized spec/contract review, generator safeguards and synthetic transform integration completed by Yolanda | Address any remaining spec confirmation separately; individual live-check outcomes are not documented here |
| W2 Han: W2.4–W2.7 | **Reported complete by the team (4 Nov):** real forms, restricted response storage, live acceptance checks, exports/transform and pilot | Individual check outcomes are not recorded here; live gates are not independent W3.8 verification |
| W3 Yolanda: W3.1, W3.2, W3.4–W3.6, W3.9 | Pinned Python 3.12 verified; validation dry run; local hashed freeze; once-only final evaluation on 545 cases; final model card; real 11-case pack and 11 charts | Private handover reported complete by team (4 Nov); continue support/review. No repeat evaluation, refitting or mandatory tag |
| W3.3 / W3.8 | Reproduction tooling and hash manifests implemented; clean-clone verification completed 4 Nov | The clean-clone run passed 62 tests, four form variants and 22 saved final-evidence hashes; protocol hash matched the manifest and lock. After later bundle-hash, workbook, privacy and demo-card regressions, the current local suite passes 97 tests. The final test was not rerun. |
| W4 Harry | Existing consent/instructions integrated and verified by Yolanda; cohort-policy clarification completed by Yolanda; pilot reported complete by team | Pre-collection operational/privacy/retention arrangements and coordination reported agreed by team (4 Nov); recruitment, collection, coding and later deletion remain |
| W5 Lucas: assignment, images, analysis | Lucas's generator/renderer integrated and verified by Yolanda; canonical assignment (50 main, 4 spares, 1 pilot), 11 genuine charts and tested scoring/coding implementation completed by Yolanda; clean-clone review completed 4 Nov | Independent scoring/coding review; static demo completed 11 Nov (`figures/demo_card/`); qualitative coding done in one pass 11 Nov |
| Everyone: report/slides | Model results, human-study results and handover text available | Report final methods/deviations and the human results; cross-review, slides and rehearsal remain unverified |

**Live-form/privacy/export gates and pilot: reported complete by the team on 4 Nov.** Participant
response collection and analysis were completed on 11 Nov (50/50, no exclusions). The canonical assignment remains sealed; do not
regenerate it. Shortest remaining sequence:

1. **Reported complete by team (4 Nov):** the genuine case pack/charts and canonical assignment
   were handed over through restricted storage; the private lookup is limited to the designated scorer.
2. **Completed locally:** `data/human_study/assignment_list.csv`, private seed/rules and
   `assignment_seal.json` now exist under owner authorization. The team reports the private
   handover/acknowledgement complete (4 Nov); this does not constitute independent approval.
   Use that exact list for form links and transformation; do not regenerate or switch lists.
3. **Reported complete:** four real forms, restricted response storage, consent/routing, live
   acceptance/export checks and one pilot. Keep the team's acceptance evidence with the study materials.
4. Follow the operational/ethics, withdrawal/deletion, recruitment and codebook arrangements
   agreed by the team before sending individual study links.
5. Collect and analyse responses only if the schedule allows; target 50, minimum 40 with at least
   18 per group. Otherwise report the study as pending without claiming findings.

W3 completion is recorded on `main` as `a7fbbb5`; this documentation update follows it.
No push is claimed. Private model/snapshot/pack/lookup/charts/assignment files are ignored and
will not be transferred by pushing Git; use restricted storage.

**What changed on 27 Oct:** participants answer a **Google Form** instead of a custom-built interface
(decision D8). The study itself is unchanged: same two groups, same 10 cases, same questions, same
consent and privacy rules. §8 lists the few deviations to disclose.

**Work allocation:** report/slides writing remains shared by all five (§5). The original
near-equal hour estimates in §7 are historical, not remaining workloads: the audit was reduced
and W3 execution is complete. Rebalance outstanding form/recruitment/review work with the team.

**implementation handover (2 Nov; status updated 4 Nov):** see `docs/HANDOFF.md` section 12 for runnable commands and
remaining gates. W1 audit, W3 guarded evaluation/export/reproduction and W5 scoring/coding
implementations are available for independent review. The validation dry run, local freeze and
final evaluation and local assignment sealing are now complete; the full audit was omitted.
The team reports pre-collection coordination, live acceptance and pilot complete. Clean-clone/
evidence verification is complete; no final-test rerun occurred.
W5 is the canonical study assignment;
W2's default assignment is fixture-only.

> **Current report deadline (announced 4 Nov): Mon 16 Nov 2026.** This supersedes the earlier
> Thu 19/Fri 20 Nov finish dates for report work. Include human-study results only if collection
> and analysis are safely complete by 15 Nov; otherwise report the study as pending.

**How to read a task:** `[I]` = **independent** (can start now). `[D: W1.2]` = **depends on** that
task finishing first. **Deadline** is the latest day the task may finish; a dependent task can start
only after what it depends on is done. **Done when** is the check the reviewer uses.

## 0. Rules for everyone

1. **Test-split gate.** The final evaluation has already run once under the 2 Nov accelerated
   amendment and local hashed freeze. Preserve the completed lock; verify saved outputs, never
   repeat the evaluation or tune on the test data. The original full-audit/live-acceptance/tag
   prerequisites were waived for evaluation, not falsely marked passed. Real collection still
   requires live privacy/acceptance and pilot checks.
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
   `requirements.txt`, run `python -m unittest discover -s tests` and confirm 62 tests pass, then
   run `python forms/test_spec.py`. Also run `python -c "import tabicl, xgboost,
   interpret, shap"` (the audit and final-test scripts need `tabicl` and `xgboost`; the tests do not).
   Report any failure in the group chat.
6. **Every new script gets a small test** and writes outputs only under `tables/`, `artifacts/` or
   `figures/`, so results reproduce from one command.
7. After any DOCX change, the report editor re-exports the PDF. For the proposal, re-check the page
   count (body 4 pages, references on page 5).
8. **Schedule update:** the original weekend-buffer rule is superseded for the final-report week:
   cross-review and assembly are scheduled for Sat 14–Sun 15 Nov to meet the announced Mon 16 Nov
   deadline. If any report milestone slips, tell the group the same day. Participant safeguards
   remain mandatory.
9. **Git workflow.** Work on your own branch (`w1-audit`, `w2-forms`, ...), commit small, `git pull
   --rebase origin main` before pushing, merge to `main` only after your reviewer has looked at it, and
   never force-push. Review time is part of the plan (§7).
   Owner-authorized exception for Yolanda's current assistant work: use `main` directly without
   creating a branch. This does not claim independent review or change teammates' workflow.

## 1. Settled decisions (D1–D8)

Initial decisions were made on 27 Oct 2026 for the then-planned Thu 19 Nov finish. The current
report deadline is Mon 16 Nov 2026 (announced 4 Nov) and supersedes those schedule assumptions;
apply the documented 2 Nov amendment.
Scientific inputs are now frozen and the final evaluation completed. Record any later operational
amendment explicitly with owner approval; never silently change scientific settings or rerun the test.

| # | Decision | Settled as | Why |
|---|---|---|---|
| D1 | Final deadline and extra deliverables | **Final project report due Mon 16 Nov 2026** (announced 4 Nov): final report DOCX/PDF and slide deck if required. Earlier Thu 19/Fri 20 Nov dates are superseded for report planning. Human-study results are included only if safely collected and analysed by 15 Nov; otherwise state that they are pending. | The newly announced deadline overrides the old project schedule; participant safeguards are not waived |
| D2 | Optional narrative condition (B2) | **Dropped.** Not built; removed from the DOCX, HANDOFF and protocol (ID W5.4 unused) | Adds build and checking time to a 24-day plan; the core study is unaffected |
| D3 | How sessions run | **Online and unsupervised** (changed 31 Oct, team decision): if the study proceeds after all safeguards and the pilot pass, each participant opens their own pre-filled Google Form link. The original 13–17 Nov window is superseded because it extends past the report deadline; use results only if collection and analysis finish by 15 Nov. Disclose the mode as a deviation and limitation (§8) | Online format avoids requiring a room/session runner; deadline does not waive safeguards |
| D4 | Subgroup and proxy diagnostics on the test split too | **Yes**, descriptive, same code, run once inside the final-test script | One extra call; recorded in the protocol before the freeze |
| D5 | Decision-support demonstration (formerly "Mode A") | **Static example case card** (screenshots from validation fixtures) in the report and slides; no software | The form replaces the app; the example still shows what an officer would see |
| D6 | Pilot participants count toward the 50 | **No.** The pilot is one extra person | Keeps the 50 clean and the groups balanced (25/25) |
| D7 | Withdrawal window and anonymity | **Current plan:** responses are pseudonymised (random participant code); withdrawal is possible until de-identification; then the code link is deleted. Never call the data "anonymous" in the consent text before de-identification | Pseudonymised is not fully anonymous; withdrawal needs a link |
| D8 | Study instrument | **Google Forms, not a custom interface.** Four forms: Group A and Group B, each in two case orders (a seeded order and its exact reverse; agreed 30 Oct); explanation images made in Python; responses to a restricted Sheet | Saves about 30–40 hours in a 24-day plan; the study design is unchanged |

## 2. Participants — everyone recruits and sends their own links (W4 coordinates)

- **Target: 50 participants in total. Every team member recruits 10** voluntary adults
  (students are fine; a few staff or advisers are a bonus) and sends each their own
  link only after the required gates pass. The original 13–17 Nov collection window is superseded:
  responses used in the report must be collected and analysed by 15 Nov; if that is not feasible,
  report the human study as pending. Do not rush or bypass safeguards to meet the deadline.
- **Recruiters do not choose groups.** Each participant gets the **next unused pre-filled link** from a
  seeded assignment list (task W5.8), held by the W4 coordinator. The link carries the participant code
  and the form variant; a recruiter cannot pick or swap it. 50 splits evenly, so groups will be 25 and 25.
- **No list of who got which code.** A recruiter sends the link and never writes the code next to a
  person's name (rule 4). W4's send log holds codes only, never names.
- W4 keeps a count per recruiter only (no names or IDs in the repo). People consent only inside the
  form, before the first question.
- **Study target remains 50; minimum remains 40 completed responses with at least 18 in each group**
  (18/22 is acceptable, 17/23 is not). These are study targets, not a reason to include incomplete
  results: report achieved counts only if collection and analysis finish by 15 Nov; otherwise state
  the study was not completed for this report.
- **Replacements keep the groups balanced.** The seeded list holds 4 spare slots (two Group A, two
  Group B). If a participant does not complete (no submission by the deadline, withdrawal, incomplete), the next
  recruited participant **inherits that empty slot's group and variant**; a spare is used only when a
  slot is empty, choosing the group that keeps the totals closest to balanced. Incomplete responses are
  logged and excluded. The older documents said "8–10, minimum 4" (see §8).
- **Time:** 30–40 minutes per person on their own device (pilot, 3 Nov: about 40 by the clock, 35 self-reported); the form's last question asks how many
  minutes it took (self-reported, §8 item 3).

## 3. Timeline at a glance (2026)

Historical baseline schedule (superseded): the accelerated 2 Nov work completed the freeze, final
evaluation and case/chart export ahead of the P2/P3 dates. The original 13–18 Nov study window and
19/20 Nov finish no longer fit the announced report deadline. Use the current tracker above; do not
assume human-study results will be available for this report.

| Phase | Dates | What | Who |
|---|---|---|---|
| **P0** Setup | Tue 27 – Wed 28 Oct | Owners and editor appointed (decisions D1–D8 already settled), environment and tests | all |
| **P1** Build (validation only) | Thu 29 Oct – Fri 6 Nov | Audit, form generator, images, final-test script, send-out kit, assignment lists, report methods drafts | W1–W5 + everyone (R) |
| **P2** Gate | Mon 9 Nov | Freeze and tag; go/no-go for the test run | W1, W2, W3 |
| **P3** Final test and study cases | Tue 10 – Thu 12 Nov | One test run, export cases, build real forms, model card | W3, W2, W5 |
| **P4** Study | Original 13–18 Nov window, superseded | Pilot, responses, scoring and coding only if safeguards pass; include results only if analysed by 15 Nov | W4 coordinates; otherwise report pending status |
| **P5** Wrap-up | By Mon 16 Nov | Report sections, cross-review, slides if required, merge and final check | **everyone** |

**Checkpoints (everyone reports status at each):**

| Date | Checkpoint | Must be true |
|---|---|---|
| Fri 30 Oct | Foundations | Form spec and case-pack contract agreed, ethics note done, 20-case script selects cases, report/slide outline and Google Docs created |
| Fri 6 Nov | Build complete | Audit tables done, form acceptance passed on validation fixtures, final-test script dry-run OK, 50 participants agreed, every section has a methods draft |
| **Mon 9 Nov** | **Gate / go-no-go** | Freeze tag created; if not ready, escalate the same day |
| By 15 Nov | Human-study report cutoff | Include only data collected, checked and analysed by this date; otherwise report pending status |
| Mon 16 Nov | Final report deadline | Final report submitted; slide deck included if required |

**Final deliverables checklist (report submission by Mon 16 Nov):**
- [ ] Final report DOCX and PDF, in the repo root next to the proposal
- [ ] Slide deck (PPTX or Google Slides export), if required by the 16 Nov submission; rehearsed once, timed
- [ ] Repo on `main`: publish reviewed work when authorized; retain local hashed-freeze evidence
  and completed final-test lock (tag not mandatory under the amendment); all 97 tests and separate
  form checks passing; final outputs already under `tables/final_test/`
- [x] Model card (`docs/HANDOFF.md` §8) and README/HANDOFF updated with model results/deviations
- [x] Add actual human-study quantitative results and limitations; aggregate sources are under
  `tables/human_study/`, `figures/human_study/` and `docs/HUMAN_STUDY_RESULTS.md`
- [ ] Raw participant data deleted everywhere (Forms, Sheet, exports, Drive trash) on the confirmed retention date, after the human-results review (R7), or the date and plan recorded; aggregates only kept
- [ ] Drive folder Restricted, no Drive or Form URL in the repo
- [ ] Final report discloses the deviations in §8

**If behind:** optional W3.7 and demo-card polish can be dropped; rebalance remaining work.
Full audits are already omitted under the amendment. Do not waive privacy/consent or silently
change the instrument, and never repeat the completed final evaluation.

## 4. Workstreams (technical and operational)

### W1 Noey — Explanation evidence and limitation note

| ID | Current task | Status / evidence | Still needed |
|---|---|---|---|
| W1.1 | Accelerated validation runner and timing | **Completed by Yolanda.** `scripts/run_explanation_audit.py`; timing estimate and genuine smoke evidence in `artifacts/` | Independent review; original 20-case execution replaced, not completed |
| W1.2 | Full deletion faithfulness audit | **Omitted before the final test** under the authorized amendment. **Later completed (11 Nov, Noey):** 544-case validation audit in `W1_analysis/`, on a refit with the frozen settings (not the frozen bundle); it does not retroactively pass the 2 Nov gate (positive faithfulness area in 536/544 cases) | Disclose that it was omitted before the final test and completed later on a refit |
| W1.3 | Full multi-case seed/background/perturbation stability | **Omitted before the final test**; one-case/two-seed execution check completed, overlap 0.8, not general stability. **Later completed (11 Nov, Noey):** 544-case validation audit in `W1_analysis/`, on a refit with the frozen settings (not the frozen bundle); it does not retroactively pass the 2 Nov gate (mean top-5 overlap: seed 0.818, background 0.745, perturbation 0.996) | Report as post-hoc evidence; no stability-certification claim |
| W1.4 | Full constrained-recourse audit | **Omitted before the final test**; helper implementation is not evidence of feasible interventions. **Later completed (11 Nov, Noey):** 544-case validation audit in `W1_analysis/`, on a refit with the frozen settings (not the frozen bundle); it does not retroactively pass the 2 Nov gate | Recourse scenarios describe model responses only; no causal/recourse claims |
| W1.5 | Smoke result and limitation note | **Completed by Yolanda:** HANDOFF §8/§12 and protocol-deviation text | Reviewer checks note; Noey incorporates it into final report R3 without invented full-audit results |

Noey remains the suggested report editor (R1/R8); appointment is not verified.
ID W1.6 moved to W2.2. The original full audit remains optional via `--full-audit`.

### W2 Han — Study instrument: Google Forms (build and test) 

| ID | Current task | Status / evidence | Still needed |
|---|---|---|---|
| W2.1 | Four-form spec: consent, 18+, code, instructions, practice, ten scored cases, confidence and three written prompts | **Han's implementation integrated and verified by Yolanda;** authorized review/cohort wording completed by Yolanda in `docs/form_spec.md` | Resolve unchecked confirmations; verify built live wording |
| W2.2 | Public pack/private lookup contract | **Existing contract integrated and verified by Yolanda;** contract review and genuine pack format/provenance checks completed by Yolanda | Independent review; never upload the private lookup to Forms |
| W2.3 | Generator for A1/A2/B1/B2 | **Han's generator integrated and verified by Yolanda;** fail-closed safeguards and synthetic checks completed by Yolanda | Preserve the completed real build and live acceptance evidence |
| W2.4 | Privacy/settings and restricted response Sheet | **Reported complete by the team (4 Nov):** response-sheet access/privacy settings and new-form checks | Individual outcomes are not recorded here; no independent W3.8 verification is implied |
| W2.8 | Wide-to-long response transform with actual source variants | **Han's transform integrated and verified by Yolanda;** source-identity/duration safeguards and synthetic CSV checks completed by Yolanda | Use the exact canonical assignment; live export/transform checks are reported complete under W2.5 |
| W2.5 | Live export/transform/cleanup check | **Reported complete by the team (4 Nov):** real-form exports and transformation checked | Detailed export results are not recorded here; keep pilot/test data out of study analysis |
| W2.6 | Seven live checks in HANDOFF §7 | **Reported complete by the team (4 Nov):** live checks and consent wording verified | Individual outcomes are not recorded here; no independent W3.8 verification is implied |
| W2.7 | Four real forms and individual prefilled links | **Reported complete by the team (4 Nov):** built from the genuine pack/charts and canonical assignment | Preserve the exact assignment for links/transformation; do not regenerate |

### W3 Yolanda — Final evaluation, study cases and reproducibility

Current W3 execution status: **completed locally** under the authorized accelerated amendment.
The pinned Python 3.12 environment, 97 tests and separate form checks pass. The local snapshot,
single final evaluation, final tables/model card, real case pack and 11 charts are complete.
The full audit was stopped/replaced by the smoke check, not left running. No independent approval
of the scientific study is claimed. W3.8 clean-clone/evidence verification was completed 4 Nov;
live W2 acceptance is reported complete by the team.
The rows below record current execution and remaining review explicitly.

| ID | Task | Depends | Deadline | Done when |
|---|---|---|---|---|
| W3.1 | **Completed:** pinned Python 3.12 environment, all 62 unit tests and separate form checks pass. | [I] | Completed 2 Nov | Exact dependency pins verified; independent reproduction is still separate. |
| W3.2 | **Completed:** guarded final runner, validation dry run, 2,000-resample paired comparisons, calibration, runtime and subgroup/proxy outputs. Exclusive pre-access lock refuses a repeat run even if tables disappear. | [I] | Completed 2 Nov | Synthetic guard/output tests pass; completed lock retained. |
| W3.3 | **Completed locally:** reproduction tooling for tests, fixtures and optional validation outputs; saved final evidence verified by hashes, never regenerated. | [I] | Completed 2 Nov | Independent verification is W3.8; private assets require separate restricted handover. |
| W3.4 | **Completed by local hashed freeze** under the 2 Nov amendment; scientific inputs and exact checkpoint copied and hashed, incomplete gates recorded honestly. | W3.2; accelerated amendment | Completed 2 Nov | Manifest/model binding and unchanged inputs verified; no tag or independent approval claimed. |
| W3.5 | **Completed:** five-model final evaluation on 545 test cases; `tables/final_test/` and completed lock retained in commit `a7fbbb5`. | [D: W3.4] | Completed 2 Nov | Saved hashes verified; never rerun or retune. |
| W3.9 | **Completed:** ten prediction-only selected test cases (5 flagged/5 unflagged), one validation practice, genuine grouped SHAP export and 11 charts. | [D: W3.5] | Completed 2 Nov | Pack provenance, deterministic selection/flags and private lookup verified; restricted handover remains. |
| W3.6 | **Completed:** HANDOFF §8 model card, final tables/figures and limitations. | [D: W3.5] | Completed 2 Nov | Final numbers agree with saved aggregates; human results not claimed. |
| W3.7 | **Completed 11 Nov (grouped form):** `scripts/run_enrolled_sensitivity.py` → `tables/sensitivity/`; validation + Enrolled shares only, test untouched. Three-class variant not run. Results in HANDOFF §5. | [I] | Completed 11 Nov | Labelled as sensitivity; not used for model selection. |
| W3.8 | **Completed 4 Nov:** clean-clone tests/fixture checks and saved-evidence verification. All 62 unit tests, four form variants and 22 final-evidence hashes passed; the protocol hash matched the manifest and lock. | [D: W3.3, W3.5, W3.6] | Completed 4 Nov | Final evaluation was not rerun. Further teammate review may be recorded if required; preserve the lock and saved evidence. |

### W4 Harry — Human-study operations and analysis

| ID | Current task | Status / evidence | Still needed / prerequisites |
|---|---|---|---|
| W4.1 | Consent, information sheet, withdrawal/access/retention arrangements | **Operational arrangements reported agreed by the team (4 Nov); live consent/privacy checks reported complete** | Preserve the agreed consent/access/retention procedures in the study record; collection must follow them |
| W4.5 | Recruitment plan and counts; any collection used in the report must finish in time for analysis by 15 Nov | **Recruitment preparation/coordination reported complete by team (4 Nov); participant counts and send/exclusion log remain collection-dependent** | Target 50, minimum 40 with 18/group. If data cannot be collected and analysed by the report deadline, report study status as pending rather than extending the report schedule or claiming results |
| W4.2 | Standard instructions, invitation/reminder/troubleshooting kit and debrief | **Preparation confirmed by team (4 Nov);** existing instructions/debrief integrated and cohort-policy clarification completed | Use agreed materials for recruitment; record actual invitations/support without storing contact details beside participant codes |
| W4.3 | Codebook: comprehension, actionability, missing information, `other/unclear`; paraphrased examples | **Pre-collection coding plan/training reported agreed by the team (4 Nov)** | Apply the agreed codebook and record coding decisions; actual coding waits for responses |
| W4.12 | Participant-number and replacement-rule parity across protocol/HANDOFF/proposal | **Partial:** current CSV allocation checks completed by Yolanda | Complete independent proposal DOCX/PDF parity check; no claim of completed three-document sign-off |
| W4.6 | One-person real-form pilot | **Reported complete by the team (4 Nov)** | Retain pilot outcome; ensure pilot/test data are excluded from study analysis and removed per the retention plan |
| W4.7 | Individual links, code-only send/exclusion log, daily response checks and restricted backup | **Completed (11 Nov):** 50 codes, 10 per recruiter, private `send_log.csv` matched to the sealed assignment | After W4.5/W4.6; log recruiter/date sent/submission/exclusion, no contact details beside codes; use canonical slots/spares and report achieved counts |
| W4.8 | Shared qualitative coding and 20% double-coding | **Completed as a single pass (11 Nov); double-coding not done (deviation 12).** All 1,500 answers coded plus 5.7 intervention ratings; results in `docs/HUMAN_STUDY_RESULTS.md`. Earlier: private send log built from the team's send-log sheet (50 codes, 10 per recruiter, matched to the sealed assignment); assignments generated: 5 worksheets of 360 items (12 participants each), 10 participants double-coded, no member codes their own recruits (`data/human_study/coding/`, git-ignored) | Optional: a member blind-codes the 20% subset and runs `agreement`; otherwise report agreement as not measured |
| W4.11 | Real response transformation/scoring and descriptive analysis | **Completed (11 Nov):** `docs/HUMAN_STUDY_RESULTS.md`, `tables/human_study/` | W4.7 plus reviewed W2.8/W5.6; participant-level accuracy, confidence, self-reported time, counts and practice checks; no significance claims |
| W4.10 | Delete raw responses/link files everywhere at confirmed retention date | **Pending; not due merely because preparation is complete** | Complete R7 before the deletion deadline; if deadline is earlier, move review earlier. Delete Forms/Sheet/CSV/backups/Drive trash and record privately; retain aggregates only |

ID W4.9 moved to W5.8.

### W5 Lucas — Explanation images, assignment lists, demo card and scoring script (code-heavy)

| ID | Current task | Status / evidence | Still needed |
|---|---|---|---|
| W5.8 | Canonical seeded assignment: 50 main, 4 spares, 1 B1 pilot; private seed/rules/hash | **Assignment completed by Yolanda using Lucas's generator, integrated and verified by Yolanda:** generated once, exact reproduction/hash verified; 8 tests pass; local seal records owner authorization; team reports restricted handover acknowledged (4 Nov) | Same CSV drives build, links and transform; no codes/seed in Git |
| W5.9 | Coding assignment/agreement tooling: non-recruiter primary, random 20% second coder, group omitted where practical | **Completed:** assignment, raw agreement, `reconcile` with adjudication sheet, and aggregate themes by group and by hidden model flag (11 Nov); full CLI loop tested on synthetic data (`tests/test_coding_reconcile.py`) | Independent review; real coding is W4.8 |
| W5.3 | Renderer and 11 genuine Group B charts, shared pack scale and neutral legend | **Lucas's renderer integrated and verified by Yolanda; chart generation completed by Yolanda.** Text checks pass and one real chart visually inspected | Complete all-chart visual/live profile/order parity; no comprehensive visual acceptance claimed |
| W5.6 | Participant-level scoring, group summaries, confidence/time and practice-check reporting | **Implementation and synthetic scoring/exclusion/practice-check regressions completed by Yolanda** | Lucas independently reviews; real analysis awaits consented post-pilot data (W4.11) |
| W5.1 | Static demo card from a validation fixture for report/slides | **Completed 11 Nov:** `scripts/build_demo_card.py` → `figures/demo_card/` (validation row 916, frozen model, refuses study cases, no recourse); 2 tests | Show profile, labelled estimated risk, contributions and limitations; no fabricated recourse or test-case answer leakage; review before publication |
| W5.5 | Full-audit deletion/stability figures | Superseded: the later W1 audit produced them (`W1_analysis/03_Full_Audit/Figures/`, `figures/report_ready/explanation_stability.png`) | Label them as refit-based, post-final-test evidence |

W5 also does **W3.8** (clean-clone verification) and builds the coding-assignment script **W5.9**; the coding itself is shared by all five (**W4.8**).
IDs W5.2, W5.4 and W5.7 are unused: those tasks moved to W3.9, dropped (D2) and W4.11.

## 5. Report and slides — everyone (shared track)

All R1–R9 final-report/deck tasks remain pending or unverified. Completed HANDOFF/model-card
source text is available for drafting; it does not prove that the shared final documents or
slides exist, have been reviewed or rehearsed.

**TA feedback response plan (4 Nov; final project report deadline: Mon 16 Nov 2026).**
Update 11 Nov: the numbers and wording for every point below are collected in
`docs/report_notes/TA_FEEDBACK_FINAL_REPORT_NOTES.md` (each point marked [DOC] for the final report or [CODE] for
analyses run: flag composition, bar sums, and a refit without protected attributes). The larger-SHAP-
budget rerun was skipped; report the budget as a limitation. The unticked boxes below are report-writing
tasks. Where the boxes below say a stability, faithfulness or recourse audit was "omitted", that was true
on 4 Nov; the W1 audit later ran them post-hoc on all 544 validation students, so report them as
post-final, validation-only evidence instead.
The proposal stays unchanged; address the feedback in the final report and presentation. Treat
the checklist below as required report work. The existing final-test results and lock are frozen:
never rerun, retune, or replace the one-time final test. Any new eligibility check must use the
validation split and be labelled exploratory/post-hoc; it cannot establish real-world eligibility
or performance for the excluded Enrolled group.

- [x] **Eligibility and the 108 validation flags (exploratory check, 4 Nov):** the saved fitted
  model bundle's SHA-256 matches `artifacts/final_test.lock`; its model was applied to validation
  rows only, without rerunning training or the final-test evaluation. The 544 validation rows
  yielded 108 flags, reproducing the saved validation confusion matrix. Of 49 records with no
  first-semester evaluations (36 Dropout, 13 Graduate), 25 were flagged; all 25 were Dropout.
  Thus 25/108 flags (23.1%) had no evaluations, and 83 flags had at least one. In the
  at-least-one-evaluation proxy subset (495 records, 177 Dropout), recalculating the top-20%
  capacity flagged 99; confusion matrix TN=318, FP=0, FN=78, TP=99 (recall 0.559, precision
  1.000, ROC-AUC 0.9486). This is a post-hoc validation sensitivity, not confirmatory evidence.
  Evaluation presence is only a proxy: it does not prove enrollment, eligibility, or reachability
  at the decision point, and this analysis says nothing about the excluded Enrolled outcome group.
- [ ] Explain that “all 108 were dropouts” is a validation-set, capacity-limited observation,
  not perfect general performance or evidence that these students would benefit from outreach.
  Discuss what the model adds beyond observable first-semester non-participation and what its
  explanations can and cannot tell an officer. Report that Enrolled outcomes were excluded and
  performance on Enrolled students is unknown; do not imply the optional sensitivity analysis
  or current model establishes their performance.
- [ ] **SHAP budget and explanation reliability:** state that the model has 33 input features
  and `max_evals=67` is the permutation explainer budget (`2 × 33 + 1`), not 67 cases. Explain
  that the full multi-case/seed/background/perturbation stability and faithfulness audits were
  omitted. The one-case, two-seed overlap of 0.8 is an execution smoke check, not stability
  evidence. If further checks are feasible, keep them validation-only, justify any larger budget,
  and report them as exploratory; otherwise make the uncertainty explicit.
- [ ] **Human-study interpretation:** state plainly that participants are asked to infer the
  model's flag, so the study tests output comprehension/inference from profiles, with or without
  contribution charts. Discuss whether contribution directions and sizes could let participants
  reconstruct the flag, despite hiding numeric scores, base value, and output. Do not claim the
  study demonstrates better support-officer decisions, improved interventions, or student outcomes.
- [ ] **Protected attributes:** explain that protected attributes are present in the research
  model and why they were retained for this analysis; discuss the observed subgroup differences
  as descriptive, not proof of fairness or a reason to allocate real outreach by protected status.
  State a clear operational position: these results do not authorize deployment/use of protected
  attributes for prioritisation; any such use would require a separately justified, governed
  decision and appropriate sensitivity analysis.
- [ ] **Fee-status recourse:** explain the direction of the observed model association without
  implying that paying fees or changing fee status prevents dropout. Fee/debtor status can reflect
  underlying financial circumstances and may be associated with risk in either direction; a
  model-score change is not a causal effect, a student-controlled action, or a recommendation.
  Disclose that the full recourse audit was omitted.
- [ ] **Reader-first report:** make page one understandable to a student-support officer: the
  decision being studied, which records the model covers, what the evidence says, and the main
  eligibility/uncertainty limitation. Define “top-20% outreach capacity” in plain language and
  avoid unexplained protocol/version jargon. Align proposed methods with what was actually done:
  disclose the accelerated local freeze, omitted audits, team-reported completed live acceptance, and the
  Google Forms study design; do not describe the proposal's planned interface/audits as completed.
- [ ] **Evidence and final review:** verify every new count against saved validation evidence,
  clearly label validation vs. locked final-test results, avoid reporting individual case details,
  and have a teammate check that each TA concern above is answered in the report. If the human
  study is incomplete by the deadline, report its status and limitation rather than inventing results.

**Updated delivery schedule overriding older milestone dates in this document:**
- By **Mon 9 Nov**: complete the validation-only eligibility check or record why the saved
  evidence does not support it; agree the protected-attribute and human-study interpretations.
- By **Thu 12 Nov**: all report sections address the checklist and are assembled in a readable draft.
- By **Sat 14 Nov**: independent cross-review; resolve evidence, eligibility, and plain-language gaps.
- By **Sun 15 Nov**: final report, references, figures, and PDF checked for consistency.
- By **Mon 16 Nov**: submit the final project report. Human-study results are included only if
  actually collected and analysed by then; otherwise report that work as pending.

**One appointed report editor** assembles the Word report and the slide deck. They do **not** write
everyone's text. Each workstream owner writes the section and slides for their own part, and each
section is cross-reviewed by a different workstream.

| Report section | Written by | Draft source |
|---|---|---|
| Introduction, data and EDA, limitations | W3 owner | HANDOFF §2–§4 |
| Predictive results and model comparison (final test), model card, reproducibility | W3 owner | W3.5, W3.6 |
| Explanation audit and limitations | W1 owner | `W1_analysis/03_Full_Audit/Reports/W1_COMPLETE_REPORT.md`; disclose that this was a later validation-only refit audit, not the pre-final gate |
| Study instrument (Google Forms), form screenshots, acceptance results, disclosed deviations | W2 owner | W2.6, HANDOFF §7 |
| Explanation images and validation-only demo; disclose omitted audit figures | W5 owner | Completed W5.3 and W5.1 (11 Nov); W5.5 superseded by the later W1 audit figures |
| Human study: methods, ethics and quantitative results | W4 owner | `docs/HUMAN_STUDY_RESULTS.md` and `tables/human_study/`; qualitative findings only after team coding |
| Discussion and conclusion | **everyone**: each owner contributes 3 bullet points; the editor merges them | R3 |

| ID | Task | Depends | Deadline | Done when |
|---|---|---|---|---|
| R1 | Report and slide setup: outline, section and slide owners, shared Google Doc and Slides in the team Drive (drafts only, no raw data), template, and the **report editor appointed** (§10). | [I] | Fri 30 Oct | Outline and owner list shared; empty Doc and Slides exist. |
| R2 | **Methods drafts:** each owner writes what their part built and how (no results yet), matching HANDOFF. | [D: R1] | Fri 6 Nov | Every section has a methods draft; each owner's reviewer has read it. |
| R3 | **Results evidence package:** model, later W1 validation audit and quantitative human-study aggregate tables/figures are prepared under `tables/report_ready/` and `figures/report_ready/`. Each owner adds limitations and 3 discussion bullets. | [D: W1 review, W3.6, R2] | Thu 12 Nov | Every number matches saved evidence; no causal, deployment or uncompleted qualitative claim is added. |
| R4 | **Cross-review:** each owner reads and comments on a different workstream's section (W1→W2, W2→W3, W3→W4, W4→W5, W5→W1), checking numbers against tables and claims against HANDOFF and the TA-response checklist above. | [D: R3] | Sat 14 Nov | Comments resolved by the writers; no claim beyond the evidence. |
| R5 | **Slides:** each owner makes 2–3 slides for their own part. W4 uses the completed aggregate quantitative study results; qualitative themes remain omitted until coded. One shared look, one message per slide. | [D: R1, R3] | Sat 14 Nov | Draft deck complete and every result traces to an aggregate table. |
| R6 | **Human-study results section and slide** by the W4 owner using `docs/HUMAN_STUDY_RESULTS.md`, including sample size, uncertainty, C01 sensitivity and limitations. | [D: W4.8, W4.11, R4] | Sun 15 Nov | Reported results match aggregate analysis; qualitative themes are absent until coding is complete. |
| R7 | **Review of the human-results section/status:** the **W3 owner** (not the author) checks any results against analysis outputs and verifies deviations, sample size, and absence of significance or causal claims. | [D: R6] | Sun 15 Nov | Comments resolved by the W4 owner before the merge. |
| R8 | **Merge and export:** the report editor assembles the final report DOCX, adds references and figures, exports the PDF, and merges the deck. | [D: R4, R5, R7] | Sun 15 Nov | Report DOCX and PDF and the deck are complete and consistent. W3.8 clean-clone/evidence prerequisite was completed 4 Nov. |
| R9 | **Final read:** two members who are not the editor read the PDF and deck end to end; README and HANDOFF updated if needed. | [D: R8] | Mon 16 Nov | No inconsistency left; final report is ready to submit by the announced deadline. |

## 6. Critical path

```
By Thu 12 Nov       R3 report sections; validation eligibility sensitivity/status included
Completed 4 Nov     W3.8 clean-clone/evidence verification (saved final hashes; no rerun)
By Sat 14 Nov       R4 cross-review · R5 slide drafts
By Sun 15 Nov       R6 human-study results only if collected/analysed, otherwise pending status
                    · R7 review · R8 merge and PDF export
Mon 16 Nov          R9 final read · submit final project report
```

Dates before the current report milestones are historical, not evidence that a gate passed. The
team reports the form, privacy, consent and pilot gates complete (4 Nov); individual check outcomes
are not documented here. Follow the agreed safeguards. Any human-study data included in the report must be
collected and analysed by 15 Nov; if that is not feasible, keep the study results pending and report
that limitation. The 16 Nov deadline does not authorize skipping participant safeguards.
The final evaluation remains complete and locked; do not rerun it. W1.2–W1.4 and W5.5 were omitted.

**Current safeguards.** The team reports real W2.7, W2.4/W2.6, W4.6 and applicable pre-collection
arrangements complete (4 Nov). Send/collect only under those agreed safeguards. The final
evaluation is already completed: preserve the lock, do not refit/repeat/tune or select another
model after test access.

## 7. Fair-share check (estimated hours per person)

These are **historical full-audit-plan estimates**, not actual hours or remaining workload.
The original equal-share calculation below no longer applies after acceleration and Yolanda's
completed cross-workstream work. Reallocate remaining tasks using the current tracker.

| Person (workstream) | Technical / operational work | Shared work (all five) | Total |
|---|---|---|---|
| W1 owner (+ report editor) | 30 audit (incl. timing test) + 9 editor (R1 3, R8 6) = **39** | 41.5 | **80.5** |
| W2 owner | 4 + 2 + 12 + 3 + 6 + 4 + 5 + 4 = **40** | 41.5 | **81.5** |
| W3 owner | 8 + 6 + 2 + 3 + 9 + 7 = 35, + 3 intro/data section + 1.5 (R7 review) = **39.5** | 41.5 | **81** |
| W4 owner | 4 + 4 (W4.5) + 5 + 3 + 2 + 3 + 8 (W4.7: coordinating 50 online responses) + 3 (coding lead) + 3 + 1 + 4 (R6) = **40** | 41.5 | **81.5** |
| W5 owner | 4 (W5.8) + 12 + 7 (W5.6) + 4 + 4 + 4 (W5.9) + 4 (W3.8) = **39** | 41.5 | **80.5** |

**Shared work per person (about 41.5 h):** day-1 setup 2 · recruiting 10 participants 6 · sending
links to their own 10 and following up 7 (in-person estimate; online needs less) · shared response coding 9 (about 300 short responses plus second-coding) ·
methods draft (R2) 3 · results section (R3) 5 · cross-review (R4) 2 · slides (R5) 3 · final read and
rehearsal (R9) 1.5 · reviewing their partner's work and PRs 3.

**Result:** totals range from 80.5 to 81.5 hours (about ±0.6%); the W3 owner's R7 review is included.
Going from 25 to 50 participants adds about 15 hours per person (recruiting, following up and
coding), on top of the Google Form saving of roughly 30–40 hours of interface work. Optional W3.7
(about 6 h) is excluded; the W3 owner takes it if time allows. If the meeting finds someone with a
lighter or heavier load, move a whole task and update the table.

## 8. Participant numbers and disclosed deviations

**Participant numbers.** The plan is **50 participants (10 recruited by each team member), 25 per group,
minimum 40 with at least 18 per group, 4 spares**. On 27 Oct these numbers replaced "8–10, minimum 4" in
`docs/HANDOFF.md` §6, `config/evaluation_protocol.json` and the proposal DOCX §5.4 (PDF re-exported).
Current assignment counts match this target. W4.12 independent proposal parity review remains
pending; it is not retroactive approval for the already-completed evaluation. The final report
states achieved numbers, not assumed targets.

**Deviations from the proposal and the original plan (state these plainly in the final report):**
1. **Google Forms replace the custom browser interface** (D8): a deliberate scope decision to protect the
   3-week deadline. The study design, cases, questions and privacy rules are unchanged.
2. **Case order:** two fixed orders per group, a seeded order and its exact reverse (four forms in total), instead of a fresh random order per person. Changed on 30 Oct from three seeded orders per group (six variants); reversing the order balances position effects within each group.
3. **Timing:** per-case time is not recorded; total time is self-reported in the form's last question, because nobody observes the online sessions.
4. **Decision-support demonstration:** originally a static example card (D5). On 11 Nov a reduced local
   interface was added (`python scripts/launch_interface.py`): one HTML page showing saved results for
   543 validation students (status and rank, top-five contributions, per-student stability warning,
   debtor/tuition check, audit panel). The saved page runs no live model, has no blinded-study mode (the study used
   Google Forms, item 1), was built after the study and was not tested with users. A local what-if mode
   (`--what-if`) re-predicts edited validation students with the frozen model; this live inference goes beyond proposal
   section 5.6 (precomputed outputs only), runs only on the local machine and adds no evidence.
5. **Withdrawal and exclusions** are handled by hand through the participant code and W4's send log.
6. **Online instead of in person** (D3, changed 31 Oct because we lack the people and room time to supervise 50 sessions): participants answered unsupervised on their own devices; collection was completed on 11 Nov. Report distractions, looking things up/help from others and uncorrected chart misunderstandings as potential limitations.
7. The optional narrative condition was dropped (D2), and think-aloud notes were dropped earlier.
8. **Accelerated explanation evidence:** full deletion, multi-case seed/background/perturbation
   stability and constrained-recourse audits were omitted before the final test. The one-case/two-seed
   smoke check establishes execution only; its overlap 0.8 is not a general stability estimate.
   These audits were later completed (11 Nov) on all 544 validation cases, after the final test and
   on a refit with the frozen settings rather than the frozen model bundle (`W1_analysis/`); the
   refit's validation predictions match the frozen model (max difference 0.00001, 108/108 flags,
   `artifacts/w1_refit_identity.json`). Report
   them as post-hoc evidence about that refit, not as a passed pre-final gate.
9. **Local hashed freeze and early final evaluation:** a copied/hash-bound code/data/checkpoint
   snapshot replaced mandatory committed/pushed-tag approval. Evaluation ran once before live
   acceptance and without independent approval. Record these deviations, not false gate passes.
10. **Interpretation:** survey accuracy is agreement with hidden model flags on a fixed balanced
    panel, not true dropout accuracy, general explanation-quality certification or deployment evidence.
11. **Post-freeze code changes:** after the 2 Nov local hashed freeze, nine hashed tooling files
    changed (`forms/build_spec.py`, `forms/render_forms.gs`, `forms/test_spec.py`,
    `forms/transform_responses.py`, `requirements.txt`, `scripts/assign_human_coding.py`,
    `scripts/export_study_cases.py`, `scripts/reproduce_results.py`, `scripts/run_final_test.py`;
    checked 11 Nov against `data/local_freeze/manifest.json`). No model, data, split, protocol or
    `src/` file changed, and the final test was not rerun; the frozen snapshot copy remains the
    reference for what was evaluated.
12. **Qualitative coding:** proposal section 5.7 planned two independent reviewers double-coding at
    least 20% of written answers and reporting raw agreement. The answers were instead coded in a
    single pass, so agreement was not measured and themes are one coder's descriptive summary. The
    5.7 intervention ratings (concrete step, feasibility, actor, unsupported cause) were applied to
    all 500 suggestions.

## 9. Risks and what to do

| Risk | Early warning | Response |
|---|---|---|
| Form generator not ready by Fri 6 Nov | W2.3 slips past Wed 4 Nov | W2 escalates immediately; build the four forms by hand from the spec (copy-paste) as a fallback; the W5 owner helps |
| Fewer than 50 recruited | Fewer than 50 agreed on Fri 6 Nov | Everyone recruits more that week; the minimum is 40 with at least 18 per group |
| Online answers are rushed or careless | Very short self-reported times or near-empty written answers in the daily Sheet check (W4.7) | Use the documented exclusions; do not invent post-hoc time cutoffs. Report duration and response-quality limitations |
| Coding is too heavy in the same week as sessions and the report | Coding less than half done by Sat 14 Nov | Everyone codes about 9 h in total; code rationale and intervention fields first; the W4 owner reassigns the remainder. Do not delay the report or invent incomplete human-study findings |
| Test run reveals a problem | Odd numbers on Tue 10 Nov | Report honestly; **no tuning and no re-run**; document as a limitation |
| Retention date earlier than report submission, or later than submission | Found in W4.1 | Earlier: move the verification chain (R6, R7, W4.8) earlier. Later: keep the data in the restricted store until that date; never delete before R7 |
| Someone deletes the final-test output and re-runs the test | Missing output tables | The committed `final_test.lock` blocks the second run; report honestly if it happened (W3.2) |
| A participant does not complete | No submission in W4's send log by the deadline | The next recruit inherits that slot's group and variant (§2); log the exclusion |
| No response after the link is sent | No submission two days after sending | Recruiter sends one reminder; after the deadline the spare for that form goes to a new person (§2) |
| Responses take longer than 40 minutes (11 profiles with three written answers each) | The W4.6 pilot's self-reported time | Clarify instructions and update the advertised time. Any question/requiredness change needs explicit approval, synchronized builder/transform/spec tests and disclosure before links; do not silently shorten the instrument |
| DOCX edit conflicts | Two people edit the DOCX | Only the report editor edits it (rule 3) |
| Writing left to the last days | R2 methods drafts missing on Fri 6 Nov | Owner writes it that weekend; editor reports the gap at the checkpoint |
| SHAP/TabICL runs too slowly on laptops | The original full audit takes hours | The authorized smoke check replaces the full audit; disclose omissions. `--full-audit` is optional, not a launch gate |
| A Group B image reveals the output | Reviewer finds a probability, base value or class in an image | Fix W5.3 and rebuild; rerun the W2.6 check before the pilot |
| A participant gets the wrong form or the link is shared | The W2.8 transform reports a code on the wrong form or twice | Each link is single-use by convention and tied to a code; discard and replace the duplicate row |
| Google Form settings expose data | Summary charts, email collection or public listing found | W2.4 checklist; re-check before the pilot and before the links go out |
| `tabicl` or `xgboost` missing on someone's machine | Day-1 import check fails | Fix on Wed 28 Oct; the audit and final-test scripts need them |
| Merge conflicts in shared files | Rebase errors | Per-workstream branches (rule 9); only the editor touches the DOCX |

## 10. Owner/reviewer tracker (current execution status)

| Workstream | Owner | Reviewer | First deadline | Status |
|---|---|---|---|---|
| W1 Explanation audit | Noey | suggested: W2 owner; acceptance not confirmed | Fri 30 Oct | Original pre-final gate remained smoke-only; later 544-case validation refit audit and report package complete; independent claim review pending |
| W2 Study instrument: Google Forms | Han | W3 owner for implementation; independent live evidence not yet reviewed | Thu 29 Oct | Team reports real build, privacy/export checks and pilot complete (4 Nov); preserve acceptance evidence |
| W3 Final evaluation, study cases, reproducibility | Yolanda | Lucas (W5) | Wed 28 Oct | Local execution/model card/cases/charts complete; clean-clone/evidence verification completed 4 Nov without rerunning the final test |
| W4 Human-study operations and analysis | Harry | suggested: W5 owner | Fri 30 Oct | Collection and quantitative analysis complete for 50 participants with no exclusions; qualitative coding done in one pass; second coder (optional) and retention action remain |
| W5 Images, assignment lists, demo card, scoring script | Lucas | suggested: W1 owner; acceptance not confirmed | Mon 2 Nov | Assignment/charts/scoring and report-ready quantitative assets complete; independent review and qualitative coding support remain |
| **Report and slides editor** (assembles only; suggested: W1 owner) | Team to confirm | — | Fri 30 Oct (R1) | Appointment and report/slides completion not verified |

**Suggested reviewers** form a ring (each owner reviews the next workstream), so everyone reviews exactly
one other person's work (3 h, already counted in §7). Change it if a pair works poorly together.

**Open items only the team can fill in:** confirm reviewer assignments and the report editor; confirm
any presentation requirement; record the course retention deadline; privately supply the
participant-code-to-recruiter mapping needed to ensure coders do not code their own recruits; optionally add a
second coder for 20% of the written answers; finish independent claim review.

| Recruiter | Participants recruited (target 10 each) | Agreed by Fri 6 Nov |
|---|---|---|
| Member 1 | | |
| Member 2 | | |
| Member 3 | | |
| Member 4 | | |
| Member 5 | | |
| **Total (target 50)** | | |
