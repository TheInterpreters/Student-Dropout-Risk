# Task Split and Timeline — Five Workstreams plus a Shared Report/Slides Track

**Latest W3 status (2 Nov, evening):** local hashed freeze and once-only five-model final evaluation
completed (545 test cases); real case pack and 11 genuine charts exported and validated. Final
aggregates/plots and completed lock are retained; model, snapshot and case lookup stay private.
Model card/results and member handover are in HANDOFF sections 8/12. W3's implementation and
local execution are complete. The canonical assignment is now locally sealed under owner
authorization; Harry/Lucas acknowledgement is not claimed. Independent W5 clean-clone verification,
real-form build, restricted response storage, live acceptance, pilot and actual study are not.
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
override this amendment. No real collection or full-audit completion is claimed.
The current full unit suite contains **62 passing tests**, with separate form checks passing.

## Current task status and launch order (2 Nov, evening)

This table is the current operational tracker. Detailed task descriptions and dates below are
the original plan unless explicitly amended here. "Implemented" does not mean independently
reviewed or accepted live. **"Completed by Yolanda"** identifies work she performed.
**"Integrated and verified by Yolanda"** identifies her integration/checking of teammates'
existing implementations, preserving original authorship. Neither label claims that member's
approval. Mixed tasks name completed and remaining components; omitted analyses are not completed.

| Workstream / task IDs | Completed or available | Still needed |
|---|---|---|
| W1 Noey: W1.1–W1.5 | Completed by Yolanda: accelerated runner, real smoke check (47.37 seconds, overlap 0.8) and limitation note in HANDOFF §8/§12 | Independently review the note; integrate into final report. Full deletion, multi-case stability and recourse audits are **omitted**, not passed |
| W2 Han: W2.1–W2.3, W2.8 | Han's implementation integrated and verified by Yolanda; authorized spec/contract review, generator safeguards and synthetic transform integration completed by Yolanda | Resolve remaining spec confirmations; build real forms and complete independent/live checks |
| W2 Han: W2.4–W2.7 | Partial old-form inspection and autosave disabling completed by Yolanda only | Restrict response storage; repeat all seven live checks on the real build; verify real exports/transform and closure outside testing. Tasks as a whole remain pending |
| W3 Yolanda: W3.1, W3.2, W3.4–W3.6, W3.9 | Pinned Python 3.12 verified; validation dry run; local hashed freeze; once-only final evaluation on 545 cases; final model card; real 11-case pack and 11 charts | Private handover to form builder/scorer; support review. No repeat evaluation, refitting or mandatory tag |
| W3.3 / W3.8, Lucas reviewer | Reproduction tooling and hash manifests implemented; local checks pass | Independent clean-clone verification of tests/validation reproduction and saved final evidence; never regenerate final-test results |
| W4 Harry | Existing consent/instructions integrated and verified by Yolanda; cohort-policy clarification completed by Yolanda | Confirm applicable course requirements, retention/access/withdrawal arrangements, remaining send-out kit, codebook and recruitment plan; pilot, collection, coding and deletion remain pending |
| W5 Lucas: assignment, images, analysis | Lucas's generator/renderer integrated and verified by Yolanda; canonical assignment (50 main, 4 spares, 1 pilot), 11 genuine charts and tested scoring/coding implementation completed by Yolanda | Harry/Lucas acknowledge private handover; complete visual/live parity and independent scoring/coding reviews; static demo and verification sign-off pending |
| Everyone: report/slides | Model results and handover text available | Report final methods/deviations, then actual human results after collection; cross-review, slides and rehearsal remain unverified |

**Ready to build the real forms: yes, the canonical assignment is now available. Ready to send to real
participants: no.** Shortest remaining sequence:

1. Yolanda privately hands over `data/study_cases/case_pack_study.json` and the 11 images in
   `forms/out/images_study/`; the private lookup goes only to the designated scorer.
2. **Completed locally:** `data/human_study/assignment_list.csv`, private seed/rules and
   `assignment_seal.json` now exist under owner authorization. Harry/Lucas acknowledge the
   private handover; no independent approval is claimed. Use that exact list for form links
   and transformation; do not regenerate or switch lists after distribution.
