"""Render existing, audited aggregate evidence as a self-contained report.
No model calls, generator execution or individual records are read.
"""
from pathlib import Path
import base64, hashlib, html, json, re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

W=Path(__file__).resolve().parent
P=W.parents[1]
A=P/'docs/report-assets-2026-11-11'
A.mkdir(parents=True,exist_ok=True)
BLUE='#4169a8'; PURPLE='#8862ad'; ORANGE='#c17936'; INK='#223047'; MUTED='#606d80'; GRAY='#a3acb9'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
 'axes.edgecolor':'#d5dce6','axes.labelcolor':MUTED,'text.color':INK,'xtick.color':MUTED,'ytick.color':MUTED,
 'axes.titleweight':'bold','axes.titlesize':11,'svg.fonttype':'none','svg.hashsalt':'evc-report-2026-11-11',
 'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda rel:json.loads((P/rel).read_text(encoding='utf-8'))
audit=load('work/scientific_use_review_v30_2026-11-11/NUMERICAL_USE_AUDIT.json')
assert audit['status']=='pass'
for rel,h in audit['input_hashes'].items():assert sha(P/rel)==h,rel
records=audit['summary_records']
bp_source=json.loads((W/'BP_PLOT_DATA.json').read_text(encoding='utf-8'))
bp=bp_source['summary_records']
inventory=json.loads((W/'RESULTS_INVENTORY.json').read_text(encoding='utf-8'))
contrast=load('work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json')['agent_information_contrasts']
idx={(r['author'],r['analysis_id']):r for r in records+bp}
get=lambda a,e:idx[(a,e)]
mean=lambda a,e:get(a,e)['mean']
ref=lambda a,e:get(a,e)['reference']['value']
asset_hashes={}
def save(fig,name):
 fig.savefig(A/(name+'.svg'),bbox_inches='tight',pad_inches=.18,metadata={'Date':'2026-11-11'})
 fig.savefig(A/(name+'.png'),bbox_inches='tight',pad_inches=.18,dpi=130)
 plt.close(fig);asset_hashes[name]=sha(A/(name+'.svg'))
def style(ax):
 ax.grid(axis='x',color='#edf0f4',lw=.7,zorder=0);ax.set_axisbelow(True)
def forest(rows,endpoints,titles,units,name):
 authors=list(dict.fromkeys(r['author'] for r in rows))
 ii={(r['author'],r['analysis_id']):r for r in rows}
 fig,axs=plt.subplots(1,len(endpoints),figsize=(11.5,4.5),gridspec_kw={'wspace':.38})
 axs=np.atleast_1d(axs)
 for ax,ep,title,unit in zip(axs,endpoints,titles,units):
  rr=ii[(authors[0],ep)]['reference'];point=rr.get('value');band=rr.get('interval') or rr.get('uncertainty') or {}
  if band.get('lower') is not None and band.get('upper') is not None:
   ax.axvspan(band['lower'],band['upper'],color=ORANGE,alpha=.10,zorder=0)
  if point is not None:ax.axvline(point,color=ORANGE,lw=1.5,zorder=1)
  for j,a in enumerate(authors):
   v=ii[(a,ep)];c=PURPLE if 'WORKFLOW' in a else BLUE
   ax.plot([v['minimum'],v['maximum']],[j,j],color=c,lw=2.2,zorder=2)
   offsets=np.linspace(-.12,.12,len(v['values']))
   ax.scatter(v['values'],j+offsets,color=c,s=15,alpha=.5,zorder=3)
   ax.scatter([v['mean']],[j],color=c,s=45,edgecolors='white',lw=.8,zorder=4)
  ax.set_yticks(range(len(authors)),[a.replace('LIPID_','').replace('PNS_','').replace('BASE_','Ordinary ').replace('WORKFLOW_','Workflow ') for a in authors] if ax is axs[0] else ['']*len(authors))
  ax.invert_yaxis();ax.set_ylim(len(authors)-.35,-.65);ax.set_title(title,pad=15);ax.set_xlabel(unit,labelpad=10);style(ax)
  ax.text(.02,1.01,'Reference = '+format(point,'.3f'),transform=ax.transAxes,color=ORANGE,fontsize=9)
  lo,hi=ax.get_xlim()
  if lo<0<hi:ax.axvline(0,color=GRAY,lw=.7,ls=':',zorder=0)
 save(fig,name)

