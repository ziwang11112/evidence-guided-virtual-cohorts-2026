"""Author aggregate-only artifacts; never imports or calls the submitted generator."""
import ast
import copy
import hashlib
import json
import math
from pathlib import Path

B = Path(__file__).resolve().parent
C = B / 'candidates' / 'initial'
C.mkdir(parents=True, exist_ok=True)
task = json.loads((B / 'task.json').read_text())
panel = json.loads((B / 'SOURCE_PANEL_SPEC.json').read_text())
evidence = json.loads((B / 'evidence_template.json').read_text())
items = {x['id']: x for x in evidence['items']}

def write(name, obj):
    path = C / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assumptions = [
    ('A_DOMAIN', 'Common computational age domain is integer 18-95, female is 0/1, BMI and HbA1c are positive and glucose is positive and below 126 mg/dL. This domain covers all three contexts; it is not an observed clinical range. Target age remains 25-79. Source age supports are author assumptions.'),
    ('A_TARGET_DESIGN', 'Target has exactly 250 rows in each female 0/1 by age-band 25-39,40-54,55-69,70-79 intersection, with integer ages uniform within each band. Quotas are supplied analytical design; within-band uniformity is assumed. No prevalence or national representativeness follows.'),
    ('A_J_AGE', 'Lifelines explicit age limits are unknown. Approximate adult age mass is proportional to exp(-0.5*((age-55.5)/9.9)^2) on integer 18-95, independently of female. The endpoints are modeling bounds, not extracted source facts; truncation and discretization slightly change published moments.'),
    ('A_P_AGE', 'Pani age-band mass is proportional to the eight published unweighted sample counts, although published means used survey weights. Integer ages are uniform in each closed band below 70. The open final band is approximated by ages 70-95 with mass exp(-(age-70)/7); 95 and decay scale 7 are assumptions. This includes ages beyond the target 79 ceiling but leaves unmodeled the true far-oldest tail and weighted age distribution.'),
    ('A_SEX', 'Lifelines female probability is the complement 0.597 of rounded male proportion 0.403; this does not decode a regression sex coefficient. Pani female probability is assumed 0.5 because its source composition was not supplied. Age and female are independent in source approximations; target follows quotas.'),
    ('A_COV_TRENDS', 'At the Lifelines age/female reference, conditional BMI and fasting glucose locations equal reported means. Assumed BMI age slope 0.025 kg/m^2/year and female contrast +0.6 kg/m^2, glucose age slope +0.10 mg/dL/year and female contrast -1.5 mg/dL. These modest slopes are structural choices, not recovered source estimates. They are constant across all contexts.'),
    ('A_JOINT', 'Conditional BMI/glucose residuals have a bivariate normal distribution with correlation 0.30 independent of age and female. This unreported covariance closes two separate Jansen projections into one joint conditional HbA1c equation; it is not identified by the evidence. Normal BMI tails, linear dependence and homoskedasticity are approximations.'),
    ('A_SELECTION', 'All contexts are generated directly as selected analytical populations. Conditional BMI/glucose pairs are redrawn until BMI>0 and 0<glucose<126, holding age and female fixed. This is an assumed selected-distribution approximation, not a mechanistic disease/diagnosis/fasting/anthropometry eligibility model. Threshold conditioning slightly changes marginal moments and projection algebra.'),
    ('A_HBA_RULE', 'HbA1c has one linear conditional rule in age, BMI and glucose, a zero direct female contrast, and independent Gaussian residuals truncated only at positivity. Zero direct female effect is an explicit assumption, not an inference from missing source coefficients. Jansen total percent SD 0.3 is decomposed using assumed covariance and Pani age slope. No interactions, saturation or age-varying residual scale are identified.'),
    ('A_PANI_LEVEL', 'Pani location is the count-weighted average of the eight reported survey age-band HbA1c means, anchored at the expected age of the assumed Pani age distribution and female probability 0.5. Mixing survey band means with unweighted counts is approximate and is not a recovered national mean. The band means constrain this one location; they are not eight independently fitted intercepts. The common linear model may disagree with their older-age plateau.'),
    ('A_SHARED_RULE', 'Jansen age/sex-adjusted BMI and glucose projection coefficients are converted to conditional coefficients only after declaring residual BMI/glucose covariance; Pani age coefficient adjusted for female/BMI/glucose is then imposed as the shared conditional age coefficient. Assuming these cross-cohort coefficients coexist in one linear law is an unverified scientific synthesis, not an identified joint regression.'),
    ('A_TRANSPORT', 'Target adopts exactly the Pani HbA1c location rule and the common Lifelines-based BMI/glucose locations, scales, trends, dependence and residual law. No ethnicity-specific or Mexico-specific correction is supplied or estimated. Transport from western-European Lifelines and US NHANES to Mexican adults is unverified, including ancestry, nutrition, adiposity, age selection and socioeconomic differences.'),
    ('A_MEASUREMENT', 'All outputs use task units; glucose conversion is fixed 18.0 mg/dL per mmol/L and HbA1c projection conversion uses 0.09148 without offset. Source feedback is identity mapping after conversion in admitted evidence. Applying fasting-plasma relationships to target fasting serum assumes no systematic plasma/serum bias, no fasting-duration effect within the target 8-12 hours, and sufficient assay comparability; these are not established by unit conversion.'),
    ('A_UNMEASURED', 'Lifelines excluded significant anemia; the target has no verified anemia or medication exclusion. No latent anemia, medication, pregnancy or lactation effect is separately identified; their net conditional effect is assumed covered by the transported residual/location. Target pregnancy/lactation exclusion applies only when documented for routed women 25-49; older unasked status remains unresolved. This model cannot verify eligibility or resolve anthropometric documentation.'),
    ('A_SURVEY', 'Pani feedback uses ordinary Monte Carlo sample means and OLS with intercept, preserving the printed adjustment set and units. It does not reconstruct complex-survey weights, strata or clusters; source row composition and estimator are approximations. Reported SEs remain sampling uncertainty and never become individual SDs.'),
    ('A_UNCERTAINTY', 'Fixed source estimates and assumed parameters define one initial scenario. Gaussian individual variation and seed variation are not evidence/model/transport uncertainty. Unknown Jansen interval confidence levels and coefficient SEs preclude a justified parameter posterior; no probability distribution over scientific assumptions is claimed.'),
    ('A_EXECUTION', 'Only the controller executes generation. Random draws use the passed seed, no external files/data/network. A finite rejection-attempt guard raises an error rather than silently clipping values; output is not locally smoke-tested by the builder.'),
]

