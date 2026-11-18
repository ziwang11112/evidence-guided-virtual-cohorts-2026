import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This whole-cohort generator requires observed=None.')
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative.')
    m = spec['model']
    rng = np.random.default_rng(seed)

    ac = m['age']
    bands = np.asarray(ac['bands_inclusive'], dtype=np.int64)
    groups = rng.choice(len(bands), size=n, p=np.asarray(ac['probabilities'], dtype=float))
    low = bands[groups, 0]
    width = bands[groups, 1] - low + 1
    age = low + np.floor(rng.random(n) * width).astype(np.int64)
    a = (age.astype(float) - 50.0) / 10.0

    fc = m['female']
    pf = fc['probability_at_age50'] + fc['probability_change_per_year'] * (age - 50.0)
    female = rng.binomial(1, pf, size=n).astype(np.int64)

    bc = m['bmi']
    log_location = (np.log(bc['median_at_age50_male'])
                    + bc['log_median_age_per_decade'] * a
                    + bc['log_median_age_decade_squared'] * a * a
                    + bc['log_median_female'] * female)
    log_lower, log_upper = np.log(np.asarray(bc['bounds'], dtype=float))
    bmi = np.empty(n, dtype=float)
    pending = np.arange(n)
    while pending.size:
        proposed_log = log_location[pending] + bc['log_sd'] * rng.standard_normal(pending.size)
        accepted = ((proposed_log >= log_lower) & (proposed_log <= log_upper)
                    & np.isfinite(proposed_log))
        bmi[pending[accepted]] = np.exp(proposed_log[accepted])
        pending = pending[~accepted]

    b = (bmi - 25.0) / 5.0
    pc = m['bp']
    sc = pc['sbp']
    dc = pc['dbp']
    mean_s = (sc['intercept'] + sc['age_per_decade'] * a
              + sc['female'] * female + sc['bmi_per5'] * b)
    mean_d = (dc['intercept'] + dc['age_per_decade'] * a
              + dc['positive_age_decade_squared'] * np.maximum(a, 0.0) ** 2
              + dc['female'] * female + dc['bmi_per5'] * b)
    rho = float(pc['pretruncation_error_correlation'])
    orthogonal_scale = np.sqrt(1.0 - rho * rho)
    s_low, s_high = pc['bounds']['sbp']
    d_low, d_high = pc['bounds']['dbp']
    pp_low, pp_high = pc['bounds']['pulse_pressure']
    sbp = np.empty(n, dtype=float)
    dbp = np.empty(n, dtype=float)
    pending = np.arange(n)
    while pending.size:
        z = rng.standard_normal((pending.size, 2))
        proposed_s = mean_s[pending] + sc['pretruncation_error_sd'] * z[:, 0]
        proposed_d = mean_d[pending] + dc['pretruncation_error_sd'] * (rho * z[:, 0] + orthogonal_scale * z[:, 1])
        pp = proposed_s - proposed_d
        accepted = ((proposed_s >= s_low) & (proposed_s <= s_high)
                    & (proposed_d >= d_low) & (proposed_d <= d_high)
                    & (pp >= pp_low) & (pp <= pp_high)
                    & np.isfinite(proposed_s) & np.isfinite(proposed_d))
        sbp[pending[accepted]] = proposed_s[accepted]
        dbp[pending[accepted]] = proposed_d[accepted]
        pending = pending[~accepted]

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': sbp,
        'dbp': dbp
    }, columns=['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp'])
