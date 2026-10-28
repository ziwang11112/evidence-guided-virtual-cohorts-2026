"""Fail-closed, generator-only WSL/bubblewrap execution.

The caller and literature Agent remain outside this sandbox. Receipts bind bytes
relative to their recorded hashes; they are not signatures or proof against a
host user rewriting both a receipt and its artifacts. Runtime paths are trusted
administrator configuration, not fields authored by a biomedical builder.
"""
from __future__ import annotations

from datetime import datetime, timezone
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import threading
import time

from .contracts import ContractError, exact_keys, require, validate_output
from .lifecycle import (_bundle, _candidate, _files, _path, read_json, read_table,
                        sha256, verify_candidate)

RUNTIME_ROOT = "/home/zwang/.cache/evidence-cohort-runtime/m2"
DEFAULT_RUNTIME = {
    "backend": "wsl_bubblewrap", "distribution": "Ubuntu-24.04",
    "venv_root": RUNTIME_ROOT + "/venv",
    "bwrap": RUNTIME_ROOT + "/bubblewrap/usr/bin/bwrap",
}


def _write(path: Path, obj: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def _name(value: str) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value),
            "Run ID must be a simple portable name")
    return value


def _runtime(value: dict | None) -> dict:
    value = dict(DEFAULT_RUNTIME if value is None else value)
    exact_keys(value, set(DEFAULT_RUNTIME), where="runtime")
    require(value == DEFAULT_RUNTIME, "Only the inspected task-specific Ubuntu runtime is supported")
    return value


def _wsl_path(path: Path) -> str:
    absolute = path.absolute()
    require(re.fullmatch(r"[A-Za-z]:", absolute.drive) is not None,
            "This adapter requires a local Windows drive path, not UNC or another backend")
    return "/mnt/" + absolute.drive[0].lower() + "/" + "/".join(absolute.parts[1:])


def _capture(command: list[str], cwd: Path, timeout: int, limit: int,
             stdout_path: Path, stderr_path: Path) -> dict:
    """Drain both pipes while retaining a bounded prefix; never buffer full logs."""
    process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stats = {}
    def drain(pipe, destination, name):
        total, kept = 0, 0
        with destination.open("xb") as stream:
            while chunk := pipe.read(8192):
                total += len(chunk)
                selected = chunk[:max(0, limit - kept)]
                stream.write(selected)
                kept += len(selected)
        pipe.close()
        stats[name] = {"bytes_seen": total, "bytes_saved": kept, "truncated": total > kept}
    threads = [threading.Thread(target=drain, args=(process.stdout, stdout_path, "stdout"), daemon=True),
               threading.Thread(target=drain, args=(process.stderr, stderr_path, "stderr"), daemon=True)]
    for thread in threads:
        thread.start()
    timed_out = False
    try:
        returncode = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        returncode = process.wait(timeout=5)
    for thread in threads:
        thread.join(timeout=5)
    require(not any(thread.is_alive() for thread in threads), "Process pipes failed to close after timeout")
    return {"returncode": returncode, "host_timeout": timed_out, "logs": stats}


def _runtime_manifest(runtime: dict) -> dict:
    """Read known runtime files through trusted Python; never import Agent code."""
    script = (
        "import sys,json,hashlib,pathlib,platform,numpy,pandas;"
        "v=pathlib.Path(sys.prefix);"
        "paths=[pathlib.Path(sys.executable).resolve(),v/'pyvenv.cfg',"
        "pathlib.Path(numpy.__file__),pathlib.Path(pandas.__file__),pathlib.Path(sys.argv[1])];"
        "print(json.dumps({'python':platform.python_version(),'numpy':numpy.__version__,"
        "'pandas':pandas.__version__,'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}))"
    )
    command = ["wsl.exe", "--distribution", runtime["distribution"], "--exec",
               runtime["venv_root"] + "/bin/python", "-I", "-c", script, runtime["bwrap"]]
    try:
        result = subprocess.run(command, capture_output=True, timeout=20, check=True)
        manifest = json.loads(result.stdout.decode("utf-8"))
    except (OSError, subprocess.SubprocessError, ValueError, UnicodeError) as error:
        raise ContractError("Required WSL runtime unavailable; no local execution fallback") from error
    require(isinstance(manifest, dict) and isinstance(manifest.get("files"), dict) and
            len(manifest["files"]) == 5, "Invalid runtime inspection result")
    return manifest


