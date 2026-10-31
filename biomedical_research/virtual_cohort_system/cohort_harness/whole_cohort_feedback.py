"""Bind permitted source diagnostics to an existing whole-cohort execution.

This collector never executes a generator, reads a supplied comparison CSV, or
reconstructs a source population. Its only data input is a successfully verified
execution's output. Linkage is relative to retained hashes, not an authorship,
biological-validity or Agent-isolation guarantee.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys

import numpy as np
import pandas as pd

from . import contracts, execution, lifecycle, source_checks, source_replay
from .contracts import exact_keys, require, string_list, text
from .lifecycle import _bundle, _candidate, _path, read_json, read_table, sha256, verify_candidate
from .source_checks import NotComputable, apply_operator


PLAN = "whole_cohort_feedback.json"
FOLDER = "whole_cohort_feedback"


def _resolve_candidate(root, candidate):
    value = str(candidate)
    if not Path(value).is_absolute() and "/" not in value and "\\" not in value:
        value = "candidates/" + execution._name(value)
    return _candidate(root, value)


def _engine():
    modules = (contracts, execution, lifecycle, source_checks, source_replay)
    result = {Path(module.__file__).name: sha256(module.__file__) for module in modules}
    result[Path(__file__).name] = sha256(__file__)
    return result


def _read_plan(directory, task):
    plan = read_json(_path(directory, PLAN))
    exact_keys(plan, {"schema_version", "population", "measurement", "assumption_ids", "checks"},
               where="whole-cohort feedback plan")
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1,
            "Invalid whole-cohort feedback schema")
    require(plan["population"] == task["population"],
            "Feedback population must name the actual execution task; no source-context transformation is implemented")
    exact_keys(plan["measurement"], {"mode", "description"}, where="feedback measurement")
    require(plan["measurement"]["mode"] == "identity", "Only identity measurement is implemented")
    text(plan["measurement"]["description"], "feedback measurement description")
    assumptions = {item["id"] for item in read_json(directory / "model_spec.json")["assumptions"]}
    string_list(plan["assumption_ids"], "feedback population assumptions")
    require(set(plan["assumption_ids"]) <= assumptions, "Unknown feedback population assumption")
    require(isinstance(plan["checks"], list) and bool(plan["checks"]), "Feedback checks must be nonempty")
    evidence = {item["id"]: item for item in read_json(directory / "evidence.json")["items"]}
    ids = set()
    for check in plan["checks"]:
        exact_keys(check, {"id", "evidence_id", "status", "operator", "assumption_ids", "reason"},
                   where="whole-cohort feedback check")
        key = execution._name(check["id"])
        require(key.casefold() not in ids, "Duplicate feedback check ID")
        ids.add(key.casefold())
        require(check["evidence_id"] in evidence, "Unknown feedback evidence ID")
        string_list(check["assumption_ids"], "feedback check assumptions")
        require(set(check["assumption_ids"]) <= assumptions, "Unknown feedback check assumption")
        text(check["reason"], "feedback check reason")
        if check["status"] == "not_computable":
            require(check["operator"] is None, "Declared not-computable check must have null operator")
        else:
            source_replay._check_metadata(check, evidence, assumptions, plan["assumption_ids"])
    return plan, evidence


def _compute(root, directory, relative, run_id, feedback_id):
    frozen = verify_candidate(root, directory)
    task = read_json(root / "task.json")
    require(task["mode"] == "whole_cohort", "Whole-cohort feedback requires whole_cohort mode")
    require(not _path(root, "observed.csv", file=False).exists(), "Observed input is forbidden")
    plan, evidence = _read_plan(directory, task)
    receipt = execution.verify_execution(root, execution._name(run_id))
    require(receipt["candidate"] == relative, "Execution belongs to a different candidate")
    require(receipt["status"] == "success", "Feedback requires a successful verified execution")
    require(receipt["route"] == frozen["route"], "Execution and candidate routes differ")
    output = _path(root, f"executions/{run_id}/output/generated.csv")
    frame = read_table(output, task, output=True)
    records = []
    for check in plan["checks"]:
        item = evidence[check["evidence_id"]]
        record = {
            "id": check["id"], "evidence_id": item["id"], "source_id": item["source_id"],
            "declared_status": check["status"], "status": check["status"],
            "assumption_ids": sorted(set(plan["assumption_ids"]) | set(check["assumption_ids"])),
            "reason": check["reason"], "operator": check["operator"],
            "reported_value": item["estimate"], "reported_uncertainty": item["uncertainty"],
            "calculation": None, "difference": None, "unavailable_reason": None,
        }
        if check["status"] == "not_computable":
            record["unavailable_reason"] = check["reason"]
        else:
            try:
                calculated = apply_operator(frame, check["operator"])
                record["calculation"] = calculated
                difference = calculated["value"] - item["estimate"]
                require(source_checks.finite(difference), "Feedback difference is nonfinite")
                record["difference"] = difference
            except NotComputable as error:
                record["status"] = "not_computable"
                record["unavailable_reason"] = str(error)
        records.append(record)
    bindings = {
        "task_sha256": sha256(root / "task.json"),
        "candidate_freeze_sha256": sha256(directory / "freeze.json"),
        "recipe_sha256": sha256(directory / PLAN),
        "evidence_sha256": sha256(directory / "evidence.json"),
        "model_spec_sha256": sha256(directory / "model_spec.json"),
        "execution_receipt_sha256": sha256(root / f"executions/{run_id}/execution.json"),
        "generated_table_sha256": sha256(output),
    }
    return {
        "schema_version": 1, "kind": "whole_cohort_execution_feedback", "feedback_id": feedback_id,
        "candidate": relative, "run_id": run_id, "status": "complete", "route": frozen["route"],
        "output_link_verified": True, "generator_execution_recorded": receipt["generator_executed"],
        "agent_authorship_verified": False, "agent_isolation": "not_provided",
        "scientific_validity": "not_assessed", "source_context_validity": "not_certified",
        "population": task["population"], "measurement": plan["measurement"],
        "bindings": bindings, "engine_sha256": _engine(),
        "calculator_runtime": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__},
        "checks": records, "n_computable": sum(x["calculation"] is not None for x in records),
        "n_not_computable": sum(x["status"] == "not_computable" for x in records),
        "limitations": [
            "No source population reconstruction or measurement conversion is performed.",
            "Declared applicability and the absence of individual records in evidence require independent review.",
            "Direct rows are copied and checked; their LLM authorship is not established by this receipt.",
            "Source discrepancies are diagnostics, not target validity or a pooled scientific quality score.",
            "Hashes are commitments relative to retained artifacts, not cryptographic signatures against a host user.",
        ],
    }


def collect_feedback(bundle, candidate, run_id, feedback_id):
    """Collect source-only diagnostics without changing a frozen candidate."""
    root = _bundle(bundle)
    directory, relative = _resolve_candidate(root, candidate)
    feedback_id = execution._name(feedback_id)
    destination = _path(root, f"{FOLDER}/{feedback_id}", file=False)
    require(not destination.exists(), "Feedback ID already exists; previous records are preserved")
    report = _compute(root, directory, relative, run_id, feedback_id)
    report["created_utc"] = datetime.now(timezone.utc).isoformat()
    destination.parent.mkdir(exist_ok=True)
    destination.mkdir()
    execution._write(destination / "feedback.json", report)
    # Re-read commitments and numerical values after the exclusive write. A
    # failure leaves its attempted report intact; it is not silently overwritten.
    return verify_feedback(root, feedback_id, candidate=relative, run_id=run_id)


def verify_feedback(bundle, feedback_id, *, candidate=None, run_id=None):
    """Recompute permitted statistics and verify every declared linkage."""
    root = _bundle(bundle)
    feedback_id = execution._name(feedback_id)
    folder = _path(root, f"{FOLDER}/{feedback_id}", file=False)
    report = read_json(_path(folder, "feedback.json"))
    files = []
    for path in folder.rglob("*"):
        relative = path.relative_to(folder).as_posix()
        _path(folder, relative, file=False)
        require(path.is_file(), "Unexpected feedback subdirectory or nonregular entry")
        files.append(relative)
    require(files == ["feedback.json"], "Feedback artifact set changed")
    require(isinstance(report, dict), "Feedback receipt must be an object")
    directory, relative = _resolve_candidate(root, report["candidate"])
    if candidate is not None:
        require(_resolve_candidate(root, candidate)[1] == relative, "Feedback is for a different candidate")
    if run_id is not None:
        require(report["run_id"] == execution._name(run_id), "Feedback is for a different execution")
    text(report.get("created_utc"), "feedback timestamp")
    expected = _compute(root, directory, relative, report["run_id"], feedback_id)
    expected["created_utc"] = report["created_utc"]
    require(report == expected, "Feedback report changed or no longer matches recomputed diagnostics")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("collect", "verify"))
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--feedback-id", required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "collect":
            result = collect_feedback(args.bundle, args.candidate, args.run_id, args.feedback_id)
        else:
            result = verify_feedback(args.bundle, args.feedback_id, candidate=args.candidate, run_id=args.run_id)
        import json
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        import json
        print(json.dumps({"status": "error", "type": type(error).__name__, "message": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