ref = {'age_mean':55.5, 'age_sd':9.9, 'female_probability':0.597,
       'bmi_mean':26.5, 'bmi_sd':4.1, 'glucose_mean':91.8, 'glucose_sd':9.0,
       'hba1c_mean':5.6, 'hba1c_sd':0.3}
trends = {'bmi_age':0.025, 'bmi_female':0.6, 'glucose_age':0.10, 'glucose_female':-1.5}
rho = 0.30
v_f = ref['female_probability'] * (1-ref['female_probability'])
s_b = math.sqrt(ref['bmi_sd']**2-trends['bmi_age']**2*ref['age_sd']**2-trends['bmi_female']**2*v_f)
s_g = math.sqrt(ref['glucose_sd']**2-trends['glucose_age']**2*ref['age_sd']**2-trends['glucose_female']**2*v_f)
q_b = items['J_T2_bmi_slope_task_derived']['estimate']
q_g = items['J_T2_glucose_slope_task_derived']['estimate']
beta_b = (q_b-q_g*rho*s_g/s_b)/(1-rho*rho)
beta_g = (q_g-q_b*rho*s_b/s_g)/(1-rho*rho)
beta_a = items['P_NHANES_age_slope']['estimate']
marginal_a = beta_a+beta_b*trends['bmi_age']+beta_g*trends['glucose_age']
marginal_f = beta_b*trends['bmi_female']+beta_g*trends['glucose_female']
explained = (marginal_a**2*ref['age_sd']**2+marginal_f**2*v_f+
             beta_b**2*s_b*s_b+beta_g**2*s_g*s_g+2*beta_b*beta_g*rho*s_b*s_g)
s_h = math.sqrt(ref['hba1c_sd']**2-explained)
coeff = {'hba1c_age':beta_a, 'hba1c_bmi':beta_b, 'hba1c_glucose':beta_g,
         'hba1c_female_direct':0.0, 'bmi_residual_sd':s_b,
         'glucose_residual_sd':s_g, 'hba1c_residual_sd':s_h}

