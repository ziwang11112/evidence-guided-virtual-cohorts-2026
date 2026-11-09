"""Compact executed-action provenance without source bodies or patient rows."""
from pathlib import Path
import hashlib
import json
from datetime import datetime
from collections import Counter

ROOT=Path(__file__).resolve().parent

def main():
    closed=json.loads((ROOT/'AUTHOR_CLOSED.json').read_text())
    b=Path(closed['bundle']);entries=[];reservations={};last_literature=None
    for p in sorted((b/'adaptive_session_v1/events').glob('*.json')):
        e=json.loads(p.read_text())['payload']
        if e['kind']=='reserve':reservations[e['action_id']]=e;continue
        begin=reservations[e['action_id']];a=begin['payload']
        response=json.loads((b/'adaptive_session_v1/results'/f"{e['action_id']}.json").read_text())
        r=response.get('result') or {}
        row={'id':e['action_id'],'kind':a['kind'],'status':response['status'],'session_status':response['session_status'],
             'duration_seconds':(datetime.fromisoformat(e['created_utc'])-datetime.fromisoformat(begin['created_utc'])).total_seconds()}
        for key in ('action','query','pmcid','version','candidate','parent','run_id','seed','feedback_id','analysis_id','adapter','final_candidate'):
            if key in a:row[key]=a[key]
        if r.get('reason'):row['reason_code']=r['reason']
        if a['kind']=='literature':last_literature=r.get('usage',last_literature)
        if a['kind']=='feedback':row.update(n_computable=r['n_computable'],n_not_computable=r['n_not_computable'])
        entries.append(row)
    totals=Counter(x['kind'] for x in entries)
    result={'kind':'executed_adaptive_action_summary','closure_sha256':hashlib.sha256((ROOT/'AUTHOR_CLOSED.json').read_bytes()).hexdigest(),
            'controller_actions':len(entries),'actions_by_kind':dict(totals),'events':entries,
            'source_usage':last_literature,'final_candidate':closed['final_candidate'],
            'interpretation':'Actions executed by one scientific author through the host controller. File reads, author reasoning, independent review and retained calculations are not counted as controller actions; tokens were not instrumented.',
            'semantic_feedback':{'reports':totals['feedback'],'numerically_computable':sum(x.get('n_computable',0) for x in entries),
                                 'unavailable':sum(x.get('n_not_computable',0) for x in entries)},
            'actual_generation':{'candidate_versions':2,'tables':6,'rows_per_table':3000,'virtual_rows_total':18000,
                                 'new_real_patient_rows':0,'all_outputs_local_only':True},
            'cost_scope':'Per-action time includes dispatch/verification. It is not total Agent compute, token cost or researcher time saved.'}
    (ROOT/'ACTION_SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'actions':len(entries),'kind_counts':dict(totals),'source_usage':last_literature,'feedback':result['semantic_feedback']}))

if __name__=='__main__':main()
