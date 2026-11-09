"""New pilot controller checks with invented nonclinical files and a mocked backend.

No author module is imported, no WSL process is launched, and no clinical rows,
statistics, historical tests, or archived outputs are generated or rerun here.
"""
import importlib.util
import json
from pathlib import Path

import pytest


def load_runner():
    path = Path(__file__).with_name("runner.py")
    spec = importlib.util.spec_from_file_location("rubric_pilot_runner_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf8")


@pytest.fixture
def pilot(tmp_path, monkeypatch):
    runner = load_runner()
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "N_ROWS", 3)
    monkeypatch.setattr(runner, "CASE_COLUMNS", {"H": ["id", "x"], "L": ["id", "x"]})
    monkeypatch.setattr(runner, "engine_hashes", lambda: {"invented_test_engine": "a" * 64})
    (tmp_path / "runner.py").write_text("# invented controller commitment\n")
    (tmp_path / "evaluate.py").write_text("# invented evaluator commitment\n")
    protocol = {"authors": runner.AUTHORS, "seeds": runner.SEEDS, "n_rows": 3,
                "max_final_tables": 18, "limits": runner.LIMITS,
                "revision_rounds": 0, "sampling_trials_before_seal": 0}
    put(tmp_path / "PROTOCOL.json", protocol)
    design_names = {"PROTOCOL.json"}
    for author in runner.AUTHORS:
        bundle = tmp_path / "bundles" / author
        task = {"schema_version": 1, "task_id": "invented-" + author, "mode": "whole_cohort",
                "population": "invented nonclinical mechanical fixture", "row_id": "id", "n_rows": 3,
                "columns": [{"name": "id", "kind": "string", "unit": "identifier", "role": "identifier", "nullable": False},
                            {"name": "x", "kind": "number", "unit": "1", "role": "generated", "nullable": False}],
                "information_policy": {"mode": "published_evidence", "excluded_cohorts": [], "allowed_tools": []},
                "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 0}}
        put(bundle / "task.json", task)
        put(bundle / "request.json", {"invented": True})
        put(bundle / "sources" / "invented.json", {"text": "Invented nonclinical source fixture"})
        design_names.update(f"bundles/{author}/{name}" for name in ("task.json", "request.json", "sources/invented.json"))
    records = {name: runner.sha(tmp_path / name) for name in sorted(design_names)}
    put(tmp_path / "DESIGN_LOCK.json", {"records": records, "author_outputs_present": False})
    put(tmp_path / "DESIGN_REVIEW.json", {"decision": "PASS_TO_AUTHOR_DISPATCH", "bound_inputs": records, "blocking_findings": []})
    for author in runner.AUTHORS:
        output = tmp_path / "bundles" / author / "output"
        output.mkdir()
        # Importing this file on the host would fail the test immediately.
        (output / "generator.py").write_text("raise RuntimeError('author code must never execute on host')\n\ndef generate(observed, specification, seed):\n    return None\n")
        put(output / "model_spec.json", {"invented": True})
        put(output / "SOURCE_USE.json", {"invented": True})
        (output / "DECISION.md").write_text("Invented nonclinical mechanical fixture.\n")
    put(tmp_path / "IMPLEMENTATION_REVIEW.json", {"decision": "PASS_TO_EXECUTE", "blocking_findings": [],
        "bound_inputs": runner.implementation_review_bindings(), "engine_sha256": runner.engine_hashes()})
    return runner


def test_static_seal_never_imports_author_program(pilot):
    lock = pilot.seal_batch()
    assert lock["all_author_outputs_fixed_before_sampling"] is True
    assert len([p for p in lock["records"] if "/output/" in p]) == 24
    assert pilot.inventory() == {}


def test_missing_sixth_submission_prevents_seal(pilot):
    (pilot.ROOT / "bundles/LC/output/DECISION.md").unlink()
    with pytest.raises(ValueError, match="exactly four"):
        pilot.seal_batch()
    assert not (pilot.ROOT / "BATCH_LOCK.json").exists()
    assert not (pilot.ROOT / "private_runs").exists()


@pytest.mark.parametrize("relative", ["bundles/HA/output/model_spec.json", "bundles/HA/sources/invented.json"])
def test_mutated_frozen_input_rejects_run_without_slot(pilot, relative):
    pilot.seal_batch()
    put(pilot.ROOT / relative, {"changed": True})
    with pytest.raises(ValueError, match="changed"):
        pilot.run_author("HA")
    assert pilot.inventory() == {}


def test_extra_author_input_is_rejected(pilot):
    put(pilot.ROOT / "bundles/HA/unlisted.json", {"unlisted": True})
    with pytest.raises(ValueError, match="inventory changed"):
        pilot.seal_batch()


def mock_author_failure(pilot, monkeypatch):
    monkeypatch.setattr(pilot.execution, "_runtime_manifest", lambda _: {"invented": "mocked"})
    def capture(command, run, timeout, limit, stdout_path, stderr_path):
        put(run / "output/worker_report.json", {"status": "failed", "generator_started": True})
        stdout_path.write_text(""); stderr_path.write_text("Invented author exception")
        return {"returncode": 2, "host_timeout": False, "logs": {}}
    monkeypatch.setattr(pilot.execution, "_capture", capture)


def test_infrastructure_failure_consumes_one_slot_and_halts(pilot, monkeypatch):
    pilot.seal_batch()
    def unavailable(_):
        raise RuntimeError("Invented unavailable runtime")
    monkeypatch.setattr(pilot.execution, "_runtime_manifest", unavailable)
    monkeypatch.setattr(pilot.execution, "_capture", lambda *a, **k: pytest.fail("No worker should launch"))
    with pytest.raises(ValueError, match="batch halted"):
        pilot.run_author("HA")
    assert len(pilot.inventory()) == 1
    receipt=pilot.verify_execution("HA", pilot.SEEDS[0])
    assert receipt["generator_executed"] is False
    assert receipt["failure_class"] == "infrastructure_unknown_or_integrity"
    assert (pilot.ROOT / "RUNNING.lock").exists()
    with pytest.raises(FileExistsError):
        pilot.run_author("HB")


def test_three_author_failed_slots_are_consumed_without_retry(pilot, monkeypatch):
    pilot.seal_batch()
    mock_author_failure(pilot, monkeypatch)
    results = pilot.run_author("HA")
    assert [r["status"] for r in results] == ["failed"] * 3
    assert len(pilot.inventory()) == 3
    assert all(pilot.verify_execution("HA", seed)["generator_executed"] is True for seed in pilot.SEEDS)
    with pytest.raises(ValueError, match="already consumed"):
        pilot.run_author("HA", pilot.SEEDS[0])
    assert not (pilot.ROOT / "RUNNING.lock").exists()


def test_native_staging_and_receipt_validation_without_author_execution(pilot, monkeypatch):
    pilot.seal_batch()
    monkeypatch.setattr(pilot.execution, "_runtime_manifest", lambda _: {"invented": "mocked; no runtime launched"})
    def fake_capture(command, run, timeout, limit, stdout_path, stderr_path):
        assert "/input/worker.py" in command
        assert set(p.name for p in (run / "input").iterdir()) == pilot.STAGED_FILES
        assert (run / "input/generator.py").read_bytes() == (pilot.ROOT / "bundles/HA/output/generator.py").read_bytes()
        assert "author.py" not in command
        # Fixed transport fixture, not a generator invocation or clinical draw.
        (run / "output/generated.csv").write_text("id,x\nr1,1\nr2,2\nr3,3\n")
        put(run / "output/worker_report.json", {"status": "completed", "generator_started": True})
        stdout_path.write_text(""); stderr_path.write_text("")
        return {"returncode": 0, "host_timeout": False, "logs": {}}
    monkeypatch.setattr(pilot.execution, "_capture", fake_capture)
    result = pilot.run_author("HA", pilot.SEEDS[0])[0]
    assert result["status"] == "success"
    assert pilot.verify_execution("HA", pilot.SEEDS[0])["generated_sha256"] == result["generated_sha256"]
    (pilot.ROOT / "private_runs/HA/seed_9301/output/generated.csv").write_text("id,x\nr1,9\nr2,2\nr3,3\n")
    with pytest.raises(ValueError, match="inventory or hashes changed"):
        pilot.verify_execution("HA", pilot.SEEDS[0])


def test_unscheduled_slot_is_rejected(pilot):
    pilot.seal_batch()
    with pytest.raises(ValueError, match="Unscheduled"):
        pilot.run_author("HA", 9304)
    (pilot.ROOT / "private_runs/HA/seed_9304").mkdir(parents=True)
    with pytest.raises(ValueError, match="Unscheduled"):
        pilot.inventory()


def test_partial_attempts_cannot_close(pilot, monkeypatch):
    pilot.seal_batch()
    mock_author_failure(pilot, monkeypatch)
    pilot.run_author("HA", pilot.SEEDS[0])
    with pytest.raises(ValueError, match="eighteen"):
        pilot.close_batch()
    assert not (pilot.ROOT / "BATCH_CLOSURE.json").exists()


def test_all_eighteen_failures_remain_in_closed_batch(pilot, monkeypatch):
    pilot.seal_batch()
    mock_author_failure(pilot, monkeypatch)
    for author in pilot.AUTHORS:
        pilot.run_author(author)
    state = pilot.close_batch()
    assert state["physical_attempts"] == state["scheduled_final_slots"] == 18
    assert len(state["records"]) == 18
    assert all(record["status"] == "failed" for record in state["records"])
    assert pilot.closure_gate() == state
    with pytest.raises(FileExistsError):
        pilot.close_batch()


def test_integrity_failure_after_confirmed_entry_halts(pilot, monkeypatch):
    pilot.seal_batch()
    monkeypatch.setattr(pilot.execution, "_runtime_manifest", lambda _: {"invented": "mocked"})
    def capture(command, run, timeout, limit, stdout_path, stderr_path):
        (run / "output/generated.csv").write_text("id,x\nr1,1\nr2,2\nr3,3\n")
        put(run / "output/worker_report.json", {"status": "completed", "generator_started": True})
        (run / "input/generator.py").write_text("# staged bytes corrupted by invented fixture\n")
        stdout_path.write_text(""); stderr_path.write_text("")
        return {"returncode": 0, "host_timeout": False, "logs": {}}
    monkeypatch.setattr(pilot.execution, "_capture", capture)
    with pytest.raises(ValueError, match="batch halted"):
        pilot.run_author("HA")
    assert len(pilot.inventory()) == 1
    receipt=pilot.read(pilot.ROOT/'private_runs/HA/seed_9301/execution.json')
    assert receipt['generator_executed'] is True
    assert receipt['failure_class']=='infrastructure_unknown_or_integrity'
    assert (pilot.ROOT/'RUNNING.lock').exists()


@pytest.mark.parametrize('failure', ['worker_plus_stage', 'schema_plus_extra_output'])
def test_model_failure_cannot_bypass_integrity_audit(pilot, monkeypatch, failure):
    pilot.seal_batch()
    monkeypatch.setattr(pilot.execution, '_runtime_manifest', lambda _: {'invented': 'mocked'})
    def capture(command, run, timeout, limit, stdout_path, stderr_path):
        if failure == 'worker_plus_stage':
            put(run/'output/worker_report.json', {'status':'failed', 'generator_started':True})
            (run/'input/generator.py').write_text('# invented corruption\n')
            returncode=2
        else:
            put(run/'output/worker_report.json', {'status':'completed', 'generator_started':True})
            (run/'output/generated.csv').write_text('wrong\n1\n')
            (run/'output/unexpected.txt').write_text('invented extra file')
            returncode=0
        stdout_path.write_text('');stderr_path.write_text('')
        return {'returncode':returncode,'host_timeout':False,'logs':{}}
    monkeypatch.setattr(pilot.execution,'_capture',capture)
    with pytest.raises(ValueError,match='batch halted'):
        pilot.run_author('HA')
    assert len(pilot.inventory())==1
    receipt=pilot.read(pilot.ROOT/'private_runs/HA/seed_9301/execution.json')
    assert receipt['generator_executed'] is True
    assert receipt['failure_class']=='infrastructure_unknown_or_integrity'
    assert receipt['preceding_error'] is not None
    assert (pilot.ROOT/'RUNNING.lock').exists()
