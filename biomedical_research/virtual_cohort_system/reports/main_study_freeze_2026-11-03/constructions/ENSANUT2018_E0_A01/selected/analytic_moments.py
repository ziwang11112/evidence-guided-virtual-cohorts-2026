"""Deterministic algebra only: no generator imports, rows, sampling or quadrature."""
import json
import math
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = json.loads((HERE / 'model_spec.json').read_text(encoding='utf-8'))
p = spec['parameters']
b, g, h, ref = [p[k] for k in ('bmi','glucose','hba1c','source_reference')]
width = b['upper']-b['lower']
q = (b['mean']-b['lower'])/width
v = (b['sd']/width)**2
concentration = q*(1-q)/v-1
alpha, beta = q*concentration, (1-q)*concentration
rg2 = g['source_sd']**2-(g['age_per_year']*ref['age_sd'])**2-g['bmi_standardized_loading']**2
rh2 = (h['source_sd']**2-(h['age_per_year']*ref['age_sd'])**2
       -h['bmi_standardized_loading']**2-h['shared_glucose_factor_loading']**2)
assert alpha > 0 and beta > 0 and rg2 > 0 and rh2 > 0
rg, rh = math.sqrt(rg2), math.sqrt(rh2)
r = math.sqrt(6*p['residual_law']['variance'])
zlo, zhi = (b['lower']-b['mean'])/b['sd'], (b['upper']-b['mean'])/b['sd']
amin, amax = min(x[0] for x in p['design']['age_bands']), max(x[1] for x in p['design']['age_bands'])
glo = g['reference_mean']+g['age_per_year']*(amin-ref['age_mean'])+g['bmi_standardized_loading']*zlo-rg*r
ghi = g['reference_mean']+g['age_per_year']*(amax-ref['age_mean'])+g['bmi_standardized_loading']*zhi+rg*r
hlo = h['reference_mean']+h['age_per_year']*(amin-ref['age_mean'])+h['bmi_standardized_loading']*zlo-h['shared_glucose_factor_loading']*r-rh*r
hhi = h['reference_mean']+h['age_per_year']*(amax-ref['age_mean'])+h['bmi_standardized_loading']*zhi+h['shared_glucose_factor_loading']*r+rh*r
assert b['lower'] > 0 and glo > 0 and ghi < 126 and hlo > 0
means = [(lo+hi)/2 for lo,hi in p['design']['age_bands']]
variances = [((hi-lo+1)**2-1)/12 for lo,hi in p['design']['age_bands']]
amean = sum(means)/len(means)
avar = sum(vv+(mm-amean)**2 for mm,vv in zip(means,variances))/len(means)
bm = b['lower']+width*alpha/(alpha+beta)
bv = width**2*alpha*beta/((alpha+beta)**2*(alpha+beta+1))
source_gv = (g['age_per_year']*ref['age_sd'])**2+g['bmi_standardized_loading']**2+rg2
source_hv = (h['age_per_year']*ref['age_sd'])**2+h['bmi_standardized_loading']**2+h['shared_glucose_factor_loading']**2+rh2
assert math.isclose(bm,b['mean'],abs_tol=1e-12) and math.isclose(bv,b['sd']**2,abs_tol=1e-12)
assert math.isclose(source_gv,g['source_sd']**2,abs_tol=1e-12) and math.isclose(source_hv,h['source_sd']**2,abs_tol=1e-12)
out = {
    'calculation':'Exact finite sums and closed-form beta/triangular/additive moments; floating-point evaluation only; no random sampling or numerical quadrature.',
    'inputs':{'model_spec_sha256':hashlib.sha256((HERE/'model_spec.json').read_bytes()).hexdigest()},
    'beta_shapes':{'alpha':alpha,'beta':beta},
    'residual_scales':{'glucose':rg,'hba1c':rh},
    'target_law_support_bounds':{'age':[amin,amax],'female':[0,1],'bmi':[b['lower'],b['upper']],'glucose':[glo,ghi],'hba1c':[hlo,hhi]},
    'hypothetical_source_moments':{'bmi_mean':bm,'bmi_sd':math.sqrt(bv),'glucose_mean':g['reference_mean'],'glucose_sd':math.sqrt(source_gv),'hba1c_mean':h['reference_mean'],'hba1c_sd':math.sqrt(source_hv)},
    'target_design_analytic_age':{'mean':amean,'variance':avar,'n_per_cell':p['design']['n_per_cell'],'n_cells':len(p['design']['female_values'])*len(p['design']['age_bands'])},
    'checks':{'positive_beta_shapes':True,'positive_residual_variances':True,'positive_support':True,'glucose_upper_below_126':True,'finite_all_moments':'bounded law','source_marginal_identity':True},
    'limits':'Model implications only. Hypothetical source context, no source replay or target empirical validation. Target age moments follow task allocation and chosen within-band law.'
}
(HERE/'analytic_moments.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2,allow_nan=False))
