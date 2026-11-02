"""New one-pass root assembly/runner integration on changed invented inputs.

Package admission is an invented input boundary; real compiler, assembler,
bridge, case guard, semantic receipt, and descriptive collector are exercised.
No real generator, ledger authorization, network or target reference is used.
"""
import copy
import sys
from pathlib import Path
from types import SimpleNamespace
import socket
import subprocess

import pytest

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))
import k01_sources as k
import bundle_assembly as assembly
import case_execution as runner
from test_k01_sources import invented_state, review, write


@pytest.fixture
def inputs(monkeypatch):
    state = invented_state()
    compiled = k._compile(state)
    package = {
        "case_id": "K01", "design_sha256": state["design_sha256"],
        "request_files": {"task_template.json": k.encoded(state["task"]),
                          "selected_source_evidence.json": state["packet_bytes"],
                          "descriptive_diagnostic_plan.json": k.encoded(state["plan"])},
        "source_files": {k.ARTIFACT: state["packet_bytes"]}, "evidence": compiled["evidence"],
        "templates": compiled["source_context_templates"], "registrations": compiled["registration_requirements"],
        "task": state["task"], "target_id": k.TARGET, "target_metadata": {"invented": True},
        "target_descriptor": {"population": state["task"]["population"], "n_rows": 5000, "measurement": "Invented target protocol; no empirical source fit"},
    }
    # Replace only fixture admission inputs, not compilation or verification.
    monkeypatch.setattr(k, "_committed", lambda: state)
    monkeypatch.setattr(assembly, "load_package", lambda case_id: copy.deepcopy(package))
    authoring = {"context_assumption_ids": {c: ["invented-" + str(i)] for i, c in enumerate([*k.SOURCE_CONTEXTS, k.TARGET])},
                 "context_varying_parameters": [], "descriptive_proxies": {}}
    contexts = {t["id"]: {"population": t["recipe"]["population"], "n_rows": 5000, "measurement": t["recipe"]["measurement"]["description"], "inputs": {}} for t in package["templates"]}
    contexts[k.TARGET] = {**package["target_descriptor"], "inputs": {}}
    spec = {"parameters": {"active_context": k.TARGET, "contexts": contexts},
            "assumptions": [{"id": "invented-" + str(i), "description": "Invented context meaning " + str(i)} for i in range(3)],
            "parameter_provenance": {n: {"evidence_ids": [], "assumption_ids": ["invented-2"], "derivation": "Invented nonclinical context fixture"} for n in ("active_context", "contexts")}}
    return state, compiled, package, authoring, spec


def prepare(root, inputs):
    state, compiled, package, authoring, spec = inputs
    assembly.prepare_bundle("K01", "A01", root, {"curator_id": "invented-curator", "reviewed_utc": "2026-11-02T00:00:00Z", "reason": "Invented fixture admission only", "package_sha256": assembly.package_digest(package)})
    candidate = root / "candidates/invented"
    candidate.mkdir(parents=True)
    plan = assembly.build_bridge_plan(package, "A01", "initial", spec, authoring)
    declaration = k.build_declaration(compiled, {c: authoring["context_assumption_ids"][c] for c in k.SOURCE_CONTEXTS}, model_spec=spec)
    declaration["review"] = review(k.declaration_digest(declaration))
    for name, value in {"model_spec.json": spec, "evidence.json": compiled["evidence"], "context_authoring.json": authoring,
                        k.bridge.PLAN: plan, k.DECLARATION: declaration,
                        "checks.json": {"scope": "fixture_only", "records": [{"name": "invented", "status": "not_computable", "detail": "No real generator execution"}], "artifacts": []}}.items():
        write(candidate / name, value)
    (candidate / "decision.md").write_text("Invented integration only", encoding="utf-8")
    (candidate / "generator.py").write_text('def generate(observed, specification, seed):\n    raise RuntimeError("This fixture source is never executed")\n', encoding="utf-8")
    k.lifecycle.freeze_candidate(root, candidate)
    k.bridge.prepare(root, "invented")
    requests = k.bridge.binding_requests(root, "invented")
    k.bridge.seal(root, "invented", {c: {"binding_review": review(r["binding_sha256"]), "supplement_review": None, "proxy_reviews": {}} for c, r in requests.items()})
    return plan


