from pathlib import Path
import copy, hashlib, importlib.util, json, sys
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
ROOT = Path.cwd()
RUN = ROOT/'runs/gap_2'
sys.path.insert(0, str(ROOT))
import loop_control as lc
initial=RUN/'initial'
spec=lc.read(initial/'model_spec.json')
ledger=lc.read(initial/'evidence.json')
static=lc.source_check(initial/'generator.py')
before_rng=np.random.get_state()
ms=importlib.util.spec_from_file_location('review_gap2_initial',initial/'generator.py')
g=importlib.util.module_from_spec(ms)
ms.loader.exec_module(g)
assert lc.rng_equal(before_rng,np.random.get_state())
_,eids=lc.validate_ledger(ledger)
lc.validate_spec(spec,eids)
gaps=lc.read(initial/'gaps.json'); actions=lc.read(initial/'actions.json')
lc.validate_gaps(gaps);lc.validate_actions(actions,gaps)
# Only candidate commitments; never touch run_commitment, participant data or target results.
freeze=lc.read(initial/'freeze.json')
for path,h in freeze['commitment'].items():
    p=Path(path)
    assert p.is_relative_to(RUN)
    assert lc.sha(p)==h
registry={(ev['artifact']['session_relative_path'],ev['artifact']['sha256']) for line in (RUN/'literature/audit.jsonl').read_text().splitlines() for ev in [json.loads(line)] if ev.get('type')=='artifact_approved' and ev.get('status')=='accepted'}
linked=0
for a in [a for s in ledger['sources'] for a in s['approved_artifacts']]+[a for x in actions for a in x['evidence_artifacts']]:
    assert (a['path'].removeprefix('literature/'),a['sha256']) in registry
    assert lc.sha(RUN/a['path'])==a['sha256']
    linked+=1
contract=lc.read(ROOT/'runner_contract.json')
rows=[(f'invented_{i}',b,a,s) for i,(b,a,s) in enumerate(( (b,a,s) for s in (1,2) for b in (12,17.5,21.25,25.5,30,42,80) for a in (20,35,45,55.5,65.5,79) ))]
fake=pd.DataFrame(rows,columns=contract['observed_columns'],index=np.arange(len(rows))*3+9)
fake0=fake.copy(deep=True);spec0=copy.deepcopy(spec)
y=g.generate(fake,spec,8801);z=g.generate(fake,spec,8801);v=g.generate(fake,spec,8802)
lc.output_check(fake,y,contract)
pd.testing.assert_frame_equal(y,z,check_exact=True)
pd.testing.assert_frame_equal(fake,fake0,check_exact=True)
assert spec==spec0 and lc.rng_equal(before_rng,np.random.get_state())
assert y.index.equals(fake.index) and not y.hdl.equals(v.hdl)
lc.output_check(fake.iloc[:0],g.generate(fake.iloc[:0],spec,42),contract)
reject=[]
for name,col,value in [('bad sex','sex',3),('NaN BMI','bmi',float('nan')),('infinite age','age',float('inf')),('zero BMI','bmi',0),('negative age','age',-1)]:
    b=fake.copy();b.loc[b.index[0],col]=value
    try:g.generate(b,spec,8)
    except ValueError:reject.append(name)
    else:raise AssertionError(name+' was accepted')
try:g.generate(fake.drop(columns=['age']),spec,8)
except ValueError:reject.append('missing column')
else:raise AssertionError('missing column accepted')
p=spec['parameters']
c=next(e for e in ledger['evidence'] if e['id']=='E_TW_CELLS')['reported']
for s in ('1','2'):
    assert p['mean_hdl_by_sex'][s]==c['mean_by_sex'][s]
    np.testing.assert_allclose(p['sd_hdl_by_sex'][s],np.array(c['standard_error_by_sex'][s])*np.sqrt(c['n_by_sex'][s]),rtol=0,atol=1e-12)
a=next(e for e in ledger['evidence'] if e['id']=='E_TW_AGE')['reported']
center=float(np.average(a['contrasts_mg_dl'],weights=a['n_age']))
assert abs(center-p['age_center_mg_dl'])<1e-12
moments=[]
for s in (1,2):
    for j,b in enumerate(p['bmi_anchor_kg_m2']+[42]):
        n=100000
        toy=pd.DataFrame({'row_id':[f'm_{i}' for i in range(n)],'bmi':b,'age':50.,'sex':s})
        m,d=g.conditional_moments(toy.iloc[:1],spec)
        draw=g.generate(toy,spec,90100+s*100+j).hdl.to_numpy()
        mean_z=float(abs(draw.mean()-m[0])/(d[0]/np.sqrt(n)))
        sd_error=float(abs(draw.std(ddof=1)/d[0]-1))
        assert mean_z<5 and sd_error<.025
        moments.append({'sex':s,'bmi':b,'age':50,'n':n,'mean_MC_SE_error':mean_z,'SD_relative_error':sd_error})
# Evaluate continuity from both sides of every interpolation/tail boundary.
continuity=[]
for s in (1,2):
    for b in p['bmi_anchor_kg_m2']:
        toy=pd.DataFrame({'row_id':['l','m','r'],'bmi':[b-1e-7,b,b+1e-7],'age':50,'sex':s})
        m,d=g.conditional_moments(toy,spec)
        assert np.max(abs(np.diff(m)))<1e-5 and np.max(abs(np.diff(d)))<1e-5
        continuity.append(float(np.max(abs(np.diff(m)))))
# Recompute the builder's declared flat-tail sensitivity independently.
alt=copy.deepcopy(spec)
alt['parameters']['tail_asymptote_by_sex']={s:p['mean_hdl_by_sex'][s][-1] for s in ('1','2')}
sensitivity=[]
for s in (1,2):
    toy=pd.DataFrame({'row_id':['a','b'],'bmi':[40,70],'age':50,'sex':s})
    chosen,_=g.conditional_moments(toy,spec);flat,_=g.conditional_moments(toy,alt)
    sensitivity.append({'sex':s,'bmi':[40,70],'chosen_minus_flat':(chosen-flat).tolist()})
checks={'scope':'Own candidate/registered approved artifacts and invented rows only; no participant CSVs or target outcomes.', 'static_check':static,'freeze_candidate_commitments_unchanged':True,'schema_and_provenance_valid':True,'registered_source_and_action_artifact_links_verified':linked,'invented_grid_rows':len(fake),'contract_checks':'pass: exact values/order/index/schema, no mutation of input/spec/global RNG, same seed identical, different seed different, positive finite, empty frame','invalid_cases_rejected':reject,'SE_to_SD_all_eight_cells':'exact within 1e-12','source_age_center':center,'monte_carlo_moment_checks':moments,'max_boundary_discontinuity_epsilon':max(continuity),'recomputed_flat_tail_sensitivity':sensitivity}
(RUN/'initial_review_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
