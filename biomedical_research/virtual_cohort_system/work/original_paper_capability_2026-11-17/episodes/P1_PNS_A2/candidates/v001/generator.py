def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    ag = spec['age']
    k = rng.choice(len(ag['probabilities']), size=n, p=np.asarray(ag['probabilities']))
    low = np.asarray(ag['lower'], dtype=int)[k]
    high = np.asarray(ag['upper'], dtype=int)[k]
    age = rng.integers(low, high + 1).astype(float)
    a = (age - 50.0) / 10.0
    sx = spec['sex']
    female = (rng.random(n) < sx['p_at_20'] + sx['p_per_year'] * (age - 20.0)).astype(int)
    bm = spec['bmi']
    mean_bmi = bm['intercept'] + bm['female'] * female + bm['age_decade'] * a + bm['age_decade_squared'] * a*a
    sd_bmi = bm['sd_male'] + bm['sd_female_increment'] * female
    shifted_mean = mean_bmi - bm['lower_shift']
    ls = np.sqrt(np.log1p((sd_bmi / shifted_mean)**2))
    bmi = bm['lower_shift'] + shifted_mean * np.exp(ls * rng.standard_normal(n) - 0.5*ls*ls)
    b = (bmi - 25.0) / 5.0
    def pressure_mean(c):
        return c['intercept'] + c['age_decade']*a + c['age_decade_squared']*a*a + c['female']*female + c['female_age_decade']*female*a + c['bmi_per5']*b
    mu_s = pressure_mean(spec['sbp_mean'])
    mu_d = pressure_mean(spec['dbp_mean'])
    er = spec['conditional_dispersion']
    vs, vd = er['sd_sbp']**2, er['sd_dbp']**2
    cov_sd = er['rho']*er['sd_sbp']*er['sd_dbp']
    vpp = vs + vd - 2.0*cov_sd
    cov_dpp = cov_sd - vd
    md = mu_d - er['dbp_lower_shift']
    mp = mu_s - mu_d
    if np.any(md <= 0) or np.any(mp <= 0):
        raise ValueError('Nonpositive conditional shifted pressure mean')
    ld = np.sqrt(np.log1p(vd / (md*md)))
    lp = np.sqrt(np.log1p(vpp / (mp*mp)))
    latent_r = np.log1p(cov_dpp/(md*mp))/(ld*lp)
    if np.any(np.abs(latent_r) >= 1):
        raise ValueError('Incompatible conditional covariance')
    z1, z2 = rng.standard_normal((2, n))
    zp = latent_r*z1 + np.sqrt(1.0-latent_r*latent_r)*z2
    dbp = er['dbp_lower_shift'] + md*np.exp(ld*z1 - 0.5*ld*ld)
    pp = mp*np.exp(lp*zp - 0.5*lp*lp)
    sbp = dbp + pp
    return pd.DataFrame({'row_id':np.arange(1,n+1,dtype=np.int64), 'age':age, 'female':female, 'bmi':bmi, 'sbp':sbp, 'dbp':dbp}, columns=['row_id','age','female','bmi','sbp','dbp'])
