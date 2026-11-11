"""Presentation-only figures from saved tables; no model or audit computation."""
from pathlib import Path
import textwrap
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
folder = root / "Figures/Presentation"
folder.mkdir(parents=True, exist_ok=True)
names = {
    "first_semester_progress": "First-semester progress",
    "first_semester_participation": "First-semester participation",
    "tuition_fees_up_to_date": "Tuition fees up to date",
    "previous_qualification_grade": "Previous qualification grade",
    "curricular_units_1st_sem_credited": "First-semester credited units",
    "scholarship_holder": "Scholarship holder",
    "mothers_occupation": "Mother's occupation",
    "fathers_occupation": "Father's occupation",
}
def label(value):
    return names.get(value, value.replace("_", " ").capitalize())

shap = pd.read_csv(root / "Tables/w1_local_shap_summary_validation.csv").head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(11, 7), layout="constrained")
ax.barh([label(v) for v in shap["feature_group"]], shap["mean_absolute_group_shap"], color="#2775ad")
ax.set_title("Grouped SHAP contributions across 544 validation students", fontsize=14, pad=14)
ax.set_xlabel("Mean absolute grouped SHAP (model probability units)")
ax.grid(axis="x", alpha=0.18)
ax.set_axisbelow(True)
fig.savefig(folder / "local_shap_importance_validation.png", dpi=160, bbox_inches="tight")
plt.close(fig)

pairs = pd.read_csv(root / "Tables/pairwise_unordered_summary_derived.csv")
pairs = pairs.loc[pairs["cases_observed"] >= 30].head(8).iloc[::-1]
labels = [textwrap.fill(f"{label(r.group_a)} + {label(r.group_b)} (n={r.cases_observed})", 47)
          for r in pairs.itertuples()]
fig, ax = plt.subplots(figsize=(12, 8.5), layout="constrained")
ax.barh(labels, pairs["mean_absolute_nonadditive_effect"], color="#2775ad")
ax.set_title("Reference-masking nonadditivity: unordered feature pairs", fontsize=14, pad=14)
ax.set_xlabel("Mean absolute nonadditive probability response")
ax.grid(axis="x", alpha=0.18)
ax.set_axisbelow(True)
fig.text(0.5, -0.015, "Pairs observed in at least 30 cases; conditional on each student's top five groups. Not causal effects.",
         ha="center", fontsize=10)
fig.savefig(folder / "pairwise_reference_masking_validation.png", dpi=160, bbox_inches="tight")
plt.close(fig)
