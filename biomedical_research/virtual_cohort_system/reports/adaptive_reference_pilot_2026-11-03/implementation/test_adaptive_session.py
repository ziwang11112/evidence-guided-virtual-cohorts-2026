"""Controller-only tests: mocked execution creates no scientific data rows."""
import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("adaptive_session", Path(__file__).with_name("adaptive_session.py"))
session_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_module)
S = session_module


@pytest.fixture
def fresh(tmp_path, monkeypatch):
    root = tmp_path / "new"
    bundle = root / "b"
    bundle.mkdir(parents=True)
    task = {"schema_version": 1, "task_id": "arbitrary-current-task", "mode": "whole_cohort",
            "population": "Invented controller test; no patients or scientific generation",
            "row_id": "id", "n_rows": 3000,
            "columns": [{"name": "id", "kind": "string", "unit": "identifier", "role": "identifier", "nullable": False},
                        {"name": "x", "kind": "number", "unit": "u", "role": "generated", "nullable": False}],
            "information_policy": {"mode": "prior_only", "excluded_cohorts": [], "allowed_tools": []},
            "budget": {"source_queries": 4, "source_downloads": 2, "revisions": 1}}
    S.write(bundle / "task.json", task)
    profile = tmp_path / "profile.json"
    S.write(profile, {"required_diagnostic_ids": ["d"], "required_analysis_ids": ["a"]})
    evaluator = tmp_path / "evaluator.py"
    evaluator.write_text("def evaluate(bundle,candidate,run_id,profile):\n    return {'diagnostics':[{'id':'d','value':1}], 'analyses':[{'id':'a','value':2}]}\n")
    S.initialize(root, bundle, profile, evaluator, author_id="actual-agent-1")
    state = S.Session(root)
    state.dispatch("initial", "actual-agent-1")

    def freeze(b, c, parent=None, revision=None):
        S.write(Path(b) / c / "freeze.json", {"route": "generator.py", "revision_index": int(parent is not None)})
        return verify(b, c)

    def verify(b, c):
        return S.lifecycle.read_json(Path(b) / c / "freeze.json")

    def run(b, c, run_id, seed):
        target = Path(b) / "executions" / run_id
        (target / "output").mkdir(parents=True)
        (target / "output/generated.csv").write_text("NO DATA: controller mock artifact\n")
        receipt = {"status": "success", "candidate": c, "candidate_freeze_sha256": S.lifecycle.sha256(Path(b) / c / "freeze.json")}
        S.write(target / "execution.json", receipt)
        return receipt

    def collect(b, c, run, fid):
        target = Path(b) / S.semantic.FOLDER / fid
        target.mkdir(parents=True)
        report = {"kind": "mock_semantic_feedback_v1", "run_id": run}
        S.write(target / "feedback.json", report)
        return report

    monkeypatch.setattr(S.lifecycle, "freeze_candidate", freeze)
    monkeypatch.setattr(S.lifecycle, "verify_candidate", verify)
    monkeypatch.setattr(S.semantic, "preflight", lambda *a: {})
    monkeypatch.setattr(S.semantic, "collect_feedback", collect)
    monkeypatch.setattr(S.semantic, "verify_feedback", lambda b, fid, **kw: S.lifecycle.read_json(Path(b) / S.semantic.FOLDER / fid / "feedback.json"))
    monkeypatch.setattr(S.execution, "run_candidate", run)
    monkeypatch.setattr(S.execution, "verify_execution", lambda b, r: S.lifecycle.read_json(Path(b) / "executions" / r / "execution.json"))

    def candidate(name, stage="trial"):
        directory = bundle / "candidates" / name
        directory.mkdir(parents=True)
        (directory / "generator.py").write_text("def generate(a,b,c):\n    raise AssertionError('Test must never run scientific code')\n")
        state.freeze(name, stage=stage)
        return name

    return state, candidate


def begin_revision(state):
    state.feedback("initial")
    state.handback("initial", "actual-agent-1")
    state.dispatch("revision", "actual-agent-1")
    state.decision({"reason": "Fixture retention after actual mock feedback", "kind": "retain",
                    "addressed_findings": [], "remaining_limitations": ["Controller fixture only"]})


