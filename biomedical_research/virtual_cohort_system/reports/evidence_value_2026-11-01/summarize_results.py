"""Render committed scalar results only; never load rows or run generators."""
from pathlib import Path
import csv
import json
import hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
report = json.loads((ROOT / 'evaluation/REPORT.json').read_text(encoding='utf-8'))
slots = report['slots']
assert len(slots) == 12 and all(s['status'] == 'success' for s in slots)
by = {(s['arm'], s['seed']): s for s in slots}
seeds = [18101, 18103, 18107]
comparisons = []
for slot in slots:
    for world, score in slot['world_scores'].items():
        comparisons.append(dict(arm=slot['arm'], seed=slot['seed'], world=world,
            n=slot['analysis']['n'], slope=slot['analysis']['primary']['slope'],
            slope_reference=score['primary_reference'],
            slope_signed_error=score['primary_difference'],
            slope_absolute_error=score['primary_absolute_difference'],
            slope_evidence_status=score['primary_evidence_status'],
            tail=slot['analysis']['tail']['contrast'],
            tail_reference=score['tail_reference']['contrast'],
            tail_signed_error=score['tail_differences']['contrast'],
            tail_absolute_error=score['tail_absolute_differences']['contrast']))
with (ROOT / 'evaluation/ALL_ENDPOINT_COMPARISONS.csv').open('w', newline='', encoding='utf-8') as f:
    writer=csv.DictWriter(f, fieldnames=list(comparisons[0])); writer.writeheader(); writer.writerows(comparisons)
criterion = all(
    by[(arm, seed)]['world_scores'][world]['primary_absolute_difference'] <
    by[('B', seed)]['world_scores'][world]['primary_absolute_difference']
    for arm,world in [('C','plus_normal'),('D','minus_normal')] for seed in seeds)
expected_change = all(r['C_minus_D_primary'] > 0 for r in report['responsiveness'])
summary = {
    'primary_report_sha256':hashlib.sha256((ROOT/'evaluation/REPORT.json').read_bytes()).hexdigest(),
    'successful_slots':12,'rows_per_table':3000,'world_comparisons':len(comparisons),
    'expected_counterfactual_change_all_seeds':expected_change,
    'both_conditional_arms_lower_absolute_error_than_B_all_seeds':criterion,
    'prespecified_concrete_translation_example':criterion and expected_change,
    'general_evidence_effect_established':False,'clinical_validation':False,
    'groups':{},'world_averaging':None,'global_quality_score':None}
for arm in 'ABCD':
    subset=[s for s in slots if s['arm']==arm]
    summary['groups'][arm]={key:[min(vals),max(vals)] for key,vals in {
        'slope_range':[s['analysis']['primary']['slope'] for s in subset],
        'tail_range':[s['analysis']['tail']['contrast'] for s in subset]}.items()}
(ROOT/'evaluation/SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')

plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
colors=['#167d9a','#bb5423','#6557a0']
worlds=report['revealed_reference']['worlds']
for col,(sign,arm) in enumerate([('plus','C'),('minus','D')]):
    arms=['A','B',arm]
    for row,key in enumerate(['primary','tail']):
        ax=axes[row,col]
        for i,a in enumerate(arms):
            values=[by[(a,s)]['analysis'][key]['slope' if key=='primary' else 'contrast'] for s in seeds]
            for j,v in enumerate(values):
                ax.scatter(i+(j-1)*.075,v,c=colors[j],s=45,zorder=3,
                           label=f'Seed {seeds[j]}' if col==0 and row==0 and i==0 else None)
        normal=worlds[sign+'_normal']
        if row==0:
            ref=normal['primary_slope']
            ax.axhline(ref,color='#222222',lw=1.4,label='Compatible-world reference')
            ax.set_ylim(-.27,.58)
            ax.set_ylabel('Pooled OLS slope')
            ax.set_title(f'{sign.capitalize()} conditional evidence: implied projection')
        else:
            ax.axhline(normal['tail']['contrast'],color='#222222',lw=1.4,label='Normal residual reference')
            ax.axhline(worlds[sign+'_t3']['tail']['contrast'],color='#ad6f00',lw=1.4,ls='--',label='Student-t(3) residual reference')
            ax.set_ylim(-.05,.085)
            ax.set_ylabel('Joint tail probability contrast')
            ax.set_title('Same supplied moments; different compatible tails')
            ax.legend(loc='upper left',fontsize=8)
        ax.axhline(0,color='#888888',lw=.6,ls=':')
        ax.set_xticks(range(3),['A: target only','B: marginal /\npairwise','C: conditional (+)' if arm=='C' else 'D: conditional (-)'])
        ax.set_xlim(-.4,2.4);ax.grid(axis='y',alpha=.18)
axes[0,0].legend(loc='upper left',fontsize=8)
fig.suptitle('Artificial whole-cohort generation: conditional evidence changes analytical output\nOne constructor per packet; three output seeds per frozen program',fontsize=14)
fig.savefig(ROOT/'evaluation/conditional_evidence_results.png',dpi=180)
fig.savefig(ROOT/'evaluation/conditional_evidence_results.svg')
plt.close(fig)
print(json.dumps(summary))
