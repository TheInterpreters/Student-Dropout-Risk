# W2: Study instrument (Google Forms)

**Owner:** Han (W2). **Reviewer:** Yolanda (W3, suggested in TASK_SPLIT §10).
**Status (team-reported 4 Nov):** the real forms, privacy/consent checks, live acceptance/export
checks and pilot are complete. This page records that aggregate status but does not contain
check-by-check results or independently verify the live environment. Keep the team's acceptance
records with the study materials. The canonical assignment remains sealed; do not regenerate it.
Full explanation audits were omitted under the accelerated amendment, not passed, and are not a
remaining form-build prerequisite.
**Last updated:** 2026-11-04
**Review update:** 2026-11-02, Yolanda on behalf of the owners with their authorisation; contract-format review
and the decisions below only, not live-form acceptance or response-Sheet permission verification.
**Related:** `docs/form_spec.md` (W2.1, what the forms contain), `docs/case_pack_contract.md` (W2.2, case file format),
`forms/README.md` (how to build, run and dry-run), `docs/TASK_SPLIT.md` (W2 tasks, D3, D8, §8), `docs/HANDOFF.md` §6–§7.

This page records what W2 built, what was decided and why, so the report's study-instrument section (methods,
form screenshots, acceptance results, disclosed deviations) can be written from it. This file used to hold
Survey 1, a background questionnaire that was dropped on 28 Oct (§9).

Team: W1 Noey · W2 Han · W3 Yolanda · W4 Harry · W5 Lucas.

Status attribution: **Completed by Yolanda** identifies work she performed;
**integrated and verified by Yolanda** identifies her integration/checking of Han's existing
implementation, preserving original authorship. Neither label claims independent/live acceptance.
Remaining tasks are stated explicitly below.

---

## 1. W2 tasks and status

| Task | Original due | Current status (updated 4 Nov) |
|---|---|---|
| W2.1 Form spec | 29 Oct | Han's spec integrated and reviewed; team reports live consent/wording checks complete (4 Nov); unmarked content-confirmation items below are not per-check acceptance evidence |
| W2.2 Case-pack format | 29 Oct | Contract and genuine 11-case format/provenance checks completed; team reports real-form integration complete; detailed independent review is not recorded here |
| W2.3 Form generator | 4 Nov | Han's generator integrated and checked; team reports the real-form build complete (4 Nov) |
| W2.4 Privacy settings and response sheet | 4 Nov | Team reports privacy/access checks complete (4 Nov); earlier observations on draft forms/Sheet below are historical and do not describe the current build |
| W2.8 Response transform script | 4 Nov | Transform safeguards and synthetic checks completed; team reports live exports/transform acceptance complete (4 Nov); detailed export results are not recorded here |
| W2.5 Dry run | 5 Nov | Synthetic checks completed; team reports live export/transform checks complete (4 Nov) |
| W2.6 Acceptance checks | 6 Nov | Team reports live acceptance checks complete (4 Nov); individual check outcomes are not documented in this page |
| W2.7 Real forms | 12 Nov | Team reports four real forms built with the genuine pack/charts and canonical assignment (4 Nov); do not regenerate or replace the assignment |

## 2. How the forms work

**Four forms.** Group A sees the student profile only; Group B also sees a contribution chart. Each group uses
two case orders so position effects balance within the group.

| Form | Group | Each profile shows | Case order | Main links |
|---|---|---|---|---|
| Form 1 | A | Profile only | Seeded order | 13 |
| Form 2 | A | Profile only | Exact reverse of Form 1 | 12 |
| Form 3 | B | Profile + contribution chart | Seeded order | 12 |
| Form 4 | B | Profile + contribution chart | Exact reverse of Form 3 | 13 |

Counts reflect the W5 study assignment (13/12/12/13). The older W2 default fixture assignment
has 13/12/13/12; it remains test-only. Seal the W5 CSV privately and use it throughout the handoff.

**Page flow (19 sections, identical in all forms):** Welcome → Research information and consent → Age check (18+)
→ Participant code (pre-filled from the link) → Instructions → Practice profile (not scored) → Student profile
1 to 10 → Closing (role; minutes taken) → Finish (debrief; the form submits here) → Thank-you page (decline only).
"I do not agree" or "No" on the age check go straight to the Thank-you page. After Submit, everyone sees
"Thank you. You can close this page now."

