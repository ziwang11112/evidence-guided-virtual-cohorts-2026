def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    a = spec['age_law']
    age = np.floor(a['lower'] + a['width'] * rng.beta(a['alpha'], a['beta'], size=n)).astype(int)
    female = rng.binomial(1, spec['female_probability'], size=n)
    bl = spec['bmi_law']
    x = age.astype(float) - bl['age_center']
    means = bl['mean_male_at_center'] + bl['female_mean_increment'] * female + bl['age_linear'] * x + bl['age_quadratic'] * x*x
    sds = np.where(female == 1, bl['sd_female'], bl['sd_male'])
    excess = means - bl['lower_shift']
    bmi = bl['lower_shift'] + rng.gamma((excess/sds)**2, sds*sds/excess)
    bp = spec['bp_mean']
    t = age.astype(float) - bp['age_center']
    z = bmi - bp['bmi_center']
    mean_s = (bp['sbp_intercept_male'] + bp['sbp_female'] * female + bp['sbp_age_linear'] * t + bp['sbp_age_quadratic'] * t*t + bp['sbp_female_older_age'] * female * np.maximum(t, 0.0) + bp['sbp_bmi_per_kg_m2'] * z)
    mean_d = (bp['dbp_intercept_male'] + bp['dbp_female'] * female + bp['dbp_age_linear'] * t + bp['dbp_age_quadratic'] * t*t + bp['dbp_bmi_per_kg_m2'] * z)
    mean_p = mean_s - mean_d
    r = spec['conditional_bp_residuals']
    vs, vd = r['sd_sbp']**2, r['sd_dbp']**2
    csd = r['rho'] * r['sd_sbp'] * r['sd_dbp']
    vp = vs + vd - 2.0*csd
    cdp = csd - vd
    # Joint lognormal diastolic pressure and pulse pressure, calibrated
    # pointwise to constant conditional variances and covariance.
    logsd_d = np.sqrt(np.log1p(vd / mean_d**2))
    logsd_p = np.sqrt(np.log1p(vp / mean_p**2))
    latent_rho = np.log1p(cdp / (mean_d*mean_p)) / (logsd_d*logsd_p)
    if np.any(mean_d <= 0) or np.any(mean_p <= 0) or np.any(np.abs(latent_rho) >= 1):
        raise ValueError('Invalid positive-pressure moment specification')
    u = rng.normal(size=n)
    v = rng.normal(size=n)
    dbp = mean_d * np.exp(logsd_d*u - 0.5*logsd_d**2)
    pp = mean_p * np.exp(logsd_p*(latent_rho*u + np.sqrt(1-latent_rho**2)*v) - 0.5*logsd_p**2)
    sbp = dbp + pp
    return pd.DataFrame({'row_id': np.arange(1,n+1,dtype=np.int64), 'age': age, 'female': female, 'bmi': bmi, 'sbp': sbp, 'dbp': dbp}, columns=['row_id','age','female','bmi','sbp','dbp'])
