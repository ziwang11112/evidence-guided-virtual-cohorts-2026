"""Controller audit of all constructions without reserved outcome parsing."""
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import sys

O=Path(__file__).resolve().parent
P=O.parents[1]
S=P/'work/analysis-utility-preparation-2026-10-29'
sys.path.insert(0,str(P))
from cohort_harness.lifecycle import verify_candidate
from cohort_harness.execution import verify_execution
from cohort_harness.source_replay import verify_source_replay

def read(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok, why):
    if not ok: raise ValueError(why)

def main():
    locations=read(O/'execution_locations.json')['constructions']
    records=[]
    for cid,loc in locations.items():
        b=Path(loc['bundle_path'])
        case='nhanes_insulin' if cid[0]=='i' else 'pns_hba1c'
        shared=S/'bundles'/case
        for rel,digest in read(shared/'input_manifest.json')['files'].items():
            require(sha(b/rel)==digest, f'{cid} changed shared input {rel}')
        f=Path(loc['selection_path'])
        if (b/'selection_pre_execution.json').exists(): f=b/'selection_pre_execution.json'
        sel=read(f)
        require(sel['target_outcomes_read'] is False, 'Outcome use declared')
        selected=b/'candidates'/sel['selected_candidate']
        verify_candidate(b, selected)
        initial=selected
        while read(initial/'freeze.json')['parent'] is not None:
            initial=b/read(initial/'freeze.json')['parent']['candidate']
        variants=[]
        for c in sorted((b/'candidates').iterdir()):
            if (c/'freeze.json').exists():
                verify_candidate(b,c)
                variants.append(c.name)
        require(len(variants)<=3, 'Candidate budget exceeded')
        sources=[]
        for p in sorted((b/'source_replays').glob('*/replay.json')):
            r=verify_source_replay(b,p.parent.name)
            sources.append({'replay_id':p.parent.name,'status':r['status'],'sha256':sha(p)})
        runs=[]
        for p in sorted((b/'executions').glob('*/execution.json')):
            r=verify_execution(b,p.parent.name)
            runs.append({'run_id':p.parent.name,'status':r['status'],'seed':r['limits']['seed'],
                         'candidate':r['candidate'],'created_utc':r['created_utc']})
        chosen=[r for r in runs if r['candidate']==selected.relative_to(b).as_posix() and r['status']=='success']
        require(sorted(r['seed'] for r in chosen)==[92101,92102,92103], 'Incomplete final execution schedule')
        timestamp=next((sel[k] for k in ['selection_recorded_at','selection_recorded_utc','selected_utc','recorded_utc','recorded_at_utc','created_utc'] if k in sel),None)
        require(timestamp is not None,'Missing pre-execution selection time')
        selected_time=datetime.fromisoformat(timestamp.replace('Z','+00:00'))
        require(all(selected_time<=datetime.fromisoformat(r['created_utc'].replace('Z','+00:00')) for r in chosen),
                'Final selection was recorded after execution')
        records.append({'construction_id':cid,'case_id':case,'bundle':str(b),'selection_path':str(f),
                        'selection_sha256':sha(f),'initial_candidate':initial.name,'selected_candidate':selected.name,
                        'frozen_candidates':variants,'source_receipts':sources,'final_receipts':runs,
                        'scientific_generator_unchanged':sha(initial/'generator.py')==sha(selected/'generator.py'),
                        'scientific_specification_unchanged':sha(initial/'model_spec.json')==sha(selected/'model_spec.json'),
                        'shared_input_bytes_unchanged':True,'selection_precedes_final_runs':True})
    independent=read(O/'blind_review.json')
    require(not independent['blocking_implementation_bugs'],'Independent review has blockers')
    report={'schema_version':'m10-implementation-review-1','recorded_utc':datetime.now(timezone.utc).isoformat(),
            'target_outcomes_read':False,'ready_for_locked_evaluation':True,'constructions':records,
            'independent_review_path':str(O/'blind_review.json'),'independent_review_sha256':sha(O/'blind_review.json'),
            'independent_review_scope':'Evaluator/controller plus ia and ha. Root reviewed ib and hb scientific code/spec/decision separately.',
            'controller_scientific_review':{
                'ia':'Code implements declared moment-derived conditional lognormal model; within-tertile covariance, sex null, damped tails and transport are assumptions.',
                'ib':'Code implements declared log-BMI/glucose/age conditional lognormal model; covariance, sex shift and bounded tails are assumptions. MACAD and Taiwan checks remain distinct.',
                'ha':'Code implements declared sex-specific age term, saturating BMI assumption and shifted-lognormal residual; clipping support is assumed.',
                'hb':'Code implements declared sex-specific age term, linear BMI assumption and shifted-lognormal residual. Source central summaries do not validate tails.',
                'all':'No fixed target answers supplied by controller. Agent authored scientific model/parameters from evidence and explicit assumptions. No scientific target-based modification.'},
            'limitations':['Source replay covariates approximate unreported source joint distributions',
                           'All transport and unreported nonlinear/subgroup findings require held-out evaluation',
                           'Source/model uncertainty not quantified by residual seeds',
                           'Agent tool access procedurally restricted; generator process alone sandboxed',
                           'Cross-study fusion is incomplete: HbA1c constructions chiefly use one compatible source cohort']}
    out=O/'implementation_review.json'
    with out.open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    print(json.dumps({'status':'ready_for_locked_evaluation','constructions':len(records),'target_outcomes_read':False}))

if __name__=='__main__': main()
