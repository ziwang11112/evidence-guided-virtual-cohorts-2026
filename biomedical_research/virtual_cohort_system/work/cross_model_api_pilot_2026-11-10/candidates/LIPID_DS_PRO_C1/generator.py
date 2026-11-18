import numpy as np
import pandas as pd
import math

def generate(observed, spec, seed):
    _ = observed
    task = spec['task']
    model = spec['model']
    n = int(task['n_rows'])
    columns = [c['name'] for c in task['columns']]
    rng = np.random.default_rng(seed)

    cov = model['joint_law']['covariates']
    out = model['joint_law']['outcome_linear_models']
    resid = model['joint_law']['residual_dependency']
    rho = float(resid['pearson_correlation'])
    factor_vals = np.asarray(resid['factor_values'], dtype=float)
    a = math.sqrt(1.0 - rho)
    b = math.sqrt(rho)

    sex_p = float(cov['sex']['p_female'])
    age_lower = float(cov['age']['lower'])
    age_upper = float(cov['age']['upper'])
    bmi_lower = float(cov['bmi']['lower'])
    bmi_upper = float(cov['bmi']['upper'])

    ids = np.array([f'id_{i:04d}' for i in range(n)], dtype=str)
    sex = np.where(rng.random(n) < sex_p, 'F', 'M')
    female = (sex == 'F').astype(float)
    age = rng.uniform(age_lower, age_upper, size=n)
    bmi = rng.uniform(bmi_lower, bmi_upper, size=n)

    z1 = rng.choice(factor_vals, size=n, replace=True)
    z2 = rng.choice(factor_vals, size=n, replace=True)
    common = rng.choice(factor_vals, size=n, replace=True)

    tc = out['total_cholesterol']
    hdl = out['hdl_cholesterol']

    eps_tc = float(tc['residual_sd']) * (a * z1 + b * common)
    eps_hdl = float(hdl['residual_sd']) * (a * z2 + b * common)

    fitted_tc = (float(tc['intercept'])
                 + float(tc['age_coef']) * age
                 + float(tc['sex_female_coef']) * female
                 + float(tc['bmi_coef']) * bmi)
    fitted_hdl = (float(hdl['intercept'])
                  + float(hdl['age_coef']) * age
                  + float(hdl['sex_female_coef']) * female
                  + float(hdl['bmi_coef']) * bmi)

    total_cholesterol = fitted_tc + eps_tc
    hdl_cholesterol = fitted_hdl + eps_hdl

    if not (np.all(np.isfinite(age)) and np.all(np.isfinite(bmi))
            and np.all(np.isfinite(total_cholesterol))
            and np.all(np.isfinite(hdl_cholesterol))
            and np.all(age >= age_lower) and np.all(age <= age_upper)
            and np.all(bmi >= bmi_lower) and np.all(bmi <= bmi_upper)
            and np.all(total_cholesterol > 0) and np.all(hdl_cholesterol > 0)):
        raise RuntimeError('Generated values violate task bounds or finiteness.')

    data = {
        'id': ids,
        'age': age,
        'sex': sex,
        'bmi': bmi,
        'total_cholesterol': total_cholesterol,
        'hdl_cholesterol': hdl_cholesterol
    }
    return pd.DataFrame(data, columns=columns)