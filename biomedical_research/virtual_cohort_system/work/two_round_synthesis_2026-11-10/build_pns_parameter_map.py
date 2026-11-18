"""Assemble a static provenance map. Reads JSON/text; never imports author code."""
from pathlib import Path
import copy
import hashlib
import json
import math

P = Path(__file__).resolve().parents[2]
U = Path(__file__).resolve().parent
R1 = 'work/cross_model_api_pilot_2026-11-10'
R2 = 'work/economy_feedback_pilot_2026-11-10'
read = lambda p: json.loads((P / p).read_text(encoding='utf-8'))
old = read(R1 + '/provenance_review/PNS_CORE_REVIEW.json')
old_by_id = {x['construction_id']: x for x in old['constructions']}
endpoints = ['bmi_sbp', 'bmi_dbp', 'residual_correlation']
bridges = [
    'Source sodium/potassium/alcohol adjustment differs from requested age/sex adjustment.',
    'Inverse-variance within-centre pooling is not the target weighted-mixture projection.',
    'Source ages 20-59 are extended to target ages 20-79.',
    'Population, measurement/device/reading aggregation, treatment and selection transport are unverified.'
]
source_operator = 'INTERSALT Table II p322: inverse-variance pooled within-centre raw BP-on-BMI coefficient, additionally adjusted for age, sex, urinary sodium/potassium and alcohol; ages 20-59; mean of two random-zero BP readings.'
common_limits = [
    'Static law consistency is not source-to-target validity; target results are joined separately by the root task.',
    'Fixed scientific parameters: seeds change individuals, not uncertainty about evidence, assumptions or transport.',
    'Source coefficient SEs 0.0359/0.0257 are not individual SDs or transfer uncertainty.',
    'Existing evidence packets were reused; no original-paper reauthentication was performed.'
]

def locators(base, spec_paths, decision_indices, code_patterns):
    lines = (P / base / 'generator.py').read_text(encoding='utf-8').splitlines()
    out = [f'{base}/model_spec.json#{path}' for path in spec_paths]
    out += [f'{base}/decision_record.json#/parameter_provenance/{i}' for i in decision_indices]
    for pat in code_patterns:
        out += [f'{base}/generator.py:{i+1}' for i, line in enumerate(lines) if pat in line]
    return list(dict.fromkeys(out))

def parameter(pid, name, value, unit, src, reported, operator, components, transform, assumptions, locations, aids, note):
    return dict(parameter_id=pid, name=name, value=value, unit=unit, source_ids=src,
                source_reported_value=reported, source_operator=operator,
                provenance_components=components, transformation=transform,
                transport_assumptions=assumptions, actual_code_use='verified',
                locators=locations, analysis_ids=aids, mathematical_note=note)

def declared(decision, aid):
    row = next(x for x in decision['requested_estimands'] if x.get('analysis_id', x.get('id')) == aid)
    for key in ['population_value', 'model_implied_population_value', 'exact_model_implied_value', 'model_implied_value', 'exact_model_implied_population_value']:
        if key in row:
            value = row[key]
            return value if isinstance(value, (float, int)) else None
    return None

def slope_parameter(base, m, paths, di, patterns, value, per5=False, astra_bridge=False):
    transform = ('Source coefficients multiplied by five before storing the per-five inputs.' if per5 else 'Program multiplies the reported per-kg/m2 inputs by the requested BMI divisor of five.')
    if astra_bridge:
        transform += ' Adds assumed omitted-score conditional BMI mean 0.2 times outcome loadings 4/3, shifting requested slopes by 0.8/0.6.'
    return parameter('bmi_coefficients', 'BMI association coefficients for SBP and DBP', value,
        'mmHg per 5 kg/m2' if per5 else 'mmHg per kg/m2 (source-anchor scale)',
        ['S_INTERSALT'], {'SBP': 0.7754, 'DBP': 0.5967, 'unit': 'mmHg per kg/m2'},
        source_operator, ['reported', 'derived', 'assumed'], transform,
        bridges + (['The omitted adjustment score and its BMI association/outcome effects are assumed, not source-estimated.'] if astra_bridge else ['No net omitted-adjustment shift in the BMI projection is assumed.']),
        locators(base, paths, di, patterns), ['bmi_sbp', 'bmi_dbp'],
        'Final-law projection is derived under the completed joint model; the source alone does not identify the requested target projection.')

