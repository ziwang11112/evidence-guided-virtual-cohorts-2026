"""Plot every primary analysis from the sealed, aggregate-only evaluation."""
from pathlib import Path
import json
import hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parent
COLORS=['#4565B5','#9163B5','#D98148']
PANELS=[('ENSANUT2018','Q1_age10','Age–HbA1c\nAdjusted for BMI, sex and glucose','HbA1c percentage points / 10 years'),
        ('ENSANUT2018','Q2_bmi5','BMI–HbA1c\nAdjusted for age and sex','HbA1c percentage points / 5 BMI'),
        ('ENSANUT2018','Q3_bmi5','BMI–HbA1c\nAlso adjusted for glucose','HbA1c percentage points / 5 BMI'),
        ('Turkana','K02-HDL-BMI','BMI–HDL cholesterol\nAdjusted for age and sex','mg/dL / 5 BMI'),
        ('Turkana','K02-TC-BMI','BMI–total cholesterol\nAdjusted for age and sex','mg/dL / 5 BMI'),
        ('Turkana','K02-LIPID-RESIDUAL','Residual TC–HDL association\nAdjusted for age, sex and BMI','Pearson correlation')]


def main():
    completed=json.loads((ROOT/'EVALUATION_COMPLETED.json').read_text())
    raw=(ROOT/'EVALUATION.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==completed['outputs']['EVALUATION.json']
    report=json.loads(raw)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
        'axes.spines.right':False,'axes.labelcolor':'#303440','text.color':'#232834',
        'axes.edgecolor':'#89909C','pdf.fonttype':42})
    fig,axs=plt.subplots(2,3,figsize=(13.2,8.0))
    for i,(ax,(case,endpoint,title,unit)) in enumerate(zip(axs.flat,PANELS)):
        rows=[r for r in report['construction_summaries'] if r['case_id']==case and r['id']==endpoint]
        assert len(rows)==3
        reference=rows[0]['reference']; ref=reference['value']
        interval=reference['uncertainty']['interval']
        if interval['status']=='available':
            ax.axhspan(interval['lower'],interval['upper'],color='#BEC4CE',alpha=.3,zorder=0)
        if ref is not None:
            ax.axhline(ref,color='#4A515E',lw=1.5,ls='--',zorder=1)
        ax.axhline(0,color='#DDE1E8',lw=.8,zorder=0)
        for j,arm in enumerate('ABC'):
            row=next(r for r in rows if r['arm']==arm)
            vals=[]
            for slot in report['all_slots']:
                if slot['case_id']==case and slot['arm']==arm:
                    item=next(r for r in slot['analyses'] if r['id']==endpoint)
                    if item['status']=='computed': vals.append(item['value'])
            ax.scatter(j+np.linspace(-.075,.075,len(vals)),vals,s=32,color=COLORS[j],alpha=.75,zorder=3)
            if vals: ax.scatter(j,np.mean(vals),s=74,marker='D',color=COLORS[j],edgecolor='white',lw=.8,zorder=4)
            ax.text(j,.03,f'{len(vals)}/3 draws',transform=ax.get_xaxis_transform(),ha='center',fontsize=8,color='#697182')
        ax.set_xlim(-.5,2.5);ax.set_xticks(range(3),['Base','+ Rubric','+ Rubric + Skill'])
        ax.set_title(title,fontsize=11,fontweight='bold',pad=11)
        ax.set_ylabel(unit,fontsize=9)
        ax.grid(axis='y',color='#E7EAF0',lw=.6);ax.set_axisbelow(True)
        ax.text(-.15,1.1,chr(97+i),transform=ax.transAxes,fontsize=14,fontweight='bold')
        ax.margins(y=.18)
    fig.suptitle('Scientific analyses of generated biomedical cohorts',fontsize=17,fontweight='bold',y=.985)
    fig.text(.5,.943,'Two cases · six authored programs · three draws per program',ha='center',fontsize=11,color='#606878')
    fig.text(.5,.025,'Dots: all generated draws  |  Diamonds: draw means  |  Dashed line and grey band: reference estimate and available interval',ha='center',fontsize=9)
    fig.text(.5,.006,'Developmental comparison: one author per condition and case; seed variation is not an estimate of method superiority.',ha='center',fontsize=9,color='#606878')
    fig.tight_layout(rect=[.01,.055,.995,.925],h_pad=2.6,w_pad=2.1)
    fig.savefig(ROOT/'primary_analyses.png',dpi=200,facecolor='white')
    fig.savefig(ROOT/'primary_analyses.pdf',facecolor='white')
    plt.close(fig)
    print('Saved all six primary analyses; no omitted endpoint or selected seed.')


if __name__=='__main__':main()
