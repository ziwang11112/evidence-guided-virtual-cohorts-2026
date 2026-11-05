"""Replot the frozen aggregate results only: no harness, row data, or evaluation.
Requires matplotlib. Pass --results RESULTS.json --out a_new_directory.
"""
from pathlib import Path
import json,statistics,hashlib,argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--results',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
args=ap.parse_args()
raw=args.results.read_bytes()
expected='8cb8a5107181ca462d80ea38152420512052d7daf15ede7ddb8ddf8d57d95672'
if hashlib.sha256(raw).hexdigest()!=expected:
    raise ValueError('Input differs from the reviewed v0.14 aggregate results')
x=json.loads(raw)
assert len(x['all_final_slots'])==18
if args.out.exists() and any(args.out.iterdir()):
    raise FileExistsError('Use a new or empty output directory; old figures are preserved')
dest=args.out
dest.mkdir(parents=True,exist_ok=True)
colors=['#4266AD','#8071BA','#CE7F60']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,
 'axes.labelsize':10,'axes.spines.top':False,'axes.spines.right':False,
 'axes.spines.left':False,'axes.edgecolor':'#CFD3DA','axes.labelcolor':'#293247',
 'xtick.color':'#596273','ytick.color':'#293247','pdf.fonttype':42,'svg.fonttype':'none'})

def panel(ax,case,endpoint,category,title,xlabel,letter):
    ids=['H01','H02','H03'] if case=='ENSANUT2018' else ['L01','L02','L03']
    slots=[s for s in x['all_final_slots'] if s['case_id']==case]
    ref=next(z['reference'] for z in slots[0][category] if z['id']==endpoint)
    iv=ref.get('interval',{})
    if iv.get('lower') is not None and iv.get('upper') is not None:
        ax.axvspan(iv['lower'],iv['upper'],color='#E8EAF0',alpha=.85,zorder=0)
    ax.axvline(ref['value'],color='#505969',lw=1.2,zorder=1)
    if category=='analyses':ax.axvline(0,color='#BBC1CA',lw=.8,ls=':',zorder=0)
    ax.scatter(ref['value'],0,c='#263147',s=46,marker='D',zorder=5)
    for index,aid in enumerate(ids):
        y=3-index
        vals=[next(z['value'] for z in s[category] if z['id']==endpoint)
              for s in slots if s['author_id']==aid]
        vals=[v for v in vals if v is not None]
        if vals:
            ax.hlines(y,min(vals),max(vals),color=colors[index],lw=2,zorder=3)
            for v,j in zip(vals,[-.10,0,.10]):ax.scatter(v,y+j,color=colors[index],s=26,zorder=4)
            ax.scatter(statistics.mean(vals),y,facecolor='white',edgecolor=colors[index],s=46,marker='D',lw=1.5,zorder=5)
    ax.set_yticks([0,1,2,3],['Sample reference',ids[2],ids[1],ids[0]])
    ax.set_ylim(-.45,3.55);ax.tick_params(axis='y',length=0,pad=5)
    ax.grid(axis='y',color='#F0F1F4',lw=.8,zorder=0)
    ax.set_xlabel(xlabel);ax.set_title(title,loc='left',pad=15,fontweight='bold')
    ax.text(-.12,1.09,letter,transform=ax.transAxes,fontsize=14,fontweight='bold',color='#263147')
    ax.margins(x=.08)

