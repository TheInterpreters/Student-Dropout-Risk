import json
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from scripts import run_final_test as final
from scripts import export_study_cases as export
from scripts import run_explanation_audit as audit
from scripts.run_explanation_audit import area_interval, run_audit, run_smoke_check
from src.evaluation import load_protocol, reliability_table
from src.freeze import create_snapshot, file_hash, verify_snapshot


class FakeModel:
    def predict_proba(self, frame):
        p = .1 + .6 * frame["x0"].to_numpy(dtype=float)
        return np.column_stack([1 - p, p])


class EvaluationRunnerTests(unittest.TestCase):
    def test_default_audit_cli_never_runs_full_audit(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            result = {"mode": "exploratory_smoke", "full_audit_completed": False}
            with patch.object(audit, "ROOT", root), \
                 patch.object(audit, "development_frames", return_value=(None, None, [])), \
                 patch.object(audit, "selected_model"), \
                 patch.object(audit, "run_smoke_check", return_value=result) as smoke, \
                 patch.object(audit, "run_audit") as full:
                self.assertEqual(audit.main([]), 0)
                smoke.assert_called_once()
                full.assert_not_called()
                evidence = json.loads((root / "artifacts" / "explanation_smoke_validation.json").read_text())
                self.assertFalse(evidence["full_audit_completed"])

    def test_local_snapshot_detects_changed_inputs_and_checkpoint(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ("requirements.txt", "artifacts/split_ids.csv",
                         "eda_uci_data/data/dropout_data.csv", "src/example.py"):
                path = root.joinpath(*name.split("/"))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("synthetic")
            checkpoint = root / "synthetic.ckpt"
            checkpoint.write_bytes(b"synthetic model")
            manifest = create_snapshot(root, root / "data" / "freeze", checkpoint, "live acceptance incomplete")
            frozen_checkpoint = verify_snapshot(root, manifest)
            self.assertEqual(file_hash(checkpoint), file_hash(frozen_checkpoint))
            code = root / "src" / "example.py"
            code.write_text("changed")
            with self.assertRaisesRegex(ValueError, "input changed"):
                verify_snapshot(root, manifest)
            code.write_text("synthetic")
            extra = root / "src" / "extra.py"
            extra.write_text("new input")
            with self.assertRaisesRegex(ValueError, "file set changed"):
                verify_snapshot(root, manifest)
            extra.unlink()
            frozen_checkpoint.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "checkpoint changed"):
                verify_snapshot(root, manifest)
            with self.assertRaises(FileExistsError):
                create_snapshot(root, root / "data" / "freeze", checkpoint, "incomplete")

    def test_local_test_requires_explicit_deviation_acknowledgement(self):
        with patch.object(final, "execute") as execute, \
             patch.object(final, "LOCK", Path("nonexistent-synthetic-final-lock")):
            with self.assertRaises(SystemExit):
                final.main(["--split", "test", "--local-freeze", "dummy.json", "--confirm-final-test"])
            execute.assert_not_called()

    def test_local_test_binds_bundle_and_keeps_once_only_lock(self):
        import joblib
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "config").mkdir()
            (root / "config" / "evaluation_protocol.json").write_text("{}")
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"incomplete_checks_and_deviation": "form acceptance incomplete"}))
            bundle_path = root / "data" / "final_evaluation" / "selected_model.joblib"
            bundle_path.parent.mkdir(parents=True)
            joblib.dump({"model": "synthetic"}, bundle_path)
            lock = root / "final_test.lock"
            args = ["--split", "test", "--local-freeze", str(manifest),
                    "--confirm-final-test", "--acknowledge-incomplete-checks"]
            with patch.object(final, "ROOT", root), patch.object(final, "LOCK", lock), \
                 patch.object(final, "verify_environment"), \
                 patch.object(final, "verify_snapshot", return_value=root / "checkpoint") as verify, \
                 patch.object(final, "execute", return_value={"split": "test"}) as execute:
                self.assertEqual(final.main(args), 0)
                self.assertEqual(verify.call_count, 2)
                self.assertEqual(execute.call_args.kwargs["checkpoint"], root / "checkpoint")
                with self.assertRaises(FileExistsError):
                    final.main(args)
                self.assertEqual(execute.call_count, 1)
            evidence = json.loads(lock.read_text())
            self.assertEqual(evidence["status"], "completed")
            self.assertEqual(evidence["review_status"], "not independently approved")
            self.assertEqual(evidence["model_bundle_sha256"], file_hash(bundle_path))
            self.assertEqual(joblib.load(bundle_path)["local_freeze_sha256"], file_hash(manifest))
            artifacts = root / "artifacts"
            artifacts.mkdir()
            (artifacts / "final_test.lock").write_text(json.dumps(evidence))
            bundle_path.write_bytes(b"tampered model")
            with patch.object(export, "ROOT", root), \
                 patch.object(export, "verify_snapshot"), \
                 patch.object(export, "development_frames") as frames:
                with self.assertRaisesRegex(ValueError, "bundle changed"):
                    export.main([])
                frames.assert_not_called()

    def test_lock_survives_deleted_outputs_and_refuses_repeat(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "final_test.lock"
            out = Path(folder) / "result.csv"
            final.acquire_lock(path, {"frozen_commit": "dummy"})
            out.write_text("fake")
            out.unlink()
            with self.assertRaises(FileExistsError):
                final.acquire_lock(path, {"frozen_commit": "dummy"})
            self.assertEqual(json.loads(path.read_text())["status"], "started")

    def test_test_needs_explicit_confirmation_before_data_access(self):
        with patch.object(final, "execute") as execute:
            with self.assertRaises(SystemExit):
                final.main(["--split", "test"])
            execute.assert_not_called()

    def test_partial_run_keeps_lock_and_does_not_retry(self):
        with tempfile.TemporaryDirectory() as folder:
            lock = Path(folder) / "lock"
            with patch.object(final, "LOCK", lock), \
                 patch.object(final, "check_gate", return_value={"frozen_commit": "dummy"}), \
                 patch.object(final, "execute", side_effect=RuntimeError("synthetic failure")) as execute:
                args = ["--split", "test", "--approval", "dummy.json", "--confirm-final-test"]
                with self.assertRaises(RuntimeError):
                    final.main(args)
                self.assertTrue(lock.exists())
                with self.assertRaises(FileExistsError):
                    final.main(args)
                self.assertEqual(execute.call_count, 1)

    def test_validation_never_acquires_final_lock(self):
        with patch.object(final, "execute", return_value={"split": "validation"}) as execute, \
             patch.object(final, "acquire_lock") as lock:
            self.assertEqual(final.main([]), 0)
            self.assertEqual(execute.call_args.args[0], "validation")
            lock.assert_not_called()

    def test_gate_requires_recorded_approvals_and_exact_protocol(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "config").mkdir()
            protocol = root / "config" / "evaluation_protocol.json"
            protocol.write_text("{}")
            approval_path = root / "config" / "approval.json"
            approval = {
                "owner": "M3", "reviewer": "M4", "validation_audit_passed": True,
                "form_acceptance_passed": True, "final_runner_dry_run_passed": True,
                "participant_plan_verified": True,
                "protocol_sha256": hashlib.sha256(protocol.read_bytes()).hexdigest(),
            }
            outputs = ["", "frozen", "frozen", "frozen\trefs/tags/protocol-1.3-frozen", "config/approval.json"]
            for key, value in ((None, None), ("form_acceptance_passed", False),
                               ("protocol_sha256", "wrong"), ("reviewer", "M3")):
                data = dict(approval)
                if key:
                    data[key] = value
                approval_path.write_text(json.dumps(data))
                with patch.object(final, "ROOT", root), patch.object(final, "verify_environment"), \
                     patch.object(final.subprocess, "check_output", side_effect=outputs):
                    if key:
                        with self.assertRaises(ValueError):
                            final.check_gate(approval_path)
                    else:
                        self.assertEqual(final.check_gate(approval_path)["frozen_commit"], "frozen")

    def test_reliability_and_case_level_uncertainty(self):
        reliability = reliability_table([0, 1, 0, 1], [.0, 1., .2, .8])
        self.assertEqual(len(reliability), 10)
        self.assertEqual(reliability["n"].sum(), 4)
        interval = area_interval([1., 1., 1.])
        self.assertEqual(interval["ci_lower_95"], 1.)
        self.assertEqual(interval["ci_upper_95"], 1.)

    def test_validation_evaluation_outputs_with_synthetic_predictions(self):
        truth = pd.Series([0, 1] * 10)
        evaluation = pd.DataFrame({"target": truth})
        predictions = {"tabicl": np.array([.1, .9] * 10),
                       "logistic_regression": np.array([.2, .8] * 10)}
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            with patch.object(final, "development_frames", return_value=(evaluation, evaluation, [])), \
                 patch.object(final, "evaluate_frozen_models",
                              return_value=(pd.DataFrame([{"model": "tabicl"}]), predictions, {})), \
                 patch.object(final, "fairness_outputs",
                              return_value=(pd.DataFrame([{"n": 20}]), pd.DataFrame([{"association": 0.}]))):
                result = final.execute("validation", out, bootstrap_resamples=10)
            self.assertEqual(result["split"], "validation")
            self.assertTrue((out / "paired_comparisons.csv").exists())
            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["split"], "validation")
            self.assertIn("metrics.csv", manifest["files_sha256"])

    def test_audit_runner_with_synthetic_model_and_explanations(self):
        rng = np.random.default_rng(42)
        columns = ["x0", "x1", "x2", "x3", "debtor", "tuition_fees_up_to_date"]
        train = pd.DataFrame(rng.uniform(0, 1, (30, 6)), columns=columns)
        validation = pd.DataFrame(rng.uniform(0, 1, (25, 6)), columns=columns)
        for frame in (train, validation):
            frame["debtor"] = 0
            frame["tuition_fees_up_to_date"] = 1
            frame["source_row_id"] = np.arange(len(frame))
        protocol = load_protocol()
        protocol["faithfulness"].update(cases=5, random_deletion_repetitions=2)
        protocol["stability"]["runs_per_case"] = 2
        protocol["shap"]["background_size"] = 3

        def fake_shap(predict, background, case, max_evals, seed):
            return SimpleNamespace(values=np.array([[.6, .2, .1, .05, -.03, .01]]))

        with patch("scripts.run_explanation_audit.permutation_shap_values", side_effect=fake_shap):
            tables, timing = run_audit(train, validation, columns, FakeModel(), protocol)
        self.assertEqual(len(tables["faithfulness_validation"]), 5)
        self.assertEqual(len(tables["stability_validation"]), 15)
        self.assertEqual(set(tables["stability_validation"]["variation"]), {"seed", "background", "perturbation"})
        self.assertFalse(timing["test_evaluated"])
        self.assertTrue((tables["stability_validation"]["top_5_overlap"] == 1).all())
        with patch("scripts.run_explanation_audit.permutation_shap_values", side_effect=fake_shap) as explain:
            result = run_smoke_check(train, validation, columns, FakeModel(), protocol)
        self.assertEqual(explain.call_count, 2)
        self.assertEqual(result["mode"], "exploratory_smoke")
        self.assertFalse(result["full_audit_completed"])
        self.assertFalse(result["test_evaluated"])
        self.assertEqual(result["single_case_top_5_overlap"], 1.)
        with patch("scripts.run_explanation_audit.permutation_shap_values",
                   return_value=SimpleNamespace(values=np.full((1, len(columns)), np.nan))):
            with self.assertRaisesRegex(ValueError, "non-finite"):
                run_smoke_check(train, validation, columns, FakeModel(), protocol)


if __name__ == "__main__":
    unittest.main()
