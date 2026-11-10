"""Synthetic unit checks only: not a real TabICL/SHAP audit."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd

RUNNER = Path(__file__).resolve().parents[1] / 'scripts' / 'run_enhanced_audit.py'
spec = importlib.util.spec_from_file_location('noey_enhanced_audit', RUNNER)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def toy_probability(frame):
    a = frame['a'].astype(float).to_numpy()
    b = frame['b'].astype(float).to_numpy()
    p = .2 + .25*a + .2*b + .15*a*b
    return np.column_stack((1-p,p))


def recourse_probability(frame):
    debt = frame['debtor'].astype(float).to_numpy()
    unpaid = 1-frame['tuition_fees_up_to_date'].astype(float).to_numpy()
    p = .2 + .3*debt + .3*unpaid
    return np.column_stack((1-p,p))


class NoeyEnhancedAuditTests(unittest.TestCase):
    def test_pair_nonadditive_effect_is_not_sum(self):
        case = pd.Series({'a': 1., 'b': 1.})
        ref = pd.Series({'a': 0., 'b': 0.})
        groups = {'a': ('a',), 'b': ('b',)}
        rows = audit.pair_deletion_audit(toy_probability, case, groups, ref, ['a','b'],recompute=lambda f:f)
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]['nonadditive_effect'], .15, places=8)
        self.assertEqual(rows[0]['interpretation_scope'], 'model reference-masking response only')

    def test_pair_masking_keeps_untouched_features(self):
        case=pd.Series({'a':1.,'b':1.,'c':42.})
        references=pd.Series({'a':0.,'b':0.,'c':1.})
        masked=audit.mask_group_union(case,['a','b'],{'a':['a'],'b':['b']},references,recompute=lambda f:f)
        self.assertEqual(masked['c'],42.)

    def test_recourse_checks_single_and_combined_scenarios(self):
        m=types.ModuleType('src.modeling')
        def capacity_predictions(probabilities, capacity=.2):
            p=np.asarray(probabilities)
            n=max(1,int(np.floor(len(p)*capacity)))
            flag=np.zeros(len(p),dtype=int)
            flag[np.lexsort((np.arange(len(p)),-p))[:n]]=1
            return flag, None
        m.capacity_predictions=capacity_predictions
        with patch.dict(sys.modules,{'src':types.ModuleType('src'),'src.modeling':m}):
            case=pd.Series({'debtor':1.,'tuition_fees_up_to_date':0.})
            cohort=np.array([.8,.7,.65,.2,.1])
            out=audit.model_recourse_scenarios(recourse_probability,case,cohort,0,capacity=.4)
        self.assertEqual(len(out),3)
        combined=[row for row in out if row['scenario_kind']=='combined_status_resolution']
        self.assertEqual(len(combined),1)
        self.assertEqual(combined[0]['status'],'leaves_flagged_group')

    def test_perturbations_are_ten_and_grade_only(self):
        e=types.ModuleType('src.explanations')
        e.recompute_first_semester_features=lambda frame:frame
        case=pd.Series({'grade':10.})
        train=pd.DataFrame({'grade':[0.,5.,10.,15.,20.]})
        def p(frame):
            v=frame['grade'].to_numpy(float)
            p=.2+.02*v
            return np.column_stack((1-p,p))
        with patch.dict(sys.modules,{'src':types.ModuleType('src'),'src.explanations':e}):
            rows=audit.eligible_grade_perturbations(p,case,train,['grade'],proposals=10)
        self.assertEqual(len(rows),10)
        self.assertTrue(rows['perturbed_value'].between(0,20).all())
        self.assertTrue(rows['grade_only_sensitivity_probe'].all())
        self.assertTrue(rows['accepted'].all())

    def test_bootstrap_is_deterministic(self):
        x=[.1,.2,.3,.4]
        self.assertEqual(audit.bootstrap_interval(x),audit.bootstrap_interval(x))

if __name__=='__main__':
    unittest.main()
