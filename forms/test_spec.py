#!/usr/bin/env python3
"""Checks for the fixture form spec. Run after build_spec.py."""
import json
import pathlib
import random
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_spec as b  # noqa: E402


def profile_texts(variant):
    return [i["text"] for s in variant["sections"] for i in s["items"] if i["id"].endswith(".profile")]


def question_sig(variant):
    return [(i["id"], i["title"], i["type"]) for s in variant["sections"] for i in s["items"]
            if re.search(r"\.Q\d$", i["id"])]


def main():
    fails, notes = [], []
    pack, lookup, spec, assignment = b.build_all()
    variants = spec["variants"]
    by_id = {v["variant_id"]: v for v in variants}

    # 1. four variants
    if sorted(by_id) != ["A1", "A2", "B1", "B2"]:
        fails.append("variant ids wrong: %s" % sorted(by_id))

    # 2. profile fields: 30 predictors, no second-semester fields, no Target
    header, _ = b.load_uci()
    fields = b.profile_fields(header)
    if len(fields) != 30:
        fails.append("profile field count %d, expected 30" % len(fields))
    for f in fields:
        if f == "Target" or f.lower().startswith("curricular units 2nd sem"):
            fails.append("forbidden field in profile: " + f)

    # 3. fixture cases come only from the validation split
    val = set(b.validation_ids())
    for cid, meta in lookup.items():
        if meta["source_row_id"] not in val:
            fails.append("%s not from validation split" % cid)
    if len(lookup) != 11:
        fails.append("expected 11 cases, got %d" % len(lookup))

    # 4. scored orders are permutations and reproduce from their seed
    for v in variants:
        if sorted(v["scored_order"]) != sorted(b.SCORED_IDS):
            fails.append("%s order is not a permutation" % v["variant_id"])
        again = list(b.SCORED_IDS)
        random.Random(v["order_seed"]).shuffle(again)
        expected = again if v["variant_id"].endswith("1") else list(reversed(again))
        if expected != v["scored_order"]:
            fails.append("%s order is not the seeded order (or its reverse)" % v["variant_id"])

    # 5. A and B match for each index: same order, profiles and questions; B adds charts and comprehension items
    for i in (1, 2):
        a, bb = by_id["A%d" % i], by_id["B%d" % i]
        if a["scored_order"] != bb["scored_order"]:
            fails.append("A%d and B%d use different orders" % (i, i))
        if profile_texts(a) != profile_texts(bb):
            fails.append("profile text differs between A%d and B%d" % (i, i))
        if question_sig(a) != question_sig(bb):
            fails.append("question wording differs between A%d and B%d" % (i, i))
        if any(it["id"].endswith(".chart") for s in a["sections"] for it in s["items"]):
            fails.append("Group A has a chart in A%d" % i)
        charts_b = sum(1 for s in bb["sections"] for it in s["items"] if it["id"].endswith(".chart"))
        if charts_b != 11:
            fails.append("B%d has %d chart blocks, expected 11" % (i, charts_b))
        comp_b = sum(1 for s in bb["sections"] for it in s["items"] if it["id"] in ("P.B1", "P.B2"))
        if comp_b != 2:
            fails.append("B%d has %d comprehension items, expected 2" % (i, comp_b))

    # 6. profile texts match the case pack; 11 cards per variant
    pack_text = {c["case_id"]: b.profile_text(c) for c in pack["cases"]}
    for v in variants:
        texts = profile_texts(v)
        if len(texts) != 11:
            fails.append("%s has %d profile cards, expected 11" % (v["variant_id"], len(texts)))
        if texts and texts[0] != pack_text[b.PRACTICE_ID]:
            fails.append("%s practice card does not match pack" % v["variant_id"])

    # 7. leakage scan over the whole spec
    blob = json.dumps(spec, ensure_ascii=False).lower()
    for phrase in b.FORBIDDEN_PHRASES:
        if re.search(r"\b" + re.escape(phrase) + r"\b", blob):
            fails.append("forbidden phrase in spec: '%s'" % phrase)

    # 8. assignment: 50 main slots (25 per group, 13/12 per form), 4 spares (one per form), 1 pilot, unique codes
    codes = [r["participant_code"] for r in assignment]
    if len(set(codes)) != len(codes):
        fails.append("duplicate participant codes")
    main = [r for r in assignment if r["role"] == "main"]
    spares = [r for r in assignment if r["role"] == "spare"]
    pilots = [r for r in assignment if r["role"] == "pilot"]
    if len(main) + len(spares) + len(pilots) != len(assignment):
        fails.append("assignment has rows with an unknown role")
    if len(pilots) != 1 or not pilots[0]["participant_code"].startswith("PILOT-") or pilots[0]["variant_id"] not in by_id:
        fails.append("expected exactly one pilot row with a PILOT- code on a real form")
    if len(main) != 50:
        fails.append("assignment has %d main slots, expected 50" % len(main))
    for g in ("A", "B"):
        n = sum(1 for r in main if r["group"] == g)
        if n != 25:
            fails.append("group %s has %d main slots, expected 25" % (g, n))
    for vid in by_id:
        n = sum(1 for r in main if r["variant_id"] == vid)
        if n not in (12, 13):
            fails.append("%s has %d main slots, expected 12 or 13" % (vid, n))
        s = sum(1 for r in spares if r["variant_id"] == vid)
        if s != 1:
            fails.append("%s has %d spares, expected 1" % (vid, s))

    # 9. reproducibility
    _, _, spec2, assignment2 = b.build_all()
    if json.dumps(spec, sort_keys=True) != json.dumps(spec2, sort_keys=True):
        fails.append("spec not reproducible")
    if assignment != assignment2:
        fails.append("assignment not reproducible")

    # 10. participant-facing items: no form version or group field
    for v in variants:
        titles = [i["title"] for s in v["sections"] for i in s["items"]]
        if any("form version" in t.lower() for t in titles):
            fails.append("%s shows a form version field" % v["variant_id"])

    # 13. the case pack follows the W2.2 format; bar ids and combined bars match the definitions in src/
    import case_pack as cp
    for problem in cp.validate_pack(pack) + cp.validate_private(lookup, pack.get("pack_kind")):
        fails.append("case pack: " + problem)
    try:
        # Read the definitions straight from src/ (no heavy imports): the column rule and the two groups.
        import ast
        mod = ast.parse((b.ROOT / "src" / "modeling.py").read_text(encoding="utf-8"))
        fn = [n for n in mod.body if isinstance(n, ast.FunctionDef) and n.name == "clean_column_name"][0]
        space = {}
        exec(compile(ast.Module(body=[fn], type_ignores=[]), "src/modeling.py", "exec"), space)
        model_clean = space["clean_column_name"]
        exp = ast.parse((b.ROOT / "src" / "explanations.py").read_text(encoding="utf-8"))
        node = [n for n in exp.body if isinstance(n, (ast.Assign, ast.AnnAssign))
                and getattr(n.target if isinstance(n, ast.AnnAssign) else n.targets[0], "id", "") == "FIRST_SEMESTER_GROUPS"][0]
        FIRST_SEMESTER_GROUPS = ast.literal_eval(node.value)
        for field in cp.profile_field_labels():
            if cp.clean_column_name(field) != model_clean(field):
                fails.append("bar id rule differs from src/modeling.py for %s" % field)
        if set(cp.GROUP_BARS) != set(FIRST_SEMESTER_GROUPS):
            fails.append("combined bar names differ from src/explanations.py")
        for g, members in cp.GROUPED_FIELDS.items():
            raw = {m for m in FIRST_SEMESTER_GROUPS.get(g, ()) if not m.startswith("first_semester_")}
            if {cp.clean_column_name(f) for f in members} != raw:
                fails.append("members of combined bar %s differ from src/explanations.py" % g)
    except Exception as e:
        fails.append("could not read src/ definitions for the bar-id cross-check: %s" % e)

    # 12. ending: completers go S6 -> COMPLETE -> submit; only the two decline answers route, to DECLINE (last page)
    for v in variants:
        vid = v["variant_id"]
        ids = [s["id"] for s in v["sections"]]
        if ids[-3:] != ["S6", "COMPLETE", "DECLINE"]:
            fails.append("%s ending sections are %s" % (vid, ids[-3:]))
        secs = {s["id"]: s for s in v["sections"]}
        if secs.get("COMPLETE", {}).get("after") != "SUBMIT":
            fails.append("%s completion page does not submit" % vid)
        items = {it["id"]: it for s in v["sections"] for it in s["items"]}
        if items["S1.1"]["goto_map"] != {"I do not agree": "DECLINE"} or items["S1.2"]["goto_map"] != {"No": "DECLINE"}:
            fails.append("%s decline routes wrong" % vid)
        if any(it.get("goto_map") for iid, it in items.items() if iid not in ("S1.1", "S1.2")):
            fails.append("%s has routes outside the consent and age items" % vid)

    # 11. every profile field has a plain label, and every code in the data has a label
    import labels as L
    mapped = sorted(f for _, fs in L.GROUPS for f, _, _ in fs)
    if mapped != sorted(fields):
        fails.append("labelled fields do not match the 30 profile fields")
    _, data_rows = b.load_uci()
    col = {h: i for i, h in enumerate(header)}
    for _, fs in L.GROUPS:
        for field, label, kind in fs:
            bad = None
            for r in data_rows:
                try:
                    L.format_value(kind, field, r[col[field]])
                except (KeyError, ValueError) as e:
                    bad = (r[col[field]], str(e))
                    break
            if bad:
                fails.append("no label for %s value %r (%s)" % (field, bad[0], bad[1]))

    notes.append("[TBD] markers still open in spec: %d" % blob.count("[tbd"))
    notes.append("pending decisions listed in spec: %d" % len(spec["decisions_pending"]))
    for n in notes:
        print("NOTE", n)
    if fails:
        for f in fails:
            print("FAIL", f)
        sys.exit(1)
    print("PASS: %d variants, all checks passed" % len(variants))


if __name__ == "__main__":
    main()
