"""Declared use coverage and execution-bound cross-variable diagnostics.

No generator execution, source retrieval, clinical coefficient or target read.
Host use contracts define requested uses/rules; the author declares evidence
coverage and applicability. Structural validation does not certify those claims.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import analysis_evidence as coverage, execution, lifecycle as lc
from .contracts import ContractError, exact_keys, number, require, string_list, text, validate_task

CONTRACT = "input/use_contract.json"
PLAN = "coherence_v1.json"
EVIDENCE_PLAN = "analysis_evidence.json"


def _normal(value):
    value = dict(value)
    for key in ("exposures", "conditioning", "adjustment"):
        value[key] = sorted(value[key])
    return json.dumps(value, sort_keys=True, allow_nan=False)


def _columns(operator):
    return ([operator["left"], operator["right"]] if operator["kind"] == "order"
            else [operator["total"], *operator["components"]])


def validate_contract(contract, task):
    """Host contract validation; invalid host policy is not an author finding."""
    exact_keys(contract, {"schema_version", "analyses", "coherence_rules"}, where="use contract")
    require(type(contract["schema_version"]) is int and contract["schema_version"] == 1,
            "Use contract version must be 1")
    columns = {c["name"]: c for c in task["columns"]}
    outcomes = {name for name, c in columns.items() if c["role"] != "identifier"}
    require(isinstance(contract["analyses"], list) and bool(contract["analyses"]), "Requested uses required")
    ids = set()
    for item in contract["analyses"]:
        exact_keys(item, {"id", "estimand"}, where="required analysis")
        text(item["id"], "analysis ID")
        require(item["id"] not in ids, "Duplicate required analysis ID")
        ids.add(item["id"])
        coverage._estimand(item["estimand"], outcomes)
    require(isinstance(contract["coherence_rules"], list), "Coherence rules must be a list")
    ids = set()
    for rule in contract["coherence_rules"]:
        exact_keys(rule, {"id", "operator", "measurement_interpretation", "basis"}, where="required rule")
        text(rule["id"], "rule ID")
        require(rule["id"] not in ids, "Duplicate required rule ID")
        ids.add(rule["id"])
        text(rule["measurement_interpretation"], "measurement interpretation")
        basis = rule["basis"]
        exact_keys(basis, {"kind", "reference", "locator"}, where="rule basis")
        require(basis["kind"] in {"source", "algebraic", "task"}, "Unsupported rule basis")
        text(basis["reference"], "basis reference")
        text(basis["locator"], "basis locator")
        op = rule["operator"]
        require(isinstance(op, dict) and op.get("kind") in {"order", "sum"}, "Unsupported coherence operator")
        fields = {"left", "right"} if op["kind"] == "order" else {"total", "components"}
        exact_keys(op, {"kind", "unit", "tolerance"} | fields, where="coherence operator")
        text(op["unit"], "operator unit")
        number(op["tolerance"], "absolute tolerance")
        require(op["tolerance"] >= 0, "Absolute tolerance must be nonnegative")
        if op["kind"] == "sum":
            string_list(op["components"], "sum components", nonempty=True)
            text(op["total"], "sum total")
        else:
            text(op["left"], "left variable"); text(op["right"], "right variable")
        names = _columns(op)
        require(len(names) == len(set(names)), "Coherence variables must be distinct")
        require(all(name in columns and columns[name]["kind"] == "number" and
                    columns[name]["role"] != "identifier" for name in names),
                "Coherence requires known nonidentifier numeric variables")
        require(all(columns[name]["unit"] == op["unit"] for name in names),
                "Coherence units must match exactly; no implicit conversion")


def _host(root):
    task = lc.read_json(lc._path(root, "task.json")); validate_task(task)
    contract_path = lc._path(root, CONTRACT)
    contract = lc.read_json(contract_path); validate_contract(contract, task)
    return task, contract, lc.sha256(contract_path)


def _plans(root, directory, task, contract, contract_sha):
    evidence = lc.read_json(lc._path(directory, "evidence.json"))
    spec = lc.read_json(lc._path(directory, "model_spec.json"))
    manifest = lc.read_json(lc._path(directory, EVIDENCE_PLAN))
    report = coverage.summarize_analysis_evidence(manifest, task, evidence, spec)
    required = {x["id"]: x["estimand"] for x in contract["analyses"]}
    actual = {x["id"]: x["estimand"] for x in manifest["analyses"]}
    require(actual.keys() == required.keys(), "Analysis declaration must cover exactly the requested IDs")
    require(all(_normal(actual[key]) == _normal(required[key]) for key in required),
            "Declared estimand differs from the pinned requested estimand")
    plan = lc.read_json(lc._path(directory, PLAN))
    exact_keys(plan, {"schema_version", "use_contract_sha256", "rules"}, where="coherence plan")
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1, "Coherence plan version must be 1")
    require(plan["use_contract_sha256"] == contract_sha, "Coherence plan use-contract hash differs")
    require(isinstance(plan["rules"], list), "Coherence rule declarations must be a list")
    required_rules = {r["id"]: r for r in contract["coherence_rules"]}
    assumptions = {a["id"] for a in spec["assumptions"]}
    declared = {}
    for rule in plan["rules"]:
        exact_keys(rule, {"id", "applicability", "reason", "assumption_ids"}, where="coherence declaration")
        text(rule["id"], "declared rule ID")
        require(rule["id"] not in declared, "Duplicate declared rule ID")
        require(isinstance(rule["applicability"], str) and
                rule["applicability"] in {"applicable", "unresolved", "not_applicable"}, "Invalid rule applicability")
        text(rule["reason"], "applicability reason")
        string_list(rule["assumption_ids"], "coherence assumptions")
        require(set(rule["assumption_ids"]) <= assumptions, "Unknown coherence assumption ID")
        declared[rule["id"]] = rule
    require(declared.keys() == required_rules.keys(), "Coherence declarations must cover exactly the required rules")
    report["requested_id_and_estimand_coverage"] = "exact_pinned_contract"
    report["limitations"][0] = "Requested ID/estimand completeness is checked against the host contract; scientific support is still declared."
    return report, [{**required_rules[key], **declared[key]} for key in required_rules]


def _bindings(root, directory, contract_sha):
    result = {"use_contract_sha256": contract_sha, "task_sha256": lc.sha256(root/"task.json")}
    for key, path in (("request", root/"request.json"), ("analysis_evidence", directory/EVIDENCE_PLAN),
                      ("coherence_plan", directory/PLAN), ("evidence", directory/"evidence.json"),
                      ("model_spec", directory/"model_spec.json")):
        # Missing author files are represented, not followed outside their root.
        checked = lc._path(root, path.relative_to(root).as_posix(), file=False)
        result[key+"_sha256"] = lc.sha256(checked) if checked.is_file() else None
    return result


def preflight(bundle, candidate):
    """Inspect declarations only. Return author errors; raise host/path errors."""
    root = lc._bundle(bundle)
    if isinstance(candidate, str) and "/" not in candidate and "\\" not in candidate:
        candidate = "candidates/" + candidate
    directory, relative = lc._candidate(root, candidate)
    task, contract, contract_sha = _host(root)
    bindings = _bindings(root, directory, contract_sha)
    base = {"schema_version": 1, "candidate": relative, "scope": "declarations_only",
            "scientific_validity": "not_certified", "basis_authenticated": False, "bindings": bindings}
    try:
        evidence, rules = _plans(root, directory, task, contract, contract_sha)
    except (ContractError, json.JSONDecodeError, UnicodeError) as error:
        return {**base, "status": "validation_error", "errors": [str(error)],
                "evidence_coverage": None, "coherence": None}
    require(lc.sha256(root/CONTRACT) == contract_sha, "Host use contract changed during preflight")
    return {**base, "status": "ready", "errors": [], "evidence_coverage": evidence,
            "coherence": rules}


def calculate_rule(frame, rule):
    """Raw numerical relation counts, separately from declared applicability."""
    op = rule["operator"]; names = _columns(op)
    missing_columns = [name for name in names if name not in frame]
    result = {"id": rule["id"], "operator": op, "n_total": len(frame),
              "applicability": rule["applicability"], "applicability_reason": rule["reason"],
              "assumption_ids": rule["assumption_ids"], "measurement_interpretation": rule["measurement_interpretation"],
              "basis": rule["basis"], "basis_authenticated": False,
              "n_missing": 0, "n_nonfinite": 0, "n_arithmetic_nonfinite": 0,
              "n_evaluated": 0, "n_unknown": len(frame), "n_violating": 0, "n_satisfying": 0,
              "violation_fraction_evaluated": None, "max_violation": None, "unit": op["unit"]}
    if missing_columns:
        return {**result, "numerical_status": "cannot_compute", "assessment": "unresolved",
                "reason": "Missing columns: " + ", ".join(missing_columns)}
    data = frame[names].apply(pd.to_numeric, errors="raise").to_numpy(dtype=float)
    missing = np.isnan(data).any(axis=1)
    nonfinite = (~np.isfinite(data)).any(axis=1) & ~missing
    complete = data[~(missing | nonfinite)]
    with np.errstate(over="ignore", invalid="ignore"):
        delta = (complete[:, 0] - complete[:, 1] if op["kind"] == "order"
                 else np.abs(complete[:, 0] - np.sum(complete[:, 1:], axis=1)))
    arithmetic_bad = ~np.isfinite(delta)
    delta = delta[~arithmetic_bad]
    violating = delta > op["tolerance"]
    n = len(delta); bad = int(violating.sum())
    result.update(n_missing=int(missing.sum()), n_nonfinite=int(nonfinite.sum()),
                  n_arithmetic_nonfinite=int(arithmetic_bad.sum()), n_evaluated=n,
                  n_unknown=len(frame)-n, n_violating=bad, n_satisfying=n-bad,
                  violation_fraction_evaluated=bad/n if n else None,
                  max_violation=float(max(0., delta.max())) if n else None)
    numerical = "violations_observed" if bad else ("no_violations_observed" if n else "cannot_compute")
    assessment = ("contradicted" if bad else ("observed_consistent" if n and n == len(frame) else "unresolved"))
    if rule["applicability"] != "applicable":
        assessment = rule["applicability"]
    return {**result, "numerical_status": numerical, "assessment": assessment,
            "reason": "Counts retain every row; consistency is conditional on the declared interpretation, not biological validation."}


def analyze(output_path, task_path, request_path):
    """Host analysis entrypoint used by unchanged adaptive_session_v2."""
    paths = [Path(p).absolute() for p in (output_path, task_path, request_path)]
    require(not any(".." in p.parts for p in paths), "Analysis path traversal is not allowed")
    output, task_path, request_path = paths
    root = lc._bundle(task_path.parent)
    require(task_path == lc._path(root, "task.json") and request_path == lc._path(root, "request.json"),
            "Analysis inputs must use canonical bundle task/request paths")
    relative = output.relative_to(root).as_posix() if output.is_relative_to(root) else ""
    parts = relative.split("/")
    require(len(parts) == 4 and parts[0] == "executions" and parts[2:] == ["output", "generated.csv"],
            "Analysis requires a canonical execution output")
    require(output == lc._path(root, relative), "Output path identity differs")
    receipt = execution.verify_execution(root, parts[1])
    require(receipt["status"] == "success", "Analysis requires successful execution")
    directory, candidate = lc._candidate(root, receipt["candidate"])
    result = preflight(root, candidate)
    result.update(scope="execution_bound_analysis_use_diagnostics", run_id=parts[1],
                  source_population_replayed=False, output_link_verified=True)
    result["bindings"].update(output_sha256=lc.sha256(output),
                              execution_receipt_sha256=lc.sha256(output.parent.parent/"execution.json"),
                              candidate_freeze_sha256=lc.sha256(directory/"freeze.json"))
    if result["status"] == "ready":
        frame = lc.read_table(output, lc.read_json(task_path), output=True)
        result["coherence"] = [calculate_rule(frame, rule) for rule in result["coherence"]]
        result["status"] = "computed"
    execution.verify_execution(root, parts[1])
    require(lc.sha256(root/CONTRACT) == result["bindings"]["use_contract_sha256"], "Host use contract changed during analysis")
    for key, value in _bindings(root, directory, result["bindings"]["use_contract_sha256"]).items():
        require(result["bindings"][key] == value, "Analysis-use input changed during analysis")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True); parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    print(json.dumps(preflight(args.bundle, args.candidate), indent=2, allow_nan=False))


if __name__ == "__main__": main()
