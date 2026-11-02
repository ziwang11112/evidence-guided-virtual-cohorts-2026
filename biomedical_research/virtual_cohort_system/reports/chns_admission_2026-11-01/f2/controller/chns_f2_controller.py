"""Released CHNS F2 schedule only: no model authoring, target reads or replay.

Four immutable stage slots, three fixed seeds each. A started stage is never
retried; failures consume their slots. Approval identities remain procedural.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from cohort_harness import contracts, execution, lifecycle
from cohort_harness import semantic_feedback_v1 as strict
from cohort_harness import conditional_feedback_v1 as conditional
from cohort_harness.contracts import exact_keys, require, text
from cohort_harness.lifecycle import _bundle, _path, read_json, sha256


FOLDER = "f2_controller"
BINDING = "f2_stage_binding.json"
REVISION_FEEDBACK = "revision_feedback.json"
CANDIDATE_REVIEW = "candidate_review.json"
CONSTRUCTIONS = ("C1", "C2")
STAGES = ("initial", "revised")
SEEDS = (1701, 1702, 1703)
SCHEDULE = {"constructions": list(CONSTRUCTIONS), "stages": list(STAGES),
            "seeds": list(SEEDS), "max_target_tables": 12}
LIMITS = {"timeout_seconds": 180, "memory_mb": 1024, "output_bytes": 20_000_000, "log_bytes": 100_000}


def _same(left, right):
    return strict._json(left) == strict._json(right)


def engine_hashes():
    return {**strict.legacy._engine(), "semantic_feedback_v1.py": sha256(strict.__file__),
            "conditional_feedback_v1.py": sha256(conditional.__file__)}


def _reference(root, reference):
    exact_keys(reference, {"path", "sha256"}, where="released file reference")
    path = _path(root, reference["path"])
    require(sha256(path) == reference["sha256"], "Released document changed: " + reference["path"])
    return path


def _release(bundle, release="F2_RELEASE.json"):
    root = _bundle(bundle)
    release_path = _path(root, release)
    contract = read_json(release_path)
    exact_keys(contract, {"schema_version", "status", "task_sha256", "evidence_sha256", "controller_sha256",
                          "engine_sha256", "protocol", "analysis_plan", "builder_brief", "feedback_policy",
                          "schedule", "limits", "independent_review"}, where="F2 release")
    require(type(contract["schema_version"]) is int and contract["schema_version"] == 1, "Invalid F2 release version")
    require(contract["status"] == "released", "F2 has not been released after independent review")
    require(contract["controller_sha256"] == sha256(__file__), "Controller differs from F2 release")
    require(_same(contract["engine_sha256"], engine_hashes()), "Released feedback/execution engines changed")
    require(_same(contract["schedule"], SCHEDULE) and _same(contract["limits"], LIMITS), "F2 schedule/limits changed")
    require(contract["task_sha256"] == sha256(root / "task.json"), "Released task changed")
    contracts._hash(contract["evidence_sha256"])
    task = read_json(root / "task.json")
    contracts.validate_task(task)
    require(task["mode"] == "whole_cohort" and task["n_rows"] == 3000 and task["budget"]["revisions"] == 1,
            "F2 requires whole-cohort 3000 rows and at most one revision")
    require([column["name"] for column in task["columns"] if column["role"] == "generated"] ==
            ["age", "female", "bmi", "glucose", "hba1c"], "Wrong F2 generated variables/order")
    require(not _path(root, "observed.csv", file=False).exists(), "F2 forbids individual input")
    for key in ("protocol", "analysis_plan", "builder_brief"):
        _reference(root, contract[key])
    policy = read_json(_reference(root, contract["feedback_policy"]))
    exact_keys(policy, {"schema_version", "strict_recipe_sha256", "strict_semantics_sha256",
                        "required_assumptions", "conditional_interpretations"}, where="F2 feedback policy")
    require(type(policy["schema_version"]) is int and policy["schema_version"] == 1, "Invalid feedback policy version")
    for key in ("strict_recipe_sha256", "strict_semantics_sha256"):
        contracts._hash(policy[key])
    require(isinstance(policy["required_assumptions"], list), "Required assumptions must be a list")
    seen = set()
    for assumption in policy["required_assumptions"]:
        exact_keys(assumption, {"id", "description"}, where="required feedback assumption")
        for value in assumption.values():
            text(value, "required assumption value")
        require(assumption["id"] not in seen, "Duplicate required assumption")
        seen.add(assumption["id"])
    require(policy["conditional_interpretations"] is None or
            isinstance(policy["conditional_interpretations"], list) and bool(policy["conditional_interpretations"]),
            "Conditional policy must be null or a nonempty fixed interpretation list")
    review = read_json(_reference(root, contract["independent_review"]))
    exact_keys(review, {"schema_version", "decision", "reviewer_id", "coordinator_id", "independent",
                        "reviewed_utc", "reason", "approved_release"}, where="F2 independent review")
    require(type(review["schema_version"]) is int and review["schema_version"] == 1 and
            review["decision"] == "approved" and review["independent"] is True, "F2 review is not approved")
    for key in ("reviewer_id", "coordinator_id", "reviewed_utc", "reason"):
        text(review[key], "F2 review " + key)
    require(review["reviewer_id"].strip().casefold() != review["coordinator_id"].strip().casefold(),
            "F2 review must declare an independent reviewer")
    require(_same(review["approved_release"], {k: v for k, v in contract.items() if k != "independent_review"}),
            "Independent review does not cover current F2 release")
    return root, contract, policy, {"release_path": release, "release_sha256": sha256(release_path),
                                    "task_sha256": contract["task_sha256"],
                                    "protocol_sha256": contract["protocol"]["sha256"]}


def _slot(construction, stage):
    require(construction in CONSTRUCTIONS and stage in STAGES, "Unbudgeted construction or stage")
    return f"{construction}_{stage}"


def _inventory(root):
    slots = {_slot(c, s) for c in CONSTRUCTIONS for s in STAGES}
    runs = {f"{slot}_s{seed}" for slot in slots for seed in SEEDS}
    for folder, allowed in ((FOLDER, slots), ("executions", runs), (strict.FOLDER, runs), (conditional.FOLDER, runs)):
        directory = _path(root, folder, file=False)
        if directory.exists():
            require(all(path.is_dir() and path.name in allowed for path in directory.iterdir()),
                    "Unbudgeted artifact in " + folder)


def _candidate_preflight(root, contract, policy, slot, binding):
    relative = "candidates/" + slot
    directory = _path(root, relative, file=False)
    require(directory.is_dir(), "Stage candidate directory is missing")
    review = read_json(_path(directory, CANDIDATE_REVIEW))
    exact_keys(review, {"schema_version", "decision", "reviewer_id", "builder_id", "independent", "reviewed_utc",
                        "reason", "release_sha256", "candidate_files", "declined_interpretations"}, where="candidate review")
    require(type(review["schema_version"]) is int and review["schema_version"] == 1 and
            review["decision"] == "approved" and review["independent"] is True, "Candidate review is not approved")
    for key in ("reviewer_id", "builder_id", "reviewed_utc", "reason"):
        text(review[key], "candidate review " + key)
    require(review["reviewer_id"].strip().casefold() != review["builder_id"].strip().casefold(),
            "Candidate needs an independent reviewer")
    require(review["release_sha256"] == binding["release_sha256"], "Candidate reviewed against a different F2 release")
    files = {name: sha256(directory / name) for name in lifecycle._files(directory)
             if name not in {CANDIDATE_REVIEW, BINDING}}
    require(_same(review["candidate_files"], files), "Candidate artifacts changed since independent review")
    require(sha256(directory / "evidence.json") == contract["evidence_sha256"], "Candidate evidence differs from release")
    require(sha256(directory / strict.legacy.PLAN) == policy["strict_recipe_sha256"] and
            sha256(directory / strict.FILE) == policy["strict_semantics_sha256"], "Candidate changed fixed feedback semantics")
    assumptions = {a["id"]: a for a in read_json(directory / "model_spec.json")["assumptions"]}
    require(all(_same(assumptions.get(a["id"]), a) for a in policy["required_assumptions"]),
            "Candidate changed required feedback assumptions")
    strict.preflight(root, relative)
    plan_path = _path(directory, conditional.FILE, file=False)
    allowed = {item["id"]: item for item in (policy["conditional_interpretations"] or [])}
    require(len(allowed) == len(policy["conditional_interpretations"] or []), "Duplicate policy interpretation ID")
    require(isinstance(review["declined_interpretations"], list), "Declined interpretations must be explicit")
    declined = set()
    for item in review["declined_interpretations"]:
        exact_keys(item, {"id", "reason"}, where="declined interpretation")
        require(item["id"] in allowed and item["id"] not in declined, "Unknown/duplicate declined interpretation")
        text(item["reason"], "interpretation declination reason")
        declined.add(item["id"])
    enabled = plan_path.exists()
    selected = set()
    if enabled:
        plan = read_json(plan_path)
        require(plan["builder_id"] == review["builder_id"], "Candidate/interpretation builder mismatch")
        for item in plan["interpretations"]:
            require(item["id"] in allowed and _same(item, allowed[item["id"]]),
                    "Candidate changed approved interpretation semantics")
            selected.add(item["id"])
        conditional.preflight(root, relative)
    require(not selected & declined and selected | declined == set(allowed),
            "Every permitted proxy must be selected or explicitly declined before freeze")
    return directory, relative, enabled


def freeze_stage(bundle, construction, stage, *, release="F2_RELEASE.json", revision=None):
    root, contract, policy, binding = _release(bundle, release)
    slot = _slot(construction, stage)
    _inventory(root)
    directory, relative, enabled = _candidate_preflight(root, contract, policy, slot, binding)
    folder = _path(root, f"{FOLDER}/{slot}", file=False)
    require(not folder.exists() and not (directory / "freeze.json").exists(), "Stage already reserved or frozen")
    require(not (directory / BINDING).exists(), "Stage binding already exists")
    parent = None
    previous_hash = None
    if stage == "revised":
        previous = revision_feedback(root, construction, release=release)
        previous_path = root / FOLDER / f"{construction}_initial" / "feedback_round.json"
        previous_hash = sha256(previous_path)
        require(_same(read_json(_path(directory, REVISION_FEEDBACK)), previous) and
                sha256(directory / REVISION_FEEDBACK) == previous_hash, "Revision must bind the complete initial feedback round")
        require(revision is not None, "Revision description required")
        lifecycle._revision(revision)
        parent = f"candidates/{construction}_initial/freeze.json"
    else:
        require(revision is None and not (directory / REVISION_FEEDBACK).exists(), "Initial stage cannot consume revision feedback")
    request = {"schema_version": 1, **binding, "construction": construction, "stage": stage,
               "candidate": relative, "seeds": list(SEEDS), "conditional_feedback": enabled,
               "initial_feedback_sha256": previous_hash, "revision": revision}
    folder.parent.mkdir(exist_ok=True)
    folder.mkdir()  # Exclusive reservation; partial failures remain visible, never resumed.
    execution._write(folder / "freeze_request.json", request)
    execution._write(directory / BINDING, request)
    frozen = lifecycle.freeze_candidate(root, relative, parent_receipt=parent, revision=revision)
    record = {"request_sha256": sha256(folder / "freeze_request.json"),
              "candidate_freeze_sha256": sha256(directory / "freeze.json"), "route": frozen["route"]}
    execution._write(folder / "frozen.json", record)
    return record


def _frozen_stage(root, contract, policy, binding, construction, stage):
    slot = _slot(construction, stage)
    directory, relative, enabled = _candidate_preflight(root, contract, policy, slot, binding)
    folder = _path(root, f"{FOLDER}/{slot}", file=False)
    request, frozen = read_json(_path(folder, "freeze_request.json")), read_json(_path(folder, "frozen.json"))
    require(all(request[key] == value for key, value in binding.items()), "Stage belongs to a different release")
    require(request["construction"] == construction and request["stage"] == stage and request["candidate"] == relative and
            request["seeds"] == list(SEEDS) and request["conditional_feedback"] is enabled, "Stage identity changed")
    require(_same(read_json(directory / BINDING), request), "Frozen stage binding changed")
    receipt = lifecycle.verify_candidate(root, relative)
    require(frozen["request_sha256"] == sha256(folder / "freeze_request.json") and
            frozen["candidate_freeze_sha256"] == sha256(directory / "freeze.json") and frozen["route"] == receipt["route"],
            "Stage freeze changed")
    return slot, directory, relative, folder, enabled, receipt


def _round(binding, slot, relative, folder, route, results):
    return {"schema_version": 1, **binding, "slot": slot, "candidate": relative, "seeds": list(SEEDS),
            "status": "all_slots_finished", "results": results,
            "result_sha256": {str(seed): sha256(folder / f"seed_{seed}_result.json") for seed in SEEDS},
            "monte_carlo_replication": "not_available_direct_table_reused" if route == "generated.csv"
                                       else "three_fixed_seed_outputs_no_calibrated_uncertainty",
            "aggregate_objective": None, "target_performance": "not_evaluated"}


def run_stage(bundle, construction, stage, *, release="F2_RELEASE.json", runtime=None):
    root, contract, policy, binding = _release(bundle, release)
    _inventory(root)
    slot, directory, relative, folder, enabled, frozen = _frozen_stage(root, contract, policy, binding, construction, stage)
    require(not (folder / "run_request.json").exists(), "Stage execution slots already consumed")
    for seed in SEEDS:
        run_id = f"{slot}_s{seed}"
        require(all(not _path(root, f"{name}/{run_id}", file=False).exists()
                    for name in ("executions", strict.FOLDER, conditional.FOLDER)), "Execution/feedback ID already exists")
    execution._write(folder / "run_request.json", {**binding, "slot": slot, "reserved_target_table_slots": 3,
                     "seeds": list(SEEDS), "limits": LIMITS, "candidate_freeze_sha256": sha256(directory / "freeze.json")})
    results = []
    for seed in SEEDS:
        run_id = f"{slot}_s{seed}"
        result = {"seed": seed, "run_id": run_id, "execution_status": "not_completed", "feedback_status": "unavailable",
                  "execution_sha256": None, "strict_feedback_sha256": None, "conditional_feedback_sha256": None,
                  "strict_feedback": None, "conditional_feedback": None, "error": None}
        execution._write(folder / f"seed_{seed}_attempt.json", {"run_id": run_id, "seed": seed})
        try:
            execution.run_candidate(root, relative, run_id, seed=seed, runtime=runtime, **LIMITS)
            receipt = execution.verify_execution(root, run_id)
            require(receipt["candidate"] == relative and receipt["limits"]["seed"] == seed, "Wrong stage execution receipt")
            result["execution_status"] = receipt["status"]
            result["execution_sha256"] = sha256(root / "executions" / run_id / "execution.json")
            if receipt["status"] == "success":
                strict.collect_feedback(root, relative, run_id, run_id)
                result["strict_feedback"] = strict.verify_feedback(root, run_id, candidate=relative, run_id=run_id)
                result["strict_feedback_sha256"] = sha256(root / strict.FOLDER / run_id / "feedback.json")
                if enabled:
                    conditional.collect_feedback(root, relative, run_id, run_id, strict_feedback_id=run_id)
                    result["conditional_feedback"] = conditional.verify_feedback(
                        root, run_id, candidate=relative, run_id=run_id, strict_feedback_id=run_id)
                    result["conditional_feedback_sha256"] = sha256(root / conditional.FOLDER / run_id / "feedback.json")
                result["feedback_status"] = "complete"
        except Exception as error:
            # Preserve failure metadata; no retry/new seed/new candidate is invented.
            result["error"] = {"type": type(error).__name__, "message": str(error)}
        execution._write(folder / f"seed_{seed}_result.json", result)
        results.append(result)
    report = _round(binding, slot, relative, folder, frozen["route"], results)
    execution._write(folder / "feedback_round.json", report)
    return report


def revision_feedback(bundle, construction, *, release="F2_RELEASE.json"):
    """Return one complete initial round, including every failed seed; no averaging."""
    root, contract, policy, binding = _release(bundle, release)
    _inventory(root)
    slot, directory, relative, folder, enabled, frozen = _frozen_stage(root, contract, policy, binding, construction, "initial")
    expected_files = {"freeze_request.json", "frozen.json", "run_request.json", "feedback_round.json"} | {
        f"seed_{seed}_{kind}.json" for seed in SEEDS for kind in ("attempt", "result")}
    require({path.name for path in folder.iterdir()} == expected_files, "Initial stage artifact set changed or incomplete")
    require(_same(read_json(folder / "run_request.json"), {**binding, "slot": slot, "reserved_target_table_slots": 3,
                  "seeds": list(SEEDS), "limits": LIMITS, "candidate_freeze_sha256": sha256(directory / "freeze.json")}),
            "Initial stage reservation changed")
    report = read_json(_path(folder, "feedback_round.json"))
    require(report["slot"] == slot and report["candidate"] == relative and report["status"] == "all_slots_finished" and
            _same(report["seeds"], list(SEEDS)) and all(report[key] == value for key, value in binding.items()),
            "Initial feedback round identity changed")
    require(len(report["results"]) == len(SEEDS), "Initial feedback must include all three seed results")
    for seed, result in zip(SEEDS, report["results"]):
        require(result["seed"] == seed and result["run_id"] == f"{slot}_s{seed}", "Initial seed result changed")
        require(_same(read_json(folder / f"seed_{seed}_attempt.json"), {"run_id": result["run_id"], "seed": seed}),
                "Initial seed attempt changed")
        require(report["result_sha256"][str(seed)] == sha256(folder / f"seed_{seed}_result.json") and
                _same(result, read_json(folder / f"seed_{seed}_result.json")), "Initial feedback result changed")
        run_id = result["run_id"]
        if result["execution_sha256"] is not None:
            receipt = execution.verify_execution(root, run_id)
            require(sha256(root / "executions" / run_id / "execution.json") == result["execution_sha256"] and
                    receipt["candidate"] == relative and receipt["limits"]["seed"] == seed and
                    receipt["status"] == result["execution_status"], "Initial execution changed")
        for module, key in ((strict, "strict_feedback"), (conditional, "conditional_feedback")):
            if result[key] is not None:
                args = {"candidate": relative, "run_id": run_id}
                if module is conditional:
                    require(enabled, "Unapproved conditional feedback")
                    args["strict_feedback_id"] = run_id
                verified = module.verify_feedback(root, run_id, **args)
                require(_same(verified, result[key]) and sha256(root / module.FOLDER / run_id / "feedback.json") ==
                        result[key + "_sha256"], "Initial feedback changed")
    require(_same(report, _round(binding, slot, relative, folder, frozen["route"], report["results"])),
            "Initial feedback summary changed")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("freeze-stage", "run-stage", "revision-feedback"))
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--release", default="F2_RELEASE.json")
    parser.add_argument("--construction", required=True, choices=CONSTRUCTIONS)
    parser.add_argument("--stage", choices=STAGES, default="initial")
    parser.add_argument("--revision-json")
    parser.add_argument("--runtime-json")
    args = parser.parse_args(argv)
    try:
        if args.action == "freeze-stage":
            result = freeze_stage(args.bundle, args.construction, args.stage, release=args.release,
                                  revision=read_json(args.revision_json) if args.revision_json else None)
        elif args.action == "run-stage":
            result = run_stage(args.bundle, args.construction, args.stage, release=args.release,
                               runtime=read_json(args.runtime_json) if args.runtime_json else None)
        else:
            result = revision_feedback(args.bundle, args.construction, release=args.release)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(json.dumps({"status": "error", "type": type(error).__name__, "message": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
