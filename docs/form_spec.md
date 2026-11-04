# Study form spec (W2.1)

Generated on 31 Oct 2026 from `forms/out/form_spec.json` (test build on dummy validation cases). The builder (`forms/build_spec.py`) is the source of truth: if this page and the forms ever differ, the builder wins. For agreement by **W2 (Han)**, **W4 (Harry)** and **W5 (Lucas)**. The questions in section 8 need an answer.

Review update, 2 Nov 2026: Yolanda reviewed on behalf of the other owners with their authorisation.
W2.1/W2.2 review was completed and Han's implementation integrated and checked. That earlier
review did not certify live Google Forms settings or response-Sheet permissions.

**Current status (team-reported 4 Nov):** the real forms, privacy/consent checks, live
acceptance/export checks and pilot are reported complete. This status summary does not provide
individual check results; retain the team's acceptance records with the study materials. The
canonical W5 assignment remains sealed; do not regenerate it. The build instructions below are
specification/runbook material, not a claim that the real build is still pending. Full explanation
audits were omitted under the accelerated amendment, not passed and not required to proceed with
the human study.

## 1. Four forms

| Form | Group | Each profile shows | Case order (by case ID) | Main slots |
|---|---|---|---|---|
| Form 1 | A | Profile only | C03 C07 C01 C02 C06 C05 C04 C10 C09 C08 | 13 |
| Form 2 | A | Profile only | C08 C09 C10 C04 C05 C06 C02 C01 C07 C03 | 12 |
| Form 3 | B | Profile + contribution chart | C03 C07 C01 C02 C06 C05 C04 C10 C09 C08 | 12 |
| Form 4 | B | Profile + contribution chart | C08 C09 C10 C04 C05 C06 C02 C01 C07 C03 | 13 |

- Forms 2 and 4 use the exact reverse of the seeded order in Forms 1 and 3. The practice case (`PR`) always comes first and is not scored.
- Counts above use the W5 block-randomised assignment, the study handoff implementation. The W2
  builder's default fixture assignment instead has B1/B2 counts 13/12; do not use that default for real links.
- Case-order seed 11 is the existing frozen builder value; record/review its resulting order in
  real-build acceptance, without modifying frozen code/config. The separate W5 allocation seed is
  privately recorded with the canonical CSV/hash and local seal; 2026 is fixture allocation only.
  Study case IDs and frozen case order stay the same. No independent live-order sign-off is claimed.

## 2. Page flow (same in all four forms)

1. **Welcome** — Short welcome; read the consent on the next page.
2. **Research information and consent** — W4.1 consent text, then "I have read the information above and I agree to take part." I agree / I do not agree. "I do not agree" goes to the Thank-you page.
3. **Age check** — "I confirm that I am 18 years or older." Yes / No. "No" goes to the Thank-you page.
4. **Participant code** — Pre-filled from the participant's link. "This code is already filled in from your link. Do not change it. Please note it down in case you want to withdraw later."
5. **Instructions** — W4.2 text under the headings: What you will see; Your task; How students are flagged; What each profile shows; For each case; Good to know. Both groups are told: "For outreach, the model flags at most the top 20% of students ranked by estimated risk in a full cohort. The 10 scored profiles are a selected sample, not a representative cohort: do not assume that 20% of these profiles are flagged." Ends with "When you are ready, continue to the practice case."
6. **Practice profile (not scored)** — Profile + the 5 questions. Group B also sees the chart and 2 chart questions (section 3).
7. **Student profile 1 of 10 ... 10 of 10** — One page per case: profile (+ chart in Group B) + the 5 questions.
8. **Closing** — "Which best describes you?" Student / Staff or adviser / Other. Then "About how many minutes did the whole activity take you?" (a number from 1 to 300; self-reported, because the study is online).
9. **Finish** — "Please press Submit below to send your answers. They are not sent until you do." then the debrief. The form submits here, so finishers never see the decline page.
10. **Thank you (decline only)** — "Thank you. You chose not to take part, so your answers will not be used. You can close this page now."

After Submit, Google shows everyone: "Thank you. You can close this page now."

## 3. Questions

Asked on the practice case and on each of the 10 cases (all required):

| # | Wording | Answer |
|---|---|---|
| Q1 | Do you think the model flagged this student? | Choose one: Yes / No |
| Q2 | How sure are you? | Scale 1 (Not sure at all) to 5 (Very sure) |
| Q3 | What made you think so? | Long text |
| Q4 | If you were the support officer, what would you say or suggest to this student? | Long text (note under it: "A short answer is fine; one suggestion is enough. Please do not type any names.") |
| Q5 | What else would you want to know about this student? | Long text |

Group B practice case only (checks the chart was read correctly; not scored as a case):

| # | Wording | Answer |
|---|---|---|
| P.B1 | In the chart, a bar pointing right means the model became: | Choose one: More worried about this student / Less worried about this student / No change / Cannot tell |
| P.B2 | In the chart, a longer bar means: | Choose one: A bigger effect / A smaller effect / The student is more likely to drop out / Cannot tell |

## 4. Profile card (identical in both groups)

