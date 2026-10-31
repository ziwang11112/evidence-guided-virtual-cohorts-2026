"""Summarize released aggregates only; never reads participant or generated rows."""
from pathlib import Path
import json,hashlib,argparse
R=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--plot-only',action='store_true')
    args=parser.parse_args()
    if args.plot_only:
        render_plot(json.loads((R/'results/summary.json').read_text()))
        print('Rendered presentation from existing aggregate summary; no analysis was rerun.')
        return
    p=R/'results/evaluation.json'
    result=json.loads(p.read_text())
    destination=R/'results/summary.json'
    if destination.exists():raise ValueError('Existing summary is not overwritten')
    ids=('global_bmi','global_age','global_curvature','global_interaction')
    ref={e['estimand']:e for e in result['reference_estimands']}
    candidates={(c['builder'],c['stage']):{e['estimand']:e for e in c['estimands']}
                for c in result['candidate_comparisons']}
    global_rows=[]
    for name in ids:
        row={'estimand':name,'measured':ref[name]['value'],'units':ref[name]['units']}
        row['candidates']={bid+'_'+stage:estimates[name]['generated']['value']
                           for (bid,stage),estimates in candidates.items()}
        global_rows.append(row)
    changes={}
    for bid in result['scheduled_builders']:
        own=[c for c in result['initial_final_changes'] if c['builder']==bid]
        changes[bid]={label:sum(c['direction']==label for c in own) for label in ('lower','higher','unchanged')}
        changes[bid]['not_computable']=sum(c['direction'] is None for c in own)
    summary={'released_json_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
        'cohort_n':result['cohort_n'],'builder_outcomes':result['builder_outcomes'],
        'global_estimates':global_rows,'absolute_discrepancy_changes':changes,
        'interpretation':'Endpoint counts are descriptive; no aggregate quality score, equivalence test or causal revision effect.'}
    destination.write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    render_plot(summary)
    print(json.dumps(summary,indent=2))

def render_plot(summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figure,axes=plt.subplots(2,2,figsize=(10,7),layout='constrained')
    labels={
      'global_bmi':('BMI association','mg/dL per 5 kg/m²'),
      'global_age':('Age association','mg/dL per 10 years'),
      'global_curvature':('Quadratic BMI term','mg/dL per b²; b = (BMI − 28)/5'),
      'global_interaction':('BMI × sex interaction','mg/dL per 5 kg/m²\n(male − female slope)'),
    }
    for ax,row in zip(axes.flat,summary['global_estimates']):
        ax.axhline(0,color='#a0a5ab',linewidth=.7,linestyle='--',zorder=0)
        ax.axhline(row['measured'],color='#20252b',linewidth=1.7,label='Measured reference')
        for j,bid in enumerate(('b1','b2','b3')):
            values=[row['candidates'].get(bid+'_'+stage) for stage in ('initial','final')]
            if None in values:continue
            ax.plot([j-.12,j+.12],values,color=('#2463a6','#b45726','#278375')[j],linewidth=1.2)
            ax.scatter(j-.12,values[0],facecolors='white',edgecolors=('#2463a6','#b45726','#278375')[j],s=48,zorder=3)
            ax.scatter(j+.12,values[1],color=('#2463a6','#b45726','#278375')[j],s=48,zorder=3)
        ax.set_xticks(range(3),['Builder 1','Builder 2','Builder 3'])
        title,unit=labels[row['estimand']]
        ax.set_title(title)
        ax.set_ylabel(unit,fontsize=9);ax.grid(axis='y',alpha=.18)
    axes.flat[0].legend(fontsize=8,frameon=False)
    figure.suptitle('Direct authorship: initial (open) and final (filled)\nOne held-out quota cohort; descriptive effects, no confidence intervals',fontsize=12)
    figure.savefig(R/'results/analysis_comparison.png',dpi=180)
    plt.close(figure)
if __name__=='__main__':main()