pani_band_defs = [(25,39,1037,'P_NHANES_hba1c_age_lt40_mean'),
                  (40,44,330,'P_NHANES_hba1c_age_40_44_mean'),
                  (45,49,322,'P_NHANES_hba1c_age_45_49_mean'),
                  (50,54,261,'P_NHANES_hba1c_age_50_54_mean'),
                  (55,59,198,'P_NHANES_hba1c_age_55_59_mean'),
                  (60,64,283,'P_NHANES_hba1c_age_60_64_mean'),
                  (65,69,198,'P_NHANES_hba1c_age_65_69_mean'),
                  (70,95,641,'P_NHANES_hba1c_age_ge70_mean')]
pani_bands = []
age_sum = h_sum = 0.0
for lo,hi,count,eid in pani_band_defs:
    ages = list(range(lo,hi+1))
    weights = [math.exp(-(a-lo)/7) if lo == 70 else 1.0 for a in ages]
    mean_a = sum(a*w for a,w in zip(ages,weights))/sum(weights)
    age_sum += count*mean_a
    h_sum += count*items[eid]['estimate']
    pani_bands.append({'minimum':lo, 'maximum':hi, 'sample_count':count,
                       'within_band':'exponential' if lo==70 else 'uniform',
                       'decay_years':7 if lo==70 else None,
                       'reported_hba1c_mean':items[eid]['estimate'], 'evidence_id':eid})
total_n = sum(x[2] for x in pani_band_defs)
h_refs = {'lifelines':{'age':55.5, 'female_probability':0.597, 'hba1c':5.6},
          'pani':{'age':age_sum/total_n, 'female_probability':0.5, 'hba1c':h_sum/total_n}}

def columns_for(lo,hi):
    cols=copy.deepcopy(task['columns'])
    cols[1]['minimum']=lo
    cols[1]['maximum']=hi
    return cols

contexts = {'target':{'population':task['population'], 'n_rows':task['n_rows'],
    'columns':copy.deepcopy(task['columns']),
    'inputs':{'sampling_design':'balanced', 'age_bands':[[25,39],[40,54],[55,69],[70,79]],
              'female_values':[0,1], 'per_cell':250, 'hba1c_reference':'pani'}},
    'lifelines':{'population':panel['contexts'][0]['published_population']+' Approximate reconstruction with assumed integer age support 18-95 and a discretized Gaussian age distribution; no source individual data.',
    'n_rows':6000, 'columns':columns_for(18,95),
    'inputs':{'sampling_design':'discrete_gaussian', 'age_mean':55.5, 'age_sd':9.9,
              'female_probability':0.597, 'hba1c_reference':'lifelines'}},
    'pani':{'population':panel['contexts'][1]['published_population']+' Approximate reconstruction with age-band probabilities proportional to unweighted counts, uniform integer ages below 70, and an assumed declining 70-95 tail; no source individual data or recovered survey weights.',
    'n_rows':6000, 'columns':columns_for(25,95),
    'inputs':{'sampling_design':'age_band_mixture', 'age_bands':pani_bands,
              'female_probability':0.5, 'hba1c_reference':'pani'}}}

parameters = {'active_context':'target', 'contexts':contexts, 'lifelines_reference':ref,
              'covariate_trends':trends, 'conditional_residual_correlation':rho,
              'reported_projection_constraints':{'bmi':q_b, 'glucose':q_g, 'age':beta_a},
              'conditional_coefficients':coeff, 'hba1c_references':h_refs,
              'max_rejection_rounds':10000}
prov = {}
def provenance(key,eids,aids,derivation):
    prov[key]={'evidence_ids':eids,'assumption_ids':aids,'derivation':derivation}
all_j_marginals = [x['id'] for x in panel['contexts'][0]['checks'] if x['operator']['kind'] != 'ols_coefficient']
p_ids = [x['id'] for x in panel['contexts'][1]['checks']]
j_proj = ['J_T2_bmi_slope_task_derived','J_T2_glucose_slope_task_derived']
provenance('active_context',[],['A_EXECUTION'],'Selector only; the bridge changes this key and no scientific setting.')
provenance('contexts',all_j_marginals+p_ids,['A_DOMAIN','A_TARGET_DESIGN','A_J_AGE','A_P_AGE','A_SEX','A_PANI_LEVEL','A_TRANSPORT'],
           'Task descriptor is copied exactly. Lifelines source age/sex distribution uses Table 1 marginal evidence. Pani band counts are the supplied Table 1 unweighted counts; tail and within-band ages are assumptions. Source tasks contain 6000 Monte Carlo rows. Target selects exactly the Pani HbA1c reference, while common covariate parameters remain unchanged.')
