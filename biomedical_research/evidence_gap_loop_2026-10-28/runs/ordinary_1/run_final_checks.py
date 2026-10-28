"""Final source-only and invented-input checks; no participant/outcome reads."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import gamma, lognorm

RUN=Path(__file__).resolve().parent
OUT=RUN/'final'
spec=json.loads((OUT/'model_spec.json').read_text(encoding='utf-8'))
ledger=json.loads((OUT/'evidence.json').read_text(encoding='utf-8'))
initial_spec=json.loads((RUN/'initial/model_spec.json').read_text(encoding='utf-8'))
review=json.loads((RUN/'initial_review.json').read_text(encoding='utf-8'))

def load_generator(path,name):
    ms=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(ms)
    ms.loader.exec_module(mod)
    return mod.generate

state_before_import=np.random.get_state()
generate=load_generator(OUT/'generator.py','ordinary1_final')
initial_generate=load_generator(RUN/'initial/generator.py','ordinary1_initial_reference')
state_after_import=np.random.get_state()
checks={'scope':'Source arithmetic and invented predictors only. No observed participant rows, own outputs or target HDL were read in this revision test harness.','tests':[]}

def record(name,passed,detail):
    checks['tests'].append({'name':name,'passed':bool(passed),'detail':detail})
    if not passed:
        raise AssertionError(name)

def rng_equal(a,b):
    return a[0]==b[0] and np.array_equal(a[1],b[1]) and a[2:]==b[2:]

record('import_does_not_mutate_global_rng',rng_equal(state_before_import,state_after_import),{})
for filename,hash_key in [('generator.py','generator_sha256'),('model_spec.json','model_spec_sha256'),('evidence.json','evidence_sha256')]:
    assert hashlib.sha256((RUN/'initial'/filename).read_bytes()).hexdigest()==review[hash_key]
record('initial_reviewed_files_preserved',True,{'verified_files':['initial/generator.py','initial/model_spec.json','initial/evidence.json'],'scope':'Hashes supplied by independent review; no outputs read.'})
eids={x['id'] for x in ledger['evidence']}
sids={x['id'] for x in ledger['sources']}
aids={x['id'] for x in spec['assumptions']}
assert set(spec['parameters'])==set(spec['parameter_provenance'])
for provenance in spec['parameter_provenance'].values():
    assert provenance['evidence_ids'] or provenance['assumption_ids']
    assert set(provenance['evidence_ids'])<=eids
    assert set(provenance['assumption_ids'])<=aids
assert all(e['source_id'] in sids for e in ledger['evidence'])
record('parameter_evidence_provenance',True,{'parameters':len(spec['parameters']),'sources':len(sids),'evidence':len(eids)})
artifact_count=0
for source in ledger['sources']:
    for a in source['approved_artifacts']:
        assert hashlib.sha256((RUN/a['path']).read_bytes()).hexdigest()==a['sha256']
        artifact_count+=1
record('source_artifact_hashes_match_gateway_returns',True,{'files_verified':artifact_count,'scope':'Byte verification of exact accepted gateway-returned paths/hashes, not a new approval.'})

source=(RUN/'literature/approved/b2ee68e3163d9d8ad18df363ac332724afec410a690bdd9d7d386b5856e5bfd2.txt').read_text(encoding='utf-8')
start=source.index('Table rev2. Multivariate regression models')
tail_table=source[start:source.index('Attachment',start)]
expected='HDL (mg/dL) -0.88 <0.001 -1.13 to -0.64 -0.33 <0.001 -0.47 to -0.20 -0.16 <0.001 -0.22 to -0.10 -21.21 <0.001 -30.34 to -12.07'
assert expected in tail_table
assert '# Adjusted for Age and Gender.' in tail_table
record('L02_embedded_subgroup_table_extraction',spec['parameters']['tail_additive_slope']==-0.33,{'locator':'PMC7644056 published Author response to Decision Letter0, Table rev2 BMI>30, HDL row and BMI column','slope':-0.33,'CI95':[-0.47,-0.20],'adjustment':'Age and gender','scope':'Cross-sectional subgroup estimate, not main Table2 or a longitudinal slope.'})
p=spec['parameters']
counts=np.array(p['source_age_counts_by_bmi'])
record('source_table_margins',np.array_equal(counts.sum(axis=1),np.array(p['source_cell_counts']['male'])+np.array(p['source_cell_counts']['female'])),{'BMI_totals':counts.sum(axis=1).tolist()})
source_sd={s:(np.array(p['source_mean_standard_errors'][s])*np.sqrt(p['source_cell_counts'][s])).tolist() for s in ('male','female')}
record('SEM_to_individual_SD',all(np.isfinite(v).all() and (np.array(v)>0).all() for v in source_sd.values()),{'individual_SDs':source_sd,'limitation':'Marginal broad-cell SD, not identified exact-predictor residual SD.'})

def moments(bmi,age,sex,model=spec):
    par=model['parameters']
    sex_label='male' if sex==1 else 'female'
    counts=np.array(par['source_age_counts_by_bmi'])
    agevals=np.array(par['age_contrasts'])
    centers=(counts@agevals)/counts.sum(axis=1)
    source_means=np.array(par['source_hdl_means'][sex_label])
    sd=np.array(par['source_mean_standard_errors'][sex_label])*np.sqrt(par['source_cell_counts'][sex_label])
    m0=np.interp(bmi,par['bmi_knots'],source_means-centers)+np.interp(age,par['age_knots'],agevals)
    excess=max(bmi-par['bmi_knots'][-1],0)
    mean=m0*np.exp(par['tail_additive_slope']*excess/m0)
    variance_log=np.interp(bmi,par['bmi_knots'],np.log1p((sd/source_means)**2))
    return float(mean),float(mean*np.sqrt(np.expm1(variance_log))),float(variance_log)

toy=pd.DataFrame({'row_id':['u5','b2','a8','c7','v3','n4'],'bmi':[14.1,21.25,25.5,30.5,77.5,100.0],'age':[20.0,35,45,55.5,79,100],'sex':[1,2,1,2,1,2]},index=[7,2,9,4,8,0])
before=toy.copy(deep=True)
spec_before=copy.deepcopy(spec)
state_before=np.random.get_state()
one=generate(toy,spec,1729)
state_after=np.random.get_state()
same=generate(toy,spec,1729)
other=generate(toy,spec,1730)
pd.testing.assert_frame_equal(toy,before,check_exact=True)
pd.testing.assert_frame_equal(one.iloc[:,:4],toy,check_exact=True)
record('interface_preservation_and_no_mutation',spec==spec_before and list(one.columns)==['row_id','bmi','age','sex','hdl'],{'observed_rows':len(toy),'nonsequential_index_preserved':one.index.equals(toy.index)})
record('seed_reproducibility_and_variation',np.array_equal(one.hdl,same.hdl) and not np.array_equal(one.hdl,other.hdl),{})
record('generation_global_rng_unchanged',rng_equal(state_before,state_after),{})
record('finite_positive_stress_inputs',np.isfinite(one.hdl).all() and (one.hdl>0).all(),{'BMI_range':[14.1,100],'age_range':[20,100],'scope':'Invented stress support, not clinical limits.'})
record('empty_input',generate(toy.iloc[:0],spec,1).shape==(0,5),{})
invalid_pass=[]
for column,value in [('sex',3),('bmi',0),('bmi',float('nan')),('age',float('inf'))]:
    invalid=toy.copy()
    invalid.loc[7,column]=value
    try:
        generate(invalid,spec,1)
        invalid_pass.append(False)
    except ValueError:
        invalid_pass.append(True)
record('invalid_inputs_rejected',all(invalid_pass),{'cases':['invalid sex','zero BMI','NaN BMI','infinite age']})

grid=pd.DataFrame([{'row_id':f'{s}-{a}-{b}','bmi':b,'age':a,'sex':s} for s in (1,2) for a in (20,35,50,65.5,79) for b in (13,17,21.25,25.5,30.5,40,60,80,100)])
draw=generate(grid,spec,482)
z=np.random.default_rng(482).standard_normal(len(grid))
expected=[]
for k,row in enumerate(grid.itertuples()):
    mean,sd,lv=moments(row.bmi,row.age,row.sex)
    expected.append(np.exp(np.log(mean)-lv/2+np.sqrt(lv)*z[k]))
relative=np.abs(draw.hdl.to_numpy()/np.array(expected)-1)
record('independent_scalar_equations',np.max(relative)<1e-12,{'rows':len(grid),'max_relative_error':float(max(relative))})

derivatives=[]
for s in (1,2):
    for a in (20,50,79):
        m0=moments(30.5,a,s)[0]
        epsilon=1e-5
        derivative=(moments(30.5+epsilon,a,s)[0]-m0)/epsilon
        derivatives.append(float(derivative))
record('cross_sectional_local_tail_derivative',max(abs(d-p['tail_additive_slope']) for d in derivatives)<1e-6,{'derivatives_mg_dl_per_BMI':derivatives,'selected_source_slope':p['tail_additive_slope'],'scope':'Local identity only; does not identify source nonlinear shape.'})

moment_checks=[]
n_mc=120000
cells=[(21.25,35,1),(21.25,35,2),(40,50,1),(40,50,2),(80,79,1),(80,79,2)]
for k,(b,a,s) in enumerate(cells):
    invented=pd.DataFrame({'row_id':np.arange(n_mc).astype(str),'bmi':b,'age':a,'sex':s})
    values=generate(invented,spec,7100+k).hdl.to_numpy()
    mean,sd,lv=moments(b,a,s)
    discrepancy=(values.mean()-mean)/(sd/np.sqrt(n_mc))
    sd_error=values.std(ddof=1)/sd-1
    moment_checks.append({'bmi':b,'age':a,'sex':s,'n':n_mc,'analytic_mean':mean,'empirical_mean':float(values.mean()),'analytic_sd':sd,'empirical_sd':float(values.std(ddof=1)),'mean_MC_SE':float(discrepancy),'relative_sd_error':float(sd_error),'passed':bool(abs(discrepancy)<6 and abs(sd_error)<.025)})
record('invented_distribution_moments',all(c['passed'] for c in moment_checks),{'cells':moment_checks,'tolerance':'Mean within6 MC standard errors, SD within2.5%; no coefficient selection.'})

# Paired sensitivities use invented rows only; choices were fixed before execution.
small=pd.DataFrame([{'row_id':f'{s}-{a}-{b}','bmi':b,'age':a,'sex':s} for s in (1,2) for a in (20,50,79) for b in (17,21.25,25.5,30.5,40,60,80)])
base=generate(small,spec,951)
alternatives={}
for name,knots in [('lower_representatives',[16.5,20,25,29]),('higher_representatives',[17.5,22.5,26,33])]:
    alt=copy.deepcopy(spec)
    alt['parameters']['bmi_knots']=knots
    alternatives[name]=alt
no_age=copy.deepcopy(spec)
no_age['parameters']['age_contrasts']=[0,0,0,0]
alternatives['zero_age_contrasts']=no_age
sensitivity=[]
for name,alt in alternatives.items():
    values=generate(small,alt,951)
    m_base=np.array([moments(r.bmi,r.age,r.sex)[0] for r in small.itertuples()])
    m_alt=np.array([moments(r.bmi,r.age,r.sex,alt)[0] for r in small.itertuples()])
    sensitivity.append({'name':name,'max_abs_mean_difference_mg_dl':float(np.max(np.abs(m_alt-m_base))),'min_mean_ratio':float(np.min(m_alt/m_base)),'max_mean_ratio':float(np.max(m_alt/m_base)),'finite_positive_draws':bool(np.isfinite(values.hdl).all() and (values.hdl>0).all())})
record('representative_and_age_sensitivity',all(x['finite_positive_draws'] for x in sensitivity),{'alternatives':sensitivity,'scope':'Illustrative assumed knot alternatives and age omission, not evidence-based intervals or target-selected winners.'})

tail_results=[]
for s in (1,2):
    m0=moments(30.5,50,s)[0]
    for b in (40,60,80):
        chosen=moments(b,50,s)[0]
        initial_slope=initial_spec['parameters']['tail_log_slopes']['male' if s==1 else 'female']
        initial_mean=m0*np.exp(initial_slope*(b-30.5))
        limits=[]
        for slope in (-.47,-.20):
            alt=copy.deepcopy(spec)
            alt['parameters']['tail_additive_slope']=slope
            limits.append(moments(b,50,s,alt)[0])
        tail_results.append({'sex':s,'age':50,'bmi':b,'selected_mean':chosen,'flat_mean':m0,'initial_longitudinal_mean':float(initial_mean),'source_linear_mean':m0+p['tail_additive_slope']*(b-30.5),'source_CI_slope_scenario_means':limits})
flat=copy.deepcopy(spec)
flat['parameters']['tail_additive_slope']=0
flat_draw=generate(small,flat,951)
expected_ratio=[]
for row in small.itertuples():
    expected_ratio.append(moments(row.bmi,row.age,row.sex)[0]/moments(row.bmi,row.age,row.sex,flat)[0])
record('tail_sensitivities_and_paired_ratio',np.allclose(base.hdl/flat_draw.hdl,expected_ratio,rtol=1e-12),{'mean_scenarios':tail_results,'scope':'Source sampling-CI and structure scenarios do not bound target uncertainty; source linear comparison limited to invented BMI<=80 where positive.'})
initial_values=initial_generate(small,initial_spec,951)
record('substantive_initial_final_difference',not np.array_equal(base.hdl,initial_values.hdl),{'max_abs_paired_relative_change':float(np.max(np.abs(base.hdl/initial_values.hdl-1))),'scope':'Model consequence on invented grid, not improvement in accuracy.'})

variance_sensitivity=[]
for factor in (.75,1.25):
    alt=copy.deepcopy(spec)
    for s in ('male','female'):
        alt['parameters']['source_mean_standard_errors'][s]=[x*factor for x in p['source_mean_standard_errors'][s]]
    m,sd,lv=moments(40,50,2,alt)
    baseline_mean,baseline_sd,_=moments(40,50,2)
    values=generate(small,alt,951)
    variance_sensitivity.append({'SD_multiplier':factor,'analytic_mean':m,'analytic_SD':sd,'variance_ratio':(sd/baseline_sd)**2,'finite_positive':bool(np.isfinite(values.hdl).all() and (values.hdl>0).all()),'mean_unchanged':bool(m==baseline_mean)})
record('conditional_spread_sensitivity',all(x['finite_positive'] and x['mean_unchanged'] for x in variance_sensitivity),{'invented_reference':{'sex':2,'age':50,'bmi':40},'scenarios':variance_sensitivity,'scope':'Multipliers are illustrative assumptions; not estimated uncertainty or changes to final model.'})
m,sd,lv=moments(40,50,2)
probs=np.array([.01,.05,.5,.95,.99])
shape=(m/sd)**2
scale=sd**2/m
gamma_q=gamma.ppf(probs,a=shape,scale=scale)
lognormal_q=lognorm.ppf(probs,s=np.sqrt(lv),scale=m*np.exp(-lv/2))
gamma_values=np.random.default_rng(6722).gamma(shape=shape,scale=scale,size=200000)
mean_z=(gamma_values.mean()-m)/(sd/np.sqrt(len(gamma_values)))
gamma_sd_error=gamma_values.std(ddof=1)/sd-1
record('matched_moment_gamma_family_sensitivity',abs(mean_z)<6 and abs(gamma_sd_error)<.025 and (gamma_values>0).all(),{'mean':m,'SD':sd,'probabilities':probs.tolist(),'lognormal_quantiles':lognormal_q.tolist(),'gamma_quantiles':gamma_q.tolist(),'gamma_simulated_n':len(gamma_values),'gamma_mean_MC_SE':float(mean_z),'gamma_relative_SD_error':float(gamma_sd_error),'scope':'Family alternative preserves moments but changes quantiles; no retrieved quantiles identify either family.'})

tree=ast.parse((OUT/'generator.py').read_text(encoding='utf-8'))
imports=[alias.name for node in ast.walk(tree) if isinstance(node,ast.Import) for alias in node.names]
forbidden=[node.func.id for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in {'open','exec','eval','compile','__import__'}]
record('generator_static_import_and_IO_scan',set(imports)<={'numpy','pandas'} and not forbidden,{'imports':imports,'forbidden_calls':forbidden,'limitation':'Simple scan, not formal verification or a sandbox.'})
checks['all_passed']=all(x['passed'] for x in checks['tests'])
checks['target_outcome_tests_performed']=False
checks['parameters_tuned_to_checks']=False
checks['retrieval_budget']={'queries_used':8,'download_attempts_used':7,'remaining_queries':4,'remaining_download_attempts':5}
checks['final_hashes']={f:hashlib.sha256((OUT/f).read_bytes()).hexdigest() for f in ('generator.py','model_spec.json','evidence.json','decision.md','revision.json')}
(OUT/'artificial_checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'all_passed':checks['all_passed'],'test_count':len(checks['tests']),'output':str(OUT/'artificial_checks.json'),'sensitivity_summary':sensitivity},indent=2))
