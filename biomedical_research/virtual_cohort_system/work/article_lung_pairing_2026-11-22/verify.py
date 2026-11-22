"""Independent extraction from publisher XML, row-level recomputation and API receipt check."""
from collections import Counter
from functools import lru_cache
import csv
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import NormalDist
import xml.etree.ElementTree as ET

import numpy as np
from scipy.stats import binomtest, linregress

HERE=Path(__file__).resolve().parent
SRC=HERE.parent/"spirometry_pairing_2026-11-21/private/source_epmc.xml"
CALLS=HERE/"private/api/calls"


def load(path): return json.loads(path.read_text(encoding="utf8"))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def digest(text): return hashlib.sha256(text.encode()).hexdigest()
def flat(cell): return " ".join("".join(cell.itertext()).split())


def source():
    tree=ET.parse(SRC)
    tabs={t.findtext("label"):t for t in tree.findall(".//body//table-wrap")}
    assert set(tabs)=={"Table 1","Table 2"}
    groups={"F":{},"M":{}}
    rows=[[flat(v) for v in tr if v.tag in ("td","th")] for tr in tabs["Table 1"].findall(".//tr")]
    assert rows[0][1:]==["Males","Females"]
    for s,position in (("M",1),("F",2)):
        for r in rows:
            if r[0]=="Less non-healthy subjects":groups[s]["source_n"]=int(r[position])
            for title,key in (("FEV1 (L)","fev1"),("FVC (L)","fvc")):
                if r[0]==title:
                    mean,sd=r[position].split("±")
                    groups[s][key+"_mean"]=float(mean)
                    groups[s][key+"_sd"]=float(sd)
    s=None
    selector=False
    for tr in tabs["Table 2"].findall(".//tr"):
        cells=[flat(v) for v in tr if v.tag in ("td","th")]
        entry=cells[0]
        if entry=="FEV1 on FVC":
            assert cells[1]=="FEV1 on FVC and age"
            selector=True
        elif selector and entry in ("males","females"):s={"males":"M","females":"F"}[entry]
        elif s and entry.startswith("FEV1"):
            mt=re.search(r"=\s*([0-9.]+)\s*[·⋅×*]\s*FVC\s*([−–-])\s*([0-9.]+)",entry)
            groups[s]["slope"]=float(mt.group(1))
            groups[s]["intercept_l"]=-float(mt.group(3))
        elif s and entry.startswith("R2"):
            m=re.search(r"=\s*([0-9.]+)\s*%,\s*r\s*=\s*([0-9.]+)",entry)
            groups[s].update(r2_pct=float(m.group(1)),pearson=float(m.group(2)))
    assert all(len(v)==9 for v in groups.values())
    return groups


def extracted(spec,gold):
    cells=spec.get("cells")
    if not isinstance(cells,dict) or set(cells)!=set(gold):return False
    if spec.get("volume_unit")!="L" or any(type(spec.get(k)) is not int or spec[k]!=t for k,t in (("marginal_table",1),("joint_table",2))):return False
    return all(isinstance(cells[s],dict) and type(cells[s].get(k)) in (int,float) and
               abs(cells[s][k]-v)<=1e-9 for s in gold for k,v in gold[s].items())


@lru_cache(maxsize=64)
def grid_pair(y_mean,y_sd,slope,intercept,r2,n):
    q=np.fromiter((NormalDist().inv_cdf((i+.5)/n) for i in range(n)),float,count=n)
    def grid(center,sd):
        shape=math.sqrt(math.log1p(sd*sd/(center*center)))
        a=np.exp(q*shape)
        avg=math.fsum(a)/n
        sig=math.sqrt(math.fsum((a-avg)**2)/n)
        return center + (sd/sig)*(a-avg)
    return grid(intercept+slope*y_mean,slope*y_sd/math.sqrt(r2/100)),grid(y_mean,y_sd)


def load_pairs(path,n):
    with path.open(encoding="utf8",newline="") as f:
        reader=csv.DictReader(f)
        assert reader.fieldnames==["row_id","fvc_index"]
        rows=[(int(r["row_id"]),int(r["fvc_index"])) for r in reader]
    assert len(rows)==2*n and all(j[0]==i for i,j in enumerate(rows))
    arrays=np.array([i[1] for i in rows],dtype=np.int64).reshape(2,n)
    assert all(np.array_equal(np.sort(line),np.arange(n)) for line in arrays)
    return arrays


