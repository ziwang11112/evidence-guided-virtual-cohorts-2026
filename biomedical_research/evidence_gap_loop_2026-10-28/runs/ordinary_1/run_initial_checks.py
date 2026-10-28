"""Checks on source arithmetic and invented predictors only, never target HDL."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import pandas as pd

RUN = Path(__file__).resolve().parent
OUT = RUN/'initial'
spec = json.loads((OUT/'model_spec.json').read_text(encoding='utf-8'))
ledger = json.loads((OUT/'evidence.json').read_text(encoding='utf-8'))
module_spec = importlib.util.spec_from_file_location('ordinary1_initial', OUT/'generator.py')
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)
generate = module.generate
p = spec['parameters']
checks = {'scope':'Source-only arithmetic, implementation contracts and invented-input numerical checks. No target HDL or target generated-cohort validation.', 'tests':[]}

def record(name, passed, detail):
    checks['tests'].append({'name':name,'passed':bool(passed),'detail':detail})
    if not passed:
        raise AssertionError(name)

eids = {e['id'] for e in ledger['evidence']}
sids = {s['id'] for s in ledger['sources']}
aids = {a['id'] for a in spec['assumptions']}
record('complete_parameter_provenance',set(p)==set(spec['parameter_provenance']),{'parameter_count':len(p)})
for name, provenance in spec['parameter_provenance'].items():
    assert provenance['evidence_ids'] or provenance['assumption_ids']
    assert set(provenance['evidence_ids']) <= eids
    assert set(provenance['assumption_ids']) <= aids
assert all(e['source_id'] in sids for e in ledger['evidence'])
record('all_provenance_ids_resolve',True,{'evidence_records':len(eids),'source_records':len(sids),'assumptions':len(aids)})
artifact_count=0
for source in ledger['sources']:
    for artifact in source['approved_artifacts']:
        assert hashlib.sha256((RUN/artifact['path']).read_bytes()).hexdigest()==artifact['sha256']
        artifact_count+=1
record('registered_artifact_bytes_match_returned_hashes',True,{'verified_files':artifact_count,'registry_scope':'Paths and hashes are exact gateway-returned accepted artifacts; this check verifies current bytes, not an independent new registry approval.'})

counts = np.array(p['source_age_counts_by_bmi'])
sex_counts=np.array(p['source_cell_counts']['male'])+np.array(p['source_cell_counts']['female'])
record('source_table_margins',np.array_equal(counts.sum(axis=1),sex_counts),{'bmi_totals':counts.sum(axis=1).tolist(),'male_total':sum(p['source_cell_counts']['male']),'female_total':sum(p['source_cell_counts']['female'])})
source_sd={label:(np.array(p['source_mean_standard_errors'][label])*np.sqrt(p['source_cell_counts'][label])).tolist() for label in ('male','female')}
record('SEM_to_SD_conversion',all(np.isfinite(v).all() and (np.array(v)>0).all() for v in source_sd.values()),{'derived_individual_SD_mg_dl':source_sd,'warning':'These are marginal broad-cell SDs, not directly measured conditional residual SDs.'})

toy=pd.DataFrame({'row_id':['q9','a1','z5','b7','c3','m2'], 'bmi':[14.1,21.25,25.5,30.5,77.5,100.0], 'age':[20,35,45,55.5,79,100], 'sex':[1,2,1,2,1,2]}, index=[7,2,9,4,8,0])
before=toy.copy(deep=True)
state_before=np.random.get_state()
one=generate(toy,spec,1729)
state_after=np.random.get_state()
two=generate(toy,spec,1729)
three=generate(toy,spec,1730)
pd.testing.assert_frame_equal(toy,before,check_exact=True)
pd.testing.assert_frame_equal(one.iloc[:,:4],toy,check_exact=True)
record('schema_order_preservation_and_no_mutation',list(one.columns)==['row_id','bmi','age','sex','hdl'],{'rows':len(toy),'nonsequential_index_preserved':one.index.equals(toy.index)})
record('seed_repeatability_and_variation',np.array_equal(one.hdl,two.hdl) and not np.array_equal(one.hdl,three.hdl),{'same_seed':1729,'different_seed':1730})
record('global_RNG_unchanged',state_before[0]==state_after[0] and np.array_equal(state_before[1],state_after[1]) and state_before[2:]==state_after[2:],{})
record('finite_positive_extreme_invented_inputs',np.isfinite(one.hdl).all() and (one.hdl>0).all(),{'bmi_range':[14.1,100],'age_range':[20,100],'outside_target_support_is_stress_test':True})
empty=generate(toy.iloc[:0],spec,1)
record('empty_input',empty.shape==(0,5),{})
invalid=toy.copy()
invalid.loc[7,'sex']=3
try:
    generate(invalid,spec,1)
    invalid_raised=False
except ValueError:
    invalid_raised=True
record('invalid_sex_rejected',invalid_raised,{})

# Independently use the stated arithmetic moment identities, then check draws.
age_values=np.array(p['age_contrasts'])
centers=counts@age_values/counts.sum(axis=1)
moment_results=[]
n_mc=100000
for code,label in ((1,'male'),(2,'female')):
    for j,bmi in enumerate(p['bmi_knots']):
        invented=pd.DataFrame({'row_id':np.arange(n_mc).astype(str),'bmi':bmi,'age':35,'sex':code})
        values=generate(invented,spec,5000+10*code+j)['hdl'].to_numpy()
        source_mean=p['source_hdl_means'][label][j]
        expected_mean=source_mean-centers[j]
        expected_sd=expected_mean*source_sd[label][j]/source_mean
        empirical_mean=float(values.mean())
        empirical_sd=float(values.std(ddof=1))
        mean_z=(empirical_mean-expected_mean)/(expected_sd/np.sqrt(n_mc))
        passed=abs(mean_z)<6 and abs(empirical_sd/expected_sd-1)<0.02
        moment_results.append({'sex':label,'bmi':bmi,'n':n_mc,'expected_mean':float(expected_mean),'empirical_mean':empirical_mean,'expected_sd':float(expected_sd),'empirical_sd':empirical_sd,'mean_MC_standard_errors':float(mean_z),'passed':bool(passed)})
record('invented_anchor_distribution_moments',all(r['passed'] for r in moment_results),{'tolerance':'mean within 6 Monte Carlo standard errors and SD within 2%; checks distribution arithmetic only','cells':moment_results})

# Age-centering algebra at reported representative age groups, without target data.
centering_error=[]
for label in ('male','female'):
    for j,m in enumerate(p['source_hdl_means'][label]):
        age_specific_mean=m-centers[j]+age_values
        weighted=(age_specific_mean*counts[j]).sum()/counts[j].sum()
        centering_error.append(abs(weighted-m))
record('source_age_centering_identity',max(centering_error)<1e-10,{'maximum_absolute_error':max(centering_error),'scope':'Exact for assumed source age-group representatives, not a claim that interpolation integrates to actual unobserved source distributions.'})

grid_rows=[{'row_id':f'{sex}-{age}-{bmi}-{rep}','bmi':bmi,'age':age,'sex':sex} for sex in (1,2) for age in (20,50,79) for bmi in (17,21.25,25.5,30.5,40,60,80) for rep in range(1000)]
grid=pd.DataFrame(grid_rows)
baseline=generate(grid,spec,901)
flat=copy.deepcopy(spec)
flat['parameters']['tail_log_slopes']={'male':0,'female':0}
flat_values=generate(grid,flat,901)
no_age=copy.deepcopy(spec)
no_age['parameters']['age_contrasts']=[0,0,0,0]
no_age_values=generate(grid,no_age,901)
ratio=baseline.hdl.to_numpy()/flat_values.hdl.to_numpy()
expected_ratio=np.exp(np.where(grid.sex==1,p['tail_log_slopes']['male'],p['tail_log_slopes']['female'])*np.maximum(grid.bmi-30.5,0))
record('paired_flat_tail_sensitivity',np.allclose(ratio,expected_ratio,rtol=1e-12,atol=1e-12),{'BMI_80_mean_ratio_selected_to_flat_male':float(np.exp(-.0077*(80-30.5))),'BMI_80_mean_ratio_selected_to_flat_female':float(np.exp(-.0042*(80-30.5))),'interpretation':'Large tail extrapolation sensitivity remains; chosen tail was not tuned using these draws.'})
record('age_pattern_sensitivity',np.isfinite(no_age_values.hdl).all() and (no_age_values.hdl>0).all(),{'max_abs_paired_relative_change':float(np.max(np.abs(no_age_values.hdl/baseline.hdl-1))),'alternative':'All age contrasts set to zero; source means, variability and other parameters unchanged.'})
record('invented_grid_positive_variability',np.isfinite(baseline.hdl).all() and (baseline.hdl>0).all() and baseline.groupby(['sex','age','bmi']).hdl.std().gt(0).all(),{'n':len(grid),'cells':42,'replicates_per_cell':1000,'HDL_min':float(baseline.hdl.min()),'HDL_max':float(baseline.hdl.max()),'scope':'Synthetic stress support only; extremes are not clinical reference limits.'})

tree=ast.parse((OUT/'generator.py').read_text(encoding='utf-8'))
imports=[]
for node in ast.walk(tree):
    if isinstance(node,ast.Import):
        imports.extend(alias.name for alias in node.names)
    elif isinstance(node,ast.ImportFrom):
        imports.append(node.module)
forbidden_calls=[node.func.id for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in {'open','eval','exec','compile','__import__'}]
record('generator_static_dependency_and_io_scan',set(imports)<= {'numpy','pandas'} and not forbidden_calls,{'imports':imports,'forbidden_calls':forbidden_calls,'limitation':'Simple source scan, not a formal security proof.'})
checks['retrieval_budget']={'used_queries':6,'used_download_attempts':5,'remaining_queries':6,'remaining_download_attempts':7}
checks['target_outcome_tests_performed']=False
checks['parameters_tuned_to_checks']=False
checks['all_passed']=all(test['passed'] for test in checks['tests'])
(OUT/'artificial_checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'all_passed':checks['all_passed'],'test_count':len(checks['tests']),'output':str(OUT/'artificial_checks.json')},indent=2))
