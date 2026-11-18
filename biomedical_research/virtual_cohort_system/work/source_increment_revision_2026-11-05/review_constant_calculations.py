"""Independent source-only review arithmetic. No stochastic or candidate execution."""
import hashlib
import itertools
import json
import math
from pathlib import Path

root = Path(r"D:/AIR-014_ECRC_Paper_Clean_2026-08-16")
dest = root / "biomedical_research/virtual_cohort_system/work/source_increment_revision_2026-11-05"
proposal_path = dest / "PROPOSAL.json"
proposal = json.loads(proposal_path.read_text(encoding="utf-8-sig"))
baseline_path = root / "evcRepE01/candidates/initial/model_spec.json"
baseline = json.loads(baseline_path.read_text(encoding="utf-8-sig"))

# These constants were checked in original source/supplement text, not copied
# from the author's calculation output. sB/rGH are retained working assumptions.
r_bg = math.sqrt((0.1642 - 0.1174) / (1 - 0.1174))
r_bh = math.sqrt((0.1164 - 0.0660) / (1 - 0.0660))
s_b, r_gh = 3.8, 0.23
beta_g, beta_h = 0.0240 * 18.0182, 0.0125
s_g, s_h = s_b * beta_g / r_bg, s_b * beta_h / r_bh
b_g = r_bg * s_g / s_b
b_h = s_h / s_b * (r_bh - r_bg * r_gh) / (1 - r_bg**2)
g_h = s_h / s_g * (r_gh - r_bg * r_bh) / (1 - r_bg**2)
v_g = s_g**2 * (1 - r_bg**2)
v_h = s_h**2 * (1 - (r_bh**2 + r_gh**2 - 2*r_bg*r_bh*r_gh)/(1-r_bg**2))
expected_patch = {
    "parameters.residual_moments.glucose_sd": s_g,
    "parameters.residual_moments.hba1c_sd": s_h,
    "parameters.glucose.bmi_slope": b_g,
    "parameters.glucose.variance": v_g,
    "parameters.hba1c.bmi_slope": b_h,
    "parameters.hba1c.glucose_slope": g_h,
    "parameters.hba1c.variance": v_h,
}
assert len(proposal["proposed_model"]["parameter_patch"]) == len(expected_patch)
checks = []
for patch in proposal["proposed_model"]["parameter_patch"]:
    value = baseline
    for part in patch["path"].split("."):
        value = value[part]
    old_ok = math.isclose(value, patch["old"], rel_tol=1e-12, abs_tol=1e-12)
    new_ok = math.isclose(patch["value"], expected_patch[patch["path"]], rel_tol=1e-12, abs_tol=1e-12)
    assert old_ok and new_ok, patch["path"]
    checks.append({"path": patch["path"], "old_matches_static_baseline": old_ok,
                   "independently_derived_value": expected_patch[patch["path"]],
                   "proposed_value_matches": new_ok})

det = 1 + 2*r_bg*r_bh*r_gh-r_bg**2-r_bh**2-r_gh**2
principal2 = [1-r_bg**2, 1-r_bh**2, 1-r_gh**2]
assert min(principal2) > 0 and det > 0
g = baseline["parameters"]["glucose"]
h = baseline["parameters"]["hba1c"]
g_means = [g["base"]+g["age_slope"]*(a-g["age_center"])
           +g["female_slope"]*(f-g["female_center"])+b_g*(b-g["bmi_center"])
           for a,f,b in itertools.product((25,79),(0,1),(15.,45.))]
h_means = [h["base"]+h["age_slope"]*(a-h["age_center"])
           +h["female_slope"]*(f-h["female_center"])+b_h*(b-h["bmi_center"])
           +g_h*(x-h["glucose_center"])
           for a,f,b,x in itertools.product((25,79),(0,1),(15.,45.),(50.,126.))]
g_min, g_max = min(g_means), max(g_means)
h_min, h_max = min(h_means), max(h_means)
variance_cap = min((x-50)*(126-x) for x in (g_min,g_max))
assert 50 < g_min <= g_max < 126 and 0 < v_g < variance_cap
assert 0 < h_min <= h_max and v_h > 0

