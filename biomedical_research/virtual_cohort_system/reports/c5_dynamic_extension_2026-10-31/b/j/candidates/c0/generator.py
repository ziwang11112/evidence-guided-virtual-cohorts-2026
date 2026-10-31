"""Independent full joint draws from the final artificial C5 source."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    if p["distribution"] != "multivariate_normal" or p["random_generator"] != "PCG64":
        raise ValueError("Unsupported distribution or random generator")
    means = np.asarray(p["mean_vector"], dtype=float)
    covariance = np.asarray(p["covariance_matrix"], dtype=float)
    lower = np.linalg.cholesky(covariance)
    rng = np.random.Generator(np.random.PCG64(seed))
    standard_normals = rng.standard_normal((p["n_rows"], len(p["variable_order"])))
    values = means + standard_normals @ lower.T
    identifier = p["identifier"]
    row_ids = [identifier["prefix"] + str(i).zfill(identifier["width"])
               for i in range(identifier["start"], identifier["start"] + p["n_rows"])]
    output = pd.DataFrame(values, columns=p["variable_order"])
    output.insert(0, identifier["column"], row_ids)
    return output
