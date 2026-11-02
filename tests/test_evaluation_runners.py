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
from scripts.run_explanation_audit import area_interval, run_audit
from src.evaluation import load_protocol, reliability_table


class FakeModel:
    def predict_proba(self, frame):
        p = .1 + .6 * frame["x0"].to_numpy(dtype=float)
        return np.column_stack([1 - p, p])


class EvaluationRunnerTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
