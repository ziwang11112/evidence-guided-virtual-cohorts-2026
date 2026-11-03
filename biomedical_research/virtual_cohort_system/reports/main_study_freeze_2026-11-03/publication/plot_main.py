"""All six prespecified uses; show all constructors/seeds, after audited closure."""
from pathlib import Path
import argparse
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
UNIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UNIT/'implementation'))
import main_session_v1 as control

TITLES={
 'CHNS2009': [('E1','BMI association | age, sex'),('E2','Glucose association | age, sex'),('E3','Age association | sex, BMI, glucose')],
 'ENSANUT2018': [('Q1_age10','Age association | sex, BMI, glucose'),('Q2_bmi5','BMI association | age, sex'),('Q3_bmi5','BMI association | age, sex, glucose')]}
COLORS={'E0':'#8c6caa','E1':'#007f7c'}

def plot(release_path,result_path,audit_path,destination):
    control.require_campaign_closed(control.READ(release_path))
    audit=control.READ(audit_path)
    assert audit['status']=='matched' and audit['result_sha256']==control.SHA(result_path)
    report=control.READ(result_path)
    assert report['release_sha256']==control.SHA(release_path)
    out=Path(destination);out.mkdir(parents=True,exist_ok=True)
    assert not (out/'main_scientific_uses.png').exists()
    fig,axes=plt.subplots(2,3,figsize=(15,9),layout='constrained')
    for row,(case,analyses) in enumerate(TITLES.items()):
        for col,(ident,title) in enumerate(analyses):
            ax=axes[row,col]
            ref=report['references'][case][ident]
            if ref['interval']['status']=='available':
                ax.axhspan(ref['interval']['lower'],ref['interval']['upper'],color='#adb5bd',alpha=.32,zorder=0)
            if ref['value'] is not None:ax.axhline(ref['value'],color='#333333',lw=1.4,zorder=1)
            ax.axhline(0,color='#cccccc',ls=':',lw=.7,zorder=0)
            labels=[]
            for x,(arm,author) in enumerate([(arm,'A%02d'%i) for arm in ['E0','E1'] for i in range(1,6)]+[('E0','S01'),('E1','S01')]):
                name=f'{case}_{arm}_{author}'
                slots=sorted([s for s in report['all_scheduled_slots'] if s['constructor_id']==name],key=lambda s:s['seed'])
                assert len(slots)==3
                values=[]
                for j,slot in enumerate(slots):
                    endpoint=next(e for e in slot['analyses'] if e['id']==ident)
                    if endpoint['value'] is not None:
                        value=endpoint['value'];values.append(value)
                        ax.scatter(x+(j-1)*.13,value,s=16,color=COLORS[arm],alpha=.6,zorder=3)
                if values:
                    ax.vlines(x,min(values),max(values),color=COLORS[arm],lw=1.4)
                    ax.scatter(x,np.mean(values),marker='D' if author=='S01' else '_',s=48,color=COLORS[arm],zorder=4)
                labels.append(f'{arm}\n{author}'+(' *' if len(values)!=3 else ''))
            ax.set_xticks(range(12),labels,fontsize=7)
            ax.set_title(f'{case}: {title}',fontsize=10)
            ax.set_ylabel('HbA1c coefficient ('+ref['unit']+')',fontsize=9)
            ax.grid(axis='y',alpha=.17);ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Prespecified scientific analyses of generated cohorts',fontsize=16)
    fig.legend(handles=[Line2D([0],[0],marker='o',ls='',color=COLORS['E0'],label='E0: marginal evidence'),Line2D([0],[0],marker='o',ls='',color=COLORS['E1'],label='E1: added relational evidence'),Line2D([0],[0],color='#333333',label='Previously exposed sample reference')],loc='outside lower center',ncol=3,frameon=False)
    for ext in ('png','pdf','svg'):fig.savefig(out/f'main_scientific_uses.{ext}',dpi=300,bbox_inches='tight')
    plt.close(fig)
    control.WRITE(out/'FIGURE_RECEIPT.json',{'code_sha256':control.SHA(__file__),'results':control.bound(result_path),'independent_audit':control.bound(audit_path),'outputs':{ext:control.SHA(out/f'main_scientific_uses.{ext}') for ext in ['png','pdf','svg']},'caption':'All 24 constructors and all three fixed final seeds. Points are individual seeds, central markers are seed means, and vertical spans are seed ranges, not inferential intervals. S01 denotes the prescribed statistical reference. A star denotes an incomplete constructor endpoint. Grey shading is the original case-specific reference interval, not an equivalence margin or population truth. Cases use different measurement units, selection and weighting. HbA1c effects are percentage-point differences per stated predictor unit. Separate panels must not be pooled as an accuracy score.'})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--release',required=True);p.add_argument('--results',required=True);p.add_argument('--audit',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    plot(a.release,a.results,a.audit,a.output)
