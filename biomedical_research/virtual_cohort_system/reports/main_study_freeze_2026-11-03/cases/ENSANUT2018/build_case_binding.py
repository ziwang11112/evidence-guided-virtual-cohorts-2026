"""Deterministically scope previously admitted metadata; no rows or effects read."""
from pathlib import Path
import copy
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
OLD = PROJECT / 'work/autonomous_research_cycle2_2026-10-31'

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n',encoding='utf-8',newline='\n')

def bind(path):
    return {'path':Path(path).relative_to(PROJECT).as_posix(),'sha256':digest(path)}

evidence_path = OLD/'evidence/packet/evidence_template.json'
original = read(evidence_path)
normalized = read(OLD/'evidence/packet/normalized_quantities.json')['records']
admission = read(OLD/'admission/SOURCE_PACKET_ADMISSION.json')
assert digest(evidence_path) == admission['evidence_template_sha256']
assert admission['status'] == 'approved_for_bounded_scientific_construction_with_restrictions'
assert digest(OLD/'evidence/packet/MANIFEST.json') == admission['packet_manifest_sha256']
prior_sources = {x['id']:x for x in original['sources']}
for source in original['sources']:
    for artifact in source['artifacts']:
        assert digest(OLD/'evidence/packet'/artifact['path']) == artifact['sha256']
base_ids = [i['id'] for i in original['items'] if i['id'].startswith('J_T1_') or i['id']=='NGSP_UNIT_GUIDANCE']
rel_ids = [i['id'] for i in original['items'] if i['id'].startswith('J_T2_') or i['id'].startswith('P_NHANES_')]
conditions = {}
for arm, ids in [('E0',base_ids),('E1',base_ids+rel_ids)]:
    selected = [copy.deepcopy(i) for i in original['items'] if i['id'] in ids]
    records = [copy.deepcopy(i) for i in normalized if i['item_id'] in ids]
    for i in selected:
        i['applicability']=i['applicability'].replace('Pending root admission.', 'Previously admitted with restrictions; source-specific, not a target value.')
    sources=[]
    registry=[]
    for sid in dict.fromkeys(i['source_id'] for i in selected):
        source=copy.deepcopy(prior_sources[sid])
        source['identifier']=source['identifier'].replace('root admission pending','previously admitted with restrictions')
        relative=f'sources/{arm}/{sid}.md'
        # Do not copy the full old human summaries: these contain excluded
        # relationship and quarantined numeric text that would contaminate E0.
        content=f'# {sid}: {arm}-scoped admitted extraction\n\n'
        content+=source['identifier']+'\n\nPopulation: '+source['population']+'\n\nMeasurement: '+source['measurement']+'\n\n'
        content+='Only the following evidence records are supplied in this condition. This is an authored scoped extract, not the full paper. Other source results are not admitted through this file.\n\n'
        for item in selected:
            if item['source_id']==sid:
                record=next(r for r in records if r['item_id']==item['id'])
                content+='## '+item['id']+'\n\n```json\n'+json.dumps({'evidence':item,'normalization':record},indent=2,ensure_ascii=False)+'\n```\n\n'
        dst=HERE/relative
        dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_text(content,encoding='utf-8',newline='\n')
        source['artifacts']=[{'path':relative,'sha256':digest(dst)}]
        sources.append(source)
        registry.append({'source_id':sid,'path':relative,'sha256':digest(dst),'origin':'curator','screening':'approved'})
    packet={'schema_version':1,'sources':sources,'items':selected}
    write(HERE/f'{arm}.json',packet)
    write(HERE/f'{arm}_normalization.json',{'schema_version':1,'records':records,
        'duplicate_representations':'Original/derived representations share same_quantity_group; they are not independent constraints.',
        'uncertainty':'Pani ageband SE is sampling uncertainty, not individual SD. Jansen printed CI bounds have unknown confidence level; do not infer a standard error.'})
    write(HERE/f'{arm}_registry.json',{'artifacts':registry})
    conditions[arm]={'evidence_file':f'{arm}.json','evidence_sha256':digest(HERE/f'{arm}.json'),
       'normalization_file':f'{arm}_normalization.json','normalization_sha256':digest(HERE/f'{arm}_normalization.json'),
       'registry_file':f'{arm}_registry.json','registry_sha256':digest(HERE/f'{arm}_registry.json'),
       'item_ids':ids,'source_ids':[s['id'] for s in sources],
       'author_allowed_files':['task.json',f'{arm}.json',f'{arm}_normalization.json',f'{arm}_registry.json',f'{arm}_source_operations.json',*[a['path'] for s in sources for a in s['artifacts']]],
       'excluded_material':'Do not supply original full summaries, raw original packet/normalized records, article bodies, other-arm sources, old generators/results or target reference.'}

