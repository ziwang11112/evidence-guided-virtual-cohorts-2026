"""Deterministic analytic and static checks; no generator import or execution.

Run this file from its retained candidate location. No RNG is used, no
individual table is read or written, and no sampled/quadrature rows are made.
"""
from pathlib import Path
import ast
import hashlib
import json
import math
from statistics import NormalDist

CANDIDATE = Path(__file__).resolve().parent
BUNDLE = CANDIDATE.parent.parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (CANDIDATE / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


task = read(BUNDLE / "task.json")
spec = read(CANDIDATE / "model_spec.json")
evidence = read(CANDIDATE / "evidence.json")
packet = read(BUNDLE / "input" / "reported_packet.json")
source_packet = read(BUNDLE / "sources" / "evidence_packet.json")
p = spec["parameters"]
assert source_packet == packet
assert packet["arm"] == "E0" and packet["relationship_records"] == []
assert evidence == read(BUNDLE / "input" / "evidence.json")
assert p["n_rows"] == task["n_rows"] == 3000
assert p["age_min"] == 35 and p["age_max"] == 74
assert 0 < p["female_probability"] < 1
assert p["female_probability"] == 2049 / 3547
assert set(spec["parameter_provenance"]) == set(p)
evidence_by_id = {item["id"]: item for item in evidence["items"]}
for variable, source_key in [("bmi", "M_M_BMI"), ("glucose", "M_M_FSG"), ("hba1c", "M_M_HBA1C_PERCENT")]:
    assert p["marginals"][variable]["mean"] == evidence_by_id[source_key + "_MEAN"]["estimate"]
    assert p["marginals"][variable]["individual_sd"] == evidence_by_id[source_key + "_SD"]["estimate"]
    assert evidence_by_id[source_key + "_SD"]["kind"] == "sd"
    assert evidence_by_id[source_key + "_SD"]["uncertainty"] == {"kind": "not_reported"}

syntax = ast.parse((CANDIDATE / "generator.py").read_text(encoding="utf-8"))
functions = [node for node in syntax.body if isinstance(node, ast.FunctionDef)]
assert len(functions) == 1 and functions[0].name == "generate"
arguments = functions[0].args
assert [a.arg for a in arguments.args] == ["observed", "spec", "seed"]
assert not arguments.vararg and not arguments.kwarg and not arguments.kwonlyargs
assert not arguments.posonlyargs
assert all(isinstance(node, (ast.Import, ast.FunctionDef)) or
           (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str))
           for node in syntax.body)
assert {alias.name for node in syntax.body if isinstance(node, ast.Import) for alias in node.names} == {"numpy", "pandas"}
calls = [node for node in ast.walk(functions[0]) if isinstance(node, ast.Call)]
for node in calls:
    if isinstance(node.func, ast.Name):
        assert node.func.id not in {"eval", "exec", "open", "__import__"}
    if isinstance(node.func, ast.Attribute):
        assert node.func.attr not in {"clip", "read_csv", "to_csv", "load", "save", "normal"}

registry = read(BUNDLE / "registry.json")
source_hash_checks = []
for artifact in registry["artifacts"]:
    actual = sha(BUNDLE / artifact["path"])
    assert actual == artifact["sha256"]
    source_hash_checks.append({"source_id": artifact["source_id"], "path": artifact["path"], "sha256": actual, "status": "pass"})

plan = read(CANDIDATE / "whole_cohort_feedback.json")
sidecar = read(CANDIDATE / "source_semantics_v1.json")
assert plan["population"] == task["population"]
assert all(x["status"] == "not_computable" and x["operator"] is None for x in plan["checks"])
assert {x["evidence_id"] for x in plan["checks"]} == set(evidence_by_id)
assert {x["check_id"] for x in sidecar["bindings"]} == {x["id"] for x in plan["checks"]}
assert sidecar["evidence_sha256"] == sha(CANDIDATE / "evidence.json")
assert sidecar["recipe_sha256"] == sha(CANDIDATE / "whole_cohort_feedback.json")
assert all(x["uncertainty_role"] == "not_reported" for x in sidecar["bindings"])
assert read(CANDIDATE / "numerical_uptake.json") == {"records": []}

normal = NormalDist()
law_margins = {}
for variable, margin in p["marginals"].items():
    m, s = margin["mean"], margin["individual_sd"]
    assert m > 0 and s > 0 and math.isfinite(m) and math.isfinite(s)
    sigma2 = math.log1p((s / m) ** 2)
    mu = math.log(m) - sigma2 / 2
    first = math.exp(mu + sigma2 / 2)
    second = math.exp(2 * mu + 2 * sigma2)
    variance = math.expm1(sigma2) * math.exp(2 * mu + sigma2)
    assert math.isclose(first, m, rel_tol=1e-12)
    assert math.isclose(second, m * m + s * s, rel_tol=1e-12)
    assert math.isclose(variance, s * s, rel_tol=1e-12)
    law_margins[variable] = {
        "unit": margin["unit"], "mu_log": mu, "variance_log": sigma2,
        "mean": first, "individual_variance": variance, "second_raw_moment": second,
        "fourth_raw_moment": math.exp(4 * mu + 8 * sigma2),
        "population_quantiles": {str(q): math.exp(mu + math.sqrt(sigma2) * normal.inv_cdf(q)) for q in (0.1, 0.5, 0.9)},
        "moment_identity_check": "pass",
    }
