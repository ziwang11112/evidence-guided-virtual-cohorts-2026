"""One bounded final evaluation after global closure; never a feedback tool.

Imports and --help do not open clinical reference files. All 72 scheduled final
slots are retained, including abandoned and failed constructions. No p-values,
pooled cross-estimand scores, equivalence verdicts or automatic superiority
claims are produced. Cases retain their own units and estimators.
"""
from __future__ import annotations
import argparse
import csv
import importlib.util
import json
import math
from pathlib import Path
from statistics import mean

import main_session_v1 as session

UNIT = Path(__file__).resolve().parents[1]
PROJECT = UNIT.parents[1]
DEFAULT_BINDINGS = Path(__file__).with_name('reference_bindings.json')


def finite(value):
    return isinstance(value,(float,int)) and not isinstance(value,bool) and math.isfinite(value)


def direction(value):
    return None if not finite(value) else ('positive' if value>0 else 'negative' if value<0 else 'zero')


def value_at(obj,path):
    try:
        for key in path:
            obj=obj[key]
    except (KeyError,TypeError,IndexError):
        return None
    return obj


def interval_record(raw,meaning):
    available=isinstance(raw,dict) and finite(raw.get('lower')) and finite(raw.get('upper'))
    if available:
        available=raw['lower']<=raw['upper'] and raw.get('status','available')=='available'
    return {'status':'available' if available else 'unavailable',
       'lower':float(raw['lower']) if available else None,
       'upper':float(raw['upper']) if available else None,
       'direction':('positive' if raw['lower']>0 else 'negative' if raw['upper']<0 else 'includes_zero') if available else None,
       'meaning':meaning,'equivalence_margin':False}


def _require_bound_release_file(release,path):
    path=Path(path).resolve()
    matches=[x for x in release['artifacts'] if Path(x['path']).resolve()==path]
    session.require(len(matches)==1,'Evaluator input is not uniquely bound in release: '+str(path))
    session.verify_bound(matches[0])


def load_references(bindings):
    """Only called by evaluate after the all-cases/all-arms closure barrier."""
    references={}
    for case,spec in bindings['cases'].items():
        artifact=spec['artifact']
        path=(PROJECT/artifact['path']).resolve()
        session.require(path.is_relative_to(PROJECT.resolve()),'Reference path escapes project')
        session.verify_bound({'path':str(path),'sha256':artifact['sha256']})
        report=session.READ(path)
        endpoints={}
        for category in ('analyses','diagnostics'):
            for item in spec[category]:
                value=value_at(report,item['value_path'])
                endpoints[item['id']]={
                  'value':float(value) if finite(value) else None,'unit':item['unit'],
                  'status':'available' if finite(value) else 'unavailable',
                  'interval':interval_record(value_at(report,item['interval_path']) if item.get('interval_path') else None,
                                            spec['reference_uncertainty_meaning']),
                  'interpretation':'Previously exposed sample reference, not known population truth.'}
        references[case]=endpoints
    return references


def missing_payload(spec,reason):
    return {category:[{'id':item['id'],'value':None,'unit':item['unit'],
             'status':'unavailable','reason':reason} for item in spec[category]]
            for category in ('analyses','diagnostics')}


def validate_payload(payload,spec):
    session.require(isinstance(payload,dict),'Generated provider must return an object')
    session.require(set(payload)<={'analyses','diagnostics','quality','n'},'Undeclared generated provider fields')
    for category in ('analyses','diagnostics'):
        rows=payload.get(category)
        session.require(isinstance(rows,list),'Provider category must be a list')
        expected={x['id']:x for x in spec[category]}
        session.require(len(rows)==len(expected) and {r.get('id') for r in rows}==set(expected),
                        'Missing/duplicate/extra generated '+category)
        for row in rows:
            session.require(set(row)<={'id','value','unit','status','n','rank','reason'},'Undeclared endpoint fields')
            session.require(row['unit']==expected[row['id']]['unit'],'Case-specific endpoint unit changed')
            session.require(row['status'] in ('computed','unavailable'),'Unknown endpoint status')
            session.require((row['status']=='computed' and finite(row['value'])) or
                            (row['status']=='unavailable' and row['value'] is None),'Status/value mismatch')


