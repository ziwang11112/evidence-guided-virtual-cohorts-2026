import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative')
    rng = np.random.default_rng(seed)

    ac = m['age']
    edges = np.asarray(ac['edges'], dtype=float)
    probabilities = np.asarray(ac['probabilities'], dtype=float)
    groups = rng.choice(len(probabilities), size=n, p=probabilities)
    age = rng.uniform(edges[groups], edges[groups + 1])
    female = rng.binomial(1, m['female']['probability'], size=n).astype(np.int64)

    bc = m['bmi']
    median = (bc['median_intercept']
              + bc['median_female_increment'] * female
              + bc['median_age_slope'] * (age - bc['median_age_reference'])
              + bc['median_age_quadratic'] * (age - bc['median_quadratic_reference']) ** 2)
    if np.any(median <= 0):
        raise ValueError('BMI median must be positive')
    log_median = np.log(median)
    bmi = np.empty(n, dtype=float)
    pending = np.arange(n)
    bmi_low, bmi_high = bc['bounds']
    while pending.size:
        candidate = rng.lognormal(mean=log_median[pending], sigma=bc['log_sd'])
        accept = (candidate >= bmi_low) & (candidate <= bmi_high)
        bmi[pending[accept]] = candidate[accept]
        pending = pending[~accept]

    bp = m['bp']
    a = (age - bp['age_reference']) / bp['age_unit']
    b = (bmi - bp['bmi_reference']) / bp['bmi_unit']
    sc = bp['sbp_location']
    dc = bp['dbp_location']
    mu_s = sc['intercept'] + sc['age'] * a + sc['female'] * female + sc['bmi'] * b
    mu_d = (dc['intercept'] + dc['age'] * a + dc['female'] * female + dc['bmi'] * b
            + dc['age_hinge_coefficient'] * np.maximum(a - dc['age_hinge_start'], 0.0))

    ec = bp['errors']
    df = float(ec['df'])
    rho = float(ec['latent_correlation'])
    if df <= 2 or not (-1 < rho < 1):
        raise ValueError('Invalid error parameters')
    sd_s = (ec['sbp_untruncated_sd_at_age20']
            + ec['sbp_untruncated_sd_increment_per_year'] * (age - 20.0))
    sd_d = float(ec['dbp_untruncated_sd'])
    region = bp['conditional_acceptance_region']
    s_low, s_high = region['sbp_bounds']
    d_low, d_high = region['dbp_bounds']
    p_low, p_high = region['pulse_pressure_bounds']
    sbp = np.empty(n, dtype=float)
    dbp = np.empty(n, dtype=float)
    pending = np.arange(n)
    while pending.size:
        k = pending.size
        z1 = rng.standard_normal(k)
        z2 = rng.standard_normal(k)
        multiplier = np.sqrt((df - 2.0) / rng.chisquare(df, size=k))
        e_s = z1 * multiplier
        e_d = (rho * z1 + np.sqrt(1.0 - rho * rho) * z2) * multiplier
        candidate_s = mu_s[pending] + sd_s[pending] * e_s
        candidate_d = mu_d[pending] + sd_d * e_d
        pulse_pressure = candidate_s - candidate_d
        accept = ((candidate_s >= s_low) & (candidate_s <= s_high)
                  & (candidate_d >= d_low) & (candidate_d <= d_high)
                  & (pulse_pressure >= p_low) & (pulse_pressure <= p_high))
        sbp[pending[accept]] = candidate_s[accept]
        dbp[pending[accept]] = candidate_d[accept]
        pending = pending[~accept]

    result = pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': sbp,
        'dbp': dbp
    })
    column_order = [column['name'] for column in spec['task']['columns']]
    return result.loc[:, column_order]
