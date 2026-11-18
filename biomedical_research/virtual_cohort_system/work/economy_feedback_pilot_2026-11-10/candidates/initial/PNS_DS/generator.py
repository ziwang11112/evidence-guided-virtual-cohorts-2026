import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    task = spec['task']
    m = spec['model']
    n = int(task['n_rows'])
    rng = np.random.default_rng(seed)
    cov = m['covariate_distributions']
    age = rng.uniform(cov['age']['lower'], cov['age']['upper'], size=n)
    female = rng.binomial(1, cov['female']['p'], size=n).astype(int)
    b = cov['bmi']
    cv = b['sd'] / b['mean']
    sigma_log = np.sqrt(np.log(1.0 + cv * cv))
    mu_log = np.log(b['mean']) - 0.5 * sigma_log * sigma_log
    bmi = rng.lognormal(mu_log, sigma_log, size=n)
    om = m['outcome_model']
    age_c = (age - om['design_center']['age_years']) / om['design_scale_age_years']
    bmi_c = (bmi - om['design_center']['bmi_kgm2']) / om['design_scale_bmi_kgm2']
    lp = om['linear_predictors']
    mu_sbp = (
        lp['sbp']['intercept_at_center']
        + lp['sbp']['age_per_10y'] * age_c
        + lp['sbp']['female_difference'] * female
        + lp['sbp']['bmi_per_5kgm2'] * bmi_c
    )
    mu_dbp = (
        lp['dbp']['intercept_at_center']
        + lp['dbp']['age_per_10y'] * age_c
        + lp['dbp']['female_difference'] * female
        + lp['dbp']['bmi_per_5kgm2'] * bmi_c
    )
    res = om['residual']
    s_s = res['sigma_sbp_mmHg']
    s_d = res['sigma_dbp_mmHg']
    rho = res['correlation']
    residual = rng.multivariate_normal(
        mean=[0.0, 0.0],
        cov=[[s_s * s_s, rho * s_s * s_d], [rho * s_s * s_d, s_d * s_d]],
        size=n
    )
    sbp = mu_sbp + residual[:, 0]
    dbp = mu_dbp + residual[:, 1]
    out = {
        'row_id': np.arange(1, n + 1),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': sbp,
        'dbp': dbp
    }
    df = pd.DataFrame(out)
    return df[task['columns']]