def add_reference(payload,reference):
    result={}
    for category in ('analyses','diagnostics'):
        result[category]=[]
        for row in payload[category]:
            ref=reference[row['id']]
            has_value=row['status']=='computed' and finite(row['value'])
            comparable=has_value and finite(ref['value'])
            value=float(row['value']) if has_value else None
            result[category].append({**row,'value':value,'generated_direction':direction(value),
              'reference_value':ref['value'],'reference_direction':direction(ref['value']),
              'reference_interval':ref['interval'],
              'signed_discrepancy':value-ref['value'] if comparable else None,
              'absolute_discrepancy':abs(value-ref['value']) if comparable else None,
              'comparison_status':'computed' if comparable else 'unavailable'})
    return result


def collect_slots(release,bindings,references):
    """Read every final slot, including null records for never attempted slots."""
    slots=[]
    for construction in release['constructions']:
        running=session.Session(construction['session_root'])
        contract=running.contract
        case=contract['case_id']
        spec=bindings['cases'][case]
        closed=running.selected('closed')[0]
        final_attempts=[e for e in running.selected('attempt') if e['purpose']=='final']
        provider_error=None
        try:
            provider_spec=importlib.util.spec_from_file_location('main_final_provider_'+construction['id'],contract['provider'])
            provider=importlib.util.module_from_spec(provider_spec)
            provider_spec.loader.exec_module(provider)
        except Exception as exc:
            provider_error=type(exc).__name__+': '+str(exc)
        for seed in session.BUDGET['final_seeds']:
            matches=[a for a in final_attempts if a['seed']==seed]
            session.require(len(matches)<=1,'Duplicated final slot')
            base={'constructor_id':construction['id'],'case_id':case,
                  'information_condition':contract['information_condition'],
                  'constructor_kind':contract['constructor_kind'],'seed':seed,
                  'scheduled':True,'closure_status':closed['status'],'candidate':None,
                  'run_id':None,'execution_status':'not_attempted','analysis_status':'unavailable',
                  'output_sha256':None,'error':None,'quality':None,'n':None}
            if not matches:
                reason='Final slot not attempted: '+closed.get('reason',closed['status'])
                payload=missing_payload(spec,reason)
                base['error']={'type':'unattempted_final_slot','message':reason}
            else:
                attempt=matches[0]
                base.update(candidate=attempt['candidate'],run_id=attempt['run_id'])
                results=[r for r in running.selected('result') if r['attempt_index']==attempt['index']]
                session.require(len(results)<=1,'Duplicated final result')
                outcome=results[0] if results else {'status':'missing_result','error':{'type':'missing_result','message':'Final attempt has no retained result'}}
                base['execution_status']=outcome['status']
                if outcome['status']!='success':
                    base['error']=outcome.get('error') or {'type':'execution_failure','message':outcome['status']}
                    payload=missing_payload(spec,'Execution unavailable: '+outcome['status'])
                else:
                    try:
                        # Generation succeeded even if a later analysis provider
                        # fails. Preserve that output identity independently.
                        base['output_sha256']=session.SHA(running.bundle/'executions'/attempt['run_id']/'output/generated.csv')
                        if provider_error:
                            raise RuntimeError('Provider import failed: '+provider_error)
                        payload=provider.evaluate_generated(running.bundle,attempt['candidate'],attempt['run_id'],Path(contract['profile']))
                        validate_payload(payload,spec)
                        base.update(quality=payload.get('quality'),n=payload.get('n'))
                        base['analysis_status']='complete' if all(x['status']=='computed' for category in ('analyses','diagnostics') for x in payload[category]) else 'incomplete'
                    except Exception as exc:
                        # No retry or alternative estimator. Keep the slot and
                        # all prespecified endpoints visibly unavailable.
                        base['analysis_status']='provider_error'
                        base['error']={'type':type(exc).__name__,'message':str(exc)}
                        payload=missing_payload(spec,'Provider error: '+type(exc).__name__+': '+str(exc))
            base.update(add_reference(payload,references[case]))
            slots.append(base)
    session.require(len(slots)==72,'Every one of the 72 final slots must be represented')
    session.require(len({(r['constructor_id'],r['seed']) for r in slots})==72,'Duplicate scheduled slot')
    return slots


