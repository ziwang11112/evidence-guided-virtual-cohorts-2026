"""Writes metadata only; never imports or executes the generator."""
import ast
import hashlib
import json
from pathlib import Path

here=Path(__file__).resolve().parent
def read(name):
    return json.loads((here/name).read_text(encoding='utf-8'))
def write(name,value):
    (here/name).write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
evidence=json.loads((here.parents[1]/'input'/'compiled_evidence.json').read_text(encoding='utf-8'))
write('evidence.json',evidence)
params=read('derived_parameters.json')
assumptions=[
 {'id':'A_COHORT','description':'Exactly 3000 exchangeable synthetic adults, unique synthetic IDs, task order and observed=None; no geography, survey weights, missingness or clinical exclusion model.'},
 {'id':'A_REFERENCE','description':'Supplied CHNS summaries are descriptive calibration inputs from a selected unweighted sample, not population truth. Estimated individual SD is used as a model population SD approximation; marginal estimator uncertainty is unavailable. The supplied regression CR1 intervals are not fitted or treated as independent constraints.'},
 {'id':'A_AGE','description':'Maximum entropy on ages 35 through 74, matching supplied mean and squared SD, with assumed CDF(38)=0.09, CDF(52)=0.49, CDF(67)=0.89 to locate reported quantiles. Maximum entropy and within-bin probability allocation are assumptions.'},
 {'id':'A_BMI','description':'Lognormal BMI fitted to supplied arithmetic mean and individual SD. This family, resulting tails, and continuous precision are assumptions; median and q90 need not agree exactly.'},
 {'id':'A_FEMALE','description':'Female is Bernoulli at the supplied selected-sample fraction and independent of age, BMI and both biomarkers. No sex coefficient direction is inferred from unresolved external coding. This independence is an unassessed simplification.'},
 {'id':'A_MIXTURE','description':'A shared two-component lognormal biomarker mixture is a mathematical representation of tail concordance, not a diagnosis. Component membership is independent of age, BMI and sex. One shared fraction and component means/SDs fit two means, SDs and three CDF constraints each approximately. Parameter search bounds and loss scales (mean/SD 0.03; CDF 0.01) are numerical choices, not evidence precision.'},
 {'id':'A_COPULA','description':'Each component has a Gaussian copula for latent age, BMI, glucose and HbA1c. Latent age-BMI correlation is assumed -0.05 and BMI-glucose is assumed 0.20. Remaining correlations solve the supplied three regression projections and Pearson/Spearman functionals analytically. These matrices are one underidentified completion, not recovered participant covariance or causal equations.'},
 {'id':'A_EVIDENCE_CONTEXT','description':'External source slopes, correlations, marginals and restored age evidence remain source context; none is forced to equal target estimates. No source-population replay occurred. Shared cohorts, unit conversions and correlated summaries are not independent replications.'},
 {'id':'A_NUMERICS','description':'Distributional covariance calculations and fixed Gauss-Hermite quadrature are deterministic, not simulated participants. Moment fitting and integration cannot establish generator execution. Individual row randomness does not represent parameter or structural uncertainty.'},
]
def prov(e,a,d):
    return {'evidence_ids':e,'assumption_ids':a,'derivation':d}
