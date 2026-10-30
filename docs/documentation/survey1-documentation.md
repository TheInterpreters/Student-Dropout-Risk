# Survey 1: Participant background form

**Status:** Dropped on 28 Oct 2026. Not part of the study; kept for the record.
**Last updated:** 2026-10-27
**Related:** `docs/HANDOFF.md` §6 (human-study protocol and consent) and §7 (Google Forms instrument); `docs/TASK_SPLIT.md` W2; proposal §3 and §6

---

## 1. Purpose

Survey 1 collects background answers from participants. These answers are the project's unstructured data (proposal §3). Answers are self-reported. They are not AIT student records.

The column names match the UCI dataset so the answers can be lined up with it later. The 28 items are the 27 UCI student columns in the first-semester window (no second-semester columns, no `Target`) plus `enrollment_year`.

## 2. Open decisions

- **How answers will be used.** Options: analysed on their own, compared with UCI, merged into the UCI table, or used to train the model. This must be decided before the consent text is final. Proposal §3 currently says responses will not enter the dropout model.
- **Target.** Not included. Deferred by the team.
- **Grade scale.** AIT grades and UCI first-semester grades (0–20) use different scales. The admission and previous-qualification grades (UCI range 95–190) have no documented scale. Confirm before any merge.
- **Economic indicators.** Not asked. They will be looked up from `enrollment_year` (PORDATA, Portugal). UCI covers enrollments from 2008/09 to 2018/19, so later enrollments may not match UCI's definitions.
- **Sample size.** TASK_SPLIT gives 25 (minimum 20). HANDOFF §6 and the protocol give 8–10 (minimum 4). Decide the target for survey 1.
- **Consent wording.** Needs team and instructor approval (see §7).

## 3. Relation to the other instrument

HANDOFF §7 describes a different Google Form: the human study, with 10 cases, yes/no predictions, confidence ratings and three free-text prompts. That is not Survey 1.

Both forms should use the same settings: no email collection, no sign-in, response editing off, summary charts hidden, and responses sent to one restricted Sheet.

## 4. Form structure

1. **Consent gate (required).** Choosing "No" ends the form.
2. **Participant code (required).** Assigned by the team. Random, with no names.
3. **Section A: Background.** Items 1–12.
4. **Section B: Personal and financial.** Items 13–21.
5. **Section C: First semester.** Items 22–28.
6. **Thank-you page.**

## 5. Questions

Protected attributes are marked as listed in the evaluation protocol (gender, nacionality, age_band, international, displaced, educational_special_needs). `age_band` is derived from `age_at_enrollment`, so it is not asked.