fig,axs=plt.subplots(1,3,figsize=(11.2,3.8),gridspec_kw={'width_ratios':[1.15,1,1],'wspace':.38})
for a,c,label in [('E01',BLUE,'E01'),('E02',PURPLE,'E02')]:
 vals=[mean(a,'Q2_bmi5'),mean(a,'Q3_bmi5')]
 axs[0].plot([0,1],vals,'o-',color=c,lw=2,label=label)
 for k,e in enumerate(['Q2_bmi5','Q3_bmi5']):axs[0].scatter([k]*3,get(a,e)['values'],color=c,s=14,alpha=.35)
axs[0].plot([0,1],[ref('E01','Q2_bmi5'),ref('E01','Q3_bmi5')],'D--',color=ORANGE,lw=1.5,label='Sample ref.')
axs[0].set_xticks([0,1],['Age + sex','+ glucose']);axs[0].set_title('BMI association attenuates');axs[0].set_ylabel('HbA1c pp per 5 BMI');axs[0].set_ylim(0,.113);axs[0].legend(frameon=False,fontsize=8,loc='upper right');axs[0].grid(axis='y',alpha=.12)
for ax,ep,title,unit in [(axs[1],'Q1_age10','Age association','HbA1c pp per 10 years'),(axs[2],'hba1c.sd_population','HbA1c dispersion','HbA1c pp (SD)')]:
 vals=[mean('E01',ep),mean('E02',ep),ref('E01',ep)]
 ax.bar(['E01','E02','Sample ref.'],vals,color=[BLUE,PURPLE,ORANGE],width=.54)
 ax.set_title(title);ax.set_ylabel(unit);ax.set_ylim(0,max(vals)*1.25)
 for k,v in enumerate(vals):ax.text(k,v+max(vals)*.035,format(v,'.3f'),ha='center',fontsize=9)
 ax.grid(axis='y',alpha=.12);ax.set_axisbelow(True)
save(fig,'glycemia-use')

bp_endpoints=['bmi_sbp','bmi_dbp','residual_correlation']
assert len(bp_endpoints)==3
forest(bp,bp_endpoints,['BMI → systolic BP','BMI → diastolic BP','SBP–DBP residual r'],['mmHg per 5 BMI','mmHg per 5 BMI','Pearson r'],'bp-analyses')
lipids=[r for r in records if r['author'].startswith('LIPID_')]
forest(lipids,['K02-TC-BMI','K02-HDL-BMI','K02-LIPID-RESIDUAL'],['BMI → total cholesterol','BMI → HDL','TC–HDL residual r'],['mg/dL per 5 BMI','mg/dL per 5 BMI','Pearson r'],'lipid-analyses')
authors=list(dict.fromkeys(r['author'] for r in lipids))
fig,axs=plt.subplots(1,2,figsize=(11.2,3.5),gridspec_kw={'wspace':.26})
for ax,ep,title in [(axs[0],'total_cholesterol.sd_sample','Total cholesterol SD'),(axs[1],'hdl_cholesterol.sd_sample','HDL SD')]:
 vals=[mean(a,ep) for a in authors];cols=[BLUE]*3+[PURPLE]*3
 ax.bar(range(6),vals,color=cols,width=.62);ax.axhline(ref(authors[0],ep),color=ORANGE,lw=1.5)
 ax.set_xticks(range(6),['O1','O2','O3','W1','W2','W3']);ax.set_title(title);ax.set_ylabel('mg/dL');ax.set_ylim(0,max(max(vals),ref(authors[0],ep))*1.28)
 for j,v in enumerate(vals):ax.text(j,v+.6,format(v,'.1f'),ha='center',fontsize=9)
 ax.text(.98,.92,'Reference '+format(ref(authors[0],ep),'.2f'),transform=ax.transAxes,ha='right',color=ORANGE,fontsize=9);ax.grid(axis='y',alpha=.12);ax.set_axisbelow(True)
