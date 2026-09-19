# Human-Study Instrument — XDS Student Dropout

**This is the project's primary unstructured-data component.** The free-text written
responses collected here are linked to UCI case IDs and to the model's explanation —
which is what makes them usable as evidence about comprehension and actionability.

Participants will be recruited voluntarily from the Asian Institute of Technology (AIT)
community. They will assess pseudonymised cases from the UCI dataset; no AIT student
records, names, AIT student IDs, or administrative data will be collected. Unless a
participant is a student-support professional, the participant is a proxy for the
intended user. The study therefore evaluates explanation comprehensibility, not model
validity or operational effectiveness at AIT.

**Covered rubric criterion:** 5. Human evidence (15 marks) — *explanation vs no
explanation, forward simulation.*

---

## 1. Design (matches the rubric)

- **Participants:** a voluntary AIT convenience sample, targeting 8–10 if feasible (the
  rubric minimum is 4–5; two reasonably sized groups are clearer). Classmates are
  acceptable; participants with education or advising experience are preferable but not
  required. Record sample size and participant role category; do NOT collect names or
  student IDs and do NOT claim statistical significance.
- **Two groups, same 10 cases, randomized order:**
  - **Group A (control):** sees the **student profile only**. No prediction, no
    explanation.
  - **Group B (explanation):** sees the **student profile + feature-contribution
    explanation** (e.g. SHAP values / top features), but **NOT the model's final class
    or probability**.
- **CRITICAL — never show the model's output before the participant answers.** Neither
  group sees the prediction, class, or probability. If they did, forward simulation is
  impossible: they'd be asked to predict an answer they can already see.
- **Task (forward simulation):** each participant answers, per case, *"What do you think
  the model predicts — will it flag this student as at-risk: yes/no?"*
- **Reveal nothing** until the participant completes all 10 cases.
- **Practice:** before the scored cases, give both groups the same standardised task
  instructions and one unscored practice profile. Group B also receives a neutral
  contribution-direction legend and comprehension check. The practice case is not one
  of the 10 study cases and contains no feedback about the scored cases.
- **Measure:** each participant's accuracy across 10 cases is the primary analysis unit;
  compare group means descriptively. Also report per-case confidence, time and written
  reasoning. Never treat the approximately 100 case responses as independent people.
- **Assignment:** assign participants to A/B with a reproducible shuffled list using a
  recorded seed before they see any case. Do not let participants choose their group.
- **Case selection:** after the one-time test prediction run, choose five flagged and
  five unflagged cases deterministically across each output group's risk range without
  outcome labels. Never select cases because their explanations look persuasive.
- **Exclusions:** exclude only participants who withdraw consent, do not complete the
  task, or were accidentally shown the hidden output. Record every exclusion and reason;
  do not exclude someone because their answers reduce the treatment effect.
- **Timing:** start the timer when a case is displayed and stop it on submission. Use
  the same mechanism for both groups and store integer seconds.

### Participant consent text

> You are invited to take part in a short class research activity about understanding an
> AI model. Participation is voluntary. You may stop at any time without penalty. Do not
> enter your name or other identifying information in free-text answers. Your responses
> will be stored under a random participant ID and reported only in aggregate or as
> paraphrased comments. By selecting “I agree,” you confirm that you understand this
> information and consent to participate.

Participation or refusal must have no effect on course standing, grades, employment, or
access to services. Before recruitment, confirm with the course instructor whether AIT
approval is required and obtain it where applicable. Do not use the responses beyond the
course project without appropriate approval.

Record `consent = yes/no`. A participant who selects “no” must not proceed.

## 2. Per-case response form (the unstructured data)

For **each** of the 10 cases, capture — keyed by a pseudonymous `case_id` (such as C01;
a private lookup holds the UCI source-row ID). The
participant never sees the model's actual output; `correct` is scored afterward by the
researcher, not shown to them.

