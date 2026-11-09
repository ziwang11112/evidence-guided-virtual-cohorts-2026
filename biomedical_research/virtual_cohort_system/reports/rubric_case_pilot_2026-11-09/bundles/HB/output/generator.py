"""Developmental whole-cohort construction; no participant data or I/O."""

import numpy as np
import pandas as pd


def _truncated_normal(rng, location, scale, lower, upper):
    """Independent normal draws conditioned on an open interval, not clipped."""
    location, scale = np.broadcast_arrays(
        np.asarray(location, dtype=float), np.asarray(scale, dtype=float)
    )
    values = rng.normal(location, scale)
    bad = (~np.isfinite(values)) | (values <= lower) | (values >= upper)
    while np.any(bad):
        values[bad] = rng.normal(location[bad], scale[bad])
        bad = (~np.isfinite(values)) | (values <= lower) | (values >= upper)
    return values


def generate(observed, specification, seed):
    """Return the exact requested columns for 3,000 fictional individuals."""
    if observed is not None:
        raise ValueError("This specification accepts no participant input.")
    rng = np.random.default_rng(seed)
    design = specification["design"]
    p = specification["parameters"]
    cell_size = int(design["rows_per_cell"])
    ages, sexes = [], []
    for female in design["female_values"]:
        for lower_age, upper_age in design["age_bands_inclusive"]:
            years = np.arange(lower_age, upper_age + 1, dtype=np.int64)
            repetitions, remainder = divmod(cell_size, years.size)
            cell_age = np.concatenate(
                (np.tile(years, repetitions), rng.permutation(years)[:remainder])
            )
            ages.append(rng.permutation(cell_age))
            sexes.append(np.full(cell_size, female, dtype=np.int64))
    age = np.concatenate(ages)
    female = np.concatenate(sexes)
    n = age.size
    if n != design["n_rows"] or n != 3000:
        raise ValueError("The submitted analytical design requires 3,000 rows.")

    bmi_p = p["bmi"]
    log_location = np.log(bmi_p["untruncated_arithmetic_mean"]) - (
        bmi_p["log_sd"] ** 2 / 2.0
    )
    log_bmi = _truncated_normal(
        rng, np.full(n, log_location), bmi_p["log_sd"],
        np.log(bmi_p["lower"]), np.log(bmi_p["upper"])
    )
    bmi = np.exp(log_bmi)

    centers = p["centers"]
    g_p = p["glucose"]
    glucose_bmi = g_p["mmol_to_mgdl"] * g_p["bmi_slope_mmol_per_bmi"]
    glucose_female = -g_p["mmol_to_mgdl"] * g_p["male_difference_mmol"]
    glucose_location = (
        g_p["reference_location"]
        + g_p["age_slope_mgdl_per_year"] * (age - centers["age"])
        + glucose_female * female
        + glucose_bmi * (bmi - centers["bmi"])
    )
    glucose = _truncated_normal(
        rng, glucose_location, g_p["residual_sd"], g_p["lower"], g_p["upper"]
    )

    h_p = p["hba1c"]
    direct_bmi = (
        h_p["reference_total_bmi_slope"] - h_p["glucose_slope"] * glucose_bmi
    )
    hba1c_location = (
        h_p["reference_location"]
        + h_p["age_slope_per_year"] * (age - centers["age"])
        + h_p["female_difference"] * female
        + direct_bmi * (bmi - centers["bmi"])
        + h_p["glucose_slope"] * (glucose - centers["glucose"])
    )
    hba1c_scale = (
        h_p["residual_sd_at_center_age"]
        + h_p["residual_sd_age_slope"] * (age - centers["age"])
    )
    hba1c = _truncated_normal(
        rng, hba1c_location, hba1c_scale, h_p["lower"], h_p["upper"]
    )

    order = rng.permutation(n)
    frame = pd.DataFrame({
        "row_id": [f"{design['identifier_prefix']}{i + 1:06d}" for i in range(n)],
        "age": age[order],
        "female": female[order],
        "bmi": bmi[order],
        "glucose": glucose[order],
        "hba1c": hba1c[order],
    })
    return frame.loc[:, specification["output_columns"]]