def residual_parameter(base, value, paths, di, patterns, source_group, transform, note, assumptions):
    if source_group:
        source_values = {'SBP_SD':20.98,'DBP_SD':11.22,'PP_SD':17.59} if source_group == '65plus' else {'SBP_SD':20.35,'DBP_SD':10.93,'PP_SD':17.2}
        source_values.update(group=source_group, unit='mmHg, individual marginal SD')
        src = ['S_BEIJING']
        operator = f'Beijing Table 1 {source_group}: unadjusted individual SBP, DBP and pulse-pressure SDs; neither conditional SD nor requested residual rho.'
        components = ['reported', 'derived', 'assumed']
    else:
        src, source_values = [], None
        operator = 'No admitted compatible conditional residual SD/correlation source; values or factor loadings are author assumptions.'
        components = ['assumed', 'derived']
    return parameter('residual_law', 'Residual covariance and individual dispersion construction', value,
        'mixed: SD/loadings in mmHg; covariance in mmHg2; rho dimensionless; see fields',
        src, source_values, operator, components, transform, assumptions,
        locators(base, paths, di, patterns), ['residual_correlation', 'sbp.sd_population', 'dbp.sd_population'],
        note + ' Residual covariance also contributes to marginal BP SD diagnostics, but does not determine them alone: marginal variance includes modeled conditional-mean and covariate variability. The core map is not an exhaustive covariate-law audit.')

