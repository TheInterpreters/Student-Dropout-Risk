#!/usr/bin/env python3
"""W2.8: turn the Google Forms response export into the analysis files.

Input: one CSV per form tab of the response Sheet (File > Download > Comma-separated values),
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
      --assignment forms/out/assignment_fixture.csv --spec forms/out/form_spec.json --label dummy

Send log (optional, from W4): a CSV with participant_code and exclude_reason, for exclusions W4
recorded (e.g. the person reported seeing the answer). Other columns are ignored.
"""
import argparse
import csv
import json
import pathlib
import sys

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


def minutes_to_seconds(text):
    try:
        minutes = float(text)
    except (TypeError, ValueError):
        return ""
    return int(round(minutes * 60)) if minutes > 0 else ""


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


def transform(exports, assignment, spec, send_log=None):
    """exports: list of (name, rows) where rows[0] is the Sheet header. Returns (long_rows, people, report)."""
    send_log = send_log or {}
    variants = {v["variant_id"]: v for v in spec["variants"]}
    titles = group_titles(spec)
    first_ids = {g: [it["id"] for it in answer_items(next(v for v in spec["variants"] if v["group"] == g))]
                 for g in titles}
    slots = {r["participant_code"]: r for r in assignment}
    report = {"files": [], "declined": 0, "pilot": 0, "unknown_code": [], "wrong_form": [], "repeat": []}
    seen, long_rows, people = set(), [], []
    for name, rows in exports:
        if not rows:
            raise ValueError("%s is empty" % name)
        header = [h.strip() for h in rows[0][1:]]
        group = next((g for g, t in titles.items() if t == header), None)
        if group is None:
            best = max(titles, key=lambda g: sum(a == b for a, b in zip(titles[g], header)))
            want = titles[best]
            at = next((i for i, (a, b) in enumerate(zip(want, header)) if a != b), min(len(want), len(header)))
            raise ValueError("%s does not match any form: column %d is %r, expected %r (%d vs %d question columns)"
                             % (name, at + 2, header[at] if at < len(header) else None,
                                want[at] if at < len(want) else None, len(header), len(want)))
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
            if v["group"] != group:
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
    ap.add_argument("exports", nargs="+", help="one CSV per form tab of the response Sheet")
    ap.add_argument("--assignment", required=True, help="assignment_<fixture|study>.csv from the same build")
    ap.add_argument("--spec", required=True, help="form_spec.json from the same build")
    ap.add_argument("--send-log", help="W4 send log CSV with participant_code and exclude_reason (optional)")
    ap.add_argument("--label", required=True, choices=LABELS, help="dummy for tests, pilot, or study")
    ap.add_argument("--out-dir", default=str(HERE / "out"))
    args = ap.parse_args(argv)

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    with open(args.assignment, newline="", encoding="utf-8") as f:
        assignment = list(csv.DictReader(f))
    log = load_send_log(args.send_log) if args.send_log else {}
    try:
        long_rows, people, report = transform([(p, read_export(p)) for p in args.exports], assignment, spec, log)
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
    for key, text in (("unknown_code", "codes not on the assignment list"), ("wrong_form", "codes on the other group's form"),
                      ("repeat", "repeat submissions (first kept)")):
        if report[key]:
            print("WARN %s: %s" % (text, ", ".join(report[key])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
