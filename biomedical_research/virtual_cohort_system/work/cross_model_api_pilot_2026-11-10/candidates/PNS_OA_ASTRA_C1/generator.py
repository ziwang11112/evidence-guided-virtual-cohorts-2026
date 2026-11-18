import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    task = spec['task']
    m = spec['model']
    rng = np.random.default_rng(seed)
    n = int(task['n_rows'])
    c = m['covariates']
    d = m['projection_design']

    female = rng.binomial(1, c['female_probability'], size=n)
    age_shapes = np.asarray(c['age_beta_shapes_by_female'], dtype=float)[female]
    lo, hi = c['age_support']
    age = lo + (hi - lo) * rng.beta(age_shapes[:, 0], age_shapes[:, 1])
    a = (age - d['age_center']) / d['age_scale']

    bm = c['bmi']
    ba, bb = bm['beta_shapes']
    bmi = (bm['location'] + bm['scaled_age_shift'] * a
           + bm['female_shift'] * female
           + bm['beta_span'] * rng.beta(ba, bb, size=n))
    b = (bmi - d['bmi_center']) / d['bmi_scale']

    x = np.column_stack((np.ones(n), a, female))
    bp = m['bp_conditional_mean']
    slopes = m['source_calibration']['intersalt_bmi_coefficient_per_kg_m2']
    mean_s = (x @ np.asarray(bp['sbp_non_bmi_coefficients'], dtype=float)
              + slopes['sbp'] * d['bmi_scale'] * b)
    mean_d = (x @ np.asarray(bp['dbp_non_bmi_coefficients'], dtype=float)
              + slopes['dbp'] * d['bmi_scale'] * b)

    inn = m['innovations']
    shapes = np.asarray(inn['beta_shapes'], dtype=float)
    alpha, beta = shapes[:, 0], shapes[:, 1]
    total = alpha + beta
    beta_mean = alpha / total
    beta_var = alpha * beta / (total ** 2 * (total + 1))
    draws = rng.beta(alpha, beta, size=(n, len(alpha)))
    errors = ((draws - beta_mean) / np.sqrt(beta_var)
              * np.asarray(inn['individual_sd_mmHg'], dtype=float))
    dbp = mean_d + errors[:, 0]
    pulse_pressure = mean_s - mean_d + errors[:, 1]
    sbp = dbp + pulse_pressure

    data = {'row_id': np.arange(n, dtype=np.int64), 'age': age,
            'female': female, 'bmi': bmi, 'sbp': sbp, 'dbp': dbp}
    return pd.DataFrame(data, columns=[column['name'] for column in task['columns']])
