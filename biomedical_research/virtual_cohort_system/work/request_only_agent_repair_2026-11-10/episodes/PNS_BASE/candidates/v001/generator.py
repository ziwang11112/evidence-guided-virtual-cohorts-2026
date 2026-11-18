import numpy as np
import pandas as pd


def analyze(df):
    """Equal-weight OLS; slopes per 5 BMI units and paired Pearson residual correlation."""
    a = df.age.to_numpy(dtype=float)
    f = df.female.to_numpy(dtype=float)
    b = (df.bmi.to_numpy(dtype=float)-27.0)/5.0
    X = np.column_stack([np.ones(len(df)), a-50.0, f, b])
    Y = df[['sbp', 'dbp']].to_numpy(dtype=float)
    coef = np.linalg.lstsq(X, Y, rcond=None)[0]
    residuals = Y-X@coef
    mse = np.sum(residuals**2, axis=0)/(len(df)-X.shape[1])
    se = np.sqrt(np.linalg.inv(X.T@X)[-1,-1]*mse)
    # A quadratic-age sensitivity avoids forcing a linear diastolic age profile.
    Xq = np.column_stack([X, ((a-50.0)/10.0)**2])
    cq = np.linalg.lstsq(Xq, Y, rcond=None)[0]
    rq = Y-Xq@cq
    return {'linear_age_bmi_slopes_per5': coef[-1].tolist(),
            'linear_age_slope_standard_errors': se.tolist(),
            'linear_age_residual_pearson_r': float(np.corrcoef(residuals.T)[0,1]),
            'quadratic_age_bmi_slopes_per5': cq[3].tolist(),
            'quadratic_age_residual_pearson_r': float(np.corrcoef(rq.T)[0,1])}


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generator requires observed=None')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    group = rng.choice(6, size=n, p=np.asarray(spec['age_decade_probabilities']))
    age = 20 + group*10 + rng.integers(0, 10, size=n)
    pf = spec['female_probability_at45'] + spec['female_age_gradient']*(age-45.0)
    female = rng.binomial(1, pf, size=n)
    # Shifted lognormal preserves BMI right-skew without a mass at a bound.
    mean_bmi = (spec['bmi_mean_at45_male'] + 0.075*(age-45.0)
                - 0.003*np.maximum(age-55.0, 0.0)**2
                + spec['bmi_female_shift']*female)
    sd_bmi = spec['bmi_sd_male'] + spec['bmi_sd_female_extra']*female
    shift = spec['bmi_lognormal_shift']
    sigma2 = np.log1p((sd_bmi/(mean_bmi-shift))**2)
    logmu = np.log(mean_bmi-shift)-0.5*sigma2
    bmi = shift + rng.lognormal(logmu, np.sqrt(sigma2))
    bad = (bmi<spec['bmi_bounds'][0]) | (bmi>spec['bmi_bounds'][1])
    while np.any(bad):
        bmi[bad] = shift + rng.lognormal(logmu[bad], np.sqrt(sigma2[bad]))
        bad = (bmi<spec['bmi_bounds'][0]) | (bmi>spec['bmi_bounds'][1])
    bmi = np.round(bmi, 2)
    a = age-50.0
    b = (bmi-27.0)/5.0
    mu_s = (spec['sbp_male_at50_bmi27'] + 0.55*a + 0.002*a*a
            + female*(-7.0+0.10*a) + spec['sbp_slope_per5']*b)
    mu_d = (spec['dbp_male_at50_bmi27'] + 0.17*a - 0.007*a*a
            - 4.0*female + spec['dbp_slope_per5']*b)
    sd_s = spec['sbp_residual_sd_at20'] + spec['sbp_residual_sd_age_increment']*(age-20.0)
    sd_d = spec['dbp_residual_sd_at20'] + spec['dbp_residual_sd_age_increment']*(age-20.0)
    rho = spec['latent_residual_correlation']
    L = np.linalg.cholesky(np.array([[1.0,rho],[rho,1.0]]))
    measurement_rho = spec['within_reading_error_correlation']
    M = np.linalg.cholesky(np.array([[1.0, measurement_rho],[measurement_rho,1.0]]))
    pressures = np.empty((n,2), dtype=float)
    remaining = np.arange(n)
    df = spec['residual_t_df']
    while len(remaining):
        m = len(remaining)
        z = rng.normal(size=(m,2)) @ L.T
        z *= np.sqrt((df-2.0)/rng.chisquare(df,size=m))[:,None]
        latent = np.column_stack([mu_s[remaining],mu_d[remaining]]) + z*np.column_stack([sd_s[remaining],sd_d[remaining]])
        # Two final same-visit readings: shared person/visit deviation above,
        # plus independent between-reading, correlated within-reading errors.
        readings = []
        for j in range(spec['assumed_final_reading_count']):
            e = rng.normal(size=(m,2)) @ M.T
            e *= np.asarray(spec['single_reading_error_sd'])
            readings.append(np.rint(latent+e))
        bp = np.mean(readings,axis=0)
        valid = ((bp[:,0]>=spec['sbp_bounds'][0]) & (bp[:,0]<=spec['sbp_bounds'][1])
                 & (bp[:,1]>=spec['dbp_bounds'][0]) & (bp[:,1]<=spec['dbp_bounds'][1])
                 & ((bp[:,0]-bp[:,1])>=spec['minimum_pulse_pressure']))
        pressures[remaining[valid]] = bp[valid]
        remaining = remaining[~valid]
    out = pd.DataFrame({'row_id': np.arange(1,n+1,dtype=np.int64),
                        'age': age.astype(np.int64), 'female': female.astype(np.int64),
                        'bmi': bmi, 'sbp': pressures[:,0], 'dbp': pressures[:,1]})
    out.attrs['fictional'] = True
    out.attrs['seed'] = int(seed)
    out.attrs['analysis'] = analyze(out)
    return out
