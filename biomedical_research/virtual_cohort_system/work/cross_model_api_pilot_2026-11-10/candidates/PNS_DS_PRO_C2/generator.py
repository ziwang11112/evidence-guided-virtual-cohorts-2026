import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('observed must be None')
    task = spec['task']
    model = spec['model']
    n_rows = task['n_rows']
    rng = np.random.default_rng(seed)

    age_cfg = model['age']
    age = np.empty(n_rows)
    for i in range(n_rows):
        while True:
            value = rng.normal(age_cfg['mean'], age_cfg['sd'])
            if age_cfg['lower'] <= value <= age_cfg['upper']:
                age[i] = value
                break

    female = rng.binomial(1, model['female']['prob'], n_rows).astype(int)

    bmi_cfg = model['bmi']
    age_c = (age - 50.0) / 10.0
    bmi_mu = bmi_cfg['mean_intercept'] + bmi_cfg['mean_age10'] * age_c + bmi_cfg['female_shift'] * female
    bmi = np.empty(n_rows)
    for i in range(n_rows):
        while True:
            value = rng.normal(bmi_mu[i], bmi_cfg['sd'])
            if bmi_cfg['lower'] <= value <= bmi_cfg['upper']:
                bmi[i] = value
                break

    bmi_c = (bmi - 25.0) / 5.0
    beta_s = model['bp']['beta_sbp']
    beta_d = model['bp']['beta_dbp']
    mu_sbp = (beta_s['intercept'] + beta_s['age_c'] * age_c + beta_s['female'] * female + beta_s['bmi_c'] * bmi_c)
    mu_dbp = (beta_d['intercept'] + beta_d['age_c'] * age_c + beta_d['female'] * female + beta_d['bmi_c'] * bmi_c)

    sd_s = model['bp']['residual_sd']['sbp']
    sd_d = model['bp']['residual_sd']['dbp']
    rho = model['bp']['residual_correlation']
    cov_sd = rho * sd_s * sd_d
    eps = rng.multivariate_normal([0.0, 0.0], [[sd_s * sd_s, cov_sd], [cov_sd, sd_d * sd_d]], size=n_rows)
    sbp = mu_sbp + eps[:, 0]
    dbp = mu_dbp + eps[:, 1]

    columns = [column['name'] for column in task['columns']]
    df = pd.DataFrame({
        'row_id': np.arange(1, n_rows + 1, dtype=int),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': sbp,
        'dbp': dbp
    })
    return df[columns]
