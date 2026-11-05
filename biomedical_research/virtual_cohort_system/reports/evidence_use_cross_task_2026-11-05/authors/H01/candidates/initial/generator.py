"""H01 reviewed hypothetical whole-cohort law. No I/O or import-time sampling."""
import numpy as np
import pandas as pd


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort construction requires observed=None")
    p = specification["parameters"]
    d, b, g, h = (p[key] for key in ("design", "bmi", "glucose", "hba1c"))
    rng = np.random.default_rng(seed)
    ages = []
    sexes = []
    for cell in d["cells"]:
        ages.append(rng.integers(cell["age_min"], cell["age_max"] + 1,
                                 size=d["rows_per_cell"]))
        sexes.append(np.full(d["rows_per_cell"], cell["female"], dtype=np.int64))
    age = np.concatenate(ages)
    female = np.concatenate(sexes)
    n = len(age)

    width = b["upper"] - b["lower"]
    fraction = (b["mean"] - b["lower"]) / width
    concentration = ((b["mean"] - b["lower"]) * (b["upper"] - b["mean"])
                     / b["sd"] ** 2 - 1)
    alpha = fraction * concentration
    beta = (1 - fraction) * concentration
    if not (width > 0 and alpha > 0 and beta > 0):
        raise ValueError("Invalid bounded BMI moment specification")
    bmi = b["lower"] + width * rng.beta(alpha, beta, n)

    glucose_location = (g["intercept"] + g["age_slope"] * (age - g["age_center"])
                        + g["female_slope"] * (female - g["female_center"])
                        + g["bmi_slope"] * (bmi - g["bmi_center"]))
    glucose = rng.normal(glucose_location, g["kernel_sd"])
    invalid = (glucose <= g["lower"]) | (glucose >= g["upper"])
    rounds = 0
    while np.any(invalid):
        if rounds >= p["implementation"]["max_glucose_redraw_rounds"]:
            raise RuntimeError("Conditional glucose rejection guard reached")
        # Only redraw G; A/F/B remain fixed. No clipping or whole-row rejection.
        glucose[invalid] = rng.normal(glucose_location[invalid], g["kernel_sd"])
        invalid = (glucose <= g["lower"]) | (glucose >= g["upper"])
        rounds += 1

    hba1c_location = (h["intercept"] + h["age_slope"] * (age - h["age_center"])
                      + h["female_slope"] * (female - h["female_center"])
                      + h["bmi_slope"] * (bmi - h["bmi_center"])
                      + h["glucose_slope"] * (glucose - h["glucose_center"]))
    residual_scale = h["residual_sd"] / np.sqrt(h["residual_shape"])
    residual_mean = h["residual_shape"] * residual_scale
    residual = rng.gamma(h["residual_shape"], residual_scale, n) - residual_mean
    hba1c = hba1c_location + residual
    if not (np.all(np.isfinite(bmi)) and np.all(np.isfinite(glucose))
            and np.all(np.isfinite(hba1c)) and np.all(hba1c > 0)):
        raise RuntimeError("Nonfinite or nonpositive output; no repair is permitted")
    frame = pd.DataFrame({
        "row_id": [d["row_id_prefix"] + str(index + 1).zfill(d["row_id_digits"])
                   for index in range(n)],
        "age": age, "female": female, "bmi": bmi,
        "glucose": glucose, "hba1c": hba1c,
    })
    return frame[d["output_columns"]]