cfg = {
 'PNS_OA_ASTRA_C1': dict(slope_paths=['/model/source_calibration/intersalt_bmi_coefficient_per_kg_m2'], slope_di=[6,8], slope_patterns=['slopes =', 'slopes['], slope_key=('source_calibration','intersalt_bmi_coefficient_per_kg_m2'), residual_paths=['/model/innovations'], residual_di=[9,10,11], residual_patterns=['inn =','errors =','dbp =','pulse_pressure =','sbp ='], residual_key=('innovations',), group=None, transform='Standardized independent beta DBP/PP errors with SDs 9/12; SBP error equals their sum.', note='Cov(S,D)=81; SD(S)=15, SD(D)=9; requested rho=0.6. No literal SBP-DBP rho is supplied.', rho=.6, sds=[15,9], covariance=[[225,81],[81,81]], law_note='Bounded covariates and beta errors; no outcome transformation after component addition.'),
 'PNS_OA_ASTRA_C2': dict(slope_paths=['/model/outcome_model/bmi_anchor_per_kg_m2'], slope_di=[6], slope_patterns=['bmi_coef =','bmi =','h =','y ='], slope_key=('outcome_model','bmi_anchor_per_kg_m2'), residual_paths=['/model/calibration','/model/residual_law','/model/outcome_model/hinge_coefficients'], residual_di=[7,8,9,10], residual_patterns=['raw =','raw[','explained','innovation_covariance','h =','y ='], residual_key=('calibration',), group='65plus', transform='Reconstruct source raw covariance; subtract hypothetical reference explained covariance; generate bounded elliptical errors. Requested OLS residuals additionally retain the age-65 hinge omitted from the analysis design.', note='Innovation rho and requested OLS residual rho differ. FWL preserves BMI slopes because residualized BMI is independent of the hinge. See inherited reviewer algebra, not a new synthetic/clinical result.', rho=0.5685432918552262, sds=[20.079417984055475,10.77660360476036], covariance=[[403.1830265784104,123.02590503274236],[123.02590503274236,116.135185254134]], law_note='A nonlinear age hinge remains in the requested linear-regression residual; its covariance must be added to innovation covariance.'),
 'PNS_OA_SOL_C1': dict(slope_paths=['/model/bp/bmi_slopes_per5'], slope_di=[9], slope_patterns=['bmi_x[:, None]'], slope_key=('bp','bmi_slopes_per5'), per5=True, residual_paths=['/model/bp/conditional_sd_mmHg','/model/bp/residual_correlation','/model/bp/innovation_beta_shapes'], residual_di=[10,11,12], residual_patterns=['rho =','sd_s, sd_d','errors ='], residual_key=('bp',), group=None, transform='Mix standardized independent beta factors using direct assumed rho 0.55; scale by SDs 16/10.', note='Final covariance [[256,88],[88,100]]; no outcome clipping or rejection.', rho=.55,sds=[16,10],covariance=[[256,88],[88,100]],law_note='Bounded additive law; correct mean design means innovations equal population projection residuals.'),
 'PNS_OA_SOL_C2': dict(slope_paths=['/model/bp/bmi_slope_per_kg_m2'],slope_di=[13],slope_patterns=['bmi_slope_per_kg_m2'],slope_key=('bp','bmi_slope_per_kg_m2'), residual_paths=['/model/bp/shared_innovation_loadings','/model/bp/specific_innovation_loadings','/model/innovations'],residual_di=[14,15,16],residual_patterns=['z =','values =','innovation_loadings'],residual_key=('bp',),group=None,transform='Standardized shared/specific uniforms with shared loadings 12/6 and specific loadings 9/8.',note='SDs sqrt(12^2+9^2)=15 and sqrt(6^2+8^2)=10; covariance 72; rho=0.48.',rho=.48,sds=[15,10],covariance=[[225,72],[72,100]],law_note='Standardization and affine factor mixing; no outcome clipping or rejection.'),
 'PNS_DS_PRO_C1': dict(slope_paths=['/model/linear_predictor/sbp/bmi_z','/model/linear_predictor/dbp/bmi_z'],slope_di=[4,5],slope_patterns=['sbp_lp =','dbp_lp ='],slope_key=None,per5=True,residual_paths=['/model/residual','/model/derived_marginal_moments'],residual_di=[6,7],residual_patterns=['r =','cov_sdp =','resid ='],residual_key=('residual',),group='overall',transform='Author subtracts assumed explained covariance from transported source marginal covariance, then stores rounded literal residual SD/rho. Program uses literals, not explanatory derived_marginal_moments.',note='The actual final-law rho is the literal 0.49151387. Author declares 0.4915139, a rounded approximation. Derived metadata is not an executed calibration step.',rho=.49151387,sds=[17.9863291885,10.348927211],covariance=None,law_note='Clipping age/BMI to their already-generated supports is an identity in the ideal law; normal BP errors are unbounded.'),
 'PNS_DS_PRO_C2': dict(slope_paths=['/model/bp/beta_sbp/bmi_c','/model/bp/beta_dbp/bmi_c'],slope_di=[3,4],slope_patterns=['mu_sbp =','mu_dbp ='],slope_key=None,per5=True,residual_paths=['/model/bp/residual_sd','/model/bp/residual_correlation'],residual_di=[5,6],residual_patterns=['sd_s =','sd_d =','rho =','eps ='],residual_key=('bp',),group=None,transform='Direct assumed bivariate-normal outcome errors with SDs 13/8.5 and rho 0.5.',note='Age/BMI are generated by rejection, so their normal proposal means/SDs are not final truncated moments. BP is linear in the final observed covariates with independent errors; its requested slopes/rho remain valid.',rho=.5,sds=[13,8.5],covariance=[[169,55.25],[55.25,72.25]],law_note='Rejection changes covariate distributions only; no BP truncation/rejection is applied.')
}

def getpath(x, keys):
    for key in keys: x=x[key]
    return x