3. Han builds four real forms from the genuine pack/charts and canonical assignment, initially
   closed. Disable autosave manually on every newly built form.
4. Sheet/Drive owner restricts raw-response access. Han/reviewer check consent/decline routing,
   hidden outputs, wording, profile/chart/order parity, signed-out access and export transformation.
5. Harry runs one pilot, checks duration and phone readability, fixes/logs issues and removes pilot
   data from study analysis. Confirm operational/ethics arrangements before real recruitment.
6. Only then send individual study links. Target 50; minimum 40 with at least 18 per group.

W3 completion is recorded on `main` as `a7fbbb5`; this documentation update follows it.
No push is claimed. Private model/snapshot/pack/lookup/charts/assignment files are ignored and
will not be transferred by pushing Git; use restricted storage.

**What changed on 27 Oct:** participants answer a **Google Form** instead of a custom-built interface
(decision D8). The study itself is unchanged: same two groups, same 10 cases, same questions, same
consent and privacy rules. §8 lists the few deviations to disclose.

**Work allocation:** report/slides writing remains shared by all five (§5). The original
near-equal hour estimates in §7 are historical, not remaining workloads: the audit was reduced
and W3 execution is complete. Rebalance outstanding form/recruitment/review work with the team.

**Implementation handover (2 Nov):** see `docs/HANDOFF.md` section 12 for runnable commands and
remaining gates. W1 audit, W3 guarded evaluation/export/reproduction and W5 scoring/coding
implementations are available for independent review. The validation dry run, local freeze and
final evaluation and local assignment sealing are now complete; the full audit was omitted.
Independent assignment acknowledgement, live acceptance and pilot remain incomplete.
W5 is the canonical study assignment;
W2's default assignment is fixture-only.

> **Deadline (settled):** "3rd week of November" = **Mon 16 – Fri 20 Nov 2026**. The plan finishes
> everything by **Thu 19 Nov**; **Fri 20 Nov is buffer** and the hard stop.

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
8. **Weekends are buffer, not plan.** If a deadline slips, tell the group the same day. (Participants
   may also answer on Sat 14 / Sun 15 Nov.)
9. **Git workflow.** Work on your own branch (`w1-audit`, `w2-forms`, ...), commit small, `git pull
   --rebase origin main` before pushing, merge to `main` only after your reviewer has looked at it, and
   never force-push. Review time is part of the plan (§7).
   Owner-authorized exception for Yolanda's current assistant work: use `main` directly without
   creating a branch. This does not claim independent review or change teammates' workflow.

## 1. Settled decisions (D1–D8)

Decided on 27 Oct 2026 to protect the Thu 19 Nov finish; apply the documented 2 Nov amendment.
Scientific inputs are now frozen and the final evaluation completed. Record any later operational
amendment explicitly with owner approval; never silently change scientific settings or rerun the test.

| # | Decision | Settled as | Why |
|---|---|---|---|
| D1 | Final deadline and extra deliverables | **Fri 20 Nov 2026** hard stop (3rd week of November), team finish Thu 19 Nov. Deliverables: final report (DOCX and PDF) and the slide deck; if the instructor asks for more, tell the report editor at once and it uses the buffer day | Fixed date for every task deadline |
| D2 | Optional narrative condition (B2) | **Dropped.** Not built; removed from the DOCX, HANDOFF and protocol (ID W5.4 unused) | Adds build and checking time to a 24-day plan; the core study is unaffected |
| D3 | How sessions run | **Online and unsupervised** (changed 31 Oct, team decision): each participant opens their own pre-filled Google Form link on their own device, in their own time, between Fri 13 and Tue 17 Nov. No room, laptops or session runner. Disclosed in the report as a deviation and a limitation (§8) | We do not have the people or room time to supervise 50 sessions; the cases, questions, groups and privacy rules are unchanged |
| D4 | Subgroup and proxy diagnostics on the test split too | **Yes**, descriptive, same code, run once inside the final-test script | One extra call; recorded in the protocol before the freeze |
| D5 | Decision-support demonstration (formerly "Mode A") | **Static example case card** (screenshots from validation fixtures) in the report and slides; no software | The form replaces the app; the example still shows what an officer would see |
| D6 | Pilot participants count toward the 50 | **No.** The pilot is one extra person | Keeps the 50 clean and the groups balanced (25/25) |
| D7 | Withdrawal window and anonymity | **Current plan:** responses are pseudonymised (random participant code); withdrawal is possible until de-identification; then the code link is deleted. Never call the data "anonymous" in the consent text before de-identification | Pseudonymised is not fully anonymous; withdrawal needs a link |
| D8 | Study instrument | **Google Forms, not a custom interface.** Four forms: Group A and Group B, each in two case orders (a seeded order and its exact reverse; agreed 30 Oct); explanation images made in Python; responses to a restricted Sheet | Saves about 30–40 hours in a 24-day plan; the study design is unchanged |

