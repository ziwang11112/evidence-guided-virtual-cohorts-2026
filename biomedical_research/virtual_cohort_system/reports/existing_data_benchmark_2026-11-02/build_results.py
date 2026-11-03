"""Present all sealed results; does not generate, fit or select a model."""
from pathlib import Path
import hashlib
import json
import statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
release = json.loads((HERE / 'RELEASE.json').read_text(encoding='utf-8'))
report_path = Path(release['bundle_root']) / 'benchmark_control/evaluation/REPORT.json'
report = json.loads(report_path.read_text(encoding='utf-8'))
verification = json.loads((HERE / 'INDEPENDENT_RECOMPUTATION.json').read_text(encoding='utf-8'))
assert verification['status'] == 'passed'
assert verification['report_sha256'] == hashlib.sha256(report_path.read_bytes()).hexdigest()
ids = [f'{arm}_A{i:02d}' for arm in ('E0', 'E1') for i in range(1, 6)]
tail_flags = ['E0_A01', 'E0_A03', 'E0_A04', 'E1_A01', 'E1_A02', 'E1_A03', 'E1_A04']
names = {'E1': 'BMI association', 'E2': 'Glucose association', 'E3': 'Jointly adjusted age association'}
units = {'E1': 'HbA1c percentage points per kg/m²', 'E2': 'HbA1c percentage points per mmol/L', 'E3': 'HbA1c percentage points per year'}

public = {
    'kind': 'completed_existing_CHNS_information_benchmark',
    'scope': 'Historically exposed CHNS benchmark; not untouched confirmation, clinical equivalence or population recovery.',
    'information': {'E0': '15 grouped marginal records and three source contexts plus unit guidance',
                    'E1': 'Same base plus four qualified relationship records'},
    'counts': {'fresh_context_constructors': 10, 'constructors_per_arm': 5, 'seeds_per_constructor': 3,
               'generated_tables': 30, 'rows_per_table': 3000, 'generated_rows': 90000,
               'measured_reference_records': 6631, 'measured_reference_communities': 218,
               'focal_coefficient_results': 90, 'execution_failures': 0, 'technical_correction_returns': 0,
               'scientific_revisions': 0, 'new_download_bytes': 0, 'patient_reference_rows_redecoded': 0},
    'cost': {'new_paid_API': False, 'training': False, 'HPC': False,
             'LLM_token_and_dollar_meter': 'not exposed; no invented cost estimate'},
    'reference': report['reference'], 'endpoints': report['endpoints'],
    'complete_arms': report['complete_arms_all_three_endpoints'],
    'both_addressed_projections_improve': report['both_addressed_projections_improve'],
    'postconstruction_tail_flags': tail_flags,
    'tail_flag_scope': 'Mathematical unbounded-support population-moment defect; not a finite-table runtime failure or a revised primary exclusion.',
    'verification': {'checks': verification['checks'], 'mismatches': len(verification['failures']),
                     'primary_report_sha256': verification['report_sha256'],
                     'independent_receipt_sha256': hashlib.sha256((HERE / 'INDEPENDENT_RECOMPUTATION.json').read_bytes()).hexdigest()},
    'slots': [{k: s[k] for k in ('constructor', 'seed', 'status', 'analysis', 'comparison')} for s in report['slots']],
}
(HERE / 'PUBLIC_RESULTS.json').write_text(json.dumps(public, indent=2) + '\n', encoding='utf-8')

fig, axes = plt.subplots(1, 3, figsize=(13.3, 6.5), sharey=True)
colors = {'E0': '#2666A6', 'E1': '#C35A20'}
for ax, endpoint in zip(axes, ('E1', 'E2', 'E3')):
    ref = report['reference']['estimands'][endpoint]
    interval = ref['interval']
    ax.axvspan(interval['lower'], interval['upper'], color='#CBD3DD', alpha=.48, zorder=0)
    ax.axvline(ref['coefficient'], color='#263746', linestyle='--', linewidth=1.25, zorder=1)
    for index, identifier in enumerate(ids):
        values = [s['analysis']['estimands'][endpoint]['coefficient'] for s in report['slots'] if s['constructor'] == identifier]
        ax.scatter(values, [index - .13, index, index + .13], s=25, color=colors[identifier[:2]], alpha=.78)
        ax.scatter([statistics.mean(values)], [index], marker='|', s=170, color='#182B39', linewidth=1.4)
    ax.axhline(4.5, color='#D9DFE7', linewidth=1)
    ax.set_title(names[endpoint], loc='left', fontsize=12, fontweight='bold')
    ax.set_xlabel(units[endpoint], fontsize=9)
    ax.grid(axis='x', alpha=.18)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=9)
