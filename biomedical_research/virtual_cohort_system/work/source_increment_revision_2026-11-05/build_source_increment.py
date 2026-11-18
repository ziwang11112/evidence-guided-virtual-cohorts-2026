"""Author one reviewed candidate from admitted static inputs; never execute its code."""
from pathlib import Path
import copy
import hashlib
import json
import shutil

ROOT = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
D = ROOT/'biomedical_research/virtual_cohort_system/work/source_increment_revision_2026-11-05'
OLD = ROOT/'evcRepE01/candidates/initial'
BUNDLE = ROOT/'evcIncE01'
CAND = BUNDLE/'candidates/source_increment'

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def leaves(value, prefix=''):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from leaves(item, prefix+'.'+key if prefix else key)
    elif isinstance(value, list):
        for i,item in enumerate(value):
            yield from leaves(item, prefix+'['+str(i)+']')
    else:
        yield prefix,value

def build():
    if CAND.exists() and any(CAND.iterdir()):
        raise RuntimeError('Candidate directory already exists; preserve it and make explicit edits only')
    CAND.mkdir(parents=True,exist_ok=True)
    (CAND/'static').mkdir()
    proposal = read_json(D/'PROPOSAL.json')
    admission = read_json(BUNDLE/'SOURCE_INCREMENT_ADMISSION.json')
    task = read_json(BUNDLE/'task.json')
    assert sha(D/'PROPOSAL.json') == admission['proposal_sha256']
    baseline_spec = read_json(OLD/'model_spec.json')
    spec = copy.deepcopy(baseline_spec)
    for patch in proposal['proposed_model']['parameter_patch']:
        steps = patch['path'].split('.')
        node = spec
        for step in steps[:-1]:
            node=node[step]
        assert node[steps[-1]] == patch['old']
        node[steps[-1]]=patch['value']

    descriptions = {
        'normal_scale':'Retired scale construction retained for historical context only: NHANES age50-54 (q97.5-mean)/Phi^-1(.975) no longer sets outcome variance; the original reported mean/quantile remain evidence. The unused normal_q975 constant is retained to keep all unreviewed parameter values unchanged.',
        'conditional_scales':'Kerman marginal BMI SD3.8 is retained as target continuous-age/sex-residual BMI SD. The two outcome residual SDs now use same-source beta/partial-r ratios times that imported BMI scale; neither is a reported absolute Finnish residual SD. Kerman glucose SD12.4 is retained as evidence and diagnostic only.',
        'r2_transport':'Within each Finnish outcome, assume conventional nested weighted projection R-squared and identical sample, weights and analysis for appendix coefficients and main Table3 R-squared. Appendix positive coefficients support the positive partial-r signs. Binary-age versus continuous-age and fasting-adjustment transport remain assumptions; full target R-squared is not constrained to source R-squared.',
        'combined_covariance':'Retain rBG/rBH source-derived partial-correlation magnitudes and use appendix beta/r ratios with target BMI SD3.8. The distinct HbA1c and glucose source adjustment sets and BMI-residual denominators are transported to a common target continuous-age/sex residual base. Retain Kerman raw-to-residual rGH0.23. No source identifies this absolute common covariance matrix.',
        'feedback_approximation':'semantic_feedback_v1 is required. Any computable ordinary Kerman diagnostic is evaluated on the target design restricted to available age/glucose source ranges, not a reconstructed source cohort; source selection, diagnosis, age/sex distribution, fasting and assay differ. Weighted Finnish/NHANES and missing-unit appendix checks remain not_computable. Raw discrepancies are neither significance nor calibration objectives.',
    }
    for assumption in spec['assumptions']:
        if assumption['id'] in descriptions:
            assumption['description']=descriptions[assumption['id']]
    spec['assumptions'] += [
        {'id':'supplement_units','description':'Additional file3 does not label outcome units or explicitly say unstandardized. Interpret S2 BMI0.0125 as HbA1c percentage points per kg/m2 and S1 BMI0.0240 as glucose mmol/L per kg/m2; main physical BMI definition, regression context and intercepts support but do not verify this. Convert the interpreted S1 coefficient with18.0182. Preserve original unit-unlabelled evidence and do not derive coefficient precision from p<0.0001.'},
        {'id':'relative_scale_transport','description':'For each aligned source weighted projection, beta/r equals the residual outcome/BMI SD ratio. Transport both ratios and partial correlations from source binary age/sex (plus fasting for glucose) to target continuous age/sex, equating both source-specific BMI residual denominators to target3.8 by assumption. Population, weights, eligibility, assay and age-range invariance are unverified. Source absolute SDs and Q3 are not identified.'},
        {'id':'retired_anchors','description':'Source glucose SD12.4 and NHANES age50-54 HbA1c q97.5=6.0 remain original evidence and diagnostic targets, but cease to define outcome scales. No expectation of matching them is asserted; all scheduled discrepancies including deterioration must be retained.'},
    ]
    for key in ('glucose','hba1c','residual_moments'):
        entry=spec['parameter_provenance'][key]
        entry['evidence_ids']=[e for e in entry['evidence_ids'] if e not in ('s4_g_sd','s1_h_q975')]
        if key=='residual_moments':
            entry['evidence_ids']=[e for e in entry['evidence_ids'] if e!='s1_h_mean']
        for e in ('supp_s1_bmi_glucose','supp_s2_bmi_hba1c'):
            if e not in entry['evidence_ids']: entry['evidence_ids'].append(e)
        entry['assumption_ids']=[a for a in entry['assumption_ids'] if a!='normal_scale']
        for a in ('supplement_units','relative_scale_transport','retired_anchors'):
            if a not in entry['assumption_ids']: entry['assumption_ids'].append(a)
    spec['parameter_provenance']['glucose']['derivation']='Retain all baseline mean anchors/age/sex effects/support. rBG=+sqrt((.1642-.1174)/(1-.1174)); sG=3.8*(.0240*18.0182)/rBG; bG=rBG*sG/3.8=.4324368; vG=sG^2*(1-rBG^2). Source unit interpretation, same-projection identity and ratio transport are declared assumptions, not source absolute variance.'
    spec['parameter_provenance']['hba1c']['derivation']='Retain baseline age/sex effects/mean anchors/family. rBH=+sqrt((.1164-.0660)/(1-.0660)); sH=3.8*.0125/rBH and sG=3.8*(.0240*18.0182)/rBG. bH=(sH/sB)*(rBH-rBG*rGH)/(1-rBG^2); gH=(sH/sG)*(rGH-rBG*rBH)/(1-rBG^2); vH=sH^2*(1-(rBH^2+rGH^2-2*rBG*rBH*rGH)/(1-rBG^2)). Retain rGH=.23 only as unverified raw-to-target-residual closure. Q2=5*(bH+gH*bG)=.0625 by target transport; Q3 not source-identified.'
    spec['parameter_provenance']['residual_moments']['derivation']='sB=3.8 imported residual anchor; rBG=sign(.0240)*sqrt((.1642-.1174)/(1-.1174)); rBH=sign(.0125)*sqrt((.1164-.0660)/(1-.0660)); sG=sB*(.0240*18.0182)/rBG; sH=sB*.0125/rBH; rGH=.23 assumed residual. normal_q975 retained unused as retired metadata; no normal quantile scale used. These are target working moments under ratio/conditioning transport, not a recovered absolute source covariance matrix.'

    baseline_evidence=read_json(OLD/'evidence.json')
    evidence=copy.deepcopy(baseline_evidence)
    source=next(s for s in evidence['sources'] if s['id']=='PMC6458679')
    source['artifacts'] += list(admission['source_map'].values())
    source['measurement'] += ' Additional file3 outcome-unit labels are absent; percent and mmol/L interpretations are model assumptions, not supplied source labels.'
    for item in evidence['items']:
        if item['id'] in ('s3_h_r2_as','s3_h_r2_asb','s3_g_r2_as','s3_g_r2_asb'):
            item['applicability']='Weighted nested R-squared. Appendix same-cohort BMI coefficients supply positive signs for conditional partial-correlation algebra, conditional on same sample/weights/conventional nested R-squared. Not a direct target residual correlation or absolute variance; binary-age/fasting transport remains assumed.'
        elif item['id']=='s4_g_sd':
            item['applicability']='Marginal individual SD retained as source evidence and approximate diagnostic; no longer determines target residual glucose scale. Source SD denominator not stated.'
        elif item['id']=='s1_h_q975':
            item['applicability']='Source weighted quantile, interpolation not reported. Retained as source evidence/unsupported diagnostic; no longer used to derive target residual HbA1c scale. No source quantile matching is asserted.'
    common_selection='Health2011 Finnish six-city reference n653,age30-64,complete cases,fast4-17h; excludes diagnosed/registered/treated diabetes,HbA1c>=6.5%,glucose>=7mmol/L; survey weighted.'
    evidence['items'] += [
        {'id':'supp_s1_bmi_glucose','source_id':'PMC6458679','locator':'Additional file3 Table S1, first Age + sex + BMI block, General population BMI beta row (converted VISIBLE_TEXT.txt TABLE1; PDF page1).','variables':['glucose','bmi'],'kind':'ols_coefficient','estimate':0.0240,'unit':'','uncertainty':{'kind':'not_reported'},'adjustment':['age_binary_30_44_vs_45_64','male_reference_female','fasting_hours_coding_unreported'],'selection':common_selection,'applicability':'Printed BMI beta0.0240,p<0.0001; outcome unit and coefficient SE/CI absent. Main Methods require fasting adjustment but coefficient/coding omitted. Unstandardized mmol/L per kg/m2 is a declared interpretation, not a verified unit. Used with same-cohort R-squared for a relative residual scale under alignment assumptions; no source absolute variance or target coefficient claimed.'},
        {'id':'supp_s2_bmi_hba1c','source_id':'PMC6458679','locator':'Additional file3 Table S2, first Age + sex + BMI block, General population BMI beta row (converted VISIBLE_TEXT.txt TABLE2; PDF page2).','variables':['hba1c','bmi'],'kind':'ols_coefficient','estimate':0.0125,'unit':'','uncertainty':{'kind':'not_reported'},'adjustment':['age_binary_30_44_vs_45_64','male_reference_female'],'selection':common_selection,'applicability':'Printed BMI beta0.0125,p<0.0001; outcome unit and coefficient SE/CI absent. Unstandardized percentage points per kg/m2 is a declared interpretation, not a verified unit. Used with same-cohort R-squared for a relative residual scale under alignment assumptions. Glucose-adjusted BMI coefficient, HbA1c-glucose covariance and absolute residual variance are not supplied.'},
    ]
    for original, current in zip(baseline_evidence['items'], evidence['items']):
        assert {k:v for k,v in original.items() if k!='applicability'} == {k:v for k,v in current.items() if k!='applicability'}
    write_json(CAND/'evidence.json',evidence)
    write_json(CAND/'model_spec.json',spec)
    shutil.copyfile(OLD/'generator.py',CAND/'generator.py')

    # Source definitions are authored from the admitted source context, not inferred
    # from target outputs. Only six Kerman ordinary-statistic comparisons are available.
    selection=[{'column':'age','op':'ge','value':18},{'column':'age','op':'le','value':75},{'column':'glucose','op':'le','value':126}]
    ordinary={
        's4_age_mean':{'kind':'mean','column':'age','unit':'year'},
        's4_bmi_sd':{'kind':'sd','column':'bmi','unit':'kg/m^2'},
        's4_g_mean':{'kind':'mean','column':'glucose','unit':'mg/dL'},
        's4_g_sd':{'kind':'sd','column':'glucose','unit':'mg/dL'},
        's4_female':{'kind':'proportion','event':{'column':'female','op':'eq','value':1},'unit':'1'},
        's4_pearson':{'kind':'correlation','x':'glucose','y':'hba1c','unit':'1'},
    }
    units={c['name']:c['unit'] for c in task['columns']}
    recipe={'schema_version':1,'population':task['population'],'measurement':{'mode':'identity','description':'Only ordinary Kerman same-printed-unit statistics can be compared under stated assay/matrix transport; no variable conversion is performed. Printed appendix units are unlabelled and Finnish weighted operators unavailable. Target design output is never called source replay.'},'assumption_ids':['feedback_approximation'],'checks':[]}
    bindings=[]
    for item in evidence['items']:
        eid=item['id']; cid='check_'+eid
        src=item['source_id']; operator=None; variable_units={}
        weights='weighted' if src in ('PMC2551641','PMC6458679') else 'none'
        transform='identity'; status='not_computable'; definition='unsupported'
        if eid in ordinary:
            operator=copy.deepcopy(ordinary[eid]); operator.update(selection=copy.deepcopy(selection),missing_policy='complete_cases')
            cols={'age','glucose'}
            if 'column' in operator: cols.add(operator['column'])
            if 'event' in operator: cols.add(operator['event']['column'])
            if 'x' in operator: cols.update((operator['x'],operator['y']))
            variable_units={c:units[c] for c in sorted(cols)}
            status='approximate'; definition='specified'
            reason='Kerman low-FBS n525: ordinary unweighted '+operator['kind']+' with age18-75 and FBS<=126; no analytic weights reported. Applied to target rows only within available source ranges. Target age/sex design, no prior diagnosis,8-12h fast and measurement/selection differ; 30 known-diabetes source cases are not represented. This is a raw target-context descriptive discrepancy, never source replay or a target conditional-moment check.'
            if operator['kind']=='sd': reason+=' Sample SD ddof1 is an explicit convention; source denominator unreported.'
            if eid=='s4_g_sd': reason+=' This original source dispersion anchor is retired from parameter-setting but retained as a diagnostic.'
        elif src=='PMC2551641':
            reason='NHANES source survey weighting cannot be represented by v1 unweighted operators. No target unweighted replacement is supplied. Source quantile interpolation or qualitative age-contrast endpoints remain unreported where applicable. Original evidence remains available including the retired HbA1c upper-quantile anchor.'
        elif src=='PMC6458679':
            reason='Finnish source survey weighting and binary-age adjustment cannot be replaced by target equal-cell continuous-age operators; glucose analyses also require unobserved fasting context. Full source regression/R-squared/predictive margins are not reproduced.'
            if eid.startswith('supp_'):
                reason+=' Appendix outcome units and coefficient standardization label are not reported; percent/mmol-L are model working interpretations only. v1 has no reviewed unit/age/weight conversion. No OLS substitute is supplied.'
                transform='not_reported'
            elif eid in ('s3_male_g','s3_female_g'):
                transform='nonidentity'
                reason+=' Reported glucose margin uses mmol/L versus target mg/dL; identity feedback cannot convert it.'
            else:
                reason+=' Partial-r algebra using the supplement is a constant derivation, not replay of these weighted source statistics.'
        elif eid=='s2_male':
            transform='nonidentity'
            reason='Source male coefficient adjusted age only cannot be relabelled as target female or fully adjusted coefficient. The model negation/transport is an assumption; v1 has no reviewed sign/coding conversion.'
        else:
            reason='Original Kerman printed slopes were declined for unresolved scale; contextual record has no numeric source constraint. No invented corrected coefficient is checked.'
        aids=['feedback_approximation']
        if status=='approximate': aids += ['selection','measurement']
        if eid in ('s4_bmi_sd','s4_g_sd'): aids.append('sd_convention')
        if eid.startswith('supp_'): aids += ['supplement_units','relative_scale_transport']
        recipe['checks'].append({'id':cid,'evidence_id':eid,'status':status,'operator':copy.deepcopy(operator),'assumption_ids':aids,'reason':reason})
        n=653 if src=='PMC6458679' else 525 if src=='PMC3075530' else 4748 if src=='PMC8038122' else 261 if eid in ('s1_h_mean','s1_h_q975') else 3270
        uncertainty=item['uncertainty']['kind']
        role='estimate' if uncertainty in ('se','ci') else 'individual_dispersion' if uncertainty=='sd' else 'not_reported'
        bindings.append({'check_id':cid,'evidence_id':eid,'source_locator':item['locator'],'definition_status':definition,'source_operator':operator,'source_variable_units':variable_units,'weights':weights,'transform':transform,'source_n':{'status':'reported','value':n,'scope':'Reported source analysis population or source age subgroup; not generated row count'},'uncertainty_role':role,'reason':reason})
    write_json(CAND/'whole_cohort_feedback.json',recipe)
    semantics={'schema_version':1,'evidence_sha256':sha(CAND/'evidence.json'),'recipe_sha256':sha(CAND/'whole_cohort_feedback.json'),'bindings':bindings}
    write_json(CAND/'source_semantics_v1.json',semantics)

    for name in ('PROPOSAL.md','PROPOSAL.json','PROPOSAL_CALCULATIONS.json','proposal_constant_calculations.py','PROPOSAL_READ_INTEGRITY.json','REVIEW.md'):
        shutil.copyfile(D/name,CAND/'static'/name)
    old_leaves=dict(leaves(baseline_spec['parameters'])); new_leaves=dict(leaves(spec['parameters']))
    changes=[{'path':key,'old':old_leaves[key],'new':new_leaves[key]} for key in old_leaves if old_leaves[key]!=new_leaves[key]]
    assert len(changes)==7 and old_leaves.keys()==new_leaves.keys()
    assert sha(OLD/'generator.py')==sha(CAND/'generator.py')
    write_json(CAND/'static/IMPLEMENTATION_STATIC_CHECKS.json',{'scope':'Static JSON, exact parameter-leaf comparison and generator byte integrity; no import, rows, RNG or execution','parameter_changes':changes,'parameter_change_count':7,'generator_bytes_identical':True,'generator_sha256':sha(CAND/'generator.py'),'original_source_items_preserved':len(evidence['items'])-2,'new_source_items':2,'source_checks_declared':len(recipe['checks']),'source_checks_approximate':6,'source_checks_not_computable':len(recipe['checks'])-6,'scientific_proposal_sha256':sha(D/'PROPOSAL.json'),'source_only_review_sha256':sha(D/'REVIEW.md')})
    decision='''# Source-increment candidate decision\n\nImplement the independently reviewed proposal as one development sensitivity construction. The generator bytes are identical to the admitted static initial generator. Exactly seven numerical parameter leaves change: two residual scales and their five dependent triangular regression/variance parameters. All scientific distribution families, supports, means, age/sex effects and correlation closure remain unchanged. See static/PROPOSAL.md for the complete law, source operators, formulas, numerical values and limitations; static/IMPLEMENTATION_STATIC_CHECKS.json records the exact diff.\n\nThe source supplement reports BMI coefficients0.0240 and0.0125 with unlabelled outcome units and no SE/CI. evidence.json preserves these as unit-empty values; model assumptions separately interpret mmol/L and percent. Combining each slope with its same-cohort nested R-squared gives a residual SD ratio under conventional aligned weighted-projection assumptions. Importing target BMI residual SD3.8 supplies absolute scales; neither absolute source variance nor a common source covariance matrix has been recovered. Q3 additionally retains the unverified raw-to-residual Kerman rGH=.23 closure.\n\nModel-implied Q1=.1 percentage points/10years, Q2=.0625 and Q3=.050951995797927516 percentage points/5kg/m2 are analytic implications, not source replay or target results. Residual distributions narrow; all scheduled diagnostics and retired glucose-SD/HbA1c-quantile discrepancies must be retained. Full Finnish intercepts, age/sex coefficients, total R-squared and margins are not reproduced.\n\nOnly semantic_feedback_v1 is designated for supplied source-statistic checks. Its sidecar and recipe retain unavailable weighted/missing-unit checks as not_computable. Six ordinary Kerman statistics remain explicitly approximate target-context descriptive comparisons under available source-range restrictions; no source reconstruction or target validation is claimed. No new favorable endpoint, parameter tuning or target-informed repair is authorized.\n\nImplementation ends at static contract validation and semantic preflight. No generator import/call, data generation, freeze, run or target evaluation is performed by this builder. Root/controller is responsible for independent code/spec review and the fixed three-seed schedule after freezing. No earlier computed feedback has been copied.\n'''
    (CAND/'decision.md').write_text(decision,encoding='utf-8')
    checks={'scope':'source_only','records':[
        {'name':'constant_only_scientific_arithmetic','status':'pass','detail':'Actual pre-implementation proposal_constant_calculations.py run checks source-ratio/triangular identities, Q1/Q2/Q3 implications, positive correlation determinant, positive beta/gamma parameters over support corners. Bound static/PROPOSAL_CALCULATIONS.json; no rows or generator execution.'},
        {'name':'exact_reviewed_parameter_and_code_diff','status':'pass','detail':'Actual construction script compares all parameter leaves: exactly seven reviewed numeric changes, no additions/deletions. generator.py is byte-identical to admitted baseline. All original evidence-item factual fields except applicability prose are unchanged. Bound static/IMPLEMENTATION_STATIC_CHECKS.json.'},
        {'name':'stage1_input_integrity','status':'pass','detail':'Actual recorded hash check of16 Stage1 input files; all manifest-listed files read match admitted hashes. Bound static/PROPOSAL_READ_INTEGRITY.json.'},
        {'name':'source_replay','status':'not_computable','detail':'No exact source replay: Finnish weights/joint covariates/fasting coding and appendix units unavailable. Six ordinary Kerman checks are declared approximate target-context comparisons only; no numerical feedback calculated in this stage.'},
        {'name':'generator_execution','status':'not_computable','detail':'Not performed or requested by builder; isolated controller execution after review/freeze remains pending.'}
    ],'artifacts':[{'path':'static/'+name,'sha256':sha(CAND/'static'/name)} for name in ('PROPOSAL_CALCULATIONS.json','IMPLEMENTATION_STATIC_CHECKS.json','PROPOSAL_READ_INTEGRITY.json')]}
    write_json(CAND/'checks.json',checks)
    print(json.dumps({'candidate':str(CAND),'parameter_changes':7,'generator_bytes_identical':True,'checks_declared':len(recipe['checks']),'generated_rows':0},indent=2))

if __name__=='__main__':
    build()