def summarize(slots,bindings,*,seeds=(5101,5102,5103)):
    """Descriptive constructor and E1-minus-E0 summaries; no inferential tests."""
    constructors=[]
    identities={r['constructor_id'] for r in slots}
    for identity in sorted(identities):
        selected=[r for r in slots if r['constructor_id']==identity]
        first=selected[0]
        session.require(len({r['seed'] for r in selected})==len(selected),'Duplicate seed in summary')
        session.require({r['seed'] for r in selected}==set(seeds),'Explicit null slots required for every scheduled seed')
        endpoint_summaries=[]
        for item in bindings['cases'][first['case_id']]['analyses']:
            rows=[next(x for x in r['analyses'] if x['id']==item['id']) for r in selected]
            values=[r['value'] for r in rows if finite(r['value']) and r['status']=='computed']
            absolute=[r['absolute_discrepancy'] for r in rows if finite(r['absolute_discrepancy'])]
            complete=len(absolute)==len(seeds)
            endpoint_summaries.append({'id':item['id'],'unit':item['unit'],'scheduled_seeds':len(seeds),
              'available_values':len(values),'available_discrepancies':len(absolute),'complete':complete,
              'mean_absolute_discrepancy':mean(absolute) if complete else None,
              'available_value_mean_absolute_discrepancy':mean(absolute) if absolute else None,
              'mean_effect':mean(values) if values else None,
              'seed_effect_range':[min(values),max(values)] if values else None,
              'seed_directions':[r['generated_direction'] for r in rows],
              'summary_status':'complete' if complete else 'incomplete_available_values_only'})
        constructors.append({'constructor_id':identity,'case_id':first['case_id'],
          'information_condition':first['information_condition'],'constructor_kind':first['constructor_kind'],
          'scheduled_final_slots':len(seeds),'successful_executions':sum(r['execution_status']=='success' for r in selected),
          'complete_analysis_slots':sum(r['analysis_status']=='complete' for r in selected),
          'endpoints':endpoint_summaries})
    contrasts=[]
    for case,spec in bindings['cases'].items():
        for endpoint in spec['analyses']:
            arms={}
            for condition in ('E0','E1'):
                members=[c for c in constructors if c['case_id']==case and c['information_condition']==condition and c['constructor_kind']=='agent']
                details=[next(x for x in m['endpoints'] if x['id']==endpoint['id']) for m in members]
                available=[d['available_value_mean_absolute_discrepancy'] for d in details if finite(d['available_value_mean_absolute_discrepancy'])]
                complete=len(members)==5 and all(d['complete'] for d in details)
                arms[condition]={'scheduled_constructors':5,'represented_constructors':len(members),
                  'constructors_with_complete_endpoint':sum(d['complete'] for d in details),
                  'constructors_with_any_discrepancy':len(available),'complete':complete,
                  'mean_constructor_mean_absolute_discrepancy':mean(available) if complete else None,
                  'incomplete_available_value_mean':mean(available) if available and not complete else None,
                  'available_value_mean':mean(available) if available else None}
            complete=all(a['complete'] for a in arms.values())
            available=all(a['available_value_mean'] is not None for a in arms.values())
            difference=arms['E1']['available_value_mean']-arms['E0']['available_value_mean'] if available else None
            contrasts.append({'case_id':case,'endpoint':endpoint['id'],'unit':endpoint['unit'],'arms':arms,
              'status':'complete_descriptive_comparison' if complete else 'incomplete_no_complete_arm_advantage_claim',
              'E1_minus_E0_mean_absolute_discrepancy':difference if complete else None,
              'incomplete_available_value_contrast':difference if not complete else None,
              'complete_arm_comparison_available':complete,
              'interpretation':'Added supplied-information descriptive contrast; no equivalence or isolated algorithmic superiority inference.'})
    return {'construction_summaries':constructors,'agent_information_contrasts':contrasts,
       'statistical_references':[c for c in constructors if c['constructor_kind']=='statistical'],
       'statistical_comparison_note':'One prescribed statistical construction per arm versus five Agent constructions; descriptive and asymmetric, not a general superiority test.',
       'pooling':'No cross-estimand or cross-case accuracy score.'}


