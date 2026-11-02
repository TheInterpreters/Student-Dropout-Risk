"""W5.6: score private response exports and write descriptive participant-level summaries."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from forms import case_pack


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames=None):
    if not rows and not fieldnames:
        raise ValueError("refusing to write an empty results table")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def score_responses(rows, lookup, label):
    problems = case_pack.validate_private(lookup, "study")
    if problems:
        raise ValueError("; ".join(problems))
    by_person = {}
    for row in rows:
        pid = row["participant_id"]
        if not pid or pid.upper().startswith("PILOT-"):
            raise ValueError("pilot or missing participant code in scoring input")
        by_person.setdefault(pid, []).append(row)
    scored, people, exclusions = [], [], []
    for pid, cases in by_person.items():
        reasons = {r["exclude_reason"] for r in cases if r["exclude_reason"]}
        if any(r["consent"] != "yes" for r in cases):
            reasons.add("no consent")
        if any(r["complete"] != "1" for r in cases):
            reasons.add("incomplete")
        if reasons:
            exclusions.append({"label": label, "participant_id": pid, "reason": "; ".join(sorted(reasons))})
            continue
        if sorted(r["case_id"] for r in cases) != case_pack.SCORED_IDS:
            raise ValueError(pid + ": expected exactly one row for each of C01-C10")
        if sorted(int(r["case_order"]) for r in cases) != list(range(1, 11)):
            raise ValueError(pid + ": invalid case order")
        groups = {r["group"] for r in cases}
        times = {float(r["time_seconds"]) for r in cases}
        if len(groups) != 1 or not groups <= {"A", "B"} or len(times) != 1:
            raise ValueError(pid + ": inconsistent group or repeated total time")
        seconds = times.pop()
        if not 60 <= seconds <= 18000:
            raise ValueError(pid + ": invalid total time")
        correct, confidence = [], []
        for row in cases:
            if row["predicted_output"] not in ("0", "1"):
                raise ValueError(pid + ": guess must be 0 or 1")
            certainty = int(row["confidence"])
            if not 1 <= certainty <= 5:
                raise ValueError(pid + ": confidence must be 1-5")
            right = int(int(row["predicted_output"]) == lookup[row["case_id"]]["model_flag"])
            correct.append(right)
            confidence.append(certainty)
            scored.append({**row, "correct": right})
        people.append({
            "label": label, "participant_id": pid, "group": groups.pop(),
            "accuracy": sum(correct) / 10, "mean_confidence": sum(confidence) / 10,
            "self_reported_minutes": seconds / 60,
        })
    if not people:
        raise ValueError("no eligible complete participants remain")
    summaries = []
    for group in ("A", "B"):
        sample = [p for p in people if p["group"] == group]
        summaries.append({
            "label": label, "group": group, "n_participants": len(sample),
            "mean_accuracy": sum(p["accuracy"] for p in sample) / len(sample) if sample else "",
            "mean_confidence": sum(p["mean_confidence"] for p in sample) / len(sample) if sample else "",
            "mean_self_reported_minutes": sum(p["self_reported_minutes"] for p in sample) / len(sample) if sample else "",
            "minimum_per_group_met": len(sample) >= 18,
            "overall_minimum_met": len(people) >= 40 and all(
                sum(p["group"] == g for p in people) >= 18 for g in ("A", "B")),
        })
    return scored, people, summaries, exclusions


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("responses")
    parser.add_argument("--private", required=True)
    parser.add_argument("--participants", required=True, help="participant export from W2.8 (practice chart checks)")
    parser.add_argument("--label", choices=["dummy", "study"], required=True)
    parser.add_argument("--out", default="data/human_study/analysis")
    args = parser.parse_args(argv)
    with open(args.private, encoding="utf-8") as f:
        lookup = json.load(f)
    scored, people, summaries, exclusions = score_responses(read_csv(args.responses), lookup, args.label)
    participant_rows = read_csv(args.participants)
    by_id = {p["participant_id"]: p for p in participant_rows}
    if len(by_id) != len(participant_rows) or any(p["participant_id"] not in by_id for p in people):
        raise ValueError("participant export is duplicated or missing included participants")
    group_b = [by_id[p["participant_id"]] for p in people if p["group"] == "B"]
    checks = []
    for field, correct in (("chart_check_b1", "More worried about this student"),
                           ("chart_check_b2", "A bigger effect"), ("chart_check_ok", "1")):
        checks.append({"label": args.label, "check": field, "n_participants": len(group_b),
                       "n_correct": sum(p[field] == correct for p in group_b)})
    out = Path(args.out)
    for name, rows in (("scored", scored), ("participants", people),
                       ("group_summary", summaries)):
        if rows:
            write_csv(out / (name + "_" + args.label + ".csv"), rows)
    write_csv(out / ("exclusions_" + args.label + ".csv"), exclusions,
              ["label", "participant_id", "reason"])
    write_csv(out / ("chart_checks_" + args.label + ".csv"), checks)
    print(f"{args.label.upper()}: {len(people)} included, {len(exclusions)} excluded; descriptive results only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