## 2. Participants — everyone recruits and sends their own links (W4 coordinates)

- **Target: 50 participants in total. Every team member recruits 10** voluntary adults from the
  AIT community (students are fine; a few staff or advisers are a bonus) and **sends each one their own
  link** from W4 between Fri 13 and Tue 17 Nov, with one reminder after two days. Each recruiter has
  **10 people who agreed to take part by Fri 6 Nov**.
- **Recruiters do not choose groups.** Each participant gets the **next unused pre-filled link** from a
  seeded assignment list (task W5.8), held by the W4 coordinator. The link carries the participant code
  and the form variant; a recruiter cannot pick or swap it. 50 splits evenly, so groups will be 25 and 25.
- **No list of who got which code.** A recruiter sends the link and never writes the code next to a
  person's name (rule 4). W4's send log holds codes only, never names.
- W4 keeps a count per recruiter only (no names or IDs in the repo). People consent only inside the
  form, before the first question.
- **Minimum: 40 completed responses with at least 18 in each group** (so 18/22 is acceptable, 17/23 is
  not). If fewer than 50 submit by Tue 17 Nov, proceed once the minimum is met and report the achieved
  sample honestly; below the minimum, describe the study as pilot-scale.
- **Replacements keep the groups balanced.** The seeded list holds 4 spare slots (two Group A, two
  Group B). If a participant does not complete (no submission by the deadline, withdrawal, incomplete), the next
  recruited participant **inherits that empty slot's group and variant**; a spare is used only when a
  slot is empty, choosing the group that keeps the totals closest to balanced. Incomplete responses are
  logged and excluded. The older documents said "8–10, minimum 4" (see §8).
- **Time:** about 30 minutes per person on their own device; the form's last question asks how many
  minutes it took (self-reported, §8 item 3).

## 3. Timeline at a glance (2026)

Historical baseline schedule: the accelerated 2 Nov work completed the freeze, final evaluation
and case/chart export ahead of the P2/P3 dates. Use the current tracker above for completion and
launch gates; dates below do not require waiting to build the real forms.

| Phase | Dates | What | Who |
|---|---|---|---|
| **P0** Setup | Tue 27 – Wed 28 Oct | Owners and editor appointed (decisions D1–D8 already settled), environment and tests | all |
| **P1** Build (validation only) | Thu 29 Oct – Fri 6 Nov | Audit, form generator, images, final-test script, send-out kit, assignment lists, report methods drafts | W1–W5 + everyone (R) |
| **P2** Gate | Mon 9 Nov | Freeze and tag; go/no-go for the test run | W1, W2, W3 |
| **P3** Final test and study cases | Tue 10 – Thu 12 Nov | One test run, export cases, build real forms, model card | W3, W2, W5 |
| **P4** Study | Fri 13 – Wed 18 Nov | Pilot, 50 online responses, scoring, shared coding | W4 coordinates; everyone sends their own links |
| **P5** Wrap-up | Mon 16 – Thu 19 Nov | Report sections, cross-review, slides, merge, final check | **everyone** |
| **Buffer** | Fri 20 Nov | Final export and submission | all |

