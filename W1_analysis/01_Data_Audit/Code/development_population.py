"""Exact development population: every saved train/validation ID, never test."""
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_COUNTS = {"train": 2541, "validation": 544}
EXPECTED_TOTAL = sum(EXPECTED_COUNTS.values())


def validate_population(train, validation, columns, splits):
    if list(splits.columns) != ["source_row_id", "split"]:
        raise ValueError("Unexpected saved split-map columns")
    if splits.source_row_id.duplicated().any() or splits.source_row_id.isna().any():
        raise ValueError("Missing or duplicated saved split IDs")
    if set(splits.split) != {"train", "validation", "test"}:
        raise ValueError("Unexpected saved split names")
    if {"source_row_id", "target", "split"}.intersection(columns):
        raise ValueError("Identity/target/split leaked into model features")
    if any(c.startswith("curricular_units_2nd_sem") for c in columns):
        raise ValueError("Second-semester feature leakage")
    frames = {"train": train, "validation": validation}
    all_ids = set()
    for name, frame in frames.items():
        ids = frame.source_row_id.tolist()
        expected = set(splits.loc[splits.split.eq(name), "source_row_id"])
        if len(frame) != EXPECTED_COUNTS[name] or len(set(ids)) != len(ids) or set(ids) != expected:
            raise ValueError(f"{name}: must include every original saved ID exactly once")
        if all_ids.intersection(ids):
            raise ValueError("Development partitions overlap")
        all_ids.update(ids)
        if frame.target.isna().any() or not set(frame.target).issubset({0, 1}):
            raise ValueError("Invalid actual binary outcomes")
        if not set(columns).issubset(frame.columns):
            raise ValueError("Missing model features")
    if all_ids.intersection(splits.loc[splits.split.eq("test"), "source_row_id"]):
        raise ValueError("Locked test ID entered development population")
    return frames


def load_population(root=ROOT):
    root = Path(root).resolve()
    if root != ROOT:
        raise ValueError("Place this package directly inside the original project root")
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from src.evaluation import development_frames
    train, validation, columns = development_frames("validation")
    splits = pd.read_csv(root / "artifacts" / "split_ids.csv")
    return validate_population(train, validation, columns, splits), columns
