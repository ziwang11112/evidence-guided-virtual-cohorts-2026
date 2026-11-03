"""Bind observed feedback and retain the scientific model without row execution."""
import hashlib
import json
from pathlib import Path

here=Path(__file__).resolve().parent
prior=here.parent/'delivery_initial'
root=here.parents[2]
feedback_path=root/'session'/'feedback'/'initial.json'
copy_names=['generator.py','model_spec.json','evidence.json','derive_parameters.py',
 'assemble_candidate.py','derived_parameters.json','analytic_report.json','static_report.json',
 'trial4201_feedback.json','trial_assessment.json','promote_after_trial.py']
for name in copy_names:
    (here/name).write_bytes((prior/name).read_bytes())
(here/'initial_delivery_feedback.json').write_bytes(feedback_path.read_bytes())
def read(path):
    return json.loads(path.read_text(encoding='utf-8'))
def write(path,obj):
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
feedback=read(feedback_path)
trial=read(here/'trial4201_feedback.json')
prior_assessment=read(here/'trial_assessment.json')
model={r['id']:r['model_distribution_functional'] for r in prior_assessment['comparisons']}
rows_by_id={}
run_reports=[]
for run in feedback['runs']:
    assert run['status']=='success'
    sf=run['semantic_feedback_v1']
    af=run['analysis_feedback']
    assert sf['output_link_verified'] and sf['n_computable']==30 and sf['n_not_computable']==1
    assert af['n']==3000
    assert len(sf['checks'])==31
    semantic_changes=[]
    for item,trial_item in zip(sf['checks'],trial['semantic_feedback_v1']['checks']):
        for key in ['id','evidence_id','semantics','semantic_status','source_id','declared_status',
                    'status','operator','reason','assumption_ids','reported_value','reported_uncertainty',
                    'estimator_uncertainty','individual_dispersion','unresolved_source_uncertainty',
                    'monte_carlo_uncertainty','difference_interpretation']:
            if item.get(key)!=trial_item.get(key):
                semantic_changes.append({'check_id':item['id'],'key':key,'old':trial_item.get(key),'new':item.get(key)})
    rows=af['analyses']+af['diagnostics']
    assert len(rows)==30
    for row in rows:
        mid=row['id']
        rows_by_id.setdefault(mid,{'id':mid,'reference':row['reference'],
            'model_distribution_functional':model[mid],
            'model_minus_reference':model[mid]-row['reference'],'runs':[]})
        rows_by_id[mid]['runs'].append({'seed':run['seed'],'value':row['value'],
            'difference_from_reference':row['difference'],'difference_from_model':row['value']-model[mid]})
    run_reports.append({'seed':run['seed'],'run_id':run['run_id'],'status':run['status'],
         'n':af['n'],'n_computable':sf['n_computable'],'n_not_computable':sf['n_not_computable'],
         'output_link_verified':sf['output_link_verified'],'quality':af['quality'],
         'semantic_changes_from_trial':semantic_changes,
         'execution_sha256':run['execution_sha256'],'generated_table_sha256':run['generated_table_sha256']})
for row in rows_by_id.values():
    values=[r['value'] for r in row['runs']]
    row['three_seed_mean']=sum(values)/len(values)
    row['three_seed_min']=min(values)
    row['three_seed_max']=max(values)
    row['interpretation']='Conditional descriptive seed variation, not an independent validation sample, reference uncertainty, or calibrated Monte Carlo interval. Sample SD and finite-sample quantiles are not necessarily unbiased for their model functionals.'
assert len(rows_by_id)==30
identity={name:(here/name).read_bytes()==(prior/name).read_bytes()
          for name in ['generator.py','model_spec.json','evidence.json']}
assert all(identity.values())
report={'decision':'retain','runs_reviewed':run_reports,'all_30_statistics_each_seed_reviewed':True,
 'scientific_byte_identity_to_initial':identity,
 'comparisons':list(rows_by_id.values()),
 'basis':'The specified family approximations were identified analytically before trial feedback. Coefficients and association population functionals match the declared sample estimates by construction. Three fixed-seed outputs show varying conditional estimates, with no execution failure or reported semantic mismatch. Retention avoids compensating particular seeds or reference interval crossings.',
 'not_claimed':['Population law recovered','Source-population replay','Clinical or causal validation',
                'Reference intervals are synthetic pass/fail limits','Three seeds estimate structural uncertainty'],
 'final_schedule':[4101,4102,4103],
 'same_seed_expectation':'Unchanged generator and model imply the final fixed-seed tables should reproduce the initial tables. Such repetition is reproducibility only, not new independent evidence.'}
