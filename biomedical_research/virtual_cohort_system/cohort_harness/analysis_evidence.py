"""Structural validation of declared analytical uses, evidence links and gaps.

This module never reads rows, executes generators, retrieves evidence or decides
scientific applicability. Assessment and comparison labels are the submitter's
judgments. A reported source estimand does not identify a target joint law.
"""
from __future__ import annotations

from .contracts import (
    exact_keys, number, require, string_list, text, validate_evidence, validate_spec,
)


KINDS = {"mean", "sd", "median", "quantile", "correlation", "spearman_correlation",
         "ols_coefficient", "proportion", "reported_other"}
DIMENSIONS = {"estimand", "population", "measurement", "selection", "conditioning",
              "adjustment", "scale"}
COMPARISONS = {"declared_match", "declared_difference", "unknown"}
GAP_DIMENSIONS = DIMENSIONS | {"joint_distribution", "interaction", "uncertainty", "other"}
RETRIEVAL_TOOLS = {"literature.search", "literature.fetch", "literature.list-supplements",
                   "literature.fetch-supplement"}


def _records(value, where, *, nonempty=False):
    require(isinstance(value, list), f"{where} must be a list")
    require(not nonempty or bool(value), f"{where} must be nonempty")


def _references(value, known, where, *, nonempty=False):
    string_list(value, where, nonempty=nonempty)
    require(set(value) <= known, f"Unknown {where}")


def _identifier(value, seen, where):
    text(value, where)
    require(value not in seen, f"Duplicate {where}")
    seen.add(value)


def _estimand(value, columns):
    exact_keys(value, {"description", "kind", "outcome", "exposures", "conditioning",
                       "adjustment", "scale", "unit", "population", "measurement", "selection"},
               {"statistic_name", "q", "method"}, where="requested estimand")
    for field in ("description", "outcome", "scale", "unit", "population", "measurement", "selection"):
        text(value[field], "estimand." + field)
    require(value["outcome"] in columns, "Unknown estimand outcome")
    require(isinstance(value["kind"], str) and value["kind"] in KINDS, "Invalid estimand kind")
    for field in ("exposures", "conditioning", "adjustment"):
        _references(value[field], columns, "estimand " + field)
        require(value["outcome"] not in value[field], "Outcome cannot also be a predictor/conditioner")
    require(not (set(value["exposures"]) & set(value["adjustment"])),
            "Exposure and adjustment roles must be distinct")
    if value["kind"] in {"correlation", "spearman_correlation", "ols_coefficient"}:
        require(len(value["exposures"]) == 1, "Association/coefficient estimand needs one focal exposure")
    elif value["kind"] != "reported_other":
        require(not value["exposures"], "Marginal summary estimand has no exposure")
    if value["kind"] == "reported_other":
        text(value.get("statistic_name"), "estimand.statistic_name")
    else:
        require("statistic_name" not in value, "statistic_name only applies to reported_other")
    if value["kind"] in {"median", "quantile"}:
        require(isinstance(value.get("method"), str) and
                value["method"] in {"linear", "not_reported"}, "Invalid requested quantile method")
    else:
        require("method" not in value, "method only applies to median/quantile")
    if value["kind"] == "quantile":
        require("q" in value, "Requested quantile needs q")
        number(value["q"], "estimand.q")
        require(0 <= value["q"] <= 1, "Requested quantile q outside [0,1]")
    else:
        require("q" not in value, "q only applies to quantile")


def _same_statistic(request, item):
    """Check only fields the existing evidence schema actually represents."""
    return (request["kind"] == item["kind"] and
            all(request.get(field) == item.get(field)
                for field in ("statistic_name", "q", "method")))


