"""Invented action cards exercise routing contracts, without rows or retrieval.

The source record is an in-memory declaration. Tests neither register artifacts
nor assess the scientific truth of a diagnosis or its proposed action.
"""
import copy

import pytest

from cohort_harness.contracts import ContractError
from cohort_harness.evidence_actions_v1 import route_evidence_actions
from test_analysis_evidence import transported_manifest


@pytest.fixture
def routing_inputs():
    task = {
        "schema_version": 1, "task_id": "invented-routing-only", "mode": "whole_cohort",
        "population": "Invented task population", "row_id": "sample_id", "n_rows": 1,
        "columns": [
            {"name": "sample_id", "kind": "string", "unit": "identifier", "role": "identifier", "nullable": False},
            {"name": "x", "kind": "number", "unit": "x_unit", "role": "generated", "nullable": False},
            {"name": "y", "kind": "number", "unit": "y_unit", "role": "generated", "nullable": False}],
        "information_policy": {"mode": "published_evidence", "excluded_cohorts": [], "allowed_tools": []},
        "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 0},
    }
    evidence = {
        "schema_version": 1,
        "sources": [{"id": "S1", "identifier": "fixture:source-declaration", "population": "Invented source population",
                     "measurement": "Invented exact measurement", "cohort_ids": ["invented-routing-cohort"],
                     "artifacts": [{"path": "sources/invented.txt", "sha256": "a" * 64}]}],
        "items": [{"id": "E1", "source_id": "S1", "locator": "Invented table 1", "variables": ["y"],
                   "kind": "mean", "estimate": 7, "unit": "y_unit", "uncertainty": {"kind": "not_reported"},
                   "adjustment": [], "selection": "Invented source eligibility", "applicability": "Interface fixture only"}],
    }
    spec = {
        "parameters": {"invented_parameter": 7},
        "assumptions": [{"id": "A1", "description": "Invented population transfer assumption"}],
        "parameter_provenance": {"invented_parameter": {
            "evidence_ids": ["E1"], "assumption_ids": ["A1"], "derivation": "Invented declared mean"}},
    }
    cards = {"schema_version": 1, "cards": [{
        "id": "card_population", "analysis_id": "mean_y", "gap_ids": ["G1"],
        "diagnosis": "context_difference", "evidence_ids": ["E1"], "action_kind": "limit_use",
        "retrieval_action_id": None,
        "request": "Restrict demonstrations to source-population arithmetic; prohibit target-population mean claims.",
        "success_criterion": "The documented allowed uses exclude the unresolved target-population mean.",
        "fallback": "limit_use",
    }]}
    return transported_manifest(), cards, task, evidence, spec, {
        "retrieval_phase": "closed", "queries_used": 0, "downloads_used": 0,
    }


def route(inputs, required_analysis_ids=None):
    return route_evidence_actions(*inputs, required_analysis_ids=(
        ["mean_y"] if required_analysis_ids is None else required_analysis_ids))


@pytest.mark.parametrize("attack", ["missing_card", "duplicate_gap", "unknown_gap", "unknown_analysis",
                                   "unlisted_use", "missing_required_use", "duplicate_card_id"])
def test_every_required_use_and_gap_is_accounted_for(routing_inputs, attack):
    manifest, cards, *_ = routing_inputs
    required = ["mean_y"]
    if attack == "missing_card":
        cards["cards"] = []
    elif attack == "duplicate_gap":
        duplicate = copy.deepcopy(cards["cards"][0])
        duplicate["id"] = "another_card"
        cards["cards"].append(duplicate)
    elif attack == "unknown_gap":
        cards["cards"][0]["gap_ids"] = ["absent_gap"]
    elif attack == "unknown_analysis":
        cards["cards"][0]["analysis_id"] = "absent_analysis"
    elif attack == "unlisted_use":
        other = copy.deepcopy(manifest["analyses"][0])
        other["id"] = "undeclared_required_use"
        manifest["analyses"].append(other)
    elif attack == "missing_required_use":
        required.append("missing_original_request")
    else:
        second_gap = copy.deepcopy(manifest["analyses"][0]["gaps"][0])
        second_gap["id"] = "G2"
        manifest["analyses"][0]["gaps"].append(second_gap)
        manifest["analyses"][0]["actions"][0]["gap_ids"].append("G2")
        duplicate = copy.deepcopy(cards["cards"][0])
        duplicate["gap_ids"] = ["G2"]
        cards["cards"].append(duplicate)
    with pytest.raises(ContractError):
        route(routing_inputs, required)