provenance('lifelines_reference',all_j_marginals,['A_J_AGE','A_JOINT','A_SELECTION','A_MEASUREMENT'],
           'Jansen Table 1 printed percent HbA1c mean/SD 5.6/0.3; no use of the rounded alternate IFCC marginal. FPG 5.1/0.5 mmol/L becomes 91.8/9.0 mg/dL using 18.0. Female 0.597 is 1-0.403. Marginal moments do not identify a joint law.')
provenance('covariate_trends',[],['A_COV_TRENDS','A_TRANSPORT'],'Four assumed conditional age and female associations, shared across all populations; none is a recovered scientific coefficient.')
provenance('conditional_residual_correlation',[],['A_JOINT'],'Residual BMI/glucose Pearson correlation 0.30 is an explicit closure assumption; not extracted or fitted to generated data.')
provenance('reported_projection_constraints',j_proj+['P_NHANES_age_slope'],['A_SHARED_RULE','A_MEASUREMENT'],
           'Preserves two separate Jansen age/female-adjusted projections and the Pani female/BMI/glucose-adjusted age coefficient. Jansen slopes use NGSP multiplier and glucose factor only; no Liu or Table 3 calibration.')
provenance('conditional_coefficients',j_proj+['P_NHANES_age_slope']+all_j_marginals,
           ['A_JOINT','A_COV_TRENDS','A_HBA_RULE','A_SHARED_RULE','A_SELECTION','A_UNCERTAINTY'],
           'Analytical, pre-truncation construction: sB^2=SD_B^2-bA^2*SD_A^2-bF^2*pF*(1-pF), likewise sG. Given r=0.30, betaB=(qB-qG*r*sG/sB)/(1-r^2), betaG=(qG-qB*r*sB/sG)/(1-r^2). Thus the separate age/female-adjusted projection equations are qB=betaB+betaG*r*sG/sB and qG=betaG+betaB*r*sB/sG, rather than concatenating qB and qG. betaAge=0.010. Independent HbA1c residual variance is 0.3^2 minus variance of the linear signal under assumed Lifelines age/sex moments. Gaussian truncation and finite age approximation make all source equalities approximate.')
provenance('hba1c_references',['J_T1_hba1c_mean_pct']+p_ids[1:],['A_PANI_LEVEL','A_P_AGE','A_SEX','A_TRANSPORT'],
           'Lifelines level 5.6 is anchored at age55.5/female probability0.597. Pani level=sum(unweighted band n*reported survey band mean)/3270, anchored at the count-weighted expected age under declared within-band age laws and assumed female probability0.5. Target reuses precisely this Pani anchor. This aggregate operation does not identify a survey-weighted overall mean or fit eight individual age curves.')
provenance('max_rejection_rounds',[],['A_EXECUTION'],'Computational guard only, no clipping or numerical fallback on failure.')
spec={'parameters':parameters,'assumptions':[{'id':i,'description':d} for i,d in assumptions], 'parameter_provenance':prov}
write('model_spec.json',spec)
(C/'evidence.json').write_bytes((B/'evidence_template.json').read_bytes())

