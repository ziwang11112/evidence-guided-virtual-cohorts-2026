"""White-background, native-unit paper figures from frozen v10 aggregates.

This only redraws existing estimates/intervals. It reads no individual rows,
runs no generator or clinical fit, and invents no curve or experiment.
"""
from pathlib import Path
import argparse
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MaxNLocator

HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
SOURCE='manuscript/conference_figures_v10_2026-11-04/FIG45_NUMERIC_BINDINGS.json'
SOURCE_SHA='fca43b243ff0d3ec9c452e409aa09681106674a441edf0d5b4261fd7cc7ccca6'
NAVY='#182647'; BLUE='#4169B1'; VIOLET='#8264B5'; CORAL='#D97762'; SLATE='#778394'
PALE='#E4E7ED'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def fmt(x,pos=None): return '0' if abs(x)<1e-12 else f'{x:.3g}'.replace('-', '−')


def configure():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7.4,
        'axes.labelsize':7,'axes.titlesize':7.8,'xtick.labelsize':6.8,'ytick.labelsize':6.8,
        'text.color':NAVY,'axes.labelcolor':NAVY,'axes.linewidth':.6,
        'svg.fonttype':'none','pdf.fonttype':42,'svg.hashsalt':'v12-native-use-2026-11-04'})


def style(ax):
    ax.spines[['top','right','left']].set_visible(False)
    ax.spines['bottom'].set_color('#A7ADB7')
    ax.tick_params(axis='y',length=0)
    ax.xaxis.set_major_formatter(FuncFormatter(fmt))
    ax.xaxis.set_major_locator(MaxNLocator(nbins=3,steps=[1,2,2.5,5,10]))


def save(fig,out,name):
    outputs={}
    for ext in ('.svg','.png','.pdf'):
        path=out/(name+ext)
        metadata={'Date':None} if ext=='.svg' else ({'CreationDate':None,'ModDate':None} if ext=='.pdf' else {})
        fig.savefig(path,dpi=300,metadata=metadata)
        outputs[path.name]={'sha256':sha(path),'bytes':path.stat().st_size}
    plt.close(fig)
    return outputs


def longitudinal(binding,out):
    fig,axes=plt.subplots(1,2,figsize=(7,2.15),sharey=True)
    fig.subplots_adjust(left=.085,right=.985,top=.84,bottom=.31,wspace=.20)
    rows=[];sources=[]
    for i,(ax,panel) in enumerate(zip(axes,binding['figure4']['panels'])):
        ax.axvline(0,color='#C1C6CE',lw=.65,zorder=0)
        ax.axvline(panel['source_coefficient'],color=SLATE,lw=1,ls=(0,(3,2)),zorder=1)
        for arm,color,marker,offset in [('agent',BLUE,'o',-.16),('native',VIOLET,'s',.16)]:
            for row,seed in enumerate((6101,6102,6103)):
                c=next(c for c in panel['coefficient_rows'] if c['arm']==arm and c['seed']==seed)
                ax.errorbar(c['estimate'],row+offset,
                    xerr=[[c['estimate']-c['wald_lower']],[c['wald_upper']-c['estimate']]],
                    fmt=marker,ms=3.8,capsize=2,lw=.95,color=color,zorder=3)
                rows.append(dict(c))
        ax.set_ylim(2.6,-.6);ax.set_xlim(-.082,.082)
        ax.set_yticks([0,1,2],['6101','6102','6103'])
        ax.set_xticks([-.08,-.04,0,.04,.08]);ax.xaxis.set_major_formatter(FuncFormatter(fmt))
        ax.set_title(f"({chr(97+i)}) HbA1c spline {'< 6.5%' if i==0 else '≥ 6.5%'}",loc='left',pad=5)
        ax.set_xlabel('Longitudinal interaction coefficient',labelpad=3)
        ax.spines[['top','right','left']].set_visible(False);ax.spines['bottom'].set_color('#A7ADB7')
        ax.tick_params(axis='y',length=0)
        if i==0:ax.set_ylabel('Seed',labelpad=4)
        sources.append({'term':panel['term'],'source_coefficient':panel['source_coefficient'],
            'source_standard_error_not_plotted':panel['source_standard_error_recorded_not_plotted']})
    fig.legend(handles=[Line2D([],[],marker='o',color=BLUE,lw=.9,ms=3.8,label='Agent'),
        Line2D([],[],marker='s',color=VIOLET,lw=.9,ms=3.8,label='Published law'),
        Line2D([],[],color=SLATE,lw=1,ls=(0,(3,2)),label='Source coefficient')],
        loc='lower center',bbox_to_anchor=(.53,.015),ncol=3,frameon=False,fontsize=7,
        handlelength=1.8,columnspacing=1.9)
    assert len(rows)==12 and len(sources)==2
    return {'dimensions_inches':[7,2.15],'native_rows':rows,'source_coefficients':sources,
        'interval_type':'Stored generated-data mixed-model 95% Wald intervals; source coefficient line only.'},save(fig,out,'fig4-longitudinal-use')


