"""Metadata-only Greiner-to-harness compiler; no fitting, sampling or checks.

Source percentages stay percentages in evidence/feedback. Only the separate
S01 input view divides them by 100, with a retained original and derivation.
"""
from __future__ import annotations

import copy
import hashlib
import json

from cohort_harness import contracts, execution

CONTEXTS = ("malawi_rural_men", "malawi_urban_men", "uganda_men", "malawi_rural_women", "malawi_urban_women", "uganda_women")
ARTIFACT = "sources/greiner_source_packet.json"
UNITS = {"age": "year", "sex": "1", "bmi": "kg/m^2", "total_cholesterol": "mmol/L", "hdl_cholesterol": "mmol/L", "non_hdl_cholesterol": "mmol/L"}
require = contracts.require


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def _unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def _finite(value):
    contracts.number(value, "source value")
    return value


def _uncertainty(record):
    original = record["uncertainty"]
    if original["kind"] == "not_reported":
        require(original["role"] == "not_reported", "Unknown uncertainty role")
        return {"kind": "not_reported"}
    require(original["kind"] == "confidence_interval" and original["role"] == "estimation_uncertainty"
            and original["is_individual_dispersion"] is False and original["use_for_precision_weighting"] is False,
            "Confidence interval cannot become individual dispersion or a fit weight")
    require(original["unit"] == record["unit"], "Source CI unit mismatch")
    value = {"kind": "ci", "low": original["lower"], "high": original["upper"], "level": original["level"]}
    contracts._uncertainty(value)
    return value