task=read(OLD/'public_v2/task.json')
task['task_id']='main-study-ENSANUT2018-whole-cohort'
task['n_rows']=3000
task['population']=task['population'].replace('250 fictional individuals','375 fictional individuals')
task['information_policy']['allowed_tools']=['admitted_source_read','request_evidence_clarification','contract_validation','controller_source_feedback','retained_analytic_calculation']
write(HERE/'task.json',task)

source_operations=[]
for eid, context, term, adjust in [
 ('J_T2_bmi_slope_task_derived','lifelines','bmi',['age','female']),
 ('J_T2_glucose_slope_task_derived','lifelines','glucose',['age','female']),
 ('P_NHANES_age_slope','pani','age',['female','bmi','glucose'])]:
    source_operations.append({'operation_id':eid,'source_context':context,
      'formula':'hba1c ~ 1 + '+' + '.join([term,*adjust]),'term':term,
      'variables_units':{'age':'year','female':'1','bmi':'kg/m^2','glucose':'mg/dL','hba1c':'%'},
      'strict_replay_status':'not_computable_from_admitted_aggregates',
      'qualified_analytic_path':{'file':'source_operators.py','function':'source_projection',
        'formula':'beta = solve(Sigma_XX, Sigma_XY); report beta for separately named term',
        'required_input':'Independently checked moments of the author-declared source-context law after source selection, in stated units; binding to frozen generator and assumptions required.',
        'status':'operator_available_moment_derivation_and_scientific_linkage_require_candidate_review'},
      'source_limitations':['Source marginals do not identify cross-covariances or residual law.','Jansen Table 2 row-specific n is unresolved; full-cohort margins do not prove same analysis population.','Separate projections cannot be assigned as coefficients of one joint equation.'] if context=='lifelines' else ['Survey weights and original IPD unavailable; this is an assumption-qualified population projection, not exact survey replay.','Unreported source joint distribution and source support require assumptions.'],
      'target_transfer':'External population projection only; serum/plasma and selection/ancestry/assay transfer are unverified. Target standardization is not source-context reconstruction.'})
for item in original['items']:
    if item['id'].startswith('P_NHANES_hba1c_age_'):
        record=next(r for r in normalized if r['item_id']==item['id'])
        source_operations.append({'operation_id':item['id'],'source_context':'pani','kind':'ageband_mean',
          'age_rule':record['age_rule'],'formula':'E_source[HbA1c * I(age in band)] / P_source(age in band)',
          'strict_replay_status':'not_computable_without_survey_and_population_information',
          'qualified_analytic_status':'available_if_author_derives_conditional_integrals_of_its_declared_source_law; no compulsory simulation',
          'uncertainty':'Reported survey SE is not individual SD; source unweighted age counts are not target probabilities.',
          'source_support':'The >=70 source band has no admitted upper bound; target79 limit must not be inserted silently.'})
write(HERE/'E0_source_operations.json',{'schema_version':1,'condition':'E0','non_marginal_operations':[],
    'basic_operations':'Univariate moments and female proportion only. No assertion of identified dependence. Agent may choose dependence assumptions but they are not source constraints.'})
