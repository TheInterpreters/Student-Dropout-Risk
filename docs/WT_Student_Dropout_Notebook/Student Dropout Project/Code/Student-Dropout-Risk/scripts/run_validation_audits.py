"""Generate validation-only global explanation and fairness audit tables."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.auditing import proxy_association_table, subgroup_diagnostics  # noqa: E402
from src.explanations import (  # noqa: E402
    accumulated_local_effect,
    grouped_permutation_importance,
    semantic_feature_groups,
)
from src.modeling import (  # noqa: E402
    add_first_semester_features,
    build_tfm,
    EBM_NOMINAL_COLUMNS,
    capacity_predictions,
    feature_columns,
    load_primary_data,
    make_splits,
    prepare_tfm_frame,
    select_split,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reuse-importance",
        action="store_true",
        help="Reuse an existing validation PFI table while regenerating ALE/fairness.",
    )
    args = parser.parse_args()
    frame = add_first_semester_features(load_primary_data())
    columns = feature_columns(frame, "first_semester")
    splits = make_splits(frame)
    train = select_split(frame, splits.train_ids)
    validation = select_split(frame, splits.validation_ids)
    x_train = prepare_tfm_frame(train, columns)
    x_validation = prepare_tfm_frame(validation, columns)
    model = build_tfm("tabicl", columns, n_estimators=4)
    model.fit(x_train, train["target"])
    probability = model.predict_proba(x_validation)[:, 1]
    capacity_labels, boundary = capacity_predictions(probability, capacity=0.20)

    groups = semantic_feature_groups(columns)
    audit_index = validation.sample(n=100, random_state=42).index
    x_audit = x_validation.loc[audit_index].reset_index(drop=True)
    y_audit = validation.loc[audit_index, "target"].reset_index(drop=True)
    table_dir = ROOT / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    importance_path = table_dir / "grouped_permutation_importance_validation.csv"
    if args.reuse_importance and importance_path.exists():
        importance = pd.read_csv(importance_path)
    else:
        importance = grouped_permutation_importance(
            model.predict_proba,
            x_audit,
            y_audit,
            groups,
            repeats=5,
            seed=42,
        )
        importance.to_csv(importance_path, index=False)

    numeric_candidates = [
        name
        for name in importance["feature_group"]
        if name in x_validation.columns
        and name not in set(columns).intersection(
            {
                column
                for column in columns
                if isinstance(x_validation[column].dtype, pd.CategoricalDtype)
            }
        )
        and x_validation[name].nunique() > 10
    ][:3]
    ale_tables = [
        accumulated_local_effect(model.predict_proba, x_validation, feature, bins=10)
        for feature in numeric_candidates
    ]
    if ale_tables:
        pd.concat(ale_tables, ignore_index=True).to_csv(
            table_dir / "ale_validation.csv", index=False
        )

    fairness_frames = []
    protected = {
        "gender": validation["gender"],
        "nacionality": validation["nacionality"],
        "international": validation["international"],
        "displaced": validation["displaced"],
        "educational_special_needs": validation["educational_special_needs"],
        "age_band": pd.cut(
            validation["age_at_enrollment"],
            bins=[0, 20, 25, 35, float("inf")],
            labels=["<=20", "21-25", "26-35", "36+"],
        ),
    }
    for attribute, values in protected.items():
        report = subgroup_diagnostics(
            validation["target"], probability, values, capacity_labels, min_group_size=30
        )
        if not report.empty:
            report.insert(0, "attribute", attribute)
            fairness_frames.append(report)
    if fairness_frames:
        pd.concat(fairness_frames, ignore_index=True).to_csv(
            table_dir / "subgroup_diagnostics_validation.csv", index=False
        )

    protected_sources = {
        "gender",
        "nacionality",
        "international",
        "displaced",
        "educational_special_needs",
        "age_at_enrollment",
    }
    proxy_features = [column for column in columns if column not in protected_sources]
    proxy_association_table(
        validation,
        protected,
        proxy_features,
        EBM_NOMINAL_COLUMNS,
    ).to_csv(table_dir / "proxy_associations_validation.csv", index=False)

    print(importance.head(10).to_string(index=False))
    print(f"ALE features: {numeric_candidates}")
    print(f"Validation capacity boundary: {boundary:.6f}")


if __name__ == "__main__":
    main()
