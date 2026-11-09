"""Summarize actual completed actions; never publish source bodies or rows."""
from pathlib import Path
import hashlib
import json
from datetime import datetime
from collections import Counter

ROOT=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
    closure=read(ROOT/'AUTHOR_CLOSED.json'); b=Path(closure['bundle'])
    entries=[]; reservations={}
    for p in sorted((b/'adaptive_session_v2/events').glob('*.json')):
        e=read(p)['payload']
        if e['kind']=='reserve': reservations[e['action_id']]=e; continue
        begin=reservations[e['action_id']]; a=begin['payload']
        response=read(b/'adaptive_session_v2/results'/f"{e['action_id']}.json"); r=response.get('result') or {}
        row={'id':e['action_id'],'kind':a['kind'],'status':response['status'],'session_status':response['session_status'],
             'duration_seconds':(datetime.fromisoformat(e['created_utc'])-datetime.fromisoformat(begin['created_utc'])).total_seconds()}
        for key in ('action','query','pmcid','version','url','source_id','purpose','source_type','candidate','parent',
                    'run_id','seed','feedback_id','analysis_id','adapter','final_candidate'):
            if key in a: row[key]=a[key]
        if r.get('reason'): row['reason_code']=r['reason']
        if a['kind']=='feedback' and response['status']=='success':
            row['strict']={k:r['strict'][k] for k in ('n_computable','n_not_computable')}
            checks=r['descriptive']['checks']
            row['descriptive']={'requested':len(checks),'calculated':sum(x['calculation'] is not None for x in checks),
                   'definition_statuses':dict(Counter(x['source_definition_match']['status'] for x in checks))}
        entries.append(row)
    executions=[read(b/'executions'/run/'execution.json') for run in closure['runs']]
    successes=sum(r['status']=='success' for r in executions)
    native=[]
    log=b/'external_discovery.jsonl'
    if log.exists(): native=[json.loads(line) for line in log.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    result={'kind':'executed_adaptive_v2_summary','closure_sha256':hashlib.sha256((ROOT/'AUTHOR_CLOSED.json').read_bytes()).hexdigest(),
            'controller_actions':len(entries),'actions_by_kind':dict(Counter(x['kind'] for x in entries)),
            'events':entries,'final_candidate':closure['final_candidate'],
            'native_discovery_log_entries':len(native),'native_discovery_scope':'External procedural tool log; not screened controller actions; unmetered traffic and tokens.',
            'shared_gateway_usage':read(b/'gateway/session/state.json')['usage'],
            'web_usage':read(b/'web_evidence_v1/state.json')['usage'],
            'actual_generation':{'candidate_versions':len(closure['candidates']),'attempted_tables':len(executions),
               'successful_tables':successes,'rows_per_table':read(b/'task.json')['n_rows'],
               'virtual_rows_total':successes*read(b/'task.json')['n_rows'],'new_real_patient_rows':0},
            'cost_scope':'Dispatch time and received web-body bytes; no claim of measured human time saved or total model cost.',
            'scientific_scope':'Existing-case development; source checks and native discovery do not establish target usefulness.'}
    (ROOT/'ACTION_SUMMARY.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ('controller_actions','actions_by_kind','actual_generation','web_usage')}))

if __name__=='__main__': main()
