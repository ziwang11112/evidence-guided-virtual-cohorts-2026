"""Only small invented arrays; no I/O, generator or real target is exercised."""
import builtins
import copy
from pathlib import Path
import socket
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent))
from generated_validity import validate_generated_release


@pytest.fixture
def sample():
    task = {"schema_version": 1, "task_id": "invented-k02-validity-fixture", "mode": "whole_cohort",
            "population": "Invented small validity fixture, not a clinical release", "row_id": "id", "n_rows": 3,
            "columns": [
                {"name": "id", "kind": "string", "unit": "1", "role": "identifier", "nullable": False},
                {"name": "age", "kind": "number", "unit": "year", "role": "generated", "nullable": False, "minimum": 18},
                {"name": "sex", "kind": "category", "unit": "1", "role": "generated", "nullable": False, "categories": ["F", "M"]},
                {"name": "bmi", "kind": "number", "unit": "kg/m^2", "role": "generated", "nullable": False},
                {"name": "total_cholesterol", "kind": "number", "unit": "mmol/L", "role": "generated", "nullable": False},
                {"name": "hdl_cholesterol", "kind": "number", "unit": "mmol/L", "role": "generated", "nullable": False}],
            "information_policy": {"mode": "prior_only", "excluded_cohorts": [], "allowed_tools": []},
            "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 0}}
    frame = pd.DataFrame({"id": ["invented-a", "invented-b", "invented-c"], "age": [18.0, 19.0, 20.0], "sex": ["F", "M", "F"],
                          "bmi": [1.0, 2.0, 3.0], "total_cholesterol": [2.0, 3.0, 4.0], "hdl_cholesterol": [1.0, 2.0, 3.0]})
    return frame, task


def test_valid_release_retains_all_rows_and_reports_scope(sample):
    frame, task = sample
    before_frame, before_task = frame.copy(deep=True), copy.deepcopy(task)
    report = validate_generated_release(frame, task)
    assert report["status"] == "valid" and report["validated_rows"] == report["required_rows"] == 3
    assert report["all_required_rows_valid"] and report["rows_filtered"] == report["rows_repaired"] == 0
    assert not report["execution_authenticated"] and not report["approved_task_authenticated"]
    assert report["scientific_validity"] == "not_assessed"
    pd.testing.assert_frame_equal(frame, before_frame)
    assert task == before_task
    assert report == validate_generated_release(frame, task)


@pytest.mark.parametrize("column", ["bmi", "total_cholesterol", "hdl_cholesterol"])
@pytest.mark.parametrize("value", [0.0, -1.0])
def test_zero_or_negative_generated_value_rejects_whole_release_without_filter(sample, column, value):
    frame, task = sample
    frame.loc[1, column] = value
    before = frame.copy(deep=True)
    with pytest.raises(ValueError, match="strictly positive"):
        validate_generated_release(frame, task)
    pd.testing.assert_frame_equal(frame, before)
    assert len(frame) == task["n_rows"]


@pytest.mark.parametrize("column,value", [
    ("age", 17.99), ("age", np.inf), ("age", np.nan),
    ("bmi", -np.inf), ("total_cholesterol", np.inf), ("hdl_cholesterol", np.nan),
    ("sex", "X"), ("sex", "female"), ("sex", "f"), ("sex", None), ("id", None), ("id", " ")])
def test_invalid_fields_reject_without_mutation(sample, column, value):
    frame, task = sample
    frame.loc[1, column] = value
    before = frame.copy(deep=True)
    with pytest.raises(ValueError):
        validate_generated_release(frame, task)
    pd.testing.assert_frame_equal(frame, before)


@pytest.mark.parametrize("value", [True, "2", complex(1, 1)])
def test_invalid_numeric_types_rejected(sample, value):
    frame, task = sample
    frame["bmi"] = frame["bmi"].astype(object)
    frame.loc[1, "bmi"] = value
    with pytest.raises(ValueError):
        validate_generated_release(frame, task)


@pytest.mark.parametrize("mutation", ["short", "long", "duplicate_id", "extra_column", "missing_column", "reordered"])
def test_shape_and_identifier_errors_reject(sample, mutation):
    frame, task = sample
    if mutation == "short": frame = frame.iloc[:2].copy()
    elif mutation == "long": frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    elif mutation == "duplicate_id": frame.loc[1, "id"] = frame.loc[0, "id"]
    elif mutation == "extra_column": frame["unexpected"] = 1
    elif mutation == "missing_column": frame = frame.drop(columns=["bmi"])
    else: frame = frame[list(reversed(frame.columns))]
    before = frame.copy(deep=True)
    with pytest.raises(ValueError):
        validate_generated_release(frame, task)
    pd.testing.assert_frame_equal(frame, before)


@pytest.mark.parametrize("mutation", ["wrong_unit", "wrong_kind", "wrong_mode", "nullable", "extra_sex_category", "bool_count"])
def test_supplied_task_must_be_canonical_k02_contract(sample, mutation):
    frame, task = sample
    if mutation == "wrong_unit": task["columns"][4]["unit"] = "mg/dL"
    elif mutation == "wrong_kind": task["columns"][1]["kind"] = "integer"
    elif mutation == "wrong_mode": task["mode"] = "completion"
    elif mutation == "nullable": task["columns"][0]["nullable"] = True
    elif mutation == "extra_sex_category": task["columns"][2]["categories"].append("X")
    else: task["n_rows"] = True
    with pytest.raises(ValueError):
        validate_generated_release(frame, task)


def test_strict_age_rule_does_not_depend_on_task_inclusive_minimum(sample):
    frame, task = sample
    task["columns"][1].pop("minimum")
    frame.loc[0, "age"] = 17
    with pytest.raises(ValueError, match="at least 18"):
        validate_generated_release(frame, task)


def test_positive_values_are_not_clipped_to_arbitrary_floor(sample):
    frame, task = sample
    frame.loc[0, "hdl_cholesterol"] = np.nextafter(0.0, 1.0)
    report = validate_generated_release(frame, task)
    assert report["all_required_rows_valid"]
    assert frame.loc[0, "hdl_cholesterol"] == np.nextafter(0.0, 1.0)


def test_content_and_task_commitments_change_with_actual_inputs(sample):
    frame, task = sample
    original = validate_generated_release(frame, task)
    changed = frame.copy()
    changed.loc[1, "bmi"] = 2.5
    assert validate_generated_release(changed, task)["frame_content_sha256"] != original["frame_content_sha256"]
    changed_task = copy.deepcopy(task)
    changed_task["population"] = "Another explicit invented context"
    assert validate_generated_release(frame, changed_task)["task_contract_sha256"] != original["task_contract_sha256"]


def test_guard_has_no_file_process_or_network_actions(sample, monkeypatch):
    frame, task = sample
    def forbidden(*args, **kwargs):
        pytest.fail("Validity guard may not perform I/O, process launch or networking")
    with monkeypatch.context() as patch:
        for owner, name in [(builtins, "open"), (Path, "open"), (subprocess, "run"), (subprocess, "Popen"), (socket, "create_connection")]:
            patch.setattr(owner, name, forbidden)
        report = validate_generated_release(frame, task)
    assert report["status"] == "valid"