def _command(runtime: dict, directory: Path, timeout: int) -> list[str]:
    stage = _wsl_path(directory / "input")
    output = _wsl_path(directory / "output")
    return [
        "wsl.exe", "--distribution", runtime["distribution"], "--exec",
        "/usr/bin/timeout", "--signal=KILL", str(timeout + 2),
        runtime["bwrap"], "--unshare-all", "--unshare-user", "--die-with-parent", "--new-session",
        "--disable-userns", "--cap-drop", "ALL", "--clearenv",
        "--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib",
        "--ro-bind-try", "/lib64", "/lib64",
        "--ro-bind", runtime["venv_root"], "/runtime",
        "--ro-bind", stage, "/input",
        "--dir", "/output",
        "--bind", output + "/generated.csv", "/output/generated.csv",
        "--bind", output + "/worker_report.json", "/output/worker_report.json",
        "--proc", "/proc", "--remount-ro", "/proc",
        "--size", str(64 * 1024**2), "--tmpfs", "/tmp",
        "--size", str(1024**2), "--tmpfs", "/dev",
        "--dev-bind", "/dev/null", "/dev/null",
        "--dev-bind", "/dev/zero", "/dev/zero",
        "--dev-bind", "/dev/random", "/dev/random",
        "--dev-bind", "/dev/urandom", "/dev/urandom",
        "--ro-bind-try", "/etc/ld.so.cache", "/etc/ld.so.cache",
        "--remount-ro", "/",
        "--chdir", "/tmp",
        "--setenv", "PATH", "/runtime/bin:/usr/bin",
        "--setenv", "HOME", "/tmp",
        "--setenv", "TMPDIR", "/tmp",
        "--setenv", "LANG", "C.UTF-8",
        "--setenv", "OPENBLAS_NUM_THREADS", "1",
        "--setenv", "OMP_NUM_THREADS", "1",
        "--setenv", "MKL_NUM_THREADS", "1",
        "--setenv", "NUMEXPR_NUM_THREADS", "1",
        "/runtime/bin/python", "-I", "-B", "/input/worker.py",
    ]


def _limits(timeout_seconds, memory_mb, output_bytes, log_bytes, seed):
    for name, value, lower, upper in (
        ("timeout_seconds", timeout_seconds, 1, 300), ("memory_mb", memory_mb, 256, 8192),
        ("output_bytes", output_bytes, 1024, 100_000_000), ("log_bytes", log_bytes, 1024, 1_000_000),
        ("seed", seed, 0, 2**32 - 1),
    ):
        require(type(value) is int and lower <= value <= upper, f"Invalid {name}")
    return {"timeout_seconds": timeout_seconds, "memory_mb": memory_mb,
            "output_bytes": output_bytes, "log_bytes": log_bytes, "seed": seed}


def _csv_guard(path: Path, task: dict, output_bytes: int) -> None:
    """Bound shape/field work before pandas allocates a host-side frame."""
    require(0 < path.stat().st_size <= output_bytes, "Generated CSV is empty or exceeds output limit")
    expected = [column["name"] for column in task["columns"]]
    maximum = 1_000_000
    old_limit = csv.field_size_limit(maximum)
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            def lines():
                while line := stream.readline(maximum + 1):
                    require(len(line) <= maximum, "CSV physical line exceeds safety limit")
                    yield line
            reader = csv.reader(lines(), strict=True)
            require(next(reader, None) == expected, "CSV header/order differs from trusted task")
            rows = 0
            for row in reader:
                rows += 1
                require(rows <= task["n_rows"], "CSV has more rows than trusted task")
                require(len(row) == len(expected), "CSV row has wrong field count")
            require(rows == task["n_rows"], "CSV has fewer rows than trusted task")
    except (csv.Error, UnicodeError) as error:
        raise ContractError("Invalid bounded CSV output") from error
    finally:
        csv.field_size_limit(old_limit)


