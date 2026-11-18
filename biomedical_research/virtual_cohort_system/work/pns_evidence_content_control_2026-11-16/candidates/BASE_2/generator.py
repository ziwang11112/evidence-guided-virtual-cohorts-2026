import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative')
    rng = np.random.default_rng(seed)

    bands = np.asarray(m['age']['bands_inclusive'], dtype=np.int64)
    probabilities = np.asarray(m['age']['probabilities'], dtype=float)
    group = rng.choice(len(bands), size=n, p=probabilities)
    lower = bands[group, 0]
    width = bands[group, 1] - lower + 1
    age = lower + np.floor(rng.random(n) * width).astype(np.int64)
    female = rng.binomial(1, m['female']['probability'], size=n).astype(np.int64)

    scale = m['design_scaling']
    A = (age - scale['age_center']) / scale['age_scale']
    bm = m['bmi']
    median = (bm['median_intercept'] + bm['median_age'] * A
              + bm['median_age2'] * A * A + bm['median_female'] * female)
    log_sd = np.where(female == 1, bm['log_sd_female'], bm['log_sd_male'])
    bmi_low, bmi_high = bm['bounds']
    bmi = np.empty(n, dtype=float)
    pending = np.arange(n)
    while pending.size:
        candidate = np.exp(np.log(median[pending])
                           + log_sd[pending] * rng.standard_normal(pending.size))
        accept = (np.isfinite(candidate) & (candidate >= bmi_low)
                  & (candidate <= bmi_high))
        bmi[pending[accept]] = candidate[accept]
        pending = pending[~accept]

    B = (bmi - scale['bmi_center']) / scale['bmi_scale']
    bp = m['bp']
    sp = bp['sbp']
    dp = bp['dbp']

    def mean_surface(p):
        return (p['intercept'] + p['age'] * A + p['age2'] * A * A
                + p['female'] * female + p['bmi'] * B)

    mean_s = mean_surface(sp)
    mean_d = mean_surface(dp)
    rho = float(bp['innovation_correlation'])
    independent_scale = np.sqrt(1.0 - rho * rho)
    support = bp['support']
    s_low, s_high = support['sbp']
    d_low, d_high = support['dbp']
    pp_low = support['minimum_pulse_pressure']
    sbp = np.empty(n, dtype=float)
    dbp = np.empty(n, dtype=float)
    pending = np.arange(n)
    while pending.size:
        z1 = rng.standard_normal(pending.size)
        z2 = rng.standard_normal(pending.size)
        candidate_s = mean_s[pending] + sp['sd'] * z1
        candidate_d = mean_d[pending] + dp['sd'] * (
            rho * z1 + independent_scale * z2)
        accept = (np.isfinite(candidate_s) & np.isfinite(candidate_d)
                  & (candidate_s >= s_low) & (candidate_s <= s_high)
                  & (candidate_d >= d_low) & (candidate_d <= d_high)
                  & ((candidate_s - candidate_d) >= pp_low))
        sbp[pending[accept]] = candidate_s[accept]
        dbp[pending[accept]] = candidate_d[accept]
        pending = pending[~accept]

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': sbp,
        'dbp': dbp
    }, columns=['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp'])