count = p["age_max"] - p["age_min"] + 1
age_mean = (p["age_min"] + p["age_max"]) / 2
age_var = (count * count - 1) / 12
f = p["female_probability"]
law_margins["age"] = {"unit": "year", "mean": age_mean, "individual_variance": age_var, "second_raw_moment": age_var + age_mean * age_mean}
law_margins["female"] = {"unit": "1", "mean": f, "individual_variance": f * (1 - f), "second_raw_moment": f}

analyses = read(BUNDLE / "input" / "analysis_definitions.json")
projections = []
for use in analyses["uses"]:
    diagonal = [law_margins[name]["individual_variance"] for name in use["predictors"]]
    assert all(x > 0 and math.isfinite(x) for x in diagonal)
    projections.append({
        "id": use["id"], "predictors": use["predictors"], "outcome": use["outcome"],
        "term": use["term"], "unit": use["unit"],
        "predictor_covariance_diagonal": diagonal,
        "predictor_covariance_off_diagonals": "All zero under A_INDEPENDENCE; not measured facts.",
        "outcome_predictor_covariance_vector": [0.0 for _ in diagonal],
        "population_focal_coefficient": 0.0,
        "population_intercept": p["marginals"]["hba1c"]["mean"],
        "interpretation": "Algebraically fixed by the assumed product law; not a source or target-reference estimate.",
    })

analytic = {
    "scope": "deterministic_moments_of_declared_probability_law_only",
    "method": "Closed-form normal MGF, discrete-uniform/Bernoulli formulas, and diagonal covariance least-squares identity. Normal quantiles use statistics.NormalDist.inv_cdf; no integration, quadrature, Monte Carlo or generated rows.",
    "generator_imported": False, "generator_executed": False, "rows_produced": False,
    "inputs": {"model_spec.json": sha(CANDIDATE / "model_spec.json"), "evidence.json": sha(CANDIDATE / "evidence.json"), "generator.py": sha(CANDIDATE / "generator.py"), "analysis_definitions.json": sha(BUNDLE / "input" / "analysis_definitions.json")},
    "marginals": law_margins, "population_projections": projections,
    "source_replay": "unavailable", "source_fit_claim": False, "target_reference_access": False,
    "finite_first_second_moments": True,
}
write("analytical_results.json", analytic)
write("static_audit.json", {
    "scope": "author_static_representation_and_formula_checks_only",
    "generator_imported": False, "generator_executed": False, "rows_produced": False,
    "checks": {
        "allowed_source_bytes_match_registry": source_hash_checks,
        "reported_packet_equals_registered_packet": "pass",
        "copied_evidence_preserves_items_and_SD_roles": "pass",
        "E0_nonmarginal_uptake_is_empty": "pass",
        "generator_AST_positional_signature": "pass",
        "generator_no_top_level_execution_or_file_IO": "pass",
        "parameters_match_declared_task_and_source_anchors": "pass",
        "all_source_comparisons_unavailable": "pass",
        "sidecar_coverage_and_hashes": "pass",
        "lognormal_moment_identities": "pass",
        "positive_population_predictor_variances": "pass",
    },
    "bindings": {"generator.py": sha(CANDIDATE / "generator.py"), "model_spec.json": sha(CANDIDATE / "model_spec.json"), "analytical_audit.py": sha(Path(__file__)), "analytical_results.json": sha(CANDIDATE / "analytical_results.json")},
    "limitations": ["No actual DataFrame, runtime imports, finite-sample rank or execution is tested.", "No source-context or target-reference numerical validation is performed.", "Artifact contract validation and semantic preflight are separate coordinator-visible operations."],
})
write("checks.json", {
    "scope": "source_only",
    "records": [
        {"name": "static_contract_and_provenance_audit", "status": "pass", "detail": "Retained analytical_audit.py actually checked Python AST/signature, admitted source hashes, unchanged source evidence and SD roles, task/spec constants, absent E0 relationships, and source-sidecar hash/coverage using no rows. Results in static_audit.json. This is not generator execution or full harness validation."},
        {"name": "analytic_probability_law", "status": "pass", "detail": "Closed-form lognormal and discrete moment identities were actually evaluated without generator import, random draws, numerical integration or tables. All population predictor variances are positive; the three population focal OLS coefficients equal zero because independence was assumed. See analytical_results.json and mathematical_properties.md."},
        {"name": "source_statistic_replay", "status": "not_computable", "detail": "No source-population table/replay supplied. All whole-cohort and semantic source checks are unavailable. Parameterizing a target-law margin by source values is not source replay."},
        {"name": "generator_execution_and_output_contract", "status": "not_computable", "detail": "The author has not executed or imported the generator and has not produced rows. The coordinator owns frozen execution and actual output checks."},
        {"name": "target_scientific_validation", "status": "not_computable", "detail": "No target values or results supplied or accessed. The product assumption fixes model projections but cannot validate target associations."},
    ],
    "artifacts": [{"path": name, "sha256": sha(CANDIDATE / name)} for name in ["analytical_audit.py", "analytical_results.json", "static_audit.json", "mathematical_properties.md", "source_use.json", "numerical_uptake.json"]],
})
print(json.dumps({"analytic_and_static_status": "pass", "generator_imported": False, "generator_executed": False, "rows_produced": False, "source_checks": "all_unavailable", "population_coefficients": {x["id"]: x["population_focal_coefficient"] for x in projections}}))