records=[]
for outcome in read(R1+'/CONSTRUCTION_OUTCOMES.json')['records']:
    if outcome['case_id'] != 'PNS': continue
    vid=outcome['construction_id']
    base=R1+'/candidates/'+vid
    rec=dict(round='R1',version_id=vid,case_id='PNS',kind='initial',parent_version_id=None,
        model_config=outcome['model_config'],context=outcome['context'],independent_author=True,
        artifact_status='complete' if outcome['status']=='sealed' else 'incomplete_response',
        artifact_paths=[R1+'/CONSTRUCTION_OUTCOMES.json'],parameters=[],endpoint_claims={},review_change=None,
        failure_reason=outcome['failure_reason'],limitations=common_limits.copy(),
        results_join=dict(path=R1+'/EVALUATION.json',id=vid), scientific_eligibility='law_available' if outcome['status']=='sealed' else 'not_delivered')
    if outcome['status']!='sealed':
        rec['endpoint_claims']={aid:dict(declared_population_value=None,validated_population_value=None,validation_status='unavailable',note='No complete scientific artifact; do not infer parameters from partial output.') for aid in endpoints}
        rec['execution_status']='candidate_unavailable'
        records.append(rec);continue
    m=read(base+'/model_spec.json')['model'];d=read(base+'/decision_record.json');c=cfg[vid]
    rec['artifact_paths'] += [base+'/'+f for f in ['model_spec.json','generator.py','decision_record.json']]
    rec['artifact_paths'].append(R1+'/provenance_review/PNS_CORE_REVIEW.json')
    rec['artifact_sha256']={f:hashlib.sha256((P/base/f).read_bytes()).hexdigest() for f in ['model_spec.json','generator.py','decision_record.json']}
    val=getpath(m,c['slope_key']) if c['slope_key'] else ([m['linear_predictor'][k]['bmi_z'] for k in ['sbp','dbp']] if vid.endswith('C1') else [m['bp'][k]['bmi_c'] for k in ['beta_sbp','beta_dbp']])
    rec['parameters'].append(slope_parameter(base,m,c['slope_paths'],c['slope_di'],c['slope_patterns'],val,c.get('per5',False)))
    rv=getpath(m,c['residual_key'])
    if vid=='PNS_OA_SOL_C1': rv={k:rv[k] for k in ['conditional_sd_mmHg','residual_correlation','innovation_beta_shapes']}
    if vid=='PNS_OA_SOL_C2': rv={k:rv[k] for k in ['shared_innovation_loadings','specific_innovation_loadings']}
    if vid=='PNS_DS_PRO_C2': rv={k:rv[k] for k in ['residual_sd','residual_correlation']}
    if vid=='PNS_OA_ASTRA_C2': rv=dict(calibration=rv,hinge_coefficients=m['outcome_model']['hinge_coefficients'],residual_law=m['residual_law'])
    assumptions=['Homoscedastic error law and distribution family are assumptions.']
    if c['group']: assumptions += ['Source marginal dispersion transfers across age, selection, geography and measurement.', 'Explained-covariance decomposition uses assumed covariate distributions and effects; rounded source moments treated as plug-in values.']
    else: assumptions += ['The packet does not identify the chosen conditional covariance or individual SDs.']
    rec['parameters'].append(residual_parameter(base,rv,c['residual_paths'],c['residual_di'],c['residual_patterns'],c['group'],c['transform'],c['note'],assumptions))
    covariance=c['covariance'] or [[c['sds'][0]**2,c['rho']*c['sds'][0]*c['sds'][1]],[c['rho']*c['sds'][0]*c['sds'][1],c['sds'][1]**2]]
    rec['analytic_residual_moments']={'outcome_order':['sbp','dbp'],'sd_mmHg':c['sds'],'covariance_mmHg2':covariance,'rho':c['rho'],'scope':'Requested population OLS residuals under the fixed assumed law; not target or synthetic sample estimates.'}
    if vid=='PNS_OA_ASTRA_C2':rec['analytic_residual_moments']['innovation_distinction']=old_by_id[vid]['core_choices'][1]['reviewer_math']
    rec['endpoint_claims']={aid:dict(declared_population_value=declared(d,aid),validated_population_value=value,validation_status='exact_law',note=c['note'] if aid=='residual_correlation' else old_by_id[vid]['core_choices'][0]['projection_check']) for aid,value in zip(endpoints,[3.877,2.9835,c['rho']])}
    rec['execution_status']='success_existing_frozen_evaluation'
    rec['mathematical_status']='Core final-law claims statically consistent, conditional on stated assumptions; floating-point numbers approximate analytic law.'
    rec['limitations'] += [c['law_note']]
    records.append(rec)

