"""Population-level iron case estimands. No individual data appear in outputs.

Target intervals use the full positive-phlebotomy-weight design. Each JKn
replicate omits one PSU and inflates the remaining weights in its stratum.
Rank statistics (including tie handling) are recomputed in each replicate.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit, logit
from scipy.stats import t


NAMES = ("odds_ratio", "joint_prevalence", "spearman")
CELL_NAMES = ("both_low", "only_hb_low", "only_ferritin_low", "neither_low")


def _midrank(x, w):
    # Mid-distribution function of the weighted empirical distribution, ties pooled.
    _, inverse = np.unique(x, return_inverse=True)
    mass = np.bincount(inverse, weights=w)
    return ((np.cumsum(mass) - mass / 2) / mass.sum())[inverse]


def _point(hb, ferritin, weight):
    keep = weight > 0
    hb, ferritin, w = hb[keep], ferritin[keep], weight[keep]
    if not (np.isfinite(hb).all() and np.isfinite(ferritin).all()):
        raise ValueError("Missing biomarker in a positive-weight analysis row")
    # Equality to a threshold belongs to the upper group.
    index = (hb >= 12).astype(int) * 2 + (ferritin >= 15).astype(int)
    raw = np.bincount(index, minlength=4)
    mass = np.bincount(index, weights=w, minlength=4)
    out = dict.fromkeys(NAMES)
    if len(w):
        if np.all(mass > 0):
            out["odds_ratio"] = float((mass[0] / mass[1]) * (mass[3] / mass[2]))
        out["joint_prevalence"] = float(mass[0] / mass.sum())
        if np.unique(hb).size > 1 and np.unique(ferritin).size > 1:
            x, y = _midrank(hb, w), _midrank(ferritin, w)
            x -= np.average(x, weights=w)
            y -= np.average(y, weights=w)
            denom = np.sqrt(np.dot(w, x*x) * np.dot(w, y*y))
            out["spearman"] = float(np.clip(np.dot(w, x*y) / denom, -1, 1))
    return out, raw, mass


def _describe(point, raw, mass):
    cells = {
        key: {"n": int(n), "weighted_count": float(s), "weighted_fraction":
              float(s / mass.sum()) if mass.sum() else None}
        for key, n, s in zip(CELL_NAMES, raw, mass)
    }
    flags = []
    if min(raw) < 10:
        flags.append("one_or_more_raw_cells_below_10")
    if min(raw) == 0:
        flags.append("zero_cell_odds_ratio_not_estimable_no_continuity_correction")
    est = {key: {"estimate": val} for key, val in point.items()}
    return {"cells": cells, "estimands": est, "flags": flags}


def _numeric(s):
    # pandas' XPT reader maps all tagged SAS numeric missings to NaN.
    # Accommodate the printed form in fixtures or alternate SAS readers.
    s = s.replace(r"^\.(?:[A-Za-z_])?$", np.nan, regex=True)
    return pd.to_numeric(s, errors="raise")


def _fields(frame, names, label):
    if not set(names) <= set(frame.columns):
        raise ValueError(f"{label}: required field absent")
    out = frame.loc[:, names].copy()
    for name in names:
        out[name] = _numeric(out[name])
    if (out.SEQN.isna().any() or not np.isfinite(out.SEQN).all()
            or (out.SEQN <= 0).any() or (out.SEQN % 1 != 0).any() or not out.SEQN.is_unique):
        raise ValueError(f"{label}: invalid or duplicated SEQN")
    return out


def _linked(demo, cbc, ferritin):
    demo = _fields(demo, ["SEQN", "RIAGENDR", "RIDAGEYR", "RIDEXPRG",
                         "SDMVSTRA", "SDMVPSU"], "DEMO")
    cbc = _fields(cbc, ["SEQN", "WTPH2YR", "LBXHGB"], "CBC")
    ferritin = _fields(ferritin, ["SEQN", "WTPH2YR", "LBDFERSI"], "FERTIN")
    for lab in (cbc, ferritin):
        if not lab.SEQN.isin(demo.SEQN).all():
            raise ValueError("Laboratory SEQN absent from demographics")
        observed = lab.WTPH2YR.dropna()
        if (observed < 0).any() or not np.isfinite(observed).all():
            raise ValueError("Invalid laboratory phlebotomy weight")
    linked = demo.merge(cbc, how="left", on="SEQN", validate="one_to_one")
    linked = linked.merge(ferritin.rename(columns={"WTPH2YR": "ferritin_weight"}),
                          how="left", on="SEQN", validate="one_to_one")
    both = linked.WTPH2YR.notna() & linked.ferritin_weight.notna()
    if not np.allclose(linked.loc[both, "WTPH2YR"], linked.loc[both, "ferritin_weight"],
                       rtol=1e-10, atol=1e-8):
        raise ValueError("CBC and ferritin phlebotomy weights disagree")
    linked["weight"] = linked.WTPH2YR.combine_first(linked.ferritin_weight)
    for field in ("LBXHGB", "LBDFERSI"):
        measured = linked[field].dropna()
        if not np.isfinite(measured).all() or (measured < 0).any():
            raise ValueError(f"Invalid measurement in {field}")
    return linked


def _transform(name, value):
    if value is None:
        return None
    if name == "odds_ratio":
        return np.log(value) if value > 0 else None
    if name == "joint_prevalence":
        return logit(value) if 0 < value < 1 else None
    return np.arctanh(value) if abs(value) < 1 else None


def analyze_target(demo, cbc, ferritin):
    linked = _linked(demo, cbc, ferritin)
    f = linked.loc[linked.weight > 0].copy()
    if f.empty:
        raise ValueError("No positive phlebotomy weight")
    if not np.isfinite(f[["SDMVSTRA", "SDMVPSU"]]).all().all():
        raise ValueError("Missing full-design stratum/PSU")
    if (f[["SDMVSTRA", "SDMVPSU"]] % 1 != 0).any().any():
        raise ValueError("Invalid full-design stratum/PSU")
    adult = (f.RIAGENDR == 2) & f.RIDAGEYR.between(20, 44)
    eligible = adult & (f.RIDEXPRG == 2)
    q = eligible & f.LBXHGB.notna() & f.LBDFERSI.notna()
    hb, ferr = f.LBXHGB.to_numpy(), f.LBDFERSI.to_numpy()
    w = np.where(q, f.weight, 0.0)
    point, raw, mass = _point(hb, ferr, w)
    out = _describe(point, raw, mass)
    out["flow"] = {
        "demographic_rows": len(demo), "cbc_rows": len(cbc), "ferritin_rows": len(ferritin),
        "positive_phlebotomy_frame": len(f),
        "women_age20_44_in_frame": int(adult.sum()),
        "nonpregnant_women_age20_44_in_frame": int(eligible.sum()),
        "eligible_with_hb": int((eligible & f.LBXHGB.notna()).sum()),
        "eligible_with_ferritin": int((eligible & f.LBDFERSI.notna()).sum()),
        "eligible_with_both": int(q.sum()),
        "weighted_complete_fraction_among_eligible":
            float(w.sum() / f.loc[eligible, "weight"].sum()) if eligible.any() else None,
    }
    # All PSUs in the full frame contribute to degrees of freedom, even if a
    # particular PSU contributes no domain members to the binary thresholds.
    strata, psu = f.SDMVSTRA.to_numpy(), f.SDMVPSU.to_numpy()
    groups = [(s, np.unique(psu[strata == s])) for s in np.unique(strata)]
    df = sum(len(psus) - 1 for _, psus in groups)
    lonely = any(len(psus) < 2 for _, psus in groups)
    out["design"] = {
        "strata": len(groups), "psus": sum(len(psus) for _, psus in groups),
        "df": df, "lonely_stratum": lonely,
        "method": "Stratified delete-one-PSU JKn; full-estimate centering; t(df) 95%",
    }
    for entry in out["estimands"].values():
        entry.update({"ci95": None, "se_transformed": None, "invalid_replicates": None})
    if lonely or df <= 0:
        out["flags"].append("insufficient_design_for_intervals")
        return out

    var = dict.fromkeys(NAMES, 0.0)
    invalid = dict.fromkeys(NAMES, 0)
    center = {name: _transform(name, point[name]) for name in NAMES}
    for s, psus in groups:
        m = len(psus)
        in_stratum = strata == s
        for dropped in psus:
            rw = w.copy()
            rw[in_stratum] *= m / (m - 1)
            rw[in_stratum & (psu == dropped)] = 0
            rep_point = _point(hb, ferr, rw)[0]
            for name in NAMES:
                theta = _transform(name, rep_point[name])
                if theta is None or center[name] is None:
                    invalid[name] += 1
                else:
                    var[name] += (m-1) / m * (theta - center[name])**2
    backtransforms = {"odds_ratio": np.exp, "joint_prevalence": expit, "spearman": np.tanh}
    critical = t.ppf(.975, df)
    for name in NAMES:
        entry = out["estimands"][name]
        entry["invalid_replicates"] = invalid[name]
        if invalid[name] or center[name] is None:
            out["flags"].append(f"{name}_interval_not_estimable")
            continue
        se = np.sqrt(var[name])
        endpoints = backtransforms[name](center[name] + np.array([-1, 1]) * critical * se)
        if not np.isfinite(endpoints).all():
            out["flags"].append(f"{name}_interval_outside_numeric_range")
            continue
        entry.update({"se_transformed": float(se), "ci95": endpoints.tolist()})
    return out


def analyze_synthetic(df, hb="hb_g_dl", ferritin="ferritin_ug_l"):
    x = _numeric(df[hb]).to_numpy(dtype=float)
    y = _numeric(df[ferritin]).to_numpy(dtype=float)
    if len(df) == 0 or not np.isfinite(x).all() or not np.isfinite(y).all() or min(x) < 0 or min(y) < 0:
        raise ValueError("Synthetic table contains empty, missing, negative or nonfinite measurements")
    point, raw, mass = _point(x, y, np.ones(len(x)))
    out = _describe(point, raw, mass)
    out["rows"] = len(df)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    target = modes.add_parser("target")
    for opt in ("demo", "cbc", "ferritin"):
        target.add_argument("--" + opt, type=Path, required=True)
    syn = modes.add_parser("synthetic")
    syn.add_argument("--table", type=Path, required=True)
    syn.add_argument("--hb", default="hb_g_dl")
    syn.add_argument("--ferritin-col", default="ferritin_ug_l")
    for mode in (target, syn):
        mode.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "synthetic":
        answer = analyze_synthetic(pd.read_csv(args.table), args.hb, args.ferritin_col)
    else:
        answer = analyze_target(*(pd.read_sas(path, format="xport")
                                  for path in (args.demo, args.cbc, args.ferritin)))
    args.out.write_text(json.dumps(answer, indent=2, allow_nan=False)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
