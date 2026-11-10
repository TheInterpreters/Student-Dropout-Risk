"""Audit scope and incomplete-evidence guards, independent of project TabICL."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("noey_full_cohort", ROOT / "scripts" / "run_enhanced_audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class FullCohortScopeTests(unittest.TestCase):
    def test_full_validation_cohort_not_sampled_twenty(self):
        p=json.loads((ROOT/'config'/'full_cohort_protocol.json').read_text())
        self.assertEqual(p['scope'],'all_validation_rows')
        self.assertEqual(p['expected_validation_rows'],544)
        self.assertEqual(audit.EXPECTED_CASES,544)
        self.assertEqual(audit.SELECTED_SPLIT,'validation')

    def test_unstarted_audit_cannot_be_reported_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            cases=base/'cases'
            cases.mkdir()
            # No manifest or case evidence -> no report, no fabricated statistics.
            with self.assertRaises(FileNotFoundError):
                audit.report({'artifacts':cases,'tables':base/'tables',
                              'figures':base/'figures','lock':base/'final_test.lock'})

    def test_case_id_duplicated_stops_loading(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)
            (a/'case_00001.json').write_text(json.dumps({'source_row_id':7}))
            (a/'case_00002.json').write_text(json.dumps({'source_row_id':7}))
            with self.assertRaises(ValueError):audit.load_cases(a)

if __name__=='__main__': unittest.main()
