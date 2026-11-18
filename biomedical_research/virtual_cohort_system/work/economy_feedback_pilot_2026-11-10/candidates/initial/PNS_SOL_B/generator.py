import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    task = spec['task']
    m = spec['model']
    n = int(task['n_rows'])
    rng = np.random.default_rng(seed)
    coding = m['predictor_coding']
    cov = m['covariates']
    ag = cov['age']
    lo, hi = int(ag['lower']), int(ag['upper'])
    age = rng.integers(lo, hi + 1, size=n)
    p = cov['female']['probability']
    female = rng.binomial(1, p, size=n)
    a = (age - coding['age_center']) / coding['age_scale']
    f = female - p
    bm = cov['bmi']
    alpha, beta = bm['beta_shapes']
    innovation = rng.beta(alpha, beta, size=n)
    beta_mean = alpha / (alpha + beta)
    bmi = (bm['reference_mean'] + bm['age_effect_per_standard_unit'] * a
           + bm['female_difference'] * f
           + bm['beta_scale'] * (innovation - beta_mean))
    b = (bmi - coding['bmi_center']) / coding['bmi_scale']
    bp = m['bp_mean']
    reference = np.asarray(bp['reference'], dtype=float)
    age_effect = np.asarray(bp['age_effect_per_standard_unit'], dtype=float)
    sex_effect = np.asarray(bp['female_difference'], dtype=float)
    bmi_effect = np.asarray(bp['bmi_effect_per_kg_m2'], dtype=float)
    mean = (reference + a[:, None] * age_effect + f[:, None] * sex_effect
            + b[:, None] * (coding['bmi_scale'] * bmi_effect))
    age_variance = (((hi - lo + 1) ** 2 - 1) / 12) / coding['age_scale'] ** 2
    beta_variance = alpha * beta / ((alpha + beta) ** 2 * (alpha + beta + 1))
    root_variances = np.array([age_variance, p * (1 - p), beta_variance])
    loadings = np.column_stack((
        age_effect + bmi_effect * bm['age_effect_per_standard_unit'],
        sex_effect + bmi_effect * bm['female_difference'],
        bmi_effect * bm['beta_scale']))
    mean_covariance = (loadings * root_variances) @ loadings.T
    anchor = m['bp_dispersion_bridge']
    vs = anchor['sbp_sd'] ** 2
    vd = anchor['dbp_sd'] ** 2
    csd = (vs + vd - anchor['pulse_pressure_sd'] ** 2) / 2
    marginal_covariance = np.array([[vs, csd], [csd, vd]])
    residual_covariance = marginal_covariance - mean_covariance
    factor = np.linalg.cholesky(residual_covariance)
    radius = m['residual_law']['standard_disk_radius'] * np.sqrt(rng.random(n))
    angle = 2 * np.pi * rng.random(n)
    disk = np.column_stack((radius * np.cos(angle), radius * np.sin(angle)))
    outcomes = mean + disk @ factor.T
    frame = pd.DataFrame({'row_id': np.arange(n, dtype=np.int64),
                          'age': age, 'female': female, 'bmi': bmi,
                          'sbp': outcomes[:, 0], 'dbp': outcomes[:, 1]})
    return frame[[column['name'] for column in task['columns']]]
