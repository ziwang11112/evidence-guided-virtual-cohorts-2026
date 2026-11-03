"""Version-specific controller checks. All execution is mocked; no scientific rows."""
import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("information_session_v1", Path(__file__).with_name("information_session_v1.py"))
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


@pytest.fixture
def factory(tmp_path, monkeypatch):
    def freeze(b, c, parent=None, revision=None):
        S.write(Path(b) / c / "freeze.json", {"route": "generator.py", "revision_index": int(parent is not None)})
        return verify(b, c)

    def verify(b, c):
        return S.lifecycle.read_json(Path(b) / c / "freeze.json")

    def run(b, c, run_id, seed):
        directory = Path(b) / "executions" / run_id
        (directory / "output").mkdir(parents=True)
        (directory / "output/generated.csv").write_text("CONTROLLER TEST ONLY: NO SCIENTIFIC DATA\n")
        receipt = {"status": "success", "candidate": c,
                   "candidate_freeze_sha256": S.lifecycle.sha256(Path(b) / c / "freeze.json")}
        S.write(directory / "execution.json", receipt)
        return receipt

    def collect(b, c, run_id, feedback_id):
        directory = Path(b) / S.semantic.FOLDER / feedback_id
        directory.mkdir(parents=True)
        report = {"kind": "semantic_whole_cohort_feedback_v1", "run_id": run_id,
                  "checks": [{"evidence_id": "external", "semantic_status": "unavailable",
                              "reported_value": 123, "calculation": None, "difference": None}],
                  "n_computable": 0}
        S.write(directory / "feedback.json", report)
        return report

    monkeypatch.setattr(S.lifecycle, "freeze_candidate", freeze)
    monkeypatch.setattr(S.lifecycle, "verify_candidate", verify)
    monkeypatch.setattr(S.semantic, "preflight", lambda *a: {"checks": [{"evidence_id": "external", "semantic_status": "unavailable"}]})
    monkeypatch.setattr(S.semantic, "collect_feedback", collect)
    monkeypatch.setattr(S.semantic, "verify_feedback", lambda b, fid, **kw: S.lifecycle.read_json(Path(b) / S.semantic.FOLDER / fid / "feedback.json"))
    monkeypatch.setattr(S.execution, "run_candidate", run)
    monkeypatch.setattr(S.execution, "verify_execution", lambda b, r: S.lifecycle.read_json(Path(b) / "executions" / r / "execution.json"))

    def make(condition="L", bad_profile=False):
        root = tmp_path / condition
        bundle = root / "b"
        bundle.mkdir(parents=True)
        task = {"schema_version": 1, "task_id": "controller-fixture-" + condition, "mode": "whole_cohort",
                "population": "Invented controller fixture; no patients", "row_id": "id", "n_rows": 3000,
                "columns": [{"name": "id", "kind": "string", "unit": "identifier", "role": "identifier", "nullable": False},
                            {"name": "x", "kind": "number", "unit": "u", "role": "generated", "nullable": False}],
                "information_policy": {"mode": "prior_only", "excluded_cohorts": [], "allowed_tools": []},
                "budget": {"source_queries": 2, "source_downloads": 1, "revisions": 1}}
        S.write(bundle / "task.json", task)
        profile = tmp_path / (condition + "_profile.json")
        data = {"information_condition": condition, "required_diagnostic_ids": ["d"], "required_analysis_ids": ["a"]}
        if condition == "R" or bad_profile:
            reference = tmp_path / "REFERENCE_SENTINEL_87e194.json"
            S.write(reference, {"point": 874319.72})
            data["reference_summary"] = str(reference)
        S.write(profile, data)
        evaluator = tmp_path / (condition + "_evaluator.py")
        evaluator.write_text("def evaluate(bundle,candidate,run_id,profile):\n"
                             "    return {'reference_path':'REFERENCE_SENTINEL_87e194', 'diagnostics':[{'id':'d','value':1.25,'status':'computed','unit':'u','reference':874319.72,'difference':42,'ratio':17,'reference_ci':[5,9]}], 'analyses':[{'id':'a','value':2.5,'n':3000,'rank':2,'conclusion':'REFERENCE_SENTINEL_87e194'}]}\n")
        S.initialize(root, bundle, profile, evaluator, author_id="fresh-author-" + condition)
        state = S.Session(root)
        state.dispatch("initial", "fresh-author-" + condition)

        def candidate(name, stage="trial"):
            directory = bundle / "candidates" / name
            directory.mkdir(parents=True)
            (directory / "generator.py").write_text("def generate(a,b,c):\n    raise AssertionError('Never execute fixture scientific code')\n")
            state.freeze(name, stage=stage)
            return name

        return state, candidate
    return make