@pytest.mark.parametrize("attack", ["unknown_evidence", "unlinked_evidence", "unknown_diagnosis",
                                   "unknown_action", "completed", "claims_support", "schema_bool"])
def test_cards_cannot_invent_references_or_execution_claims(routing_inputs, attack):
    _, cards, _, evidence, *_ = routing_inputs
    card = cards["cards"][0]
    if attack == "unknown_evidence":
        card["evidence_ids"] = ["absent_evidence"]
    elif attack == "unlinked_evidence":
        evidence["items"].append({**copy.deepcopy(evidence["items"][0]), "id": "E2"})
        card["evidence_ids"] = ["E2"]
    elif attack == "unknown_diagnosis":
        card["diagnosis"] = "scientifically_validated"
    elif attack == "unknown_action":
        card["action_kind"] = "execute_generator"
    elif attack == "completed":
        card["status"] = "completed"
    elif attack == "claims_support":
        card["scientific_validity"] = "supported"
    else:
        cards["schema_version"] = True
    with pytest.raises(ContractError):
        route(routing_inputs)


def test_cross_analysis_action_cannot_address_another_uses_gap(routing_inputs):
    manifest, cards, *_ = routing_inputs
    other = copy.deepcopy(manifest["analyses"][0])
    other["id"] = "mean_x"
    other["gaps"][0]["id"] = "G2"
    other["actions"][0]["gap_ids"] = ["G2"]
    manifest["analyses"].append(other)
    cards["cards"][0]["gap_ids"] = ["G2"]
    second = copy.deepcopy(cards["cards"][0])
    second.update(id="other_card", analysis_id="mean_x", gap_ids=["G1"])
    cards["cards"].append(second)
    with pytest.raises(ContractError):
        route(routing_inputs, ["mean_y", "mean_x"])


def targeted(inputs, *, permitted=False, tool="literature.search"):
    manifest, cards, task, _, _, availability = inputs
    action = manifest["analyses"][0]["actions"][0]
    action.update(tool=tool, request="Invented target population arithmetic mean y with sampling uncertainty")
    cards["cards"][0].update(action_kind="targeted_retrieval", retrieval_action_id="R1")
    if permitted:
        task["information_policy"]["allowed_tools"] = [tool]
        task["budget"].update(source_queries=1, source_downloads=1)
        action["status"] = "planned"
        availability["retrieval_phase"] = "open"
    return inputs


def test_closed_zero_budget_proposal_cannot_grant_retrieval(routing_inputs):
    targeted(routing_inputs)
    before = copy.deepcopy(routing_inputs)
    report = route(routing_inputs)
    item = report["routes"][0]
    assert item["disposition"] == "retrieval_blocked"
    assert set(item["blockers"]) == {
        "acquisition_phase_closed", "tool_not_permitted", "author_declared_unavailable", "query_budget_insufficient"}
    assert report["initial_task_budget_remaining"] == report["after_estimated_plan"] == {"queries": 0, "downloads": 0}
    assert report["budget_reserved"] is report["retrieval_executed"] is report["candidate_modified"] is False
    assert routing_inputs == before


def test_open_snapshot_cannot_override_task_or_author_denial(routing_inputs):
    targeted(routing_inputs)
    routing_inputs[-1]["retrieval_phase"] = "open"
    routing_inputs[2]["budget"]["source_queries"] = 1
    item = route(routing_inputs)["routes"][0]
    assert item["disposition"] == "retrieval_blocked"
    assert set(item["blockers"]) == {"tool_not_permitted", "author_declared_unavailable"}


