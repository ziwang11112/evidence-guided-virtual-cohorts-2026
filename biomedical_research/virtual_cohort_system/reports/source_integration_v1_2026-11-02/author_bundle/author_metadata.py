"""Emit a single source-only candidate. No generator import, RNG, or row creation."""
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parent
C = ROOT / 'candidates' / 'initial'
E = json.loads((C / 'evidence.json').read_text(encoding='utf-8-sig'))
TASK = json.loads((ROOT / 'task.json').read_text(encoding='utf-8-sig'))
ITEM = {x['id']: x for x in E['items']}
SOURCE = {x['id']: x for x in E['sources']}
EVIDENCE_BYTES = (C / 'evidence.json').read_bytes()

def write(name, value):
    (C / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def log_params(mean, sd):
    variance = math.log1p((sd / mean) ** 2)
    return math.log(mean) - variance / 2, math.sqrt(variance)

def cdf(x):
    return (1 + math.erf(x / math.sqrt(2))) / 2

def age_normal(lo, hi, mean, sd):
    ages = list(range(lo, hi + 1))
    mass = [cdf((a + .5 - mean) / sd) - cdf((a - .5 - mean) / sd) for a in ages]
    return ages, [p / sum(mass) for p in mass]

def age_bao():
    # Piecewise probability interpolation, not conversion of quartiles to SD.
    knots = [19.5, 37.9, 49.4, 57.7, 80.5]
    def f(x):
        if x <= knots[0]: return 0.0
        if x >= knots[-1]: return 1.0
        j = next(i for i in range(4) if knots[i] <= x <= knots[i + 1])
        return .25 * (j + (x - knots[j]) / (knots[j + 1] - knots[j]))
    ages = list(range(20, 81))
    return ages, [f(a + .5) - f(a - .5) for a in ages]

ASSUMPTIONS = {
 'A_LAW': 'Within each context, BMI, unbounded glucose precursor and HbA1c have lognormal marginal laws joined by a Gaussian latent model. This is a distributional assumption, not identified by the reported summaries. J alone clips observed glucose at 6.999 mmol/L; clipping is not conditional truncation and creates an upper atom. No individual rows are reconstructed.',
 'A_AGESEX': 'Age and female membership are independent of each other and of all biomarker latent drivers. This deliberately sparse scenario assumes no age or sex association; absence of a reported relationship is not evidence for this independence. In particular the population A_AGE coefficient is zero by assumption, not a source-supported target result. No age/sex interactions are represented.',
 'A_BG': 'The latent Gaussian BMI-glucose correlation is 0.25 in every context. It is not the raw-scale correlation and is not reported by the packet. J separate projections identify the residual BMI-HbA1c loading only conditional on this choice and the marginal laws.',
 'A_PROJECTION': 'For construction only, J separate age/gender-adjusted BMI and FPG coefficients are interpreted as marginal biomarker projections because modeled age and female are independent. Each slope is converted to its own pairwise latent correlation using lognormal covariance identities. The two reported slopes are never installed as simultaneous regression coefficients. The FPG identity is applied before J glucose clipping, so the eventual clipped FPG projection can differ from the reported value.',
 'A_MARGINALS': 'Source means/individual SDs set lognormal source scale inputs. Bao log-location uses its median and log-dispersion uses the difference of log quartile endpoints divided by twice the standard-normal 0.75 quantile, under a lognormal shape assumption; this is not an empirical SD estimate. Rounded/asymmetric source quantiles need not all be reproduced. Source SDs and unknown-level intervals are not estimator SEs or weights.',
 'A_SOURCE_AGES': 'Source integer ages have explicit finite probability masses. J uses discretized normal-shape weights from mean 55.5 and SD 9.9 over assumed adult support 18 through 81; the upper age bound is a modeling choice. Bao includes integer 20, takes assumed upper bound 80, and interpolates its three quantiles with piecewise-uniform probability mass before integer coarsening. M uses discretized normal-shape weights from mean 69.5 and SD 4.2 over 61 through 80. Truncation/coarsening changes original moments and quantiles; original fractional ages and rounding cannot be recovered.',
 'A_J_SELECTION': 'J is a scenario conditional on all reported eligibility criteria. Glucose <7 is enforced in generated columns; self-reported diabetes, anemia, relatedness, ancestry/GWAS selection and availability of original erythrocyte/FPG/HbA1c records are unobserved conditioning assumptions, not verified exclusions.',
 'A_B_SELECTION': 'Bao integer age 20 is included by convention because the under-20 exclusion and over-20 prose disagree. Prior diagnosed diabetes, cancer, severe psychiatric disturbance, chronic kidney disease, pregnancy, glucocorticoids and questionnaire exclusions are unobserved conditioning assumptions. Screen-detected diabetes remains allowed; there is no upper glucose cutoff.',
 'A_M_SELECTION': 'M represents selected follow-up at age 61-80, conditional on being free of dementia and functional disability, neither of which is observed here. Known diabetes is included. The dependence law links prior-year BMI/demographics to later labs without an identified longitudinal model; published imputation impacts cannot be reconstructed.',
 'A_T_POP': 'T describes only the supplied selected analytical population; no participant observations, target moments, target effects, treatment/pregnancy exclusions or population weights were supplied. Integer age is uniform 35-74 and female probability 0.5 by prior choice. Assumed positive biomarker mean/SD pairs are BMI 25/4.5, glucose 5.7/1.2, HbA1c 6.0/0.8. These are hypothetical scale choices, not known target summaries.',
 'A_TRANSFER': 'The residual BMI loading identified under J assumptions is shared in all contexts. For unrestricted contexts, glucose-HbA1c latent correlation is a linear function of glucose log-dispersion through the Bao and MIND anchors; dormant T uses this same function at its assumed dispersion, between the two anchors. This unvalidated transport scenario links sources to T; it is not meta-analysis, precision weighting, evidence of a universal biological mechanism, or permission to tune target parameters from feedback.',
 'A_B_CORR': 'Bao reported Pearson is interpreted as a raw-scale population Pearson anchor under equal-weight complete generated rows. The lognormal covariance identity converts that Pearson anchor into a latent Gaussian correlation; it is not reinterpreted as a residual correlation.',
 'A_M_CORR': 'MIND reported Spearman is interpreted as a marginal rank-correlation anchor. Under continuous Gaussian copula marginals only, latent rho=2*sin(pi*r_s/6). The reviewed check remains Spearman with average ties, never Pearson. Original tie handling and imputation remain unresolved; finite precision may introduce ties.',
 'A_EQUAL': 'Qualified source comparisons use every complete generated row with equal weights and missing_policy error. Original weighting and exact estimator-row processing are unknown; this defines a qualified scenario, not strict reproduction. There is no empirical uncertainty or confidence-interval pass criterion.',
 'A_ALIAS': 'Native source aliases are read-only names for this context: BMI=bmi; FPG=glucose in J/B; FSG=glucose in M; HbA1c_percent=hba1c. They do not prove assay, specimen, fasting or timing equivalence across contexts. M FSG is the reported serum assay and never its separately mentioned plasma assay.',
 'A_GENDER': 'female is integer 1 for female and 0 for male with source fractions derived from the packet counts. gender_binary aliases this category partition in J; original coding is unresolved. For the specified intercept-including, no-interaction OLS, reversing binary nuisance coding preserves the focal coefficient under full rank and identical rows.',
 'A_UNITS': 'HbA1c output is represented on NGSP percent scale. For J only, native IFCC response is (HbA1c_percent-2.152)/0.09148 using U_NGSP_SCALE. The same equation converts J mean and individual SD for model scale inputs, with offset only for the mean. This deterministic scale relation does not assert assay equivalence. The positive lognormal NGSP law has nonzero probability below 2.152, which maps to a negative IFCC value; this extreme-tail support mismatch remains a scientific limitation and is not repaired by the point-comparison mapping.',
 'A_POINT': 'Only point-functionals are planned. All population predictor moment matrices are nonsingular under positive marginal dispersions, nondegenerate age/female, independent age/female and a nondegenerate bivariate biomarker density (including J interior below its clipping atom). Finite realized samples can still lack category or age variation; runtime rank/category checks must decide that. No interval inference is certified.',
 'A_SCHEDULE': 'One initial candidate and fixed source draws J=23011, B=23012, M=23013 at 1000 rows each. T=23999/3000 is a dormant mechanical slot, never authorized for dispatch in this unit. Seeds and rows are not extra clinical evidence. No construction samples or source diagnostics have been run.'
}

z75 = 0.6744897501960817
unit = {'ngsp_percent_per_ifcc': .09148, 'ngsp_percent_intercept': 2.152}
jmH, jsH = 38 * unit['ngsp_percent_per_ifcc'] + unit['ngsp_percent_intercept'], 3 * unit['ngsp_percent_per_ifcc']
jB, jG, jH = log_params(26.5, 4.1), log_params(5.1, .5), log_params(jmH, jsH)
bB = (math.log(23.5), (math.log(25.9)-math.log(21.4))/(2*z75))
bG = (math.log(5.2), (math.log(5.6)-math.log(4.8))/(2*z75))
bH = (math.log(5.6), (math.log(5.9)-math.log(5.3))/(2*z75))
mB, mG, mH = log_params(25, 3.6), log_params(5.2, 1.4), log_params(6.1, 1)
tB, tG, tH = log_params(25, 4.5), log_params(5.7, 1.2), log_params(6, .8)
q = .25
j_r_bh = math.log1p((.13*.09148) * 4.1**2/(jmH*26.5))/(jB[1]*jH[1])
j_r_gh = math.log1p((2.29*.09148) * .5**2/(jmH*5.1))/(jG[1]*jH[1])
k = (j_r_bh - q*j_r_gh)/math.sqrt(1-q*q)
b_r = math.log1p(.619*math.sqrt(math.expm1(bG[1]**2)*math.expm1(bH[1]**2)))/(bG[1]*bH[1])
m_r = 2*math.sin(math.pi*.529/6)
dep = {'bmi_glucose_latent_correlation':q, 'shared_bmi_residual_loading':k,
       'jansen_restricted_latent_correlation':j_r_gh, 'bao_latent_correlation':b_r,
       'mind_latent_correlation':m_r, 'bao_glucose_log_sd':bG[1], 'mind_glucose_log_sd':mG[1]}

source_ids = {'J':'S_JANSEN_2013','B':'S_BAO_2010','M':'S_MIND_2024'}
population = {x: SOURCE[s]['population'] for x,s in source_ids.items()}
population['T'] = TASK['population']
measurement = {x: SOURCE[s]['measurement'] for x,s in source_ids.items()}
measurement['T'] = 'Target age in integer years, female 0/1, BMI kg/m^2 from released height/weight, central-serum glucose mmol/L and whole-blood HbA1c percent under the supplied analytical release policy; no assay equivalence to sources is asserted.'
ageJ, ageB, ageM = age_normal(18,81,55.5,9.9), age_bao(), age_normal(61,80,69.5,4.2)
ageT = (list(range(35,75)), [.025]*40)
contexts = {}
for ident, age, female, B, G, H, cap, rule in [
 ('J',ageJ,1-1176/2921,jB,jG,jH,6.999,'restricted'),
 ('B',ageB,3058/4886,bB,bG,bH,None,'unrestricted'),
 ('M',ageM,2049/3547,mB,mG,mH,None,'unrestricted'),
 ('T',ageT,.5,tB,tG,tH,None,'unrestricted')]:
    contexts[ident] = {'population':population[ident], 'n_rows':3000 if ident=='T' else 1000,
        'measurement':measurement[ident], 'inputs':{'age_values':age[0], 'age_probabilities':age[1],
        'female_probability':female, 'bmi_log_mean':B[0], 'bmi_log_sd':B[1],
        'glucose_log_mean':G[0], 'glucose_log_sd':G[1], 'hba1c_log_mean':H[0], 'hba1c_log_sd':H[1],
        'glucose_upper_clip':cap, 'dependence_rule':rule}}
params = {'active_context':'T', 'contexts':contexts, 'dependence':dep, 'unit_mapping':unit}
prov = {
 'active_context': {'evidence_ids':[], 'assumption_ids':['A_SCHEDULE'], 'derivation':'Dormant target context required by bridge ABI; no target dispatch authorized.'},
 'contexts': {'evidence_ids':[x['id'] for x in E['items'] if x['id'].startswith('M_')]+['U_NGSP_SCALE'],
 'assumption_ids':['A_LAW','A_MARGINALS','A_SOURCE_AGES','A_J_SELECTION','A_B_SELECTION','A_M_SELECTION','A_T_POP','A_ALIAS','A_GENDER','A_UNITS'],
 'derivation':'J/M mean-SD pairs use sigma_log=sqrt(log(1+(sd/mean)^2)), mu_log=log(mean)-sigma_log^2/2. J HbA1c mean/SD use NGSP mapping. Bao medians and log-IQR determine lognormal scale under assumption, not an observed SD. Source age masses and sex fractions follow stated constructions. T values are explicit assumptions. Source context descriptions and counts are administrative, not target statistics.'},
 'dependence': {'evidence_ids':['R_JANSEN_BMI','R_JANSEN_FPG','R_BAO_PEARSON','R_MIND_SPEARMAN','U_NGSP_SCALE','M_J_BMI_MEAN','M_J_BMI_SD','M_J_FPG_MEAN','M_J_FPG_SD','M_J_HBA1C_IFCC_MEAN','M_J_HBA1C_IFCC_SD','M_B_FPG_Q1','M_B_FPG_Q3','M_B_HBA1C_PERCENT_Q1','M_B_HBA1C_PERCENT_Q3','M_M_FSG_MEAN','M_M_FSG_SD'],
 'assumption_ids':['A_LAW','A_AGESEX','A_BG','A_PROJECTION','A_MARGINALS','A_B_CORR','A_M_CORR','A_TRANSFER','A_EQUAL','A_UNITS'],
 'derivation':'For J each separate projection beta_X becomes rho_XH=log(1+beta_X*Var(X)/(E(X)*E(H)))/(sigma_log_X*sigma_log_H), after slope scale conversion; FPG formula precedes clipping. Let q=.25 and k=(rho_BH-q*rho_GH)/sqrt(1-q^2). Bao rho=log(1+r_P*sqrt(expm1(sigmaG^2)*expm1(sigmaH^2)))/(sigmaG*sigmaH). M rho=2*sin(pi*r_S/6). In B/M/T use rho=rho_B+(rho_M-rho_B)*(sigmaG-sigmaG_B)/(sigmaG_M-sigmaG_B). No coefficient/CI pooling or sampled calibration.'},
 'unit_mapping': {'evidence_ids':['U_NGSP_SCALE'], 'assumption_ids':['A_UNITS'], 'derivation':'Admitted NGSP percent=0.09148*IFCC+2.152; deterministic representation only.'}
}
spec = {'parameters':params,'assumptions':[{'id':a,'description':d} for a,d in ASSUMPTIONS.items()], 'parameter_provenance':prov}
write('model_spec.json',spec)

def rho_for(c):
    if c['dependence_rule']=='restricted': return dep['jansen_restricted_latent_correlation']
    return b_r+(m_r-b_r)*(c['glucose_log_sd']-bG[1])/(mG[1]-bG[1])

def ref(n): return {'op':'ref','name':n}
def aff(e,a,b=0): return {'op':'affine','input':e,'scale':a,'shift':b}
def summ(*terms): return {'op':'sum','terms':list(terms)}
laws = {}
for ident, desc in contexts.items():
    c=desc['inputs']; r=rho_for(c); rem=1-r*r-k*k
    assert rem>0 and abs(q)<1
    v={'age':{'op':'mixture','components':[{'weight':p,'law':{'op':'constant','value':a}} for a,p in zip(c['age_values'],c['age_probabilities'])]},
       'female':{'op':'bernoulli','p':c['female_probability']},
       'z_g':{'op':'normal','mean':0,'sd':1},'z_b':{'op':'normal','mean':0,'sd':1},'z_h':{'op':'normal','mean':0,'sd':1},
       'bmi_latent':summ(aff(ref('z_g'),q),aff(ref('z_b'),math.sqrt(1-q*q))),
       'hba1c_latent':summ(aff(ref('z_g'),r),aff(ref('z_b'),k),aff(ref('z_h'),math.sqrt(rem))),
       'bmi':{'op':'exp','input':aff(ref('bmi_latent'),c['bmi_log_sd'],c['bmi_log_mean'])},
       'glucose_precursor':{'op':'exp','input':aff(ref('z_g'),c['glucose_log_sd'],c['glucose_log_mean'])},
       'glucose':ref('glucose_precursor') if c['glucose_upper_clip'] is None else {'op':'clip','input':ref('glucose_precursor'),'lower':0,'upper':c['glucose_upper_clip']},
       'hba1c':{'op':'exp','input':aff(ref('hba1c_latent'),c['hba1c_log_sd'],c['hba1c_log_mean'])}}
    laws[ident]={'schema_version':'scientific_validity_v1','variables':v,
      'independence':[['age','female','z_g','z_b','z_h']],
      'analyses':[{'id':'A_BMI','kind':'ols','outcome':'hba1c','predictors':['age','female','bmi']},
                  {'id':'A_GLUCOSE','kind':'ols','outcome':'hba1c','predictors':['age','female','glucose']},
                  {'id':'A_AGE','kind':'ols','outcome':'hba1c','predictors':['age','female','bmi','glucose']}]}
write('scientific_validity_v1.json',{'schema_version':1,'context_laws':laws})

context_as = {x:['A_LAW','A_AGESEX','A_BG','A_MARGINALS','A_SOURCE_AGES','A_ALIAS','A_GENDER','A_POINT',f'A_{x}_SELECTION'] for x in 'JBM'}
context_as['J'] += ['A_PROJECTION','A_UNITS','A_EQUAL']
context_as['B'] += ['A_B_CORR','A_TRANSFER','A_EQUAL']
context_as['M'] += ['A_M_CORR','A_TRANSFER','A_EQUAL']
context_as['T'] = ['A_LAW','A_AGESEX','A_BG','A_T_POP','A_TRANSFER','A_POINT','A_SCHEDULE']
relation_ids={'J':[('J_bmi','R_JANSEN_BMI'),('J_fpg','R_JANSEN_FPG')], 'B':[('B_pearson','R_BAO_PEARSON')], 'M':[('M_spearman','R_MIND_SPEARMAN')]}
reasons={
 'J':'Original weights, exact regression rows/processing and original intercept convention are not certified. The original source operator therefore remains unavailable; a distinct qualified native-unit OLS uses disclosed conventions.',
 'B':'Original weights and correlation-specific missing processing are unreported. A distinct complete-row equal-weight Pearson scenario does not repair strict replay.',
 'M':'Original weights, imputation impacts and correlation tie handling are unreported. A distinct complete-row equal-weight Spearman scenario with average ties does not repair strict replay.'}
bridge_contexts=[]; qualified={}
for ident in 'JBMT':
    base={'id':ident,'role':'target' if ident=='T' else 'source','source_ids':[] if ident=='T' else [source_ids[ident]],
          'assumption_ids':context_as[ident], 'feedback_policy':'none' if ident=='T' else 'semantic_v1',
          'recipe':None,'semantics':None,'supplement':None}
    if ident!='T':
        base['recipe']={'schema_version':1,'population':population[ident], 'measurement':{'mode':'identity','description':measurement[ident]},
          'assumption_ids':context_as[ident], 'checks':[{'id':cid,'evidence_id':eid,'status':'not_computable','operator':None,'assumption_ids':['A_EQUAL'],'reason':reasons[ident]} for cid,eid in relation_ids[ident]]}
        base['semantics']={'schema_version':1,'evidence_sha256':'','recipe_sha256':'','bindings':[
          {'check_id':cid,'evidence_id':eid,'source_locator':ITEM[eid]['locator'],'definition_status':'not_reported',
           'source_operator':None,'weights':'not_reported','transform':'identity','source_variable_units':{},
           'source_n':{'status':'not_reported'},'uncertainty_role':'not_reported','reason':reasons[ident]} for cid,eid in relation_ids[ident]]}
        aliases=[{'source_name':'HbA1c_percent','generated_name':'hba1c','assumption_ids':['A_ALIAS','A_UNITS']}]
        aliases += [{'source_name':'FSG' if ident=='M' else 'FPG','generated_name':'glucose','assumption_ids':['A_ALIAS']}]
        if ident=='J':
            aliases += [{'source_name':'BMI','generated_name':'bmi','assumption_ids':['A_ALIAS']}, {'source_name':'gender_binary','generated_name':'female','assumption_ids':['A_GENDER']}]
        qc=[]
        for cid,eid in relation_ids[ident]:
            item=ITEM[eid]
            op={'kind':item['kind'],'unit':item['unit'],'selection':[],'missing_policy':'error'}
            if ident=='J':
                term='BMI' if cid=='J_bmi' else 'FPG'
                op.update(outcome='HbA1c_IFCC',predictors=['age','gender_binary',term],term=term,include_intercept=True)
                mapping={'kind':'hba1c_ngsp_to_ifcc','input_column':'HbA1c_percent','output_column':'HbA1c_IFCC',**unit,'unit_evidence_id':'U_NGSP_SCALE','assumption_ids':['A_UNITS']}
            else:
                op.update(x='FPG' if ident=='B' else 'FSG',y='HbA1c_percent'); mapping={'kind':'identity'}
            qc.append({'id':'Q_'+cid,'evidence_id':eid,'semantic_check_id':cid,'operator':op,
              'source_relation':{'kind':'same_reported_functional_under_declared_assumptions','assumed_weights':'equal','assumption_ids':context_as[ident],
                 'unresolved_original_details':[reasons[ident]],'reason':'Native functional and adjustment preserved; all complete generated rows, equal weights, explicit J intercept and M average ties. Qualified point comparison only.'},'measurement_mapping':mapping})
        qualified[ident]={'schema_version':1,'bindings':{},
          'context_role':'source','context_id':ident,'population':population[ident],'measurement':measurement[ident], 'source_ids':[source_ids[ident]],
          'assumption_ids':context_as[ident],'column_aliases':aliases,'checks':qc}
    bridge_contexts.append(base)
bridge={'schema_version':1,'shared_parameters':['dependence','unit_mapping'],
 'context_varying_parameters':[{'name':name,'reason':'Source scale/selection or assumed target input; scientific provenance is in contexts and named assumptions.',
  'evidence_ids':prov['contexts']['evidence_ids'],'assumption_ids':prov['contexts']['assumption_ids']+['A_TRANSFER']} for name in contexts['J']['inputs']],
 'contexts':bridge_contexts,'trials':[{'id':name,'context_id':ident,'seed':seed,'n_rows':contexts[ident]['n_rows']} for name,ident,seed in [('srcJ','J',23011),('srcB','B',23012),('srcM','M',23013),('dormantT','T',23999)]],
 'execution_limits':{'timeout_seconds':60,'memory_mb':1536,'output_bytes':4000000,'log_bytes':20000},
 'budget':{'source_attempts':3,'source_rows':3000,'target_attempts':1,'target_rows':3000}}
write('context_bridge_v1.json',bridge)
write('qualified_plan_v1.json',{'schema_version':1,'contexts':qualified})
eligible={}
for ident,desc in contexts.items():
    ages=desc['inputs']['age_values']
    conditions=[{'column':'age','op':'ge','value':min(ages)},{'column':'age','op':'le','value':max(ages)},
      {'column':'female','op':'ge','value':0},{'column':'female','op':'le','value':1},
      {'column':'bmi','op':'gt','value':0},{'column':'glucose','op':'gt','value':0},{'column':'hba1c','op':'gt','value':0}]
    if ident=='J': conditions.append({'column':'glucose','op':'lt','value':7})
    eligible[ident]={'output_conditions':conditions,'unobserved_selection_assumptions':[f'A_{ident}_SELECTION'] if ident!='T' else ['A_T_POP'],
      'notes':['Task contract separately enforces integer age and female, unique identifiers and complete finite values.',
       ASSUMPTIONS[f'A_{ident}_SELECTION'] if ident!='T' else ASSUMPTIONS['A_T_POP']]}
write('context_eligibility.json',{'schema_version':1,'contexts':eligible})

use=[]
rid={eid:(ident,cid) for ident,pairs in relation_ids.items() for cid,eid in pairs}
for item in E['items']:
    eid=item['id']; sid=item['source_id']; ident=next((x for x,s in source_ids.items() if s==sid),None)
    row={'evidence_id':eid,'role':'qualitative_context','source_reference':{'source_id':sid,'source_sha256':digest(SOURCE[sid]),'item_sha256':digest(item)},
      'context_id':ident,'check_ids':[],'parameter_names':['contexts'],'structure_names':['generate'],
      'code_references':[{'path':'generator.py','symbol':'generate'}],'assumption_ids':['A_MARGINALS','A_SOURCE_AGES','A_GENDER'],
      'gaps':[],'rationale':'Used as source distribution/composition context and parameter input under explicit shape/coarsening assumptions. No marginal numerical check is scheduled and no fidelity claim follows; this role records contextual use, not an unused statistic. Related summaries remain one source group.', 'source_comparison':'not_applicable'}
    if eid in rid:
        ident,cid=rid[eid]
        aa=context_as[ident]
        row.update(role='qualified_numerical_comparison',context_id=ident,check_ids=[cid],parameter_names=['dependence','contexts'],structure_names=['dependence_rho','generate'],
          code_references=[{'path':'generator.py','symbol':'dependence_rho'},{'path':'generator.py','symbol':'generate'}],assumption_ids=aa,
          gaps=[{'id':'unknown_estimator','dimension':'uncertainty','description':reasons[ident],'assumption_ids':['A_EQUAL']},
                {'id':'joint_law','dimension':'joint_distribution','description':'Sparse source statistics do not identify the Gaussian/lognormal joint law or target transfer.','assumption_ids':['A_LAW','A_BG']}],
          rationale='Numerically exercised only by its separately qualified native functional after authorized execution. Its reported point informs the declared latent model using the distinct analytical derivations in parameter provenance; no draw or discrepancy has been calculated.',source_comparison='qualified')
    if eid=='U_NGSP_SCALE':
        row.update(context_id='J',parameter_names=['unit_mapping','contexts','dependence'],assumption_ids=['A_UNITS'],
          rationale='Actively used to derive J model HbA1c scale/converted projection slopes and native-unit qualified response mapping. Deterministic unit guidance is not a participant study or independent numerical constraint.')
    use.append(row)
write('evidence_use_v1.json',{'schema_version':1,'evidence_sha256':digest(E),'items':use})

analyses=[]
for aid,exposure,adjust,eids in [('A_BMI','bmi',['age','female'],['R_JANSEN_BMI']),
 ('A_GLUCOSE','glucose',['age','female'],['R_JANSEN_FPG','R_BAO_PEARSON','R_MIND_SPEARMAN']),
 ('A_AGE','age',['female','bmi','glucose'],[])]:
    aa=['A_LAW','A_AGESEX','A_BG','A_T_POP','A_TRANSFER','A_POINT','A_ALIAS','A_EQUAL','A_UNITS']
    dimensions=['estimand','population','measurement','selection','conditioning','adjustment','scale','joint_distribution','uncertainty']
    gaps=[{'id':'G_'+d,'dimension':d,'description':{'estimand':'No target adjusted coefficient is reported.',
      'population':'No target participant distribution or age/sex composition is supplied.',
      'measurement':'Source assay, specimen, timing and target correspondence are unresolved.',
      'selection':'Source exclusions and target analytical selection differ.',
      'conditioning':'Age/sex and joint biomarker conditioning are not identified.',
      'adjustment':'Native source variable names/sets and separate projections do not establish the full target adjustment problem.',
      'scale':'J IFCC conversion is deterministic; it does not establish the target estimand or source assay equivalence.',
      'joint_distribution':'Copula form, BMI-glucose dependence and dispersion-based transport are assumptions.',
      'uncertainty':'No estimator-precision or transport-uncertainty model is supplied.'}[d],
      'consequence':'This analytical use remains assumption-dependent; source fit cannot close this gap.','assumption_ids':aa} for d in dimensions]
    links=[{'evidence_id':eid,'relation':'component','comparisons':{d:'unknown' for d in dimensions[:7]},'assumption_ids':aa,
            'rationale':'A native source relationship informs one component of the hypothesized joint law; it is not this target estimand.'} for eid in eids]
    analyses.append({'id':aid,'estimand':{'description':'Intercept-including OLS coefficient for '+exposure+' in the supplied selected target population.',
      'kind':'ols_coefficient','outcome':'hba1c','exposures':[exposure],'conditioning':[],'adjustment':adjust,
      'scale':'Unstandardized population linear-projection coefficient; associational, not causal.',
      'unit':{'bmi':'%/(kg/m^2)','glucose':'%/(mmol/L)','age':'%/year'}[exposure],
      'population':TASK['population'],'measurement':measurement['T'],'selection':'Frozen common-complete-case analytical population with age 35-74; no additional exclusions claimed.'},
      'assessment':'partial' if links else 'unassessed','rationale':'Source relationships partially inform the model; transfer and full joint law are unsupported.' if links else 'No age-effect evidence is admitted. The modeled absence of age association is an explicit scenario assumption, not a finding.',
      'assumption_ids':aa,'evidence_links':links,'gaps':gaps,
      'actions':[{'id':'R_context','gap_ids':[x['id'] for x in gaps],'tool':'none','request':'Obtain source-specific joint-distribution, assay, selection, adjustment and precision information relevant to this stated target coefficient.',
        'status':'unavailable','reason':'Fixed-packet source-only unit permits zero retrieval and zero target access; no gap is claimed resolved.'}]})
write('analysis_evidence.json',{'schema_version':1,'analyses':analyses})
write('checks.json',{'scope':'source_only','records':[{'name':'pre_execution','status':'not_computable','detail':'Generator not imported or executed. Metadata/static checks will be recorded only after actual completion.'}],'artifacts':[]})
assert (C/'evidence.json').read_bytes()==EVIDENCE_BYTES
print(json.dumps({'emitted_candidate':'initial','evidence_raw_sha256':hashlib.sha256(EVIDENCE_BYTES).hexdigest(),
 'context_latent_correlations':{x:rho_for(d['inputs']) for x,d in contexts.items()},
 'shared_bmi_residual_loading':k,'no_generator_import_or_sampling':True},indent=2))
