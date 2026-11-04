"""Request-intake integration checks on invented metadata/records only.

No literature request, Agent call, generator execution or patient data is used.
"""
from __future__ import annotations

import copy
import hashlib
import json

import pytest

from cohort_harness import literature
from cohort_harness.contracts import validate_input, validate_task
from cohort_harness.lifecycle import read_table
from cohort_harness.request_intake import prepare_request


def request(mode="whole_cohort"):
    columns = [
        {"name": "record_key", "kind": "string", "unit": "identifier", "role": "identifier", "nullable": False},
        {"name": "alpha", "kind": "number", "unit": "alpha_unit",
         "role": "generated" if mode == "whole_cohort" else "observed", "nullable": False},
        {"name": "beta", "kind": "number", "unit": "beta_unit", "role": "generated", "nullable": False},
    ]
    return {
        "schema_version": 1,
        "purpose": "Explore the relation of invented alpha and beta for an interface test.",
        "analyses": ["Estimate the beta-on-alpha association with an intercept.", "Describe beta dispersion."],
        "task": {
            "schema_version": 1, "task_id": "invented-request-intake", "mode": mode,
            "population": "Three invented records only; no biomedical claims.",
            "row_id": "record_key", "n_rows": 3, "columns": columns,
            "information_policy": {"mode": "published_evidence", "excluded_cohorts": ["held-out-fixture"],
                                   "allowed_tools": ["literature.search", "literature.fetch"]},
            "budget": {"source_queries": 2, "source_downloads": 1, "revisions": 1},
        },
    }


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def snapshots(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_whole_cohort_request_preserved_without_a_scientific_candidate(tmp_path):
    value = request()
    original = copy.deepcopy(value)
    out = tmp_path / "bundle"
    prepare_request(value, out)
    assert value == original
    assert read(out / "task.json") == original["task"]
    validate_task(read(out / "task.json"))
    assert read(out / "request.json") == original
    author = (out / "AUTHOR_TASK.md").read_text(encoding="utf-8")
    assert original["purpose"] in author
    assert all(analysis in author for analysis in original["analyses"])
    assert read(out / "registry.json") == {"artifacts": []}
    assert not (out / "observed.csv").exists()
    assert (out / "candidates").is_dir()
    assert not any((out / "candidates").iterdir())
    assert not any(p.name in {"generator.py", "generated.csv", "model_spec.json", "evidence.json"}
                   for p in out.rglob("*"))


@pytest.mark.parametrize("mode,raw", [
    ("enrichment", b"record_key,alpha\r\n001,1.2345678901234567\r\nNA,2\r\n003,3\r\n"),
    ("completion", b"record_key,alpha,beta\r\n001,1.2345678901234567,\r\nNA,2,4.123456789012345\r\n003,3,\r\n"),
])
def test_observed_input_bytes_and_measurements_preserved(tmp_path, mode, raw):
    value = request(mode)
    source = tmp_path / "input.csv"
    source.write_bytes(raw)
    out = tmp_path / "bundle"
    prepare_request(value, out, observed_path=source)
    assert source.read_bytes() == raw
    assert (out / "observed.csv").read_bytes() == raw
    frame = read_table(out / "observed.csv", value["task"])
    validate_input(frame, value["task"])
    assert frame["record_key"].tolist() == ["001", "NA", "003"]
    receipt_text = (out / "intake_receipt.json").read_text(encoding="utf-8")
    assert hashlib.sha256(raw).hexdigest() in receipt_text


@pytest.mark.parametrize("bad", ["empty_purpose", "null_analyses", "duplicate_analyses",
                                  "unknown_request_field", "invalid_unit_type", "invalid_task_mode",
                                  "duplicate_column"])
def test_invalid_request_contract_leaves_no_bundle(tmp_path, bad):
    value = request()
    if bad == "empty_purpose":
        value["purpose"] = " "
    elif bad == "null_analyses":
        value["analyses"] = None
    elif bad == "duplicate_analyses":
        value["analyses"] = ["same request", "same request"]
    elif bad == "unknown_request_field":
        value["target_effect"] = 123
    elif bad == "invalid_unit_type":
        value["task"]["columns"][1]["unit"] = None
    elif bad == "invalid_task_mode":
        value["task"]["mode"] = "unspecified"
    elif bad == "duplicate_column":
        value["task"]["columns"].append(copy.deepcopy(value["task"]["columns"][1]))
    out = tmp_path / "bundle"
    with pytest.raises((ValueError, TypeError)):
        prepare_request(value, out)
    assert not out.exists()


@pytest.mark.parametrize("bad", ["duplicate_identifier", "missing_column", "nonnumeric",
                                  "missing_required_observations", "forbidden_whole_cohort_observations"])
def test_invalid_observations_leave_no_bundle(tmp_path, bad):
    value = request("enrichment")
    source = tmp_path / "input.csv"
    raw = b"record_key,alpha\n001,1\n002,2\n003,3\n"
    if bad == "duplicate_identifier":
        raw = b"record_key,alpha\n001,1\n001,2\n003,3\n"
    elif bad == "missing_column":
        raw = b"record_key\n001\n002\n003\n"
    elif bad == "nonnumeric":
        raw = b"record_key,alpha\n001,one\n002,2\n003,3\n"
    elif bad == "forbidden_whole_cohort_observations":
        value = request()
    source.write_bytes(raw)
    observed = None if bad == "missing_required_observations" else source
    out = tmp_path / "bundle"
    with pytest.raises((ValueError, TypeError)):
        prepare_request(value, out, observed_path=observed)
    assert source.read_bytes() == raw
    assert not out.exists()


def test_existing_bundle_is_not_overwritten_or_reset(tmp_path):
    out = tmp_path / "bundle"
    prepare_request(request(), out)
    (out / "sources" / "previous.txt").write_bytes(b"retained source record")
    before = snapshots(out)
    changed = request()
    changed["purpose"] = "A different request may not overwrite prior work."
    with pytest.raises((ValueError, OSError)):
        prepare_request(changed, out)
    assert snapshots(out) == before


def test_prior_only_task_does_not_gain_literature_permission(tmp_path, monkeypatch):
    value = request()
    value["task"]["information_policy"]["mode"] = "prior_only"
    value["task"]["information_policy"]["allowed_tools"] = []
    value["task"]["budget"].update(source_queries=0, source_downloads=0)
    def never(*args, **kwargs):
        pytest.fail("Intake/prior-only initialization attempted HTTP")
    monkeypatch.setattr(literature.gateway, "http_get", never)
    out = tmp_path / "bundle"
    prepare_request(value, out)
    assert read(out / "task.json") == value["task"]
    result = literature.run_literature(out, "init")
    assert result["status"] == "error"
    assert not (out / "gateway").exists()


def test_created_bundle_initializes_real_literature_adapter_without_http(tmp_path, monkeypatch):
    def never(*args, **kwargs):
        pytest.fail("Local literature initialization attempted HTTP")
    monkeypatch.setattr(literature.gateway, "http_get", never)
    value = request()
    out = tmp_path / "bundle"
    prepare_request(value, out)
    result = literature.run_literature(out, "init")
    assert result["status"] == "ok"
    assert result["budgets"]["queries"] == 2
    assert result["budgets"]["downloads"] == 1
    assert read(out / "registry.json") == {"artifacts": []}
    assert read(out / "task.json") == value["task"]


def test_whole_cohort_packet_points_to_versioned_semantic_adapter(tmp_path):
    out = tmp_path / "bundle"
    prepare_request(request(), out)
    adapters = read(out / "adapters.json")
    serialized = json.dumps(adapters)
    assert "semantic_feedback_v1" in serialized
    assert "cohort_harness.whole_cohort_feedback" not in serialized
    assert "cohort_harness.semantic_feedback_v1" in (out / "AUTHOR_TASK.md").read_text(encoding="utf-8")
