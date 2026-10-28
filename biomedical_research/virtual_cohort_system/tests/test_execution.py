"""Execution integrity tests. Mocked backend tests do NOT establish isolation."""
from __future__ import annotations
import json
from pathlib import Path
import sys

import pandas as pd
import pytest

from cohort_harness import execution as ex
from cohort_harness.demo import make_demo
from cohort_harness.lifecycle import freeze_candidate

PROGRAM = """def generate(observed, spec, seed):
    out = observed.copy()
    p = spec['parameters']
    out['y'] = p['intercept'] + p['slope'] * out['x']
    return out
"""


def bundle(tmp_path, program=True):
    root = make_demo(tmp_path / "bundle")
    candidate = root / "candidates" / "initial"
    if program:
        (candidate / "generated.csv").unlink()
        (candidate / "generator.py").write_text(PROGRAM, encoding="utf-8")
    freeze_candidate(root, candidate)
    return root, candidate


def fake_backend(monkeypatch, change=None, returncode=0, worker_report=None):
    monkeypatch.setattr(ex, "_runtime_manifest", lambda runtime: {"mock": True, "not_isolation_evidence": True})
    def capture(command, cwd, timeout, limit, stdout_path, stderr_path):
        task = ex.read_json(cwd / "input/task.json")
        observed = ex.read_table(cwd / "input/observed.csv", task)
        output = observed.assign(y=1 + 2 * observed.x)
        if change:
            output = change(output)
        output.to_csv(cwd / "output/generated.csv", index=False)
        report = {"status": "completed" if returncode == 0 else "executing", "generator_started": True}
        if worker_report is not None:
            report = worker_report
        (cwd / "output/worker_report.json").write_text(json.dumps(report))
        stdout_path.write_bytes(b"mocked backend, not an isolation test\n")
        stderr_path.write_bytes(b"")
        return {"returncode": returncode, "host_timeout": False, "logs": {}}
    monkeypatch.setattr(ex, "_capture", capture)


def test_direct_rows_verified_without_executing_code(tmp_path):
    root, candidate = bundle(tmp_path, program=False)
    result = ex.run_candidate(root, candidate, "direct", 1)
    assert result["status"] == "success"
    assert result["generator_executed"] is False
    assert result["isolation_scope"] == "no_code_execution"
    assert ex.verify_execution(root, "direct") == result


def test_requires_existing_freeze(tmp_path):
    root = make_demo(tmp_path / "new")
    with pytest.raises(ValueError):
        ex.run_candidate(root, root / "candidates/initial", "run", 1)


def test_no_overwrite_or_path_escape(tmp_path):
    root, candidate = bundle(tmp_path, program=False)
    ex.run_candidate(root, candidate, "first", 0)
    for name in ("first", "../escape", "a/b", "C:/escape", ""):
        with pytest.raises(ValueError):
            ex.run_candidate(root, candidate, name, 0)


@pytest.mark.parametrize("parameter,value", [
    ("seed", True), ("seed", -1), ("timeout_seconds", 0), ("memory_mb", 1),
    ("output_bytes", 0), ("log_bytes", 2_000_000)])
def test_invalid_resource_values(tmp_path, parameter, value):
    root, candidate = bundle(tmp_path, program=False)
    args = {"seed": 1, parameter: value}
    with pytest.raises(ValueError):
        ex.run_candidate(root, candidate, "bad", **args)


def test_mocked_program_result_binds_inputs_and_output(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch)
    before = ex.sha256(candidate / "freeze.json")
    result = ex.run_candidate(root, candidate, "fake", 42)
    assert result["status"] == "success"
    assert result["generator_executed"] is True
    assert ex.sha256(candidate / "freeze.json") == before
    assert result["agent_isolation"] == "not_provided"
    assert "input/worker.py" in result["files"]
    assert "runtime_manifest.json" in result["files"]
    assert ex.verify_execution(root, "fake") == result


def test_runtime_unavailable_is_recorded_without_fallback(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    def unavailable(runtime):
        raise ValueError("runtime unavailable")
    monkeypatch.setattr(ex, "_runtime_manifest", unavailable)
    monkeypatch.setattr(ex, "_capture", lambda *a: pytest.fail("must not run a local fallback"))
    result = ex.run_candidate(root, candidate, "unavailable", 1)
    assert result["status"] == "failed"
    assert result["generator_executed"] is False
    assert "unavailable" in result["error"]["message"]
    assert ex.verify_execution(root, "unavailable") == result


def test_rejects_uninspected_runtime(tmp_path):
    root, candidate = bundle(tmp_path)
    result = ex.run_candidate(root, candidate, "bad_runtime", 1, runtime={"backend": "local"})
    assert result["status"] == "failed"
    assert result["generator_executed"] is False


def test_damage_to_observed_cells_is_failed_and_preserved(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch, change=lambda frame: frame.assign(x=frame.x + 1))
    result = ex.run_candidate(root, candidate, "damage", 1)
    assert result["status"] == "failed"
    assert "Observed" in result["error"]["message"]
    assert (root / "executions/damage/output/generated.csv").is_file()
    assert ex.verify_execution(root, "damage") == result


def test_timeout_retains_receipt_and_logs(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch, returncode=137)
    result = ex.run_candidate(root, candidate, "timeout", 1)
    assert result["status"] == "timeout"
    assert result["generator_executed"] is True
    assert (root / "executions/timeout/stderr.log").exists()
    assert ex.verify_execution(root, "timeout") == result


@pytest.mark.parametrize("report", [[], "text", 3, {"status": "completed", "generator_started": "yes"}])
def test_untrusted_worker_report_types_preserve_failure_receipt(tmp_path, monkeypatch, report):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch, worker_report=report)
    result = ex.run_candidate(root, candidate, "malformed_report", 1)
    assert result["status"] == "failed"
    assert result["generator_executed"] is None
    assert ex.verify_execution(root, "malformed_report") == result


