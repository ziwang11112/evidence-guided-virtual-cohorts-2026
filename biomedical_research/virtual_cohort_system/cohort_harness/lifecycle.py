"""Freeze and verify portable candidate bundles without executing Agent code.

Canonical layout: task.json, registry.json, optional observed.csv, sources/,
and candidates/<name>/. Registry records are append-only and each receipt binds
the canonical prefix visible at freeze time. A registry is a trusted procedural input;
these hash checks do not independently prove screening, source truth, actual
check execution, or secure exclusion of reference data.
"""
from __future__ import annotations

import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from .contracts import (
    ContractError, _hash, exact_keys, require, string_list, text,
    validate_evidence, validate_input, validate_output, validate_spec, validate_task,
)
from .analysis_evidence import validate_analysis_evidence


_SUBMISSION_FILES = {"generator.py", "generated.csv", "model_spec.json", "evidence.json",
                     "decision.md", "checks.json", "freeze.json", "analysis_evidence.json"}
_RECEIPT_KEYS = {"schema_version", "kind", "created_utc", "candidate", "route", "commitments",
                 "candidate_files", "parent", "revision", "revision_index", "acceptance", "isolation",
                 "registry_snapshot"}


def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON object key")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ContractError(f"Nonfinite JSON number: {value}")


def read_json(path: str | Path) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                          object_pairs_hook=_object, parse_constant=_invalid_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ContractError(f"Cannot read valid JSON: {Path(path).name}") from error


def _link(path: Path) -> bool:
    return path.is_symlink() or bool(getattr(path, "is_junction", lambda: False)())


def _bundle(path: str | Path) -> Path:
    raw = Path(path)
    require(".." not in raw.parts, "Bundle path traversal is not allowed")
    absolute = Path(os.path.abspath(raw))
    for part in [absolute, *absolute.parents]:
        require(not _link(part), "Bundle path contains a symbolic link or junction")
    require(absolute.is_dir(), "Bundle directory does not exist")
    return absolute.resolve()


def safe_relative(value: str) -> tuple[str, ...]:
    """Accept portable forward-slash paths without traversal or Windows devices."""
    text(value, "relative path")
    require(not any(c in value for c in '\\:\x00<>"|?*'), "Unsafe relative path characters")
    require(all(ord(c) >= 32 for c in value), "Control characters are not allowed in paths")
    parts = value.split("/")
    require(all(p not in {"", ".", ".."} and not p.endswith((".", " ")) for p in parts),
            "Invalid relative path segment")
    devices = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)),
               *(f"lpt{i}" for i in range(1, 10))}
    require(all(p.split(".")[0].casefold() not in devices for p in parts), "Windows device path rejected")
    return tuple(parts)


def _path(root: Path, relative: str, *, file: bool = True) -> Path:
    parts = safe_relative(relative)
    current = root
    for part in parts:
        current = current / part
        require(not _link(current), "Symbolic links and junctions are not accepted")
    require(current.resolve().is_relative_to(root), "Artifact escapes its declared root")
    if file:
        require(current.is_file(), f"Required regular file is missing: {relative}")
    return current


def _candidate(bundle: Path, value: str | Path) -> tuple[Path, str]:
    raw = Path(value)
    require(".." not in raw.parts, "Candidate path traversal is not allowed")
    if raw.is_absolute():
        try:
            relative = raw.relative_to(bundle).as_posix()
        except ValueError as error:
            raise ContractError("Candidate is outside bundle") from error
    else:
        relative = raw.as_posix()
    parts = safe_relative(relative)
    require(len(parts) == 2 and parts[0] == "candidates", "Candidate must be bundle/candidates/<name>")
    directory = _path(bundle, relative, file=False)
    require(directory.is_dir(), "Candidate directory does not exist")
    return directory, relative


def _files(directory: Path) -> list[str]:
    result = []
    for path in sorted(directory.rglob("*")):
        relative = path.relative_to(directory).as_posix()
        _path(directory, relative, file=False)
        require(path.is_dir() or path.is_file(), "Candidate has a nonregular filesystem entry")
        if path.is_file() and relative != "freeze.json":
            result.append(relative)
    return sorted(result)


def read_table(path: str | Path, task: dict, *, output: bool = False) -> pd.DataFrame:
    """Read contract strings as strings; numeric identifiers retain numeric type."""
    dtype = {}
    for column in task["columns"]:
        if column["kind"] == "string" or (column["kind"] == "category" and
                                            all(isinstance(v, str) for v in column["categories"])):
            dtype[column["name"]] = "string"
    try:
        # Empty CSV fields represent missing cells; literal strings such as NA
        # remain strings. This is a transport convention, not an imputation rule.
        return pd.read_csv(path, dtype=dtype, float_precision="round_trip", keep_default_na=False,
                           na_values=[""])
    except (OSError, ValueError, pd.errors.ParserError) as error:
        raise ContractError(f"Invalid CSV table: {Path(path).name}") from error


