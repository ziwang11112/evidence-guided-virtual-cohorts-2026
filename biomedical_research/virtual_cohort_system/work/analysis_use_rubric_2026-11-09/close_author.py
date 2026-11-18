"""Seal a completed adaptive author session before accessing reference results."""
from pathlib import Path
import hashlib
import json
import sys
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
sys.path.insert(0,str(PROJECT))
from cohort_harness import adaptive_session_v2 as session

def main():
    protocol=json.loads((ROOT/'PROTOCOL.json').read_text())
    bundle=Path(protocol['bundle'])
    summary=session.verify_session(bundle)
    if summary['status']!='completed' or summary['pending'] is not None:
        raise ValueError('Session must be completed with a selected final candidate')
    with session.ledger._operation(bundle/session.DIRECTORY,'close-inspect'):
        state=session._load(bundle,bundle/session.DIRECTORY)
    finishes=[e['action'] for e in state['actions'].values() if e['action']['kind']=='finish' and e.get('result',{}).get('status')=='success']
    if len(finishes)!=1:raise ValueError('Expected one final selection')
    slots=[{'run_id':e['action']['run_id'],'candidate':e['action']['candidate'],'seed':e['action']['seed']} for e in state['actions'].values() if e['action']['kind']=='execute']
    runs=sorted(x['run_id'] for x in slots)
    actual=sorted(p.parent.name for p in (bundle/'executions').glob('*/execution.json'))
    if runs!=actual:raise ValueError('Execution inventory differs from session actions')
    expected={(c,s) for c in summary['candidates'] for s in protocol['seeds']}
    if len(slots)!=len(expected) or {(x['candidate'],x['seed']) for x in slots}!=expected:raise ValueError('Execution schedule differs')
    files={p.relative_to(bundle).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
           for p in bundle.rglob('*') if p.is_file()}
    result={'status':'author_finished_no_further_revision','bundle':str(bundle),
            'final_candidate':finishes[0]['final_candidate'],'reason':finishes[0]['reason'],
            'candidates':summary['candidates'],'runs':runs,'execution_slots':slots,'files':files,'session':summary}
    with (ROOT/'AUTHOR_CLOSED.json').open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'final_candidate':result['final_candidate'],'runs':len(runs),'files_sealed':len(files)}))

if __name__=='__main__':main()
