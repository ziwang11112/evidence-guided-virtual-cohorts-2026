"""Execution-backed source diagnostics for frozen enrichment generators.

Source covariates and their interpretation are declared by the builder. The
harness changes only the child task's population and row count, never scientific
parameters. Hash linkage is relative to the retained receipts, not a signature
or proof of substantive source-population/measurement equivalence.
"""
from __future__ import annotations

import copy
import csv
from datetime import datetime, timezone
from pathlib import Path

from . import execution
from .contracts import exact_keys, require, string_list, text, validate_input
from .lifecycle import (_bundle, _candidate, _files, _path, freeze_candidate,
                        read_json, read_table, sha256, verify_candidate)
from .source_checks import NotComputable, apply_operator, finite


def _check_metadata(check, evidence, assumptions, context_assumptions):
    exact_keys(check, {"id", "evidence_id", "status", "operator", "assumption_ids", "reason"},
               where="source replay check")
    execution._name(check["id"])
    require(check["evidence_id"] in evidence, "Unknown source replay evidence ID")
    require(check["status"] in {"computed", "approximate"}, "Replay check must be computed or approximate")
    text(check["reason"], "source replay check reason")
    string_list(check["assumption_ids"], "source replay check assumptions")
    require(set(check["assumption_ids"]) <= assumptions, "Unknown source replay check assumption")
    combined = set(check["assumption_ids"]) | set(context_assumptions)
    require(bool(combined) == (check["status"] == "approximate"),
            "Source context or check assumptions require explicit approximate status")
    item, operator = evidence[check["evidence_id"]], check["operator"]
    require(isinstance(operator, dict), "Source replay operator must be an object")
    require(operator.get("kind") == item["kind"], "Source/operator statistic-kind mismatch")
    require(operator.get("unit") == item["unit"], "Source/operator unit-label mismatch")
    require(finite(item["estimate"]), "Numeric source estimate required")
    kind = operator["kind"]
    if kind in {"mean", "sd"}:
        variables = {operator.get("column")}
    elif kind == "correlation":
        variables = {operator.get("x"), operator.get("y")}
    elif kind == "ols_coefficient":
        require(isinstance(operator.get("predictors"), list), "OLS predictors must be a list")
        variables = {operator.get("outcome"), *operator["predictors"]}
    elif kind == "proportion":
        require(isinstance(operator.get("event"), dict), "Proportion event must be an object")
        variables = {operator["event"].get("column")}
    else:
        raise ValueError("Source statistic has no implemented replay operator")
    aligned = variables == set(item["variables"]) | set(item["adjustment"])
    if kind == "ols_coefficient":
        aligned = aligned and set(item["adjustment"]) <= set(operator["predictors"])
    require(aligned or check["status"] == "approximate",
            "Source/operator variable or adjustment mismatch; explicit approximation required")
    return item, aligned


def _input_task(candidate, context, task, byte_limit):
    """Validate bounded covariate-only CSV before deriving the child task."""
    source = _path(candidate, context["input"]["path"])
    require(sha256(source) == context["input"]["sha256"], "Source covariate hash mismatch")
    require(0 < source.stat().st_size <= byte_limit, "Source covariate CSV exceeds execution byte limit")
    expected = [c["name"] for c in task["columns"] if c["role"] != "generated"]
    maximum, previous_limit = 1_000_000, csv.field_size_limit(1_000_000)
    try:
        with source.open(encoding="utf-8-sig", newline="") as stream:
            def lines():
                while line := stream.readline(maximum + 1):
                    require(len(line) <= maximum, "Source CSV physical line exceeds safety limit")
                    yield line
            reader = csv.reader(lines(), strict=True)
            require(next(reader, None) == expected,
                    "Source input must contain exactly identifier and observed covariates; outcomes are forbidden")
            count = 0
            for row in reader:
                count += 1
                require(count <= maximum, "Source context exceeds one million rows")
                require(len(row) == len(expected), "Source covariate CSV field count mismatch")
    except (csv.Error, UnicodeError) as error:
        raise ValueError("Invalid source covariate CSV") from error
    finally:
        csv.field_size_limit(previous_limit)
    require(count > 0, "Source context must contain covariate rows")
    child_task = copy.deepcopy(task)
    child_task["population"], child_task["n_rows"] = context["population"], count
    validate_input(read_table(source, child_task), child_task)
    return source, child_task


