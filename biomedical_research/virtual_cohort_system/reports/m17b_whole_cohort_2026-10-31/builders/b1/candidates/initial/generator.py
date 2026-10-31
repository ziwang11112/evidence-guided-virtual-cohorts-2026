import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Generate fictional quota records; scientific settings live in spec."""
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    pieces = []
    for female in p["design"]["female_levels"]:
        for lower, upper in p["design"]["age_bins"]:
            count = p["design"]["rows_per_cell"]
            age = rng.integers(lower, upper, size=count)
            bmi_mean = np.interp(age, p["age_knots"], p["bmi_mean_by_female"][female])
            bmi_sd = np.interp(age, p["age_knots"], p["bmi_sd_by_female"][female])
            urate_mean = np.interp(age, p["age_knots"], p["urate_mean_by_female"][female])
            urate_sd = np.interp(age, p["age_knots"], p["urate_sd_by_female"][female])
            sigma_b = np.sqrt(np.log1p((bmi_sd / bmi_mean) ** 2))
            sigma_u = np.sqrt(np.log1p((urate_sd / urate_mean) ** 2))
            rho = p["copula_rho_by_female"][female]
            z_u = rng.standard_normal(count)
            z_b = rho * z_u + np.sqrt(1.0 - rho ** 2) * rng.standard_normal(count)
            bmi = np.exp(np.log(bmi_mean) - sigma_b ** 2 / 2.0 + sigma_b * z_b)
            urate = np.exp(np.log(urate_mean) - sigma_u ** 2 / 2.0 + sigma_u * z_u)
            pieces.append(pd.DataFrame({"age": age, "female": female, "bmi": bmi, "urate": urate}))
    frame = pd.concat(pieces, ignore_index=True)
    prefix = p["output"]["identifier_prefix"]
    frame.insert(0, "sample_id", [prefix + str(i + 1).zfill(4) for i in range(len(frame))])
    if p["output"]["shuffle_rows"]:
        frame = frame.iloc[rng.permutation(len(frame))].reset_index(drop=True)
    return frame[p["output"]["columns"]]

