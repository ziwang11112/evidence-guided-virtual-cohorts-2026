"""Display the entire scheduled M13-B release; no model or estimator changes."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent


def main():
    report=json.loads((ROOT/'results/aggregate.json').read_text(encoding='utf-8'))
    real={r['endpoint']:r for r in report['measured']}
    groups={f"{g['builder']}_{g['candidate']}":{r['endpoint']:r for r in g['panel']}
            for g in report['seed_summaries']}
    summary=[]
    for key,panel in groups.items():
        for endpoint,row in panel.items():
            sums=row['summaries'];m=real[endpoint]
            summary.append(dict(group=key,endpoint=endpoint,measured=m['estimate'],
                 measured_ci_low=m.get('ci_low'),measured_ci_high=m.get('ci_high'),
                 generated_mean=(sums['estimate'] or {}).get('mean'),
                 generated_min=(sums['estimate'] or {}).get('min'),
                 generated_max=(sums['estimate'] or {}).get('max'),
                 mean_absolute_error=(sums['absolute_error'] or {}).get('mean'),
                 measured_status=m['status'],generated_status=row['status']))
    pd.DataFrame(summary).to_csv(ROOT/'results/seed_comparison.csv',index=False)
    comparisons=[]
    for b in ['build01','build02']:
        for e in real:
            old=groups[b+'_initial'][e]['summaries']['absolute_error']
            new=groups[b+'_source_reviewed'][e]['summaries']['absolute_error']
            delta=None if old is None or new is None else new['mean']-old['mean']
            comparisons.append({'builder':b,'endpoint':e,'initial_mae':None if old is None else old['mean'],
                    'source_reviewed_mae':None if new is None else new['mean'],
                    'change_final_minus_initial':delta,
                    'description':'unavailable' if delta is None else 'improved' if delta < -1e-10 else 'worsened' if delta>1e-10 else 'unchanged'})
    pd.DataFrame(comparisons).to_csv(ROOT/'results/revision_changes.csv',index=False)
    styles=[('build01_initial','Agent 1 initial','#6b8bc3'),('build01_source_reviewed','Agent 1 revised','#124b8e'),
            ('build02_initial','Agent 2 initial','#e8b770'),('build02_source_reviewed','Agent 2 revised','#b16214'),
            ('published_reference_gallagher_normal','Equation + noise','#747474')]
    fig,axes=plt.subplots(2,4,figsize=(15,8),constrained_layout=True)
    statistics=[('mean','Mean (percentage points)'),('bmi_per5','BMI association (pp / 5 kg/m²)'),
                ('age_per10','Age association (pp / 10 years)'),('bmi_curvature_second_difference','BMI curvature (pp)')]
    deterministic=next(t for t in report['tables'] if t['table_id']=='gallagher_mean')
    det={r['endpoint']:r for r in deterministic['panel']}
    for r,sex in enumerate(['male','female']):
        for c,(stat,title) in enumerate(statistics):
            ax=axes[r,c];e=f'primary.{sex}.{stat}';actual=real[e]
            if actual['status']=='estimable':
                ax.axvspan(actual['ci_low'],actual['ci_high'],color='#2b8c5a',alpha=.14)
                ax.axvline(actual['estimate'],color='#216d45',lw=2,label='Measured estimate / 95% design CI')
            for y,(key,label,color) in enumerate(styles):
                s=groups[key][e]['summaries']['estimate']
                if s:
                    ax.plot([s['min'],s['max']],[y,y],color=color,lw=2)
                    ax.scatter(s['mean'],y,color=color,s=35,zorder=3)
            if det[e]['status']=='estimable':ax.scatter(det[e]['estimate'],5,marker='x',c='black',s=40)
            ax.set_yticks(range(6),[x[1] for x in styles]+['Equation mean'])
            if c:ax.set_yticklabels([])
            ax.invert_yaxis();ax.set_title(f'{sex.title()} · {title}',fontsize=10)
            ax.grid(axis='x',alpha=.2)
    fig.suptitle('Body-fat enrichment: all frozen primary analytical results\nGreen: measured estimate and pointwise 95% design CI; dots/bars: generated three-draw mean and range (not CI)',fontsize=12)
    fig.savefig(ROOT/'results/primary_analyses.png',dpi=180)
    fig.savefig(ROOT/'results/primary_analyses.pdf')
    plt.close(fig)
    cells=[e for e in real if e.endswith('.iqr')]
    fig,ax=plt.subplots(figsize=(13,7),constrained_layout=True)
    offsets=np.linspace(-.34,.34,len(styles)+1)
    for i,(key,label,color) in enumerate(styles):
        for j,e in enumerate(cells):
            s=groups[key][e]['summaries']['estimate'];m=real[e]['estimate']
            if s and m is not None:
                ax.plot([s['min']-m,s['max']-m],[j+offsets[i]]*2,c=color,lw=1)
                ax.scatter(s['mean']-m,j+offsets[i],c=color,s=17,label=label if j==0 else None)
    for j,e in enumerate(cells):
        if det[e]['estimate'] is not None and real[e]['estimate'] is not None:
            ax.scatter(det[e]['estimate']-real[e]['estimate'],j+offsets[-1],c='black',marker='x',s=23,
                       label='Equation mean' if j==0 else None)
    ax.axvline(0,c='#216d45');ax.set_yticks(range(len(cells)),[e.replace('.iqr','').replace('.',' / ') for e in cells],fontsize=8)
    ax.invert_yaxis();ax.grid(axis='x',alpha=.2);ax.legend(loc='upper right',fontsize=8)
    ax.set_xlabel('Generated minus measured within-cell IQR (percentage points)')
    ax.set_title('All scheduled conditional spread checks\nStochastic dots/bars: three-draw mean/range; crosses: deterministic reference; no quantile sampling intervals')
    fig.savefig(ROOT/'results/conditional_spread.png',dpi=180);fig.savefig(ROOT/'results/conditional_spread.pdf');plt.close(fig)
    print(json.dumps({'tables':report['table_count'],'endpoints':report['panel_count'],
       'flow':report['exclusion_flow'], 'revisions':{b:pd.DataFrame(comparisons).query('builder==@b').description.value_counts().to_dict() for b in ['build01','build02']}},indent=2))


if __name__=='__main__':main()
