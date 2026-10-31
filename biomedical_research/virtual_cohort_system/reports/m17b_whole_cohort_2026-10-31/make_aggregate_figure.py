"""Plot locked aggregate analysis results only; no patient/generator execution."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

p = Path(__file__).resolve().parent
report = json.loads((p/'custodian/results/evaluation.json').read_text())
comp = pd.read_csv(p/'custodian/results/comparisons.csv')
comp = comp[comp.stage == 'final']
out = p/'figures'
out.mkdir(exist_ok=True)
labels = [
    ('adjusted_bmi', 'Adjusted BMI association', 'mg/dL per 5 kg/m²'),
    ('adjusted_age', 'Adjusted age association', 'mg/dL per decade'),
    ('adjusted_sex', 'Female–male adjusted contrast', 'mg/dL'),
    ('bmi_curvature', 'BMI curvature contrast', 'mg/dL; second difference at BMI 25, 30, 35'),
    ('bmi_sex_interaction', 'Female–male BMI slope difference', 'mg/dL per 5 kg/m²'),
    ('male_bmi', 'Male BMI association', 'mg/dL per 5 kg/m²'),
    ('female_bmi', 'Female BMI association', 'mg/dL per 5 kg/m²'),
    ('reverse_urate', 'Reverse urate association with BMI', 'kg/m² per mg/dL')]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig, axes = plt.subplots(4,2,figsize=(12.5,12.3))
for ax,(key,title,unit) in zip(axes.flat,labels):
    ref = report['reference']['endpoints'][key]
    ax.axvspan(ref['ci95_lo'],ref['ci95_hi'],color='#E9EEF5',zorder=0)
    ax.axvline(0,color='#9099A4',linewidth=.8,linestyle=':')
    ax.errorbar(ref['estimate'],2,xerr=[[ref['estimate']-ref['ci95_lo']],[ref['ci95_hi']-ref['estimate']]],fmt='D',color='#24354B',capsize=4,markersize=6)
    for builder,y,color in [('b1',1,'#3367BA'),('b2',0,'#138A78')]:
        values=comp[(comp.builder==builder)&(comp.endpoint==key)].sort_values('seed').generated_estimate.to_numpy()
        ax.scatter(values,y+np.linspace(-.12,.12,len(values)),color=color,s=40,zorder=3)
    ax.set_yticks([0,1,2],['Agent B2','Agent B1','Real reference'])
    ax.set_ylim(-.4,2.4)
    ax.set_title(title,loc='left',fontweight='bold',fontsize=11)
    ax.set_xlabel(unit,fontsize=9)
    ax.grid(axis='x',alpha=.16)
fig.suptitle('Complete virtual cohorts from published evidence',fontsize=19,fontweight='bold',x=.07,ha='left',y=.985)
fig.text(.07,.956,'No individual records supplied · 2 Agent constructions · 3 draws each · 320 rows per cohort',fontsize=11,color='#43536A')
fig.text(.07,.026,'Reference bars/shading: 95% HC3 intervals in the fixed 320-person quota sample, not complex-survey inference.\nColored dots: stochastic draws of frozen models, not clinical replications or calibrated model uncertainty. Both models retained after feedback.',fontsize=9,color='#43536A')
fig.tight_layout(rect=[.02,.065,.99,.94],h_pad=2.1,w_pad=2.8)
fig.savefig(out/'analytical_use.png',dpi=180)
fig.savefig(out/'analytical_use.svg')
plt.close(fig)
print(str(out/'analytical_use.png'))
