"""First target disclosure after public prediction seal; score all estimands and all frozen laws."""
import argparse
import json
import subprocess

import numpy as np

from reference_spiro import malawi, nhanes, summarize
from study import HERE, MARGINS, PRIVATE, SEEDS, USES, canonical, gain_bounds, named, read, score, seal, sha, status, target_grids


def verify_published(commit):
    repo=HERE.parents[2]/"github_virtual_cohort_2026-10-27"
    key="biomedical_research/virtual_cohort_system/work/"+HERE.name+"/PREDICTIONS.json"
    subprocess.run(["git","-C",str(repo),"merge-base","--is-ancestor",commit,"origin/main"],check=True)
    pub=subprocess.check_output(["git","-C",str(repo),"show",commit+":"+key])
    assert json.loads(pub)==read(HERE/"PREDICTIONS.json")


def diagnostic(frame,predictions):
    gs=target_grids(frame)
    out={}
    for label,rec in predictions["methods"].items():
        per=[]
        invalid=[]
        for draw in rec["draws"]:
            path=PRIVATE/"draws"/label/(str(draw["seed"])+".npz")
            assert sha(path)==draw["virtual_records_sha256"]
            with np.load(path,allow_pickle=False) as bundle:
                order=bundle["accepted_fvc_index"]
            per.append(score(gs,order))
            invalid.append(100*np.mean(np.concatenate([x>y[q] for (_,x,y),q in zip(gs,order,strict=True)])))
        out[label]={"values":named(np.mean(per,axis=0)),"invalid_pct":float(np.mean(invalid))}
    assert np.ptp([r["values"][USES[1]] for r in out.values()])<1e-9
    return out


def compare(pred,ref):
    methods=pred["methods"]
    effects={}
    for arm,control in [("M","physical_uniform"),("J","source_gaussian")]:
        laws=[methods[f"{arm}{i}"] for i in range(1,5) if f"{arm}{i}" in methods]
        if len(laws)!=4:
            effects[arm]=None
            continue
        effects[arm]={}
        for endpoint in USES:
            a=[methods[control]["values"][endpoint]]
            b=[x["values"][endpoint] for x in laws]
            actual=ref[endpoint]
            gain=gain_bounds(a,b,actual["estimate"],actual["ci"])
            assert max(abs(x) for x in [gain["point"],*gain["over_reference_interval"]])<=pred["upper_bounds_on_median_error_gain"][arm][endpoint]+1e-8
            effects[arm][endpoint]=gain
    classifications={}
    for k,record in methods.items():
        classifications[k]={u:{"absolute_error":abs(record["values"][u]-ref[u]["estimate"]),
                               "status":status(record["values"][u],ref[u]["ci"],MARGINS[u])} for u in USES}
    return {"error_reduction":effects,"intended_uses":classifications}


def main(commit):
    import trial
    from pathlib import Path
    assert Path(trial.__file__).resolve() == HERE / "trial.py"
    trial.guard()
    verify_published(commit)
    pred=read(HERE/"PREDICTIONS.json")
    assert pred["freeze"]==canonical(HERE/"FREEZE.json") and pred["authors"]==canonical(HERE/"AUTHORS.json")
    if (HERE/"RESULTS.json").exists():
        raise FileExistsError("Target results are already published")
    marker=HERE/"REFERENCE_OPEN.json"
    if not marker.exists():
        seal(marker,{"utc":trial.now(),"prediction_commit":commit,"prediction_hash":canonical(HERE/"PREDICTIONS.json"),
                     "scope":"First access to paired pre-dose target measurements for the registered analyses"})
    assert read(marker)["prediction_commit"]==commit and read(marker)["prediction_hash"]==canonical(HERE/"PREDICTIONS.json")
    refs,failures={},{}
    for name,load in (("US_NHANES",nhanes),("MW_ALHS_Y1",malawi)):
        try:
            frame,design,files=load()
            estimates,uncertainty=summarize(frame,design)
            sizes=frame.groupby("sex").size().to_dict()
            refs[name]={"n":len(frame),"n_by_sex":sizes,"measured_fev1_above_fvc":int((frame.x>frame.y).sum()),
                        "files":files,"estimates":estimates,"uncertainty":uncertainty,
                        "comparisons":compare(pred,estimates),"target_marginal_diagnostic":diagnostic(frame,pred)}
            print(name,len(frame),estimates,flush=True)
        except (ValueError,KeyError,AssertionError,RuntimeError,OSError,ImportError) as err:
            failures[name]=repr(err)[:550]
            print(name,"failed",failures[name],flush=True)
    complete=len(refs)==2 and all(x["comparisons"]["error_reduction"]["J"] is not None for x in refs.values())
    cs=[x["comparisons"]["error_reduction"]["J"][USES[0]] for x in refs.values()] if complete else []
    decision={"complete":complete,"threshold_pp":1.,
              "material_gain_at_both_points":all(g["point"]>=1 for g in cs) if complete else None,
              "material_gain_across_both_intervals":all(g["over_reference_interval"][0]>=1 for g in cs) if complete else None}
    seal(HERE/"RESULTS.json",{"utc":trial.now(),"prediction_commit":commit,"reference":refs,"failed_sites":failures,
                             "failed_authors":pred["failures"],"primary_test":decision,"use_margins":MARGINS})


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("prediction_commit")
    main(parser.parse_args().prediction_commit)