**Each case (practice and the 10 scored):** Q1 "Do you think the model flagged this student?" (Yes/No);
Q2 "How sure are you?" (1 Not sure at all to 5 Very sure); Q3 "What made you think so?"; Q4 "If you were the
support officer, what would you say or suggest to this student?" (note: no names); Q5 "What else would you want
to know about this student?". All required. No answers or feedback are ever shown.

**Group B only:** the chart under every profile (bars right = model more worried, left = less worried, longer =
bigger effect; no numbers, score or final answer), the chart explanation in the instructions, and two practice
chart questions (P.B1 direction, P.B2 bar length) recorded as a manipulation check.

**Links and assignment:** a seeded list gives each slot a random code (W5: P plus four readable characters) and a form: 50 main slots (25 per
group), 4 spares (one per form) and 1 pilot link (`PILOT-01`, Form 3, not counted). The link pre-fills only the
code. Nobody chooses a group; Harry (W4) hands out the next unused link.

**Collection (online, from 31 Oct):** each participant opens their own link on their own device between
Fri 13 and Tue 17 Nov (closes 23:59). One reminder after two days. A spare replaces anyone who does not submit by
the deadline. Total time is self-reported in the last question.

## 3. Decisions and reasons

| Date | Decision | Reason |
|---|---|---|
| 27 Oct | Google Forms instead of a custom interface (D8) | Saves about 30–40 hours in a 3-week plan; study design unchanged |
| 28 Oct | Survey 1 dropped; the human study is the only instrument | No additional survey needed; only UCI data is used for the model |
| 30 Oct | **Four forms** (A/B × seeded order and its exact reverse) instead of six variants (A/B × three seeded orders) | Fewer forms to build, check and share; reversing still balances position effects within each group; agreed by the team |
| 30 Oct | Profiles decoded from UCI codes into plain words (`forms/labels.py`) | Participants cannot read codes; every code in the data has a label (test 11) |
| 30 Oct | Label fixes from team review: pass mark on grades, "units = course subjects", "evaluations = exams or assessments", plain admission routes, units on economy fields, parents' job "Student (as recorded)" | Most participants do not know the Portuguese system; jargon would distort guesses |
| 30 Oct | Economy fields shown as "National economy": unemployment rate (%), inflation rate (%), GDP growth (%) | Values match Portugal's national yearly figures (§4); the old "regional" label was wrong |
| 30 Oct | Grade 0 shown as "none (no units passed)" | In the data, 0 appears exactly for students who passed no units, so it is not a real score (§4) |
| 30 Oct | "Units credited" kept, with a clearer label | 0 in all test cases, but 13% of students have some; real cases may differ |
| 30 Oct | Consent text from W4; brackets and grammar fixed; no retention date, withdrawal deadline or named contact; questions go to "the person who sent you this form" | Team decision to keep the text flexible; everyone recruits their own participants |
| 30 Oct | Participant code page asks people to note the code | Withdrawal works only through the code |
| 30 Oct | Separate Finish page; decline routes to its own Thank-you page; neutral confirmation message | Finishers must never see "You chose not to take part"; Google shows one confirmation to everyone |
| 30 Oct | Decline text says answers "will not be used" (not "not saved") | Google still stores the consent answer if the person submits; the transform drops those rows |
| 30 Oct | Instructions replaced with W4's text (headings: What you will see, Your task, What each profile shows, For each case, Good to know) | Standard instruction text (W4.2) |
| 30 Oct | "There are no right or wrong answers" narrowed to "…to the three written questions"; dataset-origin sentence dropped | The yes/no guess does have a right answer; team asked to drop the country line |
| 30 Oct | 4 spare links (one per form) | Replacement rule in TASK_SPLIT §2 keeps groups and orders balanced |
| 31 Oct | 1 pilot link `PILOT-01` on Form 3 | The pilot is not one of the 50 and must not use a spare; Group B shows the most to check |
| 31 Oct | Sign-in switched off by the script | "No sign-in" rule (W2.4); AIT school accounts may restrict forms to signed-in users |
| 31 Oct | Case-pack format agreed in writing (W2.2): two files, top-5 contributions, chart file `chart_<case>.png`, IDs by ascending dataset row | The study export on 11 Nov must drop straight into the builder and the chart renderer; IDs must not reveal the flag |
| 31 Oct | **Study runs online and unsupervised** (D3) | Not enough people or room time to supervise 50 sessions; disclosed as a limitation (§8) |
| 31 Oct | Total time is self-reported ("About how many minutes…", number 1–300); consent says so | Nobody observes online sessions; Google records only the submission time |
| 31 Oct | Consent adds "If you close the page before pressing Submit, nothing is sent"; instructions ask for one sitting, alone, without looking anything up | Online participants need this said explicitly |
| 31 Oct | No "re-read the chart" page after a wrong practice answer | Google Forms routes on only one question per page, and the Back button would let people change their answers after seeing the explanation |
| 2 Nov | Yolanda's authorised review: record and report wrong practice chart answers without correction or automatic exclusion | Preserve the manipulation check; report correct counts and denominators per item and for both together |
| 2 Nov | State the at-most-top-20% full-cohort policy in both groups' instructions, explicitly distinguishing it from the selected sample | Clarify the operating policy without revealing the sample's actual flag mix; Han must rebuild the live forms |
| 2 Nov | Keep the current grade label pending stronger evidence | The official UCI definition does not specify that the average covers passed units only |
| 3 Nov | Time stated as "30–40 minutes" in the consent and the invitation | The pilot took about 40 minutes by the clock (35 self-reported) and felt a little long |
| 3 Nov | Note under the support officer question (Q4): "A short answer is fine; one suggestion is enough. Please do not type any names." | In the pilot, thinking of reasons from the officer's point of view felt long |
| 3 Nov | Cases not changed after the pilot | They were fixed after the one-time final test; changing them now would mean choosing cases after seeing results |

