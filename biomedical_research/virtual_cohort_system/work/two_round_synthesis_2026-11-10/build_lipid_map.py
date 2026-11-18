"""Static retrospective normalization only; never imports or runs a candidate."""
import copy
import hashlib
import json
import math
from pathlib import Path

P = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
R1 = P / 'work/cross_model_api_pilot_2026-11-10'
R2 = P / 'work/economy_feedback_pilot_2026-11-10'
EP = ['K02-HDL-BMI', 'K02-TC-BMI', 'K02-LIPID-RESIDUAL']
AG = 'agongo_2018_navrongo'
OB = 'obirikorang_2015_ashanti'
GR = 'greiner_2021'
DIAG = ['total_cholesterol.sd_sample', 'hdl_cholesterol.sd_sample', 'hdl_above_total_fraction']

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def rel(p):
    return p.relative_to(P).as_posix()

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

old = read(R1 / 'provenance_review/LIPID_CORE_REVIEW.json')
evidence = read(R1 / 'packets/LIPID/evidence.json')
anchors = copy.deepcopy(old['source_dictionary'])
alias_ids = {a: AG if a.startswith('AGONGO') else OB if a.startswith('OBIRI') else GR for a in anchors}
for alias, a in anchors.items():
    a['native_source_id'] = alias_ids[alias]
    a['packet'] = rel(R1 / 'packets/LIPID/evidence.json')
anchors['GREINER_MOMENTS']['path'] = '/sources/1/reported_statistics/rows'
anchors['GREINER_MOMENTS']['locator'] = 'Tables 1–2; Uganda sex-specific age quantiles and BMI/lipid geometric means'
greiner = evidence['sources'][1]['reported_statistics']
greiner_rows = []
for i, row in enumerate(greiner['rows']):
    r = dict(zip(greiner['columns'], row))
    if r['context'].startswith('uganda') and r['variable'] in ['age','bmi','total_cholesterol','hdl_cholesterol']:
        greiner_rows.append({'id': r['id'], 'value': r['estimate'], 'unit': r['unit'], 'locator': r['locator'], 'packet_pointer': f'/sources/1/reported_statistics/rows/{i}'})
anchors['GREINER_MOMENTS']['recoverable_rows'] = greiner_rows
sources = {}
for sid in [AG, OB, GR]:
    s = next(x for x in evidence['sources'] if x['curator_source_id'] == sid)
    sources[sid] = {'doi': s['doi'], 'title': s['title'], 'extraction_status': 'Captured curator transcription; not freshly authenticated against original paper', 'anchors': {a:v for a,v in anchors.items() if alias_ids[a] == sid}}

def provenance(aliases):
    return list(dict.fromkeys(alias_ids[a] for a in aliases))

def param(pid, name, value, unit, aliases, components, transformation, assumptions, locators, endpoints=None, note=''):
    return {'parameter_id': pid, 'name': name, 'value': value, 'unit': unit,
            'source_ids': provenance(aliases),
            'source_reported_value': {a: anchors[a].get('values') for a in aliases} if aliases else None,
            'source_operator': '; '.join(a + ': ' + anchors[a].get('operator', '') for a in aliases) if aliases else 'No source statistic identifies these completion parameters.',
            'provenance_components': components, 'transformation': transformation,
            'transport_assumptions': assumptions, 'actual_code_use': 'verified',
            'locators': locators, 'analysis_ids': endpoints or EP + DIAG, 'mathematical_note': note}

def make_record(round_, name, directory, kind='initial', parent=None):
    unit = R1 if round_ == 'R1' else R2
    files = [directory / x for x in ['generator.py','model_spec.json','decision_record.json']]
    call = unit / ('calls/' + name + '_initial' if round_ == 'R1' else 'calls/' + kind + '/' + name)
    if (call / 'artifact.json').exists(): files.append(call / 'artifact.json')
    return {'round': round_, 'version_id': name, 'case_id': 'lipids', 'kind': kind, 'parent_version_id': parent,
            'artifact_status': 'complete', 'artifact_paths': [rel(x) for x in files], 'artifact_sha256': {rel(x):sha(x) for x in files},
            'parameters': [], 'endpoint_claims': {}, 'review_change': None, 'limitations': []}

