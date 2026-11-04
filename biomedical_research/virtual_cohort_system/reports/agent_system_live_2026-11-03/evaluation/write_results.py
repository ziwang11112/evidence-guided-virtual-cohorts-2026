"""Render aggregate results already computed after closure; no participant reads."""
import csv,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
r=json.loads((H/'REPORT.json').read_text(encoding='utf-8'))
def fmt(x):return f'{x:.5f}'
def ran(values):return f'{fmt(min(values))} to {fmt(max(values))}'
def selected(key):return [s for s in r['slots'] if s['request']==key and s['stage']=='initial']
lines=['# Live Agent integration: two research requests', '',
'The bounded live integration produced scientifically analyzable whole-cohort data for both requests. It demonstrated some useful relationships, but the glucose-adjusted BMI relationship in request B did not match the real reference. Both authors retained their initial models after feedback, so this run provides no evidence of post-feedback revision benefit.', '',
'This is a developmental comparison against the previously exposed CHNS 2009 selected sample: 6,631 complete cases, ages 35–74, and 218 communities. It is not a new untouched confirmation, a nationally representative estimate or known population truth. The generator authors did not receive target outcome values or results. Both authors closed before the evaluator read the reference.', '',
'## Actual work and counts', '',
'- Two fresh authors retrieved the approved original literature, extracted evidence, authored distinct stochastic programs and parameter specifications, received generated-only diagnostics and semantic source-check statuses, and explicitly chose retention.',
'- Eight physical executions succeeded: one trial and three delivery seeds per request. Each output has 3,000 rows; 24,000 physical synthetic rows include trials. The six unique delivery tables contain 18,000 rows. Six final-stage records alias those same tables and are not additional samples.',
'- All 12 initial/final evaluation slots are preserved. Seeds are 7301, 7302 and 7303; the two trials use 7300. No revision-trial or new final-generation run was needed.',
'- The v1 feedback interface ran, but all nine A and eight B declared source checks were unavailable. A completed feedback artifact is not a successful source replay or numeric calibration.', '',
'## All model coefficients', '',
'A: HbA1c ~ intercept + BMI + age + female. B adds serum glucose. Units are HbA1c percentage points per predictor unit (BMI kg/m²; glucose mmol/L; age years; female 0/1). The reference interval is community-cluster CR1-t 95%. Generated ranges span the three fixed seeds and are not confidence intervals.', '',
'| Request | Term | Reference estimate [95% CI] | Generated point-estimate range | Generated conditional interval directions |',
'|---|---|---:|---:|---|']
for key in ('A','B'):
    slots=selected(key)
    for term,ref in r['reference'][key]['coefficients'].items():
        gen=[s['analysis']['coefficients'][term] for s in slots]
        lines.append(f"| {key} | {term} | {fmt(ref['value'])} [{fmt(ref['lower'])}, {fmt(ref['upper'])}] | {ran([g['value'] for g in gen])} | "+', '.join(g['interval_direction'] for g in gen)+' |')
lines += ['', 'Final estimates are byte-identical to initial estimates because both final decisions retain the same frozen candidates and output files. There is no before/after improvement to infer.', '',
'Generated HC3-t intervals condition on each model and synthetic draw. They exclude source, parameter, transport and model uncertainty. Their overlap with a reference interval is not an equivalence test.', '',
'## Scientific interpretation', '',
'Request A recovers positive BMI and age associations. Its BMI association is weaker than the reference estimate across all three seeds. Its age estimates are on a similar scale to the reference. Female point estimates are negative, but all three generated conditional intervals include zero, whereas the selected real sample has a narrowly negative interval.', '',
'Request B reproduces a strong positive glucose association of roughly the reference scale. Its primary, glucose-adjusted BMI coefficient is negative in all three draws, whereas the reference coefficient is positive with a positive interval. Only one generated BMI interval is entirely negative; the other two cross zero. Its age coefficient is positive but appreciably smaller than the reference. The reference female interval includes zero, so its positive point estimate is not evidence of an established positive female effect.', '',
'The important limitation is joint structure: positive marginal BMI–HbA1c association and a realistic glucose–HbA1c association do not determine the BMI coefficient after glucose adjustment. This is an algebraic property of the requested multivariable analysis, not a new post-hoc endpoint. The sources did not identify the needed conditional slopes, and the authors marked them as assumptions.', '',
'## Marginal distributions', '',
'These are descriptive checks, not targets imposed on the authors or proof that a real sample mean equals a population mean.', '',
'| Request | Variable | Summary | Reference | Generated range |', '|---|---|---|---:|---:|']
for key in ('A','B'):
    for variable,ref in r['reference'][key]['marginal'].items():
        for stat in ('mean','sd','q10','median','q90'):
            vals=[s['analysis']['marginal'][variable][stat] for s in selected(key)]
            lines.append(f'| {key} | {variable} | {stat} | {fmt(ref[stat])} | {ran(vals)} |')
