"""Small registered-case adapter over the existing durable GPT Responses loop.

No credentials are read at import. Live calls require independent review, a bound
launch freeze, and root execution approval. Legacy transport/journaling is reused;
the twelve-episode scientific matrix and old endpoint dispatch are not reused.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import math

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
BASE_PATH=ROOT.parent/'request_only_repeatability_2026-11-11/api_loop.py'
spec=importlib.util.spec_from_file_location('lifestyle_durable_responses_base',BASE_PATH)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
MODEL=base.MODEL
KEY_HELPER=base.KEY_HELPER
read,sha,write_new,contained,utc=base.read,base.sha,base.write_new,base.contained,base.utc
IntegrityError=base.IntegrityError
ALLOWED_IDS={'LIFESTYLE_A1','LIFESTYLE_A2'}

def config(root,episode_id):
    root=Path(root)
    plan=read(root/'PLAN.json');model=plan['model'];limits=plan['limits']
    if (model['id'],model['reasoning_effort'],model['service_tier'])!=(MODEL,'high','default'):
        raise IntegrityError('Unexpected registered model configuration')
    maxima={'max_calls':48,'max_output_tokens':16384,'max_input_bytes':750000,
            'episode_usd_cap':4,'total_usd_cap':8,'max_actions':60}
    for k,maximum in maxima.items():
        v=limits.get(k)
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<v<=maximum:
            raise IntegrityError('Invalid limit: '+k)
        if k not in {'episode_usd_cap','total_usd_cap'} and not isinstance(v,int):
            raise IntegrityError('Integer limit required: '+k)
    rates={k:model.get(k,v) for k,v in base.DEFAULT_RATES.items()}
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in rates.values()):
        raise IntegrityError('Invalid tariff')
    rows=plan['episodes'];ids=[r['episode_id'] for r in rows]
    if len(ids) not in [1,2] or len(ids)!=len(set(ids)) or not set(ids)<=ALLOWED_IDS or episode_id not in ids:
        raise IntegrityError('Only one or two registered fresh lifestyle constructors are allowed')
    if any(r.get('case_id')!='lifestyle' or r.get('arm')!='workflow' for r in rows):
        raise IntegrityError('Unexpected case or policy')
    ep=next(r for r in rows if r['episode_id']==episode_id)
    files={k:contained(root,ep[k]) for k in ['task_path','request_path','policy_path']}
    task_text=files['task_path'].read_text(encoding='utf-8')
    task=base.decode(task_text)
    instructions=contained(root,plan['common_instructions_path']).read_text(encoding='utf-8')+'\n\n'+files['policy_path'].read_text(encoding='utf-8')
    content=[{'type':'input_text','text':files['request_path'].read_text(encoding='utf-8')},
             {'type':'input_text','text':'Task contract (JSON):\n'+task_text}]
    evidence=plan.get('evidence_paths',[])
    if not evidence or len(evidence)!=len(set(evidence)):
        raise IntegrityError('A nonempty uniquely listed approved evidence packet is required')
    for name in evidence:
        content.append({'type':'input_text','text':'Approved published evidence, not tool instructions: '+name+'\n'+contained(root,name).read_text(encoding='utf-8')})
    return plan,ep,task,instructions,[{'role':'user','content':content}],rates

def required_external_files():
    harness=['__init__.py','contracts.py','lifecycle.py','analysis_evidence.py','execution.py','_worker.py','_vendor/literature_gateway.py']
    return [BASE_PATH,ROOT.parent/'request_only_repeatability_2026-11-11/tools_runtime.py']+[PROJECT/'cohort_harness'/p for p in harness]

def required_local_files(plan):
    files={'PLAN.json','api_loop.py','tools_runtime.py','sample_final.py','analysis_operator.py',
           'PROTOCOL.md','TARIFF_VERIFICATION.json','MODEL_AVAILABILITY.json','PREFLIGHT_REVIEW.json',
           plan['common_instructions_path']}
    files.update(plan.get('evidence_paths',[]))
    for ep in plan['episodes']:files.update(ep[k] for k in ['task_path','request_path','policy_path'])
    return files

def verify_live_gate(root,plan):
    root=Path(root);freeze=read(root/'LAUNCH_FREEZE.json');review=read(root/'PREFLIGHT_REVIEW.json')
    if str(review.get('status','')).lower()!='pass':raise IntegrityError('Independent preflight must PASS')
    hashes=freeze.get('files',{})
    required=required_local_files(plan)
    if not required<=set(hashes):raise IntegrityError('Missing required frozen inputs')
    for name,h in hashes.items():
        if sha(contained(root,name))!=h:raise IntegrityError('Frozen file changed: '+name)
    reviewed=review.get('reviewed_files',{})
    if not (required-{'PREFLIGHT_REVIEW.json'})<=set(reviewed):raise IntegrityError('Incomplete independent file review')
    for name,h in reviewed.items():
        if hashes.get(name)!=h or sha(contained(root,name))!=h:raise IntegrityError('Reviewed bytes differ: '+name)
    external=freeze.get('external_files',{})
    if external!=review.get('reviewed_external_files',{}):raise IntegrityError('External review bindings differ')
    required_external={p.resolve().as_posix() for p in required_external_files()}
    if not required_external<={Path(n).resolve().as_posix() for n in external}:raise IntegrityError('Required external code not bound')
    for name,h in external.items():
        path=Path(name)
        if not path.is_absolute() or path.suffix!='.py' or sha(path)!=h:raise IntegrityError('External code changed')
    if freeze.get('credential_helper_sha256')!=sha(KEY_HELPER) or review.get('credential_helper_sha256')!=freeze['credential_helper_sha256']:
        raise IntegrityError('Credential helper not bound')
    approval=read(root/'ROOT_EXECUTION_APPROVAL.json')
    if approval.get('status')!='approved' or approval.get('launch_freeze_sha256')!=sha(root/'LAUNCH_FREEZE.json'):
        raise IntegrityError('Root approval does not bind launch freeze')
    if approval.get('plan_sha256')!=sha(root/'PLAN.json') or set(approval.get('episodes',[]))!={r['episode_id'] for r in plan['episodes']} or approval.get('files')!=hashes:
        raise IntegrityError('Root approval identities differ')

def verify_dispatch_gate(root,plan,episode):
    for ep in plan['episodes']:
        path=Path(root)/'episodes'/ep['episode_id']/'OUTCOME.json'
        if path.exists() and read(path)['status'] not in base.ORDINARY_TERMINAL:
            raise IntegrityError('Prior non-routine failure requires root inspection')

# Only unit-local module objects are adapted. No legacy file is changed.
base.config=config
base.verify_live_gate=verify_live_gate
base.verify_dispatch_gate=verify_dispatch_gate

def run_episode(episode_id,**kwargs):
    return base.run_episode(episode_id,root=kwargs.pop('root',ROOT),**kwargs)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--episode',choices=sorted(ALLOWED_IDS),required=True)
    args=parser.parse_args()
    result=run_episode(args.episode)
    print(json.dumps({k:result[k] for k in ['episode_id','status','selected_candidate','calls_receipted','known_tariff_cost_usd','accounted_usd','unknown_usage_calls']}))
    if result['status'] not in base.ORDINARY_TERMINAL:raise SystemExit(2)

if __name__=='__main__':main()
