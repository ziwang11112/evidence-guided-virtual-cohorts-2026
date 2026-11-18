import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    # observed is intentionally unused: there are no observed target rows.
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative')
    model = spec['model']
    law = model['law']
    if law not in ('single_dp_lognormal', 'two_class_dp_lognormal'):
        raise ValueError('Unknown population law')

    c = model['calibration']
    ms = float(c['mean_sbp'])
    md = float(c['mean_dbp'])
    vs = float(c['sd_sbp']) ** 2
    vd = float(c['sd_dbp']) ** 2
    csd = float(c['pearson_sbp_dbp']) * float(c['sd_sbp']) * float(c['sd_dbp'])

    # Population coordinates are D = DBP and P = SBP - DBP.
    mean_dp = np.array([md, ms - md], dtype=float)
    cov_dp = np.array([[vd, csd - vd],
                       [csd - vd, vs + vd - 2.0 * csd]], dtype=float)
    weights = np.asarray(model['component_weights'], dtype=float)
    offsets = np.asarray(model['component_mean_offsets_dbp_pulse'], dtype=float)
    k = len(weights)
    if offsets.shape != (k, 2):
        raise ValueError('Invalid component offsets')
    if np.any(weights <= 0.0) or not np.isclose(weights.sum(), 1.0, atol=1e-12, rtol=0.0):
        raise ValueError('Invalid mixture weights')
    if not np.allclose(weights @ offsets, np.zeros(2), atol=1e-12, rtol=0.0):
        raise ValueError('Population mean offsets must average to zero')
    if (law == 'single_dp_lognormal' and k != 1) or (law == 'two_class_dp_lognormal' and k != 2):
        raise ValueError('Law and component count disagree')

    # All calibration below is population-level algebra, not sample adjustment.
    component_means = mean_dp[None, :] + offsets
    if np.any(component_means <= 0.0):
        raise ValueError('Component means must be positive')
    between_cov = offsets.T @ (weights[:, None] * offsets)
    within_cov = cov_dp - between_cov
    log_parameters = []
    for j in range(k):
        cm = component_means[j]
        ratios = within_cov / np.outer(cm, cm)
        if np.any(ratios <= -1.0):
            raise ValueError('Invalid lognormal covariance')
        log_cov = np.log1p(ratios)
        chol = np.linalg.cholesky(log_cov)
        log_mean = np.log(cm) - 0.5 * np.diag(log_cov)
        log_parameters.append((log_mean, chol))

    rng = np.random.default_rng(seed)
    labels = rng.choice(k, size=n, p=weights)
    z = rng.standard_normal((n, 2))
    dp = np.empty((n, 2), dtype=float)
    for j, (log_mean, chol) in enumerate(log_parameters):
        idx = np.flatnonzero(labels == j)
        dp[idx, :] = np.exp(log_mean + z[idx, :] @ chol.T)

    dbp = dp[:, 0]
    sbp = dbp + dp[:, 1]
    return pd.DataFrame({
        'person_id': np.arange(1, n + 1, dtype=np.int64),
        'SBP': sbp,
        'DBP': dbp
    }, columns=['person_id', 'SBP', 'DBP'])
