"""Pure declaration/reference checks; never execute code, inspect rows, or admit evidence.

The caller supplies already admitted evidence and a model specification. Canonical
JSON digests here bind metadata values; they are NOT raw artifact/file hashes.
Full task/evidence validation and frozen artifact verification remain caller work.
"""
from __future__ import annotations

import hashlib
import json
import math
import re


ROLES = frozenset({"numerical_constraint", "qualified_numerical_comparison",
                   "qualitative_context", "unused"})
NUMERICAL_ROLES = frozenset({"numerical_constraint", "qualified_numerical_comparison"})
GAP_DIMENSIONS = frozenset({"estimand", "population", "measurement", "selection",
                            "conditioning", "adjustment", "scale", "joint_distribution",
                            "interaction", "uncertainty", "other"})


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _text(value, where):
    _require(isinstance(value, str) and bool(value.strip()), f"{where} must be nonempty text")


def _keys(value, required, where, optional=frozenset()):
    _require(isinstance(value, dict), f"{where} must be an object")
    _require(all(isinstance(key, str) for key in value), f"{where} keys must be strings")
    _require(required <= set(value), f"{where} missing fields: {sorted(required - set(value))}")
    _require(set(value) <= required | optional,
             f"{where} unknown fields: {sorted(set(value) - required - optional)}")


def _list(value, where):
    _require(isinstance(value, list), f"{where} must be a list")


def _refs(value, where, known=None, *, nonempty=False):
    _list(value, where)
    for entry in value:
        _text(entry, where)
    _require(len(value) == len(set(value)), f"Duplicate {where}")
    _require(not nonempty or bool(value), f"{where} must be nonempty")
    _require(known is None or set(value) <= known, f"Unknown {where}")


def _json_value(value, where):
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        _require(math.isfinite(value), f"{where} contains a nonfinite number")
    elif isinstance(value, list):
        for item in value:
            _json_value(item, where)
    elif isinstance(value, dict):
        _require(all(isinstance(key, str) for key in value), f"{where} keys must be strings")
        for item in value.values():
            _json_value(item, where)
    else:
        raise ValueError(f"{where} contains a non-JSON value")


def canonical_json_sha256(value):
    """SHA-256 of UTF-8 JSON, sorted keys, compact separators, unescaped Unicode.

    The input must contain only JSON types and finite numbers. This digest is
    deliberately independent of input file whitespace/key order, not file bytes.
    """
    try:
        _json_value(value, "hash input")
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, UnicodeError, RecursionError) as error:
        raise ValueError("Hash input must be finite, acyclic UTF-8 JSON") from error
    return hashlib.sha256(encoded).hexdigest()


def _hash_matches(value, expected, where):
    _require(isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None,
             f"{where} must be a lowercase SHA-256 digest")
    _require(value == expected, f"{where} mismatch")


def _evidence_index(evidence):
    """Check the reference-bearing slice, not task admission or statistic semantics."""
    _keys(evidence, {"schema_version", "sources", "items"}, "evidence")
    _require(type(evidence["schema_version"]) is int and evidence["schema_version"] == 1,
             "evidence schema_version must be 1")
    _list(evidence["sources"], "evidence sources")
    _list(evidence["items"], "evidence items")
    sources, items = {}, {}
    for source in evidence["sources"]:
        _keys(source, {"id", "identifier", "population", "measurement", "cohort_ids", "artifacts"},
              "source")
        for key in ("id", "identifier", "population", "measurement"):
            _text(source[key], "source " + key)
        _require(source["id"] not in sources, "Duplicate source ID")
        _refs(source["cohort_ids"], "source cohort IDs")
        _list(source["artifacts"], "source artifacts")
        _require(bool(source["artifacts"]), "source artifacts must be nonempty")
        paths = []
        for artifact in source["artifacts"]:
            _keys(artifact, {"path", "sha256"}, "source artifact")
            _text(artifact["path"], "source artifact path")
            _require(isinstance(artifact["sha256"], str) and
                     re.fullmatch(r"[a-f0-9]{64}", artifact["sha256"]), "Invalid source artifact SHA-256")
            paths.append(artifact["path"])
        _refs(paths, "source artifact paths")
        sources[source["id"]] = source
    for item in evidence["items"]:
        _keys(item, {"id", "source_id", "locator", "variables", "kind", "estimate", "unit",
                     "uncertainty", "adjustment", "selection", "applicability"}, "evidence item",
              {"statistic_name", "q", "method"})
        for key in ("id", "source_id", "locator", "kind", "selection", "applicability"):
            _text(item[key], "evidence item " + key)
        _require(isinstance(item["unit"], str), "evidence item unit must be text")
        _refs(item["variables"], "evidence variables")
        _refs(item["adjustment"], "evidence adjustment")
        _require(isinstance(item["uncertainty"], dict), "evidence uncertainty must be an object")
        _require(item["id"] not in items, "Duplicate admitted evidence ID")
        _require(item["source_id"] in sources, "Unknown admitted evidence source")
        items[item["id"]] = item
    return sources, items


