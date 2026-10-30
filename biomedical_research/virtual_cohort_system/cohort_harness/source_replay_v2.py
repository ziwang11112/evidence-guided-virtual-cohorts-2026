"""Versioned source replay with source eligibility independent of the target.

M12-A: enrichment, identical variable semantics, identity measurement only.
The legacy execution, statistic and verification engines are reused unchanged.
This verifies execution linkage, not scientific applicability or target utility.
"""
from __future__ import annotations

import argparse
import copy
import csv
import json
from datetime import datetime, timezone

import pandas as pd

from . import contracts, execution, lifecycle, source_checks, source_context
from . import source_replay as legacy
from .contracts import exact_keys, require, string_list, text
from .lifecycle import (_bundle, _candidate, _files, _path, read_json,
                        read_table, sha256, verify_candidate)

PLAN = "source_replay_v2.json"
REPLAY_DIR = "source_replays_v2"
KIND = "independent_context_source_replay"


def _engines():
    return {"source_replay_v2": sha256(__file__), **{
        module.__name__: sha256(module.__file__)
        for module in (source_context, legacy, source_checks, contracts, lifecycle, execution)}}


def _source_frame(candidate, context, target, byte_limit):
    """Reject outcome/extra columns and bound CSV work before pandas loading."""
    source = _path(candidate, context["input"]["path"])
    require(sha256(source) == context["input"]["sha256"], "Source covariate hash mismatch")
    require(0 < source.stat().st_size <= byte_limit, "Source input exceeds byte limit")
    expected = [c["name"] for c in target["columns"] if c["role"] != "generated"]
    maximum, previous = 1_000_000, csv.field_size_limit(1_000_000)
    try:
        with source.open(encoding="utf-8-sig", newline="") as stream:
            def lines():
                while line := stream.readline(maximum + 1):
                    require(len(line) <= maximum, "Source CSV physical line exceeds limit")
                    yield line
            rows = csv.reader(lines(), strict=True)
            require(next(rows, None) == expected, "Source input must contain only identifier and observed columns")
            count = 0
            for row in rows:
                count += 1
                require(count <= maximum and len(row) == len(expected), "Source CSV shape exceeds contract")
            require(count > 0, "Source context is empty")
    except (csv.Error, UnicodeError) as error:
        raise contracts.ContractError("Invalid bounded source CSV") from error
    finally:
        csv.field_size_limit(previous)
    reading_task = copy.deepcopy(target)
    reading_task.update(columns=copy.deepcopy(context["columns"]), n_rows=count, population=context["population"])
    contracts.validate_task(reading_task)
    return source, read_table(source, reading_task)


def _operator_preflight(operator, task):
    """Reuse the legacy parser on typed empty data; compute no source statistics."""
    columns = {c["name"]: c for c in task["columns"]}
    numeric = {name for name, c in columns.items() if c["kind"] in {"number", "integer"} or
               (c["kind"] == "category" and all(source_checks.finite(v) for v in c["categories"]))}
    empty = pd.DataFrame({name: pd.Series([], dtype="float64" if name in numeric else "string") for name in columns})
    try:
        source_checks.apply_operator(empty, operator)
    except source_checks.NotComputable:
        pass  # Empty input is intentional; other schema/type errors must propagate.
    for selection in operator["selection"]:
        _filter_type(selection, columns)
    kind = operator["kind"]
    if kind == "ols_coefficient":
        terms = operator["predictors"] + (["intercept"] if operator["include_intercept"] else [])
        require(operator["term"] in terms, "Unknown OLS coefficient term")
        variables = [operator["outcome"], *operator["predictors"]]
    elif kind in {"correlation", "spearman_correlation"}:
        variables = [operator["x"], operator["y"]]
    elif kind == "proportion":
        source_checks.condition(empty, operator["event"])
        _filter_type(operator["event"], columns)
        variables = []
    else:
        variables = [operator["column"]]
    require(set(variables) <= numeric, "Numeric operator requires numeric source columns or explicit encoding")


