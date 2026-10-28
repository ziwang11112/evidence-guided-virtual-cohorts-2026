"""Re-run candidate checks and add invented structural-identification checks."""
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
from scipy.stats import gamma as gamma_dist
from scipy.stats import lognorm

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
runpy.run_path(str(HERE / "check_final.py"))
results = json.loads((HERE / "artificial_checks.json").read_text(encoding="utf-8"))
spec = json.loads((HERE / "model_spec.json").read_text(encoding="utf-8"))
ledger = json.loads((HERE / "evidence.json").read_text(encoding="utf-8"))
p = spec["parameters"]
rho = 2*np.sin(np.pi*p["partial_spearman_bmi_hdl"]/6)

def add(name, passed, details):
    results["tests"].append({"name": name, "passed": bool(passed), "details": details})
    if not passed:
        raise AssertionError(name)

identities = []
for file in ["generator.py", "model_spec.json"]:
    h_initial = hashlib.sha256((RUN/"initial"/file).read_bytes()).hexdigest()
    h_final = hashlib.sha256((HERE/file).read_bytes()).hexdigest()
    identities.append({"file": file, "initial_sha256": h_initial, "final_sha256": h_final, "byte_identical": h_initial == h_final})
add("exact_generator_and_spec_noop", all(x["byte_identical"] for x in identities), identities)

audit = [json.loads(line) for line in (RUN/"literature/audit.jsonl").read_text(encoding="utf-8").splitlines()]
registry = {(x["artifact"]["session_relative_path"], x["artifact"]["sha256"]) for x in audit if x.get("type") == "artifact_approved" and x.get("status") == "accepted"}
retrieval_checks = []
for search in ledger["retrieval_summary"]["revision_searches"]:
    a = search["artifact"]
    h = hashlib.sha256((RUN/a["path"]).read_bytes()).hexdigest()
    ok = h == a["sha256"] and (a["path"].removeprefix("literature/"), h) in registry
    retrieval_checks.append({"path": a["path"], "registered_and_hash_verified": ok})
add("revision_search_artifact_registration", all(x["registered_and_hash_verified"] for x in retrieval_checks), retrieval_checks)

# X=standardized BMI; Y=age-residualized standardized log HDL; C=an invented
# omitted adjustment variable. X=a*C+sqrt(1-a^2)*U and
# Y=d*C+sqrt(1-d^2)*(rho*U+sqrt(1-rho^2)*E), with independent normal C,U,E.
# This preserves standard normal marginals and a common residual correlation.
# It is a counterexample under the model's assumed bridge, NOT recovery of
# the article's unspecified procedure for calculating partial Spearman ranks.
covariance_cases = []
for label, a, d in [
    ("no_omitted_covariation", 0.0, 0.0),
    ("BMI_explained_by_omitted_factor", 0.6, 0.0),
    ("positive_shared_factor", 0.6, 0.4),
    ("opposite_shared_factor", 0.6, -0.4),
]:
    marginal_r = a*d + np.sqrt((1-a*a)*(1-d*d))*rho
    recovered_partial_r = (marginal_r-a*d)/np.sqrt((1-a*a)*(1-d*d))
    residual_rank = (6/np.pi)*np.arcsin(recovered_partial_r/2)
    matrix = np.array([[1,a,marginal_r],[a,1,d],[marginal_r,d,1]])
    slopes = {}
    contrasts = {}
    for sex in ["1", "2"]:
        m = p["reference_hdl_mean_mgdl"][sex]
        sd = p["reference_hdl_sd_mgdl"][sex]
        g = p["log_hdl_age_slope_per_year"][sex]
        v = np.log1p((sd/m)**2)-(g*p["reference_age_sd_years"])**2
        beta = marginal_r*np.sqrt(v)/p["reference_bmi_sd"][sex]
        slopes[sex] = float(beta)
        contrasts[sex] = float(np.exp(beta*(40-25)))
    covariance_cases.append({
        "scenario": label, "correlation_BMI_C": a, "correlation_logHDL_C": d,
        "BMI_residual_SD_fraction": float(np.sqrt(1-a*a)),
        "logHDL_residual_SD_fraction": float(np.sqrt(1-d*d)),
        "marginal_latent_correlation_after_omitting_C": float(marginal_r),
        "partial_latent_correlation_given_C": float(recovered_partial_r),
        "Spearman_of_Gaussian_residuals_given_C": float(residual_rank),
        "minimum_covariance_eigenvalue": float(np.linalg.eigvalsh(matrix).min()),
        "logHDL_BMI_slopes_when_C_unavailable": slopes,
        "conditional_mean_ratio_BMI40_vs25": contrasts
    })