axes[0].set_yticks(range(10), [i + (' *' if i in tail_flags else '') for i in ids])
axes[0].invert_yaxis()
fig.suptitle('All 10 Agent constructions: three fixed draws each', x=.08, ha='left', fontsize=16, fontweight='bold')
fig.legend(handles=[Line2D([0], [0], marker='o', color='w', markerfacecolor=colors[a], label=a + ('  Marginals' if a == 'E0' else '  Marginals + relations')) for a in ('E0', 'E1')]
           + [Line2D([0], [0], color='#263746', linestyle='--', label='Measured CHNS estimate')],
           loc='upper left', bbox_to_anchor=(.075, .935), ncol=3, frameon=False, fontsize=10)
fig.text(.08, .085, 'Dots: fixed seeds; short ticks: constructor means. Shading: existing clustered reference interval, not an acceptance margin.', fontsize=9)
fig.text(.08, .045, '* Post-construction audit: nested exponential tail has non-finite population moments. All finite-table results remain included.', fontsize=9)
fig.subplots_adjust(left=.10, right=.98, top=.82, bottom=.19, wspace=.30)
(HERE / 'figures').mkdir(exist_ok=True)
fig.savefig(HERE / 'figures/all_constructors.png', dpi=160)
fig.savefig(HERE / 'figures/all_constructors.svg')
plt.close(fig)

lines = ['# CHNS existing-data information experiment: completed results', '',
'**A partial glucose-analysis gain was observed, but the prespecified overall improvement condition failed.** All 30 frozen target draws completed and all 90 focal coefficients were independently recomputed. A separate static audit identified a serious population-tail defect in seven generated laws. No model was repaired, replaced or excluded after results were seen.', '',
'## What actually ran', '',
'Ten fresh-context scientific Agent constructors authored executable whole-cohort laws, five per arm. They received no participant observations and no CHNS numerical results. E0 contained three source contexts and 15 grouped marginal records. E1 added four reviewed relationships to that identical base: two separate Jansen adjusted projections, Bao Pearson and MIND Spearman. Both arms received the same target task, unit guidance and interface. Each author chose its own structure, parameters and assumptions.', '',
'Each frozen law generated 3,000 rows at seeds 1701, 1702 and 1703 in the existing isolated runtime: **30 tables and 90,000 virtual rows**. These are Monte Carlo draws from ten constructions, not 30 independent clinical cohorts. There were zero technical correction returns, zero execution failures, zero scientific revisions and no new downloads, patient-reference redecoding, training, HPC or new paid API. Model-version/temperature and LLM token/dollar metering were not exposed by the authoring API.', '',
'All outputs closed before the new comparison. CHNS was already exposed to the researchers and was selected with historical results known. Its existing measured-reference analysis includes 6,631 eligible records and 218 communities. These are sample estimates with uncertainty, not known population truths. Fresh author contexts and procedural access restrictions do not erase coordinator exposure or a model\'s possible pretrained biomedical knowledge.', '',
'## Prespecified scientific comparisons', '',
'Every regression includes an intercept. The BMI and glucose analyses adjust age and female category separately; the age analysis jointly adjusts female category, BMI and glucose. The summary is **mean absolute discrepancy across the three seeds within each constructor, then the mean over five constructors per arm**. It is not absolute error after averaging signed estimates.', '',
'| Analysis | Measured reference | E0 mean absolute discrepancy | E1 mean absolute discrepancy | E1 − E0 |',
'|---|---:|---:|---:|---:|']
for endpoint in ('E1', 'E2', 'E3'):
    x = report['endpoints'][endpoint]
    lines.append(f"| {names[endpoint]} | {x['reference_point']:.6f} | {x['arm_mean_absolute_discrepancy']['E0']:.6f} | {x['arm_mean_absolute_discrepancy']['E1']:.6f} | {x['E1_minus_E0']:+.6f} |")