| # | Column name | Question shown to participant | Type | Optional | Notes |
|---|---|---|---|---|---|
| 1 | marital_status | What is your marital status? (e.g., single, married, divorced) | Text | No | |
| 2 | application_mode | How did you apply to your programme? (e.g., online, through an agency) | Text | No | |
| 3 | application_order | Which choice was this programme on your application? (1 = first choice) | Number | No | |
| 4 | course | What is the name of your programme? | Text | No | |
| 5 | daytime_evening_attendance | Do you attend classes in the daytime or evening? (e.g., daytime) | Text | No | |
| 6 | previous_qualification | What is your highest qualification before this programme? (e.g., bachelor's degree) | Text | No | |
| 7 | previous_qualification_grade | What was your grade in that qualification? (digits only) | Number | No | Grade scale unresolved |
| 8 | admission_grade | What was your admission grade? (digits only, as on your admission letter) | Number | No | Grade scale unresolved |
| 9 | mothers_qualification | What is your mother's highest qualification? (e.g., secondary school, don't know) | Text | No | |
| 10 | fathers_qualification | What is your father's highest qualification? (same examples) | Text | No | |
| 11 | mothers_occupation | What is your mother's job? (e.g., teacher, unemployed, don't know) | Text | No | |
| 12 | fathers_occupation | What is your father's job? (same examples) | Text | No | |
| 13 | nacionality | What is your nationality? | Text | Yes | Protected attribute |
| 14 | displaced | Are you a displaced person, meaning you were forced to move from your home area? | Yes/No | Yes | Protected attribute. Wording to confirm against the UCI data paper |
| 15 | educational_special_needs | Do you have any educational special needs? | Yes/No | Yes | Protected attribute |
| 16 | debtor | Do you currently owe money to the institution? | Yes/No | Yes | Financial |
| 17 | tuition_fees_up_to_date | Are your tuition fees paid up to date? | Yes/No | Yes | Financial |
| 18 | gender | What is your gender? (e.g., male, female) | Text | Yes | Protected attribute |
| 19 | scholarship_holder | Do you hold a scholarship? | Yes/No | Yes | Financial |
| 20 | age_at_enrollment | How old were you when you started this programme? (digits only) | Number | No | Source for `age_band` |
| 21 | international | Are you an international student? | Yes/No | Yes | Protected attribute |
| 22 | enrollment_year | What year did you start this programme? (e.g., 2025) | Number | No | Lookup key for economic indicators. Not a UCI column |
| 23 | curricular_units_1st_sem_credited | How many course units were credited (recognised from earlier study) in your first semester? (0 if none) | Number | No | |
| 24 | curricular_units_1st_sem_enrolled | How many course units did you enrol in during your first semester? | Number | No | |
| 25 | curricular_units_1st_sem_evaluations | How many assessments (exams, assignments, tests) did you take in your first semester? | Number | No | |
| 26 | curricular_units_1st_sem_approved | How many course units did you pass in your first semester? | Number | No | |
| 27 | curricular_units_1st_sem_grade | What was your average grade in your first semester? (as on your transcript) | Number | No | Grade scale unresolved |
| 28 | curricular_units_1st_sem_without_evaluations | How many course units did you enrol in but not get assessed? | Number | No | |

## 6. Answer rules

- **Numbers:** digits only (19, not "nineteen"). No commas or units.
- **Yes/No:** stored as 1 for yes and 0 for no.
- **Text categories:** stored as written first, then mapped to UCI codes with a codebook built from UCI data paper Appendix A. Code counts: marital status 6, application mode 18, course 17, previous qualification 17, parents' qualification 34, parents' occupation 46.
- **"Don't know":** kept as text and mapped later.
- **"Prefer not to say" or skipped:** left blank.
- **Gender:** UCI coding is 1 = male, 0 = female (EDA notebook).
- **Column names:** lowercase, apostrophes removed, `/`, `(`, `)` and `-` replaced, spaces changed to underscores (the `clean_col` rule in `eda_dropout.ipynb`).

## 7. Consent (summary)

The consent text must say:
- what the study is and who runs it;
- that answers are pseudonymous, not anonymous, because the team keeps a code-to-consent list so people can withdraw;
- how answers will be used (see §2);
- who can see them and where they are stored;
- how long they are kept and the deletion date [to confirm];
- how to withdraw (using the participant code) and until when;
- that answers are optional and that taking part has no effect on studies or grades;
- that only aggregate results and checked quotes will be published.

Consent gate checkboxes: "I am 18 or older," "I have read this information," and "I agree to take part." The full text should follow the consent template in HANDOFF §6.

## 8. Data handling

- No names, AIT IDs or emails are collected.
- Raw responses and the code-to-consent list stay out of version control (HANDOFF §7).
- The code-to-consent list is stored separately from the answers and deleted on [date].
- Only summary numbers and checked quotes go into the report.

## 9. Checks before launch

- Dry run with one or two people outside the team. Time it.
- Confirm the 28 column names match the notebook's cleaned names.
- Confirm the consent text matches the decision in §2.
- Confirm the form settings match §3.

## 10. Change log

- 2026-10-27: First draft of the question set and form structure.
- 2026-10-28: Dropped. The study has no additional survey; the human study is the only instrument.
