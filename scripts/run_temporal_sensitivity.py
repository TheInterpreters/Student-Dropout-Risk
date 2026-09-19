"""Compare admission-time and first-semester windows on validation only."""

from __future__ import annotations

from pathlib import Path
import sys
from time import perf_counter

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.modeling import (  # noqa: E402
    add_first_semester_features,
    build_baselines,
    build_tfm,
    capacity_predictions,
    evaluate_predictions,
    feature_columns,
    fit_and_evaluate,
    load_primary_data,
    make_splits,
    prepare_tfm_frame,
    select_split,
)


def main() -> None:
    frame = add_first_semester_features(load_primary_data())
    splits = make_splits(frame)
    train = select_split(frame, splits.train_ids)
    validation = select_split(frame, splits.validation_ids)
    rows: list[dict[str, object]] = []
    for window in ("enrollment", "first_semester"):
        columns = feature_columns(frame, window)
        for model_name, model in build_baselines(columns).items():
            metrics = fit_and_evaluate(model, train, validation, columns)
            rows.append({"window": window, "model": model_name, **metrics})

        x_train = prepare_tfm_frame(train, columns)
        x_validation = prepare_tfm_frame(validation, columns)
        model = build_tfm("tabicl", columns, n_estimators=4)
        start = perf_counter()
        model.fit(x_train, train["target"])
        fit_seconds = perf_counter() - start
        probability = model.predict_proba(x_validation)[:, 1]
        predictions, threshold = capacity_predictions(probability, capacity=0.20)
        metrics = evaluate_predictions(validation["target"], predictions, probability)
        rows.append(
            {
                "window": window,
                "model": "tabicl",
                **metrics,
                "threshold": threshold,
                "fit_seconds": fit_seconds,
            }
        )

    result = pd.DataFrame(rows)
    output = ROOT / "tables" / "temporal_window_validation_metrics.csv"
    result.to_csv(output, index=False)
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
