"""W5.1: static decision-support demo card from ONE validation case (never a test/study case).

Uses the saved final model bundle (no refitting, no test-split access, no final-test rerun).
The card shows what an adviser-facing screen could look like: the student profile, a clearly
labelled model estimate, the five largest grouped SHAP contributions and plain limitations.
It deliberately shows no recourse/"what to change" advice (constrained recourse is not causal).

Selection rule (deterministic, label-free): among validation cases flagged by the top-20%
capacity policy, excluding the study practice case (validation position 0), take the case whose
predicted probability is the median of that flagged set (ties: lowest source_row_id).

Usage (from the repo root, in .venv-core):
    python scripts/build_demo_card.py
Outputs (aggregate/public UCI data only, safe to commit):
    figures/demo_card/demo_card_validation.png
    figures/demo_card/demo_card_validation.json
"""
from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "forms"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from forms import case_pack as cp  # noqa: E402
from forms import labels as lb  # noqa: E402
from src.evaluation import development_frames, load_protocol  # noqa: E402
from src.explanations import (  # noqa: E402
    aggregate_shap_by_group, permutation_shap_values, semantic_feature_groups,
)
from src.freeze import file_hash  # noqa: E402
from src.modeling import capacity_predictions, prepare_tfm_frame  # noqa: E402

PRACTICE_POSITION = 0  # validation.iloc[0] is the study practice case (scripts/export_study_cases.py)
MORE_COLOR = "#D55E00"
LESS_COLOR = "#0072B2"
LIMITATIONS = [
    "This is a model estimate for adviser review, not a decision and not a diagnosis.",
    "The flag means 'in the top 20% of estimated risk for this cohort' (outreach capacity), "
    "not a fixed probability cut-off.",
    "Bars show how the model's estimate moved (grouped SHAP); they are associations, "
    "not causes, and do not say what the student should change.",
    "SHAP rankings vary with random seed and background sample (see the W1 stability audit); "
    "read the top bars as approximate.",
    "Trained and checked on one Portuguese higher-education dataset (UCI); not validated "
    "for any other institution.",
]


def load_bundle():
    import joblib
    lock = json.loads((ROOT / "artifacts" / "final_test.lock").read_text(encoding="utf-8"))
    if lock.get("status") != "completed":
        raise ValueError("demo card requires the completed final-test lock (saved model)")
    path = ROOT / "data" / "final_evaluation" / "selected_model.joblib"
    if file_hash(path) != lock.get("model_bundle_sha256"):
        raise ValueError("saved model bundle does not match the final-test lock")
    return joblib.load(path), lock


def choose_case(probability, flags, source_ids):
    candidates = [i for i in np.flatnonzero(flags == 1) if i != PRACTICE_POSITION]
    if not candidates:
        raise ValueError("no flagged validation case available")
    ordered = sorted(candidates, key=lambda i: (probability[i], source_ids[i]))
    return int(ordered[(len(ordered) - 1) // 2])


def profile_lines(raw_row):
    lines = []
    for heading, fields in lb.GROUPS:
        lines.append((heading, None))
        for field, label, kind in fields:
            lines.append((label, lb.format_value(kind, field, raw_row[field])))
    return lines


def render(card, destination):
    fig = plt.figure(figsize=(13.5, 8.6))
    fig.suptitle("Student support early-warning: example adviser card (validation student, "
                 "not a study case)", fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.985)

    # Left: profile
    ax = fig.add_axes([0.02, 0.03, 0.38, 0.90])
    ax.axis("off")
    ax.text(0, 1, "Student profile (information available after the first semester)",
            fontsize=10.5, fontweight="bold", va="top", transform=ax.transAxes)
    y, step = 0.955, 0.0225
    for label, value in card["profile"]:
        if value is None:
            y -= 0.006
            ax.text(0, y, label, fontsize=9, fontweight="bold", color="#333333", va="top",
                    transform=ax.transAxes)
        else:
            ax.text(0.02, y, f"{label}:", fontsize=8.3, va="top", transform=ax.transAxes)
            ax.text(0.52, y, textwrap.shorten(value, 44), fontsize=8.3, va="top",
                    transform=ax.transAxes)
        y -= step

    # Top right: model estimate
    ax = fig.add_axes([0.44, 0.70, 0.54, 0.22])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, facecolor="#F4F4F4",
                               edgecolor="#999999"))
    status = ("FLAGGED for adviser review (in this cohort's top 20% of estimated risk)"
              if card["flagged"] else "Not flagged (outside this cohort's top 20% of estimated risk)")
    ax.text(0.03, 0.80, "Model estimate (TabICL, frozen final model)", fontsize=10.5,
            fontweight="bold", transform=ax.transAxes)
    ax.text(0.03, 0.52, f"Estimated dropout probability: {card['predicted_probability']:.3f}",
            fontsize=15, transform=ax.transAxes)
    ax.text(0.62, 0.53, "(a model score, not a certainty)", fontsize=9, color="#444444",
            transform=ax.transAxes)
    ax.text(0.03, 0.30, status, fontsize=10.5, color=MORE_COLOR if card["flagged"] else "#333333",
            fontweight="bold", transform=ax.transAxes)
    ax.text(0.03, 0.10, f"Cohort rank {card['cohort_rank']} of {card['cohort_size']} validation "
            f"students; {card['cohort_flagged']} flagged at 20% capacity.",
            fontsize=9, color="#444444", transform=ax.transAxes)

    # Middle right: contributions
    ax = fig.add_axes([0.62, 0.33, 0.35, 0.31])
    bars = list(reversed(card["contributions"]))
    values = [b["value"] for b in bars]
    names = ["\n".join(textwrap.wrap(b["label"], 30)) for b in bars]
    ax.barh(range(len(bars)), values, color=[MORE_COLOR if v > 0 else LESS_COLOR for v in values])
    ax.set_yticks(range(len(bars)), names, fontsize=8.5)
    ax.axvline(0, color="#333333", lw=0.8)
    limit = max(abs(v) for v in values) * 1.35
    ax.set_xlim(-limit, limit)
    for i, v in enumerate(values):
        ax.text(v + (0.01 * limit if v >= 0 else -0.01 * limit), i, f"{v:+.3f}",
                va="center", ha="left" if v >= 0 else "right", fontsize=8)
    ax.set_xlabel("Change in estimated dropout probability vs. a reference group of\n"
                  "25 training students (grouped SHAP)", fontsize=8.5)
    ax.set_title("Five factors that moved the estimate most\n"
                 "◄ lowered the estimate      raised the estimate ►", fontsize=9.5)
    ax.grid(axis="x", alpha=0.25)

    # Bottom right: limitations
    ax = fig.add_axes([0.44, 0.02, 0.54, 0.22])
    ax.axis("off")
    ax.text(0, 0.97, "Read before acting", fontsize=10.5, fontweight="bold", va="top",
            transform=ax.transAxes)
    text = "\n".join("• " + "\n   ".join(textwrap.wrap(item, 95)) for item in LIMITATIONS)
    ax.text(0, 0.82, text, fontsize=8.3, va="top", transform=ax.transAxes, linespacing=1.35)

    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=200)
    plt.close(fig)