generator = '''"""Shared aggregate-evidence construction. No I/O or local execution path."""
import numpy as np
import pandas as pd


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort mode requires observed=None")
    p = specification["parameters"]
    active = p["active_context"]
    context = p["contexts"][active]
    inputs = context["inputs"]
    columns = context["columns"]
    bounds = {x["name"]: x for x in columns}
    n = context["n_rows"]
    rng = np.random.default_rng(seed)
    design = inputs["sampling_design"]
    if design == "balanced":
        age_parts, female_parts = [], []
        for female_value in inputs["female_values"]:
            for low, high in inputs["age_bands"]:
                size = inputs["per_cell"]
                age_parts.append(rng.integers(low, high + 1, size=size))
                female_parts.append(np.full(size, female_value, dtype=int))
        age = np.concatenate(age_parts)
        female = np.concatenate(female_parts)
        if len(age) != n:
            raise ValueError("Balanced design count disagrees with context")
    else:
        support = np.arange(bounds["age"]["minimum"], bounds["age"]["maximum"] + 1)
        if design == "discrete_gaussian":
            weights = np.exp(-0.5 * ((support-inputs["age_mean"])/inputs["age_sd"])**2)
        elif design == "age_band_mixture":
            weights = np.zeros(len(support), dtype=float)
            for band in inputs["age_bands"]:
                use = (support >= band["minimum"]) & (support <= band["maximum"])
                local = np.ones(int(use.sum()))
                if band["within_band"] == "exponential":
                    local = np.exp(-(support[use]-band["minimum"])/band["decay_years"])
                elif band["within_band"] != "uniform":
                    raise ValueError("Unknown within-band age law")
                weights[use] = band["sample_count"] * local/local.sum()
        else:
            raise ValueError("Unknown sampling design")
        age = rng.choice(support, size=n, p=weights/weights.sum())
        female = rng.binomial(1, inputs["female_probability"], size=n)

    reference = p["lifelines_reference"]
    trend = p["covariate_trends"]
    coefficient = p["conditional_coefficients"]
    correlation = p["conditional_residual_correlation"]
    centered_age = age-reference["age_mean"]
    centered_female = female-reference["female_probability"]
    mean_bmi = reference["bmi_mean"] + trend["bmi_age"]*centered_age + trend["bmi_female"]*centered_female
    mean_glucose = reference["glucose_mean"] + trend["glucose_age"]*centered_age + trend["glucose_female"]*centered_female
    bmi = np.empty(n)
    glucose = np.empty(n)
    pending = np.arange(n)
    for _ in range(p["max_rejection_rounds"]):
        if len(pending) == 0:
            break
        z = rng.normal(size=(len(pending), 2))
        b = mean_bmi[pending] + coefficient["bmi_residual_sd"]*z[:, 0]
        g = mean_glucose[pending] + coefficient["glucose_residual_sd"]*(correlation*z[:, 0] + np.sqrt(1-correlation**2)*z[:, 1])
        ok = (b > 0) & (g > 0) & (g <= bounds["glucose"]["maximum"])
        bmi[pending[ok]], glucose[pending[ok]] = b[ok], g[ok]
        pending = pending[~ok]
    if len(pending):
        raise RuntimeError("Conditional covariate rejection limit reached")

    anchor = p["hba1c_references"][inputs["hba1c_reference"]]
    anchor_bmi = reference["bmi_mean"] + trend["bmi_age"]*(anchor["age"]-reference["age_mean"]) + trend["bmi_female"]*(anchor["female_probability"]-reference["female_probability"])
    anchor_glucose = reference["glucose_mean"] + trend["glucose_age"]*(anchor["age"]-reference["age_mean"]) + trend["glucose_female"]*(anchor["female_probability"]-reference["female_probability"])
    mean_hba1c = (anchor["hba1c"] + coefficient["hba1c_age"]*(age-anchor["age"])
                  + coefficient["hba1c_bmi"]*(bmi-anchor_bmi)
                  + coefficient["hba1c_glucose"]*(glucose-anchor_glucose)
                  + coefficient["hba1c_female_direct"]*(female-anchor["female_probability"]))
    hba1c = np.empty(n)
    pending = np.arange(n)
    for _ in range(p["max_rejection_rounds"]):
        if len(pending) == 0:
            break
        h = mean_hba1c[pending] + rng.normal(0, coefficient["hba1c_residual_sd"], size=len(pending))
        ok = h > 0
        hba1c[pending[ok]] = h[ok]
        pending = pending[~ok]
    if len(pending):
        raise RuntimeError("Conditional HbA1c rejection limit reached")
    order = rng.permutation(n)
    return pd.DataFrame({
        "row_id": [f"SYN-{active}-{i:06d}" for i in range(1, n+1)],
        "age": age[order].astype(int), "female": female[order].astype(int),
        "bmi": bmi[order], "glucose": glucose[order], "hba1c": hba1c[order]
    }, columns=[c["name"] for c in columns])
'''
(C/'generator.py').write_text(generator,encoding='utf-8')

