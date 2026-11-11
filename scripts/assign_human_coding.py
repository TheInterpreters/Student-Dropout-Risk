"""W5.9: private blinded coding assignments and raw agreement, using pseudonymous member IDs."""
from __future__ import annotations

import argparse
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.analyze_human_study import read_csv, write_csv

FIELDS = ("rationale_freetext", "intervention_freetext", "missing_info_freetext")
ALLOWED_CODES = {
    "rationale_freetext": {
        "academic_evidence", "financial_or_admin", "personal_or_demographic",
        "course_or_application", "explanation_chart", "multiple_or_holistic", "unclear_other",
    },
    "intervention_freetext": {
        "academic_support", "financial_or_admin_support", "advising_or_monitoring",
        "wellbeing_or_social_support", "verify_or_gather_information",
        "no_action_or_punitive", "unclear_other",
    },
    "missing_info_freetext": {
        "academic_engagement", "financial_or_admin", "personal_wellbeing",
        "course_or_institution", "support_history", "nothing_else", "unclear_other",
    },
}


def validate_code(field, code):
    if field not in ALLOWED_CODES or code not in ALLOWED_CODES[field]:
        raise ValueError(f"invalid code {code!r} for {field}")


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
        validate_code(row["field"], row["code"].strip())
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


def _required_items(assignments):
    return [(row["participant_id"], f"C{i:02d}", field)
            for row in assignments for i in range(1, 11) for field in FIELDS]


def reconcile(assignments, coded, decisions=None):
    """Build one agreed code per participant/case/field.

    Single-coded items take the primary coder's code. Double-coded items take the shared code when
    both coders agree; otherwise the adjudicator's `resolved_code` from `decisions` (the returned
    disagreement sheet, filled in) is used. Returns (reconciled_rows, open_disagreements).
    """
    coders = {row["participant_id"]: (row["primary_coder"], row["secondary_coder"]) for row in assignments}
    if len(coders) != len(assignments):
        raise ValueError("duplicate participants in assignments")
    codes, texts = {}, {}
    for row in coded:
        pid = row["participant_id"]
        if pid not in coders:
            raise ValueError(pid + ": coded participant is not in the assignments")
        if row["coder"] not in coders[pid] or not row["coder"]:
            raise ValueError(pid + ": unexpected coder " + repr(row["coder"]))
        key = (pid, row["case_id"], row["field"], row["coder"])
        if key in codes:
            raise ValueError("duplicate coded item: " + "/".join(key))
        code = row["code"].strip()
        if not code:
            raise ValueError("missing code: " + "/".join(key))
        validate_code(row["field"], code)
        codes[key] = code
        texts[key[:3]] = row.get("text", "")
    resolved = {}
    for row in decisions or []:
        key = (row["participant_id"], row["case_id"], row["field"])
        code = row.get("resolved_code", "").strip()
        if code:
            validate_code(row["field"], code)
            resolved[key] = code
    reconciled, open_items, used = [], [], set()
    for item in _required_items(assignments):
        primary, secondary = coders[item[0]]
        first = codes.get(item + (primary,))
        if first is None:
            raise ValueError("primary coder has not coded " + "/".join(item))
        if not secondary:
            reconciled.append(dict(zip(("participant_id", "case_id", "field"), item),
                                   code=first, source="single"))
            continue
        second = codes.get(item + (secondary,))
        if second is None:
            raise ValueError("secondary coder has not coded " + "/".join(item))
        if first == second:
            reconciled.append(dict(zip(("participant_id", "case_id", "field"), item),
                                   code=first, source="agreed"))
        elif item in resolved:
            used.add(item)
            reconciled.append(dict(zip(("participant_id", "case_id", "field"), item),
                                   code=resolved[item], source="adjudicated"))
        else:
            open_items.append({"participant_id": item[0], "case_id": item[1], "field": item[2],
                               "text": texts.get(item, ""), "primary_code": first,
                               "secondary_code": second, "resolved_code": ""})
    stale = set(resolved) - used
    if stale:
        raise ValueError("decisions given for items that are not disagreements: "
                         + ", ".join("/".join(k) for k in sorted(stale)))
    return reconciled, open_items


def theme_by_group(coded, responses, lookup=None):
    """Aggregate reconciled codes by study group (and by hidden model flag when a lookup is given)."""
    groups = {}
    for row in responses:
        groups.setdefault(row["participant_id"], row["group"])
    flags = {case: str(value["model_flag"]) for case, value in (lookup or {}).items()}
    counts, totals = {}, {}
    for row in coded:
        group = groups.get(row["participant_id"])
        if group not in ("A", "B"):
            raise ValueError(row["participant_id"] + ": participant has no study group")
        code = row["code"].strip()
        validate_code(row["field"], code)
        strata = [("all", group)]
        if lookup is not None:
            if row["case_id"] not in flags:
                raise ValueError(row["case_id"] + ": case missing from private lookup")
            strata.append((flags[row["case_id"]], group))
        for flag, grp in strata:
            counts[(row["field"], grp, flag, code)] = counts.get((row["field"], grp, flag, code), 0) + 1
            totals[(row["field"], grp, flag)] = totals.get((row["field"], grp, flag), 0) + 1
    result = []
    for (field, grp, flag), total in sorted(totals.items()):
        for code in sorted(ALLOWED_CODES[field]):
            n = counts.get((field, grp, flag, code), 0)
            result.append({"field": field, "group": grp, "model_flag": flag, "code": code,
                           "n_items": n, "n_field_items": total, "share_within_stratum": n / total})
    return result


FLAG_COLUMNS = ("concrete_next_step", "feasible_before_second_semester", "unsupported_causal_assumption")
ACTORS = ("student", "institution", "both", "none")