def run_candidate(bundle: str | Path, candidate: str | Path, run_id: str, seed: int,
                  *, runtime: dict | None = None, timeout_seconds: int = 30,
                  memory_mb: int = 1024, output_bytes: int = 20_000_000,
                  log_bytes: int = 100_000) -> dict:
    """Run a frozen candidate; preserve failure receipts instead of overwriting it.

    Invalid initial contracts raise. A launched or attempted run returns a receipt
    with status success, failed or timeout. Caller must inspect status.
    """
    limits = _limits(timeout_seconds, memory_mb, output_bytes, log_bytes, seed)
    root = _bundle(bundle)
    directory, relative = _candidate(root, candidate)
    frozen = verify_candidate(root, directory)
    frozen_hash = sha256(directory / "freeze.json")
    task = read_json(root / "task.json")
    observed = None if task["mode"] == "whole_cohort" else read_table(root / "observed.csv", task)
    run_id = _name(run_id)
    runs = _path(root, "executions", file=False)
    runs.mkdir(exist_ok=True)
    run = _path(root, "executions/" + run_id, file=False)
    require(not run.exists(), "Run already exists; choose a new ID")
    run.mkdir()
    stage, output = run / "input", run / "output"
    stage.mkdir()
    output.mkdir()
    route = frozen["route"]
    request = {"schema_version": 1, **limits, "task_id": task["task_id"]}
    receipt = {
        "schema_version": 1, "kind": "generator_execution", "run_id": run_id,
        "candidate": relative, "candidate_freeze_sha256": frozen_hash,
        "created_utc": datetime.now(timezone.utc).isoformat(), "route": route,
        "status": "failed", "generator_executed": False, "limits": limits,
        "isolation_scope": "generator_process_only" if route == "generator.py" else "no_code_execution",
        "agent_isolation": "not_provided", "scientific_validity": "not_assessed",
        "error": None, "process": None, "runtime": None, "files": {},
    }
    started = time.monotonic()
    try:
        copies = {"task.json": root / "task.json", "model_spec.json": directory / "model_spec.json",
                  route: directory / route}
        if observed is not None:
            copies["observed.csv"] = root / "observed.csv"
        for name, source in copies.items():
            stage.joinpath(name).write_bytes(source.read_bytes())
        _write(stage / "request.json", request)
        staged_bindings = {name: sha256(path) for name, path in copies.items()}
        for name, expected in staged_bindings.items():
            require(sha256(stage / name) == expected, "Input changed during staging")
        _write(run / "input_bindings.json", {
            "candidate_freeze_sha256": frozen_hash, "files": staged_bindings})
        if route == "generator.py":
            runtime = _runtime(runtime)
            receipt["runtime"] = runtime
            worker = Path(__file__).with_name("_worker.py")
            stage.joinpath("worker.py").write_bytes(worker.read_bytes())
            _write(run / "runtime_manifest.json", _runtime_manifest(runtime))
            for name in ("generated.csv", "worker_report.json"):
                output.joinpath(name).touch(exist_ok=False)
            command = _command(runtime, run, timeout_seconds)
            _write(run / "launch.json", {"argv": command, "runtime": runtime,
                                       "worker_sha256": sha256(stage / "worker.py"),
                                       "isolation": "curated_bubblewrap_mounts_no_network",
                                       "authentication": "not_a_signature"})
            verify_candidate(root, directory)
            require(sha256(directory / "freeze.json") == frozen_hash, "Candidate changed before launch")
            receipt["generator_executed"] = None
            process = _capture(command, run, timeout_seconds + 20, log_bytes,
                               run / "stdout.log", run / "stderr.log")
            receipt["process"] = process
            # True means the wrapper reached module execution, not that it succeeded.
            report_size = output.joinpath("worker_report.json").stat().st_size
            require(report_size <= 65_536, "Worker report exceeds 64 KiB safety limit")
            report = read_json(output / "worker_report.json") if report_size else {}
            require(isinstance(report, dict), "Worker report must be an object")
            if report:
                require(report.get("status") in {"started", "executing", "completed", "failed"} and
                        type(report.get("generator_started")) is bool,
                        "Invalid worker report state")
            receipt["generator_executed"] = report.get("generator_started") if report else None
            if process["host_timeout"] or process["returncode"] in {124, 137, -9}:
                receipt["status"] = "timeout"
                raise ContractError("Generator time/resource termination; inspect bounded logs")
            require(process["returncode"] == 0, "Isolated worker failed; inspect bounded logs")
            require(report.get("status") == "completed", "Worker did not report completion")
            require(report.get("generator_started") is True, "Completed worker must report generator entry")
        else:
            receipt["runtime"] = {"backend": "direct_rows_validation"}
            output.joinpath("generated.csv").write_bytes(stage.joinpath("generated.csv").read_bytes())
            require(output.joinpath("generated.csv").stat().st_size <= output_bytes, "Direct table exceeds output limit")
        generated_path = _path(output, "generated.csv")
        _csv_guard(generated_path, task, output_bytes)
        generated = read_table(generated_path, task, output=True)
        validate_output(observed, generated, task)
        # Verify exact candidate, source, observed and registry commitments again.
        verify_candidate(root, directory)
        require(sha256(directory / "freeze.json") == frozen_hash, "Candidate receipt changed during execution")
        for name, expected in staged_bindings.items():
            require(sha256(_path(stage, name)) == expected, "Read-only staged input changed")
        receipt["status"] = "success"
    except (OSError, ValueError, TypeError, KeyError, RecursionError, subprocess.SubprocessError) as error:
        receipt["error"] = {"type": type(error).__name__, "message": str(error)[:2000]}
    receipt["elapsed_seconds"] = round(time.monotonic() - started, 6)
    # _files refuses symlinks/junctions. Unexpected output entries also fail closed.
    try:
        require(set(_files(output)) <= {"generated.csv", "worker_report.json"}, "Unexpected output artifact")
        files = _files(run)
        receipt["files"] = {name: sha256(_path(run, name)) for name in files}
    except (OSError, ValueError) as error:
        receipt["status"] = "failed"
        receipt["error"] = {"type": type(error).__name__, "message": str(error)[:2000]}
        receipt["files"] = {}
    _write(run / "execution.json", receipt)
    return receipt


