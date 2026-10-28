"""Present every locked endpoint after the separate custodian evaluation.

Reads aggregate evaluation outputs and model/action metadata only; never reads
participant tables. The reporting plan was fixed before outcome evaluation.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
NAMES = ['ordinary_1','ordinary_2','gap_1','gap_2']


def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value): Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def interval_class(low, high):
    if low is None or high is None or not np.isfinite(low+high): return 'unavailable'
    if low>0: return 'positive'
    if high<0: return 'negative'
    return 'unresolved'


def main():
    evaluated = ROOT/'custodian/results'
    result = read(evaluated/'analysis_results.json')
    if result['release_manifest_sha256'] != sha(ROOT/'custodian/evaluation_release.json'):
        raise ValueError('Evaluation release hash changed')
    table = pd.read_csv(evaluated/'all_endpoint_draws.csv')
    spec = read(ROOT/'custodian/analysis_spec.json')
    refs = {x['endpoint']:x for x in result['reference']['endpoints']}
    assert len(table)==320 and len(refs)==8
    destination = ROOT/'report'
    if destination.exists(): raise RuntimeError('Preserve earlier report')
    destination.mkdir()
    rows=[]
    for (construction,arm,stage,endpoint),group in table.groupby(['construction','arm','stage','endpoint'],sort=True):
        assert len(group)==5 and group.draw.nunique()==5
        ref=refs[endpoint]
        classes=[interval_class(float(a),float(b)) for a,b in zip(group.ci95_low,group.ci95_high)]
        estimates=group.estimate.to_numpy(float)
        rows.append({'construction':construction,'arm':arm,'stage':stage,'endpoint':endpoint,'role':ref['role'],
            'reference_estimate':ref['estimate'],'reference_ci95_low':ref['ci95_low'],'reference_ci95_high':ref['ci95_high'],
            'reference_interval_class':interval_class(ref['ci95_low'],ref['ci95_high']),
            'generated_median':float(np.median(estimates)),'generated_min':float(estimates.min()),'generated_max':float(estimates.max()),
            'positive_point_draws':int((estimates>0).sum()),'negative_point_draws':int((estimates<0).sum()),'zero_point_draws':int((estimates==0).sum()),
            'positive_interval_draws':classes.count('positive'),'negative_interval_draws':classes.count('negative'),
            'unresolved_interval_draws':classes.count('unresolved'),'unavailable_interval_draws':classes.count('unavailable')})
    report=pd.DataFrame(rows)
    assert len(report)==64
    report.to_csv(destination/'all_analysis_interpretations.csv',index=False)
    process=[]
    for name in NAMES:
        run=ROOT/'runs'/name
        initial,final=read(run/'initial/model_spec.json'),read(run/'final/model_spec.json')
        evidence0,evidence1=read(run/'initial/evidence.json'),read(run/'final/evidence.json')
        snapshot0,snapshot1=read(run/'initial/gateway_snapshot.json'),read(run/'final/gateway_snapshot.json')
        keys=set(initial['parameters'])|set(final['parameters'])
        changed=[k for k in sorted(keys) if initial['parameters'].get(k)!=final['parameters'].get(k)]
        actions=read(run/'final/actions.json') if (run/'final/actions.json').exists() else []
        process.append({'construction':name,'arm':read(run/'run.json')['policy'],
            'generator_bytes_changed':sha(run/'initial/generator.py')!=sha(run/'final/generator.py'),
            'parameter_keys_changed':changed,'initial_source_count':len(evidence0['sources']),'final_source_count':len(evidence1['sources']),
            'initial_usage':snapshot0['usage'],'final_usage':snapshot1['usage'],
            'revision':read(run/'final/revision.json'),
            'action_counts':{key:sum(a['action']==key for a in actions) for key in sorted({a['action'] for a in actions})},
            'caution':'Code/parameter changes describe process, not proof of scientific improvement; exact model token costs unavailable.'})
    write(destination/'process_summary.json',process)

    endpoints=[e['name'] for e in spec['endpoints']]
    titles=['Crude BMI / 5','Adjusted BMI / 5 (PRIMARY)','Adjusted age / 10','Female - male',
            'BMI slope at 35 - 25','Female - male BMI slope','Male BMI slope / 5','Female BMI slope / 5']
    colors={'ordinary_1':'#2563a5','ordinary_2':'#2563a5','gap_1':'#16816a','gap_2':'#16816a'}
    fig,axes=plt.subplots(2,4,figsize=(19,9),constrained_layout=True)
    finalrows=report[report.stage=='final']
    for ax,endpoint,title in zip(axes.flat,endpoints,titles):
        ref=refs[endpoint]
        est,lo,hi=ref['estimate'],ref['ci95_low'],ref['ci95_high']
        ax.errorbar(est,4,xerr=[[est-lo],[hi-est]],fmt='D',color='black',capsize=4,label='Real estimate and 95% interval')
        for index,name in enumerate(NAMES):
            row=finalrows[(finalrows.construction==name)&(finalrows.endpoint==endpoint)].iloc[0]
            median,lower,upper=row.generated_median,row.generated_min,row.generated_max
            ax.errorbar(median,3-index,xerr=[[median-lower],[upper-median]],fmt='o',color=colors[name],capsize=4)
        ax.axvline(0,color='#b8bec6',linewidth=.9,linestyle='--')
        ax.set_yticks([4,3,2,1,0],['Real','Ordinary 1','Ordinary 2','Gap policy 1','Gap policy 2'])
        ax.set_ylim(-.6,4.6)
        ax.set_title(title,fontsize=12)
        ax.set_xlabel('HDL contrast (mg/dL)',fontsize=10)
        ax.grid(axis='x',alpha=.15)
    fig.suptitle('Final generators: all eight locked scientific analyses\nBlack: real estimate / 95% interval. Colored: median / min-max of five draws (not a confidence interval).',fontsize=15)
    fig.savefig(destination/'final_analysis_comparison.png',dpi=180)
    fig.savefig(destination/'final_analysis_comparison.pdf')
    plt.close(fig)

    lines=['# Complete analytical comparison','',
        'All eight endpoints are reported for every construction. Numerical agreement is descriptive; two Agent builds per workflow do not establish superiority.', '',
        'The reference interval is based on the public survey design. Generated ranges describe five residual draws, not five independent Agents or calibrated uncertainty about a wholly unobserved variable.', '',
        '| Analysis | Role | Real estimate [95% interval] | Ordinary 1 median [range] | Ordinary 2 median [range] | Gap 1 median [range] | Gap 2 median [range] |',
        '|---|---|---|---|---|---|---|']
    for endpoint in endpoints:
        ref=refs[endpoint]
        cells=[endpoint,ref['role'],f"{ref['estimate']:.3f} [{ref['ci95_low']:.3f}, {ref['ci95_high']:.3f}]"]
        for name in NAMES:
            x=finalrows[(finalrows.construction==name)&(finalrows.endpoint==endpoint)].iloc[0]
            cells.append(f'{x.generated_median:.3f} [{x.generated_min:.3f}, {x.generated_max:.3f}]')
        lines.append('| '+' | '.join(cells)+' |')
    lines += ['', '## Direction and conditional interval patterns', '',
        'A zero-overlapping real interval is unresolved, not an established null. Generated interval patterns are conditional on that generator; matching significance is not a universal success criterion.', '',
        '| Construction | Endpoint | Reference interval class | Positive / negative point draws | Positive / negative / unresolved interval draws |',
        '|---|---|---|---|---|']
    for _,x in finalrows.iterrows():
        lines.append(f'| {x.construction} | {x.endpoint} | {x.reference_interval_class} | {x.positive_point_draws} / {x.negative_point_draws} | {x.positive_interval_draws} / {x.negative_interval_draws} / {x.unresolved_interval_draws} |')
    lines += ['', '## Files', '',
        '- `all_analysis_interpretations.csv`: all 64 initial/final construction-by-endpoint summaries.',
        '- `process_summary.json`: actual initial/final retrieval counts, parameter changes, revision reasons and action types.',
        '- `../custodian/results/all_endpoint_draws.csv`: all 320 generated endpoint records.',
        '- `../custodian/results/initial_final_changes.csv`: descriptive numerical revision diagnostics.',
        '- `final_analysis_comparison.png` and `.pdf`: all final constructions without selective endpoint filtering.', '',
        'Input-supported association agreement is evidence translation. Reserved analytical agreement is a stronger check, but neither establishes novel biology, individual recovery or replacement of real measurements.']
    (destination/'ALL_ANALYSES.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    write(destination/'report_manifest.json',{'input_release_sha256':sha(ROOT/'custodian/evaluation_release.json'),
        'input_analysis_sha256':sha(evaluated/'analysis_results.json'),'reporting_plan_sha256':sha(ROOT/'reporting_plan.json'),
        'script_sha256':sha(__file__),'files':{p.name:sha(p) for p in destination.iterdir() if p.is_file()},
        'observed_or_reference_rows_read':False})
    print(json.dumps({'report':str(destination),'endpoint_summaries':len(report),'constructions':4,'all_endpoints':8}))


if __name__ == '__main__': main()
