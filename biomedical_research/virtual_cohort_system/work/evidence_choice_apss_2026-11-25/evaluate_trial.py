"""Score published evidence and, after independent sealing, the measured BMI uses."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
FILE_SHA = "91bd4f5b2e48fec969397c8be68577ea5419ec3190c929f0a956c6525d7c0f45"
SHEET = "Online_versus_F2F"
FIELDS = {
    "age": "Age",
    "online_height": "OL_SR_height", "online_mass": "OL_SR_weight", "online_bmi": "OL_BMI",
    "measured_height": "F2F_measured_height", "measured_mass": "F2F_measured_weight",
    "measured_bmi": "F2F_calculated_bmi(measured)",
}
SEEDS = (251131, 251137, 251143)
CELL_ORDER = ["both_positive", "online_positive_only", "measured_positive_only", "both_negative"]
ATOL = 1e-10
TAIL_MARGIN_PP = 3.0
MEAN_MARGIN = 0.30
TV_MARGIN_PP = 3.0


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rounded_source_tables(n=91, r=8, m=12, kappa=0.776):
    """Enumerate every integer table compatible with margins and the printed kappa."""
    chance = (r * m + (n - r) * (n - m)) / n**2
    possible = []
    for overlap in range(max(0, r + m - n), min(r, m) + 1):
        cells = [overlap, r - overlap, m - overlap, n - r - m + overlap]
        agreement = (cells[0] + cells[3]) / n
        coef = (agreement - chance) / (1 - chance)
        if kappa - 0.0005 <= coef < kappa + 0.0005:
            possible.append({"cells": cells, "kappa": coef, "agreement_pct": 100 * agreement})
    return possible


def numeric(series):
    return pd.to_numeric(series.replace(r"^\s*$", np.nan, regex=True), errors="raise").to_numpy(
        dtype=float, na_value=np.nan)


def bmi_pair(r, m):
    r, m = np.asarray(r, dtype=float), np.asarray(m, dtype=float)
    if r.shape != m.shape or r.ndim != 1 or r.size < 2:
        raise ValueError("Expected two paired vectors of length >= 2")
    if not (np.isfinite(r).all() and np.isfinite(m).all() and (r > 0).all() and (m > 0).all()):
        raise ValueError("All scored pairs must contain positive finite BMI on both sides")
    return r, m


def estimates(r, m, bootstrap=False):
    r, m = bmi_pair(r, m)
    diff = r - m
    ties = np.isclose(diff, -2, rtol=0, atol=ATOL)
    tail = (diff < -2) & ~ties
    rc, mc = r >= 30, m >= 30
    cells = np.bincount(2*(~rc).astype(int) + (~mc).astype(int), minlength=4)
    compatible = rounded_source_tables()
    if len(compatible) != 1:
        raise ValueError("Published joint table not uniquely recoverable; review frozen case")
    source_p = np.asarray(compatible[0]["cells"]) / 91
    probs = cells / len(r)
    tv = 50 * np.abs(probs - source_p).sum()
    out = {"n": len(r), "tail_count": int(tail.sum()), "threshold_ties": int(ties.sum()),
           "tail_pct": 100*float(tail.mean()), "signed_mean": float(diff.mean()),
           "source_joint_cell_order": CELL_ORDER, "joint_cells": cells.tolist(),
           "joint_pct": (100*probs).tolist(), "source_joint_tv_pp": float(tv),
           "joint_agreement_pct": float(100 * (probs[0] + probs[3]))}
    if bootstrap:
        rng = np.random.default_rng(20261125)
        est = np.empty((2000, 2))
        for idx in range(len(est)):
            take = rng.integers(0, len(r), size=len(r))
            est[idx] = [tail[take].mean()*100, diff[take].mean()]
        q = np.quantile(est, [0.025, 0.975], axis=0)
        out["paired_participant_bootstrap"] = {
            "replicates": len(est), "seed": 20261125, "tail_pct_interval": q[:, 0].tolist(),
            "signed_mean_interval": q[:, 1].tolist(),
        }
    return out


def measurement_pairs(frame):
    """Apply the source's adult rule and derive BMI from paired cm and kg measurements."""
    if list(frame.columns).count("Age") != 1 or not set(FIELDS.values()) <= set(frame):
        raise ValueError("Study headers differ from the prespecified dictionary")
    data = {role: numeric(frame[col]) for role, col in FIELDS.items()}
    if any(np.isinf(v).any() for v in data.values()):
        raise ValueError("Nonfinite source values outside documented missingness")
    adult = data["age"] >= 18
    if np.any(adult & (data["age"] > 75)):
        raise ValueError("Adult beyond the published eligibility ages; reconcile first")
    pairs, checks = [], {}
    for side in ("online", "measured"):
        h, w, stored = (data[side + "_" + k] for k in ("height", "mass", "bmi"))
        complete = np.isfinite(h) & np.isfinite(w)
        if np.any(adult & (((h <= 0) & np.isfinite(h)) | ((w <= 0) & np.isfinite(w)))):
            raise ValueError("Nonpositive anthropometry in an eligible adult; reconcile coding")
        val = np.full(len(frame), np.nan)
        val[complete] = w[complete] / (h[complete] / 100)**2
        comparable = adult & complete & (stored > 0) & np.isfinite(stored)
        height_unit = "cm"
        if comparable.any():
            ratios = val[comparable] / stored[comparable]
            if not 0.8 <= float(np.median(ratios)) <= 1.2:
                # Workbook headers omit storage units. Recognize metres only when the
                # cached same-side BMI verifies that scale independently of the endpoint.
                if np.mean((ratios >= 8000) & (ratios <= 12000)) < 0.90:
                    raise ValueError("Source raw units/calculated BMI cross-check failed; reconcile before analysis")
                val[complete] = w[complete] / h[complete]**2
                height_unit = "m (confirmed by stored BMI)"
        checks[side] = {"adult_missing_components": int(np.sum(adult & ~complete)),
                        "height_storage": height_unit,
                        "comparable_stored_bmi": int(comparable.sum()),
                        "within_0.1_of_stored": int(np.sum(comparable & (np.abs(val - stored) <= .1)))}
        pairs.append(val)
    use = adult & np.isfinite(pairs[0]) & np.isfinite(pairs[1])
    audit = {"n_sheet_rows": len(frame), "n_missing_age": int(np.isnan(data["age"]).sum()),
             "n_known_age_under18": int(np.sum(np.isfinite(data["age"]) & ~adult)),
             "n_adult": int(adult.sum()), "n_complete": int(use.sum()),
             "exact_repeats_on_all_available_columns": int(frame.duplicated().sum()),
             "source_table_n": 91, "complete_n_differs_from_source": int(use.sum()) != 91,
             "identity": "One volunteer per published row; no ID column. Repeated phenotypes retained.",
             "component_checks": checks}
    return *bmi_pair(pairs[0][use], pairs[1][use]), audit


