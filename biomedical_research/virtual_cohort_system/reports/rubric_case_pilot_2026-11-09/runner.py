"""Sealed, bounded program execution for the developmental rubric case pilot.

The only author-code import happens in the trusted worker inside WSL/bubblewrap.
All six constructions are committed before any of the eighteen scheduled draws.
This runner performs schema validation only: no source feedback, reference reads,
clinical fits, trial draws, repairs, or revisions. Historical controllers are untouched.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness import contracts, execution, lifecycle
from cohort_harness.contracts import require

AUTHORS = ["HA", "HB", "HC", "LA", "LB", "LC"]
SEEDS = [9301, 9302, 9303]
N_ROWS = 3000
MAX_TABLES = 18
LIMITS = {"timeout_seconds": 45, "memory_mb": 1536,
          "output_bytes": 20_000_000, "log_bytes": 50_000}
OUTPUT_FILES = {"generator.py", "model_spec.json", "SOURCE_USE.json", "DECISION.md"}
STAGED_FILES = {"generator.py", "model_spec.json", "task.json", "request.json", "worker.py"}
WORKER = Path(execution.__file__).with_name("_worker.py")
CASE_COLUMNS = {
    "H": ["row_id", "age", "female", "bmi", "glucose", "hba1c"],
    "L": ["id", "age", "sex", "bmi", "total_cholesterol", "hdl_cholesterol"],
}


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return lifecycle.read_json(path)


def sha(path):
    return lifecycle.sha256(path)


def safe_path(relative, *, file=True):
    parts = lifecycle.safe_relative(relative)
    path = ROOT.joinpath(*parts)
    require(not any(lifecycle._link(p) for p in [path, *path.parents]), "Linked path rejected")
    require(path.resolve().is_relative_to(ROOT.resolve()), "Path escapes pilot")
    if file:
        require(path.is_file(), "Missing required file: " + relative)
    return path


def safe_file(relative):
    return safe_path(relative)


def file_inventory(directory):
    """Return every regular file; do not omit arbitrary freeze-named files."""
    require(directory.is_dir() and not lifecycle._link(directory), "Invalid artifact directory")
    result = {}
    for path in sorted(directory.rglob("*")):
        require(not any(lifecycle._link(p) for p in [path, *path.parents]), "Linked artifact rejected")
        require(path.is_file() or path.is_dir(), "Nonregular artifact rejected")
        require(path.resolve().is_relative_to(directory.resolve()), "Artifact escapes directory")
        if path.is_file():
            relative = path.relative_to(directory).as_posix()
            lifecycle.safe_relative(relative)
            result[relative] = sha(path)
    return result


def engine_hashes():
    """Trusted code commitments; never inspect or import an author's module."""
    paths = {"cohort_harness/" + p.name: p for p in (PROJECT / "cohort_harness").glob("*.py")}
    paths.update({
        "glycemia_provider": PROJECT / "work/main_study_freeze_2026-11-03/cases/ENSANUT2018/generated_feedback.py",
        "glycemia_estimator": PROJECT / "work/autonomous_research_cycle2_2026-10-31/analysis/analytical_engine.py",
        "lipid_provider": PROJECT / "work/evidence_use_cross_task_2026-11-05/lipid_provider.py",
        "lipid_estimator": PROJECT / "work/scaleup_2026-11-01/analysis/k02_analysis.py",
    })
    return {name: sha(path) for name, path in sorted(paths.items())}


def protocol():
    value = read(safe_file("PROTOCOL.json"))
    expected = {"authors": AUTHORS, "seeds": SEEDS, "n_rows": N_ROWS,
                "max_final_tables": MAX_TABLES, "limits": LIMITS,
                "revision_rounds": 0, "sampling_trials_before_seal": 0}
    for key, expected_value in expected.items():
        require(value.get(key) == expected_value, "Fixed protocol differs: " + key)
    execution._limits(**LIMITS, seed=SEEDS[0])
    return value


def _check_records(records):
    require(isinstance(records, dict) and bool(records), "Nonempty file commitments required")
    for relative, expected in records.items():
        require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected), "Invalid file commitment")
        require(sha(safe_file(relative)) == expected, "Committed input changed: " + relative)


