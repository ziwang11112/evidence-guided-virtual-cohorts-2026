"""Additive, source-only revision entrypoint. No target dispatch is exposed.

An independently reviewed frozen scientific declaration gates existing isolated
execution. Old bridge preparation, sealing and receipt verification are reused;
only its source slots are dispatched. Authoring tools themselves are not isolated.
"""
from __future__ import annotations

import ast
import copy
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[3]
BRIDGE_DIRECTORY = PROJECT / "work/scaleup_2026-11-01/bridge"
if not BRIDGE_DIRECTORY.is_dir():
    BRIDGE_DIRECTORY = PROJECT / "reports/scaleup_2026-11-01/bridge"
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(BRIDGE_DIRECTORY))

from cohort_harness import execution, lifecycle, semantic_feedback_v1 as semantic
from cohort_harness.analysis_evidence import validate_analysis_evidence
from cohort_harness.contracts import exact_keys, require, text
from cohort_harness.lifecycle import _path, read_json, sha256
import context_bridge as bridge
from evidence_use_v1 import assess_evidence_use
from scientific_validity_v1 import assess_law
import qualified_relationships_v1 as qualified

FOLDER = "source_revision_v1"
REQUIRED = ("analysis_evidence.json", "evidence_use_v1.json", "scientific_validity_v1.json")
REVIEW_CHECKS = {"code_correspondence", "nondegenerate_analysis_design",
                 "shared_dependency_paths", "source_context_assumptions", "point_estimate_scope"}


def _engines():
    files = [Path(__file__), Path(__file__).with_name("evidence_use_v1.py"),
             Path(__file__).with_name("scientific_validity_v1.py"),
             Path(qualified.__file__),
             Path(bridge.__file__)]
    return {p.name: sha256(p) for p in files}


def _controller_root(state):
    return _path(state["root"], FOLDER + "/" + state["relative"].split("/")[1], file=False)