def _validate_packet(packet, task):
    contracts.validate_task(task)
    require(task["mode"] == "whole_cohort" and task["row_id"] == "id", "Whole-cohort canonical task required")
    require([c["name"] for c in task["columns"]] == ["id", "age", "sex", "bmi", "total_cholesterol", "hdl_cholesterol"], "Canonical ordered columns required")
    for column in task["columns"][1:]:
        require(column["unit"] == UNITS[column["name"]], "Canonical units changed")
    require(packet["schema_version"] == "source_candidate_greiner.v1", "Unsupported source packet")
    contexts = packet["contexts"]
    require(len(contexts) == 6 and {c["id"] for c in contexts} == set(CONTEXTS), "Six distinct source contexts required")
    definitions = packet["operator_definitions"]
    for key in ("geometric_mean_positive", "threshold_percentage"):
        definition = definitions[key]
        require(definition["source_weighting"] == "not_reported" and definition["weighting_assumption_required"] is True,
                "Unknown source weighting must remain unknown")
        require(definition["formula_weighting"] == "equal_weight_operational_definition" and definition["adjustment_set"] == [], "Operator weighting/adjustment changed")
    require(definitions["geometric_mean_positive"]["statistic"] == "geometric_mean" and definitions["geometric_mean_positive"]["input_domain"] == "finite x > 0", "Geometric-mean meaning changed")
    require(definitions["threshold_percentage"]["comparison"] == "strict_lt", "Threshold boundary changed")
    require(definitions["reported_age_quantile"]["interpolation"] == "not_reported" and definitions["reported_age_quantile"]["executable_recipe"] is None,
            "Unresolved quantile convention must remain unavailable")
    groups = {c["id"]: c for c in contexts}
    for identifier, group in groups.items():
        require(group["sex"] == ("male" if identifier.endswith("_men") else "female"), "Source sex/context mismatch")
        require(group["selection_rules_ref"] == packet["selection_rules"]["id"], "Source selection binding mismatch")
        require(packet["measurements"][group["measurement_ref"]]["source_unit"] == "mmol/L", "Source measurement units changed")
    records = packet["constraint_candidates"]
    expected = {f"{context}__{variable}__geometric_mean" for context in CONTEXTS for variable in ("bmi", "total_cholesterol", "hdl_cholesterol", "non_hdl_cholesterol")}
    expected |= {f"{context}__age__{q}" for context in CONTEXTS for q in ("q1", "median", "q3")}
    expected |= {f"{context}__hdl_cholesterol__low_prevalence" for context in CONTEXTS}
    require(len(records) == 48 and {r["id"] for r in records} == expected, "Original record coverage or IDs changed")
    for record in records:
        context = record["population_ref"]
        require(context in groups and record["id"].startswith(context + "__"), "Record/context binding mismatch")
        variable, statistic = record["variable"], record["reported_statistic"]
        if statistic == "geometric_mean":
            require(record["id"] == f"{context}__{variable}__geometric_mean", "Evidence ID/analyte/statistic mismatch")
        elif statistic == "proportion":
            require(record["id"] == f"{context}__{variable}__low_prevalence", "Evidence ID/analyte/statistic mismatch")
        denominator = record["denominator"]
        table = 1 if variable in {"age", "bmi"} else 2
        require(denominator["population_ref"] == context and denominator["selection_rules_ref"] == packet["selection_rules"]["id"] and denominator["source_table"] == table,
                "Source denominator identity changed")
        require(denominator["reported_group_n"] == groups[context][f"reported_table_{table}_group_n"], "Table-specific denominator changed")
        require(denominator["row_specific_n"] is None and denominator["row_specific_n_status"] == "not_separately_reported"
                and denominator["uncertainty_weighting_allowed"] is False and denominator["event_conditioned"] is False,
                "Do not invent row N, event-conditioned denominator or uncertainty weights")
        require(record["provenance"]["source_doi"] == packet["provenance"]["source_doi"], "Source DOI linkage mismatch")
        contracts.text(record["provenance"]["locator"], "source locator")
        _finite(record["value"])
        _uncertainty(record)
        if statistic == "geometric_mean":
            require(record["record_class"] == "numerical_candidate" and record["value"] > 0 and record["unit"] == UNITS[variable], "Invalid geometric-mean record")
            require(record["operator"] == {"definition_ref": "geometric_mean_positive", "column": variable}, "Geometric operator changed")
        elif statistic == "proportion":
            operator = record["operator"]
            require(record["record_class"] == "numerical_candidate" and variable == "hdl_cholesterol" and record["unit"] == "%" and 0 <= record["value"] <= 100,
                    "Original prevalence must be a printed percentage, never an already-normalized fraction")
            require(operator["definition_ref"] == "threshold_percentage" and operator["column"] == variable and operator["comparison"] == "lt"
                    and operator["threshold_unit"] == "mmol/L" and type(operator["output_multiplier"]) is int and operator["output_multiplier"] == 100,
                    "Prevalence unit, multiplier or threshold operator changed")
            require(_finite(operator["threshold"]) > 0, "Positive original threshold required")
        else:
            q = {"q1": 0.25, "median": 0.5, "q3": 0.75}[record["id"].split("__")[-1]]
            require(record["record_class"] == "context_only_quantile" and variable == "age" and record["unit"] == "year"
                    and statistic == ("median" if q == 0.5 else "quantile"), "Context-only age meaning changed")
            require(record["operator"] == {"definition_ref": "reported_age_quantile", "column": "age", "q": q, "interpolation": "not_reported"}
                    and record["admission"]["numerical_calibration_allowed"] is False, "Age quantile cannot be activated")
        if statistic in {"geometric_mean", "proportion"}:
            require(record["admission"]["source_weighting"] == "not_reported", "Per-record source weights changed")
    regressions = packet["contextual_regressions"]
    require(len(regressions) == 12 and len({r["id"] for r in regressions}) == 12, "Contextual regression coverage changed")
    for row in regressions:
        require(row["provenance"]["source_doi"] == packet["provenance"]["source_doi"], "Contextual regression DOI linkage mismatch")
        require(row["record_class"] == "context_only_regression" and row["response_label"] == "HDL"
                and row["predictor_label"] in {"bmi", "non_hdl_cholesterol"}, "Unrecognized contextual regression")
        require(row["numerical_calibration_allowed"] is False and row["executable_operator"] is None
                and row["unit"] == "unresolved_regression_scale" and row["weighting"] == "not_reported"
                and row["response_transform"] == row["predictor_transform"] == "not_unambiguously_reported"
                and row["uncertainty_role"] == "estimation_uncertainty", "Unresolved regression cannot become an executable slope")
        _finite(row["reported_estimate"])
    return groups


