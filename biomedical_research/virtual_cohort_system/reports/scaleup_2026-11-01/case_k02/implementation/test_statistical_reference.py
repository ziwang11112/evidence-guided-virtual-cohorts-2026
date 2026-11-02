"""Small invented constraints/arrays only; never fit or sample real evidence."""
import copy
import math
from pathlib import Path
from statistics import NormalDist
import sys

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

sys.path.insert(0, str(Path(__file__).parent))
import statistical_reference as reference


@pytest.fixture
def invented():
    rows = []
    for index, context in enumerate(reference.CONTEXT_IDS):
        row = {"context_id": context}
        for field, variable, unit, value in [
            ("bmi_geometric_mean", "bmi", "kg/m^2", 12.0 + index),
            ("hdl_geometric_mean", "hdl_cholesterol", "mmol/L", 2.0 + 0.2 * index),
            ("non_hdl_geometric_mean", "non_hdl_cholesterol", "mmol/L", 4.0 + 0.3 * index),
        ]:
            row[field] = {"evidence_id": f"{context}__{variable}__geometric_mean",
                          "locator": "Invented test-only values; no published source numbers",
                          "variable": variable, "statistic": "geometric_mean", "unit": unit, "value": value}
        row["low_hdl_proportion"] = {
            "evidence_id": f"{context}__hdl_cholesterol__low_prevalence",
            "locator": "Invented analytic pair with sigma=0.5; not a clinical threshold",
            "variable": "hdl_cholesterol", "statistic": "proportion", "unit": "1",
            "value": NormalDist().cdf(-1.0), "comparison": "lt",
            "threshold": row["hdl_geometric_mean"]["value"] * math.exp(-0.5), "threshold_unit": "mmol/L",
        }
        rows.append(row)
    return rows