def main(argv=None):
    import csv
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=str(ROOT / "figures" / "demo_card"))
    args = parser.parse_args(argv)

    bundle, lock = load_bundle()
    train, validation, columns = development_frames("validation")
    if list(columns) != bundle["columns"]:
        raise ValueError("validation features do not match the saved model")
    model = bundle["model"]
    probability = model.predict_proba(prepare_tfm_frame(validation, columns))[:, 1]
    flags, _ = capacity_predictions(probability)
    source_ids = validation["source_row_id"].to_numpy(int)
    position = choose_case(probability, flags, source_ids)
    source_id = int(source_ids[position])

    study = ROOT / "data" / "study_cases" / "private_lookup_study.json"
    if study.exists():
        used = {int(v["source_row_id"]) for v in json.loads(study.read_text(encoding="utf-8")).values()}
        if source_id in used:
            raise ValueError("chosen demo case is a study case; refusing")

    protocol = load_protocol()
    background = prepare_tfm_frame(train, columns).sample(n=25, random_state=42)
    frame = prepare_tfm_frame(validation.iloc[[position]], columns)
    explanation = permutation_shap_values(model.predict_proba, background, frame,
                                          max_evals=protocol["shap"]["max_evals"], seed=42)
    groups = aggregate_shap_by_group(explanation.values[0], columns,
                                     semantic_feature_groups(columns)).head(5)
    bar_labels = cp.bar_labels()
    contributions = [{"bar_id": r.feature_group, "label": bar_labels[r.feature_group],
                      "value": float(r.signed_shap)} for r in groups.itertuples()]

    with open(ROOT / "eda_uci_data" / "data" / "dropout_data.csv", newline="", encoding="utf-8") as f:
        raw = [{k.strip(): v.strip() for k, v in r.items()} for r in csv.DictReader(f)]
    rank = int(np.sum(probability > probability[position])) + 1
    card = {
        "split": "validation",
        "source_row_id": source_id,
        "validation_position": position,
        "selection_rule": "median predicted probability among flagged validation cases, "
                          "excluding the study practice case",
        "predicted_probability": float(probability[position]),
        "flagged": bool(flags[position]),
        "cohort_rank": rank,
        "cohort_size": int(len(probability)),
        "cohort_flagged": int(flags.sum()),
        "contributions": contributions,
        "profile": profile_lines(raw[source_id]),
        "model_bundle_sha256": lock["model_bundle_sha256"],
        "shap_settings": {"background_rows": 25, "background_seed": 42,
                          "max_evals": protocol["shap"]["max_evals"], "seed": 42},
        "test_split_accessed": False,
        "recourse_shown": False,
    }
    out = Path(args.out)
    render(card, out / "demo_card_validation.png")
    (out / "demo_card_validation.json").write_text(json.dumps(card, indent=2), encoding="utf-8")
    print(f"Demo card: validation row {source_id}, p={card['predicted_probability']:.3f}, "
          f"flagged={card['flagged']} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
