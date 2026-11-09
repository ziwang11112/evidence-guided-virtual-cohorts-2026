"""Adaptive dispatch on invented data; intercepted HTTP, no clinical data/model calls."""
from copy import deepcopy
import json
import shutil

import pytest

from cohort_harness import adaptive_session_v1 as session
from cohort_harness import execution, literature, semantic_feedback_v1 as semantic
from cohort_harness.lifecycle import read_json, sha256
from test_semantic_feedback_v1 import prepared
from test_whole_cohort_feedback import write, fake_program_backend
from test_literature_adapter import transport


def fixture(tmp_path, *, seeds=(11,), program=False, adapter=True):
    root, candidate = prepared(tmp_path)
    # The helper creates a frozen invented fixture; this new session starts before freezing.
    (candidate / "freeze.json").unlink()
    task = read_json(root / "task.json")
    task["information_policy"]["allowed_tools"] = ["literature." + a for a in literature.ACTIONS if a != "init"]
    task["budget"].update(source_queries=3, source_downloads=2, revisions=2)
    write(root / "task.json", task)
    write(root / "request.json", {"schema_version": 1, "purpose": "Invented dispatch test",
                                  "analyses": ["Describe invented output"], "task": task})
    if program:
        (candidate / "generated.csv").unlink()
        (candidate / "generator.py").write_text("def generate(observed, spec, seed):\n    raise RuntimeError('fixture')\n")
    config = {"schema_version": 1, "limits": {"actions": 30, "candidates": 3, "executions": 6,
               "feedbacks": 6, "analyses": 6}, "allowed_seeds": list(seeds),
              "runtime": deepcopy(execution.DEFAULT_RUNTIME) if program else None,
              "execution_limits": {"timeout_seconds": 30, "memory_mb": 1024, "output_bytes": 20000000, "log_bytes": 10000},
              "analysis_adapters": {}}
    if adapter:
        source = tmp_path / "generated_analysis.py"
        source.write_text("import pandas as pd\ndef analyze(output_path, task_path, request_path):\n"
                          "    frame = pd.read_csv(output_path)\n"
                          "    return {'n': len(frame), 'mean_y': float(frame.y.mean())}\n")
        config["analysis_adapters"]["generated"] = {"path": str(source.resolve()), "function": "analyze", "sha256": sha256(source)}
    return root, candidate, config


def act(root, name, kind, **kwargs):
    return session.dispatch(root, name, {"kind": kind, **kwargs})


def check_run(root, seed=11, candidate="initial", prefix="a", analysis=True):
    run_id = prefix + "run"
    assert act(root, prefix + "execute", "execute", candidate=candidate, run_id=run_id, seed=seed)["status"] == "success"
    report = act(root, prefix + "feedback", "feedback", candidate=candidate, run_id=run_id, feedback_id=prefix + "fb")
    assert report["status"] == "success"
    if analysis:
        result = act(root, prefix + "analysis", "analysis", candidate=candidate, run_id=run_id, adapter="generated", analysis_id=prefix + "ana")
        assert result["status"] == "success"
        assert result["result"]["reference_role"] == "none"
        assert result["result"]["result"]["mean_y"] == pytest.approx(1.3)
    return report


def test_direct_end_to_end_and_terminal_finish(tmp_path):
    root, candidate, config = fixture(tmp_path)
    assert session.create_session(root, config)["status"] == "active"
    assert act(root, "submit", "submit", candidate="initial")["status"] == "success"
    before = {p.name: sha256(p) for p in candidate.iterdir()}
    report = check_run(root)
    assert report["result"]["generator_execution_recorded"] is False
    assert report["result"]["source_context_validity"] == "not_certified"
    assert act(root, "done", "finish", final_candidate="initial", reason="Requested analyses inspected")["session_status"] == "completed"
    summary = session.verify_session(root)
    assert summary["usage"] == {"actions": 5, "candidates": 1, "executions": 1, "feedbacks": 1, "analyses": 1}
    assert before == {p.name: sha256(p) for p in candidate.iterdir()}
    with pytest.raises(ValueError, match="terminal"):
        act(root, "later", "literature", action="init")


