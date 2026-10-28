"""Verify all frozen candidates/runs, then authorize one locked target evaluation."""
from pathlib import Path
import hashlib
import json
import sys
from datetime import datetime, timezone

root=Path(__file__).resolve().parent
project=root.parents[1]
sys.path.insert(0,str(project))
from cohort_harness.lifecycle import verify_candidate
from cohort_harness.execution import verify_execution
from cohort_harness.source_replay import verify_source_replay

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
bundle=root/'tg_agent_bundle'
custodian=root/'custodian/nhanes_tg_j_v2'
protocol=read(bundle/'protocol.json')
guard=custodian/'evaluator_guard_amendment.json'
assert sha(guard)=='852401a856dd43f31ee9424802225bbb9c721c200f90766339c01c1ede2c5e10'
outputs=[]
candidates=[]
for stage in ('initial','final'):
    candidate=bundle/'candidates'/stage
    receipt=verify_candidate(bundle,candidate)
    assert receipt['revision_index']==(0 if stage=='initial' else 1)
    source=verify_source_replay(bundle,stage+'_feedback',candidate=candidate)
    assert source['status']=='success'
    target=read(bundle/'controller_runs'/(stage+'_target_summary.json'))
    assert target['candidate_freeze_sha256']==sha(candidate/'freeze.json')
    assert [o['seed'] for o in target['outputs']]==protocol['target_seeds']
    candidates.append({'label':'tg_builder','stage':stage,'path':str(candidate/'freeze.json'),
                       'sha256':sha(candidate/'freeze.json')})
    for output in target['outputs']:
        path=Path(output['path'])
        assert output['stage']==stage and path.is_relative_to(bundle/'executions')
        assert sha(path)==output['sha256']
        execution=verify_execution(bundle,output['label'])
        assert execution['status']=='success' and execution['candidate']=='candidates/'+stage
        assert execution['limits']['seed']==output['seed']
        outputs.append({'label':'tg_builder','stage':stage,'seed':output['seed'],
                        'path':str(path),'sha256':sha(path)})
assert len(outputs)==2*len(protocol['target_seeds'])
commitment={'created_utc':datetime.now(timezone.utc).isoformat(),
    'all_initial_final_committed':True,'authorize_target_evaluation':True,
    'authorization_basis':'User requested source-feedback loop followed by held-out public-data evaluation',
    'custodian_amendment_sha256':sha(guard),'candidate_commitments':candidates,'outputs':outputs,
    'controller_protocol_sha256':sha(bundle/'protocol.json'),
    'observed_sha256':sha(bundle/'observed.csv'),
    'post_evaluation_builder_revision_allowed':False}
path=root/'evaluation_commitment.json'
with path.open('x',encoding='utf-8') as stream: json.dump(commitment,stream,indent=2,allow_nan=False)
print(json.dumps({'commitment':str(path),'sha256':sha(path),'outputs':len(outputs),
                  'target_outcomes_read_by_controller':False},indent=2))
