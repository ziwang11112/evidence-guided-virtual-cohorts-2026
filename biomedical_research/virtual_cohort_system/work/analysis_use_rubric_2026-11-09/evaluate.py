"""Postclosure controlled repair report; deliberately no real-reference input."""
from pathlib import Path
import importlib.util
import json
import statistics
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0,str(PROJECT))
from cohort_harness import adaptive_session_v2 as session, execution, lifecycle as lc

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))

def check_stages(candidates,baseline,cap):
    if not candidates or candidates[0]!=baseline or len(candidates)>cap or len(candidates)!=len(set(candidates)):
        raise ValueError('The unchanged baseline must be the first submitted stage, without duplicate/excess stages')

def gate():
    spec=importlib.util.spec_from_file_location('repair_arithmetic_gate',HERE/'independent_recompute.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    closed,protocol,bundle=module.closure_gate(HERE)
    for name,digest in read(HERE/'DESIGN_LOCK.json')['files'].items():
        if lc.sha256(HERE/name)!=digest:raise ValueError('Design file changed: '+name)
    summary=session.verify_session(bundle)
    if summary['status']!='completed' or summary['pending'] is not None:raise ValueError('Session not completed')
    with session.ledger._operation(bundle/session.DIRECTORY,'repair-report-inspect'):
        state=session._load(bundle,bundle/session.DIRECTORY)
    stages=closed['candidates'];check_stages(stages,protocol['baseline_candidate'],protocol['candidate_cap'])
    expected={(c,s) for c in stages for s in protocol['seeds']}
    actions=[x['action'] for x in state['actions'].values()]
    actual=[(a['candidate'],a['seed']) for a in actions if a['kind']=='execute']
    runs=[a['run_id'] for a in actions if a['kind']=='execute']
    selected=[a['final_candidate'] for a in actions if a['kind']=='finish']
    if stages!=summary['candidates'] or len(actual)!=len(expected) or set(actual)!=expected:raise ValueError('Stage/seed coverage differs')
    if sorted(runs)!=closed['runs'] or selected!=[closed['final_candidate']]:raise ValueError('Closed selection or runs differ')
    for name,digest in protocol['baseline_science'].items():
        if lc.sha256(bundle/protocol['baseline_candidate']/name)!=digest:raise ValueError('Baseline scientific law changed')
    return closed,protocol,bundle,state

def one_analysis(state,run_id,adapter):
    entries=[e for e in state['actions'].values() if e['action']['kind']=='analysis' and e['action']['run_id']==run_id and e['action']['adapter']==adapter]
    if len(entries)!=1 or entries[0]['result']['status']!='success':raise ValueError('Missing/duplicate/failed adapter action')
    return entries[0]['result']['result']['result']

def endpoints(payload,protocol):
    result={}
    for category,items in [('analyses',protocol['required_analyses']),('diagnostics',protocol['required_diagnostics'])]:
        expected={i['id']:i.get('unit',i.get('analysis_unit')) for i in items}
        if payload is None:
            result[category]=[{'id':key,'unit':unit,'value':None,'status':'unavailable','reason':'execution failed'} for key,unit in expected.items()]
            continue
        values=payload[category]
        if len(values)!=len(expected) or {v['id']:v['unit'] for v in values}!=expected:raise ValueError('Requested endpoint coverage differs')
        result[category]=[{**v,'status':'computed' if v['value'] is not None else 'unavailable'} for v in values]
    return result

def summarize(runs,candidates,selected):
    stages=[]
    for c in candidates:
        subset=[r for r in runs if r['candidate']==c]
        stage={'candidate':c,'selected_final':c==selected,'n_attempted':len(subset),'n_successful':sum(r['status']=='success' for r in subset)}
        for category in ('analyses','diagnostics'):
            stage[category]=[]
            for item in subset[0][category]:
                values=[next(v['value'] for v in r[category] if v['id']==item['id']) for r in subset]
                finite=[v for v in values if v is not None]
                stage[category].append({'id':item['id'],'unit':item['unit'],'mean':statistics.mean(finite) if finite else None,
                    'seed_min':min(finite) if finite else None,'seed_max':max(finite) if finite else None,'available':len(finite),'attempted':len(values)})
        stage['coherence']=[{'run_id':r['run_id'],'seed':r['seed'],'analysis_status':r.get('use_status'),
                             'rules':r.get('coherence'),'errors':r.get('use_errors',[])} for r in subset]
        stage['declared_evidence_coverage']=[{'run_id':r['run_id'],'coverage':r.get('evidence_coverage')} for r in subset]
        stages.append(stage)
    return stages

def main():
    closed,protocol,bundle,state=gate();runs=[]
    for run_id in closed['runs']:
        receipt=execution.verify_execution(bundle,run_id)
        row={'run_id':run_id,'candidate':receipt['candidate'],'seed':receipt['limits']['seed'],'status':receipt['status'],'route':receipt['route'],'output_sha256':None}
        if receipt['status']=='success':
            payload=one_analysis(state,run_id,'generated');use=one_analysis(state,run_id,'analysis_use')
            row.update(output_sha256=lc.sha256(bundle/'executions'/run_id/'output/generated.csv'),quality=payload['quality'],
                       use_status=use['status'],use_errors=use['errors'],coherence=use['coherence'],evidence_coverage=use['evidence_coverage'],use_bindings=use['bindings'])
            if use['bindings']['output_sha256']!=row['output_sha256']:raise ValueError('Use report output binding differs')
            row.update(endpoints(payload,protocol))
        else: row.update(endpoints(None,protocol))
        runs.append(row)
    stages=summarize(runs,closed['candidates'],closed['final_candidate'])
    baseline=stages[0]; final=next(s for s in stages if s['selected_final'])
    changes=[]
    for category in ('analyses','diagnostics'):
        for a,b in zip(baseline[category],final[category]):
            changes.append({'id':a['id'],'unit':a['unit'],'category':category,'baseline_mean':a['mean'],'selected_mean':b['mean'],
                            'selected_minus_baseline':b['mean']-a['mean'] if a['mean'] is not None and b['mean'] is not None else None})
    feedback=[]
    for e in state['actions'].values():
        if e['action']['kind']=='feedback' and e['result']['status']=='success':
            r=e['result']['result'];feedback.append({'run_id':e['action']['run_id'],
               'strict_computable':r['strict']['n_computable'],'strict_unavailable':r['strict']['n_not_computable'],
               'descriptive_computable':r['descriptive']['n_computable'],'descriptive_unavailable':r['descriptive']['n_not_computable'],
               'checks':[{k:v for k,v in c.items() if k in {'id','calculation','difference','calculation_status','source_definition_match','unavailable_reason'}} for c in r['descriptive']['checks']]})
    result={'scope':'Controlled coherence repair and declared scientific-use coverage; no target-reference comparison',
       'closure_sha256':lc.sha256(HERE/'AUTHOR_CLOSED.json'),'protocol_sha256':lc.sha256(HERE/'PROTOCOL.json'),
       'reference_read':False,'runs':runs,'stages':stages,'selected_minus_baseline':changes,'source_feedback':feedback,
       'controller_usage':state['usage'],'action_outcomes':[{'id':key,'kind':e['action']['kind'],'status':e['result']['status']} for key,e in state['actions'].items()],
       'limits':['New underlying-concentration use claim; historical measured-output metadata are provenance.',
                 'Numerical coherence and declared evidence links do not establish scientific validity or improved clinical accuracy.',
                 'Preservation changes are descriptive; no clinical equivalence margin supplied.',
                 'Common seed labels do not imply paired people or latent draws after a changed algorithm.',
                 'One author and one development case do not establish general or causal Agent advantage.']}
    gate()
    with (HERE/'EVALUATION.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'stages':len(stages),'runs':len(runs),'reference_read':False,'controller_usage':state['usage']}))

if __name__=='__main__':main()
