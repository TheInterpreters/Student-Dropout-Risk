"""Tests for forms/render_images.py (W5.3). Uses made-up bars only."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "forms"))

import render_images as ri  # noqa: E402

BARS = [
    {"bar_id": "a", "label": "Attendance", "value": -0.10},
    {"bar_id": "b", "label": "Admission route", "value": -0.09},
    {"bar_id": "c", "label": "First-semester progress (passed units, grade)", "value": 0.07},
    {"bar_id": "d", "label": "Father's job", "value": -0.02},
    {"bar_id": "e", "label": "GDP growth (%)", "value": 0.01},
]


class RenderImagesTests(unittest.TestCase):
    def test_chart_is_written_and_has_no_digits(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "chart_X.png"
            texts = ri.render_chart(BARS, path, scale_max=0.10)
            self.assertEqual(path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            self.assertGreater(path.stat().st_size, 5000)
        self.assertFalse(any(ch.isdigit() for t in texts for ch in t))

    def test_chart_is_reproducible(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / "a.png", Path(d) / "b.png"
            ri.render_chart(BARS, a, 0.10)
            ri.render_chart(BARS, b, 0.10)
            self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_forbidden_text_is_refused(self):
        for bad in ["Probability of dropout", "Model score", "Base value", "Flagged by the model",
                    "Top 20% capacity", "Rank 3", "Class: Graduate", "Case 7"]:
            with self.assertRaises(ValueError, msg=bad):
                ri.check_chart_text([bad])
        ri.check_chart_text(["Attendance", "Unemployment rate (%)", "Tuition fees paid up to date"])

    def test_bad_label_stops_rendering(self):
        bars = [dict(b) for b in BARS]
        bars[0]["label"] = "Predicted probability"
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                ri.render_chart(bars, Path(d) / "x.png", 0.10)
            self.assertFalse((Path(d) / "x.png").exists())

    def test_shared_scale_is_largest_bar_in_pack(self):
        pack = {"cases": [{"contributions": BARS},
                          {"contributions": [{"value": 0.3}, {"value": -0.5}]}]}
        self.assertEqual(ri.pack_scale_max(pack), 0.5)

    def test_fixture_pack_renders_11_charts_and_profiles(self):
        fixture = ROOT / "forms" / "out" / "case_pack_fixture.json"
        if not fixture.exists():
            self.skipTest("build the fixture first: python3 forms/build_spec.py")
        with tempfile.TemporaryDirectory() as d:
            written, _ = ri.render_pack(fixture, d, profiles=True)
            names = sorted(p.name for p in written)
        self.assertEqual(len([n for n in names if n.startswith("chart_")]), 11)
        self.assertEqual(len([n for n in names if n.startswith("profile_")]), 11)


if __name__ == "__main__":
    unittest.main()