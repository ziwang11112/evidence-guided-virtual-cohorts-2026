"""Bind actual source feedback and retain the initial scientific bytes; no generation."""
import hashlib
import json
import shutil
from pathlib import Path

B=Path(__file__).resolve().parent
INITIAL=B/'candidates/initial'
FINAL=B/'candidates/final'
FEEDBACK=B/'controller_feedback/initial'
assert not FINAL.exists(), 'Final candidate already exists; do not overwrite it.'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')

initial_inventory={str(p.relative_to(INITIAL)):digest(p) for p in INITIAL.rglob('*') if p.is_file()}
manifest=read(FEEDBACK/'FEEDBACK_MANIFEST.json')
assert manifest['candidate_freeze_sha256']==digest(INITIAL/'freeze.json')
assert manifest['target_results_included'] is False
assert manifest['source_seed']==18101 and manifest['source_context_rows']==6000
assert set(manifest['files'])=={'lifelines_feedback.json','pani_feedback.json','source_context_report.json','source_context_preparation.json'}
for name,expected in manifest['files'].items():
    assert digest(FEEDBACK/name)==expected
report=read(FEEDBACK/'source_context_report.json')
preparation=read(FEEDBACK/'source_context_preparation.json')
assert report['status']=='success'
assert report['preparation_sha256']==digest(FEEDBACK/'source_context_preparation.json')
assert preparation['status']=='prepared'
panel=read(B/'SOURCE_PANEL_SPEC.json')
full_reviews=[]
table_rows=[]
for name,expected_count in [('lifelines',11),('pani',9)]:
    feedback=read(FEEDBACK/f'{name}_feedback.json')
    context=next(c for c in report['contexts'] if c['id']==name)
    source_preparation=next(c for c in preparation['contexts'] if c['id']==name)
    fixed=next(c for c in panel['contexts'] if c['id']==name)['checks']
    assert context['status']=='success' and context['generation_link_verified'] is True
    assert context['feedback']==feedback
    assert context['feedback_sha256']==digest(FEEDBACK/f'{name}_feedback.json')
    assert feedback['status']=='complete' and feedback['output_link_verified'] is True
    assert feedback['generator_execution_recorded'] is True
    assert feedback['n_computable']==expected_count and feedback['n_not_computable']==0
    assert feedback['bindings']['candidate_freeze_sha256']==source_preparation['freeze_sha256']
    assert feedback['bindings']['recipe_sha256']==digest(INITIAL/f'source_contexts/{name}/whole_cohort_feedback.json')
    assert len(feedback['checks'])==len(fixed)==expected_count
    for item,original in zip(feedback['checks'],fixed):
        assert (item['id'],item['evidence_id'],item['operator'])==(original['id'],original['evidence_id'],original['operator'])
        assert item['status']=='approximate' and item['calculation'] is not None
        assert item['calculation']['n_input']==6000
        table_rows.append(f"| {item['id']} | {item['reported_value']:.9g} | {item['calculation']['value']:.9g} | {item['difference']:+.9g} | {item['calculation']['n_used']} |")
    full_reviews.append({'context':name,'checks':feedback['checks'],'source_feedback_sha256':digest(FEEDBACK/f'{name}_feedback.json')})

FINAL.mkdir()
for source in INITIAL.rglob('*'):
    if source.is_file() and source.name!='freeze.json':
        destination=FINAL/source.relative_to(INITIAL)
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,destination)
for name in ['FEEDBACK_MANIFEST.json',*manifest['files']]:
    destination=FINAL/'controller_feedback/initial'/name
    destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(FEEDBACK/name,destination)

