import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Generate a wholly fictional adult cohort; no observed records are used."""
    if observed is not None:
        raise ValueError('This generator is for whole-cohort generation only.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    female = rng.random(n) < spec['female_probability']
    sex = np.where(female, 'F', 'M')
    a = spec['age']
    age = np.floor(a['minimum'] + a['span'] * rng.beta(a['beta_a'], a['beta_b'], n)).astype(int)

    # This is an assumed recruitment mixture, not a measured lifestyle variable.
    settled = rng.random(n) < spec['settled_probability']
    b = spec['bmi']
    group_mean = np.where(settled,
        np.where(female, b['settled_mean_F'], b['settled_mean_M']),
        np.where(female, b['active_mean_F'], b['active_mean_M']))
    group_sd = np.where(settled,
        np.where(female, b['settled_sd_F'], b['settled_sd_M']),
        np.where(female, b['active_sd_F'], b['active_sd_M']))
    mean_bmi = (group_mean + b['age_slope'] * (age-b['reference_age'])
                - b['older_age_curvature'] * np.maximum(age-b['older_age_start'], 0)**2)
    bmi_sigma = np.sqrt(np.log1p((group_sd/mean_bmi)**2))
    log_bmi = np.log(mean_bmi) - 0.5*bmi_sigma**2 + bmi_sigma*rng.standard_normal(n)
    bmi = np.exp(np.clip(log_bmi, -30, 30))

    # Correlated lognormal lipids with specified conditional arithmetic means.
    # Lifestyle affects lipids through BMI only; no unmeasured direct group effect.
    l = spec['lipids']
    delta_bmi = bmi - l['reference_bmi']
    delta_age = age - l['reference_age']
    log_mean_tc = (np.log(np.where(female, l['tc_mean_F'], l['tc_mean_M']))
                   + l['tc_log_bmi_slope']*delta_bmi
                   + np.where(female, l['tc_log_age_F'], l['tc_log_age_M'])*delta_age)
    log_mean_hdl = (np.log(np.where(female, l['hdl_mean_F'], l['hdl_mean_M']))
                    + l['hdl_log_bmi_slope']*delta_bmi
                    + l['hdl_log_age_slope']*delta_age)
    st = np.where(female, l['tc_log_residual_sd_F'], l['tc_log_residual_sd_M'])
    sh = np.where(female, l['hdl_log_residual_sd_F'], l['hdl_log_residual_sd_M'])
    z1 = rng.standard_normal(n)
    z2 = rng.standard_normal(n)
    rho = l['log_residual_correlation']
    log_tc = log_mean_tc - 0.5*st**2 + st*z1
    log_hdl = log_mean_hdl - 0.5*sh**2 + sh*(rho*z1 + np.sqrt(1-rho**2)*z2)
    tc = np.exp(np.clip(log_tc, -30, 30))
    hdl = np.exp(np.clip(log_hdl, -30, 30))
    result = pd.DataFrame({
        'id': [f'SYN{i:06d}' for i in range(1,n+1)],
        'age': age,
        'sex': sex,
        'bmi': bmi,
        'total_cholesterol': tc,
        'hdl_cholesterol': hdl
    })
    values = result[['age','bmi','total_cholesterol','hdl_cholesterol']].to_numpy()
    if not np.isfinite(values).all() or not (result[['bmi','total_cholesterol','hdl_cholesterol']].to_numpy()>0).all():
        raise RuntimeError('Unexpected nonfinite or nonpositive generation.')
    return result