lines += ['', 'Units are HbA1c percentage points per kg/m², per mmol/L and per year, respectively. Lower discrepancy is better. Glucose discrepancy fell **74.3%**; BMI discrepancy rose **10.7%** and age discrepancy rose **19.8%**. Both addressed projections had to improve; that fixed condition is **false**. The same contrast directions hold at both endpoints of each existing reference interval. This endpoint sensitivity does not establish robustness throughout an interval, equivalence or generalization.', '',
'All 90 finite-table slopes are positive, matching the measured-reference directions. The authors also explicitly assumed positive physiological dependencies, so direction agreement alone is weak evidence of new joint recovery. For glucose, 12/15 E1 estimates lie inside the existing reference interval, versus 0/15 E0; for BMI the counts are 0/15 in both arms; for age they are 2/15 and 3/15. These descriptive interval memberships are not equivalence tests or calibrated synthetic uncertainty.', '',
'![Every construction and seed](figures/all_constructors.svg)', '',
'## What the implementation audit found', '',
'The Agent made substantive scientific generation choices: demographic distributions, BMI response, latent glycemia, mixture frequency, residual dependence and tails. The coordinator did not install desired slopes. However, the additional evidence usually influenced narrative and qualitative structure rather than numerically constraining source analyses. The independent, outcome-blind audit found **19/20 author-by-relationship uses qualitative-only**. E1_A01 used MIND 0.529 through an assumed copula conversion and attenuation, then reassigned it to conditional log residuals; this did not enforce the reported marginal Spearman relationship. None of the five E1 models numerically enforced either Jansen adjusted projection.', '',
'All ten constructions use variants of a demographic/BMI hierarchy with a shared glycemic mixture or tail. There are genuine differences in age laws, saturated versus raw/log BMI predictors, and additive versus multiplicative gamma/lognormal tails, but this is limited structural diversity. E0 also has pretrained biomedical priors and explicitly assumed positive dependencies. Thus the experiment describes the effect of supplying the extra records in this bounded authoring procedure; it does not isolate exact numerical evidence fitting or prove broad superiority over a conventional generator.', '',
'### A concrete scientific generator defect', '',
'Seven frozen laws generate nondegenerate, unbounded lognormal BMI and then exponentiate a strictly positive linear function of raw BMI for glucose and HbA1c. For such B, E[exp(cB)] diverges for every c>0. Consequently these declared population laws do not have the ordinary finite biomarker moments required for population-moment and OLS interpretations. The affected laws are E0_A01/A03/A04 and E1_A01/A02/A03/A04.', '',
'This was discovered by static code/specification audit after construction and independently confirmed. It is a mathematical tail defect, **not an observed overflow or failure of finite-table least squares**. The three 3,000-row draws per law did not reveal it through runtime checks. E0_A02\'s bounded tanh driver and E0_A05/E1_A05\'s log-BMI drivers avoid this particular defect; that does not independently validate those three models. All ten remain in the original denominator. No survivor-only analysis or revised success rule is substituted.', '',
'Other prespecified diagnostics reinforce the distinction between selected-analysis agreement and full joint fidelity: the measured HbA1c sample SD is 0.954 percentage points, while the E1 finite-table SDs range from 0.561 to 0.861. Measured glucose/HbA1c Spearman is 0.361; E1 values range from 0.499 to 0.585. A close adjusted glucose slope therefore does not establish recovery of the joint distribution. These sample summaries have their own uncertainty; their discrepancies are not automatically population biases.', '',
'## Verification and decision', '',
f"Independent CSV parsing and QR solves reproduced all 90 focal coefficients and the per-seed, constructor, arm and reference-endpoint arithmetic: **{verification['checks']} checks, zero mismatches**, with no generator reruns and no patient-row reads. The primary immutable report's initial verification-pending field is superseded by the separate bound [verification receipt](INDEPENDENT_RECOMPUTATION.json) and [review](RESULTS_REVIEW.md). [All aggregate results](PUBLIC_RESULTS.json) retain every constructor, seed and diagnostic. [The construction audit](CONSTRUCTION_EVIDENCE_AUDIT.md) records evidence use and tail mathematics.", '',
'**Continue focused method development; do not freeze the current scientific generator strategy for a manuscript.** The useful finding is a sizeable, bounded glucose-analysis gain together with precise reasons the broader claim is not yet supported. The next framework change should require the Agent to distinguish numerical source constraints from qualitative context and unsupported assumptions, and should check whether the chosen distributional composition admits the moments required by the intended analyses. Appropriate source-statistic feedback must replay the source population/measurement/operator, not quietly calibrate to the already revealed CHNS target.', '',
'No additional dataset or larger virtual n is the next bottleneck. Do not run more copies of this frozen design or hand-adjust BMI/age coefficients to the known CHNS results. A separately frozen developmental comparison can test one source-evidence/analytic-validity revision on existing data, preserve both gains and trade-offs, and then assess reuse under unchanged rules in another already available benchmark. This report does not authorize or start that next experiment.']
(HERE / 'RESULTS.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(json.dumps({'results': str(HERE / 'RESULTS.md'), 'figure': str(HERE / 'figures/all_constructors.png'), 'primary_gate': report['both_addressed_projections_improve']}))