def test_exact_ten_attempt_budget_and_one_cycle(fresh):
    state, candidate = fresh
    trial = candidate("trial0")
    state.trial(trial, 101)
    state.trial(trial, 102, context="source_context")
    with pytest.raises(ValueError, match="trial budget"):
        state.trial(trial, 103)
    candidate("initial", "initial")
    assert len(state.deliver("initial")) == 3
    begin_revision(state)
    revised_trial = candidate("trial1")
    state.trial(revised_trial, 201, phase="revision")
    state.trial(revised_trial, 202, phase="revision", context="source_context")
    candidate("final", "final")
    assert len(state.deliver("final")) == 3
    state.feedback("final")
    status = state.verify()
    assert status["attempts"] == 10 and status["deliveries"] == 6
    assert status["scientific_review_rounds"] == 2
    assert {e["seed"] for e in state.selected("attempt") if e["purpose"] == "delivery"} == {3101, 3102, 3103}
    with pytest.raises(ValueError):
        state.deliver("final")
    with pytest.raises(ValueError, match="One revision"):
        state.decision({})


def test_failed_attempt_is_preserved_and_consumes_slot_without_fallback(fresh, monkeypatch):
    state, candidate = fresh
    trial = candidate("trial")
    calls = []
    def failed(*args, **kwargs):
        calls.append(args)
        raise RuntimeError("WSL unavailable; no fallback")
    monkeypatch.setattr(S.execution, "run_candidate", failed)
    for seed in [1, 2]:
        with pytest.raises(RuntimeError, match="WSL unavailable"):
            state.trial(trial, seed)
    with pytest.raises(ValueError, match="trial budget"):
        state.trial(trial, 3)
    assert len(calls) == 2
    assert state.status()["initial_trials"] == 2
    assert [r["status"] for r in state.selected("result")] == ["adapter_error", "adapter_error"]


def test_failed_middle_delivery_keeps_next_seed_and_reports_unavailable(fresh, monkeypatch):
    state, candidate = fresh
    candidate("initial", "initial")
    real_mock = S.execution.run_candidate
    calls = []
    def mixed(b, c, run, seed):
        calls.append(seed)
        if seed == 3102:
            raise RuntimeError("Simulated isolated adapter failure")
        return real_mock(b, c, run, seed)
    monkeypatch.setattr(S.execution, "run_candidate", mixed)
    assert [r["status"] for r in state.deliver("initial")] == ["success", "adapter_error", "success"]
    report = state.feedback("initial")
    assert calls == [3101, 3102, 3103]
    assert report["runs"][1]["reference_evaluation"]["analyses"][0]["status"] == "unavailable"
    assert state.verify_feedback("initial") == report
    with pytest.raises(ValueError, match="already attempted"):
        state.deliver("initial")
    assert calls == [3101, 3102, 3103]


def test_second_author_is_rejected(fresh):
    state, _ = fresh
    with pytest.raises(ValueError, match="one declared author"):
        state.dispatch("revision", "different-author")


def test_outside_root_mutation_rejected_before_freeze(fresh, tmp_path):
    state, _ = fresh
    old = tmp_path / "old_bundle"
    old.mkdir()
    sentinel = old / "immutable_receipt.txt"
    sentinel.write_text("old release")
    before = S.lifecycle.sha256(sentinel)
    with pytest.raises(ValueError, match="outside new session root"):
        state.freeze("candidate", bundle=old)
    assert S.lifecycle.sha256(sentinel) == before
    assert sorted(p.name for p in old.iterdir()) == [sentinel.name]


@pytest.mark.parametrize("target", ["feedback", "execution", "output"])
def test_feedback_hash_binds_retained_report_execution_and_output(fresh, target):
    state, candidate = fresh
    candidate("initial", "initial")
    state.deliver("initial")
    report = state.feedback("initial")
    run_id = report["runs"][0]["run_id"]
    path = {"feedback": state.folder / "feedback/initial.json",
            "execution": state.bundle / "executions" / run_id / "execution.json",
            "output": state.bundle / "executions" / run_id / "output/generated.csv"}[target]
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="hash changed|receipt changed|recomputed"):
        state.verify_feedback("initial")


def test_revision_requires_actual_handback_and_complete_coverage(fresh):
    state, candidate = fresh
    candidate("initial", "initial")
    state.deliver("initial")
    state.feedback("initial")
    with pytest.raises(ValueError, match="handback"):
        state.dispatch("revision", "actual-agent-1")
    state.handback("initial", "actual-agent-1")
    state.dispatch("revision", "actual-agent-1")
    assert len(state.selected("author_dispatch")) == 2


def test_actual_profile_snapshot_is_checked(fresh):
    state, _ = fresh
    path = Path(state.contract["profile"])
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="implementation/profile changed"):
        state.status()