def claims(directory, status, validated=None, note=''):
    decisions = read(directory / 'decision_record.json').get('requested_estimands', [])
    if isinstance(decisions, dict): decisions = list(decisions.values())
    result = {}
    for eid in EP:
        d = next((d for d in decisions if isinstance(d,dict) and d.get('analysis_id',d.get('id')) == eid), {})
        v = None
        for key in ['exact_model_implied_population_value','model_implied_population_value','value']:
            x = d.get(key)
            if isinstance(x,(int,float)) and not isinstance(x,bool): v = x; break
        result[eid] = {'declared_population_value': v, 'validated_population_value': validated.get(eid) if validated else None,
                       'validation_status': status, 'note': note, 'locator': rel(directory / 'decision_record.json') + '#/requested_estimands'}
    return result

records = []
old_records = {r['construction_id']:r for r in old['constructions']}
old_ids = [f'LIPID_{model}_C{context}' for context in [1,2] for model in ['OA_ASTRA','DS_PRO','CL_FABLE','GE_CARBON','OA_SOL']]
exact_values = {
 'LIPID_DS_PRO_C1': [-0.96675, 7.734, 0.14],
 'LIPID_CL_FABLE_C1': [-1.1601, 9.6675, 0.35],
 'LIPID_CL_FABLE_C2': [-1.063425, 9.6675, 0.33/math.sqrt(0.33**2+0.8**2)],
 'LIPID_OA_SOL_C1': [-1.542933, 8.1187665, 0.15],
}
classes = {
 'LIPID_DS_PRO_C1': [['reported','derived','assumed'],['assumed'],['derived','assumed'],['assumed']],
 'LIPID_DS_PRO_C2': [['reported','derived','assumed'],['reported','derived','assumed'],['assumed'],['assumed']],
 'LIPID_CL_FABLE_C1': [['assumed'],['assumed'],['derived','assumed'],['assumed']],
 'LIPID_CL_FABLE_C2': [['assumed'],['derived','assumed'],['derived','assumed'],['derived','assumed']],
 'LIPID_OA_SOL_C1': [['reported','derived','assumed'],['derived','assumed'],['reported','derived','assumed']],
}
for name in old_ids:
    if 'GE_CARBON' in name:
        receipt = R1 / 'calls' / (name + '_initial') / 'receipt.json'
        records.append({'round':'R1','version_id':name,'case_id':'lipids','kind':'initial','parent_version_id':None,
          'artifact_status':'incomplete_response','artifact_paths':[rel(receipt)],'artifact_sha256':{rel(receipt):sha(receipt)},
          'capture_status': {'finish_reason':'MAX_TOKENS','usable_artifact':False}, 'parameters':[],
          'endpoint_claims':{e:{'declared_population_value':None,'validated_population_value':None,'validation_status':'unavailable','note':'No complete scientific artifact was delivered.'} for e in EP},
          'review_change':None,'limitations':['No parameters inferred from an incomplete or hidden response. Included in the attempted-construction denominator.']})
        continue
    directory = R1 / 'candidates' / name
    rec = make_record('R1', name, directory)
    m = read(directory/'model_spec.json')['model']
    audit = old_records[name]
    rec['family'] = audit['family']
    rec['prior_audit_locator'] = rel(R1/'provenance_review/LIPID_CORE_REVIEW.json') + '#/constructions/' + str(list(old_records).index(name))
    for i, core in enumerate(audit['core']):
        loc = [rel(directory/'model_spec.json') + '#' + p for p in core['spec_paths']]
        loc += [rel(directory/'generator.py') + ':' + str(n) for n in core['actual_code_use']['lines']]
        loc += [rel(directory/'decision_record.json') + '#/parameter_provenance']
        aliases = core['source_refs']
        c = classes.get(name, [['reported','derived','assumed']]*len(audit['core']))[i]
        p = param('core_' + str(i+1), core['core_choice'], core['value'], core['unit'], aliases, c, core['review'],
          ['External population/measurement transfer is unvalidated; the implemented conditioning and operator are those stated here.',
           'Reported input values do not establish the final target-adjusted relationship; assumed components remain assumptions.'],
          loc, core.get('requested_estimands', EP+DIAG), 'Value can include explicitly labelled algebraic consequences as well as direct settings. Source SD is individual dispersion, not parameter uncertainty.')
        rec['parameters'].append(p)
    if name in exact_values:
        rec['endpoint_claims'] = claims(directory,'exact_law',dict(zip(EP,exact_values[name])),audit['requested_estimand_claim_review'] + ' Exactness is under this fixed mathematical law, not evidence that its assumptions identify a target population.')
    elif name == 'LIPID_DS_PRO_C2':
        rec['endpoint_claims'] = claims(directory,'not_established',note=audit['requested_estimand_claim_review'])
    else:
        rec['endpoint_claims'] = claims(directory,'derived_recipe_only',note=audit['requested_estimand_claim_review'] + ' Numerical population values were not computed in this synthesis.')
    if name == 'LIPID_OA_ASTRA_C1':
        extra = {'sex':m['sex'],'age':m['age'],'BMI_GM':m['marginals']['geometric_mean_by_sex']['bmi'],'BMI_shape_reference':m['marginals']['shape_reference_arithmetic_mean_sd']['bmi'],'age_latent_correlations':m['dependence']['age_latent_correlations']}
        aliases = ['GREINER_MOMENTS','AGONGO_BMI']; components=['reported','derived','assumed']
        transform = 'Uganda BMI geometric means and age quartiles are retained; Ghana BMI CVs supply log-shape. Linear age-quantile interpolation, exponential tail scales 14/13, equal sex mixture and age latent links [0.15,0.20,0.05] are assumed.'
        note = 'Geometric mean is not arithmetic mean. Cross-source CV borrowing does not preserve Ghana lipid SDs. No clipping, rejection or component ordering. Upper age tail is unbounded.'
        rec['limitations'].append('Prior audit incorrectly stated the packet used reported_statistics.records. The actual captured packet uses reported_statistics.rows; declared row locators and IDs are recoverable. This synthesis corrects only its own locator.')
    elif name == 'LIPID_OA_ASTRA_C2':
        extra={k:m[k] for k in ['sex','age','bmi']};extra['age_latent_correlations']=m['dependence']['age_latent_correlations_with_remaining']
        aliases=['AGONGO_BMI'];components=['reported','derived','assumed']
        transform='Sex-specific BMI moments are reported inputs converted to lognormal margins; age-gap means 22/24, SDs 14/14, equal sex mixture and age latent links are assumptions.'
        note='Lipid sex ratios 1.08/1.04 and a shared conditional log-variance solve stipulated pooled first/second moments, not conditional residual variance. No clipping, rejection or ordering; unbounded age tail.'
    elif name == 'LIPID_OA_SOL_C2':
        extra={'recorded_sex':m['recorded_sex'],'age':m['margins']['age'],'bmi':m['margins']['bmi'],'latent_links':m['dependence']['latent_links']}
        aliases=['AGONGO_BMI'];components=['reported','derived','assumed']
        transform='Reported pooled BMI moments become a lognormal margin; shifted-lognormal age, sex threshold and all seven demographic latent links are assumed.'
        note='Thresholded sex contributes raw covariance. Requested coefficients require the full raw covariance projection, not the rank triple. No component ordering or outcome rejection.'
    elif name == 'LIPID_OA_SOL_C1':
        extra={'sex':m['sex'],'age':m['age'],'bmi':m['bmi'],'lipid_age_slopes':m['lipids']['age_slope'],'lipid_F_minus_M':m['lipids']['F_minus_M'],'innovations':'independent Uniform(-sqrt(3),sqrt(3))'}
        aliases=['AGONGO_BMI'];components=['reported','derived','assumed']
        transform='BMI marginal moments anchor a bounded linear covariate law; female-minus-male BMI 1.41 is arithmetic subtraction. Its adjusted interpretation, age effects, lipid demographic effects and uniform shape are assumptions.'
        note='Residual variance subtracts the full linear-mean variance including BMI-age and BMI-sex covariance. Positivity follows from bounded supports (TC lower bound about 0.497, HDL about 0.227 mmol/L); no lipid clipping/rejection.'
    elif name == 'LIPID_DS_PRO_C1':
        extra={'covariates':m['joint_law']['covariates'],'outcome_linear_models':m['joint_law']['outcome_linear_models'],'innovations':'independent Rademacher shared and outcome-specific factors'}
        aliases=[];components=['assumed']
        transform='Independent bounded covariates and raw linear means are completion choices. Errors use sqrt(rho) times a common Rademacher plus sqrt(1-rho) times an independent Rademacher.'
        note='The positivity guard raises rather than conditions or clips; supplied supports keep both outcomes positive. Independent centered errors and full design rank justify exact output projection identities.'
    elif name == 'LIPID_DS_PRO_C2':
        extra={'sex':m['sex'],'age':m['age'],'bmi':m['bmi'],'tc_mean':m['lipids_mmol_L']['tc'],'hdl_mean':m['lipids_mmol_L']['hdl'],'maximum_attempts':1000,'fallback_floor':0.05}
        aliases=[];components=['assumed']
        transform='Sex-specific gamma age and lognormal BMI feed raw linear proposal means. Each bivariate normal lipid proposal is redrawn until both positive, up to 1000 attempts, then floored.'
        note='Acceptance depends on covariates through the means. Accepted errors are not centered independent innovations; proposal slopes, SDs and rho are not established output estimands. This is a final-law derivation issue regardless of its sample magnitude.'
    elif name == 'LIPID_CL_FABLE_C1':
        extra={'covariates':m['covariates'],'TC_mean':m['lipids']['total_cholesterol']['mean_coefficients'],'HDL_mean':m['lipids']['hdl_cholesterol']['mean_coefficients'],'positive_floor':0.05}
        aliases=[];components=['assumed']
        transform='Bounded beta age and sex/age-dependent truncated lognormal BMI feed linear lipid means; shifted-lognormal innovations are independent of covariates.'
        note='The error-copula inversion is valid; its correlation clamp and output floor are inactive for supplied parameters (TC bound >0.358, HDL >0.10 mmol/L). Covariate truncation does not invalidate the exact conditional-mean identity. No TC≥HDL component law.'
    else:
        extra={'covariates':m['covariates'],'hdl':m['lipids']['hdl'],'non_hdl':m['lipids']['non_hdl'],'positive_floor':0.01,'construction':'TC = HDL + non-HDL'}
        aliases=[];components=['derived','assumed']
        transform='Bounded covariates feed separate HDL/non-HDL linear means; centered standardized shifted-lognormal errors use shapes 0.40/0.42 with zero component-error correlation. TC is the sum.'
        note='Component floors are inactive (HDL and non-HDL lower bounds about 0.158 and 0.157 mmol/L). TC≥HDL is structural. HDL/non-HDL rho=0 implies positive TC/HDL residual rho, not zero. Non-HDL SD 0.80 also includes subjective reduction from a hypothetical variance budget.'
    rec['parameters'].append(param('joint_law_completion','Covariates, remaining mean structure and final output law',extra,'Mixed explicitly named raw units / latent correlations',aliases,components,transform,
        ['Unreported age/sex composition, demographic effects, tail shape and measurement/selection transport are scientific completion assumptions.'],
        [rel(directory/'model_spec.json')+'#/model',rel(directory/'generator.py'),rel(directory/'decision_record.json')],note=note))
    rec['limitations'] += ['Fixed plug-in scenario: seeds vary individuals, not evidence/transport parameters. No target validity follows from exact internal algebra.']
    if name in ['LIPID_DS_PRO_C2','LIPID_CL_FABLE_C1','LIPID_CL_FABLE_C2']:
        rec['limitations'] += [x['finding'] for x in audit.get('findings',[])]
    records.append(rec)