def _model_references(model_spec, evidence_ids):
    _keys(model_spec, {"parameters", "assumptions", "parameter_provenance"}, "model_spec")
    _require(isinstance(model_spec["parameters"], dict), "model_spec parameters must be an object")
    parameters = set(model_spec["parameters"])
    for parameter in parameters:
        _text(parameter, "parameter name")
    _list(model_spec["assumptions"], "model assumptions")
    assumptions = set()
    for assumption in model_spec["assumptions"]:
        _keys(assumption, {"id", "description"}, "model assumption")
        _text(assumption["id"], "assumption ID")
        _text(assumption["description"], "assumption description")
        _require(assumption["id"] not in assumptions, "Duplicate assumption ID")
        assumptions.add(assumption["id"])
    provenance = model_spec["parameter_provenance"]
    _require(isinstance(provenance, dict) and set(provenance) == parameters,
             "Parameter provenance keys must exactly match parameters")
    for entry in provenance.values():
        _keys(entry, {"evidence_ids", "assumption_ids", "derivation"}, "parameter provenance")
        _refs(entry["evidence_ids"], "parameter evidence IDs", evidence_ids)
        _refs(entry["assumption_ids"], "parameter assumption IDs", assumptions)
        _text(entry["derivation"], "parameter derivation")
        _require(bool(entry["evidence_ids"] or entry["assumption_ids"]), "Parameter lacks provenance")
    return parameters, assumptions


