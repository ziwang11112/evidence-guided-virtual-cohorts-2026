"""Invented data only. No downloads and no import/execution of any generator."""
from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd
from scipy.stats import t
import statsmodels.api as sm

import bodyfat_evaluator as ev


def invented_full():
    """Four strata/two PSUs, 48 subjects per cell, twelve cells plus outsiders."""
    rows = []
    seqn = 1
    for h in range(4):
        for j in (1, 2):
            for sex in (1, 2):
                for age_base in (20, 40):
                    for bmi_base in (18.5, 25, 30):
                        for k in range(6):
                            age = age_base + 2*k + h
                            bmi = bmi_base + .7*k + .1*(j-1)
                            race = 3 + k % 2
                            B, A = (bmi-24)/5, (age-40)/10
                            y = 30 + 3*B + 2*A + 1.5*B*B + (sex == 2)*8 + (race == 4)*2 + .1*h + .2*j
                            rows.append([f"invented_{seqn}", seqn, 1 + .1*k, h, j, age, sex, race, bmi, 1, y])
                            seqn += 1
            # Full-frame retained rows outside adult age/race/valid-outcome domain.
            rows.append([f"invented_{seqn}", seqn, 2, h, j, 10, 1, 3, 20, np.nan, np.nan])
            seqn += 1
    return pd.DataFrame(rows, columns=ev.FULL_COLUMNS)


def invented_manifest(directory, observed):
    """Every CSV is freshly invented here; never invokes a submitted generator."""
    observed.to_csv(directory/"observed.csv", index=False)
    tables = []
    specs = ev.scheduled_roster()
    for index, identity in enumerate(specs):
        table_id = identity["table_id"]
        generated = observed.copy()
        generated["bodyfat"] = 30 + .2 * generated.age + .4 * generated.bmi - 8 * generated.male + index/10
        generated.to_csv(directory/f"{table_id}.csv", index=False)
        table = dict(identity, path=f"{table_id}.csv", status="complete", sha256=ev._hash(directory/f"{table_id}.csv"))
        if identity["kind"] == "agent":
            table.update(execution_receipt_path="invented_not_read.json", execution_status="success")
        else:
            table["reference_receipt_path"] = "invented_not_read.json"
        tables.append(table)
    protocol = dict(tables=specs, observed_columns=list(ev.OBSERVED_COLUMNS), generated_column="bodyfat",
                    seeds=list(ev.SEEDS), quantile_intervals=False)
    (directory/"protocol.json").write_text(json.dumps(protocol), encoding="utf-8")
    frozen = dict(phase="before_target_acquisition", files={"protocol.json": ev._hash(directory/"protocol.json"),
                    "evaluator/bodyfat_evaluator.py": ev._hash(Path(ev.__file__))})
    (directory/"preaccess_freeze.json").write_text(json.dumps(frozen), encoding="utf-8")
    return dict(schema_version=ev.SCHEMA_VERSION, observed_path="observed.csv", tables=tables,
                preaccess_sha256=ev._hash(directory/"preaccess_freeze.json"))


