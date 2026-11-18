import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri


def generate(observed, spec, seed):
    """Generate a wholly fictional adult cohort; all lipids are in mmol/L."""
    if observed is not None:
        raise ValueError('This generator is for whole-cohort generation only.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    female = rng.random(n) < spec['female_probability']
    male = (~female).astype(float)
    sex = np.where(female, 'F', 'M')
    age_cfg = spec['age']
    age = age_cfg['minimum'] + (age_cfg['maximum'] - age_cfg['minimum']) * rng.beta(age_cfg['beta_a'], age_cfg['beta_b'], n)
    group = rng.choice(3, size=n, p=spec['mixture']['probabilities'])
    b = spec['bmi']
    base_mean = np.where(female, np.asarray(b['female_means'])[group], np.asarray(b['male_means'])[group])
    base_sd = np.where(female, np.asarray(b['female_sds'])[group], np.asarray(b['male_sds'])[group])
    age_shift = b['age_slope_to_50'] * (np.minimum(age, 50.0) - 38.0) + b['age_slope_after_50'] * np.maximum(age - 50.0, 0.0)
    bmi_mean = base_mean + age_shift
    # Inverse-CDF truncated lognormal: no clipping, missing records, or row removal.
    log_sd = np.sqrt(np.log1p((base_sd / bmi_mean) ** 2))
    log_mean = np.log(bmi_mean) - 0.5 * log_sd ** 2
    p_lo = ndtr((np.log(b['lower_bound']) - log_mean) / log_sd)
    p_hi = ndtr((np.log(b['upper_bound']) - log_mean) / log_sd)
    u = p_lo + (p_hi - p_lo) * rng.random(n)
    u = np.clip(u, np.finfo(float).eps, 1.0 - np.finfo(float).eps)
    bmi = np.exp(log_mean + log_sd * ndtri(u))
    lip = spec['lipids']
    hdl_mean = (lip['hdl_at_reference_female'] + lip['hdl_male_difference'] * male
                + np.asarray(lip['hdl_group_offsets'])[group]
                + lip['hdl_per_year'] * (age - 40.0)
                + lip['hdl_per_bmi'] * (bmi - 22.0))
    nonhdl_mean = (lip['nonhdl_at_reference_female'] + lip['nonhdl_male_difference'] * male
                   + np.asarray(lip['nonhdl_group_offsets'])[group]
                   + lip['nonhdl_per_year'] * (age - 40.0)
                   + lip['nonhdl_per_bmi'] * (bmi - 22.0))
    if np.any(hdl_mean <= 0) or np.any(nonhdl_mean <= 0):
        raise ValueError('Nonpositive conditional mean under supplied specification.')
    z_h = rng.standard_normal(n)
    rho = lip['log_error_correlation_hdl_nonhdl']
    z_n = rho * z_h + np.sqrt(1.0 - rho ** 2) * rng.standard_normal(n)
    sh = np.sqrt(np.log1p(lip['hdl_cv'] ** 2))
    sn = np.sqrt(np.log1p(lip['nonhdl_cv'] ** 2))
    hdl = hdl_mean * np.exp(sh * z_h - 0.5 * sh ** 2)
    nonhdl = nonhdl_mean * np.exp(sn * z_n - 0.5 * sn ** 2)
    total = hdl + nonhdl
    result = pd.DataFrame({
        'id': ['SYN%05d' % (i + 1) for i in range(n)],
        'age': age,
        'sex': sex,
        'bmi': bmi,
        'total_cholesterol': total,
        'hdl_cholesterol': hdl
    })
    assert result.shape == (n, 6)
    vals = result[['age', 'bmi', 'total_cholesterol', 'hdl_cholesterol']].to_numpy()
    assert np.isfinite(vals).all()
    assert (vals[:, 0] >= 18.0).all() and (vals[:, 1:] > 0).all()
    return result
