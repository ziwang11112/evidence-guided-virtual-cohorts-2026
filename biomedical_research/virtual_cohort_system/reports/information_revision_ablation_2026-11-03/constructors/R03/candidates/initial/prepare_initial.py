"""Retain trial scientific model and bind its real permitted feedback; no rows."""
import hashlib
import json
import math
from pathlib import Path
from scipy.special import ndtri

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'mixture_trial01'
ROOT=HERE.parents[2]
FEEDBACK=ROOT/'session/feedback/a01_initial_4201.json'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def write(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

# All copied material is our own trial candidate. Never copy its freeze receipt.
for file in OLD.iterdir():
    if file.is_file() and file.name!='freeze.json':
        (HERE/file.name).write_bytes(file.read_bytes())
(HERE/'trial4201_feedback.json').write_bytes(FEEDBACK.read_bytes())
feedback=read(FEEDBACK)
assert feedback['status']=='success'
assert feedback['semantic_feedback_v1']['n_computable']==30
analysis=feedback['analysis_feedback']
spec=read(HERE/'model_spec.json')
ref=read(HERE.parent.parent/'input/reference_summary.json')
rows=analysis['analyses']+analysis['diagnostics']
assert len(rows)==30
means=[]
for variable in ['age','female','bmi','glucose','hba1c']:
    r=next(x for x in rows if x['id']==variable+'_mean')
    variance=ref['diagnostics']['marginal'][variable]['sd']**2
    if variable=='female':
        p=spec['parameters']['female_probability']
        variance=p*(1-p)
    se=math.sqrt(variance/3000)
    means.append({'variable':variable,'synthetic_mean':r['value'],
        'working_population_mean':r['reference'],'difference':r['difference'],
        'model_based_iid_mean_sd':se,'difference_divided_by_model_sd':r['difference']/se,
        'scope':'Finite-cohort model variability only; not reference sampling or structural uncertainty.'})
bp=spec['parameters']
bmi_quantiles=[]
for name,q in [('q10',.1),('median',.5),('q90',.9)]:
    model=math.exp(bp['bmi_log_mean']+bp['bmi_log_sd']*float(ndtri(q)))
    target=ref['diagnostics']['marginal']['bmi'][name]
    observed=next(x['value'] for x in rows if x['id']=='bmi_'+name)
    bmi_quantiles.append({'statistic':name,'model_population':model,'reference':target,
        'structural_approximation_difference':model-target,'trial':observed,
        'trial_minus_model':observed-model})
interpretation={
 'parent_candidate':'mixture_trial01','new_candidate':'mixture_initial01',
 'decision':'retain','requested_stage':'initial_delivery_4101_4102_4103',
 'feedback_path':'trial4201_feedback.json','feedback_sha256':sha(HERE/'trial4201_feedback.json'),
 'all_30_feedback_statistics':rows,'quality':analysis['quality'],
 'finite_cohort_mean_diagnostics':means,'bmi_quantile_approximation':bmi_quantiles,
 'scientific_files_unchanged':{name:sha(HERE/name)==sha(OLD/name) for name in ['generator.py','model_spec.json','evidence.json']},
 'reason':'The first isolated draw succeeds. Population moment equations match the admitted working anchors by construction. All mean differences are modest relative to conditional model-based sampling SD; this is compatible with finite-cohort variation. A single trial and no Monte Carlo uncertainty estimate do not prove the cause of every discrepancy. Preserve the pre-trial scientific model, acknowledge BMI family approximation and continuous-tie simplification, and assess the three fixed delivery seeds without seed selection.',
 'limitations':['Source-context replay remains not_computable.',
  'Reference agreement is a development fit, not independent validation.',
  'Pearson/Spearman and projection Monte Carlo uncertainty is not estimated by the supplied trial report.',
  'Sex independence, latent mixture nesting, tail behavior and unreported covariate couplings remain assumptions.',
  'No fitted value is altered to compensate for the observed trial seed.'],
 'row_producing_local_execution':False,
 'retrieval':{'queries':[],'documents':[]}}
write('trial_interpretation.json',interpretation)
checks=read(HERE/'checks.json')
for record in checks['records']:
    if record['name']=='isolated_output_contract':
        record['status']='pass'
        record['detail']='Coordinator trial4201 succeeded with verified output linkage and all 30 task statistics computed on 3000 rows. No nonpositive glycemia or duplicate measurement rows. This certifies that execution only; the new candidate has identical generator/specification bytes and awaits fixed initial delivery.'
checks['records'].append({'name':'trial4201_review_and_retention','status':'pass',
 'detail':'Actual full feedback and interpretation are bound. All 30 values and semantics reviewed. Retain unchanged scientific parameters; finite-seed differences are compatible with conditional variability but not proven purely random. BMI quantile family approximation is separated analytically. No source replay or independent validation claimed.'})
for name in ['trial4201_feedback.json','trial_interpretation.json']:
    checks['artifacts'].append({'path':name,'sha256':sha(HERE/name)})
write('checks.json',checks)
prior=(HERE/'decision.md').read_text(encoding='utf-8')
(HERE/'decision.md').write_text(prior+'''

## Initial delivery decision after actual trial4201

Retain the scientific model in a new unfrozen candidate, mixture_initial01. The generator, model specification and evidence bytes are identical to mixture_trial01. Bind the complete actual feedback and trial_interpretation.json. The trial produced 3000 valid rows and all 30 requested statistics; no nonpositive glycemia or duplicate measurement rows were reported.

E1=0.0605241, E2=0.401491 and E3=0.00754840; Pearson=0.646977 and Spearman=0.349772. Age quantiles and all binary quantiles match the working anchors. Glycemic SDs are somewhat higher in this draw, while glycemic population moments are anchored by deterministic equations. Model-based mean sampling SD calculations suggest ordinary finite-cohort fluctuations are a plausible explanation, not proof that every discrepancy is noise. The source reference coefficient intervals are not used as synthetic-cohort acceptance thresholds.

BMI population quantiles differ slightly from the reference because its lognormal family is fitted only to mean and SD. That structural approximation is separated from trial fluctuation in the retained interpretation artifact. Female independence, copula/mixture assumptions, continuous HbA1c versus tied reference measurements, and source-transfer uncertainty remain unresolved. No scientific parameter changes, seed selection or additional trial are justified by this one draw.

Requested next stage: initial delivery at fixed seeds 4101, 4102 and 4103. The earlier trial-stage request above is historical. No new retrieval or local row generation occurred.
''',encoding='utf-8')
print(json.dumps({'candidate':HERE.name,'stage':'initial_delivery','retained':interpretation['scientific_files_unchanged'],'mean_diagnostics':means,'bmi_quantiles':bmi_quantiles},indent=2))
