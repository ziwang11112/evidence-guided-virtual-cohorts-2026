"""Toy-only checks; never read real project inputs or reference outcomes."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd
from scipy.stats import t

import evaluate as ev


HERE = Path(__file__).resolve().parent


def toy_tables():
    rng = np.random.default_rng(80201)
    rows = []
    # Third PSU in every stratum is entirely outside the scored domain.
    for h in range(8):
        for j in range(3):
            for k in range(8):
                rows.append({"row_id": f"toy_{h}_{j}_{k}", "weight": str(1+(h+k)%5),
                             "stratum": str(h), "psu": str(j)})
    spine = pd.DataFrame(rows)
    domain = spine[spine.psu != "2"].reset_index(drop=True)
    n = len(domain)
    observed = pd.DataFrame({"row_id": domain.row_id, "bmi": [str(v) for v in rng.uniform(19, 44, n)],
                             "age": [str(v) for v in rng.integers(20, 80, n)],
                             "sex": [str(v) for v in rng.integers(1, 3, n)],
                             "retained_text": ["" if i%3 else "keep this" for i in range(n)],
                             "insulin": [""]*n})
    # Arbitrary mathematical fixture; signs are deliberately not constrained.
    b = (observed.bmi.astype(float).to_numpy()-30)/5
    a = (observed.age.astype(float).to_numpy()-50)/10
    s = (observed.sex == "2").to_numpy(dtype=float)
    insulin = np.exp(1.3-0.27*b+0.11*a-0.18*s+rng.normal(0, 0.2, n))
    reference = domain.copy()
    reference["insulin"] = [str(v) for v in insulin]
    return observed, reference, spine


class EvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="toy_test_", dir=HERE)
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.assertEqual(self.work.parent, HERE)
        self.observed, self.reference, self.spine = toy_tables()
        self.observed_path = self.work/"observed.csv"
        self.observed.to_csv(self.observed_path, index=False)
        self.spec_path = self.work/"frozen.json"
        self.spec = ev.freeze(self.observed_path, self.spec_path)

    def test_predictor_only_freeze_and_reject_unmasked_outcome(self):
        np.testing.assert_allclose(self.spec["bmi_knots"], np.quantile(self.observed.bmi.astype(float), [.1,.5,.9]))
        self.assertEqual(self.spec["predictor_fingerprint"], ev.fingerprint(self.observed))
        self.assertNotIn("insulin", json.dumps(self.spec))
        self.observed.loc[0, "insulin"] = "999"
        other = self.work/"not_masked.csv"
        self.observed.to_csv(other, index=False)
        with self.assertRaisesRegex(ev.EvaluationError, "not wholly withheld"):
            ev.freeze(other, self.work/"invalid.json")

    def test_wls_point_estimate_and_negative_slope_allowed(self):
        X, _ = ev.model_matrices(self.observed, self.spec)["B"]
        y = np.log(self.reference.insulin.astype(float).to_numpy())
        w = self.reference.weight.astype(float).to_numpy()
        beta, cov, diagnostic = ev.taylor_fit(X, y, self.reference, self.spine)
        expected = np.linalg.lstsq(X*np.sqrt(w)[:, None], y*np.sqrt(w), rcond=None)[0]
        np.testing.assert_allclose(beta, expected, atol=1e-12)
        self.assertLess(beta[1], 0)
        self.assertEqual(diagnostic["full_psus"], 24)
        self.assertEqual(diagnostic["domain_psus"], 16)
        self.assertEqual(diagnostic["design_df"], 16)
        self.assertEqual(diagnostic["residual_df"], 13)
        self.assertGreaterEqual(np.linalg.eigvalsh(cov).min(), -1e-14)

    def test_absent_insulin_and_exact_numeric_value_preservation(self):
        observed = self.observed.drop(columns="insulin").copy()
        observed.loc[0, "bmi"] = "21.1"
        absent_path = self.work/"absent_insulin.csv"
        observed.to_csv(absent_path, index=False)
        frozen = ev.freeze(absent_path, self.work/"absent_frozen.json")
        self.assertEqual(frozen["row_count"], len(observed))
        generated = observed.copy()
        generated["insulin"] = self.reference.insulin
        generated.loc[0, "bmi"] = "21.100000000000001"
        generated["age"] = generated.age.map(lambda value: format(float(value), ".1f"))
        generated["sex"] = generated.sex.map(lambda value: format(float(value), ".1f"))
        values, preserved = ev.match_generated(observed, generated)
        self.assertEqual(len(values), len(observed))
        self.assertTrue(preserved)
        # A one-bit numerical change is not formatting and must fail.
        generated.loc[0, "bmi"] = repr(float(np.nextafter(float(observed.loc[0,"bmi"]), np.inf)))
        with self.assertRaisesRegex(ev.EvaluationError, "changed observed cells in bmi"):
            ev.match_generated(observed, generated)
        # Adding even one observed target value is forbidden at freeze time.
        observed["insulin"] = ""
        observed.loc[0, "insulin"] = "0.125"
        observed.to_csv(self.work/"injected_target.csv", index=False)
        with self.assertRaisesRegex(ev.EvaluationError, "not wholly withheld"):
            ev.freeze(self.work/"injected_target.csv", self.work/"injected_spec.json")

    def test_hand_calculated_outside_domain_psu_variance(self):
        domain = pd.DataFrame({"row_id": ["a","b","c"], "weight": ["1"]*3,
                               "stratum": ["s1","s1","s2"], "psu": ["p1","p2","p1"]})
        spine = pd.concat([domain, pd.DataFrame({"row_id":["outside"], "weight":["1"],
                                                "stratum":["s2"], "psu":["p2"]})], ignore_index=True)
        beta, cov, diagnostic = ev.taylor_fit(np.ones((3,1)), [1,3,7], domain, spine)
        self.assertAlmostEqual(beta[0], 11/3)
        self.assertAlmostEqual(cov[0,0], 136/81)
        self.assertEqual(diagnostic["residual_df"], 2)
        ci = ev.linear_contrast(beta, cov, [1], 2)
        self.assertAlmostEqual(ci["ci95_high_log_scale"], 11/3+t.ppf(.975,2)*np.sqrt(136/81))
        with self.assertRaisesRegex(ev.EvaluationError, "Singleton"):
            ev.taylor_fit(np.ones((3,1)), [1,3,7], domain, domain)

    def test_linear_spline_contrast_zero_and_nonlinear_contrast(self):
        X, _ = ev.model_matrices(self.observed, self.spec)["C"]
        chosen = np.array([0.7, -0.13, 0.31, 0.03, -0.09])
        y = X@chosen
        beta, cov, diagnostic = ev.taylor_fit(X, y, self.reference, self.spine)
        contrast = ev.contrasts(self.spec)["C"][0][1]
        actual = ev.linear_contrast(beta, cov, contrast, diagnostic["residual_df"])["estimate_log_scale"]
        q1,q2,q3 = self.spec["bmi_contrast_locations"]
        qx = pd.DataFrame({"bmi":[str(q1),str(q2),str(q3)], "age":["50"]*3,
                           "sex":[self.spec["sex_reference"]]*3})
        qmatrix, _ = ev.model_matrices(qx, self.spec)["C"]
        predictions = qmatrix@chosen
        expected = 5*((predictions[2]-predictions[1])/(q3-q2)-(predictions[1]-predictions[0])/(q2-q1))
        self.assertAlmostEqual(actual, expected, places=11)
        chosen[2] = 0
        beta, cov, diagnostic = ev.taylor_fit(X, X@chosen, self.reference, self.spine)
        self.assertAlmostEqual(float(np.asarray(contrast)@beta), 0, places=11)
        # Restricted cubic basis is linear beyond the upper boundary knot.
        upper = self.spec["bmi_knots"][2]
        values = ev.spline_term([upper+2,upper+3,upper+4], self.spec["bmi_knots"])
        self.assertAlmostEqual(values[2]-2*values[1]+values[0], 0, places=11)

    def test_row_matching_and_preservation(self):
        shuffled = self.reference.sample(frac=1, random_state=8)
        matched = ev.match_reference(self.observed, shuffled, self.spine)
        self.assertEqual(matched.row_id.tolist(), self.observed.row_id.tolist())
        generated = self.observed.copy()
        generated["insulin"] = self.reference.insulin
        generated = generated.sample(frac=1, random_state=9)
        values, order = ev.match_generated(self.observed, generated)
        np.testing.assert_allclose(values, self.reference.insulin.astype(float), rtol=1e-14)
        self.assertFalse(order)
        generated.loc[generated.index[0], "retained_text"] = "changed"
        with self.assertRaisesRegex(ev.EvaluationError, "changed observed cells"):
            ev.match_generated(self.observed, generated)
        with self.assertRaisesRegex(ev.EvaluationError, "row ID sets differ"):
            ev.match_reference(self.observed, self.reference.iloc[1:], self.spine)

    def test_identical_draw_full_evaluation_reports_all_endpoints(self):
        reference_path, spine_path = self.work/"reference.csv", self.work/"spine.csv"
        self.reference.sample(frac=1, random_state=10).to_csv(reference_path, index=False)
        self.spine.to_csv(spine_path, index=False)
        generated_path = self.work/"draw.csv"
        generated = self.observed.copy()
        generated["insulin"] = self.reference.insulin
        generated.to_csv(generated_path, index=False)
        manifest = {"analysis_spec":{"path":"frozen.json", "sha256":ev.sha256(self.spec_path)},
                    "observed_sha256":ev.sha256(self.observed_path),
                    "reference_sha256":ev.sha256(reference_path), "spine_sha256":ev.sha256(spine_path),
                    "draws":[{"model":"toy_revision", "draw_id":"1", "path":"draw.csv", "sha256":ev.sha256(generated_path)}]}
        manifest_path = self.work/"manifest.json"
        ev.json_write(manifest_path, manifest)
        result = ev.evaluate(self.observed_path, reference_path, spine_path, manifest_path, self.work/"scores")
        self.assertEqual(len(result["reference"]["endpoints"]), 8)
        self.assertEqual(len(result["generated"][0]["endpoints"]), 8)
        for row in result["generated"][0]["endpoints"]:
            self.assertAlmostEqual(row["signed_difference_from_reference"], 0)
        self.assertTrue((self.work/"scores"/"endpoints.csv").exists())
        # Mutated artifacts fail before target parsing.
        generated.loc[0, "insulin"] = "500"
        generated.to_csv(generated_path, index=False)
        with self.assertRaisesRegex(ev.EvaluationError, "Generated file hash mismatch"):
            ev.evaluate(self.observed_path, "does-not-exist.csv", spine_path, manifest_path, self.work/"bad_scores")

    def test_weight_scaling_invariance_and_design_mismatch(self):
        X, _ = ev.model_matrices(self.observed, self.spec)["A"]
        y = np.log(self.reference.insulin.astype(float))
        beta, cov, _ = ev.taylor_fit(X, y, self.reference, self.spine)
        domain, spine = self.reference.copy(), self.spine.copy()
        domain["weight"] = (domain.weight.astype(float)*100).astype(str)
        spine["weight"] = (spine.weight.astype(float)*100).astype(str)
        beta2, cov2, _ = ev.taylor_fit(X, y, domain, spine)
        np.testing.assert_allclose(beta, beta2, atol=1e-12)
        np.testing.assert_allclose(cov, cov2, atol=1e-12)
        domain.loc[0, "stratum"] = "wrong"
        with self.assertRaisesRegex(ev.EvaluationError, "stratum mismatch"):
            ev.taylor_fit(X, y, domain, spine)


if __name__ == "__main__":
    unittest.main(verbosity=2)
