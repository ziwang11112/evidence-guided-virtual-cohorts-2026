"""Same scientific estimators for real and virtual data; all outputs are aggregates."""
import numpy as np
import pandas as pd

MOMENTS = ("mean_s", "mean_d", "sd_s", "sd_d", "Q1")


def summary(values):
    a = np.asarray(values, dtype=float)
    if a.ndim != 2 or a.shape[1] != 2 or len(a) < 3 or not np.isfinite(a).all():
        raise ValueError("Need at least three complete finite paired pressures")
    n = len(a)
    means = a.mean(axis=0)
    centered = a - means
    scale = np.sqrt((centered ** 2).mean(axis=0))
    if np.any(scale <= 0):
        raise ValueError("Degenerate pressure distribution")
    z = centered / scale
    r = (z[:, 0] * z[:, 1]).mean()
    event = ((a[:, 0] >= 140) & (a[:, 1] >= 90)).astype(float)
    estimates = [*means, *a.std(axis=0, ddof=1), r, event.mean()]
    influence = np.column_stack((centered, (centered ** 2 - scale ** 2)/(2 * scale),
                                 z[:, 0] * z[:, 1] - r * (z ** 2).sum(axis=1)/2, event))
    keys = [*MOMENTS, "Q2"]
    return {"n": n, "estimates": dict(zip(keys, map(float, estimates))),
            "iid_mcse": dict(zip(keys, map(float, influence.std(axis=0, ddof=1)/np.sqrt(n)))),
            "nonpositive": int((a <= 0).any(axis=1).sum()),
            "unordered": int((a[:, 0] <= a[:, 1]).sum())}


def source_checks(result, source):
    targets = [source["means"]["SBP"], source["means"]["DBP"], source["sd"]["SBP"],
               source["sd"]["DBP"], source["pearson"]]
    checks = {}
    for key, target in zip(MOMENTS, targets):
        delta = result["estimates"][key] - target
        allowance = source["rounding_half_unit"] + 4 * result["iid_mcse"][key]
        checks[key] = {"signed_delta": float(delta), "allowance": float(allowance),
                       "pass": bool(abs(delta) <= allowance)}
    compatible = all(c["pass"] for c in checks.values()) and result["nonpositive"] == result["unordered"] == 0
    return {"moments": checks, "compatible": compatible}


def load_target(path):
    cols = ["V1_SN", "V8_A_Cats", "V2_Z", "V6_PS", "V6_PD"]
    frame = pd.read_excel(path, sheet_name="Mastersheet", usecols=cols)
    if frame["V1_SN"].isna().any() or not frame["V1_SN"].is_unique:
        raise ValueError("Duplicate or missing target identifiers")
    eligible = frame["V8_A_Cats"].isin([2, 3, 4]) & frame["V2_Z"].notna()
    out = frame.loc[eligible, ["V6_PS", "V6_PD", "V2_Z"]].copy()
    out.columns = ["SBP", "DBP", "zone"]
    a = out[["SBP", "DBP"]].apply(pd.to_numeric, errors="coerce")
    ok = np.isfinite(a).all(axis=1) & (a > 0).all(axis=1)
    out[["SBP", "DBP"]] = a
    return out.loc[ok].reset_index(drop=True)


def zone_intervals(target, repeats=2000, seed=18127):
    a = target[["SBP", "DBP"]].to_numpy()
    groups = [np.flatnonzero(target["zone"].to_numpy() == z) for z in sorted(target["zone"].unique())]
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(repeats):
        indices = np.concatenate([g[rng.integers(0, len(g), size=len(g))] for g in groups])
        sample = a[indices]
        r = np.corrcoef(sample.T)[0, 1]
        both = ((sample[:, 0] >= 140) & (sample[:, 1] >= 90)).mean()
        draws.append([r, both])
    bounds = np.quantile(draws, [0.025, 0.975], axis=0).T
    return {k: list(map(float, v)) for k, v in zip(["Q1", "Q2"], bounds)}
