"""Bounded source-only calibration of an immutable scientific structure.

This is numerical search, not an Agent or a target-validity estimator. Each trial
is a separate frozen bundle. Generated Python is executed only by source_replay_v2.
Interrupted sessions are inspectable but deliberately cannot resume in this version.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path

from . import calibration_budget as budget
from . import execution, lifecycle, source_replay_v2 as replay
from .contracts import exact_keys, require, text
from .lifecycle import _bundle, _candidate, _files, _path, read_json, sha256, verify_candidate

DIR = "cal"


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def _integer(value, minimum, maximum, label):
    require(type(value) is int and minimum <= value <= maximum, "Invalid " + label)


def _engines():
    return {"calibration": sha256(__file__), "calibration_budget": sha256(budget.__file__),
            **replay._engines()}


def _validate(root, candidate, plan):
    exact_keys(plan, {"schema_version", "parameters", "constraints", "fit_seeds", "replay_seeds",
                      "optimizer", "execution", "noncomputable"}, where="calibration plan")
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1, "Invalid calibration version")
    require(plan["noncomputable"] == "infeasible", "Undefined constraints must make a trial infeasible")
    exact_keys(plan["execution"], {"timeout_seconds", "memory_mb", "output_bytes", "log_bytes"},
               where="calibration execution")
    for name in ("fit_seeds", "replay_seeds"):
        seeds = plan[name]
        require(isinstance(seeds, list) and 1 <= len(seeds) <= 16, "Invalid seed schedule")
        for seed in seeds:
            execution._limits(**plan["execution"], seed=seed)
        require(len(seeds) == len(set(seeds)), "Duplicate simulation seeds")
    require(not set(plan["fit_seeds"]) & set(plan["replay_seeds"]), "Fit and replay seeds must be disjoint")
    frozen, contexts, evidence, _ = replay._plan(root, candidate, plan["execution"]["output_bytes"])
    require("source_check_report.json" not in replay.legacy._candidate_bindings(frozen),
            "Cached source-check reports need a fresh scientific submission before calibration")
    spec = read_json(candidate / "model_spec.json")
    require(isinstance(plan["parameters"], list) and 1 <= len(plan["parameters"]) <= 32, "Allowed parameters required")
    names = []
    for parameter in plan["parameters"]:
        exact_keys(parameter, {"name", "lower", "upper", "step"}, where="calibrated scalar parameter")
        name = parameter["name"]
        text(name, "parameter name")
        require(name in spec["parameters"], "Unknown calibrated parameter")
        lo, hi, step = (parameter[k] for k in ("lower", "upper", "step"))
        require(all(_finite(v) for v in (lo, hi, step, spec["parameters"][name])), "Finite scalar parameters required")
        require(lo < hi and math.isfinite(hi-lo) and 0 < step <= hi-lo and
                lo <= spec["parameters"][name] <= hi, "Invalid parameter bounds/step")
        names.append(name)
    require(len(names) == len(set(names)), "Duplicate calibrated parameter")
    opt = plan["optimizer"]
    exact_keys(opt, {"method", "max_trials", "shrink", "min_step_fraction", "target_loss"}, where="optimizer")
    require(opt["method"] == "bounded_coordinate_search", "Unsupported optimizer")
    _integer(opt["max_trials"], 1, 10000, "trial budget")
    require(_finite(opt["shrink"]) and 0 < opt["shrink"] < 1, "Invalid step shrink")
    require(_finite(opt["min_step_fraction"]) and 0 < opt["min_step_fraction"] <= 1, "Invalid minimum step")
    require(all(opt["min_step_fraction"] * (p["upper"]-p["lower"]) > 0 for p in plan["parameters"]),
            "Minimum step threshold underflows; rescale the parameter")
    require(_finite(opt["target_loss"]) and opt["target_loss"] >= 0, "Invalid stopping loss")
    expected = {(c[0]["id"], check["id"]) for c in contexts for check in c[0]["checks"]}
    require(isinstance(plan["constraints"], list) and bool(plan["constraints"]), "Fixed constraints required")
    selected = []
    for constraint in plan["constraints"]:
        exact_keys(constraint, {"context_id", "check_id", "scale", "scale_reason"}, where="loss constraint")
        text(constraint["context_id"], "constraint context")
        text(constraint["check_id"], "constraint check")
        text(constraint["scale_reason"], "loss scale reason")
        require(_finite(constraint["scale"]) and constraint["scale"] > 0, "Positive loss scale required")
        selected.append((constraint["context_id"], constraint["check_id"]))
    require(len(selected) == len(set(selected)) and set(selected) == expected,
            "All source checks must occur exactly once in the fixed objective")
    return frozen, contexts, evidence, spec


def _search(plan, parameters):
    """Deterministic ask/tell search; None means an infeasible evaluation."""
    names = [p["name"] for p in plan["parameters"]]
    bounds = [(p["lower"], p["upper"]) for p in plan["parameters"]]
    steps = [p["step"] for p in plan["parameters"]]
    best = {name: parameters[name] for name in names}
    best_loss = yield best.copy()
    best_loss = math.inf if best_loss is None else best_loss
    seen = {tuple(best.values())}
    count, rounds, opt = 1, 0, plan["optimizer"]
    while True:
        if best_loss <= opt["target_loss"]:
            return "target_loss"
        if count >= opt["max_trials"]:
            return "max_trials"
        if all(step <= opt["min_step_fraction"] * (hi-lo) for step, (lo, hi) in zip(steps, bounds)):
            return "minimum_step"
        if rounds >= opt["max_trials"]:
            return "max_rounds"
        rounds += 1
        improved = False
        for i, name in enumerate(names):
            anchor = best.copy()
            for sign in (1, -1):
                trial = anchor.copy()
                trial[name] = min(bounds[i][1], max(bounds[i][0], anchor[name] + sign*steps[i]))
                key = tuple(trial[n] for n in names)
                if key in seen:
                    continue
                seen.add(key)
                count += 1
                loss = yield trial
                if loss is not None and loss < best_loss:
                    best, best_loss, improved = trial, loss, True
                if best_loss <= opt["target_loss"]:
                    return "target_loss"
                if count >= opt["max_trials"]:
                    return "max_trials"
        if not improved:
            smaller = [step * opt["shrink"] for step in steps]
            if smaller == steps:
                return "numerical_step_limit"
            steps = smaller


def _spec(parent, values, binding, index):
    spec = copy.deepcopy(parent)
    for name, value in values.items():
        spec["parameters"][name] = value
        spec["parameter_provenance"][name]["derivation"] = (
            "Calibrated numerical trial %d under locked plan %s. Original derivation: %s" %
            (index, binding["plan_sha256"], parent["parameter_provenance"][name]["derivation"]))
    return spec


def _trial_note(values, binding, index):
    return {"schema_version": 1, "kind": "numerical_parameter_trial", "trial_index": index,
            "parent_binding": binding, "parameter_values": values,
            "value_origin": "calibrated_trial", "scope": "source_only_not_target_validated"}


def _materialize(root, candidate, frozen, child, spec, values, binding, index):
    child.mkdir(parents=True)
    execution._write(child / "task.json", read_json(root / "task.json"))
    execution._write(child / "registry.json", {"artifacts": read_json(root / "registry.json")["artifacts"]
                                             [:frozen["registry_snapshot"]["artifact_count"]]})
    for relative in frozen["commitments"]:
        if relative.startswith("sources/") or relative == "observed.csv":
            destination = child / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(_path(root, relative).read_bytes())
    copied = child / "candidates/t"
    copied.mkdir(parents=True)
    require("calibration_trial.json" not in replay.legacy._candidate_bindings(frozen),
            "Parent already contains a numerical trial sidecar; submit a scientific candidate instead")
    for relative in replay.legacy._candidate_bindings(frozen):
        if relative == "model_spec.json":
            continue
        destination = copied / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(_path(candidate, relative).read_bytes())
    execution._write(copied / "model_spec.json", _spec(spec, values, binding, index))
    execution._write(copied / "calibration_trial.json", _trial_note(values, binding, index))
    lifecycle.freeze_candidate(child, copied)


def _verify_trial(root, candidate, frozen, child, spec, values, binding, index):
    actual = verify_candidate(child, "candidates/t")
    require(read_json(child / "task.json") == read_json(root / "task.json"), "Trial task changed")
    require(read_json(child / "registry.json") == {"artifacts": read_json(root / "registry.json")["artifacts"]
              [:frozen["registry_snapshot"]["artifact_count"]]}, "Trial registry changed")
    for relative, digest in frozen["commitments"].items():
        if relative.startswith("sources/") or relative == "observed.csv":
            require(sha256(_path(child, relative)) == digest, "Trial source/observed input changed")
    expected = replay.legacy._candidate_bindings(frozen)
    actual_files = replay.legacy._candidate_bindings(actual)
    require(set(actual_files) == set(expected) | {"calibration_trial.json"}, "Trial candidate files changed")
    for name, digest in expected.items():
        if name != "model_spec.json":
            require(actual_files[name] == digest, "Trial changed fixed scientific structure or evidence")
    directory = child / "candidates/t"
    require(read_json(directory / "model_spec.json") == _spec(spec, values, binding, index),
            "Trial changed a parameter or provenance outside the locked plan")
    require(read_json(directory / "calibration_trial.json") == _trial_note(values, binding, index),
            "Trial provenance differs from session")


def _score(reports, plan):
    details, squares = [], []
    for report in reports:
        checks = {(c["id"], k["id"]): k for c in report["contexts"] for k in c["checks"]}
        for constraint in plan["constraints"]:
            key = (constraint["context_id"], constraint["check_id"])
            check = checks.get(key)
            row = {"seed": report["limits"]["seed"], **constraint,
                   "status": "unavailable", "value": None, "reported_value": None, "scaled_error": None}
            if check and check.get("status") != "not_computable" and _finite(check.get("value")):
                error = (check["value"] - check["reported_value"]) / constraint["scale"]
                square = error * error
                if math.isfinite(square):
                    row.update(status="computed", value=check["value"], reported_value=check["reported_value"],
                               scaled_error=error)
                    squares.append(square)
            if row["status"] != "computed":
                row["reason"] = check.get("computation_error", "missing or nonfinite statistic") if check else "execution failed"
            details.append(row)
    feasible = len(squares) == len(reports)*len(plan["constraints"]) and bool(reports)
    loss = math.fsum(s / len(squares) for s in squares) if feasible else None
    return {"feasible": feasible, "loss": loss, "constraints": details}


def _reservation(plan, contexts):
    trials = plan["optimizer"]["max_trials"]
    executions = (trials * len(plan["fit_seeds"]) + len(plan["replay_seeds"])) * len(contexts)
    return {"sessions": 1, "trials": trials, "executions": executions,
            "reserved_seconds": math.ceil(executions * plan["execution"]["timeout_seconds"])}


def _binding(root, candidate, relative, plan):
    return {"candidate": relative, "parent_freeze_sha256": sha256(candidate / "freeze.json"),
            "task_sha256": sha256(root / "task.json"), "plan_sha256": _digest(plan),
            "engines_sha256": _digest(_engines())}


def run_calibration(bundle, candidate, session_id, plan, *, runtime=None):
    """Run a pre-reserved, bounded session. Unexpected exceptions leave it pending.

    The caller must first create the fixed bundle-level budget. No target outcome
    input is accepted. All copied candidate/source artifacts are already exposed.
    """
    root = _bundle(bundle)
    candidate, relative = _candidate(root, candidate)
    plan = copy.deepcopy(plan)
    frozen, contexts, _, spec = _validate(root, candidate, plan)
    runtime = execution._runtime(runtime)
    require("calibration_trial.json" not in replay.legacy._candidate_bindings(frozen), "Numerical trials cannot parent sessions")
    session_id = execution._name(session_id)
    session = _path(root, DIR + "/" + session_id, file=False)
    require(not session.exists(), "Calibration session already exists")
    binding, engines = _binding(root, candidate, relative, plan), _engines()
    reservation = _reservation(plan, contexts)
    reserved = budget.reserve_session(root, session_id, reservation, binding)
    session.mkdir(parents=True)
    execution._write(session / "plan.json", plan)
    execution._write(session / "intent.json", {"binding": binding, "engines": engines,
        "reservation": reservation, "budget_record": reserved, "runtime_config_sha256": _digest(runtime)})
    search = _search(plan, spec["parameters"])
    proposal, records, chosen = next(search), [], None
    while True:
        index = len(records)
        child = session / ("t%04d" % index)
        _materialize(root, candidate, frozen, child, spec, proposal, binding, index)
        reports = []
        for i, seed in enumerate(plan["fit_seeds"]):
            reports.append(replay.run_source_replay(child, "candidates/t", "f%d" % i, seed,
                                                   runtime=runtime, **plan["execution"]))
        score = _score(reports, plan)
        record = {"index": index, "parameters": proposal, "fit": score}
        execution._write(child / "trial.json", record)
        records.append(record)
        if score["feasible"] and (chosen is None or score["loss"] < records[chosen]["fit"]["loss"]):
            chosen = index
        verify_candidate(root, candidate)
        require(_binding(root, candidate, relative, plan) == binding, "Session inputs or engines changed")
        try:
            proposal = search.send(score["loss"])
        except StopIteration as stop:
            stop_reason = stop.value
            break
    check = None
    execution._write(session / "selection.json", {"selected_trial": chosen, "stop_reason": stop_reason,
        "fit_record_hashes": [sha256(session / ("t%04d" % r["index"]) / "trial.json") for r in records],
        "replay_seeds": plan["replay_seeds"], "policy": "fit_only_selection_before_replay"})
    if chosen is not None:
        child = session / ("t%04d" % chosen)
        checks = [replay.run_source_replay(child, "candidates/t", "v%d" % i, seed,
                    runtime=runtime, **plan["execution"]) for i, seed in enumerate(plan["replay_seeds"])]
        check = _score(checks, plan)
    executions = (len(records)*len(plan["fit_seeds"]) + (len(plan["replay_seeds"]) if chosen is not None else 0))*len(contexts)
    usage = {"sessions": 1, "trials": len(records), "executions": executions,
             "reserved_seconds": math.ceil(executions * plan["execution"]["timeout_seconds"])}
    result = {"schema_version": 1, "kind": "bounded_source_calibration", "session_id": session_id,
        "binding": binding, "engines": engines, "stop_reason": stop_reason,
        "status": "no_feasible_trial" if chosen is None else "fit_threshold_met" if
                  records[chosen]["fit"]["loss"] <= plan["optimizer"]["target_loss"] else "fit_threshold_not_met",
        "trials": records, "selected_trial": chosen, "replay": check, "usage": usage,
        "scope": "source_fit_only_no_target_validation",
        "files": {name: sha256(_path(session, name)) for name in _files(session)}}
    execution._write(session / "result.json", result)
    # Verify all receipts and the complete optimizer transcript before closing budget.
    verify_calibration(root, session_id, allow_pending=True)
    budget.finish_session(root, session_id, "completed", usage)
    return verify_calibration(root, session_id)


def verify_calibration(bundle, session_id, *, allow_pending=False):
    root = _bundle(bundle)
    session_id = execution._name(session_id)
    session = _path(root, DIR + "/" + session_id, file=False)
    result, plan, intent = (read_json(_path(session, f)) for f in ("result.json", "plan.json", "intent.json"))
    exact_keys(intent, {"binding", "engines", "reservation", "budget_record", "runtime_config_sha256"},
               where="calibration intent")
    require(intent["runtime_config_sha256"] == _digest(execution.DEFAULT_RUNTIME), "Runtime declaration changed")
    exact_keys(result, {"schema_version", "kind", "session_id", "binding", "engines", "stop_reason", "status",
                       "trials", "selected_trial", "replay", "usage", "scope", "files"}, where="calibration result")
    require(type(result["schema_version"]) is int and result["schema_version"] == 1 and result["kind"] == "bounded_source_calibration" and
            result["session_id"] == session_id and result["scope"] == "source_fit_only_no_target_validation",
            "Invalid calibration identity/scope")
    candidate, relative = _candidate(root, result["binding"]["candidate"])
    frozen, contexts, _, spec = _validate(root, candidate, plan)
    binding = _binding(root, candidate, relative, plan)
    require(result["binding"] == binding == intent["binding"], "Calibration input binding changed")
    require(result["engines"] == _engines() == intent["engines"], "Calibration engine changed")
    require(intent["reservation"] == _reservation(plan, contexts), "Reservation disagrees with plan")
    require(sorted(result["files"]) == sorted(n for n in _files(session) if n != "result.json"), "Session inventory changed")
    for name, digest in result["files"].items():
        require(sha256(_path(session, name)) == digest, "Session artifact hash changed")
    # Budget has its own task-bound immutable event chain. Its result API is checked below.
    ledger = budget.get_budget(root)
    _verify_budget_record(ledger, session_id, intent, result, allow_pending)
    search, chosen, reason = _search(plan, spec["parameters"]), None, None
    proposal = next(search)
    for index, record in enumerate(result["trials"]):
        require(reason is None, "Trials continued after the stopping rule")
        require(type(record["index"]) is int and record["index"] == index and
                isinstance(record["parameters"], dict) and all(_finite(v) for v in record["parameters"].values()) and
                record["parameters"] == proposal, "Optimizer transcript differs")
        child = _bundle(session / ("t%04d" % index))
        _verify_trial(root, candidate, frozen, child, spec, proposal, binding, index)
        require(read_json(child / "trial.json") == record, "Trial record changed")
        expected_ids = {"f%d" % i for i in range(len(plan["fit_seeds"]))}
        if index == result["selected_trial"]:
            expected_ids |= {"v%d" % i for i in range(len(plan["replay_seeds"]))}
        replay_dir = _path(child, replay.REPLAY_DIR, file=False)
        require({p.name for p in replay_dir.iterdir() if p.is_dir()} == expected_ids and
                all(p.is_dir() for p in replay_dir.iterdir()), "Unexpected or missing replay attempt")
        reports = [replay.verify_source_replay(child, "f%d" % i, candidate="candidates/t")
                   for i in range(len(plan["fit_seeds"]))]
        for report, seed in zip(reports, plan["fit_seeds"]):
            require(report["limits"] == {**plan["execution"], "seed": seed}, "Fit seed/limits changed")
        score = _score(reports, plan)
        require(record == {"index": index, "parameters": proposal, "fit": score}, "Stored loss differs from source statistics")
        if score["feasible"] and (chosen is None or score["loss"] < result["trials"][chosen]["fit"]["loss"]):
            chosen = index
        try:
            proposal = search.send(score["loss"])
        except StopIteration as stop:
            reason = stop.value
    require(reason is not None and result["stop_reason"] == reason, "Incomplete or altered search transcript")
    require((result["selected_trial"] is None or type(result["selected_trial"]) is int) and
            result["selected_trial"] == chosen, "Selected trial is not earliest best fit")
    require(read_json(session / "selection.json") == {"selected_trial": chosen, "stop_reason": reason,
        "fit_record_hashes": [sha256(session / ("t%04d" % r["index"]) / "trial.json") for r in result["trials"]],
        "replay_seeds": plan["replay_seeds"], "policy": "fit_only_selection_before_replay"},
        "Pre-replay selection seal differs from fitted trials")
    check = None
    if chosen is not None:
        child = session / ("t%04d" % chosen)
        reports = [replay.verify_source_replay(child, "v%d" % i, candidate="candidates/t")
                   for i in range(len(plan["replay_seeds"]))]
        for report, seed in zip(reports, plan["replay_seeds"]):
            require(report["limits"] == {**plan["execution"], "seed": seed}, "Replay seed/limits changed")
        check = _score(reports, plan)
    require(result["replay"] == check, "Independent-seed diagnostics changed")
    expected_status = "no_feasible_trial" if chosen is None else "fit_threshold_met" if (
        result["trials"][chosen]["fit"]["loss"] <= plan["optimizer"]["target_loss"]) else "fit_threshold_not_met"
    require(result["status"] == expected_status, "Calibration status differs from fit")
    executions = (len(result["trials"])*len(plan["fit_seeds"]) + (len(plan["replay_seeds"]) if chosen is not None else 0))*len(contexts)
    require(result["usage"] == {"sessions": 1, "trials": len(result["trials"]), "executions": executions,
            "reserved_seconds": math.ceil(executions*plan["execution"]["timeout_seconds"])}, "Session usage changed")
    return result


def _verify_budget_record(ledger, session_id, intent, result, allow_pending):
    """Bind the durable pre-dispatch reserve event, including its owner and hash."""
    require(session_id in ledger["sessions"], "Session has no global reservation")
    record = ledger["sessions"][session_id]
    require(record["reservation"] == intent["reservation"] and record["binding"] == intent["binding"],
            "Budget reservation differs from calibration")
    require(intent["budget_record"] == {"status": "pending", **{key: record[key] for key in
            ("reservation", "binding", "reservation_sha256", "owner")}}, "Pre-dispatch reservation receipt changed")
    require(record["status"] == "completed" or (allow_pending and record["status"] == "pending"),
            "Calibration budget is not completed")
    if record["status"] == "completed":
        require(record["usage"] == result["usage"], "Budget usage differs from verified trial count")