def test_permitted_plan_still_requires_adapter_and_is_not_a_reservation(routing_inputs):
    targeted(routing_inputs, permitted=True)
    before = copy.deepcopy(routing_inputs)
    report = route(routing_inputs)
    assert report == route(routing_inputs)
    item = report["routes"][0]
    assert item["disposition"] == "retrieval_proposed_adapter_recheck_required"
    assert item["estimated_planning_cost"] == {"queries": 1, "downloads": 0}
    assert report["after_estimated_plan"] == {"queries": 0, "downloads": 1}
    assert report["budget_reserved"] is item["executed"] is False
    assert routing_inputs == before


def test_used_query_budget_is_not_reset_by_a_new_card(routing_inputs):
    targeted(routing_inputs, permitted=True)
    routing_inputs[-1]["queries_used"] = 1
    report = route(routing_inputs)
    assert report["routes"][0]["blockers"] == ["query_budget_insufficient"]
    assert report["after_estimated_plan"]["queries"] == 0


def test_fetch_planning_accounts_for_a_possible_metadata_query(routing_inputs):
    targeted(routing_inputs, permitted=True, tool="literature.fetch")
    routing_inputs[2]["budget"]["source_queries"] = 0
    item = route(routing_inputs)["routes"][0]
    assert item["disposition"] == "retrieval_blocked"
    assert item["blockers"] == ["query_budget_insufficient"]


def test_supplement_fetch_does_not_require_an_unused_metadata_query(routing_inputs):
    targeted(routing_inputs, permitted=True, tool="literature.fetch-supplement")
    routing_inputs[2]["budget"]["source_queries"] = 0
    report = route(routing_inputs)
    item = report["routes"][0]
    assert item["disposition"] == "retrieval_proposed_adapter_recheck_required"
    assert item["estimated_planning_cost"] == {"queries": 0, "downloads": 1}
    assert report["budget_reserved"] is item["executed"] is False


def test_identical_requests_share_only_a_planning_allocation(routing_inputs):
    targeted(routing_inputs, permitted=True)
    manifest, cards, *_ = routing_inputs
    analysis = manifest["analyses"][0]
    for gap_id, card_id in [("G2", "shared_card"), ("G3", "distinct_card")]:
        analysis["gaps"].append({**copy.deepcopy(analysis["gaps"][0]), "id": gap_id})
        cards["cards"].append({**copy.deepcopy(cards["cards"][0]), "id": card_id, "gap_ids": [gap_id]})
    analysis["actions"][0]["gap_ids"].append("G2")
    analysis["actions"].append({**copy.deepcopy(analysis["actions"][0]), "id": "R2", "gap_ids": ["G3"],
                                "request": "A distinct invented population mean with uncertainty"})
    cards["cards"][2]["retrieval_action_id"] = "R2"
    report = route(routing_inputs)
    first, shared, distinct = report["routes"]
    assert first["shared_proposal_card_id"] is None
    assert shared["disposition"] == "shared_retrieval_proposal"
    assert shared["shared_proposal_card_id"] == first["card_id"]
    assert shared["estimated_planning_cost"] == {"queries": 0, "downloads": 0}
    assert distinct["disposition"] == "retrieval_blocked"
    assert distinct["blockers"] == ["query_budget_insufficient"]
    assert distinct["shared_proposal_card_id"] is None
    assert all(item["gap_status"] == "unresolved" and item["executed"] is False for item in report["routes"])
    assert report["budget_reserved"] is False


def test_unavailable_identical_request_cannot_inherit_another_cards_proposal(routing_inputs):
    targeted(routing_inputs, permitted=True)
    manifest, cards, *_ = routing_inputs
    analysis = manifest["analyses"][0]
    analysis["gaps"].append({**copy.deepcopy(analysis["gaps"][0]), "id": "G2"})
    analysis["actions"].append({**copy.deepcopy(analysis["actions"][0]), "id": "R2", "gap_ids": ["G2"],
                                "status": "unavailable"})
    cards["cards"].append({**copy.deepcopy(cards["cards"][0]), "id": "unavailable_card", "gap_ids": ["G2"],
                           "retrieval_action_id": "R2"})
    second = route(routing_inputs)["routes"][1]
    assert second["disposition"] == "retrieval_blocked"
    assert "author_declared_unavailable" in second["blockers"]
    assert second["shared_proposal_card_id"] is None


