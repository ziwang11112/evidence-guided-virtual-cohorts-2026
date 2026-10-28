"""Run source-only and invented-input checks; writes artificial_checks.json."""
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
spec = json.loads((HERE / "model_spec.json").read_text(encoding="utf-8"))
ledger = json.loads((HERE / "evidence.json").read_text(encoding="utf-8"))
module_spec = importlib.util.spec_from_file_location("candidate", HERE / "generator.py")
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)
generate = module.generate
p = spec["parameters"]
results = {"scope": "Implementation, invented inputs, and external source consistency only; no target HDL or outcome-derived test", "tests": []}

def record(name, passed, details):
    results["tests"].append({"name": name, "passed": bool(passed), "details": details})
    if not passed:
        raise AssertionError(name)

eids = {x["id"] for x in ledger["evidence"]}
aids = {x["id"] for x in spec["assumptions"]}
sids = {x["id"] for x in ledger["sources"]}
valid = set(p) == set(spec["parameter_provenance"])
for entry in spec["parameter_provenance"].values():
    valid &= bool(entry["evidence_ids"] or entry["assumption_ids"])
    valid &= set(entry["evidence_ids"]).issubset(eids)
    valid &= set(entry["assumption_ids"]).issubset(aids)
valid &= all(x["source_id"] in sids for x in ledger["evidence"])
record("provenance_ids_and_parameter_coverage", valid, {"parameters": len(p), "sources": len(sids), "evidence_items": len(eids)})

audit = [json.loads(line) for line in (RUN / "literature/audit.jsonl").read_text(encoding="utf-8").splitlines()]
accepted = {(x["artifact"]["session_relative_path"], x["artifact"]["sha256"]) for x in audit if x.get("type") == "artifact_approved" and x.get("status") == "accepted"}
checked = []
for source in ledger["sources"]:
    for a in source["approved_artifacts"]:
        digest = hashlib.sha256((RUN / a["path"]).read_bytes()).hexdigest()
        match = digest == a["sha256"] and (a["path"].removeprefix("literature/"), digest) in accepted
        checked.append({"path": a["path"], "hash_and_registration_match": match})
record("approved_source_hashes_and_session_registration", all(x["hash_and_registration_match"] for x in checked), checked)

toy = pd.DataFrame([
    {"row_id": f"invented_{s}_{b}_{a}", "bmi": b, "age": a, "sex": s}
    for s in [1, 2] for b in [14.1, 25.0, 40.0, 77.5] for a in [20, 79]
], index=np.arange(80, 96)[::-1])
before = toy.copy(deep=True)
global_state_before = np.random.get_state()
out = generate(toy, spec, 48291)
global_state_after = np.random.get_state()
record("input_preservation_and_output_contract", toy.equals(before) and out.iloc[:, :4].equals(before) and list(out.columns) == ["row_id", "bmi", "age", "sex", "hdl"], {"rows": len(out), "nonstandard_index_preserved": out.index.equals(toy.index)})
record("finite_positive_on_invented_boundary_grid", np.isfinite(out.hdl).all() and (out.hdl > 0).all(), {"bmi_range": [14.1, 77.5], "age_range": [20, 79], "min_hdl": float(out.hdl.min()), "max_hdl": float(out.hdl.max())})
same = generate(toy, spec, 48291)
different = generate(toy, spec, 48292)
record("local_seed_reproducibility_and_variability", out.equals(same) and not np.array_equal(out.hdl, different.hdl), {"same_seed_equal": out.equals(same), "different_seed_changes_hdl": not np.array_equal(out.hdl, different.hdl)})
record("global_rng_unchanged", all(np.array_equal(a, b) for a, b in zip(global_state_before, global_state_after)), "Compared NumPy legacy global RNG state before and after generator call")
record("empty_input", generate(toy.iloc[:0], spec, 1).shape == (0, 5), "Empty valid input returns zero rows with the required five columns")
rejections = []
for column, bad in [("bmi", -1), ("age", np.nan), ("sex", 3)]:
    case = toy.copy()
    case.iloc[0, case.columns.get_loc(column)] = bad
    try:
        generate(case, spec, 3)
        rejections.append(False)
    except ValueError:
        rejections.append(True)
record("invalid_predictor_rejection", all(rejections), {"negative_bmi_nan_age_invalid_sex_rejected": rejections})

