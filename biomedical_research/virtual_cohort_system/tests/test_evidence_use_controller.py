"""Exercise the additive controller loader with temporary invented artifacts only."""
import importlib.util
from pathlib import Path

import pytest

from cohort_harness.contracts import ContractError
from test_evidence_actions_v1 import routing_inputs
from test_evidence_use_v1 import bind, encoded, obj, revision, use_fixture


LOADER_PATH = (Path(__file__).resolve().parents[1] / "work/evidence_use_cross_task_2026-11-05"
               / "controller_evidence_use.py")
module_spec = importlib.util.spec_from_file_location("evidence_use_controller_under_test", LOADER_PATH)
loader = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(loader)


def write_bundle(root, fixture):
    manifest, artifacts = fixture
    for relative, raw in artifacts.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    (root / "candidates/new/evidence_use_v1.json").write_bytes(encoded(manifest))


def test_loader_binds_actual_initial_files_without_executing_generator(tmp_path, use_fixture):
    write_bundle(tmp_path, use_fixture)
    result = loader.validate_candidate_use(tmp_path, "candidates/new", ["mean_y"])
    assert result["mode"] == "initial"
    assert result["generator_parameter_use"] == "not_assessed"


def test_loader_binds_actual_revision_and_baseline_files(tmp_path, use_fixture):
    revision(use_fixture)
    write_bundle(tmp_path, use_fixture)
    result = loader.validate_candidate_use(tmp_path, "candidates/new", ["mean_y"], baseline="candidates/old")
    assert result["parameter_status"] == "changed"
    assert result["generator_bytes_changed"] is False


def test_sidecar_cannot_substitute_another_task_with_identical_bytes(tmp_path, use_fixture):
    manifest, artifacts = use_fixture
    manifest["bindings"]["task"]["path"] = "other_task.json"
    artifacts["other_task.json"] = artifacts.pop("task.json")
    write_bundle(tmp_path, use_fixture)
    with pytest.raises(ContractError, match="different actual input"):
        loader.validate_candidate_use(tmp_path, "candidates/new", ["mean_y"])


def test_sidecar_cannot_choose_a_different_baseline(tmp_path, use_fixture):
    revision(use_fixture)
    write_bundle(tmp_path, use_fixture)
    (tmp_path / "candidates/other").mkdir()
    with pytest.raises(ContractError, match="different actual input"):
        loader.validate_candidate_use(tmp_path, "candidates/new", ["mean_y"], baseline="candidates/other")


def test_actual_code_edit_is_rejected_before_any_execution(tmp_path, use_fixture):
    write_bundle(tmp_path, use_fixture)
    (tmp_path / "candidates/new/generator.py").write_bytes(b"edited opaque code")
    with pytest.raises(ContractError, match="hash mismatch"):
        loader.validate_candidate_use(tmp_path, "candidates/new", ["mean_y"])


def test_check_artifact_path_cannot_escape_candidate(tmp_path, use_fixture):
    checks = obj(use_fixture, "checks")
    checks["artifacts"][0]["path"] = "../elsewhere.txt"
    bind(use_fixture, "checks", checks)
    write_bundle(tmp_path, use_fixture)
    with pytest.raises(ContractError, match="relative path segment"):
        loader.validate_candidate_use(tmp_path, "candidates/new", ["mean_y"])


def test_controller_required_use_is_not_taken_from_sidecar(tmp_path, use_fixture):
    write_bundle(tmp_path, use_fixture)
    with pytest.raises(ContractError, match="Missing required"):
        loader.validate_candidate_use(tmp_path, "candidates/new", ["mean_y", "omitted_use"])
