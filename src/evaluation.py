"""Shared frozen-model preparation and descriptive evaluation outputs."""
from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from src.auditing import proxy_association_table, subgroup_diagnostics
from src.modeling import (
    ROOT, EBM_NOMINAL_COLUMNS, add_first_semester_features, build_baselines, build_ebm,
    build_tfm, capacity_predictions, evaluate_predictions, feature_columns,
    load_primary_data, prepare_ebm_frame, prepare_tfm_frame,
)


def load_protocol():
    return json.loads((ROOT / "config" / "evaluation_protocol.json").read_text(encoding="utf-8"))


def development_frames(evaluation_split):
    if evaluation_split not in ("validation", "test"):
        raise ValueError("evaluation split must be validation or test")
    frame = add_first_semester_features(load_primary_data())
    split = pd.read_csv(ROOT / "artifacts" / "split_ids.csv")
    if split["source_row_id"].duplicated().any() or set(split["source_row_id"]) != set(frame["source_row_id"]):
        raise ValueError("saved split IDs are duplicated or do not cover the binary dataset")
    if set(split["split"]) != {"train", "validation", "test"}:
        raise ValueError("saved split names are invalid")
    merged = frame.merge(split, on="source_row_id", validate="one_to_one")
    train = merged.loc[merged["split"] == "train"].drop(columns="split").sort_values("source_row_id").reset_index(drop=True)
    evaluation = merged.loc[merged["split"] == evaluation_split].drop(columns="split").sort_values("source_row_id").reset_index(drop=True)
    columns = feature_columns(frame, "first_semester")
    return train, evaluation, columns


def selected_model(train, columns):
    protocol = load_protocol()
    model = build_tfm(protocol["model"]["name"], columns,
                      n_estimators=protocol["model"]["n_estimators"])
    model.fit(prepare_tfm_frame(train, columns), train["target"])
    return model


def reliability_table(truth, probabilities):
    truth = np.asarray(truth, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    bins = np.minimum((probabilities * 10).astype(int), 9)
    return pd.DataFrame([
        {"bin": i, "lower": i / 10, "upper": (i + 1) / 10, "n": int((bins == i).sum()),
         "mean_probability": float(probabilities[bins == i].mean()) if (bins == i).any() else np.nan,
         "outcome_rate": float(truth[bins == i].mean()) if (bins == i).any() else np.nan}
        for i in range(10)
    ])


def protected_attributes(frame):
    result = {name: frame[name] for name in (
        "gender", "nacionality", "international", "displaced", "educational_special_needs")}
    result["age_band"] = pd.cut(frame["age_at_enrollment"], [0, 20, 25, 35, float("inf")],
                               labels=["<=20", "21-25", "26-35", "36+"])
    return result


def fairness_outputs(frame, probabilities, predictions, columns):
    protected = protected_attributes(frame)
    protocol = load_protocol()
    groups = []
    for name, values in protected.items():
        report = subgroup_diagnostics(frame["target"], probabilities, values, predictions,
                                      min_group_size=protocol["fairness"]["minimum_group_size"])
        report.insert(0, "attribute", name)
        groups.append(report)
    excluded = set(protected) | {"age_at_enrollment"}
    proxy = proxy_association_table(frame, protected, [c for c in columns if c not in excluded],
                                    EBM_NOMINAL_COLUMNS)
    return pd.concat(groups, ignore_index=True), proxy


def evaluate_frozen_models(train, evaluation, columns, checkpoint=None):
    protocol = load_protocol()
    models = build_baselines(columns)
    models["explainable_boosting_main_effects"] = build_ebm(columns)
    models["tabicl"] = build_tfm("tabicl", columns, protocol["model"]["n_estimators"])
    if checkpoint is not None:
        models["tabicl"].set_params(model_path=str(checkpoint), allow_auto_download=False)
    metrics, predictions, fitted = [], {}, {}
    for name, model in models.items():
        prepare = prepare_tfm_frame if name == "tabicl" else (
            prepare_ebm_frame if name == "explainable_boosting_main_effects" else lambda f, c: f[c])
        start = perf_counter()
        model.fit(prepare(train, columns), train["target"])
        fit_seconds = perf_counter() - start
        start = perf_counter()
        probability = np.asarray(model.predict_proba(prepare(evaluation, columns)))[:, 1]
        prediction_seconds = perf_counter() - start
        if not np.isfinite(probability).all() or ((probability < 0) | (probability > 1)).any():
            raise ValueError(name + ": invalid prediction probabilities")
        flags, boundary = capacity_predictions(probability, protocol["operating_policy"]["maximum_flag_fraction"])
        result = evaluate_predictions(evaluation["target"], flags, probability)
        result["confusion_matrix"] = json.dumps(result["confusion_matrix"])
        metrics.append({"model": name, **result, "capacity_boundary": boundary,
                        "fit_seconds": fit_seconds, "prediction_seconds": prediction_seconds})
        predictions[name] = probability
        fitted[name] = model
    return pd.DataFrame(metrics), predictions, fitted


def save_reliability_figure(table, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], "--", color="gray")
    ax.plot(table["mean_probability"], table["outcome_rate"], "o-")
    ax.set(xlabel="Mean estimated model risk", ylabel="Observed dropout proportion",
           xlim=(0, 1), ylim=(0, 1))
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
