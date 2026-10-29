"""Source-only M6 analysis. Never imports or executes candidate generators.

Only root-committed, hash-bound aggregate reports and synthetic source/probe
tables beneath this experiment are accepted. There are no real-cohort reads.
"""
import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd

LABELS = ("zero", "minus", "plus")
SOURCE_SEEDS = (78101, 78102, 78103)
PROBE_SEEDS = (78201, 78202, 78203)
Y = "tg_mg_dl"
E = Path(__file__).resolve().parent.parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_path(path):
    p = Path(path).resolve()
    if not p.is_relative_to(E):
        raise ValueError(f"Read outside the assigned experiment denied: {p}")
    return p


def bound(path, sha):
    p = safe_path(path)
    if digest(p) != sha:
        raise ValueError(f"Hash mismatch: {p}")
    return p


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_table(path):
    return pd.read_csv(path, float_precision="round_trip", dtype={"record_id":str,"tg_assay":str})


def json_write(path, value):
    def clean(item):
        if isinstance(item,dict): return {str(k):clean(v) for k,v in item.items()}
        if isinstance(item,(list,tuple)): return [clean(v) for v in item]
        if isinstance(item,np.generic): item=item.item()
        if isinstance(item,float) and not math.isfinite(item): return None
        return item
    Path(path).write_text(json.dumps(clean(value), indent=2, allow_nan=False) + "\n", encoding="utf-8")


def finite(value):
    return value is not None and isinstance(value, (int, float)) and math.isfinite(value)


def basis(age, bmi):
    age, bmi = np.asarray(age), np.asarray(bmi)
    ha = (9103 / 18693) * ((age >= 35) & (age <= 44)) - ((age >= 55) & (age <= 64)).astype(float)
    hb = (10388 / 14851) * ((bmi >= 22) & (bmi < 24)) - ((bmi >= 26) & (bmi < 28)).astype(float)
    return ha, hb


def input_preservation(output, observed):
    if len(output) != len(observed):
        return {"passed": False, "reason": "row-count mismatch", "changed_columns": list(observed.columns)}
    changed = []
    for col in observed.columns:
        if col not in output or not output[col].equals(observed[col]):
            changed.append(col)
    values_ok = Y in output and np.isfinite(output[Y]).all() and (output[Y] > 0).all()
    ids_ok = "record_id" in output and not output.record_id.duplicated().any()
    return {"passed": not changed and bool(values_ok) and bool(ids_ok), "changed_columns": changed,
            "row_count": len(output), "finite_positive_outcome": bool(values_ok), "unique_record_ids": bool(ids_ok)}


def paired_invariants(zero, other):
    ha, hb = basis(zero.age.to_numpy(), zero.bmi.to_numpy())
    y0, yt = zero[Y].to_numpy(), other[Y].to_numpy()
    active = (zero.sex.to_numpy() == 1) & (ha != 0) & (hb != 0)
    masks = {"female_rows": zero.sex.to_numpy() == 2, "outside_active_covariates": ~active,
             "baseline_outside_70_190": (y0 <= 70) | (y0 >= 190)}
    result = {}
    for name, mask in masks.items():
        result[name] = {"n_rows": int(mask.sum()), "changed_rows": int(np.count_nonzero(y0[mask] != yt[mask])),
                        "exact_equal": bool(np.array_equal(y0[mask], yt[mask]))}
    for threshold in (200, 500):
        result[f"below_{threshold}_indicators"] = {"changed_rows": int(np.count_nonzero((y0 < threshold) != (yt < threshold))),
                                                   "exact_equal": bool(np.array_equal(y0 < threshold, yt < threshold))}
    changed = y0 != yt
    result["changed_row_count"] = int(changed.sum())
    result["max_absolute_change_mg_dl"] = float(np.max(np.abs(yt-y0)))
    result["changes_stay_inside_70_190"] = bool(np.all((yt[changed] > 70) & (yt[changed] < 190)))
    observed_columns = [c for c in zero.columns if c != Y]
    result["paired_observed_cells_equal"] = zero[observed_columns].equals(other[observed_columns])
    result["passed"] = all(v["exact_equal"] for v in result.values() if isinstance(v, dict)) and result["changes_stay_inside_70_190"] and result["paired_observed_cells_equal"]
    return result


