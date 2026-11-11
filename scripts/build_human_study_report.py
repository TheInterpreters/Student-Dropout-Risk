"""Build privacy-safe, report-ready quantitative human-study tables and figures."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


GROUP_LABELS = {"A": "Profiles only", "B": "Profiles + explanations"}
METRICS = ("accuracy", "mean_confidence", "self_reported_minutes")


def read_csv(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def mean_interval(values, rng, resamples=10_000):
    values = np.asarray(values, dtype=float)
    draws = values[rng.integers(0, len(values), size=(resamples, len(values)))].mean(axis=1)
    return np.quantile(draws, [0.025, 0.975])


def group_difference(left, right, rng, resamples=10_000):
    """Return B-minus-A effect, stratified bootstrap CI, permutation p, and Hedges g."""
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    observed = float(right.mean() - left.mean())
    left_draws = left[rng.integers(0, len(left), size=(resamples, len(left)))].mean(axis=1)
    right_draws = right[rng.integers(0, len(right), size=(resamples, len(right)))].mean(axis=1)
    low, high = np.quantile(right_draws - left_draws, [0.025, 0.975])
    combined = np.concatenate([left, right])
    permutation = []
    for _ in range(resamples):
        shuffled = rng.permutation(combined)
        permutation.append(shuffled[len(left):].mean() - shuffled[:len(left)].mean())
    p_value = (1 + np.sum(np.abs(permutation) >= abs(observed))) / (resamples + 1)
    pooled_numerator = (len(left) - 1) * left.var(ddof=1) + (len(right) - 1) * right.var(ddof=1)
    pooled_sd = np.sqrt(pooled_numerator / (len(left) + len(right) - 2))
    correction = 1 - 3 / (4 * (len(left) + len(right)) - 9)
    hedges_g = observed / pooled_sd * correction if pooled_sd else 0.0
    return observed, float(low), float(high), float(p_value), float(hedges_g)


def wilson_interval(successes, total):
    if not total:
        return np.nan, np.nan
    z = 1.959963984540054
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    half = z * np.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return centre - half, centre + half


def build_tables(scored, people, participant_export, lookup, seed=42, resamples=10_000):
    scored = scored.copy()
    people = people.copy()
    participant_export = participant_export.copy()
    for column in ("correct", "confidence"):
        scored[column] = pd.to_numeric(scored[column], errors="raise")
    for column in METRICS:
        people[column] = pd.to_numeric(people[column], errors="raise")
    if len(people) != 50 or set(people["group"]) != {"A", "B"}:
        raise ValueError("report build requires the completed two-group study")
    if people["participant_id"].duplicated().any() or len(scored) != 10 * len(people):
        raise ValueError("participant summaries or scored case rows are duplicated/incomplete")
    details = participant_export[["participant_id", "variant_id", "role", "chart_check_b1",
                                  "chart_check_b2", "chart_check_ok"]]
    people = people.merge(details, on="participant_id", validate="one_to_one")
    rng = np.random.default_rng(seed)

    group_rows = []
    for group in ("A", "B"):
        sample = people.loc[people["group"] == group]
        for metric in METRICS:
            values = sample[metric].to_numpy(float)
            low, high = mean_interval(values, rng, resamples)
            group_rows.append({
                "group": group, "group_label": GROUP_LABELS[group], "metric": metric,
                "n": len(values), "mean": values.mean(), "sd": values.std(ddof=1),
                "median": np.median(values), "q1": np.quantile(values, 0.25),
                "q3": np.quantile(values, 0.75), "mean_ci_lower_95": low,
                "mean_ci_upper_95": high,
            })
    group_summary = pd.DataFrame(group_rows)

    comparison_rows = []
    for metric in METRICS:
        left = people.loc[people["group"] == "A", metric]
        right = people.loc[people["group"] == "B", metric]
        difference, low, high, p_value, hedges_g = group_difference(left, right, rng, resamples)
        comparison_rows.append({
            "comparison": "Profiles + explanations minus profiles only", "metric": metric,
            "difference": difference, "ci_lower_95": low, "ci_upper_95": high,
            "exploratory_permutation_p_two_sided": p_value, "hedges_g": hedges_g,
            "bootstrap_resamples": resamples, "permutation_resamples": resamples, "seed": seed,
        })
    comparisons = pd.DataFrame(comparison_rows)

    flag_lookup = {case_id: int(values["model_flag"]) for case_id, values in lookup.items()}
    scored["model_flag"] = scored["case_id"].map(flag_lookup)
    case_rows = []
    for (case_id, group), sample in scored.groupby(["case_id", "group"], sort=True):
        case_rows.append({
            "case_id": case_id, "group": group, "group_label": GROUP_LABELS[group],
            "model_flag": int(sample["model_flag"].iloc[0]), "n": len(sample),
            "accuracy": sample["correct"].mean(), "mean_confidence": sample["confidence"].mean(),
        })
    case_summary = pd.DataFrame(case_rows)

    leave_one_out_rows = []
    for omitted_case in sorted(scored["case_id"].unique()):
        reduced = (scored.loc[scored["case_id"] != omitted_case]
                   .groupby(["participant_id", "group"], as_index=False)["correct"].mean())
        left = reduced.loc[reduced["group"] == "A", "correct"]
        right = reduced.loc[reduced["group"] == "B", "correct"]
        difference, low, high, p_value, hedges_g = group_difference(left, right, rng, resamples)
        leave_one_out_rows.append({
            "omitted_case": omitted_case, "cases_per_participant": 9,
            "profiles_only_mean_accuracy": left.mean(),
            "profiles_plus_explanations_mean_accuracy": right.mean(),
            "difference_explanations_minus_profiles": difference,
            "ci_lower_95": low, "ci_upper_95": high,
            "exploratory_permutation_p_two_sided": p_value, "hedges_g": hedges_g,
            "bootstrap_resamples": resamples, "permutation_resamples": resamples, "seed": seed,
        })
    leave_one_case_out = pd.DataFrame(leave_one_out_rows)

    flag_rows = []
    for (group, model_flag), sample in scored.groupby(["group", "model_flag"], sort=True):
        flag_rows.append({
            "group": group, "group_label": GROUP_LABELS[group], "model_flag": int(model_flag),
            "n_responses": len(sample), "accuracy": sample["correct"].mean(),
            "mean_confidence": sample["confidence"].mean(),
        })
    flag_summary = pd.DataFrame(flag_rows)

    role_summary = people.groupby(["group", "role"], as_index=False).agg(
        n=("participant_id", "size"), mean_accuracy=("accuracy", "mean"),
        mean_confidence=("mean_confidence", "mean"), mean_minutes=("self_reported_minutes", "mean"))
    variant_summary = people.groupby(["group", "variant_id"], as_index=False).agg(
        n=("participant_id", "size"), mean_accuracy=("accuracy", "mean"),
        mean_confidence=("mean_confidence", "mean"), mean_minutes=("self_reported_minutes", "mean"))

    practice_rows = []
    group_b = people.loc[people["group"] == "B"]
    for check, correct in (("bar_direction", "More worried about this student"),
                           ("bar_length", "A bigger effect"), ("both_correct", "1")):
        column = {"bar_direction": "chart_check_b1", "bar_length": "chart_check_b2",
                  "both_correct": "chart_check_ok"}[check]
        successes = int((group_b[column] == correct).sum())
        low, high = wilson_interval(successes, len(group_b))
        practice_rows.append({"check": check, "n": len(group_b), "n_correct": successes,
                              "proportion_correct": successes / len(group_b),
                              "ci_lower_95": low, "ci_upper_95": high})
    practice_checks = pd.DataFrame(practice_rows)

    return {
        "group_summary": group_summary, "group_comparisons": comparisons,
        "case_summary": case_summary, "leave_one_case_out": leave_one_case_out,
        "flag_summary": flag_summary,
        "role_summary": role_summary, "variant_summary": variant_summary,
        "practice_checks": practice_checks,
    }, people, scored


def build_figures(people, scored, tables, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    colours = {"A": "#4C78A8", "B": "#F58518"}

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    rng = np.random.default_rng(42)
    for position, group in enumerate(("A", "B"), 1):
        values = people.loc[people["group"] == group, "accuracy"].to_numpy(float)
        ax.boxplot(values, positions=[position], widths=0.45, patch_artist=True,
                   boxprops={"facecolor": colours[group], "alpha": 0.25}, medianprops={"color": "black"})
        ax.scatter(position + rng.uniform(-0.10, 0.10, len(values)), values,
                   color=colours[group], alpha=0.8, s=28)
    ax.set(xticks=[1, 2], xticklabels=[GROUP_LABELS["A"], GROUP_LABELS["B"]],
           ylabel="Participant accuracy (10 cases)", ylim=(0, 1.04))
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(destination / "human_accuracy_by_group.png", dpi=200)
    plt.close(fig)

    case = tables["case_summary"]
    pivot = case.pivot(index="case_id", columns="group", values="accuracy")
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    x = np.arange(len(pivot))
    ax.bar(x - 0.2, pivot["A"], width=0.4, label=GROUP_LABELS["A"], color=colours["A"])
    ax.bar(x + 0.2, pivot["B"], width=0.4, label=GROUP_LABELS["B"], color=colours["B"])
    ax.set(xticks=x, xticklabels=pivot.index, ylabel="Accuracy", xlabel="Study case", ylim=(0, 1.04))
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(destination / "human_accuracy_by_case.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    for group in ("A", "B"):
        sample = people.loc[people["group"] == group]
        ax.scatter(sample["mean_confidence"], sample["accuracy"], label=GROUP_LABELS[group],
                   color=colours[group], alpha=0.8, s=34)
    ax.set(xlabel="Mean confidence (1-5)", ylabel="Participant accuracy", ylim=(0, 1.04))
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(destination / "human_confidence_vs_accuracy.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    bins = np.arange(5, 66, 5)
    for group in ("A", "B"):
        ax.hist(people.loc[people["group"] == group, "self_reported_minutes"].astype(float),
                bins=bins, alpha=0.55, label=GROUP_LABELS[group], color=colours[group])
    ax.set(xlabel="Self-reported completion time (minutes)", ylabel="Participants")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(destination / "human_completion_time.png", dpi=200)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scored", required=True)
    parser.add_argument("--people", required=True)
    parser.add_argument("--participants", required=True)
    parser.add_argument("--private", required=True)
    parser.add_argument("--tables", default="tables/human_study")
    parser.add_argument("--figures", default="figures/human_study")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resamples", type=int, default=10_000)
    args = parser.parse_args(argv)
    with open(args.private, encoding="utf-8") as stream:
        lookup = json.load(stream)
    tables, people, scored = build_tables(
        read_csv(args.scored), read_csv(args.people), read_csv(args.participants), lookup,
        seed=args.seed, resamples=args.resamples)
    table_dir = Path(args.tables)
    table_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(table_dir / f"{name}.csv", index=False)
    build_figures(people, scored, tables, args.figures)
    summary = {
        "study_status": "completed", "included_participants": int(len(people)),
        "groups": {group: int((people["group"] == group).sum()) for group in ("A", "B")},
        "primary_unit": "participant accuracy across 10 cases",
        "primary_comparison": tables["group_comparisons"].iloc[0].to_dict(),
        "interpretation": "Between-group estimates are exploratory; the study measures comprehension of model flags, not intervention benefit or deployment validity.",
    }
    (table_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    outputs = sorted(path for path in table_dir.glob("*") if path.name != "manifest.json")
    outputs += sorted(Path(args.figures).glob("*.png"))
    manifest = {
        "seed": args.seed, "resamples": args.resamples,
        "private_inputs_sha256": {Path(path).name: file_hash(path) for path in
                                  (args.scored, args.people, args.participants, args.private)},
        "aggregate_outputs_sha256": {str(path.as_posix()): file_hash(path) for path in outputs},
        "contains_free_text": False,
    }
    (table_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Report-ready human-study assets: {len(people)} participants, {len(scored)} case responses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