## 4. Evidence behind the label choices

- **GDP growth.** The 10 distinct (unemployment, inflation, GDP) combinations in the data match Portugal's yearly
  national figures; for example GDP −4.06 = 2012 and 3.51 = 2017 real GDP growth (World Bank, via StatisticsTimes),
  unemployment 7.6–16.2 and inflation −0.8–3.7. So GDP is annual growth in %, and unemployment is national.
- **Average grade.** The first-semester grade is 0 for exactly the 718 students who passed no units, and never
  otherwise; the lowest non-zero average is 9.8. This pattern alone does not establish that the average covers
  passed units only. The [official UCI definition](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success),
  checked on 2 Nov, says "Grade average in the 1st semester (between 0 and 20)" and does not resolve that question.
  Keep the current label pending stronger evidence.
- **Units credited.** Non-zero for 577 of 4,424 students (13%).
- **Codebook coverage.** Every code in all 4,424 rows has a plain label (test 11).

## 5. Build pipeline and tests

| File | What it does |
|---|---|
| `forms/build_spec.py` | Builds the case pack (fixture), the four form specs and the assignment list; `--case-pack/--private` for the real build |
| `forms/labels.py` | Plain labels for the profile card |
| `forms/case_pack.py` | Checks a case pack and its private file against the W2.2 format |
| `forms/render_forms.gs` | Apps Script: builds the four forms, settings, routes, chart images, links sheet |
| `forms/transform_responses.py` | W2.8: response export → long CSV (template columns) and a participant file |
| `forms/test_spec.py` | All checks; must print PASS |

**Tests (15 checks):** four variants; 30 profile fields, no second-semester fields or Target; test cases only from
the validation split; orders are the seeded order or its reverse; A/B identical except charts and chart questions;
profiles match the case pack; leak scan; assignment counts (50/4/1, 25 per group, 13/12 per form); rebuild is
identical; no form-version field; every code labelled; ending routes; case-pack format and bar names match `src/`;
a real case pack builds the same forms and a broken one is refused; the transform puts every answer under the
right case and drops declines, the pilot and bad codes.

**Never in git:** `forms/out/` (case packs, private lookup, participant codes, response files), Drive and form
links, responses. These live only in the restricted Drive folder.

## 6. Build log