def verify_design():
    """Check immutable author inputs without loading reference values."""
    protocol()
    design = read(safe_file("DESIGN_LOCK.json"))
    review = read(safe_file("DESIGN_REVIEW.json"))
    require(design.get("author_outputs_present") is False, "Design must precede author outputs")
    records = design.get("records")
    _check_records(records)
    require("PROTOCOL.json" in records, "Design must bind the protocol")
    require(not any(name.startswith("private_runs/") or "/output/" in name for name in records),
            "Design cannot include generated tables or author outputs")
    require(review.get("decision") == "PASS_TO_AUTHOR_DISPATCH" and
            review.get("blocking_findings") == [], "Design review has not passed")
    require(review.get("bound_inputs") == records, "Design review covers different inputs")
    for author in AUTHORS:
        prefix = f"bundles/{author}/"
        require(all(prefix + name in records for name in ("task.json", "request.json")),
                "Design lacks task/request for " + author)
        require(any(name.startswith(prefix + "sources/") for name in records),
                "Design lacks admitted sources for " + author)
        bundle = safe_path(prefix.rstrip("/"), file=False)
        actual = {prefix + name: digest for name, digest in file_inventory(bundle).items()
                  if not name.startswith("output/")}
        expected = {name: digest for name, digest in records.items() if name.startswith(prefix)}
        require(actual == expected, "Author input inventory changed: " + author)
        require(not (bundle / "observed.csv").exists(), "Participant rows are forbidden")
    return design


def task_contract(author):
    require(author in AUTHORS, "Unknown author")
    task = read(safe_file(f"bundles/{author}/task.json"))
    contracts.validate_task(task)
    require(task["mode"] == "whole_cohort" and task["n_rows"] == N_ROWS,
            "Expected the fixed whole-cohort task")
    require([c["name"] for c in task["columns"]] == CASE_COLUMNS[author[0]], "Wrong clinical task columns")
    require(task["budget"]["revisions"] == 0, "This pilot does not permit revision rounds")
    return task


def validate_submissions():
    """Static validation only; a generator is parsed, never imported on the host."""
    design = verify_design()
    records = {}
    for author in AUTHORS:
        task_contract(author)
        directory = safe_path(f"bundles/{author}/output", file=False)
        files = file_inventory(directory)
        require(set(files) == OUTPUT_FILES and all(p.is_file() for p in directory.iterdir()),
                "Author output must contain exactly four regular files: " + author)
        lifecycle.validate_program(directory / "generator.py")
        require(isinstance(read(directory / "model_spec.json"), dict), "Specification must be a JSON object")
        require(isinstance(read(directory / "SOURCE_USE.json"), dict), "Source-use record must be a JSON object")
        require(bool((directory / "DECISION.md").read_text(encoding="utf-8-sig").strip()), "Empty author decision")
        records.update({f"bundles/{author}/output/{name}": digest for name, digest in files.items()})
    return design, records


def implementation_review_bindings():
    return {name: sha(safe_file(name)) for name in ("runner.py", "evaluate.py", "PROTOCOL.json")}


def verify_implementation():
    review = read(safe_file("IMPLEMENTATION_REVIEW.json"))
    require(review.get("decision") == "PASS_TO_EXECUTE" and review.get("blocking_findings") == [],
            "Implementation review has not passed")
    require(review.get("bound_inputs") == implementation_review_bindings(), "Implementation review is stale")
    require(review.get("engine_sha256") == engine_hashes(), "Reviewed execution/analysis dependencies changed")
    return review


def required_batch_files():
    design = read(safe_file("DESIGN_LOCK.json"))
    return set(design["records"]) | {
        "DESIGN_LOCK.json", "DESIGN_REVIEW.json", "runner.py", "evaluate.py", "IMPLEMENTATION_REVIEW.json"
    } | {f"bundles/{author}/output/{name}" for author in AUTHORS for name in OUTPUT_FILES}


def batch_records():
    return {name: sha(safe_file(name)) for name in sorted(required_batch_files())}


def verify_batch():
    validate_submissions()
    verify_implementation()
    lock = read(safe_file("BATCH_LOCK.json"))
    require(lock.get("records") == batch_records(), "Batch file inventory or commitments changed")
    require(lock.get("engine_sha256") == engine_hashes(), "Trusted engine changed after seal")
    return protocol(), lock


def seal_batch():
    validate_submissions()
    verify_implementation()
    require(not inventory(), "Cannot seal after sampling starts")
    require(not safe_path("RUNNING.lock", file=False).exists(), "An execution operation is active")
    lock = {"schema_version": 1, "kind": "rubric_case_pilot_batch_v1", "created_utc": now(),
            "records": batch_records(), "engine_sha256": engine_hashes(),
            "authors": AUTHORS, "seeds": SEEDS, "all_author_outputs_fixed_before_sampling": True}
    execution._write(safe_path("BATCH_LOCK.json", file=False), lock)
    verify_batch()
    return lock


