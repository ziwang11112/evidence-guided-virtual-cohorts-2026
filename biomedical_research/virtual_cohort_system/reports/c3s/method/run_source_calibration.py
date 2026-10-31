"""Case-local bounded source-only calibration; never import submitted programs.

Reuse calibration._search and calibration_budget, but dispatch whole-cohort
trials through the existing WSL/bubblewrap source-context bridge. No resume.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import math
from pathlib import Path
import sys
import time

# Only trusted infrastructure is imported. Candidate paths never enter sys.path.
PROJECT = Path(__file__).resolve().parents[3]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))
from cohort_harness import calibration, calibration_budget as budget, execution, lifecycle
from cohort_harness.contracts import exact_keys, require, text
from cohort_harness.lifecycle import _bundle, _path, read_json, sha256

BRIDGE_PATH = PROJECT / "work/autonomous_research_cycle2_2026-10-31/method/run_source_contexts.py"
_loader = importlib.util.spec_from_file_location("c3s_trusted_source_bridge", BRIDGE_PATH)
bridge = importlib.util.module_from_spec(_loader)
_loader.loader.exec_module(bridge)
DIR = "source_calibration"
KIND = "bounded_whole_cohort_source_calibration"
SCOPE = "source_fit_only_no_target_validation"
_digest = calibration._digest
_finite = calibration._finite


def _engines():
    return {"adapter": sha256(__file__), "calibration": sha256(calibration.__file__),
            "calibration_budget": sha256(budget.__file__), **bridge._engines()}


def _validate(root, directory, plan, criteria):
    frozen, spec, contexts = bridge._read_plan(root, directory)
    require(not (root / "observed.csv").exists(), "Observed input is forbidden")
    require(not (directory / "calibration_trial.json").exists(), "Numerical trials cannot parent sessions")
    require(len(contexts) == 2 and all(c[1]["n_rows"] == 6000 for c in contexts),
            "Exactly two source contexts of 6000 rows are required")
    exact_keys(plan, {"schema_version", "parameters", "constraints", "fit_seeds", "replay_seeds",
                      "optimizer", "execution", "noncomputable"}, where="calibration plan")
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1, "Invalid plan version")
    require(plan["noncomputable"] == "infeasible", "Undefined checks must be infeasible")
    require(plan["fit_seeds"] == [19101] and plan["replay_seeds"] == [19111, 19123], "Seed schedule is fixed")
    exact_keys(plan["execution"], {"timeout_seconds", "memory_mb", "output_bytes", "log_bytes"}, where="execution limits")
    for seed in plan["fit_seeds"] + plan["replay_seeds"]:
        execution._limits(**plan["execution"], seed=seed)
    require(isinstance(plan["parameters"], list) and 1 <= len(plan["parameters"]) <= 32, "Scalar parameters required")
    names = []
    for parameter in plan["parameters"]:
        exact_keys(parameter, {"name", "lower", "upper", "step"}, where="calibrated scalar")
        name = parameter["name"]
        text(name, "parameter name")
        require(name in spec["parameters"] and name not in {"contexts", "active_context"}, "Unknown or structural parameter")
        lo, hi, step = (parameter[k] for k in ("lower", "upper", "step"))
        require(all(_finite(v) for v in (lo, hi, step, spec["parameters"][name])), "Top-level finite scalars required")
        require(lo < hi and math.isfinite(hi-lo) and 0 < step <= hi-lo and lo <= spec["parameters"][name] <= hi,
                "Invalid parameter bounds/step")
        names.append(name)
    require(len(names) == len(set(names)), "Duplicate parameter")
    opt = plan["optimizer"]
    exact_keys(opt, {"method", "max_trials", "shrink", "min_step_fraction", "target_loss"}, where="optimizer")
    require(opt["method"] == "bounded_coordinate_search", "Unsupported optimizer")
    calibration._integer(opt["max_trials"], 1, 40, "trial cap inclusive of baseline")
    require(_finite(opt["shrink"]) and 0 < opt["shrink"] < 1, "Invalid step shrink")
    require(_finite(opt["min_step_fraction"]) and 0 < opt["min_step_fraction"] <= 1, "Invalid minimum step")
    require(all(opt["min_step_fraction"] * (p["upper"]-p["lower"]) > 0 for p in plan["parameters"]),
            "Minimum step underflows")
    require(_finite(opt["target_loss"]) and opt["target_loss"] >= 0, "Invalid stopping loss")
    checks = {(c[0]["id"], check["id"]): check for c in contexts for check in c[2]["checks"]}
    require(len(checks) == 20, "Exactly 20 fixed source checks are required")
    require(isinstance(plan["constraints"], list), "Constraints must be a list")
    pairs = []
    for item in plan["constraints"]:
        exact_keys(item, {"context_id", "check_id", "scale", "scale_reason"}, where="loss constraint")
        text(item["context_id"], "context ID")
        text(item["check_id"], "check ID")
        text(item["scale_reason"], "Agent-authored scale rationale")
        require(_finite(item["scale"]) and item["scale"] > 0, "Positive explicit scale required")
        pairs.append((item["context_id"], item["check_id"]))
    require(len(pairs) == len(set(pairs)) and set(pairs) == set(checks), "Every source check must appear exactly once")
    exact_keys(criteria, {"schema_version", "scope", "parameter_roles", "check_weights", "scientific_requirements"},
               where="source criteria")
    require(type(criteria["schema_version"]) is int and criteria["schema_version"] == 1 and
            criteria["scope"] == "source_only", "Invalid source criteria identity")
    require(isinstance(criteria["parameter_roles"], list), "Parameter role declarations required")
    roles = {}
    for item in criteria["parameter_roles"]:
        exact_keys(item, {"name", "role", "rationale"}, where="parameter role")
        text(item["name"], "parameter role name")
        text(item["rationale"], "parameter rationale")
        require(item["name"] not in roles and item["role"] in {"source_parameter", "covariance", "context", "domain"},
                "Duplicate or unsupported parameter role")
        roles[item["name"]] = item["role"]
    require(set(roles) == set(names), "Parameter roles must match optimized parameters")
    require(isinstance(criteria["check_weights"], list), "Check weights required")
    weights = {}
    for item in criteria["check_weights"]:
        exact_keys(item, {"context_id", "check_id", "weight", "weight_reason"}, where="check weight")
        text(item["context_id"], "weight context")
        text(item["check_id"], "weight check")
        text(item["weight_reason"], "Agent-authored weight rationale")
        key = (item["context_id"], item["check_id"])
        require(key not in weights and _finite(item["weight"]) and item["weight"] > 0, "Invalid/duplicate weight")
        weights[key] = item["weight"]
    require(set(weights) == set(checks) and _finite(sum(weights.values())), "All checks need finite total positive weight")
    require(isinstance(criteria["scientific_requirements"], list) and criteria["scientific_requirements"],
            "Predeclared scientific review requirements required")
    for value in criteria["scientific_requirements"]:
        text(value, "scientific requirement")
    return frozen, spec, contexts


def _reservation(plan):
    # Reserve baseline AND selected replay even when they will be the same trial.
    executions = 2 * plan["optimizer"]["max_trials"] + 8
    return {"sessions": 1, "trials": plan["optimizer"]["max_trials"], "executions": executions,
            "reserved_seconds": executions * plan["execution"]["timeout_seconds"]}


def _binding(root, directory, relative, plan, criteria):
    return {"candidate": relative, "parent_freeze_sha256": sha256(directory / "freeze.json"),
            "task_sha256": sha256(root / "task.json"), "plan_sha256": _digest(plan),
            "criteria_sha256": _digest(criteria), "adapter_sha256": sha256(__file__),
            "engines_sha256": _digest(_engines()), "runtime_sha256": _digest(execution.DEFAULT_RUNTIME)}


def validate_calibration(bundle, candidate, plan, criteria):
    root = _bundle(bundle)
    directory, relative = bridge._candidate_path(root, candidate)
    _, _, contexts = _validate(root, directory, plan, criteria)
    return {"status": "validated_no_execution", "binding": _binding(root, directory, relative, plan, criteria),
            "reservation": _reservation(plan), "contexts": [c[0]["id"] for c in contexts], "checks": 20,
            "required_restricted_authorizations": sorted(p["name"] for p in criteria["parameter_roles"]
                                                          if p["role"] != "source_parameter")}


def _release(release, session_id, validation):
    exact_keys(release, {"schema_version", "kind", "decision", "session_id", "binding",
                         "authorized_restricted_parameters", "reason"}, where="root release")
    require(type(release["schema_version"]) is int and release["schema_version"] == 1 and
            release["kind"] == "root_source_calibration_release" and release["decision"] == "release",
            "Explicit root execution release required")
    require(release["session_id"] == session_id and release["binding"] == validation["binding"],
            "Root release input/session binding differs")
    require(release["authorized_restricted_parameters"] == validation["required_restricted_authorizations"],
            "Root must explicitly authorize every restricted scalar")
    text(release["reason"], "root release reason")


def _trial_spec(spec, values, binding, index):
    changed = {name: value for name, value in values.items()
               if bridge._canonical(value) != bridge._canonical(spec["parameters"][name])}
    # Existing helper annotates derivation only; evidence/assumptions stay fixed.
    return calibration._spec(spec, changed, binding, index)


def _trial_note(values, binding, index):
    note = calibration._trial_note(values, binding, index)
    if index == 0:
        note["value_origin"] = "unchanged_baseline"
    return note


def _materialize(root, directory, frozen, spec, values, child, binding, index):
    child.mkdir(parents=True)
    execution._write(child / "task.json", read_json(root / "task.json"))
    execution._write(child / "registry.json", {"artifacts": read_json(root / "registry.json")["artifacts"]
                                             [:frozen["registry_snapshot"]["artifact_count"]]})
    for name in frozen["commitments"]:
        if name.startswith("sources/"):
            output = child / name
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(_path(root, name).read_bytes())
    copied = child / "candidates/t"
    copied.mkdir(parents=True)
    prefix = frozen["candidate"] + "/"
    for name in frozen["candidate_files"]:
        relative = name.removeprefix(prefix)
        if relative == "model_spec.json":
            continue
        output = copied / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(_path(directory, relative).read_bytes())
    execution._write(copied / "model_spec.json", _trial_spec(spec, values, binding, index))
    execution._write(copied / "calibration_trial.json", _trial_note(values, binding, index))
    lifecycle.freeze_candidate(child, copied)


def _verify_trial(root, directory, frozen, spec, values, child, binding, index):
    actual = lifecycle.verify_candidate(child, "candidates/t")
    require(read_json(child / "task.json") == read_json(root / "task.json"), "Trial task changed")
    require(read_json(child / "registry.json") == {"artifacts": read_json(root / "registry.json")["artifacts"]
              [:frozen["registry_snapshot"]["artifact_count"]]}, "Trial registry changed")
    expected = {name.removeprefix(frozen["candidate"] + "/"): frozen["commitments"][name]
                for name in frozen["candidate_files"]}
    got = {name.removeprefix("candidates/t/"): actual["commitments"][name] for name in actual["candidate_files"]}
    require(set(got) == set(expected) | {"calibration_trial.json"}, "Trial candidate file set changed")
    for name, digest in expected.items():
        if name != "model_spec.json":
            require(got[name] == digest, "Fixed candidate science changed")
    require(bridge._canonical(read_json(child / "candidates/t/model_spec.json")) ==
            bridge._canonical(_trial_spec(spec, values, binding, index)), "Trial changed undeclared scalar or fixed structure")
    require(read_json(child / "candidates/t/calibration_trial.json") == _trial_note(values, binding, index),
            "Trial lineage/provenance changed")
    for name, digest in frozen["commitments"].items():
        if name.startswith("sources/"):
            require(sha256(_path(child, name)) == digest, "Trial source input changed")


def _score(report, plan, criteria, seed):
    weights = {(r["context_id"], r["check_id"]): r for r in criteria["check_weights"]}
    checks = {(c["id"], k["id"]): k for c in report["contexts"] if c["feedback"] is not None
              for k in c["feedback"]["checks"]}
    rows, terms = [], []
    total = math.fsum(w["weight"] for w in weights.values())
    for constraint in plan["constraints"]:
        key = (constraint["context_id"], constraint["check_id"])
        weight = weights[key]
        check = checks.get(key)
        row = {"seed": seed, **constraint, "weight": weight["weight"], "weight_reason": weight["weight_reason"],
               "status": "unavailable", "value": None, "reported_value": None, "scaled_error": None,
               "weighted_square": None}
        calculation = check.get("calculation") if check else None
        if check and check.get("status") != "not_computable" and isinstance(calculation, dict) and \
                _finite(calculation.get("value")) and _finite(check.get("reported_value")):
            error = (calculation["value"] - check["reported_value"]) / constraint["scale"]
            square = error * error
            term = (weight["weight"] / total) * square
            if math.isfinite(square) and math.isfinite(term):
                row.update(status="computed", value=calculation["value"], reported_value=check["reported_value"],
                           scaled_error=error, weighted_square=term)
                terms.append(term)
        if row["status"] != "computed":
            row["reason"] = (check.get("unavailable_reason") or "nonfinite statistic") if check else "execution failed"
        rows.append(row)
    feasible = len(terms) == len(plan["constraints"])
    return {"feasible": feasible, "loss": math.fsum(terms) if feasible else None, "constraints": rows}


def _evaluate(child, destination, seed, plan):
    bridge.prepare_source_contexts(child, "t", destination, seed, **plan["execution"])
    bridge.execute_source_contexts(child, destination, candidate="t")
    return bridge.verify_source_contexts(child, destination, candidate="t")


def _report(child, destination, seed, plan):
    report = bridge.verify_source_contexts(child, destination, candidate="t")
    require(read_json(destination / "intent.json")["limits"] == {**plan["execution"], "seed": seed},
            "Source replay seed or limits changed")
    return report


def _selection(session, records, chosen, reason, plan):
    return {"selected_trial": chosen, "stop_reason": reason,
            "fit_record_hashes": [sha256(session / ("t%04d" % r["index"]) / "trial.json") for r in records],
            "selected_freeze_sha256": None if chosen is None else sha256(session / ("t%04d" % chosen) / "bundle/candidates/t/freeze.json"),
            "replay_seeds": plan["replay_seeds"], "policy": "fit_only_selection_before_baseline_and_selected_replay"}


def _usage(plan, trial_count, replay_trials):
    executions = 2 * trial_count + 4 * replay_trials
    return {"sessions": 1, "trials": trial_count, "executions": executions,
            "reserved_seconds": executions * plan["execution"]["timeout_seconds"]}


def run_calibration(bundle, candidate, session_id, plan, criteria, release):
    root = _bundle(bundle)
    directory, relative = bridge._candidate_path(root, candidate)
    plan, criteria, release = map(copy.deepcopy, (plan, criteria, release))
    validation = validate_calibration(root, relative, plan, criteria)
    session_id = execution._name(session_id)
    _release(release, session_id, validation)
    frozen, spec, _ = _validate(root, directory, plan, criteria)
    session = _path(root, DIR + "/" + session_id, file=False)
    require(not session.exists(), "Session already exists; no resume or rerun")
    ledger = budget.get_budget(root)
    require(not any(r["binding"].get("parent_freeze_sha256") == validation["binding"]["parent_freeze_sha256"]
                    for r in ledger["sessions"].values()), "This frozen structure already has a session; rerun forbidden")
    binding = {**validation["binding"], "release_sha256": _digest(release)}
    reserved = budget.reserve_session(root, session_id, validation["reservation"], binding)
    # Recheck inside the pending reservation: a stale preflight cannot admit a
    # second same-parent session if another process finished before our reserve.
    require(sum(r["binding"].get("parent_freeze_sha256") == binding["parent_freeze_sha256"]
                for r in budget.get_budget(root)["sessions"].values()) == 1,
            "Concurrent same-parent reservation; retained pending, no dispatch")
    session.mkdir(parents=True)
    started = time.monotonic()
    execution._write(session / "plan.json", plan)
    execution._write(session / "criteria.json", criteria)
    execution._write(session / "release.json", release)
    intent = {"binding": binding, "engines": _engines(), "reservation": validation["reservation"],
              "budget_record": reserved, "runtime": execution.DEFAULT_RUNTIME}
    execution._write(session / "intent.json", intent)
    try:
        search = calibration._search(plan, spec["parameters"])
        proposal, records, chosen = next(search), [], None
        while True:
            index = len(records)
            folder = session / ("t%04d" % index)
            child = folder / "bundle"
            _materialize(root, directory, frozen, spec, proposal, child, binding, index)
            report = _evaluate(child, folder / "fit", 19101, plan)
            fit = _score(report, plan, criteria, 19101)
            record = {"index": index, "parameters": proposal, "fit": fit,
                      "fit_report_sha256": sha256(folder / "fit/report.json")}
            execution._write(folder / "trial.json", record)
            records.append(record)
            if fit["feasible"] and (chosen is None or fit["loss"] < records[chosen]["fit"]["loss"]):
                chosen = index
            lifecycle.verify_candidate(root, directory)
            require(_binding(root, directory, relative, plan, criteria) == validation["binding"], "Session input or engine changed")
            try:
                proposal = search.send(fit["loss"])
            except StopIteration as stop:
                reason = stop.value
                break
        execution._write(session / "selection.json", _selection(session, records, chosen, reason, plan))
        replay = {}
        for index in sorted({0} | ({chosen} if chosen is not None else set())):
            folder = session / ("t%04d" % index)
            replay[str(index)] = []
            for seed in plan["replay_seeds"]:
                destination = folder / ("v%d" % seed)
                report = _evaluate(folder / "bundle", destination, seed, plan)
                replay[str(index)].append({"seed": seed, "score": _score(report, plan, criteria, seed),
                                          "report_sha256": sha256(destination / "report.json")})
        result = {"schema_version": 1, "kind": KIND, "session_id": session_id, "scope": SCOPE,
                  "binding": binding, "engines": _engines(), "trials": records, "selected_trial": chosen,
                  "stop_reason": reason, "replay": replay, "baseline_replay_trial": 0, "selected_replay_trial": chosen,
                  "usage": _usage(plan, len(records), len(replay)), "elapsed_seconds": round(time.monotonic()-started, 6),
                  "status": "no_feasible_trial" if chosen is None else "fit_complete_requires_scientific_review",
                  "files": bridge._inventory(session)}
        execution._write(session / "result.json", result)
        verify_calibration(root, session_id, allow_pending=True)
        budget.finish_session(root, session_id, "completed", result["usage"])
        return verify_calibration(root, session_id)
    except BaseException as error:
        # The reservation remains pending and permanently charged. No retry is
        # dispatched. Normal failed execution receipts instead score infeasible.
        if not (session / "failure.json").exists():
            execution._write(session / "failure.json", {"status": "interrupted_no_resume", "type": type(error).__name__,
                "message": str(error), "elapsed_seconds": round(time.monotonic()-started, 6),
                "files_at_failure": bridge._inventory(session)})
        raise


def verify_calibration(bundle, session_id, *, allow_pending=False):
    root = _bundle(bundle)
    session_id = execution._name(session_id)
    session = _bundle(_path(root, DIR + "/" + session_id, file=False))
    require(not (session / "failure.json").exists(), "Session interrupted; inspect retained failure and pending budget; no resume")
    result, plan, criteria, intent, release = (read_json(_path(session, name + ".json"))
                                             for name in ("result", "plan", "criteria", "intent", "release"))
    directory, relative = bridge._candidate_path(root, result["binding"]["candidate"])
    validation = validate_calibration(root, relative, plan, criteria)
    _release(release, session_id, validation)
    binding = {**validation["binding"], "release_sha256": _digest(release)}
    require(result["binding"] == intent["binding"] == binding, "Session input bindings changed")
    require(result["engines"] == intent["engines"] == _engines(), "Session engines changed")
    require(intent["runtime"] == execution.DEFAULT_RUNTIME and intent["reservation"] == _reservation(plan), "Intent changed")
    expected_intent = {"binding", "engines", "reservation", "budget_record", "runtime"}
    exact_keys(intent, expected_intent, where="session intent")
    files = bridge._inventory(session)
    del files["result.json"]
    require(result["files"] == files, "Session artifact inventory/hash changed")
    calibration._verify_budget_record(budget.get_budget(root), session_id, intent, result, allow_pending)
    frozen, spec, _ = _validate(root, directory, plan, criteria)
    search, chosen, reason = calibration._search(plan, spec["parameters"]), None, None
    proposal = next(search)
    for index, record in enumerate(result["trials"]):
        require(reason is None and type(record["index"]) is int and record["index"] == index and
                bridge._canonical(record["parameters"]) == bridge._canonical(proposal), "Optimizer transcript changed")
        folder = session / ("t%04d" % index)
        child = _bundle(folder / "bundle")
        _verify_trial(root, directory, frozen, spec, proposal, child, binding, index)
        report = _report(child, folder / "fit", 19101, plan)
        fit = _score(report, plan, criteria, 19101)
        expected = {"index": index, "parameters": proposal, "fit": fit,
                    "fit_report_sha256": sha256(folder / "fit/report.json")}
        require(record == read_json(folder / "trial.json") == expected, "Trial score/receipt changed")
        if fit["feasible"] and (chosen is None or fit["loss"] < result["trials"][chosen]["fit"]["loss"]):
            chosen = index
        try:
            proposal = search.send(fit["loss"])
        except StopIteration as stop:
            reason = stop.value
    require(reason is not None and reason == result["stop_reason"] and result["selected_trial"] == chosen,
            "Incomplete search or wrong fit-only selection")
    require(read_json(session / "selection.json") == _selection(session, result["trials"], chosen, reason, plan),
            "Selection seal changed")
    replay = {}
    replay_trials = {0} | ({chosen} if chosen is not None else set())
    for index, _ in enumerate(result["trials"]):
        folder = session / ("t%04d" % index)
        expected_names = {"bundle", "fit", "trial.json"}
        if index in replay_trials:
            expected_names |= {"v%d" % s for s in plan["replay_seeds"]}
            replay[str(index)] = []
            for seed in plan["replay_seeds"]:
                destination = folder / ("v%d" % seed)
                report = _report(folder / "bundle", destination, seed, plan)
                replay[str(index)].append({"seed": seed, "score": _score(report, plan, criteria, seed),
                                          "report_sha256": sha256(destination / "report.json")})
        require({p.name for p in folder.iterdir()} == expected_names, "Unexpected/missing trial attempt")
    expected_names = {"intent.json", "plan.json", "criteria.json", "release.json", "selection.json", "result.json"} | \
                     {"t%04d" % i for i in range(len(result["trials"]))}
    require({p.name for p in session.iterdir()} == expected_names, "Unexpected/missing session artifact")
    require(_finite(result["elapsed_seconds"]) and result["elapsed_seconds"] >= 0, "Invalid recorded elapsed time")
    expected_result = {"schema_version": 1, "kind": KIND, "session_id": session_id, "scope": SCOPE,
        "binding": binding, "engines": _engines(), "trials": result["trials"], "selected_trial": chosen,
        "stop_reason": reason, "replay": replay, "baseline_replay_trial": 0, "selected_replay_trial": chosen,
        "usage": _usage(plan, len(result["trials"]), len(replay)), "elapsed_seconds": result["elapsed_seconds"],
        "status": "no_feasible_trial" if chosen is None else "fit_complete_requires_scientific_review", "files": files}
    require(result == expected_result, "Result/replay/usage differs from verified transcript")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("validate", "run", "verify"))
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--candidate", default="initial")
    parser.add_argument("--plan")
    parser.add_argument("--criteria")
    parser.add_argument("--session")
    parser.add_argument("--release")
    args = parser.parse_args(argv)
    if args.action == "verify":
        require(args.session is not None, "--session required")
        result = verify_calibration(args.bundle, args.session)
    else:
        require(args.plan is not None and args.criteria is not None, "--plan and --criteria required")
        plan, criteria = read_json(args.plan), read_json(args.criteria)
        if args.action == "validate":
            result = validate_calibration(args.bundle, args.candidate, plan, criteria)
        else:
            require(args.session is not None and args.release is not None, "--session and separate root --release required")
            result = run_calibration(args.bundle, args.candidate, args.session, plan, criteria, read_json(args.release))
    import json
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
