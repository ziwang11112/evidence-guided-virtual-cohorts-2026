"""Deterministic closed-form algebra only; no generator import or sampling."""
from pathlib import Path
import hashlib
import json
import math
from fractions import Fraction

C = Path(__file__).resolve().parent
spec = json.loads((C / 'model_spec.json').read_text(encoding='utf-8-sig'))
evidence = json.loads((C / 'evidence.json').read_text(encoding='utf-8-sig'))
p = spec['parameters']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def lognormal(settings):
    m, s = settings['arithmetic_mean'], settings['individual_sd']
    t = math.log1p((s/m)**2)
    u = math.log(m)-t/2
    return {'log_mean':u,'log_variance':t,'log_sd':math.sqrt(t),
            'mean_from_law':math.exp(u+t/2),
            'second_moment_from_law':math.exp(2*u+2*t),
            'variance_from_law':math.expm1(t)*math.exp(2*u+t),
            'first_second_moments_finite':True}

law = {'bmi':lognormal(p['bmi']), 'hba1c':lognormal(p['hba1c'])}
g = p['glucose']
w = g['upper']-g['lower']
pr = (g['arithmetic_mean']-g['lower'])/w
v = (g['individual_sd']/w)**2
k = pr*(1-pr)/v-1
alpha, beta = pr*k, (1-pr)*k
assert alpha > 0 and beta > 0
ey = alpha/(alpha+beta)
vy = alpha*beta/((alpha+beta)**2*(alpha+beta+1))
eg = g['lower']+w*ey
vg = w*w*vy
law['glucose'] = {'alpha':alpha,'beta':beta,'mean_from_law':eg,
                  'variance_from_law':vg,'second_moment_from_law':eg*eg+vg,
                  'first_second_moments_finite':True,'open_support':[g['lower'],g['upper']]}

# Exact finite-support algebra, not synthetic rows or numerical quadrature.
bands = p['design']['age_bands']
band_moments = []
for lower, upper in bands:
    m = Fraction(lower+upper, 2)
    variance = Fraction((upper-lower+1)**2-1,12)
    band_moments.append((m, variance+m*m))
age_mean = sum(x[0] for x in band_moments)/len(band_moments)
age_second = sum(x[1] for x in band_moments)/len(band_moments)
age_variance = age_second-age_mean*age_mean
law['age'] = {'mean_from_law':float(age_mean),'second_moment_from_law':float(age_second),
              'variance_from_law':float(age_variance),'exact_mean':str(age_mean),
              'exact_variance':str(age_variance),'first_second_moments_finite':True}
law['female'] = {'mean_from_law':0.5,'second_moment_from_law':0.5,
                 'variance_from_law':0.25,'first_second_moments_finite':True}
ordering = ['age','female','bmi','glucose','hba1c']
covariance = [[law[a]['variance_from_law'] if a==b else 0.0 for b in ordering] for a in ordering]

source_records = []
item_map = {i['id']:i for i in evidence['items']}
selected = [('bmi','mean','J_T1_bmi_mean_task'), ('bmi','sd','J_T1_bmi_sd_task'),
            ('glucose','mean','J_T1_glucose_mean_mg_dL_derived'), ('glucose','sd','J_T1_glucose_sd_mg_dL_derived'),
            ('hba1c','mean','J_T1_hba1c_mean_pct'), ('hba1c','sd','J_T1_hba1c_sd_pct')]
for variable, kind, item_id in selected:
    calc = law[variable]['mean_from_law'] if kind=='mean' else math.sqrt(law[variable]['variance_from_law'])
    reported = item_map[item_id]['estimate']
    assert math.isclose(calc,reported,rel_tol=1e-12,abs_tol=1e-12)
    source_records.append({'evidence_id':item_id,'source_id':'JANSEN2013',
                           'source_locator':item_map[item_id]['locator'],
                           'parameter_path':'model_spec.json#/parameters/'+variable,
                           'law_path':'generator.py:positive_marginal' if variable!='glucose' else 'generator.py:scaled_beta_block',
                           'reported_value':reported,'law_analytic_value':calc,'difference':calc-reported,
                           'kind':kind,'unit':item_map[item_id]['unit'],
                           'status':'algebraic_constraint_verified_not_independent_validation'})
