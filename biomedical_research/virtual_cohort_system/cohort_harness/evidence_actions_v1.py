"""Route Agent-declared evidence gaps into concrete, bounded action proposals.

Pure planning API. Does not extract scientific meanings, execute tools, allocate
real budget, edit a candidate, or upgrade a declared support assessment.
"""
from __future__ import annotations

from .analysis_evidence import summarize_analysis_evidence
from .contracts import exact_keys, require, string_list, text, validate_task


KINDS = {"local_reextract", "targeted_retrieval", "operator_review", "scenario_review", "limit_use"}
DIAGNOSES = {
    "missing_relation", "unverified_bridge", "context_difference", "source_conflict",
    "undefined_statistic", "operator_missing", "unassessed",
}
ALLOWED = {
    "source_conflict": {"local_reextract", "scenario_review", "limit_use"},
    "operator_missing": {"operator_review", "limit_use"},
}
DEFAULT_ACTIONS = KINDS - {"operator_review"}
# Planning upper bounds on the two task-level counters only. The live adapter
# also checks auxiliary requests, bytes, exclusions, receipts and current usage.
COSTS = {
    "literature.search": (1, 0),
    "literature.fetch": (1, 1),
    "literature.list-supplements": (0, 0),
    "literature.fetch-supplement": (0, 1),
}


def _enum(value, choices, name):
    require(isinstance(value, str) and value in choices, "Invalid " + name)