def cost_and_prompts(closure,frozen):
    total=0.; known=0.; actual=0; first_body=None; by_role=Counter();n_usage=0
    statuses=Counter()
    for tag,rec in sorted(closure["calls"].items()):
        status=rec["status"];statuses[status]+=1
        folder=CALLS/tag
        if status.startswith("unissued"):
            assert not (folder/"reservation.json").exists()
            continue
        original=load(folder/"receipt.json")
        assert status==original["status"] and sha(folder/"request.json")==rec["request_sha256"]
        assert sha(folder/"prompt.txt")==rec["prompt_sha256"] and original["no_automatic_retry"]
        if rec.get("response_text.txt_sha256"):
            assert rec["response_text.txt_sha256"]==sha(folder/"response_text.txt")
        body=load(folder/"request.json")["body"];text=(folder/"prompt.txt").read_text(encoding="utf8")
        assert body["input"]==text and body["model"]=="gpt-6.1-sol" and body["service_tier"]=="default" and body["store"] is False
        assert body["max_output_tokens"]==12000 and body["reasoning"]["effort"]=="medium"
        assert digest(body["instructions"])==frozen["system_sha256"]
        block,role=tag.split("_");actual+=1
        paper,inst=text.rsplit("\n\nAUTHORING REQUEST\n",1)
        assert digest(inst)==frozen["instruction_sha256"][role]
        if role=="initial":assert digest(text)==frozen["initial_prompt_sha256"]
        else:
            paper,submitted=paper.split("\n\nINITIAL SUBMISSION\n",1)
            assert json.loads(submitted)==load(CALLS/(block+"_initial")/"artifact.json")
        if first_body is None:first_body=paper
        assert paper==first_body
        if rec["tariff_cost_usd"] is None:
            amount=load(folder/"reservation.json")["reserved_usd"]
        else:
            u=load(folder/"response_raw.json")["usage"]
            cache=u["input_tokens_details"].get("cached_tokens",0) or 0
            writes=u["input_tokens_details"].get("cache_write_tokens",0) or 0
            fee=(2*(u["input_tokens"]-cache-writes)+.1*cache+2.5*writes+10*u["output_tokens"])/1e6
            assert math.isclose(fee,rec["tariff_cost_usd"],rel_tol=0,abs_tol=1e-10)
            amount=fee;known+=fee;n_usage+=1
        total+=amount;by_role[role]+=amount
    assert abs(total-closure["accounted_usd"])<1e-8 and total<=18
    return {"issued":actual,"itemized_usage":n_usage,"statuses":dict(statuses),
            "tariff_usd":round(known,9),"accounted_usd":round(total,9),
            "role_accounted_usd":{k:round(v,9) for k,v in by_role.items()}}


