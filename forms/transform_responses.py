#!/usr/bin/env python3
"""W2.8: turn the Google Forms response export into the analysis files.

Input: either one CSV per form tab of the response Sheet, or the original Excel workbook,
plus the assignment list and form_spec.json from the same build, and optionally W4's send log.

Output, in --out-dir (forms/out by default, never committed):
  responses_long_<label>.csv          one row per participant per scored case; columns from
                                      docs/human_study_response_template.csv
  responses_participants_<label>.csv  one row per participant: form, role, practice guess,
                                      Group B chart check

Dropped and reported: declined consent or age, the pilot code, codes not on the assignment list,
a code used on the other group's form, and repeat submissions of one code (the first is kept).
`correct` stays empty: the scoring script (W5.6) fills it from the private file.
`time_seconds` is the participant's self-reported total time (last question, minutes x 60), repeated on
each case row: sessions are online and Google Forms cannot time single cases.

Dry run (W2.5):
  python3 forms/transform_responses.py form1.csv form2.csv form3.csv form4.csv \\
      --variants A1 A2 B1 B2 --assignment forms/out/assignment_fixture.csv --spec forms/out/form_spec.json --label dummy

Send log (optional, from W4): a CSV with participant_code and exclude_reason, for exclusions W4
recorded (e.g. the person reported seeing the answer). Other columns are ignored.
"""
import argparse
import csv
import json
import math
import pathlib
import sys

from openpyxl import load_workbook

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "docs" / "human_study_response_template.csv"
ANSWER_TYPES = {"multiple_choice", "scale", "paragraph", "short_text"}
CONSENT_ID, AGE_ID, CODE_ID, ROLE_ID, MINUTES_ID = "S1.1", "S1.2", "S2.1", "S6.1", "S6.2"
AGREE, ADULT = "I agree", "Yes"
CHART_CHECK = {"P.B1": "More worried about this student", "P.B2": "A bigger effect"}  # right answers
PARTICIPANT_COLUMNS = ["participant_id", "form", "variant_id", "group", "role", "practice_guess",
                       "chart_check_b1", "chart_check_b2", "chart_check_ok", "submitted_at",
                       "self_reported_minutes", "complete", "exclude_reason"]
LABELS = ("dummy", "pilot", "study")


def template_columns():
    with open(TEMPLATE, newline="", encoding="utf-8") as f:
        return next(csv.reader(f))


def answer_items(variant):
    """Items that become a column in the response Sheet, in form order."""
    return [it for s in variant["sections"] for it in s["items"] if it["type"] in ANSWER_TYPES]


def group_titles(spec):
    titles = {}
    for v in spec["variants"]:
        t = [it["title"] for it in answer_items(v)]
        if titles.setdefault(v["group"], t) != t:
            raise ValueError("forms in group %s have different questions" % v["group"])
    return titles


def export_header_matches(expected, actual):
    """Accept Google Sheets' numeric suffixes for repeated question titles."""
    if len(expected) != len(actual):
        return False
    occurrences = {}
    for wanted, observed in zip(expected, actual):
        occurrences[wanted] = occurrences.get(wanted, 0) + 1
        number = occurrences[wanted]
        exported = wanted if number == 1 else f"{wanted} {number}"
        if observed not in (wanted, exported):
            return False
    return True


def minutes_to_seconds(text):
    if not str(text).strip():
        return ""
    try:
        minutes = float(text)
    except (TypeError, ValueError):
        raise ValueError("duration must be a number from 1 to 300 minutes") from None
    if not math.isfinite(minutes) or not 1 <= minutes <= 300:
        raise ValueError("duration must be finite and between 1 and 300 minutes")
    return int(round(minutes * 60))


def load_send_log(path):
    """W4's send log: participant_code -> exclude_reason (other columns ignored)."""
    out = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            code = (r.get("participant_code") or "").strip()
            if code:
                out[code] = {"exclude_reason": (r.get("exclude_reason") or "").strip()}
    return out


