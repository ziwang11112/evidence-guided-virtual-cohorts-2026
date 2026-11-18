import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    rng = np.random.default_rng(seed)
    n = int(spec['task']['n_rows'])
    m = spec['model']

    ap = m['age']
    age = 20.0 + 59.0 * rng.beta(ap['alpha'], ap['beta'], size=n)
    female = rng.binomial(1, m['female']['probability'], size=n).astype(np.int64)
    a = (age - 50.0) / 10.0

    bpmi = m['bmi']
    cm = bpmi['untruncated_arithmetic_mean']
    mean_bmi = (cm['intercept'] + cm['age_per_decade'] * a
                + cm['age_per_decade_squared'] * a * a
                + cm['female'] * female)
    log_sd = bpmi['log_sd']
    log_location = np.log(mean_bmi - bpmi['shift']) - 0.5 * log_sd ** 2
    bmi = np.empty(n, dtype=float)
    pending = np.arange(n)
    while pending.size:
        candidates = bpmi['shift'] + np.exp(
            rng.normal(log_location[pending], log_sd, size=pending.size)
        )
        good = (np.isfinite(candidates)
                & (candidates >= bpmi['lower'])
                & (candidates <= bpmi['upper']))
        bmi[pending[good]] = candidates[good]
        pending = pending[~good]

    bp = m['bp']
    a = (age - bp['age_center']) / bp['age_scale']
    b = (bmi - bp['bmi_center']) / bp['bmi_scale']
    positive_age_squared = np.maximum(a, 0.0) ** 2

    def outcome_mean(parameters):
        return (parameters['intercept'] + parameters['age'] * a
                + parameters['positive_age_squared'] * positive_age_squared
                + parameters['female'] * female + parameters['bmi'] * b)

    mu_s = outcome_mean(bp['sbp_mean'])
    mu_d = outcome_mean(bp['dbp_mean'])
    sigma_s = bp['innovation_sd_sbp']
    sigma_d = bp['innovation_sd_dbp']
    rho = bp['innovation_correlation']
    independent_scale = np.sqrt(1.0 - rho ** 2)
    bounds = bp['support']
    sbp = np.empty(n, dtype=float)
    dbp = np.empty(n, dtype=float)
    pending = np.arange(n)
    while pending.size:
        z = rng.standard_normal((pending.size, 2))
        s = mu_s[pending] + sigma_s * z[:, 0]
        d = mu_d[pending] + sigma_d * (rho * z[:, 0] + independent_scale * z[:, 1])
        pulse_pressure = s - d
        good = (np.isfinite(s) & np.isfinite(d)
                & (s >= bounds['sbp_lower']) & (s <= bounds['sbp_upper'])
                & (d >= bounds['dbp_lower']) & (d <= bounds['dbp_upper'])
                & (pulse_pressure >= bounds['pulse_pressure_lower'])
                & (pulse_pressure <= bounds['pulse_pressure_upper']))
        sbp[pending[good]] = s[good]
        dbp[pending[good]] = d[good]
        pending = pending[~good]

    return pd.DataFrame({
        'row_id': np.arange(n, dtype=np.int64),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': sbp,
        'dbp': dbp
    }, columns=['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp'])
