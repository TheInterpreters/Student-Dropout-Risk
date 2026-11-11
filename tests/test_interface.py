import json
import tempfile
import unittest
from pathlib import Path

from scripts import launch_interface as ui

LABELS = {f"g{i}": f"Group {i}" for i in range(6)}


def case(sid, position, probability, flagged, **overrides):
    record = {
        "source_row_id": sid, "validation_position": position,
        "predicted_probability": probability, "flagged": flagged,
        "baseline_group_contributions": [{"feature_group": f"g{i}", "signed_shap": 0.1 - i * 0.05}
                                         for i in range(5)],
        "stability": [{"variation": v, "top_5_overlap": 0.9} for v in ("seed", "background", "perturbation")],
        "recourse": ([{"status": "recourse_found", "changed_features": "debtor", "capacity_rank": 3}]
                     if flagged else [{"status": "not_flagged"}]),
    }
    record.update(overrides)
    return record


def write_cases(folder, records):
    for record in records:
        (Path(folder) / f"case_{record['source_row_id']:05d}.json").write_text(json.dumps(record))


class InterfaceTests(unittest.TestCase):
    def cohort(self):
        # 10 cases -> 2 flagged at 20%; position 0 is the practice case.
        return [case(100 + i, i, 0.9 - i * 0.05, int(i in (1, 2))) for i in range(1, 10)] + \
               [case(100, 0, 0.1, 0)]

    def test_ranks_whole_cohort_and_hides_practice_and_study_cases(self):
        with tempfile.TemporaryDirectory() as folder:
            write_cases(folder, self.cohort())
            shown, n_cases, n_flag, cohort = ui.load_cases(folder, LABELS, refused_ids={105})
        self.assertEqual(len(cohort), 10)
        self.assertEqual(cohort, sorted(cohort, reverse=True))
        self.assertEqual((n_cases, n_flag), (10, 2))
        ids = [c["source_row_id"] for c in shown]
        self.assertNotIn(100, ids)
        self.assertNotIn(105, ids)
        self.assertEqual(shown[0]["rank"], 1)
        self.assertEqual(shown[0]["recourse"][0]["changes"], ["debt to the university resolved"])

    def test_rejects_flag_that_breaks_the_rank_rule(self):
        records = self.cohort()
        records[3]["flagged"] = 1
        with tempfile.TemporaryDirectory() as folder:
            write_cases(folder, records)
            with self.assertRaises(ValueError):
                ui.load_cases(folder, LABELS)

    def test_rejects_invalid_fields_instead_of_repairing(self):
        bad = [case(1, 1, 1.5, 0), case(1, 1, 0.5, 2), case(1, 1, 0.5, 0, stability=[]),
               case(1, 1, 0.5, 0, baseline_group_contributions=[{"feature_group": "zz", "signed_shap": 0.1}] * 5),
               case(1, 1, 0.5, 1, recourse=[{"status": "recourse_found", "changed_features": "grade",
                                             "capacity_rank": 9}])]
        for record in bad:
            with self.assertRaises(ValueError):
                ui.validate_case(record, LABELS)
        missing = case(1, 1, 0.5, 0)
        del missing["recourse"]
        with self.assertRaises(ValueError):
            ui.validate_case(missing, LABELS)

    def test_real_build_is_validation_only(self):
        with tempfile.TemporaryDirectory() as folder:
            out = ui.build(Path(folder) / "demo.html")
            page = out.read_text(encoding="utf-8")
        self.assertIn("validation only", page)
        data = json.loads(page.split('type="application/json">', 1)[1].split("</script>", 1)[0]
                          .replace("<\\/", "</"))
        self.assertEqual(data["n_cases"], 544)
        self.assertEqual(sum(c["flagged"] for c in data["cases"]), data["n_flag"])
        self.assertEqual(len(data["cohort"]), 544)
        self.assertTrue(all(c["source_row_id"] not in ui.study_source_ids() for c in data["cases"]))


if __name__ == "__main__":
    unittest.main()
