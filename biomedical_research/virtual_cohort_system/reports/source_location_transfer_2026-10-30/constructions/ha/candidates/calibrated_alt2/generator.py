"""Source-informed enrichment. Scientific execution is harness-only."""
import numpy as np

def generate(observed, spec, seed):
    p = spec["parameters"]
    result = observed.copy(deep=True)
    male = observed["sex"].to_numpy() == "male"
    age = observed["age_years"].to_numpy(dtype=float)
    bmi = observed["bmi_kg_m2"].to_numpy(dtype=float)
    location = np.where(male, p["location_pct"]["male"], p["location_pct"]["female"])
    age_slope = np.where(male, p["age_slope_per_year"]["male"], p["age_slope_per_year"]["female"])
    scale = np.where(male, p["residual_scale_pct"]["male"], p["residual_scale_pct"]["female"])
    rng = np.random.default_rng(seed)
    residual = scale * np.expm1(p["residual_log_sigma"] * rng.standard_normal(len(observed)))
    bmi_term = p["bmi_amplitude_pct"] * np.tanh((bmi - p["bmi_reference"]) / p["bmi_scale"])
    y = location + age_slope * (age-p["age_reference"]) + bmi_term + residual
    result["hba1c_pct"] = np.clip(y, *p["output_bounds_pct"])
    return result
