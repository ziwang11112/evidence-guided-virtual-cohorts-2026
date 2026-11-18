import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    rng = np.random.default_rng(seed)

    ac = m['age']
    age = ac['lower'] + (ac['upper'] - ac['lower']) * rng.beta(
        ac['beta_shape_a'], ac['beta_shape_b'], size=n
    )
    female = rng.binomial(1, m['female_probability'], size=n).astype(np.int64)
    a = (age - 50.0) / 10.0

    bc = m['bmi']
    log_location = (
        np.log(bc['reference_unshifted_median'])
        + bc['log_age_coefficient_per_decade'] * a
        + bc['log_female_coefficient'] * female
    )
    bmi = np.empty(n, dtype=float)
    pending = np.arange(n)
    while pending.size:
        candidate = bc['shift'] + np.exp(
            log_location[pending] + bc['log_sd'] * rng.standard_normal(pending.size)
        )
        accept = (
            np.isfinite(candidate)
            & (candidate >= bc['lower'])
            & (candidate <= bc['upper'])
        )
        bmi[pending[accept]] = candidate[accept]
        pending = pending[~accept]

    b = (bmi - 25.0) / 5.0
    cs = np.asarray(m['conditional_mean_coefficients']['sbp'], dtype=float)
    cd = np.asarray(m['conditional_mean_coefficients']['dbp'], dtype=float)
    mu_s = cs[0] + cs[1] * a + cs[2] * female + cs[3] * b
    mu_d = cd[0] + cd[1] * a + cd[2] * female + cd[3] * b

    rc = m['residual']
    ss = float(rc['reference_sbp_sd'])
    sd = float(rc['reference_dbp_sd'])
    rho = float(rc['correlation'])
    radial_multiplier = float(rc['radial_squared_multiplier'])
    rmax = np.sqrt(radial_multiplier)
    pp_sd = np.sqrt(ss * ss + sd * sd - 2.0 * rho * ss * sd)
    pc = m['physiological_support']
    g = np.minimum.reduce([
        np.ones(n),
        (mu_s - pc['sbp_lower']) / (rmax * ss),
        (pc['sbp_upper'] - mu_s) / (rmax * ss),
        (mu_d - pc['dbp_lower']) / (rmax * sd),
        (pc['dbp_upper'] - mu_d) / (rmax * sd),
        (mu_s - mu_d - pc['pulse_pressure_lower']) / (rmax * pp_sd)
    ])
    if np.any(g <= 0.0):
        raise ValueError('Conditional means do not lie inside the specified physiological support.')

    radius = np.sqrt(radial_multiplier * rng.beta(
        rc['radial_beta_a'], rc['radial_beta_b'], size=n
    ))
    theta = rng.uniform(0.0, 2.0 * np.pi, size=n)
    z1 = radius * np.cos(theta)
    z2 = radius * np.sin(theta)
    sbp = mu_s + g * ss * z1
    dbp = mu_d + g * sd * (rho * z1 + np.sqrt(1.0 - rho * rho) * z2)

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': sbp,
        'dbp': dbp
    }, columns=['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp'])
