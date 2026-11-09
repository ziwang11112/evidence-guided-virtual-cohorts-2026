import numpy as np
import pandas as pd


def _scaled_beta(rng, mean, sd, lower, upper, size):
    """Beta distribution parameterized by its arithmetic mean and SD."""
    width = upper - lower
    fraction = (mean - lower) / width
    concentration = (mean - lower) * (upper - mean) / (sd * sd) - 1.0
    return lower + width * rng.beta(
        fraction * concentration, (1.0 - fraction) * concentration, size=size
    )


def generate(observed, specification, seed):
    """Draw one fictional equal-cell cohort; observed must be None."""
    if observed is not None:
        raise ValueError("This specification constructs a whole cohort from None.")
    rng = np.random.default_rng(seed)
    design = specification["design"]
    centers = specification["centers"]
    bmi_spec = specification["parameters"]["bmi"]
    glucose_spec = specification["parameters"]["glucose"]
    hb_spec = specification["parameters"]["hba1c"]
    female_parts = []
    age_parts = []
    for female_value in design["female_values"]:
        for lower, upper in design["age_bands_inclusive"]:
            count = design["rows_per_cell"]
            female_parts.append(np.full(count, female_value, dtype=np.int64))
            age_parts.append(rng.integers(lower, upper + 1, size=count))
    female = np.concatenate(female_parts)
    age = np.concatenate(age_parts)
    n = age.size
    if n != design["n_rows"]:
        raise ValueError("Cell counts must sum to the specified cohort size.")
    bmi = _scaled_beta(
        rng, bmi_spec["mean"], bmi_spec["sd"],
        bmi_spec["lower"], bmi_spec["upper"], n
    )
    conversion = specification["unit_conversion"]["glucose_mg_dl_per_mmol_l"]
    glucose_age = (
        -glucose_spec["source_young_minus_old_mmol_l"] * conversion
        / glucose_spec["assumed_age_group_midpoint_gap_years"]
    )
    glucose_bmi = glucose_spec["source_bmi_slope_mmol_l"] * conversion
    glucose_female = -glucose_spec["source_male_minus_female_mmol_l"] * conversion
    glucose_mean = (
        glucose_spec["mean_at_centers"]
        + glucose_age * (age - centers["age"])
        + glucose_bmi * (bmi - centers["bmi"])
        + glucose_female * (female - centers["female"])
    )
    glucose = _scaled_beta(
        rng, glucose_mean, glucose_spec["conditional_sd"],
        glucose_spec["lower"], glucose_spec["upper_exclusive"], n
    )
    # Roundoff protection only: no substantive eligibility clipping or rejection.
    glucose = np.minimum(
        glucose, np.nextafter(float(glucose_spec["upper_exclusive"]), -np.inf)
    )
    glucose_hb = hb_spec["conditional_glucose_slope"]
    conditional_bmi = hb_spec["reduced_bmi_slope"] - glucose_hb * glucose_bmi
    conditional_female = (
        hb_spec["reduced_female_contrast"] - glucose_hb * glucose_female
    )
    hb_mean = (
        hb_spec["mean_at_centers"]
        + hb_spec["conditional_age_slope"] * (age - centers["age"])
        + conditional_bmi * (bmi - centers["bmi"])
        + conditional_female * (female - centers["female"])
        + glucose_hb * (glucose - centers["glucose"])
    )
    shape = hb_spec["symmetric_residual_beta_shape"]
    residual = (
        hb_spec["conditional_residual_sd"] * np.sqrt(2.0 * shape + 1.0)
        * (2.0 * rng.beta(shape, shape, size=n) - 1.0)
    )
    hba1c = hb_mean + residual
    data = pd.DataFrame({
        "row_id": [f"{design['identifier_prefix']}{i + 1:06d}" for i in range(n)],
        "age": age,
        "female": female,
        "bmi": bmi,
        "glucose": glucose,
        "hba1c": hba1c,
    })
    return data.loc[:, design["column_order"]]
