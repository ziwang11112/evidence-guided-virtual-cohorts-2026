"""Contract and analytic-result checks only. Generator is parsed, never imported."""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import json
from pathlib import Path

candidate = Path(__file__).resolve().parent
bundle = candidate.parent.parent
session = bundle.parent
interface_root = Path("D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system")
sys.path.insert(0, str(interface_root))
from cohort_harness import contracts, lifecycle, semantic_feedback_v1

read = lifecycle.read_json
task, evidence, spec = read(bundle/"task.json"), read(candidate/"evidence.json"), read(candidate/"model_spec.json")
contracts.validate_task(task)
evidence_ids = contracts.validate_evidence(evidence, task)
contracts.validate_spec(spec, evidence_ids)
contracts.validate_input(None, task)
lifecycle.validate_program(candidate/"generator.py")
tree = ast.parse((candidate/"generator.py").read_text(encoding="utf-8"))
assert all(isinstance(n, (ast.Expr, ast.Import, ast.ImportFrom, ast.FunctionDef)) for n in tree.body)
assert {n.names[0].name for n in tree.body if isinstance(n, ast.Import)} == {"numpy","pandas"}
assert spec["parameters"]["n_rows"] == task["n_rows"] == 3000
assert spec["parameters"]["output_columns"] == [c["name"] for c in task["columns"]]
assert read(candidate/"numerical_uptake.json") == {"records":[]}
assert read(bundle/"sources"/"evidence_packet.json")["relationship_records"] == []
analytic = read(candidate/"analytic_properties.json")
assert analytic["spec_sha256"] == lifecycle.sha256(candidate/"model_spec.json")
assert analytic["generator_sha256"] == lifecycle.sha256(candidate/"generator.py")
assert analytic["covariance_min_eigenvalue"] > 0
assert analytic["residual_covariance_min_eigenvalue"] > 0
assert analytic["source_marginal_scale_recovery_max_abs_mean_error"] < 1e-10
assert analytic["source_marginal_scale_recovery_max_abs_sd_error"] < 1e-10
preflight = semantic_feedback_v1.preflight(bundle, "initial")
assert len(preflight["checks"]) == len(evidence["items"])
assert all(item["semantic_status"]=="unavailable" for item in preflight["checks"])
report = {
    "status":"pass", "generator_imported":False, "generator_executed":False,
    "rows_generated":0,"exploratory_attempts_consumed_by_author":0,
    "checks":["task/evidence/spec/input contracts", "AST-only synchronous three-positional-argument ABI", "3000-row parameter and exact output schema", "E0 operation list empty", "analytic report binds current model and generator bytes", "positive definite analytic residual and full covariance", "analytic normalization recovers chosen means and SDs", "semantic preflight: every source comparison unavailable"],
    "source_comparison_count":len(preflight["checks"]),
    "limitations":["No row-level output or runtime behavior was tested.","No source-population replay or empirical target validation was performed.","Contract and algebraic checks do not validate scientific transport or joint assumptions."],
    "hashes":{"generator.py":lifecycle.sha256(candidate/"generator.py"),"model_spec.json":lifecycle.sha256(candidate/"model_spec.json"),"evidence.json":lifecycle.sha256(candidate/"evidence.json"),"analytic_properties.py":lifecycle.sha256(candidate/"analytic_properties.py")}
}
(candidate/"static_validation.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
checks = {"scope":"source_only","records":[
    {"name":"static_contracts","status":"pass","detail":"Task/evidence/model and ABI checked without generator import; see static_validation.json."},
    {"name":"analytic_law_properties","status":"pass","detail":"Exact finite demographic sums and Gaussian MGFs establish model moments and population OLS; retained script executed without RNG, generator import or generated rows. These are scenario properties, not source validation."},
    {"name":"source_semantics_preflight","status":"pass","detail":"All 32 source comparisons are explicitly unavailable; evidence and feedback-recipe hashes match the semantic sidecar."},
    {"name":"generator_execution","status":"not_computable","detail":"Controller-owned isolated execution has not been requested or performed by the author."},
    {"name":"source_population_replay","status":"not_computable","detail":"Not supplied. Target table cannot stand in for a source population."},
    {"name":"clinical_target_validation","status":"not_computable","detail":"Outside author allocation; no target empirical values read or fitted."}
],"artifacts":[{"path":name,"sha256":lifecycle.sha256(candidate/name)} for name in ["analytic_properties.py","analytic_properties.json","validate_static.py","static_validation.json"]]}
(candidate/"checks.json").write_text(json.dumps(checks,indent=2,allow_nan=False)+"\n",encoding="utf-8")
state = lifecycle._state(bundle.resolve(),candidate.resolve(),"candidates/initial")
final_preflight = semantic_feedback_v1.preflight(bundle,"initial")
final = {"status":"pass","candidate":"candidates/initial","route":state["route"],"candidate_files":state["candidate_files"],"freeze_created":False,"generator_imported":False,"generator_executed":False,"source_semantic_unavailable_count":len(final_preflight["checks"]),"limitations":"Static contracts, analytic law properties and source-unavailability declarations only."}
(session/"validation_summary.json").write_text(json.dumps(final,indent=2,allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps(final,indent=2))
