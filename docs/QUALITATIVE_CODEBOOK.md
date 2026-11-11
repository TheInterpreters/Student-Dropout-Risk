# Human-study qualitative codebook

Use this codebook for the three free-text answers. It is a light descriptive analysis, not an
automated sentiment analysis. Each answer receives exactly one **primary** code for its field so
that the planned raw exact agreement is interpretable. If several themes occur, choose the theme
that occupies the most substantive part of the answer; use the stated tie-breaking rule.

Coders work from their private blinded worksheet. Do not add names, group labels or recruiter
identity. Use `unclear_other` only after checking the field-specific codes.

## Why did the participant think the model made that decision?

Field: `rationale_freetext`

| Code | Apply when the primary rationale is |
| --- | --- |
| `academic_evidence` | grades, approved/enrolled units, examinations, participation or academic progress |
| `financial_or_admin` | tuition status, debt, scholarship or another administrative/financial status |
| `personal_or_demographic` | age, gender, family, marital or other personal/demographic information |
| `course_or_application` | course, application mode/order or previous qualification |
| `explanation_chart` | explicitly the chart, bar direction/length or highlighted model contribution |
| `multiple_or_holistic` | several categories are deliberately combined without one clearly primary |
| `unclear_other` | no interpretable rationale, or a rationale outside the categories |

Tie-break: use `explanation_chart` only when the participant explicitly relies on the chart itself;
otherwise code the underlying feature. Use `multiple_or_holistic` when two or more categories have
similar emphasis.

Clarifications applied during coding (11 Nov):
- Any explicit reference to the chart, a bar, its direction or its length used as a reason is
  `explanation_chart`, even when features are also named. Group A never saw charts, so this code
  cannot occur there.
- An academic conclusion with other features mentioned only as caveats ("despite the debt") is
  `academic_evidence`; two or more categories offered as joint reasons is `multiple_or_holistic`.

## What support would the participant suggest?

Field: `intervention_freetext`

| Code | Apply when the primary suggestion is |
| --- | --- |
| `academic_support` | tutoring, study planning, teaching support or academic-skills help |
| `financial_or_admin_support` | financial aid, payment plan, scholarship or administrative correction/referral |
| `advising_or_monitoring` | adviser meeting, progress monitoring, check-in or general academic counselling |
| `wellbeing_or_social_support` | mental-health, wellbeing, family, peer or social support |
| `verify_or_gather_information` | first check the record, ask the student or investigate the barrier |
| `no_action_or_punitive` | no support, punishment, blame or exclusion is the primary response |
| `unclear_other` | suggestion is unclear or outside the categories |

Tie-break: prefer a specific support service over general advising. Code `verify_or_gather_information`
only when investigation is the main proposed action rather than a preface to a specific service.

Clarifications applied during coding (11 Nov):
- Fees plus academic help in one answer: `financial_or_admin_support` (the fee step is usually the
  first and most specific). A lighter unit load, resits or catch-up plans count as `academic_support`.
- Praise only, "keep it up", enrichment for strong students (internships, mentoring others), or
  support offered only "if the student asks" are `no_action_or_punitive`: no support action is proposed.
  Suggesting the student drop out is also coded here.
- Motivational phrases with no action ("don't give up", "study hard") are `unclear_other`.
- "Same as previous answer" is coded as the answer it refers to.

**Intervention ratings (proposal section 5.7).** Each intervention answer is also rated on four items,
stored privately in `intervention_flags_study.csv` (`participant_id,case_id,...`):

| Column | Value |
| --- | --- |
| `concrete_next_step` | 1 if a specific action is named (a meeting, tutoring, payment plan, call); 0 for general advice |
| `feasible_before_second_semester` | 1 if it could plausibly start before the next semester's results; 0 otherwise or if no action |
| `responsible_actor` | `student`, `institution`, `both` or `none` (who must act) |
| `unsupported_causal_assumption` | 1 if the answer asserts a cause the profile does not show (for example "debt pushes students out", "this course does not fit him") |

These ratings describe the written suggestion only; they do not judge whether it would work.

## What additional information would the participant want?

Field: `missing_info_freetext`

| Code | Apply when the primary requested information concerns |
| --- | --- |
| `academic_engagement` | attendance, study habits, assessments, progress or academic engagement |
| `financial_or_admin` | finances, debt, tuition, scholarship or administrative status |
| `personal_wellbeing` | motivation, health, wellbeing, family, work or personal circumstances |
| `course_or_institution` | course context, teaching, institution, facilities or program requirements |
| `support_history` | prior contact, services, interventions or help already offered |
| `nothing_else` | explicitly no additional information is needed |
| `unclear_other` | request is unclear or outside the categories |

