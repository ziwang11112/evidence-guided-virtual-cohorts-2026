import numpy as np
import pandas as pd
import json
from scipy.special import ndtr, ndtri
from scipy.stats import t as student_t


def generate(observed, spec, seed):
    """Whole-cohort fictional adult sample. No source rows or target records used."""
    if observed is not None:
        raise ValueError('This generator requires observed=None.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    g = rng.choice(3, size=n, p=spec['age_band_probabilities'])
    age = np.empty(n, dtype=int)
    for k, (lo, hi, aa, bb) in enumerate(spec['age_band_beta']):
        ii = np.flatnonzero(g == k)
        age[ii] = np.minimum(hi, lo + np.floor((hi-lo+1)*rng.beta(aa, bb, len(ii))).astype(int))
    female = rng.binomial(1, np.asarray(spec['female_probabilities'])[g]).astype(int)
    a = age.astype(float) - 52.0

    # Positive skew and sex-specific spread: conditional arithmetic mean specified.
    bmi_mean = np.interp(age, spec['bmi_age_knots'], spec['bmi_mean_knots'])
    bmi_mean += spec['bmi_time_transport_shift'] + spec['bmi_female_contrast']*(female-0.53)
    bmi_sd = np.where(female == 1, spec['bmi_conditional_sd'][1], spec['bmi_conditional_sd'][0])
    sig = np.sqrt(np.log1p((bmi_sd / bmi_mean)**2))
    mu = np.log(bmi_mean) - sig**2/2
    lo, hi = spec['bmi_support']
    pl, ph = ndtr((np.log(lo)-mu)/sig), ndtr((np.log(hi)-mu)/sig)
    bmi = np.exp(mu + sig*ndtri(pl + (ph-pl)*rng.random(n)))
    bmi = np.round(bmi, 2)

    # All-treatment-status marginal associations; no hypertension/diabetes exclusion.
    bs = np.where(female == 1, spec['sbp_bmi_slopes'][1], spec['sbp_bmi_slopes'][0])
    bd = bs * spec['dbp_to_sbp_bmi_slope_ratio']
    s_mean = (spec['sbp_male_reference'] + spec['sbp_age_below52']*a
              + spec['sbp_age_extra_above52']*np.maximum(a, 0)
              + female*(spec['sbp_female_reference_contrast'] + spec['sbp_age_sex_interaction']*a)
              + bs*(bmi-27.0))
    d_mean = (spec['dbp_male_reference'] + spec['dbp_age_below55']*a
              + spec['dbp_age_extra_above55']*np.maximum(a-3.0, 0)
              + female*(spec['dbp_female_reference_contrast'] + spec['dbp_age_sex_interaction']*a)
              + bd*(bmi-27.0))
    s_sd = spec['sbp_latent_sd_at35'] + spec['sbp_latent_sd_age_increment']*np.maximum(age-35.0, 0)
    d_sd = np.full(n, spec['dbp_latent_sd'])
    rho = spec['latent_residual_correlation']
    rme = spec['reading_error_correlation']
    err_sd = np.asarray(spec['single_reading_error_sd'])
    m = int(spec['number_of_averaged_readings'])
    df = spec['latent_t_df']
    sbp, dbp = np.empty(n), np.empty(n)
    todo = np.arange(n)
    rejected = 0
    for _ in range(1000):
        if len(todo) == 0:
            break
        z = rng.normal(size=(len(todo), 2))
        scale = np.sqrt((df-2.0)/rng.chisquare(df, len(todo)))
        es = s_sd[todo]*z[:, 0]*scale
        ed = d_sd[todo]*(rho*z[:, 0] + np.sqrt(1-rho*rho)*z[:, 1])*scale
        # Independent between readings conditional on a shared visit/person residual.
        e = rng.normal(size=(len(todo), m, 2))
        ems = err_sd[0]*e[:, :, 0].mean(axis=1)
        emd = err_sd[1]*(rme*e[:, :, 0] + np.sqrt(1-rme*rme)*e[:, :, 1]).mean(axis=1)
        s = np.round(s_mean[todo] + es + ems, 1)
        d = np.round(d_mean[todo] + ed + emd, 1)
        ok = ((s >= spec['sbp_support'][0]) & (s <= spec['sbp_support'][1])
              & (d >= spec['dbp_support'][0]) & (d <= spec['dbp_support'][1])
              & ((s-d) >= spec['pulse_pressure_support'][0])
              & ((s-d) <= spec['pulse_pressure_support'][1]))
        sbp[todo[ok]], dbp[todo[ok]] = s[ok], d[ok]
        rejected += int((~ok).sum())
        todo = todo[~ok]
    if len(todo):
        raise RuntimeError('Pressure rejection sampler failed to terminate.')
    out = pd.DataFrame({'row_id': np.arange(1, n+1, dtype=np.int64),
                        'age': age, 'female': female, 'bmi': bmi,
                        'sbp': sbp, 'dbp': dbp})

    # Generated-only analyses, never calibration or forced sample correlations.
    def analyze(X):
        yy = out[['sbp', 'dbp']].to_numpy()
        coef = np.linalg.lstsq(X, yy, rcond=None)[0]
        res = yy-X@coef
        v = np.linalg.inv(X.T@X)
        se = np.sqrt(np.sum(res**2, axis=0)/(n-X.shape[1])*v[-1, -1])
        q = student_t.ppf(0.975, n-X.shape[1])
        r = float(np.corrcoef(res.T)[0, 1])
        return {'bmi_slopes_per_5': coef[-1].tolist(),
                'slope_95ci': np.stack([coef[-1]-q*se, coef[-1]+q*se], axis=1).tolist(),
                'pressure_residual_pearson_r': r,
                'residual_r_approx_95ci': np.tanh(np.arctanh(r)+np.array([-1, 1])*1.96/np.sqrt(n-X.shape[1]-2)).tolist()}
    X = np.column_stack([np.ones(n), a, female, bmi/5.0])
    Xflex = np.column_stack([np.ones(n), a, female, np.maximum(a,0), np.maximum(a-3,0), a*female, bmi/5.0])
    diagnostic = {'linear_age_sex_adjustment': analyze(X),
                  'piecewise_age_and_age_sex_sensitivity': analyze(Xflex),
                  'pressure_pair_redraws': rejected,
                  'n': n}
    out.attrs['generated_only_analyses'] = diagnostic
    out.attrs['fictional'] = True
    print(json.dumps(diagnostic, sort_keys=True))
    return out
