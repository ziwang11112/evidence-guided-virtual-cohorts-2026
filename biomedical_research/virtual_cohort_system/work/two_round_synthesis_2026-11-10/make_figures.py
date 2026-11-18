from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
U=Path(__file__).resolve().parent
COL={'OA_SOL':'#315B96','OA_ASTRA':'#BE7348','DS_PRO':'#8463A5','CL_FABLE':'#B89236','GE_CARBON':'#89909B'}
NAME={'OA_SOL':'Sol','OA_ASTRA':'Astra','DS_PRO':'DeepSeek','CL_FABLE':'Fable','GE_CARBON':'Gemini'}
def label(r):
 ident=r['version_id'];suffix=ident.split('_')[-1]
 if r['round']=='R2' and r['model_config']=='OA_SOL':suffix=ident[-1]
 if r['round']=='R2' and r['model_config']!='OA_SOL':suffix=''
 return r['round']+'  '+NAME[r['model_config']]+' '+suffix

def main():
 v=json.loads((U/'SYNTHESIS.json').read_text());ss=v['analysis_summaries'];out=U/'figures';out.mkdir(exist_ok=True)
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
 fig,axs=plt.subplots(1,2,figsize=(13,8));fig.subplots_adjust(left=.14,right=.98,top=.83,bottom=.28,wspace=.42)
 for ax,case,aid,title in zip(axs,['PNS','lipids'],['residual_correlation','K02-LIPID-RESIDUAL'],['A  Blood pressure','B  Lipids']):
  rows=[r for r in ss if r['kind']=='initial' and r['case_id']==case and r['analysis_id']==aid and r['available_seeds']==3]
  for i,r in enumerate(rows):
   y=len(rows)-1-i;color=COL[r['model_config']];ax.plot([r['seed_min'],r['seed_max']],[y,y],color=color,lw=1.7);ax.scatter(r['seed_mean'],y,color=color,s=42,zorder=4)
   if isinstance(r['validated_population_value'],(float,int)):ax.scatter(r['validated_population_value'],y,marker='x',color='#222F43',s=30,linewidth=1,zorder=5)
  ref=rows[0]['reference_value'];unc=rows[0]['reference_uncertainty'];ax.axvline(ref,color='#374152',ls='--',lw=1.5)
  if unc.get('lower') is not None:ax.axvspan(unc['lower'],unc['upper'],color='#C8CED7',alpha=.38,lw=0)
  ax.set_yticks(range(len(rows)),[label(r) for r in rows][::-1]);ax.tick_params(axis='y',length=0);ax.set_ylim(-.65,len(rows)-.35);ax.set_xlim(0,.8 if case=='PNS' else .6);ax.set_title(title+f"  ({len(rows)} initial constructions)",loc='left',fontweight='bold');ax.set_xlabel('Age / sex / BMI-adjusted residual Pearson correlation');ax.grid(axis='x',alpha=.12)
 fig.suptitle('Residual dependence stays below the sample references',x=.14,y=.97,ha='left',fontsize=18,fontweight='bold',color='#202D43')
 fig.text(.14,.905,'Two fixed evidence packets, multiple constructions; this is a repeated pattern within two tasks.',fontsize=11,color='#5E6675')
 handles=[Line2D([0],[0],color=c,marker='o',label=NAME[k],lw=1.5) for k,c in COL.items() if k!='GE_CARBON']+[Line2D([0],[0],marker='x',ls='',color='#222F43',label='Statically validated law value, when available')]
 fig.legend(handles=handles,loc='lower left',bbox_to_anchor=(.13,.105),ncol=3,frameon=False,fontsize=10)
 fig.text(.14,.04,'Dots: three-seed means; whiskers: seed ranges, not confidence intervals. Dashed: previously exposed real-sample reference.\nPNS shading: conditional IID row-resampling stability; lipid residual interval unavailable. No equivalence margins.\nEight initial attempts produced no usable table; their failures remain in the complete ledger. Reviews are excluded from independent-construction counts.',fontsize=9,color='#626B79')
 for ext in ['png','pdf','svg']:fig.savefig(out/('residual_dependence.'+ext),dpi=200,facecolor='white')
 plt.close(fig)
 fig,axs=plt.subplots(1,2,figsize=(12,7));fig.subplots_adjust(left=.16,right=.98,top=.8,bottom=.28,wspace=.35)
 for ax,aid,anchor,title in zip(axs,['bmi_sbp','bmi_dbp'],[3.877,2.9835],['A  BMI to systolic blood pressure','B  BMI to diastolic blood pressure']):
  rows=[r for r in ss if r['kind']=='initial' and r['case_id']=='PNS' and r['analysis_id']==aid and r['available_seeds']==3]
  ref=rows[0]['reference_value'];unc=rows[0]['reference_uncertainty'];ax.axvspan(unc['lower'],unc['upper'],color='#C8CED7',alpha=.3,lw=0);ax.axvline(ref,color='#374152',ls='--',lw=1.4);ax.axvline(anchor,color='#AE8B35',ls=':',lw=1.7)
  for i,r in enumerate(rows):
   y=len(rows)-1-i;law=r['validated_population_value'];color=COL[r['model_config']]
   ax.plot([r['seed_min'],r['seed_max']],[y,y],color=color,lw=1.4);ax.scatter(r['seed_mean'],y,c=color,s=40,zorder=3);ax.scatter(law,y,marker='D',facecolors='white',edgecolors='#1C293E',s=34,zorder=4)
  ax.set_yticks(range(len(rows)),[label(r) for r in rows][::-1]);ax.tick_params(axis='y',length=0);ax.set_title(title,loc='left',fontweight='bold');ax.set_xlabel('Adjusted coefficient: mmHg per 5 kg/m²');ax.grid(axis='x',alpha=.12);ax.set_ylim(-.6,len(rows)-.35)
 fig.suptitle('Source anchor, completed model, generated analysis',x=.16,y=.96,ha='left',fontsize=18,fontweight='bold',color='#202D43')
 fig.text(.16,.88,'PNS illustrates a source-to-target bridge: correct unit conversion does not establish transport.',fontsize=11,color='#5E6675')
 handles=[Line2D([0],[0],color='#AE8B35',ls=':',label='INTERSALT source coefficient × 5'),Line2D([0],[0],marker='D',mfc='white',color='#1C293E',ls='',label='Completed-law adjusted coefficient'),Line2D([0],[0],marker='o',color='#315B96',label='Generated mean / seed range'),Line2D([0],[0],color='#374152',ls='--',label='Existing sample reference')]
 fig.legend(handles=handles,loc='lower left',bbox_to_anchor=(.15,.10),ncol=2,frameon=False,fontsize=10)
 fig.text(.16,.035,'R2 Astra adds an explicit assumed omitted-adjustment contribution; the changed model coefficient is not a unit-conversion error.\nSource adjustment, centre pooling, ages and measurement differ from the target analysis. Grey bands are sample stability, not equivalence.',fontsize=9,color='#626B79')
 for ext in ['png','pdf','svg']:fig.savefig(out/('source_model_analysis.'+ext),dpi=200,facecolor='white')
 print(json.dumps({'figure_files':[str(p.relative_to(U)) for p in out.glob('*')]}))
if __name__=='__main__':main()
