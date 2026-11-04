"""Read only closed outputs and pinned previously exposed aggregate references.

No reference is read on import or before the all-four closure gate. All scheduled
slots and endpoints remain present, including failures. No model feedback here.
"""
from pathlib import Path
from statistics import mean
import csv, json, math
import runner

ROOT=Path(__file__).resolve().parent
def finite(v):return type(v) in (int,float) and math.isfinite(v)
def direction(v):return 'positive' if v>0 else 'negative' if v<0 else 'zero'
def missing(contract,reason):
    return {c:[{**x,'status':'unavailable','value':None,'reason':reason} for x in contract[c]] for c in ('analyses','diagnostics')}
def validate(payload,contract):
    for category in ('analyses','diagnostics'):
        expected={x['id']:x['unit'] for x in contract[category]}
        values=payload[category]
        runner.require(len(values)==len(expected) and {x['id'] for x in values}==set(expected),'Endpoint coverage mismatch')
        for x in values:
            runner.require(x['unit']==expected[x['id']],'Changed endpoint unit')
            runner.require((x['status']=='computed' and finite(x['value'])) or (x['status']=='unavailable' and x['value'] is None),'Endpoint value/status invalid')
def add_reference(payload,references):
    out={}
    for category in ('analyses','diagnostics'):
        out[category]=[]
        for row in payload[category]:
            ref=references[row['id']]
            runner.require(row['unit']==ref['unit'],'Reference unit mismatch')
            ok=row['status']=='computed' and finite(row['value']) and finite(ref['value'])
            out[category].append({**row,'reference':ref,
             'comparison_status':'computed' if ok else 'unavailable',
             'generated_direction':direction(row['value']) if finite(row['value']) else None,
             'reference_direction':direction(ref['value']) if finite(ref['value']) else None,
             'signed_difference':row['value']-ref['value'] if ok else None,
             'absolute_difference':abs(row['value']-ref['value']) if ok else None})
    return out
