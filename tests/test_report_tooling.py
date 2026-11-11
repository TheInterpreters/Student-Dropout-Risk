import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd

from scripts import audit_human_study_privacy as privacy
from scripts import build_report_assets as assets
from scripts import check_w1_refit_identity as identity
from scripts import run_enrolled_sensitivity as enrolled
from scripts import verify_release_readiness as release

FIELDS = ("rationale_freetext", "intervention_freetext", "missing_info_freetext")


def write_responses(path, texts):
    rows = [{"participant_id": f"P{i}", **{f: t for f in FIELDS}} for i, t in enumerate(texts)]
    pd.DataFrame(rows).to_csv(path, index=False)


class PrivacyAuditTests(unittest.TestCase):
    def test_clean_text_passes_and_identifiers_are_flagged(self):
        with tempfile.TemporaryDirectory() as folder:
            clean = Path(folder) / "clean.csv"
            write_responses(clean, ["low grades in first semester", "offer tutoring"])
            self.assertEqual(privacy.audit(clean)["status"], "pass")
            risky = Path(folder) / "risky.csv"
            write_responses(risky, ["email me at someone@example.com", "call +66 81 234 5678",
                                    "see www.example.org", "my name is Test"])
            result = privacy.audit(risky)
            self.assertEqual(result["status"], "manual_review_required")
            self.assertTrue(all(result["pattern_match_rows"][k] >= 1 for k in privacy.PATTERNS))

    def test_blank_text_requires_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "blank.csv"
            write_responses(path, [""])
            self.assertEqual(privacy.audit(path)["status"], "manual_review_required")


class RefitIdentityTests(unittest.TestCase):
    def test_identical_and_tiny_differences_pass(self):
        p = np.linspace(0.01, 0.99, 50)
        flags = (p >= np.sort(p)[-10]).astype(int)
        self.assertTrue(identity.compare(p, p + 1e-6, flags)["identical_within_tolerance"])

    def test_probability_or_flag_differences_fail(self):
        p = np.linspace(0.01, 0.99, 50)
        flags = (p >= np.sort(p)[-10]).astype(int)
        self.assertFalse(identity.compare(p, p + 0.01, flags)["identical_within_tolerance"])
        wrong = flags.copy()
        wrong[0] = 1
        result = identity.compare(p, p, wrong)
        self.assertEqual(result["flag_disagreements"], 1)
        self.assertFalse(result["identical_within_tolerance"])


class ReportAssetTests(unittest.TestCase):
    def test_coding_assets_pending_then_copied_and_free_text_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root, out = Path(folder), Path(folder) / "out"
            out.mkdir()
            coding = root / "data" / "human_study" / "coding"
            coding.mkdir(parents=True)
            with mock.patch.object(assets, "ROOT", root), mock.patch.object(assets, "TABLE_OUT", out):
                self.assertEqual(assets.coding_assets()["status"], "pending")
                for name in ("theme_summary_study", "theme_by_group_study"):
                    pd.DataFrame([{"field": "rationale_freetext", "n_items": 1}]).to_csv(
                        coding / f"{name}.csv", index=False)
                self.assertEqual(assets.coding_assets()["status"], "partial")
                pd.DataFrame([{"group": "A", "n_items": 1}]).to_csv(
                    coding / "intervention_flags_by_group_study.csv", index=False)
                single = assets.coding_assets()
                self.assertEqual(single["status"], "completed_single_pass")
                self.assertEqual(single["inter_coder_agreement"], "not measured")
                pd.DataFrame([{"field": "rationale_freetext", "agreement": 1.0}]).to_csv(
                    coding / "agreement_study.csv", index=False)
                self.assertEqual(assets.coding_assets()["status"], "completed")
                self.assertTrue((out / "human_study_theme_by_group.csv").is_file())
                pd.DataFrame([{"participant_id": "P1", "text": "free text"}]).to_csv(
                    coding / "theme_by_group_study.csv", index=False)
                with self.assertRaises(ValueError):
                    assets.coding_assets()

    def test_demo_card_must_be_validation_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            card = root / "figures" / "demo_card"
            card.mkdir(parents=True)
            (card / "demo_card_validation.json").write_text(
                json.dumps({"split": "test", "test_split_accessed": True}), encoding="utf-8")
            with mock.patch.object(assets, "ROOT", root), \
                    mock.patch.object(assets, "FIGURE_OUT", root / "figures" / "report_ready"):
                with self.assertRaises(ValueError):
                    assets.demo_card_assets()


class ReleaseManifestTests(unittest.TestCase):
    def test_manifest_detects_missing_and_changed_files(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "a.txt").write_text("one", encoding="utf-8")
            manifest = base / "manifest.json"
            manifest.write_text(json.dumps({"files_sha256": {
                "a.txt": release.file_hash(base / "a.txt"), "b.txt": "0" * 64}}), encoding="utf-8")
            failures = release.verify_manifest(manifest, base)
            self.assertEqual(len(failures), 1)
            (base / "a.txt").write_text("two", encoding="utf-8")
            self.assertEqual(len(release.verify_manifest(manifest, base)), 2)


class EnrolledSensitivityTests(unittest.TestCase):
    def test_enrolled_shares_are_disjoint_from_the_binary_split(self):
        train, validation, total = enrolled.enrolled_shares()
        split_ids = set(pd.read_csv(Path(enrolled.ROOT) / "artifacts" / "split_ids.csv")["source_row_id"])
        self.assertEqual(total, 794)
        self.assertEqual((len(train), len(validation)), (555, 119))
        self.assertFalse(split_ids & set(train["source_row_id"]))
        self.assertFalse(set(train["source_row_id"]) & set(validation["source_row_id"]))
        self.assertTrue((train["target"] == 0).all() and (validation["target"] == 0).all())

    def test_metric_row_uses_twenty_percent_capacity(self):
        y = np.array([1] * 20 + [0] * 80)
        p = np.linspace(1, 0, 100)
        row = enrolled.metric_row("toy", y, p)
        self.assertAlmostEqual(row["flag_rate"], 0.20)
        self.assertAlmostEqual(row["dropout_recall"], 1.0)


if __name__ == "__main__":
    unittest.main()