def validate_manifest(m, phase):
    authorization = "authorize_source_analysis" if phase == "source" else "authorize_probe_analysis"
    if m.get(authorization) is not True:
        raise ValueError(f"Root release missing {authorization}=true")
    if bound(m["analysis_script_path"], m["analysis_script_sha256"]) != Path(__file__).resolve():
        raise ValueError("The executing analysis script is not the root-committed script")
    bound(m["protocol_path"], m["protocol_sha256"])
    commitment_path=bound(m["protocol_commitment_path"],m["protocol_commitment_sha256"])
    commitment=read_json(commitment_path)
    for relative,sha in commitment["files"].items():
        bound(E / relative,sha)
    gate_path = bound(m["gate_path"], m["gate_sha256"])
    bundle_path = safe_path(m["bundle_path"])
    bound(m["observed_path"], m["observed_sha256"])
    if safe_path(m["observed_path"]) != bundle_path / "observed.csv":
        raise ValueError("Probe observed file is not the committed bundle observed.csv")
    expected = {(label, seed, context) for label in LABELS for seed in SOURCE_SEEDS for context in ("oh", "bansal")}
    actual = [(r["label"], r["seed"], r["context"]) for r in m["sources"]]
    if set(actual) != expected or len(actual) != len(expected):
        raise ValueError("Source schedule incomplete or duplicated")
    for r in m["sources"]:
        if r["replay_id"] != f"{r['label']}_{r['seed']}":
            raise ValueError("Source label/seed/replay linkage mismatch")
        child=bundle_path/"source_replays"/r["replay_id"]/"contexts"/r["context"]/"bundle"
        if bound(r["path"], r["sha256"]) != child/"executions/replay/output/generated.csv":
            raise ValueError("Source output outside its committed replay slot")
        if bound(r["observed_path"], r["observed_sha256"]) != child/"observed.csv":
            raise ValueError("Source input outside its committed replay slot")
        if "replay_report_path" in r:
            bound(r["replay_report_path"], r["replay_report_sha256"])
            report=read_json(r["replay_report_path"])
            if report["status"]!="success" or report["limits"]["seed"]!=r["seed"]:
                raise ValueError("Root-bound replay was not successful at the committed seed")
    if phase == "complete":
        expected = {(label, seed) for label in LABELS for seed in PROBE_SEEDS}
        actual = [(r["label"], r["seed"]) for r in m["probes"]]
        if set(actual) != expected or len(actual) != len(expected):
            raise ValueError("Probe schedule incomplete or duplicated")
        for r in m["probes"]:
            if r["run_id"] != f"{r['label']}_{r['seed']}":
                raise ValueError("Probe label/seed/run linkage mismatch")
            if bound(r["path"], r["sha256"]) != bundle_path/"executions"/r["run_id"]/"output/generated.csv":
                raise ValueError("Probe output outside its committed run slot")
    elif m.get("probes"):
        raise ValueError("Source-only release must not expose probe outputs")
    if {r["label"] for r in m["portfolios"]} != set(LABELS) or len(m["portfolios"]) != 3:
        raise ValueError("Exactly three portfolios are required")
    for r in m["portfolios"]:
        bound(r["path"], r["sha256"])
    if {r["label"] for r in m["candidates"]} != set(LABELS) or len(m["candidates"]) != 3:
        raise ValueError("Exactly three frozen candidates are required")
    for r in m["candidates"]:
        candidate = safe_path(r["path"])
        bound(candidate / "freeze.json", r["freeze_sha256"])
        bound(r["model_spec_path"], r["model_spec_sha256"])
        bound(candidate / "generator.py", r["generator_sha256"])
        if "analytic_certificate_sha256" in r:
            bound(candidate / "analytic_certificate.json", r["analytic_certificate_sha256"])
        else:
            raise ValueError("Root must bind each analytic_certificate_sha256")
    gate = read_json(gate_path)
    if len(gate["checks"]) != 46:
        raise ValueError("Incomplete frozen threshold artifact")
    return gate


def source_gate(manifest, gate):
    portfolios = {r["label"]: read_json(r["path"]) for r in manifest["portfolios"]}
    thresholds = {r["check_id"]: r for r in gate["checks"]}
    maps = {}
    for label, portfolio in portfolios.items():
        cmap = {c["definition"]["check_id"]: c for c in portfolio["checks"]}
        if len(cmap) != 46 or set(cmap) != set(thresholds):
            raise ValueError(f"Incomplete check vector for {label}")
        for cid, c in cmap.items():
            definition, frozen = c["definition"], thresholds[cid]
            if definition["operator"] != frozen["operator"] or definition["reported_value"] != frozen["reported_value"]:
                raise ValueError(f"Changed operator or literature value: {label}/{cid}")
            if definition["context_input_sha256"] != frozen["historical_context_input_sha256"]:
                raise ValueError(f"Changed source context: {label}/{cid}")
            if sorted(r["seed"] for r in c["runs"]) != list(SOURCE_SEEDS):
                raise ValueError(f"Incomplete scheduled check: {label}/{cid}")
        maps[label] = cmap
    rows = []
    for cid, frozen in thresholds.items():
        zero_runs = {r["seed"]: r for r in maps["zero"][cid]["runs"]}
        for label in LABELS:
            for run in maps[label][cid]["runs"]:
                ref = zero_runs[run["seed"]]
                defined = finite(run.get("value")) and finite(ref.get("value")) and not run.get("computation_error") and not ref.get("computation_error")
                defined = defined and run.get("status") in ("approximate", "computed", "pass", "ok") and ref.get("status") in ("approximate", "computed", "pass", "ok")
                diff = run["value"]-ref["value"] if defined else None
                limit = frozen["paired_absolute_limit"]
                passed = defined and abs(diff) <= limit
                if label != "zero" and (frozen["kind"] == "input-only" or frozen["context_id"] == "bansal" or "female" in cid or cid.endswith("below_200") or cid.endswith("below_500")):
                    exact_invariant = defined and diff == 0
                else:
                    exact_invariant = None
                rows.append({"label": label, "seed": run["seed"], "context_id": frozen["context_id"], "check_id": cid,
                             "kind": frozen["kind"], "status": run.get("status"), "value": run.get("value"),
                             "reported_value": frozen["reported_value"],
                             "signed_discrepancy": run["value"]-frozen["reported_value"] if finite(run.get("value")) else None,
                             "absolute_discrepancy": abs(run["value"]-frozen["reported_value"]) if finite(run.get("value")) else None,
                             "paired_change_vs_zero": diff, "historical_seed_sd": frozen["historical_generator_seed_draw_sd"],
                             "paired_absolute_limit": limit, "gate_pass": bool(passed), "exact_invariant_pass": exact_invariant,
                             "n_used": run.get("n_used"), "computation_error": run.get("computation_error")})
    frame = pd.DataFrame(rows)
    summaries = []
    for (label, cid), group in frame.groupby(["label", "check_id"], sort=False):
        values = group.value.to_numpy(dtype=float)
        changes = group.paired_change_vs_zero.to_numpy(dtype=float)
        valid = bool(np.isfinite(values).all() and np.isfinite(changes).all())
        summaries.append({"label": label, "check_id": cid, "kind": group.iloc[0]["kind"], "n_draws": len(group),
                          "mean": float(values.mean()) if valid else None,
                          "minimum": float(values.min()) if valid else None, "maximum": float(values.max()) if valid else None,
                          "generator_seed_draw_sd": float(values.std(ddof=1)) if valid else None,
                          "mean_signed_discrepancy": float(group.signed_discrepancy.mean()) if valid else None,
                          "mean_absolute_discrepancy": float(group.absolute_discrepancy.mean()) if valid else None,
                          "mean_paired_change_vs_zero": float(changes.mean()) if valid else None,
                          "paired_change_seed_sd": float(changes.std(ddof=1)) if valid else None,
                          "all_seed_gate_pass": bool(group.gate_pass.all())})
    alternatives = frame[frame.label != "zero"]
    exact = alternatives.exact_invariant_pass.dropna()
    ci_rows = frame[frame.check_id == "e_oh_bmi_age_sex_slope"]
    ci = [{"label": r.label, "seed": int(r.seed), "value": r.value, "reported_ci_low": 5.853, "reported_ci_high": 7.774,
           "inside_reported_ci": bool(5.853 <= r.value <= 7.774) if finite(r.value) else None} for r in ci_rows.itertuples()]
    summary = {"n_all_records": len(frame), "n_paired_comparisons": len(alternatives),
               "n_gate_failures": int((~alternatives.gate_pass).sum()), "all_46_each_seed_paired_gate_pass": bool(alternatives.gate_pass.all()),
               "exact_diagnostic_invariants_pass": bool(exact.all()),
               "reported_Table3_CI_location_only": ci,
               "interpretation": gate["interpretation"]}
    return frame, pd.DataFrame(summaries), summary


