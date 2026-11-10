#!/usr/bin/env python3
"""W5.3 - image renderer for the study forms.

Reads a case pack (docs/case_pack_contract.md) and writes images, one per case:
  chart_<case_id>.png     the Group B contribution chart (5 bars: direction and length only)
  profile_<case_id>.png   optional (--profiles): the profile card as one image

Usage (from the repo root):
  python forms/render_images.py forms/out/case_pack_fixture.json
  python forms/render_images.py forms/out/case_pack_fixture.json --profiles
  python forms/render_images.py <pack.json> --out some/folder --scale case

Default output folder: forms/out/images_<fixture|study>/ (git-ignored, like forms/out).
Study images show real test cases: never commit them (rule 4).

What a chart draws: plain bar names, bars pointing left (less worried) or right (more
worried), longer = bigger effect, and a small legend. It never draws a number, the base
value, a probability, a score, the capacity boundary, a class name or the case ID.
check_chart_text() refuses to save a chart whose text breaks this.
"""
import argparse
import json
import re
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

import case_pack  # noqa: E402  (forms/case_pack.py; this folder is on sys.path when run as a script)
import labels  # noqa: E402

DPI = 200
MORE_COLOR = "#D55E00"   # orange: more worried (right). Colour-blind safe pair, plus text and side.
LESS_COLOR = "#0072B2"   # blue: less worried (left)
TITLE = "The five factors with the biggest effect\non the model's view of this student"
LEGEND_LEFT = "\u25c4 Less worried\nabout this student"
LEGEND_RIGHT = "More worried \u25ba\nabout this student"
SIZE_NOTE = "A longer bar means a bigger effect."

# Anything matching these must never appear as text in a chart (W5.3 done-when).
FORBIDDEN_IN_CHART = [
    r"\d", r"probab", r"score", r"\bbase", r"expected", r"flag", r"capacity", r"threshold",
    r"boundary", r"\bclass", r"drop\s?out", r"graduat", r"target", r"predict", r"top[\s-]?20",
    r"\brank", r"\brisk",
]


def check_chart_text(texts):
    """Raise ValueError if any text drawn on a chart could reveal the model output."""
    for t in texts:
        for pattern in FORBIDDEN_IN_CHART:
            if re.search(pattern, t, flags=re.IGNORECASE):
                raise ValueError("chart text %r matches forbidden pattern %r" % (t, pattern))


def render_chart(contributions, out_path, scale_max):
    """Draw one contribution chart. Returns the list of texts drawn (for tests and checks).

    scale_max: bar value that reaches the edge of the chart. Use one shared value for a
    whole pack so that "longer = bigger effect" holds across cases.
    """
    bars = list(contributions)
    values = [float(b["value"]) for b in bars]
    names = [textwrap.fill(b["label"], 30) for b in bars]
    texts = names + [TITLE, LEGEND_LEFT, LEGEND_RIGHT, SIZE_NOTE]
    check_chart_text(texts)

    limit = max(float(scale_max), 1e-9) * 1.05
    n = len(bars)
    ys = list(range(n))[::-1]  # largest bar on top

    fig, ax = plt.subplots(figsize=(8, 4.4), dpi=DPI)
    ax.barh(ys, values, color=[MORE_COLOR if v > 0 else LESS_COLOR for v in values], height=0.6)
    ax.axvline(0, color="#555555", linewidth=1)
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_yticks(ys)
    ax.set_yticklabels(names, fontsize=11)
    ax.set_xticks([])  # no numbers anywhere
    ax.tick_params(axis="y", length=0)
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.set_title(TITLE, fontsize=12, pad=12)
    ax.text(0.25, -0.05, LEGEND_LEFT, transform=ax.transAxes, ha="center", va="top",
            fontsize=10.5, color=LESS_COLOR)
    ax.text(0.75, -0.05, LEGEND_RIGHT, transform=ax.transAxes, ha="center", va="top",
            fontsize=10.5, color=MORE_COLOR)
    fig.text(0.5, 0.025, SIZE_NOTE, ha="center", fontsize=10, color="#555555")
    fig.subplots_adjust(left=0.36, right=0.97, top=0.80, bottom=0.24)
    fig.savefig(out_path, dpi=DPI, metadata={"Software": None})
    plt.close(fig)
    return texts


