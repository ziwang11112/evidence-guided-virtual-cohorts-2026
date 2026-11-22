"""Frozen lung-source checks, executable within-person assignments and downstream estimands."""
from concurrent.futures import ThreadPoolExecutor
import math
from pathlib import Path
import tempfile

import numpy as np
import pandas as pd
from scipy.special import ndtri
from scipy.stats import binomtest

import trial as t

SEXES = ("F", "M")
FIELDS = ("source_n","fev1_mean","fev1_sd","fvc_mean","fvc_sd","pearson","slope","intercept_l","r2_pct")
STEPS = {"fev1_mean":.1, "fev1_sd":.1, "fvc_mean":.1, "fvc_sd":.1,
         "pearson":.01, "r2_pct":.1, "slope":.01, "intercept_l":.01}


def gold():
    m = {g["sex"]:g for g in t.read(t.LUNG/"MARGINAL_SOURCE.json")["cells"]}
    j = {g["sex"]:g for g in t.read(t.LUNG/"JOINT_SOURCE.json")["cells"]}
    return {s:{**{k:m[s][k] for k in FIELDS[:5]}, **{k:j[s][k] for k in FIELDS[5:8]},
               "r2_pct":round(100*j[s]["R2"],1)} for s in SEXES}


def evidence(spec):
    expected = gold()
    cells = spec.get("cells")
    cells = cells if isinstance(cells,dict) else {}
    extracted = {s:{} for s in SEXES}
    wrong = []
    for s in SEXES:
        source = cells.get(s)
        source = source if isinstance(source,dict) else {}
        for name,target in expected[s].items():
            v = source.get(name)
            if type(v) in (int,float) and math.isfinite(v):
                extracted[s][name] = v
            if name not in extracted[s] or not math.isclose(extracted[s][name],target,rel_tol=0,abs_tol=1e-9):
                wrong.append(s+"."+name)
    if set(cells) != set(SEXES): wrong.append("sex_groups")
    for key,correct in (("volume_unit","L"),("marginal_table",1),("joint_table",2)):
        if type(spec.get(key)) != type(correct) or spec[key] != correct: wrong.append(key)
    return extracted,wrong


def grids(cells,n):
    z = ndtri((np.arange(n,dtype=float)+.5)/n)
    def column(mu,sd):
        if not (mu>0 and sd>0): raise ValueError("Nonpositive volume moment")
        v = np.exp(math.sqrt(math.log1p((sd/mu)**2))*z)
        return mu+sd*(v-v.mean())/v.std()
    groups = []
    for sex in SEXES:
        c = cells[sex]
        root = math.sqrt(c["r2_pct"]/100.)
        if not 0<root<=1: raise ValueError("Invalid reported R-squared")
        y = column(c["fvc_mean"], c["fvc_sd"])
        x = column(c["intercept_l"]+c["slope"]*c["fvc_mean"], c["slope"]*c["fvc_sd"]/root)
        if not np.all(np.isfinite(x)&np.isfinite(y)&(x>0)&(y>0)) or not np.all((np.diff(x)>0)&(np.diff(y)>0)):
            raise ValueError("Invalid marginal grids")
        groups.append((sex,x,y))
    return groups


def in_bin(value,point,step):
    return point-step/2 <= value < point+step/2


def cell_moments(x,y):
    mx,my = float(x.mean()),float(y.mean())
    sx,sy = float(x.std()),float(y.std())
    r = float(np.mean((x-mx)*(y-my))/(sx*sy))
    slope = r*sx/sy
    return {"fev1_mean":mx,"fev1_sd":sx,"fvc_mean":my,"fvc_sd":sy,"pearson":r,
            "r2_pct":100*r*r,"slope":slope,"intercept_l":mx-slope*my}


def valid_permutation(values,n):
    v=np.asarray(values)
    if v.shape!=(n,) or v.dtype.kind not in "iu" or not np.array_equal(np.sort(v),np.arange(n)):
        raise ValueError("Invalid within-sex index permutation")
    return v


def score_rows(groups,indices,expected):
    checks, details = [], {}
    for (sex,x,y),order in zip(groups,indices,strict=True):
        y2=y[valid_permutation(order,len(x))]
        ms=cell_moments(x,y2)
        failures=[k for k in STEPS if not in_bin(ms[k],expected[sex][k],STEPS[k])]
        if abs(y.mean()-y2.mean())>1e-10 or abs(y.std()-y2.std())>1e-10: failures.append("marginal_invariance")
        impossible=int(np.count_nonzero(x>y2))
        if impossible: failures.append("FEV1_exceeds_FVC")
        checks.extend(sex+"."+f for f in failures)
        details[sex]={"moments":ms,"n":len(x),"below":int(np.count_nonzero(x/y2<.70)),
                      "invalid_order":impossible}
    pc=float(np.mean([100*d["below"]/d["n"] for d in details.values()]))
    fixed=100*sum(d["moments"]["fev1_mean"] for d in details.values())/sum(d["moments"]["fvc_mean"] for d in details.values())
    return {"percent":pc,"ratio_of_means_pct":fixed,"sex":details,"failures":checks}