def main():
    a=load(HERE/"AUTHORS.json");r=load(HERE/"RESULTS.json");f=load(HERE/"FREEZE.json")["design"]
    assert sha(HERE/"AUTHORS.json")==r["author_sha256"] and sha(HERE/"FREEZE.json")==a["freeze_sha256"]
    assert f["source_xml_sha256"]==sha(SRC)
    g=source(); n=f["n_per_sex"]; assert n==8000
    passes={}; seeded={}; inspected=0;errors=0;correct=0
    bins={"fev1_mean":.1,"fvc_mean":.1,"fev1_sd":.1,"fvc_sd":.1,
          "r2_pct":.1,"pearson":.01,"slope":.01,"intercept_l":.01}
    for name,model in sorted(r["models"].items()):
        path=CALLS/name/"artifact.json"
        if not path.exists() or "extraction_failures" not in model:
            assert not model["usable"] and not model["draws"]
            passes[name]=False;seeded[name]=[]
            continue
        spec=load(path)["model_spec"]
        assert sha(path)==a["calls"][name]["artifact.json_sha256"]
        ok=extracted(spec,g)
        assert ok==(not model["extraction_failures"])
        correct+=int(ok);gs=[]
        for row in model["draws"]:
            folder=HERE/"private/draws"/name/str(row["seed"])/"run/output"
            if "outcome" not in row:
                errors+=1;ok=False
                worker=folder/"worker_report.json"
                if worker.is_file() and worker.stat().st_size and load(worker).get("status")=="completed":
                    try:load_pairs(folder/"generated.csv",n)
                    except (ValueError,AssertionError,TypeError):pass
                    else:raise AssertionError("Unexplained failure for a completed valid permutation "+name)
                continue
            out=row["outcome"]
            assert sha(folder/"generated.csv")==row["sha256"]
            orders=load_pairs(folder/"generated.csv",n)
            counts=[];xx=[];yy=[];fails=[]
            for line,s in zip(orders,("F","M"),strict=True):
                v=spec["cells"][s]
                x,y=grid_pair(v["fvc_mean"],v["fvc_sd"],v["slope"],v["intercept_l"],v["r2_pct"],n)
                y=y[line]; info=out["sex"][s]
                l=linregress(y,x)
                vals={"fev1_mean":np.mean(x),"fvc_mean":np.mean(y),"fev1_sd":np.std(x),"fvc_sd":np.std(y),
                      "slope":l.slope,"intercept_l":l.intercept,"r2_pct":100*l.rvalue*l.rvalue,"pearson":l.rvalue}
                for k,step in bins.items():
                    assert abs(vals[k]-info["moments"][k])<1e-8,(name,s,k)
                    if not g[s][k]-step/2<=vals[k]<g[s][k]+step/2:fails.append(s+"."+k)
                invalid=int(np.count_nonzero(x>y))
                assert invalid==info["invalid_order"]
                if invalid:fails.append(s+".FEV1_exceeds_FVC")
                count=int(np.count_nonzero(x/y<.70))
                assert count==info["below"] and info["n"]==n
                counts.append(count);xx.append(np.mean(x));yy.append(np.mean(y))
            percent=100*(sum(counts)/(2*n));fixed=100*sum(xx)/sum(yy)
            assert abs(percent-out["percent"])<1e-10 and abs(fixed-out["ratio_of_means_pct"])<1e-9
            assert set(fails)==set(out["failures"])
            gs.append(percent);ok &= not bool(fails);inspected+=1
        ok=bool(ok and len(gs)==3)
        assert ok==model["usable"],name
        if len(gs)==3:assert abs(np.mean(gs)-model["percent"])<1e-9
        passes[name]=ok;seeded[name]=gs
    pairs=[];complete=0
    for block,data in sorted(r["blocks"].items()):
        init=block+"_initial"; flags=[]; both=True
        for arm in ("ordinary","alternative"):
            nxt=block+"_"+arm;ok=passes[init] and passes[nxt];m=False
            if ok:
                ds=np.subtract(seeded[nxt],seeded[init]);avg=float(ds.mean())
                assert abs(avg-data[arm]["gap_pp"])<1e-10
                m=abs(avg)>5 and min(np.sign(avg)*ds)>2
            assert (ok, bool(m))==(data[arm]["valid"],data[arm]["material"])
            flags.append(bool(m));both &= ok
        pairs.append(tuple(flags));complete+=int(both)
    pos=pairs.count((False,True));neg=pairs.count((True,False))
    prim={"n_blocks":len(pairs),"both_arms_valid":complete,"ordinary_material":sum(i for i,j in pairs),
          "targeted_material":sum(j for i,j in pairs),"ordinary_only":neg,"targeted_only":pos,
          "p_exact_paired":float(binomtest(pos,pos+neg,.5).pvalue) if pos+neg else 1.,
          "next_gate_before_verification":complete>=8 and pos>neg}
    assert prim==r["primary"]
    report={"article_doi":"10.1186/1465-9921-13-57","primary":prim,"article_extractions_pass":correct,
            "scored_draws_independently_recomputed":inspected,"unscored_draws":errors,
            "valid_programs":sum(passes.values()),"matched_comparisons_recomputed":len(pairs)*2,
            "paired_prompt_source_and_parent_checked":True,"cost":cost_and_prompts(a,f),
            "results_sha256":sha(HERE/"RESULTS.json")}
    out=HERE/"VERIFICATION.json"
    if out.exists():assert load(out)==report
    else:out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8",newline="\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":main()
