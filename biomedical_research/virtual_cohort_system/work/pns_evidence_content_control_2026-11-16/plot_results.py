"""Plot the complete frozen endpoint profile after analysis; no generation."""
from pathlib import Path
import csv,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

W=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
data=read(W/'analysis/seed_results.json')
authors=read(W/'analysis/author_results.json')
refs=read(W/'analysis/REFERENCE_USED.json')['PNS']
arms=['BASE','SUMMARY','JOINT'];colors=['#6C7486','#C77936','#5962B6']
labels=['Base','+ summaries','+ joint block']
offsets={1:-.2,2:0,3:.2};seeds=[16211,16213,16217]
panels=[('residual_correlation','a  Paired BP dependence','Residual correlation'),
        ('bmi_sbp','b  BMI–systolic BP','mmHg per 5 kg/m²'),
        ('bmi_dbp','c  BMI–diastolic BP','mmHg per 5 kg/m²'),
        ('sbp.sd_population','d  Systolic BP spread','SD (mmHg)'),
        ('dbp.sd_population','e  Diastolic BP spread','SD (mmHg)')]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,
    'axes.labelsize':9,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none',
    'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,3,figsize=(11.2,6.1))
plotted=[]
for ax,(key,title,unit) in zip(axes.flat,panels):
    ref=refs[key]['value'];ax.axhline(ref,ls=(0,(4,3)),color='#252938',lw=1.15,zorder=1)
    plotted.append({'panel':key,'kind':'sample_reference','id':'reference','seed':'','value':ref})
    for i,arm in enumerate(arms):
        for r in data:
            if r['arm']!=arm or r['estimand']!=key or r['value'] is None:continue
            author=int(r['id'].rsplit('_',1)[1]);x=i+offsets[author]+(seeds.index(r['seed'])-1)*.035
            ax.scatter(x,r['value'],s=17,color=colors[i],alpha=.38,edgecolors='none',zorder=2)
            plotted.append({'panel':key,'kind':'draw','id':r['id'],'seed':r['seed'],'value':r['value']})
        for r in authors:
            if r['arm']!=arm or r['estimand']!=key or r['seed_mean'] is None:continue
            author=int(r['id'].rsplit('_',1)[1]);x=i+offsets[author]
            ax.scatter(x,r['seed_mean'],marker='D',s=28,color=colors[i],edgecolors='white',linewidths=.45,zorder=3)
            plotted.append({'panel':key,'kind':'constructor_mean','id':r['id'],'seed':'mean','value':r['seed_mean']})
    ax.set_title(title,loc='left',fontweight='semibold',pad=9);ax.set_ylabel(unit)
    ax.set_xticks(range(3),labels);ax.set_xlim(-.5,2.5);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)

ax=axes.flat[-1]
for i,arm in enumerate(arms):
    for path in sorted((W/'calls').glob(arm+'_*/receipt.json')):
        r=read(path);cost=r.get('tariff_cost_usd')
        if cost is None:continue
        author=int(path.parent.name.rsplit('_',1)[1])
        ax.scatter(i+offsets[author],cost,s=29,color=colors[i],edgecolors='white',linewidths=.45)
        plotted.append({'panel':'cost','kind':'receipt_tariff_cost','id':path.parent.name,'seed':'','value':cost})
ax.set_title('f  Recorded construction cost',loc='left',fontweight='semibold',pad=9)
ax.set_ylabel('Estimated USD / construction');ax.set_xticks(range(3),labels)
ax.set_xlim(-.5,2.5);ax.set_ylim(bottom=0);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.suptitle('Evidence content and scientific analysis utility',x=.06,ha='left',fontsize=14,fontweight='semibold',y=.99)
handles=[Line2D([0],[0],color='#252938',ls='--',lw=1.15,label='Measured-sample reference'),
    Line2D([0],[0],marker='D',color='none',markerfacecolor='#5962B6',markeredgecolor='white',label='Constructor mean'),
    Line2D([0],[0],marker='o',color='none',markerfacecolor='#5962B6',alpha=.38,label='Saved draw')]
fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.015),ncol=3,frameon=False)
fig.text(.06,.005,'One exposed PNS case · 3 constructors per condition · 3 draws per constructor · same additional paper in the two augmented conditions',fontsize=8,color='#555C6C')
fig.tight_layout(rect=[.025,.085,1,.965],w_pad=2.2,h_pad=2.0)
dest=W/'figures';dest.mkdir(exist_ok=False)
for ext in ['png','pdf','svg']:fig.savefig(dest/f'evidence_content_control.{ext}',dpi=190,bbox_inches='tight',facecolor='white')
with (dest/'PLOTTED_VALUES.csv').open('w',encoding='utf8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['panel','kind','id','seed','value']);writer.writeheader();writer.writerows(plotted)
print(json.dumps({'figure_files':3,'plotted_values':len(plotted),'source':'complete post-closure analysis; no new fits or rows'}))