def science_request(bundle, candidate):
    """Hash-bound review request, not an approval or universal validity proof."""
    state = bridge.preflight(bundle, candidate)
    directory = state["directory"]
    evidence = read_json(directory / "evidence.json")
    for name in REQUIRED:
        _path(directory, name)
    analyses = read_json(directory / "analysis_evidence.json")
    validate_analysis_evidence(analyses, state["task"], evidence, state["spec"])
    checks = {}
    for context in state["plan"]["contexts"]:
        if context["role"] == "source":
            for check in context["recipe"]["checks"]:
                require(check["id"] not in checks, "Check IDs must be globally unique in revision v1")
                checks[check["id"]] = (context["id"], check["evidence_id"])
    evidence_use = read_json(directory / "evidence_use_v1.json")
    uptake = assess_evidence_use(evidence_use, evidence, state["spec"],
                                recipe_check_ids=list(checks))
    for item in evidence_use["items"]:
        for check_id in item["check_ids"]:
            require(checks[check_id] == (item["context_id"], item["evidence_id"]),
                    "Evidence-use recipe references another context or evidence item")
        for reference in item["code_references"]:
            code = _path(directory, reference["path"])
            require(code.suffix == ".py", "Code reference must name a frozen Python file")
            tree = ast.parse(code.read_text(encoding="utf-8-sig"))
            symbols = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
            symbols |= {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
            require(reference["symbol"] in symbols, "Declared code symbol is absent")
    by_check = {check_id: item for item in evidence_use["items"] for check_id in item["check_ids"]}
    for context in state["plan"]["contexts"]:
        if context["role"] == "source":
            for check in context["recipe"]["checks"]:
                if check["status"] != "not_computable":
                    require(check["id"] in by_check and by_check[check["id"]]["role"] in
                            {"numerical_constraint", "qualified_numerical_comparison"},
                            "Computable recipe check lacks a numerical evidence-use declaration")
    wrapper = read_json(directory / "scientific_validity_v1.json")
    exact_keys(wrapper, {"schema_version", "context_laws"}, where="context law wrapper")
    require(type(wrapper["schema_version"]) is int and wrapper["schema_version"] == 1,
            "Invalid context law version")
    require(set(wrapper["context_laws"]) == {c["id"] for c in state["plan"]["contexts"]},
            "Every source and target context requires its own law declaration")
    requested = {a["id"]: a["estimand"] for a in analyses["analyses"]}
    mathematical = {}
    numeric_outputs = {c["name"] for c in state["task"]["columns"]
                       if c["role"] != "identifier" and c["kind"] in {"number", "integer"}}
    for context_id, law in wrapper["context_laws"].items():
        mathematical[context_id] = assess_law(law)
        require({a["id"] for a in law["analyses"]} == set(requested),
                "Every context law must cover exactly the intended analyses")
        operands = set()
        for analysis in law["analyses"]:
            estimand = requested[analysis["id"]]
            if estimand["kind"] == "ols_coefficient":
                require(analysis["kind"] == "ols" and analysis["outcome"] == estimand["outcome"] and
                        set(analysis["predictors"]) == set(estimand["exposures"] + estimand["adjustment"]),
                        "Law analysis must match the actual OLS operands")
                operands.update([analysis["outcome"], *analysis["predictors"]])
            elif estimand["kind"] == "correlation":
                require(analysis["kind"] == "pearson" and
                        set(analysis["variables"]) == {estimand["outcome"], *estimand["exposures"]},
                        "Law analysis must match Pearson operands")
                operands.update(analysis["variables"])
            else:
                raise ValueError("This gate currently supports OLS and Pearson point analyses only")
        require(numeric_outputs <= operands,
                "This entrypoint requires moment coverage of every numeric source/target output")
    eligible = all(m["manifest_valid"] and bool(m["analyses"]) and all(
        a["second_moment_status"] == "pass" for a in m["analyses"]) for m in mathematical.values())
    payload = {"schema_version": 1, "candidate": state["relative"],
               "parent": bridge._parent_binding(state), "engine_sha256": _engines(),
               "sidecar_sha256": {n: sha256(directory / n) for n in REQUIRED},
               "evidence_use": uptake, "declared_law": mathematical,
               "eligible_for_independent_review": eligible,
               "independent_review_checks": sorted(REVIEW_CHECKS),
               "uncertainty_scope": "point_estimates_only_no_interval_procedure_approved",
               "scope": "declared_moments_and_references_not_automatic_code_or_transport_proof"}
    return {"request": payload, "request_sha256": bridge.digest(payload)}


def _review(review, request):
    exact_keys(review, {"decision", "independent", "reviewer_id", "producer_id", "reviewed_utc",
                        "reason", "approved_sha256", "checks"}, where="scientific review")
    basic = {k: v for k, v in review.items() if k != "checks"}
    bridge.supplement._review(basic, request["request_sha256"])
    require(set(review["checks"]) == REVIEW_CHECKS and all(v is True for v in review["checks"].values()),
            "Scientific review must explicitly approve every required check")
    require(request["request"]["eligible_for_independent_review"],
            "Required declared moments failed or remain unresolved")


def qualified_requests(bundle, candidate):
    """Bind an optional frozen authored qualified plan to sealed source children."""
    state = bridge.preflight(bundle, candidate)
    destination = bridge._destination(state["root"], state["relative"])
    bridge._verify_seal(state, destination)
    path = state["directory"] / "qualified_plan_v1.json"
    if not path.exists():
        return {}
    plan = read_json(path)
    exact_keys(plan, {"schema_version", "contexts"}, where="qualified parent plan")
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1, "Invalid qualified parent plan")
    source_contexts = {c["id"] for c in state["plan"]["contexts"] if c["role"] == "source"}
    require(isinstance(plan["contexts"], dict) and set(plan["contexts"]) <= source_contexts,
            "Qualified plan references an unknown or target context")
    result = {}
    ledger = {i["evidence_id"]: i for i in read_json(state["directory"] / "evidence_use_v1.json")["items"]}
    for context_id, authored in plan["contexts"].items():
        require(authored["bindings"] == {}, "Authored qualified plan must leave derived bindings empty")
        require(authored["context_id"] == context_id and authored["context_role"] == "source", "Qualified context mismatch")
        for check in authored["checks"]:
            item = ledger.get(check["evidence_id"])
            require(item is not None and item["role"] == "qualified_numerical_comparison" and
                    item["context_id"] == context_id and check["semantic_check_id"] in item["check_ids"],
                    "Qualified check lacks the matching evidence-use declaration")
            mapping = check["measurement_mapping"]
            if mapping["kind"] != "identity":
                unit_item = ledger.get(mapping["unit_evidence_id"])
                require(unit_item is not None and unit_item["role"] != "unused",
                        "Used measurement-conversion evidence is declared unused")
        child = bridge._child_root(destination, context_id)
        directory = child / bridge.CHILD
        declaration = copy.deepcopy(authored)
        files = {"task_sha256": child / "task.json", "candidate_freeze_sha256": directory / "freeze.json",
                 "evidence_sha256": directory / "evidence.json", "model_spec_sha256": directory / "model_spec.json",
                 "semantics_sha256": directory / semantic.FILE, "bridge_plan_sha256": directory / bridge.PLAN}
        declaration["bindings"] = {key: sha256(path) for key, path in files.items()}
        result[context_id] = {"declaration": declaration, "declaration_sha256": qualified.declaration_digest(declaration)}
    return result


