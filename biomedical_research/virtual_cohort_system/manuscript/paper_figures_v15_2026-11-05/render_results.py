"""Render four v15 scientific figures from SHA-pinned, reviewed aggregates only.

No participant rows, generated tables, experiment execution, or model fitting.
Use --output NEW_DIRECTORY for a separate reproduction; PDFs are vector artwork.
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
PROJECT = HERE.parents[1]
UTILITY = 'manuscript/utility_package_2026-11-03/AGGREGATE_SOURCE.json'
MAIN = 'main_study_freeze_2026-11-03/final_evaluation/RESULTS.json'
SUMMARY = 'information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json'
CROSS = 'evidence_use_cross_task_2026-11-05/evaluation/RESULTS.json'
PINS = {
    UTILITY: '3459ac8bc63a3de39aab1d23ee1e29c5c6369e52e2adbd90f2bdf6376215bef7',
    MAIN: '1fbc32d2f982d31c649d9217e644a34c02b81e08c093380fba8f3aaec9e4c2cb',
    SUMMARY: 'd64b7cd5bd1097a4ea51b84b00a3721d54c092cc87db85da9418bdd24bd187a0',
    CROSS: '8cb8a5107181ca462d80ea38152420512052d7daf15ede7ddb8ddf8d57d95672',
}
C = {'blue':'#4266AD', 'violet':'#8071BA', 'terracotta':'#CE7F60',
     'grey':'#7C8798', 'ink':'#283448', 'band':'#E8EBF0',
     'axis':'#A5ADBA', 'grid':'#EEF0F3', 'reference':'#626D7E'}
CONDITION = {'E0':C['violet'], 'E1':C['blue'], 'L':C['violet'], 'R':C['blue']}
AUTHOR_COLORS = [C['blue'], C['violet'], C['terracotta']]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def at(document, pointer):
    for key in pointer.strip('/').split('/'):
        key = key.replace('~1','/').replace('~0','~')
        document = document[int(key)] if isinstance(document,list) else document[key]
    return document

def fmt(value, _position):
    return '0' if abs(value) < 1e-10 else f'{value:.3g}'

def configure():
    plt.rcParams.update({
        'font.family':'DejaVu Sans', 'font.size':8, 'text.color':C['ink'],
        'axes.labelcolor':C['ink'], 'axes.titlesize':8.8, 'axes.labelsize':8,
        'xtick.labelsize':7.5, 'ytick.labelsize':7.5, 'axes.linewidth':.65,
        'xtick.color':C['ink'], 'ytick.color':C['ink'], 'legend.fontsize':7.5,
        'svg.fonttype':'none', 'pdf.fonttype':42, 'svg.hashsalt':'evc-paper-v15-results',
    })

def audit_historical(utility, main, summary):
    counts = {}
    for key,doc,seeds,expected in [
        ('main_experiment',main,[5101,5102,5103],(6,72,216)),
        ('historical_information_experiment',summary,[4101,4102,4103],(5,30,90)),
    ]:
        means = points = 0
        for panel in utility[key]['panels']:
            reference = at(doc,panel['reference_pointer'])
            if key == 'main_experiment':
                assert panel['reference'] == reference
            else:
                assert panel['reference']['value'] == reference
                assert panel['reference']['interval'] == (at(doc,panel['interval_pointer']) if 'interval_pointer' in panel else None)
            for series in panel['series']:
                assert [z['seed'] for z in series['seeds']] == seeds
                values = [z['value'] for z in series['seeds']]
                assert all(z['value'] == at(doc,z['pointer']) for z in series['seeds'])
                assert abs(series['mean'] - statistics.mean(values)) < 1e-14
                assert series['range'] == [min(values),max(values)]
                source_summary = at(doc,series['summary_pointer'])
                assert series['mean'] == source_summary['mean_effect' if key == 'main_experiment' else 'mean']
                points += len(values)
                means += 1
        assert (len(utility[key]['panels']),means,points) == expected
        counts[key] = {'endpoints':expected[0], 'constructor_means':means, 'seed_statistics':points}
    assert main['planned_constructions'] == 24 and main['unique_successful_table_contents'] == 72
    assert summary['independent_constructors'] == 6 and summary['attempts'] == 42 and summary['distinct_table_hashes'] == 24
    counts['main_experiment'].update(constructions=24,final_tables=72)
    counts['historical_information_experiment'].update(constructions=6,final_tables=18)
    return counts

def base_axis(ax, horizontal=False):
    ax.set_facecolor('white')
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['left','bottom']].set_color(C['axis'])
    ax.tick_params(length=2.6,width=.65,pad=3)
    numeric_axis = ax.xaxis if horizontal else ax.yaxis
    numeric_axis.set_major_locator(MaxNLocator(nbins=4))
    numeric_axis.set_major_formatter(FuncFormatter(fmt))

def vertical_reference(ax, panel, include_zero):
    base_axis(ax)
    reference = panel['reference']
    interval = reference.get('interval')
    values = [z['value'] for s in panel['series'] for z in s['seeds']] + [reference['value']]
    if interval and interval.get('status') == 'available':
        ax.axhspan(interval['lower'],interval['upper'],color=C['band'],zorder=0)
        values += [interval['lower'],interval['upper']]
    ax.axhline(reference['value'],color=C['reference'],lw=.9,ls=(0,(3,2)),zorder=1)
    lo,hi = min(values),max(values)
    if include_zero:
        lo,hi = min(lo,0),max(hi,0)
    span = max(hi-lo,abs(hi)*.05,1e-4)
    ax.set_ylim(lo-.09*span,hi+.12*span)
    if lo <= 0 <= hi:
        ax.axhline(0,color='#BFC5CE',lw=.6,zorder=1)

def vertical_series(ax, series, position, color, offset=.032):
    ax.plot([position,position],series['range'],color=color,lw=.7,alpha=.75,zorder=2)
    ax.scatter([position-offset,position,position+offset], [z['value'] for z in series['seeds']],
               s=11,color=color,edgecolors='white',linewidths=.25,zorder=3)
    ax.scatter(position,series['mean'],s=21,marker='D',facecolor='white',edgecolor=color,linewidths=.95,zorder=4)

def common_legend(fig, anchor=.005, historical=False, horizontal=False):
    handles = [
        Line2D([],[],ls='',marker='o',ms=3.4,color=C['grey'],label='Seed'),
        Line2D([],[],ls='',marker='D',ms=4.2,mfc='white',mec=C['grey'],mew=.95,label='Constructor mean'),
        Line2D([],[],ls=(0,(3,2)),lw=.9,color=C['reference'],label='Reference'),
        Patch(facecolor=C['band'],edgecolor='none',label='Reference band'),
    ]
    if historical:
        handles[0:1] = [
            Line2D([],[],ls='',marker='o',ms=3.4,color=CONDITION['L'],label='L seed'),
            Line2D([],[],ls='',marker='o',ms=3.4,color=CONDITION['R'],label='R seed'),
        ]
    if horizontal:
        handles[2] = Line2D([],[],ls=(0,(3,2)),lw=.9,marker='D',ms=3.6,
                            color=C['reference'],label='Reference')
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,anchor),ncol=len(handles),
               frameon=False,handlelength=1.45,columnspacing=1.1,handletextpad=.5)

def render_evidence(utility):
    fig,axes = plt.subplots(2,3,figsize=(7,4.35))
    fig.subplots_adjust(left=.085,right=.988,bottom=.16,top=.925,hspace=.55,wspace=.50)
    for i,(ax,panel) in enumerate(zip(axes.flat,utility['main_experiment']['panels'])):
        vertical_reference(ax,panel,True)
        case = 'CHNS' if panel['case']=='CHNS2009' else 'ENSANUT'
        title = f'({chr(97+i)}) {case}: {panel["predictor"]}'
        ax.set_title(title,loc='left',pad=8)
        ax.set_ylabel('HbA1c pp / '+panel['display_unit'].removeprefix('per '),labelpad=4)
        centers = [0,1.2,2.3,3.05]
        for (kind,condition),center in zip([('agent','E0'),('agent','E1'),('statistical','E0'),('statistical','E1')],centers):
            series = [s for s in panel['series'] if s['kind']==kind and s['condition']==condition]
            assert len(series) == (5 if kind=='agent' else 1)
            offsets = [-.36,-.18,0,.18,.36] if kind=='agent' else [0]
            for item,delta in zip(series,offsets):
                vertical_series(ax,item,center+delta,CONDITION[condition] if kind=='agent' else C['grey'])
        ax.set_xlim(-.58,3.42)
        ax.set_xticks(centers,['Agent\nE0','Agent\nE1','Stat.\nE0','Stat.\nE1'])
        for label,color in zip(ax.get_xticklabels(),[CONDITION['E0'],CONDITION['E1'],C['grey'],C['grey']]):
            label.set_color(color)
    common_legend(fig)
    return fig

def render_summary(utility):
    fig = plt.figure(figsize=(7,4.35))
    grid = fig.add_gridspec(2,6,left=.085,right=.988,bottom=.16,top=.925,hspace=.55,wspace=1.05)
    axes = [fig.add_subplot(grid[0,j:j+2]) for j in [0,2,4]]
    axes += [fig.add_subplot(grid[1,1:3]),fig.add_subplot(grid[1,3:5])]
    for i,(ax,panel) in enumerate(zip(axes,utility['historical_information_experiment']['panels'])):
        vertical_reference(ax,panel,i<3)
        title = panel['predictor'] if i<3 else 'Pearson correlation' if i==3 else 'Spearman correlation'
        ax.set_title(f'({chr(97+i)}) {title}',loc='left',pad=8)
        ylabel = panel['axis_label'].replace('HbA1c percentage points\nper ','HbA1c pp / ') if i<3 else ('Pearson r' if i==3 else 'Spearman rho')
        ax.set_ylabel(ylabel,labelpad=4)
        positions = [0,1,2,4,5,6]
        for series,position in zip(panel['series'],positions,strict=True):
            vertical_series(ax,series,position,CONDITION[series['condition']],offset=.14)
        ax.set_xlim(-.7,6.7)
        ax.set_xticks(positions,[s['constructor'] for s in panel['series']])
        ax.tick_params(axis='x',labelsize=7.2)
        for label,series in zip(ax.get_xticklabels(),panel['series']):
            label.set_color(CONDITION[series['condition']])
    common_legend(fig,historical=True)
    return fig

PRIMARY_SPECS = [
    ('ENSANUT2018','Q1_age10','HbA1c: age','HbA1c pp / 10 years','Sex, BMI and glucose'),
    ('Turkana','K02-HDL-BMI','HDL: BMI','HDL mg/dL / 5 kg/m²','Age and sex'),
    ('ENSANUT2018','Q2_bmi5','HbA1c: BMI','HbA1c pp / 5 kg/m²','Age and sex'),
    ('Turkana','K02-TC-BMI','TC: BMI','TC mg/dL / 5 kg/m²','Age and sex'),
    ('ENSANUT2018','Q3_bmi5','HbA1c: BMI + glucose','HbA1c pp / 5 kg/m²','Age, sex and glucose'),
    ('Turkana','K02-LIPID-RESIDUAL','TC-HDL residual correlation','Pearson r','Age, sex and BMI'),
]
DISPERSION_SPECS = [
    ('ENSANUT2018','hba1c.sd_population','HbA1c: marginal spread','HbA1c SD, pp',None),
    ('ENSANUT2018','q1_residual_rms','HbA1c: conditional spread','Full-model residual RMS, pp',None),
    ('Turkana','total_cholesterol.sd_sample','TC: marginal spread','TC sample SD, mg/dL',None),
    ('Turkana','hdl_cholesterol.sd_sample','HDL: marginal spread','HDL sample SD, mg/dL',None),
]

def cross_panels(cross, specs, category):
    panels = []
    assert len(cross['all_final_slots'])==18 and cross['unique_final_table_hashes']==18
    for case,endpoint,title,label,adjustment in specs:
        authors = ['H01','H02','H03'] if case=='ENSANUT2018' else ['L01','L02','L03']
        series = []
        for author in authors:
            points = []
            for si,slot in enumerate(cross['all_final_slots']):
                if slot['case_id']!=case or slot['author_id']!=author:
                    continue
                ei = next(i for i,z in enumerate(slot[category]) if z['id']==endpoint)
                row = slot[category][ei]
                assert row['value'] is not None
                points.append({'seed':slot['seed'],'value':row['value'],'unit':row['unit'],
                               'pointer':f'/all_final_slots/{si}/{category}/{ei}/value',
                               'reference_pointer':f'/all_final_slots/{si}/{category}/{ei}/reference',
                               'table_sha256':slot['table_sha256']})
            assert [z['seed'] for z in points]==[9101,9102,9103]
            values = [z['value'] for z in points]
            mean,span = statistics.mean(values),[min(values),max(values)]
            summary_index = next((i for i,z in enumerate(cross['all_author_endpoint_summaries']) if z['author_id']==author and z['endpoint']==endpoint),None)
            reference = at(cross,points[0]['reference_pointer'])
            assert all(at(cross,z['reference_pointer'])==reference for z in points)
            if summary_index is not None:
                summary = cross['all_author_endpoint_summaries'][summary_index]
                assert abs(mean-summary['slot_mean']) < 1e-14 and span==summary['slot_range']
                assert summary['reference']==reference
            # Identical display-only arithmetic to the reviewed v14 renderer;
            # diagnostic means were not separately stored in the aggregate file.
            series.append({'constructor':author,'seeds':points,'mean':mean,'range':span,
                           'summary_pointer':f'/all_author_endpoint_summaries/{summary_index}' if summary_index is not None else None,
                           'display_arithmetic':'statistics.mean and min/max, identical to v14 renderer'})
        assert all(at(cross,z['reference_pointer'])==reference for s in series for z in s['seeds'])
        panels.append({'case':case,'endpoint':endpoint,'title':title,'axis_label':label,
                       'adjustment':adjustment,'reference':reference,'series':series})
    return panels

def horizontal_panel(ax,panel,index):
    base_axis(ax,horizontal=True)
    ax.spines['left'].set_visible(False)
    reference = panel['reference']
    interval = reference.get('interval')
    values = [p['value'] for s in panel['series'] for p in s['seeds']] + [reference['value']]
    if interval and interval.get('lower') is not None and interval.get('upper') is not None:
        ax.axvspan(interval['lower'],interval['upper'],color=C['band'],zorder=0)
        values += [interval['lower'],interval['upper']]
    ax.axvline(reference['value'],color=C['reference'],lw=.9,ls=(0,(3,2)),zorder=1)
    if panel['endpoint'] in [s[1] for s in PRIMARY_SPECS]:
        values.append(0)
        ax.axvline(0,color='#BFC5CE',lw=.65,zorder=1)
    ax.scatter(reference['value'],0,color=C['reference'],s=23,marker='D',zorder=4)
    for i,series in enumerate(panel['series']):
        y = 3-i
        color = AUTHOR_COLORS[i]
        ax.hlines(y,*series['range'],color=color,lw=.85,zorder=2)
        ax.scatter([z['value'] for z in series['seeds']],[y-.13,y,y+.13],s=14,
                   color=color,edgecolors='white',linewidths=.25,zorder=3)
        ax.scatter(series['mean'],y,facecolor='white',edgecolor=color,s=25,marker='D',lw=.95,zorder=4)
    lo,hi = min(values),max(values)
    span = max(hi-lo,abs(hi)*.05,1e-4)
    ax.set_xlim(lo-.08*span,hi+.10*span)
    ax.set_yticks([3,2,1,0],[s['constructor'] for s in panel['series']]+['Ref.'])
    for label,color in zip(ax.get_yticklabels(),AUTHOR_COLORS+[C['reference']]):
        label.set_color(color)
    ax.set_ylim(-.4,3.5)
    ax.tick_params(axis='y',length=0,pad=5,labelsize=8)
    ax.grid(axis='y',color=C['grid'],lw=.55,zorder=0)
    ax.set_title(f'({chr(97+index)}) {panel["title"]}',loc='left',pad=8)
    ax.set_xlabel(panel['axis_label'],labelpad=4)

def render_cross(panels, dispersion=False):
    nrows = 2 if dispersion else 3
    fig,axes = plt.subplots(nrows,2,figsize=(7,4.2 if dispersion else 5.85))
    fig.subplots_adjust(left=.085,right=.98,bottom=.15 if dispersion else .11,
                        top=.925 if dispersion else .945,hspace=.78 if dispersion else .88,wspace=.28)
    for i,(ax,panel) in enumerate(zip(axes.flat,panels)):
        horizontal_panel(ax,panel,i)
    common_legend(fig,horizontal=True)
    return fig

def inspect_layout(fig):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    fonts = []
    clipped = []
    outside_ticks = set()
    for axis in fig.axes:
        for numeric,limits in [(axis.xaxis,axis.get_xlim()),(axis.yaxis,axis.get_ylim())]:
            for tick in numeric.get_major_ticks():
                if not min(limits) <= tick.get_loc() <= max(limits):
                    outside_ticks.update([tick.label1,tick.label2])
    for item in fig.findobj(match=matplotlib.text.Text):
        if not item.get_visible() or not item.get_text() or item in outside_ticks:
            continue
        bounds = item.get_window_extent(renderer)
        if bounds.x0 < -1 or bounds.y0 < -1 or bounds.x1 > fig.bbox.x1+1 or bounds.y1 > fig.bbox.y1+1:
            clipped.append(item.get_text())
        fonts.append(item.get_fontsize())
    assert not clipped,('Text outside canvas',clipped)
    assert min(fonts)>=7.2,min(fonts)
    return {'minimum_font_pt':min(fonts),'maximum_font_pt':max(fonts),'canvas_text_clipping':clipped,
            'width_inches':fig.get_figwidth(),'height_inches':fig.get_figheight()}

def save(fig,output,name):
    layout = inspect_layout(fig)
    date = datetime(2026,11,5,tzinfo=timezone.utc)
    outputs = {}
    for extension in ['svg','png','pdf']:
        path = output/f'{name}.{extension}'
        metadata = {'Date':None} if extension=='svg' else {'CreationDate':date,'ModDate':date} if extension=='pdf' else {}
        fig.savefig(path,dpi=300,metadata=metadata,facecolor='white')
        outputs[path.name] = {'sha256':sha(path),'bytes':path.stat().st_size}
    # 100 dpi is a compact near-print-size inspection image, not the deliverable.
    review_dir = output/'qa'
    review_dir.mkdir(exist_ok=True)
    fig.savefig(review_dir/f'{name}-print-size.png',dpi=100,facecolor='white')
    plt.close(fig)
    return outputs,layout

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE)
    parser.add_argument('--project',type=Path,default=PROJECT)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True,exist_ok=True)
    profile = 'work' if (args.project/'work').is_dir() else 'reports'
    documents,input_hashes = {},{}
    for name,pin in PINS.items():
        path = args.project/name if name==UTILITY else args.project/profile/name
        if name==SUMMARY and profile=='reports':
            pin = '6f55901630fc0a0e5071b8e878d53230255c8c68b8d42f302a7f2cf842a36a9f'
        assert sha(path)==pin,('Reviewed aggregate hash mismatch',str(path))
        input_hashes[path.relative_to(args.project).as_posix()] = pin
        documents[name] = json.loads(path.read_text(encoding='utf-8-sig'))
    utility,main_results,summary,cross = [documents[k] for k in [UTILITY,MAIN,SUMMARY,CROSS]]
    counts = audit_historical(utility,main_results,summary)
    primary_panels = cross_panels(cross,PRIMARY_SPECS,'analyses')
    dispersion_panels = cross_panels(cross,DISPERSION_SPECS,'diagnostics')
    counts['cross_task_primary'] = {'endpoints':6,'constructor_means':18,'seed_statistics':54,'constructions':6,'final_tables':18}
    counts['cross_task_dispersion'] = {'endpoints':4,'constructor_means':12,'seed_statistics':36,'constructions':6,'final_tables':18}
    assert sum(len(s['seeds']) for p in primary_panels for s in p['series'])==54
    assert sum(len(s['seeds']) for p in dispersion_panels for s in p['series'])==36
    configure()
    figures = [
        ('fig2-evidence-results',render_evidence(utility)),
        ('fig3-cross-task',render_cross(primary_panels)),
        ('fig4-summary-results',render_summary(utility)),
        ('figS3-dispersion',render_cross(dispersion_panels,True)),
    ]
    outputs,layouts = {},{}
    for name,figure in figures:
        artifact_hashes,layout = save(figure,output,name)
        outputs.update(artifact_hashes)
        layouts[name] = layout
    bindings = {
        'status':'PASS','scope':'Presentation-only redraw from reviewed aggregates; no scientific semantic changes.',
        'input_sha256':input_hashes,'script_sha256':sha(Path(__file__)),
        'verified_value_counts':counts,
        'figure2':utility['main_experiment'], 'figure3':primary_panels,
        'figure4':utility['historical_information_experiment'], 'figureS3':dispersion_panels,
        'style':{'colors':C,'layouts':layouts,'seed':'Three filled circles; offsets only separate marks.',
                 'mean':'Open diamond, existing reviewed mean.',
                 'range':'Within-constructor min/max, not a confidence interval.',
                 'reference':'Dashed line; dark diamond also marks horizontal-panel reference row.',
                 'normalization':'None. All axes retain endpoint-specific native units.',
                 'paired_matching':'None. E0/E1 and L/R constructors are independent.',
                 'selection':'All endpoints, constructors, and final seeds from the four preceding displays.'},
        'output_sha256':outputs,'individual_rows_read':False,'generator_executed':False,
        'clinical_analysis_rerun':False,'semantic_changes':[],
    }
    (output/'NUMERIC_BINDINGS_RESULTS.json').write_text(json.dumps(bindings,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','counts':counts,'layouts':layouts,'outputs':list(outputs)},indent=2))

if __name__=='__main__':
    main()
