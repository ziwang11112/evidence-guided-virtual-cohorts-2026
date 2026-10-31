"""Fictional whole-cohort generator; scientific settings are in model_spec.json."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generation requires observed=None')
    p = spec['parameters']
    d = p['design']
    if p['distribution']['family'] != 'bivariate_lognormal':
        raise ValueError('Unsupported distribution family')
    rng = np.random.default_rng(seed)
    ages, sexes = [], []
    for sex in d['sex_values']:
        for lo, hi in d['age_bins']:
            ages.extend(rng.integers(lo, hi, size=d['rows_per_cell']).tolist())
            sexes.extend([sex] * d['rows_per_cell'])
    age = np.asarray(ages, dtype=int)
    female = np.asarray(sexes, dtype=int)
    n = len(age)
    bmi = np.empty(n, dtype=float)
    urate = np.empty(n, dtype=float)
    for sex in d['sex_values']:
        selected = female == sex
        m = p['moments_by_female'][str(sex)]
        values = {key: np.interp(age[selected], p['age_knots'], val) for key, val in m.items()}
        mb, mu = values['bmi_mean'], values['urate_mean']
        sb, su = values['bmi_sd'], values['urate_sd']
        lb = np.sqrt(np.log1p((sb / mb) ** 2))
        lu = np.sqrt(np.log1p((su / mu) ** 2))
        rho = np.log1p(values['bmi_on_urate'] * su ** 2 / (mb * mu)) / (lb * lu)
        if np.any(np.abs(rho) >= 1):
            raise ValueError('Specified moments and dependence are incompatible')
        zu = rng.standard_normal(int(selected.sum()))
        zb = rho * zu + np.sqrt(1 - rho ** 2) * rng.standard_normal(int(selected.sum()))
        urate[selected] = np.exp(np.log(mu) - lu ** 2 / 2 + lu * zu)
        bmi[selected] = np.exp(np.log(mb) - lb ** 2 / 2 + lb * zb)
    frame = pd.DataFrame({'sample_id':[d['id_prefix']+str(i+1).zfill(4) for i in range(n)],
                          'age':age,'female':female,'bmi':bmi,'urate':urate})
    if d['shuffle_rows']:
        frame = frame.iloc[rng.permutation(n)].reset_index(drop=True)
    return frame.loc[:, d['columns']]
