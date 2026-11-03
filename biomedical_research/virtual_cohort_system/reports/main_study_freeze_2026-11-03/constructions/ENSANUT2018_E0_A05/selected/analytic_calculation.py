"""Deterministic algebra only: no generator imports, row sampling or quadrature."""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import json
import math
from pathlib import Path
import numpy as np

C = Path(__file__).resolve().parent
p = json.loads((C/'model_spec.json').read_text(encoding='utf-8'))['parameters']
means = [(low+high)/2 for low,high in p['age_bands']]
within = [((high-low+1)**2-1)/12 for low,high in p['age_bands']]
am = sum(means)/len(means)
av = sum(v+(m-am)**2 for v,m in zip(within,means))/len(means)
asd = math.sqrt(av)
b,g,h = (p[k] for k in ['bmi_loadings','glucose_loadings','hba1c_loadings'])
rb,rg,rh = (math.sqrt(1-sum(x*x for x in d.values())) for d in [b,g,h])
L = np.array([
 [asd,0,0,0,0],
 [0,0.5,0,0,0],
 [p['bmi_sd']*b['age'],p['bmi_sd']*b['female'],p['bmi_sd']*rb,0,0],
 [p['glucose_sd']*g['age'],p['glucose_sd']*g['female'],p['glucose_sd']*g['bmi_factor'],p['glucose_sd']*rg,0],
 [p['hba1c_sd']*h['age'],p['hba1c_sd']*h['female'],p['hba1c_sd']*h['bmi_factor'],p['hba1c_sd']*h['glucose_factor'],p['hba1c_sd']*rh]
])
names = ['age','female','bmi','glucose','hba1c']
mu = np.array([am,0.5,p['bmi_mean'],p['glucose_mean'],p['hba1c_mean']])
cov = L@L.T
r = math.sqrt(2*p['residual_beta_shape']+1)
low = np.array([(min(x[0] for x in p['age_bands'])-am)/asd,-1,-r,-r,-r])
high = np.array([(max(x[1] for x in p['age_bands'])-am)/asd,1,r,r,r])
supports = {}
for i,name in enumerate(names):
    lo = float(mu[i]+np.sum(np.where(L[i]>=0,L[i]*low,L[i]*high)))
    hi = float(mu[i]+np.sum(np.where(L[i]>=0,L[i]*high,L[i]*low)))
    supports[name] = [lo,hi]
transform = np.diag([0.1,1,0.2,0.1,1])
tcov = transform@cov@transform
tmu = np.array([(am-50)/10,0.5,(p['bmi_mean']-25)/5,(p['glucose_mean']-100)/10,p['hba1c_mean']])
def projection(indices,outcome):
    xx = tcov[np.ix_(indices,indices)]
    xy = tcov[indices,outcome]
    beta = np.linalg.solve(xx,xy)
    residual = float(tcov[outcome,outcome]-xy@beta)
    return {'terms':[['age10','female','bmi5','glucose10','hba1c'][i] for i in indices], 'coefficients':beta.tolist(), 'intercept':float(tmu[outcome]-tmu[indices]@beta), 'residual_variance':residual,'residual_RMS':math.sqrt(residual),'smallest_predictor_covariance_eigenvalue':float(np.linalg.eigvalsh(xx).min())}
full = projection([0,1,2,3],4)
reduced = projection([0,1,2],4)
secondary = projection([0,1],3)
qb = h['bmi_factor']/rb
qg = h['glucose_factor']/rg
conditional_b = (h['bmi_factor']-qg*g['bmi_factor'])/rb
conditional_a = h['age']-qg*g['age']-conditional_b*b['age']
formula_values = {'Q1_age10':p['hba1c_sd']*conditional_a/asd*10,'Q2_bmi5':p['hba1c_sd']*qb/p['bmi_sd']*5,'Q3_bmi5':p['hba1c_sd']*conditional_b/p['bmi_sd']*5}
formula_values['Q2_minus_Q3_bmi5'] = formula_values['Q2_bmi5']-formula_values['Q3_bmi5']
checks = {
 'n_rows_exact':p['rows_per_cell']*len(p['female_values'])*len(p['age_bands'])==3000,
 'all_residual_variances_positive':all(1-sum(x*x for x in d.values())>0 for d in [b,g,h]),
 'bmi_positive_support':supports['bmi'][0]>0,
 'glucose_positive_support':supports['glucose'][0]>0,
 'glucose_strictly_below_126_support':supports['glucose'][1]<126,
 'hba1c_positive_support':supports['hba1c'][0]>0,
 'all_covariance_eigenvalues_positive':bool(np.linalg.eigvalsh(cov).min()>0),
 'full_projection_matches_substitution':bool(np.allclose([full['coefficients'][0],reduced['coefficients'][2],full['coefficients'][2]],[formula_values['Q1_age10'],formula_values['Q2_bmi5'],formula_values['Q3_bmi5']],atol=1e-12,rtol=1e-12)),
 'full_residual_variance_matches_law':bool(math.isclose(full['residual_variance'],(p['hba1c_sd']*rh)**2,abs_tol=1e-12)),
 'marginal_sds_match_transferred_scales':bool(np.allclose(np.sqrt(np.diag(cov))[2:],[p['bmi_sd'],p['glucose_sd'],p['hba1c_sd']],atol=1e-12)),
}
assert all(checks.values()), checks
tree=ast.parse((C/'generator.py').read_text(encoding='utf-8'))
fn=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='generate']
assert len(fn)==1 and len(fn[0].args.args)==3
out = {
 'method':'Closed-form discrete-uniform and Beta moments, interval arithmetic for affine support, matrix multiplication and linear-system solution. No numerical quadrature, Monte Carlo, generated rows or generator import/execution.',
 'population':'One uniformly selected row from the fixed equal-cell task design; these are assumptions-implied target-law quantities, not source-context validation or supplied target values.',
 'inputs':{'model_spec_sha256':hashlib.sha256((C/'model_spec.json').read_bytes()).hexdigest(),'generator_sha256':hashlib.sha256((C/'generator.py').read_bytes()).hexdigest()},
 'factor_order':['A','S','U_B','U_G','U_H'], 'variables':names, 'age_mean':am,'age_variance':av,'age_sd':asd,
 'beta_shape':p['residual_beta_shape'],'beta_mean':0.5,'beta_variance':1/(4*(2*p['residual_beta_shape']+1)),
 'standardized_factor_support':[low.tolist(),high.tolist()], 'residual_coefficients':{'bmi':rb,'glucose':rg,'hba1c':rh},
 'raw_affine_loading_matrix':L.tolist(),'raw_means':dict(zip(names,mu.tolist())),
 'raw_covariance_matrix':cov.tolist(),'raw_second_moment_matrix':(cov+np.outer(mu,mu)).tolist(),'closed_support_bounds':supports,
 'Q1_and_Q3_projection':full,'Q2_projection':reduced,'secondary_glucose10_age_sex_projection':secondary,
 'substitution_formula_values':formula_values,
 'unit_representation_calculations':{'glucose_mean':5.1*18,'glucose_sd':0.5*18,'alternative_hba1c_mean_from_IFCC_not_fitted':38*0.09148+2.152,'alternative_hba1c_sd_from_IFCC_not_fitted':3*0.09148},
 'source_comparisons':'Unavailable: the law-linked calculations concern the generated task law and do not reconstruct the Jansen source population.',
 'checks':checks,'generator_AST_ABI':'pass; source parsed only; generator not executed'
}
(C/'analytic_results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'checks':checks,'supports':supports,'projection_values':formula_values,'residual_RMS':full['residual_RMS']},indent=2))