domain_cols = columns_for(18,95)
write('source_context_plan.json',{'schema_version':1,'model_domain':{
    'columns':domain_cols,'assumption_ids':['A_DOMAIN'],
    'description':'Common positive selected-distribution domain with integer ages18-95. Lifelines support is assumed18-95, Pani25-95 includes the older open band beyond79, target25-79 retains supplied quotas. Unbounded positive BMI/HbA1c are not claims about plausible extrema.'},
    'contexts':[{'id':name,'task_path':f'source_contexts/{name}/task.json',
                 'feedback_path':f'source_contexts/{name}/whole_cohort_feedback.json'} for name in ('lifelines','pani')]})
for panel_context in panel['contexts']:
    name=panel_context['id']
    child=copy.deepcopy(task)
    child.update({k:contexts[name][k] for k in ('population','n_rows','columns')})
    write(f'source_contexts/{name}/task.json',child)
    if name=='lifelines':
        population_assumptions=['A_DOMAIN','A_J_AGE','A_SEX','A_COV_TRENDS','A_JOINT','A_SELECTION','A_HBA_RULE','A_SHARED_RULE','A_MEASUREMENT']
        reason='Approximate Lifelines reconstruction from marginals with assumed adult age support, covariate trends and joint dependence. Normal-law moment/projection algebra applies before small support conditioning; finite Monte Carlo variation remains. The exact supplied operator preserves units and adjustment; Table 2 row-specific sample size is unknown.'
    else:
        population_assumptions=['A_DOMAIN','A_P_AGE','A_SEX','A_COV_TRENDS','A_JOINT','A_SELECTION','A_HBA_RULE','A_PANI_LEVEL','A_SHARED_RULE','A_MEASUREMENT','A_SURVEY']
        reason='Approximate Pani source-population projection under unweighted sample-count age-band mass, assumed within-band ages/sex/covariates and a shared linear rule. These Monte Carlo statistics do not reproduce the original survey estimator. All eight band means remain diagnostics; only their aggregate location is calibrated, so age-pattern disagreement is possible.'
    checks=[{'id':x['id'],'evidence_id':x['evidence_id'],'status':'approximate',
             'operator':copy.deepcopy(x['operator']),'assumption_ids':[], 'reason':reason} for x in panel_context['checks']]
    write(f'source_contexts/{name}/whole_cohort_feedback.json',{
        'schema_version':1,'population':child['population'],
        'measurement':{'mode':'identity','description':'Generated age in years, binary female, BMI kg/m^2, glucose mg/dL and HbA1c percent. Admitted projection unit conversions occur in the shared specification/evidence; feedback applies no transformation. Assay and fasting comparability remain assumptions.'},
        'assumption_ids':population_assumptions,'checks':checks})

write('algebra_derivation.json',{'kind':'deterministic_aggregate_algebra_not_simulation',
    'source_data':'Approved aggregate quantities only; no individuals, random draws, generator import or output table.',
    'conditional_coefficients':coeff,'residual_correlation':rho,
    'implied_separate_projection_bmi':beta_b+beta_g*rho*s_g/s_b,
    'implied_separate_projection_glucose':beta_g+beta_b*rho*s_b/s_g,
    'reported_separate_projection_bmi':q_b,'reported_separate_projection_glucose':q_g,
    'pre_truncation_hba1c_variance':explained+s_h*s_h,
    'pani_unweighted_band_count_sum':total_n,'hba1c_references':h_refs,
    'qualification':'Analytical equations only. They do not prove runtime output agreement or source-population validity.'})

write('evidence_grouping.json',{'source_panel_sha256':sha(B/'SOURCE_PANEL_SPEC.json'),
    'normalized_quantity_records':json.loads((B/'source_packet/normalized_quantities.json').read_text())['records'],
    'policy':'All 32 grouping records preserved. Original/derived quantities are not independent evidence. Contextual/quarantined quantities are retained and never used as numeric calibration constraints.'})