lines += ['', 'A has a somewhat higher HbA1c mean but similar individual dispersion. B has a higher BMI distribution and somewhat lower HbA1c dispersion. Its serum-glucose mean and median are near the sample reference, while its upper quantile is higher. Both use a chosen uniform age composition, which differs from the selected sample composition.', '',
'## Joint relationships', '',
'| Request | Pair | Statistic | Reference | Generated range |', '|---|---|---|---:|---:|']
for key in ('A','B'):
    for pair,ref in r['reference'][key]['relationships'].items():
        for stat in ('pearson','spearman'):
            vals=[s['analysis']['relationships'][pair][stat] for s in selected(key)]
            lines.append(f'| {key} | {pair} | {stat} | {fmt(ref[stat])} | {ran(vals)} |')
lines += ['', 'B shows close Pearson glucose–HbA1c correlation but higher rank correlation than the reference. This difference reinforces that one matching correlation does not establish the whole joint distribution.', '',
'## Verification and implementation findings', '',
'- The closure gate verified both decisions, initial/final lineage, all charged attempts, execution receipts, source bindings, table hashes and fixed seeds before the exclusive reference read receipt.',
'- The four CHNS input hashes and original fixed selection were preserved. A separate linkage order and BMI/eligibility calculation reproduced the selected records. No target-guided recoding, exclusion or parameter change occurred.',
'- Independent QR regression and covariance calculations verified all reference and generated coefficients, standard errors and interval endpoints; independent NumPy/rank expressions verified the marginal and pairwise diagnostics. Maximum reference discrepancy was below 5.3e-14. Existing E1 and E3 helper calculations also agreed.',
'- Root review found a pre-freeze divergent-moment risk in B: positive exp(k×lognormal BMI) terms. The author preserved the original draft and replaced those BMI links with positive linear multipliers before any execution. This was a mathematical implementation repair, not a post-feedback or target-driven improvement.',
'- The original runner lacked cross-stage model-family enforcement. This was corrected before scientific execution and checked with eight isolated mocks. An initial mock failed due to a missing mocked read_json method, then passed after the mock was fixed.',
'- A broad statsmodels import was blocked by Windows Application Control. No policy bypass or installation occurred; NumPy/SciPy implementations were independently checked instead.',
'- The full Jansen original was unavailable through the approved gateway. Both authors used its original abstract only and did not represent its conditional numeric coefficients as retrieved. Two full originals were available. Precise retrieval counts and source audit are recorded in the parent run artifacts; no paid API, training, HPC or additional clinical download was used here.', '',
'## Supported conclusion and next action', '',
'The implemented Agent can retrieve original evidence, construct whole-cohort generators for two related analysis requests, produce executable data, and expose assumptions and unsupported checks. This run supports partial scientific usefulness, especially the A age relation and B glucose relation. It does not establish reliable conditional BMI recovery, automatic numerical source calibration, post-feedback improvement or robustness across independent clinical datasets.', '',
'Keep these candidates frozen and preserve the unfavorable B result. The next framework decision should address how requested conditional relationships acquire usable source constraints and a genuine source-context numerical check. A failure to compute every source check should be surfaced as an evidence-coverage limitation, not hidden behind a completed feedback status. Merely increasing synthetic row counts cannot resolve that missing identification.', '',
'Full seed-specific values, conditional intervals, failures, aliases and recomputation receipts are in `REPORT.json`. There is no pooled success score.', '']
(H/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
with (H/'COEFFICIENTS.csv').open('w',encoding='utf-8',newline='') as stream:
    writer=csv.writer(stream)
    writer.writerow(['request','stage','seed','run_id','aliased_initial','term','generated','generated_lower','generated_upper','reference','reference_lower','reference_upper'])
    for slot in r['slots']:
        for term,row in slot['analysis']['coefficients'].items():
            ref=r['reference'][slot['request']]['coefficients'][term]
            writer.writerow([slot['request'],slot['stage'],slot['seed'],slot['run_id'],slot['aliased_initial'],term,row['value'],row['lower'],row['upper'],ref['value'],ref['lower'],ref['upper']])
summary={'report_sha256':hashlib.sha256((H/'REPORT.json').read_bytes()).hexdigest(),
         'physical_attempts':8,'unique_delivery_tables':6,'retained_final_aliases':6,
         'unique_delivery_rows':18000,'all_physical_rows_including_trials':24000,
         'reference_n':r['reference']['A']['n'],'reference_communities':r['reference']['A']['cluster_count'],
         'requests':{}}
for key in ('A','B'):
    summary['requests'][key]={'decision':r['inventories'][key]['choice'],'coefficients':{}}
    for term,ref in r['reference'][key]['coefficients'].items():
        vals=[s['analysis']['coefficients'][term]['value'] for s in selected(key)]
        summary['requests'][key]['coefficients'][term]={'reference':ref['value'],'reference_ci':[ref['lower'],ref['upper']],
            'generated_seed_range':[min(vals),max(vals)]}
(H/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'results_file':str(H/'RESULTS.md'),'summary':str(H/'SUMMARY.json'),'coefficient_rows':54},indent=2))
