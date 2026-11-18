import numpy as np
import pandas as pd
from scipy.special import ndtri


def generate(observed, spec, seed):
    task = spec["task"]
    model = spec["model"]
    n = int(task["n_rows"])
    names = model["latent_order"]
    index = {name: j for j, name in enumerate(names)}
    correlation = np.eye(len(names))
    for link in model["dependence"]["rank_links"]:
        a, b = link["variables"]
        value = 2 * np.sin(np.pi * link["spearman_rho"] / 6)
        correlation[index[a], index[b]] = value
        correlation[index[b], index[a]] = value
    for link in model["dependence"]["latent_links"]:
        a, b = link["variables"]
        value = link["pearson_rho"]
        correlation[index[a], index[b]] = value
        correlation[index[b], index[a]] = value
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((n, len(names))) @ np.linalg.cholesky(correlation).T
    result = {task["row_id"]: ["v" + str(j) for j in range(n)]}
    for name, margin in model["margins"].items():
        mean = margin["mean_above_offset"]
        sd = margin["sd_above_offset"]
        variance_log = np.log1p((sd / mean) ** 2)
        location_log = np.log(mean) - variance_log / 2
        result[name] = margin["offset"] + np.exp(
            location_log + np.sqrt(variance_log) * z[:, index[margin["latent_name"]]]
        )
    sex = model["recorded_sex"]
    threshold = ndtri(1 - sex["probability_F"])
    result["sex"] = np.where(
        z[:, index["sex_score"]] > threshold,
        sex["above_threshold_code"],
        sex["otherwise_code"],
    )
    return pd.DataFrame(result, columns=[column["name"] for column in task["columns"]])
