"""Prepare an unfrozen, scientifically unchanged initial delivery.

Copies prior author artifacts and actual coordinator feedback; no random calls,
generator imports, or synthetic rows occur.
"""
import hashlib
import json
import math
from pathlib import Path

here=Path(__file__).resolve().parent
prior=here.parent/'initial_mixture'
root=here.parents[2]
feedback_path=root/'session'/'feedback'/'a01_initial_4201.json'
files=['generator.py','model_spec.json','evidence.json','derive_parameters.py',
       'assemble_candidate.py','derived_parameters.json','analytic_report.json','static_report.json']
for name in files:
    (here/name).write_bytes((prior/name).read_bytes())
(here/'trial4201_feedback.json').write_bytes(feedback_path.read_bytes())
def read(path):
    return json.loads(path.read_text(encoding='utf-8'))
def write(name,value):
    (here/name).write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
feedback=read(feedback_path)
assert feedback['status']=='success'
sf=feedback['semantic_feedback_v1']
assert sf['output_link_verified'] and sf['n_computable']==30
analysis=feedback['analysis_feedback']
assert analysis['n']==3000
math_report=read(here/'analytic_report.json')
spec=read(here/'model_spec.json')['parameters']
functionals={k:v for k,v in zip(['E1','E2','E3','glucose_hba1c_pearson','glucose_hba1c_spearman'],
                               math_report['functionals_order80'])}
for variable,stats in math_report['predicted_marginals'].items():
    for statistic in ['mean','sd','q10','median','q90']:
        if statistic in stats:
            functionals[f'{variable}_{statistic}']=stats[statistic]
cumulative=0.0
for key,q in [('age_q10',.1),('age_median',.5),('age_q90',.9)]:
    cumulative=0.0
    for age,p in zip(spec['age_values'],spec['age_probabilities']):
        cumulative+=p
        if cumulative>=q:
            functionals[key]=age
            break
fp=spec['female_probability']
functionals.update(female_mean=fp,female_sd=math.sqrt(fp*(1-fp)),
                  female_q10=0,female_median=1,female_q90=1)
rows=analysis['analyses']+analysis['diagnostics']
assert len(rows)==30
assessment=[]
for row in rows:
    m=functionals[row['id']]
    assessment.append({'id':row['id'],'reference':row['reference'],'model_distribution_functional':m,
       'trial4201':row['value'],'model_minus_reference':m-row['reference'],
       'trial_minus_model':row['value']-m,'trial_minus_reference':row['difference'],
       'interpretation':'Descriptive decomposition; trial-minus-model is realized finite-draw discrepancy, not an estimated Monte Carlo interval. Population SD is compared with sample SD; nonlinear finite-sample estimators need not be unbiased.'})
report={'decision':'retain','stage_requested':'initial_delivery','seed_schedule':[4101,4102,4103],
 'trial_used':'a01_initial_4201','all_30_statistics_reviewed':True,
 'generator_unchanged':(here/'generator.py').read_bytes()==(prior/'generator.py').read_bytes(),
 'model_spec_unchanged':(here/'model_spec.json').read_bytes()==(prior/'model_spec.json').read_bytes(),
 'evidence_unchanged':(here/'evidence.json').read_bytes()==(prior/'evidence.json').read_bytes(),
 'comparisons':assessment,
 'rationale':'No implementation failure or systematic relationship mismatch demonstrated. Exact distribution-level coefficient and correlation calibration was established before this trial. One draw differs from those values. Known marginal family approximation is retained rather than retuning to this draw. No source replay or Monte Carlo uncertainty estimate is inferred.',
 'limitations':['The model remains one underidentified completion of selected-sample summaries.',
    'The glucose distribution q90 is about 0.077 below the reference despite this trial q90 being about 0.071 above it.',
    'Mixture glucose and HbA1c means exceed reference by about 0.015 and 0.014 respectively.',
    'Sex independence, component independence, continuous laboratory precision, tails and covariance completion remain assumptions.',
    'No source-population validation or calibrated uncertainty exists.']}
write('trial_assessment.json',report)
decision=(prior/'decision.md').read_text(encoding='utf-8')
decision=decision.replace('First request: freeze this candidate and execute the authorized trial seed 4201. Do not interpret its fit as population recovery.',
    'Initial delivery request: freeze this new candidate and execute fixed seeds 4101, 4102 and 4103. The generator, evidence, and model specification are byte-identical to the trial candidate. Do not interpret its fit as population recovery.')
decision+='''\n\n## Trial 4201 reviewed; scientific model retained\n\nThe isolated trial succeeded with 3,000 rows and all 30 statistics computed. There were no nonpositive glucose/HbA1c values or duplicate measurement rows. The actual feedback is bound as trial4201_feedback.json, and trial_assessment.json records every statistic against both the supplied sample summary and the pre-existing distribution calculation. Source replay remains not computable.\n\nTrial E1, E2 and E3 were 0.051973, 0.387654 and 0.00724015, compared with model-distribution values 0.0549461, 0.402093 and 0.00810704. Pearson was 0.630093 versus 0.660968, and Spearman 0.359926 versus approximately 0.361460. No scientific parameter is shifted to offset those realized differences. The single trial does not provide a Monte Carlo uncertainty estimate, and the reference's cluster-based confidence intervals are not acceptance thresholds for synthetic draws.\n\nThere is also known model-family approximation: glucose and HbA1c means are about 0.015 and 0.014 above their references; model glucose q90 is about 0.077 below the reference, whereas this finite trial q90 is about 0.071 above it. BMI lognormal median and q90 are about 0.035 and 0.076 above the references. These are retained descriptive limitations. All other finite-sample differences are recorded without manufacturing a pass threshold. No extra initial trial is needed to choose this unchanged initial delivery; later fixed delivery feedback will be reviewed under the permitted final decision cycle.\n'''
(here/'decision.md').write_text(decision,encoding='utf-8')
checks=read(prior/'checks.json')
checks['records']=[r for r in checks['records'] if r['name']!='isolated_generation_and_30_statistics']
checks['records'].extend([
 {'name':'prior_isolated_trial_output','status':'pass','detail':'Actual bound coordinator feedback reports successful seed4201 execution, output linkage, 3000 rows, and all 30 statistics computable. This is an implementation/output check, not scientific validity.'},
 {'name':'scientific_model_retention','status':'pass','detail':'Byte comparison confirms generator.py, model_spec.json and evidence.json unchanged from the frozen trial candidate; all 30 comparisons and model-family limitations recorded in trial_assessment.json.'},
 {'name':'delivery_schedule','status':'not_computable','detail':'Fixed initial delivery seeds4101/4102/4103 have not yet been executed for this candidate.'}])
checks['artifacts']=[{'path':f,'sha256':hashlib.sha256((here/f).read_bytes()).hexdigest()}
 for f in ['analytic_report.json','static_report.json','trial4201_feedback.json','trial_assessment.json']]
write('checks.json',checks)
print('Prepared delivery_initial without executing or importing any generator.')
