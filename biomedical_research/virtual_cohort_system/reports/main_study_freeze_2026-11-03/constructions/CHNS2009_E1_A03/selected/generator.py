"""Whole-cohort latent-factor scenario. Controller execution only."""
import math
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generator requires observed=None')
    p = spec['parameters']
    n = int(p['n_rows'])
    rng = np.random.default_rng(seed)
    age = rng.integers(p['target_age']['minimum'], p['target_age']['maximum'] + 1, size=n)
    female = rng.binomial(1, p['target_female_probability'], size=n)
    innovations = rng.standard_normal((n, 3))
    r_bg = p['dependence']['latent_bmi_glucose']
    r_gh = 2 * math.sin(math.pi * p['dependence']['source_spearman_glucose_hba1c'] / 6)
    z_g = innovations[:, 0]
    z_b = r_bg * z_g + math.sqrt(1-r_bg*r_bg) * innovations[:, 1]
    z_h = r_gh * z_g + math.sqrt(1-r_gh*r_gh) * innovations[:, 2]
    values = {}
    for name, latent in [('bmi', z_b), ('glucose', z_g), ('hba1c', z_h)]:
        mean = p['target_marginals'][name]['mean']
        sd = p['target_marginals'][name]['sd']
        variance_log = math.log1p((sd/mean)**2)
        mean_log = math.log(mean) - variance_log/2
        values[name] = np.exp(mean_log + math.sqrt(variance_log)*latent)
    frame = pd.DataFrame({
        'row_id': [p['row_id_prefix'] + str(i+1).zfill(6) for i in range(n)],
        'age': age,
        'female': female,
        'bmi': values['bmi'],
        'glucose': values['glucose'],
        'hba1c': values['hba1c'],
    })
    if not np.isfinite(frame[['age','female','bmi','glucose','hba1c']].to_numpy()).all():
        raise FloatingPointError('Nonfinite floating-point realization; no replacement or clipping is allowed')
    if not (frame[['bmi','glucose','hba1c']].to_numpy() > 0).all():
        raise FloatingPointError('Nonpositive floating-point realization; no replacement or clipping is allowed')
    return frame
