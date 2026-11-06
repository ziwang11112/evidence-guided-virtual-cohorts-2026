"""Run the iron pilot's compact author ABI in the existing WSL/Bubblewrap worker."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness import execution, lifecycle, semantic_feedback_v1 as semantic
from cohort_harness.source_checks import apply_operator
from cohort_harness.contracts import require

COLUMNS = ["hb_g_dl", "ferritin_ug_l"]
SIZES = {"source": 100000, "target": 5000}
SEEDS = {"source": [4101], "target": [5101, 5102, 5103]}
CONTEXTS = {"source": "zhu_source", "target": "target"}
LIMITS = {"timeout_seconds": 45, "memory_mb": 1536, "output_bytes": 16000000, "log_bytes": 50000}
WORKER = Path(execution.__file__).with_name("_worker.py")
BRIDGE = """# Trusted adapter loaded inside /input by the existing worker.
import importlib.util
import numpy as np


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Expected a whole-cohort request")
    spec = importlib.util.spec_from_file_location("iron_author", "/input/author.py")
    author = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(author)
    return author.generate(specification["n"], np.random.default_rng(seed), specification["context"])
"""


def _validate(frame):
    require(list(frame.columns) == COLUMNS, "Iron column names or order differ from contract")
    require(all(pd.api.types.is_numeric_dtype(frame[c]) and not pd.api.types.is_bool_dtype(frame[c]) for c in COLUMNS),
            "Expected two numeric columns")
    matrix = frame.to_numpy(dtype=float)
    require(np.isfinite(matrix).all() and (matrix > 0).all(), "Expected finite positive measurements")


def _checked_operator(frame, operator, units):
    columns = {key: {"kind": "number", "unit": unit} for key, unit in units.items()}
    semantic._signature(operator)
    semantic._task_operator(operator, columns)
    semantic._measurement({"transform": "identity", "source_variable_units": units}, operator, columns)
    return apply_operator(frame, operator)


def zhu_statistics(frame):
    """Apply the raw-ferritin Zhu operators to the simulated source population."""
    _validate(frame)
    hb, ferritin = (frame[c].to_numpy(dtype=float) for c in COLUMNS)
    hb_low = hb < 12
    low = ferritin < 15
    cells = [int(np.count_nonzero(x)) for x in (hb_low & low, hb_low & ~low, ~hb_low & low, ~hb_low & ~low)]
    a, b, c, d = cells
    groups = {}
    transformed = frame.assign(log_ferritin=np.log(ferritin))
    for name, conditions in (("hb_lt10", [("lt", 10)]), ("hb_10_to_lt12", [("ge", 10), ("lt", 12)]),
                             ("hb_ge12", [("ge", 12)])):
        selected = [{"column": "hb_g_dl", "op": cmp, "value": cut} for cmp, cut in conditions]
        predicate = np.ones(len(hb), dtype=bool)
        for cmp, cut in conditions:
            predicate &= (hb < cut if cmp == "lt" else hb >= cut)
        n = int(predicate.sum())
        geom, frac = None, None
        if n:
            base = {"selection": selected, "missing_policy": "error"}
            avg = _checked_operator(transformed, {**base, "kind": "mean", "column": "log_ferritin",
                                    "unit": "ln(ug/L relative to 1 ug/L)"},
                                    {"hb_g_dl": "g/dL", "log_ferritin": "ln(ug/L relative to 1 ug/L)"})
            freq = _checked_operator(frame, {**base, "kind": "proportion", "unit": "1",
                        "event": {"column": "ferritin_ug_l", "op": "lt", "value": 15}},
                        {"hb_g_dl": "g/dL", "ferritin_ug_l": "ug/L"})
            require(avg["n_used"] == freq["n_used"] == n, "Group denominator mismatch")
            geom, frac = float(np.exp(avg["value"])), freq["value"]
        groups[name] = {"n": n, "fraction": n / len(hb), "ferritin_geomean_ug_l": geom,
                        "ferritin_lt15_fraction": frac}
    return {"scope": "simulated Zhu source population", "rows": len(hb),
            "cell_order": ["both_low", "hb_low_only", "ferritin_low_only", "neither_low"],
            "cells_n": cells, "cells_fraction": [v / len(hb) for v in cells],
            "crude_or": a * d / (b * c) if all(cells) else None,
            "table_iii_hb_bands_g_dl": groups}


def _json_write(path, obj):
    execution._write(path, obj)


def _time():
    return datetime.now(timezone.utc).isoformat()


def run_one(generator, expected_hash, run, n, seed, context):
    """One exclusive attempt. Only the staged scientific module enters the sandbox."""
    generator = Path(generator).resolve(strict=True)
    require(re.fullmatch(r"[0-9a-f]{64}", expected_hash) is not None, "Expected SHA-256")
    require(lifecycle.sha256(generator) == expected_hash, "Authored code differs from approved hash")
    lifecycle.validate_program(generator)
    limits = execution._limits(**LIMITS, seed=seed)
    task = {"mode": "whole_cohort", "n_rows": n, "columns": [{"name": c, "kind": "number"} for c in COLUMNS]}
    run.mkdir(parents=True, exist_ok=False)
    stage, output = run / "input", run / "output"
    stage.mkdir()
    output.mkdir()
    receipt = {"kind": "iron_generation_v1", "status": "failed", "agent_code_sha256": expected_hash,
               "adapter_sha256": lifecycle.sha256(Path(__file__)), "started_utc": _time(), "context": context,
               "rows": n, "limits": limits, "reference_read": False}
    try:
        (stage / "author.py").write_bytes(generator.read_bytes())
        require(lifecycle.sha256(stage / "author.py") == expected_hash, "Staged author bytes differ")
        (stage / "worker.py").write_bytes(WORKER.read_bytes())
        (stage / "generator.py").write_text(BRIDGE, encoding="utf8", newline="\n")
        _json_write(stage / "task.json", task)
        _json_write(stage / "model_spec.json", {"n": n, "context": context})
        _json_write(stage / "request.json", limits)
        bindings = {path.name: lifecycle.sha256(path) for path in sorted(stage.iterdir())}
        _json_write(run / "input_bindings.json", bindings)
        runtime = execution._runtime(None)
        _json_write(run / "runtime_manifest.json", execution._runtime_manifest(runtime))
        for name in ["generated.csv", "worker_report.json"]:
            (output / name).touch(exist_ok=False)
        command = execution._command(runtime, run, LIMITS["timeout_seconds"])
        _json_write(run / "launch.json", {"command": command, "network": "unshared", "inputs": "read-only stage"})
        receipt["process"] = execution._capture(command, run, LIMITS["timeout_seconds"] + 20, LIMITS["log_bytes"],
                                                run / "stdout.log", run / "stderr.log")
        require(receipt["process"]["returncode"] == 0 and not receipt["process"]["host_timeout"], "Worker failed or timed out")
        require((output / "worker_report.json").stat().st_size <= 65536, "Oversize worker report")
        report = lifecycle.read_json(output / "worker_report.json")
        require(report.get("status") == "completed" and report.get("generator_started") is True, "No completed generator")
        execution._csv_guard(output / "generated.csv", task, LIMITS["output_bytes"])
        frame = pd.read_csv(output / "generated.csv", float_precision="round_trip")
        _validate(frame)
        for name, binding in bindings.items():
            require(lifecycle.sha256(stage / name) == binding, "Staged input changed")
        require(lifecycle.sha256(generator) == expected_hash, "Reviewed code changed during run")
        receipt["generated_sha256"] = lifecycle.sha256(output / "generated.csv")
        if context == "zhu_source":
            _json_write(run / "source_diagnostics.json", zhu_statistics(frame))
        receipt["status"] = "success"
    except Exception as error:
        receipt["error"] = {"type": type(error).__name__, "message": str(error)[:1500]}
    finally:
        receipt["completed_utc"] = _time()
        receipt["files"] = {file.relative_to(run).as_posix(): lifecycle.sha256(file) for file in sorted(run.rglob("*")) if file.is_file()}
        _json_write(run / "execution.json", receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generator", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--author", choices=["A", "B"], required=True)
    parser.add_argument("--stage", choices=["initial", "final"], required=True)
    parser.add_argument("--mode", choices=list(SEEDS), required=True)
    args = parser.parse_args()
    require(args.mode != "target" or args.stage == "final", "Only a selected final law may generate the target")
    results = []
    for seed in SEEDS[args.mode]:
        directory = ROOT / "private_runs" / args.author / args.stage / (args.mode + "_" + str(seed))
        receipt = run_one(args.generator, args.sha256, directory, SIZES[args.mode], seed, CONTEXTS[args.mode])
        results.append({k: receipt.get(k) for k in ("status", "rows", "context", "generated_sha256", "error")})
    print(json.dumps(results, indent=2, allow_nan=False))
    return int(any(result["status"] != "success" for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
