"""Postclosure descriptive reporting only; does not call or modify generators."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyzer import REFERENCE,ESTIMANDS
ROOT=Path(__file__).resolve().parent
ORDER=['none','anchor_only','bridge_only','combined']
NAMES=['Common only','Common + A','Common + B','Common + A + B']
COLORS=['#7F8BA0','#8575B4','#D99248','#4268AD']

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    out=ROOT/'analysis';a=pd.read_csv(out/'analyses.csv');s=pd.read_csv(out/'source_checks.csv');l=pd.read_csv(out/'identification_labels.csv')
    costs=read(out/'COSTS.json');closure=read(ROOT/'CONSTRUCTION_CLOSURE.json');failures=read(out/'failures.json')
    recomputation=read(out/'INDEPENDENT_RECOMPUTATION.json')
    agg=a.groupby(['family','condition','id','estimand','identified'],sort=False).agg(
        mean=('value','mean'),minimum=('value','min'),maximum=('value','max'),draw_sd=('value','std'),
        mean_absolute_distance_to_full_information_world=('absolute_error_to_full_information_world','mean'),
        completed_draws=('value','size')).reset_index()
    agg=agg.merge(l[['id','name','declared_status','declared_value','identifiedness_correct']],left_on=['id','estimand'],right_on=['id','name'],how='left').drop(columns='name')
    agg['mean_minus_declared']=agg['mean']-agg['declared_value']
    agg.to_csv(out/'constructor_analyses.csv',index=False)
    cells=[]
    for family in ESTIMANDS:
        for condition in ORDER:
            subset=a[(a.family==family)&(a.condition==condition)&(a.estimand==ESTIMANDS[family][0])]
            ss=s[(s.family==family)&(s.condition==condition)]
            ll=l[(l.family==family)&(l.condition==condition)]
            c=agg[(agg.family==family)&(agg.condition==condition)&(agg.estimand==ESTIMANDS[family][0])]
            cells.append({'family':family,'condition':condition,'constructed':len(c),
                'primary_mean_min':float(c['mean'].min()),'primary_mean_max':float(c['mean'].max()),
                'primary_draw_min':float(subset.value.min()),'primary_draw_max':float(subset.value.max()),
                'primary_MAE_if_identified':float(subset.absolute_error_to_full_information_world.mean()) if condition=='combined' else None,
                'primary_passes_if_identified':int(subset.identified_within_0_08.sum()) if condition=='combined' else None,
                'primary_evaluations':len(subset),'source_checks_passed':int(ss.within_tolerance.sum()),'source_checks_total':len(ss),
                'identification_correct':int(ll.identifiedness_correct.sum()),'identification_total':len(ll)})
    pd.DataFrame(cells).to_csv(out/'cell_summary.csv',index=False)
    summary={'construction_attempts':len(closure['rows']),'sealed_constructions':sum(r['status']=='sealed' for r in closure['rows']),
        'tables_evaluated':a[['id','seed']].drop_duplicates().shape[0],
        'analysis_estimates':len(a),'identified_analysis_estimates':int(a.identified.sum()),
        'identified_within_tolerance':int(a.identified_within_0_08.fillna(False).astype(bool).sum()),
        'source_checks_passed':int(s.within_tolerance.sum()),'source_checks_total':len(s),
        'identification_correct':int(l.identifiedness_correct.sum()),'identification_total':len(l),
        'mean_to_declaration_max_abs':float(agg.mean_minus_declared.abs().max()),
        'costs':costs,'failures':failures,'cells':cells,
        'independent_recomputation':{k:v for k,v in recomputation.items() if k!='checks'},
        'scope':'controlled artificial evidence composition; not clinical transport or method superiority'}
    with (out/'SUMMARY.json').open('x',encoding='utf-8') as f:json.dump(summary,f,indent=2,allow_nan=False)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axes=plt.subplots(1,2,figsize=(12,4.6),sharey=True)
    for ax,(family,title) in zip(axes, [('adjusted','a  Covariate-adjusted association'),('longitudinal','b  Correlation of within-person changes')]):
        name=ESTIMANDS[family][0];ref=REFERENCE[family][name]
        for j,condition in enumerate(ORDER):
            cc=agg[(agg.family==family)&(agg.condition==condition)&(agg.estimand==name)].sort_values('id')
            for offset,(_,row) in zip(np.linspace(-.17,.17,len(cc)),cc.iterrows()):
                x=j+offset
                ax.plot([x,x],[row.minimum,row.maximum],color=COLORS[j],lw=1.7,alpha=.85)
                ax.scatter([x],[row['mean']],s=45,color=COLORS[j],edgecolor='white',linewidth=.6,zorder=4)
        ax.axvspan(2.58,3.42,color='#EAF0F9',zorder=-2)
        ax.plot([2.58,3.42],[ref,ref],color='#1A2D49',ls='--',lw=1.4)
        ax.text(3,ref+.10,f'Identified value {ref:g}',ha='center',fontsize=9,color='#1A2D49')
        ax.axhline(0,color='#DFE3E9',lw=.8,zorder=-1)
        ax.set_xticks(range(4),NAMES,rotation=12,ha='right');ax.set_ylim(-1,1);ax.set_xlim(-.45,3.45)
        ax.set_title(title,loc='left',fontweight='bold',pad=13)
        ax.text(1,-.93,'Chosen scenarios: primary relation is not identified',ha='center',fontsize=8,color='#626B79')
    axes[0].set_ylabel('Primary correlation in generated data')
    fig.text(.5,.01,'Dot = one author, mean of 3 draws; line = draw range. Dashed reference applies only to the complete-evidence condition.',ha='center',fontsize=9,color='#586373')
    fig.tight_layout(rect=[0,.065,1,1]);fig.savefig(out/'evidence_composition.png',dpi=200);fig.savefig(out/'evidence_composition.pdf');plt.close(fig)
    lines=['# Evidence composition pilot — results','',
        'This unit tests exact-moment composition in artificial populations. It does not establish clinical transport, literature-search reliability or workflow superiority.','',
        f"Completed {summary['sealed_constructions']}/{summary['construction_attempts']} constructions and {summary['tables_evaluated']} tables. All {summary['analysis_estimates']} predefined analysis estimates are retained. Three random draws per author are nested repetitions, not new independent authors.",'',
        '| Family | Evidence | Authors | Primary range across author means | MAE when identified | Source checks within tolerance | Correct identification labels |',
        '|---|---|---:|---:|---:|---:|---:|']
    for r in cells:
        err='Not an error score' if r['primary_MAE_if_identified'] is None else f"{r['primary_MAE_if_identified']:.5f}"
        lines.append(f"| {r['family']} | {r['condition']} | {r['constructed']} | {r['primary_mean_min']:.4f} to {r['primary_mean_max']:.4f} | {err} | {r['source_checks_passed']}/{r['source_checks_total']} | {r['identification_correct']}/{r['identification_total']} |")
    lines += ['',f"All identified primary/secondary analyses: {summary['identified_within_tolerance']}/{summary['identified_analysis_estimates']} inside the preregistered numerical tolerance. Source diagnostics: {summary['source_checks_passed']}/{summary['source_checks_total']}. Identification labels: {summary['identification_correct']}/{summary['identification_total']}.",
              '', '## How to read the result','',
              'The reference line appears only where the primary estimand is identified. A source-consistent point scenario in an incomplete-evidence cell is not counted as incorrect because it differs from that line. Narrow variation across authors or seeds is not evidence that an assumed relationship is correct.',
              '', '## Implementation and cost','',
              f"Requested and returned models: {costs['requested_models']} / {costs['returned_models']}. Calls: {costs['api_calls']}; returned-usage tariff estimate: ${costs['known_tariff_usd']:.6f}; unresolved charge reservations: ${costs['unknown_call_reservations_usd']:.6f}. These are tariff estimates, not invoices.",
              '',f"Covariance-based recomputation checked {recomputation['comparisons']} estimates across {recomputation['recomputed_tables']} tables. Maximum discrepancy: {recomputation['max_absolute_difference']:.3g}. Independently coded by the same root assistant, not independent personnel adjudication.",
              '',f"Recorded failures: {len(failures)}. Complete failures are in analysis/failures.json; all calls, scientific programs, specifications and output tables remain local.",
              '', '## Files','',
              '- `PROTOCOL.md`, `FREEZE.json`: fixed design and hashes.',
              '- `inputs/`: exact approved records, schema and prompts.',
              '- `calls/`: requests, raw responses, usage and cost receipts.',
              '- `candidates/`: model-authored code, provenance, sealed specifications.',
              '- `executions/`: isolated execution bindings, logs and generated rows.',
              '- `analysis/constructor_analyses.csv`: all author-level results and declared values.',
              '- `analysis/cell_summary.csv`, `analysis/identification_labels.csv`: complete summaries.',
              '- `analysis/INDEPENDENT_RECOMPUTATION.json`: alternative numerical route.',
              '- `analysis/evidence_composition.png` and `.pdf`: result figure.',
              '', 'See `IMPLEMENTATION_REVIEW.md` for code-level interpretation and the next-step decision.']
    (ROOT/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('cells','costs','independent_recomputation')},ensure_ascii=False))

if __name__=='__main__':main()
