"""Lock reviewed new setup, then create AND verify before releasing to author."""
from pathlib import Path
import hashlib
import json
import sys
HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
sys.path.insert(0,str(PROJECT))
from cohort_harness import adaptive_session_v2 as session

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    with p.open('x',encoding='utf8') as f:json.dump(x,f,indent=2);f.write('\n')

def main():
    review=read(HERE/'SETUP_REVIEW.json')
    if review.get('remaining_blockers') != []:raise ValueError('Setup review unresolved')
    if review.get('status') != 'ready_for_fresh_session_creation':raise ValueError('Setup review not ready')
    protocol=read(HERE/'PROTOCOL.json');bundle=Path(protocol['bundle'])
    names=['initialize_corrected.py','prepare.py','start_session.py','PROTOCOL.json','SESSION_CONFIG.json',
        'analysis_use_adapter.py','generated_analysis.py','close_author.py','evaluate.py','independent_recompute.py',
        'test_evaluate.py','test_adapter_integration.py','test_inherited_registry.py','RULE_BASIS.json','RULE_BASIS.md',
        'SETUP_CORRECTION.json','SETUP_REVIEW.json','SETUP_REVIEW.md']
    write(HERE/'DESIGN_LOCK.json',{'purpose':'Prospective no-target coherence development; corrected unused source import',
        'files':{n:sha(HERE/n) for n in names}})
    write(HERE/'INITIAL_INPUTS.json',{p.relative_to(bundle).as_posix():sha(p) for p in bundle.rglob('*') if p.is_file()})
    created=session.create_session(bundle,read(HERE/'SESSION_CONFIG.json'))
    write(HERE/'SESSION_CREATED.json',created)
    verified=session.verify_session(bundle)
    write(HERE/'SESSION_VERIFIED.json',verified)
    state={'phase':'session_verified_author_ready','bundle':str(bundle),'reference_access':'none','executions':0,
        'design_sha256':sha(HERE/'DESIGN_LOCK.json'),'setup_failure_retained':'../analysis_use_rubric_2026-11-09/SETUP_FAILURE.json'}
    (HERE/'STATE.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
    print(json.dumps(verified))

if __name__=='__main__':main()
