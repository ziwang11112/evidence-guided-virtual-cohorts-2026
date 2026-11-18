import math
import numpy as np
import pandas as pd
from scipy.stats import norm


def generate(observed, spec, seed):
    task, m = spec['task'], spec['model']
    n = int(task['n_rows'])
    rng = np.random.default_rng(seed)
    cov, lip, des = m['covariates'], m['lipids'], m['design']
    female = rng.random(n) < cov['sex']['p_female']
    a = cov['age']
    age = a['min'] + (a['max'] - a['min']) * rng.beta(a['beta_a'], a['beta_b'], n)
    if a['floor_to_completed_years']:
        age = np.floor(age)
    age = np.clip(age, a['min'], a['max'])
    b = cov['bmi']
    g = b['geometric_mean_at_reference_age']
    s = b['log_sd']
    gm = np.where(female, g['F'], g['M'])
    sd = np.where(female, s['F'], s['M'])
    loc = np.log(gm) + b['log_slope_per_decade_age'] * (age - b['reference_age']) / 10.0
    lo = norm.cdf((math.log(b['min']) - loc) / sd)
    hi = norm.cdf((math.log(b['max']) - loc) / sd)
    z = norm.ppf(lo + (hi - lo) * rng.random(n))
    bmi = np.clip(np.round(np.exp(loc + sd * z), int(b['round_decimals'])), b['min'], b['max'])
    x_age = (age - des['age_center']) / des['age_scale']
    x_bmi = (bmi - des['bmi_center']) / des['bmi_scale']
    f = female.astype(float)
    names = ['total_cholesterol', 'hdl_cholesterol']
    cv = [lip[k]['error']['residual_sd'] / lip[k]['error']['shift'] for k in names]
    sig = [math.sqrt(math.log(1.0 + c * c)) for c in cv]
    r = math.log(1.0 + lip['residual_pearson_correlation'] * cv[0] * cv[1]) / (sig[0] * sig[1])
    r = max(-1.0, min(1.0, r))
    z0 = rng.standard_normal(n)
    zs = [z0, r * z0 + math.sqrt(1.0 - r * r) * rng.standard_normal(n)]
    data = {'id': [m['id']['prefix'] + str(i + 1).zfill(int(m['id']['width'])) for i in range(n)], 'age': age, 'sex': np.where(female, 'F', 'M'), 'bmi': bmi}
    for k, sg, zz in zip(names, sig, zs):
        co = lip[k]['mean_coefficients']
        mu = co['intercept'] + co['age_per_decade'] * x_age + co['female'] * f + co['bmi_per_5'] * x_bmi
        err = lip[k]['error']['shift'] * (np.exp(sg * zz - 0.5 * sg * sg) - 1.0)
        data[k] = np.maximum(mu + err, lip['positive_floor'])
    return pd.DataFrame(data)[[c['name'] for c in task['columns']]]
