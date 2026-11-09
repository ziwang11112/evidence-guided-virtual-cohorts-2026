"""Plot every frozen stage and draw; changes are not clinical quality scores."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE=Path(__file__).resolve().parent

def main():
    result=json.loads((HERE/'EVALUATION.json').read_text())
    audit=json.loads((HERE/'RECOMPUTATION.json').read_text())
    if audit['checks']!=audit['passed']:raise ValueError('Arithmetic audit failed')
    stages=result['stages'];colors=['#476EAC','#CF7545']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
        'axes.spines.right':False,'axes.labelcolor':'#283044','text.color':'#283044',
        'xtick.color':'#4F5667','ytick.color':'#4F5667','pdf.fonttype':42})
    fig,axes=plt.subplots(2,2,figsize=(10,6.7))
    metrics=[None,'K02-HDL-BMI','K02-TC-BMI','K02-LIPID-RESIDUAL']
    titles=['A  Component coherence','B  BMI–HDL analysis','C  BMI–total cholesterol analysis','D  Adjusted lipid dependence']
    labels=['Rows with HDL > total cholesterol\nper 3,000 generated rows',
            'Adjusted slope\nmg/dL per 5 kg/m² BMI',
            'Adjusted slope\nmg/dL per 5 kg/m² BMI','Pearson correlation of residuals']
    for ax,metric,title,label in zip(axes.flat,metrics,titles,labels):
        for idx,stage in enumerate(stages):
            runs=[r for r in result['runs'] if r['candidate']==stage['candidate']]
            values=[]
            for r in runs:
                if metric is None:
                    rules=r.get('coherence') or []
                    item=next((x for x in rules if x['id']=='lipid_component_order'),None)
                    value=None if item is None or item['n_unknown'] else item['n_violating']
                else:value=next(x['value'] for x in r['analyses'] if x['id']==metric)
                values.append(value)
            available=[v for v in values if v is not None]
            jitter=np.linspace(-.10,.10,len(values))
            for j,v in enumerate(values):
                if v is not None:ax.scatter(idx+jitter[j],v,s=45,c=colors[idx],edgecolors='white',linewidths=.6,zorder=3)
            if available:
                mean=sum(available)/len(available)
                ax.plot([idx-.16,idx+.16],[mean,mean],color=colors[idx],lw=2.3,zorder=2)
            if len(available)!=len(values):
                ax.text(idx,.92,f'{len(values)-len(available)} unavailable',ha='center',transform=ax.get_xaxis_transform(),fontsize=8)
        ax.set_title(title,loc='left',fontweight='bold',pad=12)
        ax.set_ylabel(label)
        ax.set_xticks(range(len(stages)),['Baseline' if i==0 else 'Agent revision' for i in range(len(stages))])
        ax.set_xlim(-.5,len(stages)-.5)
        ax.grid(axis='y',alpha=.18,zorder=0)
        if metric is None:ax.set_ylim(bottom=-.35)
    fig.suptitle('Coherence repair and its analytical consequences',x=.07,ha='left',fontsize=15,fontweight='bold')
    fig.text(.07,.025,'Each dot is one fixed-seed draw; horizontal marks are means. No real-reference comparison.\nLower violations assess the stated concentration rule; other shifts are changes, not measured improvements.',fontsize=9,color='#555D70')
    fig.tight_layout(rect=(.02,.10,.995,.94))
    fig.savefig(HERE/'coherence_and_analyses.png',dpi=220,facecolor='white')
    fig.savefig(HERE/'coherence_and_analyses.pdf',facecolor='white')
    plt.close(fig)

if __name__=='__main__':main()