def validate_analysis_evidence(manifest, task, evidence, model_spec):
    """Validate declarations/references, including evidence and spec contracts.

    The optional sidecar itself owns its requested-use list. This API cannot
    establish that the submitter included every use the user intended. It does
    not require task-population equality: source replay copies this target-use
    declaration unchanged into a derived source execution task.
    """
    evidence_ids = validate_evidence(evidence, task)
    validate_spec(model_spec, evidence_ids)
    exact_keys(manifest, {"schema_version", "analyses"}, where="analysis evidence")
    require(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1,
            "analysis evidence schema_version must be 1")
    _records(manifest["analyses"], "analyses", nonempty=True)
    items = {item["id"]: item for item in evidence["items"]}
    assumptions = {item["id"] for item in model_spec["assumptions"]}
    columns = {column["name"] for column in task["columns"] if column["role"] != "identifier"}
    analysis_ids = set()
    for analysis in manifest["analyses"]:
        exact_keys(analysis, {"id", "estimand", "assessment", "rationale", "assumption_ids",
                              "evidence_links", "gaps", "actions"}, where="analysis")
        _identifier(analysis["id"], analysis_ids, "analysis ID")
        _estimand(analysis["estimand"], columns)
        request = analysis["estimand"]
        require(isinstance(analysis["assessment"], str) and analysis["assessment"] in
                {"directly_reported", "transported", "partial", "unassessed"}, "Invalid declared assessment")
        text(analysis["rationale"], "analysis rationale")
        _references(analysis["assumption_ids"], assumptions, "analysis assumptions")
        local_assumptions = set(analysis["assumption_ids"])
        _records(analysis["evidence_links"], "evidence links")
        links, direct = set(), []
        for link in analysis["evidence_links"]:
            exact_keys(link, {"evidence_id", "relation", "comparisons", "assumption_ids", "rationale"},
                       where="analysis evidence link")
            _identifier(link["evidence_id"], links, "linked evidence ID")
            require(link["evidence_id"] in items, "Unknown linked evidence ID")
            require(isinstance(link["relation"], str) and
                    link["relation"] in {"direct_estimand", "component"}, "Invalid evidence relation")
            text(link["rationale"], "evidence-link rationale")
            _references(link["assumption_ids"], local_assumptions, "link assumptions")
            comparisons = link["comparisons"]
            exact_keys(comparisons, DIMENSIONS, where="declared comparisons")
            require(all(isinstance(v, str) and v in COMPARISONS for v in comparisons.values()),
                    "Invalid declared comparison")
            item = items[link["evidence_id"]]
            same_statistic = _same_statistic(request, item)
            if link["relation"] == "direct_estimand":
                require(same_statistic, "Direct-estimand link cannot substitute a different statistic/definition")
                direct.append(link)
            if comparisons["estimand"] == "declared_match":
                require(same_statistic, "Declared estimand match uses a different statistic/definition")
                require(set(item["variables"]) == {request["outcome"], *request["exposures"]},
                        "Declared estimand match has a different variable set")
            if comparisons["adjustment"] == "declared_match":
                require(set(item["adjustment"]) == set(request["adjustment"]),
                        "Declared adjustment match has a different adjustment set")
            if comparisons["scale"] == "declared_match":
                require(item["unit"] == request["unit"], "Declared scale match has a different unit label")

        _records(analysis["gaps"], "analysis gaps")
        gap_ids = set()
        for gap in analysis["gaps"]:
            exact_keys(gap, {"id", "dimension", "description", "consequence", "assumption_ids"},
                       where="unresolved analysis gap")
            _identifier(gap["id"], gap_ids, "gap ID")
            require(isinstance(gap["dimension"], str) and gap["dimension"] in GAP_DIMENSIONS,
                    "Invalid gap dimension")
            for field in ("description", "consequence"):
                text(gap[field], "gap " + field)
            _references(gap["assumption_ids"], local_assumptions, "gap assumptions")
        gap_dimensions = {gap["dimension"] for gap in analysis["gaps"]}
        for link in analysis["evidence_links"]:
            for dimension, comparison in link["comparisons"].items():
                if comparison != "declared_match":
                    covered = dimension in gap_dimensions or (
                        dimension == "estimand" and bool(gap_dimensions & {"joint_distribution", "interaction"}))
                    require(covered, "Every declared difference/unknown needs a corresponding unresolved gap")

        _records(analysis["actions"], "retrieval actions")
        action_ids, addressed = set(), set()
        for action in analysis["actions"]:
            exact_keys(action, {"id", "gap_ids", "tool", "request", "status", "reason"},
                       where="planned retrieval action")
            _identifier(action["id"], action_ids, "action ID")
            _references(action["gap_ids"], gap_ids, "action gaps", nonempty=True)
            addressed.update(action["gap_ids"])
            for field in ("request", "reason"):
                text(action[field], "action " + field)
            require(isinstance(action["tool"], str) and action["tool"] in RETRIEVAL_TOOLS | {"none"},
                    "Unknown retrieval tool")
            require(isinstance(action["status"], str) and action["status"] in {"planned", "unavailable"},
                    "Action is a plan, not a claim of executed retrieval")
            if action["status"] == "planned":
                require(task["information_policy"]["mode"] == "published_evidence" and
                        action["tool"] in RETRIEVAL_TOOLS and
                        action["tool"] in task["information_policy"]["allowed_tools"],
                        "Planned retrieval tool is not permitted by task")
                if action["tool"] == "literature.list-supplements":
                    budget = task["budget"]["source_queries"] + task["budget"]["source_downloads"]
                else:
                    budget_key = "source_queries" if action["tool"] == "literature.search" else "source_downloads"
                    budget = task["budget"][budget_key]
                require(budget > 0, "Planned retrieval has zero task budget")
        require(addressed == gap_ids, "Every unresolved gap needs a planned or unavailable action")

        assessment = analysis["assessment"]
        if assessment == "directly_reported":
            require(bool(direct) and len(direct) == len(analysis["evidence_links"]),
                    "Directly reported assessment requires direct-estimand links only")
            require(not gap_ids and not local_assumptions, "Directly reported assessment cannot hide gaps/assumptions")
            require(all(all(v == "declared_match" for v in link["comparisons"].values()) for link in direct),
                    "Directly reported assessment requires all declared context matches")
        else:
            require(bool(gap_ids), "Non-direct assessment must retain unresolved gaps")
            if assessment == "unassessed":
                require(not links, "Unassessed assessment has no claimed evidence coverage")
            elif assessment == "partial":
                require(bool(links), "Partial assessment needs at least one evidence link")
            else:
                require(bool(direct) and bool(local_assumptions),
                        "Transported assessment requires a source estimand and explicit assumptions")
                require(any(any(v != "declared_match" for v in link["comparisons"].values())
                            for link in direct), "Transported assessment needs a declared difference/unknown")
                require(all(link["assumption_ids"] for link in direct),
                        "Transported direct links must name their bridge assumptions")


