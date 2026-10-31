"""Tests for scripts/make_assignment_list.py (W5.8). Uses a dummy seed only."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "make_assignment_list",
    Path(__file__).resolve().parents[1] / "scripts" / "make_assignment_list.py",
)
mal = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(mal)

DUMMY_SEED = 12345


class AssignmentListTests(unittest.TestCase):
    def test_counts_and_validation(self):
        rows = mal.build_assignment(DUMMY_SEED)
        mal.validate(rows)
        self.assertEqual(len(rows), 54)

    def test_reproducible_from_seed(self):
        self.assertEqual(mal.build_assignment(DUMMY_SEED), mal.build_assignment(DUMMY_SEED))
        self.assertNotEqual(mal.build_assignment(DUMMY_SEED), mal.build_assignment(DUMMY_SEED + 1))

    def test_prefix_stays_balanced(self):
        main = [r for r in mal.build_assignment(DUMMY_SEED) if r["is_spare"] == "no"]
        diff = 0
        for r in main:
            diff += 1 if r["group"] == "A" else -1
            self.assertLessEqual(abs(diff), 2)

    def test_one_spare_per_form(self):
        spare = [r for r in mal.build_assignment(DUMMY_SEED) if r["is_spare"] == "yes"]
        self.assertEqual(sorted(r["variant"] for r in spare), ["A1", "A2", "B1", "B2"])

    def test_validate_rejects_tampering(self):
        rows = mal.build_assignment(DUMMY_SEED)
        rows[0]["participant_code"] = rows[1]["participant_code"]
        with self.assertRaises(ValueError):
            mal.validate(rows)

    def test_files_written_and_hash_stable(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            self.assertEqual(mal.main(["--seed", str(DUMMY_SEED), "--out", d1]), 0)
            self.assertEqual(mal.main(["--seed", str(DUMMY_SEED), "--out", d2]), 0)
            self.assertEqual((Path(d1) / "assignment_list.csv").read_bytes(),
                             (Path(d2) / "assignment_list.csv").read_bytes())
            self.assertIn("REPLACEMENT RULE", (Path(d1) / "assignment_list_RULES.txt").read_text())


if __name__ == "__main__":
    unittest.main()