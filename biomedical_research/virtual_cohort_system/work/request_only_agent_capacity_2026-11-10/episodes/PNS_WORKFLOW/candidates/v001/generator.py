def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd
    from scipy.special import expit
    rng = np.random.default_rng(seed)
    n = int(spec['n'])
    ag = spec['demography']
    group = rng.choice(len(ag['age_probabilities']), size=n, p=ag['age_probabilities'])
    edges = np.asarray(ag['age_edges'], dtype=int)
    age = edges[group] + np.floor(rng.random(n) * (edges[group+1]-edges[group])).astype(int)
    pf = expit(ag['female_logit_at_45'] + ag['female_logit_age_slope']*(age-45))
    female = rng.binomial(1, pf, n)
    b = spec['bmi_model']
    a = age - spec['reference']['age_mean']
    mean_bmi = b['reference_mean'] + b['age_linear']*a + b['age_quadratic']*a*a + b['female_effect']*(female-spec['reference']['female_fraction'])
    sd_bmi = np.where(female==1, b['sd_female'], b['sd_male'])
    shifted_mean = mean_bmi-b['shift']
    logs = np.sqrt(np.log1p((sd_bmi/shifted_mean)**2))
    logmu = np.log(shifted_mean)-0.5*logs*logs
    bmi = b['shift'] + np.exp(logmu+logs*rng.standard_normal(n))
    bad = (bmi < b['bounds'][0]) | (bmi > b['bounds'][1])
    while np.any(bad):
        bmi[bad] = b['shift']+np.exp(logmu[bad]+logs[bad]*rng.standard_normal(int(bad.sum())))
        bad = (bmi < b['bounds'][0]) | (bmi > b['bounds'][1])
    p = spec['bp_model']
    ref = spec['reference']
    # Approximate sequential variance budget in the external reference population.
    vage, vf, vb = ref['age_sd']**2, ref['female_fraction']*(1-ref['female_fraction']), b['reference_sd']**2
    vs0 = ref['sbp_sd']**2 - p['sbp_age_linear']**2*vage - p['sbp_female_effect']**2*vf
    vd0 = ref['dbp_sd']**2 - p['dbp_age_linear']**2*vage - p['dbp_female_effect']**2*vf
    bs, bd = p['sbp_bmi_slope_per_unit'], p['dbp_bmi_slope_per_unit']
    vs, vd = vs0-bs*bs*vb, vd0-bd*bd*vb
    r_proxy = np.sin(np.pi*p['external_kendall_tau']/2.0)
    cov = r_proxy*np.sqrt(vs0*vd0)-bs*bd*vb
    rho = cov/np.sqrt(vs*vd)
    if not (vs>0 and vd>0 and abs(rho)<1):
        raise ValueError('Invalid external variance-budget assumptions')
    f = female-ref['female_fraction']
    ms = ref['sbp_mean'] + p['sbp_age_linear']*a + p['sbp_age_quadratic']*(a*a-vage) + p['sbp_female_effect']*f + bs*(bmi-b['reference_mean'])
    md = ref['dbp_mean'] + p['dbp_age_linear']*a + p['dbp_age_quadratic']*(a*a-vage) + p['dbp_female_effect']*f + bd*(bmi-b['reference_mean'])
    sbp = np.empty(n)
    dbp = np.empty(n)
    todo = np.arange(n)
    step = p['rounding_step']
    while len(todo):
        z = rng.standard_normal((len(todo),2))
        s = ms[todo] + np.sqrt(vs)*z[:,0]
        d = md[todo] + np.sqrt(vd)*(rho*z[:,0]+np.sqrt(1-rho*rho)*z[:,1])
        s = np.round(s/step)*step
        d = np.round(d/step)*step
        keep = ((s>=p['sbp_bounds'][0]) & (s<=p['sbp_bounds'][1]) & (d>=p['dbp_bounds'][0]) & (d<=p['dbp_bounds'][1]) & (s-d>=p['minimum_pulse_pressure']))
        sbp[todo[keep]], dbp[todo[keep]] = s[keep], d[keep]
        todo = todo[~keep]
    return pd.DataFrame({'row_id':np.arange(1,n+1,dtype=np.int64), 'age':age, 'female':female.astype(np.int64), 'bmi':bmi, 'sbp':sbp, 'dbp':dbp}, columns=['row_id','age','female','bmi','sbp','dbp'])
