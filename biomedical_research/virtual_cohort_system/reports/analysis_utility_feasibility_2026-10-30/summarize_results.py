"""Presentation of frozen analyses only; no fitting or generator changes."""
from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

O=Path(__file__).resolve().parent
R=O/'results'
r=json.loads((R/'aggregate_report.json').read_text())
labels={'adjusted_age_per10':'Adjusted age association / 10 years',
        'adjusted_bmi_per5':'Adjusted BMI association / 5 kg/m²',
        'bmi_curvature_second_difference':'BMI curvature: quadratic contrast',
        'female_minus_male_bmi_slope_per5':'Female − male BMI slope / 5 kg/m²'}
rows=[]
for case in r['reference']:
    fig, axes=plt.subplots(2,2,figsize=(12,7.5))
    ref=r['reference'][case]['weighted']
    constructions=[c for c in r['constructions'] if c['case_id']==case]
    for ax,endpoint in zip(axes.flat,r['primary_family']):
        value=ref[endpoint]
        ax.axvline(0,color='#cbd5e1',lw=1,ls='--')
        ax.plot(value['estimate'],2,'D',color='#172554',ms=7,zorder=4)
        if value.get('ci_status')=='estimated':
            ax.hlines(2,value['ci_lower'],value['ci_upper'],color='#172554',lw=2)
        for i,c in enumerate(constructions):
            z=c['residual_summary']['weighted'][endpoint]
            color=['#0f766e','#b45309'][i]
            ax.hlines(1-i,z['minimum'],z['maximum'],color=color,lw=3)
            ax.plot(z['median'],1-i,'o',color=color,ms=7,zorder=4)
            agreements=sum(d['comparison']['weighted'][endpoint]['point_direction_agreement'] for d in c['draws'])
            rows.append(dict(case_id=case,construction_id=c['construction_id'],endpoint=endpoint,
                             reference=value['estimate'],reference_ci_lower=value.get('ci_lower'),
                             reference_ci_upper=value.get('ci_upper'),generated_median=z['median'],
                             generated_min=z['minimum'],generated_max=z['maximum'],
                             point_direction_agreement_draws=agreements,scheduled_residual_draws=3,
                             reference_inference=value.get('zero_null_screen','design_CI_unavailable')))
        ax.set_yticks([2,1,0],['Reserved real data','Construction A','Construction B'])
        ax.set_ylim(-.55,2.5)
        ax.set_title(labels[endpoint],loc='left',fontsize=11)
        ax.set_xlabel('Natural-log insulin units' if case=='nhanes_insulin' else 'HbA1c percentage points')
        for side in ['top','right','left']: ax.spines[side].set_visible(False)
        ax.grid(axis='x',alpha=.12)
    title='Fasting insulin · NHANES 2015–2016 · n = 1,961' if case=='nhanes_insulin' else 'HbA1c · PNS laboratory cohort · n = 7,979'
    fig.suptitle(title,fontsize=16,fontweight='bold',x=.06,ha='left')
    note=('Real-data line: descriptive 95% survey-design CI. ' if case=='nhanes_insulin' else 'Real-data point only: public PSU/stratum identifiers unavailable. ')
    note+='Generated lines: range of 3 residual draws; dots: median. These ranges are NOT evidence uncertainty.'
    fig.text(.06,.03,note,fontsize=9,color='#475569',wrap=True)
    fig.tight_layout(rect=(.025,.08,1,.94),h_pad=3,w_pad=2)
    fig.savefig(R/(case+'_analysis.png'),dpi=180)
    fig.savefig(R/(case+'_analysis.svg'))
    plt.close(fig)
summary=pd.DataFrame(rows)
summary.to_csv(R/'primary_summary.csv',index=False)
details=[]
for c in r['constructions']:
    case=c['case_id'];ref=r['reference'][case]['weighted']
    for name in ['weighted_arithmetic_mean','derived_homa1_ir_mean']:
        if name not in ref:continue
        z=c['residual_summary']['weighted'][name]
        details.append({'case_id':case,'construction_id':c['construction_id'],'endpoint':name,
                        'reference':ref[name]['estimate'],**{k:z[k] for k in ['median','minimum','maximum']}})
pd.DataFrame(details).to_csv(R/'diagnostic_means.csv',index=False)
print(summary.to_string(index=False))
print('DIAGNOSTIC MEANS')
print(pd.DataFrame(details).to_string(index=False))
