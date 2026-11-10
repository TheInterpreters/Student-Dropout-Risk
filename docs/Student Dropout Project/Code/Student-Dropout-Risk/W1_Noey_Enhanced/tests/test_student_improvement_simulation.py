"""Synthetic tests for Noey W1 scenario analysis. No held-out test and no TabICL downloads."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

S=Path(__file__).resolve().parents[1]/'scripts'/'student_improvement_simulation.py'
spec=importlib.util.spec_from_file_location('noey_sim',S)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestNumericalDemo(unittest.TestCase):
    def test_known_example(self):
        r=module.toy_demonstration()
        self.assertEqual(len(r),9)
        self.assertAlmostEqual(float(r.iloc[0].illustrative_probability),0.8685653814768144,places=9)
        self.assertAlmostEqual(float(r.iloc[-1].illustrative_probability),0.29456117836013185,places=9)
        self.assertLess(float(r.iloc[-1].change_percentage_points),-50)

    def test_semester_dependencies_and_limits(self):
        row=pd.Series({'curricular_units_1st_sem_grade':9.,
          'curricular_units_1st_sem_approved':2,
          'curricular_units_1st_sem_enrolled':6,
          'tuition_fees_up_to_date':0,'debtor':1,'first_semester_pass_rate':0.3})
        def recalc(frame):
            frame=frame.copy();frame['first_semester_pass_rate']=frame['curricular_units_1st_sem_approved']/frame['curricular_units_1st_sem_enrolled'];return frame
        x=module.recompute_and_validate(row,{'curricular_units_1st_sem_approved':4},recalc)
        self.assertAlmostEqual(float(x['first_semester_pass_rate']),2/3)
        with self.assertRaises(ValueError):
            module.recompute_and_validate(row,{'curricular_units_1st_sem_approved':8},recalc)
        with self.assertRaises(ValueError):
            module.recompute_and_validate(row,{'gender':1},recalc)

    def test_scenarios_do_not_edit_original(self):
        row=pd.Series({'curricular_units_1st_sem_grade':9.,
          'curricular_units_1st_sem_approved':2,'curricular_units_1st_sem_enrolled':6,
          'tuition_fees_up_to_date':0,'debtor':1,'first_semester_pass_rate':1/3})
        def recalc(frame):
            frame=frame.copy();frame['first_semester_pass_rate']=frame['curricular_units_1st_sem_approved']/frame['curricular_units_1st_sem_enrolled'];return frame
        s=module.proposal_scenarios(row,recalc)
        self.assertEqual(float(row['curricular_units_1st_sem_grade']),9.0)
        self.assertTrue(any(v[0]=='Academic measures + both finance statuses' for v in s))

if __name__=='__main__': unittest.main()
