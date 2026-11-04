"""Aggregate-only display; never opens participant-like tables or runs a model."""
from pathlib import Path
from collections import Counter
from statistics import mean
import csv
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

ROOT = Path(__file__).resolve().parent
EVAL = ROOT / 'evaluation_v2'
OUT = ROOT / 'display'
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_text(encoding='utf-8'))
completed = READ(EVAL / 'EVALUATION_COMPLETED.json')
for name, digest in completed['outputs'].items():
    assert SHA(EVAL / name) == digest, name
data = READ(EVAL / 'RESULTS.json')
assert len(data['all_final_slots']) == 12
assert all(s['analysis_status'] == 'complete' for s in data['all_final_slots'])
assert len(data['all_author_endpoint_summaries']) == 12
OUT.mkdir(exist_ok=True)

PANELS = [
    ('CHNS2009', 'E1', 'BMI association', 'Adjusted for age and sex', 'HbA1c pp per kg/m²'),
    ('CHNS2009', 'E2', 'Glucose association', 'Adjusted for age and sex', 'HbA1c pp per mmol/L'),
    ('CHNS2009', 'E3', 'Age association', 'Adjusted for sex, BMI and glucose', 'HbA1c pp per year'),
    ('ENSANUT2018', 'Q1_age10', 'Age association', 'Adjusted for sex, BMI and glucose', 'HbA1c pp per 10 years'),
    ('ENSANUT2018', 'Q2_bmi5', 'BMI association', 'Adjusted for age and sex', 'HbA1c pp per 5 kg/m²'),
    ('ENSANUT2018', 'Q3_bmi5', 'BMI association', 'Adjusted for age, sex and glucose', 'HbA1c pp per 5 kg/m²'),
]
COLORS = ['#325DAD', '#8462AD']
CORAL = '#C7654F'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.spines.left': False, 'axes.edgecolor': '#ABB4C2',
                     'axes.labelcolor': '#334155', 'text.color': '#15243C',
                     'xtick.color': '#475569', 'ytick.color': '#334155',
                     'svg.fonttype': 'none', 'pdf.fonttype': 42})
fig, axes = plt.subplots(2, 3, figsize=(13.4, 7.4))
fig.subplots_adjust(left=.065, right=.985, top=.72, bottom=.20, hspace=1.15, wspace=.34)
fig.suptitle('Open evidence → Agent-authored cohorts → scientific analyses',
             x=.05, y=.985, ha='left', fontsize=17, fontweight='bold')
fig.text(.05, .935, '4 Agent constructions · 12 final tables · 3,000 virtual people per table',
         fontsize=11, color='#526176')
fig.text(.05, .81, 'CHNS 2009 request', fontsize=12, fontweight='bold')
fig.text(.05, .455, 'ENSANUT 2018 request', fontsize=12, fontweight='bold')
legend = [Line2D([0], [0], color=c, marker='D', ms=6, lw=1.5, label=l)
          for c, l in zip(COLORS, ['Construction 1 (C01 / E01)', 'Construction 2 (C02 / E02)'])]
legend += [Line2D([0], [0], color=CORAL, lw=1.7, label='Existing sample reference'),
           Patch(facecolor='#EAEDF2', label='Reference interval / stability band')]
fig.legend(handles=legend, loc='upper left', bbox_to_anchor=(.045, .905), ncol=2,
           frameon=False, columnspacing=2.5, fontsize=10)

