"""Analytic and invented in-memory examples, never patient validation."""
import copy
import importlib.util
import math
from pathlib import Path
import socket
import subprocess

import numpy as np
import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location("contextual_statistics", Path(__file__).with_name("contextual_statistics.py"))
ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ops)


@pytest.fixture
def example():
    frame = pd.DataFrame({"x": [1., 4., 16., 100., 1000.], "sex": ["F", "F", "F", "M", "F"],
                          "site": ["A", "A", "A", "A", "B"]})
    operator = {"kind": "geometric_mean", "column": "x", "unit": "example_unit", "selection": [
        {"column": "sex", "op": "eq", "value": "F"}, {"column": "site", "op": "eq", "value": "A"}],
        "selection_missing_policy": "error", "missing_policy": "error"}
    context = {"kind": "source_context_simulation", "context_id": "invented-source-context",
               "population": "Invented source population", "measurement": "Invented original-scale assay",
               "variable_units": {"x": "example_unit", "sex": "1", "site": "1"},
               "variable_scales": {"x": "original", "sex": "categorical", "site": "categorical"}}
    source = {**{k: copy.deepcopy(v) for k, v in context.items() if k != "kind"}, "source_id": "invented-study",
              "locator": "Invented table; no real study values", "operator": copy.deepcopy(operator), "weights": "none",
              "definition_status": "specified", "uncertainty_role": "estimator_confidence_interval"}
    return frame, operator, context, source


def approve(example):
    return {"decision": "approved", "independent": True, "reviewer_id": "test-reviewer", "producer_id": "test-producer",
            "reviewed_utc": "2026-11-02T00:00:00Z", "reason": "Invented metadata approval for a unit test only",
            "approved_contract": ops.context_contract(*example)}


def evaluate(example, approved=True):
    return ops.diagnostic(*example, approval=approve(example) if approved else None)


def test_analytic_geometric_mean_and_explicit_sex_site_selection(example):
    frame = example[0].copy(deep=True)
    result = evaluate(example)
    assert result["diagnostic"]["value"] == pytest.approx(4)
    assert result["diagnostic"]["value"] != pytest.approx((1 + 4 + 16) / 3)
    assert result["diagnostic"]["n_input"] == 5
    assert result["diagnostic"]["n_selected"] == result["diagnostic"]["n_used"] == 3
    assert result["exact_source_check_allowed"]
    pd.testing.assert_frame_equal(frame, example[0])


def test_product_overflow_avoided_by_log_definition(example):
    example[0].loc[:2, "x"] = [1e200, 1e200, 1e-200]
    assert evaluate(example)["diagnostic"]["value"] == pytest.approx(10 ** (200 / 3), rel=1e-12)


@pytest.mark.parametrize("value", [0., -1., np.nan, np.inf, -np.inf])
def test_undefined_values_are_not_silently_repaired(example, value):
    example[0].loc[0, "x"] = value
    result = evaluate(example)
    assert not result["diagnostic_available"] and result["diagnostic"] is None
    assert not result["exact_source_check_allowed"]


def test_complete_cases_only_excludes_declared_missing_values(example):
    example[0].loc[0, "x"] = np.nan
    example[1]["missing_policy"] = example[3]["operator"]["missing_policy"] = "complete_cases"
    result = evaluate(example)
    assert result["diagnostic"]["value"] == pytest.approx(8)
    assert result["diagnostic"]["n_used"] == 2 and result["diagnostic"]["n_missing_dropped"] == 1
    example[0].loc[0, "x"] = 0
    assert not evaluate(example)["diagnostic_available"]


def test_missing_selection_needs_its_own_declared_policy(example):
    example[0].loc[0, "sex"] = None
    assert not evaluate(example)["diagnostic_available"]
    example[1]["selection_missing_policy"] = example[3]["operator"]["selection_missing_policy"] = "exclude"
    result = evaluate(example)
    assert result["diagnostic"]["value"] == pytest.approx(8)
    assert result["diagnostic"]["n_missing_selection_excluded"] == 1


def test_empty_stratum_is_unavailable(example):
    example[0]["site"] = "B"
    assert not evaluate(example)["diagnostic_available"]


