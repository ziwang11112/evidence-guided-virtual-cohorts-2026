"""Hand-computed invented fixtures; no patient data or scientific tuning."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from cohort_harness.contracts import validate_evidence
from cohort_harness.demo import make_demo
from cohort_harness.lifecycle import read_json
from cohort_harness.source_checks import NotComputable, apply_operator, run_source_checks
from test_source_replay import write


def op(kind, **fields):
    return {"kind": kind, "unit": "1" if kind == "spearman_correlation" else "y_unit",
            "selection": [], "missing_policy": "error", **fields}


@pytest.mark.parametrize("values,expected", [([9, 1, 6], 6), ([9, 1, 3, 7], 5), ([12], 12)])
def test_median_odd_even_and_singleton(values, expected):
    result = apply_operator(pd.DataFrame({"y": values}), op("median", column="y", method="linear"))
    assert result == {"value": expected, "n_input": len(values), "n_selected": len(values),
                      "n_used": len(values), "n_missing_dropped": 0, "unit": "y_unit"}


@pytest.mark.parametrize("q,expected", [(0, 0), (0.25, 3), (0.5, 6), (0.75, 11), (1, 20)])
def test_linear_quantile_uses_fractional_n_minus_one_index(q, expected):
    # Sorted [0,4,8,20]. q=.25 has h=(4-1)*.25=.75, giving 0+.75*(4-0)=3.
    result = apply_operator(pd.DataFrame({"y": [20, 4, 0, 8]}),
                            op("quantile", column="y", q=q, method="linear"))
    assert result["value"] == expected


@pytest.mark.parametrize("q", [0, 0.3, 1])
def test_quantile_singleton_is_defined(q):
    assert apply_operator(pd.DataFrame({"y": [12]}),
                          op("quantile", column="y", q=q, method="linear"))["value"] == 12


def test_quantile_selection_missing_rows_and_ties():
    table = pd.DataFrame({"y": [999, 0, np.nan, 0, 8, 20], "group": [0, 1, 1, 1, 1, 0]})
    operator = op("quantile", column="y", q=0.75, method="linear", missing_policy="complete_cases",
                  selection=[{"column": "group", "op": "eq", "value": 1}])
    result = apply_operator(table, operator)
    # Complete selected values [0,0,8]; h=1.5, halfway between 0 and 8.
    assert result == {"value": 4, "n_input": 6, "n_selected": 4, "n_used": 3,
                      "n_missing_dropped": 1, "unit": "y_unit"}
    with pytest.raises(ValueError, match="Missing"):
        apply_operator(table, {**operator, "missing_policy": "error"})


@pytest.mark.parametrize("q", [-0.01, 1.01, True, None, "0.5", np.nan, np.inf, 10 ** 400])
def test_quantile_rejects_invalid_probability(q):
    with pytest.raises(ValueError, match="Quantile q"):
        apply_operator(pd.DataFrame({"y": [1, 2]}), op("quantile", column="y", q=q, method="linear"))


@pytest.mark.parametrize("operator", [
    op("quantile", column="y", q=0.25),
    op("quantile", column="y", method="linear"),
    op("quantile", column="y", q=0.25, method="nearest"),
    op("median", column="y"),
    op("median", column="y", method="not_reported"),
    op("median", column="y", q=0.5, method="linear"),
    op("spearman_correlation", x="x", y="y", method="dense"),
    op("mean", column="y", method="linear"),
])
def test_operator_definition_fields_are_strict(operator):
    with pytest.raises(ValueError):
        apply_operator(pd.DataFrame({"x": [1, 2], "y": [1, 2]}), operator)


def test_spearman_average_ties_matches_hand_rank_correlation():
    # Ranks x=[1.5,1.5,3,4.5,4.5], y=[1,2.5,2.5,4,5], both have mean 3.
    # Centered cross-product=8.25; squared sums=9 and 9.5.
    table = pd.DataFrame({"x": [1, 1, 2, 3, 3], "y": [1, 2, 2, 3, 4]})
    assert apply_operator(table, op("spearman_correlation", x="x", y="y"))["value"] == pytest.approx(
        8.25 / math.sqrt(9 * 9.5))


def test_spearman_is_distinct_from_pearson_and_handles_reverse_order():
    table = pd.DataFrame({"x": [1, 2, 3, 4], "y": [1, 2, 4, 8]})
    assert apply_operator(table, op("spearman_correlation", x="x", y="y"))["value"] == pytest.approx(1)
    assert apply_operator(table, op("correlation", x="x", y="y"))["value"] < 0.97
    table["y"] = [8, 4, 2, 1]
    assert apply_operator(table, op("spearman_correlation", x="x", y="y"))["value"] == pytest.approx(-1)


def test_spearman_ranks_only_complete_selected_pairs():
    table = pd.DataFrame({"x": [0, 1, 1, 2, 3, 99], "y": [8, 4, 3, np.nan, 1, 0],
                          "group": [0, 1, 1, 1, 1, 0]})
    operator = op("spearman_correlation", x="x", y="y", missing_policy="complete_cases",
                  selection=[{"column": "group", "op": "eq", "value": 1}])
    result = apply_operator(table, operator)
    # Complete selected ranks [1.5,1.5,3] and [3,2,1]: -1.5/sqrt(1.5*2).
    assert result["value"] == pytest.approx(-math.sqrt(3) / 2)
    assert (result["n_input"], result["n_selected"], result["n_used"], result["n_missing_dropped"]) == (6, 4, 3, 1)
    with pytest.raises(ValueError, match="Missing"):
        apply_operator(table, {**operator, "missing_policy": "error"})


@pytest.mark.parametrize("table", [pd.DataFrame({"x": [1], "y": [2]}),
                                   pd.DataFrame({"x": [1, 1], "y": [2, 3]}),
                                   pd.DataFrame({"x": [1, 2], "y": [3, 3]})])
def test_spearman_rejects_singleton_or_constant_ranks(table):
    with pytest.raises(NotComputable, match="nonconstant ranks"):
        apply_operator(table, op("spearman_correlation", x="x", y="y"))


@pytest.mark.parametrize("operator", [op("median", column="y", method="linear"),
                                      op("quantile", column="y", q=0.25, method="linear"),
                                      op("spearman_correlation", x="x", y="y")])
@pytest.mark.parametrize("values,message", [([1, np.inf], "Nonfinite"), ([1, -np.inf], "Nonfinite"),
                                            ([True, False], "Numeric"), (["1", "2"], "Numeric")])
def test_new_operators_reject_nonfinite_or_implicit_encoding(operator, values, message):
    with pytest.raises(ValueError, match=message):
        apply_operator(pd.DataFrame({"x": [1, 2], "y": values}), operator)


@pytest.mark.parametrize("operator", [op("median", column="y", method="linear"),
                                      op("quantile", column="y", q=0.25, method="linear"),
                                      op("spearman_correlation", x="x", y="y")])
def test_new_operators_reject_empty_complete_selection(operator):
    with pytest.raises(NotComputable, match="No complete"):
        apply_operator(pd.DataFrame({"x": [1], "y": [np.nan]}),
                       {**operator, "missing_policy": "complete_cases"})


def checked_bundle(tmp_path, kind, *, method="linear"):
    root = make_demo(tmp_path / "bundle")
    candidate = root / "candidates/initial"
    evidence = read_json(candidate / "evidence.json")
    item = evidence["items"][0]
    item.update(kind=kind)
    if kind == "spearman_correlation":
        item.update(variables=["x", "y"], unit="1", estimate=1)
        operator = op(kind, x="x", y="y")
    else:
        item["method"] = method
        operator = op(kind, column="y", method="linear")
        if kind == "quantile":
            item.update(q=0.25, estimate=4)
            operator["q"] = 0.25
    write(candidate / "evidence.json", evidence)
    plan = read_json(candidate / "source_checks.json")
    plan["checks"][0]["operator"] = operator
    write(candidate / "source_checks.json", plan)
    return root, candidate, evidence, plan


@pytest.mark.parametrize("kind,expected", [("median", 7), ("quantile", 4), ("spearman_correlation", 1)])
def test_new_kinds_bind_evidence_and_table_in_source_report(tmp_path, kind, expected):
    root, candidate, _, _ = checked_bundle(tmp_path, kind)
    record = run_source_checks(root, candidate)["checks"][0]
    assert record["value"] == pytest.approx(expected)
    assert record["difference"] == pytest.approx(0)
    assert record["generation_link_verified"] is False


@pytest.mark.parametrize("kind", ["median", "quantile"])
def test_unreported_source_method_requires_named_approximation(tmp_path, kind):
    root, candidate, _, plan = checked_bundle(tmp_path, kind, method="not_reported")
    with pytest.raises(ValueError, match="requires explicit approximation"):
        run_source_checks(root, candidate)
    plan["checks"][0].update(status="approximate", assumption_ids=["A1"],
                              reason="Source method unknown; linear sample interpolation is an explicit assumption.")
    write(candidate / "source_checks.json", plan)
    assert run_source_checks(root, candidate)["checks"][0]["status"] == "approximate"
    plan["checks"][0]["assumption_ids"] = []
    write(candidate / "source_checks.json", plan)
    with pytest.raises(ValueError, match="name its assumptions"):
        run_source_checks(root, candidate)


def test_probability_mismatch_rejected_even_with_approximation(tmp_path):
    root, candidate, _, plan = checked_bundle(tmp_path, "quantile")
    plan["checks"][0].update(status="approximate", assumption_ids=["A1"])
    plan["checks"][0]["operator"]["q"] = 0.75
    write(candidate / "source_checks.json", plan)
    with pytest.raises(ValueError, match="probability mismatch"):
        run_source_checks(root, candidate)


@pytest.mark.parametrize("mutation", ["missing_q", "bad_q", "boolean_q", "nonfinite_q", "missing_method",
                                      "unknown_method", "median_q", "mean_method", "pearson_relabel",
                                      "spearman_range", "spearman_unit"])
def test_evidence_definitions_are_strict(tmp_path, mutation):
    root, candidate, evidence, _ = checked_bundle(tmp_path, "quantile")
    item = evidence["items"][0]
    if mutation == "missing_q":
        del item["q"]
    elif mutation == "bad_q":
        item["q"] = 2
    elif mutation == "boolean_q":
        item["q"] = True
    elif mutation == "nonfinite_q":
        item["q"] = np.nan
    elif mutation == "missing_method":
        del item["method"]
    elif mutation == "unknown_method":
        item["method"] = "nearest"
    elif mutation == "median_q":
        item["kind"] = "median"
    elif mutation == "mean_method":
        item["kind"] = "mean"
        del item["q"]
    else:
        item.update(kind="spearman_correlation", variables=["x", "y"], unit="1", estimate=1)
        del item["q"], item["method"]
        if mutation == "spearman_range":
            item["estimate"] = 1.1
        elif mutation == "spearman_unit":
            item["unit"] = "%"
        else:
            write(candidate / "evidence.json", evidence)
            with pytest.raises(ValueError, match="statistic-kind mismatch"):
                run_source_checks(root, candidate)
            return
    with pytest.raises(ValueError):
        validate_evidence(evidence, read_json(root / "task.json"))


def test_legacy_reported_other_is_retained_without_reinterpretation(tmp_path):
    root, candidate, evidence, plan = checked_bundle(tmp_path, "quantile")
    item = evidence["items"][0]
    item.update(kind="reported_other", statistic_name="published quartile with different interpolation")
    del item["q"], item["method"]
    plan["checks"][0].update(status="not_computable", operator=None, table=None,
                              reason="The reported interpolation is unsupported; retain the original statistic.")
    write(candidate / "evidence.json", evidence)
    write(candidate / "source_checks.json", plan)
    assert run_source_checks(root, candidate)["checks"][0]["status"] == "not_computable"