def inventory():
    base = safe_path("private_runs", file=False)
    if not base.exists():
        return {}
    require(base.is_dir(), "Invalid attempt root")
    found = {}
    for author_dir in base.iterdir():
        require(author_dir.is_dir() and not lifecycle._link(author_dir) and author_dir.name in AUTHORS,
                "Unknown attempt author or linked directory")
        for run in author_dir.iterdir():
            require(run.is_dir() and not lifecycle._link(run) and run.name in {f"seed_{s}" for s in SEEDS},
                    "Unscheduled seed, retry, or unexpected attempt artifact")
            found[(author_dir.name, int(run.name[5:]))] = run
    require(len(found) <= MAX_TABLES, "Physical attempt budget exceeded")
    return found


def run_one(author, seed):
    """One create-only slot. Called by run_author under the global operation lock."""
    _, lock = verify_batch()
    require(author in AUTHORS and seed in SEEDS, "Unscheduled author/seed")
    operation = read(safe_file("RUNNING.lock"))
    require(operation.get("author") == author and seed in operation.get("seeds", []), "Execution lock does not cover slot")
    attempts = inventory()
    require((author, seed) not in attempts and len(attempts) < MAX_TABLES, "Attempt already consumed or budget exhausted")
    task = task_contract(author)
    submitted = safe_path(f"bundles/{author}/output", file=False)
    run = safe_path(f"private_runs/{author}/seed_{seed}", file=False)
    run.mkdir(parents=True, exist_ok=False)
    receipt = {"kind": "rubric_case_pilot_execution_v1", "status": "failed", "author": author,
               "seed": seed, "n_rows": N_ROWS, "started_utc": now(), "reference_read": False,
               "source_feedback": False, "generator_executed": False,
               "isolation_scope": "generator_process_only", "agent_isolation": "not_provided",
               "batch_lock_sha256": sha(ROOT / "BATCH_LOCK.json"), "engine_sha256": lock["engine_sha256"],
               "limits": execution._limits(**LIMITS, seed=seed), "process": None, "error": None,
               "files": {}, "generated_sha256": None, "failure_class": None}
    execution._write(run / "ATTEMPT.json", {key: receipt[key] for key in
                     ("kind", "author", "seed", "n_rows", "started_utc", "batch_lock_sha256", "limits")})
    stage, output = run / "input", run / "output"
    phase = "infrastructure"
    bindings = None
    expected_output_inventory = None
    try:
        stage.mkdir(); output.mkdir()
        copies = {"generator.py": submitted / "generator.py", "model_spec.json": submitted / "model_spec.json",
                  "task.json": safe_file(f"bundles/{author}/task.json"), "worker.py": WORKER}
        for name, source in copies.items():
            (stage / name).write_bytes(source.read_bytes())
        execution._write(stage / "request.json", receipt["limits"])
        bindings = file_inventory(stage)
        require(set(bindings) == STAGED_FILES, "Unexpected staged file inventory")
        require(all(bindings[name] == sha(source) for name, source in copies.items()), "Input changed during staging")
        execution._write(run / "input_bindings.json", bindings)
        runtime = execution._runtime(None)
        execution._write(run / "runtime_manifest.json", execution._runtime_manifest(runtime))
        for name in ("generated.csv", "worker_report.json"):
            (output / name).touch(exist_ok=False)
        expected_output_inventory = {"generated.csv", "worker_report.json"}
        command = execution._command(runtime, run, LIMITS["timeout_seconds"])
        execution._write(run / "launch.json", {"command": command, "runtime": runtime,
                                               "network": "unshared", "input": "read_only",
                                               "reference_staged": False, "source_staged": False,
                                               "worker_sha256": bindings["worker.py"]})
        verify_batch()
        receipt["generator_executed"] = None
        receipt["process"] = execution._capture(command, run, LIMITS["timeout_seconds"] + 20,
                                                 LIMITS["log_bytes"], run / "stdout.log", run / "stderr.log")
        process = receipt["process"]
        if process["host_timeout"] or process["returncode"] in {124, 137, -9}:
            receipt["status"] = "timeout"
        require((output / "worker_report.json").stat().st_size <= 65536, "Oversized worker report")
        worker = read(output / "worker_report.json") if (output / "worker_report.json").stat().st_size else {}
        require(isinstance(worker, dict), "Worker report must be an object")
        if worker:
            require(type(worker.get("generator_started")) is bool, "Invalid worker entry report")
            receipt["generator_executed"] = worker["generator_started"]
        phase = "worker_result"
        require(process["returncode"] == 0 and not process["host_timeout"], "Worker failed or timed out")
        require(worker.get("status") == "completed" and worker.get("generator_started") is True,
                "No completed generator")
        phase = "output_validation"
        execution._csv_guard(output / "generated.csv", task, LIMITS["output_bytes"])
        frame = lifecycle.read_table(output / "generated.csv", task, output=True)
        contracts.validate_output(None, frame, task)
        phase = "integrity"
        require(file_inventory(stage) == bindings, "Staged inputs changed")
        require(set(file_inventory(output)) == {"generated.csv", "worker_report.json"}, "Unexpected output artifact")
        verify_batch()
        receipt.update(status="success", generated_sha256=sha(output / "generated.csv"))
    except BaseException as error:
        receipt["error"] = {"type": type(error).__name__, "message": str(error)[:1500]}
        receipt["failure_class"] = (
            "author_execution_or_output" if receipt["generator_executed"] is True
            and phase in {"worker_result", "output_validation"}
            else "infrastructure_unknown_or_integrity")
        if not isinstance(error, Exception):
            raise
    finally:
        receipt["completed_utc"] = now()
        # A model exception or malformed CSV must not bypass immutability checks.
        # Any independent audit failure overrides an ordinary author failure.
        try:
            verify_batch()
            if bindings is not None:
                require(file_inventory(stage) == bindings, "Staged inputs changed (final audit)")
            if expected_output_inventory is not None:
                require(set(file_inventory(output)) == expected_output_inventory,
                        "Unexpected output inventory (final audit)")
        except Exception as audit_error:
            receipt["preceding_error"] = receipt["error"]
            receipt.update(status="failed", failure_class="infrastructure_unknown_or_integrity",
                           error={"type": type(audit_error).__name__, "message": str(audit_error)[:1500]})
        try:
            receipt["files"] = file_inventory(run)
        except Exception as error:
            receipt.update(status="failed", files={}, failure_class="infrastructure_unknown_or_integrity",
                           error={"type": type(error).__name__, "message": str(error)[:1500]})
        execution._write(run / "execution.json", receipt)
    return receipt


