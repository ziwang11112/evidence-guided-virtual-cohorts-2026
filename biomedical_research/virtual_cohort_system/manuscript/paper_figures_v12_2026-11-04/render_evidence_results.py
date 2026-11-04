"""Native-unit result figures from previously frozen, aggregate-only results.

No patient records, generator execution, clinical fitting or network access.
--output writes a separate reproduction directory.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator, FuncFormatter

HERE = Path(__file__).resolve().parent
P = HERE.parents[1]
C = {'E0':'#8264B5','E1':'#4169B1','L':'#8264B5','R':'#4169B1',
     'statistical':'#778394','reference':'#778394','band':'#E9ECF1','ink':'#182647'}
UTILITY='manuscript/utility_package_2026-11-03/AGGREGATE_SOURCE.json'
PINS={
 'local':{UTILITY:'3459ac8bc63a3de39aab1d23ee1e29c5c6369e52e2adbd90f2bdf6376215bef7',
 'work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json':'1fbc32d2f982d31c649d9217e644a34c02b81e08c093380fba8f3aaec9e4c2cb',
 'work/information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json':'d64b7cd5bd1097a4ea51b84b00a3721d54c092cc87db85da9418bdd24bd187a0'},
 'public':{UTILITY:'3459ac8bc63a3de39aab1d23ee1e29c5c6369e52e2adbd90f2bdf6376215bef7',
 'reports/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json':'1fbc32d2f982d31c649d9217e644a34c02b81e08c093380fba8f3aaec9e4c2cb',
 'reports/information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json':'6f55901630fc0a0e5071b8e878d53230255c8c68b8d42f302a7f2cf842a36a9f'}}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def at(d,p):
    for k in p.strip('/').split('/'):
        k=k.replace('~1','/').replace('~0','~')
        d=d[int(k)] if isinstance(d,list) else d[k]
    return d

def audit(u,m,h):
    result={}
    for key,doc,seeds,expected in [('main_experiment',m,[5101,5102,5103],(6,72,216)),
                                  ('historical_information_experiment',h,[4101,4102,4103],(5,30,90))]:
        ns=nm=0
        for p in u[key]['panels']:
            r=at(doc,p['reference_pointer'])
            assert p['reference']==r if key=='main_experiment' else p['reference']['value']==r
            if key!='main_experiment':
                assert p['reference']['interval']==(at(doc,p['interval_pointer']) if 'interval_pointer' in p else None)
            for s in p['series']:
                assert [z['seed'] for z in s['seeds']]==seeds
                vals=[z['value'] for z in s['seeds']]
                assert all(z['value']==at(doc,z['pointer']) for z in s['seeds'])
                assert abs(s['mean']-statistics.mean(vals))<1e-14
                assert s['range']==[min(vals),max(vals)]
                ss=at(doc,s['summary_pointer'])
                assert s['mean']==ss['mean_effect' if key=='main_experiment' else 'mean']
                ns+=3;nm+=1
        assert (len(u[key]['panels']),nm,ns)==expected
        result[key]={'endpoints':expected[0],'constructor_means':nm,'seed_statistics':ns}
    assert m['planned_constructions']==24 and m['unique_successful_table_contents']==72
    assert h['independent_constructors']==6 and h['attempts']==42 and h['distinct_table_hashes']==24
    return result

def configure():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7.6,'text.color':C['ink'],
     'axes.labelcolor':C['ink'],'axes.titlesize':8.2,'axes.labelsize':7.2,
     'xtick.labelsize':6.9,'ytick.labelsize':7.0,'axes.linewidth':.6,
     'svg.fonttype':'none','pdf.fonttype':42,'svg.hashsalt':'evc-paper-v12-fig23'})

def fmt(x,p):return '0' if abs(x)<1e-10 else f'{x:.3g}'

def axis_style(ax,p,include_zero):
    ax.set_facecolor('white')
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['left','bottom']].set_color('#929AA7')
    ax.tick_params(length=2.5,width=.55,pad=2.5)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
    ax.yaxis.set_major_formatter(FuncFormatter(fmt))
    r=p['reference'];iv=r.get('interval')
    if iv and iv.get('status')=='available':
        ax.axhspan(iv['lower'],iv['upper'],color=C['band'],zorder=0)
    ax.axhline(r['value'],color=C['reference'],lw=.9,ls=(0,(3,2)),zorder=1)
    vals=[z['value'] for s in p['series'] for z in s['seeds']]+[r['value']]
    if iv and iv.get('status')=='available':vals += [iv['lower'],iv['upper']]
    lo,hi=min(vals),max(vals)
    if include_zero:lo=min(lo,0);hi=max(hi,0)
    span=max(hi-lo,abs(hi)*.05,1e-4)
    ax.set_ylim(lo-.08*span,hi+.12*span)
    if lo<=0<=hi:ax.axhline(0,color='#C7CCD4',lw=.6,zorder=1)

def dots(ax,s,x,color,offset=.029):
    ax.plot([x,x],s['range'],color=color,lw=.65,alpha=.6,zorder=2)
    ax.scatter([x-offset,x,x+offset],[q['value'] for q in s['seeds']],s=8.5,
               color=color,alpha=.9,edgecolors='white',linewidths=.25,zorder=3)
    ax.scatter(x,s['mean'],s=18,marker='D',facecolor='white',edgecolor=color,linewidths=.85,zorder=4)

def ref_legend():
    return [Line2D([],[],ls='',marker='o',ms=3,color=C['statistical'],label='Seed'),
      Line2D([],[],ls='',marker='D',ms=4,mfc='white',mec=C['statistical'],label='Constructor mean'),
      Line2D([],[],ls=(0,(3,2)),lw=.9,color=C['reference'],label='Reference estimate'),
      Patch(facecolor=C['band'],edgecolor='none',label='Reference interval / band')]

def render_main(u):
    fig,axes=plt.subplots(2,3,figsize=(7,4.65))
    fig.subplots_adjust(left=.083,right=.99,bottom=.135,top=.91,hspace=.71,wspace=.48)
    for i,(ax,p) in enumerate(zip(axes.flat,u['main_experiment']['panels'])):
        axis_style(ax,p,True)
        case='CHNS' if p['case']=='CHNS2009' else 'ENSANUT'
        ax.set_title(f'({chr(97+i)}) {case}: {p["predictor"]}',loc='left',pad=15,fontweight='normal')
        ax.text(0,1.022,'Adjusted: '+p['adjustment'].lower().replace('bmi','BMI'),
                transform=ax.transAxes,fontsize=6.6,color='#586174')
        ax.set_ylabel('HbA1c pp '+p['display_unit'],labelpad=3)
        groups=[('agent','E0'),('agent','E1'),('statistical','E0'),('statistical','E1')]
        centers=[0,1.15,2.2,2.95]
        for (kind,condition),center in zip(groups,centers):
            ss=[s for s in p['series'] if s['kind']==kind and s['condition']==condition]
            assert len(ss)==(5 if kind=='agent' else 1)
            offsets=[-.32,-.16,0,.16,.32] if kind=='agent' else [0]
            for s,dx in zip(ss,offsets):dots(ax,s,center+dx,C[condition] if kind=='agent' else C['statistical'])
        ax.set_xlim(-.53,3.25)
        ax.set_xticks(centers,['Agent\nE0','Agent\nE1','Stat.\nE0','Stat.\nE1'])
        for label,color in zip(ax.get_xticklabels(),[C['E0'],C['E1'],C['statistical'],C['statistical']]):label.set_color(color)
    fig.legend(handles=ref_legend(),loc='lower center',bbox_to_anchor=(.53,.008),ncol=4,
               fontsize=6.9,frameon=False,handlelength=1.6,columnspacing=1.25)
    return fig

def render_summary(u):
    # Three regression panels above, two centered correlation panels below.
    fig=plt.figure(figsize=(7,4.6))
    gs=fig.add_gridspec(2,6,left=.083,right=.99,bottom=.135,top=.91,hspace=.71,wspace=1.0)
    axes=[fig.add_subplot(gs[0,j:j+2]) for j in [0,2,4]]
    axes += [fig.add_subplot(gs[1,1:3]),fig.add_subplot(gs[1,3:5])]
    for i,(ax,p) in enumerate(zip(axes,u['historical_information_experiment']['panels'])):
        axis_style(ax,p,i<3)
        name=p['predictor'] if i<3 else 'Pearson correlation' if i==3 else 'Spearman correlation'
        subtitle='Adjusted: '+p['adjustment'].lower().replace('bmi','BMI') if i<3 else 'Glucose-HbA1c'
        ax.set_title(f'({chr(97+i)}) {name}',loc='left',pad=15,fontweight='normal')
        ax.text(0,1.022,subtitle,transform=ax.transAxes,fontsize=6.6,color='#586174')
        ylabel=p['axis_label'].replace('HbA1c percentage points\nper ','HbA1c pp per ') if i<3 else 'Correlation coefficient'
        ax.set_ylabel(ylabel,labelpad=3)
        positions=[0,1,2,4,5,6]
        for s,x in zip(p['series'],positions,strict=True):dots(ax,s,x,C[s['condition']],offset=.13)
        ax.set_xlim(-.6,6.6);ax.set_xticks(positions,[s['constructor'] for s in p['series']])
        ax.tick_params(axis='x',labelsize=6.2)
        for label,s in zip(ax.get_xticklabels(),p['series']):label.set_color(C[s['condition']])
    legends=[Line2D([],[],ls='',marker='o',ms=3,color=C['L'],label='L seed'),
      Line2D([],[],ls='',marker='o',ms=3,color=C['R'],label='R seed'),*ref_legend()[1:]]
    fig.legend(handles=legends,loc='lower center',bbox_to_anchor=(.52,.009),ncol=5,
               fontsize=6.8,frameon=False,handlelength=1.35,columnspacing=1.1)
    return fig

def save(fig,out,name):
    date=datetime(2026,11,4,tzinfo=timezone.utc);outputs={}
    for ext in ['svg','png','pdf']:
        p=out/f'{name}.{ext}'
        meta={'Date':None} if ext=='svg' else {'CreationDate':date,'ModDate':date} if ext=='pdf' else {}
        fig.savefig(p,dpi=300,metadata=meta);outputs[p.name]={'sha256':sha(p),'bytes':p.stat().st_size}
    plt.close(fig);return outputs

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=HERE);args=parser.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    profile='local' if (P/'work').is_dir() else 'public';root='work' if profile=='local' else 'reports'
    for p,h in PINS[profile].items():assert sha(P/p)==h,('input hash mismatch',p)
    u=read(P/UTILITY);m=read(P/root/'main_study_freeze_2026-11-03/final_evaluation/RESULTS.json');h=read(P/root/'information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json')
    counts=audit(u,m,h);configure();outputs=save(render_main(u),out,'fig2-evidence-results')
    outputs.update(save(render_summary(u),out,'fig3-summary-results'))
    contrasts=[]
    for c in m['agent_information_contrasts']:
        e0=c['arms']['E0']['mean_constructor_mean_absolute_discrepancy'];e1=c['arms']['E1']['mean_constructor_mean_absolute_discrepancy']
        contrasts.append({'case':c['case_id'],'endpoint':c['endpoint'],'unit':c['unit'],'E0_MAE':e0,'E1_MAE':e1,
           'difference':e1-e0,'percent_change':100*(e1-e0)/e0})
    binding={'status':'PASS','scope':'Native-unit presentation-only redraw. No empirical experiment or normalization added to graphics.',
      'profile':profile,'input_sha256':PINS[profile],'script_sha256':sha(Path(__file__)),
      'verified_value_counts':counts,'figure2':u['main_experiment'],'figure3':u['historical_information_experiment'],
      'six_information_contrasts_for_caption_and_reading_guide_not_additional_plot':contrasts,
      'style':{'width_inches':7,'heights_inches':[4.65,4.6],'colors':C,'background':'white',
        'mean':'Open diamond','seed':'Three small dots with visibility-only horizontal offsets',
        'range':'Thin within-constructor three-seed min/max line, not confidence interval',
        'reference':'Dashed line; original native-unit estimate',
        'bands':'CHNS CR1-t intervals, ENSANUT cluster-resampling stability bands; historical correlations have no interval.',
        'normalization':'None. Each vertical axis retains its native units and own range.',
        'selection':'All six main endpoints and five summary endpoints; all constructors and scheduled final seeds.',
        'authors':'Ordinal order; not paired across E0/E1 or L/R.'},
      'output_sha256':outputs,'individual_rows_read':False,'generator_executed':False,'clinical_analysis_rerun':False}
    (out/'NUMERIC_BINDINGS_23.json').write_text(json.dumps(binding,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','counts':counts,'outputs':list(outputs)}))

if __name__=='__main__':main()
