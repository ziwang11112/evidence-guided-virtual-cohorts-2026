"""Seal a completed adaptive author session before accessing reference results."""
from pathlib import Path
import hashlib
import json
import sys
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
sys.path.insert(0,str(PROJECT))
from cohort_harness import adaptive_session_v1 as session

def main():
    protocol=json.loads((ROOT/'PROTOCOL.json').read_text())
    bundle=Path(protocol['bundle'])
    summary=session.verify_session(bundle)
    if summary['status']!='completed' or summary['pending'] is not None:
        raise ValueError('Session must be completed with a selected final candidate')
    results=[json.loads(p.read_text(encoding='utf-8-sig')) for p in (bundle/'adaptive_session_v1/results').glob('*.json')]
    finishes=[r['result'] for r in results if isinstance(r.get('result'),dict) and 'final_candidate' in r['result']]
    if len(finishes)!=1:raise ValueError('Expected one final selection')
    runs=sorted(p.parent.name for p in (bundle/'executions').glob('*/execution.json'))
    files={p.relative_to(bundle).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
           for p in bundle.rglob('*') if p.is_file()}
    result={'status':'author_finished_no_further_revision','bundle':str(bundle),
            'final_candidate':finishes[0]['final_candidate'],'reason':finishes[0]['reason'],
            'candidates':summary['candidates'],'runs':runs,'files':files,'session':summary}
    with (ROOT/'AUTHOR_CLOSED.json').open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'final_candidate':result['final_candidate'],'runs':len(runs),'files_sealed':len(files)}))

if __name__=='__main__':main()
