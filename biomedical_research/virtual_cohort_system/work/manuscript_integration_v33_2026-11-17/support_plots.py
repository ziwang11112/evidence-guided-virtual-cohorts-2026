"""Publication figures from closed aggregate results only; no model or patient data."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parent
P=ROOT.parents[1]
OUT=P/'manuscript/paper_figures_v33_2026-11-17'
INK='#233047'; BLUE='#4169AA'; ORANGE='#C36A37'; PURPLE='#7861AA'; GRAY='#8490A2'; GRID='#E4E8EF'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.labelsize':11,'axes.titlesize':12,
 'axes.titleweight':'bold','axes.titlelocation':'left','text.color':INK,'axes.labelcolor':INK,
 'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':'#ADB7C5','axes.linewidth':.7,
 'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})
DATA=[]

def read(rel):return json.loads((P/rel).read_text(encoding='utf-8'))
def record(fig,**kw):DATA.append({'figure':fig,**kw})
def tidy(ax,grid='x'):
    for name in ['top','right']:ax.spines[name].set_visible(False)
    ax.grid(axis=grid,color=GRID,lw=.6,zorder=0);ax.set_axisbelow(True)
    ax.tick_params(length=3,width=.6)
def save(fig,stem):
    for ext in ['pdf','svg','png']:fig.savefig(OUT/f'{stem}.{ext}',dpi=220,bbox_inches='tight',pad_inches=.07)
    plt.close(fig)

def lifestyle():
    name='fig2-scientific-use';df=pd.read_csv(P/'work/lifestyle_application_2026-11-11/ANALYSIS_CONTRASTS.csv')
    df=df[df.stratum=='pooled'];assert len(df)==63
    contrasts=['urban_minus_pastoralist','urban_minus_rural','rural_minus_pastoralist']
    labels=['Urban - pastoralist','Urban - rural','Rural - pastoralist']
    traits=[('bmi','a  BMI','kg/m²'),('total_cholesterol','b  Total cholesterol','mg/dL'),('hdl_cholesterol','c  HDL cholesterol','mg/dL')]
    fig,axes=plt.subplots(1,3,figsize=(11.7,4.2),sharey=True)
    for ax,(trait,title,unit) in zip(axes,traits):
        sub=df[df.trait==trait];assert len(sub)==21
        for j,contrast in enumerate(contrasts):
            z=sub[sub.contrast==contrast];ref=z[z.dataset_id=='real'].iloc[0]
            y=2-j
            ax.errorbar(ref.raw_estimate,y+.22,xerr=[[ref.raw_estimate-ref.raw_lower],[ref.raw_upper-ref.raw_estimate]],fmt='s',ms=5,color=INK,elinewidth=1.5,capsize=3,zorder=4)
            record(name,trait=trait,contrast=contrast,kind='real_reference',dataset='real',x=float(ref.raw_estimate),lower=float(ref.raw_lower),upper=float(ref.raw_upper),n=int(ref.n))
            for author,color,shift in [('A1',BLUE,0),('A2',ORANGE,-.20)]:
                vals=z[z.dataset_id.str.startswith('LIFESTYLE_'+author+'_')];assert len(vals)==3
                v=vals.raw_estimate.to_numpy();yy=y+shift
                ax.plot([v.min(),v.max()],[yy,yy],color=color,lw=1.4,zorder=2)
                ax.scatter(v,np.full(3,yy)+np.array([-.035,0,.035]),s=23,facecolor='white',edgecolor=color,lw=1,zorder=3)
                ax.scatter([v.mean()],[yy],s=43,marker='D',color=color,edgecolor='white',lw=.7,zorder=4)
                for _,r in vals.iterrows():record(name,trait=trait,contrast=contrast,kind='draw',dataset=r.dataset_id,x=float(r.raw_estimate))
                record(name,trait=trait,contrast=contrast,kind='constructor_mean',dataset=author,x=float(v.mean()))
        ax.axvline(0,color='#A7AFBD',lw=.7,ls=':');ax.set_title(title,pad=11);ax.set_xlabel('Adjusted contrast ('+unit+')')
        ax.set_yticks([2,1,0],labels);ax.set_ylim(-.50,2.60);tidy(ax)
    handles=[Line2D([],[],marker='s',color=INK,lw=1.5,label='Real sample: estimate + 95% CI',ms=5),
             Line2D([],[],marker='D',color=BLUE,lw=1.3,label='Agent 1: mean + draw range',ms=5),
             Line2D([],[],marker='D',color=ORANGE,lw=1.3,label='Agent 2: mean + draw range',ms=5)]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.53,.01),ncol=3,frameon=False,fontsize=10)
    fig.subplots_adjust(left=.17,right=.99,top=.88,bottom=.25,wspace=.27)
    save(fig,name)

def composition():
    name='fig3-evidence-composition';df=pd.read_csv(P/'work/evidence_composition_pilot_2026-11-16/analysis/analyses.csv')
    defs=[('adjusted','partial_xy_given_z','a  Adjusted association'),('longitudinal','change_correlation','b  Within-person changes')]
    conditions=['none','anchor_only','bridge_only','combined'];colors=[GRAY,BLUE,ORANGE,PURPLE]
    fig,axes=plt.subplots(1,2,figsize=(10.6,4.5),sharey=True)
    for ax,(family,endpoint,title) in zip(axes,defs):
        sub=df[(df.family==family)&(df.estimand==endpoint)];assert len(sub)==36
        ax.axvspan(2.58,3.42,color='#F0EBF7',zorder=0)
        for c,(cond,color) in enumerate(zip(conditions,colors)):
            group=sub[sub.condition==cond];assert len(group)==9
            for k,(cid,g) in enumerate(group.groupby('id',sort=True)):
                x=c+[-.17,0,.17][k];v=g.value.to_numpy();assert len(v)==3
                ax.plot([x,x],[v.min(),v.max()],color=color,lw=1.2)
                ax.scatter(x+np.array([-.027,0,.027]),v,s=21,facecolors='white',edgecolors=color,lw=.85,zorder=3)
                ax.scatter([x],[v.mean()],s=48,marker='D',color=color,edgecolors='white',lw=.6,zorder=4)
                for _,r in g.iterrows():record(name,task=family,condition=cond,kind='draw',dataset=cid,seed=int(r.seed),x=float(r.value),identified=bool(r.identified))
                record(name,task=family,condition=cond,kind='constructor_mean',dataset=cid,x=float(v.mean()),identified=bool(g.iloc[0].identified))
            if cond=='combined':
                refs=group.reference.unique();assert len(refs)==1 and group.identified.all();ref=float(refs[0])
                ax.hlines(ref,2.58,3.42,colors=INK,ls='--',lw=1.4)
                ax.text(3,ref+(.10 if ref<.5 else -.13),f'Identified: {ref:g}',ha='center',fontsize=10,color=INK)
                record(name,task=family,condition=cond,kind='identified_reference',x=ref)
        ax.set_title(title,pad=11);ax.set_xticks(range(4),['Basic\nsummaries','+ A','+ B','+ A + B']);ax.set_xlim(-.45,3.45)
        ax.set_ylim(-1,1);ax.set_yticks(np.arange(-1,1.01,.5));ax.axhline(0,color=GRID,lw=.7)
        ax.text(1,-.89,'Not identified: different completions are possible',ha='center',fontsize=9.5,color='#626F84')
        tidy(ax,'y')
    axes[0].set_ylabel('Correlation in generated records')
    fig.text(.52,.02,'Diamond: constructor mean    Open circles: three draws    Reference shown only where identified',ha='center',fontsize=10,color='#626F84')
    fig.subplots_adjust(left=.08,right=.99,top=.89,bottom=.19,wspace=.18)
    save(fig,name)

def pns():
    name='figS1-search-followup';rows=read('work/pns_joint_evidence_2026-11-16/analysis/seed_results.json');df=pd.DataFrame(rows)
    defs=[('residual_correlation','a  Paired BP dependence','Residual Pearson correlation'),('bmi_sbp','b  BMI - systolic BP','mmHg per 5 kg/m²'),('bmi_dbp','c  BMI - diastolic BP','mmHg per 5 kg/m²'),('sbp.sd_population','d  Systolic BP variability','SD (mmHg)'),('dbp.sd_population','e  Diastolic BP variability','SD (mmHg)')]
    fig,axes=plt.subplots(2,3,figsize=(11.7,6.7));axes=axes.ravel()
    for idx,(ax,(endpoint,title,unit)) in enumerate(zip(axes,defs)):
        sub=df[df.estimand==endpoint];assert len(sub)==18
        refs=sub.reference.unique();assert len(refs)==1;ref=float(refs[0])
        ax.axvline(ref,color=INK,ls='--',lw=1.2,zorder=1)
        ax.axhline(2.5,color=GRID,lw=.9)
        for j,cid in enumerate([f'{arm}_{i}' for arm in ['ORIGINAL','AUGMENTED'] for i in [1,2,3]]):
            g=sub[sub.id==cid];assert len(g)==3;v=g.value.to_numpy();y=5-j;color=BLUE if j<3 else ORANGE
            ax.plot([v.min(),v.max()],[y,y],color=color,lw=1.2)
            ax.scatter(v,y+np.array([-.04,0,.04]),s=19,facecolors='white',edgecolors=color,lw=.9,zorder=3)
            ax.scatter([v.mean()],[y],s=43,marker='D',color=color,edgecolors='white',lw=.65,zorder=4)
            for _,r in g.iterrows():record(name,analysis=endpoint,kind='draw',dataset=cid,arm=r.arm,seed=int(r.seed),x=float(r.value))
            record(name,analysis=endpoint,kind='constructor_mean',dataset=cid,arm=g.iloc[0].arm,x=float(v.mean()))
        record(name,analysis=endpoint,kind='real_reference',dataset='PNS',x=ref)
        ax.set_title(title,pad=12);ax.set_yticks(range(5,-1,-1),['Original 1','Original 2','Original 3','Added 1','Added 2','Added 3'] if idx in [0,3] else [])
        ax.set_ylim(-.55,5.65);ax.set_xlabel(unit)
        ax.text(.98,1.015,f'Ref. {ref:.3f}',transform=ax.transAxes,ha='right',va='bottom',fontsize=9,color='#626F84')
        tidy(ax)
    legend=axes[-1];legend.axis('off')
    handles=[Line2D([],[],color=INK,ls='--',label='Real-sample reference'),
             Line2D([],[],color=BLUE,marker='D',label='Original evidence',ms=5),
             Line2D([],[],color=ORANGE,marker='D',label='Added joint evidence',ms=5),
             Line2D([],[],color=GRAY,marker='o',markerfacecolor='white',lw=0,label='One generated draw',ms=5)]
    legend.legend(handles=handles,loc='upper left',frameon=False,fontsize=11,borderaxespad=0,handlelength=2.3,labelspacing=1)
    legend.text(0,.18,'3 constructors per arm\n3 draws per constructor\nAll five analyses shown',transform=legend.transAxes,fontsize=10.5,color='#626F84',linespacing=1.65)
    fig.subplots_adjust(left=.115,right=.99,top=.92,bottom=.085,wspace=.27,hspace=.55)
    save(fig,name)

