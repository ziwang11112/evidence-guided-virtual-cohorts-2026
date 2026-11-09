"""Bounded host dispatch; target generation/analysis remains sealed during authoring."""
from pathlib import Path
import datetime, hashlib, json, sys
HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
sys.path.insert(0,str(PROJECT))
from cohort_harness import adaptive_session_v2 as session
from cohort_harness import whole_cohort_source_replay_v1 as source
from cohort_harness import lifecycle as lc
from cohort_harness import web_evidence_v1 as web

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')

def check_design():
    for path,expected in read(HERE/'DESIGN_LOCK.json')['files'].items():
        if sha(Path(path))!=expected:raise ValueError('Locked design changed: '+path)

def candidate_budget(bundle,name,protocol):
    if name not in ['candidates/'+x for x in protocol['candidate_names']]:raise ValueError('Unexpected candidate name')
    directory=bundle/name
    plan=read(directory/source.PLAN)
    if plan['budget']!={'max_evaluations':24,'max_rows_per_evaluation':10000}:raise ValueError('Wrong source budget')
    if len(plan['schedule'])>24:raise ValueError('Source schedule exceeds cap')
    keys=set()
    for e in plan['schedule']:
        key=(e['candidate'],e['context_id'],e['seed'])
        if key in keys:raise ValueError('Duplicate candidate/context/seed schedule slot')
        keys.add(key)
        if e['candidate'] not in ['candidates/'+x for x in protocol['candidate_names']]:raise ValueError('Unexpected candidate')
        if e['context_id'] not in protocol['source_context_ids_allowed'] or e['seed'] not in protocol['source_seeds']:raise ValueError('Unexpected source schedule')
        if not 0<e['n_rows']<=10000:raise ValueError('Invalid source rows')
    budget=read(directory/'calculation_budget.json')
    # Author declaration is code-reviewed, not automatically trusted runtime instrumentation.
    for field in ('analytic_objective_evaluations','simulated_objective_evaluations'):
        if type(budget[field]) is not int or budget[field]<0:raise ValueError('Objective counts must be nonnegative integers')
    total=budget['analytic_objective_evaluations']+budget['simulated_objective_evaluations']
    if type(total) is not int or total<0 or total>protocol['objective_evaluation_cap']:raise ValueError('Invalid objective count')
    if budget['unlogged_inner_sampling_loops'] is not False:raise ValueError('Unlogged loops declared')
    if name.endswith('/revised'):
        original=read(bundle/'candidates/initial/calculation_budget.json')
        for field in ('analytic_objective_evaluations','simulated_objective_evaluations'):
            if type(original[field]) is not int or original[field]<0:raise ValueError('Invalid initial objective count')
        total+=original['analytic_objective_evaluations']+original['simulated_objective_evaluations']
        if total>protocol['objective_evaluation_cap']:raise ValueError('Combined objective cap exceeded')
    read(directory/'source_to_target_link.json')

def verify_author_seal(bundle):
    seal=read(HERE/'AUTHOR_SEALED.json')
    current=session.verify_session(bundle)
    if set(seal['candidate_freezes'])!=set(current['candidates']):raise ValueError('Scientific stage inventory differs from seal')
    for name,expected in seal['candidate_freezes'].items():
        lc.verify_candidate(bundle,name)
        if sha(bundle/name/'freeze.json')!=expected:raise ValueError('Sealed scientific stage changed')
    if seal['final_candidate'] not in current['candidates']:raise ValueError('Wrong final scientific stage')
    if seal['decision'] not in {'retain','revise'}:raise ValueError('Unknown scientific decision')
    if len(current['candidates'])==1 and seal['decision']!='retain':raise ValueError('One-stage seal requires explicit retain decision')
    path=lc._path(bundle,seal['author_decision']['path'])
    if sha(path)!=seal['author_decision']['sha256']:raise ValueError('Author decision changed')
    actual=list((bundle/source.FOLDER).glob('*/replay.json'))
    if set(seal['source_feedback'])!={p.relative_to(bundle).as_posix() for p in actual}:raise ValueError('Source feedback inventory changed')
    for relative,expected in seal['source_feedback'].items():
        if sha(lc._path(bundle,relative))!=expected:raise ValueError('Source feedback changed')
        source.verify_source_replay(bundle,Path(relative).parent.name)
    return seal

def dispatch(action_id,action):
    check_design()
    protocol=read(HERE/'PROTOCOL.json');bundle=Path(protocol['bundle'])
    folder=HERE/'actions';folder.mkdir(exist_ok=True)
    lc.safe_relative(action_id)
    if '/' in action_id or '\\' in action_id:raise ValueError('Simple action id required')
    req=folder/(action_id+'.request.json');out=folder/(action_id+'.result.json')
    write(req,{'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'action':action})
    try:
        kind=action['kind']
        if kind=='literature':raise ValueError('This unit uses one web_evidence acquisition lane; no independent literature allowance')
        if kind in {'execute','feedback','analysis','finish'}:
            verify_author_seal(bundle)
        elif (HERE/'AUTHOR_SEALED.json').exists():
            raise ValueError('Scientific authoring/retrieval closed after seal')
        if kind in {'discovery_reserve','web_evidence'}:
            discovery=HERE/'discovery_reservations';discovery.mkdir(exist_ok=True)
            requests=list(discovery.glob('*.json'))
            if len(requests)+web.verify(bundle)['usage']['http_attempts']>=protocol['discovery_requests_remaining']:
                raise ValueError('Combined discovery/acquisition allowance exhausted')
            if kind=='discovery_reserve':
                if not isinstance(action.get('query'),str) or not action['query'].strip():raise ValueError('Missing discovery query')
                write(discovery/(action_id+'.json'),{'query':action['query'],'charged':True,'failed_attempts_not_refunded':True})
                result={'status':'reserved','scope':'Native discovery must be executed by host and its result logged; this is not a search result'}
                write(out,{'status':'returned','result':result})
                return result
        if kind in {'preflight','submit','source_preflight','source_replay'}:
            name=action['candidate'];name=name if name.startswith('candidates/') else 'candidates/'+name
            candidate_budget(bundle,name,protocol)
        if kind=='source_preflight':
            result=source.preflight(bundle,name)
        elif kind=='source_replay':
            current=session.verify_session(bundle)
            if current['status']!='active' or name not in current['candidates']:raise ValueError('Source candidate is not session-submitted')
            result=source.run_source_replay(bundle,name,action['replay_id'],action['context_id'],action['seed'],
                       runtime=protocol['runtime'],**protocol['execution_limits'])
        else:
            result=session.dispatch(bundle,action_id,action)
        write(out,{'status':'returned','result':result})
        return result
    except Exception as e:
        write(out,{'status':'error','type':type(e).__name__,'message':str(e)})
        raise

if __name__=='__main__':
    action=read(Path(sys.argv[2]))
    result=dispatch(sys.argv[1],action)
    # Full reports remain in actions/. Scientific output rows are never printed.
    print(json.dumps({'action_id':sys.argv[1],'status':result.get('status'),
                      'result_path':str(HERE/'actions'/(sys.argv[1]+'.result.json'))},indent=2))
