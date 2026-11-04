"""Render every prespecified nonintercept term from closed aggregate outputs."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

R = Path(__file__).resolve().parent
d = json.loads((R / 'evaluation/REPORT.json').read_text(encoding='utf-8'))
slots = [x for x in d['slots'] if x['stage'] == 'final']
assert len(slots) == 3 and all(x['status'] == 'success' for x in slots)
fig, axes = plt.subplots(2, 4, figsize=(13.8, 6.8))
labels = {'bmi': 'BMI (per kg/m²)', 'glucose': 'Glucose (per mmol/L)', 'age': 'Age (per year)', 'female': 'Female − male'}
for row, terms in enumerate([['bmi', 'glucose', 'age', 'female'], ['bmi', 'age', 'female']]):
    ref = d['reference']['B' if row == 0 else 'A']
    for col, term in enumerate(terms):
        ax = axes[row, col]
        rc = ref['coefficients'][term]
        ax.axvspan(rc['lower'], rc['upper'], color='#b9bfc8', alpha=.35)
        ax.axvline(rc['value'], color='#4a515e', lw=1.4, ls='--')
        ax.axvline(0, color='#b6bbc3', lw=.8)
        for y, slot in enumerate(slots):
            analysis = slot['analysis'] if row == 0 else slot['analysis']['descriptive_secondary']
            c = analysis['coefficients'][term]
            ax.errorbar(c['value'], y, xerr=[[c['value']-c['lower']], [c['upper']-c['value']]], fmt='o', color='#2275a8', capsize=3, ms=5, lw=1.3)
        ax.set_yticks(range(3), [str(x['seed']) for x in slots])
        ax.set_ylim(2.7, -.7)
        ax.set_title(labels[term], fontsize=10, loc='left')
        ax.set_xlabel('HbA1c percentage-point coefficient', fontsize=8)
        ax.tick_params(labelsize=8)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.spines[['right', 'top']].set_visible(False)
        if col == 0: ax.set_ylabel('Synthetic seed', fontsize=9)
axes[1, 3].axis('off')
axes[1, 3].text(0, .94, 'Gray: existing real-sample estimate\nand 95% community-cluster interval.\n\nBlue: three draws from one Agent\nmodel, with conditional HC3-t intervals.\n\nDifferent uncertainty meanings.\nNot an equivalence test or three\nindependent clinical validations.', fontsize=9, va='top', linespacing=1.5)
fig.suptitle('Scientific analysis of an evidence-guided virtual cohort versus the existing reference', fontsize=14, x=.06, ha='left')
fig.text(.06, .92, 'Primary: HbA1c ~ BMI + glucose + age + female', fontsize=10, weight='bold')
fig.text(.06, .475, 'Prespecified secondary: HbA1c ~ BMI + age + female', fontsize=10, weight='bold')
fig.subplots_adjust(left=.065, right=.985, top=.855, bottom=.085, wspace=.42, hspace=.75)
fig.savefig(R / 'ANALYSIS_UTILITY.svg', metadata={'Creator': 'Matplotlib; closed aggregate report, all terms'})
fig.savefig(R / 'ANALYSIS_UTILITY.png', dpi=160)
plt.close(fig)
print('Rendered all seven nonintercept terms from three final delivery slots; no data fitting.')
