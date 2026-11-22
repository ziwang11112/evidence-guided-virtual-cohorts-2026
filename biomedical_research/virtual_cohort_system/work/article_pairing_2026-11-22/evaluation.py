"""Source extraction, frozen marginal construction, isolated sampling and matched estimands."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import math
import re
import sys

import numpy as np
import pandas as pd
from scipy.special import ndtri
from scipy.stats import binomtest

import experiment as ex

sys.path.insert(0, str(ex.OLD))
from science import fit_marginal
sys.path.insert(0, str(ex.HERE.parent / "kdd_v40_pairing_review_2026-11-20"))
from scoring import score

KEYS = ("tc_mean", "hdl_mean", "mean_individual_ratio", "nonhdl_mean",
        "tc_high_pct", "hdl_low_pct", "tc_high_cut", "hdl_low_cut")


def reference():
    raw = ex.read(ex.OLD / "SOURCE.json")
    result = {k: (raw[k]["estimate"], raw[k]["table"], raw[k]["row"]) for k in KEYS[:-2]}
    for cutoff, pct in (("tc_high_cut", "tc_high_pct"), ("hdl_low_cut", "hdl_low_pct")):
        series = raw[pct]
        value = float(re.search(r"[0-9]+(?:\.[0-9]+)?", series["row"]).group(0))
        result[cutoff] = (value, series["table"], series["row"])
    return result


def source_check(spec):
    gold = reference()
    evidence = spec.get("evidence")
    evidence = evidence if isinstance(evidence, dict) else {}
    numbers, wrong, citations, row_diff = {}, [], [], []
    for key in KEYS:
        item = evidence.get(key)
        item = item if isinstance(item, dict) else {}
        value = item.get("value")
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
            numbers[key] = float(value)
        if key not in numbers or not math.isclose(numbers[key], gold[key][0], rel_tol=0, abs_tol=1e-8):
            wrong.append(key)
        row = item.get("row")
        if not (str(item.get("table")) == str(gold[key][1]) and isinstance(row, str) and row.strip()):
            citations.append(key)
        if not isinstance(row,str) or " ".join(row.casefold().split()) != " ".join(gold[key][2].casefold().split()):
            row_diff.append(key)
    population = "mwanza" in str(spec.get("population","")).casefold()
    return numbers, {"pass": not wrong and not citations and population, "wrong_values": wrong,
                     "incorrect_table_or_missing_row": citations, "row_label_not_verbatim": row_diff,
                     "correct_municipal_locator": population}


def grids(v, n):
    tc, hdl = v["tc_mean"], v["hdl_mean"]
    if not (min(tc,hdl,v["tc_high_cut"],v["hdl_low_cut"]) > 0 and
            all(0 < v[k] < 100 for k in ("tc_high_pct","hdl_low_pct"))):
        raise ValueError("Source declarations cannot define positive marginal grids")
    s1, _ = fit_marginal(tc, v["tc_high_cut"], 1 - v["tc_high_pct"]/100)
    s2, _ = fit_marginal(hdl, v["hdl_low_cut"], v["hdl_low_pct"]/100)
    z = ndtri((np.arange(n, dtype=float)+.5)/n)
    m = np.exp(z[:, None] * np.array([s1, s2]))
    m *= (38.67*np.array([tc, hdl]))/m.mean(axis=0)
    if not np.all(np.isfinite(m)):
        raise ValueError("Nonfinite marginal grid")
    return m[:, 0], m[:, 1]


def task(n):
    t = {"schema_version":1, "task_id":"original_article_lipid_pairing", "mode":"whole_cohort",
         "population":"Mwanza municipal adults in the source-only sensitivity study",
         "row_id":"row_id", "n_rows":n,
         "columns":[{"name":x, "kind":"integer","role":role,"unit":"","nullable":False}
                    for x,role in (("row_id","identifier"),("hdl_index","generated"))],
         "information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
         "budget":{"source_queries":0,"source_downloads":0,"revisions":0}}
    ex.harness.contracts.validate_task(t)
    return t


def execute_candidate(obj, tc, hdl, seed, folder):
    candidate = folder/"input_candidate"
    candidate.mkdir(parents=True, exist_ok=False)
    t = task(len(tc))
    (candidate/"generator.py").write_text(obj["generator_py"], encoding="utf-8", newline="\n")
    ex.save(candidate/"model_spec.json", {"model":obj["model_spec"], "task":t,
            "tc_mg_dl":tc.tolist(),"hdl_mg_dl":hdl.tolist()})
    run = folder/"run"
    rec = ex.harness.isolated(candidate, t, run, seed)
    if rec["status"] != "success":
        report = run/"output/worker_report.json"
        detail = ex.read(report).get("error") if report.is_file() and report.stat().st_size else rec.get("error")
        raise ValueError("Isolated execution: " + str(detail)[:350])
    csv = run/"output/generated.csv"
    if ex.sha(csv) != rec["generated_sha256"]:
        raise RuntimeError("Output hash mismatch")
    rows = pd.read_csv(csv)
    if list(rows) != ["row_id","hdl_index"] or not np.array_equal(rows.row_id.to_numpy(), np.arange(len(tc))):
        raise ValueError("Incomplete or misaligned row identifiers")
    results = score(tc, hdl, rows.hdl_index.to_numpy())
    return {"seed":seed,"score":results,"output_sha256":rec["generated_sha256"]}


def model_result(name):
    model = ex.artifact(name)
    if model is None:
        return {"usable":False,"reason":"no_valid_model_artifact","draws":[]}
    v, audit = source_check(model["model_spec"])
    result = {"extraction":audit,"usable":False,"draws":[]}
    try:
        tc, hdl = grids(v,ex.N)
    except (ValueError, KeyError, ArithmeticError) as error:
        result["reason"] = "invalid_grid: "+str(error)
        return result
    for seed in ex.SEEDS:
        folder = ex.PRIVATE/"draws"/name/str(seed)
        out = folder/"RESULT.json"
        if out.is_file():
            row = ex.read(out)
            if "score" in row and ex.sha(folder/"run/output/generated.csv") != row["output_sha256"]:
                raise RuntimeError("Saved draw changed")
        else:
            try:
                row = execute_candidate(model, tc, hdl, seed, folder)
            except (ValueError, RuntimeError, OSError, AssertionError, TypeError) as error:
                row = {"seed":seed,"error":str(error)[:500]}
            ex.save(out,row)
        result["draws"].append(row)
    scores = [d["score"] for d in result["draws"] if "score" in d]
    if len(scores) != len(ex.SEEDS):
        result["reason"]="incomplete_generation"
        return result
    ref = reference()
    ratio = float(np.mean([s["mean_ratio"] for s in scores]))
    anchor = ref["mean_individual_ratio"][0]
    failures = []
    if not audit["pass"]: failures.append("source_extraction")
    if any(s["invalid_order"] for s in scores): failures.append("HDL_exceeds_TC")
    if any(abs(s["mean_ratio"]-anchor) > .02+1e-12 for s in scores): failures.append("per_seed_ratio")
    if not anchor-.005 <= ratio < anchor+.005: failures.append("pooled_ratio")
    implied = 38.67*(ref["tc_mean"][0]-ref["hdl_mean"][0])
    if any(abs(s["mean"]-implied)>1e-7 for s in scores):failures.append("component_mean_identity")
    result.update(usable=not failures,scientific_failures=failures,
                  percent=float(np.mean([s["percent"] for s in scores])),
                  mean=float(np.mean([s["mean"] for s in scores])), pooled_ratio=ratio)
    return result


def contrast(first, follow):
    valid = first["usable"] and follow["usable"]
    pair = {"both_valid":valid,"material":False}
    if valid:
        if abs(first["mean"]-follow["mean"])>1e-7:
            raise ArithmeticError("Fixed-component invariance failed for a valid pair")
        gaps = [b["score"]["percent"]-a["score"]["percent"]
                for a,b in zip(first["draws"],follow["draws"],strict=True)]
        avg = float(np.mean(gaps))
        pair.update(gap_pp=abs(avg), seed_gaps_pp=gaps, first_pct=first["percent"], second_pct=follow["percent"],
                    material=bool(abs(avg)>4 and all(np.sign(avg)*u>2 for u in gaps)))
    return pair


def matched(blocks):
    alt = [i["alternative"]["material"] for i in blocks.values()]
    ordinary = [i["ordinary"]["material"] for i in blocks.values()]
    plus = sum(a and not o for a,o in zip(alt,ordinary,strict=True))
    minus = sum(o and not a for a,o in zip(alt,ordinary,strict=True))
    both_valid = sum(i["alternative"]["both_valid"] and i["ordinary"]["both_valid"] for i in blocks.values())
    return {"n_blocks":len(blocks),"alternative_material":sum(alt),"ordinary_material":sum(ordinary),
            "both_material":sum(a and o for a,o in zip(alt,ordinary,strict=True)),
            "alternative_only":plus, "ordinary_only":minus, "both_arms_valid":both_valid,
            "difference_fraction":(sum(alt)-sum(ordinary))/len(blocks),
            "exact_two_sided_p":float(binomtest(plus,plus+minus,.5).pvalue) if plus+minus else 1.0,
            "next_source_gate_before_independent_check":both_valid>=8 and sum(alt)>sum(ordinary)}


def evaluate():
    ex.guard()
    closure=ex.read(ex.HERE/"AUTHORS.json")
    if closure["freeze_sha256"]!=ex.sha(ex.HERE/"FREEZE.json"):
        raise RuntimeError("Unexpected author closure")
    dest=ex.HERE/"RESULTS.json"
    if dest.exists():return
    with ThreadPoolExecutor(max_workers=3) as workers:
        names=sorted(closure["calls"])
        models=dict(zip(names,workers.map(model_result,names),strict=True))
    blocks={b:{a:contrast(models[b+"_initial"],models[b+"_"+a]) for a in ex.ARMS} for b in ex.BLOCKS}
    ex.save(dest,{"closed_utc":ex.now(),"authors_sha256":ex.sha(ex.HERE/"AUTHORS.json"),
                  "models":models,"blocks":blocks,"primary":matched(blocks)})
    print("Scoring closed.",flush=True)


def preflight():
    gold=reference()
    stub={"population":"Mwanza municipality",
          "evidence":{k:{"value":v,"table":t,"row":r} for k,(v,t,r) in gold.items()}}
    v,check=source_check(stub)
    assert check["pass"] and not check["row_label_not_verbatim"]
    invalid={**stub, "evidence":dict(stub["evidence"], tc_mean={"value":2,"table":3,"row":"x"})}
    assert not source_check(invalid)[1]["pass"]
    x,y=grids(v,64)
    assert abs(np.mean(x-y)-38.67*(v["tc_mean"]-v["hdl_mean"])) < 1e-8
    try:score(x,y,np.zeros(64,dtype=int))
    except ValueError:pass
    else:raise AssertionError("Invalid permutation accepted")
    fixture={"model_spec":stub,"generator_py":"import numpy as np\nimport pandas as pd\ndef generate(observed,spec,seed):\n    ix=np.arange(spec['task']['n_rows'])\n    return pd.DataFrame({'row_id':ix,'hdl_index':ix})\n"}
    folder=ex.PRIVATE/"preflight_worker"
    import tempfile
    folder.mkdir(parents=True,exist_ok=True)
    row=execute_candidate(fixture,x,y,17,Path(tempfile.mkdtemp(dir=folder)))
    assert row["score"]==score(x,y,np.arange(64))
    def fake(seq):
        return {"usable":True,"mean":1,"percent":float(np.mean(seq)),
                "draws":[{"score":{"percent":x}} for x in seq]}
    assert contrast(fake([10,10,10]),fake([15,15,15]))["material"]
    assert not contrast(fake([10,10,10]),fake([11,16,17]))["material"]
    assert not contrast(fake([10,10,10]),fake([14,14,14]))["material"]
    captions = re.findall(r"^Table (\d+)\. ", ex.article(), flags=re.M)
    assert captions == ["1", "2", "3", "4", "5"]
    return {"source_checker":True,"duplicate_rejected":True,"isolated_generator":True,
            "threshold_and_matched_seed_tests":True, "n_original_tables":len(captions)}