def read_export(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


def read_workbook(path, sheets):
    """Read selected workbook sheets in the same row-oriented form as CSV exports."""
    def cell_text(value):
        if value is None:
            return ""
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    workbook = load_workbook(path, read_only=True, data_only=True)
    missing = [sheet for sheet in sheets if sheet not in workbook.sheetnames]
    if missing:
        raise ValueError("workbook is missing sheets: " + ", ".join(missing))
    exports = []
    for sheet in sheets:
        rows = [
            [cell_text(value) for value in record]
            for record in workbook[sheet].iter_rows(values_only=True)
        ]
        exports.append((sheet, rows))
    workbook.close()
    return exports


def transform(exports, assignment, spec, send_log=None, source_variants=None):
    """exports: list of (name, rows) where rows[0] is the Sheet header. Returns (long_rows, people, report)."""
    send_log = send_log or {}
    variants = {v["variant_id"]: v for v in spec["variants"]}
    codes = [r["participant_code"] for r in assignment]
    if any(not code for code in codes) or len(codes) != len(set(codes)):
        raise ValueError("assignment codes must be nonempty and unique")
    for row in assignment:
        if row.get("variant_id") not in variants or row.get("group") != variants[row["variant_id"]]["group"]:
            raise ValueError("assignment has an unknown variant or inconsistent group")
    titles = group_titles(spec)
    first_ids = {g: [it["id"] for it in answer_items(next(v for v in spec["variants"] if v["group"] == g))]
                 for g in titles}
    slots = {r["participant_code"]: r for r in assignment}
    report = {"files": [], "declined": 0, "pilot": 0, "unknown_code": [], "wrong_form": [], "repeat": []}
    seen, long_rows, people = set(), [], []
    for name, rows in exports:
        variant_id = (source_variants or {}).get(name)
        if variant_id not in variants:
            raise ValueError("%s: specify the actual source form variant (A1, A2, B1 or B2)" % name)
        source_variant = variants[variant_id]
        if not rows:
            raise ValueError("%s is empty" % name)
        header = [h.strip() for h in rows[0][1:]]
        group = next((g for g, t in titles.items() if export_header_matches(t, header)), None)
        if group is None:
            best = max(titles, key=lambda g: sum(a == b for a, b in zip(titles[g], header)))
            want = titles[best]
            at = next((i for i, (a, b) in enumerate(zip(want, header)) if a != b), min(len(want), len(header)))
            raise ValueError("%s does not match any form: column %d is %r, expected %r (%d vs %d question columns)"
                             % (name, at + 2, header[at] if at < len(header) else None,
                                want[at] if at < len(want) else None, len(header), len(want)))
        if source_variant["group"] != group:
            raise ValueError("%s: header does not match declared source variant %s" % (name, variant_id))
        pos = {iid: i for i, iid in enumerate(first_ids[group])}  # consent, age and code sit at the same place in every form
        report["files"].append((name, group, len(rows) - 1))
        for row in rows[1:]:
            if not any(cell.strip() for cell in row):
                continue
            stamp, answers = row[0], (row[1:] + [""] * len(header))[:len(header)]
            if answers[pos[CONSENT_ID]].strip() != AGREE or answers[pos[AGE_ID]].strip() != ADULT:
                report["declined"] += 1
                continue
            code = answers[pos[CODE_ID]].strip()
            if code.upper().startswith("PILOT-"):
                report["pilot"] += 1
                continue
            slot = slots.get(code)
            if slot is None:
                report["unknown_code"].append(code or "(blank)")
                continue
            v = variants[slot["variant_id"]]
            if v["variant_id"] != variant_id:
                report["wrong_form"].append(code)
                continue
            if code in seen:
                report["repeat"].append(code)
                continue
            seen.add(code)
            values = dict(zip([it["id"] for it in answer_items(v)], (a.strip() for a in answers)))
            log = send_log.get(code, {})
            seconds = minutes_to_seconds(values.get(MINUTES_ID))
            cases, complete = [], bool(values.get(ROLE_ID)) and seconds != ""
            for order, cid in enumerate(v["scored_order"], 1):
                q = [values.get("%s.Q%d" % (cid, n), "") for n in range(1, 6)]
                complete = complete and all(q)
                cases.append((order, cid, q))
            reason = log.get("exclude_reason") or ("" if complete else "incomplete")
            for order, cid, q in cases:
                long_rows.append({
                    "participant_id": code, "consent": "yes", "group": v["group"], "case_order": order,
                    "case_id": cid, "predicted_output": {"Yes": 1, "No": 0}.get(q[0], ""), "confidence": q[1],
                    "correct": "", "time_seconds": seconds, "rationale_freetext": q[2],
                    "intervention_freetext": q[3], "missing_info_freetext": q[4],
                    "complete": int(complete), "exclude_reason": reason})
            b1, b2 = values.get("P.B1", ""), values.get("P.B2", "")
            people.append({
                "participant_id": code, "form": v["form_label"], "variant_id": v["variant_id"], "group": v["group"],
                "role": values.get(ROLE_ID, ""), "practice_guess": values.get("PR.Q1", ""),
                "chart_check_b1": b1, "chart_check_b2": b2,
                "chart_check_ok": "" if v["group"] == "A" else int(b1 == CHART_CHECK["P.B1"] and b2 == CHART_CHECK["P.B2"]),
                "submitted_at": stamp, "self_reported_minutes": values.get(MINUTES_ID, ""),
                "complete": int(complete), "exclude_reason": reason})
    return long_rows, people, report


def write_csv(path, columns, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="W2.8: Google Forms export -> long CSV for analysis.")
    ap.add_argument("exports", nargs="*", help="one CSV per form tab of the response Sheet")
    ap.add_argument("--workbook", help="original .xlsx response workbook")
    ap.add_argument("--sheets", nargs="+", help="workbook sheet names, in --variants order")
    ap.add_argument("--variants", nargs="+", required=True,
                    choices=["A1", "A2", "B1", "B2"],
                    help="actual source variant for each export, in the same order (from the form/tab, not the code)")
    ap.add_argument("--assignment", required=True, help="assignment_<fixture|study>.csv from the same build")
    ap.add_argument("--spec", required=True, help="form_spec.json from the same build")
    ap.add_argument("--send-log", help="W4 send log CSV with participant_code and exclude_reason (optional)")
    ap.add_argument("--label", required=True, choices=LABELS, help="dummy for tests, pilot, or study")
    ap.add_argument("--out-dir", default=str(HERE / "out"))
    args = ap.parse_args(argv)
    if bool(args.workbook) == bool(args.exports):
        ap.error("provide either CSV exports or --workbook, but not both")
    if args.workbook:
        if not args.sheets or len(args.sheets) != len(args.variants) or len(set(args.sheets)) != len(args.sheets):
            ap.error("--workbook needs one unique --sheets entry per --variants entry")
        source_names = args.sheets
    else:
        if args.sheets:
            ap.error("--sheets is only valid with --workbook")
        if len(args.variants) != len(args.exports) or len(set(args.exports)) != len(args.exports):
            ap.error("provide one --variants entry per unique export path")
        source_names = args.exports

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    with open(args.assignment, newline="", encoding="utf-8") as f:
        assignment = list(csv.DictReader(f))
    log = load_send_log(args.send_log) if args.send_log else {}
    try:
        exports = (read_workbook(args.workbook, args.sheets) if args.workbook
                   else [(p, read_export(p)) for p in args.exports])
        long_rows, people, report = transform(
            exports, assignment, spec, log,
            dict(zip(source_names, args.variants)))
    except ValueError as e:
        print("ERROR:", e)
        return 1
    columns = template_columns()
    if long_rows and set(long_rows[0]) != set(columns):
        print("ERROR: output columns differ from", TEMPLATE.name)
        return 1
    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    long_path = out / ("responses_long_%s.csv" % args.label)
    people_path = out / ("responses_participants_%s.csv" % args.label)
    write_csv(long_path, columns, long_rows)
    write_csv(people_path, PARTICIPANT_COLUMNS, people)

    print("Label: %s%s" % (args.label.upper(), " (fake data, never report as results)" if args.label == "dummy" else ""))
    for name, group, n in report["files"]:
        print("  %s: Group %s, %d rows" % (pathlib.Path(name).name, group, n))
    groups = {g: sum(1 for p in people if p["group"] == g) for g in ("A", "B")}
    print("Kept %d participants (A %d, B %d), %d complete; %d case rows -> %s"
          % (len(people), groups["A"], groups["B"], sum(p["complete"] for p in people), len(long_rows), long_path.name))
    print("Dropped: %d declined, %d pilot" % (report["declined"], report["pilot"]))
    for key, text in (("unknown_code", "codes not on the assignment list"), ("wrong_form", "codes on a different form variant"),
                      ("repeat", "repeat submissions (first kept)")):
        if report[key]:
            print("WARN %s: %s" % (text, ", ".join(report[key])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
