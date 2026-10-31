"""Bind verified source-only feedback and retain the initial scientific bytes.

This script checks/copies static artifacts only. It never imports, calls or
simulates the submitted generator and never opens an individual-level table.
"""
from pathlib import Path
import copy
import hashlib
import json
import shutil

B = Path(__file__).resolve().parent
I = B / 'candidates' / 'initial'
F = B / 'candidates' / 'final'
H = B / 'controller_feedback' / 'initial'

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')

assert not F.exists(), 'Final authoring is single-use; do not overwrite a candidate.'
manifest = read(H/'FEEDBACK_MANIFEST.json')
assert manifest['candidate_freeze_sha256'] == sha(I/'freeze.json')
assert manifest['stage']=='initial' and manifest['target_results_included'] is False
assert manifest['source_seed']==18101 and manifest['source_context_rows']==6000
assert set(manifest['files'])=={'lifelines_feedback.json','pani_feedback.json','source_context_preparation.json','source_context_report.json'}
for name, digest in manifest['files'].items():
    assert sha(H/name)==digest, name

initial_receipt=read(I/'freeze.json')
initial_before={p.relative_to(I).as_posix():sha(p) for p in I.rglob('*') if p.is_file()}
for relative,digest in initial_receipt['commitments'].items():
    assert sha(B/relative)==digest, relative

panel = read(B/'SOURCE_PANEL_SPEC.json')
report=read(H/'source_context_report.json')
preparation=read(H/'source_context_preparation.json')
assert report['status']=='success'
assert report['preparation_sha256']==sha(H/'source_context_preparation.json')
assert preparation['status']=='prepared'
assert {c['id'] for c in report['contexts']}=={'lifelines','pani'}
source_reports={sid:read(H/(sid+'_feedback.json')) for sid in ['lifelines','pani']}
review=[]
for sid, feedback in source_reports.items():
    bound=next(c for c in report['contexts'] if c['id']==sid)
    prepared=next(c for c in preparation['contexts'] if c['id']==sid)
    expected=next(c for c in panel['contexts'] if c['id']==sid)
    recipe=read(I/f'source_contexts/{sid}/whole_cohort_feedback.json')
    assert bound['status']=='success' and bound['generation_link_verified'] is True
    assert bound['feedback_sha256']==sha(H/(sid+'_feedback.json'))
    assert bound['feedback']==feedback
    assert feedback['status']=='complete' and feedback['output_link_verified'] is True
    assert feedback['generator_execution_recorded'] is True
    assert feedback['bindings']['candidate_freeze_sha256']==prepared['freeze_sha256']
    assert feedback['bindings']['model_spec_sha256']==prepared['spec_sha256']
    assert feedback['bindings']['task_sha256']==prepared['task_sha256']
    assert feedback['bindings']['recipe_sha256']==sha(I/f'source_contexts/{sid}/whole_cohort_feedback.json')
    assert len(feedback['checks'])==len(expected['checks'])==len(recipe['checks'])
    assert feedback['n_not_computable']==0
    for actual, fixed, declared in zip(feedback['checks'],expected['checks'],recipe['checks']):
        for key in ['id','evidence_id','operator']:
            assert actual[key]==fixed[key]==declared[key]
        assert actual['status']=='approximate' and actual['unavailable_reason'] is None
        assert actual['calculation']['n_input']==6000 and actual['calculation']['n_missing_dropped']==0
        review.append({'context':sid,'id':actual['id'],'reported':actual['reported_value'],
                       'computed':actual['calculation']['value'],'difference':actual['difference'],
                       'reported_uncertainty':actual['reported_uncertainty'],
                       'n_used':actual['calculation']['n_used'],'status':actual['status']})
assert len(review)==20

F.mkdir()
for path in I.rglob('*'):
    if path.is_file() and path.name!='freeze.json':
        dest=F/path.relative_to(I)
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,dest)
shutil.copyfile(I/'decision.md',F/'initial_decision.md')
for name in ['FEEDBACK_MANIFEST.json',*manifest['files']]:
    dest=F/'feedback'/'initial'/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(H/name,dest)

