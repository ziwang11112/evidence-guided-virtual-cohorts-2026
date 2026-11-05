"""Optional evidence-use gate over controller-supplied artifact bytes.

Checks declarations, references and actual specification differences. Never reads
files, executes code, chooses scientific parameters or certifies applicability.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import PurePosixPath

from .analysis_evidence import validate_analysis_evidence
from .contracts import ContractError, _hash, exact_keys, number, require, string_list, text, validate_evidence, validate_spec
from .lifecycle import _invalid_constant, _object, safe_relative


ROLES = {"task", "evidence", "model_spec", "analysis_evidence", "checks", "generator"}
BASELINE_ROLES = {"baseline_evidence", "baseline_model_spec", "baseline_generator"}
CHOICES = {"relationship", "dispersion", "check_only", "scenario", "retain_assumption"}
MODEL_USES = {"relationship", "dispersion", "scenario"}
RESERVED = {"task.json", "evidence.json", "model_spec.json", "analysis_evidence.json", "checks.json",
            "generator.py", "generated.csv", "decision.md", "freeze.json", "evidence_use_v1.json"}


def _json(raw, where):
    try:
        return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_object, parse_constant=_invalid_constant)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ContractError("Invalid bound JSON: " + where) from error


def _bound(binding, artifacts):
    exact_keys(binding, {"path", "sha256"}, where="artifact binding")
    safe_relative(binding["path"])
    _hash(binding["sha256"])
    require(binding["path"] in artifacts, "Missing bound artifact: " + binding["path"])
    raw = artifacts[binding["path"]]
    require(isinstance(raw, bytes), "Artifact content must be exact bytes")
    require(hashlib.sha256(raw).hexdigest() == binding["sha256"], "Artifact hash mismatch: " + binding["path"])
    return raw


def _escape(value):
    return value.replace("~", "~0").replace("/", "~1")


def _parts(pointer):
    text(pointer, "parameter pointer")
    require(pointer.startswith("/parameters/"), "Use an exact /parameters/... JSON pointer")
    parts = pointer[1:].split("/")
    decoded = [part.replace("~1", "/").replace("~0", "~") for part in parts]
    require("/" + "/".join(_escape(part) for part in decoded) == pointer, "Noncanonical JSON pointer")
    return decoded


def _resolve(spec, pointer):
    value = spec
    for part in _parts(pointer):
        if isinstance(value, dict):
            require(part in value, "Parameter pointer does not exist: " + pointer)
            value = value[part]
        elif isinstance(value, list):
            require(part.isascii() and part.isdigit() and str(int(part)) == part and int(part) < len(value),
                    "Invalid array parameter pointer: " + pointer)
            value = value[int(part)]
        else:
            raise ContractError("Parameter pointer traverses a scalar: " + pointer)
    return value


def _equal(before, after):
    # JSON bool is not the numerical value 0/1. Int/float formatting alone is
    # not a numerical parameter change.
    if isinstance(before, bool) != isinstance(after, bool):
        return False
    return before == after


def _diff(before, after, path="/parameters"):
    if isinstance(before, dict) and isinstance(after, dict):
        result = set()
        for key in before.keys() | after.keys():
            child = path + "/" + _escape(key)
            if key not in before or key not in after:
                result.add(child)
            else:
                result.update(_diff(before[key], after[key], child))
        return result
    if isinstance(before, list) and isinstance(after, list) and len(before) == len(after):
        return set().union(*(_diff(a, b, path + "/" + str(i)) for i, (a, b) in enumerate(zip(before, after))))
    return set() if _equal(before, after) else {path}


def _checks(checks, artifacts, parent, metadata_paths):
    exact_keys(checks, {"scope", "records", "artifacts"}, where="checks")
    require(isinstance(checks["scope"], str) and checks["scope"] in {"fixture_only", "source_only"},
            "Checks scope must exclude target feedback")
    require(isinstance(checks["records"], list) and bool(checks["records"]), "Check records required")
    records = {}
    for record in checks["records"]:
        exact_keys(record, {"name", "status", "detail"}, where="check record")
        text(record["name"], "check name")
        text(record["detail"], "check detail")
        require(record["name"] not in records, "Duplicate check name")
        require(isinstance(record["status"], str) and record["status"] in {"pass", "fail", "not_computable"},
                "Invalid check status")
        records[record["name"]] = record
    require(isinstance(checks["artifacts"], list), "Check artifacts must be a list")
    paths = set()
    for artifact in checks["artifacts"]:
        exact_keys(artifact, {"path", "sha256"}, where="check artifact")
        safe_relative(artifact["path"])
        require(PurePosixPath(artifact["path"]).name.casefold() not in RESERVED,
                "Check artifact must be an auxiliary result file")
        path = str(parent / artifact["path"])
        require(path.casefold() not in {p.casefold() for p in metadata_paths}, "Metadata cannot be a check-result artifact")
        require(artifact["path"].casefold() not in {p.casefold() for p in paths}, "Duplicate check artifact")
        _bound({"path": path, "sha256": artifact["sha256"]}, artifacts)
        paths.add(artifact["path"])
    require(paths or all(record["status"] == "not_computable" for record in records.values()),
            "Computed checks require bound result artifacts")
    return records, paths


def validate_evidence_use(manifest, artifacts, *, required_analysis_ids):
    """Return a structural report or raise ContractError; mutate nothing.

    `artifacts` maps portable paths to exact file bytes loaded by the controller.
    The controller selects the actual candidate/baseline and the requested-use
    IDs. This pure API does not authenticate those choices or verify a registry.
    Omit all baseline bindings for initial construction; provide all for revision.
    """
    exact_keys(manifest, {"schema_version", "bindings", "decisions"}, where="evidence use")
    require(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1,
            "Evidence-use schema_version must be 1")
    exact_keys(manifest["bindings"], ROLES, BASELINE_ROLES, where="evidence-use bindings")
    bindings = manifest["bindings"]
    revision = bool(BASELINE_ROLES & bindings.keys())
    require(not revision or BASELINE_ROLES <= bindings.keys(), "Revision requires every baseline binding")
    require(isinstance(artifacts, dict), "Artifacts must be a byte mapping")
    raw = {role: _bound(binding, artifacts) for role, binding in bindings.items()}
    paths = [binding["path"] for binding in bindings.values()]
    require(len(paths) == len({path.casefold() for path in paths}), "Bound roles must use distinct paths")
    candidate_parent = PurePosixPath(bindings["model_spec"]["path"]).parent
    for role in ROLES - {"task"}:
        expected_name = "generator.py" if role == "generator" else role + ".json"
        require(PurePosixPath(bindings[role]["path"]) == candidate_parent / expected_name,
                "Candidate metadata roles must name files in one candidate directory")
    if revision:
        baseline_parent = PurePosixPath(bindings["baseline_model_spec"]["path"]).parent
        require(str(baseline_parent).casefold() != str(candidate_parent).casefold(),
                "Revision baseline must be a distinct candidate")
        for role in BASELINE_ROLES:
            name = role.removeprefix("baseline_")
            expected_name = "generator.py" if name == "generator" else name + ".json"
            require(PurePosixPath(bindings[role]["path"]) == baseline_parent / expected_name,
                    "Baseline roles must name files in one baseline directory")
    objects = {role: _json(value, role) for role, value in raw.items() if not role.endswith("generator")}
    task, evidence, spec = (objects[role] for role in ("task", "evidence", "model_spec"))
    analysis_manifest = objects["analysis_evidence"]
    validate_analysis_evidence(analysis_manifest, task, evidence, spec)
    baseline = None
    if revision:
        baseline = objects["baseline_model_spec"]
        validate_spec(baseline, validate_evidence(objects["baseline_evidence"], task))
    records, check_paths = _checks(objects["checks"], artifacts, candidate_parent, set(paths))
    analyses = {analysis["id"]: analysis for analysis in analysis_manifest["analyses"]}
    string_list(required_analysis_ids, "required analysis IDs", nonempty=True)
    require(set(required_analysis_ids) <= analyses.keys(), "Missing required analytical use")
    require(isinstance(manifest["decisions"], list) and bool(manifest["decisions"]), "Evidence-use decisions required")
    actual_changes = _diff(baseline["parameters"], spec["parameters"]) if revision else set()
    claimed_changes, seen_ids, covered_analyses, decisions = set(), set(), set(), []
    for decision in manifest["decisions"]:
        exact_keys(decision, {"id", "analysis_id", "evidence_ids", "choice", "parameter_paths",
                              "assumption_ids", "check_names", "check_artifact_paths"}, where="evidence-use decision")
        text(decision["id"], "decision ID")
        require(decision["id"] not in seen_ids, "Duplicate decision ID")
        seen_ids.add(decision["id"])
        text(decision["analysis_id"], "decision analysis ID")
        require(decision["analysis_id"] in analyses, "Unknown decision analysis")
        analysis = analyses[decision["analysis_id"]]
        covered_analyses.add(analysis["id"])
        choice = decision["choice"]
        require(isinstance(choice, str) and choice in CHOICES, "Invalid evidence-use choice")
        for field in ("evidence_ids", "parameter_paths", "assumption_ids", "check_names", "check_artifact_paths"):
            string_list(decision[field], "decision " + field, nonempty=field == "check_names")
        links = {link["evidence_id"]: link for link in analysis["evidence_links"]}
        eids, aids = set(decision["evidence_ids"]), set(decision["assumption_ids"])
        require(eids <= links.keys(), "Decision evidence must be linked to its analysis")
        require(aids <= set(analysis["assumption_ids"]), "Decision assumptions must belong to its analysis")
        require(set(decision["check_names"]) <= records.keys(), "Unknown decision check name")
        require(set(decision["check_artifact_paths"]) <= check_paths, "Unknown decision check artifact")
        computed = any(records[name]["status"] != "not_computable" for name in decision["check_names"])
        require(not computed or bool(decision["check_artifact_paths"]), "Computed decision check needs an artifact")
        if choice == "check_only":
            require(eids and not decision["parameter_paths"], "Check-only needs evidence and no parameter paths")
        if choice in MODEL_USES:
            require((eids or aids) and decision["parameter_paths"],
                    "Model use needs evidence or explicit assumptions and concrete parameter paths")
        if choice == "scenario":
            require(aids, "Scenario needs explicit assumptions")
        if choice == "retain_assumption":
            require((eids or aids) and decision["parameter_paths"],
                    "Retention needs evidence or assumptions and parameter paths")
        # Bridge requirements use existing typed comparisons and unresolved gaps.
        # They cannot find missing scientific assumptions hidden in prose.
        needed_assumptions = set()
        if choice in MODEL_USES:
            for eid in eids:
                link = links[eid]
                needed_assumptions.update(link["assumption_ids"])
                for dimension, comparison in link["comparisons"].items():
                    if dimension == "estimand" or comparison == "declared_match":
                        continue
                    gaps = [gap for gap in analysis["gaps"] if gap["dimension"] == dimension]
                    bridges = set(link["assumption_ids"]) & {aid for gap in gaps for aid in gap["assumption_ids"]}
                    require(bridges, "Unmarked " + dimension + " bridge assumption")
                    needed_assumptions.update(bridges)
            require(needed_assumptions <= aids, "Decision omits linked bridge assumptions")
        effects = {}
        for pointer in decision["parameter_paths"]:
            parts = _parts(pointer)
            # A removed parameter is allowed only as an explicitly scoped scenario
            # change; its provenance remains available in the bound baseline.
            removed = False
            try:
                _resolve(spec, pointer)
            except ContractError:
                removed = revision and pointer in actual_changes
                require(removed, "Parameter pointer does not exist: " + pointer)
            owner = baseline if removed else spec
            value = _resolve(owner, pointer)
            provenance = owner["parameter_provenance"][parts[1]]
            require(eids <= set(provenance["evidence_ids"]) and aids <= set(provenance["assumption_ids"]),
                    "Decision evidence/assumptions missing from parameter provenance")
            if choice in {"relationship", "dispersion"}:
                require(not removed, "Numerical evidence use cannot remove a parameter")
                number(value, "numerical evidence-use parameter")
            if revision:
                overlaps_change = any(pointer == changed or pointer.startswith(changed + "/") or
                                      changed.startswith(pointer + "/") for changed in actual_changes)
                if choice in MODEL_USES:
                    require(pointer in actual_changes or not overlaps_change,
                            "Declared use does not match an exact changed parameter path")
                    if pointer in actual_changes:
                        claimed_changes.add(pointer)
                else:
                    require(not overlaps_change, "Retained parameter path actually changed")
                effects[pointer] = "removed" if removed else "changed" if pointer in actual_changes else "unchanged"
            else:
                effects[pointer] = "initial_value_bound"
        decisions.append({"id": decision["id"], "analysis_id": analysis["id"], "choice": choice,
                          "parameter_paths": list(decision["parameter_paths"]),
                          "parameter_effects": effects,
                          "support_origin": "evidence_and_assumptions" if eids and aids else
                                            "evidence_only" if eids else "assumption_only",
                          "check_statuses": {name: records[name]["status"] for name in decision["check_names"]},
                          "unresolved_gap_ids": [gap["id"] for gap in analysis["gaps"]]})
    require(set(required_analysis_ids) <= covered_analyses, "Every required analysis needs an evidence-use decision")
    require(not revision or claimed_changes == actual_changes, "Unaccounted changed parameter paths")
    return {
        "schema_version": 1, "scope": "artifact_binding_and_declared_specification_use_only",
        "contract": "structurally_valid", "mode": "revision" if revision else "initial",
        "parameter_status": ("changed" if actual_changes else "unchanged") if revision else "initial_values_bound",
        "changed_parameter_paths": sorted(actual_changes) if revision else None,
        "generator_bytes_changed": raw["generator"] != raw["baseline_generator"] if revision else None,
        "specification_bytes_changed": raw["model_spec"] != raw["baseline_model_spec"] if revision else None,
        "decisions": decisions, "generator_parameter_use": "not_assessed", "scientific_validity": "not_assessed",
        "data_quality_gain": "not_tested", "check_execution": "not_verified",
        "limitations": [
            "Controller supplies the actual candidate, baseline, requested analysis IDs and bytes; source admission remains external.",
            "Relationship/dispersion/scenario meanings and bridge completeness remain scientific declarations.",
            "Byte bindings and check records do not prove generator parameter use or execution of a check.",
            "Parameter no-change does not imply unchanged code, provenance, assumptions or scientific validity.",
        ],
    }
