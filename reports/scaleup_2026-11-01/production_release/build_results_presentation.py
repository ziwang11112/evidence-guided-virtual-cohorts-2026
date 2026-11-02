"""Present the complete frozen evaluation; no participant data or new analyses."""
from pathlib import Path
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[4]
SOURCE = WORKSPACE / 'evcA/evaluation_results/PUBLISHABLE_AGGREGATES.json'
v = json.loads(SOURCE.read_text())
orders = {
    'K01': ['K01-GLUCOSE-BMI', 'K01-GLUCOSE-AGE', 'K01-SEX-BMI'],
    'K02': ['K02-HDL-BMI', 'K02-TC-BMI', 'K02-LIPID-RESIDUAL'],
}
titles = ['Glucose: adjusted BMI contrast', 'Glucose: adjusted age contrast',
          'Glucose: female-minus-male BMI contrast', 'HDL: adjusted BMI contrast',
          'Total cholesterol: adjusted BMI contrast', 'TC / HDL residual correlation']
constructors = ['A01', 'A02', 'A03', 'A04', 'A05', 'S01']
summary = {'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'scope': 'Presentation of all frozen endpoints; no new analyses or selection',
           'initial_final_identical_retained_aliases': True, 'cases': {}}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'svg.fonttype': 'none'})
fig, axes = plt.subplots(2, 3, figsize=(15, 8.4), constrained_layout=True)
for row, case in enumerate(orders):
    ref = v['references'][case]
    info = {'reference_eligible_n': ref['selection']['eligible_rows'], 'analyses': {}}
    for col, endpoint in enumerate(orders[case]):
        ax = axes[row, col]
        reference = ref['estimands'][endpoint]
        band = reference['interval']
        if band['status'] == 'available':
            ax.axvspan(band['lower'], band['upper'], color='#dbe7ed', alpha=.85, zorder=0)
        ax.axvline(reference['estimate'], color='#163f55', lw=1.5, label='Measured reference')
        ax.axvline(0, color='#8c959b', lw=.8, ls=':')
        item = {'reference_estimate': reference['estimate'], 'unit': reference['unit'],
                'reference_interval': band, 'constructors': {}}
        for y, constructor in enumerate(constructors):
            slots = [x for x in v['target_slots'] if x['case'] == case and
                     x['constructor'] == constructor and x['stage'] == 'final']
            assert len(slots) == 3
            values = [x['analysis']['estimands'][endpoint]['estimate'] for x in slots]
            errors = [x['comparison'][endpoint]['normalized_discrepancy'] for x in slots]
            agrees = sum(x['comparison'][endpoint]['direction_agrees'] for x in slots)
            item['constructors'][constructor] = {'values': values, 'seeds': [x['seed'] for x in slots],
                'min': min(values), 'max': max(values), 'max_normalized_discrepancy': max(errors),
                'direction_agreement_count': agrees, 'seed_count': 3,
                'all_seeds_within_0_10': all(e <= .1 for e in errors)}
            color = '#237b85' if constructor != 'S01' else '#9b633b'
            ax.plot([min(values), max(values)], [y, y], color=color, lw=2, zorder=2)
            ax.scatter(values, [y-.10, y, y+.10], s=21, color=color, zorder=3)
        ax.set_yticks(range(6), constructors)
        ax.invert_yaxis()
        ax.set_title(titles[row*3+col], loc='left', fontsize=10, fontweight='bold')
        ax.set_xlabel(reference['unit'])
        ax.grid(axis='x', color='#dddddd', lw=.5)
        ax.spines[['top', 'right']].set_visible(False)
        info['analyses'][endpoint] = item
    summary['cases'][case] = info
fig.suptitle('Whole-cohort generation: every constructor and all three fixed seeds', fontsize=15)
fig.supxlabel('Top: HAALSI (n=4,394); bottom: Turkana (n=397, qualified holdout). '
              'Dots / short lines: three synthetic draws, not confidence intervals.\n'
              'Dark line: measured-sample estimate; shading: HC3 working sensitivity interval '
              '(unweighted; no population or transport coverage).', fontsize=9)
out = HERE / 'figures'
out.mkdir(exist_ok=True)
fig.savefig(out/'all_scientific_analyses.svg')
fig.savefig(out/'all_scientific_analyses.png', dpi=160)
plt.close(fig)
(HERE/'PRESENTATION_SUMMARY.json').write_text(json.dumps(summary, indent=2)+'\n')
lines = ['| Case / constructor | Analysis 1: max discrepancy | Analysis 2: max discrepancy | Analysis 3: max discrepancy | All nine within 0.10 |',
         '| --- | ---: | ---: | ---: | :---: |']
for case in orders:
    for constructor in constructors:
        errors = [summary['cases'][case]['analyses'][e]['constructors'][constructor]['max_normalized_discrepancy'] for e in orders[case]]
        passed = v['aggregate']['bundles'][f'{case}:{constructor}:final']['passes']['0.1']
        lines.append(f'| {case} / {constructor} | '+ ' | '.join(f'{e:.4f}' for e in errors)+f' | {"Yes" if passed else "No"} |')
(HERE/'CONSTRUCTOR_RESULTS_TABLE.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'cases': list(summary['cases']), 'figure': str(out/'all_scientific_analyses.png')}))
