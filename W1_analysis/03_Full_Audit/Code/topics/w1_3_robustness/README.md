# W1.3 — Robustness from saved ranking repeats

`analysis.py` reconstructs mean pairwise top-five overlap from the stored seed, background and accepted-grade ranking lists. It reports conditional retention of each feature group among cases where it appeared in the baseline top five. Conditional retention is not its overall prevalence.

Original warning flags are preserved. A separate column uses a 1e-12 tolerance so values numerically indistinguishable from 0.80 are not described as materially below 0.80. For this run, recorded seed/background warnings were 213/411; tolerance-corrected counts are 194/403. The original case JSON files are not edited.

This does not establish robustness to arbitrary future changes or causal interventions.