def verify_execution(bundle: str | Path, run_id: str) -> dict:
    """Verify recorded bytes and successful-output preservation, without executing."""
    root = _bundle(bundle)
    run = _path(root, "executions/" + _name(run_id), file=False)
    receipt = read_json(_path(run, "execution.json"))
    require(isinstance(receipt, dict), "Execution receipt must be an object")
    require(receipt.get("schema_version") == 1 and receipt.get("kind") == "generator_execution" and
            receipt.get("run_id") == run_id, "Invalid execution receipt")
    require(receipt.get("status") in {"success", "failed", "timeout"}, "Invalid execution status")
    require(receipt.get("agent_isolation") == "not_provided" and
            receipt.get("scientific_validity") == "not_assessed", "Receipt overstates its scope")
    expected_scope = "generator_process_only" if receipt.get("route") == "generator.py" else "no_code_execution"
    require(receipt.get("isolation_scope") == expected_scope, "Execution scope mismatch")
    limits = receipt.get("limits")
    require(isinstance(limits, dict) and set(limits) == {"seed", "timeout_seconds", "memory_mb", "output_bytes", "log_bytes"},
            "Invalid execution limits")
    _limits(**limits)
    files = receipt.get("files")
    require(isinstance(files, dict) and bool(files), "No verifiable run artifacts")
    actual = sorted(name for name in _files(run) if name != "execution.json")
    require(actual == sorted(files), "Run artifact set changed")
    for name, expected in files.items():
        require(sha256(_path(run, name)) == expected, "Run artifact hash changed")
    directory, _ = _candidate(root, receipt["candidate"])
    frozen = verify_candidate(root, directory)
    require(sha256(directory / "freeze.json") == receipt["candidate_freeze_sha256"],
            "Frozen candidate receipt changed")
    require(frozen["route"] == receipt["route"], "Execution route mismatch")
    bindings = read_json(_path(run, "input_bindings.json"))
    require(isinstance(bindings, dict) and isinstance(bindings.get("files"), dict), "Invalid input bindings")
    require(bindings["candidate_freeze_sha256"] == receipt["candidate_freeze_sha256"],
            "Input binding receipt mismatch")
    request = read_json(_path(run, "input/request.json"))
    require(isinstance(request, dict), "Staged request must be an object")
    require({name: request.get(name) for name in limits} == limits, "Execution limits/seed differ from staged request")
    for name, expected in bindings["files"].items():
        source = root / name if name in {"task.json", "observed.csv"} else directory / name
        require(sha256(_path(run / "input", name)) == expected == sha256(source), "Staged input binding changed")
    if receipt["status"] == "success":
        if receipt["route"] == "generator.py":
            require(receipt.get("generator_executed") is True and receipt.get("runtime") == DEFAULT_RUNTIME,
                    "Successful program receipt lacks its execution identity")
            launch = read_json(_path(run, "launch.json"))
            require(launch.get("worker_sha256") == sha256(_path(run, "input/worker.py")), "Worker binding changed")
        else:
            require(receipt.get("generator_executed") is False, "Direct route cannot claim code execution")
        task = read_json(root / "task.json")
        observed = None if task["mode"] == "whole_cohort" else read_table(root / "observed.csv", task)
        generated_path = _path(run, "output/generated.csv")
        _csv_guard(generated_path, task, limits["output_bytes"])
        validate_output(observed, read_table(generated_path, task, output=True), task)
    return receipt

