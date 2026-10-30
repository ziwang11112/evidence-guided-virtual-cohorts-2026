"""Controller for source-only M11 replay; biomedical code runs only in supplied adapter."""
from __future__ import annotations
import argparse, copy, hashlib, json, shutil, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
from cohort_harness.lifecycle import freeze_candidate, verify_candidate
from cohort_harness.source_replay import run_source_replay, verify_source_replay
from cohort_harness.source_replay import _check_metadata, _input_task

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
    Path(p).parent.mkdir(exist_ok=True,parents=True)
    Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8')
PLAN=read(HERE/'source_plan.json')
RUNTIME=read(ROOT/'work/m2-runtime-config.json')

def log(bundle,event,**kw):
    x={'event':event,'time_unix':time.time(),**kw}
    with (bundle/'source_controller_status.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(x,allow_nan=False)+'\n')
    print(json.dumps(x,allow_nan=False),flush=True)

def precheck(bundle,cand):
    ev={x['id']:x for x in read(cand/'evidence.json')['items']}
    ass={x['id'] for x in read(cand/'model_spec.json')['assumptions']}
    for context in read(cand/'source_replay.json')['contexts']:
        for check in context['checks']:_check_metadata(check,ev,ass,context['assumption_ids'])
        _input_task(cand,context,read(bundle/'task.json'),20000000)

def frozen(bundle,name,parent=None,revision=None):
    cand=bundle/'candidates'/name
    precheck(bundle,cand)
    if (cand/'freeze.json').exists():r=verify_candidate(bundle,cand)
    else:r=freeze_candidate(bundle,cand,parent_receipt=None if parent is None else f'candidates/{parent}/freeze.json',revision=revision)
    log(bundle,'frozen_verified',candidate=name,freeze_sha256=sha(cand/'freeze.json'),route=r['route'])

def replay(bundle,name,seed):
    rid=f'{name}_{seed}'
    rp=bundle/'source_replays'/rid/'replay.json'
    if rp.exists():r=verify_source_replay(bundle,rid,candidate=f'candidates/{name}')
    else:r=run_source_replay(bundle,f'candidates/{name}',rid,seed,runtime=RUNTIME,timeout_seconds=60,memory_mb=1024,output_bytes=20000000,log_bytes=100000)
    log(bundle,'replay_verified',candidate=name,seed=seed,status=r['status'],contexts=[{'id':x['id'],'status':x['status'],'checks':len(x.get('checks',[]))} for x in r['contexts']])
    if r['status']!='success':raise RuntimeError('Retained failed source replay; no local fallback')
    return r

def initial(bundle):
    assert sha(HERE/'source_plan.json')==sha(bundle/'candidates/initial/source_plan.json'),'Source plan differs from candidate plan'
    frozen(bundle,'initial')
    for seed in PLAN['source_seeds']:replay(bundle,'initial',seed)

def calibrate(bundle,family):
    parent=bundle/'candidates/initial';verify_candidate(bundle,parent)
    assert sha(HERE/'source_plan.json')==sha(parent/'source_plan.json'),'Source plan differs from frozen initial plan'
    original=read(parent/'model_spec.json');key='location_pct' if family=='ha' else 'location_by_sex'
    reports={seed:verify_source_replay(bundle,f'initial_{seed}',candidate='candidates/initial') for seed in PLAN['source_seeds']}
    assert all(r['status']=='success' for r in reports.values())
    result={}
    for scenario in PLAN['scenarios']:
        sid=scenario['id'];name='calibrated_'+sid;cand=bundle/'candidates'/name
        if cand.exists():
            verify_candidate(bundle,cand);result[sid]=read(cand/'calibration.json');continue
        frames=[];inputs=[]
        for seed,report in reports.items():
            context=next(x for x in report['contexts'] if x['id']==sid)
            assert context['status']=='success' and all(x.get('generation_link_verified') is True for x in context['checks'])
            p=bundle/f'source_replays/initial_{seed}/contexts/{sid}/bundle/executions/replay/output/generated.csv'
            digest=sha(p)
            assert all(x['generated_sha256']==digest for x in context['checks'])
            d=pd.read_csv(p,usecols=['sex','hba1c_pct'],float_precision='round_trip');assert len(d)==PLAN['source_n']
            frames.append(d);inputs.append({'seed':seed,'output_path':p.relative_to(bundle).as_posix(),'sha256':digest,'replay_sha256':sha(bundle/f'source_replays/initial_{seed}/replay.json'),'n':len(d)})
        pooled=pd.concat(frames,ignore_index=True)
        cal={'schema_version':1,'scope':'source_only_derived_calibration','family':family,'scenario':sid,'source_plan_sha256':sha(HERE/'source_plan.json'),'initial_freeze_sha256':sha(parent/'freeze.json'),'generator_sha256':sha(parent/'generator.py'),'initial_model_spec_sha256':sha(parent/'model_spec.json'),'source_context_sha256':sha(parent/f'source_contexts/{sid}.csv'),'source_seeds':PLAN['source_seeds'],'inputs':inputs,'estimator':'Pool verified rows across all3seeds withinsex; numpy quantile(method=linear,q=.5), Hyndman-Fan type7. Not an average of seed medians.','operation':'new_location=old_location+reported_source_median-pooled_initial_source_median','not_harness_native_pooled_operator':True,'sex':{},'target_outcomes_or_results_used':False}
        spec=copy.deepcopy(original)
        for sex,m in PLAN['calibration']['targets_pct'].items():
            y=pooled.loc[pooled.sex.eq(sex),'hba1c_pct'].to_numpy();assert np.isfinite(y).all()
            sy=np.sort(y);n=len(y);central=[float(sy[(n-1)//2]),float(sy[n//2])]
            if family=='ha':assert 3<central[0]<=central[1]<20,'Clipped central statistics do not identify latent median'
            q=float(np.quantile(y,.5,method='linear'));old=original['parameters'][key][sex];delta=m-q
            spec['parameters'][key][sex]=old+delta
            cal['sex'][sex]={'n_pooled':n,'central_order_statistics':central,'published_median':m,'initial_pooled_median':q,'offset':delta,'initial_location':old,'calibrated_location':old+delta}
        for k in original['parameters']:
            if k!=key:assert original['parameters'][k]==spec['parameters'][k]
        for a in spec['assumptions']:
            if a['id'] in {'A_location','Alocation'}:a['description']=f'Conditional reference locations at age49.5 and BMI27 calibrated by the fixed additive source-median rule in scenario {sid}; see calibration.json. This is conditional on approximated source covariates and inherited residual law, not an identified source intercept.'
            if a['id']=='M11_calibration':a['description']=f'Applied fixed source-only pooled-median offset to each sex location using scenario {sid} and all3source seeds. Only locations changed; no target information. Fitted source median agreement is mechanical, not independent validation.'
        pr=spec['parameter_provenance'][key]
        pr['assumption_ids']=list(dict.fromkeys(pr['assumption_ids']+['M11_calibration','M11_source_X','M11_BMI','M11_dependence','M11_support']))
        pr['derivation']=f'Initial inherited location + published SHIP-Trend marginal median - pooled verified initial source median, scenario {sid}, seeds94101/94102/94103; all inputs and signed offsets bound in calibration.json.'
        shutil.copytree(parent,cand,ignore=shutil.ignore_patterns('freeze.json'))
        write(cand/'model_spec.json',spec);write(cand/'calibration.json',cal)
        recipe=read(parent/'source_replay.json');recipe['contexts']=[x for x in recipe['contexts'] if x['id']==sid];write(cand/'source_replay.json',recipe)
        artifacts=[{'path':'calibration.json','sha256':sha(cand/'calibration.json')}]
        for seed in PLAN['source_seeds']:
            rel=f'feedback/initial_{seed}.json';(cand/'feedback').mkdir(exist_ok=True)
            shutil.copyfile(bundle/f'source_replays/initial_{seed}/replay.json',cand/rel)
            artifacts.append({'path':rel,'sha256':sha(cand/rel)})
        pair={'same_generator_bytes':sha(cand/'generator.py')==sha(parent/'generator.py'),'same_evidence_bytes':sha(cand/'evidence.json')==sha(parent/'evidence.json'),'same_context_files':{s['id']:sha(cand/f'source_contexts/{s["id"]}.csv')==sha(parent/f'source_contexts/{s["id"]}.csv') for s in PLAN['scenarios']},'scientific_parameter_changes':[key],'all_nonlocation_parameters_identical':all(spec['parameters'][k]==original['parameters'][k] for k in original['parameters'] if k!=key),'own_replay_not_yet_run':True}
        assert pair['same_generator_bytes'] and pair['same_evidence_bytes'] and all(pair['same_context_files'].values()) and pair['all_nonlocation_parameters_identical']
        write(cand/'paired_integrity_check.json',pair);artifacts.append({'path':'paired_integrity_check.json','sha256':sha(cand/'paired_integrity_check.json')})
        write(cand/'checks.json',{'scope':'source_only','records':[{'name':'verified_initial_source_feedback','status':'pass','detail':'All three actual source replay reports verified against initial candidate before pooling; original reports copied and hashed.'},{'name':'pooled_source_location_derivation','status':'pass','detail':'Computed source-only pooled type7 medians, inspected interior central statistics for ha, applied prescribed signed offsets; calibration.json records input/output hashes and numbers. This derived operation is not a native harness pooled estimator.'},{'name':'paired_science_integrity','status':'pass','detail':'Generator bytes/evidence/context files match initial; every nonlocation scientific parameter unchanged. Metadata describes the derivation.'},{'name':'own_source_replay','status':'not_computable','detail':'Not run when frozen; verified replay reports remain outside candidate and are retained by controller.'}],'artifacts':artifacts})
        (cand/'decision.md').write_text(f'Prespecified {family} family, {sid} source-location sensitivity. The only scientific change is the sex location offset in calibration.json, derived from three verified initial source executions. All source evidence, context CSVs, age/BMI/residual functions and generator bytes are unchanged; own replay selects the corresponding context. No target feedback was used. All versions retained, no winner selected. Rounded published anchors and unknown source joint laws limit interpretation; source median fit is calibration only.\n',encoding='utf-8')
        revision={'reason':f'Apply prospectively fixed source-only marginal-median to conditional-location correction for {sid}.','kind':'revise','addressed_findings':['Inherited marginal medians were assumed conditional reference locations; actual frozen source replay quantifies the mismatch under the declared source-X scenario.'],'remaining_limitations':['Source joint distribution and residual law underidentified.','Open>=70 age bin compressed to70-79; n4420 versus n4402 mismatch.','BMI effect/residual law/transport unchanged assumptions.','Fitted source median agreement is not independent target validation.']}
        write(bundle/f'revisions/{name}.json',revision);frozen(bundle,name,'initial',revision)
        result[sid]=cal
        log(bundle,'calibrated_frozen',candidate=name,offsets={s:x['offset'] for s,x in cal['sex'].items()},locations=spec['parameters'][key])
    write(bundle/'source_calibration_summary.json',result)

def recheck(bundle):
    assert sha(HERE/'source_plan.json')==sha(bundle/'candidates/initial/source_plan.json'),'Source plan differs from frozen initial plan'
    for s in PLAN['scenarios']:
        for seed in PLAN['source_seeds']:replay(bundle,'calibrated_'+s['id'],seed)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--family',choices=['ha','hb'],required=True);ap.add_argument('--phase',choices=['initial','calibrate','recheck'],required=True);args=ap.parse_args();bundle=args.bundle.resolve()
    try:
        if args.phase=='initial':initial(bundle)
        elif args.phase=='calibrate':calibrate(bundle,args.family)
        else:recheck(bundle)
    except Exception as e:
        log(bundle,'controller_failure',phase=args.phase,error_type=type(e).__name__,message=str(e));raise