def _qualified_reviews(state, requests, reviews):
    require(isinstance(reviews, dict) and set(reviews) == set(requests), "Qualified review contexts differ")
    destination = bridge._destination(state["root"], state["relative"])
    for context_id, request in requests.items():
        child = bridge._child_root(destination, context_id)
        qualified._prepare(child, bridge.CHILD, request["declaration"], reviews[context_id])


def open_source_phase(bundle, candidate, scientific_review, *, qualified_reviews=None):
    """Reserve one source-only phase after real bridge seal and science review."""
    current = bridge.verify(bundle, candidate)
    require(current["attempts_consumed"] == 0, "Source phase requires an unattempted sealed bridge")
    state = bridge.preflight(bundle, candidate)
    request = science_request(bundle, candidate)
    _review(scientific_review, request)
    requests = qualified_requests(bundle, candidate)
    reviews = {} if qualified_reviews is None else qualified_reviews
    _qualified_reviews(state, requests, reviews)
    destination = _controller_root(state)
    destination.parent.mkdir(exist_ok=True)
    destination.mkdir()  # Exclusive reservation; no reset/retry by entrypoint.
    sources = {c["id"] for c in state["plan"]["contexts"] if c["role"] == "source"}
    intent = {"schema_version": 1, "kind": "source_only_revision_phase",
              "request": request, "scientific_review": scientific_review,
              "qualified_requests": requests, "qualified_reviews": reviews,
              "source_trial_ids": [t["id"] for t in state["plan"]["trials"] if t["context_id"] in sources],
              "target_dispatch_authorized": False,
              "scope": "one_candidate_source_phase_no_campaign_or_target_release"}
    execution._write(destination / "intent.json", intent)
    return verify_source_phase(bundle, candidate)


def verify_source_phase(bundle, candidate):
    state = bridge.preflight(bundle, candidate)
    destination = _controller_root(state)
    intent = read_json(destination / "intent.json")
    request = science_request(bundle, candidate)
    bridge._same(intent["request"], request, "Scientific artifacts or entrypoint changed")
    _review(intent["scientific_review"], request)
    requests = qualified_requests(bundle, candidate)
    bridge._same(intent["qualified_requests"], requests, "Qualified declarations or bindings changed")
    _qualified_reviews(state, requests, intent["qualified_reviews"])
    require(intent["target_dispatch_authorized"] is False, "Target dispatch is prohibited in this entrypoint")
    sources = {c["id"] for c in state["plan"]["contexts"] if c["role"] == "source"}
    ids = [t["id"] for t in state["plan"]["trials"] if t["context_id"] in sources]
    require(intent["source_trial_ids"] == ids, "Source schedule changed")
    verified = bridge.verify(bundle, candidate)
    require(all(t["trial_id"] in ids for t in verified["trials"]), "Target or undeclared execution appeared")
    require(not verified["completion_committed"], "Source-only phase cannot close the full bridge")
    dispatch = destination / "dispatch_intent.json"
    if dispatch.exists():
        dispatch_record = read_json(dispatch)
        exact_keys(dispatch_record, {"intent_sha256"}, where="dispatch intent")
        require(dispatch_record["intent_sha256"] == sha256(destination / "intent.json"), "Dispatch intent changed")
    require(not verified["trials"] or dispatch.exists(), "Execution appeared without phase dispatch intent")
    finished = destination / "source_completion.json"
    status = "ready" if not verified["trials"] and not dispatch.exists() else "incomplete"
    if finished.exists():
        completion = read_json(finished)
        require(len(verified["trials"]) == len(ids) and all(t["status"] != "interrupted" for t in verified["trials"]),
                "Source completion omits or interrupts a source slot")
        bridge._same(completion["bridge_inventory"], bridge._inventory(bridge._destination(state["root"], state["relative"])),
                     "Completed source artifacts changed")
        require(completion["intent_sha256"] == sha256(destination / "intent.json"), "Phase intent changed")
        require(completion["dispatch_sha256"] == sha256(dispatch), "Completed dispatch changed")
        status = "complete" if all(t["status"] == "success" for t in verified["trials"]) else "finished_with_failures"
    allowed = {"intent.json", "dispatch_intent.json", "source_completion.json", "decision.json", "decision_commitment.json"}
    require(all(p.is_file() and p.name in allowed for p in destination.iterdir()), "Unexpected controller artifact")
    result = {"status": status, "trials": verified["trials"], "source_slots": len(ids),
            "unattempted_source_ids": [i for i in ids if i not in {t["trial_id"] for t in verified["trials"]}],
            "target_attempts": 0, "target_release_authorized": False,
            "declared_law_reviewed": True, "transport_validity": "not_assessed",
            "source_completion_sha256": sha256(finished) if finished.exists() else None}
    if (destination / "decision.json").exists():
        commitment = read_json(destination / "decision_commitment.json")
        exact_keys(commitment, {"decision_sha256", "intent_sha256"}, where="decision commitment")
        require(commitment["decision_sha256"] == sha256(destination / "decision.json") and
                commitment["intent_sha256"] == sha256(destination / "intent.json"), "Retained decision bytes changed")
        _validate_decision(read_json(destination / "decision.json"), _feedback_from_phase(state, result))
    else:
        require(not (destination / "decision_commitment.json").exists(), "Decision commitment has no decision")
    return result


