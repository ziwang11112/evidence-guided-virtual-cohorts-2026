import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This whole-cohort generator expects observed=None.')
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative.')
    m = spec['model']
    rng = np.random.default_rng(seed)

    ap = m['age']
    age = ap['minimum'] + (ap['maximum'] - ap['minimum']) * rng.beta(
        ap['beta_alpha'], ap['beta_beta'], size=n
    )
    female = rng.binomial(1, m['female_probability'], size=n).astype(np.int64)
    a = (age - 50.0) / 10.0

    # Conditional rejection changes BMI's conditional mean, not age/sex frequencies.
    bm = m['bmi']
    nominal_mean = (
        bm['untruncated_mean_at_age50_male']
        + bm['female_mean_increment'] * female
        + bm['age_decade_linear'] * a
        + bm['age_decade_quadratic'] * a * a
    )
    log_mean = np.log(nominal_mean - bm['shift']) - 0.5 * bm['log_sd'] ** 2
    bmi = np.empty(n, dtype=float)
    pending = np.arange(n)
    while pending.size:
        candidate = bm['shift'] + rng.lognormal(
            mean=log_mean[pending], sigma=bm['log_sd'], size=pending.size
        )
        accepted = (
            np.isfinite(candidate)
            & (candidate >= bm['minimum'])
            & (candidate <= bm['maximum'])
        )
        bmi[pending[accepted]] = candidate[accepted]
        pending = pending[~accepted]

    bp = m['bp']
    b = (bmi - 25.0) / 5.0
    hinge = np.maximum((age - bp['age_hinge_years']) / 10.0, 0.0)
    location = (
        np.asarray(bp['intercepts'], dtype=float)[None, :]
        + a[:, None] * np.asarray(bp['age_decade_coefficients'], dtype=float)[None, :]
        + female[:, None] * np.asarray(bp['female_coefficients'], dtype=float)[None, :]
        + b[:, None] * np.asarray(bp['bmi_per5_coefficients'], dtype=float)[None, :]
        + hinge[:, None] * np.asarray(bp['age_hinge_decade_coefficients'], dtype=float)[None, :]
    )
    nu = float(bp['residual_df'])
    rho = float(bp['pretruncation_residual_correlation'])
    sd = np.asarray(bp['pretruncation_residual_sd'], dtype=float)
    if nu <= 2.0 or abs(rho) >= 1.0 or np.any(sd <= 0.0):
        raise ValueError('Invalid residual covariance parameters.')
    outcomes = np.empty((n, 2), dtype=float)
    pending = np.arange(n)
    while pending.size:
        z = rng.standard_normal((pending.size, 2))
        # A common chi-square draw gives an elliptical bivariate t per person.
        # This scaling makes the pretruncation marginal variances equal sd**2.
        scale = np.sqrt((nu - 2.0) / rng.chisquare(nu, size=pending.size))
        errors = np.column_stack((
            sd[0] * z[:, 0],
            sd[1] * (rho * z[:, 0] + np.sqrt(1.0 - rho * rho) * z[:, 1])
        )) * scale[:, None]
        candidate = location[pending] + errors
        pulse_pressure = candidate[:, 0] - candidate[:, 1]
        accepted = (
            np.isfinite(candidate).all(axis=1)
            & (candidate[:, 0] >= bp['sbp_bounds'][0])
            & (candidate[:, 0] <= bp['sbp_bounds'][1])
            & (candidate[:, 1] >= bp['dbp_bounds'][0])
            & (candidate[:, 1] <= bp['dbp_bounds'][1])
            & (pulse_pressure >= bp['pulse_pressure_bounds'][0])
            & (pulse_pressure <= bp['pulse_pressure_bounds'][1])
        )
        outcomes[pending[accepted]] = candidate[accepted]
        pending = pending[~accepted]

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': outcomes[:, 0],
        'dbp': outcomes[:, 1]
    }, columns=['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp'])
