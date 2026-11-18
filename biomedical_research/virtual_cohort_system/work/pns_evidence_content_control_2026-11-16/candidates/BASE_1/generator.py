import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative')
    rng = np.random.default_rng(seed)

    am = m['age']
    age = am['lower'] + (am['upper'] - am['lower']) * rng.beta(
        am['beta_alpha'], am['beta_beta'], size=n
    )
    female = (rng.random(n) < m['female_probability']).astype(np.int64)
    a = (age - 50.0) / 10.0

    bm = m['bmi']
    log_location = (
        np.log(bm['median_excess_at_reference'])
        + bm['log_excess_age_coefficient'] * a
        + bm['log_excess_age_squared_coefficient'] * a * a
        + bm['log_excess_female_coefficient'] * female
    )
    bmi = np.empty(n, dtype=float)
    pending = np.arange(n, dtype=np.int64)
    while pending.size:
        proposal = bm['lower_shift'] + np.exp(
            log_location[pending]
            + bm['log_excess_sd'] * rng.standard_normal(pending.size)
        )
        accept = (
            np.isfinite(proposal)
            & (proposal > bm['lower_shift'])
            & (proposal <= bm['upper'])
        )
        bmi[pending[accept]] = proposal[accept]
        pending = pending[~accept]

    b = (bmi - 25.0) / 5.0
    bp = m['conditional_bp']
    sm = bp['sbp']
    dm = bp['dbp']
    mean_s = (
        sm['intercept'] + sm['age_per_decade'] * a
        + sm['female'] * female + sm['bmi_per5'] * b
    )
    mean_d = (
        dm['intercept'] + dm['age_per_decade'] * a
        + dm['female'] * female + dm['bmi_per5'] * b
        + dm['age_hinge_coefficient'] * np.maximum(a - dm['age_hinge_start'], 0.0)
    )
    rho = bp['error_correlation']
    orthogonal_scale = np.sqrt(1.0 - rho * rho)
    bounds = m['bp_support']
    sbp = np.empty(n, dtype=float)
    dbp = np.empty(n, dtype=float)
    pending = np.arange(n, dtype=np.int64)
    while pending.size:
        z = rng.standard_normal((pending.size, 2))
        s = mean_s[pending] + bp['sd_sbp'] * z[:, 0]
        d = mean_d[pending] + bp['sd_dbp'] * (
            rho * z[:, 0] + orthogonal_scale * z[:, 1]
        )
        pp = s - d
        accept = (
            np.isfinite(s) & np.isfinite(d)
            & (s >= bounds['sbp'][0]) & (s <= bounds['sbp'][1])
            & (d >= bounds['dbp'][0]) & (d <= bounds['dbp'][1])
            & (pp >= bounds['pulse_pressure'][0])
            & (pp <= bounds['pulse_pressure'][1])
        )
        sbp[pending[accept]] = s[accept]
        dbp[pending[accept]] = d[accept]
        pending = pending[~accept]

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': sbp,
        'dbp': dbp
    }, columns=['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp'])
