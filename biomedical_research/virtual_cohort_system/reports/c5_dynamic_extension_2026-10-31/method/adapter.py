"""Trusted transition plumbing; no language parser or scientific construction.

This C5 entry point consumes a controller-pinned, sealed-source authorization.
It uses the unchanged native harness for validation and isolated execution.
Hashes are commitments, not signatures against an administrator rewriting files.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

from cohort_harness import execution
from cohort_harness.contracts import (
    _hash, exact_keys, require, string_list, text, validate_input, validate_output,
    validate_task,
)
from cohort_harness.lifecycle import (
    _bundle, _path, _registry, read_json, read_table, safe_relative, sha256,
    verify_candidate,
)


def digest(value: dict) -> str:
    """Canonical JSON commitment, used by the controller before preparation."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def request_digest(raw_request: str) -> str:
    return hashlib.sha256(raw_request.encode("utf-8")).hexdigest()


def _write(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as out:
        json.dump(value, out, ensure_ascii=False, indent=2, allow_nan=False)
        out.write("\n")


def _copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as out:
        out.write(source.read_bytes())


def _origins(parent_root: Path, task: dict) -> list[dict]:
    observed = read_table(parent_root / "observed.csv", task) if task["mode"] == "completion" else None
    result = []
    for column in task["columns"]:
        origin = {"name": column["name"], "origin": "preserved_parent_input_origin_unverified"}
        if task["mode"] == "whole_cohort" or (column["role"] == "generated" and observed is None):
            origin["origin"] = "synthetic_generated"
        elif column["role"] == "generated":
            missing = observed[column["name"]].isna().tolist()
            origin.update(origin="mixed_synthetic_and_preserved_input_origin_unverified",
                          synthetic_row_positions=[i for i, value in enumerate(missing) if value],
                          preserved_input_row_positions=[i for i, value in enumerate(missing) if not value])
        result.append(origin)
    return result


def _parent(workspace: Path, reference: dict) -> tuple[Path, dict, dict]:
    exact_keys(reference, {"bundle", "run_id", "execution_sha256"}, where="parent")
    _hash(reference["execution_sha256"])
    root = _bundle(_path(workspace, reference["bundle"], file=False))
    # Native verifier also rejects unsafe run IDs and traversals.
    receipt = execution.verify_execution(root, reference["run_id"])
    require(receipt["status"] == "success", "Parent execution must be successful, not merely intact")
    path = _path(root, "executions/" + reference["run_id"] + "/execution.json")
    require(sha256(path) == reference["execution_sha256"], "Pinned parent execution changed")
    task = read_json(_path(root, "task.json"))
    validate_task(task)
    return root, receipt, task


def _source(workspace: Path, reference: dict) -> tuple[Path, dict]:
    exact_keys(reference, {"bundle", "registry_sha256"}, where="source")
    _hash(reference["registry_sha256"])
    root = _bundle(_path(workspace, reference["bundle"], file=False))
    require(sha256(_path(root, "registry.json")) == reference["registry_sha256"],
            "Pinned source registry changed")
    _registry(root)  # Existing approved records and artifact hashes; creates no approvals.
    return root, read_json(root / "registry.json")


def _decision(raw_request: str, decision: dict, parent_task: dict, registry: dict) -> None:
    text(raw_request, "raw request")
    exact_keys(decision, {"schema_version", "action", "raw_request_sha256", "population",
                         "row_id", "n_rows", "requested_variables", "reason", "evidence_refs",
                         "unresolved_evidence"}, where="Agent decision")
    require(type(decision["schema_version"]) is int and decision["schema_version"] == 1,
            "Invalid decision schema")
    require(decision["action"] in {"reuse", "extend", "new_population", "revise", "clarify"},
            "Invalid decision action")
    require(decision["raw_request_sha256"] == request_digest(raw_request), "Raw request hash mismatch")
    for key in ("population", "row_id", "reason"):
        text(decision[key], key)
    require(type(decision["n_rows"]) is int and decision["n_rows"] > 0, "Invalid requested row count")
    string_list(decision["evidence_refs"], "evidence references")
    string_list(decision["unresolved_evidence"], "unresolved evidence")
    source_ids = {entry["source_id"] for entry in registry["artifacts"]}
    require(set(decision["evidence_refs"]) <= source_ids, "Decision cites an unapproved source")
    columns = decision["requested_variables"]
    require(isinstance(columns, list) and all(isinstance(c, dict) for c in columns),
            "requested_variables must contain typed column definitions")
    names = [c.get("name") for c in columns]
    require(all(isinstance(name, str) for name in names) and len(set(names)) == len(names),
            "Duplicate or invalid requested variable")
    action = decision["action"]
    same_population = all(decision[key] == parent_task[key] for key in ("population", "row_id", "n_rows"))
    if action in {"reuse", "extend", "revise"}:
        require(same_population, "Population, identifier or row-count change requires new_population or clarify")
    if action == "new_population":
        require(not same_population, "new_population requires an explicit population/row identity change")
    if action == "reuse":
        original = {c["name"]: c for c in parent_task["columns"]}
        require(bool(columns), "Reuse needs requested variables")
        require(all(c["name"] in original and c == original[c["name"]] for c in columns),
                "Reuse requires available variables with unchanged definitions")
    if action == "extend":
        old = parent_task["columns"]
        expected = [dict(c, role="identifier" if c["role"] == "identifier" else "observed") for c in old]
        require(len(columns) > len(old) and columns[:len(old)] == expected,
                "Extension must preserve old fields, units, definitions and order")
        require(all(c.get("role") == "generated" for c in columns[len(old):]),
                "Only new generated fields may be appended")
        trial = dict(parent_task, mode="enrichment", columns=columns)
        validate_task(trial)


def _authorization(authorization: dict, expected_sha256: str, destination: str) -> None:
    _hash(expected_sha256)
    require(digest(authorization) == expected_sha256, "Controller authorization hash mismatch")
    exact_keys(authorization, {"schema_version", "authorization_id", "destination", "max_extensions",
                              "parent", "source", "decision_sha256", "child_task_id", "child_budget"},
               where="transition authorization")
    require(type(authorization["schema_version"]) is int and authorization["schema_version"] == 1,
            "Invalid authorization schema")
    text(authorization["authorization_id"], "authorization ID")
    require(authorization["destination"] == destination, "Authorization is bound to another destination")
    safe_relative(destination)
    require(type(authorization["max_extensions"]) is int and authorization["max_extensions"] == 1,
            "This adapter admits one extension per exact destination authorization")
    _hash(authorization["decision_sha256"])
    text(authorization["child_task_id"], "child task ID")
    # C5 is explicitly sealed. A future retrieval-capable transition needs a
    # controller's shared global budget/session design, not a new empty session.
    require(authorization["child_budget"] == {"source_queries": 0, "source_downloads": 0, "revisions": 0},
            "C5 sealed transition requires the explicitly authorized zero task budget")
    require(all(type(v) is int for v in authorization["child_budget"].values()), "Budget must use integers")


def prepare_transition(workspace: str | Path, destination: str, *, raw_request: str,
                       decision: dict, authorization: dict, authorization_sha256: str) -> dict:
    """Write a new routing record; only extend also creates a native child bundle.

    All paths are workspace-relative and pinned by the controller authorization.
    Generator/evidence/model submission and freezing happen separately afterward.
    """
    workspace = _bundle(workspace)
    _authorization(authorization, authorization_sha256, destination)
    require(digest(decision) == authorization["decision_sha256"], "Pinned Agent decision changed")
    parent_root, parent_receipt, parent_task = _parent(workspace, authorization["parent"])
    source_root, registry = _source(workspace, authorization["source"])
    _decision(raw_request, decision, parent_task, registry)
    output = _path(workspace, destination, file=False)
    require(not output.exists(), "Transition destination already exists; artifacts cannot be overwritten")
    require(not output.is_relative_to(parent_root) and not parent_root.is_relative_to(output),
            "Transition cannot overlap the parent bundle")
    require(not output.is_relative_to(source_root) and not source_root.is_relative_to(output),
            "Transition cannot overlap the source intake")
    child_task = None
    if decision["action"] == "extend":
        require(authorization["child_task_id"] != parent_task["task_id"], "Extension requires an explicit new task ID")
        child_task = deepcopy(parent_task)
        child_task.update(task_id=authorization["child_task_id"], mode="enrichment",
                          columns=deepcopy(decision["requested_variables"]), budget=deepcopy(authorization["child_budget"]))
        validate_task(child_task)
        generated_path = _path(parent_root, "executions/" + authorization["parent"]["run_id"] + "/output/generated.csv")
        validate_input(read_table(generated_path, child_task), child_task)
    output.mkdir(parents=True)
    _write(output / "authorization.json", authorization)
    _write(output / "agent_decision.json", decision)
    with (output / "raw_request.txt").open("x", encoding="utf-8", newline="") as out:
        out.write(raw_request)
    bindings = {name: sha256(output / name) for name in ("authorization.json", "agent_decision.json", "raw_request.txt")}
    if child_task is not None:
        child = output / "child"
        child.mkdir()
        _write(child / "task.json", child_task)
        _copy(source_root / "registry.json", child / "registry.json")
        for entry in registry["artifacts"]:
            target = _path(child, entry["path"], file=False)
            if not target.exists():
                _copy(_path(source_root, entry["path"]), target)
        _copy(generated_path, child / "observed.csv")
        provenance = {
            "schema_version": 1, "parent": authorization["parent"],
            "parent_output_sha256": sha256(generated_path),
            "observed_input_sha256": sha256(child / "observed.csv"),
            "observed_means": "fixed input in the native contract, not real-patient measurement",
            "real_patient_measurements_claimed": False,
            "columns": _origins(parent_root, parent_task),
        }
        _write(output / "input_provenance.json", provenance)
        for path in child.rglob("*"):
            if path.is_file():
                bindings[path.relative_to(output).as_posix()] = sha256(path)
        bindings["input_provenance.json"] = sha256(output / "input_provenance.json")
    record = {
        "schema_version": 1, "kind": "variable_transition", "action": decision["action"],
        "status": "prepared" if child_task else "routed", "destination": destination,
        "authorization_sha256": authorization_sha256, "decision_sha256": digest(decision),
        "raw_request_sha256": request_digest(raw_request), "bindings": bindings,
        "parent": authorization["parent"], "source": authorization["source"],
        "child_bundle": destination + "/child" if child_task else None,
        "execution_permitted": child_task is not None,
        "scientific_validity": "not_assessed", "agent_isolation": "not_provided",
    }
    # Recheck external commitments before publishing the preparation receipt.
    _parent(workspace, authorization["parent"])
    _source(workspace, authorization["source"])
    _write(output / "transition.json", record)
    return record


def verify_transition(workspace: str | Path, destination: str, *, transition_sha256: str) -> dict:
    """Verify a controller-pinned transition and its still-current parent/source."""
    workspace = _bundle(workspace)
    root = _bundle(_path(workspace, destination, file=False))
    _hash(transition_sha256)
    require(sha256(_path(root, "transition.json")) == transition_sha256, "Pinned transition changed")
    record = read_json(root / "transition.json")
    require(record["destination"] == destination, "Transition destination changed")
    for name, expected in record["bindings"].items():
        require(sha256(_path(root, name)) == expected, "Prepared transition artifact changed: " + name)
    authorization = read_json(_path(root, "authorization.json"))
    _authorization(authorization, record["authorization_sha256"], destination)
    parent_root, parent_receipt, task = _parent(workspace, authorization["parent"])
    source_root, registry = _source(workspace, authorization["source"])
    decision = read_json(root / "agent_decision.json")
    require(digest(decision) == authorization["decision_sha256"] == record["decision_sha256"], "Decision changed")
    raw_request = (root / "raw_request.txt").read_bytes().decode("utf-8")
    _decision(raw_request, decision, task, registry)
    require(record["action"] == decision["action"], "Transition action mismatch")
    if record["action"] == "extend":
        child = _bundle(_path(workspace, record["child_bundle"], file=False))
        require(sha256(child / "registry.json") == authorization["source"]["registry_sha256"], "Child registry changed")
        _registry(child)
        validate_input(read_table(child / "observed.csv", read_json(child / "task.json")), read_json(child / "task.json"))
        parent_output = _path(parent_root, "executions/" + authorization["parent"]["run_id"] + "/output/generated.csv")
        require(sha256(child / "observed.csv") == sha256(parent_output), "Parent output was not copied exactly")
    return record


def _preservation(workspace: Path, record: dict, run_id: str, transition_sha256: str) -> dict:
    child = _bundle(_path(workspace, record["child_bundle"], file=False))
    receipt = execution.verify_execution(child, run_id)
    preserved = receipt["status"] == "success"
    task = read_json(child / "task.json")
    output = _path(child, "executions/" + run_id + "/output/generated.csv", file=False)
    if preserved:
        validate_output(read_table(child / "observed.csv", task), read_table(output, task), task)
    return {"schema_version": 1, "kind": "extension_preservation", "run_id": run_id,
            "transition_sha256": transition_sha256, "execution_status": receipt["status"],
            "execution_sha256": sha256(child / "executions" / run_id / "execution.json"),
            "old_cells_and_row_order_preserved": preserved,
            "preservation_status": "verified" if preserved else "not_verified", "n_rows": task["n_rows"],
            "preserved_columns": [c["name"] for c in task["columns"] if c["role"] != "generated"],
            "observed_sha256": sha256(child / "observed.csv"),
            "output_sha256": sha256(output) if output.is_file() else None,
            "scientific_validity": "not_assessed"}


def execute_extension(workspace: str | Path, destination: str, *, transition_sha256: str,
                      candidate: str, run_id: str, seed: int, **limits) -> dict:
    """Run only a frozen generator through the unchanged isolated backend."""
    workspace = _bundle(workspace)
    record = verify_transition(workspace, destination, transition_sha256=transition_sha256)
    require(record["action"] == "extend", "Routing-only decisions cannot execute")
    child = _path(workspace, record["child_bundle"], file=False)
    frozen = verify_candidate(child, candidate)
    require(frozen["route"] == "generator.py", "Extension execution requires the isolated generator route")
    require(set(limits) <= {"timeout_seconds", "memory_mb", "output_bytes", "log_bytes"},
            "Only native resource limits may be supplied; runtime/backend is fixed")
    execution.run_candidate(child, candidate, run_id, seed, **limits)
    verify_transition(workspace, destination, transition_sha256=transition_sha256)
    report = _preservation(workspace, record, run_id, transition_sha256)
    reports = _path(workspace, destination + "/preservation", file=False)
    reports.mkdir(exist_ok=True)
    _write(_path(reports, run_id + ".json", file=False), report)
    return report


def verify_preservation(workspace: str | Path, destination: str, run_id: str, *, transition_sha256: str) -> dict:
    """Recompute the report from verified native artifacts, never execute code."""
    workspace = _bundle(workspace)
    record = verify_transition(workspace, destination, transition_sha256=transition_sha256)
    require(record["action"] == "extend", "Only extensions have preservation reports")
    expected = _preservation(workspace, record, run_id, transition_sha256)
    actual = read_json(_path(workspace, destination + "/preservation/" + run_id + ".json"))
    require(actual == expected, "Preservation report differs from verified execution")
    return actual
