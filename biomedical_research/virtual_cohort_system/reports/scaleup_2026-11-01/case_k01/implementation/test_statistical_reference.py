"""Invented inputs only: no candidate evidence files or participant data are read."""
import copy
import math
from statistics import NormalDist

import numpy as np
import pandas as pd
import pytest
from scipy.special import betainc

import statistical_reference as ref


def invented_records():
    """All moments/counts are invented; IDs denote schema slots, not real values."""
    rows = []
    def moment(context, item, variable, statistic, unit, value):
        rows.append(dict(evidence_id=item, context_id=context, variable=variable,
                         statistic=statistic, unit=unit, value=value,
                         locator="Invented fixture, not a published estimate"))
    for context, prefix, variables in [
        (ref.MIND_CONTEXT, "MIND_K01", [("age", "age", "year", 70., 3.),
           ("bmi", "bmi", "kg/m^2", 26., 4.5), ("serum_glucose_fsg", "glucose", "mmol/L", 6., 1.2)]),
        (ref.AYELE_CONTEXT, "ayele", [("age", "age", "year", 44., 9.)]),
    ]:
        for name, variable, unit, mean, sd in variables:
            moment(context, prefix+"_"+name+"_mean", variable, "arithmetic_mean", unit, mean)
            moment(context, prefix+"_"+name+"_sd", variable, "individual_standard_deviation", unit, sd)
    def count(context, item, variable, group, numerator, denominator):
        record = dict(evidence_id=item, context_id=context, variable=variable,
                      statistic="count_ratio", unit="1", group=group,
                      numerator=numerator, denominator=denominator,
                      locator="Invented fixture count, not a published value")
        if context == ref.AYELE_CONTEXT:
            record["reported_percentage"] = round(100*numerator/denominator, 1)
        rows.append(record)
    count(ref.MIND_CONTEXT, "MIND_K01_female_proportion", "sex", "Female", 6, 10)
    for item, variable, group, numerator in [
        ("ayele_sex_male", "sex", "Male", 5),
        ("ayele_sex_female", "sex", "Female", 7),
        ("ayele_age_25_34", "age", "25–34", 3),
        ("ayele_age_35_44", "age", "35–44", 3),
        ("ayele_age_45_54", "age", "45–54", 3),
        ("ayele_age_55_64", "age", "55–64", 3),
        ("ayele_bmi_underweight", "bmi", "<18.5", 3),
        ("ayele_bmi_normal", "bmi", "18.5–24.9", 6),
        ("ayele_bmi_overweight", "bmi", ">=25", 3),
    ]:
        count(ref.AYELE_CONTEXT, item, variable, group, numerator, 12)
    return rows


def item(rows, evidence_id):
    return next(row for row in rows if row["evidence_id"] == evidence_id)


def test_analytic_moment_and_tail_inversion_without_sampling():
    result = ref.fit_reference(invented_records())
    parameters = result["parameters"]
    for context, expected_mean, expected_sd in zip(parameters["contexts"], (70., 44.), (3., 9.)):
        age = context["age"]
        a, b, width = age["alpha"], age["beta"], age["high"]-age["low"]
        assert age["low"] + width*a/(a+b) == pytest.approx(expected_mean)
        variance = width**2*a*b/((a+b)**2*(a+b+1))
        assert math.sqrt(variance) == pytest.approx(expected_sd)
    for distribution, mean, sd in ((parameters["contexts"][0]["bmi"], 26., 4.5),
                                   (parameters["glucose"], 6., 1.2)):
        mu, sigma = distribution["mu"], distribution["sigma"]
        assert math.exp(mu+sigma*sigma/2) == pytest.approx(mean)
        assert math.sqrt(math.expm1(sigma*sigma)*math.exp(2*mu+sigma*sigma)) == pytest.approx(sd)
    bmi = parameters["contexts"][1]["bmi"]
    cdf = lambda x: NormalDist().cdf((math.log(x)-bmi["mu"])/bmi["sigma"])
    assert cdf(18.5) == pytest.approx(3/12)
    assert 1-cdf(25) == pytest.approx(3/12)
    # The literal24.9 upper endpoint is not silently replaced with25.
    assert cdf(24.9)-cdf(18.5) < 6/12
    assert parameters["contexts"][0]["female_probability"] == 6/10
    assert parameters["contexts"][1]["female_probability"] == 7/12
    assert result["provenance"]["sampled_rows"] == result["provenance"]["optimizer_calls"] == 0


def test_count_fitting_ignores_printed_rounding_and_unfitted_age_bins():
    rows = invented_records()
    first = ref.fit_reference(rows)
    item(rows, "ayele_bmi_underweight")["reported_percentage"] = 26.2
    item(rows, "ayele_sex_female")["reported_percentage"] = 57.1
    item(rows, "ayele_age_25_34")["numerator"] = 2
    item(rows, "ayele_age_35_44")["numerator"] = 4
    second = ref.fit_reference(rows)
    assert second["parameters"] == first["parameters"]
    assert second["provenance"]["normalized_constraints_sha256"] != first["provenance"]["normalized_constraints_sha256"]


