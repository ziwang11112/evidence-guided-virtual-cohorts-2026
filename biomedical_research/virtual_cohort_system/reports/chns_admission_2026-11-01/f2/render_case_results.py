"""Render published aggregates only; never read participant/generated tables."""
from pathlib import Path
import json
import hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
report = json.loads((ROOT / 'evaluation_results/REPORT.json').read_text(encoding='utf-8'))
reference = report['reference']
slots = report['slots']
def rng(values):
    return [min(values), max(values)]
def format_range(values):
    return f'{min(values):.5f}–{max(values):.5f}'
summary = {
    'source_report_sha256': hashlib.sha256((ROOT/'evaluation_results/REPORT.json').read_bytes()).hexdigest(),
    'information_regime': 'whole_cohort_no_individual_input',
    'reference_n': reference['n'], 'constructed_models': 2,
    'executed_slots': 12, 'unique_generated_tables': 6,
    'rows_per_table': 3000, 'source_revision_decisions': {'C1': 'retain', 'C2': 'retain'},
    'revision_gain_demonstrated': False,
    'reference_estimands': reference['estimands'], 'constructions': {},
    'interpretation': 'Directional feasibility only in one selected sample; no equivalence, calibrated uncertainty, method superiority or patient-measurement replacement claim.'
}
for c in ('C1', 'C2'):
    selected = [s for s in slots if s['construction'] == c and s['stage'] == 'initial']
    summary['constructions'][c] = {
        'estimands': {eid: {
            'seed_range': rng([s['analysis']['estimands'][eid]['coefficient'] for s in selected]),
            'relative_to_reference_range': rng([s['comparison'][eid]['ratio'] for s in selected]),
            'direction': report['stages'][f'{c}_initial'][eid]['direction_status'],
        } for eid in ('E1','E2','E3')},
        'marginal_ranges': {v: {k: rng([s['analysis']['diagnostics']['marginal'][v][k] for s in selected])
            for k in ('mean','sd','q10','median','q90')} for v in ('age','female','bmi','glucose','hba1c')},
        'joint_ranges': {k: rng([s['analysis']['diagnostics']['joint'][k] for s in selected]) for k in ('pearson','spearman')}
    }
(ROOT/'RESULTS_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
fig, axes = plt.subplots(1,3,figsize=(12,4.3))
titles = ['E1 · BMI association','E2 · Glucose association','E3 · Age association']
labels = ['HbA1c percentage points / (kg/m²)','HbA1c percentage points / (mmol/L)','HbA1c percentage points / year']
for ax,eid,title,label in zip(axes,('E1','E2','E3'),titles,labels):
    ref = reference['estimands'][eid]; interval = ref['interval']
    ax.axvspan(interval['lower'],interval['upper'],color='#64748b',alpha=.15)
    ax.errorbar(ref['coefficient'],2,xerr=[[ref['coefficient']-interval['lower']],[interval['upper']-ref['coefficient']]],fmt='D',color='#334155',capsize=5)
    for c,y,color in [('C1',1,'#0284c7'),('C2',0,'#c2410c')]:
        values=[s['analysis']['estimands'][eid]['coefficient'] for s in slots if s['construction']==c and s['stage']=='initial']
        ax.plot([min(values),max(values)],[y,y],color=color,linewidth=2)
        ax.scatter(values,[y]*3,color=color,s=30,zorder=3)
    ax.set_yticks([2,1,0],['CHNS reference','C1 · conditional','C2 · mixture'])
    ax.set_ylim(-.5,2.5);ax.set_title(title,fontsize=11);ax.set_xlabel(label,fontsize=8)
    ax.tick_params(axis='both',labelsize=8);ax.grid(axis='x',alpha=.15)
    ax.spines[['top','right']].set_visible(False)
fig.suptitle('Whole-cohort generation: directions retained, effect magnitudes differ',fontsize=13)
fig.text(.5,.03,'Reference: selected-sample nominal 95% community CR1/t interval. Generated dots: three seeds, not confidence intervals.\nRetained stages repeat these exact outputs and are not additional evidence.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.13,1,.92])
(ROOT/'figures').mkdir(exist_ok=True)
fig.savefig(ROOT/'figures/primary_associations.png',dpi=180)
plt.close(fig)
print(json.dumps({'summary':'RESULTS_SUMMARY.json','figure':'figures/primary_associations.png','source':'aggregate REPORT only'}))
