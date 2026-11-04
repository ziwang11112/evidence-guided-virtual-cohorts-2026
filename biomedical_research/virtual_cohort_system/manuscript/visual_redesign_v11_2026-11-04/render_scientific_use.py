"""Original v11 use-case displays from immutable v10 aggregate bindings.

Only affine display coordinates are newly calculated. No patient records,
generator, clinical fit or additional scientific experiment is executed.
"""
from pathlib import Path
import argparse
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
INPUT='manuscript/conference_figures_v10_2026-11-04/FIG45_NUMERIC_BINDINGS.json'
INPUT_SHA='fca43b243ff0d3ec9c452e409aa09681106674a441edf0d5b4261fd7cc7ccca6'
HRS_SHA='412764441069d3520374bff25fecb5d91615d431ec6f770c2646610f0bdfdfcb'
NAVY='#182647'; BLUE='#4169B1'; VIOLET='#8264B5'; CORAL='#D97762'; SLATE='#778394'
LIGHT_BLUE='#EEF2FA'; LAVENDER='#F2EEF7'; PEACH='#FCF1ED'; LINE='#DBE0E9'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def num(v,pos=None): return '0' if abs(v)<1e-12 else f'{v:.3g}'.replace('-', '−')
def rc():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7.5,
        'axes.labelsize':7.5,'xtick.labelsize':7,'ytick.labelsize':7,
        'axes.linewidth':.65,'text.color':NAVY,'axes.labelcolor':NAVY,
        'xtick.color':SLATE,'ytick.color':SLATE,
        'svg.fonttype':'none','pdf.fonttype':42,'svg.hashsalt':'v11-scientific-use-2026-11-04'})


def save(fig,out,name):
    result={}
    for ext in ('.svg','.png','.pdf'):
        path=out/(name+ext)
        metadata={'Date':None} if ext=='.svg' else ({'CreationDate':None,'ModDate':None} if ext=='.pdf' else {})
        fig.savefig(path,dpi=300,metadata=metadata)
        result[path.name]={'sha256':sha(path),'bytes':path.stat().st_size}
    plt.close(fig)
    return result