save(fig,'lipid-dispersion')

repairauthors=['LIPID_BASE_R2','R04_GENERIC','R04_STRUCTURED']
fig,axs=plt.subplots(1,2,figsize=(11.2,3.2),gridspec_kw={'wspace':.30})
for ax,ep,title in [(axs[0],'K02-TC-BMI','BMI → total cholesterol'),(axs[1],'K02-LIPID-RESIDUAL','TC–HDL residual correlation')]:
 vals=[mean(a,ep) for a in repairauthors]
 ax.plot(range(3),vals,color=BLUE,lw=1.3);ax.scatter(range(3),vals,c=[GRAY,BLUE,PURPLE],s=65,zorder=3)
 ax.axhline(ref(repairauthors[0],ep),color=ORANGE,lw=1.5,ls='--')
 ax.set_xticks(range(3),['Initial','Ordinary review','Structured review']);ax.set_title(title);ax.set_xlim(-.25,2.25)
 ax.set_ylim(0,max(max(vals),ref(repairauthors[0],ep))*1.25);ax.set_ylabel('mg/dL per 5 BMI' if ep=='K02-TC-BMI' else 'Pearson r');ax.grid(axis='y',alpha=.12)
 for j,v in enumerate(vals):ax.annotate(format(v,'.3f'),(j,v),xytext=(0,10),textcoords='offset points',ha='center',fontsize=9)
 ax.text(2.2,ref(repairauthors[0],ep),' Sample reference',ha='right',va='bottom',color=ORANGE,fontsize=9)
save(fig,'repair-analyses')

titles=['CHNS: BMI','CHNS: glucose','CHNS: age','ENSANUT: age','ENSANUT: BMI','ENSANUT: BMI | glucose']
fig,axs=plt.subplots(3,2,figsize=(5.8,6.2),gridspec_kw={'hspace':.8,'wspace':.4})
for ax,c,t in zip(axs.flat,contrast,titles):
 v=[c['arms'][arm]['mean_constructor_mean_absolute_discrepancy'] for arm in ['E0','E1']]
 ax.barh([1,0],v,color=[GRAY,BLUE],height=.45);ax.set_yticks([1,0],['E0','E1']);ax.set_title(t,loc='left',fontsize=9);ax.set_xlim(0,max(v)*1.44);ax.set_ylim(-.5,1.5)
 for j,n in zip([1,0],v):ax.text(n+max(v)*.04,j,format(n,'.4f'),va='center',fontsize=8)
 ax.set_xlabel(c['unit'].replace('%','pp'),fontsize=7);ax.tick_params(axis='x',labelsize=7);style(ax)
save(fig,'evidence-contrast')