def evaluate():
    closed=runner.closure_gate()
    protocol=runner.protocol()
    refinfo=protocol['reference']
    runner.verify_bound(refinfo)
    refs=runner.READ(refinfo['path'])['references']
    schema=runner.READ(ROOT/'ENDPOINT_CONTRACT.json')['cases']
    dest=ROOT/'evaluation'
    runner.require(not dest.exists(),'Evaluation already reserved; no silent rerun')
    dest.mkdir()
    runner.WRITE(dest/'EVALUATION_STARTED.json',{'batch_closure_sha256':runner.SHA(ROOT/'BATCH_CLOSURE.json'),'reference_sha256':refinfo['sha256'],'created_utc':runner.now()})
    try:
        slots=[];cost=[];author_records=[]
        for aid,setting in protocol['authors'].items():
            s=runner.Session(aid);s.verify();events=s.events();case=setting['case_id']
            attempts=s.selected('attempt');results=s.selected('result')
            decisions=s.selected('decision');terminal=s.selected('closed')[0]
            author_records.append({'author_id':aid,'case_id':case,'external_author_id':s.contract['external_author_id'],
             'initial_and_revision_freezes':[{k:f[k] for k in ('candidate','stage','freeze_sha256')} for f in s.selected('freeze')],
             'decision':decisions[0]['action'] if decisions else None,'terminal_status':terminal['status'],
             'terminal_reason':terminal.get('reason'),'gateway_usage':runner.READ(s.bundle/'gateway/session/state.json')['usage'],
             'source_ids':runner.READ(s.folder/'inputs.json')['original_source_ids']})
            for a in attempts:
                matches=[r for r in results if r['attempt_index']==a['index']]
                outcome=matches[0] if matches else {'status':'missing_result'}
                item={k:a[k] for k in ('run_id','purpose','stage','seed')};item.update(author_id=aid,status=outcome['status'],generator_process_seconds=None,output_route=outcome.get('output_route'),seed_role=outcome.get('seed_role'))
                if outcome.get('receipt'):
                    receipt=runner.READ(outcome['receipt']['path'])
                    item['receipt_keys_available']=sorted(receipt)
                    # Retain raw resource record; report a time only when its name/scope is explicit.
                    item['resources']=receipt.get('resources')
                    item['timing']=receipt.get('timing')
                    item['generator_executed']=receipt.get('generator_executed')
                    item['execution_adapter_elapsed_seconds']=receipt.get('elapsed_seconds')
                    item['elapsed_scope']='Adapter operation wall time; includes setup/validation, excludes Agent and literature acquisition.'
                cost.append(item)
            for seed in protocol['final_seeds']:
                matching=[a for a in attempts if a['purpose']=='final' and a['seed']==seed]
                runner.require(len(matching)<=1,'Duplicated final slot')
                slot={'author_id':aid,'case_id':case,'seed':seed,'scheduled':True,'run_id':None,'candidate':None,'execution_status':'not_attempted','analysis_status':'unavailable','table_sha256':None,'error':None,'output_route':None,'seed_role':None}
                payload=missing(schema[case],terminal.get('reason','No attempted final slot'))
                if matching:
                    a=matching[0];outcomes=[r for r in results if r['attempt_index']==a['index']]
                    runner.require(len(outcomes)==1,'Unresolved scheduled final attempt')
                    o=outcomes[0];slot.update(run_id=a['run_id'],candidate=a['candidate'],execution_status=o['status'],error=o.get('error'),output_route=o.get('output_route'),seed_role=o.get('seed_role'))
                    if o['status']=='success':
                        try:
                            runner.require(o.get('table') is not None,'Successful slot lacks verified table')
                            runner.verify_bound(o['table']);slot['table_sha256']=o['table']['sha256']
                            payload=runner.generated_statistics(s,a['run_id']);validate(payload,schema[case])
                            slot.update(analysis_status='complete' if all(x['status']=='computed' for c in ('analyses','diagnostics') for x in payload[c]) else 'incomplete',quality=payload.get('quality'),n=payload.get('n'))
                        except Exception as e:
                            slot['error']={'type':type(e).__name__,'message':str(e)}
                            payload=missing(schema[case],'Generated-table evaluator failed: '+type(e).__name__+': '+str(e))
                    else:payload=missing(schema[case],'Execution '+o['status'])
                slot.update(add_reference(payload,refs[case]));slots.append(slot)
        summaries=[]
        for aid,setting in protocol['authors'].items():
            these=[s for s in slots if s['author_id']==aid]
            for spec in schema[setting['case_id']]['analyses']:
                rows=[next(x for x in s['analyses'] if x['id']==spec['id']) for s in these]
                good=[r for r in rows if r['comparison_status']=='computed']
                summaries.append({'author_id':aid,'case_id':setting['case_id'],'endpoint':spec['id'],'unit':spec['unit'],'available_slots':len(good),'scheduled_slots':3,
                 'output_routes':sorted({s['output_route'] for s in these if s['output_route']}),
                 'unique_validated_table_hashes':len({s['table_sha256'] for s in these if s['table_sha256']}),
                 'slot_mean':mean(r['value'] for r in good) if good else None,'slot_range':[min(r['value'] for r in good),max(r['value'] for r in good)] if good else None,
                 'reference':refs[setting['case_id']][spec['id']],
                 'mean_absolute_reference_difference':mean(r['absolute_difference'] for r in good) if good else None,
                 'same_direction_slot_count':sum(r['generated_direction']==r['reference_direction'] for r in good),
                 'interpretation':'Descriptive scheduled-slot summary. Direct-row slots validate the same fixed table, not independent draws. Program seed independence requires code review. Not a validated accuracy/success score or uncertainty over structures.'})
        runner.closure_gate();runner.verify_bound(refinfo)
        report={'schema_version':'core_workflow_replication_results_v1','protocol_sha256':runner.SHA(ROOT/'PROTOCOL.json'),'batch_closure_sha256':runner.SHA(ROOT/'BATCH_CLOSURE.json'),
         'reference_sha256':refinfo['sha256'],'new_clinical_reads_or_fits':False,'exposed_development':True,
         'scheduled_authors':4,'reference_families':2,'scheduled_final_slots':12,'successful_final_executions':sum(s['execution_status']=='success' for s in slots),
         'unique_final_table_hashes':len({s['table_sha256'] for s in slots if s['table_sha256']}),'physical_attempts':closed['physical_attempts'],
         'authors':author_records,'all_final_slots':slots,'all_author_endpoint_summaries':summaries,'all_attempt_cost_records':cost,
         'interpretation':'Open author-selected PMC/EuropePMC evidence under fixed budgets; all authors and scheduled endpoints retained. No causal retrieval benefit, universal method ranking, equivalence claim or fresh clinical validation.'}
        runner.WRITE(dest/'RESULTS.json',report)
        with (dest/'ALL_ENDPOINTS.csv').open('x',encoding='utf-8',newline='') as f:
            fields=['author_id','case_id','seed','execution_status','category','endpoint','unit','generated_value','reference_value','signed_difference','absolute_difference','comparison_status']
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
            for s in slots:
                for category in ('analyses','diagnostics'):
                    for x in s[category]:writer.writerow({**{k:s[k] for k in fields[:4]},'category':category,'endpoint':x['id'],'unit':x['unit'],'generated_value':x['value'],'reference_value':x['reference']['value'],**{k:x[k] for k in fields[-3:]}})
        runner.WRITE(dest/'EVALUATION_COMPLETED.json',{'outputs':{n:runner.SHA(dest/n) for n in ('RESULTS.json','ALL_ENDPOINTS.csv')},'independent_numerical_review':'pending','created_utc':runner.now()})
        return {k:report[k] for k in ('scheduled_authors','scheduled_final_slots','successful_final_executions','physical_attempts')}
    except Exception as e:
        runner.WRITE(dest/'EVALUATION_FAILURE.json',{'type':type(e).__name__,'message':str(e),'no_silent_retry':True});raise
if __name__=='__main__':print(json.dumps(evaluate(),indent=2))