for name in ['LIPID_SOL_A','LIPID_SOL_B','LIPID_ASTRA','LIPID_DS','LIPID_SOL_A_FEEDBACK','LIPID_SOL_A_SECOND_LOOK']:
    review = name.endswith('FEEDBACK') or name.endswith('SECOND_LOOK')
    kind='review' if review else 'initial'
    if name == 'LIPID_DS':
        receipt=R2/'calls/initial/LIPID_DS/receipt.json'
        rr=read(receipt)
        records.append({'round':'R2','version_id':name,'case_id':'lipids','kind':'initial','parent_version_id':None,
          'artifact_status':'transport_failure','artifact_paths':[rel(receipt)],'artifact_sha256':{rel(receipt):sha(receipt)},
          'capture_status':{'status':rr.get('status'),'error_type':rr.get('error_type'),'error':rr.get('error')},'parameters':[],
          'endpoint_claims':{e:{'declared_population_value':None,'validated_population_value':None,'validation_status':'unavailable','note':'Response transport ended prematurely; no complete scientific artifact.'} for e in EP},
          'review_change':None,'limitations':['No scientific parameters or scientific-quality judgment attributed to a network/capture failure. No retry.']})
        continue
    directory=R2/'candidates'/kind/name
    rec=make_record('R2',name,directory,kind,'LIPID_SOL_A' if review else None)
    rec['role']='review_branch' if review else 'paired_parent' if name=='LIPID_SOL_A' else 'benchmark'
    m=read(directory/'model_spec.json')['model']
    within = name.startswith('LIPID_SOL_A')
    loc=[rel(directory/'model_spec.json')+'#/model',rel(directory/'generator.py'),rel(directory/'decision_record.json')+'#/parameter_provenance']
    margin = m['margins'] if within else m['marginals']
    rec['parameters'].append(param('marginal_moments','BMI and lipid marginal moments / lognormal family',margin,'BMI kg/m²; lipid arithmetic mean and individual SD mmol/L; age units explicit where included',
      ['AGONGO_BMI','AGONGO_MOMENTS'],['reported','derived','assumed'],
      'Set log variance log(1+(SD/mean)^2), log location log(mean)-log variance/2. '+('Sex-specific BMI moments retained; the same pooled lipid moments are duplicated within both sexes.' if within else 'Pooled BMI and lipid moments are unconditional anchors; demographic associations enter through the copula. Age margin, where included, is assumed.'),
      ['Source moments from restricted-age Ghana adults transport across population, selection and assay protocols.', 'Lognormal shape is assumed; sample SD is a plug-in population dispersion parameter, not estimation uncertainty.'] + (['Pooled lipid margins also apply separately within each recorded sex.'] if within else []),loc,note='Marginal SDs are not residual SDs. Lipid arithmetic moments match under the stipulated family; adjusted slopes/rho require full covariances.'))
    ranks = m['dependence']['conditional_spearman_parameters'] if within else m['latent']['spearman_pairs'] if name=='LIPID_SOL_B' else m['copula']['rank_correlations']
    rec['parameters'].append(param('lipid_rank_block','BMI–TC, BMI–HDL and TC–HDL rank anchors',ranks,
      ('Within-sex' if within else 'Unconditional')+' Spearman correlation; latent Gaussian Pearson after bridge',
      ['OBIRI_RURAL'],['reported','derived','assumed'],'For each continuous pair use latent r=2 sin(pi*Spearman/6). Rural ranks are 0.212, -0.100, 0.106 in BMI–TC, BMI–HDL, TC–HDL order.',
      ['One source community supplies all three dependent summaries; Gaussian copula and source-to-target transport are assumptions.']+(['Pooled-sex source ranks are applied within each target sex stratum.'] if within else []),loc,
      note='Neither source ranks nor latent r are the requested raw age/sex-adjusted slopes or full-design residual Pearson rho. Source pair N/uncertainty unresolved; urban values are not averaged.'))
    demog={'sex':m['sex'],'age':m['age'],'age_bmi_latent_correlation':m['dependence']['age_bmi_latent_correlation']} if within else {'sex':m['sex'],'latent_links':m['latent']['pearson_pairs'] if name=='LIPID_SOL_B' else m['copula']['latent_correlations'],'age':m['marginals']['age'] if name=='LIPID_SOL_B' else m['marginals'][0]}
    rec['parameters'].append(param('demographic_joint_law','Sex composition, age margin and demographic dependence',demog,'Years / probabilities / latent-normal correlations',[],['derived','assumed'],
      ('Draw M/F with probability 0.5/0.5; Z_age=0.3 Z_BMI+sqrt(1-0.3²)Z_ind. Age-gap mean/SD pairs are (24,16)/(26,17). '+('Age=18+82*BetaPPF(Phi(Z_age)); q=m/82, c=m*(82-m)/s²-1, shapes q*c and (1-q)*c.' if name.endswith('FEEDBACK') else 'Moment-match shifted-lognormal age, age=18+gap; no finite upper age endpoint.')) if within else
      'Seven explicit latent demographic correlations complete the joint normal law; sex is a 0.5-probability threshold. Age=18+lognormal gap with mean 22 and SD 15.',
      ['Adult lower boundary 18 comes from task eligibility; upper shape/support, mixture and all demographic dependence parameters are assumed, not source-estimated.'],loc,
      note=('Upper endpoint 100 is a new support assumption, not an observed target maximum or task exclusion. Beta shape algebra preserves the assumed conditional age mean/SD, but changes age covariances and hence may change adjusted estimands.' if name.endswith('FEEDBACK') else 'Demographic dependence participates in the projection; even identical lipid margins/ranks need not give identical adjusted endpoints.')))
    rec['parameters'].append(param('projection_and_support','Full raw-scale projection and component-law interpretation',
      {'design':['1','(age-50)/10',"I(sex=='F')",'(bmi-25)/5'],'mg_dl_per_mmol_l':38.67,'enforce_TC_ge_HDL':False,'outcome_clipping':False,'outcome_rejection':False},
      'Slopes mg/dL per 5 kg/m²; residual Pearson correlation unitless',[],['derived','assumed'],
      'For Z=(age,F,BMI), slope vector C^-1 Cov(Z,L); residual covariance Cov(TC,HDL)-k_TC^T C^-1 k_HDL, divided by residual SD product. '+
      (('Within-sex lognormal covariance is mi*mj*expm1(si*sj*r); mix with covariance of conditional means. '+('For beta age f_s, E[age*L|s]=mean_L*integral f_s(z) exp(tz-t²/2) phi(z) dz, t=logSD_L*r_age,L.' if name.endswith('FEEDBACK') else 'The same lognormal covariance formula applies to the age gap.')) if within else 'Continuous covariance is mi*mj*expm1(si*sj*r). Threshold-sex covariance is mL*[Phi(logSD_L*r-q)-p]; full raw moments feed the normal equations.'),
      ['This is a fixed observed-measurement scenario without a separate assay-error model. It does not establish physiological component coherence.'],
      [rel(directory/'decision_record.json')+'#/structure',rel(directory/'decision_record.json')+'#/requested_estimands',rel(directory/'generator.py')],
      note='No numeric exact endpoint is supplied or retrofitted from samples. Positive nondegenerate copula lipids permit HDL>TC; this is an internal component diagnostic, not an unauthorized exclusion or schema failure.'))
    rec['endpoint_claims']=claims(directory,'derived_recipe_only',note='Correct raw-moment/full-design projection recipe under the stipulated family; no scalar population result independently calculated here. Rank and latent correlations are not substituted as residual correlation.')
    rec['limitations']=['Individual seeds do not propagate source or transport uncertainty.', 'All-adult target transport, recorded sex mapping, distribution shape and assay equivalence are unverified completion assumptions.', 'No new external evidence or target feedback introduced in review.']
    if review:
        rec['arm']='feedback' if name.endswith('FEEDBACK') else 'second_look'
        rec['disposition']='revised' if name.endswith('FEEDBACK') else 'retained_noop'
        rec['selected_candidate_path']=rel(directory if name.endswith('FEEDBACK') else R2/'candidates/initial/LIPID_SOL_A')
        rec['reporting_artifact_path']=rel(R2/'calls/review'/name/'artifact.json')
        rec['review_change']='Only age marginal changed from shifted lognormal to shifted-scaled Beta on [18,100], preserving assumed sex-specific age means/SDs and the latent loading. Projection recipe updated for beta age. Same random draw ordering leaves all non-age columns unchanged for a matched seed.' if name.endswith('FEEDBACK') else 'Generator and model_spec identical to the parent; retained initial candidate. Returned review decision clarifies assumptions and projection recipe; reporting artifact differs and is retained separately.'
        rec['limitations'].append('Both branches use exactly the same parent; only the feedback branch receives its own generated diagnostic summary. Branches are not independent initial authorings.')
    records.append(rec)

