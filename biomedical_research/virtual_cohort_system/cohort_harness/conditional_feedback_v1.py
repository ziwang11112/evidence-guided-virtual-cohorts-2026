"""Opt-in equal-weight interpretations of named correlations on task output.

Strict semantic feedback remains unavailable for unreported original weights.
An independently approved interpretation is a separate, assumption-defined raw
task-population proxy, not source reproduction or a fallback from strict errors.
No generator, source population or reference data is accessed here.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from . import execution, semantic_feedback_v1 as strict, source_checks
from .contracts import exact_keys, require, string_list, text
from .lifecycle import _bundle, _path, read_json, read_table, sha256, verify_candidate
from .whole_cohort_feedback import PLAN as STRICT_PLAN, _resolve_candidate


FILE = "conditional_interpretations_v1.json"
FOLDER = "conditional_feedback_v1"
SCOPE = "conditional_source_interpretation_target_proxy"
_NAMED = {"Pearson": "correlation", "Spearman": "spearman_correlation"}
_BINDINGS = {
    "task_sha256": "task.json", "evidence_sha256": "evidence.json",
    "recipe_sha256": STRICT_PLAN, "semantics_sha256": strict.FILE,
    "model_spec_sha256": "model_spec.json",
}


def _approval(directory, plan, evidence):
    reference = plan["approval"]
    exact_keys(reference, {"path", "sha256"}, where="interpretation approval reference")
    path = _path(directory, reference["path"])
    require(path != directory / FILE, "Approval cannot be the interpretation plan")
    require(reference["sha256"] == sha256(path), "Interpretation approval hash mismatch")
    approval = read_json(path)
    exact_keys(approval, {"schema_version", "decision", "reviewer_id", "builder_id",
                         "independent_of_builder", "reviewed_utc", "rationale", "approved_plan",
                         "evidence_dispositions"}, where="interpretation approval")
    require(type(approval["schema_version"]) is int and approval["schema_version"] == 1,
            "Invalid interpretation approval version")
    require(approval["decision"] == "approved", "Interpretation lacks approval")
    for field in ("reviewer_id", "builder_id", "reviewed_utc", "rationale"):
        text(approval[field], "approval " + field)
    require(approval["independent_of_builder"] is True and
            approval["reviewer_id"].strip().casefold() != approval["builder_id"].strip().casefold(),
            "Approval must declare an independent reviewer")
    require(approval["builder_id"] == plan["builder_id"], "Approval builder mismatch")
    payload = {key: value for key, value in plan.items() if key != "approval"}
    require(strict._json(approval["approved_plan"]) == strict._json(payload),
            "Approval does not cover this interpretation plan")
    dispositions = approval["evidence_dispositions"]
    require(isinstance(dispositions, list), "Evidence dispositions must be a list")
    by_id = {}
    for item in dispositions:
        exact_keys(item, {"evidence_id", "source_id", "status", "reason"}, where="evidence disposition")
        evidence_id = item["evidence_id"]
        require(isinstance(evidence_id, str) and evidence_id in evidence and evidence_id not in by_id,
                "Unknown or duplicate disposition evidence ID")
        require(item["source_id"] == evidence[evidence_id]["source_id"], "Disposition source mismatch")
        require(item["status"] in {"interpretation_approved", "not_approved", "quarantined"},
                "Unknown evidence disposition")
        text(item["reason"], "disposition reason")
        by_id[evidence_id] = item
    require(set(by_id) == set(evidence), "Approval must disposition every evidence item")
    requested = {item["evidence_id"] for item in plan["interpretations"]}
    require({key for key, item in by_id.items() if item["status"] == "interpretation_approved"} == requested,
            "Interpretation evidence is unapproved or quarantined")
    return approval, reference["path"]


def _preflight(root, directory, relative):
    # Strict semantic validation always runs, unchanged and without table reads.
    strict_gate = strict.preflight(root, relative)
    task = read_json(root / "task.json")
    evidence_document = read_json(directory / "evidence.json")
    evidence = {item["id"]: item for item in evidence_document["items"]}
    sources = {source["id"]: source for source in evidence_document["sources"]}
    recipe = read_json(directory / STRICT_PLAN)
    checks = {check["id"]: check for check in recipe["checks"]}
    gates = {gate["id"]: gate for gate in strict_gate["checks"]}
    assumption_records = {item["id"]: item for item in read_json(directory / "model_spec.json")["assumptions"]}
    assumptions = set(assumption_records)
    plan = read_json(_path(directory, FILE))
    exact_keys(plan, {"schema_version", "scope", "population", "builder_id", "interpretations", "approval"}
               | set(_BINDINGS), where="conditional interpretation plan")
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1, "Invalid interpretation version")
    require(plan["scope"] == "task_population_proxy", "Only task-population proxy interpretations are supported")
    require(plan["population"] == task["population"], "Interpretation population differs from task")
    text(plan["builder_id"], "interpretation builder")
    for key, name in _BINDINGS.items():
        path = root / name if name == "task.json" else directory / name
        require(plan[key] == sha256(path), "Interpretation binding changed: " + key)
    require(isinstance(plan["interpretations"], list) and 0 < len(plan["interpretations"]) <= 12,
            "One to twelve explicit interpretations are required")
    ids, check_ids, evidence_ids = set(), set(), set()
    for interpretation in plan["interpretations"]:
        exact_keys(interpretation, {"id", "strict_check_id", "evidence_id", "source_id", "source_identifier",
                                   "source_locator", "named_estimator", "operator", "equal_weight_assumption_id",
                                   "applicability_assumption_ids", "reason"}, where="conditional interpretation")
        key = execution._name(interpretation["id"]).casefold()
        require(key not in ids, "Duplicate interpretation ID")
        ids.add(key)
        check_id, evidence_id = interpretation["strict_check_id"], interpretation["evidence_id"]
        require(isinstance(check_id, str) and check_id in checks and check_id not in check_ids,
                "Unknown or reused strict check")
        require(isinstance(evidence_id, str) and evidence_id in evidence and evidence_id not in evidence_ids,
                "Unknown or reused interpretation evidence")
        check_ids.add(check_id)
        evidence_ids.add(evidence_id)
        check, gate, item = checks[check_id], gates[check_id], evidence[evidence_id]
        binding = gate["semantics"]
        require(check["evidence_id"] == evidence_id, "Interpretation/strict evidence mismatch")
        require(interpretation["source_id"] == item["source_id"] and
                interpretation["source_identifier"] == sources[item["source_id"]]["identifier"] and
                interpretation["source_locator"] == item["locator"], "Interpretation source identity/locator mismatch")
        require(binding["weights"] == "not_reported", "Only unreported original weights may be interpreted")
        require(binding["definition_status"] == "specified" and binding["transform"] == "identity",
                "Interpretation cannot replace an unknown definition or transform")
        require(check["status"] == "approximate" and check["operator"] is not None,
                "Interpretation requires an explicitly approximate strict recipe")
        require(gate["semantic_status"] == "unavailable", "Original strict check must remain unavailable")
        named = interpretation["named_estimator"]
        require(isinstance(named, str) and named in _NAMED, "Only named Pearson/Spearman interpretations are supported")
        operator = interpretation["operator"]
        require(isinstance(operator, dict) and operator.get("kind") == _NAMED[named], "Named estimator/operator mismatch")
        require(strict._signature(operator) == strict._signature(binding["source_operator"]) ==
                strict._signature(check["operator"]), "Interpretation changes the source/operator definition")
        # Reuse exact source/task identity/type/unit validation, without changing weights.
        strict._task_operator(operator, {column["name"]: column for column in task["columns"]})
        strict._measurement(binding, operator, {column["name"]: column for column in task["columns"]})
        strict._bind_evidence(item, operator)
        require(operator["unit"] == "1", "Correlation must be dimensionless")
        weight_assumption = interpretation["equal_weight_assumption_id"]
        require(isinstance(weight_assumption, str) and weight_assumption in assumptions,
                "Equal-weight interpretation needs a declared assumption")
        applicability = interpretation["applicability_assumption_ids"]
        string_list(applicability, "task-population applicability assumptions", nonempty=True)
        require(set(applicability) <= assumptions and weight_assumption not in applicability,
                "Task applicability requires distinct declared assumptions")
        text(interpretation["reason"], "interpretation reason")
    approval, approval_path = _approval(directory, plan, evidence)
    context = {"sources": sources, "evidence": evidence, "assumptions": assumption_records}
    return task, plan, approval, approval_path, gates, context


def preflight(bundle, candidate):
    """Validate all declarations/approval, reading no individual tables."""
    root = _bundle(bundle)
    directory, relative = _resolve_candidate(root, candidate)
    _, plan, approval, _, gates, _ = _preflight(root, directory, relative)
    return {"schema_version": 1, "scope": SCOPE, "candidate": relative, "status": "approved_declarations",
            "plan_sha256": sha256(directory / FILE), "approval_sha256": plan["approval"]["sha256"],
            "reviewer_id": approval["reviewer_id"], "reviewer_identity_verified": False,
            "interpretations": [{"id": item["id"], "strict_check_id": item["strict_check_id"],
                                 "original_weight_use": "not_reported", "assumed_weighting": "equal",
                                 "strict_semantic_status": gates[item["strict_check_id"]]["semantic_status"]}
                                for item in plan["interpretations"]], "source_reproduction": "not_established"}


def _compute(root, directory, relative, run_id, feedback_id, strict_feedback_id):
    # Finish every interpretation gate before strict re-verification or arithmetic.
    task, plan, approval, approval_path, _, context = _preflight(root, directory, relative)
    frozen = verify_candidate(root, directory)
    require(all(relative + "/" + name in frozen["candidate_files"] for name in (FILE, approval_path, strict.FILE)),
            "Interpretation, approval and strict sidecar must be frozen")
    strict_report = strict.verify_feedback(root, strict_feedback_id, candidate=relative, run_id=run_id)
    # The inherited verifier uses Python equality, where True == 1. Preserve its
    # full verification, then additionally require typed JSON equality here.
    typed_expected = strict._compute(root, directory, relative, run_id, strict_feedback_id)
    typed_expected["created_utc"] = strict_report["created_utc"]
    require(strict._json(strict_report) == strict._json(typed_expected),
            "Strict feedback has typed changes or differs from recomputed diagnostics")
    rows = {row["id"]: row for row in strict_report["checks"]}
    for interpretation in plan["interpretations"]:
        row = rows[interpretation["strict_check_id"]]
        require(row["status"] == "not_computable" and row["calculation"] is None and row["difference"] is None,
                "Original strict result must stay unavailable with no numeric discrepancy")
    output = _path(root, f"executions/{run_id}/output/generated.csv")
    frame = read_table(output, task, output=True)
    records = []
    for interpretation in plan["interpretations"]:
        strict_row = rows[interpretation["strict_check_id"]]
        row = {"id": interpretation["id"], "evidence_id": interpretation["evidence_id"],
               "interpretation": interpretation, "strict_status": "not_computable", "strict_result": strict_row,
               "context": {
                   "equal_weight_assumption": context["assumptions"][interpretation["equal_weight_assumption_id"]],
                   "applicability_assumptions": [context["assumptions"][key]
                                                 for key in interpretation["applicability_assumption_ids"]],
                   "source": context["sources"][interpretation["source_id"]],
                   "evidence_item": context["evidence"][interpretation["evidence_id"]],
               },
               "original_weight_use": "not_reported", "assumed_weighting": "equal",
               "reported_value": strict_row["reported_value"], "status": "conditional_computed",
               "calculation": None, "difference": None, "unavailable_reason": None,
               "difference_interpretation": "assumption_defined_unstandardized_raw_diagnostic_only"}
        try:
            row["calculation"] = source_checks.apply_operator(frame, interpretation["operator"])
            row["difference"] = row["calculation"]["value"] - row["reported_value"]
            require(source_checks.finite(row["difference"]), "Conditional difference is nonfinite")
        except source_checks.NotComputable as error:
            row.update(status="not_computable", unavailable_reason=str(error))
        records.append(row)
    strict_path = _path(root, f"{strict.FOLDER}/{strict_feedback_id}/feedback.json")
    return {"schema_version": 1, "kind": "conditional_correlation_feedback_v1", "scope": SCOPE,
            "feedback_id": feedback_id, "strict_feedback_id": strict_feedback_id,
            "candidate": relative, "run_id": run_id, "status": "complete", "population": task["population"],
            "source_reproduction": "not_established", "source_context_generated": False,
            "target_performance": "not_assessed", "uncertainty_calibration": "not_provided",
            "output_link_verified": True, "generator_execution_recorded": strict_report["generator_execution_recorded"],
            "agent_authorship_verified": False, "reviewer_identity_verified": False,
            "reviewer_id": approval["reviewer_id"],
            "bindings": {**{key: plan[key] for key in _BINDINGS},
                         "candidate_freeze_sha256": sha256(directory / "freeze.json"),
                         "plan_sha256": sha256(directory / FILE), "approval_sha256": plan["approval"]["sha256"],
                         "strict_feedback_sha256": sha256(strict_path), "generated_table_sha256": sha256(output)},
            "engine_sha256": {**strict_report["engine_sha256"], Path(__file__).name: sha256(__file__)},
            "calculator_runtime": strict_report["calculator_runtime"], "checks": records,
            "n_conditional_computable": sum(row["calculation"] is not None for row in records),
            "n_not_computable": sum(row["status"] == "not_computable" for row in records),
            "limitations": ["Original weighting remains unknown; strict results are not changed.",
                            "These are approved assumption-defined task-population proxies, not source reproduction.",
                            "No generator execution, source-context reconstruction or reference evaluation occurs.",
                            "Raw discrepancies are not calibrated intervals, significance tests or target utility.",
                            "Approval and source authenticity are procedural declarations, not authenticated identities.",
                            "Hashes detect changes relative to retained records, not coordinated host rewriting."]}


def collect_feedback(bundle, candidate, run_id, feedback_id, *, strict_feedback_id):
    """Collect only after a separate strict v1 report exists; never alter it."""
    root = _bundle(bundle)
    directory, relative = _resolve_candidate(root, candidate)
    run_id, feedback_id, strict_feedback_id = map(execution._name, (run_id, feedback_id, strict_feedback_id))
    destination = _path(root, f"{FOLDER}/{feedback_id}", file=False)
    require(not destination.exists(), "Conditional feedback ID already exists")
    report = _compute(root, directory, relative, run_id, feedback_id, strict_feedback_id)
    report["created_utc"] = datetime.now(timezone.utc).isoformat()
    destination.parent.mkdir(exist_ok=True)
    destination.mkdir()
    execution._write(destination / "feedback.json", report)
    return verify_feedback(root, feedback_id, candidate=relative, run_id=run_id,
                           strict_feedback_id=strict_feedback_id)


def verify_feedback(bundle, feedback_id, *, candidate=None, run_id=None, strict_feedback_id=None):
    root = _bundle(bundle)
    feedback_id = execution._name(feedback_id)
    folder = _path(root, f"{FOLDER}/{feedback_id}", file=False)
    require([path.name for path in folder.iterdir()] == ["feedback.json"], "Conditional feedback artifact set changed")
    report = read_json(_path(folder, "feedback.json"))
    directory, relative = _resolve_candidate(root, report["candidate"])
    if candidate is not None:
        require(_resolve_candidate(root, candidate)[1] == relative, "Wrong conditional candidate")
    if run_id is not None:
        require(report["run_id"] == execution._name(run_id), "Wrong conditional execution")
    if strict_feedback_id is not None:
        require(report["strict_feedback_id"] == execution._name(strict_feedback_id), "Wrong strict feedback")
    text(report.get("created_utc"), "conditional feedback timestamp")
    expected = _compute(root, directory, relative, execution._name(report["run_id"]), feedback_id,
                        execution._name(report["strict_feedback_id"]))
    expected["created_utc"] = report["created_utc"]
    require(strict._json(report) == strict._json(expected),
            "Conditional feedback changed or differs from recomputed diagnostics")
    return report
