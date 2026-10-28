import math
import unittest

import numpy as np
import pandas as pd

from biomedical_research.population_framework.observers import (
    compare_invariants, derive, observe, validate_frame,
)


class ObserverTests(unittest.TestCase):
    def test_paired_change_sd_is_not_marginal_sd_difference(self):
        original = pd.DataFrame({"before": [1., 2., 3.], "after": [3., 2., 1.]})
        data = derive(original, [{"name": "change", "kind": "difference",
                                  "left": "after", "right": "before"}])
        self.assertEqual(observe(data, {"kind": "sd", "column": "change"}), 2.)
        self.assertEqual(observe(data, {"kind": "sd", "column": "after"}), 1.)
        self.assertNotIn("change", original)

    def test_regression_and_residual_denominator(self):
        # Centered residuals [1, -1, -1, 1] are orthogonal to [0, 1, 2, 3].
        data = pd.DataFrame({"x": [0., 1., 2., 3.], "y": [2., 2., 4., 8.]})
        common = {"x": "x", "y": "y"}
        self.assertAlmostEqual(observe(data, {**common, "kind": "ols_slope"}), 2.)
        self.assertAlmostEqual(observe(data, {**common, "kind": "ols_intercept"}), 1.)
        self.assertAlmostEqual(observe(data, {**common, "kind": "residual_sd"}), math.sqrt(2))
        self.assertAlmostEqual(observe(data, {**common, "kind": "correlation"}), math.sqrt(5 / 6))

    def test_probability_filters_and_where_use_subset_denominator(self):
        data = pd.DataFrame({"x": [0, 1, 2, 3], "group": ["a", "a", "b", "b"]})
        self.assertEqual(observe(data, {"kind": "probability",
            "where": [{"column": "group", "op": "eq", "value": "b"}],
            "filters": [{"column": "x", "op": "ge", "value": 3}]}), .5)
        self.assertEqual(observe(data, {"kind": "probability", "filters": [
            {"column": "x", "op": "gt", "value": 0},
            {"column": "x", "op": "le", "value": 2}]}), .5)
        with self.assertRaises(ValueError):
            observe(data, {"kind": "mean", "column": "x", "where": [
                {"column": "group", "op": "eq", "value": "absent"}]})

    def test_undefined_statistics_raise(self):
        data = pd.DataFrame({"x": [1., 1.], "y": [2., 3.]})
        for kind in ("correlation", "ols_slope", "ols_intercept", "residual_sd"):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                observe(data, {"kind": kind, "x": "x", "y": "y"})
        with self.assertRaises(ValueError):
            observe(data, {"kind": "correlation", "x": "y", "y": "x"})
        with self.assertRaises(ValueError):
            observe(data.iloc[:1], {"kind": "sd", "column": "x"})
        with self.assertRaises(ValueError):
            observe(pd.DataFrame({"x": [0, 1], "y": [0, 2]}),
                    {"kind": "residual_sd", "x": "x", "y": "y"})

    def test_derived_ratio_domains_and_values(self):
        data = pd.DataFrame({"before": [4., 8.], "after": [2., 12.]})
        result = derive(data, [
            {"name": "pct", "kind": "percent_change", "left": "after", "right": "before"},
            {"name": "log", "kind": "log_ratio", "left": "after", "right": "before"}])
        np.testing.assert_allclose(result["pct"], [-50, 50])
        np.testing.assert_allclose(result["log"], [math.log(.5), math.log(1.5)])
        for kind, left, right in (("percent_change", 1, 0), ("log_ratio", 0, 1),
                                  ("log_ratio", -1, -2), ("difference", np.inf, 1)):
            with self.subTest(kind=kind, left=left, right=right), self.assertRaises(ValueError):
                derive(pd.DataFrame({"l": [left], "r": [right]}),
                       [{"name": "z", "kind": kind, "left": "l", "right": "r"}])
        with self.assertRaises(ValueError):
            derive(data, [{"name": "before", "kind": "difference", "left": "after", "right": "before"}])

    def test_schema_finite_bounds_categories_and_extra_columns(self):
        schema = {"x": {"type": "number", "exclusive_minimum": 0, "maximum": 3},
                  "group": {"type": "category", "values": ["a", "b"]}}
        valid = pd.DataFrame({"x": ["1", "2"], "group": ["a", "b"], "extra": [3, 4]})
        result = validate_frame(valid, 2, schema)
        self.assertIn("extra", result)
        self.assertEqual(valid.x.iloc[0], "1")
        self.assertEqual(result.x.iloc[0], 1.)
        for changed in (valid.assign(x=[0, 1]), valid.assign(x=[1, np.nan]),
                        valid.assign(x=[1, np.inf]), valid.assign(x=[1, 4]),
                        valid.assign(group=["a", "c"]), valid.assign(group=["a", None])):
            with self.assertRaises(ValueError):
                validate_frame(changed, 2, schema)
        with self.assertRaises(ValueError):
            validate_frame(valid, 3, schema)
        with self.assertRaises(ValueError):
            validate_frame(valid.drop(columns="group"), 2, schema)

    def test_invariants_exact_positional_and_row_mismatch(self):
        before = pd.DataFrame({"x": [1., 2.], "category": ["a", "b"]})
        after = before.copy()
        after.index = [4, 7]
        self.assertEqual(compare_invariants(before, after, ["x", "category"])["status"], "pass")
        after.loc[7, "x"] = 2. + 1e-12
        result = compare_invariants(before, after, ["x", "category"])
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["equal_rows"], 1)
        self.assertEqual(result["columns"]["category"]["status"], "pass")
        result = compare_invariants(before, after.iloc[:1], ["x"])
        self.assertEqual(result["status"], "not_testable")
        self.assertIsNone(result["equal_rows"])
        self.assertEqual(compare_invariants(before, after, ["missing"])["status"], "fail")

    def test_quantile_and_bad_filter_rejected(self):
        data = pd.DataFrame({"x": [0, 2, 4]})
        self.assertEqual(observe(data, {"kind": "quantile", "column": "x", "q": .25}), 1.)
        for q in (-.1, 1.1, float("nan")):
            with self.assertRaises(ValueError):
                observe(data, {"kind": "quantile", "column": "x", "q": q})
        with self.assertRaises(ValueError):
            observe(data, {"kind": "probability", "filters": [{"column": "x", "op": "exec", "value": 1}]})


if __name__ == "__main__":
    unittest.main()
