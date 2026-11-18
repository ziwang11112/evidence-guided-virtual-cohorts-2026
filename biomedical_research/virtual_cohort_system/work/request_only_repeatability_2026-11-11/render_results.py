"""Postclosure reporting only; never modifies authors, samples or estimators."""
from pathlib import Path
import csv
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

ROOT = Path(__file__).resolve().parent
COLORS = {'ordinary': '#3765AF', 'workflow': '#D37A35'}
PANELS = [
    ('PNS', 'bmi_sbp', 'BMI–SBP association', 'mmHg per 5 kg/m²'),
    ('PNS', 'bmi_dbp', 'BMI–DBP association', 'mmHg per 5 kg/m²'),
    ('PNS', 'residual_correlation', 'SBP–DBP residual dependence', 'Pearson correlation'),
    ('lipids', 'K02-TC-BMI', 'BMI–TC association', 'mg/dL per 5 kg/m²'),
    ('lipids', 'K02-HDL-BMI', 'BMI–HDL association', 'mg/dL per 5 kg/m²'),
    ('lipids', 'K02-LIPID-RESIDUAL', 'TC–HDL residual dependence', 'Pearson correlation'),
]


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def row_order(rows):
    return sorted(rows, key=lambda r: (r['arm'] != 'ordinary', int(r['episode_id'].rsplit('_R', 1)[1])))