Tie-break: code the first clearly requested information type when several are listed with no stated
priority; record the tie during reconciliation if the second coder chose differently.

Clarifications applied during coding (11 Nov): work, family, housing, living away from home and career
plans are `personal_wellbeing`; attendance, still enrolled, which unit failed and why are
`academic_engagement`; course choice, transfer, prerequisites and scholarship rules about the programme
are `course_or_institution` unless the question is about paying (`financial_or_admin`). A blank ("-")
or a generic "any difficulties?" is `unclear_other`. 15 of 500 answers were blank.

## Workflow

1. Privately create the recruiter mapping required by `assign_human_coding.py`; member IDs must be
   pseudonyms such as M1–M5. A coder cannot code their own recruit.
2. Generate primary assignments plus a seeded 20% double-coded subset.
3. Train all coders on the same small practice set and discuss only code definitions, not study-group
   comparisons.
4. Code independently. Do not change a code after learning the other coder's decision.
5. Run the agreement command on completed worksheets; report raw exact agreement by field.
6. Run `reconcile`. Single-coded items take the primary code; matching double codes are accepted.
   Any disagreement stops the run and writes `disagreements_study.csv`; the W4 lead fills
   `resolved_code` for each row and reruns with `--decisions`. The output has one row per
   participant/case/field and a `source` column (`single`, `agreed`, `adjudicated`).
7. Run `summary` with `--responses` and `--private`. It writes overall theme counts plus
   `theme_by_group_study.csv` (Group A vs B, all cases and split by hidden model flag). The group is
   joined here, after coding, so coders never see it. Only these aggregate files go into the report
   (`python scripts/build_report_assets.py` copies them). Never commit worksheets or text.

Agreement describes consistency of this primary-theme codebook. It does not validate the truth,
quality or causal appropriateness of participants' explanations or suggested interventions.

Commands after the private `send_log.csv` (`participant_code,recruiter`) is available:

```powershell
python scripts/assign_human_coding.py assign data/human_study/analysis/responses_long_study.csv `
  --send-log data/human_study/send_log.csv --members M1 M2 M3 M4 M5 --label study

python scripts/assign_human_coding.py agreement `
  --assignments data/human_study/coding/assignments_study.csv `
  --coded data/human_study/coding/completed_study.csv --label study

# Combine every coder's completed worksheet (keep all columns) into completed_study.csv first.
python scripts/assign_human_coding.py reconcile `
  --assignments data/human_study/coding/assignments_study.csv `
  --coded data/human_study/coding/completed_study.csv --label study
# Exit code 2 = disagreements to resolve. Fill resolved_code, then:
python scripts/assign_human_coding.py reconcile `
  --assignments data/human_study/coding/assignments_study.csv `
  --coded data/human_study/coding/completed_study.csv `
  --decisions data/human_study/coding/disagreements_study.csv --label study

python scripts/assign_human_coding.py summary `
  --coded data/human_study/coding/reconciled_study.csv `
  --responses data/human_study/analysis/responses_long_study.csv `
  --private data/human_study/scoring_private/private_lookup_study.json --label study

python scripts/build_report_assets.py
python scripts/verify_release_readiness.py
```

**What was actually done (11 Nov).** All 1,500 answers were coded in one pass with this codebook,
with all three fields of a participant coded together, and every intervention answer was given the
four ratings above. The team's planned independent second coding of 20% of participants was not done,
so inter-coder agreement was **not measured**. The coded file is `reconciled_study.csv` with
`source = single_pass`. Summary command used:

```powershell
python scripts/assign_human_coding.py summary `
  --coded data/human_study/coding/reconciled_study.csv `
  --responses data/human_study/analysis/responses_long_study.csv `
  --private data/human_study/scoring_private/private_lookup_study.json `
  --flags data/human_study/coding/intervention_flags_study.csv --label study
```

If a second coder later codes the 20% subset in `assignments_study.csv` blind to these codes, run
`agreement`; `build_report_assets.py` then copies `agreement_study.csv` and reports agreement as measured.

Planned workload (not used): 50 participants × 10 cases × 3 fields = 1,500 primary items plus 300 second-coder items,
about 360 items per member.
