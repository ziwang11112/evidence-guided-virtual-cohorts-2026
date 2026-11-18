import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    task = spec['task']
    model = spec['model']
    n = int(task['n_rows'])
    ordered = [c['name'] for c in task['columns']]
    cd = model['covariate_distribution']
    rng = np.random.default_rng(seed)
    age = rng.uniform(cd['age']['lower'], cd['age']['upper'], size=n)
    female = rng.binomial(1, cd['female']['p'], size=n).astype(np.int64)
    b = cd['bmi']
    bmi = b['lower'] + (b['upper'] - b['lower']) * rng.beta(b['alpha'], b['beta'], size=n)
    age = np.clip(age, cd['age']['lower'], cd['age']['upper'])
    bmi = np.clip(bmi, b['lower'], b['upper'])
    lp = model['linear_predictor']
    age_z = (age - lp['age_center']) / lp['age_scale']
    bmi_z = (bmi - lp['bmi_center']) / lp['bmi_scale']
    sbp_lp = lp['sbp']['intercept'] + lp['sbp']['age_z'] * age_z + lp['sbp']['female'] * female + lp['sbp']['bmi_z'] * bmi_z
    dbp_lp = lp['dbp']['intercept'] + lp['dbp']['age_z'] * age_z + lp['dbp']['female'] * female + lp['dbp']['bmi_z'] * bmi_z
    r = model['residual']
    cov_sdp = r['correlation'] * r['sbp_sd'] * r['dbp_sd']
    resid = rng.multivariate_normal(np.zeros(2), [[r['sbp_sd'] ** 2, cov_sdp], [cov_sdp, r['dbp_sd'] ** 2]], size=n)
    sbp = sbp_lp + resid[:, 0]
    dbp = dbp_lp + resid[:, 1]
    row_id = np.arange(1, n + 1, dtype=np.int64)
    df = pd.DataFrame({
        ordered[0]: row_id,
        ordered[1]: age,
        ordered[2]: female,
        ordered[3]: bmi,
        ordered[4]: sbp,
        ordered[5]: dbp
    })
    return df[ordered]