- **Background:** Age when starting, Gender, Nationality, International student, Marital status, Displaced, Special educational needs, Previous qualification, Previous qualification grade
- **Application:** Admission route, Application choice, Course, Attendance, Admission grade
- **Family:** Mother's education, Father's education, Mother's job, Father's job
- **Finances:** Scholarship, Tuition fees paid up to date, Owes money to the university
- **First-semester results:** Units enrolled (course subjects), Units credited from earlier studies, Evaluations taken (exams or assessments), Units passed, Units with no evaluation, Average grade
- **National economy:** Unemployment rate (%), Inflation rate (%), GDP growth (%)

Codes are shown as plain words from the UCI codebook (`forms/labels.py`). The model's output is never shown.

## 5. Group A vs Group B

- Everything above is identical, except that Group B also gets: a contribution chart under every profile (W5.3 image; bars right = more worried, left = less worried, longer = bigger effect, no numbers or answer), the chart explanation in the instructions, and the 2 practice chart questions.
- Group A's instructions say each profile shows "the student's recorded information only".

## 6. Settings (set by `forms/render_forms.gs`)

- No quiz mode; no correct answers or feedback shown anywhere.
- No email collection; response editing off; summary charts hidden; no "submit another response" link.
- Disable autosave for all respondents in Settings > Presentation after every build; confirm
  "Saving disabled" on all four respondent pages before collecting any answers.
- No sign-in: check that "Restrict to users in AIT" is off (W2.4).
- Closed to responses until the pilot; open only for tests and the study window (Fri 13 – Tue 17 Nov). Participants answer online on their own device (D3).
- Responses go to one restricted Sheet shared only with the W4 owner and the W2 reviewer.

## 7. Links and assignment

- 50 main slots (25 per group; 13 or 12 per form), 4 spares (one per form) and 1 pilot link (Form 3, code `PILOT-01`, not counted; its row is deleted after the pilot).
- Each link pre-fills only the participant code. Recruiters never choose a group: W4 hands out the next link from the sealed list.
- A study build requires `--assignment` with the sealed W5 CSV. Use that same CSV for rendering
  and response transformation. Each response export must also be labelled with its **actual source
  form** using `--variants A1 A2 B1 B2`, not inferred from participant codes. Mismatched codes are
  dropped and reported even when the two forms belong to the same group.
- Replacement: if someone does not complete, log it; the next recruit gets the spare for the same form (TASK_SPLIT section 2).

## 8. Please confirm (W4 and W5)

The unchecked items below are confirmation fields not resolved in this document. Their status
does not override the team's 4 Nov report that live form/privacy/acceptance gates and the pilot
are complete; retain any associated live-check results separately.

- [ ] The role question stays at the end (section 2, step 8).
- [ ] Q3 to Q5 (written answers) are required.
- [x] Yolanda, on behalf of the owners (2 Nov): record and report wrong practice chart answers, without correction or automatic exclusion. The participant export retains both answers and `chart_check_ok`; report the number of Group B participants who answered each item correctly and both correctly, with denominators.
- [ ] Participants are not told how many of the 10 students are flagged.
- [x] Yolanda, on behalf of the owners (2 Nov): state the top-20% full-cohort policy in both groups' instructions, explicitly distinguishing it from the selected 10-case sample. Do not disclose the sample's actual flag mix. Check the rebuilt live forms in acceptance check 6.
- [ ] Keep "Average grade" unchanged pending stronger evidence for "(passed units only)". The [official UCI definition](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success), checked on 2 Nov, says "Grade average in the 1st semester (between 0 and 20)"; it does not specify passed units only. The observed data pattern alone does not establish that definition.
- [x] Yolanda, on behalf of W5 (2 Nov): approve the naming contract `chart_<case ID>.png` (e.g. `chart_C07.png`), 11 in total, using W2.2. This approves the format, not delivery or visual acceptance of the charts.

The two online consent changes (self-reported duration and closing before Submit) were reviewed in
the builder. A 2 Nov inspection found Google draft saving enabled; it was disabled on the then-
existing forms and "Saving disabled" was seen on their respondent pages. The team reports the
subsequent real-form privacy and acceptance checks complete on 4 Nov. This historical inspection
is not a record of each later acceptance result; refer to the team's live acceptance evidence.
If forms are rebuilt, repeat the applicable manual settings and checks.

## 9. Implementation safeguards and handover (2 Nov)

- Study rendering preflights every chart before creating forms. Routing/login-setting failures raise
  errors rather than falling back to an apparently working form. Forms start closed and are opened
  only after rendering and link generation succeed, if explicitly configured.
- The export transform requires actual source-form identities and finite durations in 1-300 minutes.
- The case-pack checker verifies unique dataset rows, ascending scored row IDs, validation-only
  practice, test-only scored study cases, and exact profile/source-row parity. These checks do not
  prove that supplied SHAP values were computed correctly; the export runner and reviewer must do that.
- Follow `forms/README.md` for commands and `docs/HANDOFF.md` section 12 for workstream handover.
  This code/document review did not independently repeat the live acceptance checks.
