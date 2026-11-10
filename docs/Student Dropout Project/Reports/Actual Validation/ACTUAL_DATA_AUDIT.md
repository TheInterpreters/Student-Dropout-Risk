# Actual validation-data audit

**Data checks completed: 544/544 validation observations, 33 model features.**
Actual recorded outcomes: 213 Dropout and 331 Graduate.

The 2,541 training rows are fitting/reference data, not audit cases. The 545 locked test rows are excluded from this analysis. The original saved split IDs are used; no sampling or re-splitting occurs.

| Data check | Rows flagged |
| --- | ---: |
| has nonfinite model feature | 0 |
| approved exceeds enrolled | 0 |
| negative enrolled or approved | 0 |
| grade outside 0 20 | 0 |
| duplicate feature profile | 0 |

These checks establish only the listed data properties. Zero flags do not certify the entire data-generating process, feature validity, model accuracy, explanation quality or intervention efficacy. Rows are checked without deleting or changing source records.

**Next:** compare the trained model's predictions with the 544 recorded outcomes (`--compare`), then run/resume all 544 explanation cases (`--run`). This data report alone does not mean either model stage has run. Their evidence is stored separately.

Provenance: source data SHA256 `0e7313f006da5a9d8b419b859467a01b06b59b7f14b3eeb672c9be60684ab7ef`; saved split SHA256 `0ec71619191097ab2e4d0475aeb748cc0961422de17095f49646312c65a81940`. See `data_audit_summary.json`, `feature_quality_by_split.csv`, `actual_outcome_counts_by_split.csv` (row-level checks remain in the local audit outputs).
