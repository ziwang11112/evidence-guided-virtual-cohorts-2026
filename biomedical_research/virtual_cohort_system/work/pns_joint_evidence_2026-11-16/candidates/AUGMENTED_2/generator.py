import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    task = spec['task']
    m = spec['model']
    n = int(task['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative')
    rng = np.random.default_rng(seed)

    # Every location and scale below is a population parameter, not a sample statistic.
    def centered_beta(bounds, variance):
        lo, hi = map(float, bounds)
        variance = float(variance)
        if not (lo < 0.0 < hi and 0.0 < variance < -lo * hi):
            raise ValueError('Invalid bounded mean-zero beta parameters')
        p = -lo / (hi - lo)
        concentration = (-lo * hi) / variance - 1.0
        return lo + (hi - lo) * rng.beta(
            p * concentration, (1.0 - p) * concentration, size=n
        )

    ag = m['age']
    age = ag['lower'] + (ag['upper'] - ag['lower']) * rng.beta(
        ag['beta_alpha'], ag['beta_beta'], size=n
    )
    female = rng.binomial(1, m['female_probability'], size=n).astype(np.int64)

    c = m['coordinates']
    age_c = (age - c['age_center']) / c['age_scale']
    bm = m['bmi']
    bmi_mean = (
        bm['conditional_mean_at_age50_male']
        + bm['age_effect_per_decade'] * age_c
        + bm['female_increment'] * female
    )
    bmi_p = (bmi_mean - bm['lower']) / (bm['upper'] - bm['lower'])
    if np.any((bmi_p <= 0.0) | (bmi_p >= 1.0)):
        raise ValueError('Conditional BMI mean must lie inside BMI support')
    concentration = float(bm['beta_concentration'])
    if concentration <= 0.0:
        raise ValueError('BMI concentration must be positive')
    bmi = bm['lower'] + (bm['upper'] - bm['lower']) * rng.beta(
        concentration * bmi_p, concentration * (1.0 - bmi_p)
    )
    bmi_c = (bmi - c['bmi_center']) / c['bmi_scale']
    X = np.column_stack((np.ones(n), age_c, female, bmi_c))

    bp = m['bp']
    mu_s = X @ np.asarray(bp['sbp_coefficients'], dtype=float)
    mu_d = X @ np.asarray(bp['dbp_coefficients'], dtype=float)
    r = bp['residual']
    sigma_s = float(r['sbp_sd'])
    sigma_d = float(r['dbp_sd'])
    rho = float(r['correlation'])
    if not (sigma_s > 0.0 and sigma_d > 0.0 and -1.0 < rho < 1.0):
        raise ValueError('Invalid BP residual covariance parameters')

    error_d = centered_beta(r['dbp_error_bounds'], sigma_d ** 2)
    innovation_s = centered_beta(
        r['sbp_innovation_bounds'], sigma_s ** 2 * (1.0 - rho ** 2)
    )
    loading = rho * sigma_s / sigma_d
    dbp = mu_d + error_d
    sbp = mu_s + loading * error_d + innovation_s

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': sbp,
        'dbp': dbp
    }, columns=['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp'])