AGE_STRATA = [("<=29", -np.inf, 30), ("30-39", 30, 40), ("40-49", 40, 50), ("50-59", 50, 60), (">=60", 60, np.inf)]
BMI_STRATA = [("<20", -np.inf, 20), ("20-23", 20, 23), ("23-25", 23, 25), ("25-30", 25, 30), (">30", 30, np.inf)]
TABLE2 = {("age",1): [143,147.5,140.6,143.5,128.1], ("age",2): [78.1,80.7,89.4,127.8,135.3],
          ("bmi",1): [91.8,109.4,141.4,165.3,220.5], ("bmi",2): [73.8,86.5,100.9,126.7,127.3]}


def table2_rows(frame, label, seed):
    rows = []
    for variable, strata in (("age", AGE_STRATA), ("bmi", BMI_STRATA)):
        for sex in (1,2):
            for i, (name, lo, hi) in enumerate(strata):
                mask = (frame.sex == sex) & (frame[variable] >= lo) & (frame[variable] < hi)
                y = frame.loc[mask, Y].to_numpy()
                for kind in ("arithmetic", "geometric"):
                    value = float(y.mean()) if kind == "arithmetic" and len(y) else float(np.exp(np.log(y).mean())) if len(y) else None
                    reported = TABLE2[(variable, sex)][i]
                    rows.append({"label": label, "seed": seed, "variable": variable, "sex": sex, "reported_stratum": name,
                                 "calculation_interval": f"[{lo},{hi})", "interpretation": kind,
                                 "reported_kind": "reported_other; arithmetic/geometric ambiguity unresolved",
                                 "n": len(y), "value": value, "reported_value": reported,
                                 "signed_discrepancy": value-reported if value is not None else None,
                                 "absolute_discrepancy": abs(value-reported) if value is not None else None})
    return rows


def add_pair_changes(frame, keys):
    ref = frame[frame.label == "zero"][[*keys, "value"]].rename(columns={"value": "zero_value"})
    out = frame.merge(ref, on=keys, how="left", validate="many_to_one")
    out["paired_change_vs_zero"] = out.value-out.zero_value
    return out