source_checks = []
conditional_checks = []
grid = []
rho = 2 * np.sin(np.pi * p["partial_spearman_bmi_hdl"] / 6)
for sex in [1, 2]:
    key = str(sex)
    mean = p["reference_hdl_mean_mgdl"][key]
    sd = p["reference_hdl_sd_mgdl"][key]
    bmean = p["reference_bmi_mean"][key]
    bsd = p["reference_bmi_sd"][key]
    gamma = p["log_hdl_age_slope_per_year"][key]
    tau2 = np.log1p((sd / mean) ** 2)
    v_age = (gamma * p["reference_age_sd_years"]) ** 2
    beta = rho * np.sqrt(tau2 - v_age) / bsd
    resid2 = (1-rho**2)*(tau2-v_age)
    total_var = resid2 + (beta*bsd)**2 + v_age
    implied_mean = np.exp(np.log(mean)-tau2/2+total_var/2)
    implied_sd = implied_mean*np.sqrt(np.expm1(total_var))
    source_checks.append({"sex": sex, "analytic_reference_mean": float(implied_mean), "source_mean": mean, "analytic_reference_sd": float(implied_sd), "source_sd": sd, "reference_median_if_lognormal": float(mean*np.exp(-tau2/2)), "reported_source_median": 43 if sex == 1 else 54, "beta_bmi": float(beta), "residual_log_sd": float(np.sqrt(resid2))})
    n = 160000
    ref = pd.DataFrame({"row_id": [f"repeat_{sex}_{i}" for i in range(n)], "bmi": bmean, "age": p["reference_age_mean_years"], "sex": sex})
    simulated = generate(ref, spec, 11901 + sex).hdl
    wanted_mean = np.exp(np.log(mean)-tau2/2+resid2/2)
    wanted_sd = wanted_mean*np.sqrt(np.expm1(resid2))
    conditional_checks.append({"sex": sex, "n": n, "expected_mean": float(wanted_mean), "simulated_mean": float(simulated.mean()), "expected_sd": float(wanted_sd), "simulated_sd": float(simulated.std(ddof=1)), "mean_abs_error": float(abs(simulated.mean()-wanted_mean)), "sd_abs_error": float(abs(simulated.std(ddof=1)-wanted_sd))})
    for b in [14.1, 25.0, 40.0, 77.5]:
        for a in [20, 40, 60, 79]:
            mu = np.log(mean)-tau2/2+beta*(b-bmean)+gamma*(a-62)
            grid.append({"sex": sex, "bmi": b, "age": a, "conditional_mean_hdl": float(np.exp(mu+resid2/2))})
record("reference_moment_algebra", all(abs(x["analytic_reference_mean"]-x["source_mean"]) < 1e-10 and abs(x["analytic_reference_sd"]-x["source_sd"]) < 1e-10 for x in source_checks), source_checks)
record("conditional_monte_carlo_on_invented_repeated_cells", all(x["mean_abs_error"] < 0.15 and x["sd_abs_error"] < 0.15 for x in conditional_checks), conditional_checks)

rng = np.random.default_rng(651290)
x = rng.normal(size=250000)
z = rng.normal(size=250000)
y = rho*x + np.sqrt(1-rho*rho)*z
empirical_rank = float(spearmanr(x, y).statistic)
record("gaussian_copula_conversion_on_invented_inputs", abs(empirical_rank-p["partial_spearman_bmi_hdl"]) < 0.01, {"latent_rho": float(rho), "requested_rank_correlation": -0.26, "simulated_rank_correlation": empirical_rank, "scope": "Checks the mathematical bridge under Gaussian assumptions; not the empirical validity of transporting partial Spearman coefficients"})

age_check = []
for sex, young, middle in [(1, 1.27, 1.38), (2, 1.45, 1.49)]:
    predicted = young*np.exp(p["log_hdl_age_slope_per_year"][str(sex)]*(54.5-34.5))
    age_check.append({"sex": sex, "source_middle_age_mean_mmolL": middle, "endpoint_log_linear_prediction": float(predicted), "relative_difference": float(predicted/middle-1)})
record("middle_age_source_interpolation_check", all(abs(x["relative_difference"]) < 0.03 for x in age_check), {"details": age_check, "interpretation": "Within 3% is an exploratory shape check, not a CI or target validation; group means are rounded and adjustment reference values unknown"})

results["invented_conditional_mean_grid"] = grid
results["sensitivity_assessment"] = {
    "scope": "Analytic response to stated structural alternatives, not fitted or selected from outcomes",
    "eliminate_age_term_at_age20_relative_to_age62": {str(s): float(np.exp(-p["log_hdl_age_slope_per_year"][str(s)]*(20-62))) for s in [1,2]},
    "double_absolute_bmi_slope_extra_mean_ratio_at_bmi40_vs_reference": {str(x["sex"]): float(np.exp(x["beta_bmi"]*(40-p["reference_bmi_mean"][str(x["sex"])]))) for x in source_checks},
    "interpretation": "Age transport and BMI-shape changes can materially alter predictions; no test identifies the correct alternative without independent evidence."
}
results["target_outcome_validation_run"] = False
results["passed"] = all(x["passed"] for x in results["tests"])
results["remaining_budget"] = {"queries": 0, "downloads": 5}
(HERE / "artificial_checks.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps({"passed": results["passed"], "tests": len(results["tests"]), "output": str(HERE / "artificial_checks.json"), "conditional_tests": conditional_checks, "age_check": age_check}, indent=2))
