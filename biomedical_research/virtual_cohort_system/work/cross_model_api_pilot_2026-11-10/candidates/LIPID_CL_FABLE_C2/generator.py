import math
import numpy as np
import pandas as pd
from scipy import stats


def _std_shifted_lognormal(z, s):
    v = math.exp(s * s)
    return (np.exp(s * z) - math.sqrt(v)) / math.sqrt((v - 1.0) * v)


def generate(observed, spec, seed):
    task = spec['task']
    m = spec['model']
    n = int(task['n_rows'])
    rng = np.random.default_rng(seed)
    cov = m['covariates']
    female = rng.random(n) < cov['sex']['p_female']
    a = cov['age']
    g = stats.gamma(a['gamma_shape'], scale=a['gamma_scale_year'])
    age = a['min_year'] + g.ppf(rng.random(n) * g.cdf(a['max_year'] - a['min_year']))
    age = np.clip(age, a['min_year'], a['max_year'])
    b = cov['bmi']
    mu_log = np.where(female, math.log(b['geometric_mean_F']), math.log(b['geometric_mean_M']))
    mu_log = mu_log + b['log_slope_per_decade'] * (age - b['reference_age_year']) / 10.0
    sd_log = np.where(female, b['log_sd_F'], b['log_sd_M'])
    p_lo = stats.norm.cdf((math.log(b['min']) - mu_log) / sd_log)
    p_hi = stats.norm.cdf((math.log(b['max']) - mu_log) / sd_log)
    bmi = np.exp(mu_log + sd_log * stats.norm.ppf(p_lo + rng.random(n) * (p_hi - p_lo)))
    bmi = np.clip(bmi, b['min'], b['max'])
    d = m['design']
    X = np.column_stack([
        np.ones(n),
        (age - d['age_center_year']) / d['age_scale_year'],
        female.astype(float),
        (bmi - d['bmi_center']) / d['bmi_scale'],
    ])
    lip = m['lipids']
    h = lip['hdl']
    q = lip['non_hdl']
    sh = h['lognormal_shape']
    sq = q['lognormal_shape']
    rho = lip['residual_pearson_correlation_hdl_nonhdl']
    arg = 1.0 + rho * math.sqrt((math.exp(sh * sh) - 1.0) * (math.exp(sq * sq) - 1.0))
    rz = max(-1.0, min(1.0, math.log(arg) / (sh * sq)))
    z1 = rng.standard_normal(n)
    z2 = rz * z1 + math.sqrt(1.0 - rz * rz) * rng.standard_normal(n)
    hdl = X @ np.asarray(h['coef'], dtype=float) + h['residual_sd'] * _std_shifted_lognormal(z1, sh)
    non = X @ np.asarray(q['coef'], dtype=float) + q['residual_sd'] * _std_shifted_lognormal(z2, sq)
    floor = lip['positivity_floor_mmol_L']
    hdl = np.maximum(hdl, floor)
    non = np.maximum(non, floor)
    tc = hdl + non
    data = {
        'id': ['TKV%06d' % (i + 1) for i in range(n)],
        'age': age.astype(float),
        'sex': np.where(female, 'F', 'M'),
        'bmi': bmi.astype(float),
        'total_cholesterol': tc.astype(float),
        'hdl_cholesterol': hdl.astype(float),
    }
    df = pd.DataFrame(data)
    return df[[c['name'] for c in task['columns']]]