def context_departure(frame, delta):
    men = frame[frame.sex == 1]
    ha, hb = basis(men.age.to_numpy(), men.bmi.to_numpy())
    n = len(men)
    ac = [int(((men.age >= 35)&(men.age <= 44)).sum()), int(((men.age >= 55)&(men.age <= 64)).sum())]
    bc = [int(((men.bmi >= 22)&(men.bmi < 24)).sum()), int(((men.bmi >= 26)&(men.bmi < 28)).sum())]
    ea = (Fraction(9103,18693)*ac[0]-ac[1])/n
    eb = (Fraction(10388,14851)*bc[0]-bc[1])/n
    joint = pd.crosstab(men.age, men.bmi, normalize=True)
    j = joint.to_numpy()
    product = j.sum(axis=1)[:,None]*j.sum(axis=0)[None,:]
    summaries = {"n_male_rows": n, "age_region_counts": ac, "bmi_region_counts": bc,
                 "expected_age_region_counts": [18693,9103], "expected_bmi_region_counts": [14851,10388],
                 "exact_hA_marginal_mean": str(ea), "exact_hB_marginal_mean": str(eb),
                 "marginal_centering_exact": ea == 0 and eb == 0,
                 "declared_counts_match": ac == [18693,9103] and bc == [14851,10388] and n == 61740,
                 "empirical_mean_hA_hB": float(np.mean(ha*hb)),
                 "product_of_marginal_basis_means": float(ea*eb),
                 "actual_minus_product_basis_expectation": float(np.mean(ha*hb))-float(ea*eb),
                 "full_discrete_age_bmi_total_variation_from_product": float(np.abs(j-product).sum()/2),
                 "full_discrete_age_bmi_max_absolute_cell_probability_departure": float(np.abs(j-product).max()),
                 "age_bmi_pearson_correlation": float(men[["age","bmi"]].corr().iloc[0,1]),
                 "analytic_male_mean_plus_minus_gap_fixed_context": float(-140*delta*np.mean(ha*hb)),
                 "interpretation": "Descriptive fixed synthetic context departure from its empirical-marginal product; full-grid TV reflects finite sparsity. No independence test, source-population inference, or clinical CI."}
    rows = []
    acat = np.where(ha > 0, "positive", np.where(ha < 0, "negative", "inactive"))
    bcat = np.where(hb > 0, "positive", np.where(hb < 0, "negative", "inactive"))
    for av in ("positive", "negative", "inactive"):
        for bv in ("positive", "negative", "inactive"):
            actual = float(np.mean((acat == av)&(bcat == bv)))
            prod = float(np.mean(acat == av)*np.mean(bcat == bv))
            rows.append({"age_basis_region": av, "bmi_basis_region": bv, "joint_probability": actual,
                         "product_probability": prod, "departure": actual-prod})
    conditionals = []
    for variable, strata in (("age",AGE_STRATA),("bmi",BMI_STRATA)):
        for name,lo,hi in strata:
            mask = (men[variable].to_numpy() >= lo)&(men[variable].to_numpy() < hi)
            conditionals.append({"variable": variable, "stratum": name, "n": int(mask.sum()),
                                 "conditional_mean_hA_hB": float(np.mean((ha*hb)[mask])),
                                 "analytic_stratum_mean_plus_minus_gap": float(-140*delta*np.mean((ha*hb)[mask]))})
    return summaries, pd.DataFrame(rows), pd.DataFrame(conditionals)


def regressions(frame):
    y = frame[Y].to_numpy()
    a = (frame.age.to_numpy()-50)/10
    b = (frame.bmi.to_numpy()-25)/5
    f = (frame.sex.to_numpy()==2).astype(float)
    x = np.column_stack((np.ones(len(frame)), a, b, f))
    def fit(design, outcome):
        beta, _, rank, _ = np.linalg.lstsq(design, outcome, rcond=None)
        if rank != design.shape[1]:
            raise ValueError("Rank-deficient prespecified regression")
        return beta
    main = fit(x,np.log(y))
    curve = fit(np.column_stack((x,b*b)),np.log(y))
    rawcurve = fit(np.column_stack((x,b*b)),y)
    sexinteraction = fit(np.column_stack((x,b*f)),np.log(y))
    ageinteraction = fit(np.column_stack((x,a*b)),np.log(y))
    return {"logTG_age_per10": main[1], "logTG_bmi_per5": main[2], "logTG_female_minus_male": main[3],
            "logTG_bmi_curvature_2betaQ": 2*curve[4], "rawTG_bmi_curvature_2betaQ": 2*rawcurve[4],
            "logTG_bmi_by_female": sexinteraction[4], "logTG_age_by_bmi": ageinteraction[4]}


def probe_blocks(frame):
    out = []
    for age_lo, age_hi in ((35,44),(55,64)):
        for bmi_lo, bmi_hi in ((22,24),(26,28)):
            mask = (frame.sex==1)&(frame.age>=age_lo)&(frame.age<=age_hi)&(frame.bmi>=bmi_lo)&(frame.bmi<bmi_hi)
            y=frame.loc[mask,Y].to_numpy()
            if len(y)!=200:
                raise ValueError("Unexpected synthetic block size")
            out.append({"block": f"male_age{age_lo}-{age_hi}_BMI{bmi_lo}-{bmi_hi-1}", "n": len(y), "value": float(y.mean()),
                        "median": float(np.median(y)), "geometric_mean": float(np.exp(np.log(y).mean()))})
    return out


def summary_with_pairs(frame, groupcols):
    rows=[]
    for key,g in frame.groupby(["label",*groupcols],sort=False):
        if not isinstance(key,tuple): key=(key,)
        rows.append({**dict(zip(["label",*groupcols],key)), "n_draws": len(g), "mean": float(g.value.mean()),
                     "minimum": float(g.value.min()), "maximum": float(g.value.max()),
                     "generator_seed_draw_sd": float(g.value.std(ddof=1)),
                     "mean_paired_change_vs_zero": float(g.paired_change_vs_zero.mean()),
                     "paired_change_seed_sd": float(g.paired_change_vs_zero.std(ddof=1)),
                     "minimum_paired_change_vs_zero": float(g.paired_change_vs_zero.min()),
                     "maximum_paired_change_vs_zero": float(g.paired_change_vs_zero.max())})
    return pd.DataFrame(rows)


