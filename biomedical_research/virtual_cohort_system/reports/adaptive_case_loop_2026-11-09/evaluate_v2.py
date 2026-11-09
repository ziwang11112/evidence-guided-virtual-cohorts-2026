"""Coverage-preserving evaluation; additive correction before author closure."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import statistics
import sys

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
sys.path.insert(0,str(PROJECT))
from cohort_harness import execution, lifecycle, adaptive_session_v1

REFERENCE=PROJECT/'work/scaleup_2026-11-01/production_release/evaluation/PUBLISHABLE_AGGREGATES.json'
REFERENCE_SHA='889ed586f8bbe3564594c6fd73dd2fbef316037dc36e0629f49f4f30151bbf36'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def write(p,value):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')

def gate():
    for relative,expected in read(ROOT/'DESIGN_LOCK.json').items():
        if sha(ROOT/relative)!=expected:raise ValueError('Original design changed: '+relative)
    amendment=read(ROOT/'EVALUATOR_AMENDMENT.json')
    for relative,expected in amendment['files'].items():
        if sha(ROOT/relative)!=expected:raise ValueError('Amended evaluation code changed: '+relative)
    closure=read(ROOT/'AUTHOR_CLOSED.json')
    if closure['status']!='author_finished_no_further_revision':raise ValueError('Author not closed')
    bundle=Path(closure['bundle'])
    actual={p.relative_to(bundle).as_posix() for p in bundle.rglob('*') if p.is_file()}
    if actual!=set(closure['files']):raise ValueError('Closed bundle inventory changed')
    for relative,expected in closure['files'].items():
        if sha(bundle/relative)!=expected:raise ValueError('Closed bundle changed: '+relative)
    summary=adaptive_session_v1.verify_session(bundle)
    if summary['status']!='completed' or summary['pending'] is not None or summary!=closure['session']:
        raise ValueError('Closed session differs from verified live session')
    # This verifies controller/adapter/transitive dependency bytes before imports.
    for candidate in closure['candidates']:lifecycle.verify_candidate(bundle,candidate)
    for run in closure['runs']:execution.verify_execution(bundle,run)
    if sha(REFERENCE)!=REFERENCE_SHA:raise ValueError('Existing aggregate reference changed')
    return closure,bundle

def contract(protocol):
    result={'analyses':[{'id':x['id'],'unit':x['analysis_unit']} for x in protocol['required_analyses']],
            'diagnostics':protocol['required_diagnostics']}
    if len(result['analyses'])!=3 or len(result['diagnostics'])!=23:raise ValueError('Endpoint plan changed')
    return result

def references(source,plan):
    result={}
    for category,items in plan.items():
        for item in items:
            r=None;interval=None
            if category=='analyses':
                raw=source['estimands'][item['id']]
                if raw['unit']!=item['unit']:raise ValueError('Reference unit mismatch')
                r=raw['estimate'];interval=raw.get('interval')
            else:
                for column in ('total_cholesterol','hdl_cholesterol'):
                    if item['id']==column+'.sd_sample':r=source['metric_denominators'][column]['sample_sd']
            if r is not None and not finite(r):raise ValueError('Nonfinite reference')
            result[item['id']]={'reference_value':r,'reference_interval':interval}
    return result

def normalize(payload,plan,refs,failed_reason=None):
    out={}
    for category,items in plan.items():
        rows=[] if payload is None else payload[category]
        if payload is not None and (len(rows)!=len(items) or {x['id'] for x in rows}!={x['id'] for x in items}):
            raise ValueError('Generated endpoint coverage mismatch')
        lookup={x['id']:x for x in rows};out[category]=[]
        for item in items:
            raw=lookup.get(item['id'])
            if raw is not None and raw['unit']!=item['unit']:raise ValueError('Generated unit mismatch')
            available=raw is not None and raw['status']=='computed' and finite(raw['value'])
            if raw is not None and not available and not(raw['status']=='unavailable' and raw['value'] is None):
                raise ValueError('Invalid generated status/value')
            v=float(raw['value']) if available else None;r=refs[item['id']]['reference_value']
            out[category].append({**item,'value':v,'status':'computed' if available else 'unavailable',
                'reason':None if available else failed_reason or 'estimator_not_computable',
                **refs[item['id']],'difference':v-r if available and r is not None else None,
                'comparison':'available' if available and r is not None else 'unavailable'})
    return out

def summarize(runs,candidates,final_candidate,plan,refs):
    stages=[]
    for candidate in candidates:
        selected=[r for r in runs if r['candidate']==candidate]
        row={'candidate':candidate,'n_attempted':len(selected),'n_successful':sum(r['status']=='success' for r in selected),
             'selected_final':candidate==final_candidate,'analyses':[],'diagnostics':[]}
        for category,items in plan.items():
            for item in items:
                vals=[x['value'] for r in selected for x in r[category] if x['id']==item['id'] and x['value'] is not None]
                ref=refs[item['id']];m=statistics.mean(vals) if vals else None
                row[category].append({**item,'status':'computed' if vals else 'unavailable','mean':m,
                    'seed_min':min(vals) if vals else None,'seed_max':max(vals) if vals else None,
                    'n_draws':len(vals),'n_unavailable':len(selected)-len(vals),**ref,
                    'absolute_point_difference':abs(m-ref['reference_value']) if m is not None and ref['reference_value'] is not None else None})
        stages.append(row)
    return stages

def fmt(value):return 'unavailable' if value is None else f'{value:.4f}'
def interval_text(interval):
    if not isinstance(interval,dict) or not finite(interval.get('lower')) or not finite(interval.get('upper')):return 'unavailable'
    return f"[{interval['lower']:.4f}, {interval['upper']:.4f}]"

def main():
    closure,bundle=gate()
    plan=contract(read(ROOT/'PROTOCOL.json'))
    refs=references(read(REFERENCE)['references']['K02'],plan)
    spec=importlib.util.spec_from_file_location('adaptive_final_analysis',ROOT/'generated_analysis.py')
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    runs=[]
    for run_id in closure['runs']:
        receipt=execution.verify_execution(bundle,run_id)
        row={'run_id':run_id,'candidate':receipt['candidate'],'seed':receipt['limits']['seed'],
             'status':receipt['status'],'elapsed_seconds':receipt['elapsed_seconds'],'route':receipt['route'],
             'output_sha256':None,'failure_category':None}
        if receipt['status']=='success':
            output=bundle/'executions'/run_id/'output/generated.csv'
            payload=adapter.analyze(output,bundle/'task.json',bundle/'request.json')
            row['quality']=payload['quality'];row['output_sha256']=sha(output)
            row.update(normalize(payload,plan,refs))
        else:
            row['failure_category']='execution_'+receipt['status']
            row.update(normalize(None,plan,refs,failed_reason=row['failure_category']))
        runs.append(row)
    stages=summarize(runs,closure['candidates'],closure['final_candidate'],plan,refs)
    initial=stages[0];final=next(s for s in stages if s['selected_final'])
    changes=[]
    for category in plan:
        for a,b in zip(initial[category],final[category]):
            delta=b['mean']-a['mean'] if b['mean'] is not None and a['mean'] is not None else None
            distance=(b['absolute_point_difference']-a['absolute_point_difference']) if b['absolute_point_difference'] is not None and a['absolute_point_difference'] is not None else None
            changes.append({'id':a['id'],'category':category,'unit':a['unit'],'final_minus_initial':delta,
                            'change_in_absolute_point_difference':distance})
    result={'scope':'developmental existing case; every attempted version and planned endpoint retained',
            'closure_sha256':sha(ROOT/'AUTHOR_CLOSED.json'),'amendment_sha256':sha(ROOT/'EVALUATOR_AMENDMENT.json'),
            'reference_sha256':REFERENCE_SHA,'runs':runs,'stages':stages,'initial_to_final':changes,
            'uncertainty':'Seed ranges are Monte Carlo variation, not clinical CIs. Reference slope intervals retain their supplied HC3 conditional sensitivity meaning; they are not equivalence margins.',
            'limits':['One adaptive author and an already exposed reference; no new independent clinical confirmation.',
                      'Twenty-one diagnostics have no reference; all remain generated-only.',
                      'No causal attribution of changes to retrieval, skill or feedback; all endpoints retained.',
                      'Repeated direct rows across seeds are one table, not independent draws.']}
    gate();write(ROOT/'EVALUATION.json',result)
    lines=['# Adaptive existing-case evaluation','',result['scope'],'',
           '| Stage | Analysis | Unit | Generated mean [seed range] | Available / attempted | Existing sample [supplied interval] | Absolute point difference |',
           '|---|---|---|---:|---:|---:|---:|']
    for stage in stages:
        for x in stage['analyses']:
            lines.append(f"| {stage['candidate']} | {x['id']} | {x['unit']} | {fmt(x['mean'])} [{fmt(x['seed_min'])}, {fmt(x['seed_max'])}] | {x['n_draws']} / {stage['n_attempted']} | {fmt(x['reference_value'])} {interval_text(x['reference_interval'])} | {fmt(x['absolute_point_difference'])} |")
    lines+=['',result['uncertainty'],'','## Initial to final','',
            '| Analysis | Final minus initial | Change in distance to sample point estimate (negative = closer) |','|---|---:|---:|']
    for x in changes:
        if x['category']=='analyses':lines.append(f"| {x['id']} | {fmt(x['final_minus_initial'])} | {fmt(x['change_in_absolute_point_difference'])} |")
    lines+=['','## Dispersion and coverage','','| Stage | Diagnostic | Unit | Mean | Reference | Available / attempted |','|---|---|---|---:|---:|---:|']
    for s in stages:
        for x in s['diagnostics']:
            if x['reference_value'] is not None or x['id'].endswith('.conditional_rms'):
                lines.append(f"| {s['candidate']} | {x['id']} | {x['unit']} | {fmt(x['mean'])} | {fmt(x['reference_value'])} | {x['n_draws']} / {s['n_attempted']} |")
        unavailable=sum(x['n_unavailable'] for cat in plan for x in s[cat])
        lines+=['',f"{s['candidate']}: {s['n_successful']} successful / {s['n_attempted']} attempted tables; all 26 planned endpoint records per attempt retained; {unavailable} unavailable endpoint values.",'']
    lines+=['## Limits','']+['- '+s for s in result['limits']]
    (ROOT/'EVALUATION.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'stages':len(stages),'successful_runs':sum(r['status']=='success' for r in runs),'retained_runs':len(runs)}))

if __name__=='__main__':main()
