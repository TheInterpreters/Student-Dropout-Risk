#!/usr/bin/env python3
"""Fixture build for the human-study forms. No real cases, no model outputs.

Uses validation-split rows only (artifacts/split_ids.csv). Writes to forms/out/:
  case_pack_fixture.json       profile cards: PR (practice) and C01-C10 (scored)
  private_lookup_fixture.json  case -> UCI source row. Keep private.
  form_spec.json               six variants: A1-A3 (control), B1-B3 (explanation)
  assignment_fixture.csv       participant slots (50 main + 4 spares) -> form
Anything marked [TBD] or 'placeholder' must be replaced before a real run.
"""
import csv
import json
import labels
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "eda_uci_data" / "data" / "dropout_data.csv"
SPLIT = ROOT / "artifacts" / "split_ids.csv"
OUT = ROOT / "forms" / "out"

FIXTURE_SEED = 1               # picks dummy validation rows (fixture only)
ORDER_SEEDS = [11]  # one fixed order shared by both groups; placeholder seed, record the real one
ALLOCATION_SEED = 2026         # placeholder: record real seed
PER_GROUP = 25  # 50 participants, 25 per group (13 + 12 across the group's two forms)
SPARES_PER_FORM = 1  # 4 spares, one per form (two per group), held by W4 (TASK_SPLIT section 2)
PRACTICE_ID = "PR"
SCORED_IDS = ["C%02d" % i for i in range(1, 11)]
FORM_TITLE = "Understanding an AI Model's Predictions: Class Research Activity"
FORBIDDEN_PHRASES = ["probability", "base value", "capacity boundary",
                     "predicted class", "final score", "score", "correct answer"]

DECISIONS_PENDING = [
    "Survey 1 is dropped. No background questions appear in this form.",
    "Role item S6.1 is included (default; confirm in W2.1).",
    "Q3 to Q5 are required (default; question bank item 10).",
    "A wrong practice answer makes the runner re-read the legend and continue (default; item 4).",
    "Participants are not told the flag mix (default; item 8).",
    "Four forms: each group sees the seeded order (Form 1 and Form 3) and its reverse (Form 2 and Form 4). Agreed by the team on 30 Oct; TASK_SPLIT, HANDOFF and the protocol JSON updated.",
    "Order seed and allocation seed are placeholders. Total is 50 participants (25 per group, 13 or 12 per form).",
    "Consent has no retention date, withdrawal deadline or named contact (team decision, 30 Oct). The person who sent the form is the contact.",
    "Economic indicators are shown on profile cards (UCI cases are Portuguese students).",
]

CONSENT_TEXT = "\n\n".join([
    "What this is\nYou are invited to take part in a short class research activity about how people understand the predictions of an AI model. It takes about 30 minutes.",
    "What you will do\n• Look at 11 student profiles (1 practice and 10 scored).\n• For each one, guess whether the model flagged the student as at risk (yes or no).\n• Rate how confident you are.\n• Write three short answers.",
    "What we record\n• Your answers, your confidence ratings and your total session time.\n• They are stored under a random participant code.\n• We do not ask for your name or any identifying information. Please do not type any such information into your answers.",
    "Your choice\n• Taking part is voluntary, and you must be 18 or older.\n• You can stop at any time without penalty.\n• Taking part, or not, will not affect your grades, standing, employment or any services.",
    "How your data is used\n• Your responses are kept in access-restricted storage that only the research team can open.\n• They are used only for this course project, and reported only as group totals or paraphrased comments.",
    "If you want to withdraw\nTo withdraw after you submit, send your participant code to the person who sent you this form. Later we remove the codes and combine the responses into group results. After that, your answers can no longer be separated out.",
    "Risk & Benefits\nThe risks are no greater than everyday computer use. There is no direct benefit to you.",
    "Questions\nPlease contact the person who sent you this form.",
    "On this page and the next, you will be asked to confirm that you are 18 or older and that you agree to take part.",
])
# Instruction page (W4.2 text, 30 Oct). Each block shows as a heading plus text in Google Forms.
INSTRUCTION_BLOCKS = [
    ("What you will see", "You will see 11 student profiles: 1 practice case, then 10 scored cases. For each profile, a machine-learning model has already predicted whether that student is at high risk of dropping out after their first semester."),
    ("Your task", "Guess what the model predicted. We are not asking what you think will happen to the student."),
]
FOR_EACH_CASE = ("For each case", "\u2022 Choose Yes if you think the model flagged the student as at risk, or No if you think it did not.\n\u2022 Rate your confidence from 1 (not at all) to 5 (very).\n\u2022 Answer three short questions in your own words.")
GOOD_TO_KNOW = ("Good to know", "\u2022 There are no right or wrong answers to the three written questions. We want your honest reasoning.\n\u2022 Please do not type names or any identifying details.\n\u2022 You will not be told whether your answers are correct during the session.\n\u2022 Please work on your own, and do not discuss the cases with anyone until the session is over.\n\u2022 You can stop at any time without penalty.")
READY_LINE = "When you are ready, continue to the practice case."
INSTR_A = ("Each profile shows the student's recorded information only. "
           "Use it to decide what you think the model will do.")
