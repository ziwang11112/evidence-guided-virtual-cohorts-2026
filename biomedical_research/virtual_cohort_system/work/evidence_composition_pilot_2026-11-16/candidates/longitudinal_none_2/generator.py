def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = spec["task"]["n_rows"]
    model = spec["model"]
    rng = np.random.default_rng(seed)
    means = np.asarray(model["measurement_means"], dtype=float)
    bv = np.asarray(model["between_person_variances"], dtype=float)
    wv = np.asarray(model["within_person_variances"], dtype=float)
    rb = float(model["between_person_correlation"])
    rw = float(model["within_visit_deviation_correlation"])

    # Independent rows; independent stable components and visit deviations.
    z_between = rng.standard_normal((n, 2))
    z_within = rng.standard_normal((n, 2, 2))
    stable_x = np.sqrt(bv[0]) * z_between[:, 0]
    stable_y = np.sqrt(bv[1]) * (
        rb * z_between[:, 0] + np.sqrt(1.0 - rb * rb) * z_between[:, 1]
    )
    deviation_x = np.sqrt(wv[0]) * z_within[:, :, 0]
    deviation_y = np.sqrt(wv[1]) * (
        rw * z_within[:, :, 0] + np.sqrt(1.0 - rw * rw) * z_within[:, :, 1]
    )
    x = means[0] + stable_x[:, None] + deviation_x
    y = means[1] + stable_y[:, None] + deviation_y

    return pd.DataFrame({
        "person_id": np.arange(n, dtype=np.int64),
        "X_visit1": x[:, 0],
        "Y_visit1": y[:, 0],
        "X_visit2": x[:, 1],
        "Y_visit2": y[:, 1]
    }, columns=["person_id", "X_visit1", "Y_visit1", "X_visit2", "Y_visit2"])