def task(n):
    obj={"schema_version":1,"task_id":"article_lung_source","mode":"whole_cohort",
         "population":"Equal-sex virtual population of healthy adults in the Polish publication",
         "row_id":"row_id","n_rows":n,
         "columns":[{"name":name,"kind":"integer","role":role,"unit":"","nullable":False}
                    for name,role in (("row_id","identifier"),("fvc_index","generated"))],
         "information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
         "budget":{"source_queries":0,"source_downloads":0,"revisions":0}}
    t.harness.contracts.validate_task(obj)
    return obj


def run_model(obj,groups,seed,path):
    folder=path/"candidate"
    folder.mkdir(parents=True,exist_ok=False)
    n=len(groups[0][1])
    contract=task(2*n)
    (folder/"generator.py").write_text(obj["generator_py"],encoding="utf8",newline="\n")
    t.save(folder/"model_spec.json",{"model":obj["model_spec"],"task":contract,
           "groups":[{"sex":s,"fev1":x.tolist(),"fvc":y.tolist()} for s,x,y in groups]})
    run=path/"run"
    rec=t.harness.isolated(folder,contract,run,seed)
    if rec["status"]!="success":
        report=run/"output/worker_report.json"
        detail=t.read(report).get("error") if report.is_file() and report.stat().st_size else rec.get("error")
        raise ValueError("Worker failure: "+str(detail)[:350])
    out=run/"output/generated.csv"
    if t.sha(out)!=rec["generated_sha256"]: raise RuntimeError("CSV hash changed")
    rows=pd.read_csv(out)
    if list(rows)!=["row_id","fvc_index"] or not np.array_equal(rows.row_id.to_numpy(),np.arange(2*n)):
        raise ValueError("Output row identity error")
    index=rows.fvc_index.to_numpy()
    return [valid_permutation(v,n) for v in (index[:n],index[n:])],rec["generated_sha256"]


def evaluate_slot(slot):
    obj=t.artifact(slot)
    if obj is None: return {"usable":False,"reason":"unavailable_artifact","draws":[]}
    cells,issues=evidence(obj["model_spec"])
    out={"usable":False,"extraction_failures":issues,"draws":[]}
    try:
        g=grids(cells,t.N)
    except (KeyError,ValueError,TypeError,ArithmeticError) as error:
        out["reason"]="invalid_grid: "+str(error)[:160]
        return out
    for seed in t.SEEDS:
        path=t.PRIVATE/"draws"/slot/str(seed)
        receipt=path/"DRAW.json"
        if receipt.is_file():
            draw=t.read(receipt)
            if "sha256" in draw and t.sha(path/"run/output/generated.csv")!=draw["sha256"]:
                raise RuntimeError("Recorded assignment changed")
        else:
            try:
                orders,h=run_model(obj,g,seed,path)
                draw={"seed":seed,"sha256":h,"outcome":score_rows(g,orders,gold())}
            except (OSError,ValueError,RuntimeError,TypeError,AssertionError,ArithmeticError) as error:
                draw={"seed":seed,"error":str(error)[:450]}
            t.save(receipt,draw)
        out["draws"].append(draw)
    valid_draws=[d["outcome"] for d in out["draws"] if "outcome" in d]
    if len(valid_draws)!=len(t.SEEDS):
        out["reason"]="incomplete_generation"
        return out
    failures=sorted({f for d in valid_draws for f in d["failures"]})
    out.update(usable=not issues and not failures,scientific_failures=failures,
               percent=float(np.mean([d["percent"] for d in valid_draws])),
               ratio_of_means_pct=float(np.mean([d["ratio_of_means_pct"] for d in valid_draws])))
    return out


def compare(first,second):
    ok=first["usable"] and second["usable"]
    pair={"valid":ok,"material":False}
    if ok:
        if abs(first["ratio_of_means_pct"]-second["ratio_of_means_pct"])>1e-8:
            raise ValueError("Ratio-of-means identity failed")
        gaps=np.array([b["outcome"]["percent"]-a["outcome"]["percent"]
                       for a,b in zip(first["draws"],second["draws"],strict=True)])
        mean=float(gaps.mean())
        pair.update(gap_pp=mean,seed_gaps_pp=gaps.tolist(),material=bool(abs(mean)>5 and np.all(np.sign(mean)*gaps>2)))
    return pair


