"""W5.8: build a seeded assignment CSV for the W2 forms and response transform."""
from __future__ import annotations

import argparse
import csv
import hashlib
import random
import sys
from pathlib import Path

N_BLOCKS = 12
VARIANT_INFO = {
    "A1": ("A", "seeded"),
    "A2": ("A", "reverse"),
    "B1": ("B", "seeded"),
    "B2": ("B", "reverse"),
}
CODE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
PILOT_CODE = "PILOT-01"
PILOT_FORM = "B1"
FIELDS = ["slot", "participant_code", "variant_id", "group", "role"]


def _row(slot: int, code: str, variant: str, role: str) -> dict:
    return {
        "slot": slot,
        "participant_code": code,
        "variant_id": variant,
        "group": VARIANT_INFO[variant][0],
        "role": role,
    }


def build_assignment(seed: int) -> list[dict]:
    rng = random.Random(seed)
    variants: list[str] = []
    for _ in range(N_BLOCKS):
        block = list(VARIANT_INFO)
        rng.shuffle(block)
        variants.extend(block)
    tail = ["A1", "B2"]
    rng.shuffle(tail)
    variants.extend(tail)
    used: set[str] = {PILOT_CODE}

    def new_code() -> str:
        while True:
            code = "P" + "".join(rng.choice(CODE_ALPHABET) for _ in range(4))
            if code not in used:
                used.add(code)
                return code

    rows = [_row(i, new_code(), variant, "main")
            for i, variant in enumerate(variants, start=1)]
    for variant in VARIANT_INFO:
        rows.append(_row(len(rows) + 1, new_code(), variant, "spare"))
    rows.append(_row(len(rows) + 1, PILOT_CODE, PILOT_FORM, "pilot"))
    return rows


def validate(rows: list[dict]) -> None:
    """Raise ValueError if the assignment breaks the W2 handoff contract."""
    for row in rows:
        if set(row) != set(FIELDS):
            raise ValueError("assignment columns must match the W2 contract")
        if row["variant_id"] not in VARIANT_INFO:
            raise ValueError(f"unknown form variant: {row['variant_id']}")
        if row["group"] != VARIANT_INFO[row["variant_id"]][0]:
            raise ValueError(f"slot {row['slot']}: group does not match variant")
        if row["role"] not in ("main", "spare", "pilot"):
            raise ValueError(f"slot {row['slot']}: unknown role")
        if not isinstance(row["participant_code"], str) or not row["participant_code"].strip():
            raise ValueError("participant codes must be nonempty strings")
    main = [r for r in rows if r["role"] == "main"]
    spare = [r for r in rows if r["role"] == "spare"]
    pilots = [r for r in rows if r["role"] == "pilot"]
    if len(main) != 50 or len(spare) != 4 or len(pilots) != 1:
        raise ValueError("expected 50 main + 4 spare + 1 pilot")
    if [r["slot"] for r in rows] != list(range(1, 56)):
        raise ValueError("slots must be in order from 1 to 55")
    codes = [r["participant_code"] for r in rows]
    if len(set(codes)) != len(codes):
        raise ValueError("participant codes are not unique")
    if pilots[0]["participant_code"] != PILOT_CODE or pilots[0]["variant_id"] != PILOT_FORM:
        raise ValueError("pilot must be PILOT-01 on B1")
    for group in "AB":
        if sum(r["group"] == group for r in main) != 25:
            raise ValueError(f"group {group} must have 25 main slots")
    for order in ("seeded", "reverse"):
        if sum(VARIANT_INFO[r["variant_id"]][1] == order for r in main) != 25:
            raise ValueError(f"order {order} must have 25 main slots")
    for variant in VARIANT_INFO:
        if sum(r["variant_id"] == variant for r in main) not in (12, 13):
            raise ValueError(f"variant {variant} must have 12 or 13 main slots")
    if sorted(r["variant_id"] for r in spare) != sorted(VARIANT_INFO):
        raise ValueError("spares must be exactly one per form variant")


def write_csv(rows: list[dict], path: Path) -> str:
    validate(rows)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rules_text(seed: int, sha256: str) -> str:
    return f"""SEALED ASSIGNMENT LIST - human study (W5.8)
Seed: {seed}
CSV SHA-256: {sha256}
Rebuild: python scripts/make_assignment_list.py --seed {seed}
(Use the same Python version; the CSV SHA-256 must match.)

Contents: 50 main slots (25 per group, 25 seeded / 25 reverse),
4 spares (one per form) and PILOT-01 on B1 (not counted).
Forms: A1/A2 = Group A; B1/B2 = Group B; 1 = seeded, 2 = reverse.

HANDOFF
Upload THIS CSV as the assignment file for forms/render_forms.gs.
Use THIS SAME CSV with forms/transform_responses.py --assignment.
It replaces the builder's default assignment for that run; do not mix lists.
This block-randomised list has different codes and allocation from the W2
builder, even with the same seed. Agree and seal it before distributing links.
Do not replace an assignment after links have been distributed.

LINKS AND REPLACEMENT
Only W4 and the designated reviewer hold the list, seed and hash.
W4 gives recruiters the next unused MAIN link in slot order.
The PILOT-01 link is for the pilot only; delete its response afterwards.
Recruiters send one link per person, never in group chats, and never write
codes next to names. Keep the send log separately, using codes only.
For a non-completer (no submission by Tue 17 Nov 23:59, withdrawal or
incomplete response), the next recruit inherits that empty slot's group
and form. Use the spare for that same form only when a slot is empty,
choosing the group that keeps totals closest to balanced.
Log and exclude incomplete responses.
Minimum: 40 completed responses with at least 18 per group.
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", default="data/human_study")
    ap.add_argument("--check", action="store_true", help="validate without writing files")
    args = ap.parse_args(argv)
    rows = build_assignment(args.seed)
    validate(rows)
    if args.check:
        print("OK: 50 main + 4 spare + 1 pilot; 25/25 main groups.")
        return 0
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    sha = write_csv(rows, out / "assignment_list.csv")
    (out / "assignment_list_RULES.txt").write_text(rules_text(args.seed, sha), encoding="utf-8")
    print(f"Wrote {out / 'assignment_list.csv'} and assignment_list_RULES.txt")
    print(f"SHA-256: {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