def _filter_type(condition, columns):
    """Empty arrays cannot expose incompatible scalar comparisons by themselves."""
    column = columns[condition["column"]]
    kind, op = column["kind"], condition["op"]
    values = condition["value"] if op == "in" else [condition["value"]]
    if kind == "category":
        categories = column["categories"]
        numeric = all(source_checks.finite(v) for v in categories)
        strings = all(isinstance(v, str) for v in categories)
        if op in {"lt", "le", "gt", "ge"}:
            require(numeric or strings, "Ordered filters require uniformly typed category support")
    else:
        numeric, strings = kind in {"number", "integer"}, kind == "string"
    for value in values:
        valid = source_checks.finite(value) if numeric else isinstance(value, str) if strings else (
            source_checks.finite(value) or isinstance(value, str))
        require(valid, "Filter scalar type does not match source column")


def _plan(root, candidate, byte_limit):
    frozen = verify_candidate(root, candidate)
    require(frozen["route"] == "generator.py", "Source replay requires a frozen generator")
    target = read_json(root / "task.json")
    require(target["mode"] == "enrichment", "Independent source replay supports enrichment only")
    plan = read_json(_path(candidate, PLAN))
    exact_keys(plan, {"schema_version", "model_domain", "contexts"}, where="source replay v2")
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 2, "Invalid source plan version")
    require(isinstance(plan["contexts"], list) and bool(plan["contexts"]), "Source contexts required")
    evidence = {x["id"]: x for x in read_json(candidate / "evidence.json")["items"]}
    assumptions = {x["id"] for x in read_json(candidate / "model_spec.json")["assumptions"]}
    contexts, ids = [], set()
    for context in plan["contexts"]:
        exact_keys(context, {"id", "population", "reason", "assumption_ids", "measurement", "input", "checks", "columns"},
                   where="independent source context")
        execution._name(context["id"])
        require(context["id"].casefold() not in ids, "Duplicate source context (case-insensitive)")
        ids.add(context["id"].casefold())
        for field in ("population", "reason"):
            text(context[field], "source context " + field)
        string_list(context["assumption_ids"], "context assumptions")
        exact_keys(context["measurement"], {"mode", "description"}, where="measurement mapping")
        require(context["measurement"]["mode"] == "identity", "Only identity measurement is implemented")
        text(context["measurement"]["description"], "measurement description")
        exact_keys(context["input"], {"path", "sha256", "origin"}, where="source input")
        require(context["input"]["origin"] == "declared_source_covariates", "Invalid source input origin")
        source, frame = _source_frame(candidate, context, target, byte_limit)
        task = source_context.compile_source_task(target, context, plan["model_domain"], frame,
                                                  assumption_ids=assumptions)
        require(set(plan["model_domain"]["assumption_ids"]) <= set(context["assumption_ids"]),
                "Model-domain assumptions must also be declared by each context")
        require(isinstance(context["checks"], list) and bool(context["checks"]), "Source checks required")
        check_ids = set()
        for check in context["checks"]:
            legacy._check_metadata(check, evidence, assumptions, context["assumption_ids"])
            _operator_preflight(check["operator"], task)
            require(check["id"] not in check_ids, "Duplicate source check")
            check_ids.add(check["id"])
        contexts.append((context, source, task))
    return frozen, contexts, evidence, assumptions


def _parent(candidate, relative):
    return {"candidate": relative, **{name + "_sha256": sha256(candidate / name)
            for name in ("freeze.json", "generator.py", "model_spec.json", PLAN)}}