def revision(state):
    state.feedback("initial")
    state.handback("initial", state.contract["author_id"])
    state.dispatch("revision", state.contract["author_id"])
    state.decision({"reason": "Fixture-only retention", "kind": "retain", "addressed_findings": [],
                    "remaining_limitations": ["No scientific data generated"]})


def test_L_measurement_allowlist_removes_reference_sentinel(factory):
    state, candidate = factory()
    candidate("initial", "initial")
    state.deliver("initial")
    report = state.feedback("initial")
    encoded = json.dumps(report)
    assert "REFERENCE_SENTINEL_87e194" not in encoded
    assert "874319.72" not in encoded
    row = report["runs"][0]["analysis_feedback"]["diagnostics"][0]
    assert row == {"id": "d", "value": 1.25, "status": "computed", "unit": "u"}
    assert report["runs"][0]["semantic_feedback_v1"]["n_computable"] == 0
    assert "reference_summary" not in state.contract["bindings"]
    assert state.verify_feedback("initial") == report


def test_R_preserves_its_declared_comparison_fields(factory):
    state, candidate = factory("R")
    candidate("initial", "initial")
    state.deliver("initial")
    report = state.feedback("initial")
    assert report["runs"][0]["analysis_feedback"]["diagnostics"][0]["reference"] == 874319.72
    assert any("REFERENCE_SENTINEL_87e194" in p for p in state.contract["bindings"])


def test_L_reference_profile_rejected_before_session_creation(factory):
    with pytest.raises(ValueError, match="L profile must not contain"):
        factory(bad_profile=True)


def test_new_seeds_exact_budget_phases_and_author_feedback_chain(factory):
    state, candidate = factory()
    trial = candidate("initial_trial")
    state.trial(trial, 4201)
    state.trial(trial, 4202)
    with pytest.raises(ValueError, match="trial budget"):
        state.trial(trial, 4203)
    candidate("initial", "initial")
    state.deliver("initial")
    revision(state)
    with pytest.raises(ValueError, match="Initial phase is closed"):
        state.trial(trial, 4201)
    trial2 = candidate("revision_trial")
    state.trial(trial2, 4301, phase="revision")
    state.trial(trial2, 4302, phase="revision")
    candidate("final", "final")
    state.deliver("final")
    state.feedback("final")
    with pytest.raises(ValueError, match="Final phase is closed"):
        state.trial(trial2, 4301, phase="revision")
    status = state.verify()
    assert status["attempts"] == 10 and status["deliveries"] == 6
    assert {r["seed"] for r in state.selected("attempt") if r["purpose"] == "delivery"} == {4101, 4102, 4103}
    initial = state.selected("feedback")[0]
    assert state.selected("decision")[0]["based_on_feedback_sha256"] == initial["feedback_sha256"]
    assert state.selected("handback")[0]["feedback_sha256"] == initial["feedback_sha256"]
    assert [r["author_id"] for r in state.selected("author_dispatch")] == [state.contract["author_id"]] * 2


@pytest.mark.parametrize("artifact", ["feedback", "output", "execution"])
def test_feedback_recomputation_rejects_mutated_bound_artifacts(factory, artifact):
    state, candidate = factory()
    candidate("initial", "initial")
    state.deliver("initial")
    report = state.feedback("initial")
    run = report["runs"][0]["run_id"]
    path = {"feedback": state.folder / "feedback/initial.json",
            "output": state.bundle / "executions" / run / "output/generated.csv",
            "execution": state.bundle / "executions" / run / "execution.json"}[artifact]
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="hash changed|receipt changed|recomputed"):
        state.verify_feedback("initial")