@pytest.mark.parametrize("attack", ["unknown_action", "wrong_gap_coverage", "none_tool", "binding_on_local"])
def test_retrieval_card_binding_cannot_bypass_existing_action_contract(routing_inputs, attack):
    targeted(routing_inputs)
    manifest, cards, *_ = routing_inputs
    analysis, card = manifest["analyses"][0], cards["cards"][0]
    if attack == "unknown_action":
        card["retrieval_action_id"] = "absent_action"
    elif attack == "wrong_gap_coverage":
        analysis["gaps"].append({**copy.deepcopy(analysis["gaps"][0]), "id": "G2"})
        analysis["actions"].append({**copy.deepcopy(analysis["actions"][0]), "id": "R2", "gap_ids": ["G2"]})
        card["gap_ids"] = ["G1", "G2"]
    elif attack == "none_tool":
        analysis["actions"][0]["tool"] = "none"
    else:
        card["action_kind"] = "local_reextract"
    with pytest.raises(ContractError):
        route(routing_inputs)


def test_local_reextraction_uses_only_its_linked_declared_source_locations(routing_inputs):
    _, cards, _, evidence, *_ = routing_inputs
    cards["cards"][0]["action_kind"] = "local_reextract"
    report = route(routing_inputs)
    item = report["routes"][0]
    assert item["source_locations"] == [{
        "evidence_id": "E1", "source_id": "S1", "locator": "Invented table 1",
        "declared_artifacts": evidence["sources"][0]["artifacts"],
    }]
    assert item["retrieval"] is None
    assert item["disposition"] == "local_review_proposed"
    assert any("does not verify registry or file bytes" in limitation for limitation in report["limitations"])
    item["source_locations"][0]["declared_artifacts"][0]["path"] = "output-mutated-path"
    assert evidence["sources"][0]["artifacts"][0]["path"] == "sources/invented.txt"
    cards["cards"][0]["evidence_ids"] = []
    with pytest.raises(ContractError, match="existing source artifacts"):
        route(routing_inputs)


@pytest.mark.parametrize("kind,diagnosis", [
    ("operator_review", "operator_missing"), ("scenario_review", "unverified_bridge"), ("limit_use", "missing_relation")])
def test_review_routes_never_supply_new_evidence_or_resolve_gaps(routing_inputs, kind, diagnosis):
    routing_inputs[1]["cards"][0].update(action_kind=kind, diagnosis=diagnosis)
    before = copy.deepcopy(routing_inputs)
    report = route(routing_inputs)
    item = report["routes"][0]
    assert item["gap_status"] == "unresolved"
    assert item["executed"] is False and item["retrieval"] is None
    assert report["declared_evidence_summary"]["analyses"][0]["declared_assessment"] == "transported"
    assert report["declared_evidence_summary"]["analyses"][0]["unresolved_gap_ids"] == ["G1"]
    assert report["scientific_validity"] == "not_assessed" and report["data_quality_gain"] == "not_tested"
    assert routing_inputs == before


@pytest.mark.parametrize("counter", [True, -1, 0.5])
def test_usage_snapshot_rejects_values_that_cannot_be_consumed_counts(routing_inputs, counter):
    routing_inputs[-1]["queries_used"] = counter
    with pytest.raises(ContractError):
        route(routing_inputs)


def test_caller_required_use_list_does_not_hide_additional_declared_uses(routing_inputs):
    manifest, cards, *_ = routing_inputs
    other = copy.deepcopy(manifest["analyses"][0])
    other["id"] = "additional_use"
    manifest["analyses"].append(other)
    cards["cards"].append({**copy.deepcopy(cards["cards"][0]), "id": "additional_card", "analysis_id": "additional_use"})
    report = route(routing_inputs)
    assert report["additional_declared_analysis_ids"] == ["additional_use"]
    assert len(report["routes"]) == 2
