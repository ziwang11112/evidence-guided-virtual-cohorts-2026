"""Invented fixture plumbing tests. Mock execution is NOT isolation evidence."""
from copy import deepcopy
import json
from pathlib import Path

import pandas as pd
import pytest

import adapter as a
from cohort_harness import execution as ex
from cohort_harness.contracts import ContractError
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def fixture(tmp_path, mode="whole_cohort"):
    root = tmp_path / "parent"
    candidate = root / "candidates" / "initial"
    candidate.mkdir(parents=True)
    columns = [
        {"name": "subject_id", "kind": "string", "unit": "identifier", "role": "identifier", "nullable": False},
        {"name": "x1", "kind": "number", "unit": "invented_unit", "role": "generated", "nullable": False},
        {"name": "x2", "kind": "number", "unit": "invented_unit", "role": "generated", "nullable": False},
    ]
    task = {"schema_version": 1, "task_id": "declared-invented-parent", "mode": mode,
            "population": "Three explicitly invented interface rows; no patients or population inference",
            "row_id": "subject_id", "n_rows": 3, "columns": columns,
            "information_policy": {"mode": "published_evidence", "excluded_cohorts": [], "allowed_tools": []},
            "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 0}}
    write(root / "task.json", task)
    if mode == "completion":
        pd.DataFrame({"subject_id": ["f01", "f02", "f03"], "x1": [0.1, None, None],
                      "x2": [None, 4.0, None]}).to_csv(root / "observed.csv", index=False)
    source = root / "sources" / "fixture.txt"
    source.parent.mkdir()
    source.write_text("Declared invented fixture only. Not a publication or patient measurement.\n")
    entry = {"source_id": "fixture", "path": "sources/fixture.txt", "sha256": sha256(source),
             "origin": "fixture", "screening": "approved"}
    write(root / "registry.json", {"artifacts": [entry]})
    evidence = {"schema_version": 1, "sources": [{"id": "fixture", "identifier": "fixture:invented",
                "population": task["population"], "measurement": "Invented constants", "cohort_ids": ["fixture"],
                "artifacts": [{k: entry[k] for k in ("path", "sha256")}]}],
                "items": [{"id": "context", "source_id": "fixture", "locator": "line 1", "kind": "contextual",
                           "variables": ["x1", "x2"], "estimate": None, "unit": "",
                           "uncertainty": {"kind": "not_reported"}, "adjustment": [],
                           "selection": "All invented rows", "applicability": "Plumbing test only"}]}
    write(candidate / "evidence.json", evidence)
    write(candidate / "model_spec.json", {"parameters": {}, "assumptions": [], "parameter_provenance": {}})
    (candidate / "decision.md").write_text("Explicitly invented table; no scientific inference.\n")
    write(candidate / "checks.json", {"scope": "fixture_only", "records": [{"name": "science",
          "status": "not_computable", "detail": "Not a scientific construction; native contracts check the table."}], "artifacts": []})
    pd.DataFrame({"subject_id": ["f01", "f02", "f03"], "x1": [0.1, 0.2, 0.3],
                  "x2": [3.0, 4.0, 5.0]}).to_csv(candidate / "generated.csv", index=False)
    freeze_candidate(root, candidate)
    assert ex.run_candidate(root, candidate, "parent_run", 1)["status"] == "success"
    raw = "Please retain these invented rows and add the new x3 field."
    decision = {"schema_version": 1, "action": "extend", "raw_request_sha256": a.request_digest(raw),
                "population": task["population"], "row_id": task["row_id"], "n_rows": task["n_rows"],
                "requested_variables": [dict(c, role="identifier" if c["role"] == "identifier" else "observed") for c in columns] +
                    [{"name": "x3", "kind": "number", "unit": "new_invented_unit", "role": "generated", "nullable": False}],
                "reason": "Agent-authored fixture decision, not parsed by the adapter.",
                "evidence_refs": ["fixture"], "unresolved_evidence": ["No biological applicability assessed."]}
    auth = {"schema_version": 1, "authorization_id": "fixture-only-transition", "destination": "transition",
            "max_extensions": 1, "parent": {"bundle": "parent", "run_id": "parent_run",
                  "execution_sha256": sha256(root / "executions/parent_run/execution.json")},
            "source": {"bundle": "parent", "registry_sha256": sha256(root / "registry.json")},
            "decision_sha256": a.digest(decision), "child_task_id": "declared-invented-child", "child_budget": task["budget"]}
    return raw, decision, auth


def prepare(tmp_path, values):
    raw, decision, auth = values
    auth["decision_sha256"] = a.digest(decision)
    record = a.prepare_transition(tmp_path, auth["destination"], raw_request=raw, decision=decision,
                                  authorization=auth, authorization_sha256=a.digest(auth))
    pin = sha256(tmp_path / auth["destination"] / "transition.json")
    assert a.verify_transition(tmp_path, auth["destination"], transition_sha256=pin) == record
    return record, pin


def child_program(tmp_path):
    parent = tmp_path / "parent/candidates/initial"
    child = tmp_path / "transition/child"
    candidate = child / "candidates/initial"
    candidate.mkdir(parents=True)
    for name in ("evidence.json", "model_spec.json", "decision.md", "checks.json"):
        (candidate / name).write_bytes((parent / name).read_bytes())
    # If the adapter accidentally imports this module on the host, the test fails.
    (candidate / "generator.py").write_text("raise RuntimeError('DO NOT IMPORT ON HOST')\ndef generate(observed, spec, seed):\n    return observed\n")
    freeze_candidate(child, candidate)
    return child


def backend(monkeypatch, change=None, returncode=0):
    monkeypatch.setattr(ex, "_runtime_manifest", lambda runtime: {"mock": True, "isolation_proven": False})
    def capture(command, cwd, timeout, limit, stdout_path, stderr_path):
        task = read_json(cwd / "input/task.json")
        frame = ex.read_table(cwd / "input/observed.csv", task).assign(x3=[10.0, 11.0, 12.0])
        if change:
            frame = change(frame)
        frame.to_csv(cwd / "output/generated.csv", index=False)
        write(cwd / "output/worker_report.json", {"status": "completed", "generator_started": True})
        stdout_path.write_text("MOCK: no scientific generator or sandbox executed.\n")
        stderr_path.write_text("")
        return {"returncode": returncode, "host_timeout": False, "logs": {}}
    monkeypatch.setattr(ex, "_capture", capture)


def test_extension_copies_exact_synthetic_input_and_zero_budget(tmp_path):
    values = fixture(tmp_path)
    before = sha256(tmp_path / "parent/executions/parent_run/output/generated.csv")
    record, pin = prepare(tmp_path, values)
    child = tmp_path / record["child_bundle"]
    assert sha256(child / "observed.csv") == before
    assert read_json(child / "task.json")["budget"] == values[2]["child_budget"]
    provenance = read_json(tmp_path / "transition/input_provenance.json")
    assert not provenance["real_patient_measurements_claimed"]
    assert {c["origin"] for c in provenance["columns"]} == {"synthetic_generated"}
    assert not (child / "gateway").exists()
    assert not (child / "candidates").exists()
    with pytest.raises(ContractError, match="already exists"):
        prepare(tmp_path, values)


def test_completion_parent_does_not_relabel_preserved_cells_as_synthetic(tmp_path):
    prepare(tmp_path, fixture(tmp_path, mode="completion"))
    origins = read_json(tmp_path / "transition/input_provenance.json")["columns"]
    assert origins[1]["synthetic_row_positions"] == [1, 2]
    assert origins[1]["preserved_input_row_positions"] == [0]
    assert origins[2]["synthetic_row_positions"] == [0, 2]
    assert "unverified" in origins[1]["origin"]


def test_raw_request_is_bound_without_keyword_parsing_or_newline_changes(tmp_path):
    raw, decision, auth = fixture(tmp_path)
    raw = "reuse new_population revise clarify are words, not parser commands.\r\nAgent decision follows."
    decision["raw_request_sha256"] = a.request_digest(raw)
    record, _ = prepare(tmp_path, (raw, decision, auth))
    assert record["action"] == "extend"
    assert (tmp_path / "transition/raw_request.txt").read_bytes() == raw.encode()


@pytest.mark.parametrize("action", ["reuse", "new_population", "revise", "clarify"])
def test_explicit_routes_never_execute_or_make_child(tmp_path, action):
    raw, decision, auth = fixture(tmp_path)
    decision["action"] = action
    if action == "reuse":
        decision["requested_variables"] = [read_json(tmp_path / "parent/task.json")["columns"][1]]
    if action == "new_population":
        decision["population"] = "Different explicitly requested invented population"
    record, pin = prepare(tmp_path, (raw, decision, auth))
    assert record["status"] == "routed" and record["child_bundle"] is None
    assert not (tmp_path / "transition/child").exists()
    with pytest.raises(ContractError, match="cannot execute"):
        a.execute_extension(tmp_path, "transition", transition_sha256=pin, candidate="candidates/initial", run_id="run", seed=1)


@pytest.mark.parametrize("change", ["unit", "remove", "reorder", "population", "rows", "duplicate", "reuse_missing", "new_unchanged"])
def test_inconsistent_decisions_rejected_before_writes(tmp_path, change):
    raw, decision, auth = fixture(tmp_path)
    if change == "unit": decision["requested_variables"][1]["unit"] = "redefined"
    if change == "remove": decision["requested_variables"].pop(1)
    if change == "reorder": decision["requested_variables"][1:3] = reversed(decision["requested_variables"][1:3])
    if change == "population": decision["population"] = "changed"
    if change == "rows": decision["n_rows"] = 2
    if change == "duplicate": decision["requested_variables"][-1]["name"] = "x1"
    if change == "reuse_missing": decision["action"] = "reuse"
    if change == "new_unchanged": decision["action"] = "new_population"
    with pytest.raises(ContractError): prepare(tmp_path, (raw, decision, auth))
    assert not (tmp_path / "transition").exists()


@pytest.mark.parametrize("field", ["raw", "decision", "auth", "parent", "source"])
def test_external_commitment_tampering(tmp_path, field):
    raw, decision, auth = fixture(tmp_path)
    pin = a.digest(auth)
    if field == "raw": raw += " changed"
    if field == "decision": decision["reason"] += " changed"
    if field == "auth": auth["child_task_id"] = "changed"
    if field == "parent": (tmp_path / "parent/executions/parent_run/output/generated.csv").write_text("tamper")
    if field == "source": (tmp_path / "parent/sources/fixture.txt").write_text("tamper")
    with pytest.raises(ContractError):
        a.prepare_transition(tmp_path, "transition", raw_request=raw, decision=decision, authorization=auth, authorization_sha256=pin)


@pytest.mark.parametrize("destination", ["../escape", "parent/extension", "C:/escape", "transition/../../escape"])
def test_paths_cannot_escape_or_overlap(tmp_path, destination):
    raw, decision, auth = fixture(tmp_path)
    auth["destination"] = destination
    with pytest.raises(ContractError): prepare(tmp_path, (raw, decision, auth))


def test_no_budget_reset_or_unapproved_source(tmp_path):
    raw, decision, auth = fixture(tmp_path)
    auth["child_budget"]["source_queries"] = 1
    with pytest.raises(ContractError, match="zero task budget"): prepare(tmp_path, (raw, decision, auth))
    auth["child_budget"]["source_queries"] = 0
    decision["evidence_refs"] = ["not-approved"]
    with pytest.raises(ContractError, match="unapproved"): prepare(tmp_path, (raw, decision, auth))


def test_failed_verified_parent_is_not_a_successful_parent(tmp_path, monkeypatch):
    raw, decision, auth = fixture(tmp_path)
    original = ex.verify_execution
    def failed(*args):
        return dict(original(*args), status="failed")
    monkeypatch.setattr(ex, "verify_execution", failed)
    with pytest.raises(ContractError, match="must be successful"): prepare(tmp_path, (raw, decision, auth))


@pytest.mark.parametrize("mutation", [None, "cells", "rows", "discard", "schema", "failure"])
def test_native_mocked_execution_preservation_and_failure(tmp_path, monkeypatch, mutation):
    record, pin = prepare(tmp_path, fixture(tmp_path))
    child = child_program(tmp_path)
    changes = {"cells": lambda f: f.assign(x1=f.x1 + 1), "rows": lambda f: f.iloc[::-1],
               "discard": lambda f: f.iloc[:-1], "schema": lambda f: f[["subject_id", "x2", "x1", "x3"]]}
    backend(monkeypatch, changes.get(mutation), returncode=1 if mutation == "failure" else 0)
    report = a.execute_extension(tmp_path, "transition", transition_sha256=pin, candidate="candidates/initial", run_id="mock", seed=9)
    assert report["old_cells_and_row_order_preserved"] is (mutation is None)
    assert report["execution_status"] == ("success" if mutation is None else "failed")
    assert a.verify_preservation(tmp_path, "transition", "mock", transition_sha256=pin) == report
    assert (child / "executions/mock/execution.json").is_file()
    report_path = tmp_path / "transition/preservation/mock.json"
    changed = read_json(report_path)
    changed["old_cells_and_row_order_preserved"] = not changed["old_cells_and_row_order_preserved"]
    write(report_path, changed)
    with pytest.raises(ContractError, match="report differs"):
        a.verify_preservation(tmp_path, "transition", "mock", transition_sha256=pin)


def test_missing_backend_has_no_host_fallback(tmp_path, monkeypatch):
    _, pin = prepare(tmp_path, fixture(tmp_path))
    child_program(tmp_path)
    def unavailable(runtime): raise ValueError("Declared unavailable backend fixture")
    monkeypatch.setattr(ex, "_runtime_manifest", unavailable)
    monkeypatch.setattr(ex, "_capture", lambda *args: pytest.fail("must not execute any fallback"))
    report = a.execute_extension(tmp_path, "transition", transition_sha256=pin, candidate="candidates/initial", run_id="unavailable", seed=1)
    assert report["execution_status"] == "failed" and not report["old_cells_and_row_order_preserved"]


@pytest.mark.parametrize("path", ["child/observed.csv", "child/task.json", "agent_decision.json", "child/registry.json"])
def test_prepared_artifact_tampering(tmp_path, path):
    _, pin = prepare(tmp_path, fixture(tmp_path))
    with (tmp_path / "transition" / path).open("a") as stream: stream.write("tampered")
    with pytest.raises(ContractError, match="artifact changed"):
        a.verify_transition(tmp_path, "transition", transition_sha256=pin)
