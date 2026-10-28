"""Strict version-1 task, evidence, model and table contracts.

Validation enforces representation and preservation, not biological correctness.
All objects are strict unless an optional field is explicitly listed. A published
evidence run requires nonempty evidence; a prior-only run has no source records
and represents its prior choices as assumptions. ``validate_evidence`` returns
the evidence-ID set used by ``validate_spec``. Other validators return None.
"""
from __future__ import annotations

import math
from numbers import Real
from typing import Any

import numpy as np
import pandas as pd


class ContractError(ValueError):
    """A declared submission contract was not satisfied."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def exact_keys(value: Any, required: set[str], optional: set[str] | None = None,
               *, where: str) -> None:
    require(isinstance(value, dict), f"{where} must be an object")
    require(all(isinstance(k, str) for k in value), f"{where} keys must be strings")
    keys = set(value)
    require(required <= keys, f"{where} missing fields: {sorted(required - keys)}")
    require(keys <= required | (optional or set()),
            f"{where} has unknown fields: {sorted(keys - required - (optional or set()))}")


def text(value: Any, where: str, *, empty: bool = False) -> None:
    require(isinstance(value, str) and (empty or bool(value.strip())),
            f"{where} must be {'a' if empty else 'a nonempty'} string")


def string_list(value: Any, where: str, *, nonempty: bool = False) -> None:
    require(isinstance(value, list), f"{where} must be a list")
    if nonempty:
        require(bool(value), f"{where} must be nonempty")
    for item in value:
        text(item, where)
    require(len(value) == len(set(value)), f"{where} has duplicate entries")


def number(value: Any, where: str) -> None:
    require(isinstance(value, Real) and not isinstance(value, (bool, np.bool_)),
            f"{where} must be a number")
    try:
        finite = math.isfinite(float(value))
    except (OverflowError, ValueError):
        finite = False
    require(finite, f"{where} must be finite")


def _integer(value: Any, where: str, *, minimum: int = 0) -> None:
    require(type(value) is int and value >= minimum,
            f"{where} must be an integer >= {minimum}")


def _json_finite(value: Any, where: str) -> None:
    """Reject non-JSON values and nonfinite numbers inside model parameters."""
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, Real):
        number(value, where)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _json_finite(item, f"{where}[{index}]")
        return
    if isinstance(value, dict):
        require(all(isinstance(k, str) for k in value), f"{where} keys must be strings")
        for key, item in value.items():
            _json_finite(item, f"{where}.{key}")
        return
    raise ContractError(f"{where} contains a non-JSON value")


def validate_task(task: dict) -> None:
    exact_keys(task, {"schema_version", "task_id", "mode", "population", "row_id",
                      "n_rows", "columns", "information_policy", "budget"}, where="task")
    require(type(task["schema_version"]) is int and task["schema_version"] == 1,
            "task.schema_version must be 1")
    for field in ("task_id", "population", "row_id"):
        text(task[field], f"task.{field}")
    require(task["mode"] in {"whole_cohort", "enrichment", "completion"}, "Invalid task mode")
    _integer(task["n_rows"], "task.n_rows", minimum=1)
    require(isinstance(task["columns"], list) and bool(task["columns"]), "task.columns must be nonempty")
    names, identifiers, generated = [], [], []
    for column in task["columns"]:
        exact_keys(column, {"name", "kind", "unit", "role", "nullable"},
                   {"minimum", "maximum", "categories"}, where="column")
        for field in ("name", "unit"):
            text(column[field], f"column.{field}", empty=field == "unit")
        require(column["kind"] in {"number", "integer", "category", "string"}, "Invalid column kind")
        require(column["role"] in {"identifier", "observed", "generated"}, "Invalid column role")
        require(type(column["nullable"]) is bool, "column.nullable must be boolean")
        names.append(column["name"])
        if column["role"] == "identifier":
            identifiers.append(column["name"])
            require(not column["nullable"], "Identifier cannot be nullable")
        if column["role"] == "generated":
            generated.append(column["name"])
            require(not column["nullable"], "Generated output columns cannot be nullable")
        for bound in ("minimum", "maximum"):
            if bound in column:
                require(column["kind"] in {"number", "integer"}, "Bounds require a numeric column")
                number(column[bound], f"column.{bound}")
        if "minimum" in column and "maximum" in column:
            require(column["minimum"] <= column["maximum"], "Column bounds reversed")
        if column["kind"] == "category":
            require(isinstance(column.get("categories"), list) and bool(column["categories"]),
                    "Category column requires categories")
            values = column["categories"]
            for value in values:
                require(isinstance(value, (str, Real)) and not isinstance(value, (bool, np.bool_)),
                        "Categories must be strings or finite numbers")
                if isinstance(value, Real):
                    number(value, "category value")
            require(all(value not in values[:i] for i, value in enumerate(values)), "Duplicate category")
        else:
            require("categories" not in column, "categories only applies to category columns")
    require(len(names) == len(set(names)), "Duplicate column names")
    require(identifiers == [task["row_id"]], "Exactly one identifier must match task.row_id")
    require(bool(generated), "At least one generated column is required")
    if task["mode"] == "whole_cohort":
        require(all(c["role"] != "observed" for c in task["columns"]),
                "Whole-cohort tasks have no observed columns")

    policy = task["information_policy"]
    exact_keys(policy, {"mode", "excluded_cohorts", "allowed_tools"}, where="information_policy")
    require(policy["mode"] in {"published_evidence", "prior_only"}, "Invalid information mode")
    string_list(policy["excluded_cohorts"], "excluded_cohorts")
    string_list(policy["allowed_tools"], "allowed_tools")
    exact_keys(task["budget"], {"source_queries", "source_downloads", "revisions"}, where="budget")
    for key, value in task["budget"].items():
        _integer(value, f"budget.{key}")


def _table(frame: pd.DataFrame, columns: list[dict], task: dict,
           *, completion_input: bool = False) -> None:
    require(isinstance(frame, pd.DataFrame), "Expected a pandas DataFrame")
    expected = [c["name"] for c in columns]
    require(list(frame.columns) == expected, "Table columns/order do not match contract")
    require(len(frame) == task["n_rows"], "Table row count does not match task")
    for column in columns:
        series = frame[column["name"]]
        nulls = series.isna()
        allow_null = column["nullable"] or (completion_input and column["role"] == "generated")
        require(allow_null or not bool(nulls.any()), f"Null values not allowed in {column['name']}")
        values = series[~nulls].tolist()
        if column["kind"] in {"number", "integer"}:
            for value in values:
                number(value, column["name"])
                if column["kind"] == "integer":
                    require(float(value).is_integer(), f"Noninteger value in {column['name']}")
                if "minimum" in column:
                    require(value >= column["minimum"], f"Value below minimum in {column['name']}")
                if "maximum" in column:
                    require(value <= column["maximum"], f"Value above maximum in {column['name']}")
        elif column["kind"] == "string":
            require(all(isinstance(value, str) for value in values), f"Nonstring value in {column['name']}")
        else:
            require(all(not isinstance(value, (bool, np.bool_)) and value in column["categories"]
                        for value in values), f"Unknown category in {column['name']}")
        if column["role"] == "identifier":
            require(series.notna().all() and series.is_unique, "Identifiers must be unique and nonmissing")


def validate_input(frame_or_none: pd.DataFrame | None, task: dict) -> None:
    validate_task(task)
    if task["mode"] == "whole_cohort":
        require(frame_or_none is None, "Whole-cohort input must be None")
        return
    columns = task["columns"]
    if task["mode"] == "enrichment":
        columns = [c for c in columns if c["role"] != "generated"]
    _table(frame_or_none, columns, task, completion_input=task["mode"] == "completion")


def validate_output(input_frame: pd.DataFrame | None, output: pd.DataFrame, task: dict) -> None:
    validate_input(input_frame, task)
    _table(output, task["columns"], task)
    if input_frame is None:
        return
    for column in task["columns"]:
        name = column["name"]
        if name not in input_frame.columns:
            continue
        original = input_frame[name].reset_index(drop=True)
        generated = output[name].reset_index(drop=True)
        if task["mode"] == "completion" and column["role"] == "generated":
            measured = original.notna()
            original, generated = original[measured], generated[measured]
        try:
            pd.testing.assert_series_equal(original, generated, check_dtype=False, check_exact=True,
                                           check_names=False)
        except AssertionError as error:
            raise ContractError(f"Observed cells or row order changed: {name}") from error


def _uncertainty(value: dict) -> None:
    exact_keys(value, {"kind"}, {"value", "low", "high", "level"}, where="uncertainty")
    kind = value["kind"]
    require(kind in {"se", "sd", "ci", "not_reported"}, "Invalid uncertainty kind")
    if kind in {"se", "sd"}:
        require(set(value) == {"kind", "value"}, "SE/SD requires only value")
        number(value["value"], "uncertainty.value")
        require(value["value"] >= 0, "Uncertainty spread cannot be negative")
    elif kind == "ci":
        require(set(value) == {"kind", "low", "high", "level"}, "CI requires low, high and level")
        for key in ("low", "high", "level"):
            number(value[key], f"uncertainty.{key}")
        require(value["low"] <= value["high"], "CI bounds reversed")
        require(0 < value["level"] < 1, "CI level must be between zero and one")
    else:
        require(set(value) == {"kind"}, "not_reported uncertainty has no numeric fields")


def validate_evidence(evidence: dict, task: dict) -> set[str]:
    validate_task(task)
    exact_keys(evidence, {"schema_version", "sources", "items"}, where="evidence")
    require(type(evidence["schema_version"]) is int and evidence["schema_version"] == 1,
            "evidence.schema_version must be 1")
    require(isinstance(evidence["sources"], list) and isinstance(evidence["items"], list),
            "Evidence sources and items must be lists")
    if task["information_policy"]["mode"] == "prior_only":
        require(not evidence["sources"] and not evidence["items"],
                "prior_only records no retrieved evidence; declare assumptions in the model specification")
        return set()
    require(bool(evidence["sources"]) and bool(evidence["items"]), "Published evidence must be nonempty")
    excluded = {x.strip().casefold() for x in task["information_policy"]["excluded_cohorts"]}
    source_ids = set()
    for source in evidence["sources"]:
        exact_keys(source, {"id", "identifier", "population", "measurement", "cohort_ids", "artifacts"},
                   where="source")
        for field in ("id", "identifier", "population", "measurement"):
            text(source[field], f"source.{field}")
        require(source["id"] not in source_ids, "Duplicate source ID")
        source_ids.add(source["id"])
        string_list(source["cohort_ids"], "source.cohort_ids")
        require(not ({x.strip().casefold() for x in source["cohort_ids"]} & excluded),
                "Source declares an excluded cohort")
        require(isinstance(source["artifacts"], list) and bool(source["artifacts"]),
                "Source artifacts must be nonempty")
        paths = []
        for artifact in source["artifacts"]:
            exact_keys(artifact, {"path", "sha256"}, where="source artifact")
            text(artifact["path"], "artifact.path")
            _hash(artifact["sha256"])
            paths.append(artifact["path"])
        require(len(paths) == len(set(paths)), "Duplicate source artifact path")
    item_ids = set()
    for item in evidence["items"]:
        exact_keys(item, {"id", "source_id", "locator", "variables", "kind", "estimate", "unit",
                          "uncertainty", "adjustment", "selection", "applicability"},
                   {"statistic_name"}, where="evidence item")
        for field in ("id", "source_id", "locator", "selection", "applicability"):
            text(item[field], f"item.{field}")
        text(item["unit"], "item.unit", empty=True)
        require(item["id"] not in item_ids, "Duplicate evidence ID")
        item_ids.add(item["id"])
        require(item["source_id"] in source_ids, "Unknown evidence source")
        require(item["kind"] in {"mean", "sd", "correlation", "ols_coefficient", "proportion", "contextual", "reported_other"},
                "Invalid evidence kind")
        if item["kind"] == "reported_other":
            require("statistic_name" in item, "reported_other requires statistic_name")
            text(item["statistic_name"], "item.statistic_name")
        else:
            require("statistic_name" not in item, "statistic_name only applies to reported_other")
        string_list(item["variables"], "item.variables", nonempty=item["kind"] != "contextual")
        string_list(item["adjustment"], "item.adjustment")
        if item["kind"] == "contextual":
            require(item["estimate"] is None, "Contextual evidence has no numeric estimate")
        else:
            number(item["estimate"], "item.estimate")
            if item["kind"] == "sd":
                require(item["estimate"] >= 0, "SD cannot be negative")
            if item["kind"] == "correlation":
                require(-1 <= item["estimate"] <= 1, "Correlation outside [-1,1]")
            if item["kind"] == "proportion":
                require(item["unit"] in {"1", "%"}, "Proportion unit must be '1' or '%'")
                maximum = 1 if item["unit"] == "1" else 100
                require(0 <= item["estimate"] <= maximum, "Proportion outside its declared unit range")
        _uncertainty(item["uncertainty"])
        if item["kind"] == "contextual":
            require(item["uncertainty"]["kind"] == "not_reported", "Contextual uncertainty must be not_reported")
    return item_ids


def _hash(value: Any) -> None:
    import re
    require(isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None,
            "SHA256 must be 64 lowercase hexadecimal characters")


def validate_spec(spec: dict, evidence_ids: set[str]) -> None:
    exact_keys(spec, {"parameters", "assumptions", "parameter_provenance"}, where="model_spec")
    require(isinstance(spec["parameters"], dict), "parameters must be an object")
    _json_finite(spec["parameters"], "parameters")
    provenance = spec["parameter_provenance"]
    require(isinstance(provenance, dict) and set(provenance) == set(spec["parameters"]),
            "Parameter provenance keys must exactly match parameters")
    require(isinstance(spec["assumptions"], list), "assumptions must be a list")
    assumptions = set()
    for assumption in spec["assumptions"]:
        exact_keys(assumption, {"id", "description"}, where="assumption")
        text(assumption["id"], "assumption.id")
        text(assumption["description"], "assumption.description")
        require(assumption["id"] not in assumptions, "Duplicate assumption ID")
        assumptions.add(assumption["id"])
    for parameter, entry in provenance.items():
        text(parameter, "parameter key")
        exact_keys(entry, {"evidence_ids", "assumption_ids", "derivation"}, where="parameter provenance")
        string_list(entry["evidence_ids"], "parameter evidence IDs")
        string_list(entry["assumption_ids"], "parameter assumption IDs")
        text(entry["derivation"], "parameter derivation")
        require(bool(entry["evidence_ids"] or entry["assumption_ids"]), "Parameter lacks evidence or assumption")
        require(set(entry["evidence_ids"]) <= evidence_ids, "Unknown parameter evidence reference")
        require(set(entry["assumption_ids"]) <= assumptions, "Unknown parameter assumption reference")
