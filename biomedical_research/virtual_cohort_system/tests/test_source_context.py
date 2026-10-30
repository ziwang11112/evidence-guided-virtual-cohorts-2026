"""Invented source/domain fixtures; no participant data or execution backend."""
from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import pytest

from cohort_harness.contracts import ContractError, validate_input, validate_output
from cohort_harness.source_context import compile_source_task


def fixture():
    columns = [
        {"name": "row_id", "kind": "string", "unit": "", "role": "identifier", "nullable": False},
        {"name": "x", "kind": "number", "unit": "u", "role": "observed", "nullable": False,
         "minimum": 0, "maximum": 6},
        {"name": "group", "kind": "category", "unit": "", "role": "observed", "nullable": False,
         "categories": ["a", "b"]},
        {"name": "y", "kind": "number", "unit": "v", "role": "generated", "nullable": False,
         "minimum": 0, "maximum": 6},
    ]
    target = {
        "schema_version": 1, "task_id": "invented_source_compiler", "mode": "enrichment",
        "population": "Target x support zero through six", "row_id": "row_id", "n_rows": 2,
        "columns": columns,
        "information_policy": {"mode": "published_evidence", "excluded_cohorts": ["reserved"],
                               "allowed_tools": ["source_replay"]},
        "budget": {"source_queries": 1, "source_downloads": 2, "revisions": 3},
    }
    source_columns = copy.deepcopy(columns)
    source_columns[1]["maximum"] = source_columns[3]["maximum"] = 10
    domain_columns = copy.deepcopy(columns)
    domain_columns[1]["maximum"] = domain_columns[3]["maximum"] = 12
    domain_columns[2]["categories"] = ["a", "b", "c"]
    context = {
        "id": "source", "population": "Independent source support zero through ten",
        "reason": "Invented compiler test", "assumption_ids": ["source_support"],
        "measurement": {"mode": "identity", "description": "Same invented units and category labels"},
        "input": {"path": "invented.csv", "sha256": "0" * 64, "origin": "declared_source_covariates"},
        "checks": [], "columns": source_columns,
    }
    domain = {"columns": domain_columns, "assumption_ids": ["computation"],
              "description": "Declared computational support zero through twelve"}
    frame = pd.DataFrame({"row_id": ["s0", "s1", "s2"], "x": [0., 9., 10.], "group": ["a", "b", "a"]})
    return target, context, domain, frame


def compile_fixture(target, context, domain, frame):
    return compile_source_task(target, context, domain, frame,
                               assumption_ids={"source_support", "computation"})


def test_source_outside_target_is_accepted_without_mutating_or_widening_target():
    target, context, domain, frame = fixture()
    snapshots = copy.deepcopy((target, context, domain))
    original_frame = frame.copy(deep=True)
    source = compile_fixture(target, context, domain, frame)
    assert source["population"] == context["population"]
    assert source["n_rows"] == len(frame) == 3
    assert source["columns"] == context["columns"]
    assert {k: v for k, v in source.items() if k not in {"population", "n_rows", "columns"}} == {
        k: v for k, v in target.items() if k not in {"population", "n_rows", "columns"}}
    target_same_count = copy.deepcopy(target)
    target_same_count["n_rows"] = len(frame)
    with pytest.raises(ContractError, match="above maximum in x"):
        validate_input(frame, target_same_count)
    assert (target, context, domain) == snapshots
    pd.testing.assert_frame_equal(frame, original_frame)
    # The returned execution task is detached, including nested policy/budget.
    source["columns"][1]["maximum"] = 999
    source["information_policy"]["excluded_cohorts"].append("other")
    source["budget"]["revisions"] = 999
    assert (target, context, domain) == snapshots


def test_source_and_target_supports_can_be_disjoint_inside_model_domain():
    target, context, domain, frame = fixture()
    context["columns"][1]["minimum"] = 8
    frame["x"] = [8., 9., 10.]
    source = compile_fixture(target, context, domain, frame)
    validate_input(frame, source)