INSTR_B = ("Each profile shows the student's recorded information and a chart. Bars pointing right made the model MORE worried about this student. "
           "Bars pointing left made it LESS worried. A longer bar means a bigger effect. "
           "This shows how the model works, not why students really drop out. The chart shows no numbers, "
           "scores or final answer. Use it together with the profile to decide what you think the model will do.")
HELPER_TEXT = ("Please do not type names or any information that could identify a person. "
               "Q4 asks for advice to the student as an officer would give it; it is not a prediction of what the "
               "student will do.")
DEBRIEF = ("Thank you for taking part. Your answers will be stored under your participant code only. The study compares "
           "two groups that saw different material. The chart describes model behaviour, not causes. "
           "To withdraw, send your participant code to the person who sent you this form.")
Q4_HELP = "Please do not type any names."
DECLINE_TEXT = "Thank you. You chose not to take part, so your answers will not be used. You can close this page now."
FINISH_TEXT = "Please press Submit below to send your answers. They are not sent until you do."
# Shown by Google after Submit on either path, so it must suit completers and decliners alike.
CONFIRMATION = "Thank you. You can close this page now."


def load_uci():
    with open(DATA, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = [h.strip() for h in next(reader)]
        rows = [r for r in reader if r]
    return header, rows


def profile_fields(header):
    return [h for h in header if h != "Target" and not h.lower().startswith("curricular units 2nd sem")]


def validation_ids():
    with open(SPLIT, newline="", encoding="utf-8") as f:
        return [int(r["source_row_id"]) for r in csv.DictReader(f) if r["split"] == "validation"]


def build_cases(header, rows):
    fields = set(profile_fields(header))
    chosen = random.Random(FIXTURE_SEED).sample(validation_ids(), len(SCORED_IDS) + 1)
    cases, lookup = [], {}
    for case_id, src in zip([PRACTICE_ID] + SCORED_IDS, chosen):
        values = rows[src]
        profile = [{"field": h, "value": v.strip()} for h, v in zip(header, values) if h in fields]
        cases.append({"case_id": case_id, "profile": profile})
        lookup[case_id] = {"source_row_id": src}
    pack = {"pack_status": "FIXTURE: dummy cases from the validation split. Not for scoring.",
            "cases": cases}
    return pack, lookup


def profile_text(case):
    return labels.profile_text(case)


def item_mc(item_id, title, choices, goto_map=None):
    return {"id": item_id, "type": "multiple_choice", "title": title, "required": True,
            "choices": choices, "goto_map": goto_map or {}}


def item_text(item_id, kind, title, required=True, help_text=None):
    item = {"id": item_id, "type": kind, "title": title, "required": required}
    if help_text:
        item["help"] = help_text
    return item


def item_block(item_id, title, text):
    return {"id": item_id, "type": "text_block", "title": title, "text": text}


def section(sec_id, title, description, items):
    return {"id": sec_id, "title": title, "description": description, "items": items}


def profile_items(case, group):
    items = [item_block(case["case_id"] + ".profile", "Student profile", profile_text(case))]
    if group == "B":
        items.append(item_block(case["case_id"] + ".chart", "Contribution chart",
                                "[TBD: chart image rendered by W5.3; placeholder in fixture]"))
    return items


def question_items(case_id):
    return [
        item_mc(case_id + ".Q1", "Do you think the model flagged this student?",
                ["Yes", "No"]),
        {"id": case_id + ".Q2", "type": "scale", "title": "How sure are you?",
         "required": True, "low": 1, "high": 5,
         "low_label": "Not sure at all", "high_label": "Very sure"},
        item_text(case_id + ".Q3", "paragraph",
                  "What made you think so?"),
        item_text(case_id + ".Q4", "paragraph", "If you were the support officer, what would you say or suggest to this student?", help_text=Q4_HELP),
        item_text(case_id + ".Q5", "paragraph", "What else would you want to know about this student?"),
    ]


def comprehension_items():
    return [
        item_mc("P.B1", "In the chart, a bar pointing right means the model became:",
                ["More worried about this student", "Less worried about this student", "No change", "Cannot tell"]),
        item_mc("P.B2", "In the chart, a longer bar means:",
                ["A bigger effect", "A smaller effect", "The student is more likely to drop out", "Cannot tell"]),
    ]


FORM_LABELS = {"A1": "Form 1", "A2": "Form 2", "B1": "Form 3", "B2": "Form 4"}


def instruction_items(group):
    blocks = INSTRUCTION_BLOCKS + [("What each profile shows", INSTR_B if group == "B" else INSTR_A),
                                   FOR_EACH_CASE, GOOD_TO_KNOW]
    items = [item_block("S3.%d" % i, title, text) for i, (title, text) in enumerate(blocks, 1)]
    items.append(item_block("S3.%d" % (len(blocks) + 1), READY_LINE, ""))
    return items


def build_variant(group, index, seed, order, cases_by_id):
    variant_id = "%s%d" % (group, index)
    form_label = FORM_LABELS[variant_id]
    sections = [
        section("S0", "Welcome", "This is a short class research activity. Please read the consent information on the next page before you start.", []),
        section("S1", "Research information and consent", "", [
            item_block("S1.0", "Consent information", CONSENT_TEXT),
            item_mc("S1.1", "I have read the information above and I agree to take part.",
                    ["I agree", "I do not agree"], {"I do not agree": "DECLINE"}),
        ]),
        section("S1b", "Age check", "", [
            item_mc("S1.2", "I confirm that I am 18 years or older.", ["Yes", "No"], {"No": "DECLINE"}),
        ]),
        section("S2", "Participant code", "This code is already filled in from your link. Do not change it. Please note it down in case you want to withdraw later.", [
            item_text("S2.1", "short_text", "Your participant code"),
        ]),
        section("S3", "Instructions", "", instruction_items(group)),
    ]
    practice_items = profile_items(cases_by_id[PRACTICE_ID], group)
    if group == "B":
        practice_items += comprehension_items()
    practice_items += question_items(PRACTICE_ID)
    sections.append(section("S4", "Practice profile (not scored)", "", practice_items))
    for pos, case_id in enumerate(order, 1):
        sections.append(section("S5.%d" % pos, "Student profile %d of 10" % pos, "",
                                profile_items(cases_by_id[case_id], group) + question_items(case_id)))
    sections.append(section("S6", "Closing", "", [
        item_mc("S6.1", "Which best describes you?", ["Student", "Staff or adviser", "Other"]),
    ]))
    finish = section("COMPLETE", "Finish", FINISH_TEXT + "\n\n" + DEBRIEF, [])
    finish["after"] = "SUBMIT"  # completers submit here and never reach the decline page
    sections.append(finish)
    sections.append(section("DECLINE", "Thank you", DECLINE_TEXT, []))
    return {"variant_id": variant_id, "form_label": form_label, "group": group, "order_seed": seed,
            "scored_order": order, "sections": sections}


def build_assignment(variant_ids):
    rng = random.Random(ALLOCATION_SEED)
    slots = []
    half = PER_GROUP // 2 + PER_GROUP % 2  # 13 forward-order slots, 12 reversed per group
    for group in ["A", "B"]:
        slots += [group + "1"] * half + [group + "2"] * (PER_GROUP - half)
    rng.shuffle(slots)
    codes, rows = set(), []

    def new_code():
        code = "P-%04d" % rng.randint(1000, 9999)
        while code in codes:
            code = "P-%04d" % rng.randint(1000, 9999)
        codes.add(code)
        return code

    for n, variant in enumerate(slots, 1):
        rows.append({"slot": n, "participant_code": new_code(), "variant_id": variant,
                     "group": variant[0], "role": "main"})
    # Spares are drawn after the main slots, so the main 50 codes do not change.
    # A spare replaces a non-completer on the same form (TASK_SPLIT section 2).
    for variant in sorted(variant_ids):
        for _ in range(SPARES_PER_FORM):
            rows.append({"slot": len(rows) + 1, "participant_code": new_code(), "variant_id": variant,
                         "group": variant[0], "role": "spare"})
    return rows


def build_all():
    header, rows = load_uci()
    pack, lookup = build_cases(header, rows)
    cases_by_id = {c["case_id"]: c for c in pack["cases"]}
    variants = []
    seed = ORDER_SEEDS[0]
    forward = list(SCORED_IDS)
    random.Random(seed).shuffle(forward)
    orders = {1: forward, 2: list(reversed(forward))}
    for group in ["A", "B"]:
        for index in (1, 2):
            variants.append(build_variant(group, index, seed, orders[index], cases_by_id))
    spec = {"spec_status": "FIXTURE 0.1 (dummy cases, placeholders)", "form_title": FORM_TITLE,
            "debrief": DEBRIEF, "confirmation": CONFIRMATION, "decisions_pending": DECISIONS_PENDING,
            "profile_groups": [{"heading": h, "fields": [{"field": f, "label": l, "kind": k} for f, l, k in fs]} for h, fs in labels.GROUPS],
            "variants": variants}
    return pack, lookup, spec, build_assignment([v["variant_id"] for v in variants])


def write_outputs(pack, lookup, spec, assignment):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "case_pack_fixture.json", "w", encoding="utf-8") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
    with open(OUT / "private_lookup_fixture.json", "w", encoding="utf-8") as f:
        json.dump(lookup, f, indent=2)
    with open(OUT / "form_spec.json", "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    with open(OUT / "assignment_fixture.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["slot", "participant_code", "variant_id", "group", "role"])
        w.writeheader()
        w.writerows(assignment)


def main():
    pack, lookup, spec, assignment = build_all()
    write_outputs(pack, lookup, spec, assignment)
    print("Wrote outputs to", OUT)
    print("Variants:", [v["variant_id"] for v in spec["variants"]])
    print("Assignment rows:", len(assignment))


if __name__ == "__main__":
    main()
