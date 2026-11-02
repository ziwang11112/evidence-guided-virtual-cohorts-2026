"""Reviewed, explicit multiplicative units on an in-memory frame; no file I/O.

This adapter does not verify executions, fit data, or certify scientific source
claims. Review metadata and caller bindings are procedural commitments only.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from numbers import Integral, Real
from typing import Any

import numpy as np
import pandas as pd


JsonObject = dict[str, Any]
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def _exact(value: Any, fields: set[str]) -> None:
    _require(type(value) is dict and set(value) == fields, "Unexpected/missing fields")


def _text(value: Any) -> None:
    _require(type(value) is str and bool(value.strip()), "Nonempty string required")


def _finite(value: Any) -> bool:
    if not isinstance(value, Real) or isinstance(value, (bool, np.bool_)):
        return False
    try:
        return math.isfinite(float(value))
    except (OverflowError, ValueError):
        return False


def _json(value: Any) -> str:
    """Strict typed JSON: booleans never compare equal to integer commitments."""
    def check(item: Any) -> None:
        if item is None or type(item) in {str, bool, int}:
            return
        if type(item) is float:
            _require(math.isfinite(item), "Nonfinite JSON value")
            return
        if type(item) is list:
            for child in item:
                check(child)
            return
        if type(item) is dict:
            _require(all(type(key) is str for key in item), "JSON keys must be strings")
            for child in item.values():
                check(child)
            return
        raise ValueError("Only finite JSON values are supported")

    check(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _hash(value: Any) -> None:
    _require(type(value) is str and _SHA256.fullmatch(value) is not None, "Lowercase SHA256 required")


def _cell(value: Any) -> list[Any]:
    # Float hex preserves the exact in-memory value, including signed zero.
    if isinstance(value, (bool, np.bool_)):
        raise ValueError("Boolean frame cells are unsupported")
    if isinstance(value, Integral):
        return ["integer", str(int(value))]
    if isinstance(value, Real):
        _require(_finite(value), "Nonfinite/missing frame value")
        return ["float", float(value).hex()]
    _require(type(value) is str, "Only finite numbers and strings are supported; no missing values")
    return ["string", value]


def frame_digest(frame: pd.DataFrame) -> str:
    """Bind all values, column/row order, index, and pandas dtype names.

    This is a typed in-memory content digest, not a CSV byte hash. DataFrame
    attrs and unobserved categorical levels are not part of this commitment.
    """
    _require(isinstance(frame, pd.DataFrame), "DataFrame required")
    _require(frame.columns.is_unique and not isinstance(frame.index, pd.MultiIndex),
             "Duplicate columns/MultiIndex are unsupported")
    _require(all(type(name) is str and name.strip() for name in frame.columns), "Named string columns required")
    _require(frame.index.name is None or type(frame.index.name) is str, "Index name must be string or null")
    return _digest({
        "columns": list(frame.columns), "dtypes": [str(dtype) for dtype in frame.dtypes],
        "index_name": frame.index.name, "index_dtype": str(frame.index.dtype),
        "index": [_cell(value) for value in frame.index],
        "rows": [[_cell(value) for value in row] for row in frame.itertuples(index=False, name=None)],
    })


def _validate_contract(contract: JsonObject) -> None:
    _exact(contract, {"row_id", "columns"})
    _text(contract["row_id"])
    _require(type(contract["columns"]) is list and bool(contract["columns"]), "Explicit columns required")
    names = []
    for column in contract["columns"]:
        _exact(column, {"name", "kind", "role", "analyte_id", "unit", "scale"})
        for value in column.values():
            _text(value)
        _require(column["kind"] in {"number", "integer", "string", "category"}, "Unsupported column kind")
        expected_scale = "original" if column["kind"] in {"number", "integer"} else "categorical"
        _require(column["scale"] == expected_scale, "Only original numeric/categorical scales are supported")
        names.append(column["name"])
    _require(len(names) == len(set(names)) and contract["row_id"] in names, "Duplicate columns/missing row ID")
    identifiers = [c["name"] for c in contract["columns"] if c["role"] == "identifier"]
    _require(identifiers == [contract["row_id"]], "Exactly the declared row ID must have identifier role")


def contract_digest(contract: JsonObject) -> str:
    _validate_contract(contract)
    return _digest(contract)


def manifest_digest(manifest: JsonObject) -> str:
    """Hash the proposal without review; this helper does not approve it."""
    _require(type(manifest) is dict, "Manifest object required")
    return _digest({key: value for key, value in manifest.items() if key != "review"})


def validate_manifest(manifest: JsonObject, input_contract: JsonObject, output_contract: JsonObject) -> None:
    """Validate exhaustive mappings, exact declared semantics and review hash."""
    _exact(manifest, {"schema_version", "purpose", "input_contract_sha256", "output_contract_sha256", "columns", "review"})
    _require(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1, "Unsupported schema version")
    _require(manifest["purpose"] in {"target_analysis_unit_conversion", "analytic_fixture"}, "Unsupported purpose")
    _require(manifest["input_contract_sha256"] == contract_digest(input_contract), "Input contract hash mismatch")
    _require(manifest["output_contract_sha256"] == contract_digest(output_contract), "Output contract hash mismatch")
    _require(input_contract["row_id"] == output_contract["row_id"], "Row ID cannot change")
    inputs, outputs = input_contract["columns"], output_contract["columns"]
    _require([c["name"] for c in inputs] == [c["name"] for c in outputs], "Column renaming/reordering/derivation is unsupported")
    mappings = manifest["columns"]
    _require(type(mappings) is list and len(mappings) == len(inputs), "Every column requires one explicit mapping")
    for original, result, mapping in zip(inputs, outputs, mappings):
        _exact(mapping, {"column", "operation", "factor", "source"})
        _require(mapping["column"] == original["name"], "Mapping must match each column in contract order")
        _require({k: v for k, v in original.items() if k != "unit"} ==
                 {k: v for k, v in result.items() if k != "unit"}, "Kind/role/analyte/scale may not change")
        factor = mapping["factor"]
        _require(type(factor) in {int, float} and _finite(factor) and factor > 0, "Finite positive nonboolean factor required")
        _require(type(factor) is not int or int(float(factor)) == factor, "Integer factor loses precision in float arithmetic")
        if mapping["operation"] == "identity":
            _require(factor == 1 and original["unit"] == result["unit"] and mapping["source"] is None,
                     "Identity cannot relabel units or change values")
        else:
            _require(mapping["operation"] == "multiply", "Only identity and multiplication are supported")
            _require(original["kind"] == "number" and original["role"] != "identifier",
                     "Multiplication requires a nonidentifier number column")
            _require(original["unit"] != result["unit"] and factor != 1,
                     "Nonidentity conversion requires differing units and a nonunit factor")
            source = mapping["source"]
            _exact(source, {"kind", "reference", "locator", "analyte_id", "input_unit", "output_unit"})
            for value in source.values():
                _text(value)
            _require(source["kind"] in {"official_unit_documentation", "invented_fixture"}, "Unsupported factor provenance")
            _require(source["kind"] != "invented_fixture" or manifest["purpose"] == "analytic_fixture",
                     "Invented conversion factors are fixture-only")
            _require(source["analyte_id"] == original["analyte_id"] and
                     source["input_unit"] == original["unit"] and source["output_unit"] == result["unit"],
                     "Conversion source analyte/unit direction mismatch")
    review = manifest["review"]
    _exact(review, {"decision", "independent", "reviewer_id", "producer_id", "reviewed_utc", "reason", "approved_sha256"})
    _require(review["decision"] == "approved" and review["independent"] is True, "Independent approval required")
    for key in {"reviewer_id", "producer_id", "reviewed_utc", "reason"}:
        _text(review[key])
    _require(review["reviewer_id"].strip().casefold() != review["producer_id"].strip().casefold(),
             "Reviewer and producer must differ")
    _hash(review["approved_sha256"])
    _require(review["approved_sha256"] == manifest_digest(manifest), "Review does not bind this manifest")
    _json(manifest)


def _validate_frame(frame: pd.DataFrame, contract: JsonObject) -> None:
    _require(list(frame.columns) == [c["name"] for c in contract["columns"]], "Frame has unmapped/missing/reordered columns")
    for descriptor in contract["columns"]:
        series = frame[descriptor["name"]]
        if descriptor["kind"] in {"number", "integer"}:
            _require(pd.api.types.is_numeric_dtype(series.dtype) and not pd.api.types.is_bool_dtype(series.dtype),
                     "Numeric dtype required; no implicit coercion")
            _require(all(_finite(value) for value in series), "Nonfinite/missing numeric values")
            if descriptor["kind"] == "integer":
                _require(all(float(value).is_integer() for value in series), "Integer column contains fractions")
        else:
            _require(all(type(value) is str for value in series), "String/category values must be strings")
    ids = frame[contract["row_id"]]
    _require(ids.is_unique and all(not isinstance(value, str) or bool(value.strip()) for value in ids),
             "Row IDs must be unique/nonempty")


def convert_frame(
    frame: pd.DataFrame, manifest: JsonObject, *, input_contract: JsonObject,
    output_contract: JsonObject, expected_input_sha256: str, caller_binding: JsonObject,
) -> tuple[pd.DataFrame, JsonObject]:
    """Return an independently allocated converted frame and content receipt.

    Caller must verify lifecycle/byte hashes itself before use. No execution is
    performed or authenticated here. All columns, rows, identifiers and index
    are preserved; only explicitly mapped numeric values change.
    """
    validate_manifest(manifest, input_contract, output_contract)
    _hash(expected_input_sha256)
    _require(type(caller_binding) is dict and bool(caller_binding), "Nonempty caller binding required")
    binding = json.loads(_json(caller_binding))
    observed_hash = frame_digest(frame)
    _require(observed_hash == expected_input_sha256, "Input frame hash mismatch")
    _validate_frame(frame, input_contract)
    converted = frame.copy(deep=True)
    for mapping in manifest["columns"]:
        if mapping["operation"] == "multiply":
            column = mapping["column"]
            # Explicit float arithmetic avoids silent integer overflow; reject
            # nonfinite output and underflow-to-zero instead of losing values.
            _require(all(not isinstance(value, Integral) or int(float(value)) == int(value) for value in frame[column]),
                     "Integer numeric value loses precision in float arithmetic")
            with np.errstate(over="ignore", under="ignore", invalid="ignore"):
                before = frame[column].to_numpy(dtype=float)
                after = before * float(mapping["factor"])
            _require(np.isfinite(after).all() and not np.any((before != 0) & (after == 0)),
                     "Conversion overflow/underflow or nonfinite output")
            converted[column] = after
    _validate_frame(converted, output_contract)
    return converted, {
        "schema_version": 1, "kind": "multiplicative_unit_frame_receipt_v1",
        "input_frame_sha256": observed_hash, "output_frame_sha256": frame_digest(converted),
        "input_contract_sha256": contract_digest(input_contract),
        "output_contract_sha256": contract_digest(output_contract),
        "manifest_sha256": _digest(manifest), "reviewed_proposal_sha256": manifest_digest(manifest),
        "caller_binding": binding, "caller_binding_sha256": _digest(binding),
        "execution_binding_status": "caller_asserted_not_verified_by_unit_adapter",
        "rows": len(frame), "new_scientific_generation": False,
    }