def test_execution_receipt_seed_must_match_staged_request(tmp_path):
    root, candidate = bundle(tmp_path, program=False)
    result = ex.run_candidate(root, candidate, "seed", 7)
    result["limits"]["seed"] = 8
    (root / "executions/seed/execution.json").write_text(json.dumps(result))
    with pytest.raises(ValueError, match="seed"):
        ex.verify_execution(root, "seed")


def test_completed_report_without_generator_entry_cannot_succeed(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch, worker_report={"status": "completed", "generator_started": False})
    result = ex.run_candidate(root, candidate, "no_entry", 1)
    assert result["status"] == "failed"
    assert ex.verify_execution(root, "no_entry") == result


@pytest.mark.parametrize("value", [[], "invalid", 7])
def test_malformed_execution_receipt_is_clean_contract_failure(tmp_path, value):
    root, candidate = bundle(tmp_path, program=False)
    ex.run_candidate(root, candidate, "malformed", 1)
    (root / "executions/malformed/execution.json").write_text(json.dumps(value))
    with pytest.raises(ValueError, match="object"):
        ex.verify_execution(root, "malformed")


@pytest.mark.parametrize("content", ["bad,header\n1,2\n", "sample_id,x,y\na,1,2,3\n", "sample_id,x,y\n" + "a,1,2\n" * 8,
                                      "sample_id,x,y\n" + "a,1,2\n" * 6, "x," * 500_001],
                         ids=["wrong-header", "wrong-fields", "extra-rows", "missing-rows", "very-wide-header"])
def test_streaming_csv_guard_rejects_wrong_shapes(tmp_path, content):
    root, _ = bundle(tmp_path, program=False)
    path = tmp_path / "bad.csv"
    path.write_text(content)
    with pytest.raises(ValueError):
        ex._csv_guard(path, ex.read_json(root / "task.json"), 20_000_000)


def test_oversize_worker_report_rejected_before_json_parse(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch, worker_report={"status": "completed", "generator_started": True, "extra": "x" * 70_000})
    result = ex.run_candidate(root, candidate, "large_report", 1)
    assert result["status"] == "failed"
    assert "64 KiB" in result["error"]["message"]
    assert ex.verify_execution(root, "large_report") == result


def test_prelaunch_mutation_is_caught(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    def inspect(runtime):
        (candidate / "generator.py").write_text(PROGRAM + "\n# changed\n")
        return {"mock": True}
    monkeypatch.setattr(ex, "_runtime_manifest", inspect)
    monkeypatch.setattr(ex, "_capture", lambda *args: pytest.fail("must not launch after mutation"))
    result = ex.run_candidate(root, candidate, "mutation", 1)
    assert result["status"] == "failed"
    assert result["generator_executed"] is False
    assert "changed" in result["error"]["message"].lower()


@pytest.mark.parametrize("target", ["output/generated.csv", "input/request.json", "stdout.log"])
def test_verifier_rejects_modified_artifacts(tmp_path, monkeypatch, target):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch)
    ex.run_candidate(root, candidate, "tamper", 1)
    path = root / "executions/tamper" / target
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="hash"):
        ex.verify_execution(root, "tamper")


def test_verifier_rejects_added_artifact(tmp_path):
    root, candidate = bundle(tmp_path, program=False)
    ex.run_candidate(root, candidate, "extra", 1)
    (root / "executions/extra/undeclared.txt").write_text("unexpected")
    with pytest.raises(ValueError, match="set changed"):
        ex.verify_execution(root, "extra")


def test_bubblewrap_command_has_no_workspace_mount(tmp_path):
    root, candidate = bundle(tmp_path)
    run = root / "executions/planned"
    command = ex._command(ex.DEFAULT_RUNTIME, run, 15)
    assert "--unshare-all" in command and "--unshare-user" in command and "--disable-userns" in command
    assert command.count("--bind") == 2
    assert command.count("--remount-ro") == 2
    assert "--new-session" in command and "--cap-drop" in command
    assert str(root) not in command
    assert "/mnt" not in command and "/home" not in command
    assert "/runtime/bin/python" in command
    assert command[4] == "/usr/bin/timeout"


def test_pipe_capture_bounds_logs_without_buffering_entire_output(tmp_path):
    command = [sys.executable, "-c", "import sys; sys.stdout.write('x'*20000); sys.stderr.write('y'*15000)"]
    stdout, stderr = tmp_path / "stdout", tmp_path / "stderr"
    result = ex._capture(command, tmp_path, 10, 1024, stdout, stderr)
    assert result["returncode"] == 0
    assert stdout.stat().st_size == stderr.stat().st_size == 1024
    assert result["logs"]["stdout"]["bytes_seen"] == 20000
    assert result["logs"]["stderr"]["bytes_seen"] == 15000
    assert result["logs"]["stdout"]["truncated"] is True


def test_pipe_capture_trusted_test_timeout(tmp_path):
    command = [sys.executable, "-c", "import time; time.sleep(30)"]
    result = ex._capture(command, tmp_path, 1, 1024, tmp_path / "o", tmp_path / "e")
    assert result["host_timeout"] is True

