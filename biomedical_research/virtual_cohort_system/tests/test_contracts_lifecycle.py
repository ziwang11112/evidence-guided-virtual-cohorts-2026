"""Independent contract tests using invented records, never biomedical data.

These exercise information boundaries, preservation and artifact commitments.
They do not establish that an Agent's scientific model is valid or isolated.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cohort_harness.contracts import (
    validate_evidence,
    validate_input,
    validate_output,
    validate_spec,
    validate_task,
)
from cohort_harness.lifecycle import freeze_candidate, validate_program, verify_candidate


REJECTIONS = (ValueError, AssertionError)


def dump(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def task(mode: str = "enrichment") -> dict:
    columns = [
        {"name": "key", "kind": "string", "unit": "identifier", "role": "identifier", "nullable": False},
        {"name": "x", "kind": "number", "unit": "unit", "role": "observed", "nullable": False, "minimum": 0, "maximum": 10},
        {"name": "count", "kind": "integer", "unit": "count", "role": "observed", "nullable": False, "minimum": 0},
        {"name": "group", "kind": "category", "unit": "category", "role": "observed", "nullable": False, "categories": ["a", "b"]},
        {"name": "y", "kind": "number", "unit": "unit", "role": "generated", "nullable": False, "minimum": 0, "maximum": 10},
    ]
    if mode == "whole_cohort":
        for column in columns[1:]:
            column["role"] = "generated"
    return {
        "schema_version": 1,
        "task_id": "invented-contract-test",
        "mode": mode,
        "population": "Entirely invented arithmetic fixtures; not real people.",
        "row_id": "key",
        "n_rows": 3,
        "columns": columns,
        "information_policy": {
            "mode": "published_evidence", "excluded_cohorts": ["hidden-target"],
            "allowed_tools": ["fixture-reader"],
        },
        "budget": {"source_queries": 1, "source_downloads": 1, "revisions": 2},
    }


def frames(mode: str = "enrichment") -> tuple[pd.DataFrame | None, pd.DataFrame]:
    output = pd.DataFrame({
        "key": ["r01", "r02", "r03"], "x": [1.0, 2.0, 3.0],
        "count": [1, 2, 3], "group": ["a", "b", "a"], "y": [2.0, 1.5, 3.0],
    })
    if mode == "whole_cohort":
        return None, output
    if mode == "completion":
        observed = output.copy(deep=True)
        observed.loc[[0, 2], "y"] = np.nan
        return observed, output
    return output.drop(columns="y"), output


def ledger(artifact: dict | None = None) -> dict:
    artifact = artifact or {"path": "sources/paper.txt", "sha256": "a" * 64}
    return {
        "schema_version": 1,
        "sources": [{
            "id": "S1", "identifier": "fixture:paper", "population": "invented",
            "measurement": "invented units", "cohort_ids": ["source-fixture"],
            "artifacts": [artifact],
        }],
        "items": [{
            "id": "E1", "source_id": "S1", "locator": "fixture table 1",
            "variables": ["y"], "kind": "mean", "estimate": 2.0, "unit": "unit",
            "uncertainty": {"kind": "se", "value": 0.25}, "adjustment": [],
            "selection": "invented records", "applicability": "software test only",
        }],
    }


def specification() -> dict:
    return {
        "parameters": {"location": 2.0},
        "assumptions": [{"id": "A1", "description": "A fixture-only modeling assumption."}],
        "parameter_provenance": {
            "location": {"evidence_ids": ["E1"], "assumption_ids": ["A1"], "derivation": "An invented source mean."}
        },
    }


def make_bundle(tmp_path: Path, name: str = "bundle") -> tuple[Path, Path]:
    bundle = tmp_path / name
    candidate = bundle / "candidates" / "initial"
    candidate.mkdir(parents=True)
    dump(bundle / "task.json", task())
    observed, _ = frames()
    observed.to_csv(bundle / "observed.csv", index=False)
    source = bundle / "sources" / "paper.txt"
    source.parent.mkdir()
    source.write_text("Invented software fixture: the reported mean is 2 units.\n", encoding="utf-8")
    artifact = {"path": "sources/paper.txt", "sha256": digest(source)}
    dump(bundle / "registry.json", {"artifacts": [{
        "source_id": "S1", **artifact, "origin": "fixture", "screening": "approved",
    }]})
    dump(candidate / "evidence.json", ledger(artifact))
    dump(candidate / "model_spec.json", specification())
    (candidate / "generator.py").write_text(
        "def generate(observed, spec, seed):\n"
        "    # This fixture is not executed by the lifecycle tests.\n"
        "    raise NotImplementedError('contract fixture')\n", encoding="utf-8",
    )
    (candidate / "decision.md").write_text("Invented software test; no scientific claim.\n", encoding="utf-8")
    check_artifact = candidate / "fixture_check.txt"
    check_artifact.write_text("Fixture arithmetic: 1 + 1 = 2.\n", encoding="utf-8")
    dump(candidate / "checks.json", {
        "scope": "fixture_only",
        "records": [{"name": "fixture arithmetic", "status": "pass", "detail": "1 + 1 = 2; no generator execution."}],
        "artifacts": [{"path": "fixture_check.txt", "sha256": digest(check_artifact)}],
    })
    return bundle, candidate


def clone_candidate(candidate: Path, name: str = "revised") -> Path:
    other = candidate.parent / name
    other.mkdir()
    for source in candidate.iterdir():
        if source.name != "freeze.json" and source.is_file():
            (other / source.name).write_bytes(source.read_bytes())
    return other


def revision(kind: str = "retain") -> dict:
    return {
        "reason": "No new evidence warrants a model change.", "kind": kind,
        "addressed_findings": [], "remaining_limitations": ["Fixture only."],
    }


@pytest.mark.parametrize("mode", ["whole_cohort", "enrichment", "completion"])
def test_three_modes_accept_valid_contract_and_preservation(mode):
    contract = task(mode)
    observed, output = frames(mode)
    validate_task(contract)
    validate_input(observed, contract)
    validate_output(observed, output, contract)


def test_completion_cannot_overwrite_a_previously_measured_generated_cell():
    observed, output = frames("completion")
    output.loc[1, "y"] = 9.0
    with pytest.raises(REJECTIONS):
        validate_output(observed, output, task("completion"))


@pytest.mark.parametrize("mode", ["enrichment", "completion"])
def test_observed_values_and_row_order_are_preserved(mode):
    observed, output = frames(mode)
    changed = output.copy(deep=True)
    changed.loc[0, "x"] += 0.1
    with pytest.raises(REJECTIONS):
        validate_output(observed, changed, task(mode))
    with pytest.raises(REJECTIONS):
        validate_output(observed, output.iloc[::-1].reset_index(drop=True), task(mode))


@pytest.mark.parametrize("mutation", [
    lambda frame: frame.assign(key=["r01", "r01", "r03"]),
    lambda frame: frame.assign(key=["r01", None, "r03"]),
    lambda frame: frame.assign(y=[1.0, float("inf"), 3.0]),
    lambda frame: frame.assign(y=[1.0, float("nan"), 3.0]),
    lambda frame: frame.assign(y=[1.0, 11.0, 3.0]),
    lambda frame: frame.assign(count=[1.0, 2.5, 3.0]),
    lambda frame: frame.assign(group=["a", "unsupported", "a"]),
    lambda frame: frame.rename(columns={"y": "unknown"}),
    lambda frame: frame.assign(extra=1),
    lambda frame: frame.iloc[:2].copy(),
])
def test_whole_cohort_rejects_invalid_generated_data(mutation):
    _, output = frames("whole_cohort")
    with pytest.raises(REJECTIONS):
        validate_output(None, mutation(output), task("whole_cohort"))


def test_enrichment_rejects_hidden_target_column_in_inputs():
    _, output = frames()
    with pytest.raises(REJECTIONS):
        validate_input(output, task())


def test_invalid_input_does_not_pass_when_output_matches_it():
    observed, output = frames()
    observed.loc[1, "key"] = observed.loc[0, "key"]
    output.loc[1, "key"] = output.loc[0, "key"]
    with pytest.raises(REJECTIONS):
        validate_output(observed, output, task())


@pytest.mark.parametrize("mutation", [
    lambda doc: doc.update(reference_path="custodian/reference.csv"),
    lambda doc: doc.update(schema_version=True),
    lambda doc: doc.update(n_rows=True),
    lambda doc: doc.update(n_rows=0),
    lambda doc: doc["columns"].append(copy.deepcopy(doc["columns"][-1])),
    lambda doc: doc["columns"][-1].update(nullable=True),
    lambda doc: doc["columns"][0].update(role="observed"),
])
def test_task_rejects_ambiguous_or_hidden_information_fields(mutation):
    contract = task()
    mutation(contract)
    with pytest.raises(REJECTIONS):
        validate_task(contract)


def test_evidence_and_parameter_references_resolve():
    ids = validate_evidence(ledger(), task())
    assert ids == {"E1"}
    validate_spec(specification(), ids)


@pytest.mark.parametrize("mutation", [
    lambda doc: doc["items"][0].update(source_id="missing-source"),
    lambda doc: doc["items"].append(copy.deepcopy(doc["items"][0])),
    lambda doc: doc["items"][0].update(estimate=float("nan")),
    lambda doc: doc["items"][0]["uncertainty"].update(value=-0.5),
])
def test_evidence_rejects_unresolved_or_invalid_statistics(mutation):
    evidence = ledger()
    mutation(evidence)
    with pytest.raises(REJECTIONS):
        validate_evidence(evidence, task())


@pytest.mark.parametrize("field,missing", [("evidence_ids", "E_missing"), ("assumption_ids", "A_missing")])
def test_parameter_provenance_rejects_unknown_references(field, missing):
    spec = specification()
    spec["parameter_provenance"]["location"][field] = [missing]
    with pytest.raises(REJECTIONS):
        validate_spec(spec, {"E1"})


def test_prior_only_does_not_require_fake_source_records():
    contract = task()
    contract["information_policy"]["mode"] = "prior_only"
    empty = {"schema_version": 1, "sources": [], "items": []}
    assert validate_evidence(empty, contract) == set()
    spec = specification()
    spec["parameter_provenance"]["location"]["evidence_ids"] = []
    validate_spec(spec, set())
    with pytest.raises(REJECTIONS):
        validate_evidence(empty, task())


def test_freeze_and_verify_accept_complete_fixture_bundle(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    receipt = freeze_candidate(bundle, candidate)
    assert receipt
    assert (candidate / "freeze.json").is_file()
    assert verify_candidate(bundle, candidate)


def test_freeze_is_exclusive_and_does_not_overwrite(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    freeze_candidate(bundle, candidate)
    original = (candidate / "freeze.json").read_bytes()
    with pytest.raises((ValueError, FileExistsError)):
        freeze_candidate(bundle, candidate)
    assert (candidate / "freeze.json").read_bytes() == original


@pytest.mark.parametrize("relative", ["generator.py", "model_spec.json", "checks.json", "fixture_check.txt", "decision.md"])
def test_candidate_artifacts_are_hash_bound_after_freeze(tmp_path, relative):
    bundle, candidate = make_bundle(tmp_path)
    freeze_candidate(bundle, candidate)
    artifact = candidate / relative
    artifact.write_bytes(artifact.read_bytes() + b"\n ")
    with pytest.raises(REJECTIONS):
        verify_candidate(bundle, candidate)


@pytest.mark.parametrize("relative", ["task.json", "observed.csv", "sources/paper.txt"])
def test_bundle_inputs_and_source_bytes_are_hash_bound(tmp_path, relative):
    bundle, candidate = make_bundle(tmp_path)
    freeze_candidate(bundle, candidate)
    artifact = bundle / relative
    artifact.write_bytes(artifact.read_bytes() + b"\n ")
    with pytest.raises(REJECTIONS):
        verify_candidate(bundle, candidate)


def test_approved_source_append_preserves_prior_freeze_and_supports_revision(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    parent = freeze_candidate(bundle, candidate)
    new_source = bundle / "sources" / "second.txt"
    new_source.write_text("Another invented source reports 2.2 units.\n", encoding="utf-8")
    artifact = {"path": "sources/second.txt", "sha256": digest(new_source)}
    registry = json.loads((bundle / "registry.json").read_text(encoding="utf-8"))
    registry["artifacts"].append({
        "source_id": "S2", **artifact, "origin": "fixture", "screening": "approved",
    })
    dump(bundle / "registry.json", registry)
    assert verify_candidate(bundle, candidate)

    child = clone_candidate(candidate)
    evidence = ledger({"path": "sources/paper.txt", "sha256": digest(bundle / "sources" / "paper.txt")})
    evidence["sources"].append({
        "id": "S2", "identifier": "fixture:second-paper", "population": "invented",
        "measurement": "invented units", "cohort_ids": ["second-source"], "artifacts": [artifact],
    })
    item = copy.deepcopy(evidence["items"][0])
    item.update(id="E2", source_id="S2", estimate=2.2)
    evidence["items"].append(item)
    dump(child / "evidence.json", evidence)
    spec = specification()
    spec["parameters"]["location"] = 2.2
    spec["parameter_provenance"]["location"]["evidence_ids"] = ["E2"]
    dump(child / "model_spec.json", spec)
    freeze_candidate(bundle, child, parent_receipt=parent, revision=revision("revise"))
    assert verify_candidate(bundle, child)
    assert verify_candidate(bundle, candidate)


def test_registry_prefix_cannot_be_rewritten_after_freeze(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    freeze_candidate(bundle, candidate)
    registry = json.loads((bundle / "registry.json").read_text(encoding="utf-8"))
    registry["artifacts"][0]["origin"] = "curator"
    dump(bundle / "registry.json", registry)
    with pytest.raises(REJECTIONS):
        verify_candidate(bundle, candidate)


def test_unregistered_source_cannot_be_frozen(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    dump(bundle / "registry.json", {"artifacts": []})
    with pytest.raises(REJECTIONS):
        freeze_candidate(bundle, candidate)


def test_source_mutation_before_freeze_rejected(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    (bundle / "sources" / "paper.txt").write_text("changed source", encoding="utf-8")
    with pytest.raises(REJECTIONS):
        freeze_candidate(bundle, candidate)


def test_checks_file_and_declared_artifact_are_required(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    (candidate / "fixture_check.txt").unlink()
    with pytest.raises(REJECTIONS):
        freeze_candidate(bundle, candidate)
    (candidate / "checks.json").unlink()
    with pytest.raises(REJECTIONS):
        freeze_candidate(bundle, candidate)


def test_valid_retain_preserves_parent_and_binds_child(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    parent = freeze_candidate(bundle, candidate)
    child = clone_candidate(candidate)
    (child / "decision.md").write_text("Retained after review; no numerical change.\n", encoding="utf-8")
    freeze_candidate(bundle, child, parent_receipt=parent, revision=revision())
    assert verify_candidate(bundle, candidate)
    assert verify_candidate(bundle, child)


def test_retain_cannot_hide_changed_model(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    parent = freeze_candidate(bundle, candidate)
    child = clone_candidate(candidate)
    spec = specification()
    spec["parameters"]["location"] = 3.0
    dump(child / "model_spec.json", spec)
    with pytest.raises(REJECTIONS):
        freeze_candidate(bundle, child, parent_receipt=parent, revision=revision())


def test_revise_requires_actual_model_or_generator_change(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    parent = freeze_candidate(bundle, candidate)
    child = clone_candidate(candidate)
    with pytest.raises(REJECTIONS):
        freeze_candidate(bundle, child, parent_receipt=parent, revision=revision("revise"))


def test_cross_bundle_parent_is_rejected(tmp_path):
    bundle, candidate = make_bundle(tmp_path, "one")
    parent = freeze_candidate(bundle, candidate)
    other_bundle, other_candidate = make_bundle(tmp_path, "two")
    with pytest.raises(REJECTIONS):
        freeze_candidate(other_bundle, other_candidate, parent_receipt=parent, revision=revision())


@pytest.mark.parametrize("bad_path", ["../outside.txt", "sources/../../outside.txt", "C:/outside.txt", "sources/paper.txt:stream", "sources\\paper.txt"])
def test_source_artifact_paths_cannot_escape_or_use_windows_aliases(tmp_path, bad_path):
    bundle, candidate = make_bundle(tmp_path)
    evidence = json.loads((candidate / "evidence.json").read_text(encoding="utf-8"))
    evidence["sources"][0]["artifacts"][0]["path"] = bad_path
    dump(candidate / "evidence.json", evidence)
    with pytest.raises(REJECTIONS):
        freeze_candidate(bundle, candidate)


def test_extra_candidate_file_is_committed(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    extra = candidate / "extra_notes.txt"
    extra.write_text("An additional submitted artifact.\n", encoding="utf-8")
    freeze_candidate(bundle, candidate)
    extra.write_text("Changed after submission.\n", encoding="utf-8")
    with pytest.raises(REJECTIONS):
        verify_candidate(bundle, candidate)


def test_added_unfrozen_file_is_not_silently_accepted(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    freeze_candidate(bundle, candidate)
    (candidate / "unfrozen.txt").write_text("Added after freeze.\n", encoding="utf-8")
    with pytest.raises(REJECTIONS):
        verify_candidate(bundle, candidate)


def test_changed_parent_invalidates_child_lineage(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    parent = freeze_candidate(bundle, candidate)
    child = clone_candidate(candidate)
    freeze_candidate(bundle, child, parent_receipt=parent, revision=revision())
    (candidate / "generator.py").write_text("# Modified parent\n", encoding="utf-8")
    with pytest.raises(REJECTIONS):
        verify_candidate(bundle, child)


def test_revision_budget_is_enforced(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    contract = task()
    contract["budget"]["revisions"] = 0
    dump(bundle / "task.json", contract)
    parent = freeze_candidate(bundle, candidate)
    child = clone_candidate(candidate)
    with pytest.raises(REJECTIONS):
        freeze_candidate(bundle, child, parent_receipt=parent, revision=revision())


def test_candidate_cannot_choose_two_generation_routes(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    _, output = frames()
    output.to_csv(candidate / "generated.csv", index=False)
    with pytest.raises(REJECTIONS):
        freeze_candidate(bundle, candidate)


@pytest.mark.parametrize("source", [
    "def generate(observed):\n    return observed\n",
    "async def generate(a, b, c):\n    return a\n",
    "def generate(a, b, c, *extra):\n    return a\n",
    "def generate(a, b, c, **extra):\n    return a\n",
    "def generate(a, b, c, *, option=None):\n    return a\n",
    "def generate(a, b, *, seed):\n    return a\n",
], ids=["one_argument", "async", "varargs", "kwargs", "keyword_only_extra", "keyword_only_seed"])
def test_invalid_generator_abi_is_rejected_by_public_check_and_freeze(tmp_path, source):
    bundle, candidate = make_bundle(tmp_path)
    program = candidate / "generator.py"
    program.write_text(source, encoding="utf-8")
    with pytest.raises(ValueError, match="generate"):
        validate_program(program)
    with pytest.raises(ValueError, match="generate"):
        freeze_candidate(bundle, candidate)
    assert not (candidate / "freeze.json").exists()


@pytest.mark.parametrize("signature", ["records, settings, random_seed", "records, /, settings, random_seed"])
def test_three_positional_generator_arguments_accept_arbitrary_names_without_execution(tmp_path, signature):
    bundle, candidate = make_bundle(tmp_path)
    program = candidate / "generator.py"
    program.write_text(
        "raise RuntimeError('Validation must not import or execute this source')\n"
        f"def generate({signature}):\n"
        "    raise RuntimeError('Validation must not call generate')\n",
        encoding="utf-8",
    )
    validate_program(program)
    receipt = freeze_candidate(bundle, candidate)
    assert receipt["route"] == "generator.py"
    assert verify_candidate(bundle, candidate)


def test_direct_table_route_checks_observed_cell_preservation(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    (candidate / "generator.py").unlink()
    _, output = frames()
    output.loc[0, "x"] += 0.2
    output.to_csv(candidate / "generated.csv", index=False)
    with pytest.raises(REJECTIONS):
        freeze_candidate(bundle, candidate)


def test_direct_table_route_can_be_frozen_without_executing_code(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    (candidate / "generator.py").unlink()
    _, output = frames()
    output.to_csv(candidate / "generated.csv", index=False)
    freeze_candidate(bundle, candidate)
    assert verify_candidate(bundle, candidate)


def test_candidate_outside_bundle_is_rejected(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    outside_bundle, outside_candidate = make_bundle(tmp_path, "outside")
    with pytest.raises(REJECTIONS):
        freeze_candidate(bundle, outside_candidate)


def test_symlink_source_rejected_when_os_permits_symlinks(tmp_path):
    bundle, candidate = make_bundle(tmp_path)
    source = bundle / "sources" / "paper.txt"
    outside = tmp_path / "outside.txt"
    outside.write_bytes(source.read_bytes())
    source.unlink()
    try:
        source.symlink_to(outside)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"OS does not permit this symlink fixture: {exc}")
    with pytest.raises(REJECTIONS):
        freeze_candidate(bundle, candidate)

