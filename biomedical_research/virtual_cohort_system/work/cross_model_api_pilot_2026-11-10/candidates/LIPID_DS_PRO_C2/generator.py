import numpy as np
import pandas as pd
from math import exp, log


def generate(observed, spec, seed):
    task = spec['task']
    model = spec['model']
    n = int(task['n_rows'])
    columns = [col['name'] for col in task['columns']]
    rng = np.random.default_rng(seed)
    sex_cfg = model['sex']
    age_cfg = model['age']
    bmi_cfg = model['bmi']
    lip = model['lipids_mmol_L']
    rows = []
    for i in range(n):
        is_female = rng.random() < sex_cfg['p_female']
        sex = 'F' if is_female else 'M'
        acfg = age_cfg['female'] if is_female else age_cfg['male']
        age = age_cfg['minimum'] + rng.gamma(acfg['shape'], acfg['scale'])
        bcfg = bmi_cfg['female'] if is_female else bmi_cfg['male']
        log_bmi = rng.normal(log(float(bcfg['geometric_mean_kg_m2'])), float(bcfg['log_sd']))
        bmi = exp(log_bmi)
        if not np.isfinite(bmi) or bmi <= 0.0:
            bmi = float(bcfg['geometric_mean_kg_m2'])
        sd_tc = float(lip['residual_sd_tc_mmol_L'])
        sd_hdl = float(lip['residual_sd_hdl_mmol_L'])
        rho = float(lip['residual_correlation_tc_hdl'])
        cov = [[sd_tc * sd_tc, rho * sd_tc * sd_hdl], [rho * sd_tc * sd_hdl, sd_hdl * sd_hdl]]
        sex_ind = 1.0 if is_female else 0.0
        tc = None
        hdl = None
        for attempt in range(int(lip['max_attempts_per_row'])):
            e_tc, e_hdl = rng.multivariate_normal([0.0, 0.0], cov)
            tc = (float(lip['tc']['intercept_male'])
                  + float(lip['tc']['beta_female']) * sex_ind
                  + float(lip['tc']['beta_age_per_year']) * age
                  + float(lip['tc']['beta_bmi_per_kgm2']) * bmi
                  + e_tc)
            hdl = (float(lip['hdl']['intercept_male'])
                   + float(lip['hdl']['beta_female']) * sex_ind
                   + float(lip['hdl']['beta_age_per_year']) * age
                   + float(lip['hdl']['beta_bmi_per_kgm2']) * bmi
                   + e_hdl)
            if tc > 0.0 and hdl > 0.0 and np.isfinite(tc) and np.isfinite(hdl):
                break
        else:
            if not np.isfinite(tc) or tc <= 0.0:
                tc = float(lip['positivity_floor_for_post_check'])
            if not np.isfinite(hdl) or hdl <= 0.0:
                hdl = float(lip['positivity_floor_for_post_check'])
        rows.append({
            'id': f'id_{i:06d}',
            'age': float(age),
            'sex': sex,
            'bmi': float(bmi),
            'total_cholesterol': float(tc),
            'hdl_cholesterol': float(hdl)
        })
    return pd.DataFrame(rows, columns=columns)
