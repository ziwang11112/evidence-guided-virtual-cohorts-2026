"""Foreground bookkeeping only; scientific execution stays in frozen controller."""
import json
import sys
from pathlib import Path
UNIT = Path(__file__).resolve().parent
sys.path.insert(0, str(UNIT / 'implementation'))
import main_session_v1 as control

def reconcile():
    release = control.READ(UNIT / 'RELEASE.json')
    state = control.READ(UNIT / 'STATE.json')
    rows = []
    for item in release['constructions']:
        s = control.Session(item['session_root'])
        attempts = s.selected('attempt')
        results = s.selected('result')
        final_indices = {x['index'] for x in attempts if x['purpose'] == 'final'}
        rows.append({'id':item['id'], **s.status(),
                     'dispatched':bool(s.selected('dispatch')),
                     'kind':s.contract['constructor_kind'],
                     'success':sum(x['status']=='success' for x in results),
                     'final_success':sum(x['status']=='success' and x['attempt_index'] in final_indices for x in results),
                     'failed':sum(x['status']!='success' for x in results)})
    state.update(actual_sessions=rows,
                 actual_constructions=sum(x['dispatched'] for x in rows),
                 scientific_authors_dispatched=sum(x['dispatched'] and x['kind']=='agent' for x in rows),
                 actual_tables=sum(x['success'] for x in rows),
                 actual_final_tables=sum(x['final_success'] for x in rows),
                 actual_table_attempts=sum(x['attempts'] for x in rows),
                 closed_constructions=sum(x['closed'] for x in rows),
                 updated_utc=control.now())
    (UNIT/'STATE.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    return {k:state[k] for k in ['actual_constructions','scientific_authors_dispatched','actual_tables','actual_final_tables','actual_table_attempts','closed_constructions']}

def cost_snapshot(destination):
    """Observed execution time only; never attribute this to end-to-end Agent cost."""
    release=control.READ(UNIT/'RELEASE.json')
    records=[]
    for item in release['constructions']:
        s=control.Session(item['session_root']);s.verify()
        for event in s.selected('result'):
            receipt=event.get('receipt')
            if not receipt:
                records.append({'constructor_id':item['id'],'run_id':event['run_id'],'status':event['status'],'execution_elapsed_seconds':None})
                continue
            control.verify_bound(receipt)
            raw=control.READ(receipt['path'])
            records.append({'constructor_id':item['id'],'run_id':event['run_id'],'status':event['status'],
                            'execution_elapsed_seconds':raw.get('elapsed_seconds'),
                            'receipt_sha256':receipt['sha256']})
    observed=[x['execution_elapsed_seconds'] for x in records if x['execution_elapsed_seconds'] is not None]
    result={'created_utc':control.now(),'attempts_with_results':len(records),'metered_execution_receipts':len(observed),
            'sum_execution_elapsed_seconds':sum(observed),'end_to_end_llm_cost':None,'llm_tokens':None,
            'model_snapshot_id':None,'interpretation':'Receipt elapsed seconds measure isolated generator execution only; they exclude source curation, author reasoning, analytic work, review, orchestration and user time. No resource/cost-saving claim.',
            'records':records}
    control.WRITE(destination,result)
    return {k:result[k] for k in ['attempts_with_results','metered_execution_receipts','sum_execution_elapsed_seconds']}

if __name__ == '__main__':
    print(json.dumps(reconcile()))
