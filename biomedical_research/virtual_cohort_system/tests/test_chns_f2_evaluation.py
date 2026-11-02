"""Invented-only checks for the prospective F2 evaluator.

Every numeric row in this file is fabricated locally.  The only external
fixture is analysis-plan metadata; no released participant file is opened.
"""

from __future__ import annotations

import copy
import builtins
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest
from scipy.stats import t as student_t
import statsmodels.api as sm


PROJECT = Path(__file__).resolve().parents[1]
F2 = PROJECT / "reports" / "chns_admission_2026-11-01" / "f2"
MODULE_PATH = F2 / "evaluation" / "chns_f2_evaluation.py"


@pytest.fixture(scope="module")
def evaluator():
    spec = importlib.util.spec_from_file_location("invented_f2_evaluator", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def plan():
    return json.loads((F2 / "analysis_plan.json").read_text(encoding="utf-8"))


@pytest.fixture
def invented_only_cohort():
    """120 invented rows, 24 invented communities, and no rank degeneracy."""
    rng = np.random.default_rng(8675309)
    n = 120
    age = rng.integers(35, 75, size=n).astype(float)
    female = rng.integers(0, 2, size=n).astype(float)
    bmi = rng.uniform(18, 36, size=n)
    glucose = rng.uniform(3, 12, size=n)
    group_index = np.arange(n) % 24
    invented_group_noise = rng.normal(0, 0.3, size=24)[group_index]
    hba1c = (
        2.0 + 0.017 * age + 0.12 * female + 0.031 * bmi
        + 0.49 * glucose + invented_group_noise + rng.normal(0, 0.16, size=n)
    )
    return pd.DataFrame({
        "age": age,
        "female": female,
        "bmi": bmi,
        "glucose": glucose,
        "hba1c": hba1c,
        "survey_commid": 7001 + group_index,
    })


@pytest.fixture
def invented_only_sources(invented_only_cohort):
    """Fabricated source-shaped frames; IDs cannot identify real people."""
    cohort = invented_only_cohort
    n = len(cohort)
    fake_id = np.arange(900001, 900001 + n)
    invented_height = np.linspace(150.0, 185.0, n)
    return {
        "biomarker_09.sas7bdat": pd.DataFrame({
            "IDind": fake_id, "wave": 2009,
            "GLUCOSE": cohort["glucose"], "HbA1c": cohort["hba1c"],
        }),
        "pexam_00.sas7bdat": pd.DataFrame({
            "IDind": fake_id, "WAVE": 2009,
            "HEIGHT": invented_height,
            "WEIGHT": cohort["bmi"] * (invented_height / 100) ** 2,
            "CLN_HT": 0, "CLN_WT": 0,
        }),
        "mast_pub_12.sas7bdat": pd.DataFrame({
            "Idind": fake_id, "GENDER": cohort["female"] + 1,
        }),
        "surveys_pub_12.sas7bdat": pd.DataFrame({
            "Idind": fake_id, "wave": 2009,
            "age": cohort["age"], "commid": cohort["survey_commid"],
        }),
    }


def independent_ols(frame, estimand):
    """Construct the design independently from the prospective metadata."""
    predictors = estimand["predictors"]
    design = np.column_stack([np.ones(len(frame)), frame[predictors].to_numpy()])
    outcome = frame[estimand["outcome"]].to_numpy()
    coefficients = np.linalg.solve(design.T @ design, design.T @ outcome)
    term_index = 1 + predictors.index(estimand["term"])
    return design, outcome, coefficients, term_index


def test_linkage_is_by_exact_id_and_wave_not_row_order(
    evaluator, plan, invented_only_sources, invented_only_cohort
):
    sources = copy.deepcopy(invented_only_sources)
    # These three invented IDs each fail a different required inner join.
    sources["pexam_00.sas7bdat"] = sources["pexam_00.sas7bdat"].iloc[1:].copy()
    sources["surveys_pub_12.sas7bdat"].loc[1, "wave"] = 2006
    sources["mast_pub_12.sas7bdat"] = sources["mast_pub_12.sas7bdat"].drop(index=2)
    # Same IDs in another wave must never leak into the 2009 join.
    for filename, wave_column in (
        ("biomarker_09.sas7bdat", "wave"),
        ("pexam_00.sas7bdat", "WAVE"),
        ("surveys_pub_12.sas7bdat", "wave"),
    ):
        wrong_wave = sources[filename].copy()
        wrong_wave[wave_column] = 2004
        sources[filename] = pd.concat([sources[filename], wrong_wave], ignore_index=True)
    for offset, filename in enumerate(sources):
        sources[filename] = sources[filename].sample(frac=1, random_state=offset + 31)
    actual, quality = evaluator.prepare_reference_frames(sources, plan)
    columns = ["age", "female", "bmi", "glucose", "hba1c", "survey_commid"]
    expected = invented_only_cohort.iloc[3:][columns].sort_values("glucose").reset_index(drop=True)
    actual = actual[columns].sort_values("glucose").reset_index(drop=True)
    np.testing.assert_allclose(actual.to_numpy(), expected.to_numpy(), rtol=1e-12, atol=1e-12)
    assert quality["common_complete_case"] == 117


@pytest.mark.parametrize("filename,key", [
    ("biomarker_09.sas7bdat", "IDind"),
    ("pexam_00.sas7bdat", "IDind"),
    ("mast_pub_12.sas7bdat", "Idind"),
    ("surveys_pub_12.sas7bdat", "Idind"),
])
def test_duplicate_keys_stop_without_deduplication(evaluator, plan, invented_only_sources, filename, key):
    source = invented_only_sources[filename]
    invented_only_sources[filename] = pd.concat([source, source.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError):
        evaluator.prepare_reference_frames(invented_only_sources, plan)


@pytest.mark.parametrize("bad_id", [np.nan, np.inf, 900001.25, 2**53, -(2**53)])
def test_invalid_ids_stop_without_coercion_or_row_deletion(evaluator, plan, invented_only_sources, bad_id):
    source = invented_only_sources["biomarker_09.sas7bdat"]
    source["IDind"] = source["IDind"].astype(float)
    source.loc[0, "IDind"] = bad_id
    with pytest.raises(ValueError):
        evaluator.prepare_reference_frames(invented_only_sources, plan)


def test_duplicate_keys_in_another_wave_still_stop(evaluator, plan, invented_only_sources):
    source = invented_only_sources["pexam_00.sas7bdat"]
    wrong_wave = source.iloc[[0]].copy()
    wrong_wave["WAVE"] = 2004
    invented_only_sources["pexam_00.sas7bdat"] = pd.concat([source, wrong_wave, wrong_wave], ignore_index=True)
    with pytest.raises(ValueError):
        evaluator.prepare_reference_frames(invented_only_sources, plan)


@pytest.mark.parametrize("bad_wave", [np.nan, np.inf, 2009.5])
def test_invalid_wave_stops_without_silent_filtering(evaluator, plan, invented_only_sources, bad_wave):
    source = invented_only_sources["biomarker_09.sas7bdat"]
    source["wave"] = source["wave"].astype(float)
    source.loc[0, "wave"] = bad_wave
    with pytest.raises(ValueError):
        evaluator.prepare_reference_frames(invented_only_sources, plan)


@pytest.mark.parametrize("flag_column,measurement", [("CLN_HT", "HEIGHT"), ("CLN_WT", "WEIGHT")])
@pytest.mark.parametrize("flag,masked", [(9, True), (9.0, True), (8, False), (9.1, False), (-9, False), (np.nan, False)])
def test_only_exact_flag9_masks_corresponding_measurement(
    evaluator, plan, invented_only_sources, flag_column, measurement, flag, masked
):
    source = invented_only_sources["pexam_00.sas7bdat"]
    source[flag_column] = source[flag_column].astype(float)
    source.loc[0, flag_column] = flag
    signature = invented_only_sources["biomarker_09.sas7bdat"].loc[0, "GLUCOSE"]
    actual, quality = evaluator.prepare_reference_frames(invented_only_sources, plan)
    assert (signature not in actual["glucose"].to_numpy()) is masked
    assert len(actual) == 120 - int(masked)
    assert quality["flag9_masked"]["height" if measurement == "HEIGHT" else "weight"] == int(masked)
    assert quality["flag9_masked"]["weight" if measurement == "HEIGHT" else "height"] == 0


def test_gender_mapping_common_complete_case_and_no_generic_sentinels(evaluator, plan, invented_only_sources):
    bio = invented_only_sources["biomarker_09.sas7bdat"]
    exam = invented_only_sources["pexam_00.sas7bdat"]
    master = invented_only_sources["mast_pub_12.sas7bdat"]
    survey = invented_only_sources["surveys_pub_12.sas7bdat"]
    exam.loc[0, "CLN_HT"] = 9
    exam.loc[1, "CLN_WT"] = 9
    bio.loc[2, "GLUCOSE"] = np.nan
    bio.loc[3, "HbA1c"] = np.nan
    exam.loc[4, "HEIGHT"] = 0
    exam.loc[5, "WEIGHT"] = 0
    master.loc[6, "GENDER"] = 3
    survey.loc[7, "age"] = 34
    survey.loc[8, "age"] = 75
    survey.loc[9, "age"] = np.nan
    bio.loc[10, "GLUCOSE"] = np.nan
    survey.loc[11, "age"] = 35
    survey.loc[12, "age"] = 74
    master.loc[11, "GENDER"] = 1
    master.loc[12, "GENDER"] = 2
    bio.loc[16, "GLUCOSE"] = 999  # Artificial positive sentinel: no undocumented recoding.
    actual, quality = evaluator.prepare_reference_frames(invented_only_sources, plan)
    assert len(actual) == quality["common_complete_case"] == 109
    by_glucose = actual.set_index("glucose")
    assert by_glucose.loc[bio.loc[11, "GLUCOSE"], "female"] == 0
    assert by_glucose.loc[bio.loc[12, "GLUCOSE"], "female"] == 1
    assert by_glucose.loc[bio.loc[11, "GLUCOSE"], "age"] == 35
    assert by_glucose.loc[bio.loc[12, "GLUCOSE"], "age"] == 74
    assert 999 in by_glucose.index
    assert quality["native_missing"]["biomarker_09.sas7bdat"]["GLUCOSE"] == 2
    assert quality["native_missing"]["biomarker_09.sas7bdat"]["HbA1c"] == 1
    assert quality["cleaning_flag_counts"]["linked"]["CLN_HT"]["9.0"] == 1
    assert quality["cleaning_flag_counts"]["analysis"]["CLN_HT"].get("9.0", 0) == 0


@pytest.mark.parametrize("column", ["glucose", "hba1c"])
@pytest.mark.parametrize("value", [0, -0.5])
@pytest.mark.parametrize("reference", [False, True])
def test_nonpositive_glycemia_withholds_before_any_statistics(
    evaluator, plan, invented_only_cohort, monkeypatch, column, value, reference
):
    frame = invented_only_cohort.copy()
    frame.loc[0, column] = value
    original = frame.copy(deep=True)
    calls = []

    def forbidden_statistic(*args, **kwargs):
        calls.append("statistic")
        raise AssertionError("A statistic was attempted before the interpretation gate")

    monkeypatch.setattr(evaluator, "_diagnostics", forbidden_statistic)
    monkeypatch.setattr(evaluator, "_fit", forbidden_statistic)
    actual = evaluator.analyze(frame, plan, reference=reference)
    assert calls == []
    assert actual["status"] == "withheld"
    assert actual["n"] == 120
    assert actual["diagnostics"] is None
    assert actual["gate_reason"]
    for estimate in actual["estimands"].values():
        assert estimate["status"] == "unavailable"
        assert estimate["coefficient"] is None
        assert estimate["interval"]["status"] == "unavailable"
    pd.testing.assert_frame_equal(frame, original)


@pytest.mark.parametrize("column", ["GLUCOSE", "HbA1c"])
@pytest.mark.parametrize("value", [0, -0.5])
def test_reference_preparation_retains_nonpositive_glycemia_for_gate(
    evaluator, plan, invented_only_sources, column, value
):
    invented_only_sources["biomarker_09.sas7bdat"].loc[0, column] = value
    frame, quality = evaluator.prepare_reference_frames(invented_only_sources, plan)
    assert quality["common_complete_case"] == len(frame) == 120
    actual = evaluator.analyze(frame, plan, reference=True, quality=quality)
    assert actual["status"] == "withheld"
    assert actual["n"] == 120
    assert actual["diagnostics"] is None


@pytest.mark.parametrize("column", ["GLUCOSE", "HbA1c"])
@pytest.mark.parametrize("value", [np.inf, -np.inf])
def test_reference_preparation_requires_finite_glycemia_and_reports_nonfinite_separately(
    evaluator, plan, invented_only_sources, column, value
):
    bio = invented_only_sources["biomarker_09.sas7bdat"]
    bio.loc[0, column] = value
    bio.loc[1, column] = np.nan
    original = bio.copy(deep=True)
    frame, quality = evaluator.prepare_reference_frames(invented_only_sources, plan)
    assert len(frame) == quality["common_complete_case"] == 118
    assert quality["age_gender_eligible"] == 120
    assert quality["native_missing"]["biomarker_09.sas7bdat"][column] == 1
    assert quality["nonfinite_glycemia"] == {
        "scope": "linked_2009_before_age_gender_eligibility",
        "glucose": int(column == "GLUCOSE"), "hba1c": int(column == "HbA1c"),
    }
    assert np.isfinite(frame[["glucose", "hba1c"]].to_numpy()).all()
    actual = evaluator.analyze(frame, plan, reference=True, quality=quality)
    assert actual["status"] == "complete"
    assert actual["n"] == 118
    assert all(item["status"] == "computed" for item in actual["estimands"].values())
    pd.testing.assert_frame_equal(bio, original)


def test_runtime_versions_binds_installed_decoder_metadata(evaluator, monkeypatch):
    from importlib.metadata import version
    assert evaluator.runtime_versions()["pyreadstat"] == version("pyreadstat")
    calls = []

    def changed_version(package):
        calls.append(package)
        return "invented-decoder-version"

    monkeypatch.setattr(evaluator.importlib.metadata, "version", changed_version)
    assert evaluator.runtime_versions()["pyreadstat"] == "invented-decoder-version"
    assert calls == ["pyreadstat"]


@pytest.mark.parametrize("column,value", [("glucose", np.nan), ("hba1c", np.inf),
    ("glucose", np.inf), ("glucose", -np.inf), ("hba1c", -np.inf),
    ("age", 74.5), ("female", 2), ("bmi", 0)])
def test_invalid_analysis_values_withhold_instead_of_changing_population(
    evaluator, plan, invented_only_cohort, monkeypatch, column, value
):
    frame = invented_only_cohort.copy()
    frame.loc[0, column] = value

    def forbidden_statistic(*args, **kwargs):
        raise AssertionError("Invalid analysis values reached a statistic")

    monkeypatch.setattr(evaluator, "_diagnostics", forbidden_statistic)
    monkeypatch.setattr(evaluator, "_fit", forbidden_statistic)
    actual = evaluator.analyze(frame, plan)
    assert actual["status"] == "withheld"
    assert actual["n"] == 120
    assert actual["diagnostics"] is None
    assert all(estimate["coefficient"] is None for estimate in actual["estimands"].values())


@pytest.mark.parametrize("estimand_id", ["E1", "E2", "E3"])
def test_exact_ols_and_cluster_cr1_t_against_independent_oracles(
    evaluator, plan, invented_only_cohort, estimand_id
):
    frame = invented_only_cohort
    estimand = next(item for item in plan["estimands"] if item["id"] == estimand_id)
    design, outcome, coefficients, term = independent_ols(frame, estimand)
    actual = evaluator.analyze(frame, plan, reference=True)["estimands"][estimand_id]
    n, k = design.shape
    groups = frame["survey_commid"].to_numpy()
    unique_groups = np.unique(groups)
    residuals = outcome - design @ coefficients
    scores = np.array([design[groups == group].T @ residuals[groups == group] for group in unique_groups])
    bread = np.linalg.inv(design.T @ design)
    correction = len(unique_groups) / (len(unique_groups) - 1) * (n - 1) / (n - k)
    covariance = correction * bread @ scores.T @ scores @ bread
    expected_se = np.sqrt(covariance[term, term])
    statsmodels_fit = sm.OLS(outcome, design).fit(
        cov_type="cluster", cov_kwds={"groups": groups, "use_correction": True, "df_correction": True}, use_t=True,
    )
    interval = actual["interval"]
    assert actual["status"] == "computed"
    assert actual["n"] == n == 120
    assert actual["rank"] == k
    assert actual["unit"] == estimand["unit"]
    assert actual["coefficient"] == pytest.approx(coefficients[term], rel=1e-9, abs=1e-11)
    assert interval["status"] == "available"
    assert interval["groups"] == 24
    assert interval["degrees_of_freedom"] == 23
    assert interval["standard_error"] == pytest.approx(expected_se, rel=1e-9)
    assert interval["standard_error"] == pytest.approx(statsmodels_fit.bse[term], rel=1e-9)
    radius = student_t.ppf(0.975, 23) * expected_se
    assert interval["lower"] == pytest.approx(coefficients[term] - radius, rel=1e-9, abs=1e-11)
    assert interval["upper"] == pytest.approx(coefficients[term] + radius, rel=1e-9, abs=1e-11)
    np.testing.assert_allclose([interval["lower"], interval["upper"]], statsmodels_fit.conf_int()[term], rtol=1e-9, atol=1e-11)


@pytest.mark.parametrize("invalid_group", [np.nan, np.inf, 0, -1, 7001.5, "invented-invalid-group"])
def test_one_invalid_community_disables_ci_without_changing_any_point_or_row(
    evaluator, plan, invented_only_cohort, invalid_group
):
    baseline = evaluator.analyze(invented_only_cohort, plan, reference=True)
    changed = invented_only_cohort.copy()
    changed["survey_commid"] = changed["survey_commid"].astype(object if isinstance(invalid_group, str) else float)
    changed.loc[0, "survey_commid"] = invalid_group
    actual = evaluator.analyze(changed, plan, reference=True)
    assert actual["n"] == baseline["n"] == 120
    assert actual["diagnostics"] == baseline["diagnostics"]
    for estimand_id in ("E1", "E2", "E3"):
        estimate = actual["estimands"][estimand_id]
        assert estimate["coefficient"] == baseline["estimands"][estimand_id]["coefficient"]
        assert estimate["n"] == 120
        assert estimate["interval"]["status"] == "unavailable"
        assert estimate["interval"]["lower"] is None
        assert estimate["interval"]["upper"] is None


@pytest.mark.parametrize("number_of_groups,available", [(19, False), (20, True)])
def test_exact_minimum_20_community_boundary(evaluator, plan, invented_only_cohort, number_of_groups, available):
    frame = invented_only_cohort.copy()
    frame["survey_commid"] = 8001 + np.arange(len(frame)) % number_of_groups
    actual = evaluator.analyze(frame, plan, reference=True)
    for estimate in actual["estimands"].values():
        assert estimate["status"] == "computed"
        assert estimate["n"] == 120
        assert (estimate["interval"]["status"] == "available") is available
        if available:
            assert estimate["interval"]["degrees_of_freedom"] == 19


def test_generated_coefficients_never_receive_sampling_intervals(evaluator, plan, invented_only_cohort):
    actual = evaluator.analyze(invented_only_cohort.drop(columns="survey_commid"), plan)
    for estimand in plan["estimands"]:
        _, _, coefficients, term = independent_ols(invented_only_cohort, estimand)
        estimate = actual["estimands"][estimand["id"]]
        assert estimate["status"] == "computed"
        assert estimate["coefficient"] == pytest.approx(coefficients[term], rel=1e-9, abs=1e-11)
        assert estimate["interval"]["status"] == "unavailable"
        assert estimate["interval"]["lower"] is None
        assert estimate["interval"]["upper"] is None
        assert estimate["interval"]["standard_error"] is None


@pytest.mark.parametrize("n,computed", [(99, False), (100, True)])
def test_minimum_n_100_boundary_preserves_denominator(evaluator, plan, invented_only_cohort, n, computed):
    actual = evaluator.analyze(invented_only_cohort.iloc[:n], plan)
    assert actual["n"] == n
    assert actual["diagnostics"] is not None
    for estimate in actual["estimands"].values():
        assert (estimate["status"] == "computed") is computed
        assert estimate["n"] == n
        if not computed:
            assert estimate["coefficient"] is None


def test_rank_deficiency_withholds_coefficients_without_dropping_predictors(evaluator, plan, invented_only_cohort):
    frame = invented_only_cohort.copy()
    frame["age"] = 50.0
    actual = evaluator.analyze(frame, plan, reference=True)
    assert actual["n"] == 120
    for estimand in plan["estimands"]:
        estimate = actual["estimands"][estimand["id"]]
        assert estimate["status"] == "unavailable"
        assert estimate["coefficient"] is None
        assert estimate["rank"] < len(estimand["predictors"]) + 1
        assert estimate["interval"]["status"] == "unavailable"


def test_diagnostics_match_prespecified_statistics(evaluator, plan, invented_only_cohort):
    frame = invented_only_cohort.copy()
    frame.loc[:5, "glucose"] = frame.loc[0, "glucose"]  # Deliberate invented ties.
    actual = evaluator.analyze(frame, plan)["diagnostics"]
    for variable in plan["diagnostics"]["marginal_variables"]:
        values = frame[variable].to_numpy()
        marginal = actual["marginal"][variable]
        assert marginal["mean"] == pytest.approx(np.mean(values))
        assert marginal["sd"] == pytest.approx(np.std(values, ddof=1))
        assert marginal["q10"] == pytest.approx(np.quantile(values, 0.1, method="linear"))
        assert marginal["median"] == pytest.approx(np.quantile(values, 0.5, method="linear"))
        assert marginal["q90"] == pytest.approx(np.quantile(values, 0.9, method="linear"))
    expected_pearson = np.corrcoef(frame["glucose"], frame["hba1c"])[0, 1]
    expected_spearman = np.corrcoef(frame["glucose"].rank(method="average"), frame["hba1c"].rank(method="average"))[0, 1]
    assert actual["joint"]["pearson"] == pytest.approx(expected_pearson)
    assert actual["joint"]["spearman"] == pytest.approx(expected_spearman)


@pytest.mark.parametrize("reference_coefficient,lower,upper,direction,ratio", [
    (2.0, 1.0, 3.0, "positive", 2.0),
    (-2.0, -3.0, -1.0, "negative", -2.0),
    (2.0, -1.0, 3.0, "inconclusive", None),
    (2.0, 0.0, 3.0, "inconclusive", None),
    (-2.0, -3.0, 0.0, "inconclusive", None),
    (0.0, -1.0, 1.0, "inconclusive", None),
    (2.0, None, None, "inconclusive", None),
])
def test_effect_ratio_only_when_reference_interval_excludes_zero(
    evaluator, plan, invented_only_cohort, reference_coefficient, lower, upper, direction, ratio
):
    reference = evaluator.analyze(invented_only_cohort, plan, reference=True)
    generated = evaluator.analyze(invented_only_cohort, plan)
    estimate = reference["estimands"]["E2"]
    estimate["coefficient"] = reference_coefficient
    estimate["interval"].update({"status": "available" if lower is not None else "unavailable", "lower": lower, "upper": upper})
    generated["estimands"]["E2"]["coefficient"] = 4.0
    actual = evaluator.compare_estimates(reference, generated)["E2"]
    assert actual["difference"] == 4.0 - reference_coefficient
    assert actual["reference_direction"] == direction
    assert actual["ratio"] == ratio


def test_unavailable_generated_effect_has_no_fabricated_comparison(evaluator, plan, invented_only_cohort):
    reference = evaluator.analyze(invented_only_cohort, plan, reference=True)
    invalid_generated = invented_only_cohort.copy()
    invalid_generated.loc[0, "glucose"] = 0
    generated = evaluator.analyze(invalid_generated, plan)
    actual = evaluator.compare_estimates(reference, generated)
    assert set(actual) == {"E1", "E2", "E3"}
    for comparison in actual.values():
        assert comparison["difference"] is None
        assert comparison["ratio"] is None
        assert comparison["interval_membership"] is None


def test_all_12_slots_preserved_and_direct_rows_have_no_monte_carlo_credit(
    evaluator, plan, invented_only_cohort
):
    reference = evaluator.analyze(invented_only_cohort, plan, reference=True)
    generated = evaluator.analyze(invented_only_cohort, plan)
    # Explicit invented coefficients make direction expectations independent of noise.
    for estimate in generated["estimands"].values():
        estimate["coefficient"] = 1.25
    slots = []
    for construction in plan["execution"]["constructions"]:
        for stage in plan["execution"]["stages"]:
            for seed in plan["execution"]["seeds"]:
                failed = construction == "C1" and stage == "revised" and seed == 1702
                not_run = construction == "C1" and stage == "revised" and seed == 1703
                direct = construction == "C2" and stage == "initial"
                status = "failed" if failed else "not_run" if not_run else "success"
                slots.append({
                    "construction": construction, "stage": stage, "seed": seed,
                    "status": status,
                    "route": "generated.csv" if direct else "generator.py" if status == "success" else None,
                    "reason": "invented failure" if failed else "invented not run" if not_run else None,
                    "analysis": copy.deepcopy(generated) if status == "success" else None,
                })
    original = copy.deepcopy(slots)
    actual = evaluator.summarize_slots(reference, slots)
    assert len(actual["slots"]) == plan["execution"]["max_tables"] == 12
    assert actual["global_score"] is None
    identity = lambda slot: (slot["construction"], slot["stage"], slot["seed"])
    assert {identity(slot) for slot in actual["slots"]} == {identity(slot) for slot in slots}
    assert slots == original
    for result, source in zip(actual["slots"], slots):
        for key in ("construction", "stage", "seed", "status", "route", "reason"):
            assert result[key] == source[key]
    for estimand_id in ("E1", "E2", "E3"):
        programmed = actual["stages"]["C1_initial"][estimand_id]
        assert programmed["valid_seed_count"] == 3
        assert programmed["direction_status"] == "stable_positive"
        assert programmed["monte_carlo_credit"] is True
        incomplete = actual["stages"]["C1_revised"][estimand_id]
        assert incomplete["valid_seed_count"] == 1
        assert incomplete["direction_status"] == "incomplete"
        assert incomplete["monte_carlo_credit"] is False
        direct = actual["stages"]["C2_initial"][estimand_id]
        assert direct["valid_seed_count"] == 3
        assert direct["direction_status"] == "not_assessed_direct_reuse"
        assert direct["monte_carlo_credit"] is False


@pytest.mark.parametrize("coefficients,expected_status,valid_count", [
    ([-0.1, -0.2, -0.3], "stable_negative", 3),
    ([1.0, 2.0, -1.0], "unresolved", 3),
    ([1.0, 2.0, 0.0], "unresolved", 3),
    ([1.0, 2.0, None], "incomplete", 2),
])
def test_direction_stability_requires_three_valid_nonzero_matching_signs(
    evaluator, plan, invented_only_cohort, coefficients, expected_status, valid_count
):
    reference = evaluator.analyze(invented_only_cohort, plan, reference=True)
    generated = evaluator.analyze(invented_only_cohort, plan)
    slots = []
    for construction in plan["execution"]["constructions"]:
        for stage in plan["execution"]["stages"]:
            for seed_index, seed in enumerate(plan["execution"]["seeds"]):
                active = construction == "C1" and stage == "initial"
                report = copy.deepcopy(generated) if active else None
                if active:
                    estimate = report["estimands"]["E2"]
                    estimate["coefficient"] = coefficients[seed_index]
                    estimate["status"] = "computed" if coefficients[seed_index] is not None else "unavailable"
                slots.append({
                    "construction": construction, "stage": stage, "seed": seed,
                    "status": "success" if active else "not_run", "route": "generator.py" if active else None,
                    "reason": None if active else "invented not run", "analysis": report,
                })
    actual = evaluator.summarize_slots(reference, slots)["stages"]["C1_initial"]["E2"]
    assert actual["direction_status"] == expected_status
    assert actual["valid_seed_count"] == valid_count


@pytest.mark.parametrize("corruption", ["missing", "extra", "duplicate_identity"])
def test_slot_accounting_rejects_missing_extra_or_reused_slots(evaluator, corruption):
    slots = [{"construction": construction, "stage": stage, "seed": seed,
              "status": "not_run", "route": None, "reason": "invented not run", "analysis": None}
             for construction in ("C1", "C2") for stage in ("initial", "revised") for seed in (1701, 1702, 1703)]
    if corruption == "missing":
        slots.pop()
    elif corruption == "extra":
        slots.append(copy.deepcopy(slots[0]))
    else:
        slots[-1] = copy.deepcopy(slots[0])
    with pytest.raises(ValueError):
        evaluator.summarize_slots({}, slots)


@pytest.mark.parametrize("present_stages", [[], ["C1_initial", "C1_revised", "C2_initial"]])
def test_final_inventory_rejects_unreserved_stage_before_candidate_verification(
    evaluator, tmp_path, monkeypatch, present_stages
):
    invented_bundle = tmp_path / "invented-reservation-metadata-only"
    controller = invented_bundle / "f2_controller"
    controller.mkdir(parents=True)
    invented_release_hash = "0" * 64
    for stage in present_stages:
        freeze = invented_bundle / "candidates" / stage / "freeze.json"
        freeze.parent.mkdir(parents=True)
        invented_bytes = b'{"fixture":"invented-only-nonclinical-metadata"}'
        freeze.write_bytes(invented_bytes)
        request = controller / stage / "run_request.json"
        request.parent.mkdir()
        request.write_text(json.dumps({
            "slot": stage,
            "reserved_target_table_slots": 3,
            "seeds": [1701, 1702, 1703],
            "release_sha256": invented_release_hash,
            "candidate_freeze_sha256": hashlib.sha256(invented_bytes).hexdigest(),
        }), encoding="utf-8")
    inventory = {
        "schema_version": 1, "status": "final", "f2_release_sha256": invented_release_hash,
        "final_decisions": {}, "controller_state_sha256": evaluator._tree_digest(controller), "slots": [],
    }
    calls = []

    def forbidden_next_step(*args, **kwargs):
        calls.append("candidate_or_reference_access")
        raise AssertionError("Unreserved stage reached candidate verification or reference access")

    monkeypatch.setattr(evaluator.lifecycle, "verify_candidate", forbidden_next_step)
    monkeypatch.setattr(evaluator, "_read_reference_files", forbidden_next_step)
    with pytest.raises((ValueError, OSError), match="run_request.json"):
        evaluator._final_inventory(invented_bundle, inventory, {"f2_release_sha256": invented_release_hash})
    assert calls == []


def test_missing_release_fails_before_any_reference_or_generated_read(evaluator, tmp_path, monkeypatch):
    invented_bundle = tmp_path / "invented-empty-f2-bundle"
    invented_bundle.mkdir()
    calls = []

    def forbidden_read(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("A file read was attempted without an evaluation release")

    monkeypatch.setattr(evaluator, "_read_reference_files", forbidden_read)
    monkeypatch.setattr(evaluator.pd, "read_csv", forbidden_read)
    monkeypatch.setattr(evaluator.pd, "read_sas", forbidden_read)
    monkeypatch.setattr(Path, "read_text", forbidden_read)
    monkeypatch.setattr(Path, "read_bytes", forbidden_read)
    monkeypatch.setattr(Path, "open", forbidden_read)
    monkeypatch.setattr(builtins, "open", forbidden_read)
    with pytest.raises((ValueError, OSError), match="(?i)release"):
        evaluator.evaluate_released(invented_bundle, tmp_path / "invented-no-reference-files")
    assert calls == []
