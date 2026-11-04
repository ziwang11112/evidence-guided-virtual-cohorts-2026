"""Plot all retained final coefficients from aggregate-only reports."""
from pathlib import Path
import csv
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

U = Path(__file__).resolve().parent
rows = list(csv.DictReader((U/'summary/fixed_effects_all_seeds.csv').open(encoding='utf-8')))
for row in rows:
    for k in ['estimate','se','wald_lower','wald_upper','exported_coefficient','exported_source_se']:
        row[k] = float(row[k])
terms = list(dict.fromkeys(row['term'] for row in rows))
assert len(terms)==16
colors = {'native':'#B76B30','agent':'#2266A5'}
labels = {'native':'Published-law reconstruction','agent':'Evidence-guided Agent'}
figdir = U/'figures'
figdir.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10, 'font.family':'DejaVu Sans', 'svg.fonttype':'none',
                     'axes.spines.top':False, 'axes.spines.right':False})
fig, axes = plt.subplots(4,4,figsize=(15,10.5))
for ax, term in zip(axes.flat, terms):
    subset = [r for r in rows if r['term']==term]
    reference = subset[0]['exported_coefficient']
    ax.axvline(reference, color='#5E6269', linestyle='--', linewidth=1.3)
    for i,arm in enumerate(['native','agent']):
        values = [r['estimate'] for r in subset if r['arm']==arm]
        assert len(values)==3
        center = sum(values)/3
        ax.plot([min(values),max(values)],[i,i],color=colors[arm],lw=2)
        ax.scatter(values,[i-.10,i,i+.10],color=colors[arm],s=22,zorder=3)
        ax.scatter([center],[i],marker='D',s=42,facecolor='white',edgecolor=colors[arm],zorder=4)
    ax.set_ylim(-.5,1.5)
    ax.set_yticks([0,1],['Published law','Agent'])
    ax.set_title(term.replace('age60:','Age × ').replace('hba1c_','HbA1c '),fontsize=10,loc='left')
    ax.tick_params(axis='x',labelsize=8)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=4))
    ax.grid(axis='x',alpha=.14)
fig.suptitle('HRS longitudinal source-model reconstruction: all 16 fixed effects',fontsize=16,y=.985)
fig.text(.5,.026,'Points: three fixed seeds per construction. Diamond: mean. Horizontal segment: seed range. Dashed: exported source coefficient.',ha='center',fontsize=10)
fig.text(.5,.009,'11,509 synthetic subjects × 4 visits per table. Source coefficients were provided; these are not independent patient-validation results.',ha='center',fontsize=9,color='#555555')
fig.tight_layout(rect=[0,.052,1,.96],h_pad=2,w_pad=2)
for extension in ['png','svg']:
    fig.savefig(figdir/f'all_16_fixed_effects.{extension}',dpi=180)
plt.close(fig)

fig, axes = plt.subplots(1,2,figsize=(12,5.4))
for ax,term,title in zip(axes,['age60:hba1c_U65','age60:hba1c_O65'],
                         ['HbA1c below 6.5% × age','HbA1c at/above 6.5% × age']):
    subset = [r for r in rows if r['term']==term]
    ref = subset[0]['exported_coefficient']; se = subset[0]['exported_source_se']
    ax.axvline(0,color='#BBBBBB',lw=1)
    ax.axvline(ref,color='#777777',ls='--',lw=1)
    ax.errorbar(ref,7,xerr=1.959963984540054*se,fmt='s',color='#494D54',capsize=3,ms=6)
    ticklabels=['Source estimate']
    positions=[7]
    for arm,start in [('native',5.6),('agent',2.5)]:
        for j,row in enumerate(r for r in subset if r['arm']==arm):
            y=start-j*.8
            ax.errorbar(row['estimate'],y,xerr=[[row['estimate']-row['wald_lower']],[row['wald_upper']-row['estimate']]],
                         fmt='o',color=colors[arm],capsize=2,ms=5)
            positions.append(y); ticklabels.append(('Published law' if arm=='native' else 'Agent')+' '+row['seed'])
    ax.set_yticks(positions,ticklabels)
    ax.set_title(title,loc='left',fontsize=12)
    ax.set_xlabel('Memory-score change per decade per HbA1c percentage point',fontsize=9)
    ax.set_ylim(.3,7.7)
    ax.grid(axis='x',alpha=.15)
fig.suptitle('The two prespecified scientific relationships',fontsize=15,y=.99)
fig.text(.5,.02,'Intervals are model-conditional 95% Wald intervals. Synthetic rows do not add independent clinical evidence.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.05,1,.95],w_pad=2)
for extension in ['png','svg']:
    fig.savefig(figdir/f'focal_longitudinal_relationships.{extension}',dpi=180)
plt.close(fig)
manifest={'input':{'path':'summary/fixed_effects_all_seeds.csv','sha256':hashlib.sha256((U/'summary/fixed_effects_all_seeds.csv').read_bytes()).hexdigest()},
          'all_fixed_effect_seed_points':len(rows),'fixed_terms':16,'focal_terms':2,
          'plot_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in figdir.iterdir() if p.suffix in ['.svg','.png']}}
(figdir/'FIGURE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'figure_files':len(manifest['files']),'coefficient_points':len(rows)}))