@pytest.mark.parametrize("which,column,bound,value", [
    ("source", "x", "maximum", 13), ("target", "x", "maximum", 13),
    ("source", "x", "minimum", -1), ("target", "x", "minimum", -1),
    ("source", "y", "maximum", 13), ("target", "y", "minimum", -1),
])
def test_declared_support_must_fit_domain_even_when_rows_fit(which, column, bound, value):
    target, context, domain, frame = fixture()
    schemas = target["columns"] if which == "target" else context["columns"]
    next(c for c in schemas if c["name"] == column)[bound] = value
    with pytest.raises(ContractError, match="outside the model domain"):
        compile_fixture(target, context, domain, frame)


@pytest.mark.parametrize("which,column,bound", [
    ("source", "x", "minimum"), ("source", "x", "maximum"),
    ("target", "x", "minimum"), ("target", "x", "maximum"),
    ("source", "y", "maximum"), ("target", "y", "minimum"),
])
def test_missing_declared_bound_cannot_imply_finite_domain(which, column, bound):
    target, context, domain, frame = fixture()
    schemas = target["columns"] if which == "target" else context["columns"]
    del next(c for c in schemas if c["name"] == column)[bound]
    with pytest.raises(ContractError, match="needs a declared"):
        compile_fixture(target, context, domain, frame)


def test_unbounded_model_dimension_allows_missing_source_and_target_bounds():
    target, context, domain, frame = fixture()
    for schemas in [target["columns"], context["columns"], domain["columns"]]:
        schemas[1].pop("minimum")
        schemas[1].pop("maximum")
    frame["x"] = [-100., 9., 100.]
    compile_fixture(target, context, domain, frame)


@pytest.mark.parametrize("which,field,value", [
    ("source", "unit", "different"), ("domain", "unit", "different"),
    ("source", "kind", "integer"), ("domain", "kind", "integer"),
    ("source", "role", "generated"), ("domain", "role", "generated"),
    ("source", "nullable", True), ("domain", "nullable", True),
    ("source", "name", "renamed"), ("domain", "name", "renamed"),
])
def test_column_identity_must_match_target(which, field, value):
    target, context, domain, frame = fixture()
    schemas = context["columns"] if which == "source" else domain["columns"]
    schemas[1][field] = value
    with pytest.raises(ContractError, match="changes|ordered column names"):
        compile_fixture(target, context, domain, frame)


@pytest.mark.parametrize("which", ["source", "domain"])
def test_column_order_must_match_target(which):
    target, context, domain, frame = fixture()
    schemas = context["columns"] if which == "source" else domain["columns"]
    schemas[1], schemas[2] = schemas[2], schemas[1]
    with pytest.raises(ContractError, match="ordered column names"):
        compile_fixture(target, context, domain, frame)


def test_source_output_bounds_are_independent_and_enforced_by_existing_output_validator():
    target, context, domain, frame = fixture()
    frame["x"] = [1., 2., 3.]
    source = compile_fixture(target, context, domain, frame)
    generated = frame.assign(y=[9., 10., 9.5])
    validate_output(frame, generated, source)
    target_same_count = copy.deepcopy(target)
    target_same_count["n_rows"] = len(frame)
    with pytest.raises(ContractError, match="above maximum in y"):
        validate_output(frame, generated, target_same_count)
    with pytest.raises(ContractError, match="above maximum in y"):
        validate_output(frame, generated.assign(y=11.), source)


@pytest.mark.parametrize("change", ["outcome", "extra", "missing", "reordered", "duplicate_ids", "empty"])
def test_source_covariate_frame_contract(change):
    target, context, domain, frame = fixture()
    if change == "outcome":
        frame["y"] = np.nan  # Even an empty outcome column is forbidden.
    elif change == "extra":
        frame["auxiliary"] = 1
    elif change == "missing":
        frame = frame.drop(columns="group")
    elif change == "reordered":
        frame = frame[["x", "row_id", "group"]]
    elif change == "duplicate_ids":
        frame["row_id"] = "duplicate"
    else:
        frame = frame.iloc[:0]
    with pytest.raises(ContractError):
        compile_fixture(target, context, domain, frame)


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf, -0.01, 10.01])
def test_invalid_nonnullable_source_values_are_rejected_without_clipping(value):
    target, context, domain, frame = fixture()
    frame.loc[1, "x"] = value
    before = frame.copy(deep=True)
    with pytest.raises(ContractError):
        compile_fixture(target, context, domain, frame)
    pd.testing.assert_frame_equal(frame, before)


