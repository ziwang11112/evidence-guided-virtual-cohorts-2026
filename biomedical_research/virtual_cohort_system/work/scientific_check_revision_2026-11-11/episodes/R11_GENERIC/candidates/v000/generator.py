import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator implements whole-cohort generation only.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    dem = spec['demography']
    decade = rng.choice(6, size=n, p=np.asarray(dem['age_decade_probabilities'], dtype=float))
    age = 20 + 10 * decade + rng.integers(0, 10, size=n)
    female = (rng.random(n) < np.asarray(dem['female_probability_by_decade'])[decade]).astype(int)
    b = spec['bmi_model']
    knots = np.asarray(b['age_knots'], dtype=float)
    mu = np.where(female == 1, np.interp(age, knots, b['mean_female']), np.interp(age, knots, b['mean_male']))
    sd = np.where(female == 1, b['sd_female'], b['sd_male'])
    shift = float(b['shift'])
    log_sd = np.sqrt(np.log1p((sd / (mu - shift))**2))
    log_mu = np.log(mu - shift) - 0.5 * log_sd**2
    bmi = shift + rng.lognormal(log_mu, log_sd)
    lo, hi = b['support']
    bad = (bmi < lo) | (bmi > hi)
    while np.any(bad):
        bmi[bad] = shift + rng.lognormal(log_mu[bad], log_sd[bad])
        bad = (bmi < lo) | (bmi > hi)
    # Released values are fictional aggregates, not simulated individual cuff readings.
    bp = spec['bp_model']
    ak = np.asarray(bp['age_knots'], dtype=float)
    center_age = float(bp['reference_age'])
    out_means = []
    for outcome in ['sbp', 'dbp']:
        par = bp[outcome]
        male_shape = np.interp(age, ak, par['shape_male']) - np.interp(center_age, ak, par['shape_male'])
        female_shape = np.interp(age, ak, par['shape_female']) - np.interp(center_age, ak, par['shape_female'])
        female_offset = -float(par['male_minus_female'])
        male_reference = float(par['reference_marginal_mean']) - bp['reference_female_fraction'] * female_offset
        loc = male_reference + female_offset*female + np.where(female == 1, female_shape, male_shape)
        loc = loc + par['bmi_slope_per_kg_m2']*(bmi - bp['reference_bmi'])
        out_means.append(loc)
    mean_s, mean_d = out_means
    # Exact partial-correlation algebra applied separately to the published sex-specific matrices.
    rhos = []
    for sex_name in ['male', 'female']:
        c = spec['dependence_evidence'][sex_name]
        rxx = np.array([[1., c['age_bmi']], [c['age_bmi'], 1.]])
        rs = np.array(c['sbp_with_age_bmi'], dtype=float)
        rd = np.array(c['dbp_with_age_bmi'], dtype=float)
        inv = np.linalg.inv(rxx)
        cov = c['sbp_dbp'] - rs @ inv @ rd
        vs = 1. - rs @ inv @ rs
        vd = 1. - rd @ inv @ rd
        rhos.append(float(cov / np.sqrt(vs*vd)))
    rho = np.where(female == 1, rhos[1], rhos[0])
    ss = bp['sbp']['residual_sd_at_reference'] * np.interp(age, bp['sd_scale_age_knots'], bp['sbp']['residual_sd_scale'])
    ds = bp['dbp']['residual_sd_at_reference'] * np.interp(age, bp['sd_scale_age_knots'], bp['dbp']['residual_sd_scale'])
    def draw(indices):
        z = rng.normal(size=(len(indices), 2))
        es = ss[indices] * z[:, 0]
        ed = ds[indices] * (rho[indices]*z[:, 0] + np.sqrt(1-rho[indices]**2)*z[:, 1])
        return mean_s[indices]+es, mean_d[indices]+ed
    idx = np.arange(n)
    sbp, dbp = draw(idx)
    smin, smax = bp['sbp_support']
    dmin, dmax = bp['dbp_support']
    minimum_pp = bp['minimum_pulse_pressure']
    def invalid(s, d):
        return (s < smin) | (s > smax) | (d < dmin) | (d > dmax) | (s-d < minimum_pp)
    bad = invalid(sbp, dbp)
    for _ in range(10000):
        if not np.any(bad):
            break
        ii = np.flatnonzero(bad)
        sbp[ii], dbp[ii] = draw(ii)
        bad = invalid(sbp, dbp)
    if np.any(bad):
        raise RuntimeError('Unable to draw admissible pressures.')
    result = pd.DataFrame({'row_id': np.arange(1, n+1, dtype=np.int64),
                           'age': age.astype(float), 'female': female,
                           'bmi': np.round(bmi, 2), 'sbp': np.round(sbp, 1), 'dbp': np.round(dbp, 1)})
    # Diagnostics use only these generated records. No calibration or sample-forced coefficients.
    X = np.column_stack([np.ones(n), result['age'], female, result['bmi']/5.])
    Y = result[['sbp', 'dbp']].to_numpy()
    coef = np.linalg.lstsq(X, Y, rcond=None)[0]
    resid = Y - X @ coef
    # Flexible sensitivity separates the imposed nonlinear age/sex functions from BMI.
    a = (result['age'].to_numpy()-50.)/10.
    F = np.column_stack([np.ones(n), a, a*a, a*a*a, female, female*a, female*a*a, result['bmi']/5.])
    cf = np.linalg.lstsq(F, Y, rcond=None)[0]
    rf = Y - F @ cf
    result.attrs['fictional'] = True
    result.attrs['diagnostics'] = {'linear_age_bmi_slopes_per_5': coef[-1].tolist(),
        'linear_age_residual_pearson_r': float(np.corrcoef(resid.T)[0,1]),
        'flexible_age_bmi_slopes_per_5': cf[-1].tolist(),
        'flexible_age_residual_pearson_r': float(np.corrcoef(rf.T)[0,1]),
        'source_derived_sex_specific_error_correlations': rhos}
    print('GENERATED_ONLY_DIAGNOSTICS', result.attrs['diagnostics'])
    return result[['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp']]