**Checkpoints (everyone reports status at each):**

| Date | Checkpoint | Must be true |
|---|---|---|
| Fri 30 Oct | Foundations | Form spec and case-pack contract agreed, ethics note done, 20-case script selects cases, report/slide outline and Google Docs created |
| Fri 6 Nov | Build complete | Audit tables done, form acceptance passed on validation fixtures, final-test script dry-run OK, 50 participants agreed, every section has a methods draft |
| **Mon 9 Nov** | **Gate / go-no-go** | Freeze tag created; if not ready, escalate the same day |
| Fri 13 Nov | Study start | Real forms built, pilot passed, links sent |
| Tue 17 Nov | Responses close (23:59) | 50 responses complete (minimum 40, at least 18 per group); slide drafts in |
| Thu 19 Nov | Finish line | Report, slides, PDF, model card, README and HANDOFF final |

**Final deliverables checklist (all done by Thu 19 Nov):**
- [ ] Final report DOCX and PDF, in the repo root next to the proposal
- [ ] Slide deck (PPTX or Google Slides export), rehearsed once, timed
- [ ] Repo on `main`: publish reviewed work when authorized; retain local hashed-freeze evidence
  and completed final-test lock (tag not mandatory under the amendment); all 62 tests and separate
  form checks passing; final outputs already under `tables/final_test/`
- [x] Model card (`docs/HANDOFF.md` §8) and README/HANDOFF updated with model results/deviations
- [ ] Add actual human-study results and limitations after collection; do not invent pending results
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
| W1.2 | Full deletion faithfulness audit | **Omitted** under the authorized amendment; implementation available, no completed empirical audit claimed | Disclose omission; not a launch prerequisite |
| W1.3 | Full multi-case seed/background/perturbation stability | **Omitted**; one-case/two-seed execution check completed, overlap 0.8, not general stability | Disclose omission; no stability-certification claim |
| W1.4 | Full constrained-recourse audit | **Omitted**; helper implementation is not evidence of feasible interventions | Disclose omission; no causal/recourse findings |
| W1.5 | Smoke result and limitation note | **Completed by Yolanda:** HANDOFF §8/§12 and protocol-deviation text | Reviewer checks note; Noey incorporates it into final report R3 without invented full-audit results |

Noey remains the suggested report editor (R1/R8); appointment is not verified.
ID W1.6 moved to W2.2. The original full audit remains optional via `--full-audit`.

### W2 Han — Study instrument: Google Forms (build and test) 

| ID | Current task | Status / evidence | Still needed |
|---|---|---|---|
| W2.1 | Four-form spec: consent, 18+, code, instructions, practice, ten scored cases, confidence and three written prompts | **Han's implementation integrated and verified by Yolanda;** authorized review/cohort wording completed by Yolanda in `docs/form_spec.md` | Resolve unchecked confirmations; verify built live wording |
| W2.2 | Public pack/private lookup contract | **Existing contract integrated and verified by Yolanda;** contract review and genuine pack format/provenance checks completed by Yolanda | Independent review; never upload the private lookup to Forms |
| W2.3 | Generator for A1/A2/B1/B2 | **Han's generator integrated and verified by Yolanda;** fail-closed safeguards and synthetic checks completed by Yolanda | Run real build W2.7; local tests are not live acceptance |
| W2.4 | Privacy/settings and restricted response Sheet | **Partial:** old-form autosave disabling completed by Yolanda | Sheet last observed institution-wide link-editable; restrict access and verify all settings, signed-out access and new-form autosave |
| W2.8 | Wide-to-long response transform with actual source variants | **Han's transform integrated and verified by Yolanda;** source-identity/duration safeguards and synthetic CSV checks completed by Yolanda | Review actual real-build exports; use exact canonical assignment |
| W2.5 | Live export/transform/cleanup check | **Pending live;** synthetic integration checks completed by Yolanda | Verify actual form submissions/exports transform correctly; delete pilot/test rows in Forms and Sheet |
| W2.6 | Seven live checks in HANDOFF §7 | **Pending/not passed.** Partial inspection completed by Yolanda, not a full pass | Check values, hidden outputs, A/B parity, assignment/order, privacy, wording and exports on real build; record reviewer results |
| W2.7 | Four real forms and individual prefilled links | **Ready to build, not built.** Dependencies W3.9 and local W5.8 generation complete | Use genuine pack/charts and canonical CSV; start closed, repeat manual autosave and parity checks. Never distribute links before acceptance/pilot |

