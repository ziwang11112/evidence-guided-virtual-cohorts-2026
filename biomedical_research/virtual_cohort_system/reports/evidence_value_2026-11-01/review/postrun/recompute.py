"""Independent post-reveal arithmetic; no candidate/evaluator imports or sampling."""
from pathlib import Path
import csv
import hashlib
import json
import math
from datetime import datetime, timezone

UNIT = Path(__file__).resolve().parents[2]
PROJECT = UNIT.parents[1]
def read(path): return json.loads(path.read_text(encoding="utf-8"))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
numeric_checks = []
def check(name, actual, reported, tolerance=1e-12):
    delta = abs(actual-reported)
    numeric_checks.append({"field":name,"absolute_discrepancy":delta})
    assert math.isfinite(delta) and delta <= tolerance, (name,actual,reported,delta)
def average(values): return math.fsum(values)/len(values)
def ols(rows):
    x=[r[1] for r in rows]; y=[r[2] for r in rows]
    mx,my=average(x),average(y)
    xx=math.fsum((z-mx)**2 for z in x)
    slope=math.fsum((u-mx)*(v-my) for u,v in zip(x,y))/xx
    intercept=my-slope*mx
    return {"n":len(rows),"intercept":intercept,"slope":slope,
            "residual_rms":math.sqrt(average([(v-intercept-slope*u)**2 for u,v in zip(x,y)])),
            "x_mean":mx,"x_sd_population":math.sqrt(xx/len(rows))}
def source_recombine(rows):
    # Direct per-record weights, rather than recombining group raw second moments.
    counts=[sum(r[0]==k for r in rows) for k in (0,1)]
    weights=[.5/counts[r[0]] for r in rows]
    means=[math.fsum(w*r[j] for w,r in zip(weights,rows)) for j in range(3)]
    covariance=lambda j,k:math.fsum(w*(r[j]-means[j])*(r[k]-means[k]) for w,r in zip(weights,rows))
    return {"g_mean":means[0],"g_sd":math.sqrt(covariance(0,0)),
            "x_mean":means[1],"x_sd":math.sqrt(covariance(1,1)),
            "y_mean":means[2],"y_sd":math.sqrt(covariance(2,2)),
            "cov_g_x":covariance(0,1),"cov_g_y":covariance(0,2),"cov_x_y":covariance(1,2)}

report=read(UNIT/"evaluation/REPORT.json")
manifest=read(UNIT/"FREEZE_MANIFEST.json")
outputs=read(UNIT/"OUTPUTS.json")
reference=read(UNIT/"private/REFERENCE.json")
proof=read(UNIT/"review/private_math/RESULT.json")
law=read(UNIT/"private/LAW.json")
release=read(UNIT/"REVEAL_AUTHORIZATION.json")
assert release["slots"]==12 and release["successful"]==12
assert release["outputs_sha256"]==sha(UNIT/"OUTPUTS.json")==report["outputs_sha256"]
assert release["freeze_sha256"]==sha(UNIT/"FREEZE_MANIFEST.json")==report["freeze_sha256"]
assert report["private_reference_sha256"]==sha(UNIT/"private/REFERENCE.json")==proof["reference_sha256"]
assert report["revealed_reference"]==reference and proof["status"]=="passed"
assert report["world_aggregation"] is None and report["global_score"] is None
for relative,digest in manifest["files"].items(): assert sha(UNIT/relative)==digest,relative
for relative,digest in manifest["engine_files"].items(): assert sha(PROJECT/relative)==digest,relative
for arm,digest in manifest["candidate_freezes"].items():
    bundle=UNIT/"bundles"/arm
    assert sha(bundle/"candidates/initial/freeze.json")==digest
    frozen=read(bundle/"candidates/initial/freeze.json")
    for relative,committed in frozen["commitments"].items(): assert sha(bundle/relative)==committed,relative

