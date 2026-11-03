"""Invented analytic fixtures only: no rows, source fits or clinical effects."""
import copy
import ast
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

import moment_reference as mr
import build_spec
import generator


def normal(mean=0.0, sd=1.0):
    return {"kind": "normal", "mean": mean, "sd": sd}


def context(marginals, constraints):
    return {"role": "external_source", "source_context_id": "invented_fixture",
            "marginals": marginals, "constraints": constraints,
            "assumptions": ["Invented continuous source; binary nuisance independent if present"]}


def slope(eid, value, predictor, adjustments=()):
    return {"evidence_id": eid, "value": value, "numerical_scale": 1.0,
            "operator": {"kind": "ols_coefficient", "outcome": "y",
                         "regressors": [*adjustments, predictor], "term": predictor}}


class MomentReferenceTests(unittest.TestCase):
    def test_empty_information_is_maximum_entropy_independence(self):
        result = mr.fit_context(context({"x": normal(), "y": normal()}, []))
        self.assertTrue(result["success"])
        np.testing.assert_array_equal(result["latent_correlation"], np.eye(2))
        self.assertEqual(result["sampled_rows"], 0)
        self.assertFalse(result["execution_authorized"])

    def test_separate_projections_are_not_joint_coefficients(self):
        margins = {"x": normal(), "z": normal(), "y": normal()}
        result = mr.fit_context(context(margins, [slope("x_projection", 0.6, "x"),
                                                 slope("z_projection", 0.3, "z")]))
        self.assertTrue(result["success"], result)
        r = np.array(result["latent_correlation"])
        # Gaussian max entropy completion has x independent of z conditional on y.
        self.assertAlmostEqual(r[0, 1], 0.6 * 0.3, places=5)
        separate = mr.statistic(margins, r, slope("unused", 0, "x")["operator"])
        joint = mr.statistic(margins, r, slope("unused", 0, "x", ["z"])["operator"])
        self.assertAlmostEqual(separate, 0.6, places=6)
        self.assertAlmostEqual(joint, (0.6 - 0.18 * 0.3) / (1 - 0.18 ** 2), places=5)
        self.assertGreater(abs(joint - separate), 0.02)

    def test_binary_nuisance_is_explicitly_independent(self):
        margins = {"age": normal(45, 8), "female": {"kind": "bernoulli", "probability": 0.4},
                   "x": normal(10, 2), "y": normal(20, 3)}
        result = mr.fit_context(context(margins, [slope("separate", 0.4, "x", ["age", "female"])]))
        self.assertTrue(result["success"], result)
        r = np.array(result["latent_correlation"])
        np.testing.assert_array_equal(r[1, [0, 2, 3]], [0, 0, 0])

    def test_lognormal_pearson_and_rank_are_different(self):
        margins = {"x": mr.lognormal_from_mean_sd(10, 4), "y": mr.lognormal_from_mean_sd(20, 12)}
        r = np.array([[1, 0.55], [0.55, 1]])
        pearson = mr.statistic(margins, r, {"kind": "pearson_correlation", "columns": ["x", "y"]})
        spearman = mr.statistic(margins, r, {"kind": "spearman_correlation", "columns": ["x", "y"]})
        expected = 10 * 20 * math.expm1(0.55 * margins["x"]["sigma"] * margins["y"]["sigma"]) / (4 * 12)
        self.assertAlmostEqual(pearson, expected, places=12)
        self.assertAlmostEqual(spearman, 6 / math.pi * math.asin(0.55 / 2), places=12)
        self.assertGreater(abs(pearson - spearman), 0.01)

    def test_units_change_slope_but_not_fitted_dependence(self):
        base = context({"x": normal(10, 2), "y": normal(20, 3)}, [slope("s", 0.4, "x")])
        converted = copy.deepcopy(base)
        converted["marginals"]["x"] = normal(100, 20)
        converted["constraints"][0]["value"] /= 10
        converted["constraints"][0]["numerical_scale"] /= 10
        left, right = mr.fit_context(base), mr.fit_context(converted)
        self.assertTrue(left["success"] and right["success"])
        np.testing.assert_allclose(left["latent_correlation"], right["latent_correlation"], atol=1e-7)

    def test_incompatible_constraints_do_not_silently_fit(self):
        result = mr.fit_context(context({"x": normal(), "y": normal()},
                                        [slope("one", 0.2, "x"), slope("two", 0.7, "x")]))
        self.assertFalse(result["success"])
        self.assertGreater(result["max_scaled_constraint_residual"], 0.1)

    def test_unavailable_source_dispersion_is_not_invented(self):
        with self.assertRaises(ValueError):
            mr.lognormal_from_mean_sd(4.0, 0.0)
        with self.assertRaises(ValueError):
            mr.fit_context({**context({"x": normal(), "y": normal()}, []), "target_estimate": 0.2})
        with self.assertRaises(ValueError):
            mr.fit_context({**context({"x": normal(), "y": normal()}, []), "role": "target"})

    def test_truncated_source_moments_are_fitted_before_sampling(self):
        m = mr.truncated_lognormal_from_mean_sd(10.0, 2.0, 0.0, 15.0)
        mean, variance = mr.marginal_moments(m)
        self.assertAlmostEqual(mean, 10.0, places=6)
        self.assertAlmostEqual(variance, 4.0, places=6)
        with self.assertRaises(ValueError):
            mr.truncated_lognormal_from_mean_sd(10.0, 10.0, 0.0, 15.0)

    def test_uniform_normal_quadrature_matches_analytic_identity(self):
        cov = mr.pair_covariance({"kind": "uniform", "low": 2.0, "high": 8.0}, normal(5, 3), 0.4)
        self.assertAlmostEqual(cov, 6 * 3 * 0.4 / (2 * math.sqrt(math.pi)), places=8)

    def test_quantile_fit_retains_mismatch(self):
        fit = mr.lognormal_from_quartiles(8.0, 10.0, 15.0)
        self.assertEqual(len(fit["raw_residuals"]), 3)
        self.assertGreater(max(map(abs, fit["raw_residuals"])), 0.01)

    def test_shifted_lognormal_preserves_native_positive_scale(self):
        base = mr.lognormal_from_mean_sd(8.0, 2.0)
        shifted = mr.shifted_lognormal_from_mean_sd(11.0, 2.0, 3.0)
        np.testing.assert_allclose(mr.marginal_moments(shifted), (11.0, 4.0), rtol=1e-12)
        self.assertAlmostEqual(mr.pair_covariance(base, shifted, 0.4),
                               mr.pair_covariance(base, base, 0.4), places=12)

    def test_complete_builder_and_sampler_validation_without_random_rows(self):
        # Invented source inputs deliberately differ from the clinical packets.
        points = {"J_T1_age_mean_task": 50.0, "J_T1_age_sd_task": 6.0,
                  "J_T1_bmi_mean_task": 22.0, "J_T1_bmi_sd_task": 3.0,
                  "J_T1_glucose_mean_mg_dL_derived": 90.0, "J_T1_glucose_sd_mg_dL_derived": 10.0,
                  "J_T1_hba1c_mean_ifcc": 40.0, "J_T1_hba1c_sd_ifcc": 4.0,
                  "J_T1_female_proportion_derived": 0.5,
                  "J_T2_bmi_slope_task_derived": 0.015, "J_T2_glucose_slope_task_derived": 0.006,
                  "P_NHANES_age_slope": 0.008}
        packet = {"items": [{"id": k, "estimate": v} for k, v in points.items()]}
        units = {"row_id": "identifier", "age": "year", "female": "1", "bmi": "kg/m^2", "glucose": "mg/dL", "hba1c": "%"}
        task = {"mode": "whole_cohort", "n_rows": 3000,
                "columns": [{"name": k, "unit": v, **({"minimum": 25, "maximum": 79} if k == "age" else {})}
                            for k, v in units.items()]}
        with patch("numpy.random.default_rng", side_effect=AssertionError("No random rows allowed in fixture")):
            spec = build_spec.build_spec("ENSANUT2018", "E1", json.dumps(packet), json.dumps(task))
            matrices = generator.validate_parameters(spec["parameters"])
            compiled = {"items": [{"id": name} for name in points] + [{"id": "NGSP_UNIT_GUIDANCE"}]}
            packaged = build_spec.build_harness_spec("ENSANUT2018", "E1", json.dumps(packet), json.dumps(task), json.dumps(compiled))
            from cohort_harness.contracts import validate_spec
            validate_spec(packaged["model_spec"], {x["id"] for x in compiled["items"]})
            generator.validate_parameters(packaged["model_spec"]["parameters"])
        self.assertEqual(set(packaged["model_spec"]["parameter_provenance"]), set(packaged["model_spec"]["parameters"]))
        self.assertEqual(len(packaged["trace_sha256"]), 64)
        self.assertEqual(len(matrices), 1)
        self.assertEqual(len(spec["parameter_provenance"]["source_fit_reports"][0]["source_checks"]), 2)
        self.assertEqual(spec["parameter_provenance"]["unhandled_relational_items"][0]["evidence_id"], "P_NHANES_age_slope")
        self.assertEqual(spec["parameter_provenance"]["sampled_rows"], 0)
        self.assertFalse(spec["parameter_provenance"]["execution_authorized"])
        self.assertEqual(spec["parameters"]["transport"]["rows_per_age_sex_cell"], 375)
        bad = copy.deepcopy(spec["parameters"])
        bad["units"]["glucose"] = "mmol/L"
        with self.assertRaises(ValueError):
            generator.validate_parameters(bad)

    def test_sampler_static_boundary_has_no_io_or_fitting(self):
        tree = ast.parse(Path(generator.__file__).read_text(encoding="utf-8"))
        imports = {a.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for a in node.names}
        imports |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual(imports, {"math", "statistics", "numpy", "pandas"})
        called_names = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        self.assertFalse(called_names & {"open", "fit_context", "build_spec", "eval", "exec"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
