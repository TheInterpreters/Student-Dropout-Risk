"""Training-split profile by outcome for the report's exploratory-data table (Table 3).

Uses the training split only (2,541 Dropout/Graduate students); validation and test are not read.
Usage (repo root, .venv-core):  python scripts/build_eda_profile.py
Output: tables/eda/training_profile_by_outcome.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.modeling import load_primary_data  # noqa: E402

OUT = ROOT / "tables" / "eda" / "training_profile_by_outcome.csv"
E = "curricular_units_1st_sem_"


def training_profile(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, group in (("Dropout", frame[frame["target"] == 1]),
                         ("Graduate", frame[frame["target"] == 0])):
        rows.append({
            "outcome": label,
            "students": len(group),
            "units_passed_mean": round(group[E + "approved"].mean(), 1),
            "passed_no_unit_pct": round(100 * (group[E + "approved"] == 0).mean(), 1),
            "no_evaluation_pct": round(100 * (group[E + "evaluations"] == 0).mean(), 1),
            "average_grade_mean": round(group[E + "grade"].mean(), 1),
            "fees_up_to_date_pct": round(100 * group["tuition_fees_up_to_date"].mean(), 1),
            "debtor_pct": round(100 * group["debtor"].mean(), 1),
            "scholarship_pct": round(100 * group["scholarship_holder"].mean(), 1),
            "age_median": float(group["age_at_enrollment"].median()),
            "female_gender0_pct": round(100 * (group["gender"] == 0).mean(), 1),
        })
    return pd.DataFrame(rows)


def main():
    frame = load_primary_data()
    split = pd.read_csv(ROOT / "artifacts" / "split_ids.csv")
    train_ids = set(split.loc[split["split"] == "train", "source_row_id"])
    train = frame[frame["source_row_id"].isin(train_ids)]
    if len(train) != 2541:
        raise ValueError(f"expected 2,541 training students, found {len(train)}")
    table = training_profile(train)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT, index=False)
    print(table.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