def route_evidence_actions(manifest, cards, task, evidence, spec, availability, *, required_analysis_ids):
    """Return proposals from validated declarations and a caller-supplied snapshot.

    required_analysis_ids binds coverage to the supplied request; caller must
    obtain these IDs honestly. Availability is not an authentication mechanism.
    An 'open' snapshot never overrides task permissions or author unavailability.
    """
    validate_task(task)
    summary = summarize_analysis_evidence(manifest, task, evidence, spec)
    string_list(required_analysis_ids, "required analysis IDs", nonempty=True)
    analyses = {a["id"]: a for a in manifest["analyses"]}
    require(set(required_analysis_ids) <= analyses.keys(), "Missing required analytical use")
    exact_keys(availability, {"retrieval_phase", "queries_used", "downloads_used"}, where="availability")
    _enum(availability["retrieval_phase"], {"closed", "open"}, "retrieval phase")
    for key in ("queries_used", "downloads_used"):
        require(type(availability[key]) is int and availability[key] >= 0, "Invalid usage counter: " + key)
    exact_keys(cards, {"schema_version", "cards"}, where="action cards")
    require(type(cards["schema_version"]) is int and cards["schema_version"] == 1, "Action-card version must be 1")
    require(isinstance(cards["cards"], list), "cards must be a list")
    expected_gaps = {(a["id"], g["id"]) for a in manifest["analyses"] for g in a["gaps"]}
    seen_gaps, seen_cards, parsed = set(), set(), []
    items = {e["id"]: e for e in evidence["items"]}
    sources = {s["id"]: s for s in evidence["sources"]}
    for card in cards["cards"]:
        exact_keys(card, {"id", "analysis_id", "gap_ids", "diagnosis", "evidence_ids", "action_kind",
                          "retrieval_action_id", "request", "success_criterion", "fallback"}, where="action card")
        for field in ("id", "analysis_id", "request", "success_criterion"):
            text(card[field], "card " + field)
        require(card["id"] not in seen_cards, "Duplicate action card ID")
        seen_cards.add(card["id"])
        require(card["analysis_id"] in analyses, "Unknown card analysis")
        analysis = analyses[card["analysis_id"]]
        string_list(card["gap_ids"], "card gaps", nonempty=True)
        bound_gaps = {(card["analysis_id"], g) for g in card["gap_ids"]}
        require(bound_gaps <= expected_gaps, "Unknown or cross-analysis gap")
        require(not bound_gaps & seen_gaps, "Every gap must have exactly one action card")
        seen_gaps.update(bound_gaps)
        _enum(card["diagnosis"], DIAGNOSES, "gap diagnosis")
        _enum(card["action_kind"], ALLOWED.get(card["diagnosis"], DEFAULT_ACTIONS), "diagnosis/action pair")
        _enum(card["fallback"], {"scenario_review", "limit_use"}, "fallback")
        string_list(card["evidence_ids"], "card evidence IDs")
        require(set(card["evidence_ids"]) <= {l["evidence_id"] for l in analysis["evidence_links"]},
                "Card evidence must be linked to its analysis")
        locations = []
        for eid in card["evidence_ids"]:
            item = items[eid]
            source = sources[item["source_id"]]
            locations.append({"evidence_id": eid, "source_id": source["id"], "locator": item["locator"],
                              "declared_artifacts": [dict(a) for a in source["artifacts"]]})
        if card["action_kind"] == "local_reextract":
            require(bool(locations) and all(x["declared_artifacts"] for x in locations),
                    "Local re-extraction needs linked existing source artifacts")
        action = None
        if card["action_kind"] == "targeted_retrieval":
            text(card["retrieval_action_id"], "retrieval action ID")
            action = next((a for a in analysis["actions"] if a["id"] == card["retrieval_action_id"]), None)
            require(action is not None, "Unknown analysis retrieval action")
            require(set(card["gap_ids"]) <= set(action["gap_ids"]), "Retrieval action does not address card gaps")
            require(action["tool"] in COSTS, "Targeted retrieval needs a literature tool")
        else:
            require(card["retrieval_action_id"] is None, "Non-retrieval card cannot bind a retrieval action")
        parsed.append((card, action, locations))
    require(seen_gaps == expected_gaps, "Every unresolved gap needs exactly one action card")

    remaining_q = max(0, task["budget"]["source_queries"] - availability["queries_used"])
    remaining_d = max(0, task["budget"]["source_downloads"] - availability["downloads_used"])
    initial_remaining = {"queries": remaining_q, "downloads": remaining_d}
    proposed_requests, routes = {}, []
    for card, action, locations in parsed:
        blockers, cost, group = [], {"queries": 0, "downloads": 0}, None
        if action is None:
            disposition = "local_review_proposed"
        else:
            tool = action["tool"]
            group = (tool, action["request"])
            if availability["retrieval_phase"] == "closed":
                blockers.append("acquisition_phase_closed")
            if task["information_policy"]["mode"] != "published_evidence" or tool not in task["information_policy"]["allowed_tools"]:
                blockers.append("tool_not_permitted")
            if action["status"] != "planned":
                blockers.append("author_declared_unavailable")
            q, d = COSTS[tool]
            # Identical permitted requests can share one planning allocation;
            # an unavailable proposal never inherits another card's permission.
            shared = not blockers and group in proposed_requests
            if not shared:
                if q > remaining_q:
                    blockers.append("query_budget_insufficient")
                if d > remaining_d:
                    blockers.append("download_budget_insufficient")
            if blockers:
                disposition = "retrieval_blocked"
            elif shared:
                disposition = "shared_retrieval_proposal"
            else:
                remaining_q -= q
                remaining_d -= d
                cost = {"queries": q, "downloads": d}
                proposed_requests[group] = card["id"]
                disposition = "retrieval_proposed_adapter_recheck_required"
        routes.append({
            "card_id": card["id"], "analysis_id": card["analysis_id"], "gap_ids": list(card["gap_ids"]),
            "diagnosis_origin": "agent_declaration", "diagnosis": card["diagnosis"],
            "action_kind": card["action_kind"], "request": card["request"],
            "success_criterion": card["success_criterion"], "source_locations": locations,
            "retrieval": None if action is None else {"tool": action["tool"], "request": action["request"]},
            "disposition": disposition, "blockers": blockers,
            "shared_proposal_card_id": proposed_requests.get(group) if disposition == "shared_retrieval_proposal" else None,
            "estimated_planning_cost": cost, "fallback": card["fallback"],
            "gap_status": "unresolved", "executed": False,
        })
    return {
        "schema_version": 1, "scope": "agent_declaration_action_planning_only",
        "required_analysis_ids": list(required_analysis_ids),
        "additional_declared_analysis_ids": sorted(analyses.keys() - set(required_analysis_ids)),
        "declared_evidence_summary": summary, "routes": routes,
        "budget_snapshot": dict(availability), "initial_task_budget_remaining": initial_remaining,
        "after_estimated_plan": {"queries": remaining_q, "downloads": remaining_d},
        "budget_reserved": False, "retrieval_executed": False, "candidate_modified": False,
        "scientific_validity": "not_assessed", "data_quality_gain": "not_tested",
        "limitations": [
            "Scientific gap diagnoses, completeness of model dependencies and context judgments are Agent declarations.",
            "Source locations come from validated evidence records; this pure API does not verify registry or file bytes.",
            "Planning costs cover query/download counters only, not auxiliary requests or byte limits; the live adapter must recheck everything.",
            "Card order is author supplied; estimated allocations are not real reservations or tool authorization.",
            "Local/operator/scenario routes propose review, not execution, approved parameters or calibrated uncertainty.",
            "No proposed action resolves a gap or upgrades an assessment without subsequent evidence and review.",
        ],
    }