def evaluate():
    t.guard()
    close=t.read(t.HERE/"AUTHORS.json")
    assert t.sha(t.HERE/"FREEZE.json")==close["freeze_sha256"] and len(close["calls"])==36
    dest=t.HERE/"RESULTS.json"
    if dest.is_file(): return
    names=sorted(close["calls"])
    with ThreadPoolExecutor(max_workers=3) as workers:
        models=dict(zip(names,workers.map(evaluate_slot,names),strict=True))
    blocks={b:{a:compare(models[b+"_initial"],models[b+"_"+a]) for a in t.ARMS} for b in t.BLOCKS}
    flags=[(b["ordinary"]["material"],b["alternative"]["material"]) for b in blocks.values()]
    alt=flags.count((False,True));ordinary=flags.count((True,False))
    complete=sum(b["ordinary"]["valid"] and b["alternative"]["valid"] for b in blocks.values())
    primary={"n_blocks":len(blocks),"both_arms_valid":complete,"ordinary_material":sum(x for x,y in flags),
             "targeted_material":sum(y for x,y in flags),"ordinary_only":ordinary,"targeted_only":alt,
             "p_exact_paired":float(binomtest(alt,alt+ordinary,.5).pvalue) if alt+ordinary else 1.,
             "next_gate_before_verification":complete>=8 and alt>ordinary}
    t.save(dest,{"utc":t.now(),"author_sha256":t.sha(t.HERE/"AUTHORS.json"),"models":models,"blocks":blocks,"primary":primary})
    print("Closed.",flush=True)


def preflight():
    import re
    truth=gold()
    groups=grids(truth,t.N)
    fixture={}
    for sex,x,y in groups:
        c=truth[sex]
        assert np.all(x<=y)
        target=math.sqrt(c["r2_pct"]/100)
        # Establish numeric compatibility without computing the scientific screening endpoint.
        shuffled=y.copy()
        rng=np.random.default_rng(22603)
        r=cell_moments(x,shuffled)["pearson"]
        den=len(x)*x.std()*y.std()
        for _ in range(150*len(x)):
            i,j=rng.integers(0,len(x),size=2)
            delta=(x[i]-x[j])*(shuffled[j]-shuffled[i])/den
            if x[i]<=shuffled[j] and x[j]<=shuffled[i] and abs(r+delta-target)<abs(r-target):
                shuffled[i],shuffled[j]=shuffled[j],shuffled[i]
                r+=delta
            if abs(r-target)<1e-5: break
        ms=cell_moments(x,shuffled)
        assert all(in_bin(ms[k],c[k],step) for k,step in STEPS.items()) and np.all(x<=shuffled)
        fixture[sex]={"all_eight_rounding_bins_pass":True,"fev1_mean_l":ms["fev1_mean"],
                      "fev1_sd_l":ms["fev1_sd"],"witness_r":ms["pearson"]}
    try:valid_permutation([0,0],2)
    except ValueError:pass
    else:raise AssertionError("Duplicate not rejected")
    def fake(xs):return {"usable":True,"ratio_of_means_pct":75,"draws":[{"outcome":{"percent":i}} for i in xs]}
    assert compare(fake([9,9,9]),fake([15,15,15]))["material"]
    assert not compare(fake([9,9,9]),fake([14,14,14]))["material"]
    assert not compare(fake([9,9,9]),fake([11,17,17]))["material"]
    assert compare(fake([15,15,15]),fake([9,9,9]))["material"]
    args={"model_spec":{"cells":truth},"generator_py":"import numpy as np\nimport pandas as pd\ndef generate(observed,spec,seed):\n    m=len(spec['groups'][0]['fev1'])\n    return pd.DataFrame({'row_id':np.arange(2*m),'fvc_index':np.tile(np.arange(m),2)})\n"}
    orders,_=run_model(args,grids(truth,128),111,Path(tempfile.mkdtemp(dir=t.PRIVATE)))
    assert all(np.array_equal(a,np.arange(128)) for a in orders)
    rendered=t.article()
    assert re.findall(r"^Table ([12])\. ", rendered,re.M)==["1","2"]
    assert all("Figure "+str(i) in rendered for i in range(1,5))
    assert all("("+str(i)+")" in rendered for i in range(1,9))
    return {"rounding_and_physiological_witness":fixture,"isolated_worker_test":True,
            "threshold_tests":True,"source_tables":2,"source_figure_captions":4,"source_display_equations":8}