def process_boundary(monkeypatch, *, wrong_context=False):
    events = []
    monkeypatch.setitem(sys.modules, "campaign_control", SimpleNamespace(verify_dispatch=lambda *a: {"scope": "invented authorization only"}))
    for owner, name in [(subprocess, "run"), (subprocess, "Popen"), (socket, "create_connection")]:
        monkeypatch.setattr(owner, name, lambda *a, **kw: pytest.fail("No OS process/network authorized"))
    monkeypatch.setattr(k.execution, "_runtime_manifest", lambda runtime: {"fixture": "no actual runtime"})
    monkeypatch.setattr(k.execution, "_command", lambda *a, **kw: ["invented-mocked-launch"])
    original_guard = runner._guard
    def guard(frame, task, package, context_id):
        events.append(("guard", context_id))
        return original_guard(frame, task, package, context_id)
    monkeypatch.setattr(runner, "_guard", guard)
    original_semantic = k.semantic.collect_feedback
    def semantic(root, candidate, run_id, feedback_id):
        context = k.lifecycle.read_json(Path(root) / candidate / "model_spec.json")["parameters"]["active_context"]
        events.append(("semantic", context))
        return original_semantic(root, candidate, run_id, feedback_id)
    monkeypatch.setattr(k.semantic, "collect_feedback", semantic)
    def capture(command, cwd, timeout, limit, stdout_path, stderr_path):
        context = k.lifecycle.read_json(cwd / "input/model_spec.json")["parameters"]["active_context"]
        base = 62 if "mind" in context else 26 if "ayele" in context else 42
        if wrong_context and "mind" in context:
            base = 40
        (cwd / "output/generated.csv").write_text("id,age,sex,bmi,glucose\n" + "".join(f"invented-{i},{base+i%2},{'F' if i%2 else 'M'},{10+i%3},{1+i%2}\n" for i in range(5000)), encoding="utf-8")
        write(cwd / "output/worker_report.json", {"status": "completed", "generator_started": True})
        stdout_path.write_text("Invented mocked execution", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        return {"returncode": 0, "host_timeout": False, "logs": {}}
    monkeypatch.setattr(k.execution, "_capture", capture)
    return events


def test_real_root_assembly_runner_and_eighteen_descriptives(tmp_path, inputs, monkeypatch):
    events = process_boundary(monkeypatch)
    root = tmp_path / "invented"
    plan = prepare(root, inputs)
    result = runner.execute_case_stage(root, "invented", "invented-ledger-not-read", "K01", "A01", "initial")
    assert result["all_guards_valid"] is True and result["all_slots_successful"] is True
    reports = [k.collect_descriptives(root, "invented", t["id"]) for t in plan["trials"] if t["context_id"] in k.SOURCE_CONTEXTS]
    assert sum(len(r["checks"]) for r in reports) == 18
    for context in k.SOURCE_CONTEXTS:
        assert events.index(("guard", context)) < events.index(("semantic", context))
    assert not any(event == ("semantic", k.TARGET) for event in events)
    assert all(c["strict_source_difference"] is None for r in reports for c in r["checks"])
    assert all(c["computed"]["diagnostic"]["n_used"] == 5000 for r in reports for c in r["checks"])


def test_wrong_context_rows_fail_before_semantic_feedback(tmp_path, inputs, monkeypatch):
    events = process_boundary(monkeypatch, wrong_context=True)
    root = tmp_path / "invented"
    plan = prepare(root, inputs)
    result = runner.execute_case_stage(root, "invented", "invented-ledger-not-read", "K01", "A01", "initial")
    context = "source_mind_china_2019"
    trial = next(t for t in plan["trials"] if t["context_id"] == context)
    assert ("guard", context) in events and ("semantic", context) not in events
    assert result["all_guards_valid"] is False
    assert next(t for t in result["trials"] if t["trial_id"] == trial["id"])["trial_status"] == "error"
    with pytest.raises(ValueError, match="Successful verified source slot"):
        k.collect_descriptives(root, "invented", trial["id"])
    assert not (root / k.FOLDER).exists()


def test_assumption_prose_change_cannot_reuse_independent_declaration_review(inputs):
    _, compiled, _, authoring, spec = inputs
    mapping = {c: authoring["context_assumption_ids"][c] for c in k.SOURCE_CONTEXTS}
    original = k.build_declaration(compiled, mapping, model_spec=spec)
    approval = review(k.declaration_digest(original))
    changed_spec = copy.deepcopy(spec)
    changed_spec["assumptions"][0]["description"] = "Different invented scientific assumption under the same ID"
    changed = k.build_declaration(compiled, mapping, model_spec=changed_spec)
    assert changed["model_spec_sha256"] != original["model_spec_sha256"]
    with pytest.raises(ValueError, match="commitment mismatch"):
        k.bridge.supplement._review(approval, k.declaration_digest(changed))
