import unittest

import numpy as np

from scripts.build_demo_card import PRACTICE_POSITION, choose_case


class DemoCardSelectionTests(unittest.TestCase):
    def test_median_flagged_case_excludes_practice(self):
        probability = np.array([0.99, 0.10, 0.80, 0.95, 0.20, 0.90])
        flags = np.array([1, 0, 1, 1, 0, 1])
        source_ids = np.array([3, 4, 5, 6, 7, 8])
        chosen = choose_case(probability, flags, source_ids)
        self.assertNotEqual(chosen, PRACTICE_POSITION)
        self.assertEqual(chosen, 5)  # flagged non-practice: 0.80, 0.90, 0.95 -> median 0.90

    def test_no_flagged_case_is_an_error(self):
        with self.assertRaises(ValueError):
            choose_case(np.array([0.9, 0.1]), np.array([1, 0]), np.array([1, 2]))


if __name__ == "__main__":
    unittest.main()