# R2 uses the same packet; only static algebra of fixed stored inputs is evaluated.
for outcome in read(R2+'/INITIAL_OUTCOMES.json')['records']:
    if outcome['case_id']!='PNS':continue
    vid=outcome['parent_id'];base=R2+'/'+outcome['candidate_path'];m=read(base+'/model_spec.json')['model'];d=read(base+'/decision_record.json')
    rec=dict(round='R2',version_id=vid,case_id='PNS',kind='initial',parent_version_id=None,
        model_config=outcome['model_config'],context=outcome['context'],independent_author=True,artifact_status='complete',
        artifact_paths=[R2+'/calls/initial/'+vid+'/artifact.json']+[base+'/'+f for f in ['model_spec.json','generator.py','decision_record.json']],
        artifact_sha256={f:hashlib.sha256((P/base/f).read_bytes()).hexdigest() for f in ['model_spec.json','generator.py','decision_record.json']},parameters=[],endpoint_claims={},review_change=None,limitations=common_limits.copy(),
        results_join=dict(path=R2+'/EVALUATION.json',id=vid),scientific_eligibility='law_available')
    if vid=='PNS_SOL_A':
        slopes=m['bp']['transported_bmi_coefficients_per_kg_m2'];sp=['/model/bp/transported_bmi_coefficients_per_kg_m2'];di=[5];pat=['slopes =','means = means']
        rv={k:m['bp'][k] for k in ['residual_sd_mmHg','residual_mixing_matrix','residual_latent_family','residual_latent_uniform_support']};rp=['/model/bp/residual_sd_mmHg','/model/bp/residual_mixing_matrix'];rdi=[6,7];rpat=['u =','errors ='];group=None
        transform='Independent standardized uniforms mixed with rows [1,0] and [0.6,0.8], then scaled 14/9.';rho=.6;sds=[14,9];covmat=[[196,75.6],[75.6,81]]
        note='Correct additive final-law claims; bounded support already guarantees SBP>DBP. No seed-specific fitting.';slopesout=[3.877,2.9835]
    elif vid=='PNS_SOL_B':
        slopes=m['bp_mean']['bmi_effect_per_kg_m2'];sp=['/model/bp_mean/bmi_effect_per_kg_m2'];di=[9];pat=['bmi_effect =','mean =']
        rv={'bp_dispersion_bridge':m['bp_dispersion_bridge'],'bp_mean':m['bp_mean'],'covariates':m['covariates'],'residual_law':m['residual_law']};rp=['/model/bp_dispersion_bridge','/model/residual_law'];rdi=[10,11];rpat=['root_variances =','loadings =','mean_covariance','residual_covariance','disk ='];group='overall'
        loads=[[5.3877,-2.2246,21.7112],[1.29835,-0.4033,16.7076]];vars_=[3599/1200,1/4,2/63]
        K=[[sum(loads[i][k]*loads[j][k]*vars_[k] for k in range(3)) for j in range(2)] for i in range(2)]
        V=[[414.1225,118.8737],[118.8737,119.4649]];covmat=[[V[i][j]-K[i][j] for j in range(2)] for i in range(2)]
        sds=[math.sqrt(covmat[i][i]) for i in range(2)];rho=covmat[0][1]/(sds[0]*sds[1]);slopesout=[3.877,2.9835]
        transform='Reconstruct transported Beijing raw covariance, subtract analytic covariance of modeled conditional means, realize remainder with uniform radius-2 disk.'
        note='Numeric rho is reviewer scalar algebra of the author-supplied exact expression, not a new generator run; author supplied expression rather than numeric scalar.'
        rec['static_derivation']={'mean_covariance_K_mmHg2':K,'reference_marginal_covariance_V_mmHg2':V,'residual_covariance_formula':'R=V-K','scalar_algebra_only':True}
    elif vid=='PNS_ASTRA':
        slopes=m['bp']['source_bmi_slopes_mmHg_per_kg_m2'];sp=['/model/bp/source_bmi_slopes_mmHg_per_kg_m2','/model/bp/omitted_score_mean_coefficients'];di=[5,7,9];pat=['slopes =','score_mean =','outcomes =']
        rv={k:m['bp'][k] for k in ['factor_loadings_mmHg','factor_support','factor_family','omitted_score_mean_coefficients']};rp=['/model/bp/factor_loadings_mmHg','/model/bp/factor_support'];rdi=[10,11];rpat=['loadings =','innovations =','outcomes ='];group=None
        transform='Four independent Uniform(-1,1) factors with loadings [4,12,16,0] / [3,9,0,12]; factor variance 1/3.'
        rho=5/13;sds=[math.sqrt(416/3),math.sqrt(78)];covmat=[[416/3,40],[40,78]];slopesout=[4.677,3.5835]
        note='Omitted-score conditional mean adds 0.8/0.6 to the source-scaled BMI slopes. Residual rho=5/13 follows from assumed factor loadings; neither correction is reported source evidence.'
    else:
        slopes=[m['outcome_model']['linear_predictors'][x]['bmi_per_5kgm2'] for x in ['sbp','dbp']];sp=['/model/outcome_model/linear_predictors'];di=[4,5];pat=['mu_sbp =','mu_dbp =']
        rv=m['outcome_model']['residual'];rp=['/model/outcome_model/residual'];rdi=[8,9,10,11];rpat=['res =','residual =','return df'];group=None
        transform='Direct constant bivariate-normal residual law with SDs 15/9 and rho 0.5.';rho=.5;sds=[15,9];covmat=[[225,67.5],[67.5,81]];slopesout=[3.877,2.9835]
        note='Law claims are coherent, but author code returns df[task.columns] with descriptor dictionaries; all planned execution seeds failed. No delivered-data claim follows.'
    rec['parameters'].append(slope_parameter(base,m,sp,di,pat,slopes,vid=='PNS_DS',vid=='PNS_ASTRA'))
    assumptions=['Residual family/structure and homoscedasticity are assumptions.']
    assumptions+=['Source marginal moments transfer and assumed mean/covariate law permits the subtraction.'] if group else ['No compatible source conditional covariance/SD estimate identifies these values.']
    rec['parameters'].append(residual_parameter(base,rv,rp,rdi,rpat,group,transform,note,assumptions))
    rec['analytic_residual_moments']={'outcome_order':['sbp','dbp'],'sd_mmHg':sds,'covariance_mmHg2':covmat,'rho':rho,'scope':'Requested population OLS residuals under the fixed assumed law; not target or synthetic sample estimates.'}
    rec['endpoint_claims']={aid:dict(declared_population_value=declared(d,aid),validated_population_value=value,validation_status='exact_law',note=note if aid=='residual_correlation' else ('Exact additive completed-law coefficient; not an identified target coefficient. '+('Assumed omitted-score adjustment shifts the source anchor.' if vid=='PNS_ASTRA' else ''))) for aid,value in zip(endpoints,slopesout+[rho])}
    rec['execution_status']='failed_all_planned_seeds' if vid=='PNS_DS' else 'success_existing_frozen_evaluation'
    rec['execution_status_locator']=R2+'/EVALUATION_CLOSURE.json#/records'
    rec['mathematical_status']='Static final-law algebra valid; implementation delivery is separate.'
    if vid=='PNS_DS':rec['limitations']+=['Author ABI defect: TypeError unhashable type dict; no host repair. Analytic values characterize the declared law, not a delivered dataset.']
    records.append(rec)

