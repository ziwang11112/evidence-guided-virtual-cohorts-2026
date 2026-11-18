"""Create-only construction seals and unchanged WSL/bubblewrap execution.

No provider calls, credential access, reference access, scientific feedback, or
unrestricted generator execution are implemented here. Imported author code is
confined to the existing trusted worker in the approved isolated backend.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
sys.path.insert(0, str(PROJECT))
sys.dont_write_bytecode = True
from cohort_harness import contracts, execution, lifecycle

SEEDS = [31001, 31003, 31007]
N_ROWS = 3000
MAX_CONSTRUCTIONS = 20
MAX_TABLES = 60
LIMITS = dict(timeout_seconds=60, memory_mb=1536, output_bytes=20_000_000, log_bytes=50_000)
WORKER = PROJECT / "cohort_harness/_worker.py"
CASES = {"PNS": ["row_id", "age", "female", "bmi", "sbp", "dbp"],
         "lipids": ["id", "age", "sex", "bmi", "total_cholesterol", "hdl_cholesterol"]}
STAGED_FILES = {"generator.py", "model_spec.json", "task.json", "request.json", "worker.py"}


def now(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return lifecycle.read_json(path)
def require(condition, message): contracts.require(condition, message)
def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    execution._write(path, obj)
def safe(name, *, file=True): return lifecycle._path(ROOT, name, file=file)
def inventory(path): return {name: sha(lifecycle._path(path, name)) for name in lifecycle._files(path)}


def implementation_hashes():
    paths = [Path(__file__), ROOT / "analyze_pilot.py", ROOT / "EVALUATION_PROTOCOL.json",
             ROOT / "EVALUATION_PROTOCOL.md", WORKER,
             PROJECT / "cohort_harness/execution.py", PROJECT / "cohort_harness/contracts.py",
             PROJECT / "cohort_harness/lifecycle.py",
             PROJECT / "work/next_case_validation_2026-11-09/runtime/analysis_tools.py",
             PROJECT / "work/scaleup_2026-11-01/analysis/k02_analysis.py"]
    return {path.relative_to(PROJECT).as_posix(): sha(path) for path in paths}


def task_for(row):
    task = read(safe(row["task_path"]))
    contracts.validate_task(task)
    require(task["mode"] == "whole_cohort" and task["n_rows"] == N_ROWS, "Wrong task mode/count")
    require([c["name"] for c in task["columns"]] == CASES[row["case_id"]], "Wrong case columns/order")
    return task


def validate_generated_output(frame, task, case):
    """Contract validation plus the explicitly supplied strict lipid eligibility."""
    contracts.validate_output(None, frame, task)
    if case == "lipids":
        require(all(bool(frame[name].gt(0).all()) for name in
                    ["bmi", "total_cholesterol", "hdl_cholesterol"]),
                "Lipid BMI, TC and HDL must be strictly positive; no row removal")


def _record(row):
    allowed = {"construction_id", "case_id", "task_path", "candidate_path", "status", "model_config",
               "context", "repair_count", "failure_reason", "task_sha256", "files"}
    require(isinstance(row, dict) and set(row) <= allowed, "Unexpected construction record fields")
    required = {"construction_id", "case_id", "task_path", "candidate_path", "status", "model_config", "context"}
    require(required <= set(row), "Missing construction fields")
    execution._name(row["construction_id"])
    require(row["case_id"] in CASES and row["status"] in {"sealed", "failed"}, "Wrong case/status")
    require(isinstance(row["model_config"], str) and bool(row["model_config"]), "Model configuration required")
    require(type(row["context"]) in {str, int} and row["context"] not in {"", 0}, "Context identity required")
    require(type(row.get("repair_count", 0)) is int and row.get("repair_count", 0) in {0, 1}, "At most one mechanical repair")
    task = task_for(row)
    result = dict(row, task_sha256=sha(safe(row["task_path"])), files={})
    if row["status"] == "failed":
        require(row["candidate_path"] is None, "Failed construction cannot nominate a generator")
    else:
        folder = safe(row["candidate_path"], file=False)
        require(folder.is_dir(), "Candidate directory missing")
        require({"generator.py", "model_spec.json", "decision_record.json"} <= set(lifecycle._files(folder)), "Missing final artifacts")
        lifecycle.validate_program(folder / "generator.py")
        spec = read(folder / "model_spec.json")
        require(set(spec) == {"task", "model"} and spec["task"] == task and isinstance(spec["model"], dict), "Expected exact task/model wrapper")
        require(isinstance(read(folder / "decision_record.json"), dict), "Decision record must be an object")
        result["files"] = inventory(folder)
    return result


def _check_schedule(rows):
    require(len(rows) == MAX_CONSTRUCTIONS and len({r["construction_id"] for r in rows}) == MAX_CONSTRUCTIONS,
            "Exactly twenty unique construction outcomes required")
    models = {r["model_config"] for r in rows}
    contexts = {r["context"] for r in rows}
    require(len(models) == 5 and len(contexts) == 2, "Expected five model configurations and two contexts")
    require({(r["case_id"], r["model_config"], r["context"]) for r in rows} ==
            {(case, model, context) for case in CASES for model in models for context in contexts},
            "Incomplete case/model/context matrix")


def _history_hashes():
    calls = safe("calls", file=False)
    require(calls.is_dir(), "Captured initial/repair call history required before construction closure")
    values = {"calls/" + name: digest for name, digest in inventory(calls).items()}
    require(bool(values), "Empty construction history")
    for name in ["CONSTRUCTION_OUTCOMES.json", "LAUNCH_FREEZE.json", "RUN_PLAN.json"]:
        path = safe(name, file=False)
        if path.exists(): values[name] = sha(path)
    return values


def create_construction_closure(records):
    """Root calls after all initial/final submissions and mechanical repairs close."""
    require(not safe("executions", file=False).exists(), "Cannot seal after execution starts")
    rows = [_record(row) for row in records]
    _check_schedule(rows)
    protocol = read(safe("EVALUATION_PROTOCOL.json"))
    require(protocol["seeds"] == SEEDS and protocol["n_rows"] == N_ROWS and protocol["max_tables"] == MAX_TABLES,
            "Evaluation protocol schedule changed")
    snapshot = safe("_host_only/REFERENCE_SNAPSHOT.json")
    value = {"schema_version": 1, "kind": "api_pilot_construction_closure_v1", "created_utc": now(),
             "records": rows, "seeds": SEEDS, "n_rows": N_ROWS, "max_tables": MAX_TABLES,
             "all_initial_and_final_models_sealed": True, "no_scientific_feedback_during_construction": True,
             "evaluation_protocol_sha256": sha(ROOT / "EVALUATION_PROTOCOL.json"),
             "reference_snapshot_sha256": sha(snapshot), "implementation_hashes": implementation_hashes(),
             "construction_history_files": _history_hashes()}
    write(safe("CONSTRUCTION_CLOSURE.json", file=False), value)
    return verify_construction_closure()


def verify_construction_closure():
    value = read(safe("CONSTRUCTION_CLOSURE.json"))
    require(value["kind"] == "api_pilot_construction_closure_v1" and value["all_initial_and_final_models_sealed"] is True,
            "Invalid construction closure")
    require(value["no_scientific_feedback_during_construction"] is True, "Construction feedback boundary changed")
    require(value["seeds"] == SEEDS and value["n_rows"] == N_ROWS and value["max_tables"] == MAX_TABLES, "Changed schedule")
    require(value["implementation_hashes"] == implementation_hashes(), "Frozen implementation changed")
    require(value["evaluation_protocol_sha256"] == sha(safe("EVALUATION_PROTOCOL.json")), "Protocol changed")
    require(value["reference_snapshot_sha256"] == sha(safe("_host_only/REFERENCE_SNAPSHOT.json")), "Aggregate snapshot changed")
    rows = value["records"]
    _check_schedule(rows)
    require(value["construction_history_files"] == _history_hashes(), "Initial/repair construction history changed")
    require(all(_record(row) == row for row in rows), "Construction artifacts changed")
    return value


def approve_frozen_execution(review_note):
    """Root-controlled gate; this function itself executes no generator."""
    verify_construction_closure()
    require(isinstance(review_note, str) and bool(review_note.strip()), "Root review note required")
    value = {"schema_version": 1, "kind": "root_freeze_approval_v1", "created_utc": now(),
             "construction_closure_sha256": sha(safe("CONSTRUCTION_CLOSURE.json")),
             "implementation_hashes": implementation_hashes(), "review_note": review_note}
    write(safe("FREEZE_APPROVAL.json", file=False), value)
    return value


def approval_gate():
    closed = verify_construction_closure()
    approved = read(safe("FREEZE_APPROVAL.json"))
    require(approved["kind"] == "root_freeze_approval_v1" and
            approved["construction_closure_sha256"] == sha(safe("CONSTRUCTION_CLOSURE.json")) and
            approved["implementation_hashes"] == implementation_hashes(), "Root freeze approval differs")
    return closed


def runtime_probe():
    """Trusted runtime inspection only; does not import or execute a generator."""
    result = {"created_utc": now(), "generator_executed": False, "runtime": execution.DEFAULT_RUNTIME,
              "fallback_allowed": False,
              "availability_scope": "trusted runtime imports and known-file hashes only; no namespace launch or generator execution in this probe"}
    try:
        result.update(status="available", manifest=execution._runtime_manifest(execution._runtime(None)))
    except Exception as error:
        result.update(status="unavailable", error_type=type(error).__name__, error=str(error))
    return result


def run_inventory():
    root = safe("executions", file=False)
    if not root.exists(): return {}
    closed = verify_construction_closure()
    ids = {r["construction_id"] for r in closed["records"]}
    found = {}
    for directory in root.iterdir():
        require(directory.is_dir() and not lifecycle._link(directory) and directory.name in ids, "Unexpected construction run")
        for run in directory.iterdir():
            require(run.is_dir() and not lifecycle._link(run) and run.name in {f"seed_{s}" for s in SEEDS}, "Unexpected run or retry")
            found[(directory.name, int(run.name[5:]))] = run
    require(len(found) <= MAX_TABLES, "Table budget exceeded")
    return found


def _run_one(row, seed):
    closed = approval_gate()
    require(row in closed["records"], "Execution row differs from sealed construction")
    operation = read(safe("RUNNING.lock"))
    require(operation.get("planned_slots") == MAX_TABLES, "Execution operation lock required")
    require(seed in SEEDS and (row["construction_id"], seed) not in run_inventory(), "Unscheduled or consumed slot")
    run = safe(f"executions/{row['construction_id']}/seed_{seed}", file=False)
    run.mkdir(parents=True, exist_ok=False)
    receipt = {"kind": "api_pilot_execution_v1", "construction_id": row["construction_id"], "case_id": row["case_id"],
               "seed": seed, "status": "failed", "created_utc": now(), "generator_executed": False,
               "construction_closure_sha256": sha(safe("CONSTRUCTION_CLOSURE.json")),
               "reference_read": False, "source_feedback": False, "isolation_scope": "generator_process_only",
               "agent_isolation": "not_provided", "limits": execution._limits(**LIMITS, seed=seed),
               "error": None, "failure_class": None, "process": None, "generated_sha256": None, "files": {}}
    write(run / "ATTEMPT.json", {key: receipt[key] for key in ("construction_id", "case_id", "seed", "created_utc", "limits")})
    bindings = None
    phase = "infrastructure"
    try:
        if row["status"] == "failed":
            receipt.update(status="construction_failed", failure_class="construction_failed")
        else:
            stage, output = run / "input", run / "output"
            stage.mkdir(); output.mkdir()
            candidate = safe(row["candidate_path"], file=False)
            copies = {"generator.py": candidate / "generator.py", "model_spec.json": candidate / "model_spec.json",
                      "task.json": safe(row["task_path"]), "worker.py": WORKER}
            for name, source in copies.items(): (stage / name).write_bytes(source.read_bytes())
            write(stage / "request.json", receipt["limits"])
            bindings = inventory(stage)
            require(set(bindings) == STAGED_FILES and all(bindings[n] == sha(p) for n,p in copies.items()), "Staging differs")
            write(run / "input_bindings.json", bindings)
            runtime = execution._runtime(None)
            write(run / "runtime_manifest.json", execution._runtime_manifest(runtime))
            for name in ("generated.csv", "worker_report.json"): (output / name).touch(exist_ok=False)
            command = execution._command(runtime, run, LIMITS["timeout_seconds"])
            write(run / "launch.json", {"command": command, "runtime": runtime, "worker_sha256": bindings["worker.py"],
                                        "reference_staged": False, "source_staged": False})
            approval_gate()
            receipt["generator_executed"] = None
            receipt["process"] = execution._capture(command, run, LIMITS["timeout_seconds"] + 20,
                LIMITS["log_bytes"], run / "stdout.log", run / "stderr.log")
            process = receipt["process"]
            require((output / "worker_report.json").stat().st_size <= 65536, "Oversized worker report")
            worker = read(output / "worker_report.json") if (output / "worker_report.json").stat().st_size else {}
            receipt["generator_executed"] = worker.get("generator_started")
            phase = "worker_result"
            if process["host_timeout"] or process["returncode"] in {124, 137, -9}: receipt["status"] = "timeout"
            require(process["returncode"] == 0 and worker.get("status") == "completed" and worker.get("generator_started") is True,
                    "Worker did not complete")
            phase = "output_validation"
            task = task_for(row)
            execution._csv_guard(output / "generated.csv", task, LIMITS["output_bytes"])
            validate_generated_output(lifecycle.read_table(output / "generated.csv", task, output=True), task, row["case_id"])
            receipt.update(status="success", generated_sha256=sha(output / "generated.csv"))
    except Exception as error:
        receipt.update(error={"type": type(error).__name__, "message": str(error)[:1500]}, failure_class=(
            "author_execution_or_output" if receipt["generator_executed"] is True and phase in {"worker_result", "output_validation"}
            else "infrastructure_unknown_or_integrity"))
    finally:
        try:
            approval_gate()
            if bindings is not None: require(inventory(run / "input") == bindings, "Input mutated")
            if (run / "output").exists():
                require(set(inventory(run / "output")) <= {"generated.csv", "worker_report.json"}, "Unexpected output artifact")
            receipt["files"] = inventory(run)
        except Exception as error:
            receipt.update(status="failed", failure_class="infrastructure_unknown_or_integrity",
                           error={"type": type(error).__name__, "message": str(error)[:1500]}, files={})
        receipt["completed_utc"] = now()
        write(run / "execution.json", receipt)
    return receipt


def verify_execution(construction_id, seed):
    closed = approval_gate()
    rows = [r for r in closed["records"] if r["construction_id"] == construction_id]
    require(len(rows) == 1 and seed in SEEDS, "Unscheduled execution")
    row = rows[0]
    run = run_inventory().get((construction_id, seed))
    require(run is not None, "Unconsumed slot")
    value = read(run / "execution.json")
    require(value["kind"] == "api_pilot_execution_v1" and value["construction_id"] == construction_id and
            value["seed"] == seed and value["case_id"] == row["case_id"], "Execution identity differs")
    require(value["status"] in {"success", "failed", "timeout", "construction_failed"}, "Wrong execution status")
    require(value["limits"] == execution._limits(**LIMITS, seed=seed), "Execution limits differ")
    require(value["reference_read"] is False and value["source_feedback"] is False and
            value["isolation_scope"] == "generator_process_only" and value["agent_isolation"] == "not_provided",
            "Execution scope differs")
    require(value["failure_class"] in {None,"construction_failed","author_execution_or_output","infrastructure_unknown_or_integrity"},
            "Unknown failure class")
    require((value["status"] == "success") == (value["failure_class"] is None), "Status/failure class mismatch")
    require((value["status"] == "construction_failed") == (row["status"] == "failed"), "Construction outcome mismatch")
    if value["failure_class"] == "author_execution_or_output":
        require(value["generator_executed"] is True, "Author failure requires confirmed entry")
    require(value["construction_closure_sha256"] == sha(safe("CONSTRUCTION_CLOSURE.json")), "Closure differs")
    actual = inventory(run); actual.pop("execution.json")
    require(actual == value["files"] and bool(actual), "Run artifact inventory changed")
    if value["status"] == "success" or value["failure_class"] == "author_execution_or_output":
        launch = read(run / "launch.json")
        require(launch["command"] == execution._command(execution.DEFAULT_RUNTIME, run, LIMITS["timeout_seconds"]) and
                launch["runtime"] == execution.DEFAULT_RUNTIME and launch["reference_staged"] is False and launch["source_staged"] is False,
                "Isolation launch differs")
        require(set(inventory(run / "input")) == STAGED_FILES, "Staged inventory differs")
        bindings = read(run / "input_bindings.json")
        require(inventory(run / "input") == bindings and read(run / "input/request.json") == value["limits"], "Staged bindings differ")
        candidate = safe(row["candidate_path"], file=False)
        for name, source in {"generator.py":candidate / "generator.py", "model_spec.json":candidate / "model_spec.json",
                             "task.json":safe(row["task_path"]), "worker.py":WORKER}.items():
            require(bindings[name] == sha(source), "Staged input differs from sealed source")
        require(set(inventory(run / "output")) == {"generated.csv","worker_report.json"}, "Output inventory differs")
    if value["status"] == "success":
        require(value["generator_executed"] is True and value["generated_sha256"] == sha(run / "output/generated.csv"), "Generated output changed")
        require(value["process"]["returncode"] == 0 and value["process"]["host_timeout"] is False, "Completed process missing")
        task = task_for(row)
        execution._csv_guard(run / "output/generated.csv", task, LIMITS["output_bytes"])
        validate_generated_output(lifecycle.read_table(run / "output/generated.csv", task, output=True), task, row["case_id"])
    return value


def run_all():
    closed = approval_gate()
    require(not run_inventory(), "Run-all is create-only; no silent restart")
    require(not safe("EXECUTION_CLOSURE.json", file=False).exists(), "Execution batch closed")
    busy = safe("RUNNING.lock", file=False)
    write(busy, {"created_utc": now(), "planned_slots": MAX_TABLES})
    completed = False
    try:
        for row in closed["records"]:
            for seed in SEEDS:
                result = _run_one(row, seed)
                require(result["failure_class"] != "infrastructure_unknown_or_integrity",
                        "Infrastructure/integrity failure: halted with consumed receipt and lock retained")
        completed = True
    finally:
        if completed: busy.unlink()
    return close_executions()


def close_executions():
    closed = approval_gate()
    require(not safe("RUNNING.lock", file=False).exists(), "Execution active or audit required")
    expected = {(r["construction_id"], seed) for r in closed["records"] for seed in SEEDS}
    require(set(run_inventory()) == expected, "All sixty scheduled slots must have outcomes")
    rows = []
    for construction_id, seed in sorted(expected):
        value = verify_execution(construction_id, seed)
        require(value["failure_class"] != "infrastructure_unknown_or_integrity", "Infrastructure/integrity failure requires audit before closure")
        path = run_inventory()[(construction_id, seed)] / "execution.json"
        rows.append({"construction_id": construction_id, "seed": seed, "status": value["status"], "execution_sha256": sha(path)})
    value = {"kind": "api_pilot_execution_closure_v1", "created_utc": now(), "records": rows,
             "scheduled_slots": MAX_TABLES, "physical_generator_attempts": sum(r["status"] != "construction_failed" for r in rows),
             "construction_closure_sha256": sha(safe("CONSTRUCTION_CLOSURE.json"))}
    write(safe("EXECUTION_CLOSURE.json", file=False), value)
    return value


def evaluation_gate():
    closed = approval_gate()
    require(not safe("RUNNING.lock", file=False).exists(), "Execution not closed")
    batch = read(safe("EXECUTION_CLOSURE.json"))
    require(batch["kind"] == "api_pilot_execution_closure_v1" and len(batch["records"]) == MAX_TABLES,
            "Missing execution closure")
    require(batch["construction_closure_sha256"] == sha(safe("CONSTRUCTION_CLOSURE.json")), "Execution closure changed")
    expected = {(r["construction_id"], s) for r in closed["records"] for s in SEEDS}
    require({(r["construction_id"], r["seed"]) for r in batch["records"]} == expected, "Wrong slot coverage")
    for row in batch["records"]:
        value = verify_execution(row["construction_id"], row["seed"])
        require(value["status"] == row["status"] and row["execution_sha256"] == sha(run_inventory()[(row["construction_id"], row["seed"])] / "execution.json"),
                "Execution receipt differs from closure")
    return closed, batch


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["probe", "verify", "run", "close"])
    args = parser.parse_args()
    result = {"probe": runtime_probe, "verify": verify_construction_closure, "run": run_all, "close": close_executions}[args.command]()
    print(json.dumps(result, indent=2, allow_nan=False))
