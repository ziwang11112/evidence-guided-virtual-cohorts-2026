"""Independent artificial arithmetic checks; no file or participant-data reads."""

from itertools import product
import unittest

import numpy as np
import pandas as pd

import analytical_engine as engine


def factorial_fixture(*, correlated_glucose=False, residual=0.0):
    """Full factorial, whose orthogonal contrasts give coefficients by hand."""
    rows = []
    for age_start, female in product((25, 40, 55, 70), (0, 1)):
        for age_offset, bmi_contrast, glucose_contrast in product((1, 3), (-1, 1), (-1, 1)):
            age = age_start + age_offset
            age10 = (age - 50) / 10
            glucose10 = glucose_contrast + (0.5 * bmi_contrast if correlated_glucose else 0)
            hba1c = (5 + 0.12 * age10 + 0.3 * female + 0.2 * bmi_contrast
                     + 0.4 * glucose10 + residual * bmi_contrast * glucose_contrast)
            rows.append((age, female, 25 + 5 * bmi_contrast, 100 + 10 * glucose10, hba1c))
    return pd.DataFrame(rows, columns=engine.SCIENTIFIC_COLUMNS)


def add_clusters(frame, *, split_by="female"):
    frame = frame.copy()
    frame["lab_est_dis"] = "one_stratum"
    frame["lab_upm_dis"] = frame[split_by]
    return frame


class FixedDraws:
    """Predetermined cluster choices, to check hand-expanded row arithmetic."""
    def __init__(self, choices):
        self.choices = list(choices)
        self.calls = []

    def integers(self, low, high, size):
        self.calls.append((low, high, size))
        result = self.choices.pop(0)
        if len(result) != size:
            raise AssertionError("Unexpected number of draws")
        return np.array(result)