parent=next(x for x in records if x['round']=='R2' and x['version_id']=='PNS_SOL_A')
for suffix in ['SECOND_LOOK','FEEDBACK']:
    vid='PNS_SOL_A_'+suffix;artifact=read(R2+'/calls/review/'+vid+'/artifact.json');initial=read(R2+'/calls/initial/PNS_SOL_A/artifact.json')
    assert artifact['model_spec']==initial['model_spec'] and artifact['generator_py']==initial['generator_py']
    rec=copy.deepcopy(parent);rec.update(version_id=vid,kind='review',parent_version_id='PNS_SOL_A',independent_author=False,
        review_change='retained_noop: exact model dictionary and generator string unchanged; decision prose revised only',
        arm='second_look' if suffix=='SECOND_LOOK' else 'feedback',
        results_join=dict(path=R2+'/EVALUATION.json',id=vid))
    rec['artifact_paths'].append(R2+'/calls/review/'+vid+'/artifact.json')
    rec['review_artifact_sha256']=hashlib.sha256((P/R2/'calls/review'/vid/'artifact.json').read_bytes()).hexdigest()
    rec['limitations'].append('Review branch shares the same parent construction and must not be counted as an independent scientific author.')
    records.append(rec)

sources=copy.deepcopy(old['source_contexts'])
sources['S_INTERSALT']['transport_status']='Not an identified PNS age/sex-only estimand. Complete PNS constructions in both rounds use these numerical anchors with explicit, differing adjustment and population-transfer assumptions.'
for sid in sources:
    sources[sid]['packet_paths']=[R1+'/packets/PNS/evidence.json',R2+'/packets/PNS/evidence.json']
    sources[sid]['original_paper_reauthenticated_for_this_map']=False
