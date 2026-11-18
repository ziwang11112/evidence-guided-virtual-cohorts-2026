import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generation requires observed=None')
    rng = np.random.default_rng(seed)
    n = 3000
    p = spec
    # Accept the infrastructure's outer model wrapper as well as direct spec.
    for _ in range(8):
        if 'age_beta' in p:
            break
        p = p['model']
    age = 18.0 + 67.0*rng.beta(*p['age_beta'], size=n)
    female = rng.random(n) < p['female_probability']
    group = rng.choice(3, size=n, p=p['lifestyle_weights'])
    bm = np.asarray(p['bmi_group_means'])[group] + 0.7*female + 0.018*(age-35.0)
    sd = np.asarray(p['bmi_group_sds'])[group]
    bs = np.sqrt(np.log1p((sd/bm)**2))
    bmi = np.exp(np.log(bm)-0.5*bs**2+bs*rng.standard_normal(n))
    mt = p['tc_intercept'] + p['tc_bmi_slope']*(bmi-22) + p['tc_age_slope']*(age-35) + p['tc_female_difference']*(female-0.55) + np.asarray(p['tc_group_offsets'])[group]
    mh = p['hdl_intercept'] + p['hdl_bmi_slope']*(bmi-22) + p['hdl_age_slope']*(age-35) + p['hdl_female_difference']*(female-0.55) + np.asarray(p['hdl_group_offsets'])[group]
    mt = 0.5 + 0.08*np.logaddexp(0.0,(mt-0.5)/0.08)
    mh = 0.2 + 0.04*np.logaddexp(0.0,(mh-0.2)/0.04)
    st, sh = p['lipid_log_sds']
    rho = np.log1p(p['conditional_lipid_pearson']*np.sqrt(np.expm1(st*st)*np.expm1(sh*sh)))/(st*sh)
    zt = rng.standard_normal(n)
    zh = rho*zt + np.sqrt(1-rho*rho)*rng.standard_normal(n)
    out = pd.DataFrame({'id':[f'FIC-{i+1:05d}' for i in range(n)],'age':age,'sex':np.where(female,'F','M'),'bmi':bmi,'total_cholesterol':mt*np.exp(st*zt-st*st/2),'hdl_cholesterol':mh*np.exp(sh*zh-sh*sh/2)})
    assert len(out)==3000 and out.id.is_unique
    assert np.isfinite(out[['age','bmi','total_cholesterol','hdl_cholesterol']].to_numpy()).all()
    assert (out[['bmi','total_cholesterol','hdl_cholesterol']].to_numpy()>0).all()
    return out