### W3 Yolanda — Final evaluation, study cases and reproducibility

Current W3 execution status: **completed locally** under the authorized accelerated amendment.
The pinned Python 3.12 environment, 62 tests and separate form checks pass. The local snapshot,
single final evaluation, final tables/model card, real case pack and 11 charts are complete.
The full audit was stopped/replaced by the smoke check, not left running. No independent approval
is claimed. W3.8 verification and live W2 acceptance remain outstanding.
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
| W3.7 | *Optional:* sensitivity checks (Enrolled as third class or grouped). | [I] | Fri 13 Nov (drop if behind) | Labelled as sensitivity; not used for model selection. |
| W3.8 | **Independent clean-clone verification** by the W5 owner: run tests/fixture checks, verify validation reproduction as applicable and saved final hashes; transfer private assets separately if needed. | [D: W3.3, W3.5, W3.6] | Wed 18 Nov | Reviewer records checks and discrepancies; final evaluation is never repeated. |

### W4 Harry — Human-study operations and analysis

| ID | Current task | Status / evidence | Still needed / prerequisites |
|---|---|---|---|
| W4.1 | Consent, information sheet, withdrawal/access/retention arrangements | **Partial:** existing consent integrated and verified by Yolanda | Harry confirms applicable course requirements, actual deletion date and raw-access roles; restrict Drive/Sheet and verify live consent. Participants contact their recruiter with their code; the current consent omits a named contact/withdrawal deadline/retention date |
| W4.5 | Recruitment plan and counts; original window 13–17 Nov, one reminder after two days | **Pending/unverified** | Confirm schedule and ten recruits/member; no links until acceptance/pilot; target 50, minimum 40 with 18/group |
| W4.2 | Standard instructions, invitation/reminder/troubleshooting kit and debrief | **Partial:** existing instructions/debrief integrated and verified by Yolanda; cohort-policy clarification completed by Yolanda | Confirm remaining invitation/reminder/support messages and pilot-based duration; prerequisite W4.1 |
| W4.3 | Codebook: comprehension, actionability, missing information, `other/unclear`; paraphrased examples | **Pending/unverified** | Write/train before any group comparison; agree one-code-per-item convention used by tooling |
| W4.12 | Participant-number and replacement-rule parity across protocol/HANDOFF/proposal | **Partial:** current CSV allocation checks completed by Yolanda | Complete independent proposal DOCX/PDF parity check; no claim of completed three-document sign-off |
| W4.6 | One-person real-form pilot | **Pending** | After W2.7 and live/privacy checks; test code/link/row receipt/no answer leakage, duration and phone readability; log fixes, remove pilot rows from Forms/Sheet and study analysis |
| W4.7 | Individual links, code-only send/exclusion log, daily response checks and restricted backup | **Pending** | After W4.5/W4.6; log recruiter/date sent/submission/exclusion, no contact details beside codes; use canonical slots/spares and report achieved counts |
| W4.8 | Shared qualitative coding and 20% double-coding | **Pending** | W4.3/W5.9 plus incoming responses; all five code non-own recruits, blinded where practical; Harry trains/resolves disagreements; finish after W4.7, report raw agreement/themes |
| W4.11 | Real response transformation/scoring and descriptive analysis | **Pending** | W4.7 plus reviewed W2.8/W5.6; participant-level accuracy, confidence, self-reported time, counts and practice checks; no significance claims |
| W4.10 | Delete raw responses/link files everywhere at confirmed retention date | **Pending; not due merely because preparation is complete** | Complete R7 before the deletion deadline; if deadline is earlier, move review earlier. Delete Forms/Sheet/CSV/backups/Drive trash and record privately; retain aggregates only |

