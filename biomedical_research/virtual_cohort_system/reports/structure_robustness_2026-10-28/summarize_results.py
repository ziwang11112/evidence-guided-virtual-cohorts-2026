"""Summarize every committed endpoint; plot the two primary plus raw curvature.

Consumes only released aggregate results. No generator changes or new fits.
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / 'custodian/evaluation'
OUT = ROOT / 'summaries'

def main():
    OUT.mkdir(exist_ok=False)
    frame = pd.read_csv(RESULTS / 'endpoint_comparison.csv')
    reference = json.loads((RESULTS / 'reference_analyses.json').read_text())
    protocol = json.loads((ROOT / 'protocol.json').read_text())
    rows = []
    for (scale, endpoint, structure), g in frame.groupby(['measurement_scale', 'endpoint', 'structure'], sort=True):
        ref = reference[scale][endpoint]
        rows.append({'measurement_scale': scale, 'endpoint': endpoint, 'structure': structure,
            'n_draws': len(g), 'expected_draws': len(protocol['target_seeds']),
            'reference': ref['estimate'], 'reference_ci_low': ref['ci_low'], 'reference_ci_high': ref['ci_high'],
            'reference_ci_direction': ref['ci_direction'], 'median': float(g.estimate.median()),
            'minimum': float(g.estimate.min()), 'maximum': float(g.estimate.max()),
            'point_direction_agreement_count': int(g.point_direction_agrees.sum()),
            'median_absolute_error': float(g.absolute_error.median())})
    pd.DataFrame(rows).to_csv(OUT / 'structure_summary.csv', index=False)
    (OUT / 'structure_summary.json').write_text(json.dumps(rows, indent=2, allow_nan=False) + '\n')

    panels = [('adjusted_age_per10', 'Adjusted age association', 'log TG per 10 years'),
              ('bmi_curvature_second_difference', 'BMI curvature on log scale', 'Global quadratic contrast (log TG)'),
              ('raw_bmi_curvature_second_difference', 'BMI curvature on raw scale', 'Global quadratic contrast (mg/dL)')]
    colors = ['#2766A8', '#A35D19', '#27836C']
    labels = ['Reference (95% CI)', 'S1 additive mean', 'S2 multiplicative', 'S3 mixture (source-limited)']
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4), constrained_layout=True)
    for ax, (endpoint, title, unit) in zip(axes, panels):
        ref = reference['native'][endpoint]
        ax.axvline(0, color='#CBD2D9', lw=1, linestyle='--', zorder=0)
        ax.errorbar(ref['estimate'], 3, xerr=[[ref['estimate'] - ref['ci_low']],
                                             [ref['ci_high'] - ref['estimate']]],
                    fmt='D', color='#172B4D', capsize=4, markersize=5)
        for index, structure in enumerate(protocol['structures']):
            values = frame.loc[(frame.measurement_scale == 'native') &
                               (frame.endpoint == endpoint) & (frame.structure == structure)].sort_values('seed').estimate
            y = 2 - index
            ax.plot([values.min(), values.max()], [y, y], color=colors[index], lw=2, alpha=.45)
            ax.scatter(values, y + np.linspace(-.10, .10, len(values)), color=colors[index], s=22)
            ax.scatter([values.median()], [y], color=colors[index], marker='|', s=145, linewidths=2)
        ax.set_yticks([3, 2, 1, 0], labels, fontsize=9)
        ax.set_ylim(-.4, 3.5)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlabel(unit, fontsize=9)
        ax.grid(axis='x', alpha=.15)
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('New-period TG validation: frozen structural alternatives', fontsize=14, fontweight='bold')
    fig.supxlabel('NHANES 2021–2023, n = 2,660. Five dots per structure are simulation draws; colored ranges are not confidence intervals.\nAll three share source-informed assumptions; source-fit limitations are retained in the report.', fontsize=9)
    fig.savefig(OUT / 'structural_robustness.png', dpi=180)
    fig.savefig(OUT / 'structural_robustness.pdf')
    plt.close(fig)
    print(json.dumps({'summaries': len(rows), 'aggregate_rows': len(frame), 'directory': str(OUT)}))

if __name__ == '__main__':
    main()
