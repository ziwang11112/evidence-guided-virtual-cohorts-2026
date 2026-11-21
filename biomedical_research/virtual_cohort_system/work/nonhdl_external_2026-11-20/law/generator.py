import numpy as np
import pandas as pd
from scipy.special import ndtri


def _source_sigma(item):
    mean = float(item['mean'])
    threshold = float(item['threshold'])
    probability = float(item['cdf_at_threshold'])
    if not (np.isfinite(mean) and mean > 0 and
            np.isfinite(threshold) and threshold > 0 and
            np.isfinite(probability) and 0 < probability < 1):
        raise ValueError('Invalid source marginal calibration')
    z = float(ndtri(probability))
    discriminant = z * z - 2.0 * np.log(threshold / mean)
    if discriminant < 0:
        raise ValueError('Source marginal calibration has no real solution')
    root = np.sqrt(discriminant)
    positive = [x for x in (z - root, z + root) if x > 0]
    if not positive:
        raise ValueError('Source marginal calibration has no positive solution')
    return float(min(positive))


def generate(observed, spec, seed):
    # Deliberately do not inspect observed or tune to either target sample.
    if isinstance(seed, (bool, np.bool_)) or not isinstance(seed, (int, np.integer)):
        raise ValueError('seed must be an explicit nonnegative integer')
    if int(seed) < 0:
        raise ValueError('seed must be nonnegative')

    n_raw = spec['task']['n_rows']
    if isinstance(n_raw, (bool, np.bool_)) or not isinstance(n_raw, (int, np.integer)):
        raise ValueError('n_rows must be a nonnegative integer')
    n = int(n_raw)
    if n < 0:
        raise ValueError('n_rows must be nonnegative')

    tc = np.asarray(spec['tc_mg_dl'], dtype=float)
    hdl = np.asarray(spec['hdl_mg_dl'], dtype=float)
    for values in (tc, hdl):
        if values.ndim != 1 or values.size != n:
            raise ValueError('Both marginal arrays must be one-dimensional with n_rows entries')
        if not np.all(np.isfinite(values)) or np.any(values <= 0):
            raise ValueError('Marginal arrays must contain finite positive values')
        if np.any(np.diff(values) < 0):
            raise ValueError('Marginal arrays must be sorted ascending')

    model = spec['model']
    if model['name'] != 'source_ratio_gaussian_rank_copula_v1':
        raise ValueError('Unsupported model')
    calibration = model['calibration']
    if calibration['log_scale_root_rule'] != 'smallest_positive':
        raise ValueError('Unsupported marginal root rule')
    sigma_t = _source_sigma(calibration['tc'])
    sigma_h = _source_sigma(calibration['hdl'])
    mean_t = float(calibration['tc']['mean'])
    mean_h = float(calibration['hdl']['mean'])
    mean_ratio = float(calibration['mean_individual_tc_hdl_ratio'])
    if not np.isfinite(mean_ratio) or mean_ratio <= 0:
        raise ValueError('Invalid source mean individual ratio')
    covariance = sigma_h ** 2 - np.log(mean_ratio * mean_h / mean_t)
    rho = covariance / (sigma_t * sigma_h)
    if not np.isfinite(rho) or abs(rho) > 1:
        raise ValueError('Source moments are incompatible with this Gaussian copula')

    row_id = np.arange(n, dtype=np.int64)
    if n == 0:
        return pd.DataFrame({'row_id': row_id, 'hdl_index': row_id.copy()})

    rng = np.random.default_rng(int(seed))
    tc_normal_scores = ndtri((row_id.astype(float) + 0.5) / n)
    hdl_latent = rho * tc_normal_scores + np.sqrt(1.0 - rho * rho) * rng.standard_normal(n)
    order = np.argsort(hdl_latent, kind='mergesort')
    hdl_index = np.empty(n, dtype=np.int64)
    hdl_index[order] = row_id
    return pd.DataFrame({'row_id': row_id, 'hdl_index': hdl_index})