esc=lambda x:html.escape(str(x))
fmt=lambda x: '未提供' if x is None else format(x,'.4f')
def table(rows,headers):
 return '<div class="tablewrap"><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def aggregate_table(rs):
 out=[]
 labels={'Q1_age10':'年龄 → HbA1c','Q2_bmi5':'BMI → HbA1c','Q3_bmi5':'BMI → HbA1c（加血糖）','K02-TC-BMI':'BMI → TC','K02-HDL-BMI':'BMI → HDL','K02-LIPID-RESIDUAL':'TC–HDL 残差相关','total_cholesterol.sd_sample':'TC 标准差','hdl_cholesterol.sd_sample':'HDL 标准差','bmi_sbp':'BMI → 收缩压','bmi_dbp':'BMI → 舒张压','residual_correlation':'收缩压–舒张压残差相关'}
 for r in rs:
  reference=r['reference'];band=reference.get('interval') or reference.get('uncertainty') or {}
  uncertainty='未提供区间' if band.get('lower') is None else '['+fmt(band['lower'])+', '+fmt(band['upper'])+']'
  out.append([r['author'],labels.get(r['analysis_id'],r['analysis_id']),fmt(r['mean']),fmt(r['minimum'])+' ～ '+fmt(r['maximum']),fmt(reference.get('value'))+' '+uncertainty,r['unit'].replace('%','pp')])
 return table(out,['构造','分析','生成均值','种子范围','样本参照及保存区间','单位'])
gytable=aggregate_table([r for r in records if r['author'] in ['E01','E02'] and r['role']=='primary'])
liptable=aggregate_table([r for r in lipids if r['analysis_id'] in ['K02-TC-BMI','K02-HDL-BMI','K02-LIPID-RESIDUAL','total_cholesterol.sd_sample','hdl_cholesterol.sd_sample']])
reptable=aggregate_table([get(a,ep) for a in repairauthors for ep in ['K02-TC-BMI','K02-HDL-BMI','K02-LIPID-RESIDUAL','total_cholesterol.sd_sample','hdl_cholesterol.sd_sample']])
experiments=[
 ['11-03 主研究','CHNS + ENSANUT；给定 E0 / E1 材料','20 次独立 Agent 构造 + 4 个统计构造；72 张最终表','增加关系证据后 5 项差异下降、1 项上升；比较完整保留','main_study_freeze_2026-11-03'],
 ['11-04 自主检索复现','CHNS + ENSANUT；自己找论文','4 个新构造；12 张最终表','两种人群请求重复执行；ENSANUT 保留 BMI 调整模式','core_workflow_replication_2026-11-04'],
 ['11-10 两轮固定包 API','PNS + 血脂；多模型尝试','28 次初始尝试 + 4 次依赖检查；20 个可分析初始生成器','建模与参数来源比较；部分响应/执行失败，不能当作模型排行榜','two_round_synthesis_2026-11-10'],
 ['11-10 从请求出发的三轮','普通 Agent / workflow；自由检索','12 次构造尝试；8 个选定生成器；24 张成功最终表','接口/预算问题与修复记录分开保存；并非成对质量提升试验','request_only_agent_capacity_2026-11-10'],
 ['11-11 自主重复构造','PNS + 血脂；同一 GPT 与工具','12 个新构造；36 张表；331 次 API 调用','全部交付；分析表现不均一，无全面策略优势','request_only_repeatability_2026-11-11'],
 ['11-11 科学检查与修订','上一批 12 个生成器；两种检查策略','24 个依赖检查会话；72 张最终表；343 次 API 调用','修复 2 类缺陷；66 张表不变；分析收益混合','scientific_check_revision_2026-11-11'],
 ['11-11 用途核查与审阅包','既有血糖 + 血脂；汇总复核','8 个起始生成器 + 2 个依赖修订分支；无新实验','4 页简报与空白表已完成；尚无人工专业反馈','scientific_use_review_v30_2026-11-11']]
et='<table><thead><tr>'+''.join('<th>'+x+'</th>' for x in ['实验阶段','信息与任务','正确计数口径','回答什么问题'])+'</tr></thead><tbody>'
for row in experiments:
 linkfile='RESULTS_SUMMARY.md' if row[-1]=='two_round_synthesis_2026-11-10' else 'RESULTS.md'
 et+='<tr><td><a href="../work/'+row[-1]+'/'+linkfile+'">'+esc(row[0])+'</a></td>'+''.join('<td>'+esc(x)+'</td>' for x in row[1:4])+'</tr>'
