
from __future__ import annotations

import argparse
import csv
import hashlib
import random
import sys
from pathlib import Path

N_BLOCKS = 12  # 12 blocks x 4 = 48 slots, plus 2 tail slots = 50
VARIANT_INFO = {
    "A1": ("A", "seeded"),
    "A2": ("A", "reverse"),
    "B1": ("B", "seeded"),
    "B2": ("B", "reverse"),
}
# No 0/O, 1/I/L, so codes are easy to read and type.
CODE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
FIELDS = [
    "slot", "participant_code", "group", "variant", "case_order",
    "is_spare", "recruiter", "date_sent", "status",
]


def _row(slot: str, code: str, variant: str, is_spare: bool) -> dict:
    group, case_order = VARIANT_INFO[variant]
    return {
        "slot": slot,
        "participant_code": code,
        "group": group,
        "variant": variant,
        "case_order": case_order,
        "is_spare": "yes" if is_spare else "no",
        "recruiter": "",   # filled in by W4 (recruiter number only, no names)
        "date_sent": "",
        "status": "",
    }


def build_assignment(seed: int) -> list[dict]:
    rng = random.Random(seed)

    variants: list[str] = []
    for _ in range(N_BLOCKS):
        block = list(VARIANT_INFO)
        rng.shuffle(block)
        variants.extend(block)
    tail = ["A1", "B2"]  # makes A1=13, B2=13 -> 25/25 groups and orders
    rng.shuffle(tail)
    variants.extend(tail)

    used: set[str] = set()

    def new_code() -> str:
        while True:
            code = "P" + "".join(rng.choice(CODE_ALPHABET) for _ in range(4))
            if code not in used:
                used.add(code)
                return code

    rows = [_row(f"{i:02d}", new_code(), v, False)
            for i, v in enumerate(variants, start=1)]
    # one spare per form, so two per group
    rows += [_row(f"S{j}", new_code(), v, True)
             for j, v in enumerate(VARIANT_INFO, start=1)]
    return rows


def validate(rows: list[dict]) -> None:
    """Raise ValueError if the list breaks any rule in TASK_SPLIT.md (W5.8)."""
    main = [r for r in rows if r["is_spare"] == "no"]
    spare = [r for r in rows if r["is_spare"] == "yes"]
    if len(main) != 50 or len(spare) != 4:
        raise ValueError(f"expected 50 main + 4 spare, got {len(main)} + {len(spare)}")
    codes = [r["participant_code"] for r in rows]
    if len(set(codes)) != len(codes):
        raise ValueError("participant codes are not unique")
    for g in "AB":
        n = sum(r["group"] == g for r in main)
        if n != 25:
            raise ValueError(f"group {g} has {n} main slots, expected 25")
    for o in ("seeded", "reverse"):
        n = sum(r["case_order"] == o for r in main)
        if n != 25:
            raise ValueError(f"order {o} has {n} main slots, expected 25")
    if sorted(r["variant"] for r in spare) != sorted(VARIANT_INFO):
        raise ValueError("spares must be exactly one per form variant")
    for r in rows:
        if VARIANT_INFO[r["variant"]] != (r["group"], r["case_order"]):
            raise ValueError(f"slot {r['slot']}: group/order do not match variant")


def write_csv(rows: list[dict], path: Path) -> str:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rules_text(seed: int, sha256: str) -> str:
    return f"""SEALED ASSIGNMENT LIST - human study (task W5.8)
=================================================
Seed:        {seed}
CSV SHA-256: {sha256}
Rebuild:     python scripts/make_assignment_list.py --seed {seed}
             (same Python version; the SHA-256 above must match)

Contents: 50 main slots (25 Group A / 25 Group B; 25 seeded order / 25 reverse)
          + 4 spare slots S1-S4 (one per form: A1, A2, B1, B2).
Forms:    A1/A2 = Group A, seeded order / exact reverse order
          B1/B2 = Group B, seeded order / exact reverse order

HOW LINKS ARE HANDED OUT
1. Held only by the W4 coordinator (and the W4 reviewer). Recruiters never see
   this list and never choose or swap a participant's group or form.
2. W4 gives each recruiter the NEXT UNUSED pre-filled link in slot order
   (01, 02, 03, ...). Slots are in permuted blocks, so groups stay balanced.
3. A recruiter sends the link only. Never write a code next to a person's name;
   the send log holds codes only.

REPLACEMENT RULE (TASK_SPLIT.md section 2)
4. If a participant does not complete (no submission by Tue 17 Nov 23:59,
   withdrawal, or incomplete response), the next recruited participant
   INHERITS THAT EMPTY SLOT'S group and form.
5. A spare is used ONLY when a slot is empty, choosing the group that keeps the
   totals closest to balanced.
6. Incomplete responses are logged and excluded.
7. Minimum: 40 complete responses with at least 18 in each group.
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", default="data/human_study")
    ap.add_argument("--check", action="store_true",
                    help="build in memory and validate only; write nothing")
    args = ap.parse_args(argv)

    rows = build_assignment(args.seed)
    validate(rows)
    if args.check:
        print("OK: list valid (50 main + 4 spare, 25/25).")
        return 0

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    sha = write_csv(rows, out / "assignment_list.csv")
    (out / "assignment_list_RULES.txt").write_text(rules_text(args.seed, sha), encoding="utf-8")
    print(f"Wrote {out/'assignment_list.csv'} and assignment_list_RULES.txt")
    print(f"SHA-256: {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())