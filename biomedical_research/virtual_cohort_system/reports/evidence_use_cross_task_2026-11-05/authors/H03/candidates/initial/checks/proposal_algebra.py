"""Retained deterministic moment calculation; no random draws or individual rows."""
import json
import math
from pathlib import Path

bands = ((25, 39), (40, 54), (55, 69), (70, 79))
age_mean = sum((a + b) / 2 for a, b in bands) / 4
age_variance = sum(((b - a + 1) ** 2 - 1) / 12 + ((a + b) / 2 - age_mean) ** 2 for a, b in bands) / 4
bmi_mean, bmi_variance, bmi_lower, bmi_upper = 28.01, 3.8 ** 2, 10.0, 65.0
bp = (bmi_mean - bmi_lower) / (bmi_upper - bmi_lower)
bk = (bmi_mean - bmi_lower) * (bmi_upper - bmi_mean) / bmi_variance - 1
ga, gb, gf = 0.20, 0.0240 * 18.0, -0.2472 * 18.0
gm, gv, gl, gu = 91.2, 12.4 ** 2, 0.0, 126.0
vgm = ga ** 2 * age_variance + gb ** 2 * bmi_variance + gf ** 2 * 0.25
gk = ((gm - gl) * (gu - gm) - vgm) / (gv - vgm) - 1
am, av = 52.0, 2.0  # discrete-uniform ages 50--54, for the reference HbA1c moment
gmr = gm + ga * (am - age_mean)
vgmr = ga ** 2 * av + gb ** 2 * bmi_variance + gf ** 2 * 0.25
g_residual_var_ref = ((gmr - gl) * (gu - gmr) - vgmr) / (gk + 1)
h_mean_ref, h_var_ref = 5.40, ((6.0 - 5.40) / 1.959963984540054) ** 2
ha, hb_total, hf_total, rho = 0.010, 0.0125, 0.0230, 0.23

def moments(c):
    vhmu = (ha + c * ga) ** 2 * age_variance + hb_total ** 2 * bmi_variance + hf_total ** 2 * 0.25 + c * c * (gv - vgm)
    vhmu_ref = (ha + c * ga) ** 2 * av + hb_total ** 2 * bmi_variance + hf_total ** 2 * 0.25 + c * c * g_residual_var_ref
    residual_variance = h_var_ref - vhmu_ref
    vh = residual_variance + vhmu
    cov = ha * ga * age_variance + hb_total * gb * bmi_variance + hf_total * gf * 0.25 + c * (gv - gb ** 2 * bmi_variance - gf ** 2 * 0.25)
    return vh, cov, residual_variance

v0 = moments(0)[0]
v1 = (moments(1)[0] - moments(-1)[0]) / 2
v2 = (moments(1)[0] + moments(-1)[0]) / 2 - v0
k0 = moments(0)[1]
k1 = moments(1)[1] - k0
qa = k1 * k1 - rho * rho * gv * v2
qb = 2 * k0 * k1 - rho * rho * gv * v1
qc = k0 * k0 - rho * rho * gv * v0
disc = qb * qb - 4 * qa * qc
roots = [(-qb - math.sqrt(disc)) / (2 * qa), (-qb + math.sqrt(disc)) / (2 * qa)]
accepted = [c for c in roots if moments(c)[2] > 0 and abs(moments(c)[1] / math.sqrt(gv * moments(c)[0]) - rho) < 1e-10]
assert len(accepted) == 1
c = accepted[0]
hb, hf = hb_total - c * gb, hf_total - c * gf
vh, cov, residual_variance = moments(c)
corners = [(a, b, f, g) for a in (25, 79) for b in (bmi_lower, bmi_upper) for f in (0, 1) for g in (gl, gu)]
mus = [h_mean_ref + ha * (a - am) + hb * (b - bmi_mean) + hf * (f - 0.5) + c * (g - gmr) for a, b, f, g in corners]
gmeans = [gm + ga * (a - age_mean) + gb * (b - bmi_mean) + gf * (f - 0.5) for a, b, f, _ in corners]
result = {
    'scope': 'deterministic proposed-law moments only; no random rows; not target validation',
    'age_mean': age_mean, 'age_variance': age_variance,
    'bmi_beta_alpha': bp * bk, 'bmi_beta_beta': (1 - bp) * bk,
    'glucose_beta_concentration': gk, 'glucose_mean_reference_age52': gmr,
    'glucose_mean_corner_range': [min(gmeans), max(gmeans)],
    'glucose_conditional_mean_slopes': {'age': ga, 'bmi': gb, 'female': gf},
    'quadratic_roots': roots,
    'hba1c_glucose_coefficient': c, 'hba1c_bmi_coefficient': hb, 'hba1c_female_coefficient': hf,
    'hba1c_conditional_variance': residual_variance, 'hba1c_reference_marginal_sd_approximation': math.sqrt(h_var_ref),
    'hba1c_mean_corner_range': [min(mus), max(mus)],
    'implied_marginal_glucose_sd': math.sqrt(gv), 'implied_marginal_hba1c_sd': math.sqrt(vh),
    'implied_pearson_glucose_hba1c': cov / math.sqrt(gv * vh),
    'implied_Q1_age10': 10 * ha, 'implied_Q2_bmi5': 5 * hb_total, 'implied_Q3_bmi5': 5 * hb,
    'native_Kerman_crude_slope_from_r_and_SDs': 0.23 * 0.73 / 12.4,
    'native_Kerman_reverse_crude_slope_from_r_and_SDs': 0.23 * 12.4 / 0.73,
}
assert min(gmeans) > gl and max(gmeans) < gu
assert min(mus) > 0 and max(mus) < 100
assert all(mu * (100 - mu) > residual_variance for mu in mus)
Path(__file__).with_name('PROPOSAL_ALGEBRA.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2, allow_nan=False))
