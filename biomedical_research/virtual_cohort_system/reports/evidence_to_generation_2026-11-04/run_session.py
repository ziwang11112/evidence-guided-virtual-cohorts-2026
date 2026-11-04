"""Bounded evidence-to-generation controller; contains no scientific choices.

All scientific execution uses the supplied WSL/bubblewrap adapter. A reserved
attempt is never retried. Reference aggregates are evaluator-only inputs.
"""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import argparse
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent
P = ROOT.parents[1]
sys.path.insert(0, str(P))
from cohort_harness import execution, lifecycle, semantic_feedback_v1

STAGES = {"initial_trial": [7400], "initial_delivery": [7401, 7402, 7403],
          "revision_trial": [7410], "final_delivery": [7401, 7402, 7403]}
MAX_ATTEMPTS = 8


def read(path):
    return lifecycle.read_json(path)


def write(path, value):
    execution._write(Path(path), value)


def require(value, message):
    if not value:
        raise ValueError(message)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def verify_control_manifest():
    """Read no reference data: this manifest contains hashes and paths only."""
    manifest = read(ROOT / "evaluation/CONTROL_MANIFEST.json")
    require(manifest["protocol_sha256"] == lifecycle.sha256(ROOT / "PROTOCOL.json"),
            "Protocol commitment changed")
    for relative, digest in manifest["controller_files"].items():
        path = ROOT.joinpath(*lifecycle.safe_relative(relative))
        require(path.resolve().is_relative_to(ROOT.resolve()), "Controller path escapes run")
        require(lifecycle.sha256(path) == digest, "Controller file changed: " + relative)
    for relative, digest in manifest["mechanics_files"].items():
        path = P.joinpath(*lifecycle.safe_relative(relative))
        require(lifecycle.sha256(path) == digest, "Harness mechanics changed: " + relative)
    return manifest


def setup(key):
    require(key == "B", "Only request B is authorized")
    manifest = verify_control_manifest()
    protocol = read(ROOT / "PROTOCOL.json")
    require(set(protocol["bundles"]) == {"B"}, "Unexpected request bundle")
    require(protocol["stages"] == STAGES and protocol["max_physical_executions"] == MAX_ATTEMPTS
            and protocol["max_feedback_revisions"] == 1, "Controller schedule differs from protocol")
    bundle = lifecycle._bundle(protocol["bundles"][key])
    require(read(bundle / "RUN_RULES.json")["protocol_sha256"] == manifest["protocol_sha256"],
            "Bundle protocol binding changed")
    local = ROOT / "sessions" / key
    local.mkdir(parents=True, exist_ok=True)
    return bundle, local


@contextmanager
def exclusive_operation(local):
    """Prevent concurrent reservations; a crash leaves a fail-closed lock."""
    lock = local / "controller_operation.lock"
    with lock.open("x", encoding="utf-8") as stream:
        stream.write(timestamp() + "\n")
    try:
        yield
    finally:
        lock.unlink()


def family(candidate, bundle):
    return {"candidate": candidate, "freeze_sha256": lifecycle.sha256(bundle / candidate / "freeze.json")}


def bind_family(path, value):
    if path.exists():
        require(read(path) == value, "Frozen candidate family substitution rejected")
    else:
        write(path, value)


def completed_stage(local, stage):
    results = []
    for seed in STAGES[stage]:
        run_id = "b_" + stage + "_" + str(seed)
        event = local / (run_id + "_reserved.json")
        result = local / (run_id + "_result.json")
        require(event.exists() and result.exists(), "Required prior stage not complete: " + stage)
        record = read(result)
        require(record["run_id"] == run_id and record["seed"] == seed, "Result slot mismatch")
        results.append(record)
    return results


def inventory(bundle, local):
    events = [read(path) for path in local.glob("*_reserved.json")]
    ids = [event["run_id"] for event in events]
    require(len(ids) == len(set(ids)) and len(ids) <= MAX_ATTEMPTS, "Invalid attempt inventory")
    executions = bundle / "executions"
    actual = {path.name for path in executions.iterdir() if path.is_dir()} if executions.exists() else set()
    require(actual <= set(ids), "Unbudgeted execution directory")
    return events


