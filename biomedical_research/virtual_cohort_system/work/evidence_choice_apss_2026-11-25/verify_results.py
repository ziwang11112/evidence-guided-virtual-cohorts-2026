"""Independent aggregate replay. Requires completed blind review and primary scoring first."""
from collections import Counter
import csv
from fractions import Fraction
from hashlib import sha256
import json
from math import floor, fsum, isfinite
from pathlib import Path
from statistics import median
import warnings

import numpy as np
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent
EPS = 1e-10

def source_cells():
    # Invert rounded unweighted Cohen kappa to an observed number of concordant rows.
    n = 91
    chance = Fraction(8*12 + 83*79, n*n)
    lo, hi = Fraction(1551, 2000), Fraction(1553, 2000)
    agreements = [c for c in range(n+1) if lo <= (Fraction(c, n)-chance)/(1-chance) < hi]
    if len(agreements) != 1:
        raise ValueError("Source concurrence count not identifiable")
    discord = n-agreements[0]
    both = (8 + 12 - discord) / 2
    if not both.is_integer() or not 0 <= both <= 8:
        raise ValueError("Published table infeasible")
    both = int(both)
    return [both, 8-both, 12-both, agreements[0]-both]


def count_endpoints(pairs):
    cells = Counter()
    diffs, ties, qual = [], 0, []
    for a, b in pairs:
        if not (isfinite(a) and isfinite(b) and min(a,b)>0):
            raise ValueError("Invalid BMI pair")
        cells[(a>=30, b>=30)] += 1
        d = a-b
        tied = abs(d+2) <= EPS
        ties += int(tied)
        qual.append(int(d < -2 and not tied))
        diffs.append(d)
    n = len(diffs)
    if n<2: raise ValueError("Insufficient paired data")
    joint = [cells[k] for k in ((True,True),(True,False),(False,True),(False,False))]
    gold = source_cells()
    q = 50*fsum(abs(numer/n-den/91) for numer,den in zip(joint,gold))
    metric = {"n":n, "tail_count":sum(qual), "tail_pct":100*sum(qual)/n,
              "threshold_ties":ties, "signed_mean":fsum(diffs)/n,
              "joint_cells":joint, "source_joint_tv_pp":q,
              "joint_agreement_pct":100*(joint[0]+joint[3])/n}
    return metric, diffs, qual


def number(x):
    if x is None or (isinstance(x,str) and not x.strip()):
        return None
    value = float(x)
    if not isfinite(value): raise ValueError("Nonfinite acquisition value")
    return value


def measured_pairs(path, *, completed_years):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        book = load_workbook(path, read_only=True, data_only=True)
    try:
        it = iter(book["Online_versus_F2F"].values)
        for _ in range(3): next(it)
        cols = list(next(it))
        index = [cols.index(c) for c in ("Age","OL_SR_height","OL_SR_weight","OL_BMI",
                  "F2F_measured_height","F2F_measured_weight","F2F_calculated_bmi(measured)")]
        rows = [tuple(number(row[i]) for i in index) for row in it if any(v is not None and v != "" for v in row)]
    finally:
        book.close()
    adults = [q for q in rows if q[0] is not None and q[0] >=18 and
              (q[0]<76 if completed_years else q[0]<=75)]
    scales = []
    for start in (1, 4):
        anchors = []
        for q in adults:
            h,w,bmi=q[start:start+3]
            if (h is not None and h<=0) or (w is not None and w<=0):
                raise ValueError("Inadmissible anthropometry")
            if h and w and bmi is not None and bmi>0:
                anchors.append(10000*w/(h*h*bmi))
        meters = bool(anchors) and not (0.8<=median(anchors)<=1.2)
        if meters and sum(8000<=x<=12000 for x in anchors)/len(anchors) < .90:
            raise ValueError("Workbook units ambiguous")
        scales.append(1 if meters else 100)
    pairs=[]
    for _,a,w,_,b,v,_ in adults:
        if all(x is not None for x in (a,w,b,v)):
            pairs.append((w/((a/scales[0])**2), v/((b/scales[1])**2)))
    return pairs,len(adults)


def linear_quantiles(x):
    v = sorted(x)
    ans = []
    for p in (.025,.975):
        t = (len(v)-1)*p
        i = floor(t)
        ans.append(v[i] + (t-i)*(v[min(i+1,len(v)-1)]-v[i]))
    return ans


def paired_ci(d,q):
    n = len(d)
    idx = np.random.default_rng(20261125).integers(0,n,size=(2000,n))
    tail = [100*sum(q[int(j)] for j in picks)/n for picks in idx]
    means = [fsum(d[int(j)] for j in picks)/n for picks in idx]
    return {"tail_pct_interval":linear_quantiles(tail),
            "signed_mean_interval":linear_quantiles(means)}


def compare(a,b):
    if isinstance(a,(list,tuple)):
        if len(a)!=len(b): raise AssertionError("Different vector lengths")
        return max((compare(x,y) for x,y in zip(a,b)),default=0)
    diff = abs(a-b)
    if not diff <= 2e-9: raise AssertionError(f"Aggregate mismatch ({a!r}, {b!r})")
    return diff


