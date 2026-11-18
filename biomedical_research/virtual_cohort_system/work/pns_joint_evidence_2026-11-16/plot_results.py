"""Plot all prespecified primary analyses after experiment closure. No refitting."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    assert (ROOT/'EXECUTION_CLOSURE.json').exists()
    rows=read(ROOT/'analysis/seed_results.json');authors=read(ROOT/'analysis/author_results.json');refs=read(ROOT/'analysis/REFERENCE_USED.json')['PNS']
    keys=['residual_correlation','bmi_sbp','bmi_dbp']
    titles=['Paired BP dependence','BMI association with SBP','BMI association with DBP']
    labels=['Residual Pearson correlation','mmHg per 5 kg/m²','mmHg per 5 kg/m²']
    order=['ORIGINAL_1','ORIGINAL_2','ORIGINAL_3','AUGMENTED_1','AUGMENTED_2','AUGMENTED_3']
    palette={'ORIGINAL':'#4361A6','AUGMENTED':'#BA5B47'}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'svg.fonttype':'none','pdf.fonttype':42})
    fig,axs=plt.subplots(1,3,figsize=(12.6,4.6),sharey=True)
    for panel,(ax,key,title,label) in enumerate(zip(axs,keys,titles,labels)):
        ax.axhspan(-.5,2.5,color='#F2F5FA',zorder=-3);ax.axhspan(2.5,5.5,color='#FCF3F0',zorder=-3)
        ref=refs[key]['value'];ax.axvline(ref,color='#252A34',linestyle='--',lw=1.5,zorder=1)
        ax.text(.98,.98,f'Reference {ref:.3f}',transform=ax.transAxes,va='top',ha='right',fontsize=9)
        for i,identity in enumerate(order):
            selected=[r for r in rows if r['id']==identity and r['estimand']==key and r['value'] is not None]
            selected=sorted(selected,key=lambda r:r['seed'])
            record=next(r for r in authors if r['id']==identity and r['estimand']==key)
            color=palette[record['arm']]
            if selected:
                xs=[r['value'] for r in selected]
                ax.plot([min(xs),max(xs)],[i,i],color=color,lw=1,alpha=.7)
                ax.scatter(xs,[i+(j-1)*.075 for j in range(len(xs))],s=18,facecolor='white',edgecolor=color,lw=1,zorder=3)
                ax.scatter([record['seed_mean']],[i],s=62,c=color,marker='D',edgecolor='white',linewidth=.8,zorder=4)
            else:ax.text(.5,i,'Unavailable',transform=ax.get_yaxis_transform(),ha='center',fontsize=8)
        ax.set_title(f'{chr(65+panel)}  {title}',loc='left',fontsize=12,fontweight='bold',pad=12)
        ax.set_xlabel(label);ax.set_yticks(range(6));ax.set_yticklabels(['Original 1','Original 2','Original 3','Added evidence 1','Added evidence 2','Added evidence 3'])
        ax.tick_params(axis='y',length=0);ax.grid(axis='x',alpha=.12);ax.set_ylim(5.5,-.5)
    fig.suptitle('Agent-found joint evidence: the same scientific analyses on new virtual cohorts',x=.08,ha='left',fontsize=14,fontweight='bold',y=.98)
    fig.legend(handles=[Line2D([0],[0],color='#252A34',linestyle='--',label='Previously exposed real-sample estimate'),Line2D([0],[0],marker='D',color='none',markerfacecolor='#6E5D80',label='Constructor mean across three draws'),Line2D([0],[0],marker='o',color='none',markeredgecolor='#6E5D80',markerfacecolor='white',label='Individual draw (not an independent author)')],loc='lower center',ncol=3,frameon=False,fontsize=9,bbox_to_anchor=(.5,.015))
    fig.subplots_adjust(left=.13,right=.98,top=.81,bottom=.22,wspace=.18)
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    for ext in ['png','svg','pdf']:fig.savefig(out/('pns_joint_evidence.'+ext),dpi=220,facecolor='white')
    plt.close(fig)
    print('Saved PNG, editable SVG and PDF; all 6 constructors and all 3 primary analyses retained.')

if __name__=='__main__':main()
