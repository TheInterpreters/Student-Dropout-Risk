"""Scan private transformed responses for common identifier patterns; emit counts only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import pandas as pd

FIELDS = ("rationale_freetext", "intervention_freetext", "missing_info_freetext")
PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "url": re.compile(r"https?://|www\.", re.I),
    "phone_like": re.compile(r"(?<!\d)(?:\+?\d[\s().-]*){8,}(?!\d)"),
    "self_identification_phrase": re.compile(r"\b(?:my name is|i am called|contact me)\b", re.I),
}


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit(path):
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = [field for field in FIELDS if field not in frame]
    if missing:
        raise ValueError("missing free-text fields: " + ", ".join(missing))
    combined = frame[list(FIELDS)].agg("\n".join, axis=1)
    matches = {name: int(combined.map(lambda value: bool(pattern.search(value))).sum())
               for name, pattern in PATTERNS.items()}
    blank_cells = int((frame[list(FIELDS)] == "").to_numpy().sum())
    return {
        "status": "pass" if not any(matches.values()) and blank_cells == 0 else "manual_review_required",
        "participants": int(frame["participant_id"].nunique()), "case_rows": int(len(frame)),
        "free_text_cells": int(len(frame) * len(FIELDS)), "blank_free_text_cells": blank_cells,
        "pattern_match_rows": matches,
        "input_sha256": file_hash(path),
        "limitation": "Pattern screening cannot prove that free text contains no identifying information; authorized manual review is still required before quotation or release.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("responses")
    parser.add_argument("--out", default="artifacts/human_study_privacy_audit.json")
    args = parser.parse_args(argv)
    result = audit(args.responses)
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
