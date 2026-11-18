"""Stage-1 arithmetic only: constants, no candidate import, rows, RNG or generation."""
import json
import math
from itertools import product
from pathlib import Path

r_bg = math.sqrt((0.1642 - 0.1174) / (1 - 0.1174))
r_bh = math.sqrt((0.1164 - 0.0660) / (1 - 0.0660))
r_gh = 0.23
s_b = 3.8
mgdl_per_mmol = 18.0182
source_beta_g_interpreted = 0.0240 * mgdl_per_mmol
source_beta_h_interpreted = 0.0125
s_g = source_beta_g_interpreted * s_b / r_bg
s_h = source_beta_h_interpreted * s_b / r_bh
b_g = r_bg * s_g / s_b
b_h = (s_h / s_b) * (r_bh - r_bg * r_gh) / (1 - r_bg**2)
g_h = (s_h / s_g) * (r_gh - r_bg * r_bh) / (1 - r_bg**2)
v_g = s_g**2 * (1 - r_bg**2)
v_h = s_h**2 * (1 - (r_bh**2 + r_gh**2 - 2*r_bg*r_bh*r_gh) / (1-r_bg**2))

def mean_g(a, f, b):
    return 91.2 + 0.2*(a-43.8) - 5.40546*(f-296/525) + b_g*(b-28.01)

g_center = mean_g(52, 0.52, 28.01)
def mean_h(a, f, b, g):
    return 5.4 + 0.01*(a-52) - 0.08301*(f-0.52) + b_h*(b-28.01) + g_h*(g-g_center)

# Deterministic affine bounding-box evaluations, not sampled individuals.
g_bounds = [mean_g(a, f, b) for a,f,b in product((25,79),(0,1),(15,45))]
h_bounds = [mean_h(a,f,b,g) for a,f,b,g in product((25,79),(0,1),(15,45),(50,126))]
beta_caps = [(m-50)*(126-m) for m in g_bounds]
result = {
    "scope": "constant-only analytic calculations; no generated rows; no candidate execution",
    "reported_constants": {"S2_beta_unlabelled_outcome":0.0125,"S1_beta_unlabelled_outcome":0.0240,"R2_H_base":0.0660,"R2_H_full":0.1164,"R2_G_base":0.1174,"R2_G_full":0.1642},
    "working_interpretations": {"S2_outcome":"HbA1c percent","S1_outcome":"glucose mmol/L","mgdl_per_mmol":mgdl_per_mmol,"BMI_residual_sd_target":s_b,"r_gh_target_residual":r_gh},
    "same_source_conditional_algebra": {"r_bg":r_bg,"r_bh":r_bh,"sd_ratio_G_to_B_in_mgdl_per_BMI":source_beta_g_interpreted/r_bg,"sd_ratio_H_to_B_in_percent_per_BMI":source_beta_h_interpreted/r_bh},
    "proposed_parameters": {"glucose_sd":s_g,"hba1c_sd":s_h,"glucose_bmi_slope":b_g,"glucose_variance":v_g,"hba1c_bmi_slope":b_h,"hba1c_glucose_slope":g_h,"hba1c_variance":v_h,"hba1c_glucose_center":g_center},
    "analytic_implications": {"Q1_age10":0.1,"Q2_bmi5":5*(b_h+g_h*b_g),"Q3_bmi5":5*b_h,"G_conditional_sd":math.sqrt(v_g),"H_conditional_sd":math.sqrt(v_h)},
    "feasibility": {"correlation_determinant":1+2*r_bg*r_bh*r_gh-r_bg**2-r_bh**2-r_gh**2,"leading_2x2_minor":1-r_bg**2,"G_mean_min":min(g_bounds),"G_mean_max":max(g_bounds),"G_min_beta_variance_cap":min(beta_caps),"G_variance":v_g,"H_mean_min":min(h_bounds),"H_mean_max":max(h_bounds),"H_variance":v_h},
    "assertions": {}
}
result["assertions"] = {
    "G_slope_equals_interpreted_S1":math.isclose(b_g,source_beta_g_interpreted,abs_tol=1e-14),
    "H_reduced_BMI_slope_equals_interpreted_S2":math.isclose(b_h+g_h*b_g,source_beta_h_interpreted,abs_tol=1e-14),
    "source_partial_r_recovered_from_ratios":math.isclose(b_g*s_b/s_g,r_bg,abs_tol=1e-14) and math.isclose((b_h+g_h*b_g)*s_b/s_h,r_bh,abs_tol=1e-14),
    "correlation_matrix_positive_definite":result["feasibility"]["correlation_determinant"]>0 and 1-r_bg**2>0,
    "glucose_beta_shapes_positive_over_box":50<min(g_bounds) and max(g_bounds)<126 and 0<v_g<min(beta_caps),
    "hba1c_gamma_parameters_positive_over_box":min(h_bounds)>0 and v_h>0,
}
assert all(result["assertions"].values())
output_path = Path(__file__).with_name("PROPOSAL_CALCULATIONS.json")
output_path.write_text(json.dumps(result, indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