# Check immutable candidate bytes against existing stage seals, without importing any code.
checks=[]
for unit,filename,idkey in [(R1,'CONSTRUCTION_CLOSURE.json','construction_id'),(R2,'INITIAL_SEAL.json','parent_id'),(R2,'REVIEW_SEAL.json','branch_id')]:
    seal=read(unit/filename)
    for r in seal['records']:
        if not r[idkey].startswith('LIPID'): continue
        for filename_, expected in r.get('files',{}).items():
            file=unit/r['candidate_path']/filename_
            actual=sha(file)
            assert actual==expected,(file,actual,expected)
            checks.append({'path':rel(file),'sha256':actual,'matches_seal':True})
assert len(records)==16
assert len({x['version_id'] for x in records})==16
for r in records:
    assert len(r['parameters'])<=6
    for p in r['parameters']:
        assert all(s in sources for s in p['source_ids'])
    for e in r['endpoint_claims'].values():
        assert e['declared_population_value'] is None or isinstance(e['declared_population_value'],(int,float))
        assert e['validated_population_value'] is None or isinstance(e['validated_population_value'],(int,float))
result={'schema_version':1,'case_id':'lipids',
 'scope':'Retrospective static audit of captured model/spec/decision artifacts and prior audits. No new API calls, generator runs, raw-patient analysis, target-based parameter tuning, or original-paper authentication.',
 'coverage':{'R1_initial':10,'R2_initial':4,'R2_review':2,'complete':13,'incomplete_response':2,'transport_failure':1},
 'source_locator_correction':'Prior LIPID_CORE_REVIEW asserted Greiner reported_statistics.records; the captured packet actually uses columns plus rows. Correct native IDs, row indexes and locators are supplied here. No prior frozen file changed.',
 'sources':sources,'records':records,'seal_checks':checks,
 'operator_guide':{'primary_design':['1','(age-50)/10',"I(sex=='F')",'(bmi-25)/5'],
   'unit_conversion':'Raw mmol/L-per-BMI coefficient times 5*38.67; coefficient on scaled BMI times 38.67. This numerical unit conversion is not an assay calibration.',
   'rank_bridge':'2*sin(pi*Spearman/6) is a latent Pearson correlation only under a continuous Gaussian copula. Neither quantity equals a raw adjusted projection endpoint.',
   'dispersion':'Source marginal individual SD, conditional innovation SD, final projection residual SD, Monte Carlo variability and parameter uncertainty are different quantities.',
   'claim_interpretation':'Exact-law values are analytic consequences of assumed fixed laws. Recipe-only means an appropriate expression is available, not that a scalar was validated. Unavailable is not zero.',
   'components':'HDL/non-HDL independence yields positive TC/HDL correlation when TC=HDL+non-HDL. Noncomponent copulas can produce HDL>TC without violating the frozen output schema.'},
 'input_hashes':{rel(x):sha(x) for x in [R1/'packets/LIPID/evidence.json',R1/'provenance_review/LIPID_CORE_REVIEW.json',R2/'CROSS_MODEL_INITIAL_ATTRIBUTION.md',R2/'SCIENTIFIC_ATTRIBUTION_REVIEW_BRANCHES.md',OUT/'MAP_SCHEMA.json']}}