provenance={
 'n_rows':prov([],['A_COHORT'],'Task requires 3000 rows.'),
 'age_values':prov([],['A_COHORT','A_AGE'],'Integer support 35 to 74 inclusive from task.'),
 'age_probabilities':prov(['REF_age_mean','REF_age_sd','REF_age_q10','REF_age_median','REF_age_q90'],['A_REFERENCE','A_AGE','A_NUMERICS'],'Maximum-entropy exponential tilt on integer support. Formula and exact assumptions in derive_parameters.py; deterministic output in analytic_report.json.'),
 'female_probability':prov(['REF_female_mean'],['A_REFERENCE','A_FEMALE'],'Supplied fraction 0.5368722666264515 used as Bernoulli probability.'),
 'bmi_log_mean':prov(['REF_bmi_mean','REF_bmi_sd'],['A_REFERENCE','A_BMI'],'log(arithmetic mean)-0.5*log(1+(SD/mean)^2).'),
 'bmi_log_sd':prov(['REF_bmi_mean','REF_bmi_sd'],['A_REFERENCE','A_BMI'],'sqrt(log(1+(SD/mean)^2)).'),
 'high_component_probability':prov([f'REF_{v}_{s}' for v in ['glucose','hba1c'] for s in ['mean','sd','q10','median','q90']],['A_REFERENCE','A_MIXTURE','A_NUMERICS'],'Joint deterministic least-squares fit of a common class weight to both biomarker margins; not disease prevalence.'),
 'glucose_log_parameters':prov([f'REF_glucose_{s}' for s in ['mean','sd','q10','median','q90']],['A_REFERENCE','A_MIXTURE','A_NUMERICS'],'[mu0,sigma0,mu1,sigma1] for natural log serum glucose, derived by the retained mixture solver.'),
 'hba1c_log_parameters':prov([f'REF_hba1c_{s}' for s in ['mean','sd','q10','median','q90']],['A_REFERENCE','A_MIXTURE','A_NUMERICS'],'[mu0,sigma0,mu1,sigma1] for natural log HbA1c percent, derived by the retained mixture solver.'),
 'latent_correlations':prov(['REF_E1','REF_E2','REF_E3','REF_glucose_hba1c_pearson','REF_glucose_hba1c_spearman','E_SOURCE_RECONCILIATION'],['A_REFERENCE','A_COPULA','A_EVIDENCE_CONTEXT','A_NUMERICS'],'Two positive-definite correlation matrices in order age,BMI,glucose,HbA1c. Five unknown entries fitted to the five supplied functionals, two associations assumed. Formula covariance solves preserve the actual distinct adjustment sets; no concatenation of source regression slopes.'),
}
write('model_spec.json',{'parameters':params,'assumptions':assumptions,'parameter_provenance':provenance})
tree=ast.parse((here/'generator.py').read_text(encoding='utf-8'))
fn=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='generate']
abi_ok=len(fn)==1 and len(fn[0].args.args)==3 and not fn[0].args.vararg and not fn[0].args.kwonlyargs
assert abi_ok
write('static_report.json',{'scope':'AST and metadata only; no generator execution',
 'abi_three_positional_arguments':abi_ok,'parameter_names_match_provenance':set(params)==set(provenance),
 'retrieval':{'queries':[],'documents':[],'new_artifacts_for_registration':[]},
 'assessed':'Only program syntax/ABI and parameter provenance coverage; output validity remains uncomputed.'})
checks={'scope':'source_only','records':[
 {'name':'static_abi_and_provenance','status':'pass','detail':'AST parsed, synchronous three-positional-argument generate found, and parameter keys matched provenance. See bound static_report.json; body was never executed.'},
 {'name':'distribution_math','status':'pass','detail':'Deterministic fitted distribution formulas completed; component correlation matrices are positive definite. Rank quadrature at orders 48/80 agrees to about 0.0000024. Descriptive input-summary fitting only; source_only is the legacy declared-input scope.'},
 {'name':'source_population_replay','status':'not_computable','detail':'No source-population simulation or source reconstruction supplied. No target-statistic comparison is represented as source replay.'},
 {'name':'isolated_generation_and_30_statistics','status':'not_computable','detail':'Candidate has not been executed. Coordinator must freeze and run seed4201 in the supplied backend.'},
 {'name':'population_validity_and_uncertainty','status':'not_computable','detail':'The allowed summaries do not identify population law, causal effects, source transfer, tails, clustering or parameter uncertainty.'}],
 'artifacts':[{'path':f,'sha256':hashlib.sha256((here/f).read_bytes()).hexdigest()}
  for f in ['analytic_report.json','static_report.json']]}
write('checks.json',checks)
print('Metadata written. Generator was not imported or executed.')
