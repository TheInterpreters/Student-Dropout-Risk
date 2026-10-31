# Study form spec (W2.1)

Generated on 31 Oct 2026 from `forms/out/form_spec.json` (test build on dummy validation cases). The builder (`forms/build_spec.py`) is the source of truth: if this page and the forms ever differ, the builder wins. For agreement by **W2 (Han)**, **W4 (Harry)** and **W5 (Lucas)**. The questions in section 8 need an answer.

## 1. Four forms

| Form | Group | Each profile shows | Case order (by case ID) | Main slots |
|---|---|---|---|---|
| Form 1 | A | Profile only | C03 C07 C01 C02 C06 C05 C04 C10 C09 C08 | 13 |
| Form 2 | A | Profile only | C08 C09 C10 C04 C05 C06 C02 C01 C07 C03 | 12 |
| Form 3 | B | Profile + contribution chart | C03 C07 C01 C02 C06 C05 C04 C10 C09 C08 | 13 |
| Form 4 | B | Profile + contribution chart | C08 C09 C10 C04 C05 C06 C02 C01 C07 C03 | 12 |

- Forms 2 and 4 use the exact reverse of the seeded order in Forms 1 and 3. The practice case (`PR`) always comes first and is not scored.
- Order seed 11 and allocation seed 2026 are to be recorded as final (W5.8). The real study cases replace the dummy ones after the final test (W2.7); the case IDs and order stay the same.

## 2. Page flow (same in all four forms)

1. **Welcome** — Short welcome; read the consent on the next page.
2. **Research information and consent** — W4.1 consent text, then "I have read the information above and I agree to take part." I agree / I do not agree. "I do not agree" goes to the Thank-you page.
3. **Age check** — "I confirm that I am 18 years or older." Yes / No. "No" goes to the Thank-you page.
4. **Participant code** — Pre-filled from the participant's link. "This code is already filled in from your link. Do not change it. Please note it down in case you want to withdraw later."
5. **Instructions** — W4.2 text under the headings: What you will see; Your task; What each profile shows; For each case; Good to know. Ends with "When you are ready, continue to the practice case."
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
| Q4 | If you were the support officer, what would you say or suggest to this student? | Long text (note under it: "Please do not type any names.") |
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
- No sign-in: check that "Restrict to users in AIT" is off (W2.4).
- Closed to responses until the pilot; open only for tests and the study window (Fri 13 – Tue 17 Nov). Participants answer online on their own device (D3).
- Responses go to one restricted Sheet shared only with the W4 owner and the W2 reviewer.

## 7. Links and assignment

- 50 main slots (25 per group; 13 or 12 per form), 4 spares (one per form) and 1 pilot link (Form 3, code `PILOT-01`, not counted; its row is deleted after the pilot).
- Each link pre-fills only the participant code. Recruiters never choose a group: W4 hands out the next link from the sealed list.
- Replacement: if someone does not complete, log it; the next recruit gets the spare for the same form (TASK_SPLIT section 2).

## 8. Please confirm (W4 and W5)

- [ ] The role question stays at the end (section 2, step 8).
- [ ] Q3 to Q5 (written answers) are required.
- [ ] Online there is no runner: a wrong practice chart answer is recorded but not corrected. How should wrong answers be reported?
- [ ] Participants are not told how many of the 10 students are flagged.
- [ ] Should the instructions say that the model flags only a limited share of students (the top 20%)? The old line about this was dropped; acceptance check 6 compares the form with the model card.
- [ ] Should "Average grade" read "Average grade (passed units only)"? In the data, the average is 0 exactly when no units were passed, and the lowest non-zero average is 9.8.
- [ ] W5: chart images are named `chart_<case ID>.png` (e.g. `chart_C07.png`), 11 in total, and depend on the case-pack format (W2.2).
