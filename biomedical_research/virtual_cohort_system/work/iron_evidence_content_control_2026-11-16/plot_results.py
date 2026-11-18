"""Complete post-closure figure; draw-level results and costs, no new generation."""
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
refdata=read(W/'analysis/REFERENCE_USED.json');refs=refdata['values']
arms=['BASE','SUMMARY','JOINT'];colors=['#6C7486','#C77936','#5962B6'];labels=['Context','+ marginals','+ joint counts']
offsets={1:-.20,2:0,3:.20};seeds=[16311,16313,16317]
panels=[('odds_ratio','a  Low-marker association','Odds ratio (log scale)',1),
        ('joint_prevalence','b  Both markers low','Joint prevalence (%)',100),
        ('spearman','c  Continuous-marker dependence','Spearman correlation',1),
        ('low_hb_fraction','d  Low hemoglobin','Hb <12 g/dL (%)',100),
        ('low_ferritin_fraction','e  Low ferritin','Ferritin <15 µg/L (%)',100)]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':9,
  'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,3,figsize=(11.3,6.1));plotted=[]
def record(panel,kind,ident,seed,value,scale):
    plotted.append({'panel':panel,'kind':kind,'id':ident,'seed':seed,'raw_value':value,'scale':scale,'display_value':value*scale})
for ax,(key,title,unit,scale) in zip(axes.flat,panels):
    ref=refs[key];ax.axhline(ref*scale,ls=(0,(4,3)),color='#252938',lw=1.15,zorder=1)
    record(key,'sample_reference','reference','',ref,scale)
    for i,arm in enumerate(arms):
        missing=0
        for r in data:
            if r['arm']!=arm or r['estimand']!=key:continue
            if r['value'] is None:missing+=1;continue
            idx=int(r['id'].rsplit('_',1)[1]);x=i+offsets[idx]+(seeds.index(r['seed'])-1)*.035
            ax.scatter(x,r['value']*scale,s=17,color=colors[i],alpha=.40,edgecolors='none',zorder=2)
            record(key,'draw',r['id'],r['seed'],r['value'],scale)
        for r in authors:
            if r['arm']!=arm or r['estimand']!=key or r['seed_mean'] is None:continue
            idx=int(r['id'].rsplit('_',1)[1])
            ax.scatter(i+offsets[idx],r['seed_mean']*scale,marker='D',s=28,color=colors[i],edgecolors='white',linewidths=.45,zorder=3)
            record(key,'constructor_mean',r['id'],'mean',r['seed_mean'],scale)
        if missing:ax.text(i,.98,f'{missing} unavailable',transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=7,color=colors[i])
    if key=='odds_ratio':ax.set_yscale('log')
    ax.set_title(title,loc='left',fontweight='semibold',pad=9);ax.set_ylabel(unit)
    ax.set_xticks(range(3),labels);ax.set_xlim(-.5,2.5);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
ax=axes.flat[-1]
for i,arm in enumerate(arms):
    for path in sorted((W/'calls').glob(arm+'_*/receipt.json')):
        r=read(path);cost=r.get('tariff_cost_usd')
        if cost is None:continue
        idx=int(path.parent.name.rsplit('_',1)[1])
        ax.scatter(i+offsets[idx],cost,s=29,color=colors[i],edgecolors='white',linewidths=.45)
        record('cost','receipt_tariff_cost',path.parent.name,'',cost,1)
ax.set_title('f  Recorded construction cost',loc='left',fontweight='semibold',pad=9)
ax.set_ylabel('Estimated USD / construction');ax.set_xticks(range(3),labels);ax.set_xlim(-.5,2.5);ax.set_ylim(bottom=0);ax.grid(axis='y',alpha=.15)
fig.suptitle('Iron status: evidence content and scientific analysis utility',x=.06,ha='left',fontsize=14,fontweight='semibold',y=.99)
handles=[Line2D([0],[0],color='#252938',ls='--',lw=1.15,label='Measured-sample reference'),
         Line2D([0],[0],marker='D',color='none',markerfacecolor='#5962B6',markeredgecolor='white',label='Constructor mean'),
         Line2D([0],[0],marker='o',color='none',markerfacecolor='#5962B6',alpha=.4,label='Saved draw')]
fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.015),ncol=3,frameon=False)
fig.text(.06,.005,'One exposed NHANES case · 3 constructions per condition · 3 draws per construction · identical source context, controlled statistic subsets',fontsize=8,color='#555C6C')
fig.tight_layout(rect=[.025,.085,1,.965],w_pad=2.2,h_pad=2.0)
dest=W/'figures';dest.mkdir(exist_ok=False)
for ext in ['png','svg']:fig.savefig(dest/f'iron_content_control.{ext}',dpi=190,bbox_inches='tight',facecolor='white')
with (dest/'PLOTTED_VALUES.csv').open('w',encoding='utf8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['panel','kind','id','seed','raw_value','scale','display_value'])
    writer.writeheader();writer.writerows(plotted)
print(json.dumps({'figure_files':2,'plotted_values':len(plotted),'scope':'all available prespecified scientific results and marginal checks; no inferential acceptance band'}))

