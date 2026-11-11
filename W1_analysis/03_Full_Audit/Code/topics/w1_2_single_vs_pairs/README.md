# W1.2 — Single versus paired feature groups

`analysis.py` provides two comparisons from the saved evidence.

1. **Model masking response:** compare each single-group change with the joint change on the same student. Canonical unordered pair labels combine A/B and B/A; group-specific single effects are swapped consistently. Every pair retains its observed case count. Larger response is not evidence of a better human intervention.
2. **Surrogate fidelity:** compare OLS, Ridge and Lasso main-only versus with-pair models on the same students and the original eight held-out masks. The original 24 fitting masks were used in the completed audit; no surrogates or TabICL are refitted here.

$$
I_{A,B}=p(x_{A\cup B})-p(x_A)-p(x_B)+p(x).
$$

$$
\Delta\mathrm{MAE}_s=\mathrm{MAE}_{s,\mathrm{main}}-\mathrm{MAE}_{s,\mathrm{pairs}}.
$$

A positive MAE reduction favors paired terms for local approximation. Bootstrap intervals resample **students**, preserving the dependence among their eight masks. They are descriptive per-family intervals, not a new independent predictive test or a multiplicity-adjusted confirmatory study.

`single_vs_pair_summary.csv` also reports the absolute joint change minus the strongest absolute single change. An interaction can matter even when the joint response is smaller than a single response; pair terms represent dependence, not necessarily a larger favorable risk change.

Outputs are beside this file in `results/`. All 177 observed unordered pairs remain in the summary; the reporting panel applies the explicit support threshold from `policy.json`. Missing/unobserved pairs are not treated as zero effects.
