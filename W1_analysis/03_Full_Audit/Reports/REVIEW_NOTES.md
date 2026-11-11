# Completion and interpretation notes

All 544 validation case computations completed successfully. Coverage and source/probability provenance were independently checked; see `05_Provenance/full_audit_completion_validation.json`.

- Background SHAP top-five overlap averaged 0.745; 411/544 cases were below the protocol's 0.80 warning threshold.
- Seed overlap averaged 0.818; 213/544 cases were below 0.80.
- Grade-perturbation overlap averaged 0.996. These probes do not establish real-world intervention effects.
- The log contains 579 convergence warnings associated with 342 cases' surrogate fits. Some may concern inner cross-validation fits; the log does not establish that every warning concerns a final selected fit. These warnings limit unqualified claims about surrogate fitting.
- The recorded lowest pooled surrogate holdout MAE is 0.02239 for Lasso+pairs. This measures approximation of TabICL on held-out masked inputs, not dropout-outcome prediction accuracy.

## Pair-order aggregation

The original runner groups pairs by their A/B order. Its original summary can list the same unordered pair in two orders. The original report and original CSV are retained unchanged. `Tables/pairwise_unordered_summary_derived.csv` combines both orders into 177 unordered pairs using all 5,440 saved case-level probes. No student/model/audit computation was rerun. Pair summaries remain conditional on each case's selected top five groups; counts differ across pairs. The viewer displays pairs observed in at least 30 cases and retains every pair in the derived CSV.

Completion confirms all requested case calculations are available. It does not mean every explanation-quality diagnostic passed. The model was refitted from recorded settings; the original private fitted-model bundle was not supplied.

Two presentation figures are in `03_Full_Audit/Figures/Presentation/` (package-relative path). They use saved tables, readable labels and, for pairs, the derived unordered summary restricted to n >= 30 for display. All five original PNGs are retained unchanged in `03_Full_Audit/Figures/`. No SHAP/model/case computation was repeated.
