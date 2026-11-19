"""A fixed statistical example from the source table, independent inside each band and status cell."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    rng = np.random.default_rng(seed)
    n = spec["task"]["n_rows"]
    groups = np.array([53, 205, 1413], dtype=float)
    low_fraction = np.array([50, 123, 331]) / groups
    prob = groups / groups.sum()
    group = rng.choice(3, n, p=prob)
    low = rng.random(n) < low_fraction[group]
    h_lower = np.log([8., 10., 12.])
    h_upper = np.log([10., 12., 16.])
    h_upper[2] = 2 * (np.log(12.99) - prob[:2] @ ((h_lower[:2] + h_upper[:2]) / 2)) / prob[2] - h_lower[2]
    hb = np.exp(rng.uniform(h_lower[group], h_upper[group]))
    log_gm = np.log([1.3, 5.9, 22.3])
    cut = np.log(15.)
    gap = np.maximum((cut-log_gm)/low_fraction, (log_gm-cut)/(1-low_fraction)) + 0.5
    center = np.where(low, (log_gm-(1-low_fraction)*gap)[group], (log_gm+low_fraction*gap)[group])
    spread = np.minimum(0.35, 0.9 * np.abs(center-cut))
    fe = np.exp(rng.uniform(center-spread, center+spread))
    return pd.DataFrame({"row_id": np.arange(n), "hb_g_dl": hb, "ferritin_ug_l": fe})