data=dict(schema_version=1,case_id='PNS',scope='Retrospective static scientific attribution of 14 initial attempts and 2 unchanged review branches across two completed API pilots. Core BMI-coefficient and BP residual-law map; not an exhaustive covariate-law or marginal-diagnostic audit. No new APIs, generator runs, patient analyses or source reauthentication.',
    denominator={'initial_attempts':14,'complete_initial_artifacts':10,'initial_generators_with_delivered_data':9,'incomplete_initial_responses':4,'complete_but_execution_failed_initial':1,'review_lineage_rows':2,'independent_review_authors_added':0},
    sources=sources,source_packet_sha256=hashlib.sha256((P/R1/'packets/PNS/evidence.json').read_bytes()).hexdigest(),source_packets_identical=(P/R1/'packets/PNS/evidence.json').read_bytes()==(P/R2/'packets/PNS/evidence.json').read_bytes(),records=records,
    endpoint_claim_semantics='All numeric endpoint claims are static fixed-law values. They are not observed synthetic estimates or target values; mathematical precision is limited by stored decimal parameters. R1 Astra_C2 is inherited independently audited algebra; R2 Sol_B is scalar evaluation of its analytic expression.',
    no_original_paper_recertification=True,no_author_code_execution=True,no_api_calls=True)
assert len(records)==16 and len({(x['round'],x['version_id']) for x in records})==16
assert sum(x['kind']=='initial' for x in records)==14
assert all(set(x['endpoint_claims'])==set(endpoints) for x in records)
for row in records:
    for path in row['artifact_paths']:
        assert (P/path).exists(),path
