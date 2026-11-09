"""Invented source-law fixtures; mocked boundaries are never real isolation claims."""
from __future__ import annotations

from copy import deepcopy
import json
import shutil
import sys

import numpy as np
import pandas as pd
import pytest

from cohort_harness import execution as ex, semantic_feedback_v1 as sem
from cohort_harness import whole_cohort_source_replay_v1 as replay
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256, verify_candidate
from test_whole_cohort_feedback import _example, write
from test_semantic_feedback_v1 import source_units


PROGRAM = '''import json
from pathlib import Path
import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    assert observed is None
    task = json.loads(Path("/input/task.json").read_text())
    n = task["n_rows"]
    p = spec["parameters"]
    raw = np.arange(n, dtype=float) - (n - 1) / 2
    group = np.arange(n) % 2
    x = raw / raw.std(ddof=1) if "raw_x" in [c["name"] for c in task["columns"]] else raw
    result = pd.DataFrame({"sample_id": [f"invented_{i}" for i in range(n)],
        "x": x, "group": group, "y": p["offset"] + p["slope"] * x + p["group_shift"] * group,
        "raw_x": raw})
    return result[[c["name"] for c in task["columns"]]]
'''


def prepared(tmp_path, *, edit=None, freeze=True, schedule_count=2):
    root = _example.prepare(tmp_path / "b", 8)
    candidate = root / "candidates/initial"
    (candidate / "generator.py").write_text(PROGRAM, encoding="utf-8")
    task = read_json(root / "task.json")
    columns = deepcopy(task["columns"])
    columns[1]["unit"] = "1"
    columns.append({"name": "raw_x", "kind": "number", "unit": "x_unit", "role": "generated", "nullable": False})
    evidence = read_json(candidate / "evidence.json")
    item = next(i for i in evidence["items"] if i["id"] == "E_slope")
    item["unit"] = "y_unit"
    write(candidate / "evidence.json", evidence)
    context_dir = candidate / "source_contexts"
    context_dir.mkdir()
    operator = {"kind": "ols_coefficient", "unit": "y_unit", "outcome": "y", "predictors": ["x", "group"],
                "term": "x", "include_intercept": True, "selection": [], "missing_policy": "error"}
    recipe = {"schema_version": 1, "population": "Invented source only", "measurement": {"mode": "identity", "description": "Generated columns in their declared analysis units; scaling convention remains assumed."},
              "assumption_ids": ["A_fixture"], "checks": [{"id": "slope", "evidence_id": "E_slope", "status": "approximate",
                "operator": operator, "assumption_ids": [], "reason": "Invented source OLS projection."}]}
    semantics = {"schema_version": 1, "evidence_sha256": sha256(candidate / "evidence.json"), "recipe_sha256": "",
                 "bindings": [{"check_id": "slope", "evidence_id": "E_slope", "source_locator": item["locator"],
                 "definition_status": "specified", "source_operator": deepcopy(operator), "weights": "not_reported",
                 "transform": "nonidentity", "source_variable_units": source_units(operator, {"columns": columns}),
                 "source_n": {"status": "not_reported"}, "uncertainty_role": "not_reported",
                 "reason": "Invented publication does not establish this sample scaling/weighting convention."}]}
    context = {"id": "source_main", "population": recipe["population"], "n_rows": 10, "columns": columns,
               "reason": "Invented separate source task", "assumption_ids": ["A_fixture"],
               "recipe": {"path": "source_contexts/recipe.json", "sha256": ""},
               "semantics": {"path": "source_contexts/semantics.json", "sha256": ""},
               "predictor_checks": [{"kind": "zscore", "column": "x", "raw_column": "raw_x", "selection": [],
                 "reference": {"mode": "sample", "selection": [], "ddof": 1}, "assumption_ids": ["A_fixture"], "reason": "Invented sample reference."}],
               "assumed_diagnostics": [{"check_id": "slope", "assumption_ids": ["A_fixture"], "reason": "Named assumed OLS projection."}]}
    plan = {"schema_version": 1, "budget": {"max_evaluations": schedule_count, "max_rows_per_evaluation": 10},
            "schedule": [{"replay_id": f"r{i}", "candidate": "candidates/initial", "context_id": "source_main", "seed": 70 + i, "n_rows": 10}
                         for i in range(schedule_count)], "contexts": [context]}
    if edit:
        edit(root, candidate, plan, recipe, semantics)
    write(context_dir / "recipe.json", recipe)
    semantics["recipe_sha256"] = sha256(context_dir / "recipe.json")
    write(context_dir / "semantics.json", semantics)
    context["recipe"]["sha256"] = sha256(context_dir / "recipe.json")
    context["semantics"]["sha256"] = sha256(context_dir / "semantics.json")
    write(candidate / replay.PLAN, plan)
    if freeze:
        freeze_candidate(root, candidate)
    return root, candidate


