"""Pure K02 generated-release guard; no row filtering, repair, file I/O or runs.

The caller must first authenticate the execution and frozen task. This function
validates the supplied frame against that supplied task, not its provenance.
"""
from __future__ import annotations

import hashlib
import json

import pandas as pd

from cohort_harness import contracts


_COLUMNS = (
    ("id", "string", "1", "identifier"),
    ("age", "number", "year", "generated"),
    ("sex", "category", "1", "generated"),
    ("bmi", "number", "kg/m^2", "generated"),
    ("total_cholesterol", "number", "mmol/L", "generated"),
    ("hdl_cholesterol", "number", "mmol/L", "generated"),
)
_POSITIVE = ("bmi", "total_cholesterol", "hdl_cholesterol")


def _digest(value):
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _scalar(value):
    return value.item() if hasattr(value, "item") else value


def validate_generated_release(frame: pd.DataFrame, task: dict) -> dict:
    """Return a validity commitment or raise contracts.ContractError.

    Every supplied row must pass. The row count is exactly task.n_rows; the
    production caller must bind the approved 5,000-row task, not substitute a
    smaller task after filtering. Small invented tests may supply smaller tasks.
    Frame and task are never mutated; no numeric summary or row data is emitted.
    """
    contracts.validate_task(task)
    contracts.require(task["mode"] == "whole_cohort" and task["row_id"] == "id", "K02 requires whole-cohort rows with id")
    columns = task["columns"]
    contracts.require(len(columns) == len(_COLUMNS), "K02 requires exactly six ordered columns")
    for column, (name, kind, unit, role) in zip(columns, _COLUMNS):
        contracts.require(all(column[key] == value for key, value in {
            "name": name, "kind": kind, "unit": unit, "role": role, "nullable": False}.items()),
            "K02 canonical column contract mismatch: " + name)
    contracts.require(columns[2]["categories"] == ["F", "M"], "K02 requires literal F/M categories in the canonical order")
    # Existing validation rejects missing/nonfinite/bool/non-numeric values,
    # duplicate identifiers, wrong row counts and extra/reordered columns.
    contracts.validate_output(None, frame, task)
    contracts.require(all(bool(value.strip()) for value in frame["id"].tolist()), "Identifier must not be empty or whitespace")
    contracts.require(bool((frame["age"] >= 18).all()), "Every generated age must be at least 18")
    for name in _POSITIVE:
        contracts.require(bool((frame[name] > 0).all()), "Every generated value must be strictly positive: " + name)

    content = {"columns": list(frame.columns), "rows": [[_scalar(value) for value in row] for row in frame.itertuples(index=False, name=None)]}
    return {
        "schema_version": 1, "kind": "k02_generated_release_validity_v1", "status": "valid",
        "task_contract_sha256": _digest(task), "frame_content_sha256": _digest(content),
        "digest_scope": "canonical_finite_JSON_task_and_ordered_column_row_values_not_CSV_bytes_or_dataframe_index",
        "required_rows": task["n_rows"], "validated_rows": len(frame), "all_required_rows_valid": True,
        "ordered_columns": list(frame.columns), "unique_nonempty_identifiers": True,
        "finite_age_at_least_18": True, "literal_sex_categories": ["F", "M"],
        "strictly_positive_columns": list(_POSITIVE), "missing_values": 0,
        "rows_filtered": 0, "rows_repaired": 0, "inputs_mutated": False,
        "execution_authenticated": False, "approved_task_authenticated": False,
        "scientific_validity": "not_assessed", "case_or_global_release_authorized": False,
    }
