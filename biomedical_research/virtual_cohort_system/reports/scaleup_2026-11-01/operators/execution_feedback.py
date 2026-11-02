"""Supplemental diagnostics on a verified whole-cohort generator execution.

No generator, supplied comparison table, legacy-collector fallback, or implicit
source reconstruction. Prospective review is NOT the utility's frame approval.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from cohort_harness import contracts, execution, semantic_feedback_v1 as semantic
from cohort_harness.lifecycle import _bundle, _candidate, _path, read_json, read_table, sha256, verify_candidate

import contextual_statistics as statistics

FILE = "context_feedback_v1.json"
FOLDER = "context_feedback_v1"
require = statistics.require
exact = statistics.exact
text = statistics.text
canonical = statistics.canonical


def _digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def declaration_digest(declaration):
    """Review commitment, excluding only the separately checked review records."""
    payload = copy.deepcopy(declaration)
    payload.pop("context_review", None)
    for check in payload["checks"]:
        if check["proxy"] is not None:
            check["proxy"].pop("review", None)
    return _digest(payload)


def proxy_digest(declaration, check_id):
    return _digest({"declaration_sha256": declaration_digest(declaration),
                    "check_id": check_id, "role": "assumption_defined_proxy"})


def _review(review, expected):
    exact(review, {"decision", "independent", "reviewer_id", "producer_id", "reviewed_utc", "reason", "approved_sha256"})
    require(review["decision"] == "approved" and review["independent"] is True, "Independent review required")
    for key in ("reviewer_id", "producer_id", "reviewed_utc", "reason"):
        text(review[key])
    require(review["reviewer_id"].strip().casefold() != review["producer_id"].strip().casefold(), "Reviewer is producer")
    require(review["approved_sha256"] == expected, "Review commitment mismatch")


def _assumptions(values, known, *, nonempty=False):
    contracts.string_list(values, "context assumption IDs", nonempty=nonempty)
    require(len(values) == len(set(values)) and set(values) <= known, "Duplicate/unknown context assumption IDs")


def _resolve(root, candidate):
    value = str(candidate)
    if not Path(value).is_absolute() and "/" not in value and "\\" not in value:
        value = "candidates/" + execution._name(value)
    return _candidate(root, value)


def _column_types(operator, columns):
    names, operand = statistics.validate_operator(operator)
    require(names <= set(columns), "Unknown task variable")
    require(columns[operand]["kind"] in {"number", "integer"}, "Numeric task operand required")
    for predicate in operator["selection"]:
        column = columns[predicate["column"]]
        numeric = column["kind"] in {"number", "integer"}
        numeric_category = column["kind"] == "category" and all(type(v) in {int, float} for v in column["categories"])
        values = predicate["value"] if predicate["op"] == "in" else [predicate["value"]]
        require(all(statistics.finite(v) if numeric or numeric_category else type(v) is str for v in values),
                "Predicate/task type mismatch")
        if predicate["op"] in {"lt", "le", "gt", "ge"}:
            require(numeric, "Ordered selection requires numeric non-categorical task variable")
    return names


def _declaration(root, directory, frozen, relative, task, semantic_plan):
    require(relative + "/" + FILE in frozen["candidate_files"], "Context declaration must be frozen")
    declaration = read_json(_path(directory, FILE))
    exact(declaration, {"schema_version", "task_sha256", "evidence_sha256", "model_spec_sha256", "semantics_sha256",
                        "table_context", "assumption_ids", "checks", "context_review"})
    require(type(declaration["schema_version"]) is int and declaration["schema_version"] == 1, "Invalid context version")
    for key, path in {"task_sha256": root / "task.json", "evidence_sha256": directory / "evidence.json",
                      "model_spec_sha256": directory / "model_spec.json", "semantics_sha256": directory / semantic.FILE}.items():
        require(declaration[key] == sha256(path), "Declaration hash mismatch: " + key)
    evidence = read_json(_path(directory, "evidence.json"))
    ids = contracts.validate_evidence(evidence, task)
    spec = read_json(_path(directory, "model_spec.json"))
    contracts.validate_spec(spec, ids)
    known = {item["id"] for item in spec["assumptions"]}
    _assumptions(declaration["assumption_ids"], known, nonempty=True)
    checks = declaration["checks"]
    require(isinstance(checks, list) and bool(checks), "Nonempty supplemental checks required")
    columns = {column["name"]: column for column in task["columns"]}
    items = {item["id"]: item for item in evidence["items"]}
    sources = {source["id"]: source for source in evidence["sources"]}
    gates = {gate["id"]: gate for gate in semantic_plan["checks"]}
    context = declaration["table_context"]
    all_names = set()
    seen = set()
    for check in checks:
        exact(check, {"id", "evidence_id", "semantic_check_id", "operator", "source", "proxy"})
        name = execution._name(check["id"])
        require(name.casefold() not in seen, "Duplicate supplemental check ID")
        seen.add(name.casefold())
        names = _column_types(check["operator"], columns)
        all_names |= names
        require(check["evidence_id"] in items and check["semantic_check_id"] in gates, "Unknown evidence/v1 check")
        item, gate = items[check["evidence_id"]], gates[check["semantic_check_id"]]
        binding = gate["semantics"]
        require(gate["evidence_id"] == item["id"], "v1 evidence linkage mismatch")
        source = check["source"]
        statistics.descriptor(source, names, source=True)
        original = sources[item["source_id"]]
        require(source["source_id"] == item["source_id"] and source["locator"] == item["locator"], "Source identity/locator mismatch")
        require(source["population"] == original["population"] and source["measurement"] == original["measurement"],
                "Full evidence source population/measurement mismatch")
        require(source["weights"] == binding["weights"], "Source weights differ from frozen v1 semantics")
        role = {"ci": "estimator_confidence_interval", "se": "estimator_standard_error", "not_reported": "not_reported"}
        expected_role = role.get(item["uncertainty"]["kind"],
                                 "between_person_dispersion" if binding["uncertainty_role"] == "individual_dispersion" else "unresolved")
        require(source["uncertainty_role"] == expected_role, "Source uncertainty role mismatch; no uncertainty conversion")
        operator = check["operator"]
        require(source["definition_status"] == "specified" and canonical(source["operator"]) == canonical(operator),
                "Supplemental operator must retain the declared source estimator and selection")
        require(operator["unit"] == item["unit"] and not item["adjustment"], "Evidence unit/adjustment mismatch")
        operand = operator["column"] if operator["kind"] == "geometric_mean" else operator["event"]["column"]
        require(set(item["variables"]) == {operand}, "Evidence variable roles mismatch")
        require(source["variable_scales"][operand] == "original", "Source operand must be original scale")
        require(set(source["variable_scales"].values()) <= {"original", "categorical"}, "Unresolved/log source selection scale")
        for selection in operator["selection"]:
            if selection["op"] in {"lt", "le", "gt", "ge"}:
                require(source["variable_scales"][selection["column"]] == "original", "Ordered source selection requires original scale")
        if operator["kind"] == "geometric_mean":
            require(item["kind"] == "reported_other" and item.get("statistic_name") == "geometric_mean",
                    "Geometric mean must retain reported_other/statistic_name=geometric_mean")
            require(item["estimate"] > 0, "Reported geometric mean must be positive")
            require(gate["semantic_status"] == "unavailable" and binding["source_operator"] is None,
                    "Frozen v1 cannot claim geometric mean support")
        else:
            require(item["kind"] == "proportion", "Prevalence evidence kind mismatch")
            native = {key: value for key, value in operator.items() if key != "selection_missing_policy"}
            require(binding["definition_status"] == "specified" and
                    semantic._signature(binding["source_operator"]) == semantic._signature(native), "v1 proportion definition mismatch")
        for variable in names:
            require(source["variable_units"][variable] == columns[variable]["unit"], "Source/task units differ; no conversion")
        proxy = check["proxy"]
        if proxy is not None:
            exact(proxy, {"assumption_ids", "reason", "review"})
            _assumptions(proxy["assumption_ids"], known, nonempty=True)
            text(proxy["reason"])
            _review(proxy["review"], proxy_digest(declaration, name))
    statistics.descriptor(context, all_names, source=False)
    require(context["population"] == task["population"], "Table context must equal actual task population")
    # The frozen v1 recipe already declares the actual task measurement; bind it.
    recipe = read_json(_path(directory, "whole_cohort_feedback.json"))
    require(context["measurement"] == recipe["measurement"]["description"], "Task measurement declaration mismatch")
    for variable in all_names:
        require(context["variable_units"][variable] == columns[variable]["unit"], "Table/task units differ")
        scale = context["variable_scales"][variable]
        require(scale in {"original", "categorical"}, "Unsupported table scale")
        if scale == "categorical":
            require(columns[variable]["kind"] in {"category", "string"}, "Categorical scale/task type mismatch")
    if context["kind"] == "analytic_fixture":
        require(all(check["proxy"] is None for check in checks), "Analytic fixtures cannot claim source proxy comparisons")
    _review(declaration["context_review"], declaration_digest(declaration))
    return declaration, items


def _prepare(bundle, candidate, run_id):
    root = _bundle(bundle)
    directory, relative = _resolve(root, candidate)
    run_id = execution._name(run_id)
    task = read_json(_path(root, "task.json"))
    contracts.validate_task(task)
    require(task["mode"] == "whole_cohort", "Only whole_cohort execution is supported")
    require(not _path(root, "observed.csv", file=False).exists(), "Observed input is forbidden")
    frozen = verify_candidate(root, directory)
    require(frozen["route"] == "generator.py", "Supplement requires a generator execution, not direct rows")
    semantic_plan = semantic.preflight(root, relative)
    declaration, items = _declaration(root, directory, frozen, relative, task, semantic_plan)
    receipt = execution.verify_execution(root, run_id)
    require(receipt["status"] == "success" and receipt["generator_executed"] is True and receipt["route"] == "generator.py",
            "Successful recorded generator execution required")
    require(receipt["candidate"] == relative and receipt["candidate_freeze_sha256"] == sha256(directory / "freeze.json"),
            "Execution/candidate freeze linkage mismatch")
    return root, directory, relative, task, declaration, items


def _compute(prepared, run_id, feedback_id, semantic_feedback_id):
    root, directory, relative, task, declaration, items = prepared
    v1 = semantic.verify_feedback(root, semantic_feedback_id, candidate=relative, run_id=run_id)
    # v1 retains ordinary dict equality (True == 1); preserve its verification
    # and add the same typed-JSON guard used by conditional_feedback_v1.
    typed_expected = semantic._compute(root, directory, relative, run_id, semantic_feedback_id)
    typed_expected["created_utc"] = v1["created_utc"]
    require(canonical(v1) == canonical(typed_expected), "Typed v1 receipt changed")
    require(v1["kind"] == "semantic_whole_cohort_feedback_v1" and v1["output_link_verified"] is True,
            "Verified semantic_feedback_v1 receipt required")
    output = _path(root, f"executions/{run_id}/output/generated.csv")
    bindings = {"task_sha256": sha256(root / "task.json"), "candidate_freeze_sha256": sha256(directory / "freeze.json"),
                "evidence_sha256": sha256(directory / "evidence.json"), "model_spec_sha256": sha256(directory / "model_spec.json"),
                "semantics_sha256": sha256(directory / semantic.FILE),
                "execution_receipt_sha256": sha256(root / f"executions/{run_id}/execution.json"),
                "generated_table_sha256": sha256(output)}
    require(all(v1["bindings"].get(key) == value for key, value in bindings.items()), "v1/current artifact binding mismatch")
    bindings["declaration_sha256"] = sha256(directory / FILE)
    bindings["semantic_feedback_sha256"] = sha256(_path(root, f"{semantic.FOLDER}/{semantic_feedback_id}/feedback.json"))
    frame = read_table(output, task, output=True)
    contracts.validate_output(None, frame, task)
    records = []
    for check in declaration["checks"]:
        names, _ = statistics.validate_operator(check["operator"])
        context = copy.deepcopy(declaration["table_context"])
        for key in ("variable_units", "variable_scales"):
            context[key] = {name: context[key][name] for name in names}
        result = statistics.diagnostic(frame, check["operator"], context, check["source"], approval=None)
        # A prospective declaration is not independent approval of these values.
        require(result["exact_source_check_allowed"] is False, "Supplement cannot upgrade frame-specific eligibility")
        item = items[check["evidence_id"]]
        proxy = check["proxy"]
        difference = None
        if proxy is not None and result["diagnostic_available"]:
            difference = result["diagnostic"]["value"] - item["estimate"]
            require(statistics.finite(difference), "Nonfinite proxy difference")
        records.append({"id": check["id"], "evidence_id": item["id"], "semantic_check_id": check["semantic_check_id"],
                        "reported_evidence": item, "source": check["source"], "operator": check["operator"],
                        "diagnostic": result, "exact_source_check_allowed": False, "strict_source_difference": None,
                        "proxy": None if proxy is None else {
                            "status": "available" if difference is not None else "unavailable",
                            "interpretation": "assumption_defined_unweighted_raw_difference_not_strict_source_discrepancy",
                            "difference": difference, "unit": item["unit"], "reason": proxy["reason"],
                            "assumption_ids": sorted(set(declaration["assumption_ids"]) | set(proxy["assumption_ids"])),
                            "review": proxy["review"]}})
    require(sha256(output) == bindings["generated_table_sha256"], "Generated table changed during collection")
    return {"schema_version": 1, "kind": "supplemental_context_execution_feedback_v1", "status": "complete",
            "candidate": relative, "run_id": run_id, "feedback_id": feedback_id, "semantic_feedback_id": semantic_feedback_id,
            "bindings": bindings, "output_link_verified": True, "generator_execution_recorded": True,
            "context_review": declaration["context_review"], "table_context": declaration["table_context"],
            "checks": records, "cross_context_generator_linkage": "not_supplied_or_verified",
            "scientific_validity": "not_assessed", "source_authenticity": "not_certified",
            "uncertainty_conversion": "none", "agent_authorship_verified": False,
            "engine_sha256": {Path(__file__).name: sha256(__file__),
                              "contextual_statistics.py": sha256(statistics.__file__)},
            "limitations": ["Prospective context approval is not a frame-bound exact-source approval.",
                            "Proxy differences require separately reviewed declared assumptions; they do not validate transport.",
                            "No source/target model is built and no generator is executed by this collector.",
                            "Hashes are retained-byte commitments, not authentication against host-side rewriting."]}


def collect_feedback(bundle, candidate, run_id, feedback_id, *, semantic_feedback_id, collect_semantic=False):
    """Explicitly collect v1 first or verify an existing v1; never fall back."""
    feedback_id = execution._name(feedback_id)
    semantic_feedback_id = execution._name(semantic_feedback_id)
    require(type(collect_semantic) is bool, "collect_semantic must be Boolean")
    prepared = _prepare(bundle, candidate, run_id)  # Reject declaration before any write.
    root, _, relative, *_ = prepared
    destination = _path(root, f"{FOLDER}/{feedback_id}", file=False)
    require(not destination.exists(), "Supplemental feedback already exists")
    if collect_semantic:
        semantic.collect_feedback(root, relative, run_id, semantic_feedback_id)
    report = _compute(prepared, run_id, feedback_id, semantic_feedback_id)
    report["created_utc"] = datetime.now(timezone.utc).isoformat()
    destination.parent.mkdir(exist_ok=True)
    destination.mkdir()
    execution._write(destination / "feedback.json", report)
    return verify_feedback(root, feedback_id, candidate=relative, run_id=run_id)


def verify_feedback(bundle, feedback_id, *, candidate, run_id):
    feedback_id = execution._name(feedback_id)
    prepared = _prepare(bundle, candidate, run_id)
    root = prepared[0]
    folder = _path(root, f"{FOLDER}/{feedback_id}", file=False)
    require([path.name for path in folder.iterdir()] == ["feedback.json"], "Supplemental artifact set changed")
    report = read_json(_path(folder, "feedback.json"))
    text(report.get("created_utc"))
    semantic_feedback_id = execution._name(report["semantic_feedback_id"])
    expected = _compute(prepared, run_id, feedback_id, semantic_feedback_id)
    expected["created_utc"] = report["created_utc"]
    require(canonical(report) == canonical(expected), "Supplemental receipt changed or no longer matches")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("collect", "verify"))
    for name in ("bundle", "candidate", "run-id", "feedback-id"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--semantic-feedback-id")
    parser.add_argument("--collect-semantic", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "collect":
            result = collect_feedback(args.bundle, args.candidate, args.run_id, args.feedback_id,
                                      semantic_feedback_id=args.semantic_feedback_id, collect_semantic=args.collect_semantic)
        else:
            require(not args.collect_semantic and args.semantic_feedback_id is None, "verify uses its bound v1 receipt")
            result = verify_feedback(args.bundle, args.feedback_id, candidate=args.candidate, run_id=args.run_id)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(json.dumps({"status": "error", "type": type(error).__name__, "message": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