class SurveyKernelTests(unittest.TestCase):
    def setUp(self):
        self.strata = np.repeat([1, 2], 4)
        self.psu = np.tile([1, 1, 2, 2], 2)
        self.weights = np.array([1, 2, 3, 4, 2, 3, 1, 2.])
        self.y = np.array([1, 3, 2, 6, 5, 4, 7, 9.])
        self.domain = np.array([1, 1, 0, 0, 1, 1, 1, 1], dtype=bool)

    def fit(self, X=None, **overrides):
        inputs = dict(X=np.ones((8, 1)) if X is None else X, y=self.y, weights=self.weights,
                      strata=self.strata, psu=self.psu, domain=self.domain)
        inputs.update(overrides)
        return ev.fit_domain(**inputs)

    def test_hand_calculated_ratio_mean_empty_domain_psu(self):
        fit = self.fit()
        self.assertAlmostEqual(fit["beta"][0], float(Fraction(54, 11)))
        # Stratum1 score difference=-85/11; stratum2 difference=-141/11;
        # two PSUs per stratum => sum of squared differences / total_weight^2.
        self.assertAlmostEqual(fit["covariance"][0, 0], float(Fraction(27106, 14641)))
        self.assertEqual((fit["full_design_psus"], fit["domain_psus"], fit["domain_strata"], fit["df"]), (4, 3, 2, 1))
        interval = ev.contrast_interval(fit, [1])
        self.assertAlmostEqual(interval["ci_high"]-interval["estimate"], t.ppf(.975, 1)*np.sqrt(float(Fraction(27106, 14641))))

    def test_hand_calculated_wls_covariance(self):
        x = np.tile([-1., 1.], 4)
        X = np.column_stack([np.ones(8), x])
        e = np.repeat([-3., 1., -1., 3.], 2)
        fit = self.fit(X=X, y=10+2*x+e, weights=np.ones(8), domain=np.ones(8, dtype=bool))
        # beta=(10,2); PSU intercept scores=(-6,2,-2,6), slope scores=0.
        # meat_00=(-6-2)^2+(-2-6)^2=128; bread_00=1/8.
        np.testing.assert_allclose(fit["beta"], [10, 2], atol=1e-12)
        np.testing.assert_allclose(fit["covariance"], [[2, 0], [0, 0]], atol=1e-12)

    def test_weight_scale_and_row_permutation(self):
        base = self.fit()
        scale = self.fit(weights=self.weights*137)
        order = np.array([5, 1, 7, 2, 6, 3, 0, 4])
        perm = self.fit(y=self.y[order], weights=self.weights[order], strata=self.strata[order],
                        psu=self.psu[order], domain=self.domain[order])
        for fit in (scale, perm):
            np.testing.assert_allclose(base["beta"], fit["beta"])
            np.testing.assert_allclose(base["covariance"], fit["covariance"])

    def test_nested_psu_labels_equal_unique_relabeling(self):
        base = self.fit()
        renamed = self.fit(psu=self.strata*100+self.psu)
        np.testing.assert_allclose(base["covariance"], renamed["covariance"])
        self.assertEqual(base["domain_psus"], renamed["domain_psus"])

    def test_offdomain_nonfinite_x_and_y_do_not_contribute(self):
        X = np.ones((8, 1)); X[~self.domain] = np.nan
        y = self.y.copy(); y[~self.domain] = np.nan
        np.testing.assert_allclose(self.fit()["covariance"], self.fit(X=X, y=y)["covariance"])

    def test_statsmodels_wls_coefficients(self):
        X = np.column_stack([np.ones(8), np.arange(8.)])
        fit = self.fit(X=X, domain=np.ones(8, dtype=bool))
        reference = sm.WLS(self.y, X, weights=self.weights).fit()
        np.testing.assert_allclose(fit["beta"], reference.params)
        self.assertGreaterEqual(np.linalg.eigvalsh(fit["covariance"]).min(), -1e-10)

    def test_paired_difference_identity_and_covariance(self):
        X = np.column_stack([np.ones(8), np.arange(8.)])
        d = np.ones(8, dtype=bool)
        real = self.fit(X=X, domain=d)
        shift = X @ np.array([3., -0.1])
        generated = self.fit(X=X, domain=d, y=self.y+shift)
        paired = self.fit(X=X, domain=d, y=shift)
        np.testing.assert_allclose(paired["beta"], generated["beta"]-real["beta"], atol=1e-12)
        np.testing.assert_allclose(paired["covariance"], np.zeros((2, 2)), atol=1e-25)
        self.assertGreater(float((real["covariance"]+generated["covariance"])[0, 0]), 0)

    def test_singleton_and_rank_failure(self):
        with self.assertRaisesRegex(ev.ValidationError, "singleton_full_design_stratum"):
            self.fit(strata=np.array([1, 1, 2, 2, 3, 3, 3, 3]))
        with self.assertRaisesRegex(ev.ValidationError, "rank_deficient_design"):
            self.fit(X=np.ones((8, 2)))