def independent_certificate(parameters, reported):
    p=parameters
    q=p["density_interaction"]
    fixed={"age_positive":[35,44],"age_negative":[55,64],"bmi_positive":[22,24],"bmi_negative":[26,28],
           "tg_positive":[70,120],"tg_negative":[140,190],"age_positive_weight":9103/18693,
           "bmi_positive_weight":10388/14851,"safety_fraction":.8,"inverse_cdf_steps":40}
    checks={"frozen_support_bases_and_safety_fraction":all(q.get(k)==v for k,v in fixed.items()),
            "positive_softplus_width":p["positive_mean"]["width"]>0,
            "positive_residual_cv":p["residual_cv"][0]>0,
            "monotonic_mean_signs":p["bmi_slope"][0]>0 and p["age_slope"][0]<0}
    def mean(age,bmi):
        raw=p["reference"]["tg_mean"][0]+p["bmi_slope"][0]*(bmi-p["reference"]["bmi_mean"][0])+p["age_slope"][0]*(age-p["reference"]["age_mean"][0])
        floor,width=p["positive_mean"]["floor"],p["positive_mean"]["width"]
        return float(floor+width*np.logaddexp(0,(raw-floor)/width))
    bounds=[mean(64,22),mean(35,28)]
    sigma2=math.log1p(p["residual_cv"][0]**2)
    sigma=math.sqrt(sigma2)
    corners=[]
    for mu in bounds:
        for y in (70,120,140,190):
            logdensity=-math.log(y*sigma*math.sqrt(2*math.pi))-(math.log(y)-math.log(mu)+sigma2/2)**2/(2*sigma2)
            corners.append({"mu_mg_dl":mu,"y_mg_dl":y,"density":math.exp(logdensity)})
    density_min=min(c["density"] for c in corners)
    delta=q["delta"]
    certified_delta=.8*50*density_min
    close=lambda a,b:math.isclose(a,b,rel_tol=2e-13,abs_tol=2e-15)
    checks["declared_delta_matches_independent_bound"]=close(delta,certified_delta)
    checks["nonnegative_density_lower_bound"]=delta>=0 and delta/50<=density_min
    checks["certificate_scalars_match"]=all(close(reported[k],v) for k,v in (("sigma",sigma),("density_min",density_min),("delta",delta)))
    checks["certificate_mean_bounds_match"]=len(reported["mu_bounds_mg_dl"])==2 and all(close(a,b) for a,b in zip(reported["mu_bounds_mg_dl"],bounds))
    r_corners=reported["density_corner_evaluations"]
    checks["certificate_all_eight_corners_match"]=len(r_corners)==8 and all(all(close(r[k],c[k]) for k in ("mu_mg_dl","y_mg_dl","density")) for r,c in zip(r_corners,corners))
    positive_width=q["tg_positive"][1]-q["tg_positive"][0]
    negative_width=q["tg_negative"][1]-q["tg_negative"][0]
    integral=positive_width/50-negative_width/50
    first_moment=(q["tg_positive"][1]**2-q["tg_positive"][0]**2)/100-(q["tg_negative"][1]**2-q["tg_negative"][0]**2)/100
    checks["per_covariate_normalization"]=integral==0
    checks["kernel_first_moment_matches"]=first_moment==-70 and reported["hT_first_moment_mg_dl"]==-70
    cells=[]
    for age,bmi in ((40,23),(40,27),(60,23),(60,27)):
        ha,hb=basis(np.array([age]),np.array([bmi]))
        gap=float(2*delta*ha[0]*hb[0]*first_moment)
        baseline=mean(age,bmi)
        cells.append({"sex":1,"age":age,"bmi":bmi,"zero_conditional_mean_mg_dl":baseline,
                      "minus_conditional_mean_mg_dl":baseline-gap/2,"plus_conditional_mean_mg_dl":baseline+gap/2,
                      "plus_minus_conditional_mean_gap_mg_dl":gap,"absolute_gap_mg_dl":abs(gap),"individual_gap_ge_5":abs(gap)>=5})
    maximum=max(c["absolute_gap_mg_dl"] for c in cells)
    checks["maximum_over_four_cells_materiality"]=maximum>=5
    checks["certificate_materiality_value_matches"]=close(maximum,reported["materiality_value_mg_dl"]) and reported["materiality_threshold_mg_dl"]==5
    return {"passed":all(checks.values()),"checks":checks,"delta":delta,"independent_delta_from_bound":certified_delta,
            "sigma":sigma,"mean_bounds_mg_dl":bounds,"corners":corners,"density_min":density_min,
            "uniform_density_ratio_lower_bound":1-delta/(50*density_min),"kernel_integral":integral,
            "kernel_first_moment_mg_dl":first_moment,"materiality_cells":cells,"maximum_absolute_gap_mg_dl":maximum,
            "materiality_rule":"MAX absolute gap >=5 mg/dL over all four predeclared cells; not EACH cell",
            "known_pre_run_design_quantity":True,
            "proof":"Softplus is increasing, male BMI slope positive and age slope negative, so opposite enclosing rectangle corners bound the conditional mean. Log lognormal density is concave in (log y, log mean): a linear term minus a squared affine term. Its minimum on each rectangular band occurs at a vertex. The eight evaluated vertices certify f0>=d_min. Since |hA*hB|<=1 and |hT|<=1/50, delta=.8*50*d_min gives f_t>=.2*f0. The kernel integrates to zero at every covariate point. Exact marginal centering plus the declared product covariate law cancels the density perturbation from both bivariate outcome laws.",
            "numeric_tolerance":"Independent certificate number comparisons use rel_tol=2e-13, abs_tol=2e-15 for separately evaluated elementary functions only; source paired gates retain zero added tolerance."}