def run_author(author, seed=None):
    verify_batch()
    require(author in AUTHORS and (seed is None or seed in SEEDS), "Unscheduled author/seed")
    selected = SEEDS if seed is None else [seed]
    require(not any((author, value) in inventory() for value in selected), "Selected slot already consumed")
    require(not safe_path("BATCH_CLOSURE.json", file=False).exists(), "Batch is closed")
    busy = safe_path("RUNNING.lock", file=False)
    execution._write(busy, {"author": author, "seeds": selected, "started_utc": now()})
    completed = False
    try:
        results = []
        for value in selected:
            result = run_one(author, value)
            results.append(result)
            require(result["failure_class"] != "infrastructure_unknown_or_integrity",
                    "Infrastructure, unknown-entry or integrity failure: batch halted; consumed receipt and RUNNING.lock retained for audit")
        completed = True
        return results
    finally:
        # An interruption leaves a lock and its consumed slot for explicit audit.
        if completed:
            busy.unlink()


def verify_execution(author, seed):
    verify_batch()
    require(author in AUTHORS and seed in SEEDS, "Unscheduled author/seed")
    run = inventory().get((author, seed))
    require(run is not None, "Unattempted slot")
    receipt = read(run / "execution.json")
    require(receipt.get("kind") == "rubric_case_pilot_execution_v1" and
            (receipt.get("author"), receipt.get("seed"), receipt.get("n_rows")) == (author, seed, N_ROWS),
            "Execution identity differs")
    require(receipt.get("status") in {"success", "failed", "timeout"}, "Unknown execution status")
    require(receipt.get("failure_class") in {None, "author_execution_or_output", "infrastructure_unknown_or_integrity"},
            "Unknown failure classification")
    require((receipt["status"] == "success") == (receipt["failure_class"] is None),
            "Execution status and failure class disagree")
    if receipt["failure_class"] == "author_execution_or_output":
        require(receipt.get("generator_executed") is True, "Author failure requires confirmed generator entry")
    require(receipt.get("reference_read") is False and receipt.get("source_feedback") is False and
            receipt.get("isolation_scope") == "generator_process_only" and receipt.get("agent_isolation") == "not_provided",
            "Execution scope differs")
    require(receipt.get("batch_lock_sha256") == sha(ROOT / "BATCH_LOCK.json") and
            receipt.get("engine_sha256") == engine_hashes(), "Execution commitment changed")
    require(receipt.get("limits") == execution._limits(**LIMITS, seed=seed), "Wrong execution seed or limits")
    actual = file_inventory(run)
    actual.pop("execution.json", None)
    require(actual == receipt.get("files"), "Attempt file inventory or hashes changed")
    require(read(run / "ATTEMPT.json") == {key: receipt[key] for key in
            ("kind", "author", "seed", "n_rows", "started_utc", "batch_lock_sha256", "limits")}, "Attempt reservation differs")
    if receipt["status"] == "success" or receipt["failure_class"] == "author_execution_or_output":
        stage, output = run / "input", run / "output"
        bindings = read(run / "input_bindings.json")
        require(set(bindings) == STAGED_FILES and file_inventory(stage) == bindings, "Staged inventory differs")
        for name, original in {"generator.py": safe_file(f"bundles/{author}/output/generator.py"),
                               "model_spec.json": safe_file(f"bundles/{author}/output/model_spec.json"),
                               "task.json": safe_file(f"bundles/{author}/task.json"), "worker.py": WORKER}.items():
            require(bindings[name] == sha(original), "Staged input differs: " + name)
        require(read(stage / "request.json") == receipt["limits"], "Staged request differs")
        launch = read(run / "launch.json")
        require(launch["runtime"] == execution.DEFAULT_RUNTIME and
                launch["command"] == execution._command(execution.DEFAULT_RUNTIME, run, LIMITS["timeout_seconds"]) and
                launch["worker_sha256"] == bindings["worker.py"] and launch["reference_staged"] is False and
                launch["source_staged"] is False, "Launch configuration differs")
        require(set(file_inventory(output)) == {"generated.csv", "worker_report.json"}, "Unexpected output artifact")
        require(read(output / "worker_report.json").get("generator_started") is True,
                "Successful or author-failed attempt needs confirmed worker entry")
    if receipt["status"] == "success":
        require(receipt.get("generator_executed") is True and receipt["process"]["returncode"] == 0 and
                receipt["process"]["host_timeout"] is False, "Successful receipt lacks completed process")
        require(set(file_inventory(output)) == {"generated.csv", "worker_report.json"}, "Unexpected output artifact")
        require(receipt["generated_sha256"] == sha(output / "generated.csv"), "Generated table changed")
        task = task_contract(author)
        execution._csv_guard(output / "generated.csv", task, LIMITS["output_bytes"])
        contracts.validate_output(None, lifecycle.read_table(output / "generated.csv", task, output=True), task)
    return receipt


