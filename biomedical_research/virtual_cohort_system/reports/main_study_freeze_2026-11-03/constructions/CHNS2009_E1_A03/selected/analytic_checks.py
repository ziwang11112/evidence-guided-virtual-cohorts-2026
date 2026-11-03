"""Closed-form population arithmetic only: no random numbers, rows, or generator import."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
from statistics import NormalDist
import sys
import numpy as np

sys.dont_write_bytecode = True
C = Path(__file__).parent
B = C.parent.parent
def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, obj):
    p.write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n',encoding='utf-8')
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

spec = read(C/'model_spec.json')
p = spec['parameters']
evidence = {x['id']:x for x in read(C/'evidence.json')['items']}
module_path=B/'input/source_operations.py'
loader=importlib.util.spec_from_file_location('approved_source_operations',module_path)
operations=importlib.util.module_from_spec(loader)
loader.loader.exec_module(operations)
rho = 2*math.sin(math.pi*p['dependence']['source_spearman_glucose_hba1c']/6)
q = p['dependence']['latent_bmi_glucose']
R = np.array([[1,q,q*rho],[q,1,rho],[q*rho,rho,1]],dtype=float)

def log_parameters(marginals,names):
    sig2=np.array([math.log1p((marginals[n]['sd']/marginals[n]['mean'])**2) for n in names])
    sig=np.sqrt(sig2)
    mu=np.array([math.log(marginals[n]['mean']) for n in names])-sig2/2
    return mu,sig

def moments(mu,sigma,corr,selection_index=None,upper=None):
    covlog=corr*np.outer(sigma,sigma)
    d=len(mu)
    a=None if selection_index is None else (math.log(upper)-mu[selection_index])/sigma[selection_index]
    Phi=lambda x: math.erfc(-x/math.sqrt(2))/2
    prob=1.0 if a is None else Phi(a)
    def raw(power):
        power=np.asarray(power,dtype=float)
        mgf=math.exp(float(power@mu+power@covlog@power/2))
        if a is not None:
            shift=float(covlog[selection_index]@power/sigma[selection_index])
            mgf*=Phi(a-shift)/prob
        return mgf
    first=np.array([raw(np.eye(d)[i]) for i in range(d)])
    second=np.array([[raw(np.eye(d)[i]+np.eye(d)[j]) for j in range(d)] for i in range(d)])
    cov=second-np.outer(first,first)
    return {'means':first.tolist(),'covariance':cov.tolist(),'raw_second_moments':second.tolist(),'log_location':mu.tolist(),'log_covariance':covlog.tolist(),'selection_probability':prob,'selection_standardized_upper':a,'covariance_min_eigenvalue':float(np.linalg.eigvalsh(cov).min())}

target_mu,target_sigma=log_parameters(p['target_marginals'],['bmi','glucose','hba1c'])
target=moments(target_mu,target_sigma,R)
assert np.linalg.eigvalsh(R).min()>0
assert target['covariance_min_eigenvalue']>0
assert np.allclose(target['means'],[p['target_marginals'][n]['mean'] for n in ['bmi','glucose','hba1c']],rtol=1e-12)
assert np.allclose(np.diag(target['covariance']),[p['target_marginals'][n]['sd']**2 for n in ['bmi','glucose','hba1c']],rtol=1e-12)

j=p['source_jansen']
jmu,jsig=log_parameters(j['parent_marginals'],['BMI','FPG','HbA1c_IFCC'])
jm=moments(jmu,jsig,R,selection_index=1,upper=j['selection_fpg_upper_exclusive'])
covj=np.zeros((5,5))
covj[0,0]=j['age_sd']**2
covj[1,1]=j['female_probability']*(1-j['female_probability'])
covj[2:,2:]=np.array(jm['covariance'])
jctx={
 'role':'declared_source_population_moments','source_context_id':'CTX_JANSEN_SELECTED',
 'variables':['age','gender_binary','BMI','FPG','HbA1c_IFCC'],
 'means':[j['age_mean'],j['female_probability']]+jm['means'],'covariance':covj.tolist(),
 'units':{'age':'year','gender_binary':'1','BMI':'kg/m^2','FPG':'mmol/L','HbA1c_IFCC':'mmol/mol'},
 'selection_status':'moments_after_declared_source_selection','weights':'equal_assumption','gender_mapping':'female=1,male=0',
 'assumption_ids':['A_LAW','A_FACTOR','A_JANSEN','A_SOURCE_CONTEXT','A_TRANSPORT_DEPENDENCE'],
 'moment_derivation':'mathematical_properties.md: exponential tilt formula for the same latent-factor mechanism conditioned on FPG<7; analytic_checks.py:moments. Age/gender independent of biomarker law and selection. Native IFCC response.',
 'source_population':'Reported selected unrelated western-European Lifelines adults, other exclusions represented as already applied; declared approximation, not source participants.',
 'law_moments':jm,
 'age_support_assumed':[j['age_mean']-math.sqrt(3)*j['age_sd'],j['age_mean']+math.sqrt(3)*j['age_sd']],
 'remaining_selection_assumptions':'Source known-diabetes/anemia/missing-data/family preference effects assumed absent conditional on this scenario; only the explicit FPG threshold has an additional mathematical selection step.',
}

bao=p['source_bao']; names=['FPG','HbA1c_percent']; zq=NormalDist().inv_cdf(bao['quartile_probability'])
bmu=np.array([math.log(bao[n]['median']) for n in names])
bsig=np.array([math.log(bao[n]['q3']/bao[n]['q1'])/(2*zq) for n in names])
bm=moments(bmu,bsig,np.array([[1,rho],[rho,1]]))
bctx={
 'role':'declared_source_population_moments','source_context_id':'CTX_BAO_ANALYZED','variables':names,
 'means':bm['means'],'covariance':bm['covariance'],'units':{'FPG':'mmol/L','HbA1c_percent':'%'},
 'selection_status':'moments_after_declared_source_selection','weights':'equal_assumption',
 'assumption_ids':['A_LAW','A_BAO','A_SOURCE_CONTEXT','A_TRANSPORT_DEPENDENCE'],
 'moment_derivation':'mathematical_properties.md: untruncated lognormal raw moments exp(k.mu+k.Sigma.k/2) under the same shared glucose-HbA1c latent correlation. analytic_checks.py:moments.',
 'source_population':'Bao analyzed Shanghai adults; known diabetes and stated clinical/questionnaire exclusions already applied, screen-detected diabetes retained. The selected pair distribution is directly specified.',
 'law_moments':bm,
 'marginal_quantile_discrepancies':{n:{'reported_q1':bao[n]['q1'],'model_q1':math.exp(bmu[i]-zq*bsig[i]),'reported_median':bao[n]['median'],'model_median':math.exp(bmu[i]),'reported_q3':bao[n]['q3'],'model_q3':math.exp(bmu[i]+zq*bsig[i])} for i,n in enumerate(names)}
}

results=[]
for eid,ctx in [('R_JANSEN_BMI',jctx),('R_JANSEN_FPG',jctx),('R_BAO_PEARSON',bctx)]:
    out=operations.evaluate(eid,ctx)
    out['reported_source_point']=evidence[eid]['estimate']
    out['raw_calculated_minus_reported']=out['calculated_value']-out['reported_source_point']
    out['interpretation']='Qualified analytic diagnostic, not equivalence test, calibration loss, source replay, or target validation.'
    results.append(out)
mind_mu,mind_sig=log_parameters(p['source_mind'],['FSG','HbA1c_percent'])
mind=moments(mind_mu,mind_sig,np.array([[1,rho],[rho,1]]))
rank=6/math.pi*math.asin(rho/2)
results.append({'evidence_id':'R_MIND_SPEARMAN','source_context_id':'CTX_MIND_ANALYZED','calculated_value':rank,'reported_source_point':evidence['R_MIND_SPEARMAN']['estimate'],'raw_calculated_minus_reported':rank-evidence['R_MIND_SPEARMAN']['estimate'],'unit':'1','classification':'qualified_law_specific_source_rank_functional','strict_replay':'not_computable','exact_source_reconstruction':False,'transport_validated':False,'assumption_ids':['A_LAW','A_RANK','A_MIND','A_SOURCE_CONTEXT'],'moment_derivation':'mathematical_properties.md: continuous rank = normal CDF; independent-normal quadrant calculation gives (6/pi)*asin(rho/2).','interpretation':'Constraint satisfaction is algebraic by construction, not independent evidence validation; empirical mean-imputation/ties remain unresolved.'})

report={
 'scope':'deterministic_analytic_source_scenarios_and_probability_law_checks_no_rows',
 'method':'Closed-form lognormal exponential moments, normal CDF via math.erfc, inverse normal CDF via statistics.NormalDist, linear-system projections in supplied source_operations.evaluate, Gaussian quadrant identity for Spearman; no numerical quadrature, random draws, optimization or generator execution.',
 'input_hashes':{'model_spec.json':digest(C/'model_spec.json'),'evidence.json':digest(C/'evidence.json'),'generator.py_static_bytes_only':digest(C/'generator.py'),'input/source_operations.py':digest(module_path),'analytic_checks.py':digest(Path(__file__))},
 'latent_correlation':rho,'latent_matrix':R.tolist(),'latent_matrix_min_eigenvalue':float(np.linalg.eigvalsh(R).min()),
 'target_law_moments_not_source_comparisons':target,
 'target_population_age_ols_coefficient_implied_by_independence':0.0,
 'target_age_coefficient_status':'Assumed zero, not estimated, fitted, recovered or source-identified.',
 'source_contexts':{'CTX_JANSEN_SELECTED':jctx,'CTX_BAO_ANALYZED':bctx,'CTX_MIND_ANALYZED':{'role':'declared_source_population_law','selection_status':'law_after_declared_source_selection','population':'MIND age61-80 eligible rural follow-up including known diabetes; continuous approximation to processed FSG/HbA1c pair','weights':'equal_assumption','variables':['FSG','HbA1c_percent'],'units':{'FSG':'mmol/L','HbA1c_percent':'%'},'law_moments':mind,'assumption_ids':['A_LAW','A_RANK','A_MIND','A_SOURCE_CONTEXT']}},
 'source_operations':results,
 'checks':{'latent_positive_definite':True,'target_biomarker_covariance_positive_definite':True,'analytic_target_marginal_parameter_identity':True,'all_numeric_moments_finite':True,'no_generator_import_or_execution':True},
 'uncertainty':'Source estimate uncertainty, structural uncertainty and transport are not quantified. Innovations account for individual variability only. Raw discrepancies are not tests or intervals.'
}
write(C/'analytic_results.json',report)
print(json.dumps({'analytic_operations':results,'latent_correlation':rho},indent=2))
