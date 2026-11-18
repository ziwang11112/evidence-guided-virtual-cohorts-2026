import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative')
    m = spec['model']
    rng = np.random.default_rng(seed)

    ap = m['age_distribution']
    age = ap['lower'] + (ap['upper'] - ap['lower']) * rng.beta(
        ap['alpha'], ap['beta'], size=n
    )
    female = rng.binomial(
        1, m['female_distribution']['probability'], size=n
    ).astype(np.int64)

    rp = m['regression']
    a = (age - rp['age_center']) / rp['age_scale']
    bp = m['bmi_distribution']
    log_location = (
        np.log(bp['reference_median'])
        + bp['log_age_linear'] * a
        + bp['log_age_quadratic'] * a * a
        + bp['log_female'] * female
    )
    log_lower = np.log(bp['lower'])
    log_upper = np.log(bp['upper'])
    bmi = np.empty(n, dtype=float)
    pending = np.arange(n, dtype=np.int64)
    # Individual conditional rejection sampling, not cohort-level selection.
    while pending.size:
        proposed_log_bmi = rng.normal(
            loc=log_location[pending], scale=bp['log_sd'], size=pending.size
        )
        accepted = (
            (proposed_log_bmi >= log_lower)
            & (proposed_log_bmi <= log_upper)
        )
        bmi[pending[accepted]] = np.exp(proposed_log_bmi[accepted])
        pending = pending[~accepted]

    b = (bmi - rp['bmi_center']) / rp['bmi_scale']
    x = np.column_stack((np.ones(n), a, female, b))
    mean_sbp = x @ np.asarray(rp['sbp_coefficients'], dtype=float)
    mean_dbp = x @ np.asarray(rp['dbp_coefficients'], dtype=float)

    ep = m['residual_distribution']
    k = int(ep['sphere_dimension'])
    g = rng.standard_normal(size=(n, k))
    lengths = np.sqrt(np.sum(g * g, axis=1))
    zero = lengths == 0.0
    while np.any(zero):
        g[zero] = rng.standard_normal(size=(int(np.sum(zero)), k))
        lengths[zero] = np.sqrt(np.sum(g[zero] * g[zero], axis=1))
        zero = lengths == 0.0
    # Normalization is within each virtual person, never across people.
    z = g[:, :2] * (np.sqrt(float(k)) / lengths)[:, None]
    rho = ep['correlation']
    error_sbp = ep['sbp_sd'] * z[:, 0]
    error_dbp = ep['dbp_sd'] * (
        rho * z[:, 0] + np.sqrt(1.0 - rho * rho) * z[:, 1]
    )

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': mean_sbp + error_sbp,
        'dbp': mean_dbp + error_dbp
    }, columns=['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp'])
