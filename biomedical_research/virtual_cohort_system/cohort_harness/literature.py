"""Task-bound publication access with append-only source registration.

This adapter reuses a screened gateway. Its binding, state, approval log and
registry are trusted procedural inputs, not authentication or an OS sandbox.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time

from .contracts import ContractError, require, validate_task
from .lifecycle import _bundle, _path, _registry, read_json, sha256
from ._vendor import literature_gateway as gateway

ACTIONS = ("init", "search", "fetch", "list-supplements", "fetch-supplement")
NOTICE = (
    "Task-bound screened literature access; exclusion aliases are a conservative "
    "text screen, not proof of no target-derived information. Binding, gateway "
    "state, logs and registry are trusted procedural inputs, not an OS sandbox."
)


def _write_new(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8") as out:
        json.dump(value, out, ensure_ascii=True, indent=2, allow_nan=False)
        out.write("\n")


def _configuration(task: dict) -> dict:
    aliases = task["information_policy"]["excluded_cohorts"]
    require(all(gateway.compact(alias) for alias in aliases),
            "Excluded cohort aliases must contain letters or numbers")
    queries, downloads = task["budget"]["source_queries"], task["budget"]["source_downloads"]
    return {
        "schema_version": 1,
        "budgets": {"queries": queries, "downloads": downloads,
                    "auxiliary_requests": 8 * (queries + downloads)},
        "limits": {"response_bytes": 16 * 1024 * 1024, "timeout_seconds": 30,
                   "search_page_size": 10, "table_cells": 1000000},
        "exclusions": {"compact_aliases": aliases, "regexes": []},
    }


def _prepare(bundle: Path, task: dict) -> Path:
    """Create or verify the single fixed gateway location for this bundle."""
    directory = _path(bundle, "gateway", file=False)
    config = _configuration(task)
    expected = {"schema_version": 1, "bundle": str(bundle), "task_sha256": sha256(bundle / "task.json"),
                "config_sha256": gateway.digest(gateway.encoded(config)),
                "session_relative_path": "gateway/session"}
    if not directory.exists():
        directory.mkdir()
        try:
            with (directory / "config.json").open("xb") as out:
                out.write(gateway.encoded(config))
            _write_new(directory / "binding.json", expected)
        except Exception:
            # Preserve partial initialization for explicit review; never silently reset.
            raise
    for path in directory.rglob("*"):
        _path(bundle, path.relative_to(bundle).as_posix(), file=path.is_file())
    binding = read_json(_path(bundle, "gateway/binding.json"))
    require(binding == expected, "Gateway task/bundle binding changed")
    require(sha256(_path(bundle, "gateway/config.json")) == expected["config_sha256"],
            "Gateway configuration changed")
    _path(bundle, "gateway/session", file=False)
    return directory


def _approved_bytes(bundle: Path, session: gateway.Session, artifact: dict) -> bytes:
    """Verify byte hash, metadata and an accepted event from this fixed session."""
    require(isinstance(artifact, dict) and set(artifact) == {"session_relative_path", "sha256", "bytes"},
            "Invalid gateway artifact record")
    relative = artifact["session_relative_path"]
    require(isinstance(relative, str) and re.fullmatch(r"approved/[a-f0-9]{64}\.[a-z]+", relative),
            "Invalid gateway artifact path")
    require(relative.split("/")[1].split(".")[0] == artifact["sha256"],
            "Artifact name/hash mismatch")
    path = _path(bundle, "gateway/session/" + relative)
    raw = path.read_bytes()
    require(type(artifact["bytes"]) is int and len(raw) == artifact["bytes"],
            "Gateway artifact size changed")
    require(gateway.digest(raw) == artifact["sha256"], "Gateway artifact hash changed")
    audit_path = _path(bundle, "gateway/session/audit.jsonl")
    approvals = []
    for line in audit_path.read_bytes().splitlines():
        event = gateway.parse_json(line)
        if (event.get("type") == "artifact_approved" and event.get("status") == "accepted"
                and event.get("config_sha256") == session.config_hash):
            approvals.append(event.get("artifact"))
    require(artifact in approvals, "Artifact lacks accepted gateway approval event")
    return raw


def _result_artifacts(session: gateway.Session, result: dict) -> list[tuple[str, dict]]:
    """Only artifacts returned by actual gateway operations are eligible."""
    if result.get("type") == "search_results":
        return [("search-" + result["approved_artifact"]["sha256"], result["approved_artifact"])]
    if result.get("type") == "article":
        identifier = result["pmcid"]
        parent = session.parent(identifier)  # Recheck complete XML+manifest+links.
        require(result["version"] == parent["version"], "Article state version mismatch")
        require(result["xml_artifact"] == parent["xml_artifact"]
                and result["approved_artifact"] == parent["text_artifact"],
                "Article state/artifact mismatch")
        return [(identifier, parent[k]) for k in ("xml_artifact", "text_artifact", "manifest_artifact")]
    if result.get("type") == "supplement":
        identifier = result["pmcid"]
        parent = session.parent(identifier)
        matches = [x for x in parent["supplements"] if x["supplement_id"] == result["supplement_id"]]
        require(len(matches) == 1 and matches[0]["status"] == "available"
                and matches[0]["source_url"] == result["source_url"]
                and result["parent_xml_sha256"] == parent["xml_artifact"]["sha256"],
                "Supplement parent linkage mismatch")
        return [(identifier, result["approved_artifact"])]
    return []


def _register_result(bundle: Path, session: gateway.Session, result: dict) -> list[dict]:
    """Append verified source artifacts; never rewrite or remove old entries."""
    _registry(bundle)
    registry_path = bundle / "registry.json"
    registry = read_json(registry_path)
    artifacts = []
    for source_id, artifact in _result_artifacts(session, result):
        raw = _approved_bytes(bundle, session, artifact)
        filename = artifact["session_relative_path"].split("/")[-1]
        relative = "sources/gateway/" + filename
        destination = _path(bundle, relative, file=False)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            require(destination.is_file() and sha256(destination) == artifact["sha256"],
                    "Registered source path conflicts with existing content")
        else:
            with destination.open("xb") as out:
                out.write(raw)
        entry = {"source_id": source_id, "path": relative, "sha256": artifact["sha256"],
                 "origin": "gateway", "screening": "approved"}
        if entry not in registry["artifacts"]:
            require(not any(x["source_id"] == source_id and x["path"] == relative
                            for x in registry["artifacts"]), "Registry source/path conflict")
            registry["artifacts"].append(entry)
        artifacts.append(entry)
    if artifacts:
        # Session lock serializes adapter writers. The registry remains trusted;
        # an out-of-band local writer is outside this procedural concurrency model.
        temporary = _path(bundle, "gateway/registry-pending.json", file=False)
        _write_new(temporary, registry)
        os.replace(temporary, registry_path)
        _registry(bundle)
        session.audit({"type": "bundle_registration", "status": "accepted",
                       "task_sha256": sha256(bundle / "task.json"), "artifacts": artifacts})
    return artifacts


def run_literature(bundle: str | Path, action: str, *, query: str | None = None,
                   limit: int = 10, cursor: str = "*", pmcid: str | None = None,
                   version: int | None = None, supplement_id: str | None = None) -> dict:
    """Perform one action using the bundle's sole persistent gateway session.

    Retrieval permissions are literal action names, e.g. literature.search.
    A fetch may perform a screened metadata lookup and consumes query budget.
    Returns categorized errors without rejected source contents or tracebacks.
    """
    session = None
    started = time.monotonic()
    result = None
    try:
        require(action in ACTIONS, "Unknown literature action")
        root = _bundle(bundle)
        task = read_json(_path(root, "task.json"))
        validate_task(task)
        require(task["information_policy"]["mode"] == "published_evidence",
                "prior_only tasks cannot initialize or use literature retrieval")
        if action != "init":
            require("literature." + action in task["information_policy"]["allowed_tools"],
                    "Literature action not allowed by task")
        _registry(root)  # Never create/reset a registry to conceal previous artifacts.
        directory = _prepare(root, task)
        session = gateway.Session(directory / "session", directory / "config.json")
        if action == "init":
            result = {"type": "literature_session", "status": "ok",
                      "task_id": task["task_id"], "session": "gateway/session"}
        elif action == "search":
            require(isinstance(query, str), "search requires query")
            require(type(limit) is int and isinstance(cursor, str), "Invalid search pagination")
            result = session.search(query, limit, cursor)
        elif action == "fetch":
            require(isinstance(pmcid, str), "fetch requires pmcid")
            require(version is None or (type(version) is int and version >= 1), "Invalid article version")
            result = session.fetch(pmcid, version)
        elif action == "list-supplements":
            require(isinstance(pmcid, str), "list-supplements requires pmcid")
            result = session.list_supplements(pmcid)
        else:
            require(isinstance(pmcid, str) and isinstance(supplement_id, str),
                    "fetch-supplement requires pmcid and supplement_id")
            result = session.fetch_supplement(pmcid, supplement_id)
        result["registered_artifacts"] = _register_result(root, session, result)
    except gateway.GatewayError as error:
        result = {"type": "literature_error",
                  "status": "rejected" if error.reason.startswith("excluded_") else "error",
                  "reason": error.reason}
        if error.content_sha256:
            result["content_sha256"] = error.content_sha256
    except ContractError as error:
        result = {"type": "literature_error", "status": "error", "reason": "task_or_provenance_violation",
                  "detail": str(error)}
    except KeyboardInterrupt:
        result = {"type": "literature_error", "status": "error", "reason": "interrupted_command"}
    except Exception:
        result = {"type": "literature_error", "status": "error", "reason": "local_or_gateway_failure"}
    finally:
        elapsed = time.monotonic() - started
        if result is None:
            result = {"type": "literature_error", "status": "error", "reason": "interrupted_command"}
        result["elapsed_seconds"] = elapsed
        result["notice"] = NOTICE
        if session is not None:
            try:
                session.state["usage"]["command_elapsed_seconds"] += elapsed
                session.save_state()
                result["usage"] = dict(session.state["usage"])
                result["budgets"] = dict(session.config["budgets"])
                session.audit({"type": "adapter_command", "command": action, "status": result["status"],
                               "elapsed_seconds": elapsed, "usage": result["usage"],
                               "reason": result.get("reason")})
            except Exception:
                result = {"type": "literature_error", "status": "error",
                          "reason": "session_finalization_failure", "elapsed_seconds": elapsed}
            finally:
                try:
                    session.close()
                except Exception:
                    result = {"type": "literature_error", "status": "error",
                              "reason": "session_close_failure", "elapsed_seconds": elapsed}
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("init")
    search = sub.add_parser("search")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--cursor", default="*")
    for name in ("fetch", "list-supplements", "fetch-supplement"):
        command = sub.add_parser(name)
        command.add_argument("--pmcid", required=True)
        if name == "fetch":
            command.add_argument("--version", type=int)
        if name == "fetch-supplement":
            command.add_argument("--supplement-id", required=True)
    values = vars(parser.parse_args(argv))
    result = run_literature(**values)
    print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
    return 0 if result["status"] in {"ok", "accepted", "selection_required"} else 2


if __name__ == "__main__":
    raise SystemExit(main())