def freeze(key, candidate, parent=None, revision=None):
    bundle, local = setup(key)
    name = execution._name(candidate)
    relative = "candidates/" + name
    directory = bundle / relative
    with exclusive_operation(local):
        inventory(bundle, local)
        preflight = semantic_feedback_v1.preflight(bundle, relative)
        initial_path = local / "initial_family.json"
        if parent is None:
            require(revision is None, "Revision record needs a parent")
            if initial_path.exists():
                require(read(initial_path)["candidate"] == relative, "Only one initial construction is authorized")
            binding = initial_path
        else:
            parent_relative = "candidates/" + execution._name(parent)
            require(initial_path.exists(), "Revision lacks an initial family")
            require(read(initial_path)["candidate"] == parent_relative, "Revision parent must be initial")
            completed_stage(local, "initial_trial")
            completed_stage(local, "initial_delivery")
            require(revision is not None, "Revision record is required")
            binding = local / "final_family.json"
            if binding.exists():
                require(read(binding)["candidate"] == relative, "Only one revision is authorized")
        if (directory / "freeze.json").exists():
            result = lifecycle.verify_candidate(bundle, relative)
        else:
            parent_receipt = bundle / parent_relative / "freeze.json" if parent else None
            result = lifecycle.freeze_candidate(bundle, directory, parent_receipt=parent_receipt,
                                                revision=read(Path(revision)) if revision else None)
        require(result["revision_index"] == (1 if parent else 0), "Unexpected candidate revision index")
        if parent:
            require(result["parent"] == {"candidate": parent_relative,
                    "receipt_path": parent_relative + "/freeze.json",
                    "sha256": read(initial_path)["freeze_sha256"]}, "Revision parent receipt mismatch")
        else:
            require(result["parent"] is None, "Initial candidate has a parent")
        bind_family(binding, family(relative, bundle))
        preflight_path = local / (name + "_preflight.json")
        if preflight_path.exists():
            require(read(preflight_path) == preflight, "Semantic preflight changed")
        else:
            write(preflight_path, preflight)
        return result