def validate_program(path: str | Path) -> None:
    """Check the declared positional ABI without importing/executing the program.

    The three arguments receive observed data, model specification and seed in
    that order; their Python names may differ. This syntactic check is neither
    a sandbox nor a guarantee of runtime behavior.
    """
    try:
        syntax = ast.parse(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, SyntaxError, UnicodeError) as error:
        raise ContractError("Generator is not valid Python source") from error
    declarations = [node for node in syntax.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "generate"]
    require(len(declarations) == 1 and isinstance(declarations[0], ast.FunctionDef),
            "Generator must declare exactly one top-level synchronous generate function")
    arguments = declarations[0].args
    require(len(arguments.posonlyargs) + len(arguments.args) == 3 and
            arguments.vararg is None and arguments.kwarg is None and not arguments.kwonlyargs,
            "generate must have exactly three positional arguments: observed, specification, seed; "
            "no *args, **kwargs or keyword-only arguments")


def _registry(bundle: Path, count: int | None = None) -> tuple[dict, set[tuple[str, str, str]], dict[str, str]]:
    path = _path(bundle, "registry.json")
    registry = read_json(path)
    exact_keys(registry, {"artifacts"}, where="registry")
    require(isinstance(registry["artifacts"], list), "registry.artifacts must be a list")
    if count is None:
        count = len(registry["artifacts"])
    require(type(count) is int and 0 <= count <= len(registry["artifacts"]),
            "Registry prefix was removed or snapshot count is invalid")
    entries, all_entries, commitments = set(), set(), {}
    for index, entry in enumerate(registry["artifacts"]):
        exact_keys(entry, {"source_id", "path", "sha256", "origin", "screening"}, where="registry artifact")
        text(entry["source_id"], "registry source ID")
        _hash(entry["sha256"])
        require(entry["origin"] in {"fixture", "gateway", "curator"}, "Invalid registry origin")
        require(entry["screening"] == "approved", "Unapproved registry artifact")
        parts = safe_relative(entry["path"])
        require(len(parts) >= 2 and parts[0] == "sources", "Registered artifacts must be under sources/")
        key = (entry["source_id"], entry["path"], entry["sha256"])
        require(key not in all_entries, "Duplicate registry artifact")
        all_entries.add(key)
        if index < count:
            artifact = _path(bundle, entry["path"])
            require(sha256(artifact) == entry["sha256"], "Registered source artifact hash mismatch")
            entries.add(key)
            commitments[entry["path"]] = entry["sha256"]
    encoded = json.dumps(registry["artifacts"][:count], sort_keys=True, ensure_ascii=False,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    snapshot = {"path": "registry.json", "artifact_count": count,
                "sha256": hashlib.sha256(encoded).hexdigest()}
    return snapshot, entries, commitments


def _checks(candidate: Path) -> None:
    checks = read_json(_path(candidate, "checks.json"))
    exact_keys(checks, {"scope", "records", "artifacts"}, where="checks")
    require(checks["scope"] in {"fixture_only", "source_only"}, "Checks scope must exclude target feedback")
    require(isinstance(checks["records"], list) and bool(checks["records"]), "Check records required")
    names, computed = set(), False
    for record in checks["records"]:
        exact_keys(record, {"name", "status", "detail"}, where="check record")
        text(record["name"], "check name")
        text(record["detail"], "check detail")
        require(record["name"] not in names, "Duplicate check name")
        names.add(record["name"])
        require(record["status"] in {"pass", "fail", "not_computable"}, "Invalid check status")
        computed = computed or record["status"] != "not_computable"
    require(isinstance(checks["artifacts"], list), "Check artifacts must be a list")
    require(not computed or bool(checks["artifacts"]), "Computed checks require bound result artifacts")
    paths = set()
    for artifact in checks["artifacts"]:
        exact_keys(artifact, {"path", "sha256"}, where="check artifact")
        _hash(artifact["sha256"])
        require(artifact["path"] not in _SUBMISSION_FILES, "Check artifact must be an auxiliary result file")
        path = _path(candidate, artifact["path"])
        require(artifact["path"] not in paths, "Duplicate check artifact")
        paths.add(artifact["path"])
        require(sha256(path) == artifact["sha256"], "Check result artifact hash mismatch")


def _state(bundle: Path, candidate: Path, relative: str, registry_count: int | None = None) -> dict:
    task_path = _path(bundle, "task.json")
    task = read_json(task_path)
    validate_task(task)
    registry_snapshot, registry, commitments = _registry(bundle, registry_count)
    commitments["task.json"] = sha256(task_path)
    observed_path = _path(bundle, "observed.csv", file=False)
    if task["mode"] == "whole_cohort":
        require(not observed_path.exists(), "Whole-cohort bundle cannot contain observed.csv")
        observed = None
    else:
        require(observed_path.is_file(), "Observed table missing")
        observed = read_table(observed_path, task)
        commitments["observed.csv"] = sha256(observed_path)
    validate_input(observed, task)
    files = _files(candidate)
    required = {"model_spec.json", "evidence.json", "decision.md", "checks.json"}
    require(required <= set(files), "Required candidate files missing")
    routes = set(files) & {"generator.py", "generated.csv"}
    require(len(routes) == 1, "Exactly one generator.py or generated.csv route is required")
    route = next(iter(routes))
    if route == "generator.py":
        validate_program(_path(candidate, route))
    else:
        validate_output(observed, read_table(_path(candidate, route), task, output=True), task)
    require(bool(_path(candidate, "decision.md").read_text(encoding="utf-8-sig").strip()),
            "Decision record must be nonempty")
    evidence = read_json(_path(candidate, "evidence.json"))
    evidence_ids = validate_evidence(evidence, task)
    spec = read_json(_path(candidate, "model_spec.json"))
    validate_spec(spec, evidence_ids)
    if _path(candidate, "analysis_evidence.json", file=False).exists():
        validate_analysis_evidence(read_json(_path(candidate, "analysis_evidence.json")), task, evidence, spec)
    for source in evidence["sources"]:
        for artifact in source["artifacts"]:
            require((source["id"], artifact["path"], artifact["sha256"]) in registry,
                    "Evidence artifact is not registered for this source")
    _checks(candidate)
    candidate_files = []
    for name in files:
        key = relative + "/" + name
        candidate_files.append(key)
        commitments[key] = sha256(_path(candidate, name))
    return {"task": task, "route": route, "commitments": commitments, "registry_snapshot": registry_snapshot,
            "candidate_files": sorted(candidate_files)}


def _revision(value: dict) -> None:
    exact_keys(value, {"reason", "kind", "addressed_findings", "remaining_limitations"}, where="revision")
    text(value["reason"], "revision reason")
    require(value["kind"] in {"retain", "revise"}, "Invalid revision kind")
    string_list(value["addressed_findings"], "addressed_findings")
    string_list(value["remaining_limitations"], "remaining_limitations")


def _same_model(current: dict, previous: dict) -> bool:
    if current["route"] != previous["route"]:
        return False
    return all(current["commitments"][current["candidate"] + "/" + name] ==
               previous["commitments"][previous["candidate"] + "/" + name]
               for name in ("model_spec.json", current["route"]))


def _verify(bundle: Path, candidate: Path, relative: str, seen: set[str]) -> dict:
    require(relative not in seen, "Cyclic candidate lineage")
    seen.add(relative)
    receipt = read_json(_path(candidate, "freeze.json"))
    exact_keys(receipt, _RECEIPT_KEYS, where="freeze receipt")
    require(type(receipt["schema_version"]) is int and receipt["schema_version"] == 1,
            "Invalid freeze schema")
    require(receipt["kind"] == "candidate_freeze" and receipt["candidate"] == relative,
            "Freeze receipt candidate mismatch")
    require(receipt["acceptance"] == "structural_only" and receipt["isolation"] == "not_a_sandbox",
            "Freeze receipt overstates acceptance/isolation")
    text(receipt["created_utc"], "freeze time")
    snapshot = receipt["registry_snapshot"]
    exact_keys(snapshot, {"path", "artifact_count", "sha256"}, where="registry snapshot")
    require(snapshot["path"] == "registry.json", "Registry snapshot path mismatch")
    _hash(snapshot["sha256"])
    state = _state(bundle, candidate, relative, snapshot["artifact_count"])
    require(snapshot == state["registry_snapshot"], "Registry prefix changed")
    require(receipt["route"] == state["route"], "Frozen route changed")
    require(receipt["candidate_files"] == state["candidate_files"], "Frozen candidate file set changed")
    require(receipt["commitments"] == state["commitments"], "Frozen commitments changed")
    require(type(receipt["revision_index"]) is int and receipt["revision_index"] >= 0,
            "Invalid revision index")
    if receipt["parent"] is None:
        require(receipt["revision"] is None and receipt["revision_index"] == 0,
                "Initial candidate cannot declare a revision")
    else:
        parent = receipt["parent"]
        exact_keys(parent, {"candidate", "receipt_path", "sha256"}, where="parent reference")
        _hash(parent["sha256"])
        parent_dir, parent_relative = _candidate(bundle, parent["candidate"])
        require(parent["receipt_path"] == parent_relative + "/freeze.json", "Parent receipt path mismatch")
        require(sha256(_path(bundle, parent["receipt_path"])) == parent["sha256"], "Parent receipt changed")
        previous = _verify(bundle, parent_dir, parent_relative, seen)
        require(receipt["revision_index"] == previous["revision_index"] + 1, "Broken revision index")
        _revision(receipt["revision"])
        changed = not _same_model(receipt, previous)
        require((receipt["revision"]["kind"] == "revise") == changed,
                "Revision kind disagrees with code/data/model changes")
    require(receipt["revision_index"] <= state["task"]["budget"]["revisions"], "Revision budget exceeded")
    return receipt


def verify_candidate(bundle: str | Path, candidate: str | Path) -> dict:
    """Verify every committed input, artifact, candidate file and parent lineage."""
    root = _bundle(bundle)
    directory, relative = _candidate(root, candidate)
    return _verify(root, directory, relative, set())


def _parent(bundle: Path, parent_receipt: dict | str | Path) -> dict:
    if isinstance(parent_receipt, dict):
        require(isinstance(parent_receipt.get("candidate"), str), "Parent candidate missing")
        directory, relative = _candidate(bundle, parent_receipt["candidate"])
        actual = _verify(bundle, directory, relative, set())
        require(actual == parent_receipt, "Supplied parent receipt differs from frozen receipt")
        return actual
    path = Path(parent_receipt)
    require(".." not in path.parts, "Parent path traversal is not allowed")
    if path.is_absolute():
        try:
            relative = path.relative_to(bundle).as_posix()
        except ValueError as error:
            raise ContractError("Parent receipt is outside bundle") from error
    else:
        relative = path.as_posix()
    parts = safe_relative(relative)
    require(len(parts) == 3 and parts[0] == "candidates" and parts[-1] == "freeze.json",
            "Parent must be a candidate freeze.json in this bundle")
    directory, candidate_relative = _candidate(bundle, "/".join(parts[:2]))
    return _verify(bundle, directory, candidate_relative, set())


def freeze_candidate(bundle: str | Path, candidate: str | Path,
                     parent_receipt: dict | str | Path | None = None,
                     revision: dict | None = None) -> dict:
    """Create freeze.json exclusively after checking the submission.

    ``parent_receipt`` may be a verified returned receipt or its file path.
    A child needs a revision description and consumes one revision. All existing
    files remain intact on validation failure; no generator is imported/run.
    """
    root = _bundle(bundle)
    directory, relative = _candidate(root, candidate)
    destination = _path(directory, "freeze.json", file=False)
    require(not destination.exists(), "Candidate is already frozen")
    state = _state(root, directory, relative)
    report_path = _path(directory, "source_check_report.json", file=False)
    if report_path.exists():
        # This trusted engine evaluates only declared source-statistic operators;
        # it never imports or executes the candidate generator. Recompute during
        # freeze to reject stale reports after model, plan or source changes.
        # Later verification remains a byte/hash check across environments.
        _path(directory, "source_checks.json")
        stored_report = read_json(_path(directory, "source_check_report.json"))
        from .source_checks import run_source_checks
        current_report = run_source_checks(root, directory)
        require(stored_report == current_report,
                "Source-check report is stale or differs from current declared checks")
    parent, index = None, 0
    receipt = {"schema_version": 1, "kind": "candidate_freeze",
               "created_utc": datetime.now(timezone.utc).isoformat(), "candidate": relative,
               "route": state["route"], "commitments": state["commitments"],
               "registry_snapshot": state["registry_snapshot"],
               "candidate_files": state["candidate_files"], "parent": None, "revision": revision,
               "revision_index": 0, "acceptance": "structural_only", "isolation": "not_a_sandbox"}
    if parent_receipt is None:
        require(revision is None, "Revision requires a parent candidate")
    else:
        previous = _parent(root, parent_receipt)
        require(previous["candidate"] != relative, "Candidate cannot parent itself")
        _revision(revision)
        index = previous["revision_index"] + 1
        require(index <= state["task"]["budget"]["revisions"], "Revision budget exceeded")
        changed = not _same_model(receipt, previous)
        require((revision["kind"] == "revise") == changed,
                "Revision kind disagrees with code/data/model changes")
        parent_path = previous["candidate"] + "/freeze.json"
        parent = {"candidate": previous["candidate"], "receipt_path": parent_path,
                  "sha256": sha256(_path(root, parent_path))}
    receipt.update(parent=parent, revision_index=index)
    # Check the read-set once more before the exclusive write; this is a race
    # diagnostic, not a claim of transactional/OS-enforced immutability.
    for relative_path, digest in receipt["commitments"].items():
        require(sha256(_path(root, relative_path)) == digest, "Artifact changed during freeze")
    require(_registry(root, receipt["registry_snapshot"]["artifact_count"])[0] == receipt["registry_snapshot"],
            "Registry prefix changed during freeze")
    try:
        with destination.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(receipt, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
    except FileExistsError as error:
        raise ContractError("Candidate is already frozen") from error
    return verify_candidate(root, directory)