def run_source_replay(bundle, candidate, replay_id, seed, *, runtime=None,
                      timeout_seconds=30, memory_mb=1024, output_bytes=20_000_000, log_bytes=100_000):
    """Run immutable source tasks without widening or changing the target task."""
    limits = execution._limits(timeout_seconds, memory_mb, output_bytes, log_bytes, seed)
    root = _bundle(bundle)
    candidate, relative = _candidate(root, candidate)
    frozen, contexts, evidence, assumptions = _plan(root, candidate, output_bytes)
    parent, engines = _parent(candidate, relative), _engines()
    replay_id = execution._name(replay_id)
    replay = _path(root, REPLAY_DIR + "/" + replay_id, file=False)
    require(not replay.exists(), "Source replay already exists; use a new ID")
    replay.mkdir(parents=True)
    execution._write(replay / "intent.json", {"kind": KIND, "parent": parent,
        "context_ids": [c[0]["id"] for c in contexts], "limits": limits, "engines": engines})
    records = []
    for context, source, task in contexts:
        child = replay / "contexts" / context["id"] / "bundle"
        legacy._make_child(root, candidate, frozen, source, task, child)
        execution.run_candidate(child, "candidates/source", "replay", runtime=runtime, **limits)
        verify_candidate(root, candidate)
        require(_parent(candidate, relative) == parent, "Parent changed during source replay")
        records.append(legacy._context_record(root, frozen, context, source, task, child,
                                               evidence, assumptions, limits))
    require(_engines() == engines, "Source replay engine changed during execution")
    report = {"schema_version": 1, "kind": KIND, "replay_id": replay_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "success" if all(r["status"] == "success" for r in records) else "failed",
        "scope": "source_statistic_diagnostics_only", "parent": parent, "limits": limits,
        "contexts": records, "engines": engines,
        "files": {name: sha256(_path(replay, name)) for name in _files(replay)},
        "limitations": ["Source/model domains are declarations, not learned validity guarantees.",
            "Same variable semantics and identity measurement only; no extra adjustment variables.",
            "Only the generator process is isolated; Agent tools remain procedurally restricted.",
            "Hashes are not signatures; source fit does not establish target utility."]}
    execution._write(replay / "replay.json", report)
    return verify_source_replay(root, replay_id, candidate=candidate)


def verify_source_replay(bundle, replay_id, *, candidate=None):
    """Verify artifacts, all independent task schemas and recalculated statistics."""
    root = _bundle(bundle)
    replay_id = execution._name(replay_id)
    replay = _path(root, REPLAY_DIR + "/" + replay_id, file=False)
    report = read_json(_path(replay, "replay.json"))
    exact_keys(report, {"schema_version", "kind", "replay_id", "created_utc", "status", "scope", "parent",
                       "limits", "contexts", "engines", "files", "limitations"}, where="source replay v2 report")
    require(type(report["schema_version"]) is int and report["schema_version"] == 1 and
            report["kind"] == KIND and report["replay_id"] == replay_id, "Invalid replay identity/version")
    require(report["scope"] == "source_statistic_diagnostics_only", "Replay overstates its scope")
    require(report["engines"] == _engines(), "Replay engine changed; use the recorded versions")
    limits = report["limits"]
    execution._limits(**limits)
    directory, relative = _candidate(root, report["parent"]["candidate"])
    if candidate is not None:
        require(_candidate(root, candidate)[1] == relative, "Replay is for another candidate")
    frozen, contexts, evidence, assumptions = _plan(root, directory, limits["output_bytes"])
    require(report["parent"] == _parent(directory, relative), "Replay parent changed")
    require(isinstance(report["files"], dict) and bool(report["files"]), "Replay artifact inventory missing")
    actual = sorted(name for name in _files(replay) if name != "replay.json")
    require(actual == sorted(report["files"]), "Replay artifact inventory changed")
    for name, expected in report["files"].items():
        require(sha256(_path(replay, name)) == expected, "Replay artifact hash changed")
    intent = read_json(_path(replay, "intent.json"))
    require(intent == {"kind": KIND, "parent": report["parent"],
        "context_ids": [c[0]["id"] for c in contexts], "limits": limits, "engines": report["engines"]},
        "Replay intent disagrees with completed report")
    records = []
    for context, source, task in contexts:
        child = _bundle(_path(replay, "contexts/" + context["id"] + "/bundle", file=False))
        records.append(legacy._context_record(root, frozen, context, source, task, child,
                                               evidence, assumptions, limits))
    require(report["contexts"] == records, "Feedback differs from verified source execution")
    expected_status = "success" if all(r["status"] == "success" for r in records) else "failed"
    require(report["status"] == expected_status, "Replay status differs from executions")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["run", "verify"])
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--candidate")
    parser.add_argument("--replay-id", required=True)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--runtime")
    args = parser.parse_args()
    if args.action == "run":
        require(args.candidate is not None and args.seed is not None, "Run requires candidate and seed")
        result = run_source_replay(args.bundle, args.candidate, args.replay_id, args.seed,
                                  runtime=read_json(args.runtime) if args.runtime else None)
    else:
        result = verify_source_replay(args.bundle, args.replay_id, candidate=args.candidate)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
