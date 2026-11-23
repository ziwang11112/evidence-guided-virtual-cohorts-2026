import unittest

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from iron import check_source_claims, evaluate


class TestDevelopmentEvaluator(unittest.TestCase):
    def test_source_equivalents_and_two_semantic_errors(self):
        odds_depleted = (96 + 26 + 43 + 8) / (187 + 48 + 68 + 28)
        odds_replete = (45 + 17 + 22 + 1) / (687 + 166 + 166 + 63)
        correct = {
            "source_crude_or": {"value": round(odds_depleted / odds_replete, 2), "decimal_places": 2},
            "anemia_cutoff": {"value": 12, "unit": "g/dL", "comparison": "<"},
            "depletion_cutoff": {"value": 15, "unit": "ng/mL", "comparison": "<"},
            "source_spearman_assertion": "not_identified",
        }
        self.assertTrue(all(check_source_claims(correct).values()))
        for key, wrong in [
            ("source_crude_or", {"value": 6.448, "decimal_places": 3}),
            ("anemia_cutoff", {"value": 120, "unit": "g/dL", "comparison": "<"}),
            ("depletion_cutoff", {"value": 15, "unit": "μg/mL", "comparison": "<"}),
            ("source_spearman_assertion", "reported"),
        ]:
            with self.subTest(key=key):
                self.assertEqual(sum(not v for v in check_source_claims({**correct, key: wrong}).values()), 1)

    def test_joint_cells_are_invariant_under_replication(self):
        f = pd.DataFrame({"hb_g_l": [99, 119, 120, 135], "ferritin_ug_l": [10, 15, 14, 16]})
        f = f.loc[f.index.repeat([173, 85, 331, 1082])].reset_index(drop=True)
        for data in (f, pd.concat([f, f], ignore_index=True)):
            result = evaluate(data)
            self.assertAlmostEqual(result["cell_total_variation"], 0)
            self.assertAlmostEqual(result["crude_or"]["difference"], 0)
            self.assertAlmostEqual(result["continuous_spearman_on_virtual_rows"],
                                   spearmanr(data.hb_g_l, data.ferritin_ug_l).statistic)
            self.assertIsNone(result["source_continuous_spearman"])

    def test_invalid_data_and_zero_denominator(self):
        f = pd.DataFrame({"hb_g_l": [120, np.nan], "ferritin_ug_l": [13, 15]})
        self.assertNotIn("crude_or", evaluate(f))
        f["hb_g_l"] = [121, 121]
        result = evaluate(f)
        self.assertEqual(result["crude_or_status"], "undefined")
        self.assertIsNone(result["continuous_spearman_on_virtual_rows"])
        f["hb_g_l"] = [100, 121]
        self.assertEqual(evaluate(f)["crude_or_status"], "positive_infinity")


if __name__ == "__main__":
    unittest.main()
