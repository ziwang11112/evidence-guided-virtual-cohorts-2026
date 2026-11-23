"""Synthetic unit tests only."""
import math
import unittest

import numpy as np
import pandas as pd

from evaluate import evaluate


class TestIOPAnalyses(unittest.TestCase):
    def test_hand_calculation_thresholds_and_native_precision(self):
        a = np.array([12, 14, 17, 12, 20, 17, 13.0])
        b = np.array([10, 10, 12, 16, 17, 14 - 5e-12, 10 - 2e-7])
        frame = pd.DataFrame({"p": a, "g": b})
        r = evaluate(frame, "p", "g")
        self.assertEqual(r["n_complete"], 7)
        self.assertEqual(r["signed_gt_3_n"], 3)
        self.assertEqual(r["signed_equal_3_n"], 2)
        self.assertAlmostEqual(r["signed_gt_3_pct"], 300 / 7)
        self.assertEqual(r["abs_ge_4_n"], 3)
        self.assertEqual(r["among_abs_ge_4_pascal_higher_n"], 2)
        self.assertEqual(r["among_abs_ge_4_goldmann_higher_n"], 1)
        self.assertAlmostEqual(r["mean_difference_mmhg"], (16 + 2e-7 + 5e-12)/7)
        xa = a - sum(a)/len(a)
        xb = b - sum(b)/len(b)
        self.assertAlmostEqual(r["pascal_sd_mmhg"], math.sqrt(sum(xa**2)/6))
        self.assertAlmostEqual(r["goldmann_sd_mmhg"], math.sqrt(sum(xb**2)/6))
        self.assertAlmostEqual(r["pearson_r"], sum(xa*xb)/math.sqrt(sum(xa**2)*sum(xb**2)))

    def test_resample_pairs_with_constant_difference(self):
        frame = pd.DataFrame({"p":[23., 33., np.nan, 43.], "g":[20., 30., 22., 40.]})
        result = evaluate(frame, "p", "g", measured=True)
        self.assertEqual(result["n_incomplete"], 1)
        self.assertEqual(result["paired_bootstrap"]["interval_95"]["mean_difference_mmhg"],
                         [3.0, 3.0])
        self.assertEqual(result["paired_bootstrap"]["interval_95"]["signed_gt_3_pct"], [0., 0.])
        self.assertEqual(result["signed_equal_3_pct"], 100)
        self.assertAlmostEqual(result["pearson_r"], 1.)

    def test_undefined_and_invalid_inputs(self):
        f = pd.DataFrame({"p": [6., 6.], "g": [0., 1.], "person": ["a","a"]})
        r = evaluate(f, "p", "g")
        self.assertIsNone(r["pearson_r"])
        self.assertEqual(r["positive_pressure_check"]["either_nonpositive_n"], 1)
        with self.assertRaises(ValueError):
            evaluate(f, "p", "g", id_column="person")
        with self.assertRaises(ValueError):
            evaluate(f.assign(p=np.inf), "p", "g")
        with self.assertRaises(ValueError):
            evaluate(f.assign(p="oops"), "p", "g")
        with self.assertRaises(ValueError):
            evaluate(f, "g", "g")

if __name__ == "__main__":
    unittest.main()
