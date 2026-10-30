import numpy as np

def generate(observed, spec, seed):
    p = spec["parameters"]
    result = observed.copy(deep=True)
    sex = observed["sex"].to_numpy()
    age = observed["age_years"].to_numpy(dtype=float)
    bmi = observed["bmi_kg_m2"].to_numpy(dtype=float)
    location = np.array([p["location_by_sex"][s] for s in sex], dtype=float)
    slope = np.array([p["age_slope_by_sex"][s] for s in sex], dtype=float)
    z = np.random.default_rng(seed).standard_normal(len(observed))
    residual = p["residual_scale"] * np.expm1(p["residual_log_sd"] * z)
    result["hba1c_pct"] = location + slope * (age - p["reference_age"]) + p["bmi_slope"] * (bmi - p["reference_bmi"]) + residual
    return result