(OUT/'LIPID_PARAMETER_MAP.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rows=[]
for r in records:
    c=r['endpoint_claims']
    if r['artifact_status']!='complete': summary=r['artifact_status']+'; no scientific parameters inferred'
    elif c[EP[0]]['validation_status']=='exact_law': summary='Exact under fixed law: HDL '+str(c[EP[0]]['validated_population_value'])+', TC '+str(c[EP[1]]['validated_population_value'])+', residual r '+format(c[EP[2]]['validated_population_value'],'.9g')
    elif c[EP[0]]['validation_status']=='not_established': summary='Proposal claims only; positivity selection invalidates exact output identities'
    else: summary='Raw-moment projection recipe; numeric endpoints unavailable'
    rows.append('| '+r['round']+' | `'+r['version_id']+'` | '+summary+' |')
md='''# Lipid parameter map across the two completed pilots

This map covers **16 records: 10 first-round initial attempts, four second-round initial attempts, and two review branches**. Thirteen delivered scientific artifacts are mapped; two Gemini attempts ended with incomplete responses, and the second-round DeepSeek lipid attempt had a transport failure. Missing artifacts have no inferred parameters. The JSON is the detailed source/operator map; immutable evaluation results are joined separately by the root synthesis.

## Source anchors and operator bridges

The captured curator packet reports Agongo pooled arithmetic TC mean/SD **3.23/0.92** and HDL **1.14/0.38 mmol/L**, sex-specific and pooled BMI moments, and sex-specific univariate **log-lipid** BMI coefficients (TC **0.013**, male HDL **−0.007**; log base unresolved). Multiplying a coefficient by a raw mean gives a local raw derivative only after assuming a natural-log/exponential-mean bridge. Extending that derivative into a common age/sex-adjusted linear slope is another assumption.

Obirikorang rural pooled-sex Spearman anchors are **BMI–TC 0.212, BMI–HDL −0.100, TC–HDL 0.106**. Gaussian-copula models use `r = 2 sin(pi*rhoS/6)`. This is valid latent-correlation algebra under that family; it does not make either input the requested adjusted raw slope or residual Pearson correlation. Applying these pooled-sex anchors within sex, as the Astra R1 and Sol_A R2 laws do, adds a conditioning bridge. Sol C2 and the second-round Sol_B/Astra laws instead use unconditional anchors.

Greiner Uganda geometric means and age quartiles inform Astra C1's marginal construction; Agongo arithmetic coefficients of variation supply its log-shapes. Thus the cited Ghana SDs are reference shapes, not the final Uganda-centered generated SDs. Greiner regression scales remain unresolved and cannot directly identify target partial slopes or residual correlations. **Locator correction:** the captured packet uses `reported_statistics.columns` plus `reported_statistics.rows`, not `records` as asserted by the prior audit. Native row IDs and actual row indexes are recorded in the new JSON. This is a correction to the synthesis only.

## Delivered-law claims

Slope values below are **mg/dL per 5 kg/m²**. Exact values describe a fixed model's population projections, not demonstrated target validity. Copula rows retain a projection recipe without fabricating a scalar from generated samples.

| Round | Exact version ID | Static endpoint interpretation |
|---|---|---|
'''+ '\n'.join(rows)+'''

The four supported exact laws have linear conditional means in the requested design and independent centered errors. Their positive-output guards/floors are inactive for the fixed supports. DS C1 uses bounded Rademacher errors; Sol C1 uses bounded uniform common factors, with residual correlation `0.5*0.3=0.15`; Claude C1 solves the latent correlation for a chosen raw error correlation. These are internally coherent assumption-dependent laws, not source-derived adjusted regressions.

Claude C2 constructs **TC = HDL + non-HDL**. With component residual SDs 0.33 and 0.80 and zero HDL/non-HDL residual correlation, the requested TC/HDL correlation is `0.33/sqrt(0.33²+0.80²) = 0.381330923`, not zero. Its non-HDL SD includes an assumed explained-variance budget and subjective reduction, so it is not purely derived from reported marginal SD. Component floors are inactive and TC≥HDL is structural.

DS C2 repeatedly redraws bivariate-normal lipid proposals until both outcomes are positive, with a finite-attempt floor fallback. Acceptance depends on covariates. Its declared slopes and rho are therefore proposal parameters, not established exact output projections. The structural derivation issue exists even when its numerical effect in a generated sample is small.

## Paired second-round lineage

Both lipid branches descend from **LIPID_SOL_A**, with identical initial artifact and prompt. The ordinary `SECOND_LOOK` branch retains the same generator and model_spec, while its returned decision record clarifies the reporting. The `FEEDBACK` branch changes **only age**: an unbounded shifted lognormal becomes a shifted-scaled beta on **[18,100]**. The 100-year endpoint is an explicit new assumption, not a task exclusion, source estimate, or observed maximum. Beta shapes preserve the assumed sex-specific age means and SDs; the latent age–BMI loading remains 0.3.

The revised age transform consumes no extra random draws and leaves sex, BMI and both lipid columns unchanged for matched seeds. It can nevertheless change age-adjusted BMI projections and residual correlations through age covariance. The decision correctly replaces the all-lognormal age cross-moment formula with the beta-quantile integral. It cannot change the lipid component-inversion fraction when the lipid columns are unchanged. This is a comparison of paired review strategies, not two independent initial models.

## Interpretation limits

Marginal SD, innovation SD, final OLS residual SD and parameter uncertainty must remain distinct. None of the fixed-seed scenarios propagates source or transport uncertainty. Source populations, selection rules, assays, fasting protocols and recorded sex mapping are not validated merely by reusing their numbers. Positive noncomponent copula margins permit HDL>TC; that diagnostic concerns component coherence and is not a frozen schema exclusion. No new paper verification, clinical-source assertion, API call, generator run, target tuning or frozen-file edit was performed for this map.
'''
(OUT/'LIPID_PARAMETER_MAP.md').write_text(md,encoding='utf-8')
print(json.dumps({'records':len(records),'parameters':sum(len(r['parameters']) for r in records),'seal_checks':len(checks),'coverage':result['coverage'],'outputs':{x:sha(OUT/x) for x in ['LIPID_PARAMETER_MAP.json','LIPID_PARAMETER_MAP.md']}},indent=2))
