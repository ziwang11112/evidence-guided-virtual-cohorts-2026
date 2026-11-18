import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    n = spec["task"]["n_rows"]
    model = spec["model"]
    rng = np.random.default_rng(seed)

    stable = rng.multivariate_normal(
        mean=np.asarray(model["component_mean"], dtype=float),
        cov=np.asarray(model["between_covariance"], dtype=float),
        size=n
    )
    deviations = rng.multivariate_normal(
        mean=np.asarray(model["deviation_mean"], dtype=float),
        cov=np.asarray(model["within_covariance"], dtype=float),
        size=(n, 2)
    )
    visits = stable[:, None, :] + deviations

    return pd.DataFrame({
        "person_id": np.arange(n, dtype=np.int64),
        "X_visit1": visits[:, 0, 0],
        "Y_visit1": visits[:, 0, 1],
        "X_visit2": visits[:, 1, 0],
        "Y_visit2": visits[:, 1, 1]
    }, columns=[column["name"] for column in spec["task"]["columns"]])
