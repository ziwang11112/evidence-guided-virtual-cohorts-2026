import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generator expects observed=None')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    d = spec['demography']
    bins = rng.choice(len(d['age_probabilities']), size=n, p=d['age_probabilities'])
    age = np.asarray(d['age_lower_bounds'], dtype=float)[bins] + rng.integers(0, 10, size=n)
    female = rng.binomial(1, np.asarray(d['female_probabilities'])[bins])
    a_bmi = (age - 45.0) / 10.0
    b = spec['bmi']
    mean_bmi = b['intercept'] + b['female'] * female + b['age_linear'] * a_bmi + b['age_quadratic'] * a_bmi**2
    sd_bmi = np.where(female == 1, b['sd_female'], b['sd_male'])
    excess = mean_bmi - b['lower_bound']
    bmi = b['lower_bound'] + rng.gamma((excess / sd_bmi)**2, sd_bmi**2 / excess)
    a = (age - 50.0) / 10.0
    x = (bmi - 25.0) / 5.0
    p = spec['bp']
    s = p['sbp_mean']
    q = p['dbp_mean']
    mu_s = s[0] + s[1]*a + s[2]*female + s[3]*x + s[4]*a*a + s[5]*female*a
    mu_d = q[0] + q[1]*a + q[2]*female + q[3]*x + q[4]*a*a + q[5]*female*a
    mu_pp = mu_s - mu_d
    vs = p['residual_sd_sbp']**2
    vd = p['residual_sd_dbp']**2
    csd = p['residual_rho'] * p['residual_sd_sbp'] * p['residual_sd_dbp']
    vp = vs + vd - 2.0*csd
    cdp = csd - vd
    if np.any(mu_d <= 0) or np.any(mu_pp <= 0) or vp <= 0:
        raise ValueError('Invalid positive BP component means or variance')
    logsd_d = np.sqrt(np.log1p(vd / mu_d**2))
    logsd_p = np.sqrt(np.log1p(vp / mu_pp**2))
    rho_log = np.log1p(cdp / (mu_d * mu_pp)) / (logsd_d * logsd_p)
    if np.any(np.abs(rho_log) >= 1):
        raise ValueError('Infeasible component covariance')
    z1 = rng.normal(size=n)
    z2 = rng.normal(size=n)
    dbp = mu_d * np.exp(logsd_d*z1 - 0.5*logsd_d**2)
    pulse_pressure = mu_pp * np.exp(logsd_p*(rho_log*z1 + np.sqrt(1-rho_log**2)*z2) - 0.5*logsd_p**2)
    sbp = dbp + pulse_pressure
    return pd.DataFrame({'row_id': np.arange(1,n+1,dtype=np.int64), 'age': age, 'female': female.astype(np.int64), 'bmi': bmi, 'sbp': sbp, 'dbp': dbp}, columns=['row_id','age','female','bmi','sbp','dbp'])
