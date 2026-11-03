"""Finite one-pass CHNS benchmark; no reference decode or generator host import."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
sys.path.insert(0, str(PROJECT))
from cohort_harness import contracts, execution, lifecycle

IDS = tuple(f"{arm}_A{i:02d}" for arm in ("E0", "E1") for i in range(1, 6))
SEEDS = (1701, 1702, 1703)
CANDIDATE = "candidates/initial"
FILES = ("generator.py", "model_spec.json", "evidence.json", "decision.md", "checks.json")
LIMITS = dict(timeout_seconds=180, memory_mb=1024, output_bytes=2_000_000, log_bytes=10_000)
OLD = PROJECT / "work/chns_admission_2026-11-01/f2"
ANALYSIS_MODULE = OLD / "evaluation/chns_f2_evaluation.py"
ANALYSIS_PLAN = OLD / "analysis_plan.json"
RUNTIME_CHECK = PROJECT / "work/scaleup_2026-11-01/production_release/runtime/runtime_check.py"
RUNTIME_IDENTITY = RUNTIME_CHECK.parent / "RUNTIME_IDENTITY.json"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return lifecycle.read_json(Path(path))


def write(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def binding(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": sha(path)}


def release_digest(release):
    return digest({k: v for k, v in release.items() if k != "approval"})


def _approval(review, expected=None):
    require(review.get("decision") == "approved" and review.get("independent") is True, "Independent approval required")
    identities = [review.get(k, "").strip().casefold() for k in ("reviewer_id", "producer_id")]
    require(all(identities) and identities[0] != identities[1], "Reviewer must differ from producer")
    if expected is not None:
        require(review.get("approved_sha256") == expected, "Approval commitment mismatch")


def _check_binding(item):
    require(set(item) == {"path", "sha256"} and Path(item["path"]).is_absolute(), "Absolute file binding required")
    require(sha(item["path"]) == item["sha256"], "Bound file changed: " + item["path"])
    return Path(item["path"])


def _release(path):
    path = Path(path).resolve()
    r = read(path)
    require(r.get("schema_version") == 1 and r.get("kind") == "existing_chns_benchmark_release" and r.get("status") == "released", "Benchmark is not released")
    _approval(r["approval"], release_digest(r))
    root = Path(r["bundle_root"])
    require(root.is_absolute() and root.resolve() == root and root.is_dir(), "Existing absolute bundle root required")
    artifacts = r["artifacts"]
    require(len({x["path"] for x in artifacts}) == len(artifacts), "Duplicate artifact bindings")
    # Reference aggregates are deliberately unopened until inventory closure.
    refs = {r["evaluation"][k]["path"] for k in ("reference_report", "independent_reference_report")}
    require(not refs & {x["path"] for x in artifacts}, "Reference aggregates must be deferred evaluation bindings")
    for item in artifacts:
        _check_binding(item)
    required = [Path(__file__).resolve(), ANALYSIS_MODULE, ANALYSIS_PLAN, RUNTIME_CHECK, RUNTIME_IDENTITY,
                Path(execution.__file__), Path(lifecycle.__file__), Path(contracts.__file__), PROJECT / "cohort_harness/_worker.py"]
    have = {Path(x["path"]).resolve() for x in artifacts}
    require(set(p.resolve() for p in required) <= have, "Required implementation/runtime artifacts not release-bound")
    for key, expected in (("analysis_module", ANALYSIS_MODULE), ("analysis_plan", ANALYSIS_PLAN)):
        require(Path(r["evaluation"][key]["path"]).resolve() == expected.resolve(), "Use unchanged CHNS pure analysis and plan")
        _check_binding(r["evaluation"][key])
    for key, expected in (("runtime_check", RUNTIME_CHECK), ("runtime_identity", RUNTIME_IDENTITY)):
        require(Path(r[key]["path"]).resolve() == expected.resolve(), "Use unchanged trusted Wave A runtime")
        _check_binding(r[key])
    for identifier in IDS:
        bundle = root / identifier
        require(bundle.is_dir() and not bundle.is_symlink(), "Missing constructor bundle")
        for name in ("task.json", "registry.json", "sources/evidence_packet.json", "sources/NGSP_UNITS.md", "input/compiled_evidence.json"):
            require((bundle / name).resolve() in have, "Constructor input not release-bound: " + identifier + "/" + name)
        task = read(bundle / "task.json")
        require(task["mode"] == "whole_cohort" and task["n_rows"] == 3000 and not (bundle / "observed.csv").exists(), "Whole-cohort 3000-row task required")
    require(len({sha(root / i / "task.json") for i in IDS}) == 1, "Constructor tasks must match exactly")
    return r, root, path


def _control(release_path, *, open_required=True):
    r, root, path = _release(release_path)
    control = root / "benchmark_control"
    if open_required:
        saved = read(control / "RELEASE_BINDING.json")
        require(saved == {"release": binding(path), "bundle_root": str(root)}, "Ledger release identity changed")
    return r, root, control


def init(release_path):
    r, root, path = _release(release_path)
    control = root / "benchmark_control"
    control.mkdir()  # Exclusive; no replacement/reset path.
    (control / "constructors").mkdir()
    for identifier in IDS:
        (control / "constructors" / identifier).mkdir()
    write(control / "RELEASE_BINDING.json", {"release": binding(path), "bundle_root": str(root)})
    return {"status": "initialized", "constructors": 10, "reserved_slots": 30}


def _constructor(release_path, identifier):
    require(identifier in IDS, "Unknown reserved constructor")
    r, root, control = _control(release_path)
    require(not (control / "FINAL_INVENTORY.json").exists(), "Inventory already closed")
    folder = control / "constructors" / identifier
    require(not (folder / "CLOSED.json").exists(), "Constructor already closed")
    return r, root / identifier, folder


def candidate_review_files(bundle):
    bundle = Path(bundle)
    names = ("task.json", "registry.json", *(CANDIDATE + "/" + x for x in FILES))
    return {name: sha(bundle / name) for name in names}


def freeze_constructor(release_path, identifier, review_path):
    _, bundle, folder = _constructor(release_path, identifier)
    require(not (folder / "FROZEN.json").exists() and not (folder / "RUN_INTENT.json").exists(), "Candidate already bound/attempted")
    review = read(review_path)
    _approval(review)
    require(review.get("schema_version") == 1 and review.get("constructor") == identifier, "Wrong candidate review")
    require(canonical(review["files"]) == canonical(candidate_review_files(bundle)), "Reviewed candidate bytes changed")
    directory = bundle / CANDIDATE
    require(set(lifecycle._files(directory)) == set(FILES), "Exactly five candidate artifacts required before freeze")
    require(sha(directory / "evidence.json") == sha(bundle / "input/compiled_evidence.json"), "Candidate evidence differs from fixed arm evidence")
    frozen = lifecycle.freeze_candidate(bundle, CANDIDATE)
    require(frozen["route"] == "generator.py", "Program route required")
    result = {"constructor": identifier, "candidate": CANDIDATE, "freeze_sha256": sha(directory / "freeze.json"),
              "review": binding(review_path), "reviewed_files": review["files"]}
    write(folder / "FROZEN.json", result)
    return result


def _module(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _runtime(r):
    return _module(r["runtime_check"]["path"], "evcb_runtime_check").verify(r["runtime_identity"]["path"])


def _frozen(bundle, folder):
    record = read(folder / "FROZEN.json")
    _check_binding(record["review"])
    require(canonical(record["reviewed_files"]) == canonical(candidate_review_files(bundle)), "Frozen reviewed inputs changed")
    lifecycle.verify_candidate(bundle, CANDIDATE)
    require(sha(bundle / CANDIDATE / "freeze.json") == record["freeze_sha256"], "Candidate freeze changed")
    return record


def _tree(path):
    if not path.exists():
        return {}
    return {p.relative_to(path).as_posix(): sha(p) for p in sorted(path.rglob("*")) if p.is_file()}


def run_constructor(release_path, identifier):
    r, bundle, folder = _constructor(release_path, identifier)
    frozen = _frozen(bundle, folder)
    require(not (folder / "RUN_INTENT.json").exists(), "All three slots already consumed; no retry/resume")
    require(all(not (bundle / "executions" / f"initial_{s}").exists() for s in SEEDS), "Unscheduled existing execution")
    write(folder / "RUN_INTENT.json", {"constructor": identifier, "freeze_sha256": frozen["freeze_sha256"],
          "seeds": list(SEEDS), "limits": LIMITS, "allocated_attempts": 3, "created_utc": datetime.now(timezone.utc).isoformat()})
    runtime_error = None
    try:
        runtime = _runtime(r)
    except Exception as exc:
        runtime, runtime_error = None, type(exc).__name__
    outcomes = []
    for seed in SEEDS:
        run_id = f"initial_{seed}"
        result = {"constructor": identifier, "seed": seed, "run_id": run_id, "allocated": True,
                  "dispatch_attempted": False, "status": "runtime_unavailable" if runtime_error else "error",
                  "error_type": runtime_error, "execution_sha256": None, "output_sha256": None}
        if not runtime_error:
            result["dispatch_attempted"] = True
            write(folder / f"{run_id}_INTENT.json", {"seed": seed, "run_id": run_id})
            try:
                execution.run_candidate(bundle, CANDIDATE, run_id, seed, runtime=execution.DEFAULT_RUNTIME, **LIMITS)
                receipt = execution.verify_execution(bundle, run_id)
                require(receipt["candidate"] == CANDIDATE and receipt["candidate_freeze_sha256"] == frozen["freeze_sha256"], "Wrong execution candidate")
                require(receipt["limits"] == {"seed": seed, **LIMITS}, "Wrong execution limits")
                result["status"] = receipt["status"]
                result["execution_sha256"] = sha(bundle / "executions" / run_id / "execution.json")
                if receipt["status"] == "success":
                    result["output_sha256"] = sha(bundle / "executions" / run_id / "output/generated.csv")
            except Exception as exc:
                result["error_type"] = type(exc).__name__
        result["retained_artifacts"] = _tree(bundle / "executions" / run_id)
        write(folder / f"{run_id}_RESULT.json", result)
        outcomes.append(result)
    write(folder / "RUN_COMPLETE.json", {"runtime": runtime, "outcomes": outcomes})
    return {"constructor": identifier, "statuses": [x["status"] for x in outcomes], "target_effects_computed": False}


def _slots(bundle, folder, identifier):
    frozen = _frozen(bundle, folder) if (folder / "FROZEN.json").exists() else None
    intent = (folder / "RUN_INTENT.json").exists()
    slots = []
    for seed in SEEDS:
        run_id = f"initial_{seed}"
        result_path = folder / f"{run_id}_RESULT.json"
        if result_path.exists():
            result = read(result_path)
            require(result["constructor"] == identifier and result["seed"] == seed and result["run_id"] == run_id and intent, "Slot identity mismatch")
            require(result["retained_artifacts"] == _tree(bundle / "executions" / run_id), "Retained execution artifacts changed")
            if result["execution_sha256"] is not None:
                receipt = execution.verify_execution(bundle, run_id)
                require(frozen is not None and receipt["candidate_freeze_sha256"] == frozen["freeze_sha256"] and receipt["candidate"] == CANDIDATE, "Execution parent mismatch")
                require(receipt["status"] == result["status"] and receipt["limits"] == {"seed": seed, **LIMITS}, "Slot receipt mismatch")
                require(sha(bundle / "executions" / run_id / "execution.json") == result["execution_sha256"], "Execution receipt changed")
            require(result["status"] != "success" or result["output_sha256"] is not None and result["execution_sha256"] is not None, "Success lacks verified output")
        else:
            result = {"constructor": identifier, "seed": seed, "run_id": run_id, "allocated": intent,
                      "dispatch_attempted": (folder / f"{run_id}_INTENT.json").exists(),
                      "status": "interrupted_or_unrun_consumed" if intent else "not_run",
                      "error_type": None, "execution_sha256": None, "output_sha256": None,
                      "retained_artifacts": _tree(bundle / "executions" / run_id)}
        slots.append(result)
    return slots


def close_constructor(release_path, identifier, reason):
    _, bundle, folder = _constructor(release_path, identifier)
    require(isinstance(reason, str) and reason.strip(), "Closure reason required")
    record = {"constructor": identifier, "reason": reason, "slots": _slots(bundle, folder, identifier),
              "freeze_sha256": sha(bundle / CANDIDATE / "freeze.json") if (folder / "FROZEN.json").exists() else None,
              "control_files": {p.name: sha(p) for p in folder.iterdir() if p.is_file()}}
    write(folder / "CLOSED.json", record)
    return {"constructor": identifier, "closed": True, "statuses": [x["status"] for x in record["slots"]]}


def _closed(root, control):
    slots, bindings = [], []
    for identifier in IDS:
        folder = control / "constructors" / identifier
        record = read(folder / "CLOSED.json")
        require(record["constructor"] == identifier, "Wrong constructor closure")
        actual = {p.name: sha(p) for p in folder.iterdir() if p.is_file() and p.name != "CLOSED.json"}
        require(actual == record["control_files"], "Constructor control files changed after closure")
        require(canonical(record["slots"]) == canonical(_slots(root / identifier, folder, identifier)), "Closed slot inventory changed")
        slots.extend(record["slots"])
        bindings.append(binding(folder / "CLOSED.json"))
    require(len(slots) == 30, "Complete thirty-slot inventory required")
    return {"constructors": list(IDS), "seeds": list(SEEDS), "slots": slots, "closure_bindings": bindings}


def close_inventory(release_path):
    _, root, control = _control(release_path)
    inventory = _closed(root, control)
    write(control / "FINAL_INVENTORY.json", inventory)
    return {"status": "closed", "slots": 30, "successes": sum(x["status"] == "success" for x in inventory["slots"])}


def _summary_at(slots, reference, endpoint, point):
    constructors = []
    for identifier in IDS:
        records = [x for x in slots if x["constructor"] == identifier]
        values = [x["analysis"]["estimands"][endpoint]["coefficient"] for x in records
                  if x.get("analysis") and x["analysis"]["estimands"][endpoint]["status"] == "computed"]
        complete = len(records) == len(values) == 3 and all(x["status"] == "success" for x in records)
        constructors.append({"constructor": identifier, "arm": identifier[:2], "complete": complete,
                             "available_seed_estimates": values, "mean_absolute_discrepancy":
                             sum(abs(v - point) for v in values) / 3 if complete else None})
    means = {}
    for arm in ("E0", "E1"):
        group = [x for x in constructors if x["arm"] == arm]
        means[arm] = sum(x["mean_absolute_discrepancy"] for x in group) / 5 if all(x["complete"] for x in group) else None
    delta = means["E1"] - means["E0"] if all(v is not None for v in means.values()) else None
    return {"reference_point": point, "constructors": constructors, "arm_mean_absolute_discrepancy": means,
            "E1_minus_E0": delta, "complete_arms": delta is not None}


def summarize(slots, reference):
    require(len(slots) == 30 and {(x["constructor"], x["seed"]) for x in slots} == {(i, s) for i in IDS for s in SEEDS}, "All thirty distinct slots required")
    endpoints = {}
    for endpoint in ("E1", "E2", "E3"):
        ref = reference["estimands"][endpoint]
        require(ref["status"] == "computed", "Frozen reference endpoint unavailable")
        row = _summary_at(slots, reference, endpoint, ref["coefficient"])
        row["unit"] = ref["unit"]
        interval = ref["interval"]
        row["reference_interval_endpoint_sensitivity"] = ({name: _summary_at(slots, reference, endpoint, interval[name])
             for name in ("lower", "upper")} if interval["status"] == "available" else None)
        endpoints[endpoint] = row
    complete = all(x["complete_arms"] for x in endpoints.values())
    return {"endpoints": endpoints, "complete_arms_all_three_endpoints": complete,
            "both_addressed_projections_improve": complete and all(endpoints[k]["E1_minus_E0"] < 0 for k in ("E1", "E2")),
            "claim_scope": "descriptive_reused_CHNS_benchmark_not_independent_confirmation_or_equivalence",
            "sensitivity_scope": "existing_reference_interval_endpoints_only_not_entire_interval_or_joint_confidence_region",
            "reserved_slots": 30, "execution_successes": sum(x["status"] == "success" for x in slots),
            "execution_failures_or_unrun": sum(x["status"] != "success" for x in slots)}


def evaluate(release_path):
    r, root, control = _control(release_path)
    closed = read(control / "FINAL_INVENTORY.json")  # Mandatory BEFORE reference bytes.
    require(canonical(closed) == canonical(_closed(root, control)), "Final inventory changed")
    out = control / "evaluation"
    out.mkdir()  # Exclusive before aggregate access; no retry or overwrite.
    write(out / "INTENT.json", {"release": binding(Path(release_path).resolve()),
          "inventory": binding(control / "FINAL_INVENTORY.json"), "reference": r["evaluation"]["reference_report"]})
    try:
        ref_path = _check_binding(r["evaluation"]["reference_report"])
        _check_binding(r["evaluation"]["independent_reference_report"])
        reference = read(ref_path)["reference"]
        module = _module(r["evaluation"]["analysis_module"]["path"], "evcb_chns_analysis")
        plan = read(r["evaluation"]["analysis_plan"]["path"])
        slots = []
        for slot in closed["slots"]:
            result = {**slot, "analysis": None, "comparison": None, "analysis_error_type": None}
            if slot["status"] == "success":
                try:
                    bundle = root / slot["constructor"]
                    task = read(bundle / "task.json")
                    path = bundle / "executions" / slot["run_id"] / "output/generated.csv"
                    require(sha(path) == slot["output_sha256"], "Generated output changed")
                    frame = lifecycle.read_table(path, task, output=True)
                    contracts.validate_output(None, frame, task)
                    result["analysis"] = module.analyze(frame, plan, reference=False)
                    result["comparison"] = module.compare_estimates(reference, result["analysis"])
                except Exception as exc:
                    result["analysis_error_type"] = type(exc).__name__
            slots.append(result)
        report = {"schema_version": 1, "kind": "reused_CHNS_E0_E1_benchmark", "reference": reference,
                  "reference_binding": r["evaluation"]["reference_report"], "slots": slots,
                  **summarize(slots, reference), "patient_reference_redecoded": False, "independent_recomputation": "pending"}
        write(out / "REPORT.json", report)
        write(out / "COMPLETION.json", {"report": binding(out / "REPORT.json"), "intent": binding(out / "INTENT.json")})
        return {"report": str(out / "REPORT.json"), "both_addressed_projections_improve": report["both_addressed_projections_improve"], "independent_recomputation": "pending"}
    except Exception as exc:
        write(out / "FAILURE.json", {"error_type": type(exc).__name__, "no_automatic_retry": True})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("init", "close-inventory", "evaluate"):
        sub.add_parser(name)
    p = sub.add_parser("freeze"); p.add_argument("constructor", choices=IDS); p.add_argument("--review", required=True)
    p = sub.add_parser("run"); p.add_argument("constructor", choices=IDS)
    p = sub.add_parser("close"); p.add_argument("constructor", choices=IDS); p.add_argument("--reason", required=True)
    a = parser.parse_args()
    if a.action == "freeze": result = freeze_constructor(a.release, a.constructor, a.review)
    elif a.action == "run": result = run_constructor(a.release, a.constructor)
    elif a.action == "close": result = close_constructor(a.release, a.constructor, a.reason)
    else: result = {"init": init, "close-inventory": close_inventory, "evaluate": evaluate}[a.action](a.release)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