def test_nullable_missing_value_is_preserved_but_infinity_is_not_missing():
    target, context, domain, frame = fixture()
    for schemas in [target["columns"], context["columns"], domain["columns"]]:
        schemas[1]["nullable"] = True
    frame.loc[1, "x"] = np.nan
    compile_fixture(target, context, domain, frame)
    assert pd.isna(frame.loc[1, "x"])
    frame.loc[1, "x"] = np.inf
    with pytest.raises(ContractError, match="finite"):
        compile_fixture(target, context, domain, frame)


def test_domain_edges_are_inclusive_and_no_rows_are_dropped():
    target, context, domain, frame = fixture()
    context["columns"][1]["maximum"] = 12
    frame["x"] = [0., 6., 12.]
    source = compile_fixture(target, context, domain, frame)
    assert source["n_rows"] == 3
    assert frame.x.tolist() == [0., 6., 12.]


def test_category_supports_can_differ_and_category_order_is_not_identity():
    target, context, domain, frame = fixture()
    context["columns"][2]["categories"] = ["c", "b"]
    domain["columns"][2]["categories"] = ["c", "b", "a"]
    frame["group"] = ["c", "b", "c"]
    source = compile_fixture(target, context, domain, frame)
    assert source["columns"][2]["categories"] == ["c", "b"]


@pytest.mark.parametrize("which", ["source", "target"])
def test_declared_categories_must_fit_domain(which):
    target, context, domain, frame = fixture()
    schemas = context["columns"] if which == "source" else target["columns"]
    schemas[2]["categories"].append("outside")
    with pytest.raises(ContractError, match="categories are outside"):
        compile_fixture(target, context, domain, frame)


def test_source_value_must_fit_source_categories_even_if_in_model_domain():
    target, context, domain, frame = fixture()
    frame.loc[1, "group"] = "c"
    with pytest.raises(ContractError, match="Unknown category"):
        compile_fixture(target, context, domain, frame)


@pytest.mark.parametrize("change", ["domain_extra", "domain_description", "domain_unknown_assumption",
                                     "source_unknown_assumption", "duplicate_assumption", "measurement",
                                     "measurement_extra", "unknown_column_field", "reversed_bounds", "infinite_bound"])
def test_strict_metadata_and_existing_schema_validation(change):
    target, context, domain, frame = fixture()
    if change == "domain_extra":
        domain["hidden_override"] = True
    elif change == "domain_description":
        domain["description"] = " "
    elif change == "domain_unknown_assumption":
        domain["assumption_ids"] = ["unknown"]
    elif change == "source_unknown_assumption":
        context["assumption_ids"] = ["unknown"]
    elif change == "duplicate_assumption":
        context["assumption_ids"] *= 2
    elif change == "measurement":
        context["measurement"]["mode"] = "convert_units"
    elif change == "measurement_extra":
        context["measurement"]["factor"] = 2
    elif change == "unknown_column_field":
        context["columns"][1]["transform"] = "log"
    elif change == "reversed_bounds":
        domain["columns"][1]["minimum"] = 13
    else:
        domain["columns"][1]["maximum"] = np.inf
    with pytest.raises(ContractError):
        compile_fixture(target, context, domain, frame)


@pytest.mark.parametrize("mode", ["completion", "whole_cohort"])
def test_non_enrichment_modes_are_rejected(mode):
    target, context, domain, frame = fixture()
    target["mode"] = mode
    if mode == "whole_cohort":
        for column in target["columns"]:
            if column["role"] == "observed":
                column["role"] = "generated"
    with pytest.raises(ContractError, match="enrichment tasks only"):
        compile_fixture(target, context, domain, frame)
