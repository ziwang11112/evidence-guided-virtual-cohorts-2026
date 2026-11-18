import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Fictional equal-weight adults; no individual observations are used."""
    if observed is not None:
        raise ValueError('This is a whole-cohort generator; observed must be None.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    bands = rng.choice(len(spec['age_band_probabilities']), size=n,
                       p=np.asarray(spec['age_band_probabilities'], dtype=float))
    age = np.asarray(spec['age_band_starts'], dtype=int)[bands] + rng.integers(0, 10, size=n)
    female = rng.binomial(1, np.asarray(spec['female_probability_by_age_band'])[bands])
    bmi_mean = np.interp(age, spec['bmi_age_knots'], spec['male_bmi_means']) + spec['female_bmi_difference'] * female
    bmi_sd = np.where(female == 1, spec['bmi_sd_female'], spec['bmi_sd_male'])
    shifted_mean = bmi_mean - spec['bmi_shift']
    shape = (shifted_mean / bmi_sd)**2
    scale = bmi_sd**2 / shifted_mean
    bmi = spec['bmi_shift'] + rng.gamma(shape, scale)
    bad = (bmi < spec['bmi_bounds'][0]) | (bmi > spec['bmi_bounds'][1])
    for _ in range(100):
        if not bad.any():
            break
        bmi[bad] = spec['bmi_shift'] + rng.gamma(shape[bad], scale[bad])
        bad = (bmi < spec['bmi_bounds'][0]) | (bmi > spec['bmi_bounds'][1])
    if bad.any():
        raise RuntimeError('BMI rejection limit reached')
    # Conditional mean curves integrate over treatment/comorbidity, rather than excluding them.
    mu_s = np.interp(age, spec['bp_age_knots'], spec['male_sbp_means'])
    mu_d = np.interp(age, spec['bp_age_knots'], spec['male_dbp_means'])
    mu_s += female * (spec['female_sbp_at20'] + spec['female_sbp_age_gradient'] * (age - 20))
    mu_d += female * (spec['female_dbp_at20'] + spec['female_dbp_age_gradient'] * (age - 20))
    mu_s += spec['sbp_bmi_slope_per5'] * (bmi - spec['bmi_center']) / 5.0
    mu_d += spec['dbp_bmi_slope_per5'] * (bmi - spec['bmi_center']) / 5.0
    sd_s = spec['latent_sbp_sd_at20'] + spec['latent_sbp_sd_age_gradient'] * (age - 20)
    sd_d = spec['latent_dbp_sd_at20'] + spec['latent_dbp_sd_age_gradient'] * (age - 20)
    rho = spec['latent_pressure_correlation']
    r_read = spec['reading_error_correlation']
    gamma_shape = spec['shared_gamma_shape']
    agg = spec['bp_aggregation']
    if agg not in ('last2', 'mean3', 'last'):
        raise ValueError('Unsupported BP aggregation')
    sbp = np.empty(n)
    dbp = np.empty(n)
    pending = np.arange(n)
    for _ in range(100):
        if pending.size == 0:
            break
        k = pending.size
        # Shared centered gamma gives positive skew, while normals preserve heterogeneity.
        g = (rng.gamma(gamma_shape, 1.0, k) - gamma_shape) / np.sqrt(gamma_shape)
        zs, zd = rng.standard_normal((2, k))
        vs = sd_s[pending] * (np.sqrt(rho)*g + np.sqrt(1-rho)*zs)
        vd = sd_d[pending] * (np.sqrt(rho)*g + np.sqrt(1-rho)*zd)
        es, ed = rng.standard_normal((2, k, 3))
        err_s = spec['reading_error_sbp_sd'] * es
        err_d = spec['reading_error_dbp_sd'] * (r_read*es + np.sqrt(1-r_read*r_read)*ed)
        s_reads = mu_s[pending, None] + vs[:, None] + err_s + np.asarray(spec['reading_order_sbp_offsets'])
        d_reads = mu_d[pending, None] + vd[:, None] + err_d + np.asarray(spec['reading_order_dbp_offsets'])
        if agg == 'last2':
            ss, dd = s_reads[:, 1:].mean(1), d_reads[:, 1:].mean(1)
        elif agg == 'mean3':
            ss, dd = s_reads.mean(1), d_reads.mean(1)
        else:
            ss, dd = s_reads[:, -1], d_reads[:, -1]
        ok = ((ss >= spec['sbp_bounds'][0]) & (ss <= spec['sbp_bounds'][1]) &
              (dd >= spec['dbp_bounds'][0]) & (dd <= spec['dbp_bounds'][1]) &
              (ss - dd >= spec['minimum_pulse_pressure']))
        sbp[pending[ok]], dbp[pending[ok]] = ss[ok], dd[ok]
        pending = pending[~ok]
    if pending.size:
        raise RuntimeError('Joint pressure rejection limit reached')
    # No sample-level moment matching or regression-coefficient forcing.
    return pd.DataFrame({'row_id': np.arange(1, n + 1, dtype=np.int64),
                         'age': age.astype(np.int64), 'female': female.astype(np.int64),
                         'bmi': np.round(bmi, 2), 'sbp': np.round(sbp, 1),
                         'dbp': np.round(dbp, 1)},
                        columns=['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp'])


def analyze_cohort(df, nonlinear_age=False):
    """Primary OLS age/sex adjustment; optional piecewise-linear age/sex sensitivity.
    Reports BMI slopes per 5 kg/m^2 and Pearson correlation of the two OLS residuals.
    This function is not called by generate and never modifies the generated rows.
    """
    from scipy.stats import t
    age = df['age'].to_numpy(float)
    female = df['female'].to_numpy(float)
    x = [np.ones(len(df)), (age-45)/10, female]
    if nonlinear_age:
        # Same knot set as the generator, with sex-age convergence included.
        x.extend([np.maximum(age-k, 0)/10 for k in (30, 40, 50, 60, 70)])
        x.append(female*(age-20)/10)
    x.append((df['bmi'].to_numpy(float)-26.2)/5)
    X = np.column_stack(x)
    Y = df[['sbp', 'dbp']].to_numpy(float)
    beta = np.linalg.lstsq(X, Y, rcond=None)[0]
    residual = Y-X@beta
    dof = len(df)-np.linalg.matrix_rank(X)
    var = (residual**2).sum(axis=0)/dof
    se = np.sqrt(np.linalg.inv(X.T@X)[-1, -1]*var)
    q = t.ppf(0.975, dof)
    return {'age_adjustment': 'piecewise_linear_with_sex_age' if nonlinear_age else 'linear_age_and_sex',
            'sbp_bmi_slope_per5': float(beta[-1, 0]),
            'sbp_bmi_slope_95CI': [float(beta[-1,0]-q*se[0]), float(beta[-1,0]+q*se[0])],
            'dbp_bmi_slope_per5': float(beta[-1, 1]),
            'dbp_bmi_slope_95CI': [float(beta[-1,1]-q*se[1]), float(beta[-1,1]+q*se[1])],
            'pressure_residual_pearson_r': float(np.corrcoef(residual.T)[0,1])}
