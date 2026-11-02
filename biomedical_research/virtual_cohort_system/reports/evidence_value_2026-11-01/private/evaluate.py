"""Private artificial-fixture evaluator; never generates rows.
Read/reveal is gated on all four frozen candidates and all twelve finished slots.
Do not provide this file or private law/reference to constructors.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT.parents[1]))
from cohort_harness import lifecycle, execution, contracts

ARMS=("A","B","C","D")
SEEDS=(18101,18103,18107)

def read(path):
    return lifecycle.read_json(path)

def sha(path):
    return lifecycle.sha256(path)

def write_new(path,value):
    with path.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False)
        stream.write("\n")

def fit(x,y,minimum):
    if len(y)<minimum:return {"status":"unavailable","reason":"insufficient_rows","n":len(y)}
    design=np.column_stack((np.ones(len(y)),x))
    if np.linalg.matrix_rank(design)!=2:return {"status":"unavailable","reason":"rank_deficient","n":len(y)}
    beta=np.linalg.lstsq(design,y,rcond=None)[0]
    residual=y-design@beta
    return {"status":"computed","n":len(y),"intercept":float(beta[0]),"slope":float(beta[1]),
            "residual_rms":float(np.sqrt(np.mean(residual**2))),
            "residual_denominator":"n, empirical projection residual RMS; not an SE or calibrated CI"}

def analyze(frame,config):
    g=frame["g"].to_numpy(dtype=int)
    x=frame["x"].to_numpy(dtype=float);y=frame["y"].to_numpy(dtype=float)
    analysis=config["analysis"]; tail=analysis["tail"]
    groups={}; first=[];second=[]
    for value in (0,1):
        selected=g==value; xx=x[selected];yy=y[selected]
        row=fit(xx,yy,analysis["minimum_group_for_conditional"])
        row.update({"x_mean":float(np.mean(xx)) if len(xx) else None,
                    "x_sd_population":float(np.std(xx,ddof=0)) if len(xx) else None,
                    "group_proportion":float(np.mean(selected))})
        groups[str(value)]=row
        if len(xx):
            z=np.column_stack((g[selected],xx,yy))
            first.append(np.mean(z,axis=0));second.append(z.T@z/len(z))
    source=None
    if len(first)==2 and all(z["status"]=="computed" for z in groups.values()):
        mean=(first[0]+first[1])/2
        covariance=(second[0]+second[1])/2-np.outer(mean,mean)
        source={v+"_mean":float(mean[j]) for j,v in enumerate(("g","x","y"))}
        source.update({v+"_sd":float(np.sqrt(max(0,covariance[j,j]))) for j,v in enumerate(("g","x","y"))})
        source.update({"cov_g_x":float(covariance[0,1]),"cov_g_y":float(covariance[0,2]),"cov_x_y":float(covariance[1,2])})
    right=float(np.mean((x>tail["x_cut"]) & (y>tail["y_cut"])))
    left=float(np.mean((x < -tail["x_cut"]) & (y>tail["y_cut"])))
    return {"n":len(frame),"group_counts":{str(v):int(np.sum(g==v)) for v in (0,1)},
        "group_proportion":float(np.mean(g)),"primary":fit(x,y,analysis["minimum_total_for_ols"]),
        "conditional":groups,"source_equal_group_recombination":source,
        "tail":{"right_probability":right,"left_probability":left,"contrast":right-left},
        "uncertainty":"No inference from synthetic row count; seed spread is conditional Monte Carlo variability."}

def scores(arm,actual,config,reference):
    output={}
    for name in config["analysis"]["world_policy"][arm]:
        expected=reference["worlds"][name]; groups={}
        for g in ("0","1"):
            found=actual["conditional"][g];truth=expected["conditional"][g]
            groups[g]={"reference":truth,"computed":found["status"]=="computed",
                "differences":{key:found[key]-truth[target] for key,target in
                    (("intercept","intercept"),("slope","slope"),("residual_rms","residual_sd"),
                     ("x_mean","x_mean"),("x_sd_population","x_sd"))}
                    if found["status"]=="computed" else None}
        output[name]={"primary_reference":expected["primary_slope"],
            "primary_difference":actual["primary"]["slope"]-expected["primary_slope"]
                if actual["primary"]["status"]=="computed" else None,
            "primary_evidence_status":"implied_by_supplied_conditional_evidence" if arm in {"C","D"} else "assumption_dependent",
            "conditional_reference_comparison":groups,
            "conditional_evidence_status":"supplied_conditional_evidence_compliance" if arm in {"C","D"} else "unsupplied_hidden_reference_comparison",
            "tail_evidence_status":"assumption_dependent_in_all_packets",
            "tail_reference":expected["tail"],
            "tail_differences":{k:actual["tail"][k]-expected["tail"][k] for k in expected["tail"]}}
        row=output[name]
        row["primary_absolute_difference"]=abs(row["primary_difference"]) if row["primary_difference"] is not None else None
        row["tail_absolute_differences"]={k:abs(v) for k,v in row["tail_differences"].items()}
        for group in groups.values():
            group["absolute_differences"]={k:abs(v) for k,v in group["differences"].items()} if group["computed"] else None
    return output

def gate():
    commitment=read(ROOT/"CUSTODY_COMMITMENT.json")
    for name,digest in commitment["commitments"].items():
        assert sha(ROOT/name)==digest,name
    freeze=read(ROOT/"FREEZE_MANIFEST.json")
    assert freeze["maximum_tables"]==12 and freeze["seeds"]==list(SEEDS)
    assert set(freeze["candidate_freezes"])==set(ARMS)
    for name,digest in freeze["files"].items():
        assert sha(ROOT/name)==digest,name
    for name,digest in freeze["engine_files"].items():
        assert sha(ROOT.parents[1]/name)==digest,name
    for arm in ARMS:
        bundle=ROOT/"bundles"/arm
        lifecycle.verify_candidate(bundle,"candidates/initial")
        assert sha(bundle/"candidates/initial/freeze.json")==freeze["candidate_freezes"][arm]
    started=read(ROOT/"EXECUTION_STARTED.json")
    assert started["freeze_sha256"]==sha(ROOT/"FREEZE_MANIFEST.json") and started["reserved_table_slots"]==12
    outputs=read(ROOT/"OUTPUTS.json")
    assert outputs["freeze_sha256"]==sha(ROOT/"FREEZE_MANIFEST.json")
    slots=outputs["slots"]
    assert len(slots)==12 and {(r["arm"],r["seed"]) for r in slots}=={(a,s) for a in ARMS for s in SEEDS}
    assert all(r["status"] in {"success","failed","timeout"} for r in slots)
    for row in slots:
        stem=f'{row["arm"]}_{row["seed"]}'
        attempt=read(ROOT/"receipts"/(stem+"_attempt.json"))
        assert attempt=={"arm":row["arm"],"seed":row["seed"],"run_id":"s"+str(row["seed"]),
                         "freeze_sha256":sha(ROOT/"FREEZE_MANIFEST.json")}
        assert read(ROOT/"receipts"/(stem+"_result.json"))==row
    # The immutable custodian law, reference and evaluator must be admitted before output.
    assert all(freeze["files"].get(name)==digest for name,digest in commitment["private_files"].items())
    return slots,commitment

def evaluate():
    slots,commitment=gate()
    destination=ROOT/"evaluation"
    destination.mkdir(exist_ok=False)  # One reservation; no silent retry.
    write_new(destination/"REQUEST.json",{
        "created_utc":datetime.now(timezone.utc).isoformat(),"custody_sha256":sha(ROOT/"CUSTODY_COMMITMENT.json"),
        "freeze_sha256":sha(ROOT/"FREEZE_MANIFEST.json"),"outputs_sha256":sha(ROOT/"OUTPUTS.json"),
        "evaluator_sha256":sha(Path(__file__))})
    try:
        config=read(HERE/"LAW.json");reference=read(HERE/"REFERENCE.json")
        results=[]
        for slot in slots:
            row={"arm":slot["arm"],"seed":slot["seed"],"status":slot["status"],
                 "analysis":None,"world_scores":None,"source_packet_compliance":None}
            if slot["status"]=="success":
                bundle=ROOT/"bundles"/slot["arm"];run="s"+str(slot["seed"])
                receipt=execution.verify_execution(bundle,run)
                assert receipt["status"]=="success" and sha(bundle/"executions"/run/"execution.json")==slot["execution_sha256"]
                output=bundle/"executions"/run/"output/generated.csv"
                assert sha(output)==slot["generated_sha256"]
                task=read(bundle/"task.json")
                frame=lifecycle.read_table(output,task,output=True)
                contracts.validate_output(None,frame,task)
                actual=analyze(frame,config)
                row["analysis"]=actual;row["world_scores"]=scores(slot["arm"],actual,config,reference)
                if slot["arm"]!="A" and actual["source_equal_group_recombination"] is not None:
                    row["source_packet_compliance"]={
                        "method":"fixed equal-group recombination, not raw target moments or generated-source replay",
                        "differences":{k:actual["source_equal_group_recombination"][k]-v for k,v in reference["source"].items()}}
                    row["source_packet_compliance"]["absolute_differences"]={k:abs(v) for k,v in row["source_packet_compliance"]["differences"].items()}
            else:
                row["reason"]="Reserved execution failed; no replacement or favorable-world selection."
            results.append(row)
        responsiveness=[]
        for seed in SEEDS:
            plus=next(r for r in results if r["arm"]=="C" and r["seed"]==seed)
            minus=next(r for r in results if r["arm"]=="D" and r["seed"]==seed)
            computable=all(r["analysis"] is not None and r["analysis"]["primary"]["status"]=="computed" for r in (plus,minus))
            difference=plus["analysis"]["primary"]["slope"]-minus["analysis"]["primary"]["slope"] if computable else None
            responsiveness.append({"seed":seed,"computed":computable,"C_minus_D_primary":difference,
                "reference_contrast":reference["primary_plus_minus_contrast"],
                "difference_from_reference":difference-reference["primary_plus_minus_contrast"] if computable else None,
                "absolute_difference_from_reference":abs(difference-reference["primary_plus_minus_contrast"]) if computable else None,
                "qualification":"Same numeric seed does not imply common random innovations across different programs."})
        report={"schema_version":1,"status":"complete","custody_sha256":sha(ROOT/"CUSTODY_COMMITMENT.json"),
            "freeze_sha256":sha(ROOT/"FREEZE_MANIFEST.json"),"outputs_sha256":sha(ROOT/"OUTPUTS.json"),
            "private_reference_sha256":sha(HERE/"REFERENCE.json"),"slots":results,
            "responsiveness":responsiveness,"revealed_reference":reference,
            "world_aggregation":None,"global_score":None,
            "limitations":["Artificial translation/compliance check, not new biology or clinical validation.",
                "One constructor per packet cannot estimate a general causal evidence-value effect.",
                "T0/T1 outputs are compared to all compatible sign/error worlds without probability weights.",
                "T2 output compares only to its sign's compatible normal/t3 worlds; tail truth is not identified by its packet.",
                "Primary T2 projection is algebraically implied; call it a translation check, not a held-out discovery.",
                "Student t3 has infinite fourth moment; no calibrated residual-variance uncertainty is asserted.",
                "No new generator, trial table, source feedback, model repair or post-reveal tuning is authorized."]}
        write_new(destination/"REPORT.json",report)
        return {"status":"complete","slots":12,"report":"evaluation/REPORT.json","new_rows_generated":0}
    except Exception as error:
        write_new(destination/"FAILURE.json",{"type":type(error).__name__,"message":str(error)})
        raise

if __name__=="__main__":
    print(json.dumps(evaluate()))