def load_diagnostics():
    path = ROOT / "evaluation/generated_diagnostics.py"
    spec = importlib.util.spec_from_file_location("evidence_build_generated_diagnostics", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def retention_aliases(bundle, local, candidate):
    require(not (local / "revision_trial_binding.json").exists(), "Retain cannot follow a revision trial")
    records = completed_stage(local, "initial_delivery")
    require(all(row["candidate"] == candidate for row in records), "Initial delivery candidate mismatch")
    path = local / "final_delivery_aliases.json"
    aliases = [{"stage": "final_delivery", "seed": row["seed"], "candidate": candidate,
                "run_id": row["run_id"], "aliased_initial": True,
                "physical_execution": False, "status": row["status"],
                "initial_result_sha256": lifecycle.sha256(local / (row["run_id"] + "_result.json"))}
               for row in records]
    write(path, {"kind": "retained_delivery_aliases", "aliases": aliases})
    return aliases


def run(key, candidate, stage):
    bundle, local = setup(key)
    require(stage in STAGES, "Unrecognized stage")
    name = execution._name(candidate)
    relative = "candidates/" + name
    with exclusive_operation(local):
        inventory(bundle, local)
        frozen = lifecycle.verify_candidate(bundle, relative)
        initial_path = local / "initial_family.json"
        require(initial_path.exists(), "Controller freeze is required before execution")
        initial = read(initial_path)
        current = family(relative, bundle)
        if stage.startswith("initial_"):
            require(frozen["revision_index"] == 0 and frozen["parent"] is None, "Initial stage requires initial candidate")
            require(current == initial, "Initial candidate substitution rejected")
            if stage == "initial_delivery":
                completed_stage(local, "initial_trial")
        else:
            completed_stage(local, "initial_trial")
            completed_stage(local, "initial_delivery")
            if relative == initial["candidate"]:
                require(stage == "final_delivery", "Retained model needs no revision trial")
                require(current == initial, "Initial freeze changed")
            else:
                require(frozen["revision_index"] == 1 and frozen["parent"] == {
                    "candidate": initial["candidate"], "receipt_path": initial["candidate"] + "/freeze.json",
                    "sha256": initial["freeze_sha256"]},
                    "Final candidate must be a single direct revision")
            if stage == "final_delivery":
                decision = read(bundle / "FINAL_DECISION.json")
                expected = "retain" if relative == initial["candidate"] else "revise"
                require(decision["choice"] == expected and decision["candidate"] == relative,
                        "Final delivery needs an explicit matching author decision")
                bind_family(local / "final_family.json", current)
                if expected == "retain":
                    return retention_aliases(bundle, local, relative)
            else:
                bind_family(local / "final_family.json", current)
        binding = local / (stage + "_binding.json")
        bind_family(binding, current)
        diagnostics = load_diagnostics()
        results = []
        for seed in STAGES[stage]:
            run_id = "b_" + stage + "_" + str(seed)
            event = local / (run_id + "_reserved.json")
            require(not event.exists(), "Attempt already reserved; retry forbidden: " + run_id)
            require(len(inventory(bundle, local)) < MAX_ATTEMPTS, "Physical attempt budget exhausted")
            write(event, {"run_id": run_id, "seed": seed, "stage": stage,
                          "candidate": relative, "created_utc": timestamp(), "charged": True})
            record = {"run_id": run_id, "seed": seed, "stage": stage, "candidate": relative,
                      "feedback_adapter": "semantic_feedback_v1", "reference_read": False}
            try:
                receipt = execution.run_candidate(bundle, relative, run_id, seed, timeout_seconds=30,
                    memory_mb=1536, output_bytes=20_000_000, log_bytes=100_000)
                execution.verify_execution(bundle, run_id)
                record.update(status=receipt["status"], execution_status=receipt["status"],
                              execution_verified=True,
                              generator_executed=receipt["generator_executed"], error=receipt.get("error"))
                if receipt["status"] == "success":
                    table = bundle / "executions" / run_id / "output/generated.csv"
                    # Bind the verified table before feedback. Feedback failure must
                    # never remove a successful draw from the scheduled evaluation.
                    record.update(table_sha256=lifecycle.sha256(table))
                    feedback_id = run_id + "_source"
                    try:
                        feedback = semantic_feedback_v1.collect_feedback(bundle, relative, run_id, feedback_id)
                        feedback_path = bundle / "semantic_feedback_v1" / feedback_id / "feedback.json"
                        record.update(source_feedback_status=feedback["status"], source_feedback=str(feedback_path),
                                      source_feedback_sha256=lifecycle.sha256(feedback_path))
                    except Exception as error:
                        record.update(source_feedback_status="error", source_feedback_error=type(error).__name__ + ": " + str(error))
                    try:
                        analysis = diagnostics.diagnose_csv(table, key)
                        out = bundle / "author_feedback"
                        out.mkdir(exist_ok=True)
                        output = out / (run_id + "_diagnostics.json")
                        write(output, analysis)
                        record.update(diagnostics_status=analysis.get("status", "complete"), diagnostics=str(output),
                                      diagnostics_sha256=lifecycle.sha256(output))
                    except Exception as error:
                        record.update(diagnostics_status="error", diagnostics_error=type(error).__name__ + ": " + str(error))
            except Exception as error:
                record.update(status="wrapper_error", error=type(error).__name__ + ": " + str(error))
            write(local / (run_id + "_result.json"), record)
            results.append(record)
        return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["freeze", "run"])
    parser.add_argument("--request", choices=["B"], required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--stage", choices=list(STAGES))
    parser.add_argument("--parent")
    parser.add_argument("--revision")
    args = parser.parse_args()
    if args.action == "freeze":
        result = freeze(args.request, args.candidate, args.parent, args.revision)
        print(json.dumps({"status": "frozen", "candidate": args.candidate, "route": result["route"]}))
    else:
        if args.stage is None:
            parser.error("--stage required")
        print(json.dumps(run(args.request, args.candidate, args.stage), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
