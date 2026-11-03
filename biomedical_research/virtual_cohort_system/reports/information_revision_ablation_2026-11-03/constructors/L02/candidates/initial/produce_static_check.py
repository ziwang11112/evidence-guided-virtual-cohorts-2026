"""Deterministic static/analytic checks only: never imports or runs generator.py."""
from pathlib import Path
import ast, json, math, hashlib
c=Path(__file__).resolve().parent
p=json.loads((c/'model_spec.json').read_text(encoding='utf-8'))['parameters']
tree=ast.parse((c/'generator.py').read_text(encoding='utf-8'))
functions=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='generate']
assert len(functions)==1 and len(functions[0].args.args)==3
assert p['n_rows']==3000
assert all(-1<r<1 for r in p['conditional_log_error_correlation'])
a=p['age_distribution']; b=p['bmi_distribution']
# Finite support enumeration is mathematics, not sampled/generated rows.
min_b=min(b['reference_mean']+b['age_linear']*(age-b['age_center'])+b['age_quadratic']*(age-b['age_center'])**2+b['female_mean_shift']*(sex-b['female_center']) for age in range(a['minimum'],a['maximum']+1) for sex in (0,1))
assert min_b>0
mins={}
for key in ('glucose_distribution','hba1c_distribution'):
    d=p[key]
    # Affine mean is increasing in BMI. Its infimum occurs at BMI -> 0.
    assert d['bmi_mean_slope']>=0
    mins[key]=min(d['reference_means']) + min(d['age_mean_slope']*(a['minimum']-d['age_center']),d['age_mean_slope']*(a['maximum']-d['age_center'])) - d['bmi_mean_slope']*d['bmi_center']+min(d['female_mean_shift']*(-d['female_center']),d['female_mean_shift']*(1-d['female_center']))
    assert mins[key]>0
# Closed-form mixture moments at the declared centering covariates only.
w=p['glycemic_state']['reference_probability']; g=p['glucose_distribution']; h=p['hba1c_distribution']
mg=sum(q*x for q,x in zip((1-w,w),g['reference_means']))
mh=sum(q*x for q,x in zip((1-w,w),h['reference_means']))
vg=sum(q*(mu*mu*(1+cv*cv)) for q,mu,cv in zip((1-w,w),g['reference_means'],g['conditional_cv']))-mg*mg
vh=sum(q*(mu*mu*(1+cv*cv)) for q,mu,cv in zip((1-w,w),h['reference_means'],h['conditional_cv']))-mh*mh
cov=sum(q*gm*hm*math.exp(r*math.sqrt(math.log1p(gc*gc))*math.sqrt(math.log1p(hc*hc))) for q,gm,hm,gc,hc,r in zip((1-w,w),g['reference_means'],h['reference_means'],g['conditional_cv'],h['conditional_cv'],p['conditional_log_error_correlation']))-mg*mh
result={'scope':'static AST inspection and deterministic arithmetic only; no synthetic rows; no generator import or execution','inputs':{name:hashlib.sha256((c/name).read_bytes()).hexdigest() for name in ('generator.py','model_spec.json','evidence.json')},'abi_ast':'pass','bmi_conditional_mean_minimum':min_b,'biomarker_conditional_mean_infima':mins,'finite_polynomial_moments':'positive affine mean of finite-moment BMI times lognormal error; bounded age/sex and mixture probability','reference_covariate_mixture_moments_only_not_full_cohort':{'glucose_mean':mg,'glucose_sd':math.sqrt(vg),'hba1c_mean':mh,'hba1c_sd':math.sqrt(vh),'pearson':cov/math.sqrt(vg*vh)},'limitations':'No runtime behavior, output rows, source reconstruction, full marginal cohort statistics or target agreement was tested.'}
(c/'static_analytic_check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
checks=json.loads((c/'checks.json').read_text(encoding='utf-8'))
checks['records'].insert(0,{'name':'static_analytic_support','status':'pass','detail':'AST ABI and positive conditional-mean bounds checked by retained producer script. Closed-form reference-covariate mixture moments calculated; no rows or generator execution. See bound result for limits.'})
checks['artifacts'].append({'path':'static_analytic_check.json','sha256':hashlib.sha256((c/'static_analytic_check.json').read_bytes()).hexdigest()})
(c/'checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