(U/'PNS_PARAMETER_MAP.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

text=['# PNS parameter provenance across both completed API pilots','',
'This is a retrospective static map, not a new experiment or original-paper verification. It covers **14 initial attempts: 10 complete artifacts, 9 generators delivering data, 4 incomplete responses, and 1 complete artifact with execution failure**. Two unchanged review branches are separate lineage rows, not additional independent authors. No API or author code was run. Source packets are byte-identical across rounds.','',
'The table reports **population functionals of the specified laws**, not synthetic sample estimates or clinical reference values. Root-owned synthesis joins the immutable evaluation summaries separately. Slopes use mmHg per 5 kg/m2. SDs below concern residuals of the requested age/sex/BMI linear projections.','',
'| Round / initial or branch | Availability | Model-law BMI slopes: SBP / DBP | Model-law residual rho | Residual SD: SBP / DBP | Evidence route |','| --- | --- | --- | --- | --- | --- |']
for r in records:
    if r['artifact_status']!='complete': vals=['unavailable']*4;route='No complete artifact; no parameter inferred'
    else:
        ep=r['endpoint_claims'];sl=[ep[a]['validated_population_value'] for a in ['bmi_sbp','bmi_dbp']]
        vals=[r['execution_status'],f'{sl[0]:.6g} / {sl[1]:.6g}',f"{r['analytic_residual_moments']['rho']:.6g}",' / '.join(f'{v:.6g}' for v in r['analytic_residual_moments']['sd_mmHg'])]
        route='Source BMI anchor + assumed residual law'
        if r['parameters'][1]['source_ids']:route='Source BMI anchor + marginal-source covariance/assumed decomposition'
        if r['version_id']=='PNS_ASTRA':route='Source BMI anchor + assumed omitted-adjustment score and factors'
        if r['kind']=='review':route='Same PNS_SOL_A law; no independent author'
    if r['artifact_status']!='complete':vals=['incomplete response','—','—','—']
    text.append('| '+f"{r['round']} {r['version_id']}"+' | '+' | '.join(vals)+' | '+route+' |')
text += ['', '## Main distinctions', '',
'- All ten complete initial artifacts use the same INTERSALT numerical anchors. Nine specify requested BMI slopes 3.877/2.9835. R2 PNS_ASTRA adds an explicitly assumed omitted-adjustment contribution and instead implies 4.677/3.5835. Source copying, scale conversion, and target applicability are three separate steps.',
'- **No source reports the requested target residual correlation.** Some authors assume it or factor loadings. Others transport Beijing marginal moments and subtract covariance explained by assumed covariates/effects. The latter is reported + derived + assumed, not source-identified conditional evidence.',
'- R1 PNS_OA_ASTRA_C2 has innovation rho 0.578048 but requested linear-regression residual rho 0.568543 because an age hinge remains after the requested adjustment. Its author left the scalar null; the validated scalar comes from prior reviewer algebra. Do not plot the innovation rho as its requested endpoint.',
'- R1 PNS_DS_PRO_C1 uses literal residual rho 0.49151387 and literal SDs in execution. Its derived_marginal_moments block is explanatory metadata. The author-declared rho 0.4915139 is rounded; neither is an empirically measured result.',
'- R1 PNS_DS_PRO_C2 truncates age/BMI proposals, so their proposal means/SDs are not final covariate moments. Its additive BP law is evaluated on the final covariates; this does not invalidate the stated BP slopes or residual rho.',
'- R2 PNS_SOL_B correctly supplies a source-marginal-minus-explained covariance formula. This map evaluates that fixed analytic expression with scalar arithmetic only; it does not generate data.',
'- R2 PNS_DS has coherent abstract law claims but its output interface fails in all three existing evaluation slots. Treat it as **no delivered dataset**, not an inaccurate dataset. Frozen code is untouched.',
'- Both PNS review branches are exact code/specification no-ops. Additional explanatory detail is not additional scientific evidence or an independent construction.', '',
'## Traceability and use', '',
'`PNS_PARAMETER_MAP.json` contains every attempt, exact version IDs, source IDs and original locators, reported versus implemented quantities, operator/adjustment bridges, code lines, specification/decision pointers, artifact hashes, and endpoint claims. `provenance_components` deliberately permits multiple labels: deriving a number from a publication does not eliminate transport or model assumptions. Missing responses retain empty parameter lists and unavailable endpoints.', '',
'The main source is INTERSALT, Table II p322, with additionally adjusted inverse-variance-pooled within-centre coefficients. Beijing Table 1 contributes unadjusted marginal SDs only, when actually used. Study-specific means, age composition, device/measurement protocols, and selection remain different from the requested analytical population. The supplied standard errors quantify source coefficient estimation, not individual variation or uncertainty in transfer.', '',
'Numerical agreement of an output with this map can establish implementation fidelity to a chosen law. Only the separate scientific evaluation addresses agreement with the study reference. Repeated use of one anchor is not repeated independent external evidence.']
text += ['', 'Residual covariance contributes to the `sbp.sd_population` and `dbp.sd_population` diagnostics, but does not identify either marginal SD by itself. Marginal BP variation also includes variation in modeled conditional means over the covariate distribution. This core parameter map does not exhaustively audit every covariate choice or marginal diagnostic; unmatched diagnostics remain unassessed.']
(U/'PNS_PARAMETER_MAP.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
print(json.dumps({'records':len(records),'initials':14,'artifacts':10,'outputs':['PNS_PARAMETER_MAP.json','PNS_PARAMETER_MAP.md'],'r2_sol_b_rho':next(r for r in records if r['round']=='R2' and r['version_id']=='PNS_SOL_B')['analytic_residual_moments']['rho']}))
