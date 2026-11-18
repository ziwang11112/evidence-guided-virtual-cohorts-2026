"""Original diagnostic figure; aggregate inputs only, no patient data or fitting."""
from pathlib import Path
import csv
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
P = HERE.parents[1]
law = json.loads((HERE/'ANALYTIC_C01_C02.json').read_text(encoding='utf-8'))
agg = json.loads((HERE/'AGGREGATE_DIAGNOSIS.json').read_text(encoding='utf-8'))
with (P/'work/core_workflow_replication_2026-11-04/display/DIAGNOSTIC_SUMMARY.csv').open(encoding='utf-8-sig', newline='') as f:
    d = next(x for x in csv.DictReader(f) if x['author']=='C01' and x['diagnostic']=='glucose_hba1c_spearman')
panels = [('A  CHNS / C01: rank dependence', 'Glucose–HbA1c Spearman correlation',
           law['laws']['C01']['glucose_hba1c_spearman_quadrature'][-1]['spearman'],
           float(d['mean']), float(d['min']), float(d['max']), float(d['reference']), (0, .85))]
for author, endpoint, title, xlabel, lim in [
    ('C02','E2','B  CHNS / C02: glucose association','HbA1c percentage points per mmol/L', (0,.60)),
    ('E01','q1_residual_rms','C  ENSANUT / E01: residual variation','HbA1c percentage points', (0,.60)),
    ('E02','q1_residual_rms','D  ENSANUT / E02: residual variation','HbA1c percentage points', (0,.60)),
]:
    row = next(x for x in agg['diagnostics'] if x['author']==author and x['endpoint']==endpoint)
    panels.append((title,xlabel,row['law_value'],row['generated_mean'],row['seed_min'],row['seed_max'],row['reference_sample_estimate'],lim))

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titleweight':'bold',
                     'axes.labelcolor':'#253147','text.color':'#253147','svg.fonttype':'none'})
fig, axes = plt.subplots(2,2,figsize=(11.2,6.4))
for ax,(title,xlabel,lv,gv,gmin,gmax,rv,lim) in zip(axes.flat,panels):
    ax.set_title(title.replace(': ', '\n'),loc='left',fontsize=10.5,pad=14)
    ax.set_yticks([2,1,0],['Chosen model law','Frozen generated tables','Existing sample reference'])
    ax.scatter([lv],[2],marker='D',s=52,color='#2563A6',zorder=3)
    ax.plot([gmin,gmax],[1,1],color='#7955B3',linewidth=3,zorder=2)
    ax.scatter([gv],[1],s=52,color='#7955B3',zorder=3)
    ax.scatter([rv],[0],marker='s',s=52,color='#C95B4D',zorder=3)
    for value,y in ((lv,2),(gv,1),(rv,0)):
        ax.annotate(f'{value:.3f}',(value,y),xytext=(0,10),textcoords='offset points',ha='center',fontsize=10)
    ax.set_xlim(*lim); ax.set_ylim(-.5,2.6); ax.set_xlabel(xlabel,fontsize=9)
    ax.grid(axis='x',color='#E1E5EB',lw=.7); ax.set_axisbelow(True)
    for s in ('top','right','left'): ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color('#A3ADBB'); ax.tick_params(axis='y',length=0,labelsize=9)
fig.suptitle('Diagnosis: the outputs follow the chosen models',fontsize=17,fontweight='bold',x=.05,ha='left',y=.985)
fig.text(.05,.925,'Analytical implications and existing frozen summaries; no new cohorts were generated.',fontsize=10,color='#596579')
fig.text(.05,.032,'Purple segments: range of three existing seeds, not confidence intervals. Reference uncertainty is not shown.\nLaw–reference differences describe mismatch; they do not identify its causal source or prove population bias.',fontsize=9,color='#596579')
fig.subplots_adjust(left=.23,right=.98,top=.84,bottom=.17,wspace=.9,hspace=.75)
fig.savefig(HERE/'QUALITY_DIAGNOSIS.png',dpi=180,facecolor='white')
fig.savefig(HERE/'QUALITY_DIAGNOSIS.svg',facecolor='white')
plt.close(fig)
print('Saved QUALITY_DIAGNOSIS.png and .svg')
