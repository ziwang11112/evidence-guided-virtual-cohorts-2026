"""An assumed additive enrichment model for invented fixture summaries.

No source summaries, source IDs or target outcomes are consulted at runtime.
"""
import numpy as np


def generate(observed, spec, seed):
    """Preserve observed cells and append one independent residual draw per row."""
    p = spec["parameters"]
    if p["residual_law"] != "symmetric_triangular":
        raise ValueError("Unsupported declared residual law")
    sigma = float(p["residual_sd"])
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("residual_sd must be finite and positive")
    result = observed.copy(deep=True)
    x = observed["x"].to_numpy(dtype=float)
    z = observed["z"].to_numpy(dtype=float)
    mean = float(p["intercept"]) + float(p["beta_x"]) * x + float(p["beta_z"]) * z
    half_width = np.sqrt(6.0) * sigma
    residual = np.random.default_rng(seed).triangular(-half_width, 0.0, half_width, size=len(observed))
    result["y"] = mean + residual
    return result