def batch_state():
    verify_batch()
    require(not safe_path("RUNNING.lock", file=False).exists(), "Execution active or interruption requires audit")
    attempts = inventory()
    require(set(attempts) == {(author, seed) for author in AUTHORS for seed in SEEDS}, "All eighteen slots must be attempted")
    records = []
    for author in AUTHORS:
        for seed in SEEDS:
            receipt = verify_execution(author, seed)
            records.append({"author": author, "seed": seed, "status": receipt["status"],
                            "execution_sha256": sha(attempts[(author, seed)] / "execution.json")})
    return {"kind": "rubric_case_pilot_closure_v1", "batch_lock_sha256": sha(ROOT / "BATCH_LOCK.json"),
            "physical_attempts": len(records), "scheduled_final_slots": MAX_TABLES,
            "reference_read": False, "source_feedback_returned": False, "records": records}


def close_batch():
    state = batch_state()
    execution._write(safe_path("BATCH_CLOSURE.json", file=False), state)
    return state


def closure_gate():
    state = read(safe_file("BATCH_CLOSURE.json"))
    require(state == batch_state(), "Closed batch commitments changed")
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["validate", "seal", "run", "status", "verify", "close", "gate"])
    parser.add_argument("--author", choices=AUTHORS)
    parser.add_argument("--seed", type=int, choices=SEEDS)
    args = parser.parse_args()
    failed = False
    if args.action == "validate":
        _, records = validate_submissions()
        result = {"validated_authors": AUTHORS, "author_output_files": len(records), "programs_executed": 0}
    elif args.action == "seal":
        result = seal_batch()
    elif args.action == "run":
        require(args.author is not None, "--author required")
        results = run_author(args.author, args.seed)
        result = [{key: item.get(key) for key in ("author", "seed", "status", "error", "generated_sha256")} for item in results]
        failed = any(item["status"] != "success" for item in results)
    elif args.action == "status":
        result = {"slots_consumed": len(inventory()), "slots_planned": MAX_TABLES,
                  "execution_lock_present": safe_path("RUNNING.lock", file=False).exists(),
                  "attempted_slots": [{"author": author, "seed": seed} for author, seed in sorted(inventory())]}
    elif args.action == "verify":
        require(args.author is not None and args.seed is not None, "--author and --seed required")
        result = verify_execution(args.author, args.seed)
    else:
        result = close_batch() if args.action == "close" else closure_gate()
    print(json.dumps(result, indent=2, allow_nan=False))
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
