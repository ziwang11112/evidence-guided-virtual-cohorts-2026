"""C01 reviewed joint scenario. Scientific settings are supplied in spec."""
import numpy as np
import pandas as pd


def _draw_lognormal(rng, size, means, sds, correlations):
    means = np.asarray(means, dtype=float)
    sds = np.asarray(sds, dtype=float)
    cv = sds / means
    log_variances = np.log1p(cv * cv)
    log_means = np.log(means) - log_variances / 2.0
    log_covariance = np.log1p(np.asarray(correlations) * np.outer(cv, cv))
    np.fill_diagonal(log_covariance, log_variances)
    factor = np.linalg.cholesky(log_covariance)
    return np.exp(log_means + rng.standard_normal((size, len(means))) @ factor.T)


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    if p["family"] != "age_conditioned_two_component_multivariate_lognormal":
        raise ValueError("Unsupported joint law")
    rng = np.random.default_rng(seed)
    count = p["n_rows"]
    low, high = p["age_bounds"]
    age = rng.integers(low, high + 1, size=count)
    female = rng.binomial(1, p["female_probability"], size=count)
    known_surrogate = rng.binomial(1, p["known_component_probability"], size=count)
    continuous = np.empty((count, len(p["continuous_columns"])), dtype=float)
    anchor = np.asarray(p["background_means_at_reference_age"], dtype=float)
    slopes = np.asarray(p["background_age_slopes"], dtype=float)
    sex_offsets = np.asarray(p["conditional_female_offsets"], dtype=float)
    for current_age in range(low, high + 1):
        for current_sex in (0, 1):
            indices = np.flatnonzero((known_surrogate == 0) &
                                     (age == current_age) & (female == current_sex))
            if indices.size:
                means = anchor + slopes * (current_age - p["background_reference_age"])
                means = means + sex_offsets * (current_sex - p["female_probability"])
                continuous[indices] = _draw_lognormal(
                    rng, indices.size, means, p["background_conditional_sds"],
                    p["conditional_raw_correlation_matrix"])
    for current_sex in (0, 1):
        indices = np.flatnonzero((known_surrogate == 1) & (female == current_sex))
        if indices.size:
            means = np.asarray(p["known_component_arithmetic_means"], dtype=float)
            means = means + sex_offsets * (current_sex - p["female_probability"])
            continuous[indices] = _draw_lognormal(
                rng, indices.size, means, p["known_component_arithmetic_sds"],
                p["conditional_raw_correlation_matrix"])
    if not np.isfinite(continuous).all() or not (continuous > 0).all():
        raise ValueError("Nonfinite or nonpositive output; no clipping or resampling")
    result = {"row_id": [p["row_id_prefix"] + str(i + 1) for i in range(count)],
              "age": age, "female": female}
    for index, name in enumerate(p["continuous_columns"]):
        result[name] = continuous[:, index]
    return pd.DataFrame(result, columns=p["output_columns"])
