"""Offline synthetic tests — not real TabICL/SHAP scientific evidence."""
from __future__ import annotations
import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import surrogate_comparison as sc


class SurrogateComparisonTests(unittest.TestCase):
    def test_mask_holdout_protocol_and_no_overlap(self):
        masks, train, hold = sc.fixed_mask_holdout()
        self.assertEqual(masks.shape, (32, 5))
        self.assertEqual((len(train), len(hold)), (24, 8))
        self.assertFalse(set(train) & set(hold))
        self.assertTrue(np.all(masks[hold].sum(axis=1) >= 3))
        self.assertTrue(np.all(np.isin(np.where(masks.sum(axis=1) <= 2)[0], train)))

    def test_design_includes_ten_pair_terms(self):
        masks, _, _ = sc.fixed_mask_holdout()
        a, names = sc.make_binary_design(masks, list('abcde'), True)
        b, names_b = sc.make_binary_design(masks, list('abcde'), False)
        self.assertEqual((a.shape, b.shape), ((32, 15), (32, 5)))
        self.assertEqual(len(names), 15)
        self.assertEqual(len(names_b), 5)

    def test_no_penalty_main_and_pairs_are_compared(self):
        masks, _, _ = sc.fixed_mask_holdout()
        y = .25 + .09*masks[:, 0] + .07*masks[:, 1] + .12*masks[:, 0]*masks[:, 1]
        variants, details = sc.fit_six_surrogates(masks, y.astype(float), list('abcde'))
        self.assertEqual(len(variants), 6)
        self.assertEqual(len(details), 48)
        metrics = {v['variant']: v for v in variants}
        self.assertEqual(set(metrics), {'OLS+main','Ridge+main','Lasso+main',
                                        'OLS+pairs','Ridge+pairs','Lasso+pairs'})
        self.assertLess(metrics['OLS+pairs']['holdout_mae'], 1e-10)
        self.assertGreater(metrics['OLS+main']['holdout_mae'], 1e-3)
        self.assertTrue(metrics['Lasso+pairs']['nonzero_terms'] <= 15)

    def test_cv_alpha_unchanged_when_heldout_targets_change(self):
        masks, _, hold = sc.fixed_mask_holdout()
        y = .2 + .05*masks[:, 0] + .04*masks[:, 1]*masks[:, 2]
        x, _ = sc.fit_six_surrogates(masks,y.astype(float),list('abcde'))
        modified = y.astype(float).copy()
        modified[hold] += .10
        yy, _ = sc.fit_six_surrogates(masks,modified,list('abcde'))
        def a(v):return {r['variant']:r['alpha'] for r in v}
        self.assertEqual(a(x),a(yy))

    def test_reject_invalid_probability_inputs(self):
        masks, _, _ = sc.fixed_mask_holdout()
        with self.assertRaises(ValueError):
            sc.fit_six_surrogates(masks,np.ones(32)*1.3,list('abcde'))

    def test_aggregate_six_variants(self):
        masks, _, _ = sc.fixed_mask_holdout()
        y = .3 + .1*masks[:, 0] + .05*masks[:, 2]
        v, d = sc.fit_six_surrogates(masks,y.astype(float),list('abcde'))
        s, details, total = sc.aggregate_surrogate_comparisons([
            {'source_row_id': 8, 'surrogate_comparison': {'summary':v,'holdout_predictions':d}},
            {'source_row_id': 9, 'surrogate_comparison': {'summary':v,'holdout_predictions':d}},
        ])
        self.assertEqual((len(s),len(details),len(total)),(12,96,6))
        self.assertTrue((total['n_cases']==2).all())
        self.assertTrue((total['pooled_n_holdout']==16).all())

    def test_end_to_end_masked_model_single_case(self):
        case = pd.Series({k: 1.0 for k in 'abcde'})
        references = pd.Series({k: 0.0 for k in 'abcde'})
        groups = {k: (k,) for k in 'abcde'}
        def mask_fn(base, selected, groups, refs):
            o = base.copy()
            for k in selected:o[k]=refs[k]
            return o
        def model(frame):
            a = frame['a'].to_numpy(float)
            b = frame['b'].to_numpy(float)
            p = .2 + .15*a + .10*b + .12*a*b
            return np.column_stack((1-p,p))
        result = sc.run_masking_surrogates(model,case,groups,references,list('abcde'),mask_fn)
        self.assertEqual(result['masking_pattern_count'],32)
        self.assertEqual(len(result['summary']),6)

if __name__ == '__main__': unittest.main()
