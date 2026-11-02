"""Pure K01 context-aware whole-frame guard. No filtering, file I/O or runs."""
from __future__ import annotations

import hashlib
import json
import pandas as pd
from cohort_harness import contracts

CONTEXTS = {
    "target_haalsi_pooled_poc": {
        "population": "HAALSI target pooled cleaned capillary point-of-care glucose context; adults age >=40 years, no upper age limit; whole-cohort synthesis.",
        "age_minimum": 40, "age_maximum": None},
    "source_mind_china_2019": {
        "population": "MIND-China 2019 source context; selected rural Chinese adults age 61–80 years inclusive; whole-cohort synthesis.",
        "age_minimum": 61, "age_maximum": 80},
    "source_ayele_dire_dawa_2017": {
        "population": "Ayele Dire Dawa 2017 source context; urban Ethiopian adults age 25–64 years inclusive by Methods; whole-cohort synthesis.",
        "age_minimum": 25, "age_maximum": 64},
}
COLUMNS = (
    ("id", "string", "1", "identifier"), ("age", "number", "year", "generated"),
    ("sex", "category", "1", "generated"), ("bmi", "number", "kg/m^2", "generated"),
    ("glucose", "number", "mmol/L", "generated"),
)


def _digest(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(data.encode()).hexdigest()


def _scalar(value):
    return value.item() if hasattr(value, "item") else value


def validate_generated_context(frame: pd.DataFrame, task: dict, *, context_id: str) -> dict:
    """Validate exact supplied task/context tuple and ALL output rows.

    Caller must derive context_id from an authenticated frozen execution, not
    choose it after seeing rows, and bind the approved task/5000-row request.
    This function proves consistency of its inputs, not their provenance.
    """
    contracts.require(type(context_id) is str and context_id in CONTEXTS, "Unknown K01 context")
    contracts.validate_task(task)
    context = CONTEXTS[context_id]
    contracts.require(task["population"] == context["population"], "Context/task population mismatch")
    contracts.require(task["mode"] == "whole_cohort" and task["row_id"] == "id", "K01 requires whole cohort id rows")
    columns = task["columns"]
    contracts.require(len(columns) == len(COLUMNS), "K01 requires exactly five ordered columns")
    for col, (name, kind, unit, role) in zip(columns, COLUMNS):
        expected = {"name": name, "kind": kind, "unit": unit, "role": role, "nullable": False}
        if name == "sex":
            expected["categories"] = ["F", "M"]
        contracts.require(col == expected, "K01 canonical column mismatch: " + name)
    contracts.validate_output(None, frame, task)
    contracts.require(all(bool(value.strip()) for value in frame["id"].tolist()), "Identifier must not be whitespace")
    contracts.require(bool((frame["age"] >= context["age_minimum"]).all()), "Context age minimum violated")
    if context["age_maximum"] is not None:
        contracts.require(bool((frame["age"] <= context["age_maximum"]).all()), "Context age maximum violated")
    for name in ("bmi", "glucose"):
        contracts.require(bool((frame[name] > 0).all()), "All generated values must be positive: " + name)
    content = {"columns": list(frame.columns),
               "rows": [[_scalar(v) for v in row] for row in frame.itertuples(index=False, name=None)]}
    return {
        "schema_version": 1, "kind": "k01_generated_context_validity_v1", "status": "valid",
        "context_id": context_id, "context_eligibility_sha256": _digest(context),
        "task_contract_sha256": _digest(task), "frame_content_sha256": _digest(content),
        "digest_scope": "canonical_finite_JSON_task_context_and_ordered_rows_not_CSV_bytes_or_index",
        "required_rows": task["n_rows"], "validated_rows": len(frame), "all_required_rows_valid": True,
        "ordered_columns": list(frame.columns), "unique_nonempty_identifiers": True,
        "strictly_positive_columns": ["bmi", "glucose"], "rows_filtered": 0, "rows_repaired": 0,
        "inputs_mutated": False, "execution_authenticated": False, "approved_task_authenticated": False,
        "scientific_validity": "not_assessed", "case_or_global_release_authorized": False,
    }
