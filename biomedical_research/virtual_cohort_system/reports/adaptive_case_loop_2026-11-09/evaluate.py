"""Post-author-closure evaluation of every attempted stage and fixed seed.

Only an existing frozen aggregate clinical reference is loaded. No clinical
patient table is read. Generator source is never imported or executed here.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import statistics
import sys

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
sys.path.insert(0,str(PROJECT))
from cohort_harness import execution, lifecycle

REFERENCE=PROJECT/'work/scaleup_2026-11-01/production_release/evaluation/PUBLISHABLE_AGGREGATES.json'
REFERENCE_SHA='889ed586f8bbe3564594c6fd73dd2fbef316037dc36e0629f49f4f30151bbf36'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,value):
    with Path(p).open('x',encoding='utf-8') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n')

def gate():
    closure=read(ROOT/'AUTHOR_CLOSED.json')
    if closure['status']!='author_finished_no_further_revision':raise ValueError('Author not closed')
    bundle=Path(closure['bundle'])
    actual={p.relative_to(bundle).as_posix() for p in bundle.rglob('*') if p.is_file()}
    if actual!=set(closure['files']):raise ValueError('Closed bundle file inventory changed')
    for relative,expected in closure['files'].items():
        path=bundle/relative
        if sha(path)!=expected:raise ValueError('Closure artifact changed: '+relative)
    for candidate in closure['candidates']:
        lifecycle.verify_candidate(bundle,candidate)
    for run in closure['runs']:
        execution.verify_execution(bundle,run)
    if sha(REFERENCE)!=REFERENCE_SHA:raise ValueError('Existing aggregate reference changed')
    return closure,bundle

def main():
    closure,bundle=gate()
    # Reference access occurs only after the closure gate.
    reference=read(REFERENCE)['references']['K02']
    spec=importlib.util.spec_from_file_location('adaptive_final_analysis',ROOT/'generated_analysis.py')
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    runs=[]
    for run_id in closure['runs']:
        receipt=execution.verify_execution(bundle,run_id)
        item={'run_id':run_id,'candidate':receipt['candidate'],'seed':receipt['limits']['seed'],
              'status':receipt['status'],'elapsed_seconds':receipt['elapsed_seconds'],
              'route':receipt['route'],'output_sha256':None,'analyses':[],'diagnostics':[]}
        if receipt['status']!='success':
            item['error']=receipt['error'];runs.append(item);continue
        output=bundle/'executions'/run_id/'output/generated.csv'
        payload=adapter.analyze(output,bundle/'task.json',bundle/'request.json')
        item['output_sha256']=sha(output)
        item['quality']=payload['quality']
        for category in ('analyses','diagnostics'):
            for value in payload[category]:
                r=None;uncertainty=None
                if category=='analyses':
                    raw=reference['estimands'][value['id']]
                    if raw['unit']!=value['unit']:raise ValueError('Reference unit mismatch')
                    r=raw['estimate'];uncertainty=raw.get('interval')
                else:
                    for column in ('total_cholesterol','hdl_cholesterol'):
                        if value['id']==column+'.sd_sample':
                            r=reference['metric_denominators'][column]['sample_sd']
                v=value['value']
                item[category].append({**value,'reference_value':r,'reference_interval':uncertainty,
                    'difference':v-r if v is not None and r is not None else None,
                    'comparison':'available' if r is not None else 'no_reference_available'})
        runs.append(item)
    summaries=[]
    for candidate in closure['candidates']:
        selected=[r for r in runs if r['candidate']==candidate]
        row={'candidate':candidate,'n_attempted':len(selected),'n_successful':sum(r['status']=='success' for r in selected),
             'selected_final':candidate==closure['final_candidate'],'analyses':[],'diagnostics':[]}
        for category in ('analyses','diagnostics'):
            ids=list(dict.fromkeys(x['id'] for r in selected for x in r[category]))
            for key in ids:
                values=[x for r in selected for x in r[category] if x['id']==key and x['value'] is not None]
                if not values:continue
                v=[x['value'] for x in values];first=values[0];r=first['reference_value'];m=statistics.mean(v)
                row[category].append({'id':key,'unit':first['unit'],'mean':m,'seed_min':min(v),'seed_max':max(v),
                    'n_draws':len(v),'reference_value':r,'reference_interval':first['reference_interval'],
                    'absolute_point_difference':abs(m-r) if r is not None else None})
        summaries.append(row)
    result={'scope':'developmental existing case; all attempted versions retained','closure_sha256':sha(ROOT/'AUTHOR_CLOSED.json'),
            'reference_sha256':REFERENCE_SHA,'runs':runs,'stages':summaries,
            'uncertainty':'Generated seed ranges represent simulation variation, not clinical uncertainty. Reference intervals retain their original conditional sensitivity meaning, not equivalence limits.',
            'limits':['One adaptive author; no causal attribution to skills, retrieval or revision.',
                      'Existing exposed aggregate reference; no new independent patient validation.',
                      'Twenty-one diagnostics have no aggregate reference and remain generated-only.',
                      'Source transfer, study uncertainty and target composition are not identified by generating more rows.',
                      'Direct-row outputs repeated across seeds are one table, not independent generated draws.']}
    gate()
    write(ROOT/'EVALUATION.json',result)
    rows=['# Adaptive existing-case evaluation','',result['scope'],'',
          '| Stage | Analysis | Generated mean [seed range] | Existing reference | Absolute point difference |',
          '|---|---|---:|---:|---:|']
    for stage in summaries:
        for x in stage['analyses']:
            rows.append(f"| {stage['candidate']} | {x['id']} | {x['mean']:.4f} [{x['seed_min']:.4f}, {x['seed_max']:.4f}] | {x['reference_value']:.4f} | {x['absolute_point_difference']:.4f} |")
    rows+=['',result['uncertainty'],'']+['- '+x for x in result['limits']]
    (ROOT/'EVALUATION.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    print(json.dumps({'stages':len(summaries),'successful_runs':sum(r['status']=='success' for r in runs),'retained_runs':len(runs)}))

if __name__=='__main__':main()
