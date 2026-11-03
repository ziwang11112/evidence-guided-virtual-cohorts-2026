"""Build metadata-only CHNS main-study bindings; writes only this directory."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
P = HERE.parents[3]
OLD = P / "work/existing_data_benchmark_2026-11-02"

def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")

def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")

def binding(relative):
    path = P / relative
    return {"path": relative, "sha256": sha_bytes(path.read_bytes())}

def local_binding(name):
    return {"path": name, "sha256": sha_bytes((HERE / name).read_bytes())}

def build():
    e0, e1 = (load(OLD / "evidence" / f"{arm}.json") for arm in ("E0", "E1"))
    assert e0["shared_base"] == e1["shared_base"] and not e0.get("relationship_records")
    old_review = load(OLD / "evidence/PACKET_REVIEW.json")
    for arm in ("E0", "E1"):
        payload = (OLD / "evidence" / f"{arm}.json").read_bytes()
        expected = next(x["sha256"] for x in old_review["arm_bindings"] if x["path"] == f"{arm}.json")
        assert sha_bytes(payload) == expected
        (HERE / f"{arm}.json").write_bytes(payload)
    (HERE / "NGSP_UNITS.md").write_bytes((P / "work/developmental_continuation_v1_2026-11-03/author_inputs/sources/NGSP_UNITS.md").read_bytes())
    task = load(OLD / "implementation/task.json")
    task["task_id"] = "main-study-2026-11-03-CHNS2009-whole-cohort"
    task["budget"]["revisions"] = 1
    write("task.json", task)
    # Reuse the already reviewed metadata compiler, never its old build/run
    # entrypoint. Each registry points ONLY to the assigned sanitized packet.
    compiler_path = OLD / "implementation/prepare_bundles.py"
    spec = importlib.util.spec_from_file_location("chns_main_existing_compiler", compiler_path)
    compiler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compiler)
    sys.path.insert(0, str(P))
    from cohort_harness.contracts import validate_evidence
    from cohort_harness.lifecycle import _registry
    compiled_items = {}
    for arm, packet in (("E0", e0), ("E1", e1)):
        evidence, registry, groups = compiler.compile_evidence(packet, (HERE / f"{arm}.json").read_bytes(), (HERE / "NGSP_UNITS.md").read_bytes())
        validate_evidence(evidence, task)
        write(f"{arm}_evidence.json", evidence)
        write(f"{arm}_registry.json", registry)
        source_root = HERE / f"{arm}_sources"
        source_root.mkdir(exist_ok=True)
        (source_root / "evidence_packet.json").write_bytes((HERE / f"{arm}.json").read_bytes())
        (source_root / "NGSP_UNITS.md").write_bytes((HERE / "NGSP_UNITS.md").read_bytes())
        for entry in registry["artifacts"]:
            assert entry["path"] in {"sources/evidence_packet.json", "sources/NGSP_UNITS.md"}
            assert sha_bytes((source_root / Path(entry["path"]).name).read_bytes()) == entry["sha256"]
        compiled_items[arm] = evidence["items"]
        for kind in ("agent", "statistical"):
            write(f"{arm}_{kind}_profile.json", {"case_id": "CHNS2009", "information_condition": arm, "constructor_kind": kind,
                "source_numeric_mode": "reviewed_analytic_only", "analysis_ids": ["E1", "E2", "E3"],
                "budget": {"exploratory_attempts": 2, "final_attempts": 3, "total_attempts": 5, "rows": 3000, "trial_seeds": [5201, 5202], "final_seeds": [5101, 5102, 5103]}})
    assert compiled_items["E0"] == [x for x in compiled_items["E1"] if not x["id"].startswith("R_")]
    assert not any(x["kind"] in {"ols_coefficient", "correlation", "spearman_correlation"} for x in compiled_items["E0"])
    write("packet_scope_audit.json", {"schema_version": 1, "status": "static_audit_passed_independent_review_pending", "E0_exact_packet_has_no_relationship_records": not e0["relationship_records"],
        "E0_compiled_relational_items": 0, "E1_compiled_relational_items": 4, "compiled_common_items_equal": True,
        "E0_full_paper_or_broad_summary_paths": [], "registry_paths_each_arm": ["sources/evidence_packet.json", "sources/NGSP_UNITS.md"],
        "source_document_status": "Curator-derived sanitized evidence packet plus authored reuse of unit guidance; neither file is a primary-paper copy.",
        "registry_screening_basis": "Existing approved packet content and unchanged previously reviewed compiler; this is not independent approval of the new case, analytic adapter, model or release.",
        "E0_allowed_attribution": "Original DOIs and short locators only; retrieval prohibited. Descriptions of unknown correlation/row processing disclose no coefficient, direction or reconstructible relationship value.",
        "source_copy_instructions": {arm: {"registry_source": f"{arm}_registry.json", "registry_destination": "registry.json", "evidence_source": f"{arm}_evidence.json", "evidence_destination": "candidates/initial/evidence.json", "source_directory": f"{arm}_sources", "source_destination": "sources"} for arm in ("E0", "E1")}})
    plan = load(P / "work/chns_admission_2026-11-01/f2/analysis_plan.json")
    uses = []
    for item, label in zip(plan["estimands"], ("source_analogous_separate_Jansen_BMI_projection_with_transport_assumptions", "source_analogous_separate_Jansen_FPG_projection_with_measurement_and_transport_assumptions", "additional_joint_conditional_use_not_directly_supplied_or_numerically_calibrated")):
        record = {k: copy.deepcopy(v) for k, v in item.items() if k not in {"source_class", "feedback"}}
        record["evidence_support"] = label
        record["visible_to_author"] = True
        record["target_feedback"] = False
        record["direct_numerical_calibration_target"] = False
        record["source_analogous_calibration_possible"] = item["id"] != "E3"
        uses.append(record)
    evaluation = {"schema_version": 1, "case_id": "CHNS2009", "role": "author_visible_analysis_definitions_without_reference_values",
        "uses": uses, "population": "All generated rows; all three uses share the same complete five-variable table. No analysis-specific dropping.",
        "response": "HbA1c percent", "estimator": "unweighted intercept-including raw OLS", "reference_interval": plan["reference_interval"],
        "diagnostics": plan["diagnostics"], "minimum_rows_for_existing_evaluator": 100,
        "validity": "Finite numeric values; integer age 35-74; female 0/1; positive BMI. Nonpositive glucose or HbA1c withholds scientific estimates without dropping rows. Full rank and residual degrees of freedom required.",
        "interpretation": {"E1_E2": "Source-analogous projections only; no equality with target coefficients is assumed.",
            "E3": "No supplied Pani coefficient: Pani is absent from both new packets. The age term conditional on BMI and glucose is not determined by the two separate Jansen focal slopes or marginal correlations alone. Any model-implied value is an assumption-dependent consequence, not new empirical evidence.",
            "algebraic_implication_policy": "Report if a chosen model or constraint set algebraically fixes any use; do not claim such an implication is newly inferred.",
            "interval": "Existing reference CR1/t interval is sample uncertainty, not a population truth or equivalence margin.",
            "no_pooled_score": True, "synthetic_p_values_as_clinical_evidence": False}}
    write("evaluation.json", evaluation)
    source_ops = []
    for r in e1["relationship_records"]:
        supported = r["id"] != "R_MIND_SPEARMAN"
        source_ops.append({"evidence_id": r["id"], "source_context_id": r["source_context_id"], "packet": "E1.json",
            "reported_definition_pointer": f"/relationship_records/{e1['relationship_records'].index(r)}",
            "record_canonical_sha256": sha_bytes(canonical(r)), "locator": r["source_locator"],
            "locator_utf8_sha256": sha_bytes(r["source_locator"].encode()), "strict_replay": copy.deepcopy(r["strict_replay"]),
            "qualified_operation_definition": copy.deepcopy(r["executable_definition_candidate"]),
            "analytic_path": {"status": "implemented_pending_independent_review" if supported else "unavailable_from_ordinary_moments",
                "module": "source_operations.py", "function": "evaluate", "evidence_id_argument": r["id"],
                "required_input": "Author-derived finite post-selection population means/covariance in separately declared source context" if supported else "A law-specific rank-functional derivation or separately budgeted source-row check; no Gaussian-copula shortcut is automatically admitted.",
                "row_producing": False, "author_moment_derivation_required": True,
                "does_not_install_parameters": True, "does_not_establish_source_reconstruction": True},
            "existing_row_arithmetic": {"path": "cohort_harness/source_checks.py", "function": "apply_operator", "only_if_separately_bound_and_budgeted": True},
            "existing_qualified_collector": {"path": "work/evidence_revision_v1_2026-11-02/implementation/qualified_relationships_v1.py", "function": "compute_qualified_feedback", "not_activated_here": True},
            "assumptions": ["Source weighting is unreported; equal-weight analytic scenario is qualified.", "Source law, health selection, covariate dependence and original missing-data treatment are not identified by these records.", "Source contexts must retain their own eligibility and measurement meaning; no target distribution substituted.", "No CI-to-SD or precision-weighted pooled loss; only reported point and raw discrepancy may be compared."]})
    write("source_operations.json", {"schema_version": 1, "case_id": "CHNS2009", "arm": "E1", "execution_enabled": False,
        "classification": "case_bound_qualified_numerical_paths_not_strict_replay", "operations": source_ops,
        "context_plan": [{"context_id": m["source_context_id"], "mode": "analytic_declared_source_law_preferred_no_source_tables_allocated", "strict_replay": "not_computable", "row_replay": "not_allocated", "original_metadata": m,
            "source_support_rule": "Source support is separate from target age 35-74. Do not truncate a source law to target support or claim it is the original cohort. All moments must be after declared source selection."} for m in e1["shared_base"]["source_metadata"]],
        "finite_budget": "No source rows allocated by this card. All trial row production, if exceptionally approved, uses the same two total exploratory slots per construction; no renewable per-context budget.",
        "all_four_must_be_accounted": True,
        "uptake_record_fields": ["evidence_id", "status: numerical_constraint|analytic_check|contextual_only|declined|unavailable", "model_or_calculation_path", "context_id", "assumption_ids", "measurement_mapping", "moment_derivation_or_receipt", "calculated_value_or_unavailable_reason", "source_point_if_comparison", "raw_difference_if_comparison"],
        "release_gate": "At least one applicable nonmarginal analytic path independently reviewed before construction; report actual uptake for every author without silently relabelling contextual use as numerical integration."})
    prov = []
    for section, records in (("/shared_base/source_metadata", e1["shared_base"]["source_metadata"]), ("/shared_base/grouped_marginal_records", e1["shared_base"]["grouped_marginal_records"]), ("/relationship_records", e1["relationship_records"])):
        for i, record in enumerate(records):
            locator = record.get("locator", record.get("source_locator"))
            prov.append({"record_id": record["id"], "origin_file": "work/existing_data_benchmark_2026-11-02/evidence/E1.json", "origin_file_sha256": sha_bytes((OLD / "evidence/E1.json").read_bytes()), "json_pointer": f"{section}/{i}", "record_canonical_sha256": sha_bytes(canonical(record)), "locator": locator, "locator_utf8_sha256": sha_bytes(locator.encode()) if locator else None})
    write("provenance.json", {"schema_version": 1, "role": "curator_only_not_author_input", "canonicalization": "UTF8 sorted-key compact JSON ensure_ascii=false allow_nan=false", "packets_copied_byte_identically": True, "records": prov,
        "approval_bindings": [binding("work/existing_data_benchmark_2026-11-02/evidence/PACKET_REVIEW.json"), binding("work/core_highlight_2026-11-02/SOURCE_PROJECTION_APPROVAL.json"), binding("work/core_highlight_2026-11-02/SOURCE_PROJECTION_CANDIDATES.json")],
        "no_new_source_read_or_acquisition": True})
    # Only pre-recorded identities are copied from this old state; no target
    # report is opened, rehashed, recomputed or supplied to an author.
    old_state = load(OLD / "STATE.json")
    prior = [binding(path) for path in ["docs/CORE_METHOD_AND_MAIN_RUN_FREEZE_2026-11-03.md", "work/chns_admission_2026-11-01/f2/analysis_plan.json", "work/chns_admission_2026-11-01/f2/evaluation/chns_f2_evaluation.py", "work/chns_admission_2026-11-01/semantics/MEASUREMENT_POLICY_DECISION.md", "work/existing_data_benchmark_2026-11-02/evidence/E0.json", "work/existing_data_benchmark_2026-11-02/evidence/E1.json", "cohort_harness/source_checks.py", "work/evidence_revision_v1_2026-11-02/implementation/qualified_relationships_v1.py", "work/evidence_revision_v1_2026-11-02/implementation/scientific_validity_v1.py", "work/developmental_continuation_v1_2026-11-03/source_audit/independent_source_audit.py", "work/developmental_continuation_v1_2026-11-03/source_audit/AUDIT_REVIEW.md"]]
    common = ["task.json", "evaluation.json", "NGSP_UNITS.md", "AUTHOR_COMMON.md"]
    allowlist = {"E0": common + ["E0.json", "E0_evidence.json", "E0_registry.json", "E0_sources/evidence_packet.json", "E0_sources/NGSP_UNITS.md"], "E1": common + ["E1.json", "E1_evidence.json", "E1_registry.json", "E1_sources/evidence_packet.json", "E1_sources/NGSP_UNITS.md", "source_operations.json", "source_operations.py"],
        "prohibited": ["case_card.json", "provenance.json", "curator_exposure_note.md", "binding_validation.json", "build_case_binding.py", "other arm packet", "old target reports, reference files and result-bearing notes", "all participant/generated tables", "other author/comparator artifacts", "whole project workspace", "new retrieval, originals or downloads"],
        "path_resolution": "Only these case-directory relative files plus the separately frozen arm-specific session/runtime guide; no repository search or DOI retrieval.",
        "boundary": "Procedural context restriction, not proof of pretraining blindness or host sandbox isolation."}
    write("author_allowlist.json", allowlist)
    card = {"schema_version": 1, "case_id": "CHNS2009", "phase": "metadata_bound_pending_independent_review_and_global_release", "execution_enabled": False,
        "role": "curator_and_reviewer_only", "exposure": {"status": "researcher_exposed_developmental_reference", "untouched_confirmation": False, "prior_completed_units": ["CHNS_F2", "existing_data_benchmark_2026-11-02", "developmental_continuation_v1_2026-11-03", "adaptive_reference_pilot_2026-11-03"], "historical_results_unchanged": True, "fresh_authors_do_not_reset_exposure": True, "curator_incident": "curator_exposure_note.md"},
        "target_contract": {"task": local_binding("task.json"), "wave": 2009, "common_complete_variables": plan["denominator"], "linkage": plan["linkage"], "measurement_policy": plan["measurement_policy"], "input_file_identities_from_prior_plan_only": plan["input_files"], "new_patient_decode": False,
            "no_claimed_exclusions": ["diabetes", "treatment", "pregnancy"], "composition": "Age/sex empirical composition withheld; no target moments or empirical n in author packet", "scope": "selected unweighted released-data analytical sample, not national inference"},
        "evaluation": {"author_visible_definitions": local_binding("evaluation.json"), "generated_only_provider": local_binding("generated_provider.py"), "provider_entrypoint": "evaluate_generated(bundle,candidate,run_id,profile)", "numeric_engine": "work/chns_admission_2026-11-01/f2/evaluation/chns_f2_evaluation.py", "pure_functions": ["analyze", "compare_estimates"], "unchanged_numeric_plan": "work/chns_admission_2026-11-01/f2/analysis_plan.json", "old_entrypoints_not_to_run": ["evaluate_released", "_read_reference_files", "summarize_slots"], "old_plan_execution_section": "historical only; new global release owns schedule", "old_plan_E3_source_class": "historical Pani context; current E0/E1 exclude Pani, use evaluation.json interpretation", "reference_binding_deferred": old_state["reference_artifacts"], "reference_contents_not_read_for_binding": True, "common_evaluation_barrier": "Both cases and every condition/comparator close all scientific decisions and final attempts before reading frozen reference aggregates"},
        "information_conditions": {arm: {"packet": local_binding(f"{arm}.json"), "marginal_records": 15, "relationship_records": 0 if arm == "E0" else 4, "author_allowlist": allowlist[arm]} for arm in ("E0", "E1")},
        "source_operations": local_binding("source_operations.json"), "source_context_plan": "Analytic source-law moments preferred; no source-row replay allocated. Contextual/unavailable status retained where law-derived moments/rank functional are absent.",
        "numerical_uptake_requirement": "At least one qualified nonmarginal analytic path independently checked before release; per-author use/exclusion records for all quantitative relationships required. No promise every author adopts every constraint.",
        "applicability": {"shared_sources_with_ENSANUT": ["Lifelines/Jansen 2013"], "source_family_overlap": "Two Jansen projections share a source sample and are not independent studies; source evidence overlaps between target cases.", "unknown_individual_overlap": "Named source populations differ, but participant-level nonoverlap was not audited.", "transport": ["Lifelines selected western-European diabetes/anemia-excluded adults differs from all-status CHNS.", "Bao excludes known diabetes, retains screen-detected diabetes; its age20 boundary remains unresolved.", "MIND is older rural China and mixes prior-year BMI with later labs; mean/mode filling and tie convention remain incompletely reported.", "Plasma FPG and central-serum glucose are distinct; NGSP/IFCC scale conversion does not harmonize assays or fasting.", "Unreported age/sex composition, joint covariate law, tails, source-selection completeness and transport remain author assumptions."]},
        "support_and_validity": {"finite_population_first_second_moments_required": True, "no_exponential_of_unbounded_lognormal_linear_predictor_without_finite_moment_proof": True, "boundedness_not_empirical_target_truncation": True, "source_selection_not_clipping": True, "analysis_nonpositive_withholding_not_row_deletion": True, "source_moment_derivation_must_match_executable_law": True, "existing_checker": "work/evidence_revision_v1_2026-11-02/implementation/scientific_validity_v1.py:assess_law", "checker_scope": "Supported AST proof plus independent law/code review; unsupported declaration is not automatically biologically invalid or accepted."},
        "allocation": {"agents_per_arm": 5, "statistical_specifications_per_arm": 1, "arms": ["E0", "E1"], "final_rows_each": 3000, "final_seeds": [5101, 5102, 5103], "trial_seeds": [5201, 5202], "final_attempts": 36, "exploratory_attempts_per_construction_max": 2, "all_exploratory_attempts_max": 24, "maximum_physical_attempts": 60, "optional_revision_rounds_max": 1, "retention_valid": True, "source_trials_share_two_attempt_cap": True, "failures_consume_slots": True},
        "contrast": "For each estimand separately: mean absolute discrepancy over three final seeds per constructor, then mean over all five scheduled authors per arm; E1 minus E0. Missing endpoint/seed means incomplete; survivor means cannot establish complete arm advantage. Statistical specification displayed separately; no pooled heterogeneous score.",
        "prior_artifact_bindings": prior + [binding("work/existing_data_benchmark_2026-11-02/implementation/prepare_bundles.py")], "source_registry_materialization": "Copy only assigned E0_sources or E1_sources contents into that constructor's sources directory and the matching arm registry/evidence. Registry origin curator identifies scoped derivative content, not a new primary article.", "unresolved_release_gates": ["Independent source arithmetic and case semantic review", "Global exact seed/runtime/receipt/budget binding", "Same-information statistical comparator review", "Per-author moment derivation, law/code/support and uptake review", "Common two-case closure/evaluation wrapper and immutable release approval"], "scientific_parameters_set_by_curator": False, "new_generation_or_fit": False}
    write("case_card.json", card)
    files = sorted(p.relative_to(HERE).as_posix() for p in HERE.rglob("*") if p.is_file() and p.name != "binding_validation.json" and "__pycache__" not in p.parts)
    write("binding_validation.json", {"schema_version": 1, "status": "static_metadata_checks_passed_not_independent_approval", "shared_base_exact": e0["shared_base"] == e1["shared_base"], "shared_base_canonical_sha256": sha_bytes(canonical(e0["shared_base"])), "E0_relationship_count": len(e0.get("relationship_records", [])), "E1_relationship_count": len(e1["relationship_records"]), "case_evaluation_count": len(uses), "analytical_paths_bound": [r["evidence_id"] for r in source_ops if r["analytic_path"]["status"].startswith("implemented")], "file_bindings": [local_binding(n) for n in files], "target_report_read_or_hash": False, "patient_rows_read": False, "clinical_generation": False, "historical_files_edited": False})
    print(json.dumps({"created_files": files, "status": "metadata_bound_execution_disabled"}))

if __name__ == "__main__":
    build()
