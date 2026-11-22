"""Independent readback of the closed experiment from the article, API and generated assignments."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET

import numpy as np
from scipy.special import ndtri
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "nonhdl_external_2026-11-20"
API = HERE / "private/api/calls"


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def compact(el):
    return " ".join("".join(el.itertext()).split())


def article_gold():
    doc = ET.parse(OLD / "private/source.xml")
    found = {}
    lookup = {"TC (mmol/L)":"tc_mean", "HDL-C (mmol/L)":"hdl_mean",
              "TC/HDL-C ratio":"mean_individual_ratio","Non HDL cholesterol":"nonhdl_mean",
              "High TC (≥6.2 mmol/L)":"tc_high_pct", "Low HDL-C (<1 mmol/L)":"hdl_low_pct"}
    for table in doc.findall(".//body//table-wrap"):
        caption = table.findtext("label")
        if caption not in ("Table 2","Table 3"):
            continue
        municipal_column = None
        for row in table.findall(".//tr"):
            cols = [compact(c) for c in row if c.tag in ("td","th")]
            if cols[0] == "TANZANIA":
                matches = [i for i, text in enumerate(cols) if "Mwanza municipality" in text]
                assert len(matches) == 1
                municipal_column = matches[0]
            if cols[0] == "UGANDA":
                municipal_column = None
            if municipal_column is None or cols[0] not in lookup:
                continue
            key=lookup[cols[0]]
            central=float(re.match(r"\d+(?:\.\d+)?",cols[municipal_column]).group())
            found[key]=(central,int(caption.split()[1]),cols[0])
            if key.endswith("_pct"):
                cut=float(re.search(r"\d+\.?\d*",cols[0]).group())
                found[key.replace("_pct","_cut")]=(cut,int(caption.split()[1]),cols[0])
    assert len(found)==8
    return found


def check_model_evidence(spec,gold):
    ev=spec.get("evidence",{})
    if not isinstance(ev,dict): return False
    for k,(expected,table,_) in gold.items():
        entry=ev.get(k,{})
        if not isinstance(entry,dict) or type(entry.get("value")) not in (int,float):return False
        if not math.isclose(entry["value"],expected,rel_tol=0,abs_tol=1e-8):return False
        if str(entry.get("table"))!=str(table) or not str(entry.get("row") or "").strip():return False
    return "mwanza" in str(spec.get("population","")).lower()


def one_column(mean,cut,below,n):
    # Solve the reported lognormal mean/quantile condition independently.
    z=ndtri(below)
    roots=np.roots([1.,-2*z,2*np.log(cut/mean)])
    s=min(float(v.real) for v in roots if abs(v.imag)<1e-8 and v.real>0)
    values=np.exp(s*ndtri((np.arange(n,dtype=float)+0.5)/n))
    return values*(mean*38.67/values.mean())


def settled_costs(records):
    total=0.; known=0.; usage_count=0
    asserted_calls=0
    statuses=Counter()
    for tag,rec in records.items():
        statuses[rec["status"]]+=1
        if rec["status"].startswith("unissued"):
            assert not (API/tag/"reservation.json").exists()
            continue
        asserted_calls+=1
        fol=API/tag
        orig=load(fol/"receipt.json")
        assert orig["request_sha256"]==sha(fol/"request.json") and orig["prompt_sha256"]==sha(fol/"prompt.txt")
        if (fol/"response_text.txt").exists():
            assert rec["response_text.txt_sha256"]==sha(fol/"response_text.txt")
        body=load(fol/"request.json")["body"]
        assert body["model"]=="gpt-6.1-sol" and body["store"] is False and body["service_tier"]=="default"
        assert body["input"]==(fol/"prompt.txt").read_text(encoding="utf-8")
        assert body["max_output_tokens"]==12000 and body["reasoning"]["effort"]=="medium"
        if orig["tariff_cost_usd"] is None:
            total+=load(fol/"reservation.json")["reserved_usd"]
        else:
            raw=load(fol/"response_raw.json")["usage"]
            cache=raw["input_tokens_details"].get("cached_tokens",0) or 0
            written=raw["input_tokens_details"].get("cache_write_tokens",0) or 0
            amount=((raw["input_tokens"]-cache-written)*2+cache*.1+written*2.5+raw["output_tokens"]*10)/1e6
            assert abs(orig["tariff_cost_usd"]-amount)<1e-9 and abs(rec["tariff_cost_usd"]-amount)<1e-9
            total+=amount;known+=amount;usage_count+=1
    return {"model_calls":asserted_calls,"usage_available":usage_count,
            "tariff_known_usd":known,"accounted_usd":total,"statuses":dict(statuses)}


def main():
    f=load(HERE/"FREEZE.json"); authors=load(HERE/"AUTHORS.json"); result=load(HERE/"RESULTS.json")
    assert sha(HERE/"FREEZE.json")==authors["freeze_sha256"] and sha(HERE/"AUTHORS.json")==result["authors_sha256"]
    gold=article_gold()
    n=16000
    attested={};rows_checked=0;execution_errors=0;verified_evidence=0
    for tag,m in result["models"].items():
        obj_file=API/tag/"artifact.json"
        values=None
        if obj_file.is_file() and "extraction" in m:
            spec=load(obj_file)["model_spec"]
            ok=check_model_evidence(spec,gold)
            assert ok==m["extraction"]["pass"]
            verified_evidence+=1
            if isinstance(spec.get("evidence"),dict):
                values={k:v.get("value") for k,v in spec["evidence"].items() if isinstance(v,dict)}
        else:ok=False
        per_seed=[];ratio_values=[];feasible=True
        for row in m["draws"]:
            seed=row["seed"];out=HERE/"private/draws"/tag/str(seed)/"run/output"
            if "score" not in row:
                execution_errors+=1
                worker=out/"worker_report.json"
                if worker.is_file() and worker.stat().st_size and load(worker).get("status")=="completed":
                    with (out/"generated.csv").open(encoding="utf-8",newline="") as h:
                        raw=list(csv.DictReader(h))
                    ids=[x["row_id"] for x in raw];indices=[x["hdl_index"] for x in raw]
                    invalid_ids=ids!=[str(i) for i in range(n)]
                    try:invalid_index=sorted(map(int,indices))!=list(range(n))
                    except (ValueError,TypeError):invalid_index=True
                    assert invalid_ids or invalid_index, "Unexplained host-side failed output"
                feasible=False
                continue
            assert row["output_sha256"]==sha(out/"generated.csv")
            with (out/"generated.csv").open(encoding="utf-8",newline="") as h:
                reader=csv.DictReader(h); assert reader.fieldnames==["row_id","hdl_index"]
                pairs=np.array([(int(v["row_id"]),int(v["hdl_index"])) for v in reader],dtype=np.int64)
            assert pairs.shape==(n,2) and np.array_equal(pairs[:,0],np.arange(n))
            assert np.array_equal(np.sort(pairs[:,1]),np.arange(n))
            x=one_column(values["tc_mean"],values["tc_high_cut"],1-values["tc_high_pct"]/100,n)
            hdl=one_column(values["hdl_mean"],values["hdl_low_cut"],values["hdl_low_pct"]/100,n)
            y=hdl[pairs[:,1]]; delta=x-y
            ratio=float(np.mean(x/y));k=int(np.sum(delta>=160.0));invalid=int(np.sum(y>x))
            expected=row["score"]
            assert (k,invalid,n)==(expected["tail_count"],expected["invalid_order"],expected["n"])
            assert abs(ratio-expected["mean_ratio"])<1e-9 and abs(float(np.mean(delta))-expected["mean"])<1e-7
            feasible&=(invalid==0 and abs(ratio-gold["mean_individual_ratio"][0])<=.02+1e-12 and
                       abs(float(np.mean(delta))-38.67*(gold["tc_mean"][0]-gold["hdl_mean"][0]))<1e-7)
            per_seed.append(100*k/n);ratio_values.append(ratio)
            rows_checked+=1
        r=gold["mean_individual_ratio"][0]
        valid=bool(ok and feasible and len(per_seed)==3 and r-.005<=np.mean(ratio_values)<r+.005)
        assert valid==m["usable"],tag
        attested[tag]=(valid,per_seed)
    blocks=result["blocks"];matches=[]
    for block in sorted(blocks):
        initial=attested[block+"_initial"]
        prefixes=[]
        parent=API/(block+"_initial")/"artifact.json"
        for arm in ("ordinary","alternative"):
            fol=API/(block+"_"+arm)
            if (fol/"prompt.txt").is_file():
                p=(fol/"prompt.txt").read_text(encoding="utf8")
                prefix,instruction=p.rsplit("\n\nAUTHORING REQUEST\n",1)
                assert hashlib.sha256(instruction.encode()).hexdigest()==f["branch_instruction_sha256"][arm]
                article_part,prior=prefix.split("\n\nINITIAL SUBMISSION\n",1)
                assert json.loads(prior)==load(parent)
                prefixes.append(article_part+prior)
            law=attested[block+"_"+arm]
            valid=initial[0] and law[0]
            mat=False
            if valid:
                gap=np.array(law[1])-initial[1];mean=float(np.mean(gap))
                assert abs(abs(mean)-blocks[block][arm]["gap_pp"])<1e-10
                mat=abs(mean)>4 and bool(np.min(np.sign(mean)*gap)>2)
            assert (valid,mat)==(blocks[block][arm]["both_valid"],blocks[block][arm]["material"])
        assert len(set(prefixes))<=1
        matches.append((blocks[block]["ordinary"]["material"],blocks[block]["alternative"]["material"]))
    pos=matches.count((False,True));neg=matches.count((True,False))
    exact=float(binomtest(pos,pos+neg,.5).pvalue) if pos+neg else 1.
    assert result["primary"]["exact_two_sided_p"]==exact
    cost=settled_costs(authors["calls"])
    assert abs(authors["accounted_usd"]-cost["accounted_usd"])<1e-7 and cost["accounted_usd"]<=f["cap_usd"]
    report={"article": "10.1371/journal.pone.0223189","registered_blocks":len(blocks),
            "source_artifacts_verified":verified_evidence,"saved_draws_recomputed":rows_checked,
            "unscored_draw_records":execution_errors,"matched_contrasts_recomputed":2*len(blocks),
            "paired_instructions_and_parent_identity_verified":True,
            "primary_verified":result["primary"],"cost":cost,"result_sha256":sha(HERE/"RESULTS.json")}
    output=HERE/"VERIFICATION.json"
    if output.exists():
        assert load(output)==report
    else:
        output.write_text(json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