ID W4.9 moved to W5.8.

### W5 Lucas — Explanation images, assignment lists, demo card and scoring script (code-heavy)

| ID | Current task | Status / evidence | Still needed |
|---|---|---|---|
| W5.8 | Canonical seeded assignment: 50 main, 4 spares, 1 B1 pilot; private seed/rules/hash | **Assignment completed by Yolanda using Lucas's generator, integrated and verified by Yolanda:** generated once, exact reproduction/hash verified; 8 tests pass; local seal records owner authorization | Harry/Lucas acknowledge restricted handover, not a second generation or invented approval. Same CSV drives build, links and transform; no codes/seed in Git |
| W5.9 | Coding assignment/agreement tooling: non-recruiter primary, random 20% second coder, group omitted where practical | **Implementation and synthetic assignment/agreement checks completed by Yolanda** | Independent review and W4 codebook/training; real coding remains W4.8 |
| W5.3 | Renderer and 11 genuine Group B charts, shared pack scale and neutral legend | **Lucas's renderer integrated and verified by Yolanda; chart generation completed by Yolanda.** Text checks pass and one real chart visually inspected | Complete all-chart visual/live profile/order parity; no comprehensive visual acceptance claimed |
| W5.6 | Participant-level scoring, group summaries, confidence/time and practice-check reporting | **Implementation and synthetic scoring/exclusion/practice-check regressions completed by Yolanda** | Lucas independently reviews; real analysis awaits consented post-pilot data (W4.11) |
| W5.1 | Static demo card from a validation fixture for report/slides | **Pending/unverified** | Show profile, labelled estimated risk, contributions and limitations; no fabricated recourse or test-case answer leakage; review before publication |
| W5.5 | Full-audit deletion/stability figures | **Omitted** with W1.2/W1.3 | Do not invent plots/results; explain reduced evidence in report |

W5 also does **W3.8** (clean-clone verification) and builds the coding-assignment script **W5.9**; the coding itself is shared by all five (**W4.8**).
IDs W5.2, W5.4 and W5.7 are unused: those tasks moved to W3.9, dropped (D2) and W4.11.

## 5. Report and slides — everyone (shared track)

All R1–R9 final-report/deck tasks remain pending or unverified. Completed HANDOFF/model-card
source text is available for drafting; it does not prove that the shared final documents or
slides exist, have been reviewed or rehearsed.

**One appointed report editor** assembles the Word report and the slide deck. They do **not** write
everyone's text. Each workstream owner writes the section and slides for their own part, and each
section is cross-reviewed by a different workstream.

| Report section | Written by | Draft source |
|---|---|---|
| Introduction, data and EDA, limitations | W3 owner | HANDOFF §2–§4 |
| Predictive results and model comparison (final test), model card, reproducibility | W3 owner | W3.5, W3.6 |
| Explanation smoke check and omitted-audit limitations | W1 owner | Completed W1.5 note; no full-audit results; descriptive subgroup/proxy evidence is in final W3 tables |
| Study instrument (Google Forms), form screenshots, acceptance results, disclosed deviations | W2 owner | W2.6, HANDOFF §7 |
| Explanation images and validation-only demo; disclose omitted audit figures | W5 owner | Completed W5.3; pending W5.1; W5.5 omitted |
| Human study: methods, ethics, results, qualitative findings | W4 owner | W4.7, W4.8, W4.11 |
| Discussion and conclusion | **everyone**: each owner contributes 3 bullet points; the editor merges them | R3 |