- 29–30 Oct: first builder and Apps Script renderer; UCI codebook decoded from the official variable table; two
  test forms, then four.
- 30 Oct: consent and instruction text from W4; team review of labels, consent and ending; Finish page and
  routing fix; first clean run (no hand-routing needed).
- 30 Oct (night): TASK_SPLIT, HANDOFF and the protocol file updated for four forms; 4 spares added.
- 31 Oct 00:09: commit "Add form builder and update study instrumentation".
- 31 Oct: pilot link; `docs/form_spec.md` (W2.1); `docs/case_pack_contract.md` and the checker (W2.2), commit
  12:17; sign-in off, chart-image insertion and real-pack loading (W2.3); transform script (W2.8); switch to online
  across docs, consent, instructions and the time question; commit 14:48.
- 31 Oct 15:14: forms rebuilt, log clean. The links sheet lacked the pilot row because Drive still held an older
  assignment file; the pilot link was added by hand and the file re-uploaded.
- 3 Nov, about 00:20–01:10 Bangkok time (the response sheet shows UTC, 2 Nov 18:08): **pilot** (W4.6) on Form 3
  with `PILOT-01`, run by Harry. One adult outside the 50 and not a team member, alone, on their own Android phone.
  Result: all 62 questions answered; both practice chart checks correct; charts readable on the phone and rated well;
  no typos; 35 minutes self-reported, about 40 by the clock. The first 2–3 cases were slower while they learned
  the format (no wording problem). The real export matched the spec column for column and the transform dropped the
  pilot row. Local copies of the pilot response were deleted; the response itself goes with the old forms and response tab.
- 3 Nov: two wording changes from the pilot (time 30–40 minutes; Q4 note) made in the builder and patched into the
  real `form_spec.json` (only those texts; proof by diff; original kept as `form_spec_original_2nov.json`, hashes in
  `CHANGES_after_pilot.txt`). All four forms rebuilt with the same cases, charts and assignment.

## 7. Problems and fixes

- **"Invalid data updating form" when setting routes.** Google rejects a question where some answers have a route
  and others do not. Fix: unrouted answers get "continue to next section". Since then the routes are set
  automatically.
- **Links sheet error (`getRange`).** `SpreadsheetApp.create` returns a spreadsheet, not a sheet; fixed by taking
  its first sheet.
- **Stale file in Drive.** After "upload new version", check the file's last line before running
  (`55,PILOT-01,B1,B,pilot`).
- **Google Forms limits to note:** routing works on one question per page; participants can press Back and change
  earlier answers before submitting (no feedback is shown, so no answer can leak); per-case time cannot be recorded.

## 8. Deviations and limitations to state in the report

1. Google Forms instead of the custom interface in the proposal (D8).
2. Four forms with two fixed case orders per group (seeded and reversed) instead of a fresh random order per
   person; changed on 30 Oct from three seeded orders.
3. **Online and unsupervised** instead of in person (D3, 31 Oct): distractions, looking things up or help from
   others cannot be ruled out, and nobody could correct a misread chart on the practice case.
4. Total time is self-reported; per-case time is not recorded.
5. The consent text gives no withdrawal deadline, retention date or named contact (team decision for
   flexibility); W4 records the retention date privately.
6. Practice chart answers are recorded but not corrected.
7. Self-reported time runs short: the pilot reported 35 minutes for about 40 by the clock.
8. Some profiles make the flag easy to guess from the profile alone (for example many failed units or overdue fees),
   and in Group B the chart can make it easier still. Academic record and tuition status are strong signals for the
   model too, so both groups answer such cases correctly and any group difference can only show on harder cases.
   The study measures agreement with the model's hidden flag on a fixed, selected panel; the cases were not changed
   after the pilot.

## 9. Survey 1 (dropped, for the record)

Survey 1 was a 28-item background questionnaire (the 27 UCI first-semester columns plus enrollment year) drafted
on 27 Oct, to collect self-reported participant backgrounds aligned to the UCI columns. It was dropped on 28 Oct:
the study has no additional survey and the human study is the only instrument. The full draft is in git history
(`git log --follow docs/documentation/w2-documentation.md`).

## 10. Current status and remaining study work