@pytest.mark.parametrize("comparison, expected", [("gt", 100 / 3), ("ge", 200 / 3), ("lt", 100 / 3), ("le", 200 / 3)])
def test_threshold_prevalence_boundary_and_denominator(example, comparison, expected):
    operator = example[1]
    operator.pop("column")
    operator.update(kind="proportion", unit="%", event={"column": "x", "op": comparison, "value": 4.})
    example[3]["operator"] = copy.deepcopy(operator)
    result = evaluate(example)
    assert result["diagnostic"]["value"] == pytest.approx(expected)
    assert result["diagnostic"]["n_used"] == 3
    assert result["exact_source_check_allowed"]
    operator["unit"] = example[3]["operator"]["unit"] = "1"
    assert evaluate(example)["diagnostic"]["value"] == pytest.approx(expected / 100)


@pytest.mark.parametrize("weights", ["not_reported", "weighted"])
def test_unknown_or_weighted_source_is_not_equal_weight_source_check(example, weights):
    example[3]["weights"] = weights
    result = evaluate(example)
    assert result["diagnostic_available"] and result["diagnostic_weights"] == "none"
    assert result["source_weights"] == weights and not result["exact_source_check_allowed"]


def test_target_context_never_promoted_by_an_approval(example):
    example[2]["kind"] = "target_context_generated"
    result = evaluate(example)
    assert result["diagnostic_available"] and not result["exact_source_check_allowed"]
    assert result["diagnostic_scope"] == "target_context_generated"


def test_source_label_alone_does_not_enable_exact_source_check(example):
    result = evaluate(example, approved=False)
    assert result["diagnostic_available"] and not result["exact_source_check_allowed"]


def test_changed_table_cannot_reuse_source_approval(example):
    approval = approve(example)
    example[0].loc[0, "x"] = 9
    result = ops.diagnostic(*example, approval=approval)
    assert result["diagnostic_available"] and not result["exact_source_check_allowed"]


def test_relabelled_target_table_cannot_reuse_target_contract(example):
    example[2]["kind"] = "target_context_generated"
    approval = approve(example)
    example[2]["kind"] = "source_context_simulation"
    assert not ops.diagnostic(*example, approval=approval)["exact_source_check_allowed"]


@pytest.mark.parametrize("mismatch", ["population", "measurement", "unit", "selection", "source_unknown", "self_review"])
def test_context_and_definition_mismatches_are_descriptive_only(example, mismatch):
    if mismatch in {"population", "measurement"}: example[3][mismatch] = "Different source declaration"
    if mismatch == "unit": example[3]["variable_units"]["x"] = "different_unit"
    if mismatch == "selection": example[3]["operator"]["selection"][1]["value"] = "B"
    if mismatch == "source_unknown": example[3].update(definition_status="not_reported", operator=None)
    approval = approve(example)
    if mismatch == "self_review": approval["reviewer_id"] = approval["producer_id"]
    result = ops.diagnostic(*example, approval=approval)
    assert result["diagnostic_available"] and not result["exact_source_check_allowed"]


@pytest.mark.parametrize("scale", ["natural_log", "log10", "not_reported"])
def test_logged_or_unknown_input_scale_is_not_silently_backtransformed(example, scale):
    example[2]["variable_scales"]["x"] = example[3]["variable_scales"]["x"] = scale
    assert not evaluate(example)["diagnostic_available"]


def test_ci_is_not_used_as_sd_or_precision(example):
    result = evaluate(example)
    assert result["source_uncertainty_role"] == "estimator_confidence_interval"
    assert result["uncertainty_conversion"] == "none" and result["uncertainty_estimated"] is False
    assert set(result["diagnostic"]) == {"value", "unit", "n_input", "n_selected", "n_used", "n_missing_dropped", "n_missing_selection_excluded"}


