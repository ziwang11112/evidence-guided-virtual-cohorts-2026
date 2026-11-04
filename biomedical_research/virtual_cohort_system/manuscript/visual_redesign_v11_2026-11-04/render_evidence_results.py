"""Integrated publication graphics from frozen aggregates only.

No generators, patient data, clinical fitting, new inference or network access.
Run with --output to reproduce the two figures in another directory.
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
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter, MaxNLocator
import numpy as np

HERE = Path(__file__).resolve().parent
P = HERE.parents[1]
C = dict(navy='#182647', blue='#4169B1', violet='#8264B5', coral='#D97762',
         slate='#778394', ink='#27314A', line='#DCE1E9', bluewash='#EEF3FA',
         lavender='#F3EFF8', peach='#FCF0EB', paper='#FFFFFF', ref='#E4E8EE')
UTILITY = 'manuscript/utility_package_2026-11-03/AGGREGATE_SOURCE.json'
PINS = {
 'local': {UTILITY:'3459ac8bc63a3de39aab1d23ee1e29c5c6369e52e2adbd90f2bdf6376215bef7',
  'work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json':'1fbc32d2f982d31c649d9217e644a34c02b81e08c093380fba8f3aaec9e4c2cb',
  'work/information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json':'d64b7cd5bd1097a4ea51b84b00a3721d54c092cc87db85da9418bdd24bd187a0'},
 'public': {UTILITY:'3459ac8bc63a3de39aab1d23ee1e29c5c6369e52e2adbd90f2bdf6376215bef7',
  'reports/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json':'1fbc32d2f982d31c649d9217e644a34c02b81e08c093380fba8f3aaec9e4c2cb',
  'reports/information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json':'6f55901630fc0a0e5071b8e878d53230255c8c68b8d42f302a7f2cf842a36a9f'}
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def at(d,p):
    for k in p.strip('/').split('/'):
        k=k.replace('~1','/').replace('~0','~')
        d=d[int(k)] if isinstance(d,list) else d[k]
    return d

def audit(u,m,h):
    count={}
    for key,doc,seeds,expected in [('main_experiment',m,[5101,5102,5103],(6,72,216)),
                                  ('historical_information_experiment',h,[4101,4102,4103],(5,30,90))]:
        ns=nm=0
        for panel in u[key]['panels']:
            original=at(doc,panel['reference_pointer'])
            assert (panel['reference']==original if key=='main_experiment' else panel['reference']['value']==original)
            if key!='main_experiment':
                assert panel['reference']['interval']==(at(doc,panel['interval_pointer']) if 'interval_pointer' in panel else None)
            for s in panel['series']:
                assert [z['seed'] for z in s['seeds']]==seeds
                values=[z['value'] for z in s['seeds']]
                assert all(z['value']==at(doc,z['pointer']) for z in s['seeds'])
                assert abs(s['mean']-statistics.mean(values))<1e-14
                assert s['range']==[min(values),max(values)]
                summary=at(doc,s['summary_pointer'])
                assert s['mean']==summary['mean_effect' if key=='main_experiment' else 'mean']
                ns+=3;nm+=1
        assert (len(u[key]['panels']),nm,ns)==expected
        count[key]={'panels':expected[0],'constructor_means':nm,'seed_statistics':ns}
    assert m['planned_constructions']==24 and m['unique_successful_table_contents']==72
    assert h['independent_constructors']==6 and h['attempts']==42 and h['distinct_table_hashes']==24
    return count

def setup():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7.4,'text.color':C['ink'],
      'axes.labelcolor':C['ink'],'xtick.color':C['ink'],'ytick.color':C['ink'],
      'svg.fonttype':'none','pdf.fonttype':42,'svg.hashsalt':'evc-v11-evidence-results',
      'axes.linewidth':.6,'axes.labelsize':7.1,'xtick.labelsize':6.5,'ytick.labelsize':6.5})

def text(fig,x,y,s,size=8,color=None,weight='normal',**kw):
    return fig.text(x,y,s,fontsize=size,color=color or C['ink'],weight=weight,**kw)

def rect(fig,x,y,w,h,color,**kw):
    r=Rectangle((x,y),w,h,transform=fig.transFigure,facecolor=color,edgecolor='none',**kw)
    fig.add_artist(r);return r

def axis_fmt(x,pos):
    return '0' if abs(x)<1e-11 else f'{x:.3g}'

def effect_strip(ax,panel,first=False):
    ref=panel['reference'];iv=ref.get('interval')
    if iv and iv.get('status')=='available':ax.axvspan(iv['lower'],iv['upper'],color=C['ref'],alpha=.9,zorder=0)
    ax.axvline(ref['value'],color=C['slate'],lw=.85,ls=(0,(3,2)),zorder=1)
    ax.axvline(0,color=C['line'],lw=.6,zorder=0)
    groups=[('agent','E0',3),('agent','E1',2),('statistical','E0',.8),('statistical','E1',.2)]
    for kind,cond,y0 in groups:
        series=[s for s in panel['series'] if s['kind']==kind and s['condition']==cond]
        assert len(series)==(5 if kind=='agent' else 1)
        ys=np.linspace(.29,-.29,5) if kind=='agent' else [0]
        color=C['slate'] if kind=='statistical' else C['violet'] if cond=='E0' else C['blue']
        for s,dy in zip(series,ys):
            y=y0+dy
            ax.plot(s['range'],[y,y],lw=.7,color=color,alpha=.65,zorder=3)
            ax.scatter([q['value'] for q in s['seeds']],[y+.034,y,y-.034],s=6.5,color=color,
                       alpha=.85,lw=.2,edgecolors='white',zorder=4)
            ax.scatter(s['mean'],y,s=13,marker='D',facecolor='white',edgecolor=color,lw=.7,zorder=5)
    values=[z['value'] for s in panel['series'] for z in s['seeds']]+[0,ref['value']]
    if iv and iv.get('status')=='available':values += [iv['lower'],iv['upper']]
    a,b=min(values),max(values);span=max(b-a,1e-3)
    ax.set_xlim(a-.10*span,b+.12*span);ax.set_ylim(-.2,3.5)
    ax.set_yticks([3,2,.8,.2],['Agent E0','Agent E1','Stat. E0','Stat. E1'] if first else ['']*4)
    ax.tick_params(axis='y',length=0,pad=4)
    ax.tick_params(axis='x',length=2.5,width=.55,pad=3)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=3));ax.xaxis.set_major_formatter(FuncFormatter(axis_fmt))
    ax.spines[['left','top','right']].set_visible(False);ax.spines['bottom'].set_color(C['line'])
    ax.axhline(1.35,color=C['line'],lw=.65,zorder=0)
    ax.set_xlabel('HbA1c pp '+panel['display_unit'],labelpad=4,fontsize=6.5)

def render_main(u,m):
    fig=plt.figure(figsize=(7,5.25),facecolor='white')
    text(fig,.025,.971,'EVIDENCE TO SCIENTIFIC ANALYSIS',8.2,C['navy'],'bold')
    text(fig,.975,.971,'24 constructions  /  72 tables',7.2,C['slate'],ha='right')
    text(fig,.025,.925,'E0  basic / marginal',7.2,C['violet'],'semibold')
    text(fig,.265,.925,'E1  + relational evidence',7.2,C['blue'],'semibold')
    fig.legend(handles=[Line2D([],[],ls='',marker='o',ms=2.5,color=C['slate'],label='3 seeds'),
      Line2D([],[],ls='',marker='D',ms=3.2,mfc='white',mec=C['slate'],label='Mean'),
      Line2D([],[],ls='--',lw=.8,color=C['slate'],label='Reference / band')],
      loc='upper right',bbox_to_anchor=(.985,.95),ncol=3,frameon=False,fontsize=6.5,handlelength=1.1,columnspacing=.85)
    changes=[]
    for cohort,(case,n,bottom,header) in enumerate([('CHNS2009',6631,.535,.865),('ENSANUT2018',6931,.105,.435)]):
        rect(fig,.025,bottom-.066,.95,.414,'#F9FAFC',zorder=-2)
        rect(fig,.025,header-.004,.95,.041,C['bluewash'] if cohort==0 else C['lavender'],zorder=-1)
        name='CHNS 2009' if cohort==0 else 'ENSANUT'
        text(fig,.04,header+.010,name,8.5,C['navy'],'bold')
        text(fig,.215,header+.010,f'n = {n:,} selected adults',6.7,C['slate'])
        text(fig,.745,header+.010,'Evidence change',7.5,C['navy'],'bold')
        panels=[p for p in u['main_experiment']['panels'] if p['case']==case]
        cc=[c for c in m['agent_information_contrasts'] if c['case_id']==case]
        assert len(panels)==len(cc)==3
        for j,p in enumerate(panels):
            x=.118+j*.197
            ax=fig.add_axes([x,bottom,.171,.245])
            effect_strip(ax,p,j==0)
            letter='abc'[j] if cohort==0 else 'efg'[j]
            text(fig,x,bottom+.286,f'({letter})  {p["predictor"]}',7.4,C['navy'],'bold')
            adjust=p['adjustment'].replace('Age','age').replace('Sex','sex')
            text(fig,x,bottom+.262,'Adj. '+adjust,6.1,C['slate'])
        ax=fig.add_axes([.765,bottom+.025,.18,.216])
        local=[]
        for j,c in enumerate(cc):
            e0=c['arms']['E0']['mean_constructor_mean_absolute_discrepancy'];e1=c['arms']['E1']['mean_constructor_mean_absolute_discrepancy']
            pct=100*(e1-e0)/e0
            assert abs((e1-e0)-c['E1_minus_E0_mean_absolute_discrepancy'])<1e-14
            color=C['blue'] if pct<0 else C['coral']
            y=2-j
            ax.barh(y,pct,height=.32,color=color,zorder=2)
            ax.text(pct+(-4 if pct<0 else 4),y,f'{pct:+.0f}%',ha='right' if pct<0 else 'left',va='center',fontsize=6.6,color=color,weight='bold')
            local.append({'case':case,'endpoint':c['endpoint'],'E0_MAE':e0,'E1_MAE':e1,'relative_MAE_change_percent':pct})
        ax.axvline(0,color=C['slate'],lw=.75);ax.set_xlim(-130,100);ax.set_ylim(-.55,2.55)
        short=['BMI','Glucose','Age'] if cohort==0 else ['Age','BMI','BMI + G']
        ax.set_yticks([2,1,0],short,fontsize=6.5);ax.tick_params(axis='y',length=0,pad=4)
        ax.set_xticks([-100,0],['-100%','0']);ax.tick_params(axis='x',length=2,pad=3,labelsize=6.2)
        ax.spines[['top','right','left']].set_visible(False);ax.spines['bottom'].set_color(C['line'])
        text(fig,.765,bottom+.262,'(d)' if cohort==0 else '(h)',6.8,C['navy'],'bold')
        ax.set_xlabel('Change in Agent MAE',fontsize=6.3,labelpad=4)
        changes.extend(local)
    text(fig,.025,.023,'Native-unit estimates at left; per-endpoint E1 vs E0 discrepancy change at right.',6.8,C['slate'])
    return fig,changes

def render_summary(u):
    panels=u['historical_information_experiment']['panels']
    fig=plt.figure(figsize=(7,4.65),facecolor='white')
    text(fig,.025,.968,'ONE JOINT TABLE, FIVE ANALYSES',8.4,C['navy'],'bold')
    text(fig,.975,.968,'6 constructions  /  18 distinct tables',7.2,C['slate'],ha='right')
    left=.218;cw=.1235;rowh=.12;top=.76
    rect(fig,left,.858,cw*3-.007,.06,C['lavender'])
    rect(fig,left+cw*3,.858,cw*3-.007,.06,C['bluewash'])
    text(fig,left+.014,.894,'L  External literature',8,C['violet'],'bold')
    text(fig,left+cw*3+.014,.894,'R  Literature + 30 summaries',8,C['blue'],'bold')
    text(fig,.025,.816,'ANALYSIS',6.8,C['slate'],'bold')
    for j in range(6):
        text(fig,left+j*cw+cw/2,.827,f'{"L" if j<3 else "R"}{j%3+1:02d}',7.2,C['violet'] if j<3 else C['blue'],'bold',ha='center')
    text(fig,.025,.789,'Supplied reference',6.3,C['slate'])
    cmap=LinearSegmentedColormap.from_list('discrepancy',['#F4F6FA','#F5E4DF','#E7AC9D'])
    norm=Normalize(0,100,clip=True)
    details=[]
    names=['BMI coefficient','Glucose coefficient','Age coefficient','Pearson correlation','Spearman correlation']
    units=['pp per kg/m²','pp per mmol/L','pp per year','Glucose-HbA1c','Glucose-HbA1c']
    for i,p in enumerate(panels):
        y=top-i*rowh;ref=p['reference']['value'];assert ref!=0
        text(fig,.025,y-.031,names[i],7.3,C['navy'],'bold')
        text(fig,.025,y-.059,f'{ref:.6f}',7.1,C['ink'])
        text(fig,.025,y-.083,units[i],6.2,C['slate'])
        data=[]
        for j,s in enumerate(p['series']):
            assert s['constructor']==('L' if j<3 else 'R')+f'{j%3+1:02d}'
            x=left+j*cw;z=100*(s['mean']-ref)/abs(ref)
            rect(fig,x,y-.104,cw-.007,.105,cmap(norm(abs(z))),zorder=-1)
            text(fig,x+(cw-.007)/2,y-.034,f'{s["mean"]:.6f}',7.3,C['ink'],'semibold',ha='center')
            ax=fig.add_axes([x+.012,y-.093,cw-.031,.035])
            color=C['violet'] if j<3 else C['blue']
            vals=[100*(r['value']-ref)/abs(ref) for r in s['seeds']]
            assert all(-100<=v<=100 for v in vals)
            ax.plot([-100,100],[0,0],lw=.55,color='#C5CAD3',zorder=0)
            ax.plot([0,0],[-.36,.36],lw=.75,color=C['slate'],zorder=1)
            ax.scatter(vals,[.24,0,-.24],s=7.5,color=color,edgecolors='white',lw=.25,zorder=3)
            ax.set_xlim(-105,105);ax.set_ylim(-.65,.65);ax.axis('off')
            data.append({'constructor':s['constructor'],'condition':s['condition'],'native_mean':s['mean'],
               'native_seed_values':s['seeds'],'signed_relative_mean_deviation_percent':z,
               'absolute_relative_mean_deviation_percent':abs(z),'signed_relative_seed_deviations_percent':vals})
        details.append({'endpoint':p['endpoint'],'predictor':p['predictor'],'reference':p['reference'],
                        'normalization':'100 * (estimate - reference) / abs(reference)','constructors':data})
    # A compact legend makes the small glyph tracks quantitatively interpretable.
    text(fig,.025,.109,'Cell number: native constructor mean',6.9,C['ink'],'semibold')
    text(fig,.025,.073,'Dots: all three final seed estimates',6.9,C['slate'])
    ax=fig.add_axes([.415,.074,.18,.038]);ax.plot([-100,100],[0,0],lw=.6,color='#C5CAD3')
    ax.plot([0,0],[-.25,.25],lw=.8,color=C['slate']);ax.scatter([-65,-20,40],[.13,0,-.13],s=10,color=C['blue'])
    ax.set_xlim(-105,105);ax.set_ylim(-.35,.35);ax.set_yticks([]);ax.set_xticks([-100,0,100],['-100%','0','+100%']);ax.tick_params(length=0,pad=2,labelsize=6.2)
    for sp in ax.spines.values():sp.set_visible(False)
    text(fig,.505,.125,'Seed deviation from reference',6.4,C['slate'],ha='center')
    cb=fig.add_axes([.71,.08,.24,.024]);plt.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cb,orientation='horizontal',ticks=[0,50,100])
    cb.tick_params(length=0,pad=2,labelsize=6.2);cb.set_xticklabels(['0','50','100%']);cb.spines[:].set_visible(False)
    text(fig,.83,.125,'Absolute mean deviation',6.4,C['slate'],ha='center')
    text(fig,.025,.018,'R explicitly receives the reference summaries; this is reconstruction of supplied information.',6.7,C['slate'])
    return fig,details

def save(fig,out,name):
    fixed=datetime(2026,11,4,tzinfo=timezone.utc);result={}
    for ext in ['svg','png','pdf']:
        p=out/f'{name}.{ext}'
        meta={'Date':None} if ext=='svg' else {'CreationDate':fixed,'ModDate':fixed} if ext=='pdf' else {}
        fig.savefig(p,dpi=300,metadata=meta);result[p.name]={'sha256':sha(p),'bytes':p.stat().st_size}
    plt.close(fig);return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=HERE);args=ap.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    profile='local' if (P/'work').is_dir() else 'public';root='work' if profile=='local' else 'reports'
    for path,h in PINS[profile].items():assert sha(P/path)==h,('changed input',path)
    u=read(P/UTILITY);m=read(P/root/'main_study_freeze_2026-11-03/final_evaluation/RESULTS.json');h=read(P/root/'information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json')
    counts=audit(u,m,h);setup()
    f,changes=render_main(u,m);outputs=save(f,out,'fig2-evidence-results')
    f,summary=render_summary(u);outputs.update(save(f,out,'fig3-summary-results'))
    binding={'status':'PASS','scope':'Presentation-only redesign; no scientific execution, inference or participant records.',
      'input_profile':profile,'input_sha256':PINS[profile],'script_sha256':sha(Path(__file__)),'colors':C,
      'verified_original_values':counts,'figure2':{'size_inches':[7,5.25],'all_native_panels':u['main_experiment']['panels'],
       'relative_discrepancy_changes':changes,'formula':'100 * (E1_MAE-E0_MAE)/E0_MAE',
       'MAE_definition':'Mean of three seed absolute discrepancies per constructor, then mean over five authors; no pooled endpoint score.',
       'bands':'CHNS CR1-t intervals; ENSANUT cluster-resampling stability bands; not equivalence regions.',
       'construction_order':'A01-A05 top-to-bottom within each Agent group; no author pairing across conditions.'},
      'figure3':{'size_inches':[7,4.65],'panels':summary,'native_panels':u['historical_information_experiment']['panels'],
       'shade':'Absolute relative deviation of constructor mean from supplied reference; 0-100% color scale.',
       'seed_tracks':'Signed relative deviation, common [-100%,100%] track in every cell. Zero tick is reference. Seed vertical offsets are visibility only.',
       'reference_uncertainty':'Intervals not plotted in the matrix; all available original intervals retained in numeric binding. No new intervals computed.',
       'counts':{'authors':6,'distinct_final_tables':18,'means':30,'seed_statistics':90},
       'interpretation':'Reconstruction: reference summaries are supplied to R, not independent validation.'},
      'outputs':outputs,'no_patient_rows_read':True,'no_generator_executed':True,'no_clinical_fit_rerun':True}
    (out/'NUMERIC_BINDINGS_23.json').write_text(json.dumps(binding,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','counts':counts,'outputs':list(outputs)}))

if __name__=='__main__':main()