def main():
    plan = read(ROOT / 'PLAN.json')
    ids = {e['episode_id'] for e in plan['episodes']}
    assert len(ids) == 12
    for ep in ids:
        assert (ROOT / 'episodes' / ep / 'OUTCOME.json').is_file(), 'All authors must be terminal.'
    closure = read(ROOT / 'CONSTRUCTION_CLOSURE.json')
    assert closure['all_episodes_closed'] and {e['episode_id'] for e in closure['episodes']} == ids
    e = read(ROOT / 'EVALUATION.json')
    assert e['counts']['episodes'] == 12 and e['counts']['final_slots'] == 36
    assert {r['episode_id'] for r in e['episodes']} == ids
    out = ROOT / 'figures'
    out.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.titleweight': 'semibold', 'axes.labelcolor': '#303B4D',
                         'text.color': '#243044', 'axes.edgecolor': '#D3D9E3',
                         'svg.fonttype': 'none', 'pdf.fonttype': 42,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 3, figsize=(14.4, 8.3))
    numeric_rows = []
    for idx, (ax, (case, analysis, title, unit)) in enumerate(zip(axes.flat, PANELS)):
        rows = row_order([r for r in e['summaries'] if r['case_id'] == case and r['analysis_id'] == analysis])
        assert len(rows) == 6 and len({r['episode_id'] for r in rows}) == 6
        ref = rows[0]['reference']
        assert all(r['reference'] == ref for r in rows)
        rv = ref.get('value')
        unc = ref.get('uncertainty') or {}
        if unc.get('status') == 'available':
            ax.axvspan(unc['lower'], unc['upper'], color='#B3BCCB', alpha=.24, zorder=0)
        if rv is not None:
            ax.axvline(rv, color='#273247', lw=1.3, ls=(0, (4, 3)), zorder=1)
        labels = []
        for y, r in enumerate(rows):
            repeat = int(r['episode_id'].rsplit('_R', 1)[1])
            labels.append(('Ordinary' if r['arm'] == 'ordinary' else 'Workflow') + f'  {repeat}')
            numeric_rows.append({k: r.get(k) for k in ['episode_id','case_id','arm','analysis_id','unit','available_seeds','mean','minimum','maximum','mean_absolute_reference_difference']} | {'reference_value': rv})
            if r['mean'] is None:
                ax.text(.02, y, 'Unavailable', transform=ax.get_yaxis_transform(), va='center', color='#9A4550', fontsize=9)
                continue
            color = COLORS[r['arm']]
            vals = [v['value'] for v in r['values'] if v['status'] == 'success' and v['value'] is not None]
            ax.plot([r['minimum'], r['maximum']], [y, y], color=color, lw=2.2, alpha=.65, zorder=3)
            ax.scatter(vals, [y]*len(vals), facecolors='white', edgecolors=color, s=22, lw=.8, zorder=4)
            ax.scatter([r['mean']], [y], c=color, s=42, edgecolors='white', lw=.6, zorder=5)
        ax.axhline(2.5, color='#DFE4EC', lw=.8)
        ax.set_ylim(5.6, -.6)
        ax.set_yticks(range(6), labels)
        ax.tick_params(axis='both', length=0, pad=6)
        ax.set_title(f'{chr(97+idx)}   {title}', loc='left', fontsize=11, pad=12)
        ax.set_xlabel(unit, labelpad=8)
        ax.xaxis.grid(True, color='#E5E9F0', lw=.6)
        ax.set_axisbelow(True)
        lo, hi = ax.get_xlim()
        if lo < 0 < hi:
            ax.axvline(0, color='#B7BFCE', lw=.6, zorder=0)
        ax.text(.99, 1.03, 'Blood pressure' if case == 'PNS' else 'Lipids', transform=ax.transAxes,
                ha='right', fontsize=8, color='#697489')
    fig.suptitle('Repeated autonomous construction: every requested analysis', x=.075, y=.986, ha='left', fontsize=18, weight='bold')
    fig.text(.075, .944, '12 fresh sessions · 2 research requests · 3 constructors per policy and request', fontsize=11, color='#697489')
    handles = [Line2D([0],[0],marker='o',color=COLORS[a],lw=2,label=a.title()) for a in COLORS]
    handles += [Line2D([0],[0],color='#273247',ls='--',label='Existing clinical sample reference'),
                Patch(facecolor='#B3BCCB',alpha=.3,label='Available reference uncertainty')]
    fig.legend(handles=handles, loc='lower center', ncol=4, frameon=False, bbox_to_anchor=(.52,.046), fontsize=9)
    fig.text(.075,.024,'Filled dots: constructor means. Open dots / bars: three seeds / their range, including any encoded scenario draws; not confidence intervals.',fontsize=8.5,color='#697489')
    fig.text(.075,.006,'Reference intervals retain their original sampling assumptions; two exposed contexts support developmental evaluation, not general superiority.',fontsize=8.5,color='#697489')
    fig.subplots_adjust(left=.095,right=.985,top=.875,bottom=.16,wspace=.37,hspace=.55)
    for ext in ['png','svg','pdf']:
        fig.savefig(out/f'primary_analyses.{ext}', dpi=220, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    with (out/'primary_analyses.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(numeric_rows[0]));w.writeheader();w.writerows(numeric_rows)

    fig, axes = plt.subplots(1,3,figsize=(14.4,5.6))
    ep_plan={r['episode_id']:r for r in plan['episodes']}
    rows=sorted(e['episodes'],key=lambda r:(ep_plan[r['episode_id']]['case_id']!='PNS',ep_plan[r['episode_id']]['arm']!='ordinary',ep_plan[r['episode_id']]['constructor_repeat']))
    labels=[]
    for y,r in enumerate(rows):
        p=ep_plan[r['episode_id']];color=COLORS[p['arm']]
        labels.append(('BP' if p['case_id']=='PNS' else 'Lipids')+' · '+('Ord.' if p['arm']=='ordinary' else 'Flow')+f" {p['constructor_repeat']}")
        slots=[s for s in e['slots'] if s['episode_id']==r['episode_id']]
        counts=[sum(s['status']==status for s in slots)for status in ['success','failed','unavailable']]
        left=0
        for count,c in zip(counts,[color,'#A5485A','#D8DEE7']):
            if count:axes[0].barh(y,count,left=left,height=.56,color=c,edgecolor='white')
            left+=count
        axes[1].scatter(r['calls_reserved'],y,color=color,s=34)
        axes[2].plot([0,r['accounted_usd']],[y,y],color=color,lw=1.8)
        axes[2].scatter(r['known_tariff_cost_usd'],y,color=color,s=34)
        if r['unknown_usage_calls']:
            axes[2].scatter(r['accounted_usd'],y,marker='x',color='#A5485A',s=44)
    for i,(ax,title,xlabel) in enumerate(zip(axes,['Final planned tables','Model calls','Model cost'],['Tables per constructor','Reserved calls','USD; tariff estimate'])):
        ax.set_title(title,loc='left',fontsize=12,pad=12);ax.set_xlabel(xlabel)
        ax.set_ylim(11.6,-.6);ax.set_yticks(range(12),labels if i==0 else ['']*12)
        ax.tick_params(length=0,pad=5);ax.xaxis.grid(True,color='#E5E9F0',lw=.6);ax.set_axisbelow(True)
        for y in [2.5,5.5,8.5]:ax.axhline(y,color='#E1E5EC',lw=.8)
    axes[0].set_xlim(0,3.12);axes[0].set_xticks([0,1,2,3])
    axes[1].set_xlim(left=0);axes[2].set_xlim(left=0)
    fig.suptitle('Delivery and resources: all assigned constructors',x=.07,y=.99,ha='left',fontsize=18,weight='bold')
    fig.text(.07,.932,f"{e['counts']['successful_tables']} / 36 final tables delivered · {e['counts']['model_calls']} model calls · ${e['costs']['known_tariff_usd']:.3f} known model charges",fontsize=11,color='#697489')
    fig.text(.07,.025,'Blue: ordinary Agent. Orange: workflow. Red: failed final execution. Gray: unavailable. Calls and seeds are not clinical replications.',fontsize=9,color='#697489')
    fig.text(.07,.005,'Cost uses frozen tariffs; unknown usage remains reserved separately. No human review, orchestration cost or provider invoice is included.',fontsize=9,color='#697489')
    fig.subplots_adjust(left=.12,right=.98,top=.84,bottom=.15,wspace=.25)
    for ext in ['png','svg','pdf']:
        fig.savefig(out/f'delivery_resources.{ext}',dpi=220,bbox_inches='tight',facecolor='white')
    plt.close(fig)
    manifest={'evaluation_sha256':sha(ROOT/'EVALUATION.json'),'plan_sha256':sha(ROOT/'PLAN.json'),
              'primary_constructor_analysis_rows':len(numeric_rows),'generated_rows_read_by_renderer':False,
              'files':{p.name:sha(p)for p in sorted(out.iterdir())if p.is_file() and p.name!='FIGURE_MANIFEST.json'},
              'visual_review':'pending'}
    (out/'FIGURE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'figure_families':2,'primary_constructor_analysis_rows':len(numeric_rows),'output_directory':str(out)}))


if __name__=='__main__':
    main()