def dispatch_sources(bundle, candidate):
    """Dispatch only frozen source slots through WSL/bubblewrap; no fallback."""
    before = verify_source_phase(bundle, candidate)
    require(before["status"] == "ready", "Source phase already started; interrupted slots cannot be retried")
    state = bridge.preflight(bundle, candidate)
    control = _controller_root(state)
    require(not (control / "decision.json").exists(), "A retained terminal decision prohibits dispatch")
    destination = bridge._destination(state["root"], state["relative"])
    intent = read_json(control / "intent.json")
    execution._write(control / "dispatch_intent.json", {"intent_sha256": sha256(control / "intent.json")})
    runtime = read_json(destination / "intent.json")["runtime"]
    (destination / "attempts").mkdir()
    for trial in state["plan"]["trials"]:
        if trial["id"] not in intent["source_trial_ids"]:
            continue
        attempt = destination / "attempts" / trial["id"]
        attempt.mkdir()
        execution._write(attempt / "intent.json", bridge._attempt_binding(state, trial))
        child = bridge._child_root(destination, trial["context_id"])
        context = next(c for c in state["plan"]["contexts"] if c["id"] == trial["context_id"])
        outcome = {"status": "error", "error": None, "execution_verified": False,
                   "execution_sha256": None, "generated_table_sha256": None,
                   "semantic_sha256": None, "supplement_sha256": None, "artifacts": {}}
        try:
            receipt = execution.run_candidate(child, bridge.CHILD, trial["id"], trial["seed"],
                                              runtime=runtime, **state["plan"]["execution_limits"])
            outcome["status"] = receipt["status"]
            execution.verify_execution(child, trial["id"])
            outcome["execution_verified"] = True
            if receipt["status"] == "success":
                semantic.collect_feedback(child, bridge.CHILD, trial["id"], trial["id"])
                bridge._verify_semantic(child, trial["id"])
                if context["supplement"] is not None:
                    bridge.supplement.collect_feedback(child, bridge.CHILD, trial["id"], trial["id"], semantic_feedback_id=trial["id"])
        except (OSError, ValueError, TypeError, KeyError, RuntimeError) as error:
            outcome.update(status="error", error={"type": type(error).__name__, "message": str(error)[:2000]})
        artifacts = bridge._trial_artifacts(child, trial["id"])
        for field, name in {"execution_sha256": f"executions/{trial['id']}/execution.json",
                            "generated_table_sha256": f"executions/{trial['id']}/output/generated.csv",
                            "semantic_sha256": f"{semantic.FOLDER}/{trial['id']}/feedback.json",
                            "supplement_sha256": f"{bridge.supplement.FOLDER}/{trial['id']}/feedback.json"}.items():
            outcome[field] = artifacts.get(name)
        outcome["artifacts"] = artifacts
        execution._write(attempt / "outcome.json", outcome)
    verify_source_phase(bundle, candidate)
    execution._write(control / "source_completion.json", {
        "intent_sha256": sha256(control / "intent.json"), "dispatch_sha256": sha256(control / "dispatch_intent.json"),
        "bridge_inventory": bridge._inventory(destination)})
    return verify_source_phase(bundle, candidate)


def source_feedback_packet(bundle, candidate):
    """Return verified strict source summaries. Unknown semantics stay unavailable."""
    phase = verify_source_phase(bundle, candidate)
    state = bridge.preflight(bundle, candidate)
    return _feedback_from_phase(state, phase)