def test_real_literature_adapter_with_intercepted_http_and_persistent_budget(tmp_path, monkeypatch):
    root, _, config = fixture(tmp_path)
    session.create_session(root, config)
    monkeypatch.setattr(literature.gateway, "http_get", transport())
    response = act(root, "search", "literature", action="search", query="invented")
    assert response["result"]["usage"]["queries"] == 1
    assert response["result"]["registered_artifacts"]
    response = act(root, "fetch", "literature", action="fetch", pmcid="PMC123", version=1)
    assert response["result"]["status"] == "accepted"
    assert response["result"]["usage"]["downloads"] == 1
    assert session.verify_session(root)["usage"]["actions"] == 2
    state = root / "gateway/session/state.json"
    data = read_json(state)
    data["usage"]["queries"] = 0
    write(state, data)
    with pytest.raises(ValueError, match="Gateway bytes changed"):
        act(root, "reset_attempt", "literature", action="search", query="invented")


def test_preflight_failure_is_charged_without_freezing_or_legacy_fallback(tmp_path, monkeypatch):
    root, candidate, config = fixture(tmp_path)
    session.create_session(root, config)
    original = (candidate / semantic.FILE).read_bytes()
    sidecar = read_json(candidate / semantic.FILE)
    sidecar["bindings"][0]["source_operator"]["column"] = "absent"
    write(candidate / semantic.FILE, sidecar)
    from cohort_harness import whole_cohort_feedback as legacy
    monkeypatch.setattr(legacy, "collect_feedback", lambda *a, **k: pytest.fail("No fallback"))
    result = act(root, "bad", "submit", candidate="initial")
    assert result["status"] == "error" and result["session_status"] == "active"
    assert not (candidate / "freeze.json").exists()
    assert session.verify_session(root)["usage"]["candidates"] == 1
    (candidate / semantic.FILE).write_bytes(original)
    assert act(root, "fixed", "submit", candidate="initial")["status"] == "success"


def test_noop_lineage_preserves_old_candidate_and_requires_parent(tmp_path):
    root, candidate, config = fixture(tmp_path)
    session.create_session(root, config)
    act(root, "first", "submit", candidate="initial")
    frozen = (candidate / "freeze.json").read_bytes()
    new = root / "candidates/reviewed"
    shutil.copytree(candidate, new, ignore=shutil.ignore_patterns("freeze.json"))
    with pytest.raises(ValueError, match="latest"):
        act(root, "wrong", "submit", candidate="reviewed")
    revision = {"kind": "retain", "reason": "No justified scientific change", "addressed_findings": [], "remaining_limitations": []}
    result = act(root, "retain", "submit", candidate="reviewed", parent="initial", revision=revision)
    assert result["status"] == "success"
    assert result["result"]["freeze"]["revision_index"] == 1
    assert frozen == (candidate / "freeze.json").read_bytes()


def test_seed_and_finish_schedule_cannot_be_cherry_picked(tmp_path):
    root, _, config = fixture(tmp_path, seeds=(11, 12))
    session.create_session(root, config)
    act(root, "submit", "submit", candidate="initial")
    check_run(root)
    with pytest.raises(ValueError, match="scheduled seed"):
        act(root, "early", "finish", final_candidate="initial", reason="Stop early")
    with pytest.raises(ValueError, match="already attempted"):
        act(root, "retry", "execute", candidate="initial", run_id="other", seed=11)
    with pytest.raises(ValueError, match="not scheduled"):
        act(root, "best_seed", "execute", candidate="initial", run_id="other", seed=13)
    check_run(root, seed=12, prefix="b")
    assert act(root, "done", "finish", final_candidate="initial", reason="Full schedule")["session_status"] == "completed"


