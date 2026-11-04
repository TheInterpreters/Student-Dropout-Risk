# Case-pack format (W2.2), version 1.0

**Status (updated 4 Nov):** format review, real export, local data/provenance checks and 11 chart
files are complete. The team reports the real-form build, live acceptance/export checks and pilot
complete; this document does not record per-check results or independently verify the live forms.
Restricted data handling remains required. The machine check is `forms/case_pack.py`; if this page
and that file ever differ, the file wins.

The case pack carries the 11 cases (practice `PR`, scored `C01` to `C10`) from the people who make them to the
people who use them. The real pack now exists locally and is compatible with the chart renderer
and form builder. Original November deadlines below have been superseded by completed local work.

| Who | Does what with it | When |
|---|---|---|
| W2 (builder) | Uses genuine pack/charts and canonical assignment to build real forms | Real-form build and live acceptance reported complete by the team (4 Nov); this document does not contain individual check outcomes |
| W1 | Reviews explanation methods and explicitly omitted audit limitations | Independent review pending; no full-audit certification |
| W3 | Real **study** pack and private lookup exported after once-only final evaluation | Export completed 2 Nov; team reports restricted study handover and live form insertion complete by 4 Nov |
| W5 | Renderer integrated/verified; genuine chart generation completed by Yolanda; scorer uses private lookup | 11 charts exist; team reports live acceptance complete; detailed parity evidence and independent scoring review are not recorded here |

## 1. Two files

| File | Contains | Where it lives |
|---|---|---|
| `case_pack_<kind>.json` | Profiles, chart file names, top-5 contributions. **No model output.** | Restricted Drive folder (never git) |
| `private_lookup_<kind>.json` | Per case: dataset row and the model's flag | Restricted; scoring and W3 only. Never in the forms or git |

`<kind>` is `fixture` (dummy validation cases) or `study` (real cases exported on 2 Nov).
The fixture pack is rebuilt with `python3 forms/build_spec.py` (output in `forms/out/`, ignored by git).

## 2. Case pack: top level

| Field | Value |
|---|---|
| `contract_version` | `"1.0"` |
| `pack_kind` | `"fixture"` or `"study"` |
| `protocol_version` | `"1.3"` |
| `source` | One line: where the cases came from (split, selection rule, date) |
| `model_ref` | Current study: `"local-sha256:<manifest SHA-256>"`, bound to the local freeze. Original tagged mode: frozen Git tag/commit. Fixtures: `"none (fixture)"` |
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
   The checker now also enforces unique source rows, ascending C01-C10 source IDs, split membership
   (PR = validation, scored study cases = test) and profile parity with the public source row.
   The fixture mode requires all 11 rows to be validation rows. Row IDs are zero-based in the original UCI CSV.
3. Share the case pack and chart PNGs with the form builder through restricted storage.
   Keep the private lookup in a separate restricted scoring location available only to W3 and
   the designated scorer/coordinator; do not upload it as a participant-facing or Apps Script
   input. Local build validation may use it, but only public form outputs/charts are uploaded.

The checker verifies structure, row/split/profile parity, ID ordering and the 5/5 flag count.
It does **not** authenticate `model_ref`, recompute SHAP or prove flags match the fitted model.
The export runner binds model/freeze hashes; the saved-prediction selection/flag cross-check
is separate local evidence recorded in HANDOFF §12, not an independent review.

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

Contract review, 2 Nov 2026: Yolanda approves the following format requirements on behalf of the owners with
their authorisation. The SHAP settings match `config/evaluation_protocol.json`; the two semantic groups and
signed aggregation match `src/explanations.py`, and the form tests cross-check the group members and bar IDs.
That format review alone was not verification of real SHAP computation or delivery.
Subsequent execution on 2 Nov completed the genuine case export, local chart-file generation
and contract checks by Yolanda using the existing contract and renderer. The team reports that
the restricted study build/live insertion and acceptance checks were completed by 4 Nov; this
document does not independently verify them or specify individual check outcomes.
The final model bundle/snapshot hashes, deterministic selection/flags and exact profile/source
provenance verify; no independent recomputation of SHAP or full-audit certification is claimed.
The team reports live form acceptance complete. Detailed visual/parity evidence is not reproduced
here and should not be inferred from that aggregate status.

- [x] **W3:** practice case from the validation split, not a test case. Screenshots remain subject to the restricted-data rules.
- [x] **W3:** the ID rule in section 6 (ascending `source_row_id`).
- [x] **W1:** section 4 matches frozen settings/signed-group aggregation; real export complete, full explanation audits omitted rather than passed.
- [x] **W5:** the two group bar names, and charts named `chart_<case_id>.png`.
- [x] **W5:** fixtures remain testing-only. Real chart-file generation completed by Yolanda using Lucas's renderer, integrated and verified by Yolanda. The team reports the real-form/live acceptance process complete (4 Nov); retain any detailed chart/parity evidence separately.
