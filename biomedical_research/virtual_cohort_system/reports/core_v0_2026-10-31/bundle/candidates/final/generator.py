"""Source-only artificial gamma cohort; no individual data are recovered."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Generate the fixed design using the specification's scientific settings."""
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None")
    parameters = spec["parameters"]
    if parameters["distribution"] != "gamma":
        raise ValueError("Unsupported distribution")
    if parameters["random_generator"] != "numpy_default_rng":
        raise ValueError("Unsupported random generator")
    x_values = parameters["x_values"]
    counts = parameters["rows_per_stratum"]
    shapes = parameters["gamma_shape_by_stratum"]
    scales = parameters["gamma_scale_by_stratum"]
    if not (len(x_values) == len(counts) == len(shapes) == len(scales)):
        raise ValueError("Stratum settings must align")
    if len(set(x_values)) != len(x_values):
        raise ValueError("Strata must be distinct")
    if any(type(count) is not int or count <= 0 for count in counts):
        raise ValueError("Each stratum count must be a positive integer")
    if any(shape <= 0 for shape in shapes) or any(scale <= 0 for scale in scales):
        raise ValueError("Gamma shape and scale must be positive")

    rng = np.random.default_rng(seed)
    x = np.repeat(np.asarray(x_values, dtype=np.int64), counts)
    y = np.concatenate([
        rng.gamma(shape=shape, scale=scale, size=count)
        for shape, scale, count in zip(shapes, scales, counts)
    ])
    row_count = sum(counts)
    return pd.DataFrame({
        "sample_id": [parameters["row_id_prefix"] + f"{index:06d}"
                      for index in range(1, row_count + 1)],
        "x": x,
        "group": np.full(row_count, parameters["group_value"], dtype=np.int64),
        "y": y,
    })
