import numpy as np
import pandas as pd
from scipy.special import ndtr


def analyze_cohort(data, flexible_age=False):
    """OLS BMI slopes per 5 kg/m^2 and Pearson correlation of paired OLS residuals."""
    a = data['age'].to_numpy(dtype=float)
    f = data['female'].to_numpy(dtype=float)
    b = data['bmi'].to_numpy(dtype=float)
    cols = [np.ones(len(a)), a - 52.0, f, b / 5.0]
    if flexible_age:
        cols += [np.maximum(a - 50.0, 0.0),
                 np.maximum(a - 50.0, 0.0)**2,
                 np.maximum(a - 60.0, 0.0)**2]
    X = np.column_stack(cols)
    Y = data[['sbp', 'dbp']].to_numpy(dtype=float)
    beta = np.linalg.lstsq(X, Y, rcond=None)[0]
    resid = Y - X @ beta
    inv = np.linalg.inv(X.T @ X)
    se = np.sqrt(inv[3, 3] * np.sum(resid**2, axis=0) / (len(a) - X.shape[1]))
    return {'sbp_bmi_slope_per5': float(beta[3, 0]),
            'dbp_bmi_slope_per5': float(beta[3, 1]),
            'sbp_slope_ols_se': float(se[0]), 'dbp_slope_ols_se': float(se[1]),
            'pressure_residual_pearson_r': float(np.corrcoef(resid.T)[0, 1])}


