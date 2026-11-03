import itertools
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
import recompute as r


class IndependentMathTests(unittest.TestCase):
    def test_known_full_and_reduced_projections_two_cases(self):
        rows = list(itertools.product([30, 45, 60, 75], [0, 1], [22., 28.], [90., 110.]))
        frame = pd.DataFrame(rows, columns=["age", "female", "bmi", "glucose"])
        frame["hba1c"] = 4 + .1*(frame.age-50)/10 + .2*frame.female + .3*(frame.bmi-25)/5 + .4*(frame.glucose-100)/10
        result = r.calculate(frame, "ENSANUT2018", enforce_task=False)
        for name, expected in {"Q1_age10": .1, "Q2_bmi5": .3, "Q3_bmi5": .3, "Q2_minus_Q3_bmi5": 0., "glucose10_age_sex": .4}.items():
            self.assertAlmostEqual(result[name], expected, places=12)
        frame.age = frame.age.replace({30: 35, 75: 74})
        frame["glucose"] /= 18
        frame["hba1c"] = 3 + .02*frame.age + .1*frame.female + .04*frame.bmi + .6*frame.glucose
        result = r.calculate(frame, "CHNS2009", enforce_task=False)
        for name, expected in {"E1": .04, "E2": .6, "E3": .02}.items():
            self.assertAlmostEqual(result[name], expected, places=12)

    def test_quantile_left_inverse_and_rank_failure(self):
        self.assertEqual(r.inverse_weighted_quantile(np.array([9., 1., 3.]), np.array([.1, .4, .5]), .4), 1.)
        self.assertEqual(r.inverse_weighted_quantile(np.array([9., 1., 3.]), np.array([.1, .4, .5]), .5), 3.)
        self.assertIsNone(r.qr_fit(np.ones((8, 2)), np.arange(8.), np.ones(8))[0])

    def test_closed_gate_before_any_results_or_reference(self):
        with patch.object(r.control, "READ", return_value={}) as read, patch.object(r.control, "require_campaign_closed", side_effect=ValueError("still open")):
            with self.assertRaisesRegex(ValueError, "still open"):
                r.audit("release", "results", "never_created")
            read.assert_called_once_with("release")


if __name__ == "__main__":
    unittest.main()
