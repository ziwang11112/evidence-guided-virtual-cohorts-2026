"""Summarize completed real-source runs without inspecting a target dataset."""
from pathlib import Path
from collections import defaultdict
import csv
import json

P=Path(__file__).resolve().parents[2]


def summarize():
    output=P/'work/m13/source_results'
    output.mkdir(exist_ok=False)
    summaries=[];rows=[]
    for name in ['build01','build02']:
        b=P/'work/m13'/name
        r=json.loads((b/'cal/initial_fit/result.json').read_text())
        chosen=r['selected_trial'];assert chosen is not None
        result={'builder':name,'selected_trial':chosen,'usage':r['usage'],
                'status':r['status'],'stop_reason':r['stop_reason'],
                'initial_parameters':r['trials'][0]['parameters'],
                'selected_parameters':r['trials'][chosen]['parameters'],
                'stages':{}}
        groups={}
        for label,stage in [('initial_fit',r['trials'][0]['fit']),('selected_fit',r['trials'][chosen]['fit']),('selected_replay',r['replay'])]:
            assert stage['feasible'] and len(stage['constraints'])==36
            by_check=defaultdict(list);by_context=defaultdict(list)
            for c in stage['constraints']:
                by_check[(c['context_id'],c['check_id'])].append(c)
                by_context[c['context_id']].append(c['scaled_error']**2)
            groups[label]=by_check
            result['stages'][label]={'loss':stage['loss'],'source_mean_squared_scaled_errors':
                {ctx:sum(v)/len(v) for ctx,v in by_context.items()},'diagnostic_records':len(stage['constraints'])}
            for (ctx,check),v in sorted(by_check.items()):
                assert len(v)==2 and len({c['reported_value'] for c in v})==1
                values=[c['value'] for c in v];ref=v[0]['reported_value']
                rows.append({'builder':name,'stage':label,'context':ctx,'check':check,'reported':ref,
                    'mean_generated':sum(values)/len(values),'draw_min':min(values),'draw_max':max(values),
                    'mean_absolute_error':sum(abs(a-ref) for a in values)/len(values),
                    'scale':v[0]['scale'],'two_source_simulation_seeds':';'.join(str(c['seed']) for c in v)})
        changes={'improved':0,'worsened':0,'unchanged':0}
        for key,before in groups['initial_fit'].items():
            after=groups['selected_fit'][key]
            old=sum(abs(v['value']-v['reported_value']) for v in before)/2
            new=sum(abs(v['value']-v['reported_value']) for v in after)/2
            changes['improved' if new<old else 'worsened' if new>old else 'unchanged']+=1
        result['per_constraint_mean_absolute_error_changes_on_fit_seeds']=changes
        summaries.append(result)
    summary={'scope':'M13-A real-source replay, no target evaluation','builders':summaries,
             'total_sessions':sum(x['usage']['sessions'] for x in summaries),
             'total_trials':sum(x['usage']['trials'] for x in summaries),
             'total_generator_executions':sum(x['usage']['executions'] for x in summaries),
             'total_stored_source_diagnostics':sum((x['usage']['trials']*2+2)*18 for x in summaries),
             'not_a_between_builder_ranking':'Different explicitly assumed source covariate distributions; compare source changes within each construction.',
             'target_participants_used':0,'heldout_target_analyses_performed':0}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    with (output/'source_diagnostics.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':summarize()
