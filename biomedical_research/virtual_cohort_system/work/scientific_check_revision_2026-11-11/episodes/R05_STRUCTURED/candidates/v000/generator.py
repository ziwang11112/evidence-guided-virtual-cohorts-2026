import numpy as np
import pandas as pd
from scipy.special import expit


def analyze_cohort(df, flexible_age=False):
    """OLS associations in the fictional data, not causal effects or source estimates."""
    a = (df['age'].to_numpy(dtype=float) - 45.0) / 10.0
    f = df['female'].to_numpy(dtype=float)
    b5 = (df['bmi'].to_numpy(dtype=float) - 27.0) / 5.0
    terms = [np.ones(len(df)), a, f]
    if flexible_age:
        terms.extend([a*a, a*a*a, a*f])
    terms.append(b5)
    X = np.column_stack(terms)
    Y = df[['sbp', 'dbp']].to_numpy(dtype=float)
    coef = np.linalg.lstsq(X, Y, rcond=None)[0]
    residual = Y-X@coef
    dof = len(df)-X.shape[1]
    variances = (residual**2).sum(axis=0)/dof
    se = np.sqrt(np.linalg.inv(X.T@X)[-1,-1]*variances)
    return {'age_adjustment': 'cubic_age_plus_age_sex_interaction' if flexible_age else 'linear_age',
            'sbp_bmi_slope_per_5': float(coef[-1,0]),
            'dbp_bmi_slope_per_5': float(coef[-1,1]),
            'sbp_slope_se': float(se[0]), 'dbp_slope_se': float(se[1]),
            'residual_pearson_r': float(np.corrcoef(residual.T)[0,1])}


def generate(observed, spec, seed):
    """Independent equal-weight fictional adults; no target data are used."""
    if observed is not None:
        raise ValueError('This generator is whole-cohort only.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    # Shared uncertainty denotes cross-population transport, not sampling CIs.
    if spec['draw_transport_parameters']:
        z = rng.normal(size=2)
        beta_s = spec['bmi_effect_per5'][0] + spec['transport_effect_sd'][0]*z[0]
        beta_d = spec['bmi_effect_per5'][1] + spec['transport_effect_sd'][1]*(0.6*z[0]+0.8*z[1])
        person_rho = rng.uniform(*spec['person_residual_rho_range'])
    else:
        beta_s, beta_d = spec['bmi_effect_per5']
        person_rho = float(np.mean(spec['person_residual_rho_range']))

    group = rng.choice(6, size=n, p=spec['age_bin_probabilities'])
    age = 20 + 10*group + rng.integers(0, 10, size=n)
    female = rng.binomial(1, np.asarray(spec['female_probability_by_age_bin'])[group])
    knots = np.asarray(spec['age_knots'], dtype=float)
    mean_bmi = np.interp(age, knots, spec['bmi_mean_at_age_knots']) + 0.5*(female-0.54)
    sd_bmi = np.where(female==1, 4.9, 4.0)
    log_sigma = np.sqrt(np.log1p((sd_bmi/mean_bmi)**2))
    log_mu = np.log(mean_bmi)-0.5*log_sigma**2
    bmi = rng.lognormal(log_mu, log_sigma)
    bad = (bmi<15.0)|(bmi>55.0)
    while bad.any():
        bmi[bad] = rng.lognormal(log_mu[bad], log_sigma[bad])
        bad = (bmi<15.0)|(bmi>55.0)

    bp_knots = np.asarray(spec['bp_reference_age_knots'], dtype=float)
    def interp_sex(key):
        vals = spec[key]
        return np.where(female==1,
                        np.interp(age, bp_knots, vals['female']),
                        np.interp(age, bp_knots, vals['male']))
    # Reference Mexican age-sex means evaluated at native age-sex BMI means.
    bmi_reference = interp_sex('reference_bmi')
    # A weak older-age attenuation is an assumed transport of qualitative evidence.
    atten = 1.0 - 0.15*np.clip((age-60.0)/19.0, 0.0, 1.0)
    mu_s = interp_sex('reference_sbp') + beta_s*atten*(bmi-bmi_reference)/5.0
    mu_d = interp_sex('reference_dbp') + beta_d*atten*(bmi-bmi_reference)/5.0
    # Marginal observed-pressure model: includes treated/untreated implicitly;
    # no untreated BP correction, treatment assignment, HbA1c or HTN selection.
    sd_s = np.clip(14.0+0.12*(age-45.0), 11.0, 18.2)
    sd_d = np.clip(8.8+0.015*(age-45.0), 8.3, 9.4)

    def correlated_normals(m, rho):
        z = rng.normal(size=(m, 2))
        return np.column_stack([z[:,0], rho*z[:,0]+np.sqrt(1.0-rho*rho)*z[:,1]])

    def pressure_pair(indices):
        m = len(indices)
        person = correlated_normals(m, person_rho)*np.column_stack([sd_s[indices], sd_d[indices]])
        visit = correlated_normals(m, spec['visit_error_rho'])*np.array(spec['visit_error_sd'])
        readings = []
        for k in range(3):
            read_error = correlated_normals(m, spec['reading_error_rho'])*np.array(spec['reading_error_sd'])
            offset = np.array(spec['first_reading_offset']) if k==0 else np.zeros(2)
            readings.append(np.column_stack([mu_s[indices],mu_d[indices]])+person+visit+read_error+offset)
        readings = np.stack(readings,axis=1)
        if spec['bp_aggregation']=='mean_last_two':
            return readings[:,1:,:].mean(axis=1)
        if spec['bp_aggregation']=='mean_three':
            return readings.mean(axis=1)
        if spec['bp_aggregation']=='last':
            return readings[:,2,:]
        raise ValueError('Unknown bp_aggregation')

    bp = pressure_pair(np.arange(n))
    def invalid(x):
        return (x[:,0]<60.0)|(x[:,0]>270.0)|(x[:,1]<30.0)|(x[:,1]>160.0)|((x[:,0]-x[:,1])<=10.0)
    bad = invalid(bp)
    # Redraw error, not covariates, in exceptionally implausible synthetic pairs.
    for _ in range(1000):
        if not bad.any():
            break
        ix = np.flatnonzero(bad)
        bp[ix] = pressure_pair(ix)
        bad = invalid(bp)
    if bad.any():
        raise RuntimeError('Failed physiological rejection sampling')
    df = pd.DataFrame({'row_id':np.arange(1,n+1,dtype=np.int64),
                       'age':age.astype(np.int64),
                       'female':female.astype(np.int64),
                       'bmi':np.round(bmi,2),
                       'sbp':np.round(bp[:,0],1),
                       'dbp':np.round(bp[:,1],1)})
    # These summaries are computed only from the returned fictional cohort.
    print({'transport_draw': {'sbp_bmi_per5':float(beta_s), 'dbp_bmi_per5':float(beta_d),
                              'person_error_rho':float(person_rho)},
           'analysis_linear_age':analyze_cohort(df),
           'analysis_flexible_age':analyze_cohort(df,True)})
    return df[['row_id','age','female','bmi','sbp','dbp']]