def verify_certificates(manifest):
    results={}
    normalized=[]
    for record in manifest["candidates"]:
        label=record["label"]
        spec=read_json(record["model_spec_path"])
        report=read_json(Path(record["path"])/"analytic_certificate.json")
        p=spec["parameters"]
        expected_sign={"zero":0,"minus":-1,"plus":1}[label]
        result=independent_certificate(p,report)
        result["checks"]["label_sign_matches"]=p["density_interaction"]["sign"]==expected_sign
        result["passed"]=all(result["checks"].values())
        normalized.append({**p,"density_interaction":{**p["density_interaction"],"sign":0}})
        results[label]=result
    common=all(p==normalized[0] for p in normalized)
    final=results["zero"].copy()
    final["all_candidate_checks"]={k:v["checks"] for k,v in results.items()}
    final["candidate_parameters_identical_except_sign"]=common
    final["passed"]=common and all(v["passed"] for v in results.values())
    return final


def source_tables(manifest, delta):
    entries = {(r["label"],r["seed"],r["context"]):r for r in manifest["sources"]}
    invariants, preservation, semantic = [], [], []
    departure = regions = conditionals = None
    for context in ("oh","bansal"):
        for seed in SOURCE_SEEDS:
            zr=entries[("zero",seed,context)]
            zero=read_table(zr["path"])
            observed=read_table(zr["observed_path"])
            if context=="oh" and departure is None:
                departure,regions,conditionals=context_departure(zero,delta)
            for label in LABELS:
                record=entries[(label,seed,context)]
                frame=zero if label=="zero" else read_table(record["path"])
                if record["observed_sha256"] != zr["observed_sha256"]:
                    raise ValueError("Source context input differs across labels")
                check=input_preservation(frame,observed)
                check["legacy_proxy_measurement_only"]=bool(frame.tg_assay.eq("legacy_proxy").all())
                check["passed"]=check["passed"] and check["legacy_proxy_measurement_only"]
                preservation.append({"label":label,"seed":seed,"context":context,**check})
                if label!="zero":
                    if len(frame)!=len(zero):
                        invariants.append({"label":label,"seed":seed,"context":context,"passed":False,"reason":"row count mismatch"})
                    else:
                        invariants.append({"label":label,"seed":seed,"context":context,**paired_invariants(zero,frame)})
                if context=="oh":
                    semantic.extend(table2_rows(frame,label,seed))
    semantics=add_pair_changes(pd.DataFrame(semantic),["seed","variable","sex","reported_stratum","interpretation"])
    return preservation,invariants,semantics,departure,regions,conditionals


