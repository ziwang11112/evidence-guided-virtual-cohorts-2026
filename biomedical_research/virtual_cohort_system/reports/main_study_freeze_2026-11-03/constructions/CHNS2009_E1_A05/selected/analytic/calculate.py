"""Closed-form law calculations only: no row generation or random calls.

Inputs: submitted specification, admitted evidence, supplied source operation.
The generator module is neither imported nor executed.
"""
import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

CANDIDATE = Path(__file__).resolve().parents[1]
BUNDLE = CANDIDATE.parents[1]
INPUT = BUNDLE / "input"
HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False, ensure_ascii=False) + "\n", encoding="utf-8")


def marginal_moments(marginal):
    if marginal["family"] == "uniform":
        low, high = marginal["low"], marginal["high"]
        return (low + high) / 2, (high - low) ** 2 / 12
    if marginal["family"] == "lognormal":
        location, scale = marginal["log_mean"], marginal["log_sd"]
        mean = math.exp(location + scale * scale / 2)
        variance = mean * mean * math.expm1(scale * scale)
        return mean, variance
    raise ValueError("Analytical source family not implemented")


def law_moments(law):
    names = law["variables"]
    marginals = [law["marginals"][name] for name in names]
    moments = [marginal_moments(marginal) for marginal in marginals]
    means = np.array([moment[0] for moment in moments])
    variances = np.array([moment[1] for moment in moments])
    covariance = np.diag(variances)
    correlation = np.array(law["latent_correlation"])
    for i in range(len(names)):
        for j in range(i):
            families = {marginals[i]["family"], marginals[j]["family"]}
            if families == {"uniform"}:
                rank = 6 / math.pi * math.asin(correlation[i, j] / 2)
                cov = math.sqrt(variances[i] * variances[j]) * rank
            elif families == {"lognormal"}:
                cov = means[i] * means[j] * math.expm1(
                    marginals[i]["log_sd"] * marginals[j]["log_sd"] * correlation[i, j])
            else:
                raise ValueError("Mixed marginal source covariance not implemented")
            covariance[i, j] = covariance[j, i] = cov
    return means, covariance


spec = read(CANDIDATE / "model_spec.json")
p = spec["parameters"]
evidence = read(CANDIDATE / "evidence.json")
items = {item["id"]: item for item in evidence["items"]}
module_spec = importlib.util.spec_from_file_location("admitted_source_operations", INPUT / "source_operations.py")
source_operations = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(source_operations)

matrices = {"target": p["target_law"]["latent_correlation"]}
matrices.update({name: law["latent_correlation"] for name, law in p["source_laws"].items()})
matrix_checks = {}
for name, matrix in matrices.items():
    matrix = np.array(matrix)
    eigenvalues = np.linalg.eigvalsh(matrix)
    assert np.allclose(matrix, matrix.T) and np.allclose(np.diag(matrix), 1)
    assert eigenvalues.min() > 0
    matrix_checks[name] = {"eigenvalues": eigenvalues.tolist(), "positive_definite": True}

jlaw = p["source_laws"]["CTX_JANSEN_SELECTED"]
jmeans, jcov = law_moments(jlaw)
gender_p = jlaw["female_probability"]
order = [0, None, 1, 2, 3]
jfull_means = [jmeans[index] if index is not None else gender_p for index in order]
jfull_cov = np.zeros((5, 5))
for i, left in enumerate(order):
    for j, right in enumerate(order):
        if left is not None and right is not None:
            jfull_cov[i, j] = jcov[left, right]
