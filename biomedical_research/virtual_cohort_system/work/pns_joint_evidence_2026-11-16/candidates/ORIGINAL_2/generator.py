import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative')
    m = spec['model']
    rng = np.random.default_rng(seed)

    edges = np.asarray(m['age']['edges'], dtype=float)
    probabilities = np.asarray(m['age']['probabilities'], dtype=float)
    age_bin = rng.choice(len(probabilities), size=n, p=probabilities)
    age = edges[age_bin] + rng.random(n) * (edges[age_bin + 1] - edges[age_bin])
    female = rng.binomial(1, m['female_probability'], size=n).astype(np.int64)

    design = m['design']
    a = (age - design['age_center']) / design['age_scale']
    bm = m['bmi']
    bc = bm['untruncated_arithmetic_mean']
    bmi_mean = (bc['intercept'] + bc['female'] * female
                + bc['age_a'] * a + bc['age_a_squared'] * a * a)
    cv = float(bm['untruncated_coefficient_of_variation'])
    log_variance = np.log1p(cv * cv)
    log_sd = np.sqrt(log_variance)
    log_mean = np.log(bmi_mean) - 0.5 * log_variance
    bmi = np.exp(rng.normal(loc=log_mean, scale=log_sd, size=n))
    bmi_low, bmi_high = bm['bounds']
    pending = np.flatnonzero((~np.isfinite(bmi)) | (bmi < bmi_low) | (bmi > bmi_high))
    while pending.size:
        proposed = np.exp(rng.normal(loc=log_mean[pending], scale=log_sd, size=pending.size))
        good = np.isfinite(proposed) & (proposed >= bmi_low) & (proposed <= bmi_high)
        bmi[pending[good]] = proposed[good]
        pending = pending[~good]

    b = (bmi - design['bmi_center']) / design['bmi_scale']
    bp = m['bp']
    def location(coefficients):
        return (coefficients['intercept'] + coefficients['age_a'] * a
                + coefficients['female'] * female + coefficients['bmi_b'] * b
                + coefficients['age_a_squared'] * a * a)
    location_s = location(bp['untruncated_location']['sbp'])
    location_d = location(bp['untruncated_location']['dbp'])

    err = bp['errors']
    df = float(err['degrees_of_freedom'])
    sd_s, sd_d = err['untruncated_marginal_sd']
    rho = float(err['untruncated_correlation'])
    orthogonal_scale = np.sqrt(1.0 - rho * rho)
    bounds = bp['conditional_acceptance_bounds']
    s_low, s_high = bounds['sbp']
    d_low, d_high = bounds['dbp']
    pp_low, pp_high = bounds['pulse_pressure']
    sbp = np.empty(n, dtype=float)
    dbp = np.empty(n, dtype=float)
    pending = np.arange(n)
    while pending.size:
        z = rng.standard_normal((pending.size, 2))
        scale = np.sqrt((df - 2.0) / rng.chisquare(df, size=pending.size))
        proposed_s = location_s[pending] + sd_s * z[:, 0] * scale
        proposed_d = location_d[pending] + sd_d * (rho * z[:, 0] + orthogonal_scale * z[:, 1]) * scale
        pulse_pressure = proposed_s - proposed_d
        good = (np.isfinite(proposed_s) & np.isfinite(proposed_d)
                & (proposed_s >= s_low) & (proposed_s <= s_high)
                & (proposed_d >= d_low) & (proposed_d <= d_high)
                & (pulse_pressure >= pp_low) & (pulse_pressure <= pp_high))
        accepted = pending[good]
        sbp[accepted] = proposed_s[good]
        dbp[accepted] = proposed_d[good]
        pending = pending[~good]

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': sbp,
        'dbp': dbp
    }, columns=['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp'])
