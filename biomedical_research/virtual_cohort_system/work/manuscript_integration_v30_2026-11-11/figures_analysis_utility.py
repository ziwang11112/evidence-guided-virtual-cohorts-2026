"""Figure 5: aggregate-only publication figure. No models, rows or refits."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import math
import os
import shutil

PROJECT = Path(__file__).resolve().parents[2]
OUT = PROJECT / 'manuscript/paper_figures_v30_2026-11-11'
OUT.mkdir(parents=True, exist_ok=True)
os.environ['MPLCONFIGDIR'] = str(OUT / '.mplconfig')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

SOURCE = PROJECT / 'work/request_only_repeatability_2026-11-11'
SNAPSHOT = PROJECT / 'work/cross_model_api_pilot_2026-11-10/_host_only/REFERENCE_SNAPSHOT.json'
EXPECTED_EVALUATION_SHA = '23b8ec64d4c30428b6b206fb505bd428da17f90ccfe585c775724960838b57ef'
EXPECTED_REFERENCE_SHA = '2c70de16a941b2f023f249f52b2c7084789b20b3af4df9c6b0d2061316f8e002'
BLUE, PURPLE, ORANGE = '#2E69A1', '#8062A8', '#C27732'
INK, MUTED, GRID = '#253346', '#647084', '#E7EBF1'
COLORS = {'ordinary': BLUE, 'workflow': PURPLE}
PANELS = [
    ('PNS', 'bmi_sbp', 'SBP vs BMI', 'mmHg per 5 kg/m²'),
    ('PNS', 'bmi_dbp', 'DBP vs BMI', 'mmHg per 5 kg/m²'),
    ('PNS', 'residual_correlation', 'SBP-DBP dependence', 'Residual Pearson r'),
    ('lipids', 'K02-TC-BMI', 'TC vs BMI', 'mg/dL per 5 kg/m²'),
    ('lipids', 'K02-HDL-BMI', 'HDL vs BMI', 'mg/dL per 5 kg/m²'),
    ('lipids', 'K02-LIPID-RESIDUAL', 'TC-HDL dependence', 'Residual Pearson r'),
]

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assert sha(SOURCE / 'EVALUATION.json') == EXPECTED_EVALUATION_SHA
    assert sha(SNAPSHOT) == EXPECTED_REFERENCE_SHA
    evaluation = read(SOURCE / 'EVALUATION.json')
    plan = read(SOURCE / 'PLAN.json')
    closure = read(SOURCE / 'CONSTRUCTION_CLOSURE.json')
    reference = read(SNAPSHOT)['references']
    assigned = {x['episode_id'] for x in plan['episodes']}
    assert len(assigned) == 12
    assert closure['all_episodes_closed']
    assert assigned == {x['episode_id'] for x in closure['episodes']}
    assert assigned == {x['episode_id'] for x in evaluation['episodes']}
    assert evaluation['counts']['successful_tables'] == 36
    assert evaluation['reference_snapshot_sha256'] == EXPECTED_REFERENCE_SHA

    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 8,
        'axes.titlesize': 9, 'axes.titleweight': 'semibold',
        'axes.labelsize': 8, 'xtick.labelsize': 7.6, 'ytick.labelsize': 8,
        'text.color': INK, 'axes.labelcolor': INK,
        'xtick.color': MUTED, 'ytick.color': INK,
        'axes.edgecolor': GRID, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
    })
    fig, axes = plt.subplots(2, 3, figsize=(7.8, 6.0))
    fig.subplots_adjust(left=.15, right=.982, top=.865, bottom=.205,
                        wspace=.28, hspace=.69)
    rows_out, seeds_out, coverage = [], [], []
    axes_bindings = []
    for panel, (ax, (case, aid, title, unit)) in enumerate(zip(axes.flat, PANELS)):
        rows = sorted([r for r in evaluation['summaries']
                       if r['case_id'] == case and r['analysis_id'] == aid],
                      key=lambda r: (r['arm'] != 'ordinary', int(r['episode_id'].rsplit('_R', 1)[1])))
        assert len(rows) == 6 and len({r['episode_id'] for r in rows}) == 6
        ref = reference[case][aid]
        assert all(r['reference'] == ref for r in rows)
        rv = ref['value']
        uncertainty = ref.get('uncertainty') or {}
        available = uncertainty.get('status') == 'available'
        if available:
            ax.axvspan(uncertainty['lower'], uncertainty['upper'], facecolor=ORANGE,
                       alpha=.115, edgecolor='none', zorder=0)
        ax.axvline(rv, color=ORANGE, lw=1.1, ls=(0, (4, 2.6)), zorder=2)
        plot_extent = [rv]
        if available:
            plot_extent += [uncertainty['lower'], uncertainty['upper']]
        for y, r in enumerate(rows):
            values = [v['value'] for v in r['values']]
            assert r['available_seeds'] == len(values) == 3
            assert [v['seed'] for v in r['values']] == [54001, 54003, 54007]
            assert all(v['status'] == 'success' for v in r['values'])
            assert all(math.isfinite(v) for v in values)
            assert math.isclose(sum(values)/3, r['mean'], rel_tol=0, abs_tol=1e-12)
            assert min(values) == r['minimum'] and max(values) == r['maximum']
            color = COLORS[r['arm']]
            # Range is within one generated law; never a confidence interval.
            ax.plot([r['minimum'], r['maximum']], [y, y], color=color,
                    lw=1.8, alpha=.65, zorder=3, solid_capstyle='round')
            ys = [y-.065, y, y+.065]
            ax.scatter(values, ys, s=17, facecolor='white', edgecolor=color,
                       linewidth=.8, zorder=4)
            ax.scatter(r['mean'], y, marker='D', s=21, facecolor=color,
                       edgecolor='white', linewidth=.55, zorder=5)
            plot_extent += values
            row = {k:r[k] for k in ['episode_id','case_id','arm','analysis_id','unit',
                    'available_seeds','mean','minimum','maximum']}
            row.update(panel=chr(97+panel), reference_value=rv,
                       reference_interval_available=available,
                       reference_lower=uncertainty.get('lower'),
                       reference_upper=uncertainty.get('upper'),
                       reference_uncertainty_kind=uncertainty.get('kind'),
                       plot_y=y)
            rows_out.append(row)
            for v, yy in zip(r['values'], ys):
                seeds_out.append({'episode_id':r['episode_id'], 'analysis_id':aid,
                                  'seed':v['seed'], 'value':v['value'], 'plot_y':yy})
            coverage.append((r['episode_id'], aid))
        lo, hi = min(plot_extent), max(plot_extent)
        pad = (hi-lo)*.09
        ax.set_xlim(lo-pad, hi+pad)
        ax.set_ylim(5.6, -.6)
        ax.axhline(2.5, color=GRID, lw=.8, zorder=0)
        if lo < 0 < hi:
            ax.axvline(0, color='#BEC6D1', lw=.55, zorder=1)
        ax.set_yticks(range(6))
        if panel % 3 == 0:
            ax.set_yticklabels(['Ordinary 1','Ordinary 2','Ordinary 3',
                                'Workflow 1','Workflow 2','Workflow 3'])
            for label, color in zip(ax.get_yticklabels(), [BLUE]*3+[PURPLE]*3):
                label.set_color(color)
        else:
            ax.set_yticklabels([])
        ax.set_xlabel(unit, labelpad=6)
        ax.set_title(f'{chr(97+panel)}  {title}', loc='left', pad=9)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=3))
        ax.tick_params(length=0, pad=4)
        ax.spines[['top','left','right']].set_visible(False)
        ax.grid(axis='x', color=GRID, lw=.55, zorder=0)
        ax.set_axisbelow(True)
        # The label explains the reference without implying a pass/fail region.
        ax.text(.985, 1.01, f'Reference {rv:.2f}', transform=ax.transAxes,
                ha='right', color=ORANGE, fontsize=7.2)
        axes_bindings.append({'panel':chr(97+panel), 'case':case, 'analysis':aid,
                              'xlim':list(ax.get_xlim()), 'reference':ref,
                              'reference_band_plotted':available})

    assert len(coverage) == len(set(coverage)) == 36
    assert {x[0] for x in coverage} == assigned
    assert len(seeds_out) == 108
    assert sum(x['reference_band_plotted'] for x in axes_bindings) == 5
    assert not axes_bindings[5]['reference_band_plotted']
    fig.text(.15, .968, 'Blood pressure', fontsize=11, weight='bold', color=INK)
    fig.text(.15, .939, 'Age- and sex-adjusted BMI associations; joint dependence after adjustment',
             fontsize=7.8, color=MUTED)
    fig.text(.982, .969, '6 fresh constructions', ha='right', fontsize=8, color=MUTED)
    fig.text(.15, .535, 'Blood lipids', fontsize=11, weight='bold', color=INK)
    fig.text(.982, .536, '6 fresh constructions', ha='right', fontsize=8, color=MUTED)
    # Compact shared legend: policy colors and distinct statistical objects.
    handles = [
        Line2D([],[],marker='D',ms=4.5,color=BLUE,lw=0,label='Ordinary Agent'),
        Line2D([],[],marker='D',ms=4.5,color=PURPLE,lw=0,label='Workflow'),
        Line2D([],[],marker='o',ms=4.3,markerfacecolor='white',color=MUTED,
               lw=1.2,label='Seeds / range'),
        Line2D([],[],color=ORANGE,lw=1.1,ls='--',label='Real sample'),
        Patch(facecolor=ORANGE,alpha=.115,label='Reference interval'),
    ]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.54,.105),
               ncol=5, frameon=False, fontsize=7.5, handlelength=1.5,
               columnspacing=1.15, handletextpad=.5)
    fig.text(.15,.085,'Diamonds: means. Open circles: three saved seeds. Bars: seed ranges, not confidence intervals.',
             fontsize=7.2, color=MUTED)
    fig.text(.15,.061,'PNS bands: conditional row-resampling stability. Lipid slope bands: HC3 conditional sensitivity.',
             fontsize=7.2, color=MUTED)
    fig.text(.15,.037,'No interval is available for lipid residual dependence. Reference bands are not equivalence margins.',
             fontsize=7.2, color=MUTED)
    basename = 'fig5-autonomous-analysis-utility'
    for ext in ['pdf','svg','png']:
        fig.savefig(OUT/f'{basename}.{ext}',dpi=350,facecolor='white')
    plt.close(fig)
    for name, entries in [('fig5-constructor-estimates.csv',rows_out),
                          ('fig5-seed-estimates.csv',seeds_out)]:
        with (OUT/name).open('w',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(entries[0]));writer.writeheader();writer.writerows(entries)
    supplement = PROJECT/'work/scientific_check_revision_2026-11-11/reporting/paired_analysis_profiles.pdf'
    copied = OUT/'figS6-scientific-check-revision-profiles.pdf'
    shutil.copyfile(supplement,copied)
    assert sha(copied)==sha(supplement)
    manifest = {
        'created_utc':datetime.now(timezone.utc).isoformat(),
        'input_scope':'Existing saved aggregates only; no patient or generated rows read; no fit, generation or API.',
        'sources':{str(p.relative_to(PROJECT)):sha(p) for p in [SOURCE/'EVALUATION.json',SOURCE/'PLAN.json',SOURCE/'CONSTRUCTION_CLOSURE.json',SNAPSHOT,SOURCE/'render_results.py']},
        'coverage':{'constructors':12,'contexts':2,'endpoint_definitions':6,
                    'constructor_endpoint_estimates':36,'seed_estimates':108,'saved_generated_tables':36},
        'checks':{'all_assigned_constructors':True,'all_requested_endpoints':True,
                  'each_saved_seed':True,'mean_min_max_verified':True,
                  'all_reference_records_match_pinned_snapshot':True,
                  'no_reference_interval_invented':True,'no_favorable_selection':True},
        'panels':axes_bindings,
        'supplement_copy':{'source':str(supplement.relative_to(PROJECT)),
                           'destination':str(copied.relative_to(PROJECT)), 'sha256':sha(copied)},
        'outputs':{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.suffix in ['.pdf','.svg','.png','.csv']},
        'visual_qa':'pending actual PDF render',
    }
    (OUT/'FIG5_BINDINGS.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'outputs':basename,'coverage':manifest['coverage'],'supplement_copy_sha256':sha(copied)}))

if __name__=='__main__':
    main()
