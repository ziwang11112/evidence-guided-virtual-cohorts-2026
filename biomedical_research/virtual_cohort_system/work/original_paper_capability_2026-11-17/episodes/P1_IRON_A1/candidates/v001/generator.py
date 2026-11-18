def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd
    from scipy.special import ndtr, ndtri
    from scipy.optimize import brentq

    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    hb = spec['hemoglobin']
    weights = np.asarray(hb['weights'], dtype=float)
    means = np.asarray(hb['means_g_dl'], dtype=float)
    sds = np.asarray(hb['sds_g_dl'], dtype=float)
    lower, upper = hb['support_g_dl']
    pl = ndtr((lower - means) / sds)
    pu = ndtr((upper - means) / sds)
    def hb_cdf(x):
        x = np.asarray(x)
        vals = (ndtr((x[..., None] - means) / sds) - pl) / (pu - pl)
        return np.sum(weights * vals, axis=-1)

    ferr = spec['ferritin']
    mu_f = np.log(ferr['geometric_mean_ug_l'])
    p_f = ferr['probability_below_15']
    sigma_f = (np.log(15.0) - mu_f) / ndtri(p_f)
    p_h = float(hb_cdf(12.0))
    target_or = spec['dependence']['crude_or_expression'][0] * spec['dependence']['crude_or_expression'][3] / (spec['dependence']['crude_or_expression'][1] * spec['dependence']['crude_or_expression'][2])

    def joint_prob(theta):
        # Clayton lower-tail copula; this is a population-law calculation,
        # not a fit to the generated sample.
        return (np.exp(-theta * np.log(p_h)) + np.exp(-theta * np.log(p_f)) - 1.0) ** (-1.0 / theta)
    def or_equation(theta):
        a = joint_prob(theta)
        return np.log(a) + np.log(1.0-p_h-p_f+a) - np.log(p_h-a) - np.log(p_f-a) - np.log(target_or)
    theta = brentq(or_equation, 1.e-5, 5.0, xtol=1.e-12)

    # Marshall-Olkin sampling: independent virtual people, Clayton uniforms.
    w = rng.gamma(shape=1.0/theta, scale=1.0, size=n)
    e = rng.exponential(scale=1.0, size=(n, 2))
    uniforms = np.exp(-np.log1p(e / w[:, None]) / theta)
    uniforms = np.clip(uniforms, np.nextafter(0.0, 1.0), np.nextafter(1.0, 0.0))
    f = np.exp(mu_f + sigma_f * ndtri(uniforms[:, 1]))
    # Invert the fixed mixture CDF by vectorized bisection.
    lo = np.full(n, lower, dtype=float)
    hi = np.full(n, upper, dtype=float)
    for _ in range(60):
        mid = (lo + hi) / 2.0
        below = hb_cdf(mid) < uniforms[:, 0]
        lo = np.where(below, mid, lo)
        hi = np.where(below, hi, mid)
    h = (lo + hi) / 2.0
    return pd.DataFrame({'row_id': np.arange(1, n+1, dtype=np.int64),
                         'hb_g_dl': h,
                         'ferritin_ug_l': f})
