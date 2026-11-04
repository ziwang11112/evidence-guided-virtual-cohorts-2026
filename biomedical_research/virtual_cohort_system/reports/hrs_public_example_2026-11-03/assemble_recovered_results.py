"""Combine frozen Agent outputs and separately logged corrected comparator.

The invalid original comparator deliveries remain explicit incident artifacts.
"""
from pathlib import Path
import importlib.util
import json

U = Path(__file__).resolve().parent
module_spec=importlib.util.spec_from_file_location('hrs_summaries',U/'summarize.py')
summary_tools=importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(summary_tools)
read,sha=summary_tools.read,summary_tools.sha

def main():
    assert read(U/'GENERATION_CLOSED.json')['attempts_spent']==6
    assert read(U/'recovery_v1/CLOSED.json')['additional_attempts_spent']==3
    parameters=read(U/'recovery_v1/bundle/candidates/native_corrected/model_spec.json')['parameters']
    coefficients=parameters['memory']['coefficients']
    paper=read(U/'sources/HRS_PUBLISHED_REFERENCES.json')
    rows,distributions,statuses,bindings=[],[],[],{}
    for arm in ['native','agent']:
        base=U/'recovery_v1/results' if arm=='native' else U/'results'
        prefix='native_corrected' if arm=='native' else 'agent'
        for seed in [6101,6102,6103]:
            name=f'{prefix}_{seed}';record_path=base/(name+'.evaluation.json')
            record=read(record_path);statuses.append(record)
            bindings[str(record_path.relative_to(U))]=sha(record_path)
            if record['status']!='computed':continue
            path=base/(name+'.native.json');fit=read(path)
            assert sha(path)==record['native_json_sha256']
            bindings[str(path.relative_to(U))]=sha(path)
            for effect in fit['fixed_effects']:
                term=effect['term']
                rows.append({'arm':arm,'seed':seed,'term':term,
                    **{k:effect[k] for k in ['estimate','se','wald_lower','wald_upper']},
                    'exported_coefficient':coefficients[term]['estimate'],
                    'exported_source_se':coefficients[term]['standard_error'],
                    'published_original_coefficient':paper['table3'][term]['original'][0],
                    'published_synthetic_coefficient':paper['table3'][term]['synthetic'][0]})
            distributions.extend([{'arm':arm,'seed':seed,**r} for r in summary_tools.diagnostics(fit,paper)])
    invalid=[]
    for seed in [6101,6102,6103]:
        name=f'native_{seed}'
        record=read(U/'results'/(name+'.evaluation.json'))
        fit=read(U/'results'/(name+'.native.json'))
        invalid.append({'run_id':name,'status':record['status'],'error':fit.get('error'),
                        'messages':fit.get('messages'),'table2_diagnostics':fit.get('table2_diagnostics'),
                        'reason_excluded_from_method_comparison':'Incorrect source-parser coefficient block; our implementation failure, not Filshtein method performance.',
                        'native_json_sha256':sha(U/'results'/(name+'.native.json'))})
    result={'scope':'Shared published HRS source-law reconstruction; corrected comparator technical recovery explicitly distinguished from original frozen Agent outputs.',
        'counts':{'initial_physical_generations':6,'additional_technical_recovery_generations':3,
                  'total_physical_generations':9,'invalid_initial_comparator_tables':3,
                  'valid_comparison_tables':sum(x['status']=='computed' for x in statuses),
                  'computed_fits':sum(x['status']=='computed' for x in statuses),
                  'gls_passes':sum(x.get('gls_status')=='pass' and x.get('gls_returncode')==0 for x in statuses),
                  'subjects_per_table':11509,'visits_per_table':46036,
                  'new_source_participant_records':0},
        'statuses':statuses,'invalid_original_comparator':invalid,
        'fixed_effects':summary_tools.summaries(rows,['arm','term'],'estimate',
            ['exported_coefficient','published_original_coefficient','published_synthetic_coefficient']),
        'distributions':summary_tools.summaries(distributions,['arm','metric'],'estimate',
            ['original_reference','published_synthetic_reference']),
        'bindings':bindings,
        'precision_scope':'Three fixed-seed draws per construction; no aggregate superiority test, new target validation or full source/model uncertainty calculation. Report both supplied model consistency and original-paper distribution differences.'}
    folder=U/'summary';folder.mkdir(exist_ok=True)
    with (folder/'AGGREGATE_RESULTS.json').open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    summary_tools.csv_out(folder/'fixed_effects_all_seeds.csv',rows)
    summary_tools.csv_out(folder/'fixed_effects_summary.csv',result['fixed_effects'])
    summary_tools.csv_out(folder/'distributions_all_seeds.csv',distributions)
    summary_tools.csv_out(folder/'distributions_summary.csv',result['distributions'])
    print(json.dumps(result['counts']))

if __name__=='__main__':main()