def test_input_order_and_no_mutation_or_aliasing():
    rows = invented_records()
    before = copy.deepcopy(rows)
    first = ref.fit_reference(rows)
    second = ref.fit_reference(list(reversed(rows)))
    assert rows == before
    assert first == second
    first["provenance"]["normalized_constraints"][0]["locator"] = "changed returned copy"
    assert rows == before


@pytest.mark.parametrize("context,low,high", [(ref.MIND_CONTEXT, 61, 80),
    (ref.AYELE_CONTEXT, 25, 64), (ref.TARGET_CONTEXT, 40, 80)])
def test_small_deterministic_draw_and_context_bounds(context, low, high):
    parameters = ref.fit_reference(invented_records())["parameters"]
    before = copy.deepcopy(parameters)
    frame = ref.sample(parameters, context, 24, 101)
    pd.testing.assert_frame_equal(frame, ref.sample(parameters, context, 24, 101))
    assert not frame.equals(ref.sample(parameters, context, 24, 102))
    assert parameters == before
    assert list(frame.columns) == ["id", "age", "sex", "bmi", "glucose"]
    assert len(frame) == 24 and frame["id"].is_unique
    assert set(frame["sex"]) <= {"F", "M"}
    assert frame["age"].between(low, high, inclusive="both").all()
    assert np.isfinite(frame[["age", "bmi", "glucose"]]).all().all()
    assert (frame[["bmi", "glucose"]] > 0).all().all()


def test_target_sampling_structure_and_conditional_inverse_cdf(monkeypatch):
    parameters = ref.fit_reference(invented_records())["parameters"]
    ua = np.array([.15, .25, .65, .85])
    us = np.array([.2, .9, .8, .3])
    zb = np.array([-.3, .4, .9, -.8])
    zg = np.array([.7, -.6, -.2, .1])
    class FixedNoise:
        def __init__(self): self.uniform_calls = self.normal_calls = 0
        def integers(self, low, high, n):
            assert (low, high, n) == (0, 2, 4)  # equal donor selection, before conditioning
            return np.array([0, 1, 0, 1])
        def random(self, n):
            assert n == 4
            self.uniform_calls += 1
            return ua.copy() if self.uniform_calls == 1 else us.copy()
        def standard_normal(self, n):
            assert n == 4
            self.normal_calls += 1
            return zb.copy() if self.normal_calls == 1 else zg.copy()
    noise = FixedNoise()
    monkeypatch.setattr(ref.np.random, "default_rng", lambda seed: noise)
    frame = ref.sample(parameters, ref.TARGET_CONTEXT, 4, 7)
    g = parameters["glucose"]
    np.testing.assert_allclose(frame["glucose"], np.exp(g["mu"]+g["sigma"]*zg), rtol=1e-14)
    for index, donor in enumerate([0, 1, 0, 1]):
        context = parameters["contexts"][donor]
        age = context["age"]
        q = 0 if 40 <= age["low"] else betainc(age["alpha"], age["beta"], (40-age["low"])/(age["high"]-age["low"]))
        observed_cdf = betainc(age["alpha"], age["beta"], (frame.loc[index,"age"]-age["low"])/(age["high"]-age["low"]))
        assert observed_cdf == pytest.approx(q+(1-q)*ua[index], abs=2e-14)
        b = context["bmi"]
        assert frame.loc[index,"bmi"] == pytest.approx(math.exp(b["mu"]+b["sigma"]*zb[index]))
        assert frame.loc[index,"sex"] == ("F" if us[index] < context["female_probability"] else "M")
    assert (noise.uniform_calls, noise.normal_calls) == (2, 2)


def test_changing_bmi_law_does_not_change_other_noise_draws():
    parameters = ref.fit_reference(invented_records())["parameters"]
    changed = copy.deepcopy(parameters)
    for context in changed["contexts"]:
        context["bmi"]["mu"] += .2
    original = ref.sample(parameters, ref.TARGET_CONTEXT, 16, 38)
    altered = ref.sample(changed, ref.TARGET_CONTEXT, 16, 38)
    pd.testing.assert_frame_equal(original.drop(columns="bmi"), altered.drop(columns="bmi"))
    np.testing.assert_allclose(altered["bmi"], original["bmi"]*math.exp(.2))


@pytest.mark.parametrize("field,bad", [("unit", "mg/dL"), ("variable", "hdl_cholesterol"),
    ("statistic", "geometric_mean"), ("context_id", ref.AYELE_CONTEXT),
    ("locator", " "), ("value", float("nan")), ("value", float("inf")),
    ("value", 0), ("value", -1), ("value", True)])
def test_invalid_moment_records_fail(field, bad):
    rows = invented_records()
    item(rows, "MIND_K01_serum_glucose_fsg_mean")[field] = bad
    with pytest.raises(ValueError): ref.fit_reference(rows)