summaries = []
for j, (ax, spec) in enumerate(zip(axes.flat, PANELS)):
    case, endpoint, title, subtitle, unit = spec
    rows = [s for s in data['all_author_endpoint_summaries']
            if s['case_id'] == case and s['endpoint'] == endpoint]
    assert len(rows) == 2
    ref = rows[0]['reference']
    band = ref['interval']
    ax.axvspan(band['lower'], band['upper'], color='#EAEDF2', zorder=0)
    ax.axvline(ref['value'], color=CORAL, lw=1.7, zorder=1)
    xmax = max(band['upper'], *(r['slot_range'][1] for r in rows)) * 1.14
    for k, row in enumerate(rows):
        y = 1 - k
        values = [next(x['value'] for x in s['analyses'] if x['id'] == endpoint)
                  for s in data['all_final_slots'] if s['author_id'] == row['author_id']]
        assert len(values) == 3
        ax.plot(row['slot_range'], [y, y], color=COLORS[k], lw=1.8, zorder=3)
        ax.scatter(values, [y + .10, y, y - .10], s=30, facecolors='white',
                   edgecolors=COLORS[k], linewidths=1.1, zorder=4)
        ax.scatter([row['slot_mean']], [y], s=45, marker='D', color=COLORS[k], zorder=5)
        summaries.append({'case': case, 'endpoint': endpoint, 'description': title,
                          'adjustment': subtitle, 'unit': unit, 'author': row['author_id'],
                          'reference': ref['value'], 'reference_lower': band['lower'],
                          'reference_upper': band['upper'], 'generated_mean': row['slot_mean'],
                          'seed_min': row['slot_range'][0], 'seed_max': row['slot_range'][1],
                          'same_direction_draws': row['same_direction_slot_count']})
    ax.set_yticks([1, 0], [r['author_id'] for r in rows])
    ax.set_ylim(-.45, 1.45)
    ax.set_xlim(0, xmax)
    ax.tick_params(axis='y', length=0)
    ax.xaxis.set_major_locator(MaxNLocator(4))
    ax.grid(axis='x', color='#EDF0F5', lw=.6)
    ax.set_axisbelow(True)
    ax.set_xlabel(unit, fontsize=9, labelpad=6)
    ax.set_title(f'{chr(97+j)}  {title}', loc='left', fontsize=11, fontweight='bold', pad=26)
    ax.text(0, 1.11, subtitle, transform=ax.transAxes, fontsize=9, color='#526176')
fig.text(.05, .091, 'Open circles: three seed draws. Diamond: their mean. Horizontal line: seed range, not a confidence interval.', fontsize=10)
fig.text(.05, .055, 'Shading: CHNS cluster-based 95% interval; ENSANUT empirical resampling band. Neither is a pass/fail threshold.', fontsize=9, color='#526176')
fig.text(.05, .022, 'HbA1c pp = percentage points. Previously exposed references; developmental replication, not new clinical validation.', fontsize=9, color='#526176')
for extension in ('png', 'svg', 'pdf'):
    fig.savefig(OUT / f'primary_analyses.{extension}', dpi=200, facecolor='white')
plt.close(fig)
with (OUT / 'PRIMARY_SUMMARY.csv').open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(summaries[0])); w.writeheader(); w.writerows(summaries)

lines = ['# All prespecified diagnostic summaries', '',
         'Aggregate-only display of all diagnostics. Mean and range summarize three seed draws from each fixed construction; they are not confidence intervals. No across-unit score or post-hoc success threshold is applied.', '']
diag_rows = []
for aid in ('C01', 'C02', 'E01', 'E02'):
    slots = [s for s in data['all_final_slots'] if s['author_id'] == aid]
    lines += [f'## {aid}', '', '| Diagnostic | Unit | Reference | Seed mean | Seed range |', '|---|---|---:|---:|---|']
    for x in slots[0]['diagnostics']:
        vals = [next(d['value'] for d in s['diagnostics'] if d['id'] == x['id']) for s in slots]
        row = {'author': aid, 'case': slots[0]['case_id'], 'diagnostic': x['id'], 'unit': x['unit'],
               'reference': x['reference']['value'], 'mean': mean(vals), 'min': min(vals), 'max': max(vals)}
        diag_rows.append(row)
        lines.append(f"| {x['id']} | {x['unit']} | {row['reference']:.6g} | {row['mean']:.6g} | {row['min']:.6g}–{row['max']:.6g} |")
    lines.append('')
(OUT / 'ALL_DIAGNOSTICS.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
with (OUT / 'DIAGNOSTIC_SUMMARY.csv').open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(diag_rows[0])); w.writeheader(); w.writerows(diag_rows)
manifest = {'builder_sha256': SHA(Path(__file__)),
            'input_results_sha256': SHA(EVAL / 'RESULTS.json'),
            'input_completion_sha256': SHA(EVAL / 'EVALUATION_COMPLETED.json'),
            'aggregate_inputs_only': True, 'new_generation_or_patient_reads': False,
            'primary_summary_rows': len(summaries), 'diagnostic_summary_rows': len(diag_rows),
            'primary_seed_estimates': sum(len(s['analyses']) for s in data['all_final_slots']),
            'all_endpoint_estimates': sum(len(s['analyses'])+len(s['diagnostics']) for s in data['all_final_slots']),
            'outputs': {p.name: SHA(p) for p in sorted(OUT.iterdir()) if p.name != 'DISPLAY_MANIFEST.json'}}
(OUT / 'DISPLAY_MANIFEST.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'primary_summaries': len(summaries), 'diagnostic_summaries': len(diag_rows),
                  'all_analysis_statuses': dict(Counter(s['analysis_status'] for s in data['all_final_slots']))}))