# ---- profile card ----------------------------------------------------------------------
CARD_COL_W, CARD_GUTTER, CARD_MARGIN = 5.4, 0.4, 0.35
HEADER_H, LINE_H, ROW_PAD, BLOCK_GAP, WRAP = 0.45, 0.18, 0.09, 0.25, 34


def render_profile(profile, out_path):
    """Draw the profile card (same words as the form text) as one image."""
    values = {x["field"]: x["value"] for x in profile}
    blocks = []
    for title, fields in labels.GROUPS:
        rows = []
        for field, label, kind in fields:
            text = str(labels.format_value(kind, field, values[field])) if field in values else "-"
            rows.append((label, textwrap.wrap(text, WRAP) or ["-"]))
        blocks.append((title, rows))

    def block_height(rows):
        return HEADER_H + sum(len(lines) * LINE_H + ROW_PAD for _, lines in rows) + BLOCK_GAP

    columns, heights = [[], []], [0.0, 0.0]
    for block in blocks:  # fill the shorter column first, keep the order inside each column
        i = 0 if heights[0] <= heights[1] else 1
        columns[i].append(block)
        heights[i] += block_height(block[1])

    width = 2 * CARD_MARGIN + 2 * CARD_COL_W + CARD_GUTTER
    height = max(heights) + 2 * CARD_MARGIN
    fig = plt.figure(figsize=(width, height), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")
    ax.add_patch(Rectangle((0.06, 0.06), width - 0.12, height - 0.12, fill=False, edgecolor="#CCCCCC"))
    for i, column in enumerate(columns):
        x0 = CARD_MARGIN + i * (CARD_COL_W + CARD_GUTTER)
        y = CARD_MARGIN
        for title, rows in column:
            ax.text(x0, y, title, fontsize=12, fontweight="bold", va="top", color="#222222")
            ax.plot([x0, x0 + CARD_COL_W], [y + 0.31, y + 0.31], color="#BBBBBB", linewidth=0.8)
            y += HEADER_H
            for label, lines in rows:
                ax.text(x0, y, label, fontsize=9.5, va="top", color="#444444")
                ax.text(x0 + CARD_COL_W, y, "\n".join(lines), fontsize=9.5, va="top", ha="right",
                        multialignment="right", color="#111111")
                y += len(lines) * LINE_H + ROW_PAD
            y += BLOCK_GAP
    fig.savefig(out_path, dpi=DPI, metadata={"Software": None})
    plt.close(fig)


# ---- whole pack ------------------------------------------------------------------------
def pack_scale_max(pack):
    return max(abs(float(b["value"])) for c in pack["cases"] for b in c["contributions"])


def render_pack(pack_path, out_dir=None, profiles=False, scale="pack"):
    """Validate the pack, then write chart_<id>.png (and profile_<id>.png) for every case."""
    pack = json.loads(Path(pack_path).read_text(encoding="utf-8"))
    problems = case_pack.validate_pack(pack)
    if problems:
        raise ValueError("case pack does not follow the format:\n  " + "\n  ".join(problems))
    out = Path(out_dir) if out_dir else Path(__file__).resolve().parent / "out" / ("images_" + pack["pack_kind"])
    out.mkdir(parents=True, exist_ok=True)
    shared = pack_scale_max(pack)
    written = []
    for case in pack["cases"]:
        scale_max = shared if scale == "pack" else max(abs(float(b["value"])) for b in case["contributions"])
        path = out / case["chart_file"]
        render_chart(case["contributions"], path, scale_max)
        written.append(path)
        if profiles:
            path = out / ("profile_%s.png" % case["case_id"])
            render_profile(case["profile"], path)
            written.append(path)
    return written, pack


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render study-form images from a case pack (W5.3).")
    ap.add_argument("pack", help="case_pack_<fixture|study>.json")
    ap.add_argument("--out", help="output folder (default forms/out/images_<kind>)")
    ap.add_argument("--profiles", action="store_true", help="also draw profile_<case_id>.png")
    ap.add_argument("--scale", choices=["pack", "case"], default="pack",
                    help="pack: one shared scale for all charts (default); case: each chart fills its width")
    args = ap.parse_args(argv)
    written, pack = render_pack(args.pack, args.out, args.profiles, args.scale)
    for path in written:
        print("wrote", path)
    if pack.get("contributions_placeholder"):
        print("NOTE: these bars are placeholders (fixture). Do not show them as results.")
    print("PASS: %d images, no forbidden text in any chart" % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())