fig,axes=plt.subplots(2,3,figsize=(14,8.4))
specs=[
 ('ENSANUT2018','Q1_age10','HbA1c: age coefficient\nSex, BMI and glucose adjusted','HbA1c percentage points / 10 years'),
 ('ENSANUT2018','Q2_bmi5','HbA1c: BMI coefficient\nAge and sex adjusted','HbA1c percentage points / 5 BMI units'),
 ('ENSANUT2018','Q3_bmi5','HbA1c: BMI coefficient\nAge, sex and glucose adjusted','HbA1c percentage points / 5 BMI units'),
 ('Turkana','K02-HDL-BMI','HDL: BMI coefficient\nAge and sex adjusted','HDL mg/dL / 5 BMI units'),
 ('Turkana','K02-TC-BMI','TC: BMI coefficient\nAge and sex adjusted','TC mg/dL / 5 BMI units'),
 ('Turkana','K02-LIPID-RESIDUAL','TC–HDL residual correlation\nAge, sex and BMI adjusted','Pearson r, after age + sex + BMI')]
for ax,z,letter in zip(axes.flat,specs,'ABCDEF'):panel(ax,z[0],z[1],'analyses',z[2],z[3],letter)
fig.suptitle('Final virtual data across two scientific requests',x=.04,ha='left',fontsize=19,fontweight='bold',color='#263147')
fig.text(.04,.92,'Three independent Agent constructions per request · three fixed draws per construction · all final outputs shown',color='#596273',fontsize=11)
fig.legend(handles=[Line2D([0],[0],marker='o',ls='',color=colors[0],label='One generated table'),Line2D([0],[0],marker='D',ls='',markerfacecolor='white',markeredgecolor=colors[0],label='Mean of three draws'),Line2D([0],[0],marker='D',ls='',color='#263147',label='Exposed sample reference')],loc='lower left',bbox_to_anchor=(.03,.055),frameon=False,ncol=3)
fig.text(.04,.038,'Grey bands: A–C empirical cluster-resampling stability; D–E HC3 assumption-conditional sensitivity. F has no reference interval.',fontsize=9,color='#596273')
fig.text(.04,.017,'Bands are not acceptance margins. Seeds probe sampling variation, not clinical replication or uncertainty about model structure.',fontsize=9,color='#596273')
fig.subplots_adjust(left=.12,right=.985,top=.84,bottom=.19,wspace=.58,hspace=.72)
for ext in ('png','pdf','svg'):fig.savefig(dest/f'primary_analyses.{ext}',dpi=200,facecolor='white')
plt.close(fig)

fig,axes=plt.subplots(2,2,figsize=(11.4,7.5))
specs=[('ENSANUT2018','hba1c.sd_population','HbA1c marginal dispersion','HbA1c SD, percentage points'),
 ('ENSANUT2018','q1_residual_rms','HbA1c conditional dispersion','Full-model residual RMS, percentage points'),
 ('Turkana','total_cholesterol.sd_sample','TC marginal dispersion','TC sample SD, mg/dL'),
 ('Turkana','hdl_cholesterol.sd_sample','HDL marginal dispersion','HDL sample SD, mg/dL')]
for ax,z,letter in zip(axes.flat,specs,'ABCD'):panel(ax,z[0],z[1],'diagnostics',z[2],z[3],letter)
fig.suptitle('Relationship agreement and dispersion are separate properties',x=.04,ha='left',fontsize=16,fontweight='bold',color='#263147')
fig.text(.04,.914,'All three constructions and final draws retained; no best-model selection',color='#596273',fontsize=11)
fig.text(.04,.045,'Circles: individual tables. Open diamonds: draw means. Dark diamonds/lines: exposed sample references.',fontsize=9,color='#596273')
fig.text(.04,.021,'Grey HbA1c bands show empirical sample stability; lipid SD reference intervals are unavailable. These are descriptive comparisons.',fontsize=9,color='#596273')
fig.subplots_adjust(left=.16,right=.98,top=.82,bottom=.16,wspace=.50,hspace=.70)
for ext in ('png','pdf','svg'):fig.savefig(dest/f'dispersion.{ext}',dpi=200,facecolor='white')
plt.close(fig)

print(json.dumps({"aggregate_sha256":expected,"final_slots":18,"outputs":[str(f) for f in sorted(dest.iterdir())],"patient_data_read":False,"analysis_recomputed":False}))
