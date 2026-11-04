"""Render original aggregate figures and the complete metric table; no row reads."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, ScalarFormatter

HERE = Path(__file__).resolve().parent
CORE = [
    ('model_A.bmi', 'A: BMI', 'HbA1c percentage points / (kg/m²)'),
    ('model_A.age', 'A: Age', 'HbA1c percentage points / year'),
    ('model_A.female', 'A: Female coefficient', 'HbA1c percentage points'),
    ('model_B.bmi', 'B: BMI (glucose-adjusted)', 'HbA1c percentage points / (kg/m²)'),
    ('model_B.glucose', 'B: Glucose', 'HbA1c percentage points / (mmol/L)'),
    ('model_B.age', 'B: Age (glucose-adjusted)', 'HbA1c percentage points / year'),
    ('model_B.female', 'B: Female (glucose-adjusted)', 'HbA1c percentage points'),
]

def fmt(q):
    if q['median'] is None:
        return 'Unavailable'
    return f"{q['median']:.5g} [{q['q10']:.5g}, {q['q90']:.5g}]"

def main():
    report = json.loads((HERE/'REPORT.json').read_text(encoding='utf-8'))
    labels = list(report['generated'])
    fig, axes = plt.subplots(2, 4, figsize=(17, 8.2))
    colors = ['#505b68', '#1174b2', '#358eaa', '#7652a0']
    for ax, (key, title, unit) in zip(axes.flat, CORE):
        item = report['summary'][key]
        entries = [item['real_real']['absolute']] + [item['generated'][g]['sym_abs'] for g in labels]
        names = ['Real–real'] + ['G '+g for g in labels]
        for y, (q, color) in enumerate(zip(entries, colors)):
            if q['median'] is not None:
                ax.plot([q['q10'], q['q90']], [y, y], color=color, linewidth=2.3)
                ax.plot(q['median'], y, 'o', color=color, markersize=6)
        ax.set_yticks(range(4), names, fontsize=9)
        ax.set_ylim(3.6, -.6)
        ax.set_xlim(left=0)
        ax.xaxis.set_major_locator(MaxNLocator(4))
        form = ScalarFormatter(useOffset=False)
        form.set_powerlimits((-3, 3))
        ax.xaxis.set_major_formatter(form)
        ax.tick_params(axis='x', labelsize=9)
        ax.grid(axis='x', color='#e2e6ea', linewidth=.7)
        ax.set_axisbelow(True)
        ax.spines[['top','right','left']].set_visible(False)
        ax.set_title(title, loc='left', fontsize=11, fontweight='bold', pad=12)
        ax.set_xlabel('Absolute difference\n'+unit, fontsize=9)
    axes.flat[-1].axis('off')
    axes.flat[-1].text(0, .95,
        '100 fixed community splits\n3,000 people per real side\n3 frozen G tables (3,000 rows)\n\n'
        'Dot: median over splits\nLine: 10th–90th percentiles\n\n'
        'Real–real: |R1 − R2|\nG: mean of |G−R1|, |G−R2|\n\n'
        'Descriptive ranges, not CIs\nNo pass or equivalence test',
        va='top', fontsize=10, linespacing=1.3)
    fig.suptitle('Scientific-analysis discrepancies beside real-sample variation', fontsize=19, x=.055, ha='left')
    fig.text(.055, .918, 'A: HbA1c ~ BMI + age + female     B: HbA1c ~ BMI + glucose + age + female', fontsize=11, color='#444d57')
    fig.text(.055, .022, 'One exposed CHNS sample; fixed generated draws. Finite-frame dependence differs between comparisons. These are not independent-cohort validations.', fontsize=10, color='#444d57')
    fig.subplots_adjust(left=.1, right=.98, top=.83, bottom=.15, wspace=.65, hspace=.75)
    matplotlib.rcParams['svg.hashsalt'] = 'real-real-calibration-2026-11-04'
    for suffix in ['svg','png']:
        fig.savefig(HERE/f'REAL_REAL_CONTEXT.{suffix}', dpi=170, facecolor='white', bbox_inches='tight')
    plt.close(fig)
    rows = ['# Complete descriptive comparison', '',
        'Every cell is median [10th, 90th percentile] across the 100 prescribed splits, in the metric’s original units. These ranges are not confidence intervals. Each G is one frozen table from the same law.', '',
        'Real–real is |R1−R2|. The symmetric G discrepancy is (|G−R1|+|G−R2|)/2. Matching row count does not make these distributions exchangeable; no threshold or overall success score is used.', '',
        '| Metric | Real–real absolute | '+' | '.join('G '+g+' symmetric absolute' for g in labels)+' |',
        '| --- | --- | '+' | '.join('---' for _ in labels)+' |']
    for key in report['design']['metric_names']:
        item = report['summary'][key]
        rows.append('| '+key+' | '+fmt(item['real_real']['absolute'])+' | '+
                    ' | '.join(fmt(item['generated'][g]['sym_abs']) for g in labels)+' |')
    rows += ['', 'Signed and matched-R2 differences, all raw split-level statistics and availability counts are retained in REPORT.json. Intercepts correspond to covariate-zero values outside the age-restricted target and are reported for completeness.', '']
    (HERE/'COMPLETE_METRIC_TABLE.md').write_text('\n'.join(rows), encoding='utf-8')
    print(json.dumps({'report_sha256': hashlib.sha256((HERE/'REPORT.json').read_bytes()).hexdigest(),
                      'metrics': len(report['summary']), 'core_panels': len(CORE)}))

if __name__ == '__main__':
    main()