limitations=[
 'The retained model overpredicts older Pani HbA1c marginal means: differences are +0.043039 percentage points at60-64, +0.065600 at65-69 and +0.147427 at>=70; the discrepancy is unresolved.',
 'Pani unweighted age-band count probabilities, missing survey design, assumed within-band ages and independent sex composition do not reconstruct the original survey population or estimator.',
 'The conditional BMI-glucose residual correlation0.30, age/sex effects on both covariates, zero direct HbA1c sex term, normality and homoscedasticity are unidentified assumptions; source checks do not estimate these relationships.',
 'The aggregate conflict between the adjusted age coefficient and older marginal means does not identify a unique conditional age curve, age-covariate dependence, selection mechanism or survey correction.',
 'Lifelines assumed18-95 and Pani assumed25-95 age supports remain approximations; Pani>=70 is not restricted to79.',
 'US/Western-European source to Mexican target transport, plasma-to-serum comparability, ancestry, assay, 8-12-hour fasting, anemia, medication, pregnancy/lactation routing and standing-anthropometry selection differences remain unverified.',
 'No target diagnostics, causal validation, individual predictive validation or clinical measurement replacement evidence is available. Individual draws do not quantify evidence/model/transport uncertainty.'
]
addressed=[
 'Reviewed all11 Lifelines and9 Pani fixed source checks and their exact adjustment/selection operators; all20 were computable as approximate diagnostics with verified output linkage.',
 'Lifelines reported and computed HbA1c mean/SD are5.6/0.3 versus5.596215/0.294515; separate BMI and glucose projections are0.0118924/0.011638289 versus0.012152918/0.011398734. No fixed-seed recentering or coefficient repair is justified by these modest deviations.',
 'Pani adjusted age term is0.009649383 versus reported0.010; older marginal means show the anticipated systematic overshoot, most clearly>=70 at5.657427 versus5.51.',
 'Retain the exact scientific program and specification. Evidence does not resolve which unobserved source covariate/selection or nonlinear conditional mechanism should be changed. Retention preserves this limitation rather than converting a marginal pattern into an unsupported conditional law.',
 'Bind all five original controller feedback files, preserving hashes. Keep all fixed check IDs/operators and initial candidate bytes. Reuse recorded source outputs; retention earns no additional scientific draws.'
]
revision={'reason':'Retain the initial scientific model after the only source-feedback review. The feedback confirms modest Lifelines deviations and the anticipated material older-Pani marginal mismatch. It does not identify a justified conditional or transport correction; do not tune to the fixed draw or silently sacrifice the separately adjusted age projection. The retained model remains an explicitly limited scenario, not a successfully validated source/target reconstruction.',
          'kind':'retain','addressed_findings':addressed,'remaining_limitations':limitations}
write(B/'final_revision.json',revision)

table=['| Context / check | Reported | Computed | Difference | n used |',
       '|---|---:|---:|---:|---:|']
for x in review:
    table.append(f"| {x['context']} / {x['id']} | {x['reported']:.9g} | {x['computed']:.9g} | {x['difference']:+.9g} | {x['n_used']} |")
