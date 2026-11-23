"""Synthetic implementation checks only. No scientific data are used."""
import unittest

import numpy as np
import pandas as pd

from lung import evaluate, rounding_replay


class TestLung(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame({"sex": ["F", "F", "M", "M", "M", "M"],
                                   "fev1_l": [7., 1., 1., 2., 3., 4.], "fvc_l": [10., 2., 1., 2., 3., 4.]})

    def test_weighting_boundary_and_estimands(self):
        score = evaluate(self.frame)
        self.assertEqual(score["status"], "computed")
        self.assertEqual(score["equal_sex_threshold_pct"], 25.)
        self.assertEqual(score["sex"]["F"]["equal_to_threshold_count"], 1)
        self.assertAlmostEqual(score["equal_sex_ratio_of_means_pct"], 100 * 6.5 / 8.5)
        x, y = self.frame.fev1_l, self.frame.fvc_l
        self.assertNotAlmostEqual(score["equal_sex_ratio_of_means_pct"], 100 * x.sum()/y.sum())
        self.assertNotAlmostEqual(score["equal_sex_ratio_of_means_pct"], 100 * (x/y).mean())
        self.assertNotAlmostEqual(score["equal_sex_threshold_pct"], 100 * (x/y < .70).mean())

    def test_units_direction_and_reported_precision(self):
        score = evaluate(self.frame)
        f = score["sex"]["F"]["source_replay"]
        self.assertAlmostEqual(f["ols_slope"]["rows"], .75)
        self.assertAlmostEqual(f["ols_intercept_l"]["rows"], -.5)
        self.assertAlmostEqual(f["fev1_sd_l"]["rows"], np.sqrt(18.))
        wrong_units = self.frame.copy()
        wrong_units["fev1_l"] *= 1000
        self.assertEqual(evaluate(wrong_units)["nonphysical_rows_fev1_exceeding_fvc"], 6)
        self.assertTrue(rounding_replay(2.38, 2.4, .1)["inside_printed_rounding_bin"])
        self.assertFalse(rounding_replay(2.47, 2.4, .1)["inside_printed_rounding_bin"])
        self.assertTrue(rounding_replay(-.232, -.23, .01)["inside_printed_rounding_bin"])

    def test_invalid_and_degenerate(self):
        for col, invalid in (("sex", "unknown"), ("fev1_l", np.nan), ("fvc_l", 0.)):
            frame = self.frame.copy()
            frame.loc[0, col] = invalid
            self.assertEqual(evaluate(frame)["status"], "invalid_input_no_row_substitution")
        self.assertEqual(evaluate(self.frame.iloc[:2])["status"], "invalid_input_no_row_substitution")
        single = self.frame.drop(index=0)
        self.assertIn("F.pearson_r", evaluate(single)["source_replay_outside_or_undefined"])


if __name__ == "__main__":
    unittest.main()