results=[]
assert len(report["slots"])==len(outputs["slots"])==12
assert {(r["arm"],r["seed"]) for r in report["slots"]}=={(a,s) for a in "ABCD" for s in law["seeds"]}
for item in report["slots"]:
    arm,seed=item["arm"],item["seed"]
    label=f"{arm}_{seed}"
    execution=UNIT/"bundles"/arm/"executions"/f"s{seed}"
    receipt=read(execution/"execution.json")
    slot=next(q for q in outputs["slots"] if q["arm"]==arm and q["seed"]==seed)
    assert item["status"]==slot["status"]==receipt["status"]=="success"
    assert read(UNIT/"receipts"/f"{label}_result.json")==slot
    attempt=read(UNIT/"receipts"/f"{label}_attempt.json")
    assert attempt["arm"]==arm and attempt["seed"]==seed and attempt["freeze_sha256"]==report["freeze_sha256"]
    assert slot["execution_sha256"]==sha(execution/"execution.json")
    assert receipt["candidate_freeze_sha256"]==manifest["candidate_freezes"][arm]
    assert receipt["limits"]["seed"]==seed and receipt["runtime"]["backend"]=="wsl_bubblewrap"
    for relative,digest in receipt["files"].items(): assert sha(execution/relative)==digest,relative
    assert slot["generated_sha256"]==sha(execution/"output/generated.csv")
    with (execution/"output/generated.csv").open(newline="",encoding="utf-8") as handle:
        source=list(csv.DictReader(handle))
    assert len(source)==3000 and len({r["row_id"] for r in source})==3000
    rows=[(int(r["g"]),float(r["x"]),float(r["y"])) for r in source]
    assert all(g in (0,1) and math.isfinite(x) and math.isfinite(y) for g,x,y in rows)
    primary=ols(rows)
    groups={str(k):ols([r for r in rows if r[0]==k]) for k in (0,1)}
    a=item["analysis"]
    check(label+".n",len(rows),a["n"])
    check(label+".group_proportion",average([r[0] for r in rows]),a["group_proportion"])
    for key in ("n","intercept","slope","residual_rms"):
        check(label+".primary."+key,primary[key],a["primary"][key])
    for group,data in groups.items():
        assert data["n"]==a["group_counts"][group]
        for key,value in data.items(): check(label+".conditional."+group+"."+key,value,a["conditional"][group][key])
        check(label+".conditional."+group+".group_proportion",data["n"]/len(rows),a["conditional"][group]["group_proportion"])
    recombined=source_recombine(rows)
    for key,value in recombined.items(): check(label+".source."+key,value,a["source_equal_group_recombination"][key])
    right=sum(x>law["analysis"]["tail"]["x_cut"] and y>law["analysis"]["tail"]["y_cut"] for g,x,y in rows)/len(rows)
    left=sum(x<-law["analysis"]["tail"]["x_cut"] and y>law["analysis"]["tail"]["y_cut"] for g,x,y in rows)/len(rows)
    tail={"right_probability":right,"left_probability":left,"contrast":right-left}
    for key,value in tail.items(): check(label+".tail."+key,value,a["tail"][key])
    assert set(item["world_scores"])==set(law["analysis"]["world_policy"][arm])
    for world,score in item["world_scores"].items():
        ref=reference["worlds"][world]
        independent=proof["independent_worlds"][world]
        delta=primary["slope"]-independent["primary_slope"]
        check(label+world+".reference",independent["primary_slope"],score["primary_reference"])
        check(label+world+".primary_difference",delta,score["primary_difference"])
        check(label+world+".primary_absolute_difference",abs(delta),score["primary_absolute_difference"])
        assert score["primary_evidence_status"]==("implied_by_supplied_conditional_evidence" if arm in "CD" else "assumption_dependent")
        assert score["conditional_evidence_status"]==("supplied_conditional_evidence_compliance" if arm in "CD" else "unsupplied_hidden_reference_comparison")
        assert score["tail_evidence_status"]=="assumption_dependent_in_all_packets"
        for key,value in tail.items():
            truth=independent["tail"][key]
            check(label+world+".tail_reference."+key,truth,score["tail_reference"][key])
            check(label+world+".tail_difference."+key,value-truth,score["tail_differences"][key])
            check(label+world+".tail_absolute_difference."+key,abs(value-truth),score["tail_absolute_differences"][key])
        mapping={"intercept":"intercept","slope":"slope","residual_rms":"residual_sd","x_mean":"x_mean","x_sd_population":"x_sd"}
        for group,data in groups.items():
            comparison=score["conditional_reference_comparison"][group]
            assert comparison["computed"] and comparison["reference"]==ref["conditional"][group]
            for key,refkey in mapping.items():
                diff=data[key]-ref["conditional"][group][refkey]
                check(label+world+group+".difference."+key,diff,comparison["differences"][key])
                check(label+world+group+".absolute_difference."+key,abs(diff),comparison["absolute_differences"][key])
    if arm=="A": assert item["source_packet_compliance"] is None
    else:
        for key,value in recombined.items():
            delta=value-reference["source"][key]
            check(label+".source_difference."+key,delta,item["source_packet_compliance"]["differences"][key])
            check(label+".source_absolute_difference."+key,abs(delta),item["source_packet_compliance"]["absolute_differences"][key])
    results.append({"arm":arm,"seed":seed,"primary":primary,"conditional":groups,"source_equal_group_recombination":recombined,"tail":tail})

