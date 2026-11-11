# W1.5 — Selected explanatory groups and interaction hypotheses

`analysis.py` produces `results/selected_explanatory_panel.json` and CSV tables. It selects the five highest mean-absolute-SHAP groups for reporting, then up to three supported pairs within those groups ranked by mean absolute nonadditivity, provided pair-augmented surrogates have lower recorded holdout error than main-only variants. Defaults are explicit in `policy.json`; minimum support is a reporting safeguard, not a significance threshold.

The results are an exploratory explanatory shortlist. They do not remove any of the 33 original predictor inputs, establish causal interventions, or recover exact nonzero Lasso coefficients that were not saved. Feature-specific robustness, model-response coverage and convergence caveats remain visible.

For a final input set for a **new predictor**, select inputs using training-only cross-validation/nested evaluation, validate the revised predictor separately, and keep the old model/audit as its own version. Changing that predictor would require explanations appropriate to the new model. The present single/pair comparison needs no full audit rerun.