@pytest.mark.parametrize("defect", ["missing", "duplicate", "unknown_id", "extra_field",
    "zero_sd", "outside_age", "excess_age_variance", "zero_count", "noninteger_count",
    "bool_count", "denominator_zero", "inconsistent_denominator", "count_sum",
    "no_middle_mass", "all_one_sex", "wrong_group", "bad_percentage"])
def test_invalid_constraint_sets_fail(defect):
    rows = invented_records()
    if defect == "missing": rows.pop()
    elif defect == "duplicate": rows[-1] = copy.deepcopy(rows[0])
    elif defect == "unknown_id": rows[0]["evidence_id"] = "other_study"
    elif defect == "extra_field": rows[0]["unreported_adjustment"] = 1
    elif defect == "zero_sd": item(rows,"MIND_K01_age_sd")["value"] = 0
    elif defect == "outside_age": item(rows,"MIND_K01_age_mean")["value"] = 59
    elif defect == "excess_age_variance": item(rows,"ayele_age_sd")["value"] = 100
    elif defect == "zero_count":
        item(rows,"ayele_bmi_underweight")["numerator"] = 0
        item(rows,"ayele_bmi_normal")["numerator"] = 9
    elif defect == "noninteger_count": item(rows,"ayele_bmi_underweight")["numerator"] = 3.0
    elif defect == "bool_count": item(rows,"ayele_bmi_underweight")["numerator"] = True
    elif defect == "denominator_zero": item(rows,"MIND_K01_female_proportion")["denominator"] = 0
    elif defect == "inconsistent_denominator": item(rows,"ayele_bmi_normal")["denominator"] = 13
    elif defect == "count_sum": item(rows,"ayele_age_25_34")["numerator"] = 2
    elif defect == "no_middle_mass":
        item(rows,"ayele_bmi_normal")["numerator"] = 0
        item(rows,"ayele_bmi_overweight")["numerator"] = 9
    elif defect == "all_one_sex": item(rows,"MIND_K01_female_proportion")["numerator"] = 10
    elif defect == "wrong_group": item(rows,"ayele_bmi_normal")["group"] = "18.5–25"
    elif defect == "bad_percentage": item(rows,"ayele_bmi_normal")["reported_percentage"] = 101
    with pytest.raises(ValueError): ref.fit_reference(rows)


@pytest.mark.parametrize("context,n_rows,seed", [("target", 4, 1),
    ("context_bahendeka_uganda_2014", 4, 1), (ref.TARGET_CONTEXT, 0, 1),
    (ref.TARGET_CONTEXT, 5001, 1), (ref.TARGET_CONTEXT, True, 1),
    (ref.TARGET_CONTEXT, 4, -1), (ref.TARGET_CONTEXT, 4, 2**64),
    (ref.TARGET_CONTEXT, 4, True), (ref.TARGET_CONTEXT, 4, 1.5)])
def test_invalid_sample_request_fails(context, n_rows, seed):
    with pytest.raises(ValueError):
        ref.sample(ref.fit_reference(invented_records())["parameters"], context, n_rows, seed)


@pytest.mark.parametrize("defect", ["target_id", "weights", "source_bounds", "nonfinite_shape",
    "zero_shape", "wrong_context_order", "negative_sigma", "extra_parameter"])
def test_invalid_parameters_fail(defect):
    parameters = ref.fit_reference(invented_records())["parameters"]
    if defect == "target_id": parameters["target_context_id"] = "target"
    elif defect == "weights": parameters["target_donor_probabilities"] = [.8,.2]
    elif defect == "source_bounds": parameters["contexts"][1]["age"]["low"] = 40
    elif defect == "nonfinite_shape": parameters["contexts"][0]["age"]["alpha"] = float("nan")
    elif defect == "zero_shape": parameters["contexts"][0]["age"]["alpha"] = 0
    elif defect == "wrong_context_order": parameters["contexts"].reverse()
    elif defect == "negative_sigma": parameters["glucose"]["sigma"] = -1
    elif defect == "extra_parameter": parameters["wanted_target_slope"] = 1
    with pytest.raises(ValueError): ref.sample(parameters, ref.TARGET_CONTEXT, 4, 1)


def test_failed_inverse_cdf_stops_without_redraw(monkeypatch):
    parameters = ref.fit_reference(invented_records())["parameters"]
    calls = []
    def broken(alpha, beta, probabilities):
        calls.append(len(probabilities))
        return np.full_like(probabilities, np.nan)
    monkeypatch.setattr(ref, "betaincinv", broken)
    with pytest.raises(ValueError, match="inverse CDF failed"):
        ref.sample(parameters, ref.MIND_CONTEXT, 4, 1)
    assert calls == [4]


def test_no_retained_age_mass_and_nonfinite_output_stop():
    parameters = ref.fit_reference(invented_records())["parameters"]
    with pytest.raises(ValueError, match="No age mass"):
        ref._draw_age(parameters["contexts"][1]["age"], np.array([.5]), 64)
    parameters["glucose"]["mu"] = 1000
    with pytest.raises(FloatingPointError): ref.sample(parameters, ref.TARGET_CONTEXT, 4, 1)
