"""Case-local, one-attempt evaluation of a root-approved complete frozen schedule.

Import and --help perform no case, reference, candidate, or runtime operations.
No generation, scientific revision, source feedback, or execution API is called.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

SEEDS = (18203, 18211, 18223)
BINDINGS = {
    "protocol": "PROTOCOL_v2.md", "task": "public_v2/task.json",
    "source_panel": "public_v2/SOURCE_PANEL_SPEC.json",
    "analysis_engine": "analysis/analytical_engine.py",
    "evaluation_controller": "analysis/run_evaluation.py",
    "preparation_receipt": "custodian/PREPARATION_RECEIPT_v2.json",
    "preparation_release": "PREPARATION_RELEASE_v2.json",
    "preparation_script": "custodian/prepare_reference_v2.py",
}
REFERENCE = "custodian/private/reference_v2.csv"
SUCCESS_FILES = {
    "input/task.json", "input/model_spec.json", "input/generator.py", "input/request.json", "input/worker.py",
    "output/generated.csv", "output/worker_report.json", "input_bindings.json", "runtime_manifest.json",
    "launch.json", "stdout.log", "stderr.log",
}


class EvaluationError(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise EvaluationError(code)


def safe_path(root, relative):
    require(isinstance(relative, str) and bool(relative), "invalid_path")
    require(not re.search(r'[\\:\x00<>"|?*]', relative), "unsafe_path")
    parts = relative.split("/")
    devices = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)),
               *(f"lpt{i}" for i in range(1, 10))}
    require(all(p not in {"", ".", ".."} and not p.endswith((".", " ")) and
                p.split(".")[0].lower() not in devices and all(ord(c) >= 32 for c in p)
                for p in parts), "unsafe_path_segment")
    path = root
    for part in parts:
        path = path / part
        require(not path.is_symlink() and not path.is_junction(), "linked_path_rejected")
    require(path.resolve().is_relative_to(root.resolve()), "path_escape")
    return path


def digest(body):
    return hashlib.sha256(body).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def bound_bytes(root, binding, ledger, *, expected_path=None, namespace="case"):
    require(isinstance(binding, dict) and set(binding) == {"path", "sha256"}, "invalid_binding")
    require(re.fullmatch(r"[0-9a-f]{64}", str(binding["sha256"])), "invalid_sha256")
    require(expected_path is None or binding["path"] == expected_path, "binding_path_mismatch")
    body = safe_path(root, binding["path"]).read_bytes()
    require(digest(body) == binding["sha256"], "binding_hash_mismatch")
    ledger[namespace + ":" + binding["path"]] = binding["sha256"]
    return body


def validate_schedule(release):
    require(release.get("schema") == "ensanut_evaluation_release_v1", "release_schema")
    require(release.get("issuer") == "root" and release.get("status") == "approved" and
            release.get("effects_authorized") is True, "effects_not_authorized")
    require(release.get("purpose") == "fixed_target_evaluation_once" and
            isinstance(release.get("release_id"), str) and release["release_id"].strip(), "release_purpose")
    builders, schedule = release.get("builders"), release.get("schedule")
    require(isinstance(builders, list) and 1 <= len(builders) <= 2, "builder_budget")
    require(isinstance(schedule, list), "schedule_missing")
    ids = [b.get("id") for b in builders]
    require(all(isinstance(x, str) and re.fullmatch(r"[A-Za-z0-9_-]+", x) for x in ids) and
            len(ids) == len(set(ids)), "builder_identity")
    require(len({b.get("bundle") for b in builders}) == len(builders), "shared_builder_bundle")
    expected = {(builder, stage, seed) for builder in ids for stage in ("initial", "final") for seed in SEEDS}
    actual = [(s.get("builder"), s.get("stage"), s.get("seed")) for s in schedule]
    require(len(actual) == len(expected) and set(actual) == expected, "incomplete_or_duplicate_schedule")
    for slot in schedule:
        require(type(slot["seed"]) is int, "seed_type")
        require(slot.get("status") in {"success", "failed", "timeout"}, "execution_status")
        require(isinstance(slot.get("run_id"), str) and
                re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", slot["run_id"]), "run_id")
        if slot["status"] == "success":
            require(re.fullmatch(r"[0-9a-f]{64}", str(slot.get("output_sha256"))), "output_hash_required")
        else:
            require(slot.get("output_sha256") is None, "failed_output_must_not_be_released")
    return builders, schedule


def retained_identity(initial, final):
    require(final.get("revision", {}).get("kind") == "retain", "retention_not_declared")
    for name in ("generator.py", "model_spec.json", "evidence.json"):
        require(initial["commitments"][initial["candidate"] + "/" + name] ==
                final["commitments"][final["candidate"] + "/" + name], "retained_scientific_bytes_changed")
    external = lambda f: {k: v for k, v in f["commitments"].items()
                          if not k.startswith(f["candidate"] + "/")}
    require(external(initial) == external(final) and
            initial["registry_snapshot"] == final["registry_snapshot"], "retained_task_or_sources_changed")


def preflight_freezes(root, builder, ledger):
    """Block direct-row routes and unbound parents before recursive harness reads."""
    require(builder["initial_candidate"] != builder["final_candidate"], "distinct_stage_freezes_required")
    states = {}
    for stage in ("initial", "final"):
        candidate = builder[stage + "_candidate"]
        require(re.fullmatch(r"candidates/[A-Za-z0-9_-]+", candidate), "candidate_path")
        prefix = builder["bundle"] + "/" + candidate
        frozen = json.loads(bound_bytes(root, {"path": prefix + "/freeze.json",
                                               "sha256": builder[stage + "_freeze_sha256"]}, ledger))
        require(frozen.get("route") == "generator.py" and frozen.get("candidate") == candidate and
                safe_path(root, prefix + "/generator.py").is_file() and
                not safe_path(root, prefix + "/generated.csv").exists(), "only_frozen_program_candidates")
        require(frozen.get("revision_index") == (0 if stage == "initial" else 1), "stage_revision_index")
        states[stage] = frozen
    require(states["initial"].get("parent") is None, "initial_parent_must_be_absent")
    require(states["final"].get("parent") == {
        "candidate": builder["initial_candidate"], "receipt_path": builder["initial_candidate"] + "/freeze.json",
        "sha256": builder["initial_freeze_sha256"]}, "final_parent_mismatch")
    return states


def receipt_metadata(root, bundle_relative, slot, frozen, task, execution, ledger):
    """Verify success metadata before any generated CSV byte access."""
    prefix = f"{bundle_relative}/executions/{slot['run_id']}"
    receipt = json.loads(bound_bytes(root, {"path": prefix + "/execution.json",
                                         "sha256": slot["receipt_sha256"]}, ledger))
    require(receipt.get("schema_version") == 1 and receipt.get("kind") == "generator_execution" and
            receipt.get("run_id") == slot["run_id"] and receipt.get("status") == slot["status"] and
            receipt.get("candidate") == slot["execution_candidate"] and receipt.get("route") == "generator.py",
            "execution_receipt_identity")
    require(receipt.get("candidate_freeze_sha256") == slot["execution_freeze_sha256"], "execution_freeze_mismatch")
    require(receipt.get("isolation_scope") == "generator_process_only" and
            receipt.get("agent_isolation") == "not_provided" and
            receipt.get("scientific_validity") == "not_assessed", "execution_scope")
    limits = receipt.get("limits", {})
    require(limits.get("seed") == slot["seed"], "execution_seed_mismatch")
    execution._limits(**limits)
    if slot["status"] != "success":
        return receipt  # Failed/timeout outputs and logs are never opened.
    require(receipt.get("generator_executed") is True and receipt.get("runtime") == execution.DEFAULT_RUNTIME
            and receipt.get("error") is None and receipt.get("process", {}).get("returncode") == 0
            and receipt.get("process", {}).get("host_timeout") is False, "execution_not_successful")
    run = safe_path(root, prefix)
    files = receipt.get("files")
    require(isinstance(files, dict) and set(files) == SUCCESS_FILES, "unexpected_execution_artifacts")
    require(files.get("output/generated.csv") == slot["output_sha256"], "output_receipt_mismatch")
    actual = set(execution._files(run)) - {"execution.json"}
    require(actual == set(files), "execution_file_set_changed")
    for name, sha in files.items():
        if name == "output/generated.csv":
            ledger["case:" + prefix + "/" + name] = sha
        else:
            bound_bytes(root, {"path": prefix + "/" + name, "sha256": sha}, ledger)
    bindings = read_json(run / "input_bindings.json")
    require(bindings.get("candidate_freeze_sha256") == slot["execution_freeze_sha256"] and
            set(bindings.get("files", {})) == {"task.json", "model_spec.json", "generator.py"}, "staged_bindings")
    for name, sha in bindings["files"].items():
        committed = name if name == "task.json" else frozen["candidate"] + "/" + name
        require(frozen["commitments"].get(committed) == sha == files.get("input/" + name), "staged_input_changed")
    request = read_json(run / "input/request.json")
    require(request.get("schema_version") == 1 and request.get("task_id") == task["task_id"] and
            {k: request.get(k) for k in limits} == limits, "request_identity")
    launch, report = read_json(run / "launch.json"), read_json(run / "output/worker_report.json")
    require(launch.get("worker_sha256") == files.get("input/worker.py") ==
            ledger["project:cohort_harness/_worker.py"], "worker_hash_mismatch")
    require(launch.get("runtime") == execution.DEFAULT_RUNTIME and
            launch.get("isolation") == "curated_bubblewrap_mounts_no_network" and
            launch.get("argv") == execution._command(execution.DEFAULT_RUNTIME, run, limits["timeout_seconds"]),
            "isolation_launch_changed")
    require(report.get("status") == "completed" and report.get("generator_started") is True and
            report.get("rows") == 2000 and report.get("columns") == [c["name"] for c in task["columns"]],
            "worker_completion_mismatch")
    return receipt


def verify_release(root):
    """Gate metadata and freezes only; never open reference/generated CSVs."""
    root = Path(root).resolve()
    release_body = safe_path(root, "EVALUATION_RELEASE.json").read_bytes()
    release = json.loads(release_body)
    builders, schedule = validate_schedule(release)
    ledger = {"case:EVALUATION_RELEASE.json": digest(release_body)}
    require(set(release.get("bindings", {})) == set(BINDINGS), "required_bindings")
    documents = {name: bound_bytes(root, release["bindings"][name], ledger, expected_path=path)
                 for name, path in BINDINGS.items()}
    require(Path(__file__).resolve() == safe_path(root, BINDINGS["evaluation_controller"]).resolve(), "controller_location")
    task, panel = json.loads(documents["task"]), json.loads(documents["source_panel"])
    require(task.get("mode") == "whole_cohort" and task.get("n_rows") == 2000 and
            panel.get("analytical_seeds_controller_owned") == list(SEEDS), "public_schedule_mismatch")
    reference = release.get("reference", {})
    require(reference.get("path") == REFERENCE and re.fullmatch(r"[0-9a-f]{64}", str(reference.get("sha256"))), "reference_binding")
    prep = json.loads(documents["preparation_receipt"])
    prep_release = json.loads(documents["preparation_release"])
    require(prep.get("schema") == "ensanut_preparation_receipt_v2" and prep.get("readiness", {}).get("ready") is True
            and prep.get("release_sha256") == release["bindings"]["preparation_release"]["sha256"]
            and prep.get("release_id") == prep_release.get("release_id"), "reference_preparation_not_ready")
    require(prep.get("outputs", {}).get("private/reference_v2.csv", {}).get("sha256") == reference["sha256"], "reference_receipt_mismatch")
    for name in ("protocol", "analysis_engine", "preparation_script"):
        require(prep.get("bindings", {}).get(name) == release["bindings"][name], "preparation_binding_mismatch")
    project = root.parent.parent
    harness = release.get("harness_files", {})
    actual = {p.relative_to(project).as_posix() for p in (project / "cohort_harness").rglob("*.py")}
    require(isinstance(harness, dict) and bool(actual) and set(harness) == actual, "harness_implementation_set")
    for name, sha in harness.items():
        bound_bytes(project, {"path": name, "sha256": sha}, ledger, namespace="project")
    sys.path.insert(0, str(project))
    from cohort_harness import lifecycle, execution
    require(Path(lifecycle.__file__).resolve() == project / "cohort_harness/lifecycle.py" and
            Path(execution.__file__).resolve() == project / "cohort_harness/execution.py", "harness_import_location")
    states, physical_bundles = {}, set()
    for builder in builders:
        bundle = safe_path(root, builder["bundle"])
        identity = os.path.normcase(str(bundle.resolve()))
        require(identity not in physical_bundles, "shared_physical_builder_bundle")
        physical_bundles.add(identity)
        require("private" not in Path(builder["bundle"]).parts, "private_builder_bundle")
        require(digest((bundle / "task.json").read_bytes()) == release["bindings"]["task"]["sha256"], "builder_task_changed")
        states[builder["id"]] = preflight_freezes(root, builder, ledger)
    # All candidates' actual routes and exact lineage are prechecked before the
    # harness can recursively verify any candidate or parent.
    for builder in builders:
        bundle = safe_path(root, builder["bundle"])
        for stage in ("initial", "final"):
            candidate = builder[stage + "_candidate"]
            frozen = lifecycle.verify_candidate(bundle, candidate)
            states[builder["id"]][stage] = frozen
            for name, sha in frozen["commitments"].items():
                ledger["case:" + builder["bundle"] + "/" + name] = sha
        ledger["case:" + builder["bundle"] + "/registry.json"] = digest((bundle / "registry.json").read_bytes())
    by_id = {b["id"]: b for b in builders}
    receipts = {}
    for slot in schedule:
        builder, stage = by_id[slot["builder"]], slot["stage"]
        require(slot["stage_candidate"] == builder[stage + "_candidate"], "stage_candidate_mismatch")
        retained = slot.get("retained_from")
        if retained is not None:
            require(stage == "final" and retained == {"stage": "initial", "seed": slot["seed"]}, "invalid_retention_link")
            retained_identity(states[slot["builder"]]["initial"], states[slot["builder"]]["final"])
            previous = next(s for s in schedule if s["builder"] == slot["builder"] and s["stage"] == "initial" and s["seed"] == slot["seed"])
            require(all(slot.get(k) == previous.get(k) for k in ("execution_candidate", "run_id", "receipt_sha256", "output_sha256", "status")), "retained_execution_changed")
            executed_stage = "initial"
        else:
            executed_stage = stage
            require(stage == "initial" or states[slot["builder"]]["final"]["revision"]["kind"] == "revise", "retention_requires_reuse")
        require(slot["execution_candidate"] == builder[executed_stage + "_candidate"], "execution_candidate_mismatch")
        slot["execution_freeze_sha256"] = builder[executed_stage + "_freeze_sha256"]
        receipts[(slot["builder"], stage, slot["seed"])] = receipt_metadata(
            root, builder["bundle"], slot, states[slot["builder"]][executed_stage], task, execution, ledger)
    return {"root": root, "release": release, "ledger": ledger, "task": task, "receipts": receipts,
            "preparation": prep, "execution": execution, "lifecycle": lifecycle}


def write_json_exclusive(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def flatten(result):
    return {**result["questions"], **result["secondary"],
            **{f"{field}.{name}": value for field, summary in result["diagnostics"].items() for name, value in summary.items()},
            "q1_residual_rms": result["q1_residual_rms"]}


def run_authorized(root=None):
    root = Path(root).resolve() if root is not None else Path(__file__).resolve().parent.parent
    results = safe_path(root, "analysis/results")
    require(not results.exists(), "results_exist_no_repeat")
    gate = verify_release(root)
    results.mkdir()  # Exclusive one-attempt marker, before any cohort byte access.
    write_json_exclusive(results / "EVALUATION_ATTEMPT.json", {
        "release_sha256": gate["ledger"]["case:EVALUATION_RELEASE.json"],
        "started_utc": datetime.now(timezone.utc).isoformat(), "scheduled_slots": len(gate["release"]["schedule"])})
    try:
        release, schedule = gate["release"], gate["release"]["schedule"]
        builders = {b["id"]: b for b in release["builders"]}
        # Only here may successful generated outputs be opened by the existing API.
        verified_runs = set()
        for slot in schedule:
            key = (slot["builder"], slot["run_id"])
            if slot["status"] == "success" and key not in verified_runs:
                gate["execution"].verify_execution(safe_path(root, builders[slot["builder"]]["bundle"]), slot["run_id"])
                verified_runs.add(key)
        require(verify_release(root)["ledger"] == gate["ledger"], "metadata_changed_before_reference_access")
        import importlib.util
        import pandas as pd
        import numpy as np
        spec = importlib.util.spec_from_file_location("cycle2_fixed_engine", root / BINDINGS["analysis_engine"])
        engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(engine)
        body = bound_bytes(root, release["reference"], gate["ledger"], expected_path=REFERENCE)
        reference = pd.read_csv(io.BytesIO(body), float_precision="round_trip", keep_default_na=False,
                                na_values=[""], dtype={name: "string" for name in engine.CLUSTER_COLUMNS})
        require(set(reference.columns) == set(engine.SCIENTIFIC_COLUMNS + engine.CLUSTER_COLUMNS), "reference_columns")
        _, counts = engine._weights_and_counts(engine.validate_cohort(reference, require_clusters=True))
        require(len(reference) >= 400 and min(counts) >= 30 and
                len(reference) == gate["preparation"]["readiness"]["total_rows"], "reference_readiness_mismatch")
        stability = engine.cluster_stability(reference, attempts=399, seed=18301)
        reference_result = stability.pop("point_estimate")
        stability.pop("valid_replicate_estimates")  # Aggregate bands/counts only in the saved report.
        cache, slots, rows = {}, [], []
        for endpoint, value in flatten(reference_result).items():
            band = stability["bands"][endpoint]
            rows.append({"kind": "reference", "builder": "", "stage": "reference", "seed": "", "status": "success",
                         "endpoint": endpoint, "value": value, "lower": band["lower"] if band else None,
                         "upper": band["upper"] if band else None, "output_sha256": release["reference"]["sha256"]})
        for slot in schedule:
            record = {k: slot.get(k) for k in ("builder", "stage", "seed", "stage_candidate", "execution_candidate",
                                              "run_id", "retained_from", "receipt_sha256", "output_sha256")}
            key = slot["output_sha256"] if slot["status"] == "success" else None
            if key is None:
                record.update(status=slot["status"], failure="execution_" + slot["status"], analysis=None)
            else:
                if key not in cache:
                    path = safe_path(root, builders[slot["builder"]]["bundle"] + "/executions/" + slot["run_id"] + "/output/generated.csv")
                    generated = gate["lifecycle"].read_table(path, gate["task"], output=True)
                    try:
                        _, cells = engine._weights_and_counts(engine.validate_cohort(generated))
                        require(len(generated) == 2000 and all(cells == 250), "generated_cell_quota")
                        cache[key] = {"status": "success", "analysis": engine.analyze_cohort(generated)}
                    except (engine.AnalyticalError, EvaluationError) as error:
                        cache[key] = {"status": "invalid_generated_table", "failure": getattr(error, "code", str(error)), "analysis": None}
                record.update(cache[key])
            slots.append(record)
            estimates = flatten(record["analysis"]) if record["analysis"] else {name: None for name in flatten(reference_result)}
            for endpoint, value in estimates.items():
                rows.append({"kind": "generated", "builder": slot["builder"], "stage": slot["stage"], "seed": slot["seed"],
                             "status": record["status"], "endpoint": endpoint, "value": value, "lower": None,
                             "upper": None, "output_sha256": slot["output_sha256"]})
        # Recheck every consumed byte commitment before writing aggregate results.
        for key, expected in gate["ledger"].items():
            namespace, relative = key.split(":", 1)
            base = root if namespace == "case" else root.parent.parent
            require(digest(safe_path(base, relative).read_bytes()) == expected, "input_changed_before_results")
        report = {"schema": "ensanut_evaluation_aggregate_v1", "release_id": release["release_id"],
                  "interpretation": engine.STABILITY_LABEL, "input_hashes": gate["ledger"],
                  "software": {"python": sys.version, "numpy": np.__version__, "pandas": pd.__version__},
                  "scheduled_slots": len(schedule), "unique_successful_execution_runs": len(verified_runs),
                  "unique_output_contents": len(cache), "successful_analytical_slots": sum(s["status"] == "success" for s in slots),
                  "failed_slots": sum(s["status"] != "success" for s in slots),
                  "reference": reference_result, "reference_stability": stability, "scheduled_results": slots}
        write_json_exclusive(results / "aggregate.json", report)
        with (results / "all_endpoints.csv").open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        write_json_exclusive(results / "EVALUATION_COMPLETED.json", {
            "status": "completed", "completed_utc": datetime.now(timezone.utc).isoformat(),
            "release_sha256": gate["ledger"]["case:EVALUATION_RELEASE.json"],
            "outputs": {name: digest((results / name).read_bytes()) for name in ("aggregate.json", "all_endpoints.csv")}})
        return {"status": "completed", "scheduled_slots": len(schedule), "failed_slots": report["failed_slots"]}
    except Exception as error:
        write_json_exclusive(results / "EVALUATION_FAILURE.json", {
            "status": "failed_attempt_no_retry", "type": type(error).__name__,
            "reason": str(error) if isinstance(error, EvaluationError) else "unexpected_error_no_rows_exported"})
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    try:
        print(json.dumps(run_authorized()))
    except Exception as error:
        print(json.dumps({"status": "rejected_or_failed", "type": type(error).__name__,
                          "reason": str(error) if isinstance(error, EvaluationError) else "see_preserved_failure_receipt_if_created"}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
