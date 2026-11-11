# TA feedback: notes for the final report

> **Use:** documentation for the **final report only**; the proposal stays unchanged.
> Items marked **[DOC]** are to be written into the final report. Items marked **[CODE]** were
> analyses run in the repository; their results are in the "Code results" section at the end.
> Everything here is exploratory and post-hoc (run 11 Nov, after the final test).
> All numbers are validation-only (544 students); the locked final test was not opened or rerun.

| TA point | Type | Status | Where |
|---|---|---|---|
| All 108 flags are dropouts: suspicious, not good | [DOC] | Done | Enrolled-free check in TASK_SPLIT §5: precision 1.000 is a validation result with fixed capacity |
| Who are the 108? Would an officer learn anything new? | [DOC] (numbers from [CODE] 1) | Numbers saved | See below; `tables/sensitivity/ta_flag_composition.csv` |
| What will the explanations say about them? | [DOC] (numbers from [CODE] 1) | Numbers saved | See below; `tables/sensitivity/ta_flag_composition.csv` |
| Enrolled students | [DOC] | Done | Enrolled sensitivity check in `tables/sensitivity/`: Enrolled median score 0.354, they get 7 of 132 flags, AUC drops from 0.952 to 0.924 |
| Why 67? Is stability measuring the budget? | [DOC] | Explained; no larger-budget run (skipped: about 3.5 h) | See "SHAP budget" below |
| Could you predict the flag by adding up the bars? | [DOC] (numbers from [CODE] 1) | Numbers saved | See below; `tables/sensitivity/ta_bar_sum.csv` |
| Protected attributes: argue either way | [DOC] + [CODE] 2 | Done | HANDOFF: kept for auditing only, not a basis for outreach; `tables/sensitivity/no_protected_*.csv` |
| Fee status: which way does the arrow point? | [DOC] | Done | HANDOFF "Recourse and human-study interpretation" |
| Readability, first page for a support officer | [DOC] | Report work | Not in the repo; it belongs in the final report |

## [DOC] New numbers (validation only, 544 students)

- **Who the 108 are:**
  - 78 passed zero first-semester units, and 25 took no evaluations at all.
  - Of the other 30, 19 had unpaid fees.
  - A simple "passed zero units" rule picks 103 students with precision 0.874 and recall 0.42. The
    model gets 1.000 and 0.507.
  - So the model mostly confirms what an officer could already see. Its added value is narrow: it
    leaves out 25 zero-pass students (13 of whom graduated) and adds 30 others.
- **What the explanations say:** for all 108 flagged students, the top reason is "first-semester
  progress". For flagged students the explanation mostly repeats the obvious.
- **Adding up the bars:** summing all the bars reproduces the model's ranking exactly (AUC 1.0), as
  SHAP is designed to. Group B only saw the top 5 bars, and even their sum separates flagged from not
  flagged with AUC 0.97 and finds 89 of the 108 flags.
  - This means the study mainly tests whether people can read the chart, not whether explanations
    help decisions.
  - The profile-only group also scored 0.916, so the task was easy either way.
- **SHAP budget:** with 33 features, `max_evals = 2×33+1 = 67` is the smallest budget possible. It
  is exactly one permutation per explanation (shap's PermutationExplainer uses
  `max_evals // (2 × 33 + 1)` forward-and-backward permutations; shap's own default would be about
  10). That means the seed instability (0.818, with 213 of 544 students below 0.80) may come partly
  from the budget, which is the TA's point. A larger-budget rerun was not done (about 3.5 hours);
  state this as a limitation. The background instability (0.745, 411 below 0.80) is a separate
  source: it changes the comparison group, not the number of permutations.

## [CODE] items

1. **Done.** Save the numbers above as a script and tables: `scripts/run_ta_feedback_checks.py`
   (saved W1 validation cases only, no model run) → `tables/sensitivity/ta_flag_composition.csv`,
   `ta_bar_sum.csv`, `ta_feedback_summary.json`.
2. **Done.** Sensitivity run without the protected attributes (validation only):
   `scripts/run_no_protected_sensitivity.py` → `tables/sensitivity/no_protected_metrics.csv`,
   `no_protected_flag_rates.csv`, `no_protected_summary.json`.
3. **Skipped by the team:** larger-SHAP-budget stability rerun (about 3.5 hours).

## Code results

**[CODE] 1** reproduces every number in the "New numbers" section above.

**[CODE] 2: without protected attributes** (gender, nationality, age, international, displaced,
special educational needs removed; TabICL refitted on the training rows with the frozen settings;
544 validation students; top-20% rule):

| Model | Features | ROC-AUC | Brier | Recall at 20% | Precision at 20% |
|---|---|---|---|---|---|
| All features (refit control) | 33 | 0.9521 | 0.0708 | 0.507 | 1.000 |
| Without protected attributes | 27 | 0.9503 | 0.0724 | 0.507 | 1.000 |

- 103 of the 108 flags are the same; 5 swap out and 5 swap in, all 10 of them dropouts.
- The refit control matches the frozen model (ROC-AUC 0.9521), so the difference is from the
  removed columns, not from refitting.
- Dropout recall by gender (coded groups 0/1) moves from 0.404 / 0.597 to 0.455 / 0.553: the gap
  narrows from 0.19 to 0.10. Flag rates by gender: 0.120 / 0.324 → 0.135 / 0.300.
- Age band 21-25 recall falls from 0.565 to 0.500; under-20 recall rises from 0.342 to 0.378;
  displaced/not-displaced change by about 0.01. Groups under 30 are suppressed.
- **Argument for the report:** on validation, the protected attributes add almost nothing to
  accuracy, and removing them narrows the gender recall gap. That supports **not** using them to
  decide outreach. Against: removing columns does not remove proxies (course, age-linked
  admission route, etc.; see the proxy screen), and keeping them in an audit model is what lets us
  measure gaps at all. Suggested position: audit with them, do not prioritise outreach with them.
  This is validation-only and descriptive, not proof of fairness.
