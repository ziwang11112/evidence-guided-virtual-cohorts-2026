"""Produce a complete descriptive report after closed common evaluation."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
U=Path(__file__).resolve().parent
def fmt(x):return 'unavailable' if x is None else f'{x:.6g}'
def main():
 r=json.loads((U/'COMPLETE_RESULTS.json').read_text());cs=r['constructor_stage_statistics'];keys=['L01','L02','L03','R01','R02','R03']
 ids=['E1','E2','E3','glucose_hba1c_pearson','glucose_hba1c_spearman']
 lines=['# Information provision and additional revision: CHNS development results','',
 'This is one previously exposed clinical case, with three fresh scientific constructions per information condition. L used external literature and the visible research questions; R additionally received the complete existing reference summaries. Initial delivery could already use two trials; final delivery follows one additional revision/retention stage. This is not a no-feedback versus feedback experiment.','',
 f"Actual attempts: **{r['attempts']}** ({r['delivery_attempts']} delivery, {r['trial_attempts']} trial); successful tables: **{r['successful_tables']}**; distinct byte hashes: **{r['distinct_table_hashes']}**; failures: **{r['failed_attempts']}**. Each successful table has 3,000 rows. Rows and seeds are not independent clinical or author replications. No raw patient reads are recorded in the retained execution logs; author general-tool access was procedurally scoped.",'',
 'All six final stages were closed before common reference evaluation. These comparisons concern consistency with an observed development sample, not recovery of population truth or independent target validation.','',
 '## Primary and joint analyses','',
 'Numbers below are means across available fixed delivery seeds, with each author shown. Full ranges, individual seeds, missingness and matched changes are retained in COMPLETE_RESULTS.json.','',
 '| Constructor | Stage | E1 | E2 | E3 | Pearson | Spearman |','|---|---|---:|---:|---:|---:|---:|']
 for k in keys:
  for stage in ['initial','final']:
   row=[next(c for c in cs if c['constructor']==k and c['stage']==stage and c['id']==i) for i in ids]
   lines.append('| '+' | '.join([k,stage]+[fmt(x['mean']) for x in row])+' |')
 lines+=['','E1: HbA1c–BMI adjusted for age/sex; E2: HbA1c–glucose adjusted for age/sex; E3: HbA1c–age adjusted for sex/BMI/glucose. Exact operators and units remain in analysis_definitions.json.','',
 '## Revision results by construction','',
 '| Constructor | Analysis | Initial mean absolute difference | Final mean absolute difference | Matched seeds |','|---|---|---:|---:|---:|']
 for k in keys:
  for i in ids:
   c=next(c for c in r['paired_revision_changes'] if c['constructor']==k and c['id']==i)
   lines.append(f"| {k} | {i} | {fmt(c['initial_mean_absolute_difference'])} | {fmt(c['final_mean_absolute_difference'])} | {c['matched_seed_count']} |")
 lines+=['','These discrepancies retain each statistic’s own units. They are not a global accuracy score, an acceptance threshold, or proof that a reference sample estimate equals its population parameter.','',
 '## Complete distribution diagnostics','',
 'Every diagnostic is included; each cell shows initial → final mean. No favorable subset is selected.','',
 '| Diagnostic | '+' | '.join(keys)+' |','|---|'+'---:|'*len(keys)]
 for i in [x['id'] for x in cs if x['constructor']=='L01' and x['stage']=='initial' and x['group']=='diagnostics']:
  cells=[]
  for k in keys:
   vals=[next(c for c in cs if c['constructor']==k and c['stage']==s and c['id']==i)['mean'] for s in ['initial','final']]
   cells.append(fmt(vals[0])+' → '+fmt(vals[1]))
  lines.append('| '+i+' | '+' | '.join(cells)+' |')
 lines+=['','## Interpretation limits','',
 'Reference-assisted agreement demonstrates the ability to construct data consistent with supplied summaries; it is not independent discovery. Literature-only agreement is developmental evidence for transfer on this case, with unmeasured transport and joint assumptions. External source-population numerical replay was unavailable in both arms. Three fixed seeds assess conditional sampling variation, not evidence, model or transport uncertainty. All 30 summaries were supplied to R; there is no hidden-outcome generalization claim within this unit. Revisions include extra reasoning/computation, and no causal effect of feedback alone is isolated.','',
 'A final scientific interpretation and independent numerical audit must be read alongside this automatically generated complete inventory. No post-hoc equivalence margin or clinical validity label has been applied.','']
 (U/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
 titles={'E1':'HbA1c–BMI coefficient (adjusted age/sex)','E2':'HbA1c–glucose coefficient (adjusted age/sex)','E3':'HbA1c–age coefficient (adjusted sex/BMI/glucose)',
         'glucose_hba1c_pearson':'Glucose–HbA1c Pearson correlation','glucose_hba1c_spearman':'Glucose–HbA1c Spearman correlation'}
 units={'E1':'% per kg/m²','E2':'% per mmol/L','E3':'% per year'}
 reference_analyses={x['id']:x for x in next(a for a in r['runs'] if a['status']=='success')['statistics']['analyses']}
 fig,axs=plt.subplots(3,2,figsize=(13,11));axes=axs.ravel()
 for ax,i in zip(axes,ids):
  ref=next(c['reference'] for c in cs if c['id']==i and c['reference'] is not None)
  ax.axhline(ref,color='black',linestyle='--',linewidth=1,label='CHNS sample reference')
  if i in reference_analyses:
   interval=reference_analyses[i]['reference_interval']
   if interval['status']=='available':ax.axhspan(interval['lower'],interval['upper'],color='grey',alpha=.12,label='Reference coefficient 95% CI')
  for j,k in enumerate(keys):
   for s,offset,color in [('initial',-.12,'#3977a8'),('final',.12,'#ca692e')]:
    c=next(c for c in cs if c['constructor']==k and c['stage']==s and c['id']==i)
    if c['mean'] is not None:
     ax.plot([j+offset]*len([v for v in c['values'] if v is not None]),[v for v in c['values'] if v is not None],'.',color=color,alpha=.55)
     ax.scatter(j+offset,c['mean'],color=color,s=30,label=s if j==0 else None)
  ax.set_title(titles[i],fontsize=11);ax.set_ylabel(units.get(i,'Correlation'));ax.set_xticks(range(6),keys);ax.grid(axis='y',alpha=.2)
 axes[-1].axis('off');axes[-1].text(0,.9,'L: external literature; R: literature + reference summaries.\nOne exposed case; three authors per condition.\nSmall dots: three fixed delivery seeds; large dots: means.\nInitial may already use trials.\nGrey bands: reference coefficient sampling intervals.\nThey are not equivalence or acceptance margins.\nNo reference interval is supplied for the correlations.\nReference is a sample estimate, not population truth.',va='top',fontsize=10)
 axes[0].legend(fontsize=8);fig.suptitle('Information provision and an additional revision stage',fontsize=15);fig.tight_layout();fig.savefig(U/'analysis_use_profile.png',dpi=170);fig.savefig(U/'analysis_use_profile.svg');plt.close(fig)
 print('Complete descriptive report and analysis figures written')
if __name__=='__main__':main()
