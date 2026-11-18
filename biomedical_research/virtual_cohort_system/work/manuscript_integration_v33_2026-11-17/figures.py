"""Vector publication figures from frozen aggregate endpoints, never patient data."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import support_plots as s
W=Path(__file__).resolve().parent;P=W.parents[1];F=s.OUT
colors=[s.GRAY,s.ORANGE,s.PURPLE];arms=['BASE','SUMMARY','JOINT']; labels=['Base','+ Summaries','+ Joint']
def panel(ax,df,ep,mult=1,ci=None):
 d=df[df.estimand==ep];assert len(d)==27
 ref=d.reference.unique();assert len(ref)==1; ref=float(ref[0])*mult
 if ci is not None:ax.axhspan(ci[0]*mult,ci[1]*mult,color=s.INK,alpha=.07,zorder=0)
 ax.axhline(ref,color=s.INK,ls='--',lw=1.15,zorder=1)
 for i,(arm,col) in enumerate(zip(arms,colors)):
  groups=list(d[d.arm==arm].groupby('id',sort=True));assert len(groups)==3
  for j,(cid,g) in enumerate(groups):
   v=g.value.to_numpy()*mult;x=i+[-.19,0,.19][j]
   ax.plot([x,x],[v.min(),v.max()],color=col,lw=1.1,zorder=2)
   ax.scatter(x+np.array([-.025,0,.025]),v,s=15,facecolor='white',edgecolor=col,lw=.8,zorder=3)
   ax.scatter([x],[v.mean()],s=40,marker='D',color=col,edgecolor='white',lw=.6,zorder=4)
   for _,r in g.iterrows():s.record(s.current_name,analysis=ep,kind='draw',condition=arm,dataset=cid,seed=int(r.seed),x=float(r.value)*mult,multiplier=mult)
   s.record(s.current_name,analysis=ep,kind='constructor_mean',condition=arm,dataset=cid,x=float(v.mean()),multiplier=mult)
 s.record(s.current_name,analysis=ep,kind='reference',x=ref,multiplier=mult,lower=None if ci is None else ci[0]*mult,upper=None if ci is None else ci[1]*mult)
 ax.set_xticks(range(3),labels,fontsize=9);ax.set_xlim(-.45,2.45);s.tidy(ax,'y')

def control(case,defs,primary,title,refcis=None):
 folder=P/'work'/f'{case}_evidence_content_control_2026-11-16/analysis'
 df=pd.read_csv(folder/'seed_results.csv'); ar=pd.read_csv(folder/'arm_results.csv')
 name='fig4-pressure-content' if case=='pns' else 'fig5-iron-content';s.current_name=name
 fig,axs=plt.subplots(2,3,figsize=(11.5,6.7));axs=axs.ravel()
 for ax,(ep,heading,unit,mult) in zip(axs,defs):
  panel(ax,df,ep,mult,(refcis or {}).get(ep));ax.set_title(heading,fontsize=12,pad=10);ax.set_ylabel(unit,fontsize=10)
  if 'correlation' in ep or ep=='spearman':ax.set_ylim(0,1);ax.set_yticks([0,.25,.5,.75,1])
  if ep=='odds_ratio':
   ax.set_yscale('log');ax.set_ylim(1.5,42);ax.set_yticks([2,5,10,20,40],['2','5','10','20','40'])
  if ep=='joint_prevalence':ax.set_ylim(0,12)
  if ep=='low_hb_fraction':ax.set_ylim(0,25)
  if ep=='low_ferritin_fraction':ax.set_ylim(0,35)
 ax=axs[5]
 da=df[df.estimand==primary]
 for i,(arm,col) in enumerate(zip(arms,colors)):
  v=da[da.arm==arm].groupby('id').absolute_reference_difference.mean()
  for j,(cid,err) in enumerate(v.items()):
   ax.scatter(i+[-.16,0,.16][j],err,color=col,s=42,marker='D',edgecolor='white',lw=.6,zorder=3)
   s.record(name,analysis=primary,kind='constructor_discrepancy',condition=arm,dataset=cid,x=float(err))
  mean=float(v.mean()); published=ar[(ar.arm==arm)&(ar.estimand==primary)].iloc[0]
  assert abs(mean-published.author_mean_absolute_reference_difference)<1e-12
  ax.plot([i-.29,i+.29],[mean,mean],color=col,lw=2.5,zorder=2)
  s.record(name,analysis=primary,kind='arm_discrepancy',condition=arm,x=mean)
 a=ar[ar.estimand==primary].set_index('arm').author_mean_absolute_reference_difference
 imp=(1-a.JOINT/a.SUMMARY)*100
 ax.set_title('f  Primary discrepancy',fontsize=12,pad=10)
 ax.set_ylabel('Absolute r difference' if case=='pns' else 'Absolute log-OR difference',fontsize=10)
 ax.set_xticks(range(3),labels,fontsize=9);ax.set_xlim(-.45,2.45)
 ax.set_ylim(0,float(da.groupby('id').absolute_reference_difference.mean().max())*1.30);s.tidy(ax,'y')
 ax.text(.97,.96,f'{imp:.1f}% lower\nJOINT vs SUMMARY',transform=ax.transAxes,ha='right',va='top',fontsize=10.5,color=s.PURPLE,bbox=dict(facecolor='white',edgecolor='none',alpha=.9,pad=2))
 for k in range(3):axs[k].set_facecolor('#FCFBFE')
 handles=[Line2D([],[],color=s.INK,ls='--',label='Measured-sample reference'),Line2D([],[],marker='D',color=s.INK,lw=0,label='One Agent construction',ms=5),Line2D([],[],marker='o',markerfacecolor='white',color=s.GRAY,lw=1,label='Three draws + range',ms=4)]
 fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.52,.008),ncol=3,frameon=False,fontsize=10)
 fig.subplots_adjust(left=.065,right=.99,top=.94,bottom=.115,wspace=.34,hspace=.52)
 s.save(fig,name)

if __name__=='__main__':
 for r,h in json.loads((W/'INPUT_BINDINGS.json').read_text())['files'].items():assert hashlib.sha256((P/r).read_bytes()).hexdigest()==h,r
 s.lifestyle();s.composition();s.pns()
 control('pns',[
 ('residual_correlation','a  Adjusted BP dependence','Residual Pearson r',1),
 ('bmi_sbp','b  BMI–systolic pressure','mmHg per 5 kg/m²',1),
 ('bmi_dbp','c  BMI–diastolic pressure','mmHg per 5 kg/m²',1),
 ('sbp.sd_population','d  Systolic variability','SD (mmHg)',1),
 ('dbp.sd_population','e  Diastolic variability','SD (mmHg)',1)],'residual_correlation','Pressure')
 ref=json.loads((P/'work/iron_evidence_content_control_2026-11-16/analysis/REFERENCE_USED.json').read_text())
 cis={k:v['ci95'] for k,v in ref['original_aggregate']['estimands'].items()}
 control('iron',[
 ('odds_ratio','a  Low-marker association','Crude odds ratio (log axis)',1),
 ('joint_prevalence','b  Both markers low','Joint prevalence (%)',100),
 ('spearman','c  Continuous association','Spearman r',1),
 ('low_hb_fraction','d  Low hemoglobin','Prevalence (%)',100),
 ('low_ferritin_fraction','e  Low ferritin','Prevalence (%)',100)],'odds_ratio','Iron',cis)
 pd.DataFrame(s.DATA).to_csv(W/'PLOTTED_VALUES.csv',index=False)
 print(json.dumps({'plotted_records':len(s.DATA),'files':len(list(F.glob('*')))}))