class AnalyticalEngineTests(unittest.TestCase):
    def test_balanced_weights_have_unit_total_and_eighth_cell_mass(self):
        frame = factorial_fixture()
        weights = engine.demographic_weights(frame)
        np.testing.assert_allclose(weights, np.full(64, 1 / 64), rtol=0, atol=0)
        self.assertEqual(float(weights.sum()), 1.0)
        np.testing.assert_allclose(weights.reshape(8, 8).sum(axis=1), 1 / 8)

    def test_unbalanced_cells_are_standardized_not_row_averaged(self):
        base = factorial_fixture()
        frame = pd.concat([pd.concat([base.iloc[8*i:8*(i+1)]] * (i+1)) for i in range(8)])
        weights = engine.demographic_weights(frame)
        offset = 0
        for i in range(8):
            count = 8 * (i+1)
            np.testing.assert_allclose(weights[offset:offset+count], 1/(8*count))
            self.assertAlmostEqual(float(weights[offset:offset+count].sum()), 1/8)
            offset += count
        result = engine.analyze_cohort(frame)
        # Eight cell means are 27,27,42,42,57,57,72,72: standardized age mean 49.5.
        self.assertAlmostEqual(result["diagnostics"]["age"]["mean"], 49.5)
        self.assertNotAlmostEqual(frame["age"].mean(), 49.5)
        for key, value in engine.analyze_cohort(base)["questions"].items():
            self.assertAlmostEqual(result["questions"][key], value, places=12)

    def test_known_linear_coefficients_and_unit_scales(self):
        result = engine.analyze_cohort(factorial_fixture())
        coefficients = result["models"]["Q1_Q3_full"]["coefficients"]
        expected = dict(intercept=5, age10=0.12, female=0.3, bmi5=0.2, glucose10=0.4)
        for key, value in expected.items():
            self.assertAlmostEqual(coefficients[key], value, places=12)
        self.assertAlmostEqual(result["questions"]["Q1_age10"], 0.12)
        self.assertAlmostEqual(result["questions"]["Q2_bmi5"], 0.2)
        self.assertAlmostEqual(result["questions"]["Q3_bmi5"], 0.2)
        self.assertAlmostEqual(result["secondary"]["glucose10_age_sex"], 0.4)

    def test_correlated_glucose_gives_hand_calculated_bmi_change(self):
        result = engine.analyze_cohort(factorial_fixture(correlated_glucose=True))
        # G = .5*B + Z; Y = ... + .2*B + .4*G, so marginal B slope is .4.
        self.assertAlmostEqual(result["questions"]["Q2_bmi5"], 0.4)
        self.assertAlmostEqual(result["questions"]["Q3_bmi5"], 0.2)
        self.assertAlmostEqual(result["questions"]["Q2_minus_Q3_bmi5"], 0.2)
        # Cov(B,G)/Var(G) = .5/1.25; glucose-only slope .4 + .2*.4 = .48.
        self.assertAlmostEqual(result["secondary"]["glucose10_age_sex"], 0.48)

    def test_population_sd_and_residual_rms_have_no_df_correction(self):
        result = engine.analyze_cohort(factorial_fixture(correlated_glucose=True, residual=0.6))
        # B*Z is orthogonal to every model column and equals +/-1 in equal weights.
        self.assertAlmostEqual(result["q1_residual_rms"], 0.6, places=12)
        for field, mean, sd in (("female", .5, .5), ("bmi", 25, 5),
                                ("glucose", 100, 10*np.sqrt(1.25))):
            self.assertAlmostEqual(result["diagnostics"][field]["mean"], mean)
            self.assertAlmostEqual(result["diagnostics"][field]["sd_population"], sd)
        self.assertEqual(set(result["diagnostics"]), set(engine.SCIENTIFIC_COLUMNS))
        for summary in result["diagnostics"].values():
            self.assertEqual(set(summary), {"mean", "sd_population", "q10", "q50", "q90"})

    def test_quantiles_use_smallest_value_reaching_mass_without_interpolation(self):
        values, weights = [10, 2, 4, 1], [3, 4, 2, 1]
        for q, expected in ((0, 1), (.1, 1), (.5, 2), (.500001, 4), (.9, 10), (1, 10)):
            self.assertEqual(engine.weighted_quantile(values, weights, q), expected)

    def test_quantiles_ignore_zero_mass_and_handle_ties(self):
        values, weights = [-100, 2, 2, 5], [0, 2, 3, 5]
        self.assertEqual(engine.weighted_quantile(values, weights, 0), 2)
        self.assertEqual(engine.weighted_quantile(values, weights, .5), 2)
        self.assertEqual(engine.weighted_quantile(values, weights, .9), 5)

    def test_quantiles_invariant_to_repeated_support_within_cells(self):
        base = factorial_fixture()
        unbalanced = pd.concat([pd.concat([base.iloc[8*i:8*(i+1)]] * (i+1)) for i in range(8)])
        expected = engine.analyze_cohort(base)["diagnostics"]
        observed = engine.analyze_cohort(unbalanced)["diagnostics"]
        for field in engine.SCIENTIFIC_COLUMNS:
            for quantile in ("q10", "q50", "q90"):
                with self.subTest(field=field, quantile=quantile):
                    self.assertEqual(observed[field][quantile], expected[field][quantile])

    def test_quantile_half_mass_does_not_round_tied_masses_separately(self):
        # Independent review reproduction: the first four cells have exact mass 1/2.
        counts = [6, 8, 6, 21, 15, 7, 13, 19]
        ages = [28,33,36,39,31,37,33,26,33,28,31,26,36,28,43,49,50,45,51,45,
                47,52,47,40,48,43,44,46,49,41,45,41,41,43,47,50,46,41,50,52,54,
                56,62,62,62,60,55,68,61,60,62,55,55,55,61,60,55,64,64,56,56,63,61,
                77,78,76,71,76,79,70,76,74,79,78,70,77,71,73,74,78,77,72,74,79,
                76,72,78,70,75,79,75,72,72,78,76]
        weights = np.concatenate([np.full(count, 1/(8*count)) for count in counts])
        self.assertEqual(engine.weighted_quantile(ages, weights, .5), 54)

    def test_quantiles_reject_invalid_vectors(self):
        for values, weights, q in (([], [], .5), ([1], [-1], .5), ([1], [0], .5),
                                    ([np.nan], [1], .5), ([1], [np.inf], .5),
                                    ([1], [1, 2], .5), ([1], [1], -0.1)):
            with self.subTest(values=values, weights=weights, q=q):
                with self.assertRaises(engine.InputValidationError):
                    engine.weighted_quantile(values, weights, q)

    def test_age_edges_assign_exactly_eight_prespecified_cells(self):
        frame = factorial_fixture()
        frame["age"] = np.repeat([25, 39, 40, 54, 55, 69, 70, 79], 8)
        frame["female"] = np.tile(np.repeat([0, 1], 4), 8)
        np.testing.assert_allclose(engine.demographic_weights(frame), 1 / 64)

    def test_missing_demographic_cell_stops_analysis(self):
        frame = factorial_fixture()
        frame = frame[~((frame.age < 40) & (frame.female == 1))]
        with self.assertRaises(engine.EmptyDemographicCellError):
            engine.analyze_cohort(frame)

    def test_invalid_scientific_fields_are_rejected(self):
        for field, invalid in (("age", 24), ("age", 80), ("age", 50.5),
                                ("female", 2), ("female", .5), ("bmi", np.nan),
                                ("glucose", np.inf), ("hba1c", -np.inf)):
            with self.subTest(field=field, invalid=invalid):
                frame = factorial_fixture().astype(float)
                frame.loc[0, field] = invalid
                with self.assertRaises(engine.InputValidationError):
                    engine.analyze_cohort(frame)

    def test_missing_column_empty_table_and_duplicate_names_are_rejected(self):
        base = factorial_fixture()
        for frame in (base.drop(columns="bmi"), base.iloc[:0],
                      pd.concat([base, base[["age"]]], axis=1)):
            with self.assertRaises(engine.InputValidationError):
                engine.analyze_cohort(frame)

    def test_target_physical_validity_rejects_entire_table_without_filtering(self):
        for field, invalid in (("bmi", 0), ("bmi", -1), ("glucose", 0),
                                ("glucose", -1), ("glucose", 126), ("glucose", 127),
                                ("hba1c", 0), ("hba1c", -1)):
            with self.subTest(field=field, invalid=invalid):
                frame = factorial_fixture().astype(float)
                frame.loc[0, field] = invalid
                with self.assertRaises(engine.InputValidationError):
                    engine.analyze_cohort(frame)
                self.assertEqual(len(frame), 64)
                self.assertEqual(frame.loc[0, field], invalid)

    def test_exact_and_numerical_rank_deficiency_are_rejected(self):
        for tiny in (0.0, 1e-14):
            with self.subTest(tiny=tiny):
                frame = factorial_fixture()
                frame["bmi"] = 25.0 + tiny*(frame.bmi-25)/5
                with self.assertRaises(engine.SingularDesignError):
                    engine.analyze_cohort(frame)

    def test_rank_tolerance_uses_explicit_max_shape_epsilon_s0(self):
        result = engine.analyze_cohort(factorial_fixture())
        model = result["models"]["Q1_Q3_full"]
        expected = 64 * np.finfo(np.float64).eps * model["singular_values"][0]
        self.assertEqual(model["rank_tolerance"], expected)
        self.assertEqual(model["rank"], 5)

    def test_cluster_pair_identity_duplicates_and_singleton(self):
        frame = factorial_fixture().iloc[:6].copy()
        frame["lab_est_dis"] = ["A", "A", "A", "B", "B", "B"]
        frame["lab_upm_dis"] = ["one", "two", "two", "one", "one", "one"]
        frame.index = [99, 99, 8, 8, -1, -1]
        rng = FixedDraws([[1, 1]])
        indices = engine.draw_cluster_indices(frame, rng)
        np.testing.assert_array_equal(indices, [1, 2, 1, 2, 3, 4, 5])
        self.assertEqual(rng.calls, [(0, 2, 2)])
        self.assertEqual(rng.choices, [])

    def test_duplicated_clusters_recompute_group_denominators(self):
        base = factorial_fixture()
        # Three complete-cohort clusters with different row counts; select B,B,A.
        frame = pd.concat([base, base, base, base], ignore_index=True)
        frame["lab_est_dis"] = "A"
        frame["lab_upm_dis"] = np.repeat(["first", "second", "second", "third"], 64)
        indices = engine.draw_cluster_indices(frame, FixedDraws([[1, 1, 0]]))
        replicate = frame.iloc[indices]
        weights = engine.demographic_weights(replicate)
        self.assertEqual(len(replicate), 320)
        np.testing.assert_allclose(weights, 1/320)
        # Each second-cluster original appears twice: 2/320; first appears once: 1/320.
        aggregate = np.bincount(indices, weights=weights, minlength=len(frame))
        np.testing.assert_allclose(aggregate[:64], 1/320)
        np.testing.assert_allclose(aggregate[64:192], 2/320)
        np.testing.assert_array_equal(aggregate[192:], 0)
        self.assertAlmostEqual(engine.analyze_cohort(replicate)["questions"]["Q1_age10"], .12)

    def test_singleton_resampling_is_point_mass_and_keeps_fixed_attempts(self):
        frame = factorial_fixture()
        frame["lab_est_dis"] = "one"
        frame["lab_upm_dis"] = "only"
        result = engine.cluster_stability(frame, attempts=7)
        self.assertEqual((result["attempted"], result["valid"], result["failed"]), (7, 7, 0))
        self.assertEqual(result["singleton_lab_strata"], 1)
        for key, band in result["bands"].items():
            self.assertEqual(band["lower"], band["upper"])
        self.assertAlmostEqual(result["bands"]["Q1_age10"]["lower"], .12)

    def test_default_attempts_and_deterministic_empty_cell_failures(self):
        result = engine.cluster_stability(add_clusters(factorial_fixture()))
        self.assertEqual(result["seed"], 18301)
        self.assertEqual(result["attempted"], 399)
        # Fixed independent stream check: 399 pairs of fair 0/1 choices, seed 18301.
        self.assertEqual(result["valid"], 193)
        self.assertEqual(result["failed"], 206)
        self.assertEqual(result["failure_counts"], {"empty_demographic_cell": 206, "singular_design": 0})
        self.assertEqual(len(result["valid_attempts"])+len(result["failure_attempts"]), 399)

    def test_singular_replicates_count_without_adaptive_retries(self):
        result = engine.cluster_stability(add_clusters(factorial_fixture(), split_by="bmi"), attempts=9)
        self.assertEqual(result["attempted"], 9)
        self.assertEqual(result["valid"], 3)
        self.assertEqual(result["failure_counts"], {"empty_demographic_cell": 0, "singular_design": 6})

    def test_no_valid_replicates_reports_unavailable_bands(self):
        result = engine.cluster_stability(add_clusters(factorial_fixture()), attempts=1, seed=0)
        self.assertEqual((result["valid"], result["failed"]), (0, 1))
        self.assertEqual(result["band_status"], "unavailable_no_valid_replicates")
        self.assertTrue(all(band is None for band in result["bands"].values()))

    def test_band_endpoints_are_linear_percentiles_of_valid_replicates(self):
        base = factorial_fixture(residual=.2)
        frame = pd.concat([base.assign(hba1c=base.hba1c+shift) for shift in (0, 1, 4)], ignore_index=True)
        frame["lab_est_dis"] = "one"
        frame["lab_upm_dis"] = np.repeat(["A", "B", "C"], 64)
        result = engine.cluster_stability(frame, attempts=11, seed=4)
        self.assertEqual(result["valid"], 11)
        estimates = sorted(row["hba1c.mean"] for row in result["valid_replicate_estimates"])
        # For eleven sorted values, numpy linear 2.5th/97.5th positions are .25 and 9.75.
        lower = .75*estimates[0] + .25*estimates[1]
        upper = .25*estimates[9] + .75*estimates[10]
        self.assertAlmostEqual(result["bands"]["hba1c.mean"]["lower"], lower)
        self.assertAlmostEqual(result["bands"]["hba1c.mean"]["upper"], upper)
        self.assertEqual(len(result["bands"]), 31)

    def test_identical_inputs_and_seed_produce_identical_outputs(self):
        frame = add_clusters(factorial_fixture(residual=.1))
        first = engine.cluster_stability(frame, attempts=13, seed=31)
        second = engine.cluster_stability(frame, attempts=13, seed=31)
        self.assertEqual(first, second)

    def test_cluster_fields_required_only_for_resampling(self):
        base = factorial_fixture()
        self.assertEqual(engine.analyze_cohort(base)["n"], 64)
        with self.assertRaises(engine.InputValidationError):
            engine.cluster_stability(base, attempts=1)
        for column in engine.CLUSTER_COLUMNS:
            frame = add_clusters(base)
            frame[column] = frame[column].astype(object)
            frame.loc[0, column] = None
            with self.assertRaises(engine.InputValidationError):
                engine.cluster_stability(frame, attempts=1)

    def test_invalid_attempts_and_seed_rejected(self):
        frame = add_clusters(factorial_fixture())
        for attempts in (0, -1, 1.5, True):
            with self.assertRaises(engine.InputValidationError):
                engine.cluster_stability(frame, attempts=attempts)
        for seed in (-1, .5, True):
            with self.assertRaises(engine.InputValidationError):
                engine.cluster_stability(frame, attempts=1, seed=seed)

    def test_analysis_and_resampling_do_not_mutate_input(self):
        frame = add_clusters(factorial_fixture())
        before = frame.copy(deep=True)
        engine.analyze_cohort(frame)
        engine.cluster_stability(frame, attempts=3)
        pd.testing.assert_frame_equal(frame, before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