def assess_slot(draws, reference=None):
    rows = []
    for item in sorted(draws, key=lambda d: d["seed"]):
        result = {"seed": item["seed"], "runner_status": item["status"], "available": False}
        if item["path"] is not None:
            path = Path(item["path"])
            if sha(path) != item["sha256"]:
                raise ValueError("Frozen simulated draw hash mismatch")
            frame = pd.read_csv(path)
            if set(frame) != {"row_id", "reported_bmi", "measured_bmi"}:
                raise ValueError("Unexpected simulated schema")
            if frame["row_id"].isna().any() or frame["row_id"].duplicated().any():
                raise ValueError("Missing or duplicate simulated row ID")
            try:
                score = estimates(numeric(frame["reported_bmi"]), numeric(frame["measured_bmi"]))
            except ValueError:
                result["error"] = "Invalid or incomplete synthetic pairs"
            else:
                result.update(score, available=True)
                if reference is not None:
                    result["tail_error_pp"] = score["tail_pct"] - reference["tail_pct"]
                    result["signed_mean_error"] = score["signed_mean"] - reference["signed_mean"]
        rows.append(result)
    if tuple(r["seed"] for r in rows) != SEEDS:
        raise ValueError("Wrong seed slots")
    ok = all(q["available"] for q in rows)
    summary = {"all_three_available": ok}
    if ok:
        tv = float(np.mean([q["source_joint_tv_pp"] for q in rows]))
        worst = max(q["source_joint_tv_pp"] for q in rows)
        summary.update(source_joint_mean_tv_pp=tv, source_joint_max_tv_pp=worst,
                       near_source_table=worst <= TV_MARGIN_PP + ATOL)
        if reference is not None:
            t = all(abs(q["tail_error_pp"]) <= TAIL_MARGIN_PP + ATOL for q in rows)
            m = all(abs(q["signed_mean_error"]) <= MEAN_MARGIN + ATOL for q in rows)
            summary.update(all_tail_in_tolerance=t, all_means_in_tolerance=m, both=t and m)
    elif reference is not None:
        summary.update(all_tail_in_tolerance=False, all_means_in_tolerance=False, both=False)
    return {"draws": rows, **summary}


def bound_aggregate(reveal=False):
    from run_trial import reference_after_seal, verified_draws
    slots = verified_draws()
    if len(slots) != 8 or len({s["slot"] for s in slots}) != 8:
        raise RuntimeError("Eight frozen constructor slots required")
    ref, meta = None, None
    if reveal:
        from blind_review import require_review
        require_review()
        path = reference_after_seal()
        if sha(path) != FILE_SHA:
            raise ValueError("Published workbook hash mismatch")
        frame = pd.read_excel(path, sheet_name=SHEET, header=3, dtype=object, keep_default_na=False)
        r, m, meta = measurement_pairs(frame)
        ref = estimates(r, m, bootstrap=True)
    outputs = [{key: s[key] for key in ("slot", "block", "arm", "status")} |
               assess_slot(s["draws"], ref) for s in slots]
    return {"stage": "measured" if reveal else "source", "reference": ref, "reference_eligibility": meta,
            "source_table": rounded_source_tables()[0], "slots": outputs}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reveal", action="store_true")
    arg = parser.parse_args()
    result = bound_aggregate(arg.reveal)
    dest = ROOT / ("MEASURED_EVALUATION.json" if arg.reveal else "SOURCE_EVALUATION.json")
    with dest.open("x", encoding="utf-8") as out:
        json.dump(result, out, indent=2, allow_nan=False)
        out.write("\n")