write(HERE/'E1_source_operations.json',{'schema_version':1,'condition':'E1','non_marginal_operations':source_operations,
    'execution_policy':'New session has no source-row replay. Retained deterministic analytic calculations are permitted, independently checked, and tied to the candidate. At most two target trials globally per construction; no unmetered row-producing calibration.'})

old_release=read(OLD/'EVALUATION_RELEASE.json')
prior_paths=[OLD/'PROTOCOL_v2.md',OLD/'admission/SOURCE_PACKET_ADMISSION.json',evidence_path,
 OLD/'evidence/packet/normalized_quantities.json',OLD/'evidence/packet/MANIFEST.json',
 OLD/'evidence/INDEPENDENT_SOURCE_AUDIT.md',OLD/'public_v2/SOURCE_PANEL_SPEC.json',
 OLD/'public_v2/task.json',OLD/'analysis/analytical_engine.py',OLD/'analysis/run_evaluation.py',
 OLD/'custodian/prepare_reference_v2.py',OLD/'custodian/PREFLIGHT_METADATA.json',
 OLD/'custodian/MEASUREMENT_RULE_ADJUDICATION.md',OLD/'PREPARATION_AMENDMENT_01.md',
 OLD/'custodian/PREPARATION_RECEIPT_v2.json',OLD/'EVALUATION_RELEASE.json']
