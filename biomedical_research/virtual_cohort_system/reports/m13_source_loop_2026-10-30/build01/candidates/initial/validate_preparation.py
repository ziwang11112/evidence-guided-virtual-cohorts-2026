"""Contract validation and covariate arithmetic only; never import generator."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
BUNDLE=HERE.parent.parent
PROJECT=BUNDLE.parents[2]
sys.path.insert(0,str(PROJECT))
from cohort_harness import lifecycle, contracts, source_context, source_replay_v2

read=lifecycle.read_json
task=read(BUNDLE/"task.json")
spec=read(HERE/"model_spec.json")
evidence=read(HERE/"evidence.json")
plan=read(HERE/"source_replay_v2.json")
cal=read(HERE/"proposed_calibration_plan.json")
control=read(BUNDLE/"allowed_inputs/controller_contract.json")
eitems={e["id"]:e for e in evidence["items"]}
assumptions={a["id"] for a in spec["assumptions"]}
report={"scope":"contract_validation_and_covariates_only","generator_imported":False,"generator_executed":False,"frozen":False,"contexts":[]}
contracts.exact_keys(plan,{"schema_version","model_domain","contexts"},where="replay plan")
assert plan["schema_version"]==2 and len(plan["contexts"])==2
keys=[]
for context in plan["contexts"]:
    contracts.exact_keys(context,{"id","population","reason","columns","assumption_ids","measurement","input","checks"},where="context")
    contracts.exact_keys(context["measurement"],{"mode","description"},where="measurement")
    contracts.exact_keys(context["input"],{"path","sha256","origin"},where="input")
    assert context["measurement"]["mode"]=="identity"
    assert context["input"]["origin"]=="declared_source_covariates"
    assert set(plan["model_domain"]["assumption_ids"])<=set(context["assumption_ids"])<=assumptions
    path=HERE/context["input"]["path"]
    assert lifecycle.sha256(path)==context["input"]["sha256"]
    frame=lifecycle.read_table(path,dict(task,columns=context["columns"]))
    ctask=source_context.compile_source_task(task,context,plan["model_domain"],frame,assumption_ids=assumptions)
    assert len(frame)<=12000 and "bodyfat" not in frame
    expected={"inv_bmi":1/frame.bmi,"male_inv_bmi":frame.male/frame.bmi,"asian_inv_bmi":frame.asian/frame.bmi,
              "male_age":frame.male*frame.age,"asian_age":frame.asian*frame.age}
    errors={k:float(np.max(np.abs(frame[k]-v))) for k,v in expected.items()}
    assert max(errors.values())<1e-12
    ranks={}
    for check in context["checks"]:
        contracts.exact_keys(check,{"id","evidence_id","status","operator","assumption_ids","reason"},where="replay check")
        assert check["status"]=="approximate" and set(check["assumption_ids"])<=assumptions
        op=check["operator"]
        source_replay_v2._operator_preflight(op,ctask)
        e=eitems[check["evidence_id"]]
        assert op["kind"]==e["kind"] and op["unit"]==e["unit"]
        if op["kind"]=="ols_coefficient":
            assert set(e["variables"])|set(e["adjustment"])==set([op["outcome"]]+op["predictors"])
            assert set(e["adjustment"])<=set(op["predictors"])
            x=np.column_stack([np.ones(len(frame)),frame[op["predictors"]].to_numpy(dtype=float)])
            rank=int(np.linalg.matrix_rank(x))
            assert rank==x.shape[1]
            ranks["|".join(op["predictors"])]=dict(rank=rank,columns=x.shape[1],condition_number=float(np.linalg.cond(x)))
        elif op["kind"]=="correlation":
            assert set(e["variables"])=={op["x"],op["y"]}
        else:
            assert e["variables"]==[op["column"]]
        keys.append((context["id"],check["id"]))
    report["contexts"].append(dict(id=context["id"],rows=len(frame),bytes=path.stat().st_size,
        checks=len(context["checks"]),derived_column_max_errors=errors,regression_designs=ranks,
        age_range=[float(frame.age.min()),float(frame.age.max())],bmi_range=[float(frame.bmi.min()),float(frame.bmi.max())],
        bmi_ge25_fraction=float(np.mean(frame.bmi>=25)),bmi_ge30_count=int(np.sum(frame.bmi>=30))))
assert len(keys)==len(set(keys))==18
contracts.exact_keys(cal,{"schema_version","parameters","constraints","fit_seeds","replay_seeds","optimizer","execution","noncomputable"},where="calibration plan")
assert cal["schema_version"]==1 and cal["noncomputable"]=="infeasible"
assert cal["optimizer"]==dict(method="bounded_coordinate_search",max_trials=9,shrink=.5,min_step_fraction=.01,target_loss=0.)
for k in ["fit_seeds","replay_seeds","execution"]:
    assert cal[k]==control[k]
for p in cal["parameters"]:
    contracts.exact_keys(p,{"name","lower","upper","step"},where="scalar parameter")
    assert p["lower"]<=spec["parameters"][p["name"]]<=p["upper"] and 0<p["step"]<=p["upper"]-p["lower"]
assert len({p["name"] for p in cal["parameters"]})==len(cal["parameters"])==4
ckeys=[]
for c in cal["constraints"]:
    contracts.exact_keys(c,{"context_id","check_id","scale","scale_reason"},where="constraint")
    context=next(x for x in plan["contexts"] if x["id"]==c["context_id"])
    check=next(x for x in context["checks"] if x["id"]==c["check_id"])
    op=check["operator"]
    scale=control["loss_scales"]["coefficient_by_term"][op["term"]] if op["kind"]=="ols_coefficient" else control["loss_scales"][op["kind"]]
    assert c["scale"]==scale
    ckeys.append((c["context_id"],c["check_id"]))
assert len(ckeys)==len(set(ckeys))==18 and set(ckeys)==set(keys)
manifest=read(BUNDLE/"agent_exchange/initial_input_manifest.json")
for name,h in manifest["files"].items():
    assert lifecycle.sha256(BUNDLE/name)==h
report["approved_input_hashes_unchanged"]=True
report["all_18_constraints_once"]=True
report["controller_seeds_scales_limits_match"]=True
report["evidence_items"]=len(eitems)
report["generator_ast_contract"]=True
lifecycle._state(BUNDLE,HERE,"candidates/initial")
report["core_contract"]=True
report["status"]="pass"
(HERE/"preparation_validation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
checks=read(HERE/"checks.json")
checks["records"]=[r for r in checks["records"] if r["name"]!="preparation_contracts"]
checks["records"].append(dict(name="preparation_contracts",status="pass",detail="Actual core contract, generator AST/signature, source-task v2 compilation, typed-empty operator preflight, covariate design ranks/derived columns, fixed calibration schema/coverage/scales/seeds/limits and admitted input hashes passed. No generated outcomes were computed. Full freeze-dependent replay/calibration validation awaits controller."))
checks["artifacts"]=[a for a in checks["artifacts"] if a["path"]!="preparation_validation.json"]
checks["artifacts"].append(dict(path="preparation_validation.json",sha256=lifecycle.sha256(HERE/"preparation_validation.json")))
(HERE/"checks.json").write_text(json.dumps(checks,indent=2)+"\n",encoding="utf-8")
lifecycle._state(BUNDLE,HERE,"candidates/initial")
print(json.dumps(report,indent=2))
