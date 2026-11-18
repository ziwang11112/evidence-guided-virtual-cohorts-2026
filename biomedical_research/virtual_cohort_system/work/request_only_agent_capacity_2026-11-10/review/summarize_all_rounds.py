"""Combine the three completed aggregate EVALUATION files, without scientific reruns.

Only these aggregate JSON files are read. No plan, source, program, API payload,
credential, generated row, patient row or separate reference file is opened.
CSV granularity is one planned seed/endpoint (including every missing result).
"""
from collections import Counter
from datetime import datetime, timezone
import csv
import hashlib
import json
import math
from pathlib import Path

OUT=Path(__file__).resolve().parent
UNIT=OUT.parent
WORK=UNIT.parent
ROUNDS=[('R0','Initial request-only pilot','request_only_agent_pilot_2026-11-10'),
        ('R1','Mechanical interface repair','request_only_agent_repair_2026-11-10'),
        ('R2','Final shared-capacity diagnostic','request_only_agent_capacity_2026-11-10')]
PRIMARY={'PNS':{'bmi_sbp','bmi_dbp','residual_correlation'},
         'lipids':{'K02-HDL-BMI','K02-TC-BMI','K02-LIPID-RESIDUAL'}}
DIAGNOSTICS={'PNS':{'sbp.sd_population','dbp.sd_population','sbp_below_dbp_fraction'},
             'lipids':{'total_cholesterol.sd_sample','hdl_cholesterol.sd_sample','hdl_above_total_fraction'}}


def finite(value):return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
def require(condition,message):
    if not condition:raise ValueError(message)
def close(left,right):return math.isclose(left,right,rel_tol=1e-12,abs_tol=1e-12)
def pick(value,keys):return {k:value.get(k) for k in keys}


