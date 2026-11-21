"""Open the targets only after the committed predictions, then score every frozen arm."""
import argparse
import subprocess
import numpy as np
from science import (HERE, PRIVATE, CELLS, USES, SEEDS, MARGINS, canonical, gain_bounds, independent, named,
                     read, rule_permutation, score_order, seal, separate_grids, sha, source_grids, status)
import reference


def check_public(commit):
    repo=HERE.parents[2]/"github_virtual_cohort_2026-10-27"
    key="biomedical_research/virtual_cohort_system/work/"+HERE.name+"/PREDICTIONS.json"
    if subprocess.run(["git","-C",str(repo),"merge-base","--is-ancestor",commit,"origin/main"]).returncode:
        raise ValueError("Prediction commit is not on fetched public main")
    b=subprocess.check_output(["git","-C",str(repo),"show",commit+":"+key])
    import json
    assert json.loads(b)==read(HERE/"PREDICTIONS.json")


def diagnostic(grids,pred):
    base=source_grids()
    out={"independent":named(independent(grids))}
    out["ratio_rule"]=named(np.mean([score_order(grids,rule_permutation(base,s)[0]) for s in SEEDS],axis=0))
    for k,rec in pred["methods"].items():
        if "draws" not in rec:continue
        scores=[]
        for run in rec["draws"]:
            path=PRIVATE/"runs"/k/str(run["seed"])/"perm.npy"
            assert sha(path)==run["permutation_sha256"]
            scores.append(score_order(grids,np.load(path,allow_pickle=False)))
        out[k]=named(np.mean(scores,axis=0))
    assert np.ptp([v["mean_both_kg"] for v in out.values()])<1e-9
    return out


def summarize_countries(pred,reference_rows):
    methods=pred["methods"]
    results={}
    for site,ref in reference_rows.items():
        target=ref["estimates"]
        use={k:{m:{"error":abs(v["values"][m]-target[m]["estimate"]),
                   "status":status(v["values"][m],target[m]["ci"],MARGINS[m])} for m in USES}
             for k,v in methods.items()}
        values={k:r["values"][USES[0]] for k,r in methods.items()}
        m=[values[k] for k in values if k.startswith("M")]
        j=[values[k] for k in values if k.startswith("J")]
        actual=target[USES[0]]
        def compare(a,b):
            return gain_bounds(a,b,actual["estimate"],actual["ci"]) if len(a) and len(b) else None
        contrasts={"independent_to_M":compare([values["independent"]],m),
                   "M_to_J":compare(m,j),"ratio_rule_to_J":compare([values["ratio_rule"]],j)}
        results[site]={"fixed_prediction_comparisons":use,"primary_complete":len(m)==4,"contrasts":contrasts}
    return results


def main(commit):
    from trial import guard,now
    guard()
    check_public(commit)
    pred=read(HERE/"PREDICTIONS.json")
    assert pred["freeze"]==canonical(HERE/"FREEZE.json") and pred["authors"]==canonical(HERE/"AUTHORS.json")
    if (HERE/"RESULTS.json").exists():raise FileExistsError("References already scored")
    marker=HERE/"REFERENCE_OPEN.json"
    if not marker.exists():
        seal(marker,{"utc":now(),"prediction_commit":commit,"predictions":canonical(HERE/"PREDICTIONS.json"),
                     "planned_sites":list(reference.STUDIES),"scope":"First permitted access to paired grip analyses"})
    assert read(marker)["prediction_commit"]==commit and read(marker)["predictions"]==canonical(HERE/"PREDICTIONS.json")
    refs={};site_errors={}
    for name,loader in reference.STUDIES.items():
        try:
            frame,design,qc=loader()
            values,intervals,df=reference.estimate(frame,design)
            arr=tuple(frame[c].to_numpy() for c in ("cell","r","l"))
            grids=separate_grids(arr,frame.w.to_numpy())
            refs[name]={"qc":qc,"design_df":df,"estimates":{k:{"estimate":float(v),"ci":ci.tolist()}
                              for k,v,ci in zip(USES,values,intervals,strict=True)},
                        "diagnostic_using_separate_target_marginals":diagnostic(grids,pred)}
            print(name,qc["eligible_bilateral"],values.round(3),flush=True)
        except (AssertionError,ValueError,KeyError,OSError,RuntimeError) as e:
            site_errors[name]=repr(e)
            print(name,"FAILED",repr(e),flush=True)
    results=summarize_countries(pred,refs)
    primary_sites=["US_NHANES","ZA_HAALSI"]
    complete=all(k in results and results[k]["primary_complete"] for k in primary_sites)
    rule={"complete":complete,"material_gain_both_points":None,"material_gain_over_both_intervals":None}
    if complete:
        cs=[results[k]["contrasts"]["independent_to_M"] for k in primary_sites]
        rule.update(material_gain_both_points=all(z["point"]>=1 for z in cs),
                    material_gain_over_both_intervals=all(z["over_reference_interval"][0]>=1 for z in cs))
    seal(HERE/"RESULTS.json",{"utc":now(),"predictions_commit":commit,"reference":refs,"reference_failures":site_errors,
          "comparisons":results,"primary":rule,"margins":MARGINS,"author_failures":pred["failures"]})


if __name__=="__main__":
    cli=argparse.ArgumentParser();cli.add_argument("commit");main(cli.parse_args().commit)