et+='</tbody></table>'
arch=A/'architecture.drawio.svg'
assert arch.exists(),'Architecture asset must be independently prepared before report build'
def datauri(path):return 'data:image/svg+xml;base64,'+base64.b64encode(path.read_bytes()).decode('ascii')
implementation='<p>主 API 循环实际连接 <code>literature_search / read_source / list_sources / submit_candidate / run_candidate / finalize</code>。检索使用 Europe PMC 与可获得的 PMC 原文，不是任意网站浏览器。Agent 写出 <code>generator.py</code> 和 <code>model_spec.json</code>；工具在 WSL / bubblewrap 隔离进程中执行采样。</p><p>后续成对审查另接入 <code>review_schema / inspect_law</code>。本轮主路径没有调用早期 <code>semantic_feedback_v1</code> 或通用来源人群重放，不能把仓库中的全部模块都画成已运行的同一个系统。</p><p>当前数值评价器使用预先定义的血压、血脂等分析算子。系统能根据需求构造不同模型，不等于已经自动支持任何新数据类型和任意分析模型；新任务仍需要明确变量接口及评价方式。</p>'
arch_audit=W/'ARCHITECTURE_AUDIT.json'
payload={'updated':'2026-11-11','scope':'Existing aggregates only; no new experiment','glycemia_and_lipid':records,'blood_pressure':bp,'information_contrasts':contrast,'inventory':inventory,'scientific_use_audit_sha256':sha(P/'work/scientific_use_review_v30_2026-11-11/NUMERICAL_USE_AUDIT.json')}
replacements={'ARCHITECTURE':datauri(arch),'GLYCEMIA':datauri(A/'glycemia-use.svg'),'BP':datauri(A/'bp-analyses.svg'),'LIPID':datauri(A/'lipid-analyses.svg'),'LIPID_SPREAD':datauri(A/'lipid-dispersion.svg'),'REPAIR':datauri(A/'repair-analyses.svg'),'EVIDENCE':datauri(A/'evidence-contrast.svg'),'GLYCEMIA_TABLE':gytable,'BP_TABLE':aggregate_table(bp),'LIPID_TABLE':liptable,'REPAIR_TABLE':reptable,'EXPERIMENT_TABLE':et,'IMPLEMENTATION':implementation,'REPORT_DATA':json.dumps(payload,ensure_ascii=False).replace('</','<\\/')}
template=(W/'report.template.html').read_text(encoding='utf-8')
for key,value in replacements.items():template=template.replace('@@'+key+'@@',value)
assert '@@' not in template
for rel in ['docs/research-report.html','docs/research-explainer-2026-11-04.html']:(P/rel).write_text(template,encoding='utf-8')
(P/'docs/system-explorer/index.html').write_text('''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>系统报告已更新</title><meta http-equiv="refresh" content="0; url=../research-report.html#architecture"></head><body><h1>系统与结果报告已更新至 2026-11-11</h1><p><a href="../research-report.html#architecture">打开最新版系统架构、实验结果和研究进展</a></p><p>旧设计页已保存到项目 work/html_report_refresh_2026-11-11/before/，当前报告保留历史实验与新实现的区别。</p></body></html>''',encoding='utf-8')
for rel,h in audit['input_hashes'].items():assert sha(P/rel)==h,rel
receipt={'status':'built_pending_visual_and_independent_review','path':'docs/research-report.html','sha256':sha(P/'docs/research-report.html'),'bytes':(P/'docs/research-report.html').stat().st_size,'asset_hashes':asset_hashes,'source_inputs':{'scientific_use_audit':sha(P/'work/scientific_use_review_v30_2026-11-11/NUMERICAL_USE_AUDIT.json'),'bp_plot_data':sha(W/'BP_PLOT_DATA.json'),'main_results':sha(P/'work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json'),'inventory':sha(W/'RESULTS_INVENTORY.json')},'new_api_calls':0,'new_generation':0,'individual_records_read':False}
(W/'BUILD.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
