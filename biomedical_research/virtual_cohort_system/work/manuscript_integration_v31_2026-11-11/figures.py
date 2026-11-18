"""Publication-size plots from already computed aggregates only."""
from pathlib import Path
import json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
R=Path(__file__).resolve().parent;P=R.parents[1]
S=P/'work/lifestyle_application_2026-11-11/ANALYSIS_RESULTS.json'
F=P/'manuscript/paper_figures_v31_2026-11-11';F.mkdir(exist_ok=True)
data=json.loads(S.read_text())['results'];reference=next(d for d in data if d['kind']=='real_reference')
traits=['bmi','total_cholesterol','hdl_cholesterol'];titles=['BMI','Total cholesterol','HDL cholesterol']
contrast=['rural_minus_pastoralist','urban_minus_pastoralist','urban_minus_rural']
labels=['Rural - pastoralist','Urban - pastoralist','Urban - rural']
colors=['#233C62','#7653AA','#D68032'];records=[]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':9,'axes.titlesize':11,
 'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,
 'axes.spines.left':False,'axes.edgecolor':'#c7ceda','text.color':'#23344d','xtick.color':'#465670','ytick.color':'#465670'})
def get(d,t,c):
    return next(r for r in d['analysis']['contrasts'] if (r['trait'],r['stratum'],r['contrast'])==(t,'pooled',c))
for raw,name in [(True,'fig3-lifestyle-raw'),(False,'figS8-lifestyle-standardized')]:
    fig,axes=plt.subplots(3,1,figsize=(7.0,7.7))
    fig.subplots_adjust(left=.225,right=.975,top=.95,bottom=.10,hspace=.67)
    prefix='raw_' if raw else ''
    for j,(ax,t,title) in enumerate(zip(axes,traits,titles)):
        for k,c in enumerate(contrast):
            y=2-k;real=get(reference,t,c);x,lo,hi=[real[prefix+n] for n in ['estimate','lower','upper']]
            ax.errorbar(x,y+.18,xerr=[[x-lo],[hi-x]],fmt='D',ms=4.0,elinewidth=1.25,capsize=2.5,color=colors[0],zorder=5)
            records.append(dict(figure=name,trait=t,contrast=c,dataset='real',x=x,lower=lo,upper=hi))
            for ep,offset,color,marker in zip(['LIFESTYLE_A1','LIFESTYLE_A2'],[0,-.18],colors[1:],['o','s']):
                ds=sorted([d for d in data if d.get('episode_id')==ep],key=lambda d:d['seed'])
                xs=[get(d,t,c)[prefix+'estimate'] for d in ds];ax.hlines(y+offset,min(xs),max(xs),color=color,lw=2.2,alpha=.5)
                for ii,(d,x) in enumerate(zip(ds,xs)):
                    ax.plot(x,y+offset+.035*(ii-1),marker,ms=4.2,color=color,mec='white',mew=.5,zorder=6)
                    records.append(dict(figure=name,trait=t,contrast=c,dataset=d['dataset_id'],x=x))
        n=next(v['n'] for v in reference['analysis']['trait_status'] if v['trait']==t)
        ax.set_title(f'{"ABC"[j]}  {title}',loc='left',fontweight='bold',pad=7)
        ax.text(1,1.07,f'Reference n={n:,}',transform=ax.transAxes,ha='right',va='bottom',fontsize=8,color='#59657a')
        ax.set_yticks([2,1,0],labels);ax.tick_params(axis='y',length=0,pad=7)
        ax.set_ylim(-.5,2.5);ax.axvline(0,lw=.85,ls=(0,(3,3)),color='#9da9bc')
        ax.grid(axis='x',lw=.5,color='#e6eaf2');ax.set_axisbelow(True)
        ax.set_xlabel(('kg/m²' if t=='bmi' else 'mg/dL') if raw else 'Within-dataset outcome SD',labelpad=3)
        if not raw:ax.set_xlim(-.62,1.08)
    handles=[Line2D([],[],marker='D',ms=4,color=colors[0],lw=1.3,label='Real estimate + 95% CI'),Line2D([],[],marker='o',ms=4,color=colors[1],lw=2,label='A1: 3 draws'),Line2D([],[],marker='s',ms=4,color=colors[2],lw=2,label='A2: 3 draws')]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.022),ncol=3,frameon=False,fontsize=8,handlelength=1.5,columnspacing=1.7)
    fig.text(.5,.008,'Synthetic segments show draw ranges, not confidence intervals.',ha='center',fontsize=7.5,color='#59657a')
    for ext in ['pdf','svg','png']:fig.savefig(F/(name+'.'+ext),dpi=180,facecolor='white')
    plt.close(fig)
manifest=dict(aggregate_input_sha256=hashlib.sha256(S.read_bytes()).hexdigest(),plotted_records=records,
    files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in F.glob('*')},patient_rows_read=False,new_scientific_estimates=False)
(R/'FIGURE_DATA.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
assert len(records)==126
print('Two publication-size figures; 126 plotted records; aggregate inputs only')