def scientific(binding,out):
    data=binding['figure5'];fig=plt.figure(figsize=(7,4.05),facecolor='white')
    fig.legend(handles=[Line2D([],[],marker='o',color=BLUE,lw=.9,ms=3.5,label='Generated / conditional 95% CI'),
        Patch(facecolor=PALE,edgecolor=SLATE,label='Reference / 95% CI'),
        Line2D([],[],marker='D',color=CORAL,lw=0,ms=4,label='Analytical scenario')],
        loc='upper center',bbox_to_anchor=(.515,1.005),ncol=3,frameon=False,fontsize=6.8,
        handlelength=1.4,columnspacing=1.1)
    fig.text(.075,.904,'Primary: HbA1c ~ BMI + glucose + age + female',fontsize=8)
    fig.text(.075,.449,'Secondary: HbA1c ~ BMI + age + female',fontsize=8)
    labels={'bmi':('BMI','pp per kg/m²'),'glucose':('Glucose','pp per mmol/L'),
            'age':('Age','pp per year'),'female':('Female - male','pp difference')}
    # Identical native-axis limits for the same predictor across both analyses.
    limits={}
    for term in labels:
        values=[0]
        for item in data['coefficients']:
            if item['term']==term:
                values += [item['reference'][k] for k in ('lower','upper')]
                values += [x[k] for x in item['generated'] for k in ('lower','upper')]
        low,high=min(values),max(values);pad=(high-low)*.08
        limits[term]=[low-pad,high+pad]
    panels=[]
    for index,item in enumerate(data['coefficients']):
        row=0 if index<4 else 1;col=index if row==0 else index-4
        ax=fig.add_axes([.09+col*.23,.605-row*.455,.172,.225])
        ref=item['reference']
        ax.axvspan(ref['lower'],ref['upper'],color=PALE,zorder=0)
        ax.axvline(ref['value'],color=SLATE,lw=1,ls=(0,(3,2)),zorder=1)
        ax.axvline(0,color='#B9BFC8',lw=.6,zorder=0)
        for y,c in enumerate(item['generated']):
            assert c['lower']<=c['value']<=c['upper']
            ax.errorbar(c['value'],y,xerr=[[c['value']-c['lower']],[c['upper']-c['value']]],
                fmt='o',ms=3.6,lw=.95,capsize=2,color=BLUE,zorder=3)
        ax.set_yticks(range(3),[str(c['seed']) if col==0 else '' for c in item['generated']])
        if col==0:ax.set_ylabel('Seed',labelpad=3)
        ax.set_ylim(2.55,-.55);ax.set_xlim(limits[item['term']])
        ax.set_title(f"({chr(97+index)}) {labels[item['term']][0]}",loc='left',pad=5)
        ax.set_xlabel(labels[item['term']][1],labelpad=3);style(ax)
        panels.append({'panel':chr(97+index),**item,'xlim_native':limits[item['term']]})
    ax=fig.add_axes([.792,.15,.165,.225])
    for c in data['sensitivity']:
        rho=c['latent_bmi_glucose_correlation'];value=c['primary_bmi_coefficient']
        ax.plot(rho,value,marker='D',color=CORAL,ms=5,ls='none')
        ax.annotate(f'{value:+.4f}'.replace('-','−'),(rho,value),
            xytext=(0,7 if value>0 else -14),textcoords='offset points',ha='center',fontsize=6.6,color=CORAL)
    ax.axhline(0,color='#B9BFC8',lw=.6);ax.set_xlim(.02,.48);ax.set_ylim(-.031,.055)
    ax.set_xticks([.1,.4],['0.10','0.40']);ax.set_yticks([-.02,0,.02,.04])
    ax.yaxis.set_major_formatter(FuncFormatter(fmt))
    ax.set_title('(h) Primary BMI\n(pp per kg/m²)',loc='left',pad=5,fontsize=7.1)
    ax.set_xlabel('BMI-glucose ρ',labelpad=3)
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['left','bottom']].set_color('#A7ADB7');ax.tick_params(axis='y',labelsize=6.6)
    assert len(panels)==7 and sum(len(x['generated']) for x in panels)==21
    return {'dimensions_inches':[7,4.05],'coefficient_panels':panels,
        'sensitivity_points':data['sensitivity'],'delivered_model_latent_correlation':data['delivered_model_latent_correlation'],
        'display_scale':'All effects and bounds use native units; same-predictor primary/secondary panels share x limits.',
        'reference_n':data['reference_n'],'reference_clusters':data['reference_clusters']},save(fig,out,'fig5-analysis-use')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=HERE)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    assert sha(P/SOURCE)==SOURCE_SHA
    data=json.loads((P/SOURCE).read_text(encoding='utf-8'))
    configure();a,ao=longitudinal(data,out);b,bo=scientific(data,out)
    report={'schema':'paper_figures_v12_use_cases','status':'PASS','input_sha256':{SOURCE:SOURCE_SHA},
        'script_sha256':sha(Path(__file__)),'figure4':a,'figure5':b,'outputs':{**ao,**bo},
        'individual_records_read':False,'generator_executed':False,'clinical_model_refit':False,
        'new_scientific_experiment':False,'display_transform':'None; native effects and stored interval bounds.',
        'palette':{'navy':NAVY,'generated':BLUE,'published_law':VIOLET,'analytical_scenario':CORAL,'reference':SLATE}}
    (out/'NUMERIC_BINDINGS_45.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','figure4_estimates':12,'figure5_estimates':21,'analytic_points':2}))


if __name__=='__main__':main()