add("F1_omitted_covariance_nonidentification_demonstration", all(x["minimum_covariance_eigenvalue"] > 0 and abs(x["Spearman_of_Gaussian_residuals_given_C"]+0.26) < 1e-12 for x in covariance_cases), {
    "scope": "Invented Gaussian constructions, arbitrary scenario values with no evidence-based weights; all have the same Gaussian marginal predictor/outcome scales and same Gaussian-residual rank association under the assumed bridge. They yield different HDL-on-BMI relations when C is unavailable. This does not reproduce or validate the published partial Spearman calculation.",
    "cases": covariance_cases
})

age_cases = []
for sex, young, old in [("1",1.27,1.42),("2",1.45,1.50)]:
    log_contrast = np.log(old/young)
    for conditional_fraction in [0.0, 0.5, 1.0, 1.5]:
        slope = conditional_fraction*p["log_hdl_age_slope_per_year"][sex]
        hypothetical_group_offset = (1-conditional_fraction)*log_contrast
        reconstructed_old = young*np.exp(slope*35+hypothetical_group_offset)
        age_cases.append({
            "sex": sex, "fraction_of_log_group_contrast_assigned_to_conditional_age": conditional_fraction,
            "assumed_conditional_log_age_slope": float(slope),
            "hypothetical_old_vs_young_group_composition_offset": float(hypothetical_group_offset),
            "source_old_mean_mmolL": old, "reconstructed_old_group_mean_mmolL": float(reconstructed_old),
            "fixed_BMI_mean_ratio_age20_vs62": float(np.exp(slope*(20-62)))
        })
add("F2_age_contrast_decomposition_nonidentification", all(abs(x["source_old_mean_mmolL"]-x["reconstructed_old_group_mean_mmolL"]) < 1e-12 for x in age_cases), {
    "scope": "Invented decomposition only. Arbitrary conditional-age fractions plus corresponding composition/standardization offsets preserve the source endpoint means exactly. Fractions have no assigned probabilities and are not confidence limits. A zero conditional slope does not deny the observed cross-group means, nor does this exercise support choosing zero.",
    "cases": age_cases
})

tail_cases = []
for sex in ["1", "2"]:
    m = p["reference_hdl_mean_mgdl"][sex]
    sd = p["reference_hdl_sd_mgdl"][sex]
    g = p["log_hdl_age_slope_per_year"][sex]
    tau2 = np.log1p((sd/m)**2)
    v = tau2-(g*10)**2
    beta = rho*np.sqrt(v)/p["reference_bmi_sd"][sex]
    residual2 = (1-rho*rho)*v
    mu = np.log(m)-tau2/2+beta*(25-p["reference_bmi_mean"][sex])+g*(60-62)
    conditional_mean = np.exp(mu+residual2/2)
    cv2 = np.expm1(residual2)
    conditional_variance = conditional_mean**2*cv2
    log_family = lognorm(s=np.sqrt(residual2),scale=np.exp(mu))
    gamma_family = gamma_dist(a=1/cv2,scale=conditional_mean*cv2)
    tail_cases.append({
        "sex": sex, "invented_bmi": 25, "invented_age": 60,
        "shared_mean": float(conditional_mean), "shared_variance": float(conditional_variance),
        "lognormal_mean": float(log_family.mean()), "gamma_mean": float(gamma_family.mean()),
        "lognormal_variance": float(log_family.var()), "gamma_variance": float(gamma_family.var()),
        "lognormal_1st_99th_percentiles": log_family.ppf([0.01,0.99]).tolist(),
        "gamma_1st_99th_percentiles": gamma_family.ppf([0.01,0.99]).tolist(),
        "lognormal_probability_above_100": float(log_family.sf(100)),
        "gamma_probability_above_100": float(gamma_family.sf(100))
    })
add("F3_positive_families_same_moments_different_tails", all(np.isclose(x["lognormal_mean"],x["gamma_mean"]) and np.isclose(x["lognormal_variance"],x["gamma_variance"]) for x in tail_cases), {
    "scope": "Analytic invented-input comparison. Both positive-support families have identical conditional first two moments, but different tails. No source or target tail data are used to select a family. The deployed final model remains lognormal.",
    "cases": tail_cases
})

results["target_outcome_validation_run"] = False
results["structural_scenarios_are_not_probability_bounds"] = True
results["generator_and_spec_numerically_unchanged"] = True
results["remaining_budget"] = {"queries":0,"downloads":5}
results["passed"] = all(x["passed"] for x in results["tests"])
(HERE/"artificial_checks.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
print(json.dumps({"passed":results["passed"],"tests":len(results["tests"]),"covariance_cases":covariance_cases,"age_cases":age_cases,"tail_cases":tail_cases},indent=2))