# Find beta shape extrema over the whole mean interval, not merely covariate corners.
width = 76.
alpha_y = lambda y: y/width * (y*(width-y)/v_g - 1)
ylo, yhi = g_min-50, g_max-50
critical = [(width-math.sqrt(width*width-3*v_g))/3,
            (width+math.sqrt(width*width-3*v_g))/3]
alpha_points = [ylo,yhi] + [x for x in critical if ylo <= x <= yhi]
beta_points = [ylo,yhi] + [width-x for x in critical if ylo <= width-x <= yhi]
alpha_bounds = [min(alpha_y(x) for x in alpha_points), max(alpha_y(x) for x in alpha_points)]
beta_bounds = [min(alpha_y(width-x) for x in beta_points), max(alpha_y(width-x) for x in beta_points)]
assert min(alpha_bounds+beta_bounds) > 0

base_var_b = s_b*s_b
base_var_g = b_g*b_g*base_var_b+v_g
base_cov_bg = b_g*base_var_b
base_cov_bh = (b_h+g_h*b_g)*base_var_b
base_cov_gh = b_h*base_cov_bg+g_h*base_var_g
base_var_h = b_h*b_h*base_var_b+g_h*g_h*base_var_g+2*b_h*g_h*base_cov_bg+v_h
reconstructed = {
    "glucose_variance_given_age_sex": base_var_g,
    "hba1c_variance_given_age_sex": base_var_h,
    "r_bg": base_cov_bg/(s_b*math.sqrt(base_var_g)),
    "r_bh": base_cov_bh/(s_b*math.sqrt(base_var_h)),
    "r_gh": base_cov_gh/math.sqrt(base_var_g*base_var_h),
    "hba1c_variance_given_age_sex_bmi": g_h*g_h*v_g+v_h,
}
assert math.isclose(base_var_g,s_g*s_g,rel_tol=1e-12)
assert math.isclose(base_var_h,s_h*s_h,rel_tol=1e-12)
for name,val in (("r_bg",r_bg),("r_bh",r_bh),("r_gh",r_gh)):
    assert math.isclose(reconstructed[name],val,rel_tol=1e-12)
questions = {"Q1_age10": 10*h["age_slope"], "Q2_bmi5": 5*(b_h+g_h*b_g), "Q3_bmi5": 5*b_h}
for item in proposal["questions"]:
    assert math.isclose(questions[item["id"]],item["proposed_model_implication"],rel_tol=1e-12,abs_tol=1e-12)
assert math.isclose(questions["Q2_bmi5"],5*beta_h,rel_tol=1e-12)

record = {
    "scope": "Independent deterministic review only; no source rows, RNG, generator import/execution, target/evaluation access or parameter search.",
    "proposal_sha256": hashlib.sha256(proposal_path.read_bytes()).hexdigest(),
    "baseline_spec_sha256": hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
    "parameter_checks": checks,
    "source_ratios": {"G_to_B": beta_g/r_bg,"H_to_B": beta_h/r_bh},
    "correlation_principal_minors_order2": principal2,
    "correlation_determinant": det,
    "G_conditional_mean_bounds": [g_min,g_max],
    "G_min_variance_cap": variance_cap,
    "G_conditional_sd": math.sqrt(v_g),
    "G_beta_alpha_bounds": alpha_bounds,
    "G_beta_beta_bounds": beta_bounds,
    "H_conditional_mean_bounds": [h_min,h_max],
    "H_conditional_sd": math.sqrt(v_h),
    "H_gamma_shape_bounds": [h_min*h_min/v_h,h_max*h_max/v_h],
    "H_gamma_scale_bounds": [v_h/h_max,v_h/h_min],
    "reconstructed_residual_moments": reconstructed,
    "Q_model_implications": questions,
    "conditional_variance_ratio_to_baseline": {
        "glucose": v_g/g["variance"],"hba1c":v_h/h["variance"]},
    "all_checks_passed": True,
}
(dest/"REVIEW_CALCULATIONS.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
print(json.dumps(record,indent=2))