@pytest.mark.parametrize("field", ["task", "candidate", "result", "event", "registry", "adapter", "dependency"])
def test_integrity_mutation_stops_next_action(tmp_path, field):
    root, candidate, config = fixture(tmp_path)
    dependency = tmp_path / "dependency.py"
    dependency.write_text("VALUE = 1\n")
    config["analysis_adapters"]["generated"]["dependencies"] = {str(dependency.resolve()): sha256(dependency)}
    session.create_session(root, config)
    act(root, "submit", "submit", candidate="initial")
    paths = {"task": root / "task.json", "candidate": candidate / "decision.md",
             "result": root / session.DIRECTORY / "results/submit.json",
             "event": root / session.DIRECTORY / "events/00000001.json",
             "registry": root / "registry.json", "adapter": tmp_path / "generated_analysis.py", "dependency": dependency}
    if field == "registry":
        value = read_json(paths[field])
        value["artifacts"] = []
        write(paths[field], value)
    elif field == "event":
        value = read_json(paths[field])
        value["payload"]["payload"]["candidate"] = "candidates/altered"
        write(paths[field], value)
    else:
        with paths[field].open("ab") as out:
            out.write(b"\n ")
    with pytest.raises((ValueError, KeyError)):
        act(root, "next", "execute", candidate="initial", run_id="run", seed=11)
    assert not (root / "executions").exists()


def test_interrupted_operation_cannot_restart_or_reset(tmp_path):
    root, _, config = fixture(tmp_path)
    session.create_session(root, config)
    lock = root / session.DIRECTORY / ".operation.lock"
    lock.write_text("interrupted")
    with pytest.raises(ValueError, match="interrupted"):
        act(root, "x", "submit", candidate="initial")
    with pytest.raises(ValueError, match="fresh"):
        session.create_session(root, config)


def test_mocked_program_boundary_dispatches_and_failed_attempt_is_not_retried(tmp_path, monkeypatch):
    root, _, config = fixture(tmp_path, program=True)
    session.create_session(root, config)
    act(root, "submit", "submit", candidate="initial")
    fake_program_backend(monkeypatch, returncode=1)
    result = act(root, "execute", "execute", candidate="initial", run_id="run", seed=11)
    assert result["status"] == "failed" and result["session_status"] == "active"
    assert session.verify_session(root)["usage"]["executions"] == 1
    with pytest.raises(ValueError, match="already attempted"):
        act(root, "retry", "execute", candidate="initial", run_id="retry", seed=11)
    assert act(root, "abandon", "finish", final_candidate=None, reason="No useful output")["session_status"] == "abandoned"


def test_infrastructure_failure_stops_session_without_fallback(tmp_path, monkeypatch):
    root, _, config = fixture(tmp_path, program=True)
    session.create_session(root, config)
    act(root, "submit", "submit", candidate="initial")
    def unavailable(*args, **kwargs):
        raise OSError("Invented missing runtime")
    monkeypatch.setattr(execution, "_runtime_manifest", unavailable)
    result = act(root, "execute", "execute", candidate="initial", run_id="run", seed=11)
    assert result["session_status"] == "halted"
    assert (root / "executions/run/execution.json").exists()
    assert session.verify_session(root)["status"] == "halted"
    with pytest.raises(ValueError, match="terminal"):
        act(root, "retry", "literature", action="init")


@pytest.mark.parametrize("tamper", ["worker", "launch", "request", "output"])
def test_failed_program_trusted_staging_is_checked(tmp_path, monkeypatch, tamper):
    root, _, config = fixture(tmp_path, program=True)
    session.create_session(root, config)
    act(root, "submit", "submit", candidate="initial")
    fake_program_backend(monkeypatch, returncode=1)
    capture = execution._capture
    def corrupt(command, cwd, *args):
        result = capture(command, cwd, *args)
        if tamper == "worker":
            (cwd / "input/worker.py").write_text("# changed trusted worker\n")
        elif tamper == "launch":
            launch = read_json(cwd / "launch.json")
            launch["worker_sha256"] = "0" * 64
            write(cwd / "launch.json", launch)
        elif tamper == "request":
            request = read_json(cwd / "input/request.json")
            request["task_id"] = "changed"
            write(cwd / "input/request.json", request)
        else:
            (cwd / "output/unexpected.txt").write_text("unexpected")
        return result
    monkeypatch.setattr(execution, "_capture", corrupt)
    result = act(root, "execute", "execute", candidate="initial", run_id="run", seed=11)
    assert result["status"] == "error" and result["session_status"] == "halted"