def compile_source_packet(packet_bytes: bytes, task: dict, *, expected_packet_sha256: str) -> dict:
    """Compile supplied fixed source bytes; never compute a statistic on rows."""
    require(type(packet_bytes) is bytes, "Original source bytes required")
    contracts._hash(expected_packet_sha256)
    require(hashlib.sha256(packet_bytes).hexdigest() == expected_packet_sha256, "Source byte commitment mismatch")
    packet = json.loads(packet_bytes.decode("utf-8-sig"), object_pairs_hook=_unique)
    groups = _validate_packet(packet, task)
    evidence = {"schema_version": 1, "sources": [], "items": []}
    sources = {}
    for identifier in CONTEXTS:
        group = groups[identifier]
        source = {"id": "greiner_" + identifier, "identifier": packet["provenance"]["source_doi"] + " / " + identifier,
                  "population": canonical({"context": group, "selection": packet["selection_rules"]}),
                  "measurement": canonical(packet["measurements"][group["measurement_ref"]]),
                  "cohort_ids": [group["cohort"] + "_" + group["country"]],
                  "artifacts": [{"path": ARTIFACT, "sha256": expected_packet_sha256}]}
        sources[identifier] = source
        evidence["sources"].append(source)
    evidence["sources"].append({"id": "greiner_pooled_african", "identifier": packet["provenance"]["source_doi"] + " / pooled Table 3",
        "population": "Pooled source African cohorts under " + canonical(packet["selection_rules"]),
        "measurement": canonical({key: packet["measurements"][key] for key in ("malawi_lipids", "uganda_lipids")}),
        "cohort_ids": sorted({c["cohort"] + "_" + c["country"] for c in groups.values()}),
        "artifacts": [{"path": ARTIFACT, "sha256": expected_packet_sha256}]})
    provenance, dispositions = {}, []
    for index, record in enumerate(packet["constraint_candidates"]):
        statistic, variable = record["reported_statistic"], record["variable"]
        disposition = "context_only_unresolved_quantile" if variable == "age" else (
            "unavailable_derived_non_hdl_not_task_column" if variable == "non_hdl_cholesterol" else "potential_direct_supplemental_descriptive_diagnostic")
        item = {"id": record["id"], "source_id": sources[record["population_ref"]]["id"], "locator": record["provenance"]["locator"],
                "variables": [variable], "kind": "reported_other" if statistic == "geometric_mean" else statistic,
                "estimate": record["value"], "unit": record["unit"], "uncertainty": _uncertainty(record), "adjustment": [],
                "selection": canonical({"source_context": record["population_ref"], "eligibility": packet["selection_rules"], "denominator": record["denominator"]}),
                "applicability": canonical({"disposition": disposition, "issues": record.get("issue_ids", []), "uncertainty_original": record["uncertainty"],
                    "original_record_sha256": digest(record), "source_weighting": "not_reported", "source_context_reconstructed": False})}
        if statistic == "geometric_mean": item["statistic_name"] = "geometric_mean"
        if statistic in {"median", "quantile"}: item["method"] = "not_reported"
        if statistic == "quantile": item["q"] = record["operator"]["q"]
        evidence["items"].append(item)
        provenance[item["id"]] = {"source_packet_sha256": expected_packet_sha256, "pointer": f"/constraint_candidates/{index}",
            "original_record": copy.deepcopy(record), "original_record_sha256": digest(record), "evidence_item_sha256": digest(item),
            "representation": "Original value/unit preserved; CI field names projected to lifecycle ci/low/high/level without uncertainty conversion"}
        dispositions.append({"evidence_id": item["id"], "disposition": disposition, "strict_source_check_available": False, "activated": False})
    for index, record in enumerate(packet["contextual_regressions"]):
        item = {"id": record["id"], "source_id": "greiner_pooled_african", "locator": record["provenance"]["locator"],
            "variables": ["hdl_cholesterol", record["predictor_label"]], "kind": "reported_other", "statistic_name": "regression_coefficient_unresolved_scale",
            "estimate": record["reported_estimate"], "unit": record["unit"],
            "uncertainty": {"kind": "ci", "low": record["reported_ci95"][0], "high": record["reported_ci95"][1], "level": 0.95},
            "adjustment": copy.deepcopy(record["adjustment_set"]), "selection": canonical({"population": record["population"], "sex": record["sex"], "eligibility": packet["selection_rules"]}),
            "applicability": canonical({"disposition": "context_only_unresolved_regression", "original_record_sha256": digest(record), "issues": record["issue_ids"],
                "response_transform": record["response_transform"], "predictor_transform": record["predictor_transform"], "numerical_calibration_allowed": False})}
        evidence["items"].append(item)
        provenance[item["id"]] = {"source_packet_sha256": expected_packet_sha256, "pointer": f"/contextual_regressions/{index}",
            "original_record": copy.deepcopy(record), "original_record_sha256": digest(record), "evidence_item_sha256": digest(item),
            "representation": "Reported coefficient retained as reported_other, never a verified raw/log OLS operator"}
        dispositions.append({"evidence_id": item["id"], "disposition": "context_only_unresolved_regression", "strict_source_check_available": False, "activated": False})
    contracts.validate_evidence(evidence, task)
    records = {r["id"]: r for r in packet["constraint_candidates"]}
    templates, normalized, normalization_records = [], [], []
    for identifier in CONTEXTS:
        source = sources[identifier]
        selection = [{"column": "age", "op": "ge", "value": 18}, {"column": "sex", "op": "eq", "value": "M" if groups[identifier]["sex"] == "male" else "F"}]
        recipe = {"schema_version": 1, "population": source["population"], "measurement": {"mode": "identity", "description": source["measurement"]}, "assumption_ids": [], "checks": []}
        semantics = {"schema_version": 1, "evidence_sha256": "", "recipe_sha256": "", "bindings": []}
        supplemental = {"schema_version": 1, "task_sha256": "", "evidence_sha256": "", "model_spec_sha256": "", "semantics_sha256": "",
            "table_context": {"kind": "source_context_simulation", "context_id": identifier, "population": source["population"], "measurement": source["measurement"],
                "variable_units": {key: UNITS[key] for key in ("age", "sex", "bmi", "total_cholesterol", "hdl_cholesterol")},
                "variable_scales": {key: "categorical" if key == "sex" else "original" for key in ("age", "sex", "bmi", "total_cholesterol", "hdl_cholesterol")}},
            "assumption_ids": [], "checks": [], "context_review": None}
        for ordinal, suffix in enumerate(("bmi__geometric_mean", "total_cholesterol__geometric_mean", "hdl_cholesterol__geometric_mean", "hdl_cholesterol__low_prevalence"), 1):
            record = records[identifier + "__" + suffix]
            key = f"check-{ordinal}"
            geometric = record["reported_statistic"] == "geometric_mean"
            operator = {"kind": "geometric_mean" if geometric else "proportion", "unit": record["unit"], "selection": copy.deepcopy(selection), "selection_missing_policy": "error", "missing_policy": "error"}
            if geometric: operator["column"] = record["variable"]
            else: operator["event"] = {"column": "hdl_cholesterol", "op": "lt", "value": record["operator"]["threshold"]}
            names = {"age", "sex", record["variable"]}
            variable_units = {name: UNITS[name] for name in sorted(names)}
            has_ci = record["uncertainty"]["kind"] == "confidence_interval"
            native = {k: copy.deepcopy(v) for k, v in operator.items() if k != "selection_missing_policy"}
            recipe["checks"].append({"id": key, "evidence_id": record["id"], "status": "not_computable", "operator": None, "assumption_ids": [],
                "reason": "Unknown source estimator weighting; " + ("geometric mean also unsupported in semantic v1." if geometric else "retain original strict threshold and percentage scale.")})
            semantics["bindings"].append({"check_id": key, "evidence_id": record["id"], "source_locator": record["provenance"]["locator"],
                "definition_status": "unsupported" if geometric else "specified", "source_operator": None if geometric else native,
                "weights": "not_reported", "transform": "identity", "source_variable_units": {} if geometric else variable_units,
                "source_n": {"status": "not_reported"}, "uncertainty_role": "estimate" if has_ci else "not_reported", "reason": "Reported CIs remain estimator uncertainty; unreported uncertainty remains unknown. Row-specific N and weights are not reported; full table-specific provenance is retained."})
            supplemental["checks"].append({"id": key, "evidence_id": record["id"], "semantic_check_id": key, "operator": operator,
                "source": {"source_id": source["id"], "context_id": identifier, "population": source["population"], "measurement": source["measurement"],
                    "locator": record["provenance"]["locator"], "operator": copy.deepcopy(operator), "weights": "not_reported", "definition_status": "specified",
                    "uncertainty_role": "estimator_confidence_interval" if has_ci else "not_reported", "variable_units": variable_units,
                    "variable_scales": {name: "categorical" if name == "sex" else "original" for name in sorted(names)}}, "proxy": None})
        templates.append({"id": identifier, "role": "source", "source_ids": [source["id"]], "assumption_ids": [], "feedback_policy": "semantic_v1_plus_supplement",
            "recipe": recipe, "semantics": semantics, "supplement": supplemental})
        row = {"context_id": identifier}
        for field, variable in (("bmi_geometric_mean", "bmi"), ("hdl_geometric_mean", "hdl_cholesterol"), ("non_hdl_geometric_mean", "non_hdl_cholesterol")):
            record = records[identifier + "__" + variable + "__geometric_mean"]
            row[field] = {"evidence_id": record["id"], "locator": record["provenance"]["locator"], "variable": variable, "statistic": "geometric_mean", "unit": record["unit"], "value": record["value"]}
        record = records[identifier + "__hdl_cholesterol__low_prevalence"]
        row["low_hdl_proportion"] = {"evidence_id": record["id"], "locator": record["provenance"]["locator"], "variable": "hdl_cholesterol", "statistic": "proportion", "unit": "1",
            "value": record["value"] / 100, "comparison": "lt", "threshold": record["operator"]["threshold"], "threshold_unit": "mmol/L"}
        normalized.append(row)
        normalization_records.append({"context_id": identifier, "source_packet_sha256": expected_packet_sha256,
            "original_record": copy.deepcopy(record), "original_record_sha256": digest(record), "normalized_record": copy.deepcopy(row["low_hdl_proportion"]),
            "normalized_record_sha256": digest(row["low_hdl_proportion"]), "derivation": {"operation": "divide", "numerator": record["value"], "denominator": 100,
                "input_unit": "%", "output_unit": "1", "times_applied": 1},
            "uncertainty": "Original percentage CI retained above; no CI or individual/residual SD passed to S01."})
    return {"schema_version": "k02_source_compilation.v1", "source_packet_sha256": expected_packet_sha256, "task_contract_sha256": digest(task),
        "evidence": evidence, "record_provenance": provenance, "source_context_templates": templates,
        "dispositions": dispositions, "source_issues": copy.deepcopy(packet["issues"]), "s01_normalized_constraints": normalized,
        "s01_normalization_records": normalization_records, "s01_normalized_constraints_sha256": digest(normalized),
        "registration_requirements": [{"source_id": s["id"], **s["artifacts"][0]} for s in evidence["sources"]],
        "counts": {"lifecycle_evidence_items": len(evidence["items"]), "source_contexts": len(templates),
                   "potential_direct_diagnostics": sum(d["disposition"] == "potential_direct_supplemental_descriptive_diagnostic" for d in dispositions),
                   "non_hdl_unavailable": sum(d["disposition"] == "unavailable_derived_non_hdl_not_task_column" for d in dispositions),
                   "age_context_only": sum(d["disposition"] == "context_only_unresolved_quantile" for d in dispositions),
                   "regression_context_only": sum(d["disposition"] == "context_only_unresolved_regression" for d in dispositions),
                   "activated_checks": sum(d["activated"] is True for d in dispositions), "computed_checks": 0, "fitted_models": 0, "sampled_rows": 0},
        "readiness": {"candidate_frozen": False, "assumptions_supplied": False, "independent_reviews_supplied": False,
            "registry_screening_approvals_supplied": False, "case_release_authorized": False,
            "limitations": ["Templates are not executable until the Agent supplies context assumptions, model/spec/row schedule and independent binding reviews.",
                "Source health eligibility is context metadata; unavailable flags are not reconstructed or silently applied to target rows.",
                "Source sex codes are an internal convention, not a verified biological target-code legend.",
                "All v1 gates remain unavailable; descriptive supplements have proxy=null. Raw discrepancies require separate reviewed equal-weight assumptions.",
                "Non-HDL is retained evidence/S01 input, not an executable derived diagnostic or added output column.",
                "No source authenticity, scientific model compliance or population/measurement transport is certified."]}}


def bind_context_assumptions(compiled: dict, assumption_ids_by_context: dict) -> list[dict]:
    """Copy templates with externally authored assumption IDs only; no approvals."""
    require(set(assumption_ids_by_context) == set(CONTEXTS), "Assumption IDs must cover exactly the six source contexts")
    templates = copy.deepcopy(compiled["source_context_templates"])
    for context in templates:
        ids = assumption_ids_by_context[context["id"]]
        contracts.string_list(ids, "Agent-authored context assumption IDs", nonempty=True)
        context["assumption_ids"] = list(ids)
        context["recipe"]["assumption_ids"] = list(ids)
        context["supplement"]["assumption_ids"] = list(ids)
    return templates
