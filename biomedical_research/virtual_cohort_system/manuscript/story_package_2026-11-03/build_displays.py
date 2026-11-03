"""Manuscript redraws from locked aggregates only; no generation or clinical reanalysis."""
from pathlib import Path
import hashlib,json,csv
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
U=P/'work/main_study_freeze_2026-11-03'
if not U.exists():
 U=P/'reports/main_study_freeze_2026-11-03'  # Public allowlisted export layout.
R=json.loads((U/'final_evaluation/RESULTS.json').read_text(encoding='utf-8-sig'))
A=json.loads((U/'independent_audit/RESULTS.json').read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert A['status']=='matched' and A['result_sha256']==sha(U/'final_evaluation/RESULTS.json')
assert R['unique_successful_table_contents']==R['complete_analysis_slots']==72
OUT=HERE/'figures';OUT.mkdir(exist_ok=True)
TABLES=HERE/'tables';TABLES.mkdir(exist_ok=True)
COL={'E0':'#8c6caa','E1':'#007f7c'}
PANELS={
 'CHNS2009': [('E1','BMI','Age, sex','per kg/m²'),('E2','Glucose','Age, sex','per mmol/L'),('E3','Age','Sex, BMI, glucose','per year')],
 'ENSANUT2018':[('Q1_age10','Age','Sex, BMI, glucose','per 10 years'),('Q2_bmi5','BMI','Age, sex','per 5 kg/m²'),('Q3_bmi5','BMI','Age, sex, glucose','per 5 kg/m²')]}
order=[(arm,f'A{i:02d}') for arm in ['E0','E1'] for i in range(1,6)]+[('E0','S01'),('E1','S01')]
ys=[0,1,2,3,4,5.5,6.5,7.5,8.5,9.5,11,12]
plt.rcParams.update({'font.size':7.5,'axes.titlesize':8,'axes.labelsize':7,'xtick.labelsize':7,'ytick.labelsize':7,'font.family':'DejaVu Sans','pdf.fonttype':42,'svg.fonttype':'none'})
fig,axes=plt.subplots(2,3,figsize=(180/25.4,176/25.4),sharey='row')
fig.subplots_adjust(left=.12,right=.99,bottom=.17,top=.94,hspace=.44,wspace=.24)
points=[]
for row,(case,paneldefs) in enumerate(PANELS.items()):
 for col,(endpoint,predictor,adjustment,unit) in enumerate(paneldefs):
  ax=axes[row,col];ref=R['references'][case][endpoint]
  ax.axvspan(ref['interval']['lower'],ref['interval']['upper'],color='#aeb7bf',alpha=.32,lw=0)
  ax.axvline(ref['value'],color='#222222',lw=.9)
  ax.axvline(0,color='#aaaaaa',lw=.5,ls=':')
  for y,(arm,author) in zip(ys,order):
   ident=f'{case}_{arm}_{author}'
   slots=sorted((s for s in R['all_scheduled_slots'] if s['constructor_id']==ident),key=lambda s:s['seed'])
   summary=next(x for x in R['construction_summaries'] if x['constructor_id']==ident)
   stat=next(x for x in summary['endpoints'] if x['id']==endpoint)
   assert len(slots)==3 and stat['complete']
   for j,s in enumerate(slots):
    v=next(x for x in s['analyses'] if x['id']==endpoint)['value']
    ax.scatter(v,y+(j-1)*.15,s=10,color=COL[arm],alpha=.55,edgecolors='none',zorder=3)
    points.append({'panel':chr(65+row*3+col),'case':case,'endpoint':endpoint,'constructor':ident,'seed':s['seed'],'value':v,'unit':ref['unit']})
   low,high=stat['seed_effect_range'];ax.hlines(y,low,high,color=COL[arm],lw=1.0,zorder=2)
   ax.scatter(stat['mean_effect'],y,marker='D' if author=='S01' else '|',s=23 if author=='S01' else 45,color=COL[arm],linewidths=1.4,zorder=4)
  ax.set_yticks(ys,[arm+' '+author for arm,author in order]);ax.set_ylim(12.65,-.7)
  ax.set_title(chr(65+row*3+col)+'  '+('CHNS' if row==0 else 'ENSANUT')+': '+predictor+'\nAdjusted: '+adjustment,loc='left',pad=6)
  ax.set_xlabel('HbA1c percentage points\n'+unit,labelpad=4)
  ax.xaxis.set_major_locator(MaxNLocator(4));ax.tick_params(axis='y',length=0)
  ax.grid(axis='x',alpha=.15,lw=.5);ax.spines[['top','right','left']].set_visible(False)
  for sep in [4.75,10.25]:ax.axhline(sep,color='#dddddd',lw=.5)
legend=[Line2D([0],[0],marker='o',ls='',color=COL['E0'],markersize=4,label='E0: marginal/basic evidence'),Line2D([0],[0],marker='o',ls='',color=COL['E1'],markersize=4,label='E1: additional relations'),Line2D([0],[0],color='#222222',lw=.9,label='Sample reference'),Patch(facecolor='#aeb7bf',alpha=.32,label='Reference uncertainty')]
legend += [Line2D([0],[0],marker='o',ls='',color='#777777',alpha=.55,markersize=3,label='Individual seed'),Line2D([0],[0],marker='|',ls='',color='#555555',markersize=6,label='Agent constructor mean'),Line2D([0],[0],marker='D',ls='',color='#555555',markersize=4,label='Statistical constructor mean'),Line2D([0],[0],color='#777777',lw=1,label='Seed minimum–maximum')]
fig.legend(handles=legend,loc='lower center',bbox_to_anchor=(.54,.008),ncol=3,frameon=False,fontsize=6.3,columnspacing=1.2,handlelength=1.5)
for ext in ['png','pdf','svg']:fig.savefig(OUT/f'figure2_all_scientific_uses.{ext}',dpi=360)
plt.close(fig)
with (TABLES/'figure2_plotted_values.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(points[0]));w.writeheader();w.writerows(points)
assert len(points)==216
with (TABLES/'table2_information_contrasts.csv').open('w',encoding='utf-8',newline='') as f:
 fields=['case','endpoint','unit','reference','E0_MAD','E1_MAD','E1_minus_E0']
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for x in R['agent_information_contrasts']:
  w.writerow({'case':x['case_id'],'endpoint':x['endpoint'],'unit':x['unit'],'reference':R['references'][x['case_id']][x['endpoint']]['value'],'E0_MAD':x['arms']['E0']['mean_constructor_mean_absolute_discrepancy'],'E1_MAD':x['arms']['E1']['mean_constructor_mean_absolute_discrepancy'],'E1_minus_E0':x['E1_minus_E0_mean_absolute_discrepancy']})

# Native editable method schematic; explanatory data-flow arrows, not biological causation.
model=ET.Element('mxGraphModel',{'dx':'1000','dy':'560','grid':'0','page':'0','background':'#ffffff','adaptiveColors':'auto'})
root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',{'id':'0'});ET.SubElement(root,'mxCell',{'id':'1','parent':'0'})
def box(ident,label,x,y,w,h,fill='#ffffff',stroke='#b8c1cc',font=16,bold=False):
 style=f'rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontColor=#172b4d;fontFamily=Arial;fontSize={font};spacing=12;align=left;verticalAlign=middle;'
 if bold:style+='fontStyle=1;'
 cell=ET.SubElement(root,'mxCell',{'id':ident,'value':label,'style':style,'vertex':'1','parent':'1'});ET.SubElement(cell,'mxGeometry',{'x':str(x),'y':str(y),'width':str(w),'height':str(h),'as':'geometry'})
def edge(ident,source,target,dashed=False):
 style='edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;endFill=1;strokeColor=#43546b;strokeWidth=1.6;'
 if dashed:style+='dashed=1;'
 c=ET.SubElement(root,'mxCell',{'id':ident,'style':style,'edge':'1','source':source,'target':target,'parent':'1'});ET.SubElement(c,'mxGeometry',{'relative':'1','as':'geometry'})
box('title','Evidence-guided virtual data for a declared scientific use',30,10,930,45,stroke='none',font=24,bold=True)
box('studies','Published study reports<br>Curated external sources',30,75,205,65,fill='#f0f3f7',font=16)
box('request','Target population<br>Visible research questions',270,75,205,65,fill='#f0f3f7',font=16)
box('reference','Real-sample estimates<br>Withheld from constructors',750,75,205,65,fill='#f5f1e8',font=16)
box('packet','<b>1  Qualify evidence</b><br><br>Population and eligibility<br>Measurement and units<br>Statistic and adjustment<br>Estimate and uncertainty',30,185,205,165,fill='#edf1f7',font=16)
box('agent','<b>2  Agent constructs law</b><br><br>Joint model and parameters<br>Numerical evidence use<br>Explicit completion and<br>transport assumptions',270,185,205,165,fill='#e7f3f0',stroke='#007f7c',font=16)
box('data','<b>3  Generate virtual data</b><br><br>Execute the authored law<br>Age, sex, BMI, glucose,<br>and HbA1c<br><b>No individual inputs</b>',510,185,205,165,fill='#e7f3f0',stroke='#007f7c',font=16)
box('analysis','<b>4  Assess scientific use</b><br><br>All requested regressions<br>Direction and effect size<br>Joint/distribution checks<br>Case-specific uncertainty',750,185,205,165,fill='#f5f1e8',font=16)
box('roles','Evidence roles<br><b>Reported / derived / assumed</b>',30,390,300,60,fill='#fafbfc',font=15)
box('feedback','Optional generated-data diagnostics<br>Bounded revision, retention or stop',390,390,325,60,fill='#fafbfc',font=15)
box('scope','Main study: 2 development cases; E0 marginal/basic evidence versus E1 added relations.<br>References were previously exposed to researchers. Arrows indicate data flow, not biological causation.',30,490,925,60,stroke='none',font=15)
for ident,s,t,d in [('s1','studies','packet',False),('s2','request','agent',False),('s3','reference','analysis',False),('p1','packet','agent',False),('p2','agent','data',False),('p3','data','analysis',False),('f1','data','feedback',True),('f2','feedback','agent',True)]:edge(ident,s,t,d)
ET.ElementTree(model).write(OUT/'figure1-evidence-to-analysis.drawio',encoding='utf-8',xml_declaration=False)
receipt={'identity':'Aggregate-data redraw and explanatory method schematic; no new experiment or inference.','primary_result_sha256':sha(U/'final_evaluation/RESULTS.json'),'independent_audit_sha256':sha(U/'independent_audit/RESULTS.json'),'code_sha256':sha(Path(__file__)),'focal_values_plotted':216,'final_tables_represented':72,'constructors_represented':24,'figure2_nominal_width_mm':180,'figure2_nominal_height_mm':176,'uncertainty':'Seed ranges are not CIs. Sample-reference bands retain different case-specific definitions and are not acceptance thresholds.','outputs':{str(f.relative_to(HERE)):sha(f) for f in sorted([*OUT.glob('*'),*TABLES.glob('*')]) if f.is_file()}}
(HERE/'DISPLAY_PROVENANCE.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'figure2_values':len(points),'outputs':len(receipt['outputs']),'new_scientific_executions':0}))
