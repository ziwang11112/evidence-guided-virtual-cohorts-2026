import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    t = spec['task']
    m = spec['model']
    c = m['covariates']
    d = m['design']
    b = m['bp']
    n = int(t['n_rows'])
    rng = np.random.default_rng(seed)

    female = rng.binomial(1, c['female_probability'], size=n)
    age_shapes = np.asarray(c['age_beta_shapes_by_female'], dtype=float)[female]
    lo, hi = c['age_support_years']
    age = lo + (hi - lo) * rng.beta(age_shapes[:, 0], age_shapes[:, 1])
    age_x = (age - d['age_center_years']) / d['age_scale_years']
    base = np.column_stack((np.ones(n), age_x, female))

    bmi_mean = base @ np.asarray(c['bmi_conditional_mean_coefficients'], dtype=float)
    lo, hi = c['bmi_support_kg_m2']
    p = (bmi_mean - lo) / (hi - lo)
    k = c['bmi_beta_concentration']
    bmi = lo + (hi - lo) * rng.beta(k * p, k * (1 - p))
    bmi_x = (bmi - d['bmi_center_kg_m2']) / d['bmi_scale_kg_m2']

    means = base @ np.asarray(b['base_mean_coefficients'], dtype=float).T
    means += bmi_x[:, None] * np.asarray(b['bmi_slopes_per5'], dtype=float)
    alpha, beta = b['innovation_beta_shapes']
    total = alpha + beta
    innovation_mean = alpha / total
    innovation_sd = np.sqrt(alpha * beta / (total * total * (total + 1)))
    z = (rng.beta(alpha, beta, size=(n, 2)) - innovation_mean) / innovation_sd
    rho = b['residual_correlation']
    sd_s, sd_d = b['conditional_sd_mmHg']
    errors = np.column_stack((sd_s * (rho * z[:, 0] + np.sqrt(1 - rho * rho) * z[:, 1]), sd_d * z[:, 0]))
    bp = means + errors

    data = {
        t['row_id']: np.arange(n, dtype=np.int64) + m['identifier']['start'],
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': bp[:, 0],
        'dbp': bp[:, 1]
    }
    return pd.DataFrame(data, columns=[column['name'] for column in t['columns']])