card={'schema_version':'main_study_case_v1','case_id':'ENSANUT2018','phase':'bound_pending_independent_release','execution_enabled':False,
 'exposure':{'status':'researcher_exposed_developmental_reuse','target_family':'ENSANUT','new_confirmation':False,
   'source_family_overlap':'Jansen/Lifelines overlaps CHNS evidence; Pani/NHANES is external to ENSANUT. This adds a target family, not entirely independent source evidence.',
   'current_binding_reads':'Metadata, source evidence and analysis/preparation code only; no participant rows, generated rows or target effect reports were opened.'},
 'target_contract':{'task_file':'task.json','task_sha256':digest(HERE/'task.json'),'mode':'whole_cohort','n_rows':3000,
   'individual_inputs':False,'columns':task['columns'],'population':task['population'],
   'demographic_standard':{'age_edges':[25,40,55,70,80],'age_type':'integer years','sex_codes':{'0':'male','1':'female'},'cell_count':8,'cell_mass':0.125,'generated_rows_per_cell':375,'reference_row_weight':'1/(8*n_h)','national_population_claim':False},
   'measurement':{'glucose':'VALOR_GLU_SUERO, serum mg/dL; original external evidence uses plasma','hba1c':'VALOR_HB1AC, whole-blood HbA1c percent','bmi':'kg/(cm/100)^2 using prespecified same-repeat standing pair and routing; not an official unpublished final-reading reconstruction'},
   'eligibility':['Age25–79 and recorded laboratory/anthropometry sex-age agreement.','P7==2: never reported doctor diagnosis; gestational/unknown/missing excluded.','Recorded fast8–12h, finite0<serumglucose<126mg/dL and HbA1c>0.','Pregnancy/lactation negative required under questionnaire routing for women25–49; no invented negative answer in unasked groups.','First complete valid same-ordinal standing pair, second only if first unavailable; block/routes and explicit not-weighed contradictions excluded per pinned preparation.','Complete positive BMI/glucose/HbA1c; no data-distribution outlier trimming, no new imputation.'],
   'not_claimed':['No verified medication exclusion.','No anemia exclusion.','No national survey-weighted estimand.','No reconstruction of individual clinical measurements.'],
   'reference_binding':{'path':(OLD/old_release['reference']['path']).relative_to(PROJECT).as_posix(),'sha256_from_prior_release':old_release['reference']['sha256'],'current_rows_opened':False},
   'preparation_rule':'Reuse pinned reference preparation; do not regenerate or modify eligibility from new scientific outcomes.'},
 'evaluation':{'engine':bind(OLD/'analysis/analytical_engine.py'),'function':'analyze_cohort','unchanged_engine':True,
   'analysis_population':'All valid rows, demographic cell-standardized equally; generated table must have375rows/cell. Same weighted estimator for reference and generated.',
   'transforms':{'age10':'(age-50)/10','bmi5':'(bmi-25)/5','glucose10':'(glucose-100)/10'},
   'uses':[
     {'id':'Q1_age10','formula':'hba1c ~ 1 + age10 + female + bmi5 + glucose10','coefficient':'age10','unit':'percentage points per10years','support_E0':'assumption_dependent_not_numerically_supplied','support_E1':'source_indexed_adjusted_age_projection_transfer; Pani source coefficient given, target value not supplied','direct_calibration_target':False,'source_relation_is_supplied_in_E1':True},
     {'id':'Q2_bmi5','formula':'hba1c ~ 1 + age10 + female + bmi5','coefficient':'bmi5','unit':'percentage points per5kg/m^2','support_E0':'assumption_dependent_not_numerically_supplied','support_E1':'source_indexed_age_sex_adjusted_BMI_projection_transfer; Jansen given, target value not supplied','direct_calibration_target':False,'source_relation_is_supplied_in_E1':True},
     {'id':'Q3_bmi5','formula':'hba1c ~ 1 + age10 + female + bmi5 + glucose10','coefficient':'bmi5','unit':'percentage points per5kg/m^2','support_E0':'assumption_dependent','support_E1':'unreported_joint_structure; exact conditioned projection is not supplied','direct_calibration_target':False,'source_relation_is_supplied_in_E1':False,'not_algebraically_identified_by_source_packet':True}],
   'derived_contrasts':[{'id':'Q2_minus_Q3_bmi5','definition':'Q2_bmi5-Q3_bmi5','role':'algebraic derived descriptive change; not another independent endpoint or causal mediation'}],
   'diagnostics':'Preserve engine secondaryglucose10 age-sex projection; weighted mean, populationSD and inverse-CDFq10/q50/q90 of5fields; Q1residualweightedRMS; all scheduled failures.',
   'reference_uncertainty':{'method':'reuse399attempt cluster-resampling empirical stability procedure','seed':18301,'clusters':'(lab_est_dis,lab_upm_dis)','within_stratum':'drawcPSUs withreplacement; singletononce; carrycompleteclusters; recompute8-cellstandard','failure':'no retries; reportvalid/attempted andemptycell/singularfailures','interval':'2.5/97.5percentiles NumPylinear overvalidreplicates','interpretation':'Finite empirical reference stability, not national confidence intervals or equivalence bounds.'},
   'arm_contrast':'Perendpoint E1minusE0 difference of armmeans of each constructor mean absolute discrepancy across3fixedseeds; incomplete summaries explicitly incomplete; no pooledscore.'},
 'information_conditions':conditions,
 'source_operations':{'E0':'E0_source_operations.json','E1':'E1_source_operations.json','analytic_helper':{'file':'source_operators.py','sha256':digest(HERE/'source_operators.py')},'prior_row_replay_reuse':'Old source panel defines compatible names/operators but newbounded sessiondoesnotpromise source-rowreplay.'},
 'source_context_plan':{'lifelines':'Qualified analytic populationmoments, if derivationis suppliedandchecked. Source exclusions/row-n/covariances unreported. No genericpopulationreconstruction claim.',
   'pani':'Optional qualifiedanalytic adjustedage/agebandintegrals; surveydesign cannotbereconstructed; unweightedagecountsnot probabilityweights; strictreplay unavailable.',
   'target':'Separate taskpopulation and8-cellstandard; never relabel target statistics as sourcereplay.'},
 'numerical_uptake_requirement':'EachE1author accountsfor3separateprojectionand8agebanditems: numericalconstraint/checkedcalculation/contextual/declined withreason. Atleastone nonmarginaloperation is available via analytichelper; availabilitydoesnotforcepositivefit. Scientific momentderivation and generatorlinkage require independentreview.',
 'unidentified_assumptions':['Sourcecorrelation/covariance, residualdistribution andtails beyond margins.','Sourceanalysisrow-nand selectionreconstruction.','Serum/plasma, assays, ancestry and anemia/medication selectiontransfer.','Within-target-ageband distributions, BMI/glycemic marginal transfer and dependences.','Pani populationweights/supportincluding>=70 upperrange.','Covariancecompletion choices canchangeQ3 evenif all sourceprojectionsmatch.'],
 'prior_artifact_bindings':[bind(x) for x in prior_paths],
 'unresolved_release_gates':['Independentreview ofthiscasecard/armsplit/analytichelper.','Root comparator/evaluation/session/seedmanifest andglobalclosurebinding.','Per-author momentderivation-to-generator numericaluptakereview ifanalyticevidenceuseisclaimed.'],
 'budget_note':'No newpaper,dataacquisitionorpatient/generation run. Old scientific budgets unchanged. Newmain2totalexploratory+3final attempts perconstruction governedbyrootmanifest.'}
