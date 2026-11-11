# Student Dropout Project: cloud audit progress

Updated: 2026-11-11T01:00:17.169724+00:00 (UTC). The file updates every 5 seconds while the job runs. Refresh or reopen this file to load the latest snapshot. The case count increases when a complete case is saved.

**Process status: completed. Completed explanation cases: 544/544 (100.0%). Remaining: 0.**

Every validation student is selected; there is no 20-case sample limit.

Scope: all 544 original validation students. The model uses the 2,541 original training rows. The locked 545-row final test is excluded.

Original and isolated final-test locks unchanged: True.

This is a fresh isolated execution of the supplied notebook's audit driver. The earlier saved case remains in the original project and is not counted here. The previous resume attempt stopped on an exact probability-hash mismatch; its diagnostic and outputs are preserved in the previous run directory.

The verified official checkpoint and recorded settings were used to refit TabICL on training rows. The original private fitted-model file was not supplied.

Actual-outcome comparison: 544/544 validation rows scored. ROC-AUC 0.9521; dropout recall 50.70%; dropout precision 100.00% under the split's top-20% outreach rule. The model flagged 108 of 213 observed dropouts; 105 were unflagged.

First completed case: source row 3; estimated dropout probability 4.70%; outreach flagged: False. Saved 10 pair probes and 6 surrogate variants. Lowest local holdout MAE: Lasso+pairs (0.00115).

These case findings are partial and do not establish cohort-wide explanation quality or causal effects.

[Ten-minute update history](UPDATES_10_MIN.md) · [Live status JSON](live_status.json) · [Audit log](audit.log) · [Job and exit status](job.json)

Case JSON files: `project/W1_Noey_Enhanced/outputs/cases/`.

On successful completion of all 544 cases, the audit driver automatically writes `project/W1_Noey_Enhanced/outputs/tables/W1_COMPLETE_REPORT.md` and its tables and figures.