jfull_cov[1, 1] = gender_p * (1 - gender_p)
derivation = "mathematical_properties.md: common Gaussian copula, actual marginal transforms, uniform covariance identity and independent source nuisance assumptions; calculated by analytic/calculate.py"
jcontext = {
    "role": "declared_source_population_moments", "source_context_id": "CTX_JANSEN_SELECTED",
    "selection_status": "moments_after_declared_source_selection", "weights": "equal_assumption",
    "population_selection": jlaw["population_selection"], "measurement": jlaw["measurement"],
    "gender_mapping": "female=1,male=0", "variables": ["age", "gender_binary", "BMI", "FPG", "HbA1c_percent"],
    "means": [float(x) for x in jfull_means], "covariance": jfull_cov.tolist(),
    "units": {"age": "year", "gender_binary": "1", "BMI": "kg/m^2", "FPG": "mmol/L", "HbA1c_percent": "%"},
    "assumption_ids": ["A_COPULA", "A_JANSEN_SELECTED", "A_JANSEN_BMI_TRANSPORT", "A_BMI_GLUCOSE", "A_MIND_RANK_TRANSPORT", "A_SOURCE_OPERATORS", "A_MEASUREMENT"],
    "moment_derivation": derivation,
}
assert jlaw["marginals"]["age"]["low"] > 18
assert jlaw["marginals"]["glucose"]["high"] < 7.0
assert jlaw["marginals"]["bmi"]["low"] > 0
assert jlaw["marginals"]["hba1c"]["low"] > 0
write(HERE / "jansen_moments.json", jcontext)

blaw = p["source_laws"]["CTX_BAO_ANALYZED"]
bmeans, bcov = law_moments(blaw)
bcontext = {
    "role": "declared_source_population_moments", "source_context_id": "CTX_BAO_ANALYZED",
    "selection_status": "moments_after_declared_source_selection", "weights": "equal_assumption",
    "population_selection": blaw["population_selection"], "measurement": blaw["measurement"],
    "variables": ["FPG", "HbA1c_percent"], "means": bmeans.tolist(), "covariance": bcov.tolist(),
    "units": {"FPG": "mmol/L", "HbA1c_percent": "%"},
    "assumption_ids": ["A_COPULA", "A_BAO_SCENARIO", "A_MIND_RANK_TRANSPORT", "A_SOURCE_OPERATORS", "A_MEASUREMENT"],
    "moment_derivation": derivation + "; lognormal covariance m_i*m_j*expm1(s_i*s_j*rho_ij)",
}
write(HERE / "bao_moments.json", bcontext)
mlaw = p["source_laws"]["CTX_MIND_ANALYZED"]
mrho = mlaw["latent_correlation"][0][1]
rank_value = 6 / math.pi * math.asin(mrho / 2)
rank_artifact = {
    "source_context_id": "CTX_MIND_ANALYZED", "population_selection": mlaw["population_selection"],
    "measurement": mlaw["measurement"], "role": "law_specific_rank_derivation",
    "latent_normal_correlation": mrho, "calculated_spearman": rank_value,
    "formula": "12*E[Phi(Z1)*Phi(Z2)]-3 = 6/pi*asin(rho/2)",
    "proof": "mathematical_properties.md; independent-normal difference orthant derivation",
    "ties": "Continuous population has zero tie probability; original sample imputation/ties unavailable. Finite generated diagnostic ranks, if inspected by controller, use average ties.",
    "source_operation_evaluate_used": False,
    "reason": "Supplied ordinary-moment operation correctly does not calculate Spearman. This separate analytical law-specific proof does, and is submitted for controller review without claiming prior independent approval.",
    "independent_review_status": "not_performed_by_author",
}
write(HERE / "mind_rank.json", rank_artifact)
results = []
for evidence_id, context in [("R_JANSEN_BMI", jcontext), ("R_JANSEN_FPG", jcontext), ("R_BAO_PEARSON", bcontext)]:
    record = source_operations.evaluate(evidence_id, context)
    record["reported_value"] = items[evidence_id]["estimate"]
    record["raw_difference"] = record["calculated_value"] - record["reported_value"]
    record["reported_uncertainty"] = items[evidence_id]["uncertainty"]
    record["fit_interpretation"] = "Fitted source-scenario constraint, not independent validation" if evidence_id == "R_JANSEN_BMI" else "Unfitted cross-context discrepancy retained; no tolerance or precision weighting"
    results.append(record)
