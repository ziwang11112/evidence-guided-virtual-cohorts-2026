"""Plot precomputed C5 scalar endpoints; never load or execute a generator."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
data = json.loads((root / 'evaluation/evaluation.json').read_text(encoding='utf-8'))
fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.2), layout='constrained')
metrics = [('A2_slope_x1', 'Adjusted x1 slope', 'u3 / u1'),
           ('A2_slope_x2', 'Adjusted x2 slope', 'u3 / u2'),
           ('A3_residual_variance', 'Conditional residual variance', 'u3 squared')]
for ax, (key, title, unit) in zip(axes, metrics):
    ref = data['runs']['joint_r1']['analysis']['endpoints'][key]['analytical_reference']
    ax.axvline(ref, color='#68717a', lw=1.4, ls='--', label='Exact artificial population')
    for arm, center, color in [('joint', 1, '#286a9e'), ('extended', 0, '#b25f30')]:
        for i, offset in enumerate([-0.11, 0, 0.11], 1):
            value = data['runs'][f'{arm}_r{i}']['analysis']['endpoints'][key]['estimate']
            ax.scatter(value, center + offset, color=color, s=46, zorder=3)
    ax.set_yticks([0, 1], ['Extension', 'Joint'])
    ax.set_ylim(-0.4, 1.4)
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(unit)
    ax.grid(axis='x', alpha=0.15)
    ax.spines[['top', 'right']].set_visible(False)
fig.suptitle('C5 artificial implementation check: all six final draws', fontsize=14)
fig.supxlabel('Each dot: one fixed 2,000-row draw. Dashed line: exact invented reference. No superiority test.', fontsize=10)
folder = root / 'assets'
folder.mkdir(exist_ok=True)
fig.savefig(folder / 'analysis_routes.png', dpi=160)
fig.savefig(folder / 'analysis_routes.svg')
plt.close(fig)
