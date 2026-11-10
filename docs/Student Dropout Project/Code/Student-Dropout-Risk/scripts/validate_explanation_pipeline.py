"""Validation-only integration checks for TabICL and model-agnostic SHAP."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.explanations import permutation_shap_values  # noqa: E402
from src.modeling import (  # noqa: E402
    add_first_semester_features,
    build_tfm,
    feature_columns,
    load_primary_data,
    make_splits,
    prepare_tfm_frame,
    select_split,
)


def white_box_check() -> float:
    rng = np.random.default_rng(42)
    columns = [f"x{index}" for index in range(5)]
    background = pd.DataFrame(rng.uniform(-1, 1, size=(100, 5)), columns=columns)
    case = pd.DataFrame([[0.8, -0.7, 0.6, -0.5, 0.4]], columns=columns)
    coefficients = np.array([0.15, -0.10, 0.07, 0.04, -0.02])

    def known_probability(values: pd.DataFrame) -> np.ndarray:
        probability = 0.5 + values.to_numpy(dtype=float) @ coefficients
        return np.column_stack([1 - probability, probability])

    explanation = permutation_shap_values(
        known_probability, background, case, max_evals=501, seed=42
    )
    expected = coefficients * (case.iloc[0].to_numpy() - background.mean().to_numpy())
    correlation = float(spearmanr(np.abs(expected), np.abs(explanation.values[0])).statistic)
    if correlation < 0.9:
        raise AssertionError(f"white-box attribution rank correlation too low: {correlation}")
    return correlation


def main() -> None:
    frame = add_first_semester_features(load_primary_data())
    columns = feature_columns(frame, "first_semester")
    splits = make_splits(frame)
    train = select_split(frame, splits.train_ids)
    validation = select_split(frame, splits.validation_ids)
    x_train = prepare_tfm_frame(train, columns)
    x_validation = prepare_tfm_frame(validation, columns)

    model = build_tfm("tabicl", columns, n_estimators=4)
    model.fit(x_train, train["target"])
    validation_probability = model.predict_proba(x_validation)[:, 1]
    selected = np.array(
        [int(np.argmin(validation_probability)), int(np.argmax(validation_probability))]
    )
    cases = x_validation.iloc[selected].copy()
    background = x_train.sample(n=25, random_state=42).copy()
    expected_probability = model.predict_proba(cases)[:, 1]
    explanation = permutation_shap_values(
        model.predict_proba,
        background,
        cases,
        max_evals=67,
        seed=42,
    )
    reconstructed = np.asarray(explanation.base_values) + np.asarray(explanation.values).sum(axis=1)
    reconstruction_error = float(np.max(np.abs(expected_probability - reconstructed)))
    if reconstruction_error > 1e-5:
        raise AssertionError(f"SHAP local-accuracy error too high: {reconstruction_error}")

    result = {
        "split": "validation",
        "test_labels_accessed": False,
        "model": "tabicl",
        "n_estimators": 4,
        "background_size": len(background),
        "max_evals": 67,
        "integration_cases": selected.tolist(),
        "max_local_accuracy_error": reconstruction_error,
        "white_box_absolute_rank_spearman": white_box_check(),
        "status": "passed",
    }
    output = ROOT / "artifacts" / "explanation_integration.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