def test_no_target_as_source_replay_or_label_only_source_context(factory, monkeypatch):
    state, candidate = factory()
    monkeypatch.setattr(S.semantic, "preflight", lambda *a: {"checks": [{"evidence_id": "external", "semantic_status": "matched_declared"}]})
    with pytest.raises(ValueError, match="source-population replay"):
        candidate("bad")
    monkeypatch.setattr(S.semantic, "preflight", lambda *a: {"checks": [{"evidence_id": "external", "semantic_status": "unavailable"}]})
    trial = candidate("allowed")
    with pytest.raises(ValueError, match="Source-context adapter not supplied"):
        state.trial(trial, 1, context="source_context")
    assert state.status()["attempts"] == 0


def test_failed_adapter_keeps_attempt_without_local_execution(factory, monkeypatch):
    state, candidate = factory()
    trial = candidate("trial")
    calls = []
    def fail(*args):
        calls.append(args)
        raise RuntimeError("Mock isolated runtime unavailable")
    monkeypatch.setattr(S.execution, "run_candidate", fail)
    with pytest.raises(RuntimeError, match="runtime unavailable"):
        state.trial(trial, 4201)
    assert len(calls) == state.status()["attempts"] == 1
    assert state.selected("result")[0]["status"] == "adapter_error"


def test_common_quality_parity_strips_nested_reference_sentinels():
    data = {"diagnostics": [{"id": "d", "value": 0}], "analyses": [{"id": "a", "value": 0}],
            "n": 3000, "quality": {"nonpositive_glycemia": {"glucose": 2, "hba1c": 3, "reference": "LEAK_SENTINEL"},
                                   "duplicate_measurement_rows": 5, "reference_ci": "LEAK_SENTINEL"}}
    left = S.allowed_analysis_feedback(data, "L")
    right = S.allowed_analysis_feedback(data, "R")
    expected = {"nonpositive_glycemia": {"glucose": 2, "hba1c": 3}, "duplicate_measurement_rows": 5}
    assert left["quality"] == right["quality"] == expected
    assert left["n"] == right["n"] == 3000
    assert "LEAK_SENTINEL" not in json.dumps(left)
    assert "LEAK_SENTINEL" not in json.dumps(right["quality"])


@pytest.mark.parametrize("bad_count", [-1, 1.0, True, "LEAK_SENTINEL", float("inf"), {"reference": 1}])
def test_quality_counts_reject_noninteger_primitives_and_metadata(bad_count):
    data = {"diagnostics": [], "analyses": [], "quality": {
        "nonpositive_glycemia": {"glucose": bad_count, "hba1c": 0}, "duplicate_measurement_rows": 0}}
    for condition in ("L", "R"):
        with pytest.raises(ValueError, match="quality counts"):
            S.allowed_analysis_feedback(data, condition)


def test_fixed_trial_seeds_and_duplicate_trial_rejected_before_attempt(factory):
    state, candidate = factory()
    trial = candidate("trial")
    with pytest.raises(ValueError, match="Trial seed contract mismatch"):
        state.trial(trial, 4301)
    assert state.status()["attempts"] == 0
    state.trial(trial, 4201)
    with pytest.raises(ValueError, match="Trial seed already attempted"):
        state.trial(trial, 4201)
    assert state.status()["attempts"] == 1
    candidate("initial", "initial")
    state.deliver("initial")
    revision(state)
    revised = candidate("revised_trial")
    with pytest.raises(ValueError, match="Trial seed contract mismatch"):
        state.trial(revised, 4202, phase="revision")
    assert state.status()["attempts"] == 4
    state.trial(revised, 4301, phase="revision")
    with pytest.raises(ValueError, match="Trial seed already attempted"):
        state.trial(revised, 4301, phase="revision")
    assert state.status()["attempts"] == 5