response=[]
for seed in law["seeds"]:
    values={q["arm"]:q["primary"]["slope"] for q in results if q["seed"]==seed}
    contrast=values["C"]-values["D"]
    recorded=next(q for q in report["responsiveness"] if q["seed"]==seed)
    for key,value in {"C_minus_D_primary":contrast,"reference_contrast":.7,"difference_from_reference":contrast-.7,"absolute_difference_from_reference":abs(contrast-.7)}.items(): check(f"response.{seed}.{key}",value,recorded[key])
    truth_plus=proof["independent_worlds"]["plus_normal"]["primary_slope"]
    truth_minus=proof["independent_worlds"]["minus_normal"]["primary_slope"]
    response.append({"seed":seed,"correct_counterfactual_signs":values["C"]>0 and values["D"]<0,"C_error_lower_than_B":abs(values["C"]-truth_plus)<abs(values["B"]-truth_plus),"D_error_lower_than_B":abs(values["D"]-truth_minus)<abs(values["B"]-truth_minus),"C_minus_D":contrast})
result={"status":"passed","created_utc":datetime.now(timezone.utc).isoformat(),"reviewer":"/root/ev_candidate_review","primary_report_sha256":sha(UNIT/"evaluation/REPORT.json"),"script_sha256":sha(Path(__file__)),"reference_proof_sha256":sha(UNIT/"review/private_math/RESULT.json"),"frozen_and_execution_hashes":"all_matched","tables":len(results),"rows_per_table":3000,"numeric_fields_compared":len(numeric_checks),"maximum_absolute_discrepancy":max(q["absolute_discrepancy"] for q in numeric_checks),"numerical_agreement_tolerance":1e-12,"scientific_equivalence_tolerance":None,"discrepancies_above_tolerance":[],"prespecified_response":response,"favorable_concrete_translation_example":all(q["correct_counterfactual_signs"] and q["C_error_lower_than_B"] and q["D_error_lower_than_B"] for q in response),"independent_aggregate_results":results,"scope":"CSV and math.fsum centered scalar arithmetic, direct per-record source reweighting and explicit event counts. No generator or primary evaluator imported, run, revised or reused. Existing independently calculated reference proof reused without rerunning it.","interpretation":["This demonstrates conditional-evidence responsiveness and algebraic translation for this constructed problem, not novel unknown biological relations.","One author per packet confounds evidence condition with constructor variation; three seeds condition on each fixed program.","The normal and standardized-t3 laws satisfy the same evidence but differ in tails; a match to one law does not identify its scientific correctness.","There is no evidence of clinical transfer, universal superiority, feedback benefit or recovery of individual truth from this pilot."]}
with (Path(__file__).parent/"RESULT.json").open("x",encoding="utf-8",newline="\n") as handle:
    json.dump(result,handle,indent=2,allow_nan=False);handle.write("\n")
print(json.dumps({key:result[key] for key in ("status","tables","numeric_fields_compared","maximum_absolute_discrepancy","favorable_concrete_translation_example")},indent=2))
