# Reproducibility and private-input boundary

## What a clean clone can verify

A clean clone can run the unit and form-spec tests, inspect the frozen protocol, reproduce fixture
forms, verify the saved final-test output manifest, inspect the complete 544-case W1 audit, and
rebuild every aggregate report-ready table and figure from committed aggregate outputs.

```powershell
python -m unittest discover -s tests -v
python forms/test_spec.py
python scripts/build_report_assets.py
```

The locked final test must not be rerun. Its saved output hashes are in
`tables/final_test/manifest.json`, and its once-only record is `artifacts/final_test.lock`.

## Intentionally private or ignored inputs

The following are required only for their corresponding restricted reruns and are not committed:

| Asset | Purpose | Reason excluded |
| --- | --- | --- |
| `data/local_freeze/` | Exact checkpoint and frozen source snapshot | Large checkpoint/local execution evidence |
| `data/final_evaluation/selected_model.joblib` | Original local fitted model bundle | Large/private fitted artifact |
| `data/study_cases/` | Private model flags and study-case lookup | Prevent disclosure of study answers |
| `data/human_study/assignment_list.csv` | Sealed participant allocation | Pseudonymous private assignment |
| `data/human_study/scoring_private/` | Private form specification and answer lookup | Study-answer confidentiality |
| `data/human_study/scoring_private/exports/response_sheet_study.xlsx` | Raw completed survey responses and free text (moved from the repo root on 11 Nov; `*.xlsx` is git-ignored) | Participant privacy |
| `data/human_study/analysis/` | Row-level transformed and scored responses | Participant privacy |

Possession of the repository alone is deliberately insufficient to reconstruct private participant
responses or hidden study answers. Authorized team members can reproduce aggregate results using
the commands in `docs/HUMAN_STUDY_RESULTS.md`.

## Saved-evidence provenance

- The 2 November final test used the recorded local content-hashed freeze and must remain once-only.
- The later W1 audit excluded the test split and used a refit on the original training rows with the
  frozen settings and official checkpoint. It did not load the original private serialized model.
- Human-study aggregate outputs contain no participant codes or free text. Their manifest records
  hashes of the authorized private inputs and aggregate outputs.
- `tables/report_ready/project_numbers.json` is the preferred central source for headline numbers
  when the final report is written.

## Environment

The pinned Python 3.12 environment is listed in `requirements.txt`. Excel workbook ingestion uses
`openpyxl`; modeling, explanation and plotting dependencies remain pinned to the versions used by
the recorded analyses.

