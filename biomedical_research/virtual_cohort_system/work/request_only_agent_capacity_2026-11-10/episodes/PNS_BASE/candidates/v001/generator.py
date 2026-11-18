import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Generate fictional equal-weight adults; no target data are read or fitted."""
    if observed is not None:
        raise ValueError('Whole-cohort generator requires observed=None')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    bands = np.asarray(spec['age_bands'], dtype=int)
    group = rng.choice(len(bands), size=n, p=spec['age_band_probabilities'])
    age = np.array([rng.integers(bands[g, 0], bands[g, 1]+1) for g in group], dtype=int)
    female = (rng.random(n) < np.asarray(spec['female_probability_by_band'])[group]).astype(int)
    a = age.astype(float) - spec['reference_age']

    # Conditional BMI means preserve the external sex-specific mean at age 52.
    # The age trend and the extension to ages outside ELSA are assumptions.
    bmi_mean = np.asarray(spec['bmi_mean_at_reference_age'])[female]
    bmi_mean = bmi_mean + spec['bmi_age_slope_before_55']*np.minimum(age-52.0, 3.0)
    bmi_mean = bmi_mean + spec['bmi_age_slope_after_55']*np.maximum(age-55.0, 0.0)
    bmi_sd = np.asarray(spec['bmi_conditional_sd'])[female]
    shift = spec['bmi_lognormal_shift']
    log_sd = np.sqrt(np.log1p((bmi_sd/(bmi_mean-shift))**2))
    log_mean = np.log(bmi_mean-shift) - 0.5*log_sd**2
    bmi = shift + rng.lognormal(log_mean, log_sd)
    bad = (bmi < spec['bmi_bounds'][0]) | (bmi > spec['bmi_bounds'][1])
    while np.any(bad):
        bmi[bad] = shift + rng.lognormal(log_mean[bad], log_sd[bad])
        bad = (bmi < spec['bmi_bounds'][0]) | (bmi > spec['bmi_bounds'][1])
    bmi = np.round(bmi, 2)

    # These are marginal, measured BP models, not untreated/causal BP models.
    # Antihypertensive treatment and glycaemic states remain unrestricted and
    # implicit in means, slopes and total residual variation.
    sbp_mean = np.asarray(spec['sbp_mean_at_reference'])[female]
    sbp_mean = sbp_mean + np.asarray(spec['sbp_linear_age_slope'])[female]*a
    sbp_mean = sbp_mean + spec['sbp_age_quadratic']*a*a
    sbp_mean = sbp_mean + spec['bmi_sbp_slope_per_unit']*(bmi-27.0)
    dbp_mean = np.asarray(spec['dbp_mean_at_reference'])[female]
    dbp_age = spec['dbp_age_slope_to_55']*np.minimum(a, 3.0)
    dbp_age = dbp_age + spec['dbp_age_slope_after_55']*np.maximum(age-55.0, 0.0)
    dbp_mean = dbp_mean + dbp_age + spec['bmi_dbp_slope_per_unit']*(bmi-27.0)

    # Gaussian correlated total final-reading residuals. Not a claim about
    # within-person repeatability or the target release's aggregation rule.
    sds = np.asarray(spec['bp_residual_sd'], dtype=float)
    rho = float(spec['bp_residual_correlation'])
    cov = np.outer(sds, sds)*np.array([[1., rho], [rho, 1.]])
    mu = np.column_stack((sbp_mean, dbp_mean))
    pressure = mu + rng.multivariate_normal([0., 0.], cov, size=n)
    def invalid(p):
        pp = p[:, 0]-p[:, 1]
        return ((p[:, 0] < spec['sbp_bounds'][0]) |
                (p[:, 0] > spec['sbp_bounds'][1]) |
                (p[:, 1] < spec['dbp_bounds'][0]) |
                (p[:, 1] > spec['dbp_bounds'][1]) |
                (pp < spec['pulse_pressure_bounds'][0]) |
                (pp > spec['pulse_pressure_bounds'][1]))
    bad = invalid(pressure)
    rejected_pairs = int(np.sum(bad))
    while np.any(bad):
        pressure[bad] = mu[bad] + rng.multivariate_normal([0., 0.], cov, size=int(np.sum(bad)))
        bad = invalid(pressure)
        rejected_pairs += int(np.sum(bad))
    pressure = np.round(pressure, 1)
    df = pd.DataFrame({'row_id': np.arange(1, n+1, dtype=int),
                       'age': age, 'female': female, 'bmi': bmi,
                       'sbp': pressure[:, 0], 'dbp': pressure[:, 1]})

    # Analyses of these generated rows only; no coefficient matching/rescaling.
    X = np.column_stack((np.ones(n), age, female, bmi/5.0))
    Y = df[['sbp', 'dbp']].to_numpy()
    coef = np.linalg.lstsq(X, Y, rcond=None)[0]
    resid = Y-X@coef
    se = np.sqrt(np.sum(resid**2, axis=0)/(n-X.shape[1]) * np.linalg.inv(X.T@X)[3, 3])
    df.attrs['fictional'] = True
    df.attrs['analysis_formula'] = 'BP ~ intercept + linear age + female + BMI/5; equal-weight OLS'
    df.attrs['generated_only_analysis'] = {
        'sbp_bmi_slope_per_5': float(coef[3, 0]),
        'dbp_bmi_slope_per_5': float(coef[3, 1]),
        'sbp_bmi_slope_se': float(se[0]), 'dbp_bmi_slope_se': float(se[1]),
        'pearson_bp_residual_correlation': float(np.corrcoef(resid.T)[0, 1]),
        'rejected_pressure_pairs': rejected_pairs}
    return df
