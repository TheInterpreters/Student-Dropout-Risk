# Case-pack format (W2.2), version 1.0

**Status:** draft for agreement by W1, W2 (Han), W3 and W5 (Lucas). The machine check is `forms/case_pack.py`;
if this page and that file ever differ, the file wins.

The case pack carries the 11 cases (practice `PR`, scored `C01` to `C10`) from the people who make them to the
people who use them. Agreeing the format now means the study export on Wed 11 Nov drops straight into the chart
renderer and the form builder.

| Who | Does what with it | When |
|---|---|---|
| W2 (builder) | Makes the **fixture** pack now; builds the forms from a pack | now; real forms Thu 12 Nov (W2.7) |
| W1 | Confirms the contributions are computed as in section 4 | this week |
| W3 | Exports the **study** pack and private file after the final test | Wed 11 Nov (W3.9) |
| W5 | Draws one chart per case from `contributions`; scoring reads the private file | test charts by Thu 5 Nov (W5.3); scoring W5.6 |

## 1. Two files

| File | Contains | Where it lives |
|---|---|---|
| `case_pack_<kind>.json` | Profiles, chart file names, top-5 contributions. **No model output.** | Restricted Drive folder (never git) |
| `private_lookup_<kind>.json` | Per case: dataset row and the model's flag | Restricted; scoring and W3 only. Never in the forms or git |

`<kind>` is `fixture` (dummy validation cases, now) or `study` (the real cases, 11 Nov).
The fixture pack is rebuilt with `python3 forms/build_spec.py` (output in `forms/out/`, ignored by git).

## 2. Case pack: top level

| Field | Value |
|---|---|
| `contract_version` | `"1.0"` |
| `pack_kind` | `"fixture"` or `"study"` |
| `protocol_version` | `"1.3"` |
| `source` | One line: where the cases came from (split, selection rule, date) |
| `model_ref` | Git tag or commit of the frozen model, e.g. `protocol-1.3-frozen` (`"none (fixture)"` for fixtures) |
| `contributions_placeholder` | `true` only in fixtures with made-up bars; must be `false` in a study pack |
| `cases` | Exactly 11 cases in the order `PR, C01, ..., C10` |

## 3. Each case

| Field | Value |
|---|---|
| `case_id` | `PR` or `C01` to `C10` |
| `role` | `"practice"` for `PR`, `"scored"` for the rest |
| `profile` | The 30 dataset fields as `{"field": <dataset column name>, "value": <raw value>}`. Raw codes and numbers only; `forms/labels.py` turns them into plain words. No second-semester fields, no `Target` |
| `chart_file` | `chart_<case_id>.png`, e.g. `chart_C07.png` |
| `contributions` | Exactly 5 bars, largest first (section 4) |

## 4. Contributions (what the Group B chart draws)

- Computed with the frozen explanation settings: permutation SHAP on the model's dropout probability
  (25 training background rows, 67 evaluations; `config/evaluation_protocol.json`).
- First-semester features are combined into two bars by **adding their signed values**
  (`aggregate_shap_by_group` in `src/explanations.py`); every other feature is its own bar.
  That gives 27 possible bars.
- Keep the **5 bars with the largest absolute value**, sorted largest first.
- Each bar is `{"bar_id": <model feature or group name>, "label": <plain name>, "value": <signed number>}`.
  - `bar_id`: the model's feature name (dataset column after `clean_column_name` in `src/modeling.py`), or a group name below.
  - `label`: must equal `bar_labels()` in `forms/case_pack.py`, which reuses the profile card's words.
  - `value`: positive = pushed the model toward dropout risk (more worried); negative = less worried.
    Used only for bar direction and length; the chart never prints it.
- Never include the base value, probability, score, rank or flag.

| Group bar | Plain name (proposed) | Dataset fields combined (plus their derived features) |
|---|---|---|
| `first_semester_participation` | First-semester participation (units, exams) | 1st sem (enrolled), 1st sem (evaluations), 1st sem (without evaluations) |
| `first_semester_progress` | First-semester progress (passed units, grade) | 1st sem (approved), 1st sem (grade) |

## 5. Private file

Per case: `source_row_id` (whole number, row in the UCI file) and `model_flag`
(1 = flagged by the top-20% capacity policy, 0 = not; `null` in fixtures).
A study pack must have exactly 5 flagged and 5 not-flagged scored cases.
Scoring (W5.6): a guess is correct when (Q1 is "Yes") equals (`model_flag` is 1).

## 6. Rules for the study export (W3.9)

1. Number the scored cases `C01` to `C10` in **ascending `source_row_id`**, never by flag or risk, so the IDs give nothing away.
2. Check both files before handing them over; this must print `PASS`:
   `python3 forms/case_pack.py case_pack_study.json private_lookup_study.json`
3. Put both files in the restricted Drive folder and tell W2 and W5.

## 7. Example (fixture case `C01`, shortened; contribution values are placeholders)

```json
{
  "contract_version": "1.0",
  "pack_kind": "fixture",
  "protocol_version": "1.3",
  "source": "FIXTURE: 11 dummy cases from the validation split (FIXTURE_SEED 1). Not for scoring.",
  "model_ref": "none (fixture)",
  "contributions_placeholder": true,
  "cases": [
    {
      "case_id": "C01",
      "role": "scored",
      "profile": [
        {
          "field": "Marital status",
          "value": "1.0"
        },
        {
          "field": "Application mode",
          "value": "1.0"
        },
        {
          "field": "Application order",
          "value": "1.0"
        },
        {
          "field": "...",
          "value": "(all 30 fields)"
        }
      ],
      "chart_file": "chart_C01.png",
      "contributions": [
        {
          "bar_id": "daytime_evening_attendance",
          "label": "Attendance",
          "value": -0.1017
        },
        {
          "bar_id": "application_mode",
          "label": "Admission route",
          "value": -0.0925
        },
        {
          "bar_id": "tuition_fees_up_to_date",
          "label": "Tuition fees paid up to date",
          "value": -0.0734
        },
        {
          "bar_id": "fathers_occupation",
          "label": "Father's job",
          "value": -0.0164
        },
        {
          "bar_id": "gdp",
          "label": "GDP growth (%)",
          "value": 0.0112
        }
      ]
    },
    "... (PR, then C01 to C10)"
  ]
}
```

Private file:

```json
{
  "PR": {
    "source_row_id": 1234,
    "model_flag": 0
  },
  "C01": {
    "source_row_id": 2087,
    "model_flag": 1
  },
  "...": "..."
}
```

(Row numbers above are made up for the example.)

## 8. To agree

- [ ] **W3:** where the practice case comes from. Proposal: one validation-split case, so it is not a test case and can appear in screenshots.
- [ ] **W3:** the ID rule in section 6 (ascending `source_row_id`).
- [ ] **W1:** contributions computed as in section 4 (same SHAP settings as the audit, top 5, group sums).
- [ ] **W5:** the two group bar names, and charts named `chart_<case_id>.png`.
- [ ] **W5:** fixture charts drawn from `forms/out/case_pack_fixture.json`; its bars are placeholders until real validation SHAP values exist.