| ID | Task | Depends | Deadline | Done when |
|---|---|---|---|---|
| R1 | Report and slide setup: outline, section and slide owners, shared Google Doc and Slides in the team Drive (drafts only, no raw data), template, and the **report editor appointed** (§10). | [I] | Fri 30 Oct | Outline and owner list shared; empty Doc and Slides exist. |
| R2 | **Methods drafts:** each owner writes what their part built and how (no results yet), matching HANDOFF. | [D: R1] | Fri 6 Nov | Every section has a methods draft; each owner's reviewer has read it. |
| R3 | **Pending results drafts** (all but human study): use completed model results/smoke note and disclose omitted audits/figures; each owner adds limitations and 3 discussion bullets. Public screenshots/demo use validation fixtures, not hidden study-case answers, until collection ends. | [D: W1.5 note review, W2.6, W3.6, W5.1, R2] | Mon 16 Nov | Drafts reviewed; every number matches saved evidence; omitted W5.5 is not a dependency. |
| R4 | **Cross-review:** each owner reads and comments on a different workstream's section (W1→W2, W2→W3, W3→W4, W4→W5, W5→W1), checking numbers against tables and claims against HANDOFF. | [D: R3] | Wed 18 Nov | Comments resolved by the writers; no claim beyond the evidence. |
| R5 | **Slides:** each owner makes 2–3 slides for their own part (W4's human-results slide is filled in at R6). One shared look, one message per slide. | [D: R1, R3] | Tue 17 Nov | Draft deck complete with placeholders only for human results. |
| R6 | **Human-study results section and slide** by the W4 owner (using the W4.11 analysis), including limitations and sample size. | [D: W4.8, W4.11, R4] | Thu 19 Nov (12:00) | Section and slide in the shared files; sample size, group counts, accuracy, self-reported time and themes match the analysis. |
| R7 | **Review of the human-results section:** the **W3 owner** (not the author) checks it against the analysis outputs: sample size and group counts, accuracy, self-reported time, themes, deviations disclosed, and that no significance or causal claim is made. | [D: R6] | Thu 19 Nov (15:00) | Comments resolved by the W4 owner before the merge. |
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
Fri 6 Nov           W2.6 acceptance ✔ · W3.2 dry-run ✔ · W4.12 numbers verified · W4.3 · W5.6 · W5.9 · R2 · 50 slots
Mon 9 Nov           W3.4 FREEZE + TAG   (needs W1.5 + W2.6 + W3.2 + W4.12)
Tue 10 Nov          W3.5 FINAL TEST (once)
Wed 11 Nov          W3.9 export 10 study cases · W5.5 audit figures · W5.1 demo card
Thu 12 Nov          W2.7 build real forms · W3.6 model card + final-test figures
Fri 13 Nov          W4.6 pilot (morning, online) ─> links sent (afternoon)  [each member sends own 10]
Fri 13-Tue 17 Nov   W4.7 responses come in  ·  W4.8 coding starts as they arrive
Mon 16 Nov          R3 results sections written by every owner
Tue 17 Nov          R5 slide drafts
Wed 18 Nov          W4.8 coding done (rolling since Fri 13) · W4.11 transform + analysis · W3.8 clean-clone check · R4 cross-review
After R7            W4.10 delete raw data on the confirmed retention date (not automatic on 19 Nov)
Thu 19 Nov          R6 human results (12:00) ─> R7 review (15:00) ─> R8 merge + PDF (17:00) ─> R9 final read + rehearsal
Fri 20 Nov          buffer / submission
```

The dated chain above is the **original plan**, not a record that the checkmarks passed.
The current chain is: completed evaluation/cases/charts/local assignment -> restricted handover
and real-form build -> privacy and all seven acceptance checks -> pilot -> individual links ->
responses/coding -> analysis/report/review/deletion. W1.2–W1.4 and W5.5 are omitted.

**Current blocking rules.** No participant link is sent until real W2.7, W2.4/W2.6 and W4.6 pass
and applicable operational/ethics arrangements are confirmed. The final evaluation is already
completed: preserve the lock, do not refit/repeat/tune or select another model after test access.

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
4. **Decision-support demonstration:** a static example card instead of a working screen (D5).
5. **Withdrawal and exclusions** are handled by hand through the participant code and W4's send log.
6. **Online instead of in person** (D3, changed 31 Oct because we lack the people and room time to supervise 50 sessions): participants are planned to answer unsupervised on their own devices; collection has not been completed. Report distractions, looking things up/help from others and uncorrected chart misunderstandings as potential limitations.
7. The optional narrative condition was dropped (D2), and think-aloud notes were dropped earlier.
8. **Accelerated explanation evidence:** full deletion, multi-case seed/background/perturbation
   stability and constrained-recourse audits were omitted. The one-case/two-seed smoke check
   establishes execution only; its overlap 0.8 is not a general stability estimate.
9. **Local hashed freeze and early final evaluation:** a copied/hash-bound code/data/checkpoint
   snapshot replaced mandatory committed/pushed-tag approval. Evaluation ran once before live
   acceptance and without independent approval. Record these deviations, not false gate passes.
10. **Interpretation:** survey accuracy is agreement with hidden model flags on a fixed balanced
    panel, not true dropout accuracy, general explanation-quality certification or deployment evidence.

## 9. Risks and what to do

| Risk | Early warning | Response |
|---|---|---|
| Form generator not ready by Fri 6 Nov | W2.3 slips past Wed 4 Nov | W2 escalates immediately; build the four forms by hand from the spec (copy-paste) as a fallback; the W5 owner helps |
| Fewer than 50 recruited | Fewer than 50 agreed on Fri 6 Nov | Everyone recruits more that week; the minimum is 40 with at least 18 per group |
| Online answers are rushed or careless | Very short self-reported times or near-empty written answers in the daily Sheet check (W4.7) | Use the documented exclusions; do not invent post-hoc time cutoffs. Report duration and response-quality limitations |
| Coding is too heavy in the same week as sessions and the report | Coding less than half done on Tue 17 Nov | Everyone codes about 9 h in total; code rationale and intervention fields first; the W4 owner reassigns the remainder |
| Test run reveals a problem | Odd numbers on Tue 10 Nov | Report honestly; **no tuning and no re-run**; document as a limitation |
| Retention date earlier than Thu 19 Nov, or later than submission | Found in W4.1 | Earlier: move the verification chain (R6, R7, W4.8) earlier. Later: keep the data in the restricted store until that date; never delete before R7 |
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
| W1 Explanation audit | Noey | suggested: W2 owner; acceptance not confirmed | Fri 30 Oct | Smoke/note completed by Yolanda; full audits omitted; independent review pending |
| W2 Study instrument: Google Forms | Han | suggested: W3 owner; acceptance not confirmed | Thu 29 Oct | Han's implementation integrated and verified by Yolanda; review/safeguards/checks completed by Yolanda; real build/privacy/live checks pending |
| W3 Final evaluation, study cases, reproducibility | Yolanda | suggested: W4 owner; approval not claimed | Wed 28 Oct | Local execution/model card/cases/charts complete; independent W3.8 remains |
| W4 Human-study operations and analysis | Harry | suggested: W5 owner; acceptance not confirmed | Fri 30 Oct | Existing consent/instructions integrated and verified by Yolanda; operational confirmations/pilot/recruitment/analysis pending |
| W5 Images, assignment lists, demo card, scoring script | Lucas | suggested: W1 owner; acceptance not confirmed | Mon 2 Nov | Lucas's generator/renderer integrated and verified by Yolanda; assignment/charts/scoring-coding implementation completed by Yolanda; handover/reviews/demo pending |
| **Report and slides editor** (assembles only; suggested: W1 owner) | Team to confirm | — | Fri 30 Oct (R1) | Appointment and report/slides completion not verified |

**Suggested reviewers** form a ring (each owner reviews the next workstream), so everyone reviews exactly
one other person's work (3 h, already counted in §7). Change it if a pair works poorly together.

**Open items only the team can fill in:** confirm reviewer assignments above and the report editor; the
real course deadline and any required deliverable beyond the report and deck (for example a presentation
date); the course retention deadline (task W4.1); each person's real availability on Fri 13 – Tue 17 Nov.

| Recruiter | Participants recruited (target 10 each) | Agreed by Fri 6 Nov |
|---|---|---|
| Member 1 | | |
| Member 2 | | |
| Member 3 | | |
| Member 4 | | |
| Member 5 | | |
| **Total (target 50)** | | |