def assess_evidence_use(manifest, evidence, model_spec, *, recipe_check_ids=None):
    """Return a JSON-compatible declaration report, or raise ValueError.

    `recipe_check_ids`, when supplied, is a duplicate-free list of actual recipe
    IDs. Membership is checked; check/evidence correspondence and execution are
    not inferred. No file paths or code references are opened or executed.
    """
    evidence_hash = canonical_json_sha256(evidence)
    canonical_json_sha256(manifest)
    canonical_json_sha256(model_spec)
    sources, items = _evidence_index(evidence)
    parameters, assumptions = _model_references(model_spec, set(items))
    allowed_checks = None
    if recipe_check_ids is not None:
        _refs(recipe_check_ids, "recipe check IDs")
        allowed_checks = set(recipe_check_ids)
    _keys(manifest, {"schema_version", "evidence_sha256", "items"}, "evidence-use manifest")
    _require(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1,
             "evidence-use schema_version must be 1")
    _hash_matches(manifest["evidence_sha256"], evidence_hash, "canonical evidence SHA-256")
    _list(manifest["items"], "evidence-use items")
    seen, used_checks, reports = set(), set(), []
    for record in manifest["items"]:
        _keys(record, {"evidence_id", "role", "source_reference", "context_id", "check_ids",
                       "parameter_names", "structure_names", "code_references", "assumption_ids",
                       "gaps", "rationale", "source_comparison"}, "evidence-use item")
        evidence_id = record["evidence_id"]
        _text(evidence_id, "evidence-use ID")
        _require(evidence_id not in seen, "Duplicate evidence-use ID")
        _require(evidence_id in items, "Unknown evidence-use ID")
        seen.add(evidence_id)
        role = record["role"]
        _require(isinstance(role, str) and role in ROLES, "Unknown evidence-use role")
        _text(record["rationale"], "evidence-use rationale")
        reference = record["source_reference"]
        _keys(reference, {"source_id", "source_sha256", "item_sha256"}, "source reference")
        item = items[evidence_id]
        _require(reference["source_id"] == item["source_id"], "Source reference ID mismatch")
        _hash_matches(reference["source_sha256"], canonical_json_sha256(sources[item["source_id"]]),
                      "canonical source metadata SHA-256")
        _hash_matches(reference["item_sha256"], canonical_json_sha256(item),
                      "canonical evidence item SHA-256")
        _refs(record["check_ids"], "check IDs", allowed_checks)
        _require(not used_checks.intersection(record["check_ids"]),
                 "Duplicate check reference across evidence items")
        used_checks.update(record["check_ids"])
        _refs(record["parameter_names"], "parameter names", parameters)
        _refs(record["assumption_ids"], "assumption IDs", assumptions)
        _list(record["code_references"], "code references")
        code_seen, symbols = set(), set()
        for reference in record["code_references"]:
            _keys(reference, {"path", "symbol"}, "code reference")
            _text(reference["path"], "code reference path")
            _text(reference["symbol"], "code reference symbol")
            pair = (reference["path"], reference["symbol"])
            _require(pair not in code_seen, "Duplicate code reference")
            code_seen.add(pair)
            symbols.add(reference["symbol"])
        _refs(record["structure_names"], "structure names", symbols)
        _list(record["gaps"], "gaps")
        gaps = set()
        for gap in record["gaps"]:
            _keys(gap, {"id", "dimension", "description", "assumption_ids"}, "gap")
            _text(gap["id"], "gap ID")
            _require(gap["id"] not in gaps, "Duplicate gap ID")
            gaps.add(gap["id"])
            _require(isinstance(gap["dimension"], str) and gap["dimension"] in GAP_DIMENSIONS,
                     "Unknown gap dimension")
            _text(gap["description"], "gap description")
            _refs(gap["assumption_ids"], "gap assumption IDs", set(record["assumption_ids"]))
        context_id = record["context_id"]
        if context_id is not None:
            _text(context_id, "context ID")
        if role in NUMERICAL_ROLES:
            _text(context_id, "numeric context ID")
            _require(bool(record["check_ids"]), "Numeric use requires check IDs")
            _require(bool(record["code_references"]), "Numeric use requires code references")
            _require(bool(record["parameter_names"] or record["structure_names"]),
                     "Numeric use requires parameter or structure references")
            _require(type(item["estimate"]) in (int, float) and item["kind"] != "contextual",
                     "Numeric use requires a numerical evidence estimate")
            if role == "numerical_constraint":
                _require(record["source_comparison"] == "declared_strict",
                         "Numerical constraint requires declared_strict comparison")
                _require(not record["assumption_ids"] and not record["gaps"],
                         "Strict source comparison cannot hide assumptions or gaps")
            else:
                _require(record["source_comparison"] == "qualified",
                         "Qualified use cannot claim strict source replay")
                _require(bool(record["assumption_ids"]), "Qualified use requires explicit assumptions")
        else:
            _require(not record["check_ids"], "Nonnumeric use cannot bind numeric checks")
            _require(record["source_comparison"] == "not_applicable",
                     "Nonnumeric use cannot claim source comparison")
            if role == "unused":
                _require(not record["parameter_names"] and not record["structure_names"] and
                         not record["code_references"], "Unused evidence cannot claim model influence")
        reports.append({"evidence_id": evidence_id, "declared_role": role,
                        "declared_source_comparison": record["source_comparison"],
                        "context_id": context_id, "check_ids": sorted(record["check_ids"]),
                        "parameter_names": sorted(record["parameter_names"]),
                        "structure_names": sorted(record["structure_names"]),
                        "assumption_ids": sorted(record["assumption_ids"]),
                        "gap_ids": sorted(gaps), "declaration_valid": True,
                        "executed_uptake": "not_verified", "source_fidelity": "not_verified"})
    _require(seen == set(items), f"Missing admitted evidence-use items: {sorted(set(items) - seen)}")
    return {"schema_version": 1, "kind": "evidence_use_declaration_v1",
            "scope": "declarations_and_references_only", "declaration_valid": True,
            "canonical_evidence_sha256": evidence_hash,
            "recipe_check_membership_verified": allowed_checks is not None,
            "executed_uptake": "not_verified", "source_fidelity": "not_verified",
            "verification_needed": ["frozen_artifact_and_source_provenance_verification",
                                    "recipe_check_to_evidence_and_operator_binding",
                                    "source_context_and_measurement_review",
                                    "code_reference_and_parameter_dependency_review",
                                    "authenticated_source_execution_and_feedback"],
            "items": sorted(reports, key=lambda report: report["evidence_id"]),
            "limitations": ["Input evidence admission and full task/evidence contracts are caller responsibilities.",
                            "Canonical metadata digests are not raw artifact hashes or authenticity proofs.",
                            "Roles and exact/qualified comparisons are declarations, not executed uptake or source fidelity.",
                            "Code symbols, context validity, and assumption completeness are not verified.",
                            "No generator, data, source statistic, target outcome, or network is accessed."]}
