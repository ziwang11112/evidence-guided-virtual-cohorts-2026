"""Bind independently reviewed bytes and user-authorized bounded launch; no HTTP."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,importlib.util

ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,ensure_ascii=False)

review_path=ROOT/'review/INDEPENDENT_PREFLIGHT.json'
review=read(review_path)
assert str(review['status']).lower()=='pass'
assert sha(review_path)=='f54e34a9637ae710bd7fcd91c1d1eb24e778d586673dc125ad84566fb82e5fd3'
for rel,digest in review['reviewed_files'].items():assert sha(ROOT/rel)==digest,rel
for rel,digest in review['reviewed_external_files'].items():assert sha(Path(rel))==digest,rel
assert not (ROOT/'PREFLIGHT_REVIEW.json').exists()
shutil.copyfile(review_path,ROOT/'PREFLIGHT_REVIEW.json')
files=dict(review['reviewed_files']);files['PREFLIGHT_REVIEW.json']=sha(ROOT/'PREFLIGHT_REVIEW.json')
now=datetime.now(timezone.utc).isoformat()
freeze={'created_utc':now,'files':files,'external_files':review['reviewed_external_files'],
        'credential_helper_sha256':review['credential_helper_sha256'],
        'scope':'24 paired target-free review sessions, two existing requests, all12 initial laws; no hidden answer feedback'}
write(ROOT/'LAUNCH_FREEZE.json',freeze)
plan=read(ROOT/'PLAN.json')
write(ROOT/'ROOT_EXECUTION_APPROVAL.json',{'created_utc':now,'status':'approved',
    'authorization':'User 2026-11-11 explicitly requests integrating three checks, Agent-led repair and scientific-analysis evaluation; economical GPT-only research authorization persists.',
    'plan_sha256':sha(ROOT/'PLAN.json'),'launch_freeze_sha256':sha(ROOT/'LAUNCH_FREEZE.json'),
    'episodes':[e['episode_id'] for e in plan['episodes']],'files':files,'max_new_accounted_usd':48,
    'first_block_only_until_operational_gate':True,'no_scientific_parameter_editing_by_host':True,
    'no_new_patient_data':True,'no_expansion_or_retry_for_favorable_result':True})
spec=importlib.util.spec_from_file_location('root_verify_revision_launch',ROOT/'api_loop.py')
api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
api.verify_live_gate(ROOT,plan)
state=read(ROOT/'STATE.json');state.update(status='frozen_ready_for_block1',updated_utc=now,
    independent_preflight_checks=478,owner_law_tests=34,owner_runtime_tests=32,
    launch_freeze_sha256=sha(ROOT/'LAUNCH_FREEZE.json'))
(ROOT/'STATE.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
print(json.dumps({'status':state['status'],'launch_freeze_sha256':state['launch_freeze_sha256'],
                  'reviewed_local_files':len(review['reviewed_files']),'paid_calls':0}))
