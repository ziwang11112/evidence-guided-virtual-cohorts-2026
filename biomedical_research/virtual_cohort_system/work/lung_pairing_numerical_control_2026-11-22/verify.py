"""Check numerical-control assignments against the original paper and the frozen experimental rules.

Run after control.py (or restore the two private index files), then supply the
publisher XML whose SHA-256 is listed in the original lung experiment. The
only output is a JSON report written to stdout. No optimization code is used.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from statistics import correlation, fmean, pstdev
import xml.etree.ElementTree as ET

import numpy as np

HERE = Path(__file__).resolve().parent
FROZEN = HERE.parent / "article_lung_pairing_2026-11-22"
ARTICLE = HERE.parent / "spirometry_pairing_2026-11-21"
SEXES = ("F", "M")
PRINTED_STEPS = {
    "fev1_mean": .1, "fev1_sd": .1, "fvc_mean": .1, "fvc_sd": .1,
    "slope": .01, "intercept_l": .01, "pearson": .01, "r2_pct": .1,
}


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same(actual, expected, label):
    require(math.isclose(actual, expected, abs_tol=1e-8, rel_tol=0), f"{label}: {actual} != {expected}")


def published_columns(xml):
    frozen = read(FROZEN / "FREEZE.json")["design"]
    require(frozen["source_xml_sha256"] == checksum(xml), "The input XML differs from the registered source")
    document = ET.parse(xml)
    doi = document.findtext('.//article-id[@pub-id-type="doi"]')
    require(doi == "10.1186/1465-9921-13-57", "Unexpected source DOI")

    # The archived trial's independent auditor reads the XML and reconstructs
    # lognormal grids using stdlib NormalDist, separately from the production
    # evaluator and solver, which use scipy.special.ndtri.
    file = FROZEN / "verify.py"
    module_spec = importlib.util.spec_from_file_location("article_recomputation", file)
    independent = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(independent)
    independent.SRC = xml
    original = independent.source()
    margins = {c["sex"]:c for c in read(ARTICLE/"MARGINAL_SOURCE.json")["cells"]}
    joint = {c["sex"]:c for c in read(ARTICLE/"JOINT_SOURCE.json")["cells"]}
    for article_file in ("MARGINAL_SOURCE.json","JOINT_SOURCE.json"):
        registered_name = (ARTICLE / article_file).relative_to(HERE.parent.parent).as_posix()
        require(checksum(ARTICLE / article_file) == frozen["files"][registered_name], "Unregistered summaries")
    n = frozen["n_per_sex"]
    require(n == 8000 and set(original) == set(SEXES), "Unexpected population strata or allocated rows")
    grids = {}
    for sex in SEXES:
        values = original[sex]
        for key in ("source_n", "fev1_mean", "fev1_sd", "fvc_mean", "fvc_sd"):
            same(values[key], margins[sex][key], f"{sex} original Table 1 {key}")
        for key in ("pearson", "slope", "intercept_l"):
            same(values[key], joint[sex][key], f"{sex} original Table 2 {key}")
        same(values["r2_pct"],100*joint[sex]["R2"],f"{sex} original Table 2 R2")
        x,y = independent.grid_pair(values["fvc_mean"], values["fvc_sd"], values["slope"],
                                    values["intercept_l"], values["r2_pct"], n)
        require(len(x)==n and len(y)==n and 0 < x.min() and 0 < y.min(), "Nonpositive lung volumes on input")
        require(np.all(np.diff(x)>0) and np.all(np.diff(y)>0), "Volume grids are not sorted")
        grids[sex] = x,y
    return original, grids, n, doi


def recalculate(home, arm, claim, digest, gold, grids, n):
    rows = home / "private" / f"pairings_{arm}.npy"
    require(checksum(rows)==digest, f"{arm} file checksum differs")
    idx = np.load(rows, allow_pickle=False)
    require(idx.shape==(2,n) and idx.dtype.kind in "iu", f"{arm} invalid permutation dimensions or type")
    by_sex = {}
    diagnostics = {}
    means_x, means_y = [], []
    for g,sex in enumerate(SEXES):
        x, ygrid = grids[sex]
        order = idx[g]
        require(np.array_equal(np.sort(order), np.arange(n)), f"{arm}/{sex} not a complete within-sex permutation")
        y = ygrid[order]
        xs, ys = x.tolist(), y.tolist()
        mx,my = fmean(xs),fmean(ys)
        sx,sy = pstdev(xs),pstdev(ys)
        same(my, fmean(ygrid.tolist()), f"{arm}/{sex} assigned FVC mean")
        same(sy, pstdev(ygrid.tolist()), f"{arm}/{sex} assigned FVC SD")
        corr = correlation(xs,ys)
        # Estimate the unadjusted OLS intercept and slope directly using a
        # design matrix with a constant, independent of the covariance formula.
        intercept,slope = np.linalg.lstsq(np.column_stack([np.ones(n),y]), x, rcond=None)[0]
        e = x-intercept-slope*y
        r2_pct = 100*(1-float(e@e)/float((x-mx)@(x-mx)))
        moments = {"fev1_mean":mx,"fev1_sd":sx,"fvc_mean":my,"fvc_sd":sy,
                   "pearson":corr,"r2_pct":r2_pct,"slope":float(slope),"intercept_l":float(intercept)}
        claimed = claim["sex"][sex]
        for name,value in moments.items():
            same(value,claimed["moments"][name],f"{arm}/{sex}/{name}")
            mid,half = gold[sex][name], PRINTED_STEPS[name]/2
            require(mid-half <= value < mid+half, f"{arm}/{sex}/{name} outside source rounding interval")
        invalid = int(np.count_nonzero(x>y))
        ratios = x/y
        below = int(np.count_nonzero(ratios<.70))
        require(claimed["invalid_order"]==invalid==0 and claimed["below"]==below and claimed["n"]==n,
                f"{arm}/{sex} physiological order, count or denominator mismatch")
        by_sex[sex] = below
        diagnostics[sex] = int(np.count_nonzero((ratios>=.695)&(ratios<.705)))
        means_x.append(mx);means_y.append(my)
    pct = 100*sum(by_sex.values())/(2*n)
    fixed = 100*sum(means_x)/sum(means_y)
    same(pct,claim["percent"],arm+" screening percentage")
    same(fixed,claim["ratio_of_means_pct"],arm+" ratio of sex-standardized means")
    require(claim["failures"]==[],arm+" source check was reported as failed")
    return {"screened_by_sex":by_sex,"percent":pct,"ratio_of_means_pct":fixed,
            "n_per_sex":n,"all_reported_moments_and_physical_order_verified":True,
            "near_cutoff_percent":100*sum(diagnostics.values())/(2*n),"assignment_sha256":digest}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-xml",type=Path,default=ARTICLE/"private/source_epmc.xml")
    parser.add_argument("--results",type=Path,default=HERE/"RESULTS.json")
    args=parser.parse_args()
    results=read(args.results)
    for key,path in (("design_sha256",HERE/"DESIGN.md"),
                     ("registered_source_freeze_sha256",FROZEN/"FREEZE.json"),
                     ("source_validation_sha256",FROZEN/"lung.py")):
        require(results[key]==checksum(path),f"Unmatched version of {path.name}")
    gold,grids,n,doi=published_columns(args.source_xml)
    arms=results["arms"]
    verified={}
    for arm in ("low","high"):
        if arm not in arms or arms[arm] is None:
            continue
        verified[arm]=recalculate(args.results.parent,arm,arms[arm],results["sha256"][arm],gold,grids,n)
        same(verified[arm]["near_cutoff_percent"],results["cutoff_band_pct"][arm],arm+" cutoff-window occupancy")
    report={"article":doi,"article_xml_sha256":checksum(args.source_xml),"results_sha256":checksum(args.results),
            "two_complete_directions":len(verified)==2,"checked":verified}
    if len(verified)==2:
        delta=verified["high"]["percent"]-verified["low"]["percent"]
        require(delta>=0,"Endpoints reversed")
        same(delta,results["gap_pp"],"screening span")
        same(verified["high"]["ratio_of_means_pct"],verified["low"]["ratio_of_means_pct"],"fixed use between directions")
        material=delta>5
        require(material==results["material_pair"],"Materiality decision mismatch")
        report.update(feasible_span_pp=delta,material_pair=material)
    else:
        require(not results.get("material_pair"),"An incomplete pair was classified as material")
        report["reason"]="One or both directional runs have no admissible archived assignment."
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
