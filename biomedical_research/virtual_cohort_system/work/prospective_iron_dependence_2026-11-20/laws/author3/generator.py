import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    model = spec['model']
    supplied_bands = spec['bands']
    if len(supplied_bands) != 3:
        raise ValueError('Exactly three Hb bands are required.')

    bands = []
    for b, supplied in enumerate(supplied_bands):
        hb = np.asarray(supplied['hb'], dtype=float)
        fe = np.asarray(supplied['ferritin'], dtype=float)
        if hb.ndim != 1 or fe.ndim != 1 or len(hb) != len(fe):
            raise ValueError('Each band must contain equal-length one-dimensional margins.')
        if not np.all(np.isfinite(hb)) or not np.all(np.isfinite(fe)):
            raise ValueError('Margins must be finite.')
        if np.any(fe <= 0):
            raise ValueError('Ferritin must be positive for log-scale calibration.')
        if np.any(np.diff(hb) < 0) or np.any(np.diff(fe) < 0):
            raise ValueError('Margins must be sorted separately.')
        valid_hb = (hb < 12) if b == 0 else (((hb >= 12) & (hb < 14)) if b == 1 else (hb >= 14))
        if not np.all(valid_hb):
            raise ValueError('Hb values do not match their declared band.')
        bands.append((hb, fe))

    total = sum(len(hb) for hb, fe in bands)
    if total != int(spec['task']['n_rows']):
        raise ValueError('Band lengths do not sum to n_rows.')

    nd = NormalDist()
    sqrt2 = math.sqrt(2.0)

    def normal_scores(probabilities):
        return np.fromiter((nd.inv_cdf(float(p)) for p in probabilities), dtype=float, count=len(probabilities))

    def normal_cdf(values):
        return np.fromiter((0.5 * math.erfc(-float(v) / sqrt2) for v in values), dtype=float, count=len(values))

    lower, upper = map(float, model['rho_bounds'])
    if not (0.0 <= lower < upper < 1.0):
        raise ValueError('Invalid copula correlation bounds.')
    ratio = float(model['middle_band_gm_ratio'])
    if ratio <= 1.0:
        raise ValueError('This positive-association model requires a ratio greater than one.')
    target = math.log(ratio)

    # Analytic fallback: a median Hb split and normally distributed log ferritin.
    log_sd = math.log(float(model['fallback_middle_ferritin_gsd']))
    if log_sd <= 0:
        raise ValueError('Fallback geometric SD must exceed one.')
    rho = target / (2.0 * math.sqrt(2.0 / math.pi) * log_sd)
    rho = float(np.clip(rho, lower, upper))

    mid_hb, mid_fe = bands[1]
    k = len(mid_hb)
    if k >= 2:
        p_low = float(np.mean(mid_hb < float(model['middle_band_hb_split'])))
        if 0.0 < p_low < 1.0:
            z = normal_scores((np.arange(k, dtype=float) + 0.5) / k)
            threshold = nd.inv_cdf(p_low)
            log_fe = np.log(mid_fe)
            centered_log_fe = log_fe - log_fe.mean()

            def expected_log_contrast(r):
                # Midpoint normal-score quadrature over the fixed ferritin margin.
                # w is P(upper Hb subgroup | ferritin latent normal score).
                w = normal_cdf((r * z - threshold) / math.sqrt(1.0 - r * r))
                upper_mean = np.dot(w, centered_log_fe) / w.sum()
                low_weights = 1.0 - w
                lower_mean = np.dot(low_weights, centered_log_fe) / low_weights.sum()
                return float(upper_mean - lower_mean)

            d_lower = expected_log_contrast(lower)
            d_upper = expected_log_contrast(upper)
            if target <= d_lower:
                rho = lower
            elif target >= d_upper:
                # Feasible-bound projection if finite margins cannot support the contrast.
                rho = upper
            else:
                left, right = lower, upper
                for _ in range(int(model['calibration_steps'])):
                    middle = 0.5 * (left + right)
                    if expected_log_contrast(middle) < target:
                        left = middle
                    else:
                        right = middle
                rho = 0.5 * (left + right)

    rng = np.random.default_rng(seed)
    residual_sd = math.sqrt(1.0 - rho * rho)
    permutations = []
    for hb, fe in bands:
        k = len(hb)
        if k == 0:
            permutation = np.empty(0, dtype=np.int64)
        else:
            # Average ranks preserve exchangeability among any tied Hb values.
            ranks = pd.Series(hb).rank(method='average').to_numpy(dtype=float)
            x = normal_scores((ranks - 0.5) / k)
            latent_fe = rho * x + residual_sd * rng.standard_normal(k)
            order = np.argsort(latent_fe, kind='mergesort')
            permutation = np.empty(k, dtype=np.int64)
            permutation[order] = np.arange(k, dtype=np.int64)

        if not np.array_equal(np.sort(permutation), np.arange(k, dtype=np.int64)):
            raise RuntimeError('Invalid ferritin permutation.')
        if np.count_nonzero(fe[permutation] < 15.0) != np.count_nonzero(fe < 15.0):
            raise RuntimeError('Ferritin threshold count changed.')
        permutations.append(permutation)

    return pd.DataFrame({
        'row_id': np.arange(total, dtype=np.int64),
        'fe_index': np.concatenate(permutations).astype(np.int64, copy=False)
    }, columns=['row_id', 'fe_index'])