results.append({"evidence_id": "R_MIND_SPEARMAN", "source_context_id": "CTX_MIND_ANALYZED",
                "calculated_value": rank_value, "reported_value": items["R_MIND_SPEARMAN"]["estimate"],
                "raw_difference": rank_value - items["R_MIND_SPEARMAN"]["estimate"],
                "unit": "1", "classification": "author_law_specific_analytic_rank_functional",
                "strict_replay": "not_computable", "source_operation_evaluate_used": False,
                "fit_interpretation": "Fitted source rank constraint under an assumed continuous Gaussian copula; not independent validation",
                "reported_uncertainty": items["R_MIND_SPEARMAN"]["uncertainty"]})

target = p["target_law"]
assert np.allclose(np.array(target["latent_correlation"])[1:, 1:], np.array(jlaw["latent_correlation"])[1:, 1:])
assert target["latent_correlation"][2][3] == blaw["latent_correlation"][0][1] == mrho
for name in ["glucose", "hba1c"]:
    assert target["marginals"][name] == mlaw["marginals"][name]
assert target["marginals"]["age"] == {"family": "discrete_uniform", "low": 35, "high": 74}
assert p["n_rows"] == 3000 and 0 < target["female_probability"] < 1
target_moments = {}
for name in ["bmi", "glucose", "hba1c"]:
    mean, variance = marginal_moments(target["marginals"][name])
    target_moments[name] = {"law_mean": mean, "law_variance": variance, "law_second_moment": mean * mean + variance,
                            "interpretation": "Model consequence only; no target measurements or reference comparison"}
bao_quantiles = {}
from statistics import NormalDist
for name, prefix in [("glucose", "M_B_FPG_"), ("hba1c", "M_B_HBA1C_PERCENT_")]:
    marginal = blaw["marginals"][name]
    bao_quantiles[name] = []
    for quantile, suffix in [(0.25, "Q1"), (0.5, "MEDIAN"), (0.75, "Q3")]:
        predicted = math.exp(marginal["log_mean"] + marginal["log_sd"] * NormalDist().inv_cdf(quantile))
        bao_quantiles[name].append({"q": quantile, "calculated_value": predicted,
                                    "reported_value": items[prefix + suffix]["estimate"],
                                    "raw_difference": predicted - items[prefix + suffix]["estimate"]})
report = {"calculation_mode": "deterministic_closed_form_finite_dimensional_algebra", "rows_produced": 0,
    "generator_imported_or_executed": False, "monte_carlo": False, "numerical_quadrature": False,
    "inputs": {"model_spec_sha256": hashlib.sha256((CANDIDATE / "model_spec.json").read_bytes()).hexdigest(),
               "evidence_sha256": hashlib.sha256((CANDIDATE / "evidence.json").read_bytes()).hexdigest(),
               "source_operations_sha256": hashlib.sha256((INPUT / "source_operations.py").read_bytes()).hexdigest()},
    "source_results": results, "latent_matrix_checks": matrix_checks,
    "jansen_support": jlaw["marginals"], "source_target_shared_biomarker_copula_checked": True,
    "target_law_finite_moments": target_moments, "bao_approximate_quantile_checks": bao_quantiles,
    "limitations": ["Numerical agreement with an installed source constraint is algebraic, not independent validation.",
                    "Jansen and Bao unfit discrepancies are retained without revision.",
                    "Source law and context assumptions are not certified by arithmetic.",
                    "Population ranks do not recover source ties/imputation or exact sample statistics."]}
write(HERE / "source_results.json", report)