review_text='''# Complete source-feedback review and retention decision

The controller's initial-source bridge status is success. Both executions have verified generation/output linkage. Eleven Lifelines and nine Pani fixed checks are computable as approximate diagnostics; no fixed check is unavailable. This review reads the five authorized JSON handoff files only, including the preparation and outer report; it does not read source individual records, target records or additional studies. Exact original feedback bytes are bound under feedback/initial/.

All twenty results are listed below. Differences are computed minus reported, using each operator's declared units. There is no pooled loss or predeclared numerical pass threshold. These are not hypothesis tests.

'''+'\n'.join(table)+'''

The Lifelines age, BMI, glucose, HbA1c and sex summaries show modest finite-sample deviations from nominal source moments. Its BMI projection is0.012152918 versus0.0118924 and glucose projection0.011398734 versus0.011638289. Both computed values are inside the retained printed source intervals, whose confidence level is unknown; this observation is descriptive and supplies no invented confidence interval for this model. The fixed-seed discrepancies do not identify a needed parameter repair. The nominal moment and projection algebra remains the original construction, and sample recentering/refitting would conceal rather than resolve uncertainty.

Pani's adjusted age coefficient0.009649383 is close to the0.010 input. Its eight mean differences, in age order, are -0.028501, +0.015509, -0.035888, -0.015391, -0.008738, +0.043039, +0.065600 and +0.147427 percentage points. The increasing older-age overshoot confirms the initial decision record's concern about a linear age rule. The>=70 discrepancy is much larger than the published0.02 percentage-point survey SE, but that comparison is descriptive: the source estimator and Monte Carlo reconstruction are different, and neither a calibrated p-value nor a formal rejection probability follows. The discrepancy is not dismissed as Monte Carlo noise.

Retention is a scientific decision under incomplete information. A nonlinear age correction could reduce older marginal means, but it would also change the adjusted age projection unless compensating age-covariate dependence were introduced. The latter is unavailable in the admitted summaries. Age-specific glucose or BMI declines, ancestry offsets, or band-specific HbA1c corrections would be new assumptions chosen primarily to force agreement. Replacing conditional coefficients with slopes of marginal means would conflate adjustment sets. The source feedback therefore diagnoses an inadequacy without identifying a defensible unique repair. Keep the declared scenario and its inadequacy visible. This does not claim that the initial model is optimal or adequate for the intended target population.

The final generator.py and model_spec.json are byte-identical to initial. Both source tasks, both recipes, all twenty IDs/operators, source supports, level anchors and shared source-to-target mechanism are unchanged. The actual initial outputs must be reused for retained source assessment; no fresh source draw is requested or earned. No numerical improvement is claimed. The single review opportunity is consumed by retention.

Remaining unsupported relationships include BMI-glucose residual correlation; age/sex effects on covariates; direct sex effect on HbA1c; residual distribution and homoscedasticity; the explanation of Pani's age plateau; survey-weighted joint structure; source age support; and all Mexican population/selection/assay transport. The target has no verified anemia or medication exclusion, and its pregnancy/lactation and standing-route rules differ from sources. None of these are validated by small differences for other source summaries. No target diagnosis, causal effect or individual clinical prediction is validated.
'''
(F/'source_feedback_review.md').write_text(review_text,encoding='utf-8')
write(F/'source_feedback_review.json',{'decision':'retain','all_fixed_checks_reviewed':review,
      'initial_feedback_hashes':{name:sha(H/name) for name in ['FEEDBACK_MANIFEST.json',*manifest['files']]},
      'computed_source_checks':20,'noncomputable_fixed_checks':0,'numerical_improvement_claimed':False,
      'new_scientific_draws_requested':0,'remaining_limitations':limitations})

(F/'decision.md').write_text('''# Final scientific decision: retain

Retain generator.py and model_spec.json byte-for-byte after reviewing the complete controller-verified initial source feedback. Keep the source contexts, selection/adjustment operators, evidence, parameter algebra and source-to-target linkage unchanged. The final candidate binds all five actual feedback JSON files and records every result in source_feedback_review.md/json. The preserved original decision is initial_decision.md.

The source bridge and both isolated executions succeeded mechanically, with twenty computable approximate diagnostics. Lifelines marginal and projection differences do not identify a need to change coefficients. Pani's adjusted age term is0.009649383 against0.010, but its older marginal means are too high:60-64 by0.043039,65-69 by0.065600, and>=70 by0.147427 percentage points. This is the previously anticipated deficiency of the shared linear age/covariate construction. It remains unresolved and is not relabelled a successful source fit.

The admitted aggregate evidence does not determine whether nonlinear conditional aging, age-specific BMI/glucose structure, survey weighting, selection or source transport explains the older-age discrepancy. A correction to the marginal age curve would require a new choice among those mechanisms and would alter the independently adjusted age projection. No conditional coefficient, residual covariance, age-band correction or Mexico-specific offset is inferred from this discrepancy. Retention avoids claiming an identified repair where none is supplied. It is a bounded decision to retain an explicitly limited scenario, not a claim of optimality, clinical adequacy or target validity.

All eleven Lifelines and nine Pani checks retain their original approximate status and exact operators. Zero fixed source checks are non-computable after execution; target transport, causal and individual predictive validity remain unassessed. Normality, covariance0.30, source supports, missing survey design, anemia/medication status and serum/plasma/assay/ancestry selection differences remain assumptions. The uncertainty is not represented by more generated rows.

No generator was imported or called by the author, and no local data were generated. The initial candidate remains unchanged. The final scientific bytes are identical, so retention uses the existing source outputs and earns no additional source draw. No numerical improvement is claimed. Freeze the final candidate with parent initial and the sole retain revision object, then stop.
''',encoding='utf-8')