def generate(observed, spec, seed):
    """Generate fictional eligible equal-weight adults; never reads external data."""
    if observed is not None:
        raise ValueError('This generator implements whole-cohort generation only.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    female = rng.binomial(1, spec['female_probability'], size=n).astype(np.int64)
    age = np.empty(n, dtype=np.int64)
    for sex in (0, 1):
        ix = np.flatnonzero(female == sex)
        p_old = spec['age']['older_probability_by_sex'][sex]
        p_young = (1.0 - p_old) * spec['age']['young_share_within_under60_by_sex'][sex]
        group = rng.choice(3, size=len(ix), p=[p_young, 1.0 - p_old - p_young, p_old])
        for g, (low, high) in enumerate(spec['age']['bands_inclusive']):
            dest = ix[group == g]
            age[dest] = rng.integers(low, high + 1, size=len(dest))
    a = age.astype(float)
    f = female.astype(float)
    bm = spec['bmi']
    mean_bmi = (bm['male_mean_at38'] + bm['female_difference_at38'] * f
                + (bm['age_slope_male'] + bm['female_extra_age_slope'] * f) * (a - 38.0)
                - bm['late_age_quadratic'] * np.maximum(a - 60.0, 0.0)**2)
    sd_bmi = np.asarray(bm['conditional_sd_by_sex'])[female]
    shifted_mean = mean_bmi - bm['shift']
    log_variance = np.log1p((sd_bmi / shifted_mean)**2)
    log_mean = np.log(shifted_mean) - 0.5 * log_variance
    bmi = bm['shift'] + np.exp(log_mean + np.sqrt(log_variance) * rng.normal(size=n))
    bad = (bmi < bm['bounds'][0]) | (bmi > bm['bounds'][1])
    while np.any(bad):
        j = np.flatnonzero(bad)
        bmi[j] = bm['shift'] + np.exp(log_mean[j] + np.sqrt(log_variance[j]) * rng.normal(size=len(j)))
        bad = (bmi < bm['bounds'][0]) | (bmi > bm['bounds'][1])

    bp = spec['bp']
    # Approximate reference centering: ELSA subset age ~ N(52,9^2).
    def normal_positive_moments(mu, sd):
        z = mu / sd
        phi = np.exp(-0.5 * z*z) / np.sqrt(2*np.pi)
        return mu * ndtr(z) + sd * phi, (mu*mu + sd*sd) * ndtr(z) + mu * sd * phi
    ref = bp['reference']
    e50, e50sq = normal_positive_moments(ref['age_mean'] - 50.0, ref['age_sd'])
    _, e60sq = normal_positive_moments(ref['age_mean'] - 60.0, ref['age_sd'])
    h50 = np.maximum(a - 50.0, 0.0)
    h60 = np.maximum(a - 60.0, 0.0)
    mu_s = (ref['sbp_mean'] + bp['sbp_linear_age'] * (a - ref['age_mean'])
            + bp['sbp_age50_hinge'] * (h50 - e50)
            + bp['sbp_age60_square'] * (h60**2 - e60sq)
            + bp['sbp_female_difference'] * (f - ref['female_fraction'])
            + bp['bmi_slopes_per_unit'][0] * (bmi - ref['bmi_mean']))
    mu_d = (ref['dbp_mean'] + bp['dbp_linear_age'] * (a - ref['age_mean'])
            + bp['dbp_age50_square'] * (h50**2 - e50sq)
            + bp['dbp_female_difference'] * (f - ref['female_fraction'])
            + bp['bmi_slopes_per_unit'][1] * (bmi - ref['bmi_mean']))

    # Schur complement of published rounded Helsinki Pearson matrix.
    c = spec['residual_dependence']
    R = np.asarray(c['control_correlation'], dtype=float)
    rs = np.asarray(c['sbp_control_correlations'], dtype=float)
    rd = np.asarray(c['dbp_control_correlations'], dtype=float)
    cov = c['sbp_dbp_marginal_r'] - rs @ np.linalg.solve(R, rd)
    vs = 1.0 - rs @ np.linalg.solve(R, rs)
    vd = 1.0 - rd @ np.linalg.solve(R, rd)
    rho = float(cov / np.sqrt(vs * vd))
    if not (-1.0 < rho < 1.0):
        raise ValueError('Inadmissible residual correlation.')
    if c.get('override_rho') is not None:
        rho = float(c['override_rho'])
    sd_s, sd_d = bp['residual_sd']
    def draw_pressures(j):
        z = rng.normal(size=(len(j), 2))
        return mu_s[j] + sd_s*z[:, 0], mu_d[j] + sd_d*(rho*z[:, 0] + np.sqrt(1-rho*rho)*z[:, 1])
    sbp, dbp = draw_pressures(np.arange(n))
    lower_s, upper_s = bp['sbp_bounds']
    lower_d, upper_d = bp['dbp_bounds']
    def invalid():
        return ((sbp < lower_s) | (sbp > upper_s) | (dbp < lower_d) | (dbp > upper_d)
                | (sbp - dbp < bp['minimum_pulse_pressure']))
    bad = invalid()
    redraws = 0
    while np.any(bad):
        j = np.flatnonzero(bad)
        redraws += len(j)
        sbp[j], dbp[j] = draw_pressures(j)
        bad = invalid()
    out = pd.DataFrame({'row_id': np.arange(1, n+1, dtype=np.int64),
                        'age': age, 'female': female, 'bmi': bmi,
                        'sbp': sbp, 'dbp': dbp})
    out.attrs['fictional'] = True
    out.attrs['seed'] = int(seed)
    out.attrs['model_name'] = spec['model_name']
    out.attrs['pre_plausibility_rejection_residual_rho'] = rho
    out.attrs['bp_pair_redraw_count'] = redraws
    out.attrs['analysis_linear_age'] = analyze_cohort(out, flexible_age=False)
    out.attrs['analysis_flexible_age'] = analyze_cohort(out, flexible_age=True)
    if spec.get('emit_diagnostics', False):
        print('Fictional cohort only; model residual rho:', rho, 'BP pair redraws:', redraws)
        print('Linear-age analysis:', out.attrs['analysis_linear_age'])
        print('Flexible-age sensitivity analysis:', out.attrs['analysis_flexible_age'])
        print('Generated mean and SD:', out[['age','female','bmi','sbp','dbp']].agg(['mean','std']).to_dict())
    return out[['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp']]
