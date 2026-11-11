# Full explanation audit

Start with `Reports/W1_COMPLETE_REPORT.md`.

Code/ and Reports/ are together here. Cases/ holds all 544 original case JSON files and provenance. Tables/ has 17 original tables and one explicitly derived unordered-pair table. Figures/ holds the five audit figures. Read Reports/REVIEW_NOTES.md for diagnostic findings.

For package navigation, see `../START_HERE.md`.

Two presentation figures are in `03_Full_Audit/Figures/Presentation/` (package-relative path). They use saved tables, readable labels and, for pairs, the derived unordered summary restricted to n >= 30 for display. All five original PNGs are retained unchanged in `03_Full_Audit/Figures/`. No SHAP/model/case computation was repeated.

## New W1.1–W1.5 topic analysis

Open `04_View_Results/W1_Topic_Analysis.html` or the executed notebook beside it for single-versus-pair comparisons, explanatory feature selection and human-support proposals. The code and derived results are grouped by topic under `03_Full_Audit/Code/topics/`. `topics/run_all.py` uses all 544 saved cases; it does not fit TabICL or rerun SHAP. The original model still uses its 33 inputs. The explanatory panel is not a new predictive feature set or a causal intervention ranking.