def test_analytic_inversion_provenance_and_no_sampling(invented, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Analytic fitting must not construct an RNG")
    monkeypatch.setattr(np.random, "default_rng", forbidden)
    fitted = reference.fit_reference(invented)
    for source, fitted_context in zip(invented, fitted["parameters"]["contexts"]):
        assert fitted_context["sigma"] == pytest.approx(0.5)
        for parameter, field in [("mu_bmi", "bmi_geometric_mean"), ("mu_hdl", "hdl_geometric_mean"),
                                 ("mu_non_hdl", "non_hdl_geometric_mean")]:
            assert math.exp(fitted_context[parameter]) == pytest.approx(source[field]["value"])
        implied = NormalDist().cdf((math.log(source["low_hdl_proportion"]["threshold"]) - fitted_context["mu_hdl"]) / fitted_context["sigma"])
        assert implied == pytest.approx(source["low_hdl_proportion"]["value"])
    assert fitted["provenance"]["sampled_rows"] == fitted["provenance"]["optimizer_calls"] == 0
    assert fitted["provenance"]["analytic_log_evaluations"] == 24
    assert fitted["provenance"]["inverse_normal_cdf_evaluations"] == 6
    assert fitted["provenance"]["normalized_constraints"] == invented
    assert fitted["provenance"]["case_release_authorized"] is False


def test_input_order_does_not_change_context_assignment_or_provenance(invented):
    assert reference.fit_reference(invented) == reference.fit_reference(list(reversed(invented)))


def test_fit_and_sample_do_not_mutate_inputs(invented):
    before = copy.deepcopy(invented)
    model = reference.fit_reference(invented)
    parameters = copy.deepcopy(model["parameters"])
    reference.sample(model["parameters"], reference.TARGET_CONTEXT_ID, 8, 9)
    assert invented == before
    assert model["parameters"] == parameters
    model["provenance"]["normalized_constraints"][0]["bmi_geometric_mean"]["value"] = 999
    assert invented == before


def test_small_sample_schema_units_support_and_reproducibility(invented):
    parameters = reference.fit_reference(invented)["parameters"]
    first = reference.sample(parameters, reference.TARGET_CONTEXT_ID, 12, 9)
    second = reference.sample(parameters, reference.TARGET_CONTEXT_ID, 12, 9)
    assert_frame_equal(first, second)
    assert not first.equals(reference.sample(parameters, reference.TARGET_CONTEXT_ID, 12, 10))
    assert list(first.columns) == list(reference.COLUMNS)
    assert len(first) == 12 and first["id"].is_unique
    assert all(type(value) is str for value in first["id"])
    assert set(first["sex"]) <= {"F", "M"}
    assert first["age"].between(18, 80, inclusive="left").all()
    assert (first[["bmi", "total_cholesterol", "hdl_cholesterol"]] > 0).all().all()
    assert (first["total_cholesterol"] > first["hdl_cholesterol"]).all()
    assert np.isfinite(first[["age", "bmi", "total_cholesterol", "hdl_cholesterol"]].to_numpy()).all()
    assert parameters["units"]["total_cholesterol"] == parameters["units"]["hdl_cholesterol"] == "mmol/L"


def test_conditional_independence_is_separate_noise_coordinates_not_empirical_claim(invented, monkeypatch):
    parameters = reference.fit_reference(invented)["parameters"]
    calls = []
    class ControlledRng:
        def standard_normal(self, shape):
            calls.append(("normal", shape))
            return np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
        def uniform(self, low, high, size):
            calls.append(("age", low, high, size))
            return np.array([20., 21., 22., 23.])
    monkeypatch.setattr(np.random, "default_rng", lambda seed: ControlledRng())
    frame = reference.sample(parameters, reference.CONTEXT_IDS[0], 4, 3)
    assert calls == [("normal", (4, 3)), ("age", 18.0, 80.0, 4)]
    assert frame["sex"].tolist() == ["M"] * 4
    assert frame["bmi"].tolist() == pytest.approx([12, 12 * math.exp(0.5), 12, 12])
    assert frame["hdl_cholesterol"].tolist() == pytest.approx([2, 2, 2 * math.exp(0.5), 2])
    implied_non_hdl = frame["total_cholesterol"] - frame["hdl_cholesterol"]
    assert implied_non_hdl.tolist() == pytest.approx([4, 4, 4, 4 * math.exp(0.5)])
    assert parameters["conditional_noise"] == "independent_standard_normals_for_bmi_hdl_non_hdl"


def test_target_uses_equal_integer_draw_with_fixed_component_order(invented, monkeypatch):
    parameters = reference.fit_reference(invented)["parameters"]
    calls = []
    class ControlledRng:
        def integers(self, low, high, size):
            calls.append((low, high, size))
            return np.arange(6)
        def standard_normal(self, shape):
            return np.zeros(shape)
        def uniform(self, low, high, size):
            return np.full(size, 30.)
    monkeypatch.setattr(np.random, "default_rng", lambda seed: ControlledRng())
    frame = reference.sample(parameters, reference.TARGET_CONTEXT_ID, 6, 1)
    assert calls == [(0, 6, 6)]
    assert frame["sex"].tolist() == ["M", "M", "M", "F", "F", "F"]
    assert frame["hdl_cholesterol"].tolist() == pytest.approx([2 + 0.2*i for i in range(6)])


@pytest.mark.parametrize("change", ["missing", "duplicate", "unknown", "extra_field", "wrong_id"])
def test_rejects_context_or_record_identity_errors(invented, change):
    if change == "missing":
        invented.pop()
    elif change == "duplicate":
        invented[1] = copy.deepcopy(invented[0])
    elif change == "unknown":
        invented[0]["context_id"] = "wrong_context"
    elif change == "extra_field":
        invented[0]["total_cholesterol_geometric_mean"] = 3.0
    else:
        invented[0]["hdl_geometric_mean"]["evidence_id"] = invented[1]["hdl_geometric_mean"]["evidence_id"]
    with pytest.raises(ValueError):
        reference.fit_reference(invented)


@pytest.mark.parametrize("field,value", [("unit", "mg/dL"), ("statistic", "arithmetic_mean"),
                                         ("variable", "total_cholesterol"), ("locator", " "),
                                         ("value", 0), ("value", -1), ("value", True),
                                         ("value", "2"), ("value", float("nan")), ("value", float("inf"))])
def test_rejects_invalid_geometric_mean_semantics_or_values(invented, field, value):
    invented[0]["hdl_geometric_mean"][field] = value
    with pytest.raises(ValueError):
        reference.fit_reference(invented)


@pytest.mark.parametrize("field,value", [("unit", "%"), ("comparison", "le"), ("threshold_unit", "mg/dL"),
                                         ("threshold", 0), ("threshold", float("inf")), ("threshold", True),
                                         ("value", 0), ("value", 1), ("value", 0.5), ("value", -0.2),
                                         ("value", float("nan")), ("value", True), ("value", "0.2")])
def test_rejects_invalid_probability_or_threshold(invented, field, value):
    invented[0]["low_hdl_proportion"][field] = value
    with pytest.raises(ValueError):
        reference.fit_reference(invented)


@pytest.mark.parametrize("kind", ["zero_sigma", "negative_sigma"])
def test_rejects_incompatible_lognormal_pair(invented, kind):
    hdl = invented[0]["hdl_geometric_mean"]["value"]
    invented[0]["low_hdl_proportion"]["threshold"] = hdl if kind == "zero_sigma" else 2 * hdl
    with pytest.raises(ValueError, match="dispersion"):
        reference.fit_reference(invented)


@pytest.mark.parametrize("field,value", [("n_rows", 0), ("n_rows", 5001), ("n_rows", True), ("n_rows", 3.0),
                                         ("seed", -1), ("seed", 2**32), ("seed", True), ("context_id", "unknown"),
                                         ("context_id", "target")])
def test_rejects_invalid_sample_request(invented, field, value):
    parameters = reference.fit_reference(invented)["parameters"]
    request = {"context_id": reference.TARGET_CONTEXT_ID, "n_rows": 3, "seed": 4}
    request[field] = value
    with pytest.raises(ValueError):
        reference.sample(parameters, **request)


@pytest.mark.parametrize("change", ["age", "mixture", "units", "sex", "sigma", "nan", "order"])
def test_rejects_changed_fixed_conventions_or_invalid_parameters(invented, change):
    parameters = reference.fit_reference(invented)["parameters"]
    if change == "age":
        parameters["age"]["high"] = 90.0
    elif change == "mixture":
        parameters["target_mixture"] = "fitted_to_target"
    elif change == "units":
        parameters["units"]["hdl_cholesterol"] = "mg/dL"
    elif change == "sex":
        parameters["contexts"][0]["encoded_sex"] = "F"
    elif change == "sigma":
        parameters["contexts"][0]["sigma"] = 0
    elif change == "nan":
        parameters["contexts"][0]["mu_hdl"] = float("nan")
    else:
        parameters["contexts"].reverse()
    with pytest.raises(ValueError):
        reference.sample(parameters, reference.TARGET_CONTEXT_ID, 3, 2)


@pytest.mark.parametrize("parameter,value,match", [("mu_hdl", 1000.0, "Nonfinite/nonpositive"),
                                                   ("mu_hdl", -1000.0, "Nonfinite/nonpositive"),
                                                   ("mu_non_hdl", -700.0, "lost the positive")])
def test_bad_float_output_fails_without_redraw_or_clipping(invented, monkeypatch, parameter, value, match):
    parameters = reference.fit_reference(invented)["parameters"]
    parameters["contexts"][0][parameter] = value
    draws = []
    class ControlledRng:
        def standard_normal(self, shape):
            draws.append(shape)
            return np.zeros(shape)
        def uniform(self, low, high, size):
            return np.full(size, 30.)
    monkeypatch.setattr(np.random, "default_rng", lambda seed: ControlledRng())
    with pytest.raises(ValueError, match=match):
        reference.sample(parameters, reference.CONTEXT_IDS[0], 2, 1)
    assert draws == [(2, 3)]


def test_pure_api_performs_no_file_io(invented, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Pure reference cannot access files")
    monkeypatch.setattr("builtins.open", forbidden)
    model = reference.fit_reference(invented)
    frame = reference.sample(model["parameters"], reference.TARGET_CONTEXT_ID, 3, 1)
    assert len(frame) == 3
