"""Read-only, execution-bound qualified source comparisons; never strict replay.

The original semantic v1 result is retained unchanged. Only explicitly reviewed
equal-weight point functionals are computed, using the existing arithmetic.
This module neither launches generators nor writes receipts or approvals.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import numpy as np

from cohort_harness import contracts, execution, semantic_feedback_v1 as semantic, source_checks
from cohort_harness.lifecycle import _bundle, _candidate, _path, read_json, read_table, sha256, verify_candidate

BRIDGE_PLAN = "context_bridge_v1.json"
KINDS = {"ols_coefficient", "correlation", "spearman_correlation"}
require = contracts.require


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def declaration_digest(declaration):
    """Digest supplied to an independent reviewer; no review is manufactured."""
    return hashlib.sha256(canonical(declaration).encode("utf-8")).hexdigest()


def _exact(value, fields, where):
    contracts.exact_keys(value, set(fields.split()), where=where)


def _same(left, right, message):
    require(canonical(left) == canonical(right), message)


def _assumptions(values, known, where):
    contracts.string_list(values, where, nonempty=True)
    require(set(values) <= known, "Unknown " + where)


def _review(declaration, review):
    _exact(review, "decision independent reviewer_id producer_id reviewed_utc reason approved_sha256", "qualified review")
    require(review["decision"] == "approved" and review["independent"] is True, "Independent approval required")
    for key in ("reviewer_id", "producer_id", "reviewed_utc", "reason"):
        contracts.text(review[key], key)
    require(review["reviewer_id"].strip().casefold() != review["producer_id"].strip().casefold(), "Reviewer is producer")
    require(review["approved_sha256"] == declaration_digest(declaration), "Qualified review commitment mismatch")


def _alias_contract(aliases, columns, known):
    """One-step names for the same generated values, preserving every contract."""
    require(isinstance(aliases, list) and len(aliases) <= 32, "Column aliases must be a finite list")
    mapped = copy.deepcopy(columns)
    origins = {name: name for name in columns}
    for alias in aliases:
        _exact(alias, "source_name generated_name assumption_ids", "column alias")
        source, generated = alias["source_name"], alias["generated_name"]
        contracts.text(source, "source alias name")
        contracts.text(generated, "generated alias name")
        require(source not in mapped, "Column alias must be unique and cannot overwrite a column")
        require(generated in columns, "Alias must reference an original generated column; chains are forbidden")
        column = columns[generated]
        numeric = column["kind"] in {"number", "integer"} or (
            column["kind"] == "category" and all(type(value) in {int, float} for value in column["categories"]))
        require(numeric and column["role"] == "generated", "Alias requires an original numeric generated column")
        _assumptions(alias["assumption_ids"], known, "column alias measurement assumptions")
        mapped[source] = {**copy.deepcopy(column), "name": source}
        origins[source] = generated
    return mapped, origins


def _binary_column(column):
    if column["kind"] == "category":
        return all(type(value) in {int, float} for value in column["categories"]) and set(column["categories"]) == {0, 1}
    return column["kind"] == "integer" and column.get("minimum") == 0 and column.get("maximum") == 1


def _mapping_contract(mapping, operator, columns, items, known):
    """Only an identity view or the declared HbA1c NGSP-to-IFCC equation."""
    require(isinstance(mapping, dict), "Measurement mapping must be explicit")
    if mapping.get("kind") == "identity":
        _exact(mapping, "kind", "identity mapping")
        return dict(columns)
    _exact(mapping, "kind input_column output_column ngsp_percent_per_ifcc ngsp_percent_intercept unit_evidence_id assumption_ids", "HbA1c mapping")
    require(mapping["kind"] == "hba1c_ngsp_to_ifcc", "Unsupported measurement mapping")
    require(operator["kind"] == "ols_coefficient", "HbA1c mapping is limited to an OLS response")
    incoming, outgoing = mapping["input_column"], mapping["output_column"]
    require(incoming in columns and outgoing not in columns and incoming != outgoing, "Mapping must add one new response from an existing column")
    require(operator["outcome"] == outgoing and incoming not in operator["predictors"], "Mapping cannot alter a predictor")
    require(columns[incoming]["kind"] == "number" and columns[incoming]["unit"] == "%", "NGSP input must be a numeric percent column")
    unit_id = mapping["unit_evidence_id"]
    require(unit_id in items, "Unknown unit evidence")
    unit_item = items[unit_id]
    require(unit_item["kind"] == "contextual" and set(unit_item["variables"]) == {incoming, outgoing}, "Unit evidence must identify the two HbA1c representations")
    # The independently reviewed equation, not fitted values, supplies constants.
    for key in ("ngsp_percent_per_ifcc", "ngsp_percent_intercept"):
        contracts.number(mapping[key], key)
    require(mapping["ngsp_percent_per_ifcc"] > 0, "Positive HbA1c scale factor required")
    _assumptions(mapping["assumption_ids"], known, "measurement assumptions")
    mapped = dict(columns)
    mapped[outgoing] = {"name": outgoing, "kind": "number", "unit": "mmol/mol"}
    return mapped


def _operator_contract(operator, item, columns):
    require(operator.get("kind") in KINDS, "Only OLS, Pearson and Spearman are supported")
    semantic._signature(operator)
    semantic._task_operator(operator, columns)
    semantic._bind_evidence(item, operator)
    require(operator["selection"] == [] and operator["missing_policy"] == "error", "Use the entire predeclared source analysis table with no deletion")
    if operator["kind"] == "ols_coefficient":
        require(operator["include_intercept"] is True, "Qualified OLS requires an intercept")
        nuisance = set(operator["predictors"]) - {operator["term"]}
        binary = [name for name in nuisance if _binary_column(columns[name])]
        require(len(nuisance) == 2 and len(binary) == 1,
                "This narrow OLS adapter requires one explicit binary nuisance and one numeric nuisance")
        require(all(columns[name]["kind"] in {"number", "integer"} for name in nuisance - set(binary)),
                "The remaining OLS nuisance must be numeric")
        numerator = columns[operator["outcome"]]["unit"]
        denominator = columns[operator["term"]]["unit"]
        # Accept the retained evidence's parenthesized per-unit notation.
        allowed = {numerator + "/" + denominator, numerator + "/(" + denominator + ")"}
        if denominator == "1":
            allowed.add(numerator)
        require(operator["unit"] in allowed, "OLS units do not match response and focal predictor")
    else:
        require(operator["unit"] == "1", "Correlation must be dimensionless")


def _prepare(child_bundle, child_candidate, declaration, review):
    root = _bundle(child_bundle)
    candidate = str(child_candidate)
    if "/" not in candidate and "\\" not in candidate:
        candidate = "candidates/" + execution._name(candidate)
    directory, relative = _candidate(root, candidate)
    frozen = verify_candidate(root, directory)
    require(frozen["route"] == "generator.py", "Verified generator route required")
    task = read_json(root / "task.json")
    require(task["mode"] == "whole_cohort" and not (root / "observed.csv").exists(), "Whole-cohort source context only")
    _exact(declaration, "schema_version bindings context_role context_id population measurement source_ids assumption_ids column_aliases checks", "qualified declaration")
    require(type(declaration["schema_version"]) is int and declaration["schema_version"] == 1, "Invalid qualified schema")
    _review(declaration, review)
    files = {"task_sha256": root / "task.json", "candidate_freeze_sha256": directory / "freeze.json",
             "evidence_sha256": directory / "evidence.json", "model_spec_sha256": directory / "model_spec.json",
             "semantics_sha256": directory / semantic.FILE, "bridge_plan_sha256": directory / BRIDGE_PLAN}
    _same(declaration["bindings"], {key: sha256(path) for key, path in files.items()}, "Qualified input binding mismatch")
    for name in ("evidence.json", "model_spec.json", semantic.FILE, BRIDGE_PLAN, semantic.legacy.PLAN):
        require(relative + "/" + name in frozen["candidate_files"], "Required qualified artifact is not frozen: " + name)
    spec, evidence, plan = (read_json(directory / name) for name in ("model_spec.json", "evidence.json", BRIDGE_PLAN))
    known = {assumption["id"] for assumption in spec["assumptions"]}
    _assumptions(declaration["assumption_ids"], known, "context assumptions")
    active = spec["parameters"]["active_context"]
    require(active == declaration["context_id"], "Qualified context is not the executed active context")
    contexts = [context for context in plan["contexts"] if context["id"] == active]
    require(len(contexts) == 1, "Missing or ambiguous bridge context")
    context = contexts[0]
    require(context["role"] == declaration["context_role"] == "source", "Target context cannot produce source-qualified feedback")
    contracts.string_list(declaration["source_ids"], "qualified sources", nonempty=True)
    require(set(declaration["source_ids"]) == set(context["source_ids"]), "Source scope differs from frozen bridge context")
    descriptor = spec["parameters"]["contexts"][active]
    recipe = read_json(directory / semantic.legacy.PLAN)
    require(declaration["population"] == task["population"] == descriptor["population"] == recipe["population"], "Source population binding mismatch")
    require(declaration["measurement"] == descriptor["measurement"] == recipe["measurement"]["description"], "Source measurement binding mismatch")
    require(task["n_rows"] == descriptor["n_rows"], "Source row-count binding mismatch")
    gates = {gate["id"]: gate for gate in semantic.preflight(root, relative)["checks"]}
    items = {item["id"]: item for item in evidence["items"]}
    columns, origins = _alias_contract(declaration["column_aliases"], {column["name"]: column for column in task["columns"]}, known)
    checks = declaration["checks"]
    require(isinstance(checks, list) and 1 <= len(checks) <= 16, "Declare one to sixteen qualified checks")
    seen, strict_ids, evidence_ids, used_sources = set(), set(), set(), set()
    for check in checks:
        _exact(check, "id evidence_id semantic_check_id operator source_relation measurement_mapping", "qualified check")
        name = execution._name(check["id"]).casefold()
        require(name not in seen, "Duplicate qualified check ID")
        seen.add(name)
        item_id, strict_id = check["evidence_id"], check["semantic_check_id"]
        require(item_id in items and item_id not in evidence_ids and strict_id in gates and strict_id not in strict_ids, "Unknown or reused evidence/semantic check")
        evidence_ids.add(item_id)
        strict_ids.add(strict_id)
        item, gate = items[item_id], gates[strict_id]
        require(gate["evidence_id"] == item_id, "Strict check references different evidence")
        require(item["source_id"] in declaration["source_ids"], "Evidence outside actual source context")
        used_sources.add(item["source_id"])
        require(item["kind"] in KINDS and gate["semantics"]["weights"] == "not_reported", "Only declared relationships with unknown original weights are qualified")
        require(gate["semantic_status"] == "unavailable", "Original strict check must remain unavailable")
        operator, relation = check["operator"], check["source_relation"]
        if operator is None:
            require(check["measurement_mapping"] == {"kind": "identity"}, "Unavailable operator cannot apply a mapping")
        else:
            require(isinstance(operator, dict), "Operator must be an object or null")
            mapped_columns = _mapping_contract(check["measurement_mapping"], operator, columns, items, known)
            _operator_contract(operator, item, mapped_columns)
            check_origins = dict(origins)
            mapping = check["measurement_mapping"]
            if mapping["kind"] != "identity":
                check_origins[mapping["output_column"]] = origins[mapping["input_column"]]
            operands = semantic._variables(operator)
            require(len({check_origins[name] for name in operands}) == len(operands),
                    "Distinct operator operands cannot alias the same generated column")
            original_operator = gate["semantics"]["source_operator"]
            if original_operator is not None:
                _same(semantic._signature(operator), semantic._signature(original_operator), "Qualified operator changes a known original functional")
        if relation is not None:
            _exact(relation, "kind assumed_weights assumption_ids unresolved_original_details reason", "source relation")
            require(relation["kind"] == "same_reported_functional_under_declared_assumptions" and relation["assumed_weights"] == "equal", "Unsupported source interpretation")
            _assumptions(relation["assumption_ids"], known, "qualified relationship assumptions")
            contracts.string_list(relation["unresolved_original_details"], "unresolved original details", nonempty=True)
            contracts.text(relation["reason"], "qualification reason")
    require(used_sources == set(declaration["source_ids"]), "Qualified checks do not cover declared source scope")
    return root, directory, relative, task, frozen, items, gates, columns


def _calculate(frame, check, columns):
    operator = check["operator"]
    mapped = frame
    mapping = check["measurement_mapping"]
    if mapping["kind"] != "identity":
        values = frame[mapping["input_column"]]
        require(np.isfinite(values.to_numpy(dtype=float)).all(), "Nonfinite NGSP input")
        mapped = frame.copy(deep=False).assign(**{
            mapping["output_column"]: (values - mapping["ngsp_percent_intercept"]) / mapping["ngsp_percent_per_ifcc"]})
        require(np.isfinite(mapped[mapping["output_column"]].to_numpy(dtype=float)).all(), "Nonfinite mapped IFCC response")
    if operator["kind"] in {"correlation", "spearman_correlation"}:
        require(len(mapped) >= 3, "Qualified correlation requires at least three pairs")
    else:
        # Explicit categories or integer bounds establish binary coding. Other
        # integers are not guessed to mean binary source membership.
        for predictor in set(operator["predictors"]) - {operator["term"]}:
            column = columns[predictor]
            if _binary_column(column):
                require(set(mapped[predictor]) == {0, 1}, "OLS binary nuisance requires both declared 0/1 categories")
    return source_checks.apply_operator(mapped, operator)


def compute_qualified_feedback(child_bundle, child_candidate, run_id, semantic_feedback_id, declaration, review):
    """Verify retained receipts and return qualified comparisons without writes.

    All declaration/independent-review gates precede table arithmetic. A caller
    must retain this report outside the historical bridge inventory and bind it
    in its own immutable phase receipt; this API does not launch an execution.
    """
    root, directory, relative, task, frozen, items, gates, columns = _prepare(child_bundle, child_candidate, declaration, review)
    run_id, semantic_feedback_id = execution._name(run_id), execution._name(semantic_feedback_id)
    receipt = execution.verify_execution(root, run_id)
    require(receipt["candidate"] == relative and receipt["route"] == "generator.py" and receipt["status"] == "success" and receipt["generator_executed"] is True, "Successful matching generator execution required")
    require(receipt["candidate_freeze_sha256"] == sha256(directory / "freeze.json"), "Execution freeze mismatch")
    strict = semantic.verify_feedback(root, semantic_feedback_id, candidate=relative, run_id=run_id)
    expected = semantic._compute(root, directory, relative, run_id, semantic_feedback_id)
    expected["created_utc"] = strict["created_utc"]
    _same(strict, expected, "Strict feedback has typed changes or differs from recomputation")
    require(strict["output_link_verified"] is True and strict["generator_execution_recorded"] is True, "Strict feedback lacks generator linkage")
    output = _path(root, f"executions/{run_id}/output/generated.csv")
    bindings = {**declaration["bindings"], "recipe_sha256": sha256(directory / semantic.legacy.PLAN),
                "execution_receipt_sha256": sha256(root / f"executions/{run_id}/execution.json"),
                "generated_table_sha256": sha256(output),
                "semantic_feedback_sha256": sha256(_path(root, f"{semantic.FOLDER}/{semantic_feedback_id}/feedback.json")),
                "declaration_sha256": declaration_digest(declaration), "review_sha256": declaration_digest(review)}
    for key, value in strict["bindings"].items():
        require(bindings.get(key) == value, "Strict/current artifact linkage mismatch: " + key)
    strict_rows = {row["id"]: row for row in strict["checks"]}
    for check in declaration["checks"]:
        row = strict_rows[check["semantic_check_id"]]
        require(row["status"] == "not_computable" and row["calculation"] is None and row["difference"] is None, "Original strict result was promoted to numerical feedback")
    frame = read_table(output, task, output=True)
    contracts.validate_output(None, frame, task)
    # assign creates an analysis view; neither CSV bytes nor original columns
    # are changed. Alias definitions may reference only the original frame.
    analysis_frame = frame.assign(**{alias["source_name"]: frame[alias["generated_name"]]
                                    for alias in declaration["column_aliases"]})
    records = []
    for check in declaration["checks"]:
        item, relation = items[check["evidence_id"]], check["source_relation"]
        unavailable = None
        calculation, difference = None, None
        if check["operator"] is None:
            unavailable = "Qualified operator details remain unavailable"
        elif relation is None:
            unavailable = "No independently reviewed explicit relation to the reported source functional"
        else:
            try:
                calculation = _calculate(analysis_frame, check, columns)
                difference = calculation["value"] - item["estimate"]
                contracts.number(difference, "qualified raw difference")
            except (ValueError, np.linalg.LinAlgError, FloatingPointError) as error:
                calculation, difference = None, None
                unavailable = str(error)
        records.append({"id": check["id"], "evidence_id": item["id"], "source_id": item["source_id"],
                        "semantic_check_id": check["semantic_check_id"], "kind": "qualified_assumption_comparison",
                        "status": "available" if calculation is not None else "unavailable", "unavailable_reason": unavailable,
                        "reported_evidence": copy.deepcopy(item), "original_source_weights": "not_reported",
                        "assumed_weights": "equal", "strict_result": copy.deepcopy(strict_rows[check["semantic_check_id"]]),
                        "calculation": calculation, "raw_difference": difference, "unit": item["unit"],
                        "operator": copy.deepcopy(check["operator"]), "source_relation": copy.deepcopy(relation),
                        "measurement_mapping": copy.deepcopy(check["measurement_mapping"]),
                        "exact_source_check_allowed": False, "strict_source_difference": None})
    require(sha256(output) == bindings["generated_table_sha256"], "Execution output changed during qualified collection")
    # Recheck every retained binding after calculation, including the parent law.
    verify_candidate(root, directory)
    for key, path in {"execution_receipt_sha256": root / f"executions/{run_id}/execution.json",
                      "semantic_feedback_sha256": root / f"{semantic.FOLDER}/{semantic_feedback_id}/feedback.json"}.items():
        require(sha256(path) == bindings[key], "Receipt changed during qualified collection")
    return {"schema_version": 1, "kind": "qualified_source_relationship_feedback_v1", "status": "complete",
            "candidate": relative, "run_id": run_id, "semantic_feedback_id": semantic_feedback_id,
            "context_role": "source", "context_id": declaration["context_id"], "population": task["population"],
            "measurement": declaration["measurement"], "source_ids": list(declaration["source_ids"]),
            "bindings": bindings, "declaration": copy.deepcopy(declaration), "review": copy.deepcopy(review),
            "output_link_verified": True, "checks": records,
            "n_available": sum(row["status"] == "available" for row in records),
            "n_unavailable": sum(row["status"] == "unavailable" for row in records),
            "source_reconstruction": "assumption_defined_not_certified", "scientific_validity": "not_assessed",
            "transport_validity": "not_assessed", "exact_source_check_allowed": False,
            "uncertainty_conversion": "none", "pooled_loss": None,
            "engine_sha256": {Path(__file__).name: sha256(__file__), "source_checks.py": sha256(source_checks.__file__)},
            "limitations": ["Original unknown weights and strict unavailability are preserved.",
                            "Generated rows do not identify the original joint population or estimator preprocessing.",
                            "Point differences have no precision weights, CI pass rule, or transport interpretation.",
                            "HbA1c scale conversion does not establish assay or specimen equivalence.",
                            "Review hashes are procedural commitments, not verified identities or signatures."]}