review_intro='''# Final source-only feedback review and retention

Decision: retain the initial generator.py and model_spec.json byte-for-byte. The frozen source recipes, common scientific family, target transfer rule, and all20 fixed operators are also retained. The existing source executions are reused; retention does not claim a new run or numerical improvement.

The controller reported successful isolated execution and bridge verification for both6000-row source contexts at seed18101. This review checked all five supplied JSON files: manifest hashes, initial-freeze binding, preparation/report consistency, report-to-individual-feedback identity, fixed panel/operator identity, and all20 calculations. No source output table, target data, generator import, bridge execution or additional scientific draws were used by the builder.

Lifelines diagnostics show differences in age mean(+0.201 years), age SD(-0.112871), BMI mean(-0.142673 kg/m^2), BMI SD(+0.024493), glucose mean(-0.109774 mg/dL), glucose SD(+0.042745), HbA1c mean(-0.001003 percentage points), HbA1c SD(-0.003981) and female proportion(-0.001). These are retained numerical differences, not evidence of exact marginal recovery. Finite Monte Carlo variation, rounded evidence and approximation of age/support/selection can contribute; one run does not identify their separate contributions. No seed-specific location or scale correction is justified by these values alone.

Lifelines HbA1c-on-BMI adjusted for age/female is0.01053256 versus reported0.0118924, difference-0.00135984. The glucose projection is0.01154940 versus0.01163829, difference-0.00008889. Both lie within the printed converted interval endpoints, but their confidence levels are unknown and this is not a calibrated acceptance test. The reported interval endpoints remain unchanged. No inference that residual correlation0.30 is correct follows: many joint laws can satisfy the source projections.

Pani adjusted age coefficient is0.00991839 versus reported0.010, difference-0.00008161. However, the source age-band mean profile is visibly incompatible with an exact reconstruction: differences are-0.05776(<40), -0.02818(40-44), -0.06141(45-49), -0.02325(50-54), -0.03700(55-59), +0.02866(60-64), +0.02853(65-69), and+0.12261(>=70) percentage points. The oldest mean is5.63261 versus5.51, whose reported survey SE is0.02. This patterned young-low/old-high discrepancy is treated as a substantive limitation of the assumed marginal age pattern; it is not dismissed as Monte Carlo noise. Survey SEs are retained as survey uncertainty and are not converted into individual SDs or a formal discrepancy z-test.

The discrepancy was possible under the initial construction because Pani's adjusted age projection and eight marginal age-band means do not identify the source covariate age patterns, nonlinear conditional age response, within-band ages, survey weights, or selection. A revised nonlinear age curve could alter the adjusted age projection; an age-specific covariate repair could force agreement through an unreported dependence; direct band intercepts would fit marginal outcomes without resolving conditional transport. The fixed source evidence supplies no discriminating information between these explanations. Retaining the transparent limited scenario is preferred to inventing one correction from this single run. This decision is not a claim that the current source age profile is adequate.

The target remains the same analytical scenario: exact supplied quotas, the identical Pani HbA1c anchor and shared Lifelines-based covariate law. The Pani age-band mismatch specifically weakens support for age-stratified target HbA1c summaries and any analysis sensitive to nonlinear age effects. No target statistic informed the decision, and no improvement in target validity is asserted. The final model is not suitable for claiming national prevalence, clinical replacement measurements or causal effects.

Remaining unsupported relationships are the residual BMI/glucose correlation, covariate age/sex trends, zero direct female HbA1c effect, linear age response and absence of interactions, normal homoskedastic residual law, target BMI/glucose marginals, source age tails and sex-age association, survey-to-unweighted estimator mapping, ancestry/selection effects, anemia/medication/pregnancy mechanisms and fasting-plasma-to-serum/assay equivalence. The Lifelines adult support18-95 and Pani declining70-95 tail remain explicit assumptions, including truncation beyond95. All20 fixed diagnostics were computable; causal, transport and scientific validity remain unassessed.

Individual residual variation and repeated seed variation are not evidence, model or transport uncertainty. No posterior or scientific pass score has been invented. Scientific changes: none. The allowed source-feedback opportunity is now closed by retention and final freeze.

All fixed diagnostic values follow. Units, adjustment sets, uncertainty types, assumptions and full metadata are preserved in the bound original feedback JSON files; differences are calculated minus reported.

| Check ID | Reported | Calculated | Difference | Rows used |
|---|---:|---:|---:|---:|
'''
(FINAL/'feedback_review.md').write_text(review_intro+'\n'.join(table_rows)+'\n',encoding='utf-8')
write(FINAL/'feedback_review.json',{
    'kind':'review_of_controller_source_feedback','decision':'retain',
    'generator_and_specification_changed':False,'numerical_improvement_claimed':False,
    'additional_draws_requested':False,'initial_freeze_sha256':digest(INITIAL/'freeze.json'),
    'all_fixed_checks_reviewed':20,'n_not_computable':0,
    'source_age_pattern_limitation':'Pani youngest and oldest band means differ by -0.0577585 and +0.1226124 percentage points; retained as substantive model limitation.',
    'contexts':full_reviews})

