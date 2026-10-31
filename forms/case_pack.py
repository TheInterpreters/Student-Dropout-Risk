#!/usr/bin/env python3
"""Case-pack format (W2.2), version 1.0. Human-readable version: docs/case_pack_contract.md.

Two files per build (<kind> is "fixture" or "study"):
  case_pack_<kind>.json       what the forms and the chart renderer read; no model output
  private_lookup_<kind>.json  dataset row and model flag per case; scoring only, restricted

Check files before handing them over:
  python3 forms/case_pack.py case_pack_study.json private_lookup_study.json
"""
import json
import math
import sys

import labels

CONTRACT_VERSION = "1.0"
PRACTICE_ID = "PR"
SCORED_IDS = ["C%02d" % i for i in range(1, 11)]
CASE_IDS = [PRACTICE_ID] + SCORED_IDS
TOP_K = 5  # config/evaluation_protocol.json: shap.display_top_k
PACK_KINDS = ("fixture", "study")

# The two combined first-semester bars, as in src/explanations.py FIRST_SEMESTER_GROUPS.
GROUP_BARS = {
    "first_semester_participation": "First-semester participation (units, exams)",
    "first_semester_progress": "First-semester progress (passed units, grade)",
}
# Dataset columns folded into those bars (their derived features are folded in too).
GROUPED_FIELDS = {
    "first_semester_participation": ["Curricular units 1st sem (enrolled)",
                                     "Curricular units 1st sem (evaluations)",
                                     "Curricular units 1st sem (without evaluations)"],
    "first_semester_progress": ["Curricular units 1st sem (approved)",
                                "Curricular units 1st sem (grade)"],
}
# Keys that would carry the model output; they belong only in the private file.
FORBIDDEN_KEYS = {"probability", "proba", "score", "base_value", "expected_value", "model_flag", "flag",
                  "flagged", "prediction", "predicted", "target", "outcome", "rank", "risk", "source_row_id"}


def clean_column_name(column):
    """Same rule as src/modeling.clean_column_name: dataset column -> model feature name."""
    return (column.strip().replace("'", "").replace("/", "_").replace("(", "").replace(")", "")
            .replace("-", "_").replace(" ", "_").lower())


def profile_field_labels():
    return {field: label for _, fields in labels.GROUPS for field, label, _ in fields}


def bar_labels():
    """bar_id -> plain bar name. Single bars reuse the profile label, so chart and card use the same words."""
    grouped = {f for fields in GROUPED_FIELDS.values() for f in fields}
    out = dict(GROUP_BARS)
    for field, label in profile_field_labels().items():
        if field not in grouped:
            out[clean_column_name(field)] = label
    return out


def chart_file(case_id):
    return "chart_%s.png" % case_id


def _number(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _keys(v)


def validate_pack(pack):
    """Return a list of problems; an empty list means the pack follows the format."""
    if not isinstance(pack, dict):
        return ["the case pack is not a JSON object"]
    p = []
    if pack.get("contract_version") != CONTRACT_VERSION:
        p.append("contract_version must be %r" % CONTRACT_VERSION)
    kind = pack.get("pack_kind")
    if kind not in PACK_KINDS:
        p.append("pack_kind must be one of %s" % (PACK_KINDS,))
    for key in ("protocol_version", "source", "model_ref"):
        if not isinstance(pack.get(key), str) or not pack.get(key):
            p.append("%s is missing" % key)
    if not isinstance(pack.get("contributions_placeholder"), bool):
        p.append("contributions_placeholder must be true or false")
    if kind == "study" and pack.get("contributions_placeholder") is not False:
        p.append("a study pack needs real contributions (contributions_placeholder: false)")
    bad = sorted({k for k in _keys(pack) if str(k).lower() in FORBIDDEN_KEYS})
    if bad:
        p.append("keys that carry the model output are not allowed in the case pack: %s" % bad)
    cases = pack.get("cases")
    if not isinstance(cases, list):
        return p + ["cases is missing"]
    ids = [c.get("case_id") for c in cases]
    if ids != CASE_IDS:
        p.append("case ids must be %s in that order, got %s" % (" ".join(CASE_IDS), ids))
    fields = profile_field_labels()
    kinds = {f: k for _, fs in labels.GROUPS for f, _, k in fs}
    bars = bar_labels()
    for c in cases:
        cid = c.get("case_id")
        role = "practice" if cid == PRACTICE_ID else "scored"
        if c.get("role") != role:
            p.append("%s: role must be %r" % (cid, role))
        prof = c.get("profile") or []
        if sorted(x.get("field") for x in prof) != sorted(fields):
            p.append("%s: profile must have exactly the %d dataset fields, by their column names" % (cid, len(fields)))
        for x in prof:
            f = x.get("field")
            if f in kinds:
                try:
                    labels.format_value(kinds[f], f, x.get("value"))
                except Exception:
                    p.append("%s: value %r for %s is not a number or has no label" % (cid, x.get("value"), f))
        if c.get("chart_file") != chart_file(cid):
            p.append("%s: chart_file must be %r" % (cid, chart_file(cid)))
        con = c.get("contributions")
        if not isinstance(con, list) or len(con) != TOP_K:
            p.append("%s: contributions must list exactly %d bars" % (cid, TOP_K))
            continue
        seen, prev = set(), None
        for bar in con:
            bid, val = bar.get("bar_id"), _number(bar.get("value"))
            if bid not in bars:
                p.append("%s: unknown bar_id %r" % (cid, bid))
            elif bar.get("label") != bars[bid]:
                p.append("%s: label for %s must be %r" % (cid, bid, bars[bid]))
            if bid in seen:
                p.append("%s: bar %s is listed twice" % (cid, bid))
            seen.add(bid)
            if val is None:
                p.append("%s: value for %s is not a number" % (cid, bid))
                continue
            if prev is not None and abs(val) > abs(prev) + 1e-12:
                p.append("%s: bars must be sorted by size, largest first" % cid)
            prev = val
    return p


def validate_private(private, kind):
    """Problems in the private file (dataset row and model flag per case)."""
    if not isinstance(private, dict):
        return ["the private file is not a JSON object"]
    p = []
    if sorted(private) != sorted(CASE_IDS):
        p.append("the private file must have exactly the 11 case ids")
    for cid, meta in private.items():
        if not isinstance(meta.get("source_row_id"), int):
            p.append("%s: source_row_id must be a whole number" % cid)
        flag = meta.get("model_flag")
        if flag not in ((0, 1) if kind == "study" else (0, 1, None)):
            p.append("%s: model_flag must be 0 or 1%s" % (cid, "" if kind == "study" else " (or null in a fixture)"))
    if kind == "study":
        flagged = sum(1 for c in SCORED_IDS if private.get(c, {}).get("model_flag") == 1)
        if flagged != 5:
            p.append("the 10 scored cases must be 5 flagged and 5 not flagged; found %d flagged" % flagged)
    return p


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        pack = json.load(f)
    problems = validate_pack(pack)
    if len(argv) > 2:
        with open(argv[2], encoding="utf-8") as f:
            problems += validate_private(json.load(f), pack.get("pack_kind"))
    for x in problems:
        print("FAIL:", x)
    print("PASS: follows case-pack format %s" % CONTRACT_VERSION if not problems else "%d problem(s)" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