- **Completed by Yolanda:** final evaluation, genuine case export, 11 charts
  and locally sealed canonical W5 assignment; the team reports private list/seed/hash handover
  acknowledged (4 Nov).
- The team reports the real forms, restricted response storage, privacy/consent checks, live
  acceptance/export checks and pilot complete (4 Nov). Keep their detailed records separately;
  no individual check outcome is inferred in this documentation.
- Preserve the canonical assignment and do not regenerate or replace it. Do not change the frozen
  scientific inputs. If an authorized rebuild is needed, follow the runbook and repeat applicable
  manual settings/checks.
- No new arbitrary time-based exclusions: retain the documented exclusion policy. Pilot duration
  can inform advertised time; changing questions or exclusions needs explicit approval and disclosure.
- Grade label "(passed units only)": not supported by the official definition; retain current wording pending evidence.
- Remaining work is participant recruitment, response collection, coding and analysis, plus the
  later retention/deletion actions. The unchecked items
  in `docs/form_spec.md` §8 are content-confirmation records, not evidence that the team-reported
  live acceptance gates failed.

## 11. Acceptance results (W2.6; aggregate status updated 4 Nov)

**Aggregate status (team-reported 4 Nov):** live acceptance checks are complete. Specific
outcomes, dates, reviewers and notes for the seven checks are not recorded in this document; the
cells are intentionally left blank rather than inferred. The 2 Nov observations were a
partial inspection of earlier forms/Sheet, not results for the current accepted build.

| # | Check | Result | Date | Reviewer | Notes |
|---|---|---|---|---|---|
| 1 | All four forms build; displayed values match the case pack | | | | |
| 2 | Group B sees nothing that reveals the output; no feedback anywhere | | | | |
| 3 | Groups see identical profiles and differ only in the explanation | | | | |
| 4 | Assignment and case order reproduce from the seeds | | | | |
| 5 | Privacy settings: no emails, no sign-in, summary hidden, sheet restricted | | | | |
| 6 | Form text matches the model card and the consent text | | | | |
| 7 | A dry-run export transforms into the right long CSV | | | | |

## 12. Draft wording for the report (methods; human results not yet collected)

> The study uses four Google Forms generated from one specification. The canonical seeded
> list allocates 50 main slots to Group A (profile only) or Group B (profile plus contribution chart),
> 25 per group, with approximately half of each group assigned the seeded case order and half its
> reverse. One unscored validation practice and ten scored test profiles have been exported, with
> genuine contributions for Group B. Participants will consent, confirm age 18+, guess the hidden
> model flag, rate confidence 1–5 and answer three written prompts per profile, without correctness
> feedback. Sessions are online and unsupervised, with self-reported total time. The team reports
> the real-form build, restricted response storage, live acceptance and pilot complete (4 Nov).
> No main human-study results are claimed yet; after collection, replace this status with verified achieved counts
> and procedures. Task accuracy measures agreement with model flags on this fixed balanced panel,
> not actual dropout outcomes or general explanation quality.

## 13. Change log

- 2026-11-03: Pilot recorded (§6); time wording 30–40 minutes and the Q4 note added; limitations 7–8 added (§8); forms rebuilt.
- 2026-11-04: status updated to record team-reported completion of the real forms, privacy/consent,
  live acceptance/export checks and pilot; individual acceptance outcomes remain undocumented here.
- 2026-11-02, evening: task-by-task completion and contribution-specific attribution recorded;
  final evaluation/real cases/charts and local assignment seal completed; real build/privacy/acceptance/
  pilot were then pending. Removed prospective-study wording that incorrectly sounded completed.
- 2026-11-02: Yolanda's authorised review recorded; practice-check reporting and cohort-policy instructions agreed;
  grade-label proposal checked against UCI and left unconfirmed. Live forms and Sheet permissions remain unchecked.
- 2026-11-02: Handover safeguards added: explicit response-tab variants, case-row/provenance checks, duration
  validation, fail-closed study rendering and canonical W5 assignment handoff. See HANDOFF section 12.
- 2026-10-27: Survey 1 drafted (now §9).
- 2026-10-28: Survey 1 dropped.
- 2026-10-31: File repurposed as the W2 record; sections 1–12 written.