def longitudinal(binding,out):
    fig=plt.figure(figsize=(7,3.7),facecolor='white')
    fig.text(.035,.957,'(a)  Repeated-measure output',weight='bold',fontsize=9)
    fig.text(.385,.957,'(b)  Two longitudinal relationships',weight='bold',fontsize=9)
    fig.add_artist(Rectangle((.025,.12),.285,.79,transform=fig.transFigure,
                            facecolor=LIGHT_BLUE,edgecolor='none',zorder=-1))
    fig.text(.05,.838,'11,509',fontsize=21,color=BLUE,weight='bold')
    fig.text(.052,.795,'synthetic subjects per table',fontsize=7.7)
    fig.text(.05,.724,'Follow-up years',fontsize=8,weight='bold')
    structure=fig.add_axes([.064,.50,.205,.17])
    structure.plot([0,6],[0,0],color=SLATE,lw=1.2,zorder=0)
    structure.scatter([0,2,4,6],[0]*4,s=35,c=BLUE,edgecolors='white',lw=1.1,zorder=2)
    for i,t in enumerate([0,2,4,6]): structure.text(t,-.33,str(t),ha='center',va='top',fontsize=8,weight='bold')
    structure.set_xlim(-.5,6.5);structure.set_ylim(-.8,.55);structure.axis('off')
    fig.text(.05,.46,'4 visits  /  46,036 records',fontsize=8.1,weight='bold')
    fig.text(.05,.395,'Same mixed-model analysis',fontsize=7.9)
    fig.text(.05,.352,'2 constructions × 3 seeds',fontsize=7.9)
    fig.text(.05,.22,'Structure schematic',fontsize=7,color=SLATE)
    fig.text(.05,.18,'No outcome trajectory is shown.',fontsize=6.9,color=SLATE)

    ax=fig.add_axes([.50,.17,.465,.71])
    ax.set_xlim(-.082,.082);ax.set_ylim(-.85,13.6)
    ax.axvline(0,color=LINE,lw=.8,zorder=0)
    all_rows=[]; refs=[]
    groups=[(binding['figure4']['panels'][0],6.9,13.15,'HbA1c spline < 6.5%'),
            (binding['figure4']['panels'][1],-.3,5.95,'HbA1c spline ≥ 6.5%')]
    ys=[];labels=[]
    for panel,base,head,title in groups:
        source=panel['source_coefficient']
        ax.axhspan(base-.5,base+5.65,color=LAVENDER if base>0 else LIGHT_BLUE,alpha=.55,zorder=-1)
        ax.plot([source,source],[base-.5,base+5.65],color=SLATE,lw=1.1,ls=(0,(3,2)),zorder=1)
        ax.text(-.25,head,title,transform=ax.get_yaxis_transform(),ha='left',va='center',fontsize=8,weight='bold',clip_on=False)
        refs.append({'term':panel['term'],'value':source,'native_source_standard_error':panel['source_standard_error_recorded_not_plotted']})
        for arm,color,marker,offset in [('native',VIOLET,'s',3.2),('agent',BLUE,'o',0)]:
            for i,seed in enumerate((6101,6102,6103)):
                r=next(x for x in panel['coefficient_rows'] if x['arm']==arm and x['seed']==seed)
                y=base+offset+2-i
                ax.errorbar(r['estimate'],y,xerr=[[r['estimate']-r['wald_lower']],[r['wald_upper']-r['estimate']]],
                            fmt=marker,color=color,ms=4.1,capsize=2,lw=.95,zorder=3)
                ys.append(y);labels.append(('Law ' if arm=='native' else 'Agent ')+str(seed))
                all_rows.append(dict(r))
    ax.set_yticks(ys,labels);ax.tick_params(axis='y',length=0,pad=8,labelsize=6.9)
    ax.set_xticks([-.08,-.04,0,.04,.08]);ax.xaxis.set_major_formatter(FuncFormatter(num))
    ax.set_xlabel('Memory-score interaction coefficient',labelpad=5)
    ax.spines[['top','right','left']].set_visible(False);ax.spines['bottom'].set_color(LINE)
    fig.legend(handles=[Line2D([],[],marker='o',color=BLUE,lw=.9,ms=4,label='Agent'),
        Line2D([],[],marker='s',color=VIOLET,lw=.9,ms=4,label='Published law'),
        Line2D([],[],color=SLATE,ls=(0,(3,2)),lw=.9,label='Source coefficient')],
        loc='lower center',bbox_to_anchor=(.67,.018),ncol=3,frameon=False,
        fontsize=7,handlelength=1.3,columnspacing=1.1)
    assert len(all_rows)==12 and len(refs)==2
    return {'native_rows':all_rows,'source_coefficients':refs,
        'structure':{'subjects_per_table':11509,'visits_per_subject':4,'years':[0,2,4,6],
                     'records_per_table':46036,'meaning':'Illustration of existing schedule, not measurements or trajectories'},
        'dimensions_inches':[7,3.7]},save(fig,out,'fig4-longitudinal-use')


