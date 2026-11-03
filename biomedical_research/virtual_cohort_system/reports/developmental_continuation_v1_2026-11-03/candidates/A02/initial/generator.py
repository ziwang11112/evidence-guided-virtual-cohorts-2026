"""One frozen eligible-population construction; no author-side execution."""
import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation accepts no participant input")
    p = spec["parameters"]
    context_id = p["active_context"]
    descriptor = p["contexts"][context_id]
    cfg, shared = descriptor["inputs"], p["shared"]
    n = descriptor["n_rows"]
    rng = np.random.default_rng(seed)
    age_cfg = cfg["age_law"]
    weights = np.asarray(age_cfg["weights"], dtype=float)
    weights = weights / weights.sum()
    age = rng.choice(np.asarray(age_cfg["values"], dtype=np.int64), n, p=weights)
    female = rng.binomial(1, cfg["female_probability"], n).astype(np.int64)
    if cfg["primitive_family"] == "uniform":
        bound = shared["standard_uniform_bound"]
        z = rng.uniform(-bound, bound, size=(3, n))
    elif cfg["primitive_family"] == "normal":
        z = rng.normal(shared["standard_normal_mean"], shared["standard_normal_sd"], size=(3, n))
    else:
        raise ValueError("Unknown latent family")
    rbg = shared["latent_bmi_glucose_correlation"]
    rbh = shared["latent_bmi_hba1c_correlation"]
    rgh = cfg["glucose_hba1c_latent_correlation"]
    cg = np.sqrt(1.0-rbg*rbg)
    ch = (rgh-rbg*rbh)/cg
    eh2 = 1.0-rbh*rbh-ch*ch
    if not eh2 > 0:
        raise ValueError("Degenerate latent dependence")
    latent = {"bmi":z[0], "glucose":rbg*z[0]+cg*z[1],
              "hba1c":rbh*z[0]+ch*z[1]+np.sqrt(eh2)*z[2]}
    output = {"row_id":[context_id+"_"+str(i+1) for i in range(n)], "age":age, "female":female}
    with np.errstate(over="raise", under="raise", invalid="raise", divide="raise"):
        for name in ("bmi", "glucose", "hba1c"):
            margin = cfg["margins"][name]
            value = margin["location"] + margin["scale"]*latent[name]
            if margin["kind"] == "shifted_exp":
                value = margin["shift"] + np.exp(value)
            elif margin["kind"] != "affine":
                raise ValueError("Unknown margin")
            if not np.all(np.isfinite(value)) or not np.all(value > 0):
                raise ValueError("Invalid final biometric value; no repair")
            output[name] = value
    if context_id == "J":
        if not np.all(output["glucose"] < shared["j_fpg_upper_exclusive"]):
            raise ValueError("J eligibility failure; no replacement")
        native = (output["hba1c"]-shared["ngsp_percent_intercept"])/shared["ngsp_percent_per_ifcc"]
        if not np.all(np.isfinite(native)) or not np.all(native >= 0):
            raise ValueError("J native IFCC support failure")
    if not (np.all(age >= min(age_cfg["values"])) and np.all(age <= max(age_cfg["values"]))):
        raise ValueError("Age support failure")
    design = np.column_stack((np.ones(n), age, female, output["bmi"], output["glucose"]))
    if np.linalg.matrix_rank(design) != design.shape[1]:
        raise ValueError("Degenerate sampled design; no replacement")
    return pd.DataFrame(output, columns=["row_id","age","female","bmi","glucose","hba1c"])
