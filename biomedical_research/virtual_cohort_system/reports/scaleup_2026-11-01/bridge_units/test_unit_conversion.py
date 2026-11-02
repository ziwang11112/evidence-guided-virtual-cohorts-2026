"""Invented in-memory arrays only; no cohort, generator, or clinical factor."""
import copy
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

sys.path.insert(0, str(Path(__file__).parent))
import unit_conversion as unit


def approve(manifest):
    # Synthetic review is strictly test data; not a production approval helper.
    manifest["review"] = {
        "decision": "approved", "independent": True, "reviewer_id": "invented-reviewer",
        "producer_id": "invented-producer", "reviewed_utc": "2026-11-02T00:00:00Z",
        "reason": "Invented factor fixture only", "approved_sha256": unit.manifest_digest(manifest),
    }


@pytest.fixture
def case():
    frame = pd.DataFrame({"id": ["b", "a", "c"], "x": [1.5, 0.0, -2.0], "group": ["A", "B", "A"]},
                         index=pd.Index([8, 2, 7], name="invented_index"))
    inputs = {"row_id": "id", "columns": [
        {"name": "id", "kind": "string", "role": "identifier", "analyte_id": "row_id", "unit": "1", "scale": "categorical"},
        {"name": "x", "kind": "number", "role": "generated", "analyte_id": "invented_quantity", "unit": "toy_A", "scale": "original"},
        {"name": "group", "kind": "category", "role": "generated", "analyte_id": "invented_group", "unit": "1", "scale": "categorical"},
    ]}
    outputs = copy.deepcopy(inputs)
    outputs["columns"][1]["unit"] = "toy_B"
    manifest = {
        "schema_version": 1, "purpose": "analytic_fixture",
        "input_contract_sha256": unit.contract_digest(inputs), "output_contract_sha256": unit.contract_digest(outputs),
        "columns": [
            {"column": "id", "operation": "identity", "factor": 1.0, "source": None},
            {"column": "x", "operation": "multiply", "factor": 2.0, "source": {
                "kind": "invented_fixture", "reference": "Invented toy definition: B = 2 * A",
                "locator": "This test fixture", "analyte_id": "invented_quantity", "input_unit": "toy_A", "output_unit": "toy_B"}},
            {"column": "group", "operation": "identity", "factor": 1.0, "source": None},
        ], "review": None,
    }
    approve(manifest)
    return frame, inputs, outputs, manifest


def convert(case, **overrides):
    frame, inputs, outputs, manifest = case
    kwargs = {"input_contract": inputs, "output_contract": outputs, "expected_input_sha256": unit.frame_digest(frame),
              "caller_binding": {"kind": "invented_fixture", "execution_receipt_sha256": "a" * 64}}
    kwargs.update(overrides)
    return unit.convert_frame(frame, manifest, **kwargs)


def test_changes_values_preserves_identifiers_index_and_input(case):
    original = case[0].copy(deep=True)
    converted, receipt = convert(case)
    expected = original.copy(deep=True)
    expected["x"] = [3.0, 0.0, -4.0]
    assert_frame_equal(converted, expected)
    assert_frame_equal(case[0], original)
    assert receipt["input_frame_sha256"] == unit.frame_digest(original)
    assert receipt["output_frame_sha256"] == unit.frame_digest(converted)
    assert receipt["input_frame_sha256"] != receipt["output_frame_sha256"]
    assert receipt["execution_binding_status"] == "caller_asserted_not_verified_by_unit_adapter"
    assert receipt["new_scientific_generation"] is False


def test_identity_frame_remains_exact(case):
    frame, inputs, outputs, manifest = case
    outputs["columns"][1]["unit"] = inputs["columns"][1]["unit"]
    manifest["output_contract_sha256"] = unit.contract_digest(outputs)
    manifest["columns"][1] = {"column": "x", "operation": "identity", "factor": 1.0, "source": None}
    approve(manifest)
    converted, receipt = convert(case)
    assert_frame_equal(converted, frame)
    assert receipt["input_frame_sha256"] == receipt["output_frame_sha256"]
    converted.loc[8, "x"] = 99.0
    assert frame.loc[8, "x"] == 1.5


@pytest.mark.parametrize("field,value", [("analyte_id", "different_quantity"), ("role", "observed"),
                                         ("kind", "integer"), ("name", "renamed")])
def test_rejects_changed_column_semantics_even_after_review(case, field, value):
    case[2]["columns"][1][field] = value
    case[3]["output_contract_sha256"] = unit.contract_digest(case[2])
    approve(case[3])
    with pytest.raises(ValueError):
        convert(case)


@pytest.mark.parametrize("field,value", [("analyte_id", "wrong_quantity"), ("input_unit", "toy_B"),
                                         ("output_unit", "toy_A"), ("kind", "inferred_from_data")])
def test_rejects_wrong_conversion_source_mapping(case, field, value):
    case[3]["columns"][1]["source"][field] = value
    approve(case[3])
    with pytest.raises(ValueError):
        convert(case)


@pytest.mark.parametrize("factor", [True, False, 0, -2, float("nan"), float("inf"), "2", 1])
def test_rejects_invalid_factors(case, factor):
    case[3]["columns"][1]["factor"] = factor
    with pytest.raises(ValueError):
        # NaN/Inf cannot even be reviewed as canonical finite JSON.
        approve(case[3])
        convert(case)