decision = '''# Initial scientific decision

This is an aggregate-constrained scenario generator for the supplied analytical design, with all five scientific variables generated. I selected a shared linear conditional HbA1c rule and correlated conditional Gaussian BMI/glucose law. Scientific parameter choices were authored from the approved four-source packet; no prior project coefficients or individual records were used.

Jansen Table 1 supplies Lifelines means/SDs and rounded sex composition. The percent HbA1c mean/SD are 5.6/0.3; the alternate IFCC marginal does not become another constraint. Jansen Table 2 supplies two separate age/sex-adjusted projection coefficients, not one joint regression. An assumed residual BMI/glucose correlation of 0.30 and modest assumed covariate age/sex trends close the covariance equations. The derived conditional BMI coefficient is smaller than its separate projection. Pani's fully adjusted age coefficient 0.010 percentage points/year is shared across contexts. This cross-source synthesis is an assumption.

The Pani reference level is a count-weighted average of its eight survey age-band means. This approximates a source location, not a survey-weighted national estimate. It avoids fitting separate age-band intercepts. The linear rule may disagree with Pani's older-age plateau; all eight means remain in the fixed feedback panel. Pani survey SEs were not converted to individual SDs. Individual HbA1c residual SD is an algebraic decomposition of Jansen's individual SD under the chosen covariance law.

Source contexts contain 6000 Monte Carlo rows each. Lifelines adult support 18-95 is assumed because actual limits were not supplied. Pani's >=70 band extends to assumed95 with declining integer-age mass and is not capped at target79. Neither source uses target balanced quotas. The target has exact supplied quotas and uniform ages within each design band. It adopts the Pani HbA1c location rule and common Lifelines-based covariate law without a Mexico-specific repair. Transfer remains weakly identified.

Liu's univariate equation and Jansen Table 3 remain contextual/quarantined. FOS is not combined with NHANES. Pani and Liu overlap in NHANES years, so no independent-replication claim is made. NGSP is unit guidance only. Jansen's printed intervals retain unknown confidence level; no coefficient SE or posterior was invented. All 32 evidence items and grouping records are retained.

Target population documentation is taken from the public task, including serum rather than plasma, recorded8-12-hour fasting, valid standing measurements and the restricted pregnancy/lactation routing. Source selection is approximated directly; anemia, medication, assay, missingness and pregnancy mechanisms are not identified. Source-to-target equivalence for these mechanisms is an assumption, not a verified exclusion or biological finding.

I stop initial scientific construction at static freeze. No generator import, local call, self-simulation, output CSV, fitted synthetic answer, source execution or analytical execution was performed. The controller owns all numerical runs. The 20 planned source checks are approximate recipes, not passed numerical tests. One source-only feedback opportunity remains; no target diagnostic may inform revision. Structural validation/freezing cannot certify model science or runtime behavior.

Individual residual variation is modeled; source-estimation, model-form and transport uncertainty are not probabilistically identified. Seed repetitions do not supply additional clinical information. This construction is unsuitable for causal inference, national prevalence estimation or substitution for clinical measurements without independent evidence.
'''
(C/'decision.md').write_text(decision,encoding='utf-8')

linkage = '''# Transfer and common scientific rule

In every context, BMI and glucose share the same conditional law:

* BMI location = 26.5 + 0.025(age-55.5) + 0.6(female-0.597).
* Glucose location = 91.8 + 0.10(age-55.5) - 1.5(female-0.597).
* Residual BMI/glucose correlation = 0.30, with their SDs derived by subtracting assumed age/female contributions from Jansen's marginal variances. Conditional pairs are redrawn for BMI>0 and 0<glucose<126 while holding age/female fixed.

The common conditional HbA1c equation is anchor HbA1c + betaAge(age-anchorAge) + betaBMI(BMI-anchorBMI) + betaGlucose(glucose-anchorGlucose) + independent residual. Anchor BMI/glucose are the same covariate-location functions evaluated at anchor age and anchor female probability. betaAge=0.010; betaBMI and betaGlucose are derived in algebra_derivation.json from the two separate Jansen Table2 projections and the assumed residual covariance. The direct female HbA1c coefficient is assumed zero. HbA1c residual SD is derived from Jansen's percent SD0.3. Coefficients, covariate trends, covariance, residual distribution and selection rule never vary by context.

For residual SDs sB,sG and assumed r, the two projection equations are qB=betaBMI+betaGlucose*r*sG/sB and qG=betaGlucose+betaBMI*r*sB/sG. Solving these equations is different from placing qB and qG together in one structural equation. The unreported r determines the decomposition: another admissible r would give different conditional coefficients. Pani's adjusted age projection constrains betaAge only under shared linearity, joint covariate and estimator assumptions. The marginal age association also includes assumed BMI/glucose age trends. All these are observational projections, never causal effects.

Context-varying inputs are the age/sex sampling distributions and HbA1c location reference. Lifelines uses its published55.5-year/0.597-female reference with HbA1c5.6. Pani uses the eight published age-band sample counts to average their survey HbA1c means, anchoring that level at the expected age under declared within-band laws and assumed female0.5. The source aggregate location is not an exactly recovered survey estimator. All Pani age-band means are checked even though the model has no band-specific intercepts. Its linear age rule can miss the observed plateau.

The target uses the identical Pani reference and identical common conditional coefficients and covariate law. Only the public target age/sex design changes: exactly250 people in each supplied intersection. There is no target-only HbA1c coefficient, tuning factor, empirical histogram or diagnostic-dependent branch. Thus source constraints act on parameters actually used in the target. There is no reason to regard this direct US/European-to-Mexico transport as established; it is a concrete unvalidated scenario necessitated by the admitted evidence boundary.

Source ancestry, selection and measurement differ. Lifelines western-European GWAS selection favors older relatives and excludes significant anemia. Pani is a US survey with a different source population and original complex-survey estimator. Target participants have no verified anemia/medication exclusion and only documented pregnancy/lactation exclusions in routed women25-49; unasked older status remains unresolved. Transporting fasting-plasma glucose relationships to target fasting serum, different assay settings and the8-12-hour fast assumes no systematic bias. Missing covariates and selection mechanisms are not repaired by unit conversion or normal residual noise.

One frozen generator and model specification serve every context; only active_context changes in controller child copies. Positivity and threshold rejection make the simple analytical moment decomposition approximate. Finite Monte Carlo errors, source reconstruction errors and source-estimation uncertainty have different origins. Numerical source agreement, if obtained, would not identify the joint law or validate target analyses.
'''
(C/'transfer_linkage.md').write_text(linkage,encoding='utf-8')

