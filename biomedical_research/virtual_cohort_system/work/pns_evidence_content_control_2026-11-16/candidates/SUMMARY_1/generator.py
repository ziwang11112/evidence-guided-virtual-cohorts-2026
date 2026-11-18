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
    age = ap['lower'] + (ap['upper'] - ap['lower']) * rng.beta(
        ap['alpha'], ap['beta'], size=n
    )
    female = rng.binomial(1, m['sex']['female_probability'], size=n).astype(np.int64)
    design = m['design']
    a = (age - design['age_center']) / design['age_scale']

    bm = m['bmi']
    untruncated_mean = (
        bm['pretruncation_mean_intercept']
        + bm['pretruncation_mean_age_coefficient'] * a
        + bm['pretruncation_mean_age_squared_coefficient'] * a * a
        + bm['pretruncation_mean_female_coefficient'] * female
    )
    log_sd = float(bm['log_sd'])
    log_location = np.log(untruncated_mean) - 0.5 * log_sd * log_sd
    bmi = np.empty(n, dtype=float)
    pending = np.arange(n)
    while pending.size:
        candidate = rng.lognormal(log_location[pending], log_sd)
        keep = (candidate >= bm['lower']) & (candidate <= bm['upper'])
        bmi[pending[keep]] = candidate[keep]
        pending = pending[~keep]

    b = (bmi - design['bmi_center']) / design['bmi_scale']
    x = np.column_stack((np.ones(n), a, female, b))
    bp = m['bp']
    mean_s = x @ np.asarray(bp['sbp_mean_coefficients'], dtype=float)
    mean_d = x @ np.asarray(bp['dbp_mean_coefficients'], dtype=float)
    hinge = np.maximum(age - bp['dbp_age_hinge_knot'], 0.0) / bp['dbp_age_hinge_scale']
    mean_d = mean_d + bp['dbp_age_hinge_coefficient'] * hinge
    sd_s = (
        bp['sbp_residual_sd_at_age_origin']
        + bp['sbp_residual_sd_per_year'] * (age - bp['sbp_residual_sd_age_origin'])
    )
    sd_d = float(bp['dbp_residual_sd'])
    rho = float(bp['latent_residual_correlation'])
    independent_loading = np.sqrt(1.0 - rho * rho)

    sbp = np.empty(n, dtype=float)
    dbp = np.empty(n, dtype=float)
    pending = np.arange(n)
    while pending.size:
        z = rng.standard_normal((pending.size, 2))
        candidate_s = mean_s[pending] + sd_s[pending] * z[:, 0]
        candidate_d = mean_d[pending] + sd_d * (
            rho * z[:, 0] + independent_loading * z[:, 1]
        )
        keep = (
            (candidate_s >= bp['sbp_lower'])
            & (candidate_s <= bp['sbp_upper'])
            & (candidate_d >= bp['dbp_lower'])
            & (candidate_d <= bp['dbp_upper'])
            & ((candidate_s - candidate_d) >= bp['minimum_pulse_pressure'])
        )
        sbp[pending[keep]] = candidate_s[keep]
        dbp[pending[keep]] = candidate_d[keep]
        pending = pending[~keep]

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': sbp,
        'dbp': dbp
    }, columns=['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp'])
