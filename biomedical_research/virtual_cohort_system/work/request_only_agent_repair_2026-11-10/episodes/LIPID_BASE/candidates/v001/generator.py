import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Generate a wholly fictional cohort; spec is passed without a wrapper.

    Lipid units: mmol/L. No observed data, fitted target coefficients, or
    external IO are used. Latent lifestyle is deliberately not an output.
    """
    if observed is not None:
        raise ValueError('This generator is for whole-cohort generation only.')
    rng = np.random.default_rng(seed)
    n = int(spec['n'])
    female = rng.random(n) < spec['female_probability']
    sex = np.where(female, 'F', 'M')
    a = spec['age']
    age = a['minimum'] + (a['maximum'] - a['minimum']) * rng.beta(a['beta_a'], a['beta_b'], n)
    group = rng.choice(3, size=n, p=spec['lifestyle']['probabilities'])

    # Positive, right-skewed BMI. Group parameters describe means at age 40.
    b = spec['bmi']
    female_i = female.astype(int)
    means = np.asarray(b['mean_by_group_and_sex'])[group, female_i]
    sds = np.asarray(b['sd_by_group_and_sex'])[group, female_i]
    excess_mean = means - b['shift']
    sigma = np.sqrt(np.log1p((sds / excess_mean) ** 2))
    z_bmi = np.clip(rng.standard_normal(n), -8.0, 8.0)
    bmi = b['shift'] + excess_mean * np.exp(-0.5 * sigma**2 + sigma * z_bmi + b['log_excess_age_slope'] * (age - 40.0))

    # Total cholesterol is the sum of HDL and a positive non-HDL pool.
    # Independent component innovations do NOT imply zero TC/HDL correlation.
    # Latent lifestyle and the shared HDL component induce dependence.
    def component_mean(p):
        logmean = (np.log(p['reference_mean'])
                   + p['log_bmi_slope'] * (bmi - 22.0)
                   + p['log_age_slope'] * (age - 40.0)
                   + p['log_female_effect'] * female
                   + np.asarray(p['log_lifestyle_effects'])[group])
        return np.exp(logmean)

    h = spec['hdl']
    q = spec['non_hdl']
    hmean = component_mean(h)
    qmean = component_mean(q)
    # This numerical eight-SD bound has negligible effect on the intended
    # lognormal law and protects against numerical extremes, not clinical values.
    zh = np.clip(rng.standard_normal(n), -8.0, 8.0)
    zq_ind = np.clip(rng.standard_normal(n), -8.0, 8.0)
    rho = spec['component_log_innovation_correlation']
    zq = rho * zh + np.sqrt(1.0 - rho**2) * zq_ind
    hdl = hmean * np.exp(h['log_sd'] * zh - 0.5 * h['log_sd']**2)
    non_hdl = qmean * np.exp(q['log_sd'] * zq - 0.5 * q['log_sd']**2)
    total = hdl + non_hdl

    out = pd.DataFrame({
        'id': [f'SYN{i+1:06d}' for i in range(n)],
        'age': age,
        'sex': sex,
        'bmi': bmi,
        'total_cholesterol': total,
        'hdl_cholesterol': hdl,
    })
    assert out.shape == (n, 6)
    assert out['id'].is_unique
    assert (out['age'] >= 18).all()
    positive = out[['bmi', 'total_cholesterol', 'hdl_cholesterol']].to_numpy()
    assert np.isfinite(positive).all() and (positive > 0).all()
    return out