def test_no_data_read_process_or_network_calls(example, monkeypatch):
    def forbidden(*args, **kwargs): raise AssertionError("Unexpected external access")
    monkeypatch.setattr(pd, "read_csv", forbidden)
    monkeypatch.setattr(pd, "read_sas", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    assert evaluate(example)["diagnostic_available"]


def selection_review_example(example, kind, selection, *, numeric=False, scale="categorical"):
    """Isolate selection semantics from the statistic's numeric x operand."""
    _, operator, context, source = copy.deepcopy(example)
    frame = pd.DataFrame({"x": [1., 4., 16.], "site": [10., 20., 30.] if numeric else ["A", "B", "C"]})
    operator["selection"] = [selection]
    if kind == "proportion":
        operator.pop("column")
        operator.update(kind="proportion", unit="%", event={"column": "x", "op": "gt", "value": 4.})
    context["variable_units"] = {"x": "example_unit", "site": "1"}
    context["variable_scales"] = {"x": "original", "site": scale}
    source.update(operator=copy.deepcopy(operator), variable_units=copy.deepcopy(context["variable_units"]),
                  variable_scales=copy.deepcopy(context["variable_scales"]))
    return frame, operator, context, source


@pytest.mark.parametrize("kind", ["geometric_mean", "proportion"])
@pytest.mark.parametrize("comparison", ["lt", "ge"])
def test_selection_review_categorical_order_cannot_reuse_scalar_approval(example, kind, comparison):
    item = selection_review_example(example, kind, {"column": "site", "op": comparison, "value": "B"})
    approval = approve(item)
    object_result = ops.diagnostic(*item, approval=approval)
    item[0]["site"] = pd.Categorical(item[0]["site"], categories=["C", "B", "A"], ordered=True)
    # The normalized scalar commitment is deliberately unchanged. The unsafe
    # predicate must be unavailable for BOTH representations, not approved by it.
    assert ops.context_contract(*item) == approval["approved_contract"]
    categorical_result = ops.diagnostic(*item, approval=approval)
    for report in (object_result, categorical_result):
        assert not report["diagnostic_available"] and not report["exact_source_check_allowed"]
        assert any("Ordered selection requires" in reason for reason in report["eligibility_reasons"])


@pytest.mark.parametrize("kind", ["geometric_mean", "proportion"])
@pytest.mark.parametrize("comparison,value,gm,prevalence", [("eq", "A", 1., 0.), ("in", ["B", "C"], 8., 50.)])
def test_selection_review_categorical_membership_is_order_independent(example, kind, comparison, value, gm, prevalence):
    item = selection_review_example(example, kind, {"column": "site", "op": comparison, "value": value})
    approval = approve(item)
    original = ops.diagnostic(*item, approval=approval)
    item[0]["site"] = pd.Categorical(item[0]["site"], categories=["C", "B", "A"], ordered=True)
    reordered = ops.diagnostic(*item, approval=approval)
    for report in (original, reordered):
        assert report["exact_source_check_allowed"]
        assert report["diagnostic"]["value"] == pytest.approx(gm if kind == "geometric_mean" else prevalence)


@pytest.mark.parametrize("kind", ["geometric_mean", "proportion"])
@pytest.mark.parametrize("scale", ["not_reported", "natural_log", "log10"])
def test_selection_review_unknown_or_logged_numeric_scale_is_unavailable(example, kind, scale):
    item = selection_review_example(example, kind, {"column": "site", "op": "ge", "value": 20.}, numeric=True, scale=scale)
    report = evaluate(item)
    assert not report["diagnostic_available"] and not report["exact_source_check_allowed"]
    assert any("selection scales are unsupported" in reason for reason in report["eligibility_reasons"])


@pytest.mark.parametrize("scale", ["not_reported", "natural_log", "log10"])
def test_selection_review_unknown_or_logged_string_equality_is_unavailable(example, scale):
    item = selection_review_example(example, "geometric_mean", {"column": "site", "op": "eq", "value": "A"}, scale=scale)
    report = evaluate(item)
    assert not report["diagnostic_available"] and not report["exact_source_check_allowed"]


@pytest.mark.parametrize("kind", ["geometric_mean", "proportion"])
def test_selection_review_numeric_category_cannot_use_ordinal_threshold(example, kind):
    item = selection_review_example(example, kind, {"column": "site", "op": "ge", "value": 20.}, numeric=True)
    report = evaluate(item)
    assert not report["diagnostic_available"] and not report["exact_source_check_allowed"]


@pytest.mark.parametrize("kind", ["geometric_mean", "proportion"])
def test_selection_review_original_numeric_threshold_remains_available(example, kind):
    item = selection_review_example(example, kind, {"column": "site", "op": "ge", "value": 20.}, numeric=True, scale="original")
    report = evaluate(item)
    assert report["exact_source_check_allowed"] and report["diagnostic"]["n_used"] == 2
    assert report["diagnostic"]["value"] == pytest.approx(8. if kind == "geometric_mean" else 50.)
