"""Prespecified matched-moment statistical comparator, independently of the Agent."""
import numpy as np
import pandas as pd


def latent_parameters(source):
    mean_s, mean_d = source["means"]["SBP"], source["means"]["DBP"]
    sd_s, sd_d = source["sd"]["SBP"], source["sd"]["DBP"]
    cov_sd = sd_s * sd_d * source["pearson"]
    means = np.array([mean_d, mean_s - mean_d])
    cov_dg = cov_sd - sd_d ** 2
    covariance = np.array([[sd_d ** 2, cov_dg],
                           [cov_dg, sd_s ** 2 + sd_d ** 2 - 2 * cov_sd]])
    latent = np.log1p(covariance / np.outer(means, means))
    if np.min(means) <= 0 or np.min(np.linalg.eigvalsh(latent)) <= 0:
        raise ValueError("Incompatible moments for positive bivariate lognormal pressures")
    return np.log(means) - np.diag(latent) / 2, latent


def generate(observed, spec, seed):
    n = spec["task"]["n_rows"]
    mu, cov = latent_parameters(spec["model"])
    rng = np.random.default_rng(seed)
    dbp, gap = np.exp(rng.multivariate_normal(mu, cov, size=n)).T
    return pd.DataFrame({"person_id": np.arange(1, n + 1), "SBP": dbp + gap, "DBP": dbp})
