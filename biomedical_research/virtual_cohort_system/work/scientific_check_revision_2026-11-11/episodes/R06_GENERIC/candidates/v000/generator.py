import numpy as np
import pandas as pd
from scipy.stats import gamma, lognorm


def generate(observed, spec, seed):
    """Generate a fictional, complete adult cohort; no measured individuals used."""
    if observed is not None:
        raise ValueError('This generator is for whole-cohort generation only.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    female = rng.random(n) < spec['female_probability']
    sex = np.where(female, 'F', 'M')
    # Latent strata are scenario assumptions, not recovered participant labels.
    group = rng.choice(3, size=n, p=spec['lifestyle_probabilities'])
    a = spec['age']
    upper_cdf = gamma.cdf(a['upper'] - a['lower'], a=a['shape'], scale=a['scale'])
    age = a['lower'] + gamma.ppf(rng.uniform(0.0, upper_cdf, n), a=a['shape'], scale=a['scale'])
    b = spec['bmi']
    nominal_mean = np.where(female, np.asarray(b['female_means'])[group], np.asarray(b['male_means'])[group])
    nominal_mean = nominal_mean + b['age_linear'] * (age - spec['age_reference']) - b['late_age_quadratic'] * np.maximum(age - b['late_age_start'], 0.0)**2
    cv = np.where(female, np.asarray(b['female_shifted_cv'])[group], np.asarray(b['male_shifted_cv'])[group])
    bsigma = np.sqrt(np.log1p(cv**2))
    bscale = (nominal_mean - b['lower']) * np.exp(-0.5 * bsigma**2)
    # Inverse-CDF sampling of a shifted lognormal on (12,55), no clipping or row deletion.
    b_cdf = lognorm.cdf(b['upper'] - b['lower'], s=bsigma, scale=bscale)
    bmi = b['lower'] + lognorm.ppf(rng.uniform(size=n) * b_cdf, s=bsigma, scale=bscale)

    p = spec['lipids']
    # Arithmetic conditional means, in order HDL, LDL, remnant cholesterol.
    x_bmi = bmi - spec['bmi_reference']
    x_age = age - spec['age_reference']
    x_group = group - np.dot(np.arange(3), spec['lifestyle_probabilities'])
    mu = np.empty((n, 3))
    for j in range(3):
        mu[:, j] = (p['base_mean'][j]
                    + p['female_effect'][j] * female.astype(float)
                    + p['male_effect'][j] * (~female).astype(float)
                    + p['bmi_slopes'][j] * x_bmi
                    + p['age_slopes'][j] * x_age
                    + p['lifestyle_slopes'][j] * x_group)
    if not np.all(mu > 0):
        raise ValueError('Conditional lipid means must be positive; check modified specification.')
    sigma = np.sqrt(np.log1p(np.asarray(p['conditional_cv'])**2))
    chol = np.linalg.cholesky(np.asarray(p['latent_residual_correlation'], dtype=float))
    z = rng.standard_normal((n, 3)) @ chol.T
    components = mu * np.exp(z * sigma - 0.5 * sigma**2)
    hdl = components[:, 0]
    total = components.sum(axis=1)
    result = pd.DataFrame({
        'id': [f'fictional_adult_{i+1:06d}' for i in range(n)],
        'age': age,
        'sex': sex,
        'bmi': bmi,
        'total_cholesterol': total,
        'hdl_cholesterol': hdl
    }, columns=['id', 'age', 'sex', 'bmi', 'total_cholesterol', 'hdl_cholesterol'])
    values = result[['age', 'bmi', 'total_cholesterol', 'hdl_cholesterol']].to_numpy()
    assert len(result) == 3000 and result['id'].is_unique
    assert np.isfinite(values).all() and (values[:, 1:] > 0).all()
    assert (result['age'] >= 18).all() and set(result['sex']).issubset({'F', 'M'})
    return result
