"""Summarize existing verified source reports. Does not import/run a generator."""
from pathlib import Path
import json
import hashlib
import statistics

B=Path(__file__).resolve().parent.parent
S=B/'cal/initial_fit'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=read(S/'result.json'); selection=read(S/'selection.json'); plan=read(S/'plan.json')
selected=next(t for t in r['trials'] if t['index']==selection['selected_trial'])
initial=r['trials'][0]
summaries=[]
for constraint in plan['constraints']:
    key=(constraint['context_id'],constraint['check_id']); out={'constraint':'/'.join(key),'scale':constraint['scale']}
    for label,records in [('initial_fit',initial['fit']['constraints']),('selected_fit',selected['fit']['constraints']),('selected_replay',r['replay']['constraints'])]:
        rows=[x for x in records if (x['context_id'],x['check_id'])==key]
        assert len(rows)==2 and all(x['status']=='computed' for x in rows)
        target=rows[0]['reported_value']; out['reported']=target
        errors=[x['value']-target for x in rows]
        out[label]={'seeds':[x['seed'] for x in rows],'values':[x['value'] for x in rows],
            'mean_value':statistics.mean(x['value'] for x in rows),
            'mean_absolute_draw_error':statistics.mean(abs(e) for e in errors),
            'absolute_mean_error':abs(statistics.mean(errors)),
            'scaled_mse':statistics.mean((e/constraint['scale'])**2 for e in errors)}
    out['fit_mae_improved']=out['selected_fit']['mean_absolute_draw_error']<out['initial_fit']['mean_absolute_draw_error']
    out['fit_absolute_mean_improved']=out['selected_fit']['absolute_mean_error']<out['initial_fit']['absolute_mean_error']
    summaries.append(out)
reports=[]
for relative in [f't{selected["index"]:04d}/source_replays_v2/{part}/replay.json' for part in ['f0','f1','v0','v1']]:
    raw=read(S/relative)
    reports.append({'path':relative,'sha256':sha(S/relative),'status':raw['status'],
        'contexts':[{'id':c['id'],'checks':[{'id':x['id'],'status':x['status'],
            'generation_link_verified':x.get('generation_link_verified')} for x in c['checks']]} for c in raw['contexts']]})
    assert sha(S/relative)==r['files'][relative]
output={'scope':'arithmetic on permitted actual source feedback only; no generator execution',
    'result_sha256':sha(S/'result.json'),'selection_sha256':sha(S/'selection.json'),
    'selected_trial':selected['index'],'initial_parameters':initial['parameters'],'selected_parameters':selected['parameters'],
    'initial_fit_loss':initial['fit']['loss'],'selected_fit_loss':selected['fit']['loss'],'selected_replay_loss':r['replay']['loss'],
    'fit_relative_loss_reduction':1-selected['fit']['loss']/initial['fit']['loss'],
    'mae_improvements':sum(x['fit_mae_improved'] for x in summaries),
    'absolute_mean_improvements':sum(x['fit_absolute_mean_improved'] for x in summaries),
    'constraint_summaries':summaries,'source_reports':reports,
    'context_scaled_mse':{context:{label:statistics.mean(x[label]['scaled_mse'] for x in summaries if x['constraint'].startswith(context+'/'))
        for label in ['initial_fit','selected_fit','selected_replay']} for context in ['thai_development','gallagher_full']}}
(B/'agent_exchange/review_metrics.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in output.items() if k not in ['constraint_summaries','source_reports']},indent=2))
print('constraint | reported | initial mean | selected mean | replay seed values | mean(abs error) initial -> selected | abs(mean error) initial -> selected')
for x in summaries:
    a=x['initial_fit']; s=x['selected_fit']; v=x['selected_replay']
    print(f"{x['constraint']} | {x['reported']:.6g} | {a['mean_value']:.6g} | {s['mean_value']:.6g} | {v['values'][0]:.6g},{v['values'][1]:.6g} | {a['mean_absolute_draw_error']:.6g}->{s['mean_absolute_draw_error']:.6g} | {a['absolute_mean_error']:.6g}->{s['absolute_mean_error']:.6g}")
