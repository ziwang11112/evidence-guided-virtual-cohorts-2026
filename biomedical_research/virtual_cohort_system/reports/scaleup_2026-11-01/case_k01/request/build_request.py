"""Controller-only deterministic packaging of two pinned, selected evidence views.

No patient-data access, network, model fitting, sampling, approvals or execution.
Run once from any working directory; existing generated files are never overwritten.
Only the manifest's builder_files belong in a constructor's mounted packet.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CASE = HERE.parent
INPUTS = {
    "african_candidates": (CASE / "evidence/CANDIDATE_EVIDENCE.json", "70d0a2c0d7b06d020699b2fa7db22dac9882ddf76ebc2b6b8f86a596834190db"),
    "mind_selected_reuse": (CASE / "evidence/MIND_REUSE_CANDIDATE.json", "818382e977c429fbdb557c8554d0ad42ef4eb08192bb0d158fff46c5d8090b70"),
    "context_eligibility": (HERE / "context_eligibility.json", "22665dcd83e6f5e9b17b073d0bfb33e055a823311f2e57e6b9214f5296b6da94"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def read_bound(input_id: str) -> dict:
    path, expected = INPUTS[input_id]
    data = path.read_bytes()
    if digest(data) != expected:
        raise ValueError(f"Pinned input changed: {input_id}")
    return json.loads(data)


def compile_packet() -> dict[str, object]:
    african = read_bound("african_candidates")
    mind = read_bound("mind_selected_reuse")
    eligibility = read_bound("context_eligibility")
    contexts = eligibility["contexts"]
    columns = [
        {"name": "id", "kind": "string", "unit": "1", "role": "identifier", "nullable": False},
        {"name": "age", "kind": "number", "unit": "year", "role": "generated", "nullable": False},
        {"name": "sex", "kind": "category", "unit": "1", "role": "generated", "nullable": False, "categories": ["F", "M"]},
        {"name": "bmi", "kind": "number", "unit": "kg/m^2", "role": "generated", "nullable": False},
        {"name": "glucose", "kind": "number", "unit": "mmol/L", "role": "generated", "nullable": False},
    ]
    task = {
        "schema_version": 1,
        "task_id": "K01-pooled-poc-glucose-canonical-request-v1",
        "mode": "whole_cohort",
        "population": contexts["target_haalsi_pooled_poc"]["population"],
        "row_id": "id",
        "n_rows": 5000,
        "columns": columns,
        "information_policy": {
            "mode": "published_evidence",
            "excluded_cohorts": ["HAALSI", "Agincourt target cohort", "AWI-Gen overlapping populations"],
            "allowed_tools": [],
        },
        "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 1},
    }
    # The original selected records are copied exactly, rather than re-entered.
    # Their opaque old-input IDs/pointers preserve provenance without mounting
    # unrelated old source bundles, target-comparability prose, or private captures.
    records = []
    for index, original in enumerate(mind["items"]):
        records.append({
            "id": original["id"], "source_id": original["source_id"],
            "record_class": "potential_source_marginal",
            "context_id": "source_mind_china_2019",
            "canonical_variable": "glucose" if original["variable"] == "serum_glucose_fsg" else original["variable"],
            "original_selected_record": copy.deepcopy(original),
            "provenance": {"packet_input_id": "mind_selected_reuse", "json_pointer": f"/items/{index}", "original_record_canonical_sha256": digest(canonical(original))},
            "diagnostic_active": False,
            "strict_semantic_v1_status": "unavailable_pending_recipe; unspecified source weights; SD divisor also unspecified for SD items",
            "descriptive_scenario_status": "candidate only; requires explicit equal-weight/operator assumptions and separate context/recipe review",
        })
    for index, original in enumerate(african["records"]):
        ayele = original["source_id"] == "ayele_2020_dire_dawa"
        marginal = ayele and original["statistic"] != "adjusted_odds_ratio"
        records.append({
            "id": original["id"], "source_id": original["source_id"],
            "record_class": "potential_source_marginal" if marginal else "context_only_unavailable",
            "context_id": "source_ayele_dire_dawa_2017" if ayele else "context_bahendeka_uganda_2014",
            "canonical_variable": original["variable"] if marginal else None,
            "original_selected_record": copy.deepcopy(original),
            "provenance": {"packet_input_id": "african_candidates", "json_pointer": f"/records/{index}", "original_record_canonical_sha256": digest(canonical(original))},
            "diagnostic_active": False,
            "strict_semantic_v1_status": "unavailable; unspecified weights and no reviewed exact operator" if marginal else "unavailable; contextual record only",
            "descriptive_scenario_status": "candidate only; reviewed weighting/operator and literal-category interpretation required" if marginal else "not proposed for numerical activation",
        })
    if len(records) != 34 or len({r["id"] for r in records}) != 34:
        raise ValueError("Unexpected selected evidence identity/count")
    if sum(r["record_class"] == "potential_source_marginal" for r in records) != 18:
        raise ValueError("Unexpected marginal candidate count")
    source_objects = []
    for source in african["sources"]:
        projected = {k: copy.deepcopy(v) for k, v in source.items() if k != "private_capture"}
        if "private_capture" in source:
            projected["capture_provenance"] = {k: copy.deepcopy(v) for k, v in source["private_capture"].items() if k != "path"}
        source_objects.append(projected)
    source_objects.insert(0, {
        **{k: copy.deepcopy(mind["source"][k]) for k in ["source_id", "title", "doi", "article_url", "original_locator"]},
        "population": copy.deepcopy(mind["population"]),
        "measurement": copy.deepcopy(mind["measurement"]),
        "applicability": copy.deepcopy(mind["applicability_to_k01"]),
        "verification_scope": "Selected retained Table1 audit; prior independent arithmetic review focused other tables, not an independent Table1 re-transcription. New seven-item reuse was checked against retained audited files.",
    })
    evidence = {
        "schema": "k01_sanitized_selected_source_packet_v1",
        "status": "candidate_evidence_for_packet_review_only",
        "approved_for_builder": False,
        "source_objects": source_objects,
        "records": records,
        "counts": {"mind_direct_moments": 6, "mind_derived_female_proportion": 1, "ayele_covariate_marginals": 11, "ayele_contextual_odds_ratios": 6, "bahendeka_abstract_contextual": 10, "potential_source_marginal_items": 18, "context_only_items": 16, "total_selected_records": 34, "active_diagnostics": 0},
        "input_commitments": [{"input_id": k, "sha256": h} for k, (_, h) in INPUTS.items() if k != "context_eligibility"],
        "mind_original_provenance_commitments": [{k: b[k] for k in ["input_id", "sha256", "role"]} for b in mind["input_bindings"]],
        "provenance_access": "Hashes and JSON pointers identify controller-retained original inputs; those files and private captures are not constructor-mounted inputs. Source URLs identify articles, not permission for additional browsing.",
        "uncertainty_policy": "Preserve original values, scales, CI bounds and roles. Individual SD is not estimator SE, CI or conditional residual SD. Unknown weights/divisors remain unknown. No CI-to-SD conversion or extra uncertainty reconstruction.",
        "percentage_policy": "Ayele and Bahendeka printed percentages stay in percent. MIND female fraction was derived once from reported counts and is already unit1. Any later transformation must be explicit and provenance-bound, not repeated division.",
        "activation": {"active_constraints": [], "source_recipes": None, "review_approval": None, "release_authorized": False},
    }
    protocol = {
        "schema": "k01_target_protocol_metadata_v1",
        "context_id": "target_haalsi_pooled_poc",
        "population": contexts["target_haalsi_pooled_poc"]["population"],
        "definition_basis": {"release_doi": "10.7910/DVN/F5YHML", "release_version": "3.0", "codebook_year": 2016, "survey_variables_update": "2017-04-14", "basis": "Reviewed official variable definitions and sex value-label metadata only; no target outcomes or composition supplied."},
        "measurements": {
            "age": {"canonical_unit": "year", "reference_field": "rage", "definition": "Census age on 31 July 2014 at sample selection; not interview-date age", "locator": "Codebook p13; survey/variables DOCX zero-based table42 row18"},
            "sex": {"reference_field": "rsex", "canonical_categories": ["F", "M"], "mapping": {"F": "Female", "M": "Male"}, "raw_metadata_mapping": {"1": "M", "2": "F"}, "basis": "Actual-file value-label metadata independently verified; census-preloaded sex; no category frequencies supplied", "locator": "Definition codebook p95; DOCX table42 row20; reviewed selected value-label dictionary"},
            "bmi": {"canonical_unit": "kg/m^2", "reference_field": "c_bs_bmi", "definition": "BMI derived from cleaned height and weight", "unit_basis": "Conventional BMI unit interpretation from documented height cm and weight kg; actual BMI label has no explicit unit string", "locator": "Codebook p89; DOCX table41 row32"},
            "glucose": {"canonical_unit": "mmol/L", "reference_field": "c_bs_glucose", "definition": "Released cleaned point-of-care glucose from CareSens readings/checks and comments; fingerstick/capillary protocol context", "locator": "Codebook pp85–88; DOCX table41 row40", "fasting": "Pooled protocol; fasting status is not an eligibility requirement", "exact_device_model": "not_established", "plasma_or_serum_equivalence": "not_established", "feeding_mixture": "unspecified; no target proportions or dependencies supplied", "recorded_value_estimand": True},
        },
        "reference_selection": {"age_minimum_inclusive": 40, "age_maximum": None, "sex": ["F", "M"], "require_finite": ["age", "bmi", "glucose"], "require_strictly_positive": ["bmi", "glucose"], "native_and_tagged_missing": "excluded from the measured reference subset; no imputation", "unknown_nonmissing_sex_or_bad_numeric_dtype": "fail input validation rather than silently coercing", "named_numeric_nonmeasurement_sentinels": {"age": [], "bmi": [], "glucose": []}, "sentinel_qualification": "None identified in reviewed metadata; not a claim of physical absence. Range-flag cutoffs are not sentinel lists.", "flag_exclusion": False, "fasting_restriction": False, "treatment_exclusion": False, "tail_trimming_or_winsorization": False, "retain_positive_finite_cleaned_boundary_numbers": True},
        "generated_table": {"n_rows": 5000, "individual_inputs": None, "all_rows_must_satisfy_contract": True, "filtering_repair_or_shrinking_permitted": False, "mandatory_guard_contract": "context_eligibility.json", "caller_integration": "pending"},
        "transport_limits": ["Recorded cleaned boundary/substitution values do not become exact latent biological measurements.", "Source serum assays, repeated glucose averaging, fasting rules, health exclusions, imputation and age eligibility do not become target rules.", "Unknown target demographic, feeding and treatment mixture is not reconstructed from reference data; construction assumptions belong to the Agent."],
    }
    source_contexts = {
        "schema": "k01_source_context_metadata_v1",
        "canonical_task_schema": "task_template.json",
        "eligibility_contract": "context_eligibility.json",
        "all_generation_units_identical": True,
        "source_unit_or_assay_conversion_activated": False,
        "contexts": [
            {"context_id": "source_mind_china_2019", "source_ids": ["WANG2024_MIND"], "role": "potential_source_generation", "population": contexts["source_mind_china_2019"]["population"], "candidate_ids": [r["id"] for r in records if r["source_id"] == "WANG2024_MIND"], "measurement": "Source glucose represents selected fasting serum glucose-oxidase FSG in mmol/L; target is pooled capillary POC. Shared units do not assert assay or feeding equivalence.", "age_timing": "Reported 61–80 source range; demographics/BMI2018 and laboratory2019 retained without age transformation", "feedback_policy": "pending_reviewed_semantic_feedback_v1_with_explicit_approximations_if_supported", "source_n_is_generated_n": False},
            {"context_id": "source_ayele_dire_dawa_2017", "source_ids": ["ayele_2020_dire_dawa"], "role": "potential_source_generation", "population": contexts["source_ayele_dire_dawa_2017"]["population"], "candidate_ids": [r["id"] for r in records if r["context_id"] == "source_ayele_dire_dawa_2017" and r["record_class"] == "potential_source_marginal"], "context_only_ids": [r["id"] for r in records if r["source_id"] == "ayele_2020_dire_dawa" and r["record_class"] == "context_only_unavailable"], "measurement": "Covariate margins only. Original capillary three-day average and composite DM thresholds in mg/dL are contextual; no glucose margin, binary-DM check or conversion is activated. Canonical generated glucose remains mmol/L under explicit Agent assumptions.", "category_boundary_policy": "Original printed age labels25–34/35–44/45–54/55–64 and BMI18.5–24.9 remain unchanged in evidence. The fixed descriptive_diagnostic_plan.json explicitly approximates completed-year age groups by half-open[25,35),[35,45),[45,55),[55,65) under Methods25–64; it is not an exact-source operator claim. BMI middle stays closed[18.5,24.9], preserving the gap to25. No silent boundary change is permitted; strict operators remain unavailable.", "feedback_policy": "pending_reviewed_semantic_feedback_v1_with_explicit_approximations_if_supported", "source_n_is_generated_n": False},
            {"context_id": "context_bahendeka_uganda_2014", "source_ids": ["bahendeka_2016_uganda"], "role": "context_only_not_scheduled", "reported_age_range": [18, 69], "context_only_ids": [r["id"] for r in records if r["source_id"] == "bahendeka_2016_uganda"], "feedback_policy": "none", "generation_authorized": False, "limitation": "Abstract-only; weighted summaries with unavailable full operator, device/protocol and selection. No exact equal-weight check proposed."},
        ],
        "execution": {"source_trials": None, "seeds": None, "n_rows": None, "failed_attempts_count_toward_budget": True, "schedule_status": "future_finite_independently_reviewed_declaration_required", "source_checks_activated": 0},
        "scientific_parameters": {"owner": "future construction Agent", "shared_parameters": None, "context_varying_parameters": None, "joint_structure": None, "target_transport": None},
    }
    # Fixed prospective descriptive operators. This is a scientific plan, not
    # an executable collector recipe or an approval. Conjunctions must be
    # evaluated as one Boolean event over the whole context table.
    diagnostic_items = []
    for record in records:
        if record["record_class"] != "potential_source_marginal":
            continue
        original = record["original_selected_record"]
        statistic = original["statistic"]
        item = {
            "id": "descriptive__" + record["id"],
            "evidence_id": record["id"],
            "source_id": record["source_id"],
            "context_id": record["context_id"],
            "role": "descriptive_equal_weight_source_scenario_not_strict_replication",
            "original_record_canonical_sha256": record["provenance"]["original_record_canonical_sha256"],
            "selection": [],
            "denominator": "all validated rows in this source-context output; no group-selection denominator",
            "generated_row_weights": "equal",
            "source_weighting": "not_reported; equal weighting is an explicit approximation",
            "active": False,
            "strict_semantic_v1_status": "unavailable",
            "review_approval": None,
        }
        if statistic in {"arithmetic_mean", "individual_standard_deviation"}:
            item.update({
                "operator": {"kind": "mean" if statistic == "arithmetic_mean" else "standard_deviation", "column": record["canonical_variable"], **({"ddof": 1} if statistic == "individual_standard_deviation" else {})},
                "comparison_value": original.get("estimate", original.get("value")),
                "comparison_unit": original["unit"],
                "comparison_derivation": "direct reported source moment; no numerical transformation",
                "uncertainty_role": "individual dispersion, not SE/CI/residual SD" if statistic == "individual_standard_deviation" else "reported arithmetic mean; no estimator precision reconstructed",
                "sd_divisor_note": "ddof1 is a prospective descriptive scenario; source divisor not reported" if statistic == "individual_standard_deviation" else None,
            })
        else:
            if record["source_id"] == "WANG2024_MIND":
                numerator = original["derivation"]["exact_numerator"]
                denominator = original["derivation"]["exact_denominator"]
                event = {"all": [{"column": "sex", "op": "eq", "value": "F"}]}
            else:
                numerator = original["source_count"]
                denominator = original["source_denominator"]
                if original["variable"] == "sex":
                    event = {"all": [{"column": "sex", "op": "eq", "value": "M" if original["group"] == "Male" else "F"}]}
                elif original["variable"] == "age":
                    lower = int(record["id"].split("_")[-2])
                    event = {"all": [{"column": "age", "op": "ge", "value": lower}, {"column": "age", "op": "lt", "value": lower + 10}]}
                elif record["id"] == "ayele_bmi_underweight":
                    event = {"all": [{"column": "bmi", "op": "lt", "value": 18.5}]}
                elif record["id"] == "ayele_bmi_normal":
                    event = {"all": [{"column": "bmi", "op": "ge", "value": 18.5}, {"column": "bmi", "op": "le", "value": 24.9}]}
                else:
                    event = {"all": [{"column": "bmi", "op": "ge", "value": 25}]}
            item.update({
                "operator": {"kind": "proportion", "boolean_event": event, "output_unit": "1"},
                "comparison_value": numerator / denominator,
                "comparison_unit": "1",
                "comparison_derivation": {"operation": "reported count divided by reported denominator once", "numerator": numerator, "denominator": denominator, "expression": f"{numerator}/{denominator}", "not_printed_percentage_division": True},
                "original_printed_percentage": original.get("value") if original["unit"] == "%" else None,
                "original_printed_unit": original["unit"],
                "original_printed_group": original.get("group", original.get("event")),
                "count_ratio_scope": "source sample composition, not weighted population prevalence; no independent claim beyond original counts",
                "uncertainty_role": "none reconstructed; original uncertainty remains in selected evidence",
            })
            if original["variable"] == "age":
                item["boundary_assumption"] = "Explicit completed-year interpretation for continuous generated ages: half-open [25,35),[35,45),[45,55),[55,65), under source Methods25–64 inclusive guard. Printed labels retained; this is not an exact-source operator claim."
            if record["id"] == "ayele_bmi_normal":
                item["boundary_assumption"] = "Literal closed[18.5,24.9]; gap(24.9,25) retained. No rescaling to force the three BMI proportions to sum to1."
        diagnostic_items.append(item)
    if len(diagnostic_items) != 18:
        raise ValueError("Unexpected descriptive plan count")
    diagnostics = {
        "schema": "k01_prospective_descriptive_diagnostic_plan_v1",
        "status": "fixed_scientific_proposal_for_independent_review_not_activated",
        "diagnostic_count": 18,
        "items": diagnostic_items,
        "global_assumptions": ["Generated source outputs represent complete post-imputation distributions; source field-specific imputation and missingness uncertainty is not recovered.", "Equal row weights and ddof1 are declared descriptive approximations; unknown original weights/divisors are not asserted known.", "Source composition counts and printed rounded percentages are distinct; count ratios are chosen comparison values with originals preserved.", "A Boolean conjunction must be one event over all validated rows. Applying a predicate as row selection would change the denominator and is forbidden."],
        "implementation_limit": "The existing direct-column operator cannot execute arbitrary conjunctions. A thin fixed-event helper now exists outside this builder packet; its production caller/collector binding and review remain pending. It can materialize each fixed Boolean event for proportion with selection=[]. No collector recipe or diagnostic is activated here.",
        "strict_source_replication_status": "unavailable",
        "required_execution_binding": "Exact source context, immutable task and output, evidence hashes, declared operator view, finite trial ledger and independent recipe/context review before any computation.",
        "source_trials_or_approvals": None,
        "active_diagnostics": 0,
    }
    request = {
        "schema": "k01_clinical_request_v1",
        "status": "request_preparation_for_independent_review",
        "approved_for_builder": False,
        "release_authorized": False,
        "task": "task_template.json",
        "target_protocol": "target_protocol_metadata.json",
        "context_eligibility": "context_eligibility.json",
        "source_contexts": "source_contexts.json",
        "selected_source_evidence": "selected_source_evidence.json",
        "descriptive_diagnostic_plan": "descriptive_diagnostic_plan.json",
        "request": "Generate a whole cohort of exactly5000 valid rows with id, age, sex, bmi, glucose. No observed individuals are supplied. Target age>=40 with no upper cutoff is mandatory; BMI and glucose are strictly positive finite. Return canonical units and literal F/M as defined.",
        "target_context": "target_haalsi_pooled_poc",
        "schema_vs_population": "Age is finite numeric without common column min/max so the same schema can represent distinct source populations. Mandatory context_eligibility guard enforces exact context/task population and all context age bounds. The bare task validator is insufficient for release.",
        "analysis_visibility": {"variables": {"G": "glucose", "A": "age", "B": "bmi", "S": "1 if sex==F, 0 if sex==M"}, "estimator": "unweighted ordinary least squares with intercept", "primary_uses": [{"id": "K01-GLUCOSE-BMI", "formula": "G ~ 1 + A + S + B", "contrast": "5 * beta_B", "unit": "mmol/L per5kg/m^2"}, {"id": "K01-GLUCOSE-AGE", "formula": "G ~ 1 + A + S + B", "contrast": "10 * beta_A", "unit": "mmol/L per10years"}, {"id": "K01-SEX-BMI", "formula": "G ~ 1 + A + S + B + S:B", "contrast": "5 * beta_S:B", "interpretation": "Female-minus-Male difference in BMI contrast", "unit": "mmol/L per5kg/m^2"}], "expected_effects_or_signs": None, "all_three_evidence_relationships": "joint_assumption_dependent", "failure_policy": "Singular models or missing sex support are unavailable/failure, not permission to replace the analysis."},
        "agent_scientific_ownership": ["Author the common joint distribution and all unreported dependence, interactions, distribution families and residual structure; no default independence or zero effect is prescribed.", "Declare shared and context-varying scientific parameters, provenance and source-to-target measurement, feeding, age and selection transport assumptions before freeze.", "Use the same generator bytes and common scientific spec in all source/target runs, changing only the declared active_context. Hash linkage is a mechanical check, not proof of transport or adherence to scientific declarations.", "Choose assumptions without target moments, composition, effects or individual data. Source means and margins are source-context evidence, not coordinator-prescribed target parameters."],
        "feedback_policy": {"strict_route": "semantic_feedback_v1_only", "legacy_fallback": False, "source_diagnostics_activated": 0, "strict_comparison": "Unavailable for unspecified weights and unresolved operators. Unknown values are not replaced with equal weighting.", "descriptive_approximation": "Only after explicit candidate-local weighting/operator/context assumptions and separate independent recipe review; original uncertainty and incompatibility labels remain bound. No approvals are filled here.", "context_only_records": "Six Ayele composite-DM ORs and ten Bahendeka abstract records cannot become continuous-glucose coefficients or executable checks."},
        "execution_prerequisites": ["Independent packet review and exact approved task commitment.", "Agent-authored model/evidence declarations and reviewed finite source/target trial schedule, including failed attempts.", "Root-owned validate_generated_context(frame, task, context_id=context_id) wired after immutable execution verification and before feedback or analysis for target and both source contexts.", "Exact child task/population/context binding; never select a weaker source age rule for a target output.", "All5000 target rows satisfy the whole-frame guard; no filtering, repair or delivery of a smaller complete subset."],
        "integration_status": "No candidate frozen or recipe activated. Guard and thin descriptive Boolean helper are separately implemented outside this builder packet; production caller/collector binding and review remain pending. This packet alone authorizes no clinical run.",
    }
    return {"task_template.json": task, "clinical_request.json": request, "target_protocol_metadata.json": protocol, "source_contexts.json": source_contexts, "selected_source_evidence.json": evidence, "descriptive_diagnostic_plan.json": diagnostics}


def main() -> None:
    outputs = compile_packet()
    names = list(outputs) + ["packet_manifest.json"]
    if any((HERE / name).exists() for name in names):
        raise FileExistsError("Packet already exists; refuse overwrite")
    if not (HERE / "README.md").is_file():
        raise FileNotFoundError("Packet README must be reviewed before packaging")
    for name, value in outputs.items():
        with (HERE / name).open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    builder_files = list(outputs) + ["context_eligibility.json", "README.md"]
    manifest = {
        "schema": "k01_request_packet_manifest_v1",
        "status": "prepared_for_independent_review_not_release",
        "builder_files": sorted(builder_files),
        "files": {name: {"sha256": digest((HERE / name).read_bytes()), "bytes": (HERE / name).stat().st_size} for name in sorted(builder_files)},
        "controller_packager": {"file": "build_request.py", "sha256": digest(Path(__file__).read_bytes()), "not_builder_visible": True},
        "input_commitments": [{"input_id": k, "sha256": h} for k, (_, h) in INPUTS.items()],
        "source_records": 34,
        "candidate_marginal_items": 18,
        "context_only_items": 16,
        "active_diagnostics": 0,
        "new_original_studies": 0,
        "fit_sample_or_execution_performed": False,
        "approved_for_builder": False,
        "review_approval": None,
    }
    with (HERE / "packet_manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "prepared_not_released", "files": len(builder_files), "records": 34, "manifest_sha256": digest((HERE / "packet_manifest.json").read_bytes())}))


if __name__ == "__main__":
    main()
