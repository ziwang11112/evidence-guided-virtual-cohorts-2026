import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    rng = np.random.default_rng(seed)

    def truncated_normal(location, sd, lower, upper):
        location = np.asarray(location, dtype=float)
        values = rng.normal(loc=location, scale=sd)
        bad = (values < lower) | (values > upper)
        while np.any(bad):
            values[bad] = rng.normal(loc=location[bad], scale=sd)
            bad = (values < lower) | (values > upper)
        return values

    iron = m['iron_associated_component']
    log_s = truncated_normal(
        np.full(n, np.log(iron['untruncated_median_ug_l']), dtype=float),
        iron['log_sd'],
        np.log(iron['lower_ug_l']),
        np.log(iron['upper_ug_l'])
    )
    s = np.exp(log_s)

    inflammation = m['inflammation_like_component']
    other = m['other_hb_lowering_component']
    i = rng.random(n) < inflammation['probability']
    o = rng.random(n) < other['probability']
    ferritin = s * np.where(i, inflammation['ferritin_multiplier'], 1.0)

    h = m['hemoglobin']
    depletion = h['iron_depletion_amplitude_g_dl'] / (
        1.0 + (s / h['iron_depletion_half_scale_ug_l']) ** h['iron_depletion_power']
    )
    mu = (
        h['baseline_g_dl'] - depletion
        + inflammation['hb_shift_g_dl'] * i
        + other['hb_shift_g_dl'] * o
    )
    hb = truncated_normal(
        mu,
        h['conditional_sd_g_dl'],
        h['lower_g_dl'],
        h['upper_g_dl']
    )

    return pd.DataFrame(
        {
            'row_id': np.arange(n, dtype=np.int64),
            'hb_g_dl': hb,
            'ferritin_ug_l': ferritin
        },
        columns=['row_id', 'hb_g_dl', 'ferritin_ug_l']
    )