# Static checks of authored bytes/metadata. No submitted program is imported.
ast.parse(generator)
assert len(evidence['items']) == 32 and len(evidence['sources']) == 4
assert sha(C/'evidence.json') == sha(B/'evidence_template.json')
assert abs(beta_b+beta_g*rho*s_g/s_b-q_b) < 1e-12
assert abs(beta_g+beta_b*rho*s_b/s_g-q_g) < 1e-12
assert abs(explained+s_h*s_h-0.09) < 1e-12
assert len(panel['contexts'][0]['checks']) == 11 and len(panel['contexts'][1]['checks']) == 9
for source_context in panel['contexts']:
    name=source_context['id']
    recipe=json.loads((C/f'source_contexts/{name}/whole_cohort_feedback.json').read_text())
    for expected, actual in zip(source_context['checks'],recipe['checks']):
        assert expected['id']==actual['id'] and expected['evidence_id']==actual['evidence_id']
        assert expected['operator']==actual['operator']
write('static_authoring_audit.json',{'status':'pass','scope':'static source-only artifact and aggregate algebra audit',
    'generator_imported':False,'generator_called':False,'rows_generated':0,
    'checks':['Python AST parse without import','exact evidence byte equality:32 items4 sources',
              'both separate projection identities checked by deterministic scalar algebra',
              'pre-truncation HbA1c variance identity checked by deterministic scalar algebra',
              'all20 fixed check IDs/evidence IDs/operators retained verbatim'],
    'scientific_validity':'not_assessed','runtime_behavior':'not_executed'})
aux_names=['transfer_linkage.md','source_context_plan.json','algebra_derivation.json','evidence_grouping.json','static_authoring_audit.json']
for name in ('lifelines','pani'):
    aux_names += [f'source_contexts/{name}/task.json',f'source_contexts/{name}/whole_cohort_feedback.json']
write('checks.json',{'scope':'source_only','records':[
    {'name':'static_artifacts_and_algebra','status':'pass','detail':'Actual non-executing AST, evidence-byte, fixed-operator and deterministic aggregate algebra checks recorded in static_authoring_audit.json; no patient tables or scientific runtime conclusions.'},
    {'name':'numerical_source_validation','status':'not_computable','detail':'No controller source execution/report exists at authoring time. All20 source recipes are planned approximate diagnostics, not numerical passes.'},
    {'name':'target_validity','status':'not_computable','detail':'No target data or diagnostics supplied or inspected; scientific and transport validity are unassessed.'}],
    'artifacts':[{'path':name,'sha256':sha(C/name)} for name in aux_names]})
print(json.dumps({'candidate':str(C),'individual_rows_generated':0,'derived_coefficients':coeff,'pani_reference':h_refs['pani']},indent=2))
