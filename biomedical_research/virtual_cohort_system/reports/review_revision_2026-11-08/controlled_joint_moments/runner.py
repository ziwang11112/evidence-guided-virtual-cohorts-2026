"""Bounded controlled joint-moment generation; never reads custodian truth.

Author ABI: generate(n, rng, spec) -> DataFrame[Z, X1, X2, Y].
Only the reviewed program and its specification enter the WSL sandbox. All
attempts, including failures, consume their single predeclared author/seed slot.
This local adapter leaves historical controllers and receipts unchanged.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
sys.path.insert(0, str(PROJECT))
from cohort_harness import (contracts, execution, lifecycle, semantic_feedback_v1 as semantic,
                            source_checks, source_replay, whole_cohort_feedback)
from cohort_harness.contracts import require

COLUMNS = ["Z", "X1", "X2", "Y"]
AUTHORS = ["O1", "O2", "C1", "C2"]
SEEDS = [8101, 8102, 8103]
N_ROWS = 10000
MAX_TABLES = 12
LIMITS = {"timeout_seconds": 45, "memory_mb": 1536,
          "output_bytes": 16000000, "log_bytes": 50000}
WORKER = Path(execution.__file__).with_name("_worker.py")
BRIDGE = '''# Trusted adapter; executed only inside the isolated worker.
import importlib.util
import numpy as np

def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Expected no observed individual data")
    loader = importlib.util.spec_from_file_location("controlled_author", "/input/author.py")
    author = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(author)
    return author.generate(specification["n"], np.random.default_rng(seed), specification["author_spec"])
'''


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return lifecycle.read_json(path)


def sha(path):
    return lifecycle.sha256(path)


def engine_hashes():
    modules = (contracts, execution, lifecycle, semantic, source_checks,
               source_replay, whole_cohort_feedback)
    return {**{m.__name__: sha(m.__file__) for m in modules}, "worker": sha(WORKER)}


def safe_file(relative):
    parts = lifecycle.safe_relative(relative)
    path = ROOT.joinpath(*parts)
    require(not any(lifecycle._link(x) for x in [path, *path.parents]), "Linked path rejected")
    require(path.resolve().is_relative_to(ROOT), "Path escapes experiment")
    require(path.is_file(), "Missing required file: " + relative)
    return path


def validate_operator(operator, units):
    columns = {name: {"kind": "number", "unit": "1"} for name in COLUMNS}
    semantic._signature(operator)
    semantic._task_operator(operator, columns)
    used = semantic._variables(operator)
    require(used <= set(COLUMNS), "Source check uses unapproved variables")
    require(operator["selection"] == [] and operator["missing_policy"] == "error",
            "Controlled source checks require whole-population, no-missingness operators")
    semantic._measurement({"transform": "identity",
                           "source_variable_units": {name: units[name] for name in used}},
                          operator, columns)


def source_contract(protocol):
    source = read(safe_file(protocol["source_file"]))
    require(source.get("schema_version") == 1, "Unknown source schema")
    require(source.get("population") == protocol["population"], "Source population differs")
    require(source.get("units") == {name: "1" for name in COLUMNS}, "Expected standardized units")
    require(isinstance(source.get("checks"), list) and len(source["checks"]) == 15, "Expected fifteen source checks")
    ids = set()
    for check in source["checks"]:
        execution._name(check["id"])
        require(check["id"] not in ids, "Duplicate source check")
        ids.add(check["id"])
        require(source_checks.finite(check["estimate"]), "Nonfinite source estimate")
        validate_operator(check["operator"], source["units"])
        if "evidence_item" in check:
            semantic._bind_evidence(check["evidence_item"], check["operator"])
            require(check["evidence_item"]["estimate"] == check["estimate"], "Source/evidence estimate differs")
    return source


def required_batch_files():
    return {"PROTOCOL.json", "SOURCE.json", "runner.py", "evaluate.py", "DESIGN_LOCK.json",
            "DESIGN_REVIEW.json", "EVALUATION_SPEC.json"} | {
                f"bundles/{author}/{name}" for author in AUTHORS
                for name in ("generator.py", "model_spec.json", "decision.json", "REQUEST.txt", "SOURCE.json")}


def verify_design():
    """Verify public fixtures and truth commitment without reading truth contents."""
    design = read(safe_file("DESIGN_LOCK.json"))
    review = read(safe_file("DESIGN_REVIEW.json"))
    require(design.get("author_outputs_present") is False, "Design was not sealed before construction")
    require(review.get("decision") == "PASS_TO_AUTHOR_DISPATCH" and not review.get("blocking_findings"),
            "Independent design review not passed")
    require(review.get("bound_inputs") == design.get("records"), "Design review covers different fixtures")
    required = {"prepare.py", "SOURCE.json", "PROTOCOL.json", "custodian/TRUTH.json"} | {
        f"bundles/{author}/{name}" for author in AUTHORS for name in ("REQUEST.txt", "SOURCE.json")}
    require(set(design.get("records", {})) == required, "Design fixture set differs")
    for relative, expected in design["records"].items():
        require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected), "Invalid design commitment")
        if relative != "custodian/TRUTH.json":
            require(sha(safe_file(relative)) == expected, "Design fixture changed: " + relative)
    require(all(design["records"][f"bundles/{author}/SOURCE.json"] == design["records"]["SOURCE.json"]
                for author in AUTHORS), "Authors received different source evidence")
    return design


def verify_batch():
    """Check the entire batch, not merely the selected author; no truth access."""
    protocol = read(safe_file("PROTOCOL.json"))
    expected = {"schema_version": 1, "columns": COLUMNS, "authors": AUTHORS, "seeds": SEEDS,
                "n_rows": N_ROWS, "max_final_tables": MAX_TABLES, "source_file": "SOURCE.json",
                "limits": LIMITS}
    for key, value in expected.items():
        require(protocol.get(key) == value, "Fixed protocol differs: " + key)
    require(isinstance(protocol.get("population"), str) and protocol["population"].strip(), "Population required")
    require(protocol.get("revision_rounds") == protocol.get("sampling_trials_before_seal") == 0,
            "This batch permits neither feedback revisions nor trial sampling")
    design = verify_design()
    lock = read(safe_file("BATCH_LOCK.json"))
    required = required_batch_files()
    require(set(lock.get("records", {})) == required, "Batch lock must bind exactly approved inputs and implementations")
    for name, expected_hash in lock["records"].items():
        require(isinstance(expected_hash, str) and re.fullmatch(r"[0-9a-f]{64}", expected_hash), "Invalid file hash")
        require(sha(safe_file(name)) == expected_hash, "Frozen file changed: " + name)
    require(lock.get("engine_sha256") == engine_hashes(), "Execution or semantic engine changed")
    require(isinstance(lock.get("truth_sha256"), str) and
            re.fullmatch(r"[0-9a-f]{64}", lock["truth_sha256"]), "Custodian truth commitment required")
    require(lock["truth_sha256"] == design["records"]["custodian/TRUTH.json"], "Truth commitment differs from initial design")
    for author in AUTHORS:
        lifecycle.validate_program(safe_file(f"bundles/{author}/generator.py"))
        read(safe_file(f"bundles/{author}/model_spec.json"))
    source = source_contract(protocol)
    return protocol, lock, source


def task_contract():
    return {"mode": "whole_cohort", "n_rows": N_ROWS,
            "columns": [{"name": name, "kind": "number"} for name in COLUMNS]}


def validate_table(frame):
    require(list(frame.columns) == COLUMNS and len(frame) == N_ROWS, "Unexpected table schema or row count")
    require(all(pd.api.types.is_numeric_dtype(frame[c]) and not pd.api.types.is_bool_dtype(frame[c]) for c in COLUMNS),
            "All measurements must be numeric, not Boolean")
    require(np.isfinite(frame.to_numpy(dtype=float)).all(), "Nonfinite measurement")


def source_diagnostics(frame, source):
    records = []
    for check in source["checks"]:
        validate_operator(check["operator"], source["units"])
        row = {"id": check["id"], "operator": check["operator"], "reported_value": check["estimate"],
               "status": "not_computable", "calculation": None, "difference": None}
        try:
            row["calculation"] = source_checks.apply_operator(frame, check["operator"])
            row["difference"] = row["calculation"]["value"] - check["estimate"]
            require(source_checks.finite(row["difference"]), "Nonfinite diagnostic difference")
            row["status"] = "computed"
        except source_checks.NotComputable as error:
            row["reason"] = str(error)
        records.append(row)
    return {"scope": "controlled_same_population_source_diagnostics_only",
            "population": source["population"], "source_semantic_signature_and_units_checked": True,
            "published_clinical_proof": False, "checks": records}


def inventory():
    base = ROOT / "private_runs"
    if not base.exists():
        return {}
    require(not lifecycle._link(base), "Linked attempt root")
    found = {}
    for author_dir in base.iterdir():
        require(author_dir.is_dir() and author_dir.name in AUTHORS and not lifecycle._link(author_dir), "Unknown attempt author")
        for run in author_dir.iterdir():
            require(run.is_dir() and not lifecycle._link(run), "Unexpected attempt artifact")
            require(run.name in {f"seed_{s}" for s in SEEDS}, "Unbudgeted seed or retry")
            found[(author_dir.name, int(run.name[5:]))] = run
    require(len(found) <= MAX_TABLES, "Attempt budget exceeded")
    return found


def run_one(author, seed):
    protocol, lock, source = verify_batch()
    require(author in AUTHORS and seed in SEEDS, "Unscheduled author/seed")
    attempts = inventory()
    require((author, seed) not in attempts and len(attempts) < MAX_TABLES, "Attempt already consumed or budget exhausted")
    code = safe_file(f"bundles/{author}/generator.py")
    spec_path = safe_file(f"bundles/{author}/model_spec.json")
    run = ROOT / "private_runs" / author / f"seed_{seed}"
    run.mkdir(parents=True, exist_ok=False)
    receipt = {"kind": "controlled_joint_moments_execution_v1", "status": "failed", "author": author,
               "seed": seed, "n_rows": N_ROWS, "started_utc": now(), "reference_read": False,
               "batch_lock_sha256": sha(ROOT / "BATCH_LOCK.json"),
               "code_sha256": sha(code), "spec_sha256": sha(spec_path), "engine_sha256": engine_hashes(),
               "protocol_sha256": sha(ROOT / "PROTOCOL.json"), "source_sha256": sha(ROOT / "SOURCE.json")}
    stage, output = run / "input", run / "output"
    execution._write(run / "ATTEMPT.json", {k: receipt[k] for k in
                     ("kind", "author", "seed", "n_rows", "started_utc", "batch_lock_sha256", "code_sha256", "spec_sha256")})
    try:
        stage.mkdir(); output.mkdir()
        (stage / "author.py").write_bytes(code.read_bytes())
        (stage / "worker.py").write_bytes(WORKER.read_bytes())
        (stage / "generator.py").write_text(BRIDGE, encoding="utf8", newline="\n")
        execution._write(stage / "task.json", task_contract())
        execution._write(stage / "model_spec.json", {"n": N_ROWS, "author_spec": read(spec_path)})
        execution._write(stage / "request.json", execution._limits(**LIMITS, seed=seed))
        bindings = {p.name: sha(p) for p in sorted(stage.iterdir())}
        require(bindings["author.py"] == receipt["code_sha256"], "Staged scientific code changed")
        execution._write(run / "input_bindings.json", bindings)
        runtime = execution._runtime(None)
        execution._write(run / "runtime_manifest.json", execution._runtime_manifest(runtime))
        for name in ("generated.csv", "worker_report.json"):
            (output / name).touch(exist_ok=False)
        command = execution._command(runtime, run, LIMITS["timeout_seconds"])
        execution._write(run / "launch.json", {"command": command, "network": "unshared", "input": "read_only",
                                               "truth_staged": False})
        receipt["process"] = execution._capture(command, run, LIMITS["timeout_seconds"] + 20, LIMITS["log_bytes"],
                                                 run / "stdout.log", run / "stderr.log")
        require(receipt["process"]["returncode"] == 0 and not receipt["process"]["host_timeout"], "Worker failed or timed out")
        require((output / "worker_report.json").stat().st_size <= 65536, "Oversized worker report")
        worker = read(output / "worker_report.json")
        require(worker.get("status") == "completed" and worker.get("generator_started") is True, "No completed generator")
        execution._csv_guard(output / "generated.csv", task_contract(), LIMITS["output_bytes"])
        frame = pd.read_csv(output / "generated.csv", float_precision="round_trip")
        validate_table(frame)
        execution._write(run / "source_diagnostics.json", source_diagnostics(frame, source))
        require(all(sha(stage / name) == value for name, value in bindings.items()), "Staged input changed")
        verify_batch()
        receipt.update(status="success", generated_sha256=sha(output / "generated.csv"))
    except Exception as error:
        receipt["error"] = {"type": type(error).__name__, "message": str(error)[:1500]}
    finally:
        receipt["completed_utc"] = now()
        receipt["files"] = {p.relative_to(run).as_posix(): sha(p) for p in sorted(run.rglob("*")) if p.is_file()}
        execution._write(run / "execution.json", receipt)
    return receipt


def verify_execution(author, seed):
    protocol, lock, source = verify_batch()
    run = inventory().get((author, seed))
    require(run is not None, "Unattempted slot")
    receipt = read(run / "execution.json")
    require(receipt["kind"] == "controlled_joint_moments_execution_v1" and
            (receipt["author"], receipt["seed"], receipt["n_rows"]) == (author, seed, N_ROWS), "Execution identity differs")
    require(receipt["status"] in {"success", "failed"}, "Unknown execution status")
    require(receipt["batch_lock_sha256"] == sha(ROOT / "BATCH_LOCK.json") and
            receipt["engine_sha256"] == engine_hashes(), "Execution commitment changed")
    for key, relative in (("code_sha256", f"bundles/{author}/generator.py"),
                          ("spec_sha256", f"bundles/{author}/model_spec.json"),
                          ("protocol_sha256", "PROTOCOL.json"), ("source_sha256", "SOURCE.json")):
        require(receipt[key] == sha(safe_file(relative)), "Execution input differs: " + key)
    require(not any(lifecycle._link(p) for p in run.rglob("*")), "Linked attempt artifact")
    actual = {p.relative_to(run).as_posix() for p in run.rglob("*") if p.is_file() and p != run / "execution.json"}
    require(actual == set(receipt["files"]), "Attempt file inventory changed")
    for name, expected in receipt["files"].items():
        require(sha(run / name) == expected, "Attempt artifact changed: " + name)
    if receipt["status"] == "success":
        require(receipt["generated_sha256"] == sha(run / "output/generated.csv"), "Generated table hash changed")
        request = read(run / "input/request.json")
        require(request == execution._limits(**LIMITS, seed=seed), "Wrong execution seed or limits")
        require(read(run / "input/model_spec.json") == {"n": N_ROWS, "author_spec": read(safe_file(f"bundles/{author}/model_spec.json"))},
                "Staged specification differs from sealed author specification")
        require(sha(run / "input/author.py") == receipt["code_sha256"], "Wrong staged scientific code")
        require(sha(run / "input/worker.py") == sha(WORKER), "Wrong staged worker")
        require((run / "input/generator.py").read_text(encoding="utf8") == BRIDGE, "Wrong staged ABI bridge")
        require(read(run / "input/task.json") == task_contract(), "Wrong staged task")
        bindings = read(run / "input_bindings.json")
        require(set(bindings) == {p.name for p in (run / "input").iterdir()}, "Input binding inventory differs")
        require(all(sha(run / "input" / name) == expected for name, expected in bindings.items()), "Input binding mismatch")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--author", choices=AUTHORS, required=True)
    parser.add_argument("--seed", type=int, choices=SEEDS)
    args = parser.parse_args()
    verify_batch()
    selected = [args.seed] if args.seed is not None else SEEDS
    require(not any((args.author, seed) in inventory() for seed in selected),
            "Selected slot already exists; choose only an unattempted scheduled seed")
    busy = ROOT / "RUNNING.lock"
    with busy.open("x", encoding="utf8") as stream:
        stream.write(json.dumps({"author": args.author, "seeds": selected, "started_utc": now()}))
    results = []
    try:
        for seed in selected:
            results.append(run_one(args.author, seed))
    finally:
        busy.unlink()
    print(json.dumps([{k: r.get(k) for k in ("author", "seed", "status", "error", "generated_sha256")} for r in results], indent=2))
    return int(any(r["status"] != "success" for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