def _feedback_from_phase(state, phase):
    destination = bridge._destination(state["root"], state["relative"])
    ledger = {i["evidence_id"]: i for i in read_json(state["directory"] / "evidence_use_v1.json")["items"]}
    intent = read_json(_controller_root(state) / "intent.json")
    reports = []
    for trial in phase["trials"]:
        child = bridge._child_root(destination, trial["context_id"])
        outcome_path = destination / "attempts" / trial["trial_id"] / "outcome.json"
        outcome = read_json(outcome_path) if outcome_path.exists() else None
        report = {"context_id": trial["context_id"], "trial_id": trial["trial_id"], "status": trial["status"],
                  "error": outcome["error"] if outcome else {"type": "interrupted", "message": "No completed attempt receipt"},
                  "feedback": None, "feedback_status": "unavailable", "evidence_use_annotations": [],
                  "qualified_feedback": None, "qualified_status": "not_declared"}
        if outcome and outcome["execution_verified"]:
            receipt = execution.verify_execution(child, trial["trial_id"])
            report["execution_diagnostic"] = {key: receipt.get(key) for key in ("status", "error", "process", "generator_executed")}
        path = child / semantic.FOLDER / trial["trial_id"] / "feedback.json"
        if path.exists():
            try:
                report["feedback"] = bridge._verify_semantic(child, trial["trial_id"])
                report["feedback_status"] = "verified_even_if_later_component_failed"
                report["evidence_use_annotations"] = [
                    {"check_id": check["id"], "declaration": ledger[check["evidence_id"]]}
                    for check in report["feedback"]["checks"]]
            except (OSError, ValueError, TypeError, KeyError, RuntimeError) as error:
                if trial["status"] == "success":
                    raise  # A successful retained receipt may not silently degrade.
                report["feedback_status"] = "invalid_partial_artifact_not_used_for_arithmetic"
                report["feedback_error"] = {"type": type(error).__name__, "message": str(error)[:2000],
                                            "artifact_sha256": sha256(path)}
        context_id = trial["context_id"]
        if context_id in intent["qualified_requests"]:
            report["qualified_status"] = "unavailable_without_verified_strict_feedback"
            if report["feedback"] is not None:
                report["qualified_feedback"] = qualified.compute_qualified_feedback(
                    child, bridge.CHILD, trial["trial_id"], trial["trial_id"],
                    intent["qualified_requests"][context_id]["declaration"], intent["qualified_reviews"][context_id])
                report["qualified_status"] = "verified_assumption_comparison_not_strict_replay"
        reports.append(report)
    packet = {"schema_version": 1, "kind": "source_revision_feedback",
              "candidate": state["relative"], "source_phase": phase, "reports": reports,
              "target_results_included": False,
              "qualified_comparisons": "separate_reviewed_results_when_declared_never_upgrade_strict_status",
              "interpretation": "declared_source_statistics_not_target_or_transport_validation"}
    return {"packet": packet, "packet_sha256": bridge.digest(packet)}


def record_decision(bundle, candidate, decision):
    """One retained decision bound to actual feedback; never dispatch a revision."""
    packet = source_feedback_packet(bundle, candidate)
    _validate_decision(decision, packet)
    state = bridge.preflight(bundle, candidate)
    execution._write(_controller_root(state) / "decision.json", decision)
    execution._write(_controller_root(state) / "decision_commitment.json", {
        "decision_sha256": sha256(_controller_root(state) / "decision.json"),
        "intent_sha256": sha256(_controller_root(state) / "intent.json")})
    return {"decision": decision, "revision_executed": False, "target_release_authorized": False}


def _validate_decision(decision, packet):
    exact_keys(decision, {"action", "feedback_sha256", "reason", "addressed_findings", "remaining_limitations"},
               where="revision decision")
    require(decision["action"] in {"retain", "revise", "stop"}, "Unknown revision decision")
    require(decision["feedback_sha256"] == packet["packet_sha256"], "Decision refers to different feedback")
    require(decision["action"] == "stop" or packet["packet"]["source_phase"]["status"] in {"complete", "finished_with_failures"},
            "An unstarted/interrupted source phase permits only stop")
    text(decision["reason"], "revision reason")
    for field in ("addressed_findings", "remaining_limitations"):
        require(isinstance(decision[field], list) and all(isinstance(v, str) and v.strip() for v in decision[field]),
                "Decision findings/limitations must be text lists")
