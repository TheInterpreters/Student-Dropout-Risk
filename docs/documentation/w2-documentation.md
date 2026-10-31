# W2: Study instrument (Google Forms)

**Owner:** Han (W2). **Reviewer:** Yolanda (W3, suggested in TASK_SPLIT §10).
**Status:** Test forms built and checked on 11 dummy validation cases. Real forms are built on Thu 12 Nov (W2.7).
**Last updated:** 2026-10-31
**Related:** `docs/form_spec.md` (W2.1, what the forms contain), `docs/case_pack_contract.md` (W2.2, case file format),
`forms/README.md` (how to build, run and dry-run), `docs/TASK_SPLIT.md` (W2 tasks, D3, D8, §8), `docs/HANDOFF.md` §6–§7.

This page records what W2 built, what was decided and why, so the report's study-instrument section (methods,
form screenshots, acceptance results, disclosed deviations) can be written from it. This file used to hold
Survey 1, a background questionnaire that was dropped on 28 Oct (§9).

Team: W1 Noey · W2 Han · W3 Yolanda · W4 Harry · W5 Lucas.

---

## 1. W2 tasks and status

| Task | Due | Status (31 Oct) |
|---|---|---|
| W2.1 Form spec | 29 Oct | Done: `docs/form_spec.md`. Waiting for OK from Harry (W4) and Lucas (W5) on its §8 |
| W2.2 Case-pack format | 29 Oct | Done: `docs/case_pack_contract.md` and the checker `forms/case_pack.py`. Waiting for OK from Noey, Yolanda and Lucas |
| W2.3 Form generator | 4 Nov | Done: four forms from one command. Chart-image insertion and real-pack loading are built; test charts arrive from Lucas (W5.3) |
| W2.4 Privacy settings and response sheet | 4 Nov | Settings are set by the script. Still to do: the real restricted response sheet (Harry and the reviewer only) |
| W2.8 Response transform script | 4 Nov | Done and tested on fake exports: `forms/transform_responses.py` |
| W2.5 Dry run | 5 Nov | To do (steps in `forms/README.md`) |
| W2.6 Acceptance checks | 6 Nov | To do; results go in §11. Gate condition (b) for the freeze |
| W2.7 Real forms | 12 Nov | Code ready (`--case-pack`); waits for the final test and the case export (W3.9) |

## 2. How the forms work

**Four forms.** Group A sees the student profile only; Group B also sees a contribution chart. Each group uses
two case orders so position effects balance within the group.

| Form | Group | Each profile shows | Case order | Main links |
|---|---|---|---|---|
| Form 1 | A | Profile only | Seeded order | 13 |
| Form 2 | A | Profile only | Exact reverse of Form 1 | 12 |
| Form 3 | B | Profile + contribution chart | Seeded order | 13 |
| Form 4 | B | Profile + contribution chart | Exact reverse of Form 3 | 12 |

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

**Links and assignment:** a seeded list gives each slot a random code (P-xxxx) and a form: 50 main slots (25 per
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

## 4. Evidence behind the label choices

- **GDP growth.** The 10 distinct (unemployment, inflation, GDP) combinations in the data match Portugal's yearly
  national figures; for example GDP −4.06 = 2012 and 3.51 = 2017 real GDP growth (World Bank, via StatisticsTimes),
  unemployment 7.6–16.2 and inflation −0.8–3.7. So GDP is annual growth in %, and unemployment is national.
- **Average grade.** The first-semester grade is 0 for exactly the 718 students who passed no units, and never
  otherwise; the lowest non-zero average is 9.8. This suggests the average covers passed units only (team to
  decide the label; §10).
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

## 9. Survey 1 (dropped, for the record)

Survey 1 was a 28-item background questionnaire (the 27 UCI first-semester columns plus enrollment year) drafted
on 27 Oct, to collect self-reported participant backgrounds aligned to the UCI columns. It was dropped on 28 Oct:
the study has no additional survey and the human study is the only instrument. The full draft is in git history
(`git log --follow docs/documentation/w2-documentation.md`).

## 10. Open items before the freeze (Mon 9 Nov)

- Final order and allocation seeds recorded, sealed list to Harry (with Lucas, W5.8, Mon 2 Nov).
- Real restricted response sheet (W2.4).
- Lucas's test charts inserted; dry run (W2.5); acceptance checks by Yolanda (W2.6).
- Team decisions: how to report wrong practice chart answers; whether very short times lead to exclusion;
  whether the instructions mention that only the top 20% are flagged (acceptance check 6); grade label
  "(passed units only)".
- OKs on `docs/form_spec.md` (Harry, Lucas) and `docs/case_pack_contract.md` (Noey, Yolanda, Lucas); Harry's OK on
  the two online consent changes.

## 11. Acceptance results (W2.6), to fill in

| # | Check | Result | Date | Reviewer | Notes |
|---|---|---|---|---|---|
| 1 | All four forms build; displayed values match the case pack | | | | |
| 2 | Group B sees nothing that reveals the output; no feedback anywhere | | | | |
| 3 | Groups see identical profiles and differ only in the explanation | | | | |
| 4 | Assignment and case order reproduce from the seeds | | | | |
| 5 | Privacy settings: no emails, no sign-in, summary hidden, sheet restricted | | | | |
| 6 | Form text matches the model card and the consent text | | | | |
| 7 | A dry-run export transforms into the right long CSV | | | | |

## 12. Draft wording for the report (methods)

> The study instrument was a set of four Google Forms generated from a single specification by a script, so that
> every form could be rebuilt identically. Participants were randomly assigned through a seeded list of pre-filled
> links to Group A (student profile only) or Group B (profile plus a contribution chart showing the direction and
> relative size of each feature's effect, with no numbers, score or prediction). Within each group, half of the
> participants saw the ten cases in a seeded order and half in the exact reverse order. After consent and an age
> check, participants completed one unscored practice case and ten scored cases; for each case they guessed whether
> the model had flagged the student, rated their confidence from 1 to 5 and answered three open questions. No
> feedback was given. The study was completed online and unsupervised on participants' own devices, and total time
> was self-reported. Responses were stored under a random participant code without names or email addresses.

## 13. Change log

- 2026-10-27: Survey 1 drafted (now §9).
- 2026-10-28: Survey 1 dropped.
- 2026-10-31: File repurposed as the W2 record; sections 1–12 written.