decision='''# Final decision: retain

The initial scientific generator and complete model specification are retained byte-for-byte after the single source-only feedback review. No scientific parameter, population support, context selector behavior, source panel or target transfer rule changed. Actual controller feedback is bound in checks.json and reviewed completely in feedback_review.md and feedback_review.json.

Both source executions succeeded, and all11 Lifelines plus9 Pani checks were computable with verified output linkage. This establishes computation and lineage, not source or target scientific validity. The adjusted Pani age coefficient was0.00991839 versus reported0.010. The Pani age-band pattern was not adequately reproduced: <40 mean5.14224 versus5.20, and >=70 mean5.63261 versus5.51; the latter discrepancy is+0.12261 percentage points. These differences, and every other source difference, remain visible.

Retention is a scientific stopping decision under incomplete identification. The source evidence does not distinguish nonlinear conditional aging, unreported age-covariate patterns, survey weighting, age-tail assumptions or selection as explanations of the marginal-age discrepancy. Imposing one correction would add unsupported structure and could compromise the preserved conditional age projection. I do not regard the mismatch as solved, stochastic noise alone, or evidence that the target model is valid. It restricts intended use to a declared illustrative analytical scenario, particularly limiting age-stratified HbA1c conclusions.

Jansen Table1 and two separate Table2 projections remain the source constraints used by the shared covariance construction. Assumed residual correlation0.30, covariate age/sex trends, zero direct female HbA1c effect, Gaussian residuals and Pani-to-target location transport remain assumptions. Pani SEs remain survey SEs. Liu and Jansen Table3 remain contextual/quarantined, and NHANES overlap is not independent replication. All32 admitted evidence items and grouping records remain intact.

Ancestry, BMI/glucose population distributions, source age tails, medication/anemia/pregnancy mechanisms, measurement documentation, assay and fasting-plasma-to-serum transport remain unsupported. Target pregnancy/lactation eligibility is only the supplied documented routing; older unasked status is unresolved. Source fit cannot establish national prevalence, causal effects or clinical measurement substitution.

The builder did not import or call the generator, run the bridge, generate rows, inspect target diagnostics or acquire additional papers. The controller's existing isolated source executions are reused under retention; no fresh scientific draws or numerical improvements are claimed. Final freeze ends the single feedback opportunity. Initial candidate bytes are preserved.
'''
(FINAL/'decision.md').write_text(decision,encoding='utf-8')

byte_bindings={name:{'initial_sha256':digest(INITIAL/name),'final_sha256':digest(FINAL/name)}
               for name in ['generator.py','model_spec.json','evidence.json','source_context_plan.json',
                            'source_contexts/lifelines/task.json','source_contexts/lifelines/whole_cohort_feedback.json',
                            'source_contexts/pani/task.json','source_contexts/pani/whole_cohort_feedback.json']}