def scientific(binding,out):
    data=binding['figure5'];fig=plt.figure(figsize=(7,4.15),facecolor='white')
    fig.text(.035,.956,'(a)  Scientific analysis profiles',fontsize=9,weight='bold')
    fig.text(.747,.956,'(b)  Missing dependence',fontsize=8.6,weight='bold')
    # These aligned panels form one dashboard. The reference-interval units
    # below are coordinates only, not acceptance thresholds or test statistics.
    forest=fig.add_axes([.305,.17,.385,.70])
    labels=fig.add_axes([.035,.17,.26,.70],sharey=forest);labels.axis('off')
    forest.set_xlim(-6.2,4.2);forest.set_ylim(0,8.9)
    for low,high,color in [(4.1,8.8,LIGHT_BLUE),(.1,3.65,LAVENDER)]:
        forest.axhspan(low,high,color=color,alpha=.55,zorder=-2)
        labels.axhspan(low,high,color=color,alpha=.55,zorder=-2)
    forest.axvline(0,color=SLATE,lw=1,ls=(0,(3,2)),zorder=1)
    forest.set_yticks([]);forest.set_xticks([-6,-4,-2,0,2,4]);forest.xaxis.set_major_formatter(FuncFormatter(num))
    forest.spines[['top','right','left']].set_visible(False);forest.spines['bottom'].set_color(LINE)
    forest.set_xlabel('Difference from reference / reference interval half-width',fontsize=6.7,labelpad=6)
    labels.set_xlim(0,1)
    labels.text(.02,8.46,'PRIMARY',fontsize=8,weight='bold',color=BLUE,va='center')
    labels.text(.02,8.13,'BMI + glucose + age + female',fontsize=6.4,color=SLATE,va='center')
    labels.text(.02,3.38,'SECONDARY',fontsize=8,weight='bold',color=VIOLET,va='center')
    labels.text(.02,3.04,'BMI + age + female',fontsize=6.6,color=SLATE,va='center')
    term_names={'bmi':'BMI','glucose':'Glucose','age':'Age','female':'Female - male'}
    unit_labels={'bmi':'pp/(kg/m²)','glucose':'pp/(mmol/L)','age':'pp/year','female':'pp'}
    coordinates=[]
    ypos=[7.42,6.45,5.48,4.51,2.38,1.42,.46]
    for item,y in zip(data['coefficients'],ypos):
        ref=item['reference'];scale=(ref['upper']-ref['lower'])/2
        assert scale>0
        lo=(ref['lower']-ref['value'])/scale;hi=(ref['upper']-ref['value'])/scale
        forest.add_patch(Rectangle((lo,y-.33),hi-lo,.66,facecolor='#DCE2ED',edgecolor='none',zorder=0))
        labels.text(.02,y+.12,term_names[item['term']],fontsize=7.8,weight='bold',va='center')
        labels.text(.02,y-.19,f"ref {ref['value']:+.4f} {unit_labels[item['term']]}",fontsize=6.45,color=SLATE,va='center')
        transformed=[]
        for offset,c in zip([.20,0,-.20],item['generated']):
            v=(c['value']-ref['value'])/scale
            l=(c['lower']-ref['value'])/scale;u=(c['upper']-ref['value'])/scale
            forest.errorbar(v,y+offset,xerr=[[v-l],[u-v]],fmt='o',ms=3.35,
                           color=BLUE,alpha=1,capsize=1.8,lw=.85,zorder=3)
            transformed.append({'seed':c['seed'],'native':dict(c),'display_value':v,'display_lower':l,'display_upper':u})
        coordinates.append({'analysis':item['reference_analysis_key'],'term':item['term'],
            'native_reference':dict(ref),'display_center':ref['value'],'display_scale':scale,
            'reference_display_lower':lo,'reference_display_upper':hi,'generated':transformed})
    # One right-hand analysis card, without a causal graph or invented response curve.
    fig.add_artist(Rectangle((.735,.17),.245,.70,transform=fig.transFigure,
                            facecolor=PEACH,edgecolor='none',zorder=-1))
    fig.text(.752,.824,'BMI-glucose ρ',fontsize=9,weight='bold',color=CORAL)
    fig.text(.752,.781,'Unreported model dependence',fontsize=6.8,color=SLATE)
    fig.text(.752,.735,'Primary BMI effect',fontsize=7.8,weight='bold')
    sens=fig.add_axes([.784,.405,.165,.255])
    pts=[]
    for point in data['sensitivity']:
        rho=point['latent_bmi_glucose_correlation'];value=point['primary_bmi_coefficient']
        sens.plot(rho,value,'D',color=CORAL,ms=5.7)
        sens.annotate(f'{value:+.4f}'.replace('-','−'),(rho,value),
            xytext=(0,7 if value>0 else -14),textcoords='offset points',ha='center',fontsize=7,color=CORAL,weight='bold')
        pts.append(dict(point))
    sens.axhline(0,color=SLATE,lw=.6);sens.set_xlim(.01,.49);sens.set_ylim(-.032,.055)
    sens.set_xticks([.1,.4],['0.10','0.40']);sens.set_yticks([-.02,0,.04]);sens.yaxis.set_major_formatter(FuncFormatter(num))
    sens.set_xlabel('Assumed ρ',fontsize=7,labelpad=3)
    sens.set_title('HbA1c pp/(kg/m²)',fontsize=6.7,loc='left',pad=5)
    sens.spines[['top','right','left']].set_visible(False);sens.spines['bottom'].set_color(LINE)
    sens.tick_params(axis='y',length=0,pad=3,labelsize=6.5)
    fig.text(.752,.305,'Secondary BMI unchanged',fontsize=7,weight='bold')
    fig.text(.752,.251,'Same marginals; two scenarios.',fontsize=6.7,color=SLATE)
    fig.text(.752,.210,'No new draws or fitted curve.',fontsize=6.7,color=SLATE)
    fig.legend(handles=[Line2D([],[],marker='o',color=BLUE,lw=.8,ms=3.5,label='3 fixed seeds / conditional 95% intervals'),
        Rectangle((0,0),1,1,facecolor='#DCE2ED',label='Reference 95% interval')],
        loc='lower left',bbox_to_anchor=(.025,.025),frameon=False,ncol=2,fontsize=6.8,
        handlelength=1.5,columnspacing=1.7)
    assert len(coordinates)==7 and sum(len(x['generated']) for x in coordinates)==21
    assert len(pts)==2
    return {'coordinates':coordinates,'sensitivity_points':pts,
        'transformation':'z=(estimate-reference_value)/((reference_upper-reference_lower)/2)',
        'reference_limits':'Each bound separately transformed; asymmetry is retained.',
        'interpretation':'Display coordinate only, not a test statistic, equivalence criterion or acceptance threshold.',
        'delivered_model_latent_correlation':data['delivered_model_latent_correlation'],
        'dimensions_inches':[7,4.15]},save(fig,out,'fig5-analysis-use')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=HERE)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    assert sha(P/INPUT)==INPUT_SHA
    root='work' if (P/'work').is_dir() else 'reports'
    hrs_path=f'{root}/hrs_public_example_2026-11-03/RESULTS.md'
    assert sha(P/hrs_path)==HRS_SHA
    text=(P/hrs_path).read_text(encoding='utf-8')
    assert '11,509 synthetic subjects and four visits at 0,2,4,6 years: 46,036 rows' in text
    source=json.loads((P/INPUT).read_text(encoding='utf-8'))
    rc();data4,files4=longitudinal(source,out);data5,files5=scientific(source,out)
    report={'schema':'visual_redesign_v11_scientific_use_bindings','status':'PASS',
        'input_sha256':{INPUT:INPUT_SHA,hrs_path:HRS_SHA},'script_sha256':sha(Path(__file__)),
        'figure4':data4,'figure5':data5,'outputs':{**files4,**files5},
        'palette':{'navy':NAVY,'generated':BLUE,'published_law':VIOLET,'analytical_scenario':CORAL,'reference':SLATE},
        'individual_records_read':False,'generator_executed':False,'scientific_model_refit':False,
        'new_scientific_experiment':False,'only_new_calculation':'Invertible affine display coordinates; original native estimates and intervals retained.'}
    (out/'NUMERIC_BINDINGS_45.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','hrs_estimates':12,'hrs_source_coefficients':2,'scientific_estimates':21,'reference_effects':7,'analytic_points':2,'output':str(out)}))


if __name__=='__main__':main()
