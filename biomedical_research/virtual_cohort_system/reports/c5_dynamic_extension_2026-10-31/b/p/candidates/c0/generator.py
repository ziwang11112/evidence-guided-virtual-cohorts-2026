"""Independent draws from the explicitly artificial C5 initial population.

All scientific and row-layout settings are supplied by model_spec.json.
The controller supplies the seed; this program does not search or replace it.
"""

import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None")
    parameters = spec["parameters"]
    if parameters["distribution"] != "multivariate_normal":
        raise ValueError("Unsupported distribution")
    if parameters["random_generator"] != "PCG64":
        raise ValueError("Unsupported random generator")

    n_rows = parameters["n_rows"]
    means = np.asarray(parameters["mean_vector"], dtype=float)
    covariance = np.asarray(parameters["covariance_matrix"], dtype=float)
    columns = parameters["variable_order"]
    lower = np.linalg.cholesky(covariance)
    rng = np.random.Generator(np.random.PCG64(seed))
    independent_normals = rng.standard_normal((n_rows, len(columns)))
    values = means + independent_normals @ lower.T

    identifier = parameters["identifier"]
    row_ids = [
        identifier["prefix"] + str(index).zfill(identifier["width"])
        for index in range(identifier["start"], identifier["start"] + n_rows)
    ]
    output = pd.DataFrame(values, columns=columns)
    output.insert(0, identifier["column"], row_ids)
    return output