assert all(x['initial_sha256']==x['final_sha256'] for x in byte_bindings.values())
assert initial_inventory=={str(p.relative_to(INITIAL)):digest(p) for p in INITIAL.rglob('*') if p.is_file()}
write(FINAL/'retention_audit.json',{
    'status':'pass','scope':'source-feedback hashes, metadata linkage and scientific byte retention',
    'feedback_files_checked':5,'fixed_checks_reviewed':20,'byte_bindings':byte_bindings,
    'initial_file_inventory_unchanged':True,'generator_imported_or_called':False,
    'bridge_imported_or_called':False,'individual_rows_generated_by_builder':0,
    'source_execution_performed_by':'controller before final authoring',
    'scientific_adequacy':'not_certified','additional_draws_requested':False})

checks=read(INITIAL/'checks.json')
checks['records']=[r for r in checks['records'] if r['name'] not in ('numerical_source_validation','target_validity')]
checks['records'] += [
    {'name':'execution_linked_source_calculations','status':'pass','detail':'Actual controller reports bind successful isolated6000-row runs and all20 fixed computations. Pass denotes computation/linkage only, not scientific goodness of fit. Original feedback files are bound artifacts.'},
    {'name':'source_feedback_integrity_and_retention','status':'pass','detail':'All five handoff files parsed, manifest hashes and cross-report bindings checked, all20 fixed operators preserved, initial unchanged and final generator/model bytes identical; see retention_audit.json.'},
    {'name':'source_model_adequacy','status':'not_computable','detail':'No calibrated adequacy threshold is supplied. Pani age-band mismatch is substantive and unresolved: youngest -0.05776 and oldest +0.12261 percentage points. Full discrepancies and retention rationale are recorded; no scientific pass is claimed.'},
    {'name':'target_validity','status':'not_computable','detail':'No target diagnostics accessed; covariance, ancestry, selection, assay and plasma/serum transport remain unvalidated.'}]
new_aux=['feedback_review.md','feedback_review.json','retention_audit.json']
new_aux += [f'controller_feedback/initial/{name}' for name in ['FEEDBACK_MANIFEST.json',*manifest['files']]]
checks['artifacts'] += [{'path':name,'sha256':digest(FINAL/name)} for name in new_aux]
write(FINAL/'checks.json',checks)

revision={
    'reason':'Retain the shared initial model after complete verified source-only feedback. The Pani age-band discrepancy is real and unresolved, but the supplied evidence does not identify whether nonlinear age effects, unreported covariate patterns, survey weighting or selection should be changed; no seed-specific correction is justified.',
    'kind':'retain',
    'addressed_findings':[
        'Reviewed and bound all five controller handoff files and all11 Lifelines plus9 Pani diagnostics with no omitted checks.',
        'Documented Lifelines marginal and separate projection discrepancies without interpreting printed intervals as having an invented confidence level.',
        'Documented close Pani adjusted age projection alongside youngest -0.0577585 and oldest +0.1226124 percentage-point HbA1c discrepancies and all intermediate bands.',
        'Preserved the scientific program/specification, population contexts and fixed source recipes byte-for-byte; retention reuses existing source outputs and requests no new draws.',
        'Explicitly limited age-stratified HbA1c interpretation and made no source-adequacy or target-validity claim.'
    ],
    'remaining_limitations':[
        'Pani marginal age pattern remains poorly reproduced, particularly the oldest band; causal explanation is unidentified.',
        'Residual BMI/glucose covariance, covariate age/sex trends, linear age response, direct female null effect and residual law are assumed.',
        'Pani survey estimator, true within-band ages and open old-age tail are not reconstructed; Lifelines age support is assumed.',
        'Mexican ancestry/population transport and medication, anemia, pregnancy, selection, assay and fasting-plasma-to-serum effects remain unvalidated.',
        'No target diagnostics were supplied; source computations and byte identity do not establish scientific validity or clinical usefulness.'
    ]}
write(B/'revision_final.json',revision)
print(json.dumps({'candidate':str(FINAL),'decision':'retain','generator_sha256':digest(FINAL/'generator.py'),
                  'spec_sha256':digest(FINAL/'model_spec.json'),'source_checks_reviewed':20,
                  'initial_unchanged':True,'builder_generated_rows':0},indent=2))
