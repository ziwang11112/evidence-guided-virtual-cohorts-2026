import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    task = spec['task']
    m = spec['model']
    n = task['n_rows']
    rng = np.random.default_rng(seed)
    basis = m['basis']
    cov = m['covariates']
    bm = cov['bmi']
    om = m['outcome_model']
    ref = m['calibration']
    age_coef = np.asarray(om['age_coefficients'], dtype=float)
    sex_coef = np.asarray(om['female_coefficients'], dtype=float)
    hinge_coef = np.asarray(om['hinge_coefficients'], dtype=float)
    bmi_coef = np.asarray(om['bmi_anchor_per_kg_m2'], dtype=float) * basis['bmi_scale']

    p_ref = 1 - ref['male_n'] / ref['n']
    a_ref = (ref['age_mean'] - basis['age_center']) / basis['age_scale']
    h_ref = (ref['age_mean'] - basis['hinge_age']) / basis['hinge_scale']
    bmi_ref = (bm['conditional_mean_intercept'] + bm['conditional_mean_age_coefficient'] * a_ref + bm['conditional_mean_female_coefficient'] * p_ref - basis['bmi_center']) / basis['bmi_scale']
    intercept = np.asarray(ref['bp_mean'], dtype=float) - age_coef * a_ref - sex_coef * p_ref - hinge_coef * h_ref - bmi_coef * bmi_ref
    q_age = age_coef + hinge_coef * basis['age_scale'] / basis['hinge_scale'] + bmi_coef * bm['conditional_mean_age_coefficient'] / basis['bmi_scale']
    q_sex = sex_coef + bmi_coef * bm['conditional_mean_female_coefficient'] / basis['bmi_scale']
    raw = np.diag(np.square(np.asarray(ref['bp_sd'], dtype=float)))
    raw[0, 1] = raw[1, 0] = (raw[0, 0] + raw[1, 1] - ref['pp_sd'] ** 2) / 2
    explained = np.outer(q_age, q_age) * (ref['age_sd'] / basis['age_scale']) ** 2
    explained += np.outer(q_sex, q_sex) * p_ref * (1 - p_ref)
    explained += np.outer(bmi_coef, bmi_coef) * (bm['innovation_sd'] / basis['bmi_scale']) ** 2
    explained += (np.outer(q_age, q_sex) + np.outer(q_sex, q_age)) * ref['age_female_covariance_years'] / basis['age_scale']
    innovation_covariance = raw - explained
    chol = np.linalg.cholesky(innovation_covariance)

    low, high = m['support']['age_years']
    age = rng.uniform(low, high, size=n)
    a = (age - basis['age_center']) / basis['age_scale']
    p_low, p_high = cov['female_probability_at_age_endpoints']
    p_female = p_low + (p_high - p_low) * (age - low) / (high - low)
    male_code, female_code = m['support']['female_codes']
    female = np.where(rng.random(n) < p_female, female_code, male_code).astype(np.int64)
    shape_a, shape_b = bm['innovation_shapes']
    beta_mean = shape_a / (shape_a + shape_b)
    beta_sd = np.sqrt(shape_a * shape_b / ((shape_a + shape_b) ** 2 * (shape_a + shape_b + 1)))
    bmi_error = bm['innovation_sd'] * (rng.beta(shape_a, shape_b, size=n) - beta_mean) / beta_sd
    bmi = bm['conditional_mean_intercept'] + bm['conditional_mean_age_coefficient'] * a + bm['conditional_mean_female_coefficient'] * female + bmi_error
    b = (bmi - basis['bmi_center']) / basis['bmi_scale']
    h = np.maximum(age - basis['hinge_age'], 0) / basis['hinge_scale']
    angle = 2 * np.pi * rng.random(n)
    radius = m['residual_law']['standardized_disk_radius'] * np.sqrt(rng.random(n))
    z = radius[:, None] * np.column_stack((np.cos(angle), np.sin(angle)))
    y = intercept + a[:, None] * age_coef + female[:, None] * sex_coef + b[:, None] * bmi_coef + h[:, None] * hinge_coef + z @ chol.T
    start = m['support']['row_id_start']
    data = {'row_id': np.arange(start, start + n, dtype=np.int64), 'age': age, 'female': female, 'bmi': bmi}
    for j, name in enumerate(om['outcome_order']):
        data[name] = y[:, j]
    return pd.DataFrame(data, columns=[column['name'] for column in task['columns']])