scale = p['source_context']['hba1c_conversion_slope']
offset = p['source_context']['hba1c_conversion_intercept']
alternative = {'source_ifcc_mean_converted':item_map['J_T1_hba1c_mean_ifcc']['estimate']*scale+offset,
               'source_ifcc_sd_converted':item_map['J_T1_hba1c_sd_ifcc']['estimate']*scale,
               'chosen_percent_mean':p['hba1c']['arithmetic_mean'],
               'chosen_percent_sd':p['hba1c']['individual_sd'],
               'treatment':'Alternative rounded unit representations; one pair selected and no independent information counted.'}
vtrans = {'age10':float(age_variance)/100,'female':0.25,
          'bmi5':law['bmi']['variance_from_law']/25,
          'glucose10':law['glucose']['variance_from_law']/100}
projection = {}
for name, predictors in [('Q1_age10',['age10','female','bmi5','glucose10']),
                         ('Q2_bmi5',['age10','female','bmi5']),
                         ('Q3_bmi5',['age10','female','bmi5','glucose10'])]:
    projection[name] = {'predictors':predictors,'intercept':p['hba1c']['arithmetic_mean'],
                        'slopes':{x:0.0 for x in predictors},
                        'centered_gram_determinant':math.prod(vtrans[x] for x in predictors),
                        'residual_variance':law['hba1c']['variance_from_law'],
                        'basis':'Product law implies Cov(X,H)=0; positive diagonal predictor covariance.'}
assert all(v['centered_gram_determinant'] > 0 for v in projection.values())
result = {'calculation_kind':'deterministic_closed_form_algebra',
          'no_generator_import_or_execution':True,'no_random_sampling_or_quadrature':True,
          'inputs':{'model_spec_sha256':sha(C/'model_spec.json'),'evidence_sha256':sha(C/'evidence.json'),
                    'script_sha256':sha(Path(__file__))},
          'marginal_law_moments':law,
          'population_covariance':{'ordering':ordering,'matrix':covariance,
                                   'independence_is_assumption_not_evidence':True},
          'demographic_design':{'cells':len(bands)*len(p['design']['sex_values']),
                                'rows_per_cell':p['design']['rows_per_cell'],
                                'n_rows':len(bands)*len(p['design']['sex_values'])*p['design']['rows_per_cell']},
          'source_context':{'population':p['source_context']['population'],
                            'selection':evidence['sources'][0]['population'],
                            'scope':p['source_context']['scope'],
                            'assumption_ids':['A_TRANSPORT','A_FAMILY','A_UNITS','A_UNCERTAINTY'],
                            'records':source_records,'alternative_hba1c_representation':alternative,
                            'source_uncertainty':'No reported estimator precision; SDs are individual dispersion.',
                            'overlap':'One biological cohort; glucose converted units and HbA1c converted units are duplicated quantities, not independent evidence.'},
          'target_model_projections_not_source_statistics':projection,
          'Q2_minus_Q3_model_implication':0.0,
          'Q1_residual_RMS_model_implication':math.sqrt(law['hba1c']['variance_from_law']),
          'secondary_glucose10_model_projection':{'intercept':(eg-100)/10,'age10':0.0,'female':0.0},
          'limitations':['No target table read or generated; no model fit or calibration draw.',
                         'Source-context algebra checks the selected marginal constraints only; source demographic/joint law unspecified.',
                         'All association projections arise from the product assumption and are not supplied evidence.',
                         'Floating-point generation approximates the continuous law; runtime behavior remains controller work.']}
assert result['demographic_design']['n_rows']==p['design']['n_rows']
(C/'analytic_results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'status':'pass','calculation':'closed_form','age_mean':float(age_mean),'age_variance':float(age_variance),'glucose_alpha':alpha,'glucose_beta':beta,'constraint_count':len(source_records)}))