write(here/'initial_feedback_assessment.json',report)
decision={'reason':'Retain the scientific model after all 30 statistics in each of the three fixed-seed initial deliveries. The original deterministic model calculations already separate small chosen-family offsets from realized finite-draw discrepancy. No failure or new admitted evidence identifies a superior dependence law. Do not retune toward selected seeds, reference intervals, or p-values; retain an explicitly assumption-dependent descriptive cohort.',
 'kind':'retain',
 'addressed_findings':[
  'Three isolated deliveries each succeeded with 3000 rows, 30 computed statistics, no nonpositive glycemia, no duplicate measurement rows and one explicitly noncomputable external source replay.',
  'All 90 delivery values were reviewed and bound with per-statistic reference, distribution-functional, realized discrepancy, and descriptive range.',
  'E1 ranged 0.0489324 to 0.0555719; E2 ranged 0.384047 to 0.449196; E3 ranged 0.00655560 to 0.00869015. The supplied reference CR1 intervals are retained as reference-estimator uncertainty and are not acceptance gates for synthetic draws.',
  'Pearson ranged 0.622975 to 0.685662 and Spearman 0.340120 to 0.376592. No population correlation shift is inferred from those three conditional draws.',
  'Known model approximation remains explicit: glucose q90 about -0.0774 from reference; BMI q90 about +0.0759; glucose and HbA1c means about +0.0150 and +0.0138.',
  'Generator, model_spec and evidence are retained byte-for-byte in a new final candidate. Actual trial and initial delivery feedback are hashed check artifacts. No revision trial, literature retrieval, or local row generation was used.'
 ],
 'remaining_limitations':[
  'The CHNS inputs are selected-sample development summaries, not population truth or independent validation; their unreported marginal estimation uncertainty is not reconstructed.',
  'Gaussian copulas, latent component independence, female independence, two assumed predictor correlations, continuous biomarker precision and mixture tail behavior remain underidentified modeling choices.',
  'Latent classes are mathematical distribution components, not diagnosed or treated diabetes groups; their probabilities are not prevalence estimates.',
  'Clinical thresholds, individual predictions, causal conclusions, sex effects, geographic clustering, survey representativeness, missingness mechanisms, measurement equivalence and transport are unassessed.',
  'External studies retain their populations, specimens, weights and adjustment context. No external source-population replay or pooled empirical constraint has been computed.',
  'Repeating fixed seeds on an unchanged final model checks reproducibility only. Three seed draws and finite model moments do not calibrate evidence, transport or structural uncertainty.'
 ]}
write(root/'FINAL_AUTHOR_DECISION.json',decision)
text=(prior/'decision.md').read_text(encoding='utf-8')
text=text.replace('Initial delivery request: freeze this new candidate and execute fixed seeds 4101, 4102 and 4103.',
 'Final delivery request: freeze this new retained candidate and execute fixed seeds 4101, 4102 and 4103.')
text+='''\n\n## Final decision after initial delivery: retain\n\nAll 30 statistics for each seed 4101, 4102 and 4103 were reviewed. The full initial feedback and the assessment of all 90 values are bound. The generator, model specification and evidence remain byte-identical to initial delivery. No final-phase trial is requested.\n\nE1 ranged 0.0489324–0.0555719, E2 0.384047–0.449196 and E3 0.00655560–0.00869015. Pearson ranged 0.622975–0.685662; Spearman 0.340120–0.376592. These are conditional realized ranges, not a Monte Carlo confidence interval. In particular, the E2 value 0.449196 above the reference interval is not treated as a failed generator or a tuning target. The reference interval estimates uncertainty in its original clustered sample, with a different sample size and sampling process.\n\nThe distributions retain known offsets, including glucose q90 about 0.0774 below reference and BMI q90 about 0.0759 above it. These are structural approximation, not seed noise. Other discrepancies relative to the pre-existing model functionals are realized finite-draw effects, with no claim that three seeds precisely estimate their distribution. No substantive evidence supports adding complexity to remove small fitted-summary residuals or shifting the model to offset these particular seeds.\n\nThe final fixed seeds should reproduce the initial tables because the scientific bytes have not changed. That is reproducibility, not a new independent validation or an improvement. Root FINAL_AUTHOR_DECISION.json records retain, findings addressed and the remaining limits.\n'''
(here/'decision.md').write_text(text,encoding='utf-8')
checks=read(prior/'checks.json')
checks['records']=[r for r in checks['records'] if r['name']!='delivery_schedule']
checks['records'].extend([
 {'name':'initial_delivery_integrity_and_coverage','status':'pass','detail':'Bound initial feedback reports three successful linked executions, 3000 rows each, all 30 statistics computable and source replay not computable. All 90 values reviewed; comparisons preserved in initial_feedback_assessment.json.'},
 {'name':'final_scientific_retention','status':'pass','detail':'Byte comparison confirms unchanged generator.py, model_spec.json and evidence.json relative to initial delivery. No model adjustment is made from fixed-seed estimates or reference interval crossings.'},
 {'name':'final_execution','status':'not_computable','detail':'Final seed4101/4102/4103 execution is requested but has not occurred for this final candidate. Expected repetition of identical initial tables is not new scientific evidence.'}])
checks['artifacts']=[{'path':f,'sha256':hashlib.sha256((here/f).read_bytes()).hexdigest()}
 for f in ['analytic_report.json','static_report.json','trial4201_feedback.json','trial_assessment.json',
           'initial_delivery_feedback.json','initial_feedback_assessment.json']]
write(here/'checks.json',checks)
print(json.dumps({'candidate':'delivery_final','decision':'retain','scientific_byte_identity':identity,
                  'reviewed_statistics':90,'semantic_changes':[r['semantic_changes_from_trial'] for r in run_reports]},indent=2))
