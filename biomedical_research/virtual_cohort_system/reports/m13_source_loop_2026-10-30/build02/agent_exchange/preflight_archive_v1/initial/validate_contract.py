"""Pre-freeze representation checks only; never import/execute generator.py."""
from pathlib import Path
import hashlib
import json
import math
import sys
import numpy as np
import pandas as pd

C=Path(__file__).resolve().parent
B=C.parent.parent
PROJECT=B.parents[2]
sys.path.insert(0,str(PROJECT))
from cohort_harness import lifecycle, source_context, source_replay_v2
from cohort_harness.contracts import exact_keys

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,obj): path.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')

state=lifecycle._state(B,C,'candidates/initial')
task=read(B/'task.json'); original_task=read(B/'task.json')
manifest=read(B/'agent_exchange/initial_input_manifest.json')
for rel,digest in manifest['files'].items(): assert sha(B/rel)==digest,(rel,'input hash changed')
spec=read(C/'model_spec.json'); evidence={e['id']:e for e in read(C/'evidence.json')['items']}
assumptions={a['id'] for a in spec['assumptions']}
replay=read(C/'source_replay_v2.json')
exact_keys(replay,{'schema_version','model_domain','contexts'},where='source replay v2')
assert replay['schema_version']==2 and len(replay['contexts'])==2
result={'status':'pass','scope':'Pre-freeze contract, static ABI, input hashes and covariate arithmetic ONLY',
        'generator_imported':False,'generator_executed':False,'outcome_statistics_computed':False,
        'evidence_items':len(evidence),'approved_input_hashes_unchanged':True,'contexts':[],
        'deferred':['freeze','isolated generator execution','execution-backed source outcome replay','full frozen calibration-plan validation']}
all_constraints=[]
for ctx in replay['contexts']:
    exact_keys(ctx,{'id','population','reason','assumption_ids','measurement','input','checks','columns'},where='source context')
    inp=ctx['input']; assert sha(C/inp['path'])==inp['sha256']
    frame=pd.read_csv(C/inp['path'])
    source_task=source_context.compile_source_task(task,ctx,replay['model_domain'],frame,assumption_ids=assumptions)
    assert len(frame)<=12000 and 'bodyfat' not in frame
    transforms={'inv_bmi':1/frame.bmi,'male_inv_bmi':frame.male/frame.bmi,'asian_inv_bmi':frame.asian/frame.bmi,
                'male_age':frame.male*frame.age,'asian_age':frame.asian*frame.age}
    errors={name:float(np.max(np.abs(frame[name]-expected))) for name,expected in transforms.items()}
    assert max(errors.values())<1e-10,errors
    assert set(replay['model_domain']['assumption_ids'])<=set(ctx['assumption_ids'])
    for check in ctx['checks']:
        source_replay_v2.legacy._check_metadata(check,evidence,assumptions,ctx['assumption_ids'])
        source_replay_v2._operator_preflight(check['operator'],source_task)
        all_constraints.append((ctx['id'],check['id']))
    result['contexts'].append({'id':ctx['id'],'rows':len(frame),'checks':len(ctx['checks']),
        'derived_max_absolute_errors':errors,'bodyfat_absent':True,'input_sha256':sha(C/inp['path'])})
assert task==original_task
assert len(all_constraints)==18 and len(set(all_constraints))==18
control=read(B/'allowed_inputs/controller_contract.json')
plan=read(C/'proposed_calibration_plan.json')
exact_keys(plan,{'schema_version','parameters','constraints','fit_seeds','replay_seeds','optimizer','execution','noncomputable'},where='calibration plan')
assert plan['schema_version']==1 and plan['noncomputable']=='infeasible'
assert plan['fit_seeds']==control['fit_seeds'] and plan['replay_seeds']==control['replay_seeds']
assert not set(plan['fit_seeds'])&set(plan['replay_seeds'])
assert plan['execution']==control['execution']
assert plan['optimizer']=={'method':'bounded_coordinate_search','max_trials':9,'shrink':.5,'min_step_fraction':.01,'target_loss':0}
for p in plan['parameters']:
    exact_keys(p,{'name','lower','upper','step'},where='calibrated scalar parameter')
    assert isinstance(spec['parameters'][p['name']],(float,int))
    assert p['lower']<=spec['parameters'][p['name']]<=p['upper'] and p['lower']<p['upper']
    assert 0<p['step']<=p['upper']-p['lower']
assert len(plan['parameters'])==len({p['name'] for p in plan['parameters']})==4
assert [(c['context_id'],c['check_id']) for c in plan['constraints']]==all_constraints
for c in plan['constraints']:
    exact_keys(c,{'context_id','check_id','scale','scale_reason'},where='loss constraint')
    ctx=next(x for x in replay['contexts'] if x['id']==c['context_id'])
    op=next(x['operator'] for x in ctx['checks'] if x['id']==c['check_id'])
    expected=control['loss_scales']['coefficient_by_term'][op['term']] if op['kind']=='ols_coefficient' else control['loss_scales'][op['kind']]
    assert c['scale']==expected and math.isfinite(c['scale']) and c['scale']>0
result.update(replay_checks=18,calibration_constraints=18,calibration_structure='pass; frozen _validate deferred',
              target_eligibility_unchanged=True,source_domain_compile='pass')
write(C/'contract_validation.json',result)
checks=read(C/'checks.json')
checks['records']=[r for r in checks['records'] if r['name']!='pre_freeze_contract_validation']
checks['records'].append({'name':'pre_freeze_contract_validation','status':'pass',
    'detail':'Actual lifecycle _state validation, source task compilation, existing replay metadata/operator structural preflight and fixed plan/covariate arithmetic passed. No generator execution; see bound report.'})
checks['artifacts']=[a for a in checks['artifacts'] if a['path']!='contract_validation.json']
checks['artifacts'].append({'path':'contract_validation.json','sha256':sha(C/'contract_validation.json')})
checks['records']=[r for r in checks['records'] if r['name']!='validation_history']
checks['records'].append({'name':'validation_history','status':'pass',
    'detail':'First schema attempt rejected empty variable lists on sample-size evidence; preparer was corrected to identify participant-count cardinality. Subsequent validation passed. The original failed attempt is retained.'})
checks['artifacts']=[a for a in checks['artifacts'] if a['path']!='validation_attempts.json']
checks['artifacts'].append({'path':'validation_attempts.json','sha256':sha(C/'validation_attempts.json')})
write(C/'checks.json',checks)
lifecycle._state(B,C,'candidates/initial')
print(json.dumps(result,indent=2))