def _plan(root, candidate, byte_limit):
    frozen = verify_candidate(root, candidate)
    require(frozen["route"] == "generator.py", "Source replay requires a frozen generator, not supplied output rows")
    task = read_json(root / "task.json")
    require(task["mode"] == "enrichment", "Source replay currently supports enrichment tasks only")
    plan = read_json(_path(candidate, "source_replay.json"))
    exact_keys(plan, {"schema_version", "contexts"}, where="source replay plan")
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1,
            "Invalid source replay schema version")
    require(isinstance(plan["contexts"], list) and bool(plan["contexts"]), "Source replay contexts required")
    evidence = {item["id"]: item for item in read_json(candidate / "evidence.json")["items"]}
    assumptions = {item["id"] for item in read_json(candidate / "model_spec.json")["assumptions"]}
    contexts, ids = [], set()
    for context in plan["contexts"]:
        exact_keys(context, {"id", "population", "reason", "assumption_ids", "measurement", "input", "checks"},
                   where="source replay context")
        execution._name(context["id"])
        require(context["id"] not in ids, "Duplicate source context ID")
        ids.add(context["id"])
        for field in ("population", "reason"):
            text(context[field], "source context " + field)
        string_list(context["assumption_ids"], "source context assumptions")
        require(set(context["assumption_ids"]) <= assumptions, "Unknown source context assumption")
        exact_keys(context["measurement"], {"mode", "description"}, where="source measurement mapping")
        require(context["measurement"]["mode"] == "identity", "Only explicit identity measurement mapping is supported")
        text(context["measurement"]["description"], "source measurement description")
        exact_keys(context["input"], {"path", "sha256", "origin"}, where="source covariate input")
        require(context["input"]["origin"] == "declared_source_covariates", "Unsupported source input origin")
        require(isinstance(context["checks"], list) and bool(context["checks"]), "Source context checks required")
        check_ids = set()
        for check in context["checks"]:
            _check_metadata(check, evidence, assumptions, context["assumption_ids"])
            require(check["id"] not in check_ids, "Duplicate source check ID")
            check_ids.add(check["id"])
        source, child_task = _input_task(candidate, context, task, byte_limit)
        contexts.append((context, source, child_task))
    return frozen, contexts, evidence, assumptions


def _make_child(root, candidate, frozen, source, task, child):
    child.mkdir(parents=True)
    execution._write(child / "task.json", task)
    registry = read_json(root / "registry.json")
    execution._write(child / "registry.json", {
        "artifacts": registry["artifacts"][:frozen["registry_snapshot"]["artifact_count"]]})
    for relative in frozen["commitments"]:
        if relative.startswith("sources/"):
            destination = child / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(_path(root, relative).read_bytes())
    child.joinpath("observed.csv").write_bytes(source.read_bytes())
    copied = child / "candidates/source"
    copied.mkdir(parents=True)
    for relative in _candidate_bindings(frozen):
        destination = copied / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(_path(candidate, relative).read_bytes())
    freeze_candidate(child, copied)


def _candidate_bindings(frozen):
    prefix = frozen["candidate"] + "/"
    return {name.removeprefix(prefix): frozen["commitments"][name] for name in frozen["candidate_files"]}


def _context_record(root, frozen, context, source, task, child, evidence, assumptions, limits):
    """Only this verifier can produce a true generation linkage flag."""
    child_frozen = verify_candidate(child, "candidates/source")
    require(child_frozen["route"] == "generator.py" and
            _candidate_bindings(child_frozen) == _candidate_bindings(frozen),
            "Source child generator/specification or candidate artifacts differ from parent")
    require(read_json(child / "task.json") == task,
            "Source child task changed beyond declared population and row count")
    require(sha256(child / "observed.csv") == sha256(source), "Source child covariates differ from recipe")
    expected_registry = read_json(root / "registry.json")["artifacts"][:frozen["registry_snapshot"]["artifact_count"]]
    require(read_json(child / "registry.json") == {"artifacts": expected_registry}, "Source child registry differs from parent")
    receipt = execution.verify_execution(child, "replay")
    require(receipt["candidate"] == "candidates/source", "Source execution is for the wrong candidate")
    require(receipt["limits"] == limits, "Source execution limits/seed differ from replay request")
    result = {
        "id": context["id"], "status": receipt["status"],
        "child_bundle": "contexts/" + context["id"] + "/bundle",
        "execution_sha256": sha256(child / "executions/replay/execution.json"),
        "context_input_sha256": sha256(source), "measurement": context["measurement"],
        "context_assumption_ids": context["assumption_ids"],
        "generation_link_verified": False, "checks": [],
    }
    if receipt["status"] != "success":
        result["error"] = receipt["error"]
        return result
    require(receipt["route"] == "generator.py" and receipt["generator_executed"] is True,
            "Source replay lacks successful generator execution")
    output = child / "executions/replay/output/generated.csv"
    table = read_table(output, task, output=True)
    result.update(generation_link_verified=True, generated_sha256=sha256(output))
    for check in context["checks"]:
        item, aligned = _check_metadata(check, evidence, assumptions, context["assumption_ids"])
        record = {**check, "reported_value": item["estimate"], "generation_link_verified": True,
                  "variable_set_matches_source": aligned,
                  "evidence_mapping_check": "identity_declaration_variable_set_and_unit_labels_only",
                  "generated_sha256": sha256(output)}
        try:
            summary = apply_operator(table, check["operator"])
            record.update(summary, difference=summary["value"] - item["estimate"])
        except NotComputable as error:
            record.update(status="not_computable", computation_error=str(error))
        result["checks"].append(record)
    return result