def test_network_failure_is_recorded_and_allows_author_to_change_action(tmp_path, monkeypatch):
    root, _, config = fixture(tmp_path)
    session.create_session(root, config)
    def fail(*args):
        raise literature.gateway.GatewayError("network_or_timeout_failure")
    monkeypatch.setattr(literature.gateway, "http_get", fail)
    result = act(root, "search", "literature", action="search", query="invented")
    assert result["status"] == "error" and result["session_status"] == "active"
    assert result["result"]["usage"]["queries"] == 1
    assert act(root, "submit", "submit", candidate="initial")["status"] == "success"


def test_older_submitted_stage_schedule_cannot_be_omitted(tmp_path):
    root, candidate, config = fixture(tmp_path)
    session.create_session(root, config)
    act(root, "first", "submit", candidate="initial")
    new = root / "candidates/reviewed"
    shutil.copytree(candidate, new, ignore=shutil.ignore_patterns("freeze.json"))
    revision = {"kind": "retain", "reason": "No model change", "addressed_findings": [], "remaining_limitations": []}
    act(root, "retain", "submit", candidate="reviewed", parent="initial", revision=revision)
    check_run(root, candidate="reviewed")
    with pytest.raises(ValueError, match="Submitted candidate.*initial"):
        act(root, "done", "finish", final_candidate="reviewed", reason="Incomplete schedule")
    stopped = act(root, "abandon", "finish", final_candidate=None, reason="Explicit incomplete abandonment")
    assert stopped["session_status"] == "abandoned"
    assert stopped["result"]["stage_disposition"][0]["runs"][0]["status"] == "not_attempted"


def test_exhaustion_and_unapproved_adapter_do_not_dispatch(tmp_path):
    root, _, config = fixture(tmp_path)
    config["limits"]["actions"] = 1
    session.create_session(root, config)
    act(root, "submit", "submit", candidate="initial")
    with pytest.raises(ValueError, match="allowance"):
        act(root, "execute", "execute", candidate="initial", run_id="run", seed=11)
    assert not (root / "executions").exists()


def test_engine_change_stops_dispatch(tmp_path, monkeypatch):
    root, _, config = fixture(tmp_path)
    session.create_session(root, config)
    changed = session._engines()
    changed["_worker.py"] = "0" * 64
    monkeypatch.setattr(session, "_engines", lambda: changed)
    with pytest.raises(ValueError, match="engine changed"):
        act(root, "submit", "submit", candidate="initial")


@pytest.mark.parametrize("name", ["input/population_metadata.json", "skills/procedure.md", "AUTHOR_TASK.md", "SETUP_NOTES.md", "adapters.json"])
def test_static_scientific_context_is_bound(tmp_path, name):
    root, _, config = fixture(tmp_path)
    path = root / name
    path.parent.mkdir(exist_ok=True)
    path.write_text("Invented initial scientific context\n")
    session.create_session(root, config)
    path.write_text("Changed scientific context\n")
    with pytest.raises(ValueError, match="Session input changed"):
        act(root, "submit", "submit", candidate="initial")


def test_undeclared_added_context_cannot_change_author_packet(tmp_path):
    root, _, config = fixture(tmp_path)
    session.create_session(root, config)
    (root / "input").mkdir()
    (root / "input/additional.json").write_text("{}\n")
    with pytest.raises(ValueError, match="context inventory"):
        act(root, "submit", "submit", candidate="initial")


def test_cli_create_submit_and_abandon(tmp_path, capsys):
    root, _, config = fixture(tmp_path)
    config_path, action_path = tmp_path / "config.json", tmp_path / "action.json"
    write(config_path, config)
    assert session.main(["create", "--bundle", str(root), "--config", str(config_path)]) == 0
    write(action_path, {"kind": "submit", "candidate": "initial"})
    assert session.main(["act", "--bundle", str(root), "--action-id", "submit", "--action", str(action_path)]) == 0
    write(action_path, {"kind": "finish", "final_candidate": None, "reason": "CLI engineering check only"})
    assert session.main(["act", "--bundle", str(root), "--action-id", "done", "--action", str(action_path)]) == 0
    assert session.main(["verify", "--bundle", str(root)]) == 0
    assert '"status": "abandoned"' in capsys.readouterr().out
