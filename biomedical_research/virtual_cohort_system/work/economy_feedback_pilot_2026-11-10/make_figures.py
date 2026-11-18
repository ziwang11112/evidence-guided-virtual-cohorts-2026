from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
U=Path('work/economy_feedback_pilot_2026-11-10');v=json.loads((U/'EVALUATION.json').read_text());out=U/'figures';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.labelsize':10,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
items={(r['version_id'],r['id']):r for r in v['version_summaries']};colors=['#315B96','#6D77B8','#B66B43','#818894','#8A6AA7','#CE6849']
fig,axs=plt.subplots(2,3,figsize=(13,8.5));fig.subplots_adjust(left=.17,right=.98,top=.84,bottom=.24,wspace=.32,hspace=.50)
for ci,(case,prefix,ends,titles,unit) in enumerate([('PNS','PNS',['bmi_sbp','bmi_dbp','residual_correlation'],['BMI to systolic BP','BMI to diastolic BP','BP residual correlation'],'mmHg per 5 BMI units'),('lipids','LIPID',['K02-HDL-BMI','K02-TC-BMI','K02-LIPID-RESIDUAL'],['BMI to HDL cholesterol','BMI to total cholesterol','Lipid residual correlation'],'mg/dL per 5 BMI units')]):
 ids=[prefix+x for x in ['_SOL_A','_SOL_B','_ASTRA','_DS','_SOL_A_SECOND_LOOK','_SOL_A_FEEDBACK']]
 labels=['Sol A (initial)','Sol B (initial)','Astra (initial)','DeepSeek (initial)','Sol A + ordinary review','Sol A + feedback']
 for j,e in enumerate(ends):
  ax=axs[ci,j];ref=items[(ids[0],e)]['reference'];unc=ref['uncertainty']
  if unc.get('lower') is not None:ax.axvspan(unc['lower'],unc['upper'],color='#BAC2CE',alpha=.28,lw=0)
  ax.axvline(ref['value'],color='#343D4C',lw=1.4,ls='--')
  for i,ident in enumerate(ids):
   r=items[(ident,e)];y=5-i
   if r['seed_mean'] is not None:
    lo,hi=r['seed_range'];ax.plot([lo,hi],[y,y],color=colors[i],lw=2);ax.scatter(r['seed_mean'],y,c=colors[i],s=42,zorder=4)
   else:ax.text(.02,y,'No usable table',transform=ax.get_yaxis_transform(),color='#777E88',fontsize=9,va='center')
  ax.set_yticks(range(6),labels[::-1] if j==0 else ['']*6);ax.tick_params(axis='y',length=0);ax.set_ylim(-.55,5.55);ax.grid(axis='x',alpha=.13)
  ax.set_title(chr(65+ci*3+j)+'  '+titles[j],loc='left',fontweight='bold');ax.set_xlabel('Correlation' if j==2 else unit)
fig.suptitle('Scientific analyses under the economy configuration',x=.17,y=.97,ha='left',fontsize=19,fontweight='bold',color='#1E2B44')
fig.text(.17,.915,'Two source packets • 3 evaluation seeds per version • 3,000 rows per table',fontsize=11,color='#5D6675')
fig.legend(handles=[Line2D([0],[0],color='#315B96',marker='o',label='Generated mean and three-seed range (not a confidence interval)'),Line2D([0],[0],color='#343D4C',ls='--',label='Previously exposed real-sample reference')],loc='lower left',bbox_to_anchor=(.16,.07),frameon=False,fontsize=10)
fig.text(.17,.035,'Shading: PNS IID row-resampling stability; lipid coefficients HC3 conditional sensitivity. These are not equivalence bands.\nDeepSeek: PNS execution failure; lipid transport failure. Review rows share their initial parent and are not independent authors.',fontsize=9,color='#626B79')
for ext in ['png','pdf','svg']:fig.savefig(out/('scientific_analyses.'+ext),dpi=200,facecolor='white')
plt.close(fig)
ids=['LIPID_SOL_A','LIPID_SOL_A_SECOND_LOOK','LIPID_SOL_A_FEEDBACK'];labels=['Initial','Ordinary review','With feedback'];chosen={ident:[s for s in v['all_slots'] if s['version_id']==ident] for ident in ids}
fig,axes=plt.subplots(1,2,figsize=(11,5.5));fig.subplots_adjust(top=.76,bottom=.23,wspace=.35)
for i,ident in enumerate(ids):
 ages=[s['additional_generated_diagnostics']['margins_in_delivered_units']['age']['maximum'] for s in chosen[ident]]
 axes[0].scatter([i-.12,i,i+.12],ages,color=colors[[0,4,5][i]],s=48,zorder=3)
 count=sum(s['additional_generated_diagnostics']['component_gap']['negative_count'] for s in chosen[ident]);axes[1].bar(i,count,color=colors[[0,4,5][i]],width=.55);axes[1].text(i,count+1,str(count),ha='center',fontsize=12)
axes[0].axhline(100,color='#999EAA',ls=':',lw=1);axes[0].set_ylabel('Maximum generated age (years)');axes[0].set_ylim(0,330);axes[0].set_title('A  Age-tail revision',loc='left',fontweight='bold')
axes[1].set_ylabel('HDL > total cholesterol: rows / 9,000');axes[1].set_ylim(0,45);axes[1].set_title('B  Primary consistency endpoint unchanged',loc='left',fontweight='bold')
for ax in axes:ax.set_xticks(range(3),labels);ax.grid(axis='y',alpha=.12);ax.set_axisbelow(True)
fig.suptitle('A local repair, with a clear remaining limit',x=.125,y=.96,ha='left',fontsize=18,fontweight='bold',color='#1E2B44')
fig.text(.125,.85,'One fixed lipid parent; paired evaluation seeds; every delivered row retained.',fontsize=11,color='#5D6675')
fig.text(.125,.07,'The Agent introduced the age cap of 100 as an assumption, not a literature-derived or target-validated boundary.\nAll non-age columns match exactly across these versions; changing age alone leaves lipid coherence unchanged.\nThis secondary tail redesign does not constitute improvement on the prespecified primary endpoint.',fontsize=9,color='#626B79')
for ext in ['png','pdf','svg']:fig.savefig(out/('paired_feedback.'+ext),dpi=200,facecolor='white')
print(json.dumps({'figures':[str(p) for p in sorted(out.glob('*'))]}))
