import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri


def generate(observed, spec, seed):
    """Generate a fictional whole cohort; all scientific settings are in spec."""
    if observed is not None:
        raise ValueError('This generator implements whole-cohort generation only.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    g = rng.choice(3, size=n, p=np.asarray(spec['setting_probabilities'], float))
    female = rng.random(n) < spec['female_probability']
    sex = np.where(female, 'F', 'M')
    a = spec['age']
    age = a['minimum'] + (a['maximum'] - a['minimum']) * rng.beta(a['beta_alpha'], a['beta_beta'], n)

    b = spec['bmi']
    m = np.where(female, np.asarray(b['female_means'])[g], np.asarray(b['male_means'])[g])
    m = m + b['age_slope'] * (age - spec['reference_age'])
    sd = np.where(female, np.asarray(b['female_sds'])[g], np.asarray(b['male_sds'])[g])
    log_sd = np.sqrt(np.log1p((sd / m) ** 2))
    log_mean = np.log(m) - 0.5 * log_sd ** 2
    lo = ndtr((np.log(b['minimum']) - log_mean) / log_sd)
    hi = ndtr((np.log(b['maximum']) - log_mean) / log_sd)
    u = lo + (hi - lo) * rng.random(n)
    bmi = np.exp(log_mean + log_sd * ndtri(np.clip(u, 1e-14, 1 - 1e-14)))

    l = spec['lipids']
    source_sd = l['assumed_source_bmi_sd']
    tc_effect = np.where(female, np.asarray(l['tc_effect_per_bmi_sd_female'])[g], np.asarray(l['tc_effect_per_bmi_sd_male'])[g]) / source_sd
    hdl_effect = np.where(female, np.asarray(l['hdl_effect_per_bmi_sd_female'])[g], np.asarray(l['hdl_effect_per_bmi_sd_male'])[g]) / source_sd
    bmi_center = bmi - np.asarray(b['setting_reference_bmi'])[g]
    age_center = age - spec['reference_age']
    sex_center = female.astype(float) - spec['female_probability']
    tc_mean = np.asarray(l['tc_reference_means'])[g] + tc_effect * bmi_center + l['tc_age_slope'] * age_center + l['tc_female_shift'] * sex_center
    hdl_mean = np.asarray(l['hdl_reference_means'])[g] + hdl_effect * bmi_center + l['hdl_age_slope'] * age_center + l['hdl_female_shift'] * sex_center
    if np.any(tc_mean <= 0) or np.any(hdl_mean <= 0):
        raise ValueError('Lipid mean settings must remain positive on the specified covariate support.')

    # Correlated, mean-one lognormal multipliers.  The configured correlation
    # is that of raw-scale conditional lipid errors, not of log concentrations.
    cv_t, cv_h = l['tc_conditional_cv'], l['hdl_conditional_cv']
    st, sh = np.sqrt(np.log1p(cv_t ** 2)), np.sqrt(np.log1p(cv_h ** 2))
    rlog = np.log1p(l['conditional_raw_error_correlation'] * cv_t * cv_h) / (st * sh)
    if not (-1 < rlog < 1):
        raise ValueError('Incompatible conditional correlation and CV settings.')
    zt = rng.normal(size=n)
    zh = rlog * zt + np.sqrt(1 - rlog ** 2) * rng.normal(size=n)
    tc = tc_mean * np.exp(st * zt - 0.5 * st ** 2)
    hdl = hdl_mean * np.exp(sh * zh - 0.5 * sh ** 2)
    out = pd.DataFrame({
        'id': [f'FICTIONAL_{i:05d}' for i in range(1, n + 1)],
        'age': age,
        'sex': sex,
        'bmi': bmi,
        'total_cholesterol': tc,
        'hdl_cholesterol': hdl
    })
    values = out[['bmi', 'total_cholesterol', 'hdl_cholesterol']].to_numpy()
    if not np.isfinite(values).all() or not (values > 0).all():
        raise ValueError('Nonfinite or nonpositive generated value.')
    if spec.get('print_diagnostics', False):
        x = np.column_stack([np.ones(n), age, female.astype(float), bmi])
        bt = np.linalg.lstsq(x, tc, rcond=None)[0]
        bh = np.linalg.lstsq(x, hdl, rcond=None)[0]
        rt, rh = tc - x @ bt, hdl - x @ bh
        print({'fictional_only': True, 'tc_bmi_mg_dl_per_5': float(bt[-1] * 5 * 38.67),
               'hdl_bmi_mg_dl_per_5': float(bh[-1] * 5 * 38.67),
               'lipid_residual_pearson_r': float(np.corrcoef(rt, rh)[0, 1]),
               'setting_counts': np.bincount(g, minlength=3).tolist(),
               'tc_le_hdl_count_not_excluded': int(np.sum(tc <= hdl)),
               'underweight_fraction': float(np.mean(bmi < 18.5)),
               'overweight_or_obese_fraction': float(np.mean(bmi >= 25))})
    return out
