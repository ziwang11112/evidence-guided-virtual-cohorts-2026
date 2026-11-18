import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative')
    model = spec['model']
    rng = np.random.default_rng(seed)
    c = model['covariates']

    ac = c['age']
    age = 20.0 + 59.0 * rng.beta(ac['alpha'], ac['beta'], size=n)
    female = rng.binomial(1, c['female']['p'], size=n).astype(np.int64)
    a = (age - 50.0) / 10.0

    bc = c['bmi']
    cm = bc['conditional_mean']
    bmi_mean = (cm['intercept'] + cm['per_age_decade_centered_50'] * a
                + cm['female_difference'] * female)
    lo, hi = bc['lower'], bc['upper']
    q = (bmi_mean - lo) / (hi - lo)
    if np.any((q <= 0.0) | (q >= 1.0)):
        raise ValueError('Invalid conditional BMI beta parameters')
    k = bc['precision']
    bmi = lo + (hi - lo) * rng.beta(k * q, k * (1.0 - q))

    bp = model['bp']
    design = np.column_stack((np.ones(n), a, female, (bmi - 25.0) / 5.0))
    coefficients = np.array([
        bp['preconstraint_location_coefficients']['sbp'],
        bp['preconstraint_location_coefficients']['dbp']
    ], dtype=float)
    location = design @ coefficients.T

    ec = bp['error_law']
    rxx = np.asarray(ec['anchor_predictor_correlation'], dtype=float)
    ryx = np.asarray(ec['anchor_outcome_predictor_correlation'], dtype=float)
    ryy = np.asarray(ec['anchor_outcome_correlation'], dtype=float)
    source_partial = ryy - ryx @ np.linalg.solve(rxx, ryx.T)
    sd = np.asarray(ec['anchor_outcome_sd'], dtype=float)
    covariance = source_partial * np.outer(sd, sd)
    chol = np.linalg.cholesky(covariance)
    df = float(ec['degrees_of_freedom'])
    if df <= 2.0:
        raise ValueError('Finite-variance t law requires df > 2')

    support = bp['conditional_support']
    outcomes = np.empty((n, 2), dtype=float)
    pending = np.arange(n)
    while pending.size:
        count = pending.size
        z = rng.standard_normal((count, 2))
        chi = rng.chisquare(df, size=count)
        with np.errstate(over='ignore', divide='ignore', invalid='ignore'):
            errors = (z @ chol.T) * np.sqrt((df - 2.0) / chi)[:, None]
            candidate = location[pending] + errors
            pulse = candidate[:, 0] - candidate[:, 1]
        valid = np.isfinite(candidate).all(axis=1)
        valid &= candidate[:, 0] >= support['sbp_min']
        valid &= candidate[:, 0] <= support['sbp_max']
        valid &= candidate[:, 1] >= support['dbp_min']
        valid &= candidate[:, 1] <= support['dbp_max']
        valid &= pulse >= support['pulse_pressure_min']
        valid &= pulse <= support['pulse_pressure_max']
        outcomes[pending[valid]] = candidate[valid]
        pending = pending[~valid]

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': outcomes[:, 0],
        'dbp': outcomes[:, 1]
    }, columns=['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp'])
