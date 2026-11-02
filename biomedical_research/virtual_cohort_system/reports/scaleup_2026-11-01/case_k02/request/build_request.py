"""Build a draft metadata/evidence request, never a scientific model or dataset.

Only the named immutable Greiner source packet and admitted metadata documents
are inputs. No network, raw target, generator, result or execution is read/run.
Outputs are exclusive and confined to this request directory and build notes.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
SCALEUP = HERE.parent.parent
PROJECT = SCALEUP.parent.parent
SOURCE = SCALEUP / "evidence/SOURCE_CANDIDATE_GREINER.json"
sys.path.insert(0, str(PROJECT))
from cohort_harness import contracts


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write((json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8"))


def build():
    original_sha = sha(SOURCE)
    source = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    assert source["scope"]["subgroup_count"] == 6
    source_copy = HERE / "sources/greiner_source_packet.json"
    source_copy.parent.mkdir(exist_ok=True)
    with source_copy.open("xb") as stream:
        stream.write(SOURCE.read_bytes())

    task = {
        "schema_version": 1, "task_id": "K02-measured-lipids-canonical-request-v1", "mode": "whole_cohort",
        "population": "Adults aged at least 18 with recorded sex F or M in the selected Turkana 2018-2019 study-protocol target context; demographic and lifestyle mixture unspecified",
        "row_id": "id", "n_rows": 5000,
        "columns": [
            {"name": "id", "kind": "string", "unit": "1", "role": "identifier", "nullable": False},
            {"name": "age", "kind": "number", "unit": "year", "role": "generated", "nullable": False, "minimum": 18},
            {"name": "sex", "kind": "category", "unit": "1", "role": "generated", "nullable": False, "categories": ["F", "M"]},
            {"name": "bmi", "kind": "number", "unit": "kg/m^2", "role": "generated", "nullable": False},
            {"name": "total_cholesterol", "kind": "number", "unit": "mmol/L", "role": "generated", "nullable": False},
            {"name": "hdl_cholesterol", "kind": "number", "unit": "mmol/L", "role": "generated", "nullable": False}],
        "information_policy": {"mode": "published_evidence", "excluded_cohorts": ["Turkana target study", "Lea et al. 2020 Turkana", "10.1126/sciadv.abb1430", "10.5061/dryad.2z34tmpjk"], "allowed_tools": []},
        "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 1}}
    contracts.validate_task(task)
    write("task_template.json", task)

    target = {
        "schema_version": "k02_target_protocol_metadata.v1", "status": "sanitized_request_metadata_not_target_results",
        "context_id": "target_turkana_adults", "country": "Kenya", "named_context": "Turkana 2018-2019 study-protocol target",
        "population": task["population"],
        "geographic_metadata": "Reviewed study methods describe Turkana and Laikipia contexts; the pooled composition is not supplied.",
        "eligibility": {"minimum_age_inclusive": 18, "age_boundary_origin": "investigator-selected prospective use case",
            "age_maximum": None, "recognized_sex_categories": ["F", "M"],
            "common_finite_complete_variables": ["age", "sex", "bmi", "total_cholesterol", "hdl_cholesterol"],
            "strictly_positive": ["bmi", "total_cholesterol", "hdl_cholesterol"],
            "additional_exclusions": [], "no_inferred_exclusions": ["pregnancy", "HIV", "diabetes", "fasting", "lifestyle", "outliers", "TC>=HDL"]},
        "measurements": {
            "age": {"definition": "Self-reported interview age", "unit": "year", "locator": "Target supplement p.3 methods"},
            "sex": {"definition": "Recorded categorical interview field with recognized literal F/M values", "recognized_codes": ["F", "M"],
                "biological_label_legend": "not independently verified in admitted metadata", "distribution_supplied": False},
            "bmi": {"definition": "Body mass index derived from measured weight and height", "unit": "kg/m^2", "locator": "Target supplement p.5 anthropometry methods"},
            "lipids": {"analytes": ["total_cholesterol", "hdl_cholesterol"], "directly_measured": True,
                "specimen": "Venous blood collected into EDTA", "collection_volume_approximate_mL": 8,
                "test_volume_uL": 40, "instrument": "CardioChek Plus", "timing": "Measured immediately following manufacturer instructions",
                "repository_unit": "mg/dL", "generation_representation_unit": "mmol/L",
                "fasting_status": "not established in admitted metadata", "locator": "Target supplement pp.5-6 lipid methods; repository units metadata"}},
        "composition": {"age_distribution": "unspecified", "sex_proportions": "unspecified", "BMI_distribution": "unspecified",
            "lifestyle_mixture": "unspecified", "site_mixture": "unspecified", "joint_covariate_distribution": "unspecified",
            "individual_covariates_supplied": False, "raw_target_used_to_infer_composition": False},
        "inference_scope": {"purpose": "Descriptive analysis of the declared study-protocol adult selected sample", "national_representativeness_claimed": False,
            "sampling_weights": "not supplied", "cluster_identifiers": "not supplied", "causal_effect_claimed": False},
        "reference_boundary": "The measured reference and any eligibility counts, moments, fitted effects or outcome summaries are evaluator-only. This file contains request metadata alone.",
        "provenance_note": "Curated from admitted methods-only review and accepted prospective eligibility definition. Coordinator source documents are not constructor inputs because they may contain exposure or evaluation information."
    }
    write("target_protocol_metadata.json", target)

    contexts = []
    for original in source["contexts"]:
        identifier = original["id"]
        records = [item for item in source["constraint_candidates"] if item["population_ref"] == identifier]
        assert len(records) == 8
        country = original["country"]
        cohort_label = "MEIRU Urban/Rural NCD Survey" if country == "Malawi" else "Masaka General Population Cohort"
        context = {
            "id": identifier, "role": "source", "source_id": "greiner_2021", "source_packet": "sources/greiner_source_packet.json",
            "original_context_pointer": "/contexts/" + str(source["contexts"].index(original)), "original_context_record": copy.deepcopy(original),
            "population": {"country": country, "cohort": cohort_label, "site_stratum": original["site_stratum"],
                "sex_label": original["sex"], "task_sex_code": "M" if original["sex"] == "male" else "F",
                "sex_encoding_status": "Internal source-encoding convention only; not a verified biological-label mapping of the target F/M codes.",
                "age_minimum_inclusive": 18, "selection_rules": copy.deepcopy(source["selection_rules"]),
                "finer_sampling_details": "Only admitted source metadata are supplied; no unreported sampling weights, population composition or participant selection variables are reconstructed."},
            "measurement": copy.deepcopy(source["measurements"][original["measurement_ref"]]),
            "evidence_references": [{"id": item["id"], "record_class": item["record_class"], "variable": item["variable"],
                "reported_statistic": item["reported_statistic"], "source_table": item["denominator"]["source_table"],
                "locator": item["provenance"]["locator"], "source_doi": item["provenance"]["source_doi"],
                "issue_ids": item.get("issue_ids", [])} for item in records],
            "simulation": {"source_population_reconstructed": False, "n_rows": None, "seeds": None,
                "scientific_parameters": "Future Agent choices with explicit evidence/assumption provenance", "source_group_n_sets_generated_rows": False},
            "source_to_target_limits": ["Source health exclusions are not target exclusions.", "Sex/site strata are not target lifestyle categories.",
                "A unit conversion does not harmonize assays, specimen or fasting.", "Source weighting remains not_reported; no exact weighted-estimator claim."]}
        contexts.append(context)
    write("source_contexts.json", {"schema_version": "k02_source_context_requests.v1", "status": "descriptive_context_requests_not_an_executable_bridge_plan",
        "source_packet_sha256": original_sha, "source_doi": source["provenance"]["source_doi"],
        "canonical_generation_units": {"age": "year", "sex": "1", "bmi": "kg/m^2", "total_cholesterol": "mmol/L", "hdl_cholesterol": "mmol/L"},
        "contexts": contexts,
        "pooled_contextual_regression_ids": [item["id"] for item in source["contextual_regressions"]],
        "pooled_regression_scope": "Pooled African Table 3 rows are contextual evidence, not subgroup-specific or target equations. Raw/log transformations remain unresolved and numerical calibration is not allowed.",
        "source_issues": copy.deepcopy(source["issues"])})

    request = {
        "schema_version": "k02_clinical_request.v1", "case_id": "K02", "status": "draft_for_independent_packet_review_not_case_or_global_release",
        "request_type": "evidence_guided_whole_cohort_generation", "purpose": "Construct one joint virtual cohort for three prespecified descriptive analyses.",
        "n_rows_per_target_table": 5000, "task_contract": "task_template.json", "target_context": "target_protocol_metadata.json",
        "source_contexts": "source_contexts.json", "evidence_packet": "sources/greiner_source_packet.json",
        "output_route": "generator.py", "individual_inputs": None,
        "target_schema": {"row_id": "id", "ordered_columns": [c["name"] for c in task["columns"]],
            "all_values_required": True, "unique_identifier": True, "strictly_positive": ["bmi", "total_cholesterol", "hdl_cholesterol"],
            "positivity_note": "The basic harness schema has inclusive minimum bounds only. Do not replace strict positivity with an arbitrary numerical floor; the case validator must enforce the declared >0 requirement.",
            "extra_target_variables": "Not requested; derived/source-only quantities do not expand the release schema."},
        "representation": {"all_generation_contexts_same_columns_and_units": True, "lipid_generation_unit": "mmol/L",
            "target_analysis_unit": "mg/dL", "output_to_analysis_unit_map": {"path": "../unit_mapping", "status": "separate_root_owned_reviewed_artifact_required_before_activation"},
            "assay_harmonization_claimed": False, "source_feedback_unit_conversion": False},
        "scientific_uses": [
            {"id": "K02-HDL-BMI", "formula": "hdl_cholesterol ~ 1 + age + categorical sex + bmi", "estimator": "unweighted ordinary least squares", "reported_quantity": "BMI coefficient multiplied by 5", "unit": "mg/dL per 5 kg/m^2"},
            {"id": "K02-TC-BMI", "formula": "total_cholesterol ~ 1 + age + categorical sex + bmi", "estimator": "unweighted ordinary least squares", "reported_quantity": "BMI coefficient multiplied by 5", "unit": "mg/dL per 5 kg/m^2"},
            {"id": "K02-LIPID-RESIDUAL", "formula": "Pearson correlation of residuals from the two models above fitted on the same rows", "unit": "1", "role": "joint reuse"}],
        "analysis_common_rules": {"same_release_and_common_eligible_rows_for_all_three": True, "reference_category": "M", "categorical_indicator": "I(sex == 'F')",
            "contrasts_are_descriptive_not_causal": True, "expected_target_effects_supplied": False, "evaluation_margins_or_target_SD_supplied": False},
        "agent_scientific_responsibility": {
            "joint_structure": "Choose and justify from admitted evidence and explicit assumptions.",
            "parameter_values_and_distributions": "Unassigned; future Agent choices, not controller-written means, slopes, signs, variances or distribution families.",
            "shared_and_context_varying_parameters": "Declare the complete shared scientific structure and every context-varying input with rationale/provenance before freeze.",
            "target_demographic_composition": "Unspecified; choose and disclose assumptions without reading target rows or target-derived summaries.",
            "transport_assumptions": "State source selection, population composition, assay/specimen and fasting differences. Do not label their resolution as verified.",
            "unreported_relations": "May be modeled under explicit assumptions; missing evidence does not itself imply zero, independence or a release blocker.",
            "common_model": "Future source and target execution must retain one generator's bytes and the entire scientific specification except active_context; that linkage does not prove scientific compliance or transfer."},
        "feedback_rules": {"required_engine": "semantic_feedback_v1", "legacy_fallback": False,
            "supplement": "existing execution_feedback collector only where separately declared and independently reviewed",
            "geometric_means": "Keep original kind; v1 remains unavailable, supplement may compute supported descriptive values.",
            "unknown_source_weighting": "Keep not_reported; exact source-estimator comparison is unavailable. Any unweighted proxy needs a separate reviewed assumption.",
            "confidence_intervals": "Estimator uncertainty only; never participant/residual SD, acceptance bands or automatic precision weights.",
            "age_quantiles": "Reported context only because finite-sample convention is unresolved.",
            "table3_regressions": "Context only; unresolved transformations/adjustments forbid implicit raw-scale numerical constraints.",
            "non_HDL": "Original source evidence retained as TC minus HDL, a derived quantity. Current five-variable output does not include it and the collector does not add it; executable derived checks need a separately reviewed path.",
            "diagnostic_disposition": {
                "original_numerical_source_candidates": 30,
                "potential_direct_source_scenario_geometric_means": {"count": 18, "variables": ["bmi", "total_cholesterol", "hdl_cholesterol"], "status": "supplement_can_compute_descriptive_values_after_context_and_binding_review"},
                "potential_direct_source_scenario_prevalences": {"count": 6, "variable": "hdl_cholesterol", "status": "threshold_operators_available_but_unknown_source_weights_prevent_strict_source_checks"},
                "non_HDL_geometric_means": {"count": 6, "status": "evidence_retained_diagnostic_unavailable_without_separate_derived_view_not_added_here"},
                "age_quantile_context_records": 18, "pooled_regression_context_records": 12,
                "active_operational_source_checks": 0,
                "strict_source_checks": "Unavailable under current unknown weighting; geometric means also remain unsupported in frozen semantic v1."},
            "active_check_ids": [], "proxy_approvals": [], "target_feedback": "No measured-target outcome feedback to constructors."},
        "information_boundary": {"allowed_files": "manifest.json exact file allowlist", "target_individual_rows": "forbidden",
            "target_moments_effects_exposed_conclusions": "forbidden", "other_constructors_or_historical_target_results": "forbidden",
            "new_searches_studies_downloads": "not authorized for this packet", "input_boundary_is_filesystem_sandbox": False},
        "execution_and_revisions": {"execution_enabled": False, "candidate_construction_authorized_by_this_file": False,
            "maximum_feedback_decisions": 1, "per_context_source_rows_seeds_and_attempt_caps": "Controller must freeze finite schedule before execution; failed attempts count.",
            "target_seed_schedule": "Pending separate frozen controller schedule", "retention": "Explicitly retain initial outputs or make at most one revised scientific candidate; no better-seed or better-stage selection."},
        "uncertainty_and_missing_information": [
            {"item": "Target demographic and lifestyle composition", "status": "unspecified", "consequence": "Declare a target-composition assumption; do not infer it from reserved rows."},
            {"item": "Joint covariate/lipid law and conditional residual dependence", "status": "partly identified by external evidence", "consequence": "Choose an explicit scientific model and disclose unsupported relationships."},
            {"item": "Source selection details, weights and exact row denominators", "status": "partly unresolved", "consequence": "Preserve original table-specific counts and unknown weights; use only supported or explicitly assumption-defined diagnostics."},
            {"item": "Assay/specimen/fasting transfer", "status": "not validated", "consequence": "Treat as a transport limitation; unit conversion alone is insufficient."},
            {"item": "Controller budgets, unit-map approval and case/global release", "status": "not supplied as active permission", "consequence": "Operational release requirements remain separate from unspecified scientific relationships."}]
    }
    write("clinical_request.json", request)

    manifest = {"schema_version": "k02_request_manifest.v1", "status": "draft_review_commitment_not_release",
        "files": {p.relative_to(HERE).as_posix(): sha(p) for p in sorted(HERE.rglob("*")) if p.is_file() and p.name != "manifest.json"},
        "immutable_original_source_sha256": original_sha, "source_copy_sha256": sha(source_copy),
        "source_copy_byte_identical": sha(source_copy) == original_sha,
        "allowed_nonclinical_interface_documents": ["cohort_harness/contracts.py", "work/scaleup_2026-11-01/bridge/README.md", "work/scaleup_2026-11-01/operators/INTEGRATION.md"],
        "not_in_constructor_inputs": ["STATE.json", "coordinator/admission/evaluation/exposure notes", "raw target/reference files", "other candidates", "target result-bearing publications or summaries"],
        "new_searches": 0, "new_original_studies": 0, "generator_executions": 0, "target_raw_reads": 0,
        "verification": {"task_contract_validation": "passed", "source_contexts": len(contexts), "source_record_references": sum(len(c["evidence_references"]) for c in contexts),
            "source_values_changed": False, "clinical_model_written": False, "clinical_parameter_values_chosen": False}}
    assert sha(SOURCE) == original_sha == sha(source_copy)
    write("manifest.json", manifest)
    return manifest


if __name__ == "__main__":
    result = build()
    print(json.dumps({"status": "draft_request_built", "files": len(result["files"]), "verification": result["verification"]}, indent=2))
