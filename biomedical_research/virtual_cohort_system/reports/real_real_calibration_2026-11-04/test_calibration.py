"""Invented in-memory fixtures only; never call the file-backed run entrypoint."""
from __future__ import annotations

import json
import unittest

import numpy as np
import pandas as pd
from scipy import stats

import calibration as target


def invented_frame(n=180, seed=19):
    rng = np.random.Generator(np.random.PCG64(seed))
    age = rng.uniform(35, 74, n)
    bmi = rng.uniform(18, 34, n)
    glucose = rng.uniform(3, 9, n)
    female = rng.integers(0, 2, n)
    return pd.DataFrame({"age": age, "bmi": bmi, "glucose": glucose, "female": female,
                         "hba1c": 1 + .04 * age + .08 * bmi + .3 * glucose + .2 * female + rng.normal(0, .2, n)})


class CalibrationTests(unittest.TestCase):
    def setUp(self):
        self.reference = invented_frame()
        self.reference["survey_commid"] = np.repeat(np.arange(6), 30)
        self.generated = {str(seed): invented_frame(60, seed) for seed in (101, 102, 103)}

    def test_disjoint_reproducible_sampling_and_hashes(self):
        one = target.sample_disjoint_communities(self.reference, 8400, sample_size=60, expected_communities=6)
        two = target.sample_disjoint_communities(self.reference, 8400, sample_size=60, expected_communities=6)
        np.testing.assert_array_equal(one.r1_positions, two.r1_positions)
        self.assertEqual(one.audit, two.audit)
        self.assertEqual(len(set(one.r1_positions)), 60)
        self.assertEqual(len(set(one.r2_positions)), 60)
        self.assertFalse(set(one.r1_positions) & set(one.r2_positions))
        self.assertFalse(set(self.reference.iloc[one.r1_positions].survey_commid)
                         & set(self.reference.iloc[one.r2_positions].survey_commid))
        self.assertEqual(one.audit["R1"]["assigned_community_n"], 3)
        self.assertEqual(len(one.audit["R1"]["selected_row_positions_sha256"]), 64)

    def test_only_size_rejections_and_explicit_exhaustion(self):
        unbalanced = invented_frame(140)
        unbalanced["survey_commid"] = np.repeat(np.arange(4), [60, 60, 10, 10])
        selected = [target.sample_disjoint_communities(unbalanced, seed, sample_size=65, expected_communities=4)
                    for seed in range(8400, 8410)]
        self.assertTrue(any(split.audit["size_rejection_n"] > 0 for split in selected))
        for split in selected:
            for attempt in split.audit["attempts"]:
                feasible = min(attempt["r1_pool_n"], attempt["r2_pool_n"]) >= 65
                self.assertEqual(attempt["accepted"], feasible)
        impossible = invented_frame(100)
        impossible["survey_commid"] = np.repeat(np.arange(4), [70, 10, 10, 10])
        with self.assertRaisesRegex(target.SamplingExhaustedError, "no size-valid partition within 2 attempts") as caught:
            target.sample_disjoint_communities(impossible, 8400, sample_size=40, expected_communities=4, max_attempts=2)
        self.assertEqual(caught.exception.audit["failed_seed"], 8400)
        self.assertEqual(caught.exception.audit["attempt_n"], 2)
        self.assertFalse(caught.exception.audit["replacement_seed_used"])
        for number, attempt in enumerate(caught.exception.audit["attempts"], start=1):
            self.assertEqual(attempt["attempt"], number)
            self.assertEqual(attempt["r1_pool_n"] + attempt["r2_pool_n"], 100)
            self.assertFalse(attempt["accepted"])

    def test_nine_coefficients_against_exact_orthogonal_construction(self):
        bits = ((np.arange(16)[:, None] >> np.arange(4)) & 1) * 2 - 1
        frame = pd.DataFrame({"age": 52 + 10 * bits[:, 0], "bmi": 24 + 3 * bits[:, 1],
                              "glucose": 5 + bits[:, 2], "female": (bits[:, 3] + 1) / 2})
        frame["hba1c"] = 3 + .2 * frame.bmi + .04 * frame.age + .6 * frame.female + .5 * frame.glucose
        values = target.summarize_metrics(frame)
        expected = {"model_A.intercept": 5.5, "model_A.bmi": .2, "model_A.age": .04, "model_A.female": .6,
                    "model_B.intercept": 3, "model_B.bmi": .2, "model_B.glucose": .5,
                    "model_B.age": .04, "model_B.female": .6}
        for name, value in expected.items():
            self.assertAlmostEqual(values[name], value, places=10)
        self.assertEqual(len(values), 36)
        self.assertAlmostEqual(values["bmi_hba1c.spearman"], stats.spearmanr(frame.bmi, frame.hba1c).statistic)
        self.assertAlmostEqual(values["bmi.sd_ddof1"], frame.bmi.std(ddof=1))

    def test_full_hundred_split_report_and_recomputed_summaries(self):
        report = target.build_report(self.reference, self.generated, sample_size=60, expected_communities=6, expected_reference_n=180)
        self.assertEqual(len(report["splits"]), 100)
        self.assertEqual(len(report["generated"]), 3)
        self.assertEqual(len(report["summary"]), 36)
        for split in report["splits"]:
            for field in ("R1", "R2", "real_real_signed", "real_real_abs"):
                self.assertEqual(tuple(split[field]), target.METRIC_NAMES)
            for label, differences in split["generated_vs_R2"].items():
                for metric in target.METRIC_NAMES:
                    g = report["generated"][label]["metrics"][metric]
                    self.assertAlmostEqual(differences["signed"][metric], g - split["R2"][metric])
                    self.assertAlmostEqual(differences["sym_abs"][metric],
                                           (abs(g - split["R1"][metric]) + abs(g - split["R2"][metric])) / 2)
        observed = report["summary"]["model_A.bmi"]["real_real"]["absolute"]
        oracle = np.quantile([s["real_real_abs"]["model_A.bmi"] for s in report["splits"]], [.1, .5, .9], method="linear")
        np.testing.assert_allclose([observed["q10"], observed["median"], observed["q90"]], oracle)
        self.assertEqual(observed["available_n"], 100)
        serialized = json.dumps(report, allow_nan=False)
        for forbidden in ('"person_id"', '"survey_commid"', '"q95"', '"median_abs_ratio"', '"p_value"'):
            self.assertNotIn(forbidden, serialized)

    def test_unavailable_metrics_retained_without_split_replacement(self):
        reference = self.reference.copy()
        reference["female"] = 0
        reference["glucose"] = 5
        report = target.build_report(reference, self.generated, seeds=(8400, 8401), sample_size=60,
                                     expected_communities=6, expected_reference_n=180)
        for split in report["splits"]:
            original = target.sample_disjoint_communities(self.reference, split["seed"], sample_size=60, expected_communities=6)
            self.assertEqual(split["selection"], original.audit)
            self.assertIsNone(split["R1"]["model_A.bmi"])
            self.assertEqual(split["R1_unavailable"]["model_A.bmi"], "rank_deficient_design")
            self.assertIsNone(split["R1"]["glucose_hba1c.pearson"])
            self.assertIsNotNone(split["R1"]["age.mean"])
        summary = report["summary"]["model_A.bmi"]["real_real"]["absolute"]
        self.assertEqual(summary, {"q10": None, "median": None, "q90": None,
                                   "scheduled_n": 2, "available_n": 0, "unavailable_n": 2})
        json.dumps(report, allow_nan=False)

    def test_zero_differences_are_zero_without_ratios_and_invalid_rows_fail(self):
        self.assertEqual(target._quantiles([0.0, 0.0, None]), {
            "q10": 0.0, "median": 0.0, "q90": 0.0, "scheduled_n": 3, "available_n": 2, "unavailable_n": 1})
        frame = invented_frame(20)
        frame.loc[0, "bmi"] = np.nan
        with self.assertRaisesRegex(ValueError, "Nonfinite"):
            target.summarize_metrics(frame)


if __name__ == "__main__":
    unittest.main()
