"""Build aggregate tables and figures for the later report without rerunning any model."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLE_OUT = ROOT / "tables" / "report_ready"
FIGURE_OUT = ROOT / "figures" / "report_ready"


def save_figure(fig, name):
    FIGURE_OUT.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURE_OUT / name, dpi=220, bbox_inches="tight")
    plt.close(fig)


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def model_assets():
    metrics = pd.read_csv(ROOT / "tables" / "final_test" / "metrics.csv")
    metrics["model_label"] = metrics["model"].map({
        "logistic_regression": "Logistic regression", "decision_tree_depth_3": "Decision tree",
        "xgboost": "XGBoost", "explainable_boosting_main_effects": "EBM", "tabicl": "TabICL",
    })
    columns = ["model", "model_label", "roc_auc", "brier_score", "balanced_accuracy", "macro_f1",
               "dropout_recall", "dropout_precision", "flag_rate", "expected_calibration_error_10bin"]
    metrics[columns].to_csv(TABLE_OUT / "final_test_model_metrics.csv", index=False, float_format="%.4f")
    paired = pd.read_csv(ROOT / "tables" / "final_test" / "paired_comparisons.csv")
    paired.to_csv(TABLE_OUT / "tabicl_paired_comparisons.csv", index=False, float_format="%.4f")

    ordered = metrics.sort_values("roc_auc")
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2))
    axes[0].barh(ordered["model_label"], ordered["roc_auc"], color="#4C78A8")
    axes[0].set(xlabel="ROC-AUC", xlim=(0.88, 0.97), title="Discrimination")
    axes[1].barh(ordered["model_label"], ordered["brier_score"], color="#F58518")
    axes[1].set(xlabel="Brier score (lower is better)", title="Probability accuracy")
    for ax in axes:
        ax.grid(axis="x", alpha=0.25)
    save_figure(fig, "final_test_model_performance.png")

    x = np.arange(len(metrics))
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    ax.bar(x - 0.2, metrics["dropout_recall"], 0.4, label="Recall", color="#4C78A8")
    ax.bar(x + 0.2, metrics["dropout_precision"], 0.4, label="Precision", color="#54A24B")
    ax.set(xticks=x, xticklabels=metrics["model_label"], ylabel="Metric at 20% flag capacity", ylim=(0, 1.05))
    ax.tick_params(axis="x", rotation=20)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    save_figure(fig, "final_test_outreach_metrics.png")
    return metrics


def explanation_assets():
    summary = json.loads((ROOT / "W1_analysis" / "03_Full_Audit" / "Reports" / "summary.json").read_text(encoding="utf-8"))
    shap = pd.read_csv(ROOT / "W1_analysis" / "03_Full_Audit" / "Tables" / "w1_local_shap_summary_validation.csv")
    shap.head(10).to_csv(TABLE_OUT / "top_explanation_groups.csv", index=False, float_format="%.4f")
    stability = pd.DataFrame([
        {"variation": name, **values} for name, values in summary["stability"].items()
    ])
    stability.to_csv(TABLE_OUT / "explanation_stability_summary.csv", index=False, float_format="%.4f")
    audit = pd.DataFrame([{
        "validation_cases": summary["n_cases"],
        "faithfulness_mean_area": summary["faithfulness"]["mean_area"],
        "faithfulness_ci_lower_95": summary["faithfulness"]["ci_lower_95"],
        "faithfulness_ci_upper_95": summary["faithfulness"]["ci_upper_95"],
        "faithfulness_positive_cases": summary["faithfulness_positive_cases"],
        "flagged_cases": summary["recourse"]["n_flagged_cases"],
        "flagged_with_recourse_candidate": summary["recourse"]["n_cases_with_recourse"],
        "flagged_without_recourse_candidate": summary["recourse"]["n_flagged_without_recourse"],
    }])
    audit.to_csv(TABLE_OUT / "explanation_audit_headlines.csv", index=False, float_format="%.4f")

    top = shap.head(8).sort_values("mean_absolute_group_shap")
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.barh(top["feature_group"].str.replace("_", " "), top["mean_absolute_group_shap"], color="#4C78A8")
    ax.set(xlabel="Mean absolute grouped SHAP (probability units)", title="Validation explanation importance")
    ax.grid(axis="x", alpha=0.25)
    save_figure(fig, "top_explanation_groups.png")

    order = [name for name in ("seed", "background", "perturbation") if name in set(stability["variation"])]
    plotted = stability.set_index("variation").loc[order]
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    bars = ax.bar(plotted.index.str.title(), plotted["mean_top_5_overlap"], color=["#4C78A8", "#F58518", "#54A24B"])
    ax.axhline(0.8, color="#B22222", linestyle="--", label="0.80 warning threshold")
    ax.set(ylabel="Mean pairwise top-five overlap", ylim=(0, 1.05), title="Explanation stability by variation source")
    ax.bar_label(bars, fmt="%.3f", padding=3)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    save_figure(fig, "explanation_stability.png")
    return summary


def fairness_assets():
    subgroup = pd.read_csv(ROOT / "tables" / "final_test" / "tabicl_subgroups.csv")
    subgroup.to_csv(TABLE_OUT / "tabicl_subgroup_diagnostics.csv", index=False, float_format="%.4f")
    proxy = pd.read_csv(ROOT / "tables" / "final_test" / "tabicl_proxies.csv").sort_values("association", ascending=False)
    proxy.head(15).to_csv(TABLE_OUT / "top_proxy_associations.csv", index=False, float_format="%.4f")


def human_assets():
    human = pd.read_csv(ROOT / "tables" / "human_study" / "group_summary.csv")
    human.to_csv(TABLE_OUT / "human_study_group_summary.csv", index=False, float_format="%.4f")
    for name in ("group_comparisons", "case_summary", "leave_one_case_out", "flag_summary",
                 "practice_checks", "role_summary", "variant_summary"):
        pd.read_csv(ROOT / "tables" / "human_study" / f"{name}.csv").to_csv(
            TABLE_OUT / f"human_study_{name}.csv", index=False, float_format="%.4f")
    return json.loads((ROOT / "tables" / "human_study" / "summary.json").read_text(encoding="utf-8"))


def flow_assets():
    fig, ax = plt.subplots(figsize=(12, 3.3))
    ax.axis("off")
    labels = ["UCI data\n4,424 records", "Binary cohort\n3,630 records", "70/15/15 split\n2,541 / 544 / 545",
              "Five frozen models\n20% outreach capacity", "Locked final test\n+ W1 validation audit", "Human study\n50 participants"]
    positions = np.linspace(0.06, 0.94, len(labels))
    for index, (x, label) in enumerate(zip(positions, labels)):
        ax.text(x, 0.5, label, ha="center", va="center", transform=ax.transAxes,
                bbox={"boxstyle": "round,pad=0.45", "facecolor": "#E8F1FA", "edgecolor": "#4C78A8"})
        if index < len(labels) - 1:
            ax.annotate("", xy=(positions[index + 1] - 0.065, 0.5), xytext=(x + 0.065, 0.5),
                        xycoords=ax.transAxes, arrowprops={"arrowstyle": "->", "color": "#444444", "lw": 1.5})
    save_figure(fig, "project_pipeline.png")

    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    ax.axis("off")
    nodes = [(0.5, 0.86, "50 completed participants"), (0.25, 0.55, "Group A: 25\nprofiles only"),
             (0.75, 0.55, "Group B: 25\nprofiles + explanation charts"),
             (0.25, 0.20, "10 scored cases\nper participant"), (0.75, 0.20, "10 scored cases\n+ practice chart checks")]
    for x, y, label in nodes:
        ax.text(x, y, label, ha="center", va="center", transform=ax.transAxes,
                bbox={"boxstyle": "round,pad=0.5", "facecolor": "#F5F5F5", "edgecolor": "#4C78A8"})
    for start, end in (((0.5, 0.78), (0.25, 0.64)), ((0.5, 0.78), (0.75, 0.64)),
                       ((0.25, 0.46), (0.25, 0.29)), ((0.75, 0.46), (0.75, 0.29))):
        ax.annotate("", xy=end, xytext=start, xycoords=ax.transAxes,
                    arrowprops={"arrowstyle": "->", "lw": 1.5, "color": "#444444"})
    save_figure(fig, "human_study_design.png")


def sensitivity_assets():
    """Copy the optional W3.7 Enrolled sensitivity aggregates, if they have been produced."""
    folder = ROOT / "tables" / "sensitivity"
    summary_path = folder / "enrolled_summary.json"
    if not summary_path.is_file():
        return {"status": "not run"}
    for name in ("enrolled_frozen_score_distribution", "enrolled_capacity_displacement",
                 "enrolled_grouped_validation_metrics"):
        pd.read_csv(folder / f"{name}.csv").to_csv(
            TABLE_OUT / f"sensitivity_{name}.csv", index=False, float_format="%.4f")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("test_split_accessed") is not False:
        raise ValueError("sensitivity summary does not confirm the test split was untouched")
    return {"status": "completed", "capacity_displacement": summary["capacity_displacement"]}


def demo_card_assets():
    """Copy the W5.1 validation-only demo card into the central figure folder."""
    folder = ROOT / "figures" / "demo_card"
    record_path = folder / "demo_card_validation.json"
    if not record_path.is_file():
        return {"status": "not built"}
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if record.get("split") != "validation" or record.get("test_split_accessed") is not False:
        raise ValueError("demo card is not a validation-only record")
    FIGURE_OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(folder / "demo_card_validation.png", FIGURE_OUT / "demo_card_validation.png")
    return {"status": "built", "split": "validation", "source_row_id": record["source_row_id"],
            "predicted_probability": record["predicted_probability"], "flagged": record["flagged"]}


def w1_identity_assets():
    path = ROOT / "artifacts" / "w1_refit_identity.json"
    if not path.is_file():
        return {"status": "not checked"}
    record = json.loads(path.read_text(encoding="utf-8"))
    return {key: record[key] for key in ("n_cases", "max_abs_probability_difference",
                                         "flag_disagreements", "identical_within_tolerance")}


def coding_assets():
    """Copy aggregate qualitative tables once the coding has been reconciled.

    `agreement_study` exists only if independent double-coding was done; without it the status
    says that agreement was not measured.
    """
    folder = ROOT / "data" / "human_study" / "coding"
    required = ("theme_summary_study", "theme_by_group_study", "intervention_flags_by_group_study")
    found = {}
    for name in required + ("agreement_study",):
        path = folder / f"{name}.csv"
        if path.is_file():
            table = pd.read_csv(path)
            if {"participant_id", "text", "coder", "case_id"} & set(table.columns):
                raise ValueError(f"{name}.csv is not aggregate-only")
            table.to_csv(TABLE_OUT / f"human_study_{name.replace('_study', '')}.csv",
                         index=False, float_format="%.4f")
            found[name] = True
    if not any(name in found for name in required):
        return {"status": "pending"}
    if not all(name in found for name in required):
        return {"status": "partial"}
    if "agreement_study" in found:
        return {"status": "completed", "inter_coder_agreement": "measured"}
    return {"status": "completed_single_pass", "inter_coder_agreement": "not measured",
            "note": "one coding pass; the planned independent second coding of 20% was not done"}


def main():
    TABLE_OUT.mkdir(parents=True, exist_ok=True)
    metrics = model_assets()
    explanation = explanation_assets()
    fairness_assets()
    human = human_assets()
    flow_assets()
    sensitivity = sensitivity_assets()
    demo = demo_card_assets()
    w1_identity = w1_identity_assets()
    coding = coding_assets()
    tabicl = metrics.loc[metrics["model"] == "tabicl"].iloc[0]
    numbers = {
        "binary_cohort": 3630, "train": 2541, "validation": 544, "test": 545,
        "final_test": {name: float(tabicl[name]) for name in
                       ("roc_auc", "brier_score", "dropout_recall", "dropout_precision", "flag_rate")},
        "explanation_audit_cases": explanation["n_cases"],
        "human_study": human,
        "qualitative_coding": coding,
        "enrolled_sensitivity": sensitivity,
        "demo_card": demo,
        "w1_refit_vs_frozen_validation": w1_identity,
        "scope_notes": [
            "The final test was read from saved outputs and was not rerun.",
            "W1 is a validation-only supplementary audit of a refit with frozen settings; "
            "its validation predictions match the frozen model (see w1_refit_vs_frozen_validation).",
            "The Enrolled sensitivity is exploratory and was not used for model selection.",
            "Human-study comparisons measure flag comprehension, not causal intervention benefit.",
        ],
    }
    (TABLE_OUT / "project_numbers.json").write_text(json.dumps(numbers, indent=2), encoding="utf-8")
    outputs = sorted(path for path in TABLE_OUT.glob("*") if path.name != "manifest.json")
    outputs += sorted(FIGURE_OUT.glob("*.png"))
    manifest = {
        "builder": "scripts/build_report_assets.py",
        "final_test_rerun": False,
        "files_sha256": {str(path.relative_to(ROOT).as_posix()): file_hash(path) for path in outputs},
    }
    (TABLE_OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Report assets written to {TABLE_OUT.relative_to(ROOT)} and {FIGURE_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
