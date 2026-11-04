"""Conference-width Figures 2/3 from pinned, previously audited aggregates.

No patient or generated rows, generator, statistical fitting or network access.
Run from any directory. --output permits verification outside the source tree.
Local work/ and public reports/ have explicitly pinned input-byte profiles.
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
COL = {'E0': '#8064A2', 'E1': '#00857D', 'L': '#8064A2', 'R': '#00857D',
       'statistical': '#59616B', 'reference': '#808890', 'band': '#E7E9EC'}
UTILITY = 'manuscript/utility_package_2026-11-03/AGGREGATE_SOURCE.json'
PINS = {
 'local': {
  UTILITY: '3459ac8bc63a3de39aab1d23ee1e29c5c6369e52e2adbd90f2bdf6376215bef7',
  'work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json': '1fbc32d2f982d31c649d9217e644a34c02b81e08c093380fba8f3aaec9e4c2cb',
  'work/information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json': 'd64b7cd5bd1097a4ea51b84b00a3721d54c092cc87db85da9418bdd24bd187a0'},
 'public': {
  UTILITY: '3459ac8bc63a3de39aab1d23ee1e29c5c6369e52e2adbd90f2bdf6376215bef7',
  'reports/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json': '1fbc32d2f982d31c649d9217e644a34c02b81e08c093380fba8f3aaec9e4c2cb',
  'reports/information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json': '6f55901630fc0a0e5071b8e878d53230255c8c68b8d42f302a7f2cf842a36a9f'}
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def at(document, pointer):
    v = document
    for k in pointer.strip('/').split('/'):
        k = k.replace('~1', '/').replace('~0', '~')
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v

def verify(payload, main, historical):
    counts = {}
    for key, document, seedids, expected in [
        ('main_experiment', main, [5101,5102,5103], (6,72,216)),
        ('historical_information_experiment', historical, [4101,4102,4103], (5,30,90))]:
        panels = payload[key]['panels']
        ns, nm = 0, 0
        for panel in panels:
            ref = at(document, panel['reference_pointer'])
            if key == 'main_experiment':
                assert panel['reference'] == ref
            else:
                assert panel['reference']['value'] == ref
                if 'interval_pointer' in panel:
                    assert panel['reference']['interval'] == at(document, panel['interval_pointer'])
                else: assert panel['reference']['interval'] is None
            for s in panel['series']:
                assert [z['seed'] for z in s['seeds']] == seedids
                for z in s['seeds']:
                    assert z['value'] == at(document,z['pointer'])
                values=[z['value'] for z in s['seeds']]
                assert abs(s['mean']-statistics.mean(values)) < 1e-14
                assert s['range'] == [min(values),max(values)]
                summary=at(document,s['summary_pointer'])
                assert s['mean'] == summary['mean_effect' if key=='main_experiment' else 'mean']
                assert s['range'] == summary['seed_effect_range' if key=='main_experiment' else 'range']
                ns+=3; nm+=1
        assert (len(panels),nm,ns)==expected
        counts[key]={'panels':len(panels),'constructor_means':nm,'seed_values':ns}
    assert main['planned_constructions']==24
    assert main['scheduled_final_slots']==main['unique_successful_table_contents']==main['complete_analysis_slots']==72
    assert historical['attempts']==42 and historical['distinct_table_hashes']==24
    return counts

def configure():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7.5,
      'axes.titlesize':8,'axes.labelsize':7.1,'xtick.labelsize':6.5,'ytick.labelsize':6.7,
      'axes.linewidth':.6,'lines.linewidth':.8,'svg.fonttype':'none','pdf.fonttype':42,
      'svg.hashsalt':'evc-conference-fig23-v10','savefig.facecolor':'white'})

def fmt(x,pos):
    if abs(x)<1e-10:return '0'
    return f'{x:.3g}'.replace('-', '−')

def base_axis(ax,panel,main):
    ax.set_axisbelow(True)
    ax.grid(axis='y',color='#EDF0F2',linewidth=.5)
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['left','bottom']].set_color('#A2A7AD')
    ax.tick_params(width=.5,length=2.5,pad=2)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
    ax.yaxis.set_major_formatter(FuncFormatter(fmt))
    r=panel['reference']; interval=r.get('interval')
    if interval and interval.get('status')=='available':
        ax.axhspan(interval['lower'],interval['upper'],color=COL['band'],zorder=0)
    ax.axhline(r['value'],color=COL['reference'],ls=(0,(3,2)),linewidth=.8,zorder=1)
    values=[z['value'] for s in panel['series'] for z in s['seeds']]+[r['value']]
    if interval and interval.get('status')=='available': values += [interval['lower'],interval['upper']]
    low,high=min(values),max(values)
    if main: low=min(low,0);high=max(high,0)
    span=max(high-low,abs(high)*.05,1e-4)
    ax.set_ylim(low-.12*span,high+.14*span)
    if low<=0<=high: ax.axhline(0,color='#AEB4BA',lw=.6,zorder=1)

def points(ax,series,x,color):
    # In each constructor, left-to-right small dots are the three fixed seeds.
    # Diamond is the constructor mean; no author pairing across conditions.
    offsets=[-.027,0,.027]
    values=[z['value'] for z in series['seeds']]
    ax.plot([x,x],series['range'],color=color,lw=.55,alpha=.55,zorder=2)
    ax.scatter([x+d for d in offsets],values,s=8,color=color,alpha=.8,linewidths=.25,
               edgecolors='white',zorder=3)
    ax.scatter([x],[series['mean']],s=17,marker='D',facecolor='white',edgecolor=color,
               linewidths=.85,zorder=4)

def legend():
    return [Line2D([],[],ls='',marker='o',ms=3,color='#59616B',label='Seed draw'),
      Line2D([],[],ls='',marker='D',ms=4,mfc='white',mec='#59616B',label='Constructor mean'),
      Line2D([],[],ls=(0,(3,2)),lw=.8,color=COL['reference'],label='Sample reference'),
      Patch(facecolor=COL['band'],edgecolor='none',label='Reference interval / band')]

def render_main(payload):
    fig,axes=plt.subplots(2,3,figsize=(7,4.65))
    fig.subplots_adjust(left=.085,right=.99,bottom=.12,top=.925,hspace=.72,wspace=.49)
    for j,(ax,panel) in enumerate(zip(axes.flat,payload['main_experiment']['panels'])):
        base_axis(ax,panel,True)
        case='CHNS' if panel['case']=='CHNS2009' else 'ENSANUT'
        ax.set_title(f'({chr(97+j)}) {case}: {panel["predictor"]}',loc='left',pad=16,fontweight='semibold')
        ax.text(0,1.025,'Adjusted: '+panel['adjustment'].lower().replace('bmi','BMI'),transform=ax.transAxes,fontsize=6.5,color='#59616B')
        units=panel['display_unit'].replace('per ', '')
        ax.set_ylabel('HbA1c pp per '+units,labelpad=3)
        groups=[('agent','E0'),('agent','E1'),('statistical','E0'),('statistical','E1')]
        centers=[0,1.1,2.1,2.85]
        for (kind,cond),center in zip(groups,centers):
            series=[s for s in panel['series'] if s['kind']==kind and s['condition']==cond]
            expected=5 if kind=='agent' else 1
            assert len(series)==expected
            offsets=[-.32,-.16,0,.16,.32] if kind=='agent' else [0]
            for s,offset in zip(series,offsets):
                color=COL[cond] if kind=='agent' else COL['statistical']
                points(ax,s,center+offset,color)
        ax.set_xlim(-.54,3.15)
        ax.set_xticks(centers,['Agent\nE0','Agent\nE1','Stat.\nE0','Stat.\nE1'])
    fig.legend(handles=legend(),loc='lower center',bbox_to_anchor=(.53,.006),ncol=4,
               fontsize=6.6,frameon=False,handlelength=1.5,columnspacing=1.4)
    return fig

def render_historical(payload):
    fig,axes=plt.subplots(2,3,figsize=(7,4.3))
    fig.subplots_adjust(left=.085,right=.99,bottom=.10,top=.92,hspace=.7,wspace=.49)
    panels=payload['historical_information_experiment']['panels']
    for j,(ax,panel) in enumerate(zip(axes.flat,panels)):
        base_axis(ax,panel,False)
        title=panel['predictor'] if j<3 else ('Pearson correlation' if j==3 else 'Spearman correlation')
        ax.set_title(f'({chr(97+j)}) {title}',loc='left',pad=16,fontweight='semibold')
        subtitle='Adjusted: '+panel['adjustment'].lower().replace('bmi','BMI') if j<3 else 'Glucose–HbA1c'
        ax.text(0,1.025,subtitle,transform=ax.transAxes,fontsize=6.5,color='#59616B')
        label=panel['axis_label'].replace('HbA1c percentage points\nper ','HbA1c pp per ')
        if j>=3:label='Correlation coefficient'
        ax.set_ylabel(label,labelpad=3)
        for cond,center in [('L',0),('R',1)]:
            series=[s for s in panel['series'] if s['condition']==cond]
            assert len(series)==3
            for s,offset in zip(series,[-.25,0,.25]):points(ax,s,center+offset,COL[cond])
        ax.set_xlim(-.48,1.48)
        ax.set_xticks([0,1],['L: literature','R: + summaries'])
    ax=axes.flat[5];ax.axis('off')
    ax.legend(handles=legend(),loc='upper left',bbox_to_anchor=(-.03,.98),fontsize=7.1,
              frameon=False,handlelength=1.5,labelspacing=1.25)
    ax.text(.02,.03,'3 constructors per condition\n3 seed draws per constructor',transform=ax.transAxes,
            fontsize=7.1,color='#59616B',linespacing=1.5)
    return fig

def save(fig,out,stem):
    result={}
    fixed=datetime(2026,11,4,tzinfo=timezone.utc)
    for ext in ['svg','png','pdf']:
        path=out/f'{stem}.{ext}'
        metadata={'Date':None} if ext=='svg' else ({'CreationDate':fixed,'ModDate':fixed} if ext=='pdf' else {})
        fig.savefig(path,dpi=300,metadata=metadata)
        result[path.name]={'sha256':sha(path),'bytes':path.stat().st_size}
    plt.close(fig)
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=HERE)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    profile='local' if (P/'work').is_dir() else 'public'
    for path,expected in PINS[profile].items():assert sha(P/path)==expected,(path,'input hash mismatch')
    root='work' if profile=='local' else 'reports'
    payload=read(P/UTILITY)
    main_report=read(P/root/'main_study_freeze_2026-11-03/final_evaluation/RESULTS.json')
    historical=read(P/root/'information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json')
    counts=verify(payload,main_report,historical)
    configure()
    outputs=save(render_main(payload),out,'fig2-relational-evidence')
    outputs.update(save(render_historical(payload),out,'fig3-summary-reconstruction'))
    binding={'status':'PASS','scope':'Presentation-only redraw of all previously published panel values; no scientific reanalysis.',
      'profile':profile,'input_sha256':PINS[profile],'script_sha256':sha(Path(__file__)),
      'counts':counts,'all_plotted_seed_values_verified_against_original_report_pointers':306,
      'all_constructor_means_verified_against_original_report_pointers':102,
      'main_experiment':payload['main_experiment'],
      'historical_information_experiment':payload['historical_information_experiment'],
      'style':{'width_inches':7,'main_height_inches':4.65,'summary_height_inches':4.3,
               'colors':COL,'points':'All seed values; x-offsets only for visibility.',
               'means':'Open diamonds; constructors not paired across conditions.',
               'range_lines':'Three-seed ranges, not confidence intervals.',
               'references':'CHNS community CR1-t intervals; ENSANUT empirical stability bands; historical correlation intervals unavailable.'},
      'outputs':outputs}
    (out/'FIG23_NUMERIC_BINDINGS.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','profile':profile,'counts':counts,'outputs':list(outputs)},ensure_ascii=False))

if __name__=='__main__':main()
