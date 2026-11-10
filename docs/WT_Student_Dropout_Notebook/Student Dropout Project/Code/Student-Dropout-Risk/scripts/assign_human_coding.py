"""W5.9: private blinded coding assignments and raw agreement, using pseudonymous member IDs."""
from __future__ import annotations

import argparse
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.analyze_human_study import read_csv, write_csv

FIELDS = ("rationale_freetext", "intervention_freetext", "missing_info_freetext")


def assign_coding(rows, recruiters, members, seed=42):
    if len(set(members)) != 5:
        raise ValueError("provide five distinct pseudonymous member IDs")
    by_person = {}
    for row in rows:
        if row["complete"] == "1" and not row["exclude_reason"] and row["consent"] == "yes":
            by_person.setdefault(row["participant_id"], []).append(row)
    if not by_person:
        raise ValueError("no eligible responses to code")
    rng = random.Random(seed)
    ids = sorted(by_person)
    rng.shuffle(ids)
    double = set(rng.sample(sorted(ids), max(1, round(0.20 * len(ids)))))
    counts = {m: 0 for m in members}
    second_counts = {m: 0 for m in members}
    assignments, tasks = [], []
    for pid in ids:
        if sorted(r["case_id"] for r in by_person[pid]) != [f"C{i:02d}" for i in range(1, 11)]:
            raise ValueError(pid + ": coding requires exactly ten unique scored cases")
        recruiter = recruiters.get(pid)
        if recruiter not in members:
            raise ValueError(pid + ": recruiter missing or not one of the five members")
        candidates = [m for m in members if m != recruiter]
        rng.shuffle(candidates)
        primary = min(candidates, key=counts.get)
        counts[primary] += 1
        secondary = ""
        if pid in double:
            candidates = [m for m in candidates if m != primary]
            secondary = min(candidates, key=second_counts.get)
            second_counts[secondary] += 1
        assignments.append({"participant_id": pid, "primary_coder": primary, "secondary_coder": secondary})
        for coder in (primary, secondary):
            if not coder:
                continue
            for row in by_person[pid]:
                for field in FIELDS:
                    tasks.append({
                        "coder": coder, "participant_id": pid, "case_id": row["case_id"],
                        "field": field, "text": row[field], "code": "",
                    })
    return assignments, tasks


def raw_agreement(assignments, coded):
    expected = {}
    for row in assignments:
        if row["secondary_coder"]:
            expected[row["participant_id"]] = {row["primary_coder"], row["secondary_coder"]}
    ratings = {}
    for row in coded:
        if row["participant_id"] not in expected:
            continue
        key = (row["participant_id"], row["case_id"], row["field"])
        if row["coder"] not in expected[key[0]] or not row["code"].strip():
            raise ValueError("missing code or unexpected coder for a double-coded participant")
        group = ratings.setdefault(key, {})
        if row["coder"] in group:
            raise ValueError("duplicate coded item")
        group[row["coder"]] = row["code"].strip()
    required = {(pid, f"C{i:02d}", field) for pid in expected for i in range(1, 11) for field in FIELDS}
    if set(ratings) != required or any(len(v) != 2 for v in ratings.values()):
        raise ValueError("double-coded set is incomplete or contains unexpected items")
    result = []
    for field in FIELDS:
        pairs = [list(v.values()) for k, v in ratings.items() if k[2] == field]
        result.append({
            "field": field, "n_double_coded_participants": len(expected), "n_items": len(pairs),
            "raw_agreement": sum(a == b for a, b in pairs) / len(pairs) if pairs else "",
        })
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    assign = sub.add_parser("assign")
    assign.add_argument("responses")
    assign.add_argument("--send-log", required=True)
    assign.add_argument("--members", nargs=5, required=True)
    assign.add_argument("--seed", type=int, default=42)
    agreement = sub.add_parser("agreement")
    agreement.add_argument("--assignments", required=True)
    agreement.add_argument("--coded", required=True)
    for command in (assign, agreement):
        command.add_argument("--label", choices=["dummy", "study"], required=True)
        command.add_argument("--out", default="data/human_study/coding")
    args = parser.parse_args(argv)
    out = Path(args.out)
    if args.command == "assign":
        log = read_csv(args.send_log)
        recruiters = {r["participant_code"]: r["recruiter"] for r in log}
        if len(recruiters) != len(log):
            raise ValueError("duplicate participant codes in send log")
        assignments, tasks = assign_coding(read_csv(args.responses), recruiters, args.members, args.seed)
        write_csv(out / ("assignments_" + args.label + ".csv"), assignments)
        for member in args.members:
            member_tasks = [t for t in tasks if t["coder"] == member]
            if member_tasks:
                # Numeric file indexes avoid using untrusted member IDs as paths.
                index = args.members.index(member) + 1
                write_csv(out / (f"coder_{index}_" + args.label + ".csv"), member_tasks)
    else:
        write_csv(out / ("agreement_" + args.label + ".csv"),
                  [{"label": args.label, **row}
                   for row in raw_agreement(read_csv(args.assignments), read_csv(args.coded))])
    print(args.label.upper() + ": private coding outputs written; do not commit free text.")
    return 0


if __name__ == "__main__":
    # Support both `python scripts/assign_human_coding.py` and module execution.
    raise SystemExit(main())
