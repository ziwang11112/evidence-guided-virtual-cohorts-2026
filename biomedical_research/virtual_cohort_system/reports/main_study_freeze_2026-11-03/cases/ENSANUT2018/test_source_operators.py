"""Deterministic operator tests using artificial moments, never patient data."""
import unittest
import numpy as np
from source_operators import source_projection


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.variables = ("age", "female", "bmi", "glucose", "hba1c")
        # Correlated artificial predictors; no biological estimates appear.
        a = np.array([[2.,0,0,0],[.2,1,0,0],[.3,.4,2,0],[.2,.1,.5,1]])
        xx = a @ a.T
        beta = np.array([.3,-.2,.7,.5])
        self.cov = np.block([[xx, (xx @ beta)[:,None]],
                             [(xx @ beta)[None,:], np.array([[beta @ xx @ beta + 2.]])]])
        self.mu = np.array([4.,.5,3.,6.,8.])

    def run_projection(self, op, context="lifelines", **changes):
        kwargs = dict(source_context=context, variables=self.variables,
                      mean=self.mu, covariance=self.cov)
        kwargs.update(changes)
        return source_projection(op, **kwargs)

    def test_separate_bmi_projection_matches_partial_covariance_identity(self):
        idx = {name:i for i,name in enumerate(self.variables)}
        j,k = idx["bmi"],idx["hba1c"]
        z = [idx["age"],idx["female"]]
        s = self.cov
        numerator = s[j,k] - s[j,z] @ np.linalg.solve(s[np.ix_(z,z)],s[z,k])
        denominator = s[j,j] - s[j,z] @ np.linalg.solve(s[np.ix_(z,z)],s[z,j])
        got = self.run_projection("J_T2_bmi_slope_task_derived")["value"]
        self.assertAlmostEqual(got, numerator / denominator)
        self.assertNotAlmostEqual(got,.7)  # omitted glucose matters

    def test_joint_age_projection_recovers_declared_toy_law(self):
        got = self.run_projection("P_NHANES_age_slope", "pani")["value"]
        self.assertAlmostEqual(got,.3)

    def test_predictor_unit_conversion(self):
        original = self.run_projection("J_T2_glucose_slope_task_derived")["value"]
        scale = np.array([1.,1.,1.,18.,1.])
        altered = self.run_projection("J_T2_glucose_slope_task_derived",
            mean=self.mu*scale,covariance=self.cov*np.outer(scale,scale))["value"]
        self.assertAlmostEqual(altered,original/18.)

    def test_reject_wrong_context_non_psd_and_singular(self):
        with self.assertRaises(ValueError):
            self.run_projection("J_T2_bmi_slope_task_derived", "target")
        bad = self.cov.copy(); bad[4,4] = -1
        with self.assertRaises(ValueError):
            self.run_projection("J_T2_bmi_slope_task_derived",covariance=bad)
        bad = np.zeros((5,5))
        with self.assertRaises(ValueError):
            self.run_projection("J_T2_bmi_slope_task_derived",covariance=bad)

    def test_reject_nonfinite_and_dimension_mismatch(self):
        bad = self.mu.copy(); bad[0] = np.nan
        with self.assertRaises(ValueError):
            self.run_projection("J_T2_bmi_slope_task_derived",mean=bad)
        with self.assertRaises(ValueError):
            self.run_projection("J_T2_bmi_slope_task_derived",covariance=np.eye(3))

if __name__ == "__main__":
    unittest.main()