def _write_new(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False)
        stream.write('\n')


def evaluate(release_path,output_dir,bindings_path=DEFAULT_BINDINGS):
    release_path=Path(release_path).resolve()
    release=session.READ(release_path)
    # MUST occur before reference metadata dispatch, provider import or any
    # reference aggregate load. A local per-case closure is insufficient.
    closure=session.require_campaign_closed(release)
    _require_bound_release_file(release,Path(__file__))
    _require_bound_release_file(release,bindings_path)
    bindings=session.READ(bindings_path)
    session.require(bindings['schema_version']=='main_reference_bindings_v1','Unknown reference-binding schema')
    session.require(set(bindings['cases'])=={'CHNS2009','ENSANUT2018'},'Both fixed cases required')
    destination=Path(output_dir).resolve()
    session.require(not destination.exists(),'Evaluation output exists; no scientific re-evaluation or overwrite')
    destination.mkdir(parents=True)
    _write_new(destination/'EVALUATION_ATTEMPT.json',{'status':'started','created_utc':session.now(),
        'release':session.bound(release_path),'reference_bindings':session.bound(bindings_path),
        'global_closure_verified':True,'closures':closure,'retry_budget':0})
    try:
        references=load_references(bindings)
        slots=collect_slots(release,bindings,references)
        summaries=summarize(slots,bindings,seeds=session.BUDGET['final_seeds'])
        session.require_campaign_closed(release)
        session.require(session.READ(release_path)==release,'Release changed during evaluation')
        for spec in bindings['cases'].values():
            session.verify_bound({'path':str(PROJECT/spec['artifact']['path']),'sha256':spec['artifact']['sha256']})
        report={'schema_version':'main_final_evaluation_v1','scope':'Two exposed developmental references; zero new target tuning or author feedback',
          'created_utc':session.now(),'release_sha256':session.SHA(release_path),
          'reference_binding_sha256':session.SHA(bindings_path),'planned_constructions':24,'scheduled_final_slots':72,
          'successful_executions':sum(r['execution_status']=='success' for r in slots),
          'complete_analysis_slots':sum(r['analysis_status']=='complete' for r in slots),
          'unique_successful_table_contents':len({r['output_sha256'] for r in slots if r['output_sha256']}),
          'references':references,'all_scheduled_slots':slots,**summaries,
          'clinical_inference':'Synthetic rows/seeds are not independent clinical replications. Reference intervals are not acceptance margins.'}
        _write_new(destination/'RESULTS.json',report)
        fields=['constructor_id','case_id','information_condition','constructor_kind','seed','execution_status','analysis_status','category','id','value','unit','status','reason','generated_direction','reference_value','reference_direction','reference_lower','reference_upper','signed_discrepancy','absolute_discrepancy','comparison_status']
        with (destination/'ALL_ENDPOINTS.csv').open('x',encoding='utf-8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields); writer.writeheader()
            for slot in slots:
                for category in ('analyses','diagnostics'):
                    for endpoint in slot[category]:
                        row={key:slot[key] for key in fields[:7]}
                        row.update({key:endpoint.get(key) for key in fields[8:] if key not in ('reference_lower','reference_upper')})
                        row.update(category=category,reference_lower=endpoint['reference_interval']['lower'],reference_upper=endpoint['reference_interval']['upper'])
                        writer.writerow(row)
        _write_new(destination/'EVALUATION_COMPLETED.json',{'status':'completed','completed_utc':session.now(),
          'outputs':{name:session.SHA(destination/name) for name in ('RESULTS.json','ALL_ENDPOINTS.csv')},
          'independent_recomputation':'pending; this evaluator does not certify its own arithmetic'})
        return {'status':'completed','scheduled_final_slots':72,'successful_executions':report['successful_executions'],'complete_analysis_slots':report['complete_analysis_slots']}
    except Exception as exc:
        _write_new(destination/'EVALUATION_FAILURE.json',{'status':'failed','error_type':type(exc).__name__,'message':str(exc),'no_retry_or_protocol_change_authorized':True})
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(evaluate(args.release,args.output)))
