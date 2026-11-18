import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This whole-cohort generator expects observed=None.')
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative.')
    p = spec['model']
    rng = np.random.default_rng(seed)

    ap = p['age']
    age = ap['lower'] + (ap['upper'] - ap['lower']) * rng.beta(
        ap['beta_alpha'], ap['beta_beta'], size=n
    )
    female = rng.binomial(1, p['female']['probability'], size=n).astype(np.int64)
    age10 = (age - 50.0) / 10.0

    bp = p['bmi']
    lower = float(bp['lower'])
    upper = float(bp['upper'])
    mean_bmi = (
        bp['conditional_mean_intercept']
        + bp['conditional_mean_per_age_decade'] * age10
        + bp['conditional_mean_female_difference'] * female
    )
    variance_bmi = float(bp['conditional_sd']) ** 2
    concentration = (mean_bmi - lower) * (upper - mean_bmi) / variance_bmi - 1.0
    fraction = (mean_bmi - lower) / (upper - lower)
    alpha_bmi = fraction * concentration
    beta_bmi = (1.0 - fraction) * concentration
    if np.any(alpha_bmi <= 0.0) or np.any(beta_bmi <= 0.0):
        raise ValueError('Invalid conditional BMI beta parameters.')
    bmi = lower + (upper - lower) * rng.beta(alpha_bmi, beta_bmi, size=n)

    design = np.column_stack((np.ones(n), age10, female, (bmi - 25.0) / 5.0))
    mean_sbp = design @ np.asarray(p['mean_bp']['sbp_coefficients'], dtype=float)
    mean_dbp = design @ np.asarray(p['mean_bp']['dbp_coefficients'], dtype=float)

    ep = p['residual_law']
    sd_s = float(ep['sbp_sd'])
    sd_d = float(ep['dbp_sd'])
    rho = float(ep['correlation'])
    left = float(ep['dbp_negative_bound_magnitude'])
    right = float(ep['dbp_positive_bound'])
    error_concentration = left * right / (sd_d ** 2) - 1.0
    alpha_d = error_concentration * left / (left + right)
    beta_d = error_concentration * right / (left + right)
    covariance = rho * sd_s * sd_d
    loading = covariance / (sd_d ** 2)
    gamma_variance = sd_s ** 2 - covariance ** 2 / (sd_d ** 2)
    gamma_shape = float(ep['independent_gamma_shape'])
    if min(alpha_d, beta_d, gamma_variance, gamma_shape) <= 0.0:
        raise ValueError('Invalid residual-law parameters.')
    error_d = -left + (left + right) * rng.beta(alpha_d, beta_d, size=n)
    gamma_scale = np.sqrt(gamma_variance / gamma_shape)
    independent_error = (
        rng.gamma(gamma_shape, gamma_scale, size=n) - gamma_shape * gamma_scale
    )
    dbp = mean_dbp + error_d
    sbp = mean_sbp + loading * error_d + independent_error

    return pd.DataFrame(
        {
            'row_id': np.arange(1, n + 1, dtype=np.int64),
            'age': age,
            'female': female,
            'bmi': bmi,
            'sbp': sbp,
            'dbp': dbp,
        },
        columns=['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp'],
    )
