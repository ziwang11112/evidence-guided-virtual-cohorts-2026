"""Four-cell reference constructor, callable only after external release.

Inputs are the exact approved external evidence/task bytes. No reference table,
target moments, filepath discovery, random sampling or network access occurs.
This file intentionally has no CLI that silently starts a clinical fit.
"""
from __future__ import annotations

import hashlib
import json
import copy

from moment_reference import VERSION, fit_context
from source_binding import prepare_contexts


def _decode(value):
    raw = value.encode("utf-8") if isinstance(value, str) else value
    if not isinstance(raw, bytes):
        raise TypeError("Exact UTF-8 file bytes or text required")
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def build_spec(case_id, arm, packet_bytes, task_bytes):
    """Return a construction recipe/trace, not the final harness model_spec.

    Clinical calls are construction work and must wait for the campaign release.
    No retry/fallback family or best-start selection is implemented. A failed
    source fit fails this construction and leaves its returned evidence in the
    caller's failure record; no target-directed repair is permitted.
    """
    packet, packet_hash = _decode(packet_bytes)
    task, task_hash = _decode(task_bytes)
    if task.get("mode") != "whole_cohort" or task.get("n_rows") != 3000:
        raise ValueError("Reference requires the admitted 3,000-row whole-cohort task")
    expected_glucose = "mmol/L" if case_id == "CHNS2009" else "mg/dL"
    columns = {x["name"]: x for x in task["columns"]}
    expected_units = {"row_id": "identifier", "age": "year", "female": "1",
                      "bmi": "kg/m^2", "glucose": expected_glucose, "hba1c": "%"}
    if set(columns) != set(expected_units) or any(columns[k]["unit"] != v for k, v in expected_units.items()):
        raise ValueError("Case measurement units/columns differ from this fixed recipe")
    bounds = (35, 74) if case_id == "CHNS2009" else (25, 79)
    if (columns["age"].get("minimum"), columns["age"].get("maximum")) != bounds:
        raise ValueError("Age support differs from the fixed case contract")
    prepared = prepare_contexts(case_id, arm, packet)
    fits = [fit_context(c, order=64, max_iterations=300) for c in prepared["contexts"]]
    if not all(f["success"] for f in fits):
        error = ValueError("Fixed source fitting failed; no fallback or clinical sampling permitted")
        error.source_fit_reports = fits
        raise error
    components = [{"source_context_id": c["source_context_id"],
                   "marginals": c["marginals"], "variable_order": f["variable_order"],
                   "latent_correlation": f["latent_correlation"]}
                  for c, f in zip(prepared["contexts"], fits)]
    assumptions = [
        {"id": "A_family", "description": "Fixed positive Gaussian-copula reference. Source moment constraints are fitted separately in their declared source contexts; no cross-source loss or target fitting."},
        {"id": "A_missing_dependence", "description": "Unspecified continuous dependence is completed by a latent-Gaussian entropy objective. Independent binary sex is a declared simplification. Local constrained optimization does not certify a global entropy optimum."},
        {"id": "A_source_semantics", "description": "Source moments describe a qualified equal-weight analysis-population scenario. Known glucose/age support is represented in the declared margins; unavailable selection variables, assay differences and survey weights remain limitations."},
        {"id": "A_transport", "description": "Target biomarkers inherit the source-context marginal/copula laws through a prespecified donor rule. This is an unverified transport assumption, not target population estimation."},
        {"id": "A_uncertainty", "description": "Published point summaries are fixed inputs. No source-estimate, structural or transport uncertainty is calibrated. SDs remain individual variability; SEs are not converted to SDs."},
        {"id": "A_sampling", "description": "One random draw under each scheduled seed, without moment forcing, clipping, seed selection, rejection redraws or calibration inside the generator. Invalid floating-point output fails the attempt."},
    ]
    if case_id == "CHNS2009":
        transport = {"kind": "equal_source_mixture", "component_probabilities": [1 / 3] * 3,
                     "age": {"kind": "discrete_uniform", "minimum": 35, "maximum": 74},
                     "sex": "component_source_Bernoulli_fraction"}
        assumptions.append({"id": "A_chns_composition", "description": "Equal donor probabilities are not empirical target mixture weights. Target age is discrete uniform on the requested support; source sex fractions are retained by donor. No CHNS target demographic moments are used."})
    else:
        transport = {"kind": "one_source_with_exact_target_design", "component_probabilities": [1.0],
                     "age_bands": [[25, 40], [40, 55], [55, 70], [70, 80]],
                     "rows_per_age_sex_cell": 375, "sex_categories": [0, 1]}
        assumptions.append({"id": "A_ensanut_composition", "description": "The exact eight age/sex quotas are the supplied analytical design. Age is uniform over integers within each band. Those target quotas are not substituted into the Lifelines source operator."})
        assumptions.append({"id": "A_pani_unhandled", "description": "Pani age coefficient and age-band means remain contextual/unfitted because source individual dispersion, age law and survey weighting are not bound. No full Pani uptake or numerical source-fit claim is made."})
    return {
        "parameters": {"family": "sourcewise_positive_gaussian_copula_v1", "case_id": case_id,
                       "arm": arm, "n_rows": 3000, "units": expected_units,
                       "components": components, "transport": transport},
        "assumptions": assumptions,
        "parameter_provenance": {
            "input_packet_sha256": packet_hash, "input_task_sha256": task_hash,
            "fitting_version": VERSION,
            "source_context_inputs": prepared["contexts"],
            "source_fit_reports": fits,
            "normalization_records": prepared["normalization_records"],
            "unhandled_relational_items": prepared["unhandled_relational_items"],
            "marginal_rule": "source_binding.py: individual mean/SD positive lognormal; native IFCC shifted-affine lognormal; glucose upper-truncated law; Bao log-quantile least squares; bounded uniform source age; explicit source sex fraction",
            "dependence_rule": "moment_reference.py: separately named population projections/correlations; entropy completion under the source moments",
            "transport_rule": "fixed case request/support and the declared donor rule; no target effect or demographic fit",
            "sampled_rows": 0, "execution_authorized": False,
        },
    }


