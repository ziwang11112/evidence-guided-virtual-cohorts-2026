"""Checks on invented rows and publication summaries only; never reads target HDL."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm

HERE=Path(__file__).resolve().parent
spec=json.loads((HERE/'model_spec.json').read_text(encoding='utf-8'))
ledger=json.loads((HERE/'evidence.json').read_text(encoding='utf-8'))
module_spec=importlib.util.spec_from_file_location('gap2_generator', HERE/'generator.py')
module=importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)

fake=pd.DataFrame({'row_id':['art-'+str(i) for i in range(12)],
 'bmi':[14.1,17.5,21.25,25.5,30,77.5]*2,
 'age':[20,35,45,55,65,79]*2, 'sex':[1]*6+[2]*6},index=np.arange(12)*7)
before=fake.copy(deep=True)
global_before=np.random.get_state()
out=module.generate(fake,spec,101)
global_after=np.random.get_state()
same=module.generate(fake,spec,101)
other=module.generate(fake,spec,102)
global_same=all(np.array_equal(x,y) if isinstance(x,np.ndarray) else x==y for x,y in zip(global_before,global_after))
contract={
 'exact_output_columns':list(out)==['row_id','bmi','age','sex','hdl'],
 'same_row_order_and_original_index':out.index.equals(fake.index) and out.row_id.equals(fake.row_id),
 'all_original_values_preserved_exactly':out[['row_id','bmi','age','sex']].equals(before),
 'input_unmodified':fake.equals(before),
 'seed_reproducibility':out.equals(same),
 'different_seeds_change_draws':not out.hdl.equals(other.hdl),
 'finite_positive':bool(np.isfinite(out.hdl).all() and (out.hdl>0).all()),
 'global_numpy_rng_unmodified':global_same,
 'empty_input_supported':module.generate(fake.iloc[:0],spec,3).shape==(0,5)
}
assert all(contract.values())

bad=fake.copy()
bad.loc[bad.index[0],'sex']=3
try:
    module.generate(bad,spec,1)
    invalid_rejected=False
except ValueError:
    invalid_rejected=True
assert invalid_rejected
contract['invalid_sex_rejected']=invalid_rejected

p=spec['parameters']
source_conversion=[]
cell_evidence=next(x for x in ledger['evidence'] if x['id']=='E_TW_CELLS')['reported']
for s in ['1','2']:
    for j in range(4):
        derived=cell_evidence['standard_error_by_sex'][s][j]*np.sqrt(cell_evidence['n_by_sex'][s][j])
        chosen=p['sd_hdl_by_sex'][s][j]
        assert abs(derived-chosen)<1e-12
        source_conversion.append({'sex':int(s),'bmi_category_index':j,'n':cell_evidence['n_by_sex'][s][j],
          'published_SE':cell_evidence['standard_error_by_sex'][s][j], 'derived_cell_SD':float(derived),'used_SD':chosen})

nrep=60000
moment_checks=[]
for s in [1,2]:
    for j,bmi in enumerate(p['bmi_anchor_kg_m2']):
        toy=pd.DataFrame({'row_id':np.arange(nrep).astype(str),'bmi':bmi,'age':45,'sex':s})
        expected_mean,expected_sd=module.conditional_moments(toy,spec)
        draw=module.generate(toy,spec,900+s*10+j).hdl.to_numpy()
        actual_mean=float(draw.mean())
        actual_sd=float(draw.std(ddof=1))
        mean_error_sem=abs(actual_mean-expected_mean[0])/(expected_sd[0]/np.sqrt(nrep))
        sd_relative_error=abs(actual_sd/expected_sd[0]-1)
        assert mean_error_sem<5 and sd_relative_error<.025
        moment_checks.append({'sex':s,'bmi':bmi,'age':45,'n':nrep,
         'specified_arithmetic_mean':float(expected_mean[0]),'simulated_mean':actual_mean,
         'specified_SD':float(expected_sd[0]),'simulated_SD':actual_sd,
         'mean_error_in_Monte_Carlo_SE':float(mean_error_sem),'relative_SD_error':float(sd_relative_error)})

# Actual pointwise implication of source age-centered anchors; no invented source data fit.
weights=np.array([4112,4087,4141,2197],dtype=float)
weights/=weights.sum()
source_anchor_checks=[]
for s in [1,2]:
    for j,bmi in enumerate(p['bmi_anchor_kg_m2']):
        toy=pd.DataFrame({'row_id':['a','b','c','d'],'bmi':[bmi]*4,'age':p['age_knots_years'],'sex':[s]*4})
        cm,cs=module.conditional_moments(toy,spec)
        integrated=float(np.dot(weights,cm))
        anchor=p['mean_hdl_by_sex'][str(s)][j]
        assert abs(integrated-anchor)<1e-12
        source_anchor_checks.append({'sex':s,'bmi_assumed_representative':bmi,'reported_cell_mean':anchor,
          'model_mean_at_assumed_BMI_and_source_midpoint_age_mixture':integrated})

alternative=copy.deepcopy(spec)
alternative['parameters']['tail_asymptote_by_sex']={s:p['mean_hdl_by_sex'][s][-1] for s in ['1','2']}
sensitivity=[]
for s in [1,2]:
    toy=pd.DataFrame({'row_id':['tail-'+str(x) for x in range(5)],'bmi':[30,35,40,50,70],'age':[50]*5,'sex':[s]*5})
    m,sd=module.conditional_moments(toy,spec)
    alt_m,_=module.conditional_moments(toy,alternative)
    for j,bmi in enumerate(toy.bmi):
        def prob_below(mean,sd,cutoff):
            lv=np.log1p((sd/mean)**2)
            return float(norm.cdf((np.log(cutoff)-np.log(mean)+lv/2)/np.sqrt(lv)))
        # 40/50 thresholds are explicitly reported in S_TW introduction.
        threshold=40 if s==1 else 50
        sensitivity.append({'sex':s,'bmi':int(bmi),'age':50,'selected_mean':float(m[j]),
         'flat_continuation_mean':float(alt_m[j]),'mean_difference_selected_minus_flat':float(m[j]-alt_m[j]),
         'illustrative_threshold_mg_dl':threshold,'selected_probability_below':prob_below(m[j],sd[j],threshold),
         'flat_probability_below':prob_below(alt_m[j],sd[j],threshold)})

grid=pd.DataFrame([(f'grid-{s}-{a}-{b}',b,a,s) for s in [1,2] for a in [20,30,45,60,70,79] for b in [14.1,18,21.25,25.5,30,40,60,77.5]],columns=['row_id','bmi','age','sex'])
gm,gs=module.conditional_moments(grid,spec)
grid_checks={'all_means_and_sds_positive':bool((gm>0).all() and (gs>0).all()),'minimum_mean':float(gm.min()),'maximum_mean':float(gm.max()),'minimum_sd':float(gs.min()),'maximum_sd':float(gs.max())}
assert grid_checks['all_means_and_sds_positive']

hashes=[]
for source in ledger['sources']:
    for artifact in source['approved_artifacts']:
        actual=hashlib.sha256((HERE.parent/artifact['path']).read_bytes()).hexdigest()
        assert actual==artifact['sha256']
        hashes.append({'source_id':source['id'],'path':artifact['path'],'sha256_matches':True})
eids={x['id'] for x in ledger['evidence']}
aids={x['id'] for x in spec['assumptions']}
assert set(spec['parameters'])==set(spec['parameter_provenance'])
for value in spec['parameter_provenance'].values():
    assert set(value['evidence_ids'])<=eids and set(value['assumption_ids'])<=aids
    assert value['evidence_ids'] or value['assumption_ids']

checks={'scope':'Invented-input implementation checks, publication-arithmetic checks and analytical sensitivity only. No target HDL or target generated-cohort evaluation.',
 'status':'passed','contract':contract,'source_SE_to_SD_conversion':source_conversion,
 'invented_repeated_input_moments':moment_checks,'source_operator_check':{
 'status':'partial_assumption_conditional_check_only',
 'computed':source_anchor_checks,
 'qualification':'These match means at assumed representative BMI and source-age midpoint mixing by construction. Actual source sex/BMI-cell age/BMI joint distributions are absent, so the published integrated means and regression slopes cannot be independently reproduced.'},
 'focused_countermodel':{'description':'Same central anchors and same residual SDs; flat continuation above BMI 30 versus selected exponential decline.','results':sensitivity,
 'inference':'Severe-obesity location and threshold probability can change materially while central evidence anchors are identical. This finite pair is not an uncertainty interval.'},
 'invented_domain_grid':grid_checks,'source_artifact_hashes':hashes,
 'schema_reference_checks':True,
 'remaining_uncomputable_source_operators':['Dallas marginal quantile fit without its joint BMI-age-ethnicity distribution','UK/Malawi numerical slope with unavailable PDF supplement','Exact Taiwan regression/cell fit across unavailable within-category predictors']}
(HERE/'artificial_checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':checks['status'],'contract':contract,'grid':grid_checks,'maximum_mean_Monte_Carlo_SE_error':max(x['mean_error_in_Monte_Carlo_SE'] for x in moment_checks),'maximum_relative_SD_error':max(x['relative_SD_error'] for x in moment_checks),'focused_countermodel':sensitivity},indent=2))