| Field | Type | Purpose |
|---|---|---|
| `case_id` | string | stable pseudonymous ID (e.g. C01); a private lookup links it to the UCI test row |
| `participant_id` | string | anonymized (P1…P10) |
| `group` | A / B | A = control (profile only); B = explanation (profile + explanation) |
| `case_order` | integer | position in that participant's randomized sequence |
| `predicted_output` | at-risk / not-at-risk | the participant's guess at the MODEL's output |
| `confidence` | 1–5 | self-reported confidence in that guess |
| `correct` | bool | scored by researcher against the model's actual output (hidden from participant) |
| `time_seconds` | number | how long they took |
| **`rationale_freetext`** | **text** | "Why do you think the model predicts that?" — unstructured |
| **`intervention_freetext`** | **text** | "What would you tell this student to do?" — unstructured, feeds actionability |
| **`missing_info_freetext`** | **text** | "What extra info would help you decide?" — unstructured, feeds limitations |

The three `*_freetext` columns are the unstructured dataset. Because each row carries
`case_id`, the text can be joined back to the exact features and explanation the
participant saw.

## 3. What the unstructured analysis produces

- **Rationale themes:** do participants in Group B (explanation) cite the same features
  the model's explanation highlights? (A loose, qualitative faithfulness-adjacent signal.)
- **Intervention themes:** what actions participants recommend → compare against the
  model's counterfactual suggestions (criterion 6).
- **Missing-info themes:** what participants feel is absent → report limitations.

Analyze with light qualitative coding (read and group the short responses). With ~10
people × 10 cases = 100 responses per field, this is hand-codable — no embedding
pipeline needed.

### Coding procedure

1. Create a short codebook before comparing groups, with a definition and one
   paraphrased example for every code.
2. Two team members independently code at least 20% of responses, blinded to group where
   practical.
3. Report raw agreement and resolve disagreements through discussion; do not claim a
   formal reliability statistic unless the sample supports it.
4. One coder may code the remainder using the agreed codebook.
5. Report theme counts by group descriptively and retain an `other/unclear` code.

## 4. Rules

- No participant names or identifiers — `participant_id` only.
- Store responses in `data/human_study/responses.csv` (git-ignored if it contains any
  free text that could identify someone; commit only the coded/theme summary).
- Report both group accuracies, sample size, and that no significance is claimed.
- Record time-on-task; note 2–3 think-aloud comments.
- The Group B display may show contribution direction and magnitude but must suppress
  the base value, final score, probability, capacity boundary and predicted class. Pilot it to
  confirm that the answer is not printed anywhere in the visualization.
- Do not reveal correctness or the model output after individual cases; debrief only
  after all 10 scored responses are locked, preventing cross-case learning.
- Do not report subgroup comparisons with fewer than five participants in a subgroup;
  describe sparse observations qualitatively and avoid inferential claims.

## 5. Status

> **Dependency:** the development model and protocol are frozen, but this study remains
> downstream-blocked until (a) validation explanation audits pass, (b) the 10 test cases
> are selected without cherry-picking after the single final evaluation, and (c) Group B's
> explanation view is rendered and piloted. Do not collect responses before then.

- [x] Student-support officer role + decision finalized (criterion 1)
- [x] Development model and explanation configuration frozen on validation
- [ ] 10 test cases selected from UCI test set (span at-risk / not-at-risk)
- [ ] Explanation rendering chosen (SHAP bar / feature list) for Group B — NEVER shows
      the model's output, only the feature contributions
- [ ] Case order randomized per participant (seed recorded)
- [x] Response schema created (`docs/human_study_response_template.csv`)
- [ ] Two-mode browser interface built from `docs/interface_spec.md`; study mode must
      enforce the blinded A/B protocol
- [ ] Consent screen, random assignment, exclusion log and timer implemented
- [ ] Codebook drafted; two-coder subset assigned
- [ ] Piloted on 1 person, revised (check: nobody can see the answer before answering)
- [ ] Run on 8–10 people (aim 4–5 per group)
- [ ] Free-text responses coded into themes
