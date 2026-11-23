"""Numerical and semantic controls for the paired CCT estimator."""
import json
import unittest

import numpy as np
import pandas as pd

from science import evaluate


class TestPairedThickness(unittest.TestCase):
    def test_signed_mean_and_absolute_threshold_use_identical_pairs(self):
        frame = pd.DataFrame({"oct": [500, 510, 530, 520, 525, np.nan, 0],
                              "us": [520, 490, 509, 550, 500, 600, np.nan]})
        r = evaluate(frame, "oct", "us")
        self.assertEqual(r["n_complete"], 5)
        self.assertEqual(r["fraction_missing"], 2 / 7)
        self.assertEqual(r["either_nonpositive_n"], 1)
        self.assertEqual(r["oct_missing_n"], r["us_missing_n"])
        self.assertAlmostEqual(r["mean_difference_um"], 3.2)
        self.assertAlmostEqual(r["mean_absolute_difference_um"], 23.2)
        self.assertEqual((r["abs_gt20_n"], r["abs_equal20_n"], r["abs_gt20_pct"]), (3, 2, 60))
        self.assertEqual(r["sample_quantiles_um"]["difference"]["p50"], 20)
        inverse = evaluate(frame, "us", "oct")
        self.assertEqual(inverse["abs_gt20_pct"], r["abs_gt20_pct"])
        self.assertEqual(inverse["mean_difference_um"], -r["mean_difference_um"])

    def test_dispersion_correlation_and_crossing_precision(self):
        frame = pd.DataFrame({"oct": [500., 503., 506.], "us": [510., 520., 530.]})
        r = evaluate(frame, "oct", "us")
        self.assertEqual(r["oct_sd_um"], 3)
        self.assertEqual(r["us_sd_um"], 10)
        self.assertAlmostEqual(r["pearson_r"], 1)
        self.assertAlmostEqual(r["difference_sd_um"], 7)
        frame = pd.DataFrame({"oct": [520. + 1e-12, 520. + 1e-7], "us": [500., 500.]})
        r = evaluate(frame, "oct", "us")
        self.assertEqual((r["abs_gt20_n"], r["abs_equal20_n"]), (1, 1))
        self.assertIsNone(r["pearson_r"])

    def test_missing_or_nonfinite_records_and_semantic_input(self):
        frame = pd.DataFrame({"oct": pd.Series([pd.NA, 500], dtype="Int64"), "us": [520., np.nan]})
        r = evaluate(frame, "oct", "us")
        self.assertIsNone(r["mean_difference_um"])
        self.assertEqual(r["fraction_missing"], 1)
        json.dumps(r, allow_nan=False)
        for wrong in ("diagnostic_delta", "row_id", "nonnumeric", "flag", "infinite", "complex"):
            frame[wrong] = {"diagnostic_delta":[0., 0.], "row_id":[1, 2],
                            "nonnumeric":["hi", "500"], "flag":[True, False],
                            "infinite":[np.inf, 0], "complex":[1j, 2j]}[wrong]
            with self.subTest(wrong=wrong), self.assertRaises(ValueError):
                evaluate(frame, wrong, "us")
        with self.assertRaises(ValueError):
            evaluate(frame, "oct", "oct")


if __name__ == "__main__":
    unittest.main()
