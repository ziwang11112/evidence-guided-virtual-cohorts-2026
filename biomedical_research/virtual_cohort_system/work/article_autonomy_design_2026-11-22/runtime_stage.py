"""Execute an agent-declared numeric whole-cohort schema in the project worker."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))
from cohort_harness import contracts, execution, lifecycle


LIMITS = dict(timeout_seconds=60, memory_mb=1536, output_bytes=20_000_000, log_bytes=50_000)
WORKER = PROJECT / "cohort_harness" / "_worker.py"


def _save(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, allow_nan=False, ensure_ascii=False, indent=2)
        stream.write("\n")


def _task(spec, n):
    contracts.require(isinstance(spec, dict), "model_spec must be an object")
    declared = spec.get("columns")
    contracts.require(isinstance(declared, list) and bool(declared),
                      "model_spec.columns must declare at least one numeric measurement")
    columns = [dict(name="row_id", kind="integer", unit="", role="identifier", nullable=False)]
    for declaration in declared:
        contracts.require(isinstance(declaration, dict) and {"name", "unit"} <= declaration.keys(),
                          "Each generated measurement needs its name and unit")
        columns.append(dict(name=declaration["name"], kind="number", unit=declaration["unit"],
                            role="generated", nullable=False))
    task = dict(schema_version=1, task_id="article_autonomy", mode="whole_cohort",
                population=spec.get("population", "User-requested paper population"),
                row_id="row_id", n_rows=n, columns=columns,
                information_policy=dict(mode="published_evidence", excluded_cohorts=[], allowed_tools=[]),
                budget=dict(source_queries=0, source_downloads=0, revisions=0))
    contracts.validate_task(task)
    return task


def _execute_seed(folder, inputs, task, seed, runtime):
    run = folder / f"seed_{seed}"
    stage, output = run / "input", run / "output"
    stage.mkdir(parents=True)
    output.mkdir()
    for name, path in inputs.items():
        shutil.copyfile(path, stage / name)
    _save(stage / "request.json", execution._limits(seed=seed, **LIMITS))
    hashes = {p.name: lifecycle.sha256(p) for p in stage.iterdir()}
    _save(run / "input_bindings.json", hashes)
    table, report = output / "generated.csv", output / "worker_report.json"
    table.touch(exist_ok=False)
    report.touch(exist_ok=False)
    command = execution._command(runtime, run, LIMITS["timeout_seconds"])
    _save(run / "launch.json", {"command": command, "backend": runtime["backend"]})
    receipt = {"seed": seed, "status": "failed", "table": None, "generator_executed": None}
    try:
        process = execution._capture(command, run, LIMITS["timeout_seconds"] + 20, LIMITS["log_bytes"],
                                     run / "stdout.log", run / "stderr.log")
        receipt["process"] = process
        contracts.require(report.stat().st_size <= 65_536, "Oversized worker report")
        worker = lifecycle.read_json(report) if report.stat().st_size else {}
        receipt["generator_executed"] = worker.get("generator_started")
        contracts.require(process["returncode"] == 0 and worker.get("status") == "completed"
                          and worker.get("generator_started") is True,
                          f"Isolated execution failed: {str(worker.get('error', 'see bounded worker logs'))[:500]}")
        probe = worker["pre_import_probe"]
        contracts.require(probe["mnt_visible"] is False and probe["home_visible"] is False
                          and probe["route_table"] == [], "Unexpected pre-import isolation probe")
        execution._csv_guard(table, task, LIMITS["output_bytes"])
        frame = lifecycle.read_table(table, task, output=True)
        contracts.validate_output(None, frame, task)
        contracts.require(lifecycle._files(output) == ["generated.csv", "worker_report.json"],
                          "Unexpected worker output")
        receipt.update(status="success", table=str(table.resolve()), sha256=lifecycle.sha256(table))
    except (OSError, ValueError, KeyError, TypeError) as error:
        receipt["error"] = f"{type(error).__name__}: {str(error)[:700]}"
    if hashes != {p.name: lifecycle.sha256(p) for p in stage.iterdir()}:
        receipt.update(status="failed", table=None, error="Staged inputs changed")
    _save(run / "execution.json", receipt)
    return receipt


def execute(spec: dict, generator_py: str, output_dir: Path, seeds: tuple[int, ...], n: int) -> dict:
    """Store an immutable local execution and return per-seed table paths or errors.

    The worker receives the submitted spec with the registered n. It executes
    generate(None, spec, seed), expecting row_id followed by the submitted
    measurement names. A fresh output directory is required for every attempt.
    """
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=False)
    result = {"status": "failed", "runs": []}
    try:
        contracts.require(bool(seeds) and len(set(seeds)) == len(seeds), "Unique seeds required")
        for seed in seeds:
            execution._limits(seed=seed, **LIMITS)
        task = _task(spec, n)
        contracts.require("n" not in spec or (type(spec["n"]) is int and spec["n"] == n),
                          "Submitted row count differs from requested count")
        source = output_dir / "generator.py"
        source.write_text(generator_py, encoding="utf-8", newline="\n")
        lifecycle.validate_program(source)
        _save(output_dir / "task.json", task)
        _save(output_dir / "model_spec.json", {**spec, "n": n})
        inputs = {"worker.py": WORKER, "generator.py": source,
                  "task.json": output_dir / "task.json", "model_spec.json": output_dir / "model_spec.json"}
        runtime = execution._runtime(None)
        _save(output_dir / "runtime_manifest.json", execution._runtime_manifest(runtime))
        for seed in seeds:
            result["runs"].append(_execute_seed(output_dir, inputs, task, seed, runtime))
        if all(record["status"] == "success" for record in result["runs"]):
            result["status"] = "success"
    except (OSError, TypeError, ValueError, KeyError) as error:
        result["error"] = f"{type(error).__name__}: {str(error)[:700]}"
    _save(output_dir / "result.json", result)
    return result
