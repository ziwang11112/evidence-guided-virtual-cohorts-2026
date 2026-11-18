import numpy as np
import pandas as pd
from scipy.optimize import root

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generation expects observed=None')
    rng = np.random.default_rng(seed)
    n = int(spec['n'])
    p_source = np.array([1.0-spec['source_female_fraction'], spec['source_female_fraction']])
    grid = np.arange(35.,75.)
    x = (grid-52.)/10.
    refs = []
    def bmi_age(a):
        return spec['bmi_age_slope']*(a-52.)-spec['bmi_age_downturn']*np.maximum(a-55.,0.)**2
    def bp_age(a, female, outcome):
        if outcome == 'sbp':
            return spec['sbp_age_slopes'][female]*(a-52.)+spec['sbp_late_slope']*np.maximum(a-55.,0.)
        return spec['dbp_age_slopes'][female]*(a-52.)-spec['dbp_late_decline']*np.maximum(a-55.,0.)
    for f in [0,1]:
        src = spec['source_moments'][f]
        target_m = (src['age_mean']-52.)/10.
        target_m2 = (src['age_sd']/10.)**2+target_m**2
        def weights(theta):
            z = theta[0]*x+theta[1]*x*x
            w = np.exp(z-z.max())
            return w/w.sum()
        def eq(theta):
            w = weights(theta)
            return np.array([w@x-target_m,w@(x*x)-target_m2])
        sol = root(eq,[0.,-0.5])
        if not sol.success or np.max(np.abs(eq(sol.x)))>1e-7:
            raise RuntimeError('Source age moment calibration failed')
        w = weights(sol.x)
        g = bmi_age(grid)
        gbar = float(w@g)
        gc = g-gbar
        vg = float(w@(gc*gc))
        bmi_var_res = src['bmi_sd']**2-vg
        if bmi_var_res <= 0:
            raise ValueError('Inconsistent BMI variance assumptions')
        ref = {'w':w,'gbar':gbar,'vg':vg,'bmi_var_res':bmi_var_res}
        for outcome in ['sbp','dbp']:
            h = bp_age(grid,f,outcome)
            hc = h-w@h
            ref[outcome]={'hbar':float(w@h),'vh':float(w@(hc*hc)),'cov_hg':float(w@(hc*gc))}
        refs.append(ref)
    # Algebra: transfer published partial r to the age/sex-residualized
    # BMI and pressure variables in the source reference mixture.
    # V_pressure = Var(h + b*g) + b^2*V_BMI_res/r^2.
    vbr = sum(p_source[f]*refs[f]['bmi_var_res'] for f in [0,1])
    vg = sum(p_source[f]*refs[f]['vg'] for f in [0,1])
    slopes = {}
    for outcome in ['sbp','dbp']:
        r = spec['intersalt_partial_r'][outcome]
        vh = sum(p_source[f]*refs[f][outcome]['vh'] for f in [0,1])
        cov = sum(p_source[f]*refs[f][outcome]['cov_hg'] for f in [0,1])
        vy = sum(p_source[f]*spec['source_moments'][f][outcome+'_sd']**2 for f in [0,1])
        aa = vbr/(r*r)+vg
        bb = 2.*cov
        cc = vh-vy
        disc = bb*bb-4.*aa*cc
        if disc <= 0:
            raise ValueError('Inconsistent partial correlation assumptions')
        b = (-bb+np.sqrt(disc))/(2.*aa)
        slopes[outcome] = b
        for f in [0,1]:
            rr = refs[f][outcome]
            vv = spec['source_moments'][f][outcome+'_sd']**2 - (rr['vh']+2.*b*rr['cov_hg']+b*b*refs[f]['vg'])-b*b*refs[f]['bmi_var_res']
            if vv <= 0:
                raise ValueError('Nonpositive pressure innovation variance')
            rr['innovation_sd'] = np.sqrt(vv)
    bands = rng.choice(len(spec['age_band_probabilities']),size=n,p=spec['age_band_probabilities'])
    age = 20+10*bands+rng.integers(0,10,size=n)
    female = (rng.random(n)<np.array(spec['female_probability_by_band'])[bands]).astype(np.int64)
    bmi = np.empty(n)
    mu_s = np.empty(n)
    mu_d = np.empty(n)
    sd_s = np.empty(n)
    sd_d = np.empty(n)
    for f in [0,1]:
        ix = np.flatnonzero(female==f)
        a = age[ix].astype(float)
        ref = refs[f]
        src = spec['source_moments'][f]
        m = src['bmi_mean']+bmi_age(a)-ref['gbar']
        # Shifted lognormal with an age-invariant conditional variance.
        shifted_mean = m-spec['bmi_floor']
        if np.any(shifted_mean<=0):
            raise ValueError('Invalid BMI mean')
        logvar = np.log1p(ref['bmi_var_res']/shifted_mean**2)
        logmean = np.log(shifted_mean)-0.5*logvar
        bmi[ix] = spec['bmi_floor']+np.exp(logmean+np.sqrt(logvar)*rng.standard_normal(len(ix)))
        for outcome,mu_arr,sd_arr in [('sbp',mu_s,sd_s),('dbp',mu_d,sd_d)]:
            mu_arr[ix] = src[outcome+'_mean']+bp_age(a,f,outcome)-ref[outcome]['hbar']+slopes[outcome]*(bmi[ix]-src['bmi_mean'])
            sd_arr[ix] = ref[outcome]['innovation_sd']
    rho = float(spec['residual_rho'])
    if not -1.<rho<1.:
        raise ValueError('Invalid residual correlation')
    sbp = np.empty(n)
    dbp = np.empty(n)
    pending = np.arange(n)
    for attempt in range(10000):
        if pending.size==0:
            break
        z1 = rng.standard_normal(pending.size)
        z2 = rng.standard_normal(pending.size)
        ss = mu_s[pending]+sd_s[pending]*z1
        dd = mu_d[pending]+sd_d[pending]*(rho*z1+np.sqrt(1.-rho*rho)*z2)
        good = (ss>=spec['sbp_bounds'][0]) & (ss<=spec['sbp_bounds'][1]) & (dd>=spec['dbp_bounds'][0]) & (dd<=spec['dbp_bounds'][1]) & (ss-dd>=spec['min_pulse_pressure'])
        sbp[pending[good]] = ss[good]
        dbp[pending[good]] = dd[good]
        pending = pending[~good]
    if pending.size:
        raise RuntimeError('BP pair rejection did not converge')
    # Numeric precision only; no forced empirical coefficients or ranks.
    return pd.DataFrame({'row_id':np.arange(1,n+1,dtype=np.int64),'age':age.astype(float),'female':female,'bmi':np.round(bmi,4),'sbp':np.round(sbp,3),'dbp':np.round(dbp,3)})