def _used_evidence_ids(case_id, arm, packet):
    if case_id == "CHNS2009":
        ids = []
        for item in packet["shared_base"]["grouped_marginal_records"]:
            if item["kind"] == "reported_mean_and_individual_sd":
                ids += [item["id"] + "_MEAN", item["id"] + "_SD"]
            elif item["kind"] == "reported_median_and_quartile_endpoints":
                ids += [item["id"] + suffix for suffix in ("_MEDIAN", "_Q1", "_Q3")]
            elif item["kind"] == "reported_count_with_derived_fraction":
                ids += [item["id"] + "_FRACTION"]
            else:
                raise ValueError("Unmapped raw marginal record")
        ids += [x["id"] for x in packet["relationship_records"]]
        return [*ids, "U_NGSP_SCALE"]
    ids = ["J_T1_age_mean_task", "J_T1_age_sd_task", "J_T1_bmi_mean_task", "J_T1_bmi_sd_task",
           "J_T1_glucose_mean_mg_dL_derived", "J_T1_glucose_sd_mg_dL_derived",
           "J_T1_hba1c_mean_ifcc", "J_T1_hba1c_sd_ifcc", "J_T1_female_proportion_derived", "NGSP_UNIT_GUIDANCE"]
    if arm == "E1":
        ids += ["J_T2_bmi_slope_task_derived", "J_T2_glucose_slope_task_derived"]
    return ids


def build_harness_spec(case_id, arm, packet_bytes, task_bytes, compiled_evidence_bytes):
    """Construct and return {model_spec, construction_trace, trace_sha256}.

    Both returned artifacts must be persisted and hash-bound by the controller.
    Only model_spec is passed to the existing harness. The compiled evidence is
    separately validated/admitted by the controller; this wrapper checks exact
    item membership and the actual existing validate_spec ABI.
    """
    from cohort_harness.contracts import validate_spec

    packet, _ = _decode(packet_bytes)
    compiled, compiled_hash = _decode(compiled_evidence_bytes)
    declared_ids = [x["id"] for x in compiled["items"]]
    if len(declared_ids) != len(set(declared_ids)):
        raise ValueError("Duplicate compiled evidence IDs")
    used_ids = _used_evidence_ids(case_id, arm, packet)
    if not set(used_ids) <= set(declared_ids):
        raise ValueError("Compiled evidence is missing fixed normalization IDs: " + str(sorted(set(used_ids) - set(declared_ids))))
    recipe = build_spec(case_id, arm, packet_bytes, task_bytes)
    trace = copy.deepcopy(recipe["parameter_provenance"])
    trace["compiled_evidence_sha256"] = compiled_hash
    trace["used_compiled_evidence_ids"] = used_ids
    trace["raw_to_compiled_rule"] = "CHNS grouped mean/SD, quantile and fraction suffix mapping; relationship IDs unchanged; ENSANUT native admitted item IDs unchanged"
    trace_hash = hashlib.sha256(json.dumps(trace, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    assumptions = copy.deepcopy(recipe["assumptions"])
    assumptions += [
        {"id": "A_task", "description": "The bound research task determines case, row count, variables, units and explicit support/design; no reference outcome supplies these values."},
        {"id": "A_information", "description": "The bound E0/E1 packet determines the allowed source information. The reference's actual numerical uptake and declined records are retained in the separate construction trace."},
    ]
    scale_id = "U_NGSP_SCALE" if case_id == "CHNS2009" else "NGSP_UNIT_GUIDANCE"
    provenance = {
        "family": {"evidence_ids": [], "assumption_ids": ["A_family", "A_missing_dependence"], "derivation": "Prespecified positive Gaussian-copula family; no family search."},
        "case_id": {"evidence_ids": [], "assumption_ids": ["A_task"], "derivation": "Exact admitted task identity."},
        "arm": {"evidence_ids": [], "assumption_ids": ["A_information"], "derivation": "Exact admitted packet condition."},
        "n_rows": {"evidence_ids": [], "assumption_ids": ["A_task"], "derivation": "The request fixes 3,000 virtual rows, not source or target participant count."},
        "units": {"evidence_ids": [scale_id], "assumption_ids": ["A_task", "A_source_semantics"], "derivation": "Task measurement scales; explicit NGSP/IFCC and glucose unit mapping without assay-equivalence inference."},
        "components": {"evidence_ids": used_ids, "assumption_ids": ["A_family", "A_missing_dependence", "A_source_semantics", "A_uncertainty", "A_information"],
                       "derivation": "Deterministic source_binding and moment_reference calculations. Complete source moments, separate operators, residuals, unhandled evidence and input hashes are in construction_trace with canonical SHA-256 " + trace_hash},
        "transport": {"evidence_ids": [], "assumption_ids": ["A_task", "A_transport", "A_chns_composition" if case_id == "CHNS2009" else "A_ensanut_composition"],
                      "derivation": "Prespecified donor/marginal mapping and request support; no target moment or effect fitting."},
    }
    spec = {"parameters": recipe["parameters"], "assumptions": assumptions, "parameter_provenance": provenance}
    validate_spec(spec, set(declared_ids))
    return {"model_spec": spec, "construction_trace": trace, "trace_sha256": trace_hash}
