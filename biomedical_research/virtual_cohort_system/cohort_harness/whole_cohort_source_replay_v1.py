"""Frozen whole-cohort source laws, executed only by the existing isolated backend.

The adapter compiles source task metadata, never scientific coefficients. Strict
semantic feedback and explicitly requested assumption-dependent projections are
separate artifacts. No parent execution or target table is an input.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import numpy as np

from . import contracts, execution, lifecycle, semantic_feedback_v1 as semantic
from . import source_checks, whole_cohort_feedback as feedback
from .contracts import exact_keys, require, string_list, text, validate_task
from .lifecycle import _bundle, _files, _path, freeze_candidate, read_json, read_table, sha256, verify_candidate

PLAN = "whole_cohort_source_replay_v1.json"
FOLDER = "whole_cohort_source_replays_v1"
_CORE = ("generator.py", "model_spec.json", "evidence.json", "decision.md")
_LIMITATIONS = [
    "Source-law sampling and transport are declared assumptions, not recovered measurements or target validation.",
    "Strict matched_declared semantics does not certify source authenticity, applicability or an exact population law.",
    "Assumed projections never replace unavailable strict diagnostics and have no acceptance threshold.",
    "Only the generator process is isolated; hashes bind retained artifacts and are not host-authentication signatures.",
    "This ledger counts adapter source executions, including failed or interrupted reservations; objective evaluations inside a generator require a separate controller audit.",
]


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _engine():
    modules = (contracts, execution, lifecycle, semantic, source_checks, feedback)
    return {**{Path(m.__file__).name: sha256(m.__file__) for m in modules},
            Path(__file__).name: sha256(__file__)}


def _refs(values, known, where):
    string_list(values, where)
    require(set(values) <= known, "Unknown assumption in " + where)


def _protocol(plan):
    budget = plan["budget"]
    exact_keys(budget, {"max_evaluations", "max_rows_per_evaluation"}, where="source replay budget")
    for key in budget:
        require(type(budget[key]) is int and budget[key] > 0, "Source budget limits must be positive integers")
    schedule = plan["schedule"]
    require(isinstance(schedule, list) and bool(schedule), "A frozen source schedule is required")
    require(len(schedule) <= budget["max_evaluations"], "Scheduled source evaluations exceed budget")
    seen = set()
    for entry in schedule:
        exact_keys(entry, {"replay_id", "candidate", "context_id", "seed", "n_rows"}, where="source schedule entry")
        key = execution._name(entry["replay_id"]).casefold()
        require(key not in seen, "Duplicate scheduled replay ID")
        seen.add(key)
        execution._name(entry["context_id"])
        parts = lifecycle.safe_relative(entry["candidate"])
        require(len(parts) == 2 and parts[0] == "candidates", "Schedule candidate must be candidates/name")
        execution._name(parts[1])
        execution._limits(30, 1024, 20_000_000, 100_000, entry["seed"])
        require(type(entry["n_rows"]) is int and 0 < entry["n_rows"] <= budget["max_rows_per_evaluation"],
                "Scheduled source rows exceed budget")
    return {"budget": budget, "schedule": schedule}


def _bound(directory, value):
    exact_keys(value, {"path", "sha256"}, where="frozen context artifact")
    contracts._hash(value["sha256"])
    path = _path(directory, value["path"])
    require(sha256(path) == value["sha256"], "Source context artifact hash mismatch")
    return path


def _predictor_contract(check, task, spec, assumptions):
    exact_keys(check, {"kind", "column", "raw_column", "selection", "reference", "assumption_ids", "reason"},
               where="source predictor check")
    require(check["kind"] == "zscore", "Only explicit zscore predictor identities are implemented")
    columns = {c["name"]: c for c in task["columns"]}
    for field in ("column", "raw_column"):
        require(check[field] in columns and columns[check[field]]["kind"] in {"number", "integer"},
                "Predictor identity requires numeric task columns")
    require(check["column"] != check["raw_column"], "Standardized and raw columns must differ")
    require(columns[check["column"]]["unit"] == "1", "Standardized predictor must have unit 1")
    _refs(check["assumption_ids"], assumptions, "predictor assumptions")
    text(check["reason"], "predictor convention reason")
    reference = check["reference"]
    require(isinstance(reference, dict), "Predictor reference must be an object")
    if reference.get("mode") == "sample":
        exact_keys(reference, {"mode", "selection", "ddof"}, where="sample zscore reference")
        require(type(reference["ddof"]) is int and reference["ddof"] in {0, 1}, "ddof must be explicit 0 or 1")
        selections = [check["selection"], reference["selection"]]
    else:
        exact_keys(reference, {"mode", "mean_parameter", "sd_parameter"}, where="fixed zscore reference")
        require(reference["mode"] == "model_parameters", "Unknown zscore reference rule")
        for key in ("mean_parameter", "sd_parameter"):
            require(reference[key] in spec["parameters"], "Unknown zscore model parameter")
            contracts.number(spec["parameters"][reference[key]], "zscore model parameter")
        require(spec["parameters"][reference["sd_parameter"]] > 0, "Zscore reference SD must be positive")
        selections = [check["selection"]]
    for selection in selections:
        operator = {"kind": "mean", "column": check["raw_column"], "unit": columns[check["raw_column"]]["unit"],
                    "selection": selection, "missing_policy": "error"}
        semantic._signature(operator)
        semantic._task_operator(operator, columns)


def _semantic_preflight(directory, task, context):
    # The existing semantic engine needs canonical filenames. Only metadata is
    # staged here, never a table, generated code execution, or parent mutation.
    with tempfile.TemporaryDirectory(prefix="evc_src_preflight_") as temp:
        root = Path(temp)
        copied = root / "candidates/source"
        copied.mkdir(parents=True)
        execution._write(root / "task.json", task)
        for name in ("evidence.json", "model_spec.json"):
            (copied / name).write_bytes((directory / name).read_bytes())
        (copied / feedback.PLAN).write_bytes(_bound(directory, context["recipe"]).read_bytes())
        (copied / semantic.FILE).write_bytes(_bound(directory, context["semantics"]).read_bytes())
        return semantic.preflight(root, "source")


def _load_plan(root, directory, relative, *, frozen=True):
    commitment = verify_candidate(root, directory) if frozen else None
    if frozen:
        require(commitment["route"] == "generator.py", "Source replay requires a frozen generator program")
    else:
        lifecycle.validate_program(_path(directory, "generator.py"))
        require(not (directory / "generated.csv").exists(), "Source replay requires the program route")
    task = read_json(root / "task.json")
    validate_task(task)
    require(task["mode"] == "whole_cohort", "Source replay requires whole_cohort mode")
    require(not _path(root, "observed.csv", file=False).exists(), "Whole-cohort source replay forbids observed.csv")
    plan = read_json(_path(directory, PLAN))
    exact_keys(plan, {"schema_version", "budget", "schedule", "contexts"}, where=PLAN)
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1, "Invalid whole-cohort source replay version")
    protocol = _protocol(plan)
    spec = read_json(directory / "model_spec.json")
    known = {a["id"] for a in spec["assumptions"]}
    require(isinstance(plan["contexts"], list) and bool(plan["contexts"]), "Source contexts must be nonempty")
    contexts, ids = {}, set()
    for context in plan["contexts"]:
        exact_keys(context, {"id", "population", "n_rows", "columns", "reason", "assumption_ids", "recipe", "semantics",
                             "predictor_checks", "assumed_diagnostics"}, where="whole-cohort source context")
        key = execution._name(context["id"])
        require(key.casefold() not in ids, "Duplicate source context ID")
        ids.add(key.casefold())
        text(context["population"], "source population")
        text(context["reason"], "source context reason")
        _refs(context["assumption_ids"], known, "context assumptions")
        require(type(context["n_rows"]) is int and 0 < context["n_rows"] <= protocol["budget"]["max_rows_per_evaluation"],
                "Source context rows exceed budget")
        child_task = copy.deepcopy(task)
        child_task.update(population=context["population"], n_rows=context["n_rows"], columns=copy.deepcopy(context["columns"]))
        validate_task(child_task)
        recipe = read_json(_bound(directory, context["recipe"]))
        require(set(context["assumption_ids"]) <= set(recipe["assumption_ids"]),
                "Source context assumptions must propagate into the strict recipe")
        require(isinstance(context["predictor_checks"], list), "predictor_checks must be a list")
        for check in context["predictor_checks"]:
            _predictor_contract(check, child_task, spec, known)
            require(set(check["assumption_ids"]) <= set(recipe["assumption_ids"]),
                    "Predictor convention assumptions must propagate into the strict recipe")
        gates = _semantic_preflight(directory, child_task, context)
        bindings = {g["id"]: g["semantics"] for g in gates["checks"]}
        checks = {c["id"]: c for c in recipe["checks"]}
        require(isinstance(context["assumed_diagnostics"], list), "assumed_diagnostics must be a list")
        diagnostic_ids = set()
        for diagnostic in context["assumed_diagnostics"]:
            exact_keys(diagnostic, {"check_id", "assumption_ids", "reason"}, where="assumed source diagnostic")
            key_check = diagnostic["check_id"]
            require(key_check in checks and key_check not in diagnostic_ids, "Unknown or duplicate assumed diagnostic check")
            diagnostic_ids.add(key_check)
            _refs(diagnostic["assumption_ids"], known, "assumed diagnostic assumptions")
            require(bool(diagnostic["assumption_ids"]), "Assumed diagnostics require explicit assumptions")
            text(diagnostic["reason"], "assumed diagnostic reason")
            require(checks[key_check]["operator"] is not None and checks[key_check]["status"] == "approximate",
                    "Assumed diagnostic requires an explicit approximate recipe operator")
            binding = bindings[key_check]
            require(binding["definition_status"] == "specified" and binding["source_operator"] is not None,
                    "Assumed projection requires a specified source operator; unsupported estimands cannot fall back")
            # This validates numerical operand units, without changing the
            # original strict transform declaration or certifying its convention.
            semantic._measurement({**binding, "transform": "identity"}, checks[key_check]["operator"],
                                  {c["name"]: c for c in child_task["columns"]})
            if binding["transform"] != "identity":
                operator = checks[key_check]["operator"]
                verified_columns = {p["column"] for p in context["predictor_checks"]}
                require(operator["kind"] == "ols_coefficient" and operator["term"] in verified_columns,
                        "Assumed nonidentity projection supports only an explicitly checked zscore OLS term")
        contexts[key] = (context, child_task, gates)
    for entry in protocol["schedule"]:
        if entry["candidate"] == relative and entry["context_id"] in contexts:
            require(contexts[entry["context_id"]][0]["n_rows"] == entry["n_rows"], "Scheduled source row count differs from context")
    return commitment, plan, contexts


def preflight(bundle, candidate):
    """Check frozen source metadata before execution; also works before freeze."""
    root = _bundle(bundle)
    directory, relative = feedback._resolve_candidate(root, candidate)
    _, plan, contexts = _load_plan(root, directory, relative, frozen=False)
    return {"schema_version": 1, "scope": "source_metadata_only", "candidate": relative,
            "protocol_sha256": _digest(_protocol(plan)),
            "contexts": [{"id": key, "semantic_preflight": values[2]} for key, values in contexts.items()]}


def _parent(directory, relative):
    return {"candidate": relative, **{name + "_sha256": sha256(directory / name)
            for name in (*_CORE, "freeze.json", PLAN)}}


def _reserve(root, request):
    folder = _path(root, FOLDER, file=False)
    folder.mkdir(exist_ok=True)
    lock = _path(folder, "admission.lock", file=False)
    # Only serializes reservation. A crashed/stale lock fails closed; it is not
    # silently removed and no evaluation can bypass the recorded budget.
    with lock.open("x", encoding="utf-8"):
        pass
    try:
        entries = [p for p in folder.iterdir() if p.name != lock.name]
        require(len(entries) < request["protocol"]["budget"]["max_evaluations"], "Source evaluation budget exhausted")
        for entry in entries:
            _path(folder, entry.name, file=False)
            require(entry.is_dir(), "Unexpected source ledger entry")
            previous = read_json(_path(entry, "request.json"))
            require(previous["protocol"] == request["protocol"], "Source protocol changed across attempts or revisions")
            require(previous["replay_id"] == entry.name, "Source ledger identity mismatch")
            expected = {k: previous[k] for k in ("replay_id", "candidate", "context_id", "seed", "n_rows")}
            require(expected in request["protocol"]["schedule"], "Existing source attempt is not scheduled")
        destination = _path(folder, request["replay_id"], file=False)
        require(not destination.exists(), "Source replay already exists; attempts are append-only")
        destination.mkdir()
        execution._write(destination / "request.json", request)
        return destination
    finally:
        lock.unlink()


def _make_child(root, directory, frozen, context, task, child):
    child.mkdir(parents=True)
    execution._write(child / "task.json", task)
    registry = read_json(root / "registry.json")["artifacts"][:frozen["registry_snapshot"]["artifact_count"]]
    execution._write(child / "registry.json", {"artifacts": registry})
    for relative in frozen["commitments"]:
        if relative.startswith("sources/"):
            destination = child / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(_path(root, relative).read_bytes())
    copied = child / "candidates/source"
    copied.mkdir(parents=True)
    for name in _CORE:
        (copied / name).write_bytes(_path(directory, name).read_bytes())
    for binding, name in (("recipe", feedback.PLAN), ("semantics", semantic.FILE)):
        (copied / name).write_bytes(_bound(directory, context[binding]).read_bytes())
    execution._write(copied / "checks.json", {"scope": "source_only", "records": [{
        "name": "source_context_compilation", "status": "not_computable",
        "detail": "Compiler copied frozen code/specification/evidence and source-only metadata; execution is recorded separately."}], "artifacts": []})
    execution._write(copied / "parent_binding.json", {"parent": _parent(directory, frozen["candidate"]), "context": context})
    freeze_candidate(child, copied)


def _predictors(frame, context, spec, recipe):
    records = []
    covered = {}
    for check in context["predictor_checks"]:
        reference = check["reference"]
        selected = frame
        for predicate in check["selection"]:
            selected = selected.loc[source_checks.condition(selected, predicate)]
        require(len(selected) > 0, "Predictor identity selection has no rows")
        if reference["mode"] == "sample":
            reference_rows = frame
            for predicate in reference["selection"]:
                reference_rows = reference_rows.loc[source_checks.condition(reference_rows, predicate)]
            require(len(reference_rows) > reference["ddof"], "Zscore reference has insufficient rows")
            raw = reference_rows[check["raw_column"]].to_numpy(dtype=float)
            mean, sd = float(np.mean(raw)), float(np.std(raw, ddof=reference["ddof"]))
            n_reference = len(raw)
        else:
            mean = spec["parameters"][reference["mean_parameter"]]
            sd = spec["parameters"][reference["sd_parameter"]]
            n_reference = None
        require(np.isfinite(mean) and np.isfinite(sd) and sd > 0, "Zscore reference is nonfinite or constant")
        expected = (selected[check["raw_column"]].to_numpy(dtype=float) - mean) / sd
        actual = selected[check["column"]].to_numpy(dtype=float)
        require(np.isfinite(expected).all() and np.isfinite(actual).all(), "Nonfinite standardized predictor")
        # A fixed numerical identity tolerance, never a biological fit threshold.
        require(np.allclose(actual, expected, rtol=1e-9, atol=1e-9), "Generated standardized predictor fails its declared zscore identity")
        covered.setdefault(check["column"], set()).update(selected.index)
        records.append({"declaration": check, "status": "identity_verified", "n_checked": len(selected),
                        "reference_mean": mean, "reference_sd": sd, "n_reference": n_reference,
                        "maximum_absolute_error": float(np.max(np.abs(actual - expected))),
                        "rtol": 1e-9, "atol": 1e-9, "source_convention_validity": "not_certified"})
    for check in recipe["checks"]:
        operator = check["operator"]
        if operator is None:
            continue
        selected = frame
        for predicate in operator["selection"]:
            selected = selected.loc[source_checks.condition(selected, predicate)]
        for column in semantic._variables(operator) & set(covered):
            require(set(selected.index) <= covered[column],
                    "Source operator uses standardized predictor rows without an identity check")
    return records


def _assumed(frame, context, strict):
    rows = {r["id"]: r for r in strict["checks"]}
    records = []
    for declaration in context["assumed_diagnostics"]:
        row = rows[declaration["check_id"]]
        result = {"check_id": row["id"], "evidence_id": row["evidence_id"],
                  "label": "assumption_dependent_source_projection", "strict_semantic_status": row["semantic_status"],
                  "strict_unavailable_reason": row["unavailable_reason"], "reason": declaration["reason"],
                  "assumption_ids": sorted(set(row["assumption_ids"]) | set(declaration["assumption_ids"])),
                  "operator": row["operator"], "reported_value": row["reported_value"],
                  "reported_uncertainty": row["reported_uncertainty"], "uncertainty_interpretation": "source_reported_not_residual_or_acceptance_threshold",
                  "status": "computed", "calculation": None, "difference": None, "unavailable_reason": None}
        try:
            result["calculation"] = source_checks.apply_operator(frame, row["operator"])
            result["difference"] = result["calculation"]["value"] - row["reported_value"]
            require(source_checks.finite(result["difference"]), "Assumed source discrepancy is nonfinite")
        except source_checks.NotComputable as error:
            result.update(status="not_computable", unavailable_reason=str(error))
        records.append(result)
    return records


def _record(root, directory, frozen, context, task, child, request, *, collect):
    child_frozen = verify_candidate(child, "candidates/source")
    copied = child / "candidates/source"
    require(read_json(child / "task.json") == task, "Source child task differs from declared source context")
    require(not (child / "observed.csv").exists(), "Source child contains observed rows")
    require(child_frozen["route"] == "generator.py", "Source child route differs")
    require(read_json(copied / "parent_binding.json") == {"parent": request["parent"], "context": context}, "Source child parent binding changed")
    for name in _CORE:
        require(sha256(copied / name) == sha256(directory / name), "Source child code/specification/evidence differs from parent")
    for binding, name in (("recipe", feedback.PLAN), ("semantics", semantic.FILE)):
        require(sha256(copied / name) == context[binding]["sha256"], "Source child recipe/semantics differs")
    registry = read_json(root / "registry.json")["artifacts"][:frozen["registry_snapshot"]["artifact_count"]]
    require(read_json(child / "registry.json") == {"artifacts": registry}, "Source child registry differs from frozen parent")
    for name, expected in frozen["commitments"].items():
        if name.startswith("sources/"):
            require(sha256(_path(child, name)) == expected, "Source child admitted artifact changed")
    receipt = execution.verify_execution(child, "replay")
    require(receipt["candidate"] == "candidates/source" and receipt["limits"] == request["limits"], "Source execution candidate/limits mismatch")
    result = {"context_id": context["id"], "population": task["population"], "status": receipt["status"],
              "generation_link_verified": False, "source_context_validity": "not_certified",
              "execution_receipt_sha256": sha256(child / "executions/replay/execution.json"),
              "predictor_checks": [], "strict_feedback": None, "assumed_diagnostics": [], "error": receipt["error"]}
    if receipt["status"] != "success":
        return result
    require(receipt["generator_executed"] is True and receipt["route"] == "generator.py", "Source generator execution was not verified")
    output = child / "executions/replay/output/generated.csv"
    frame = read_table(output, task, output=True)
    result.update(generation_link_verified=True, generated_sha256=sha256(output))
    try:
        result["predictor_checks"] = _predictors(frame, context, read_json(directory / "model_spec.json"),
                                                read_json(copied / feedback.PLAN))
    except (ValueError, TypeError, KeyError) as error:
        result.update(status="failed", error={"type": type(error).__name__, "message": str(error)})
        return result
    strict = (semantic.collect_feedback(child, "source", "replay", "strict") if collect else
              semantic.verify_feedback(child, "strict", candidate="source", run_id="replay"))
    result["strict_feedback"] = strict
    result["assumed_diagnostics"] = _assumed(frame, context, strict)
    return result


def run_source_replay(bundle, candidate, replay_id, context_id, seed, *, runtime=None,
                      timeout_seconds=30, memory_mb=1024, output_bytes=20_000_000, log_bytes=100_000):
    """Reserve one scheduled source evaluation, execute, and retain both lanes."""
    limits = execution._limits(timeout_seconds, memory_mb, output_bytes, log_bytes, seed)
    root = _bundle(bundle)
    directory, relative = feedback._resolve_candidate(root, candidate)
    frozen, plan, contexts = _load_plan(root, directory, relative)
    replay_id, context_id = execution._name(replay_id), execution._name(context_id)
    require(context_id in contexts, "Unknown source context")
    context, task, gates = contexts[context_id]
    scheduled = {"replay_id": replay_id, "candidate": relative, "context_id": context_id, "seed": seed, "n_rows": task["n_rows"]}
    require(scheduled in plan["schedule"], "Source evaluation is not in the frozen schedule")
    request = {"schema_version": 1, "kind": "whole_cohort_source_request_v1", **scheduled,
               "parent": _parent(directory, relative), "protocol": _protocol(plan), "limits": limits,
               "created_utc": datetime.now(timezone.utc).isoformat()}
    destination = _reserve(root, request)
    child = destination / "bundle"
    # Any interruption after reservation consumes its slot. No retry, local
    # fallback, or deletion is performed automatically.
    _make_child(root, directory, frozen, context, task, child)
    execution._write(destination / "semantic_preflight.json", gates)
    execution.run_candidate(child, "candidates/source", "replay", runtime=runtime, **limits)
    verify_candidate(root, directory)
    require(_parent(directory, relative) == request["parent"], "Parent changed during source replay")
    record = _record(root, directory, frozen, context, task, child, request, collect=True)
    report = {"schema_version": 1, "kind": "whole_cohort_source_replay_v1", "replay_id": replay_id,
              "status": record["status"], "scope": "source_law_consistency_only", "request_sha256": sha256(destination / "request.json"),
              "parent": request["parent"], "context": record, "engine_sha256": _engine(), "limitations": _LIMITATIONS,
              "files": {name: sha256(_path(destination, name)) for name in _files(destination)}}
    execution._write(destination / "replay.json", report)
    return verify_source_replay(root, replay_id, candidate=relative)


def verify_source_replay(bundle, replay_id, *, candidate=None):
    """Recompute successful diagnostics and verify source-only execution lineage."""
    root = _bundle(bundle)
    replay_id = execution._name(replay_id)
    destination = _path(root, FOLDER + "/" + replay_id, file=False)
    request = read_json(_path(destination, "request.json"))
    report = read_json(_path(destination, "replay.json"))
    exact_keys(report, {"schema_version", "kind", "replay_id", "status", "scope", "request_sha256", "parent", "context", "engine_sha256", "limitations", "files"}, where="source replay report")
    require(report["schema_version"] == 1 and report["kind"] == "whole_cohort_source_replay_v1" and report["replay_id"] == replay_id,
            "Source replay identity changed")
    require(report["scope"] == "source_law_consistency_only" and report["limitations"] == _LIMITATIONS, "Source replay scope changed")
    require(report["engine_sha256"] == _engine(), "Source replay engine changed")
    actual = [name for name in _files(destination) if name != "replay.json"]
    require(sorted(report["files"]) == actual, "Source replay artifact set changed")
    for name, expected in report["files"].items():
        require(sha256(_path(destination, name)) == expected, "Source replay artifact hash changed")
    require(report["request_sha256"] == sha256(destination / "request.json"), "Source request hash changed")
    directory, relative = feedback._resolve_candidate(root, request["candidate"])
    if candidate is not None:
        require(feedback._resolve_candidate(root, candidate)[1] == relative, "Wrong source replay candidate")
    frozen, plan, contexts = _load_plan(root, directory, relative)
    require(request["parent"] == report["parent"] == _parent(directory, relative), "Source parent binding changed")
    require(request["protocol"] == _protocol(plan), "Frozen source protocol changed")
    scheduled = {k: request[k] for k in ("replay_id", "candidate", "context_id", "seed", "n_rows")}
    require(scheduled in plan["schedule"] and request["replay_id"] == replay_id, "Source request differs from frozen schedule")
    require(request["seed"] == request["limits"]["seed"], "Source seed binding mismatch")
    execution._limits(**request["limits"])
    context, task, gates = contexts[request["context_id"]]
    require(read_json(destination / "semantic_preflight.json") == gates, "Source semantic preflight changed")
    expected = _record(root, directory, frozen, context, task, _bundle(destination / "bundle"), request, collect=False)
    require(report["context"] == expected and report["status"] == expected["status"], "Source replay differs from recomputed diagnostics")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("preflight", "run", "verify"))
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--replay-id")
    parser.add_argument("--context-id")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--runtime")
    args = parser.parse_args(argv)
    try:
        if args.action == "preflight":
            result = preflight(args.bundle, args.candidate)
        elif args.action == "run":
            require(args.replay_id is not None and args.context_id is not None and args.seed is not None, "run requires replay/context IDs and seed")
            result = run_source_replay(args.bundle, args.candidate, args.replay_id, args.context_id, args.seed,
                                       runtime=read_json(args.runtime) if args.runtime else None)
        else:
            require(args.replay_id is not None, "verify requires replay ID")
            result = verify_source_replay(args.bundle, args.replay_id, candidate=args.candidate)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({"status": "error", "type": type(error).__name__, "message": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
