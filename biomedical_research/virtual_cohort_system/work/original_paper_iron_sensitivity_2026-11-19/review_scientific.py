"""Independently check the harmonized execution and export scientific programs only."""
import json
from pathlib import Path
import numpy as np
import study
import interface_bridge as bridge
from verify import verify_sources


def main():
    r=study.ROOT
    raw=study.read(r/"SOURCE_RESULTS.json")
    res=study.read(r/"SCIENTIFIC_RESULTS.json")
    execution=study.read(r/"INTERFACE_CLOSURE.json")["laws"]
    calls=study.read(r/"CLOSURE.json")["all"]
    assert (r/"VERIFICATION.json").is_file() and study.read(r/"VERIFICATION.json")["passed"]
    assert res["time_utc"] < study.read(r/"REFERENCE_OPEN.json")["time_utc"]
    out=r/"laws";out.mkdir(exist_ok=True); bindings={}
    for name in calls:
        row=calls[name]
        if not row["sealed"]: continue
        art=study.read(study.CALLS/"calls"/name/"artifact.json")
        code=art["generator_py"]; params=art["model_spec"]
        a=execution[name]
        if a["binding"]=="one_nested_model":
            err=a["key_at_failure"]
            assert err not in params and err in params["model"] and err in code
            assert not any(v["status"]=="success" for v in study.read(r/"DRAW_CLOSURE.json")["runs"][name])
            params=params["model"]
            assert study.read(study.PRIVATE/"bridge_candidates"/name/"model_spec.json")=={"task":study.task(),"model":params}
        else:
            assert study.read(study.PRIVATE/"candidates"/name/"model_spec.json")=={"task":study.task(),"model":params}
        cp=out/(name+".py"); sp=out/(name+".json")
        cp.write_text(code,encoding="utf8",newline="\n")
        sp.write_text(json.dumps(params,indent=2,ensure_ascii=False),encoding="utf8",newline="\n")
        bindings[name]={"code_lf_sha256":study.lfsha(cp),"spec_lf_sha256":study.lfsha(sp),
                        "binding":a["binding"],"private_artifact_lf_sha256":row["artifact_lf_sha256"]}
    count=0
    for name,stat in res["laws"].items():
        if "spearman" in stat:
            verify_sources(bridge.scientific_rows(name,execution[name]),stat); count+=1
        if execution[name]["binding"]=="original": assert raw["laws"][name]==stat
    for pair in res["pairs"]:
        a=res["laws"].get(pair["primary"],{})
        z=res["laws"].get(pair["primary"]+"_"+pair["branch"],{})
        assert bool(a.get("tier2") and z.get("tier2"))==pair["both_tier2"]
        if "rank_gap" in pair:
            gap=abs(a["spearman"]-z["spearman"])
            m=1.96*np.sqrt(a["rank_mcse"]**2+z["rank_mcse"]**2)
            assert np.allclose([gap,m,max(0,gap-m)],[pair["rank_gap"],pair["mc_margin"],pair["mc_lower"]])
    study.write(r/"model_bindings.json",bindings)
    study.write(r/"SCIENTIFIC_VERIFICATION.json",{"time_utc":study.sandbox.now(),"passed":True,"laws_checked":count,
        "raw_and_scientific_separate":True,"scientific_results_closed_before_reference_open":True,
        "verification":"all scientific estimates and source screens reproduced with independent estimators; all code and input binding paths checked; all paired gaps and MC margins independently reproduced"})


if __name__=="__main__":main()