assert (F/'generator.py').read_bytes()==(I/'generator.py').read_bytes()
assert (F/'model_spec.json').read_bytes()==(I/'model_spec.json').read_bytes()
assert (F/'evidence.json').read_bytes()==(B/'evidence_template.json').read_bytes()
for sid in ['lifelines','pani']:
    for name in ['task.json','whole_cohort_feedback.json']:
        rel=f'source_contexts/{sid}/{name}'
        assert (F/rel).read_bytes()==(I/rel).read_bytes()
initial_after={p.relative_to(I).as_posix():sha(p) for p in I.rglob('*') if p.is_file()}
assert initial_before==initial_after
audit={'kind':'final_retention_static_audit','generator_executed_by_author':False,'local_generated_rows':0,
       'initial_freeze_sha256':sha(I/'freeze.json'),'initial_files_preserved':True,
       'generator_bytes_identical':True,'model_spec_bytes_identical':True,
       'generator_sha256':sha(F/'generator.py'),'model_spec_sha256':sha(F/'model_spec.json'),
       'source_recipes_and_tasks_identical':True,'fixed_checks_reviewed':20,'fixed_checks_noncomputable':0,
       'feedback_manifest_and_all_four_bound_file_hashes_verified':True,
       'source_report_preparation_and_child_feedback_bindings_checked':True,
       'scope':'Static identity/handoff verification only. Uses already computed controller feedback; does not recompute from individual records or validate scientific transport.'}
write(F/'retention_audit.json',audit)

aux=[p.relative_to(F).as_posix() for p in F.rglob('*') if p.is_file()
     and p.relative_to(F).as_posix() not in {'generator.py','model_spec.json','evidence.json','decision.md','checks.json','freeze.json'}]
write(F/'checks.json',{'scope':'source_only','records':[
 {'name':'retention_and_initial_integrity','status':'pass','detail':'Actual static checks confirm identical generator/specification, unchanged initial inventory, byte-identical source tasks/recipes/evidence and fixed-panel identities; bound retention_audit.json records this scope.'},
 {'name':'verified_controller_source_feedback','status':'pass','detail':'Manifest hashes and preparation/outer-report/child-feedback links were checked. Both controller executions succeeded and all11 Lifelines plus9 Pani approximate checks have actual values. This pass concerns feedback integrity/computability, not source or target scientific validity.'},
 {'name':'pani_older_age_source_representation','status':'fail','detail':'Author scientific assessment: the retained model inadequately represents older Pani marginal means, with computed-minus-reported differences+0.043039 at60-64,+0.065600 at65-69,+0.147427 at>=70 percentage points. This qualitative inadequacy finding is not a supplied numerical pass threshold, formal hypothesis test or pooled quality score. It remains unresolved.'},
 {'name':'target_transport_and_causal_validation','status':'not_computable','detail':'No target results are included or inspected. Mexican joint relationships, clinical prediction, causality and measurement replacement are not validated by source diagnostics.'}],
 'artifacts':[{'path':x,'sha256':sha(F/x)} for x in sorted(aux)]})
print(json.dumps({'decision':'retain','final_candidate':str(F),'revision_file':str(B/'final_revision.json'),
                  'generator_identical':True,'model_spec_identical':True,'source_checks_reviewed':20,
                  'new_source_draws_requested':0,'initial_unchanged':True},indent=2))