def _parent_binding(candidate, relative):
    return {"candidate": relative, **{name + "_sha256": sha256(candidate / name)
            for name in ("freeze.json", "generator.py", "model_spec.json", "source_replay.json")}}


def run_source_replay(bundle, candidate, replay_id, seed, *, runtime=None,
                      timeout_seconds=30, memory_mb=1024, output_bytes=20_000_000, log_bytes=100_000):
    """Execute frozen source contexts and retain source-only feedback separately.

    Initial contract errors raise. Failed generator runs are retained and return
    top-level status failed, with no verified statistic for the failed context.
    No retrieval occurs, and no target/held-out table is an input to this API.
    """
    limits = execution._limits(timeout_seconds, memory_mb, output_bytes, log_bytes, seed)
    root = _bundle(bundle)
    candidate, relative = _candidate(root, candidate)
    frozen, contexts, evidence, assumptions = _plan(root, candidate, output_bytes)
    parent = _parent_binding(candidate, relative)
    replay_id = execution._name(replay_id)
    replay = _path(root, "source_replays/" + replay_id, file=False)
    require(not replay.exists(), "Source replay already exists; choose a new ID")
    replay.mkdir(parents=True)
    records = []
    for context, source, task in contexts:
        child = replay / "contexts" / context["id"] / "bundle"
        _make_child(root, candidate, frozen, source, task, child)
        execution.run_candidate(child, "candidates/source", "replay", runtime=runtime, **limits)
        verify_candidate(root, candidate)
        require(_parent_binding(candidate, relative) == parent, "Parent changed during source replay")
        records.append(_context_record(root, frozen, context, source, task, child,
                                       evidence, assumptions, limits))
    report = {
        "schema_version": 1, "kind": "execution_backed_source_replay", "replay_id": replay_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "success" if all(r["status"] == "success" for r in records) else "failed",
        "scope": "source_statistic_diagnostics_only", "parent": parent, "limits": limits,
        "contexts": records, "engine_sha256": sha256(__file__),
        "files": {name: sha256(_path(replay, name)) for name in _files(replay)},
        "limitations": [
            "Covariate population and identity measurement mapping are declarations requiring substantive review.",
            "Hashes bind retained bytes; they are not signatures against host-side receipt forgery.",
            "Only the generator process is isolated; no target validity or calibrated inference is implied.",
        ],
    }
    execution._write(replay / "replay.json", report)
    return verify_source_replay(root, replay_id, candidate=candidate)


def verify_source_replay(bundle, replay_id, *, candidate=None):
    """Recheck parent/child/execution linkage and recompute every source statistic."""
    root = _bundle(bundle)
    replay_id = execution._name(replay_id)
    replay = _path(root, "source_replays/" + replay_id, file=False)
    report = read_json(_path(replay, "replay.json"))
    exact_keys(report, {"schema_version", "kind", "replay_id", "created_utc", "status", "scope", "parent",
                        "limits", "contexts", "engine_sha256", "files", "limitations"}, where="source replay report")
    require(report["schema_version"] == 1 and report["kind"] == "execution_backed_source_replay" and
            report["replay_id"] == replay_id, "Invalid source replay identity")
    require(report["scope"] == "source_statistic_diagnostics_only", "Source replay overstates its scope")
    require(report["engine_sha256"] == sha256(__file__), "Source replay engine changed; use the recorded engine version")
    limits = report["limits"]
    require(isinstance(limits, dict), "Source replay limits must be an object")
    execution._limits(**limits)
    directory, relative = _candidate(root, report["parent"]["candidate"])
    if candidate is not None:
        _, requested = _candidate(root, candidate)
        require(relative == requested, "Source replay is for the wrong candidate")
    frozen, contexts, evidence, assumptions = _plan(root, directory, limits["output_bytes"])
    require(report["parent"] == _parent_binding(directory, relative), "Source replay parent binding changed")
    require(isinstance(report["files"], dict) and bool(report["files"]), "Source replay artifacts missing")
    actual = sorted(name for name in _files(replay) if name != "replay.json")
    require(actual == sorted(report["files"]), "Source replay artifact set changed")
    for name, expected in report["files"].items():
        require(sha256(_path(replay, name)) == expected, "Source replay artifact hash changed")
    records = []
    for context, source, task in contexts:
        child = _bundle(_path(replay, "contexts/" + context["id"] + "/bundle", file=False))
        records.append(_context_record(root, frozen, context, source, task, child,
                                       evidence, assumptions, limits))
    require(report["contexts"] == records, "Source replay feedback differs from recomputed execution statistics")
    expected_status = "success" if all(r["status"] == "success" for r in records) else "failed"
    require(report["status"] == expected_status, "Source replay status differs from execution status")
    return report