def source_frame(task, *, bad_predictor=False):
    n = task["n_rows"]
    raw = np.arange(n, dtype=float) - (n - 1) / 2
    x = raw / raw.std(ddof=1)
    group = np.arange(n) % 2
    return pd.DataFrame({"sample_id": [f"invented_{i}" for i in range(n)], "x": x + int(bad_predictor),
                         "group": group, "y": 1 + 0.75 * x + 0.6 * group, "raw_x": raw})


def mock_backend(monkeypatch, *, failed=False, bad_predictor=False):
    calls = []
    monkeypatch.setattr(ex, "_runtime_manifest", lambda runtime: {"mocked_test_boundary": True})
    def capture(command, cwd, timeout, limit, stdout_path, stderr_path):
        task = read_json(cwd / "input/task.json")
        assert task["population"] == "Invented source only"
        assert task["n_rows"] == 10
        assert not (cwd / "input/observed.csv").exists()
        calls.append(task)
        source_frame(task, bad_predictor=bad_predictor).to_csv(cwd / "output/generated.csv", index=False)
        write(cwd / "output/worker_report.json", {"status": "failed" if failed else "completed", "generator_started": True})
        stdout_path.write_text("Invented mocked backend; no generator execution here.\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        return {"returncode": 2 if failed else 0, "host_timeout": False, "logs": {}}
    monkeypatch.setattr(ex, "_capture", capture)
    return calls


def run(root, candidate, index=0):
    return replay.run_source_replay(root, candidate, f"r{index}", "source_main", 70 + index)


def test_separate_source_task_same_bytes_and_strict_unavailability(tmp_path, monkeypatch):
    root, candidate = prepared(tmp_path)
    before = {p.relative_to(candidate).as_posix(): sha256(p) for p in candidate.rglob("*") if p.is_file()}
    calls = mock_backend(monkeypatch)
    report = run(root, candidate)
    assert len(calls) == 1 and report["status"] == "success"
    record = report["context"]
    assert record["generation_link_verified"] is True
    strict = record["strict_feedback"]["checks"][0]
    assert strict["semantic_status"] == "unavailable" and strict["calculation"] is None
    assert strict["status"] == "not_computable" and strict["difference"] is None
    projection = record["assumed_diagnostics"][0]
    assert projection["label"] == "assumption_dependent_source_projection"
    assert projection["calculation"]["value"] == pytest.approx(0.75)
    assert record["predictor_checks"][0]["n_reference"] == 10
    child = root / replay.FOLDER / "r0/bundle"
    for name in replay._CORE:
        assert sha256(child / "candidates/source" / name) == sha256(candidate / name)
    assert read_json(root / "task.json")["n_rows"] == 8
    assert read_json(child / "task.json")["n_rows"] == 10
    assert sha256(candidate / "whole_cohort_feedback.json") != sha256(child / "candidates/source/whole_cohort_feedback.json")
    assert before == {p.relative_to(candidate).as_posix(): sha256(p) for p in candidate.rglob("*") if p.is_file()}
    assert replay.verify_source_replay(root, "r0", candidate=candidate) == report
    verify_candidate(root, candidate)


def test_no_parent_execution_or_target_rows_read(tmp_path, monkeypatch):
    root, candidate = prepared(tmp_path)
    poison = root / "executions/target/output"
    poison.mkdir(parents=True)
    (poison / "generated.csv").write_text("DO NOT READ TARGET", encoding="utf-8")
    original_read = replay.read_table
    def guarded(path, *args, **kwargs):
        assert str(root / "executions") not in str(path)
        return original_read(path, *args, **kwargs)
    monkeypatch.setattr(replay, "read_table", guarded)
    mock_backend(monkeypatch)
    assert run(root, candidate)["status"] == "success"


def test_preflight_is_metadata_only_and_does_not_need_frozen_parent(tmp_path, monkeypatch):
    root, candidate = prepared(tmp_path, freeze=False)
    monkeypatch.setattr(ex, "run_candidate", lambda *a, **k: pytest.fail("preflight executed"))
    monkeypatch.setattr(replay, "read_table", lambda *a, **k: pytest.fail("preflight read rows"))
    assert replay.preflight(root, candidate)["contexts"][0]["semantic_preflight"]["checks"][0]["semantic_status"] == "unavailable"
    assert not (root / replay.FOLDER).exists()


def test_strict_semantic_error_never_falls_back_or_reserves(tmp_path, monkeypatch):
    def edit(root, candidate, plan, recipe, semantics):
        semantics["bindings"][0]["source_operator"]["term"] = "group"
    root, candidate = prepared(tmp_path, edit=edit)
    monkeypatch.setattr(ex, "run_candidate", lambda *a, **k: pytest.fail("invalid semantics executed"))
    monkeypatch.setattr(replay.source_checks, "apply_operator", lambda *a, **k: pytest.fail("fallback arithmetic"))
    with pytest.raises(ValueError):
        run(root, candidate)
    assert not (root / replay.FOLDER).exists()


@pytest.mark.parametrize("mistake", ["adjustment", "outcome_units", "unresolved_definition", "unchecked_transform"])
def test_assumed_lane_cannot_bypass_source_definition_or_units(tmp_path, monkeypatch, mistake):
    def edit(root, candidate, plan, recipe, semantics):
        if mistake == "adjustment":
            evidence = read_json(candidate / "evidence.json")
            next(i for i in evidence["items"] if i["id"] == "E_slope")["adjustment"] = []
            write(candidate / "evidence.json", evidence)
            semantics["evidence_sha256"] = sha256(candidate / "evidence.json")
        elif mistake == "outcome_units":
            plan["contexts"][0]["columns"][3]["unit"] = "other_outcome_unit"
        elif mistake == "unresolved_definition":
            semantics["bindings"][0].update(definition_status="unsupported", source_operator=None, source_variable_units={})
        else:
            plan["contexts"][0]["predictor_checks"] = []
    root, candidate = prepared(tmp_path, edit=edit)
    monkeypatch.setattr(ex, "run_candidate", lambda *a, **k: pytest.fail("invalid assumed lane executed"))
    with pytest.raises(ValueError):
        run(root, candidate)
    assert not (root / replay.FOLDER).exists()


def test_predictor_check_must_cover_all_regression_rows(tmp_path, monkeypatch):
    def edit(root, candidate, plan, recipe, semantics):
        plan["contexts"][0]["predictor_checks"][0]["selection"] = [{"column": "group", "op": "eq", "value": 0}]
    root, candidate = prepared(tmp_path, edit=edit)
    mock_backend(monkeypatch)
    report = run(root, candidate)
    assert report["status"] == "failed"
    assert "without an identity check" in report["context"]["error"]["message"]
    assert report["context"]["strict_feedback"] is None


def test_failed_backend_and_failed_predictor_keep_failures(tmp_path, monkeypatch):
    root, candidate = prepared(tmp_path)
    mock_backend(monkeypatch, failed=True)
    first = run(root, candidate)
    assert first["status"] == "failed" and not first["context"]["generation_link_verified"]
    assert first["context"]["strict_feedback"] is None
    mock_backend(monkeypatch, bad_predictor=True)
    second = run(root, candidate, 1)
    assert second["status"] == "failed" and second["context"]["generation_link_verified"]
    assert "zscore identity" in second["context"]["error"]["message"]
    assert second["context"]["assumed_diagnostics"] == []
    assert replay.verify_source_replay(root, "r1") == second
    with pytest.raises(ValueError, match="budget exhausted"):
        run(root, candidate)


def test_interrupted_reservation_consumes_slot(tmp_path, monkeypatch):
    root, candidate = prepared(tmp_path)
    original = replay._make_child
    monkeypatch.setattr(replay, "_make_child", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("invented interruption")))
    with pytest.raises(RuntimeError, match="interruption"):
        run(root, candidate)
    assert (root / replay.FOLDER / "r0/request.json").exists()
    with pytest.raises(ValueError, match="append-only"):
        run(root, candidate)
    monkeypatch.setattr(replay, "_make_child", original)
    mock_backend(monkeypatch)
    assert run(root, candidate, 1)["status"] == "success"
    with pytest.raises(ValueError, match="budget exhausted"):
        run(root, candidate)