class QuantileTests(unittest.TestCase):
    def test_hand_calculated_ties_and_probability_boundaries(self):
        # Sorted mass: 10=>1, 20=>2, 30=>1, hence quartiles 10,20,20.
        q = ev.weighted_quantile([30, 20, 10, 20], [1, 1, 1, 1], [0, .25, .5, .75, 1])
        np.testing.assert_array_equal(q, [10, 10, 20, 20, 30])
        # Unequal weights, tied mass combines at first value crossing each bound.
        np.testing.assert_array_equal(ev.weighted_quantile([10, 20, 20, 40], [1, 1, 3, 3]), [20, 20, 40])

    def test_quantile_scale_and_permutation(self):
        y, w = np.array([10., 20, 20, 40]), np.array([1., 1, 3, 3])
        order = [3, 1, 0, 2]
        np.testing.assert_array_equal(ev.weighted_quantile(y, w), ev.weighted_quantile(y[order], 11*w[order]))

    def test_quantile_invalid_values(self):
        for y, w, p in (([1], [0], [.5]), ([np.nan], [1], [.5]), ([1], [1], [1.1])):
            with self.assertRaises(ev.ValidationError):
                ev.weighted_quantile(y, w, p)


class PanelAndValidationTests(unittest.TestCase):
    def setUp(self):
        self.full = ev.validate_full_frame(invented_full())
        self.observed = ev.validate_observed(ev.expected_observed(self.full), self.full)
        self.generated = self.observed.copy()
        self.generated["bodyfat"] = self.full.loc[ev.domains(self.full)["eligible"], "DXDTOPF"].to_numpy()+2

    def test_fixed_schedule_and_quadratic_multiplier(self):
        panel = ev.estimate_panel(self.full, self.full.DXDTOPF)
        self.assertEqual(len(panel), 62)
        self.assertEqual(sum(x["kind"] == "linear" for x in panel), 14)
        self.assertEqual(sum(x["kind"] == "distribution" for x in panel), 48)
        self.assertTrue(all(x["status"] == "estimable" for x in panel))
        for row in panel:
            if "curvature" in row["endpoint"]:
                # Exact quadratic truth plus h/j offset; offset has slight association.
                schedule = next(x for x in ev.panel_schedule(self.full) if x["endpoint"] == row["endpoint"])
                X, d = schedule["X"], schedule["domain"]
                pure = X @ np.array([30., 3., 2., 2., 1.5])
                fit = ev.fit_domain(X, pure, self.full.WTMEC2YR, self.full.SDMVSTRA, self.full.SDMVPSU, d)
                self.assertAlmostEqual(ev.contrast_interval(fit, schedule["contrast"])["estimate"], 1.92)
                m = lambda bmi: 30+3*(bmi-24)/5+1.5*((bmi-24)/5)**2
                self.assertAlmostEqual(m(28)-2*m(24)+m(20), 1.92)
            if row["kind"] == "distribution":
                self.assertFalse(row["interval_available"])
                self.assertIsNone(row["se"])
                self.assertIsNone(row["ci_low"])

    def test_entire_panel_paired_constant_shift(self):
        measured = ev.estimate_panel(self.full, self.full.DXDTOPF)
        panel = ev.evaluate_table(self.full, self.observed, self.generated, measured)
        for row in panel:
            expected = 0 if any(x in row["endpoint"] for x in ("bmi_per5", "age_per10", "curvature", ".iqr")) else 2
            self.assertAlmostEqual(row["signed_error"], expected, places=8)
            if row["paired_difference"] is not None:
                self.assertLess(row["paired_difference"]["se"], 1e-10)

    def test_full_panel_invariant_to_row_order(self):
        measured = ev.estimate_panel(self.full, self.full.DXDTOPF)
        reversed_full = self.full.iloc[::-1].reset_index(drop=True)
        reordered = ev.validate_observed(self.observed.iloc[::-1], reversed_full)
        newmeasured = ev.estimate_panel(reversed_full, reversed_full.DXDTOPF)
        a = ev.evaluate_table(self.full, self.observed, self.generated, measured)
        b = ev.evaluate_table(reversed_full, reordered, self.generated.iloc[::-1], newmeasured)
        np.testing.assert_allclose([x["estimate"] for x in a], [x["estimate"] for x in b], atol=1e-10)
        np.testing.assert_allclose([x["signed_error"] for x in a], [x["signed_error"] for x in b], atol=1e-10)

    def test_exact_domain_boundaries_scan_and_missingness(self):
        f = self.full.copy()
        # Independent rows: lower/upper support, primary/extension split, age, race, scan.
        edits = {0: dict(BMXBMI=18.5), 1: dict(BMXBMI=29.999), 2: dict(BMXBMI=30),
                 3: dict(BMXBMI=35), 4: dict(BMXBMI=35.001), 5: dict(BMXBMI=18.499),
                 6: dict(RIDAGEYR=19), 7: dict(RIDAGEYR=60), 8: dict(RIDRETH3=6),
                 9: dict(DXAEXSTS=2), 10: dict(DXDTOPF=np.nan), 11: dict(BMXBMI=np.nan)}
        for i, values in edits.items():
            for column, value in values.items(): f.loc[i, column] = value
        d = ev.domains(ev.validate_full_frame(f))
        self.assertEqual(d["primary"][:4].tolist(), [True, True, False, False])
        self.assertEqual(d["extension"][:4].tolist(), [False, False, True, True])
        self.assertFalse(d["eligible"][4:12].any())

    def test_sparse_gates_and_missing_race_rank(self):
        d = np.zeros(len(self.full), dtype=bool); d[:5] = True
        g = ev.gate(self.full, d)
        self.assertEqual(set(g["failures"]), {"n_below_30", "kish_below_20", "domain_psus_below_8", "domain_df_below_4"})
        f = self.full.copy(); f["RIDRETH3"] = 3
        panel = ev.estimate_panel(f, f.DXDTOPF)
        row = next(x for x in panel if x["endpoint"] == "primary.male.bmi_per5")
        self.assertEqual(row["status"], "not_estimable")
        self.assertIn("rank_deficient_design", row["gate"]["failures"])
        self.assertEqual(next(x for x in panel if x["endpoint"] == "primary.male.mean")["status"], "estimable")

    def test_whitelist_identity_and_preservation_failures(self):
        for extra in ("DXDTOPF", "DXDTOFAT", "SEQN", "WTMEC2YR", "race_group"):
            f = self.observed.copy(); f[extra] = 1
            with self.assertRaisesRegex(ev.ValidationError, "column_whitelist"):
                ev.validate_observed(f, self.full)
        duplicate = self.generated.copy(); duplicate.loc[1, "id"] = duplicate.loc[0, "id"]
        with self.assertRaisesRegex(ev.ValidationError, "duplicate_id"):
            ev.validate_generated(duplicate, self.observed)
        missing = self.generated.iloc[1:]
        with self.assertRaisesRegex(ev.ValidationError, "id_set_mismatch"):
            ev.validate_generated(missing, self.observed)
        changed = self.generated.copy(); changed.loc[0, "age"] += 1
        with self.assertRaisesRegex(ev.ValidationError, "generated_covariate_mismatch"):
            ev.validate_generated(changed, self.observed)
        for col in ("inv_bmi", "male_inv_bmi", "asian", "asian_inv_bmi", "male_age", "asian_age"):
            wrong = self.observed.copy(); wrong.loc[0, col] += .1
            with self.assertRaisesRegex(ev.ValidationError, "observed_covariate_mismatch"):
                ev.validate_observed(wrong, self.full)
        for value in (np.nan, np.inf, -0.1, 100.1):
            invalid = self.generated.copy(); invalid.loc[0, "bodyfat"] = value
            with self.assertRaisesRegex(ev.ValidationError, "invalid_generated_bodyfat"):
                ev.validate_generated(invalid, self.observed)

    def test_physical_support_and_design_failures(self):
        for col, value, reason in (("DXDTOPF", 100.01, "bodyfat_outside"),
                                   ("WTMEC2YR", 0, "nonpositive_or_nonfinite"),
                                   ("SDMVSTRA", np.nan, "invalid_design_identifier")):
            f = self.full.copy(); f.loc[0, col] = value
            with self.assertRaisesRegex(ev.ValidationError, reason): ev.validate_full_frame(f)

    def test_aggregate_end_to_end_and_failed_roster_retained(self):
        with tempfile.TemporaryDirectory(prefix="m13b_invented_", dir=Path(__file__).parent) as directory:
            p = Path(directory)
            self.full.to_csv(p/"full.csv", index=False)
            manifest = invented_manifest(p, self.observed)
            manifest["tables"][0].update(status="failed", path=None, execution_status="failed")
            del manifest["tables"][0]["sha256"]
            # A complete manifest entry with bad covariate content fails locally,
            # without suppressing the 62 scheduled outputs or any other table.
            wrongpath = p/manifest["tables"][1]["path"]
            wrong = pd.read_csv(wrongpath); wrong.loc[0, "age"] += 2; wrong.to_csv(wrongpath, index=False)
            manifest["tables"][1]["sha256"] = ev._hash(wrongpath)
            (p/"manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            result = ev.run_evaluation(p/"full.csv", p/"manifest.json")
            self.assertEqual((len(result["measured"]), len(result["tables"])), (62, 16))
            self.assertEqual(sum(x["status"] == "failed" for x in result["tables"]), 2)
            self.assertTrue(all(len(x["panel"]) == 62 for x in result["tables"]))
            summary = next(x for x in result["seed_summaries"] if x["builder"] == "build01" and x["candidate"] == "initial")
            self.assertEqual(summary["panel"][0]["status"], "not_complete")
            self.assertIsNone(summary["panel"][0]["summaries"]["estimate"])
            ev.write_aggregate(result, p/"aggregate")
            aggregate = json.loads((p/"aggregate/aggregate.json").read_text(encoding="utf-8"))
            self.assertNotIn("id", aggregate)
            self.assertNotIn("invented_1", (p/"aggregate/aggregate.json").read_text(encoding="utf-8"))
            flat = pd.read_csv(p/"aggregate/aggregate.csv")
            self.assertEqual(len(flat), 17*62)
            self.assertNotIn("DXDTOPF", flat.columns)
            with self.assertRaisesRegex(ev.ValidationError, "aggregate_output_already_exists"):
                ev.write_aggregate(result, p/"aggregate")

    def test_manifest_roster_and_extra_columns_rejected(self):
        with tempfile.TemporaryDirectory(prefix="m13b_invented_", dir=Path(__file__).parent) as directory:
            manifest = invented_manifest(Path(directory), self.observed)
            ev.validate_manifest(manifest)
            manifest["tables"][0]["seed"] = 1
            with self.assertRaisesRegex(ev.ValidationError, "invalid_agent_seed"):
                ev.validate_manifest(manifest)
            p = Path(directory)/"duplicate_columns.csv"
            p.write_text("id,id\nopaque,opaque\n", encoding="utf-8")
            with self.assertRaisesRegex(ev.ValidationError, "column_whitelist"):
                ev.read_csv_strict(p, ev.OBSERVED_COLUMNS)

    def test_preaccess_and_generated_digest_enforcement(self):
        with tempfile.TemporaryDirectory(prefix="m13b_invented_", dir=Path(__file__).parent) as directory:
            p = Path(directory)
            self.full.to_csv(p/"full.csv", index=False)
            manifest = invented_manifest(p, self.observed)
            (p/"manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            changed = p/manifest["tables"][0]["path"]
            changed.write_text(changed.read_text()+"\n", encoding="utf-8")
            result = ev.run_evaluation(p/"full.csv", p/"manifest.json")
            self.assertEqual(result["tables"][0]["failure"], "generated_file_digest_mismatch")
            (p/"protocol.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ev.ValidationError, "frozen_protocol_digest_mismatch"):
                ev.run_evaluation(p/"full.csv", p/"manifest.json")

    def test_cli_invented_full_run_and_no_raw_values_logged(self):
        with tempfile.TemporaryDirectory(prefix="m13b_invented_", dir=Path(__file__).parent) as directory:
            p = Path(directory)
            self.full.to_csv(p/"full.csv", index=False)
            manifest = invented_manifest(p, self.observed)
            (p/"manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            run = subprocess.run([sys.executable, str(Path(ev.__file__)), "--full-frame", str(p/"full.csv"),
                                  "--manifest", str(p/"manifest.json"), "--output-dir", str(p/"output")],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout), dict(status="complete", table_count=16, panel_count=62, failed_tables=0))
            self.assertEqual(run.stderr, "")
            self.assertTrue((p/"output/aggregate.json").exists())
            self.assertTrue((p/"output/aggregate.csv").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