def summarize_analysis_evidence(manifest, task, evidence, model_spec):
    """Return deterministic structural diagnostics, never a support/confidence score."""
    validate_analysis_evidence(manifest, task, evidence, model_spec)
    sources = {source["id"]: source for source in evidence["sources"]}
    items = {item["id"]: item for item in evidence["items"]}
    analyses = []
    for analysis in manifest["analyses"]:
        source_ids = sorted({items[link["evidence_id"]]["source_id"] for link in analysis["evidence_links"]})
        cohorts = {}
        for source_id in source_ids:
            for cohort_id in sources[source_id]["cohort_ids"]:
                cohorts.setdefault(cohort_id.strip().casefold(), set()).add(source_id)
        analyses.append({
            "id": analysis["id"], "declared_assessment": analysis["assessment"],
            "evidence_ids": [link["evidence_id"] for link in analysis["evidence_links"]],
            "assumption_ids": list(analysis["assumption_ids"]),
            "unresolved_gap_ids": [gap["id"] for gap in analysis["gaps"]],
            "planned_action_ids": [action["id"] for action in analysis["actions"] if action["status"] == "planned"],
            "unavailable_action_ids": [action["id"] for action in analysis["actions"] if action["status"] == "unavailable"],
            "shared_declared_cohorts": {cohort: sorted(ids) for cohort, ids in sorted(cohorts.items()) if len(ids) > 1},
            "unknown_cohort_sources": [source_id for source_id in source_ids if not sources[source_id]["cohort_ids"]],
        })
    return {
        "schema_version": 1, "scope": "declarations_and_references_only", "contract": "structurally_valid",
        "assessment_origin": "submitter_declaration", "scientific_validity": "not_assessed",
        "joint_distribution_identification": "not_assessed", "uncertainty_calibration": "not_assessed",
        "retrieval_executed": False, "analyses": analyses,
        "limitations": [
            "Requested-use completeness and source context comparisons are submitter declarations.",
            "Analysis-to-model dependency and assumption completeness are not inferred from generator code.",
            "Variable sets and unit labels do not establish estimand direction or measurement equivalence.",
            "Pairwise summaries do not by themselves identify a joint law or downstream analytical validity.",
            "Source-check/replay success and repeated seeds do not supply independent evidence or calibrated precision.",
            "Plans do not reserve budget; actual retrieval must use the task-bound adapter and its remaining budget.",
        ],
    }
