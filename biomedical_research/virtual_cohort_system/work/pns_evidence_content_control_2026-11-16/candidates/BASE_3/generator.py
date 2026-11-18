import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative')
    rng = np.random.default_rng(seed)

    age_spec = m['age']
    edges = np.asarray(age_spec['bin_edges'], dtype=np.int64)
    probabilities = np.asarray(age_spec['bin_probabilities'], dtype=float)
    groups = rng.choice(len(probabilities), size=n, p=probabilities)
    age = rng.integers(edges[groups], edges[groups + 1], size=n)

    bp_loc = m['bp_location']
    x_age = (age.astype(float) - bp_loc['age_center']) / bp_loc['age_scale']
    f_spec = m['female']
    p0 = float(f_spec['probability_at_age50'])
    log_odds = np.log(p0 / (1.0 - p0)) + f_spec['log_odds_per_age_decade'] * x_age
    p_female = 1.0 / (1.0 + np.exp(-log_odds))
    female = (rng.random(n) < p_female).astype(np.int64)

    b_spec = m['bmi']
    median_bmi = (
        b_spec['median_intercept']
        + b_spec['median_age_linear_per_decade'] * x_age
        + b_spec['median_age_quadratic_per_decade_squared'] * x_age ** 2
        + b_spec['median_female_increment'] * female
    )
    bmi = np.empty(n, dtype=float)
    pending = np.arange(n, dtype=np.int64)
    while pending.size:
        candidates = rng.lognormal(
            mean=np.log(median_bmi[pending]),
            sigma=b_spec['log_sd'],
            size=pending.size
        )
        accept = (
            np.isfinite(candidates)
            & (candidates >= b_spec['lower'])
            & (candidates <= b_spec['upper'])
        )
        bmi[pending[accept]] = candidates[accept]
        pending = pending[~accept]

    x_bmi = (bmi - bp_loc['bmi_center']) / bp_loc['bmi_scale']
    hinge = np.maximum((age.astype(float) - bp_loc['hinge_age']) / bp_loc['age_scale'], 0.0)

    def location(p):
        return (
            p['intercept']
            + p['age_per_decade'] * x_age
            + p['female'] * female
            + p['bmi_per5'] * x_bmi
            + p['age_hinge_per_decade'] * hinge
        )

    mean_sbp = location(bp_loc['sbp'])
    mean_dbp = location(bp_loc['dbp'])
    e_spec = m['bp_error']
    df = float(e_spec['df'])
    rho = float(e_spec['correlation'])
    orthogonal_scale = np.sqrt(1.0 - rho * rho)
    support = m['bp_support']
    sbp = np.empty(n, dtype=float)
    dbp = np.empty(n, dtype=float)
    pending = np.arange(n, dtype=np.int64)
    while pending.size:
        k = pending.size
        z = rng.standard_normal((k, 2))
        radial = np.sqrt((df - 2.0) / rng.chisquare(df, size=k))
        e_s = e_spec['sbp_sd'] * radial * z[:, 0]
        e_d = e_spec['dbp_sd'] * radial * (rho * z[:, 0] + orthogonal_scale * z[:, 1])
        candidate_s = mean_sbp[pending] + e_s
        candidate_d = mean_dbp[pending] + e_d
        pulse_pressure = candidate_s - candidate_d
        accept = (
            np.isfinite(candidate_s)
            & np.isfinite(candidate_d)
            & (candidate_s >= support['sbp'][0])
            & (candidate_s <= support['sbp'][1])
            & (candidate_d >= support['dbp'][0])
            & (candidate_d <= support['dbp'][1])
            & (pulse_pressure >= support['pulse_pressure'][0])
            & (pulse_pressure <= support['pulse_pressure'][1])
        )
        sbp[pending[accept]] = candidate_s[accept]
        dbp[pending[accept]] = candidate_d[accept]
        pending = pending[~accept]

    return pd.DataFrame(
        {
            'row_id': np.arange(1, n + 1, dtype=np.int64),
            'age': age,
            'female': female,
            'bmi': bmi,
            'sbp': sbp,
            'dbp': dbp
        },
        columns=[c['name'] for c in spec['task']['columns']]
    )