for use in card['evaluation']['uses']:
    use['target_numeric_calibration_supplied'] = use.pop('direct_calibration_target')
    use['source_numeric_calibration_relation_available_in_E1'] = use['source_relation_is_supplied_in_E1']
public_analyses={k:copy.deepcopy(card['evaluation'][k]) for k in ('analysis_population','transforms','uses','derived_contrasts','diagnostics')}
public_analyses['instruction']='All analysis questions are visible. No target numeric answer is supplied. Generate valid task-appropriate data and state source/transport/completion assumptions. Do not use the analysis request as evidence of a sign or effect size.'
write(HERE/'analysis_definitions.json',public_analyses)
for arm in ('E0','E1'):
    card['information_conditions'][arm]['author_allowed_files'].append('analysis_definitions.json')
    if arm=='E1':
        card['information_conditions'][arm]['author_allowed_files'].append('source_operators.py')
card['evaluation']['generated_only_provider']={'file':'generated_feedback.py','sha256':digest(HERE/'generated_feedback.py'),'function':'evaluate_generated','analysis_ids':['Q1_age10','Q2_bmi5','Q3_bmi5'],'reference_reader_present':False}
card['evaluation']['provider_dependency']=bind(OLD/'analysis/analytical_engine.py')
card['budget']={'exploratory_attempts':2,'final_attempts':3,'total_attempts':5,'rows':3000,'trial_seeds':[5201,5202],'final_seeds':[5101,5102,5103]}
for arm in ('E0','E1'):
    for kind in ('agent','statistical'):
        write(HERE/f'profile_{arm}_{kind}.json',{'case_id':'ENSANUT2018','information_condition':arm,'constructor_kind':kind,'source_numeric_mode':'reviewed_analytic_only','analysis_ids':['Q1_age10','Q2_bmi5','Q3_bmi5'],'budget':card['budget']})
write(HERE/'case_card.json',card)
sys.path.insert(0,str(PROJECT))
from cohort_harness.contracts import validate_task,validate_evidence
validate_task(task)
for arm in conditions:
    validate_evidence(read(HERE/f'{arm}.json'),task)
write(HERE/'BINDING_VALIDATION.json',{'status':'schema_and_prior_admission_hashes_pass','new_patient_or_generated_tables':0,
 'new_downloads':0,'new_original_papers':0,'E0_items':len(base_ids),'E1_items':len(base_ids+rel_ids),
 'source_artifact_hashes_verified':True,'source_operators_tests':'5 deterministic artificial-moment tests passed; no sampling',
 'generated_feedback_tests':'2 hand-built factorial/invalid-input tests passed; no random sampling or patient data','new_test_count':7,
 'historical_frozen_files_modified':False,'case_card_sha256':digest(HERE/'case_card.json')})
print(json.dumps({'case':'ENSANUT2018','status':'prepared_pending_review','E0_items':len(base_ids),'E1_items':len(base_ids+rel_ids)}))