@pytest.mark.parametrize("operation", ["log", "standardize", "affine", "identity"])
def test_rejects_unsupported_transform_or_label_only_conversion(case, operation):
    case[3]["columns"][1]["operation"] = operation
    approve(case[3])
    with pytest.raises(ValueError):
        convert(case)


def test_rejects_extra_offset_field(case):
    case[3]["columns"][1]["offset"] = 0.0
    approve(case[3])
    with pytest.raises(ValueError, match="fields"):
        convert(case)


@pytest.mark.parametrize("change", ["extra", "missing", "reorder", "duplicate"])
def test_rejects_unmapped_or_reordered_frame_columns(case, change):
    frame = case[0]
    if change == "extra":
        frame["unmapped"] = 1
    elif change == "missing":
        frame.drop(columns="group", inplace=True)
    elif change == "reorder":
        frame = frame[["x", "id", "group"]]
    else:
        frame.columns = ["id", "x", "x"]
    with pytest.raises(ValueError):
        convert((frame, *case[1:]))


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), None, True, "1.5"])
def test_rejects_nonfinite_boolean_missing_or_numeric_strings(case, value):
    case[0]["x"] = pd.Series([value, 0.0, -2.0], index=case[0].index, dtype=object)
    with pytest.raises(ValueError):
        convert(case)


def test_rejects_duplicate_row_ids(case):
    case[0].loc[2, "id"] = "b"
    with pytest.raises(ValueError, match="Row IDs"):
        convert(case)


def test_rejects_changed_input_hash(case):
    original = unit.frame_digest(case[0])
    case[0].loc[8, "x"] = 8.0
    with pytest.raises(ValueError, match="Input frame hash"):
        convert(case, expected_input_sha256=original)


def test_review_is_bound_to_exact_typed_factor(case):
    # Numerically equal int/float JSON values have different review digests.
    case[3]["columns"][1]["factor"] = 2
    with pytest.raises(ValueError, match="Review"):
        convert(case)


@pytest.mark.parametrize("field,value", [("independent", 1), ("decision", "pending"),
                                         ("reviewer_id", "invented-producer"),
                                         ("reviewer_id", " Invented-Producer "),
                                         ("reviewer_id", "INVENTED-PRODUCER"),
                                         ("approved_sha256", "0" * 64)])
def test_rejects_invalid_review(case, field, value):
    case[3]["review"][field] = value
    with pytest.raises(ValueError):
        convert(case)


def test_fixture_factor_cannot_become_production(case):
    case[3]["purpose"] = "target_analysis_unit_conversion"
    approve(case[3])
    with pytest.raises(ValueError, match="fixture-only"):
        convert(case)


def test_no_log_or_unknown_scale(case):
    for contract in case[1:3]:
        contract["columns"][1]["scale"] = "natural_log"
    with pytest.raises(ValueError, match="scales"):
        convert(case)


@pytest.mark.parametrize("value,factor", [(np.finfo(float).max, 2.0), (np.nextafter(0.0, 1.0), 0.25)])
def test_rejects_overflow_and_underflow(case, value, factor):
    case[0].loc[8, "x"] = value
    case[3]["columns"][1]["factor"] = factor
    approve(case[3])
    with pytest.raises(ValueError, match="overflow/underflow"):
        convert(case)


def test_binding_is_copied_and_not_claimed_verified(case):
    binding = {"receipt_sha256": "b" * 64, "nested": {"asserted": True}}
    _, receipt = convert(case, caller_binding=binding)
    binding["nested"]["asserted"] = False
    assert receipt["caller_binding"]["nested"]["asserted"] is True
    assert receipt["execution_binding_status"] == "caller_asserted_not_verified_by_unit_adapter"


@pytest.mark.parametrize("binding", [{}, {"not_finite": float("nan")}, {1: "bad_key"}, {"bad": Path("x")}])
def test_rejects_invalid_binding(case, binding):
    with pytest.raises(ValueError):
        convert(case, caller_binding=binding)


def test_hash_binds_row_order_index_and_dtype(case):
    frame = case[0]
    digest = unit.frame_digest(frame)
    assert digest != unit.frame_digest(frame.iloc[::-1])
    assert digest != unit.frame_digest(frame.reset_index(drop=True))
    changed = frame.copy()
    changed["x"] = changed["x"].astype("float32")
    assert digest != unit.frame_digest(changed)


def test_hash_binds_categorical_and_identity_numeric_values(case):
    before = unit.frame_digest(case[0])
    case[0].loc[8, "group"] = "B"
    assert before != unit.frame_digest(case[0])


def test_rejects_stale_contract_hash(case):
    case[1]["columns"][1]["unit"] = "unreviewed_unit"
    with pytest.raises(ValueError, match="Input contract hash"):
        convert(case)


@pytest.mark.parametrize("where", ["factor", "input"])
def test_rejects_integer_precision_loss(case, where):
    if where == "factor":
        case[3]["columns"][1]["factor"] = 2**53 + 1
        approve(case[3])
    else:
        case[0]["x"] = [2**53 + 1, 0, -2]
    with pytest.raises(ValueError, match="loses precision"):
        convert(case)