def test_protocol_cannot_reset_in_revision(tmp_path, monkeypatch):
    root, candidate = prepared(tmp_path)
    mock_backend(monkeypatch)
    run(root, candidate)
    revised = root / "candidates/revised"
    shutil.copytree(candidate, revised)
    (revised / "freeze.json").unlink()
    plan = read_json(revised / replay.PLAN)
    plan["budget"]["max_evaluations"] = 3
    plan["schedule"].append({"replay_id": "r2", "candidate": "candidates/revised", "context_id": "source_main", "seed": 72, "n_rows": 10})
    write(revised / replay.PLAN, plan)
    freeze_candidate(root, revised)
    with pytest.raises(ValueError, match="protocol changed"):
        replay.run_source_replay(root, revised, "r2", "source_main", 72)


@pytest.mark.parametrize("field", ["seed", "context", "id"])
def test_unscheduled_requests_fail_before_execution(tmp_path, monkeypatch, field):
    root, candidate = prepared(tmp_path)
    monkeypatch.setattr(ex, "run_candidate", lambda *a, **k: pytest.fail("unscheduled execution"))
    with pytest.raises(ValueError):
        replay.run_source_replay(root, candidate, "wrong" if field == "id" else "r0", "wrong" if field == "context" else "source_main", 99 if field == "seed" else 70)
    assert not (root / replay.FOLDER).exists()