def intervention_flag_summary(flags, responses, lookup=None):
    """Aggregate the proposal section 5.7 intervention ratings by group (and hidden model flag).

    Each flags row rates one intervention answer: three 0/1 columns plus `responsible_actor`.
    """
    groups = {}
    for row in responses:
        groups.setdefault(row["participant_id"], row["group"])
    model_flags = {case: str(value["model_flag"]) for case, value in (lookup or {}).items()}
    seen, cells = set(), {}
    for row in flags:
        key = (row["participant_id"], row["case_id"])
        if key in seen:
            raise ValueError("duplicate intervention rating: " + "/".join(key))
        seen.add(key)
        group = groups.get(row["participant_id"])
        if group not in ("A", "B"):
            raise ValueError(row["participant_id"] + ": participant has no study group")
        if any(row[c] not in ("0", "1") for c in FLAG_COLUMNS) or row["responsible_actor"] not in ACTORS:
            raise ValueError("invalid intervention rating: " + "/".join(key))
        strata = [("all", group), ("all", "all")]
        if lookup is not None:
            if row["case_id"] not in model_flags:
                raise ValueError(row["case_id"] + ": case missing from private lookup")
            strata.append((model_flags[row["case_id"]], group))
        for stratum in strata:
            cells.setdefault(stratum, []).append(row)
    result = []
    for (flag, group), items in sorted(cells.items()):
        n = len(items)
        record = {"group": group, "model_flag": flag, "n_items": n}
        for column in FLAG_COLUMNS:
            record["share_" + column] = sum(r[column] == "1" for r in items) / n
        for actor in ACTORS:
            record["share_actor_" + actor] = sum(r["responsible_actor"] == actor for r in items) / n
        result.append(record)
    return result


def theme_summary(coded):
    """Summarize one reconciled primary code per participant/case/field."""
    seen, counts = set(), {}
    for row in coded:
        key = (row["participant_id"], row["case_id"], row["field"])
        if key in seen:
            raise ValueError("reconciled coding contains duplicate items")
        seen.add(key)
        code = row["code"].strip()
        validate_code(row["field"], code)
        counts[(row["field"], code)] = counts.get((row["field"], code), 0) + 1
    totals = {field: sum(value for (name, _), value in counts.items() if name == field)
              for field in FIELDS}
    if not seen or any(not totals[field] for field in FIELDS):
        raise ValueError("reconciled coding must contain all three text fields")
    return [
        {"field": field, "code": code, "n_items": counts.get((field, code), 0),
         "share_within_field": counts.get((field, code), 0) / totals[field]}
        for field in FIELDS for code in sorted(ALLOWED_CODES[field])
    ]


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
    reconcile_cmd = sub.add_parser("reconcile")
    reconcile_cmd.add_argument("--assignments", required=True)
    reconcile_cmd.add_argument("--coded", required=True, help="all completed worksheets combined")
    reconcile_cmd.add_argument("--decisions",
                               help="the disagreements CSV with resolved_code filled in by the adjudicator")
    summary = sub.add_parser("summary")
    summary.add_argument("--coded", required=True,
                         help="reconciled CSV with exactly one agreed code per participant/case/field")
    summary.add_argument("--responses",
                         help="responses_long CSV; adds the by-group table (group is joined privately)")
    summary.add_argument("--private", help="private lookup JSON; adds the by-model-flag split")
    summary.add_argument("--flags", help="intervention ratings CSV (proposal 5.7); needs --responses")
    for command in (assign, agreement, reconcile_cmd, summary):
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
    elif args.command == "agreement":
        write_csv(out / ("agreement_" + args.label + ".csv"),
                  [{"label": args.label, **row}
                   for row in raw_agreement(read_csv(args.assignments), read_csv(args.coded))])
    elif args.command == "reconcile":
        decisions = read_csv(args.decisions) if args.decisions else None
        reconciled, open_items = reconcile(read_csv(args.assignments), read_csv(args.coded), decisions)
        if open_items:
            path = out / ("disagreements_" + args.label + ".csv")
            write_csv(path, open_items)
            print(f"{len(open_items)} disagreements need a decision. Fill resolved_code in {path} "
                  "and rerun with --decisions <that file>. No reconciled file was written.")
            return 2
        write_csv(out / ("reconciled_" + args.label + ".csv"), reconciled)
        sources = {s: sum(r["source"] == s for r in reconciled) for s in ("single", "agreed", "adjudicated")}
        print(f"Reconciled {len(reconciled)} items: {sources}")
    else:
        coded = read_csv(args.coded)
        write_csv(out / ("theme_summary_" + args.label + ".csv"),
                  [{"label": args.label, **row} for row in theme_summary(coded)])
        if args.responses:
            import json
            lookup = None
            if args.private:
                with open(args.private, encoding="utf-8") as stream:
                    lookup = json.load(stream)
            write_csv(out / ("theme_by_group_" + args.label + ".csv"),
                      [{"label": args.label, **row}
                       for row in theme_by_group(coded, read_csv(args.responses), lookup)])
            if args.flags:
                write_csv(out / ("intervention_flags_by_group_" + args.label + ".csv"),
                          [{"label": args.label, **row} for row in
                           intervention_flag_summary(read_csv(args.flags), read_csv(args.responses), lookup)])
        elif args.flags:
            raise SystemExit("--flags requires --responses")
    print(args.label.upper() + ": private coding outputs written; do not commit free text.")
    return 0


if __name__ == "__main__":
    # Support both `python scripts/assign_human_coding.py` and module execution.
    raise SystemExit(main())