def verify_branch(reference,slots,*,completed_years):
    measured_path=ROOT/("MEASURED_EVALUATION.json" if completed_years else "STRICT_AGE_EVALUATION.json")
    primary=json.loads(measured_path.read_text())
    if primary["stage"]!="measured": raise ValueError("Primary evaluation has not been released")
    mode="completed_years" if completed_years else "strict_numeric"
    if primary["reference_eligibility"]["age_interpretation"]!=mode:
        raise ValueError("Wrong primary or sensitivity branch")
    pairs,n_adults=measured_pairs(reference,completed_years=completed_years)
    ref,d,flags=count_endpoints(pairs)
    primary_ref=primary["reference"]
    max_diff=max(compare(v,primary_ref[k]) for k,v in ref.items())
    compare(n_adults,primary["reference_eligibility"]["n_adult"])
    ci=paired_ci(d,flags)
    for k,v in ci.items():
        max_diff=max(max_diff,compare(v,primary_ref["paired_participant_bootstrap"][k]))
    scored={e["slot"]:e for e in primary["slots"]}
    if len(scored)!=8 or set(scored)!={s["slot"] for s in slots}: raise ValueError("Slot mismatch")
    checked=0; statuses=[]
    for slot in slots:
        q=scored[slot["slot"]]
        per_seed={v["seed"]:v for v in q["draws"]}
        measures=[]
        for draw in slot["draws"]:
            exp=per_seed[draw["seed"]]
            if draw["path"] is None:
                if exp["available"]: raise AssertionError("Draw status mismatch")
                continue
            if sha256(Path(draw["path"]).read_bytes()).hexdigest()!=draw["sha256"]:
                raise AssertionError("Synthetic hash changed")
            with Path(draw["path"]).open(encoding="utf-8-sig",newline="") as file:
                rd=csv.DictReader(file)
                if set(rd.fieldnames or [])!={"reported_bmi","measured_bmi","row_id"}:
                    raise ValueError("Synthetic schema changed")
                rows=list(rd)
            ids=[s["row_id"] for s in rows]
            if "" in ids or len(set(ids))!=len(ids): raise ValueError("Synthetic IDs invalid")
            try:
                out,_,_=count_endpoints((float(s["reported_bmi"]),float(s["measured_bmi"])) for s in rows)
            except (ValueError,TypeError):
                if exp["available"]: raise AssertionError("An invalid draw was accepted")
                continue
            if not exp["available"]:raise AssertionError("A valid draw was rejected")
            for k,v in out.items():
                max_diff=max(max_diff,compare(v,exp[k]))
            e_tail=out["tail_pct"]-ref["tail_pct"]
            e_mean=out["signed_mean"]-ref["signed_mean"]
            max_diff=max(max_diff,compare(e_tail,exp["tail_error_pp"]),compare(e_mean,exp["signed_mean_error"]))
            measures.append((abs(e_tail),abs(e_mean),out["source_joint_tv_pp"]))
            checked+=1
        ok=len(measures)==3
        if ok!=q["all_three_available"]:raise AssertionError("Slot-level evaluability differs")
        rpass=ok and all(x[0]<=3+EPS for x in measures)
        mpass=ok and all(x[1]<=.30+EPS for x in measures)
        if (rpass,mpass,rpass and mpass)!=(q["all_tail_in_tolerance"],q["all_means_in_tolerance"],q["both"]):
            raise AssertionError("Scientific-use grades disagree")
        entry={"slot":slot["slot"],"arm":slot["arm"],"scored_draws":len(measures),
               "both":rpass and mpass,"all_tail_in_tolerance":rpass,"all_means_in_tolerance":mpass}
        if ok:
            tvs=[m[2] for m in measures]
            max_diff=max(max_diff,compare(max(tvs),q["source_joint_max_tv_pp"]),
                         compare(fsum(tvs)/3,q["source_joint_mean_tv_pp"]))
            if (max(tvs)<=3+EPS)!=q["near_source_table"]:raise AssertionError("Source grade differs")
            entry.update(median_abs_tail_error_pp=median(x[0] for x in measures),
                         median_abs_mean_error=median(x[1] for x in measures),
                         source_fit_all_seeds=max(tvs)<=3+EPS)
        statuses.append(entry)
    return {"primary_result_sha256":sha256(measured_path.read_bytes()).hexdigest(),
            "age_interpretation":mode,"n_adults":n_adults,
            "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
            "assigned_slots":len(slots),"available_draws_checked":checked,
            "reference":ref, "paired_reference_intervals":ci, "source_cells_by_kappa_inversion":source_cells(),
            "per_slot_checks":statuses, "max_absolute_numerical_disagreement":max_diff}


def verify():
    from blind_review import require_review
    from run_trial import reference_after_seal, verified_draws
    require_review()
    slots=verified_draws()
    if not all((ROOT/n).is_file() for n in ("MEASURED_EVALUATION.json","STRICT_AGE_EVALUATION.json")):
        raise ValueError("Both eligibility reconciliation branches must be scored first")
    reference=reference_after_seal()
    if sha256(Path(reference).read_bytes()).hexdigest()!="91bd4f5b2e48fec969397c8be68577ea5419ec3190c929f0a956c6525d7c0f45":
        raise ValueError("Unexpected publisher reference")
    main=verify_branch(reference,slots,completed_years=True)
    main["strict_numeric_sensitivity"]=verify_branch(reference,slots,completed_years=False)
    return main


if __name__=="__main__":
    value=verify()
    with (ROOT/"INDEPENDENT_CHECK.json").open("x",encoding="utf-8") as fh:
        json.dump(value,fh,indent=2,allow_nan=False)
        fh.write("\n")

