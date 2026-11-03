"""Pre-fit checks using invented summaries/laws only; writes no row tables."""
import json
import unittest
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import generator
import statistical_fit as sf


TOY_MARGINALS = {
    "age": dict(mean=55.0, sd=10.0, q10=41, median=55, q90=69),
    "bmi": dict(mean=25.0, sd=4.0, q10=20.0, median=25.0, q90=30.0),
    "glucose": dict(mean=6.0, sd=2.0, q10=4.0, median=5.5, q90=8.0),
    "hba1c": dict(mean=6.0, sd=1.0, q10=5.0, median=5.8, q90=7.0),
}


def toy_parameters():
    margins = {"age": sf._fit_age(TOY_MARGINALS["age"])[0]}
    for name in ("bmi", "glucose", "hba1c"):
        margins[name] = sf._fit_continuous(TOY_MARGINALS[name])[0]
    return {"family": sf.FAMILY, "n_rows": 3000, "margins": margins,
            "female_probability": 0.45,
            "dependence": {"tail_probability": 0.08, "rho_body": 0.15,
                           "rho_tail": sf.TAIL_RHO, "age_common": 0.25,
                           "age_difference": 0.1, "bmi_common": 0.4}}


class InventedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parameters = toy_parameters()
        cls.diag = sf.law_diagnostics(cls.parameters, order=512)

    def test_marginal_equations_and_covariance_symmetry(self):
        for name, target in TOY_MARGINALS.items():
            actual = self.diag["marginal"][name]
            for stat in sf.STATS:
                self.assertAlmostEqual(actual[stat], target[stat], places=6)
        cov = np.asarray(self.diag["covariance"])
        np.testing.assert_allclose(cov, cov.T, rtol=0, atol=1e-14)
        self.assertGreater(np.linalg.eigvalsh(cov).min(), 0)
        # Check each projection separately; E1/E2 have different adjustment sets.
        for label, ix, term in (("E1", [0, 1, 2], 2), ("E2", [0, 1, 3], 3),
                                ("E3", [1, 2, 3, 0], 0)):
            beta = np.linalg.lstsq(cov[np.ix_(ix, ix)], cov[ix, 4], rcond=None)[0]
            self.assertAlmostEqual(beta[ix.index(term)], self.diag["estimands"][label], places=12)

    def test_sampler_and_actual_law_agree_on_invented_distribution(self):
        draw = generator.generate_rows(self.parameters, 40000, 901)
        values = draw[list(sf.VARIABLES)].to_numpy(float)
        self.assertTrue(np.isfinite(values).all())
        self.assertTrue(draw.age.between(35, 74).all())
        self.assertTrue(draw.age.eq(np.floor(draw.age)).all())
        self.assertTrue(draw.female.isin([0, 1]).all())
        self.assertTrue((draw[["bmi", "glucose", "hba1c"]] > 0).all().all())
        observed = np.cov(values, rowvar=False)
        expected = np.asarray(self.diag["covariance"])
        scale = np.sqrt(np.outer(np.diag(expected), np.diag(expected)))
        self.assertLess(np.max(np.abs(observed - expected) / scale), 0.035)
        self.assertLess(abs(spearmanr(draw.glucose, draw.hba1c).statistic
                            - self.diag["joint"]["spearman"]), 0.02)

    def test_both_interfaces_and_determinism(self):
        a = generator.generate(None, {"parameters": self.parameters}, 902)
        b = generator.generate(None, {"parameters": self.parameters}, 902)
        pd.testing.assert_frame_equal(a, b)
        self.assertEqual(len(a), 3000)
        observed = pd.DataFrame({"row_id": ["a", "b", "c"]})
        c = generator.generate(observed, self.parameters, 903)
        self.assertEqual(c.row_id.tolist(), ["a", "b", "c"])

    def test_complete_locked_fit_on_invented_targets(self):
        summary = {"n": 1000, "diagnostics": {"marginal": self.diag["marginal"],
                   "joint": self.diag["joint"]}, "estimands": {
                       k: {"coefficient": v} for k, v in self.diag["estimands"].items()}}
        fitted = sf.fit(summary)
        self.assertEqual(len(fitted["usage_ledger"]), 30)
        self.assertEqual(len(fitted["fit_diagnostics"]["optimizer_runs"]), 6)
        self.assertTrue(fitted["fit_diagnostics"]["generation_allowed"])
        self.assertLess(max(abs(v) for v in fitted["fit_diagnostics"]["joint_native_residual"]), 0.003)
        self.assertLess(max(abs(v) for v in fitted["fit_diagnostics"]["estimand_native_residual"]), 0.002)
        json.dumps(fitted, allow_nan=False)
        # Only aggregate invented-fit diagnostics are printed; no row matrix persists.
        print("INVENTED_FIT_AGGREGATE " + json.dumps({k: fitted["fit_diagnostics"][k]
              for k in ("wall_seconds", "generation_allowed", "integration_checks",
                        "joint_native_residual", "estimand_native_residual")}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
