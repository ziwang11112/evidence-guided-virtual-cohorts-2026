"""Mechanical session operations only; scientific choices are author-owned."""
from pathlib import Path
import argparse,json,sys
U=Path(__file__).resolve().parent
sys.path.insert(0,str(U/'implementation'))
from information_session_v1 import Session
from attach_feedback import attach
def run(key,candidate,stage,seed=None,phase='initial'):
    root=U.parents[3]/'evcIA'/key;s=Session(root);c=s.bundle/'candidates'/candidate
    if not (c/'whole_cohort_feedback.json').exists():attach(s.bundle,candidate)
    if stage=='final' and not s.selected('decision'):
        s.decision(json.loads((root/'FINAL_AUTHOR_DECISION.json').read_text(encoding='utf-8-sig')))
    if not (c/'freeze.json').exists():s.freeze(candidate,stage=stage)
    elif not any(e.get('stage')==stage and e['candidate']=='candidates/'+candidate for e in s.selected('freeze')):
        raise ValueError('Already frozen under a different stage; author must submit an unfrozen delivery copy')
    if stage=='trial':
        result=s.trial(candidate,seed,phase=phase);report=s.trial_feedback(result['run_id'])
        feedback=root/'session/feedback'/(result['run_id']+'.json');results=[result]
    else:
        results=s.deliver(stage);report=s.feedback(stage);feedback=root/'session/feedback'/(stage+'.json')
    state=json.loads((U/'STATE.json').read_text(encoding='utf-8-sig'))
    state['phase']='scientific_constructions_in_progress';state['constructors'][key].update(status=stage+'_feedback_ready',candidate=candidate,feedback=str(feedback))
    state['attempts']=sum(len(Session(U.parents[3]/'evcIA'/k).selected('attempt')) for k in state['constructors'])
    (U/'STATE.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'constructor':key,'stage':stage,'results':[{'run_id':r['run_id'],'status':r['status'],'error':r.get('error')} for r in results],'feedback':str(feedback)},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('key');p.add_argument('candidate');p.add_argument('stage',choices=['trial','initial','final']);p.add_argument('--seed',type=int);p.add_argument('--phase',default='initial',choices=['initial','revision']);a=p.parse_args();run(a.key,a.candidate,a.stage,a.seed,a.phase)