def main():
    targets=[OUT/'ALL_ROUNDS.json',OUT/'ALL_ROUNDS.csv']
    require(not any(p.exists() for p in targets),'Combined outputs already exist; refusing overwrite')
    rounds=[];sessions=[];slots=[];summaries=[];endpoint_rows=[];input_hashes={};references={}
    for rid,label,folder in ROUNDS:
        path=WORK/folder/'EVALUATION.json'
        raw=path.read_bytes();payload=json.loads(raw)
        input_hashes[str(path)]=hashlib.sha256(raw).hexdigest()
        outcomes=payload['episodes'];original_slots=payload['slots'];original_summaries=payload['summaries']
        require(len(outcomes)==4 and len(original_slots)==12,'Round must retain four sessions and twelve planned slots')
        require(len({r['episode_id'] for r in outcomes})==4,'Duplicate episode')
        require(len({(r['episode_id'],r['seed']) for r in original_slots})==12,'Duplicate seed slot')
        metadata={}
        for summary in original_summaries:
            eid=summary['episode_id'];pair=(summary['case_id'],summary['arm'])
            require(eid not in metadata or metadata[eid]==pair,'Episode case/arm changes within summaries')
            metadata[eid]=pair
        require(set(metadata.values())=={(case,arm) for case in PRIMARY for arm in ['ordinary','workflow']},'Incomplete case/arm design')
        round_sessions=[];round_slots=[];round_summaries=[]
        for outcome in outcomes:
            eid=outcome['episode_id'];case,arm=metadata[eid];uid=rid+':'+eid
            session={'round_id':rid,'round_label':label,'session_uid':uid,'episode_id':eid,'case_id':case,'arm':arm,
                **pick(outcome,['status','finalized','selected_candidate','unable_reason','calls_reserved','calls_receipted',
                               'requested_tool_actions','tool_usage','known_tariff_cost_usd','accounted_usd','unknown_usage_calls'])}
            session['law_uid']=uid+':'+str(outcome['selected_candidate']) if outcome.get('selected_candidate') else None
            session['constructor_attempts']=1
            session['final_law_selected']=bool(outcome.get('selected_candidate'))
            selected=[s for s in original_slots if s['episode_id']==eid]
            require(len(selected)==3,'Each constructor needs three planned final slots')
            session['planned_final_seed_slots']=3
            session['final_table_status_counts']=dict(Counter(s['status'] for s in selected))
            round_sessions.append(session);sessions.append(session)
            current_summaries=[s for s in original_summaries if s['episode_id']==eid]
            require(len(current_summaries)==6 and {s['analysis_id'] for s in current_summaries}==PRIMARY[case]|DIAGNOSTICS[case],
                    'Missing or duplicate primary/diagnostic endpoint')
            for source in current_summaries:
                endpoint=source['analysis_id'];category='primary' if endpoint in PRIMARY[case] else 'diagnostic'
                ref_key=case+':'+endpoint;ref=source['reference']
                require(ref_key not in references or references[ref_key]==ref,'Reference changes between arms or rounds')
                references[ref_key]=ref
                s={'round_id':rid,'round_label':label,'session_uid':uid,'law_uid':session['law_uid'],
                   'episode_id':eid,'case_id':case,'arm':arm,'category':category,'analysis_id':endpoint,
                   **pick(source,['unit','available_seeds','mean','minimum','maximum','mean_absolute_reference_difference','values']),
                   'reference_key':ref_key,'episode_status':outcome['status']}
                require(len(s['values'])==3 and {v['seed'] for v in s['values']}=={v['seed'] for v in selected},'Summary seed set changed')
                values=[v['value'] for v in s['values'] if finite(v.get('value'))]
                require(len(values)==s['available_seeds'],'Available endpoint denominator mismatch')
                if values:
                    require(close(sum(values)/len(values),s['mean']) and min(values)==s['minimum'] and max(values)==s['maximum'],'Supplied summary arithmetic mismatch')
                    if finite(ref.get('value')):
                        require(close(sum(abs(v-ref['value']) for v in values)/len(values),s['mean_absolute_reference_difference']),'Reference-difference arithmetic mismatch')
                else:
                    require(s['mean'] is None and s['minimum'] is None and s['maximum'] is None and s['mean_absolute_reference_difference'] is None,'Missing results cannot be zero/imputed')
                round_summaries.append(s);summaries.append(s)
            for source in selected:
                require(source['case_id']==case and source['arm']==arm,'Slot metadata mismatch')
                require(source.get('candidate_id')==outcome.get('selected_candidate'),'Slot candidate differs from explicit selection')
                status=source['status'];require(status in {'success','failed','unavailable'},'Unknown table status')
                slot={'round_id':rid,'round_label':label,'session_uid':uid,'law_uid':session['law_uid'],
                    'slot_uid':uid+':seed_'+str(source['seed']),'episode_id':eid,'case_id':case,'arm':arm,
                    **pick(source,['seed','candidate_id','status','reason','error','receipt_sha256','generated_sha256'])}
                if not session['final_law_selected']:
                    require(status=='unavailable','Unselected episode cannot have delivered final table')
                round_slots.append(slot);slots.append(slot)
                for summary in current_summaries:
                    endpoint=summary['analysis_id'];category='primary' if endpoint in PRIMARY[case] else 'diagnostic'
                    estimate=next(v for v in summary['values'] if v['seed']==source['seed'])
                    require(estimate['status']==status,'Endpoint seed status differs from planned slot')
                    value=estimate.get('value');require(value is None or finite(value),'Nonfinite aggregate value')
                    statistic=next((v for group in ['analyses','diagnostics'] for v in (source.get('statistics') or {}).get(group,[]) if v['id']==endpoint),None)
                    if status=='success':
                        require(statistic is not None and statistic.get('value')==value,'Successful slot/summary value mismatch')
                    else:require(value is None,'Failed or unavailable slot has a numerical result')
                    ref=summary['reference'];uncertainty=ref.get('uncertainty') or {}
                    unavailable_reason=(statistic or {}).get('reason') if value is None else None
                    if value is None and not unavailable_reason:
                        unavailable_reason=source.get('reason') or (source.get('error') or {}).get('type') or status
                    endpoint_rows.append({'round_id':rid,'round_label':label,'session_uid':uid,'law_uid':session['law_uid'],
                        'episode_id':eid,'case_id':case,'arm':arm,'episode_status':outcome['status'],
                        'candidate_id':source.get('candidate_id'),'seed':source['seed'],'table_status':status,
                        'category':category,'analysis_id':endpoint,'unit':summary['unit'],'value':value,
                        'endpoint_status':'available' if finite(value) else 'unavailable','unavailable_reason':unavailable_reason,
                        'reference_value':ref.get('value'),'reference_status':ref.get('status'),
                        'reference_uncertainty_kind':uncertainty.get('kind'),'reference_lower':uncertainty.get('lower'),
                        'reference_upper':uncertainty.get('upper'),
                        'seed_mean':summary['mean'],'seed_minimum':summary['minimum'],'seed_maximum':summary['maximum'],
                        'available_seeds':summary['available_seeds'],
                        'mean_absolute_reference_difference':summary['mean_absolute_reference_difference']})
        counts=Counter(s['status'] for s in round_slots)
        require(counts['success']==payload['counts']['successful_tables'] and counts['failed']==payload['counts']['failed_tables']
                and counts['unavailable']==payload['counts']['unavailable_tables'],'Round table counts mismatch')
        require(sum(s['calls_reserved'] for s in round_sessions)==payload['counts']['model_calls'],'Round call count mismatch')
        require(close(sum(s['known_tariff_cost_usd'] for s in round_sessions),payload['costs']['known_tariff_usd']),'Round known cost mismatch')
        require(close(sum(s['accounted_usd'] for s in round_sessions),payload['costs']['accounted_usd']),'Round accounted cost mismatch')
        arms=[]
        for arm in ['ordinary','workflow']:
            ss=[s for s in round_sessions if s['arm']==arm];tt=[s for s in round_slots if s['arm']==arm]
            arms.append({'arm':arm,'constructor_attempts':len(ss),'selected_final_laws':sum(s['final_law_selected'] for s in ss),
                'planned_seed_slots':len(tt),'table_status_counts':dict(Counter(s['status'] for s in tt)),
                'model_calls':sum(s['calls_reserved'] for s in ss),'known_tariff_usd':sum(s['known_tariff_cost_usd'] for s in ss),
                'accounted_usd':sum(s['accounted_usd'] for s in ss)})
        rounds.append({'round_id':rid,'round_label':label,'input_path':str(path),'input_sha256':input_hashes[str(path)],
            'recorded_counts':payload['counts'],'recorded_costs':payload['costs'],
            'constructor_attempts':len(round_sessions),'selected_final_laws':sum(s['final_law_selected'] for s in round_sessions),
            'planned_final_seed_slots':len(round_slots),'terminal_status_counts':dict(Counter(s['status'] for s in round_sessions)),
            'endpoint_summary_rows':len(round_summaries),'primary_summary_rows':sum(s['category']=='primary' for s in round_summaries),
            'diagnostic_summary_rows':sum(s['category']=='diagnostic' for s in round_summaries),
            'by_arm_delivery_and_cost':arms,'recorded_limitations':payload.get('limitations',[])})
    require(len(sessions)==12 and len(slots)==36 and len(summaries)==72 and len(endpoint_rows)==216,'Combined denominators incomplete')
    require(len({s['session_uid'] for s in sessions})==12 and len({s['slot_uid'] for s in slots})==36,'Round identifiers collide')
    table_counts=Counter(s['status'] for s in slots)
    result={'schema_version':1,'created_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Read-only combination of three completed request-only aggregate evaluations; no reexecution or new scientific fit',
        'totals':{'rounds':3,'distinct_cases':2,'constructor_attempts':12,'closed_sessions':12,
            'selected_final_laws':sum(s['final_law_selected'] for s in sessions),'planned_final_seed_slots':36,
            'table_execution_status_counts':dict(table_counts),'endpoint_summary_rows':72,
            'planned_seed_endpoint_rows':216,'available_seed_endpoint_rows':sum(finite(r['value']) for r in endpoint_rows),
            'unavailable_seed_endpoint_rows':sum(r['value'] is None for r in endpoint_rows),
            'model_calls':sum(r['recorded_counts']['model_calls'] for r in rounds),
            'known_tariff_usd':sum(r['recorded_costs']['known_tariff_usd'] for r in rounds),
            'accounted_usd':sum(r['recorded_costs']['accounted_usd'] for r in rounds)},
        'interpretation':{'unit_of_authoring':'One fresh constructor session per round × case × arm; 12 attempts, not 36 independent constructors.',
            'unit_of_sampling':'Three final seeds are draws from each explicitly selected fixed law. Seed means/ranges describe simulation variation.',
            'round_comparison':'Fresh constructors and evidence choices under sequentially changed engineering conditions; descriptive, not paired causal repair or capacity effects.',
            'scientific_assessment':'Successful table execution/selection is operational delivery, not scientific accuracy, validity or overall success.',
            'no_pooling':'No endpoint sum, pooled scientific score, combined effect estimate or superiority test is calculated.',
            'missingness':'Every planned slot and endpoint is retained; unavailable values are JSON null / empty numeric CSV cells, never zero.',
            'reference_role':'The same previously exposed project references are retained, not independent clinical validation.',
            'costs':'Usage-derived tariff estimates and accounted reservations are recorded separately; neither is a provider invoice.',
            'csv_granularity':'One planned seed × endpoint per row (216 rows). Seed summaries repeat as metadata and must not be treated as independent authoring observations.'},
        'input_hashes':input_hashes,'rounds':rounds,'sessions':sessions,'planned_slots':slots,
        'references':references,'endpoint_summaries':summaries,'seed_endpoint_rows':endpoint_rows}
    with targets[0].open('x',encoding='utf-8') as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
    with targets[1].open('x',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(endpoint_rows[0]));writer.writeheader();writer.writerows(endpoint_rows)
    print(json.dumps({'status':'complete','totals':result['totals'],'outputs':[str(p) for p in targets]},indent=2))


if __name__=='__main__':main()
