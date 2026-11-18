import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator is for whole-cohort generation only.')
    rng = np.random.default_rng(seed)
    n = 3000
    p = spec['model']
    age = 18.0 + 67.0 * rng.beta(p['age_beta'][0], p['age_beta'][1], n)
    female = rng.random(n) < p['female_probability']
    sex = np.where(female, 'F', 'M')
    group = rng.choice(3, size=n, p=p['lifestyle_weights'])
    # Context labels are latent and intentionally not extra output columns.
    bmean = np.asarray(p['bmi_group_means'])[group] + 0.7*female + 0.018*(age-35.0)
    bsd = np.asarray(p['bmi_group_sds'])[group]
    bsig = np.sqrt(np.log1p((bsd/bmean)**2))
    bmi = np.exp(np.log(bmean)-0.5*bsig**2 + bsig*rng.standard_normal(n))
    mt = (p['tc_intercept'] + p['tc_bmi_slope']*(bmi-22.0)
          + p['tc_age_slope']*(age-35.0) + p['tc_female_difference']*(female-0.55)
          + np.asarray(p['tc_group_offsets'])[group])
    mh = (p['hdl_intercept'] + p['hdl_bmi_slope']*(bmi-22.0)
          + p['hdl_age_slope']*(age-35.0) + p['hdl_female_difference']*(female-0.55)
          + np.asarray(p['hdl_group_offsets'])[group])
    # Smooth asymptotic safety mapping, effectively linear in ordinary ranges.
    # Bounds conditional mean, not observations, with no row rejection.
    def positive_mean(x, floor, scale):
        return floor + scale*np.logaddexp(0.0, (x-floor)/scale)
    mt = positive_mean(mt, 0.5, 0.08)
    mh = positive_mean(mh, 0.2, 0.04)
    st, sh = p['lipid_log_sds']
    r = p['conditional_lipid_pearson']
    # For multiplicative bivariate lognormal errors, select Gaussian rho to
    # produce the specified conditional Pearson correlation on original units.
    rho = np.log1p(r*np.sqrt(np.expm1(st*st)*np.expm1(sh*sh)))/(st*sh)
    zt = rng.standard_normal(n)
    zh = rho*zt + np.sqrt(1.0-rho*rho)*rng.standard_normal(n)
    tc = mt*np.exp(st*zt-0.5*st*st)
    hdl = mh*np.exp(sh*zh-0.5*sh*sh)
    out = pd.DataFrame({'id':[f'FIC-{i+1:05d}' for i in range(n)],
                        'age':age, 'sex':sex, 'bmi':bmi,
                        'total_cholesterol':tc, 'hdl_cholesterol':hdl})
    assert len(out) == 3000 and out['id'].is_unique
    assert np.isfinite(out[['age','bmi','total_cholesterol','hdl_cholesterol']].to_numpy()).all()
    assert (out[['bmi','total_cholesterol','hdl_cholesterol']].to_numpy()>0).all()
    return out