def plot_results(out, cells, block_rows, endpoint_rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes=plt.subplots(1,3,figsize=(15.5,4.8),layout="constrained")
    names=[f"Age {r['age']}, BMI {r['bmi']}" for r in cells]
    gaps=np.array([r["plus_minus_conditional_mean_gap_mg_dl"] for r in cells])
    axes[0].barh(names,gaps,color=["#2878B5" if v>=0 else "#D75445" for v in gaps])
    axes[0].axvline(0,color="#777",lw=.8)
    for v in (-5,5): axes[0].axvline(v,color="#999",ls=":",lw=1)
    axes[0].set(title="Prespecified analytic male cells",xlabel="Plus minus minus mean TG (mg/dL)")
    blocks=block_rows[block_rows.label=="plus"].copy()
    minus=block_rows[block_rows.label=="minus"][["seed","block","value"]].rename(columns={"value":"minus_value"})
    blocks=blocks.merge(minus,on=["seed","block"],validate="one_to_one")
    blocks["difference"]=blocks.value-blocks.minus_value
    for i,(name,g) in enumerate(blocks.groupby("block",sort=False)):
        axes[1].scatter(g.difference,np.full(len(g),i)+np.linspace(-.10,.10,len(g)),s=34,color="#2878B5")
    axes[1].set_yticks(range(4),["35-44 / 22-23","35-44 / 26-27","55-64 / 22-23","55-64 / 26-27"])
    axes[1].axvline(0,color="#777",lw=.8)
    axes[1].set(title="Paired synthetic male blocks",xlabel="Plus minus minus mean TG (mg/dL)",ylabel="Age / BMI")
    interaction=endpoint_rows[endpoint_rows.endpoint=="logTG_age_by_bmi"]
    for i,label in enumerate(LABELS):
        g=interaction[interaction.label==label]
        axes[2].scatter(np.full(len(g),i)+np.linspace(-.08,.08,len(g)),g.value,s=35,label=label)
    axes[2].set_xticks(range(3),LABELS)
    axes[2].set(title="Common synthetic-grid projection",ylabel="log TG age x BMI coefficient")
    axes[2].axhline(0,color="#777",lw=.8)
    fig.suptitle("Source-conditioned constructions: analytic separation and synthetic illustrations",fontsize=14)
    fig.text(.5,-.035,"Points are three fixed generator seeds; no human reference, clinical confidence intervals, or evidence-uncertainty bands.",ha="center",fontsize=10)
    fig.savefig(out/"constructive_separation.png",dpi=220,bbox_inches="tight")
    fig.savefig(out/"constructive_separation.pdf",bbox_inches="tight")
    plt.close(fig)


def plot_source_screen(out,raw):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    tg=raw[(raw.kind=="TG-dependent")&(raw.label!="zero")].copy()
    tg["ratio"]=np.abs(tg.paired_change_vs_zero)/tg.paired_absolute_limit
    summary=tg.groupby(["check_id","label"],sort=False).ratio.max().unstack("label")
    fig,ax=plt.subplots(figsize=(11,11),layout="constrained")
    y=np.arange(len(summary))
    for label,offset,color in (("minus",-.12,"#2878B5"),("plus",.12,"#D75445")):
        ax.scatter(summary[label],y+offset,s=26,label=label,color=color)
    ax.axvline(1,color="#333",ls="--",lw=1,label="Frozen descriptive limit")
    ax.set_yticks(y,[name.removeprefix("e_").replace("_"," ") for name in summary.index],fontsize=8)
    ax.invert_yaxis()
    ax.set(xlabel="Maximum over three seeds: absolute paired change / frozen limit",
           title="All 34 TG-dependent source diagnostics: paired drift versus zero")
    ax.legend(loc="lower right")
    fig.text(.5,-.025,"Twelve input-only checks require exact equality. Limits are historical generator-seed scales, not clinical uncertainty.",ha="center",fontsize=9)
    fig.savefig(out/"source_paired_screen.png",dpi=190,bbox_inches="tight")
    fig.savefig(out/"source_paired_screen.pdf",bbox_inches="tight")
    plt.close(fig)


def run_probe(manifest,out,cells):
    observed=read_table(manifest["observed_path"])
    expected=pd.MultiIndex.from_product([range(20,80),(1,2),range(18,41)],names=["age","sex","bmi"])
    counts=observed.groupby(["age","sex","bmi"]).size().reindex(expected)
    if len(observed)!=27600 or not counts.eq(10).all() or not observed.tg_assay.eq("legacy_proxy").all():
        raise ValueError("Synthetic probe grid deviates from prespecification")
    entries={(r["label"],r["seed"]):r for r in manifest["probes"]}
    invariants,preservation,endpoints,blocks,grid=[],[],[],[],[]
    for seed in PROBE_SEEDS:
        zero=read_table(entries[("zero",seed)]["path"])
        for label in LABELS:
            frame=zero if label=="zero" else read_table(entries[(label,seed)]["path"])
            check=input_preservation(frame,observed)
            preservation.append({"label":label,"seed":seed,**check})
            if not check["passed"]:
                raise ValueError("Synthetic probe contract violation")
            if label!="zero":
                invariants.append({"label":label,"seed":seed,**paired_invariants(zero,frame)})
            endpoints.extend({"label":label,"seed":seed,"endpoint":name,"value":float(value)} for name,value in regressions(frame).items())
            blocks.extend({"label":label,"seed":seed,**row} for row in probe_blocks(frame))
            for (sex,age,bmi),group in frame.groupby(["sex","age","bmi"],sort=True):
                y=group[Y].to_numpy()
                grid.append({"label":label,"seed":seed,"sex":int(sex),"age":int(age),"bmi":float(bmi),"n":len(y),
                             "value":float(y.mean()),"median":float(np.median(y)),"geometric_mean":float(np.exp(np.log(y).mean())),
                             "proportion_ge_150":float(np.mean(y>=150)),"proportion_ge_200":float(np.mean(y>=200))})
    endpoint_frame=add_pair_changes(pd.DataFrame(endpoints),["seed","endpoint"])
    block_frame=add_pair_changes(pd.DataFrame(blocks),["seed","block"])
    grid_frame=add_pair_changes(pd.DataFrame(grid),["seed","sex","age","bmi"])
    endpoint_summary=summary_with_pairs(endpoint_frame,["endpoint"])
    block_summary=summary_with_pairs(block_frame,["block"])
    plusminus=block_frame[block_frame.label=="plus"][["seed","block","value"]].merge(
        block_frame[block_frame.label=="minus"][["seed","block","value"]],on=["seed","block"],suffixes=("_plus","_minus"),validate="one_to_one")
    plusminus["paired_plus_minus_gap"]=plusminus.value_plus-plusminus.value_minus
    frames={"probe_endpoints":endpoint_frame,"probe_endpoint_summary":endpoint_summary,
            "probe_block_means":block_frame,"probe_block_summary":block_summary,
            "probe_block_plus_minus_gaps":plusminus,"probe_grid":grid_frame}
    for name,frame in frames.items(): frame.to_csv(out/f"{name}.csv",index=False)
    plot_results(out,cells,block_frame,endpoint_frame)
    return {"preservation":preservation,"paired_invariants":invariants,
            "all_implementation_checks_pass":all(r["passed"] for r in preservation+invariants),
            "endpoint_definitions":{
                "scaling":"A=(age-50)/10; B=(BMI-25)/5; F=1(sex=2); all models have an intercept and unweighted OLS",
                "main":"log(TG)~1+A+B+F: report age, BMI and female coefficients",
                "log_curvature":"log(TG)~1+A+B+F+B^2: report 2*coefficient(B^2)",
                "raw_curvature":"TG~1+A+B+F+B^2: report 2*coefficient(B^2)",
                "sex_interaction":"log(TG)~1+A+B+F+B*F: report coefficient(B*F)",
                "age_bmi_interaction":"log(TG)~1+A+B+F+A*B: report coefficient(A*B)"},
            "endpoints":endpoint_frame.to_dict("records"),"endpoint_summary":endpoint_summary.to_dict("records"),
            "blocks":block_frame.to_dict("records"),"block_summary":block_summary.to_dict("records"),
            "block_plus_minus_gaps":plusminus.to_dict("records"),
            "grid_csv":"probe_grid.csv", "grid_records":len(grid_frame),
            "interpretation":"The common equally weighted synthetic grid is a model illustration; ten replicates per cell and three generator seeds are not human truth or clinical uncertainty. Grid projections depend on this prespecified covariate weighting."}


UNASSESSED = [
    {"source":"Oh Table 4", "estimand":"BMI coefficient with additional metabolic adjustment", "reported_value":4.385,"reported_ci":[3.406,5.363],"status":"unassessed","reason":"Required metabolic covariates and analysis specification are unavailable; cannot substitute age/sex/BMI OLS."},
    {"source":"Oh Table 5", "estimand":"BMI coefficient in mixed/family lifestyle model", "reported_value":6.91,"reported_se":.89,"status":"unassessed","reason":"Required adjustment covariates, family structure, and mixed-model estimand are unavailable."},
    {"source":"Oh co-twin analysis", "estimand":"BMI coefficient from co-twin contrast", "reported_value":9.94,"reported_ci":[3.42,16.46],"status":"unassessed","reason":"Twin pairing and within-pair design cannot be recovered from this synthetic context."}]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--phase",choices=("source","complete"),required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    manifest_path=safe_path(args.manifest)
    manifest=read_json(manifest_path)
    gate=validate_manifest(manifest,args.phase)
    out=safe_path(args.out)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("Analysis output is immutable; use a transparent reviewed rerun location")
    out.mkdir(parents=True,exist_ok=True)
    certificate=verify_certificates(manifest)
    raw,summary,gate_summary=source_gate(manifest,gate)
    preservation,invariants,semantic,departure,regions,conditionals=source_tables(manifest,certificate["delta"])
    raw.to_csv(out/"source_checks_all.csv",index=False)
    plot_source_screen(out,raw)
    summary.to_csv(out/"source_check_summary.csv",index=False)
    semantic.to_csv(out/"oh_table2_both_interpretations.csv",index=False)
    semantic_summary=summary_with_pairs(semantic,["variable","sex","reported_stratum","interpretation"])
    semantic_summary.to_csv(out/"oh_table2_summary.csv",index=False)
    regions.to_csv(out/"source_context_basis_region_departure.csv",index=False)
    conditionals.to_csv(out/"source_context_conditional_departure.csv",index=False)
    semantic_ok=len(semantic)==360 and bool(np.isfinite(semantic.value).all()) and bool((semantic.n>0).all())
    implementation_ok=all(r["passed"] for r in preservation+invariants)
    gate_summary.update({"density_certificate_passed":certificate["passed"],"source_input_preservation_and_paired_invariants_pass":implementation_ok,
                         "semantic_table2_complete_finite":semantic_ok,"source_margin_centering_pass":departure["marginal_centering_exact"] and departure["declared_counts_match"]})
    gate_summary["all_passed"]=all([gate_summary["all_46_each_seed_paired_gate_pass"],gate_summary["exact_diagnostic_invariants_pass"],
                                  certificate["passed"],implementation_ok,semantic_ok,gate_summary["source_margin_centering_pass"]])
    json_write(out/"gate_summary.json",gate_summary)
    result={"schema_version":1,"phase":args.phase,"scope":"source-only conditional-identifiability construction and synthetic probe; no real target outcomes",
            "manifest_sha256":digest(manifest_path),"analysis_script_sha256":digest(__file__),"gate_sha256":manifest["gate_sha256"],
            "protocol_sha256":manifest["protocol_sha256"],"manifest_bindings":manifest,
            "gate":gate_summary,"independent_analytic_certificate":certificate,
            "source_checks":raw.astype(object).where(pd.notnull(raw),None).to_dict("records"),
            "source_check_summary":summary.to_dict("records"),"source_input_preservation":preservation,"source_paired_invariants":invariants,
            "fixed_source_context_departure":departure,"fixed_source_context_region_departure":regions.to_dict("records"),
            "fixed_source_context_conditional_departure":conditionals.to_dict("records"),
            "oh_table2_both_interpretations":semantic.to_dict("records"),"oh_table2_summary":semantic_summary.to_dict("records"),
            "oh_table2_boundary_note":"Calculation uses lower-inclusive upper-exclusive BMI bins [20,23), [23,25), [25,30), [30,infinity); the paper's final display label >30 remains visible. Discrete reconstruction boundary assignment is an approximation.",
            "unassessed_source_estimands":UNASSESSED,
            "source_text_anomaly":"Oh Table2 FBS-stratum entries labelled TG reconstruct fasting-glucose rather than TG means; not interpreted as resolved TG constraints.",
            "limitations":["Source covariate independence, marginal shapes/support, assay mapping, and missing family/covariate structure are assumptions.",
                           "Passing preserves the chosen anchor's discrepancies and does not establish source admissibility or compatibility with all paper evidence.",
                           "Historical and new generator-seed spread describe simulation variation, not paper uncertainty or confidence intervals.",
                           "The known analytic separation threshold is a design criterion; there is no clinical interpretation.",
                           "Three additional Oh estimands remain unassessed; neither model is declared compatible with them."],
            "boundary_disclosure":"Agent inventory automatically displayed unrelated completed-agent summaries while locating the source designer. They were not used in M6; no associated artifacts, participant rows, historical target data, or target reports were opened."}
    if args.phase=="complete":
        if not gate_summary["all_passed"]:
            raise ValueError("Source screen failed; probe interpretation is forbidden")
        result["probe"]=run_probe(manifest,out,certificate["materiality_cells"])
    json_write(out/"aggregate_report.json",result)
    artifact_hashes={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()}
    json_write(out/"artifact_hashes.json",artifact_hashes)
    print(json.dumps({"phase":args.phase,"all_passed":gate_summary["all_passed"],"output":str(out),"aggregate_sha256":digest(out/"aggregate_report.json")}))


if __name__=="__main__":
    main()