@pytest.mark.parametrize("target", ["report", "output", "child_spec", "source_recipe", "extra_file"])
def test_tampering_is_detected(tmp_path, monkeypatch, target):
    root, candidate = prepared(tmp_path)
    mock_backend(monkeypatch)
    run(root, candidate)
    folder = root / replay.FOLDER / "r0"
    if target == "report":
        report = read_json(folder / "replay.json")
        report["context"]["assumed_diagnostics"][0]["calculation"]["value"] = 99
        write(folder / "replay.json", report)
    else:
        path = {"output": folder / "bundle/executions/replay/output/generated.csv",
                "child_spec": folder / "bundle/candidates/source/model_spec.json",
                "source_recipe": candidate / "source_contexts/recipe.json",
                "extra_file": folder / "unexpected.txt"}[target]
        with path.open("a", encoding="utf-8") as stream:
            stream.write(" \n")
    with pytest.raises(ValueError):
        replay.verify_source_replay(root, "r0")


def test_optional_schedule_context_need_not_be_used(tmp_path):
    def edit(root, candidate, plan, recipe, semantics):
        plan["schedule"][1]["context_id"] = "source_alt1"
    root, candidate = prepared(tmp_path, edit=edit)
    assert replay.preflight(root, candidate)["contexts"][0]["id"] == "source_main"


@pytest.mark.skipif(sys.platform != "win32", reason="Existing execution backend is Windows/WSL only")
def test_real_isolated_invented_source_reads_child_task(tmp_path):
    root, candidate = prepared(tmp_path, schedule_count=1)
    report = run(root, candidate)
    assert report["status"] == "success", report["context"]["error"]
    assert report["context"]["generation_link_verified"]
    assert report["context"]["strict_feedback"]["generator_execution_recorded"]
    assert report["context"]["assumed_diagnostics"][0]["calculation"]["value"] == pytest.approx(0.75)

