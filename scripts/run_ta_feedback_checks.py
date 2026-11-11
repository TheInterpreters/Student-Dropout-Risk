"""TA feedback checks from saved validation evidence (no model run, test split never read).

Answers three TA questions with numbers, using only the saved W1 validation cases
(`W1_analysis/03_Full_Audit/Cases/`) and the validation frame:

1. Who are the 108 flagged students? How do they compare with a simple "passed zero units" rule?
2. What do the explanations say about them (top grouped SHAP reason)?
3. Could the flag be reconstructed by adding up the contribution bars?
4. Eligibility: if students with no first-semester evaluation (who may already have left) are set
   aside, how does the same 20% rule perform on the remaining validation students?

Exploratory, post-hoc and validation-only; not used to select or change the model.
Usage (repo root, .venv-core):  python scripts/run_ta_feedback_checks.py
Outputs: tables/sensitivity/ta_flag_composition.csv, ta_bar_sum.csv, ta_eligibility_subset.csv,
ta_feedback_summary.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation import development_frames  # noqa: E402

CASES = ROOT / "W1_analysis" / "03_Full_Audit" / "Cases"
OUT = ROOT / "tables" / "sensitivity"
E = "curricular_units_1st_sem_"


def load_case_table(cases_folder=CASES):
    rows = []
    for path in sorted(Path(cases_folder).glob("case_*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        everything = case["baseline_group_contributions_all"]
        rows.append({
            "source_row_id": int(case["source_row_id"]),
            "probability": float(case["predicted_probability"]),
            "flagged": int(case["flagged"]),
            "top_reason": case["baseline_top_five_groups"][0],
            "sum_top5_bars": sum(g["signed_shap"] for g in case["baseline_group_contributions"][:5]),
            "sum_all_bars": sum(g["signed_shap"] for g in everything),
        })
    return pd.DataFrame(rows)


def rule_metrics(selected, y):
    selected, y = np.asarray(selected, bool), np.asarray(y, bool)
    return {"n_selected": int(selected.sum()),
            "precision": float(y[selected].mean()) if selected.any() else float("nan"),
            "recall": float((selected & y).sum() / y.sum())}


def top_k_hits(score, flagged, k):
    order = np.argsort(-np.asarray(score), kind="stable")[:k]
    return int(np.asarray(flagged)[order].sum())


def eligibility_subset(df, y, no_eval):
    """Re-apply the top-20% rule within students who sat at least one first-semester evaluation.

    `df` must be in validation record order so that ties break by record order, as in the protocol.
    """
    keep = ~no_eval
    prob, truth = df["probability"].to_numpy()[keep], y[keep]
    k = int(np.floor(0.2 * keep.sum()))
    flag = np.zeros(keep.sum(), bool)
    flag[np.argsort(-prob, kind="stable")[:k]] = True
    tp, fp = int((flag & truth).sum()), int((flag & ~truth).sum())
    fn, tn = int((~flag & truth).sum()), int((~flag & ~truth).sum())
    return {"subset": "at least one first-semester evaluation", "n": int(keep.sum()),
            "n_dropout": int(truth.sum()), "flagged": k, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "recall": round(tp / truth.sum(), 4), "precision": round(tp / k, 4),
            "roc_auc": round(float(roc_auc_score(truth, prob)), 4),
            "excluded_no_evaluation": int(no_eval.sum()),
            "excluded_no_evaluation_dropout": int((no_eval & y).sum())}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    _, validation, _ = development_frames("validation")
    cases = load_case_table()
    df = validation[["source_row_id", "target", E + "evaluations", E + "approved",
                     "tuition_fees_up_to_date"]].merge(cases, on="source_row_id", how="left",
                                                       validate="one_to_one")
    if df["probability"].isna().any():
        raise ValueError("saved W1 cases do not cover the validation split exactly")
    if len(df) != len(validation) or df["target"].isna().any():
        raise ValueError("saved W1 cases do not cover the validation split exactly")
    y = df["target"].astype(int).to_numpy(bool)
    flag = df["flagged"].to_numpy(bool)
    zero_pass = (df[E + "approved"] == 0).to_numpy()
    no_eval = (df[E + "evaluations"] == 0).to_numpy()
    fees_late = (df["tuition_fees_up_to_date"] == 0).to_numpy()
    n_flag = int(flag.sum())

    model = rule_metrics(flag, y)
    rule = rule_metrics(zero_pass, y)
    composition = [
        ("validation_students", len(df)), ("flagged", n_flag), ("flagged_dropout", int((flag & y).sum())),
        ("flagged_no_evaluations", int((flag & no_eval).sum())),
        ("flagged_zero_units_passed", int((flag & zero_pass).sum())),
        ("flagged_with_units_passed", int((flag & ~zero_pass).sum())),
        ("flagged_with_units_passed_fees_unpaid", int((flag & ~zero_pass & fees_late).sum())),
        ("zero_pass_rule_selected", rule["n_selected"]),
        ("zero_pass_rule_precision", round(rule["precision"], 4)),
        ("zero_pass_rule_recall", round(rule["recall"], 4)),
        ("model_precision", round(model["precision"], 4)), ("model_recall", round(model["recall"], 4)),
        ("zero_pass_not_flagged", int((zero_pass & ~flag).sum())),
        ("zero_pass_not_flagged_graduate", int((zero_pass & ~flag & ~y).sum())),
        ("flagged_top_reason_first_semester_progress",
         int(((df["top_reason"] == "first_semester_progress").to_numpy() & flag).sum())),
    ]
    pd.DataFrame(composition, columns=["measure", "value"]).to_csv(
        OUT / "ta_flag_composition.csv", index=False)

    bar_rows = []
    for column, shown in (("sum_all_bars", "all grouped contributions (not shown to participants)"),
                          ("sum_top5_bars", "top five bars (as shown to Group B, without numbers)")):
        score = df[column].to_numpy()
        bar_rows.append({"score": column, "description": shown,
                         "auc_vs_model_flag": round(float(roc_auc_score(flag, score)), 4),
                         "flags_recovered_in_top_108": top_k_hits(score, flag, n_flag),
                         "sign_agrees_with_flag": round(float(((score > 0) == flag).mean()), 4)})
    pd.DataFrame(bar_rows).to_csv(OUT / "ta_bar_sum.csv", index=False)

    eligibility = eligibility_subset(df, y, no_eval)
    pd.DataFrame([eligibility]).to_csv(OUT / "ta_eligibility_subset.csv", index=False)

    summary = {
        "analysis": "TA feedback checks from saved W1 validation cases (exploratory, post-hoc)",
        "test_split_accessed": False, "model_run": False,
        "top_reason_counts_among_flagged": dict(Counter(df.loc[flag, "top_reason"])),
        "composition": dict(composition), "bar_sum": bar_rows, "eligibility_subset": eligibility,
        "note": "Evaluation presence and units passed are proxies; these checks do not establish "
                "eligibility, benefit from outreach, or performance on Enrolled students.",
    }
    (OUT / "ta_feedback_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
