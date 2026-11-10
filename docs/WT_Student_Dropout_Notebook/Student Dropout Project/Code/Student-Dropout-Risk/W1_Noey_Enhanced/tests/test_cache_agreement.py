"""Cache checks exercise numerical bounds and exact outreach-flag agreement."""
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "W1_Noey_Enhanced/scripts")]
from run_enhanced_audit import validate_cache_agreement


class CacheAgreementTests(unittest.TestCase):
    def test_small_differences_are_disclosed_not_called_identical(self):
        result = validate_cache_agreement([.9, .6, .4, .2, .1], [.900005, .6, .4, .2, .1])
        self.assertFalse(result["bitwise_identical"])
        self.assertTrue(result["outreach_flags_equal"])
        self.assertLess(result["maximum_absolute_probability_difference"], 1e-4)

    def test_small_difference_cannot_change_outreach_membership(self):
        with self.assertRaises(ValueError):
            validate_cache_agreement([.90001, .9, .4, .2, .1], [.9, .90001, .4, .2, .1])

    def test_large_difference_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_cache_agreement([.9, .6, .4, .2, .1], [.91, .6, .4, .2, .1])

    def test_invalid_or_misaligned_predictions_are_rejected(self):
        for other in ([np.nan, .6], [.9], [1.1, .6]):
            with self.subTest(other=other), self.assertRaises(ValueError):
                validate_cache_agreement([.9, .6], other)


if __name__ == "__main__":
    unittest.main()