operations = read(INPUT / "source_operations.json")["operations"]
assert {operation["evidence_id"] for operation in operations} == {record["evidence_id"] for record in results}
result_by_id = {record["evidence_id"]: record for record in results}
uptake = []
for operation in operations:
    eid = operation["evidence_id"]
    context = operation["source_context_id"]
    constrained = eid in {"R_JANSEN_BMI", "R_MIND_SPEARMAN"}
    paths = ["model_spec.json#/parameters/source_laws/" + context, "analytic/calculate.py", "analytic/source_results.json", "mathematical_properties.md"]
    if constrained:
        paths += ["model_spec.json#/parameters/dependence_derivation", "model_spec.json#/parameters/target_law/latent_correlation"]
    extra = {"R_JANSEN_BMI": "analytic/jansen_moments.json", "R_JANSEN_FPG": "analytic/jansen_moments.json",
             "R_BAO_PEARSON": "analytic/bao_moments.json", "R_MIND_SPEARMAN": "analytic/mind_rank.json"}[eid]
    reason = {
        "R_JANSEN_BMI": "Constrains source BMI-H raw correlation only after explicit uniform-marginal and independent-nuisance assumptions; that derived rank dependence is transported, not the raw regression slope.",
        "R_JANSEN_FPG": "Analytic check of the separate age/gender-adjusted glucose projection under the common biomarker copula. Its discrepancy is retained; the healthier plasma source does not replace the serum rank constraint and no combined BMI-plus-glucose coefficient equation is created.",
        "R_BAO_PEARSON": "Analytic cross-context check with Bao lognormal source-pair margins. The Pearson discrepancy is retained; no source/target glucose assay conversion or pooled calibration is justified.",
        "R_MIND_SPEARMAN": "Constrains the Gaussian copula via the law-specific rank proof; qualified continuous-source scenario and explicit target transport only. The supplied ordinary-moment operator is not misused for Spearman.",
    }[eid]
    uptake.append({"operation_id": eid, "operation_id_convention": "source_operations.json indexes the operation by evidence_id and supplies no distinct operation_id",
        "source_id": items[eid]["source_id"], "evidence_id": eid, "source_context_id": context,
        "use": "model_constraint" if constrained else "analytic_check", "artifact_paths": paths + [extra],
        "source_population_selection": p["source_laws"][context]["population_selection"],
        "measurement_assumptions": p["source_laws"][context]["measurement"] + "; " + reason,
        "source_uncertainty_treatment": "Point-scenario only. No reported SE; Jansen printed interval confidence level unconfirmed. Marginal SDs describe individuals, not regression uncertainty. No CI-to-SD conversion, precision weight, or tolerance.",
        "cross_source_overlap": "Jansen's two regressions and all its margins share one source family; each Bao/MIND relationship shares its own marginal population. Named cohort families are distinct but participant overlap is unverified. Records are not pooled as independent precision information.",
        "identifies": "One source projection or correlation point under its reported estimand; it does not identify the complete joint distribution, target coefficient, conditional age effect, or individual measurements.",
        "construction_assumptions": [a["id"] for a in spec["assumptions"] if a["id"] in {"A_COPULA", "A_JANSEN_SELECTED", "A_JANSEN_BMI_TRANSPORT", "A_MIND_RANK_TRANSPORT", "A_BAO_SCENARIO", "A_SOURCE_OPERATORS", "A_MEASUREMENT", "A_BMI_GLUCOSE", "A_UNCERTAINTY"}],
        "calculated_value": result_by_id[eid]["calculated_value"], "source_point": items[eid]["estimate"],
        "raw_difference": result_by_id[eid]["raw_difference"], "reason": reason,
        "strict_source_replay": "not_computable_not_allocated", "target_as_source_comparison": "unavailable"})
write(CANDIDATE / "numerical_uptake.json", {"records": uptake})
print(json.dumps({"rows_produced": 0, "source_results": [{k: record[k] for k in ["evidence_id", "calculated_value", "reported_value", "raw_difference"]} for record in results], "positive_definite_matrices": list(matrix_checks)}, indent=2))
