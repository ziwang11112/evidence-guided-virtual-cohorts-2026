from pathlib import Path
import copy,hashlib,importlib.util,json,re,sys
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
ROOT=Path.cwd();RUN=ROOT/'runs/gap_2';FINAL=RUN/'final'
sys.path.insert(0,str(ROOT));import loop_control as lc
read=lc.read;sha=lc.sha
# Validate only candidate and review commitments. Do not read run_commitment files.
commitments={}
for version in ['initial','final']:
    freeze=read(RUN/version/'freeze.json')
    for name,h in freeze['commitment'].items():
        p=Path(name);assert p.is_relative_to(RUN);assert sha(p)==h
    commitments[version]=len(freeze['commitment'])
    lc.verify_gateway_snapshot(RUN/version/'gateway_snapshot.json')
for name,h in read(RUN/'review_receipt.json')['commitment'].items():
    p=Path(name);assert p.is_relative_to(RUN);assert sha(p)==h
noop={name:sha(RUN/'initial'/name)==sha(FINAL/name) for name in ['generator.py','model_spec.json']}
assert all(noop.values()) and read(FINAL/'revision.json')['generator_or_spec_changed'] is False
ledger=read(FINAL/'evidence.json');spec=read(FINAL/'model_spec.json');checks=read(FINAL/'artificial_checks.json')['revision_checks']
old=read(RUN/'initial/evidence.json')
for kind in ['sources','evidence']:
    new_by_id={v['id']:v for v in ledger[kind]}
    for v in old[kind]:assert new_by_id[v['id']]==v
_,eids=lc.validate_ledger(ledger);lc.validate_spec(spec,eids)
gaps=read(FINAL/'gaps.json');actions=read(FINAL/'actions.json')
lc.validate_gaps(gaps,final=True);lc.validate_actions(actions,gaps,final=True)
assert all(any(a['gap_id']==g['id'] and a.get('phase')=='revision' for a in actions) for g in gaps)
events=[json.loads(x) for x in (RUN/'literature/audit.jsonl').read_text().splitlines()]
registry={(e['artifact']['session_relative_path'],e['artifact']['sha256']) for e in events if e.get('type')=='artifact_approved' and e.get('status')=='accepted'}
refs=[a for s in ledger['sources'] for a in s['approved_artifacts']]+[a for act in actions for a in act['evidence_artifacts']]
for a in refs:
    assert (a['path'].removeprefix('literature/'),a['sha256']) in registry
    assert sha(RUN/a['path'])==a['sha256']
state=read(RUN/'literature/state.json')
assert state['usage']['queries']==8 and state['usage']['downloads']==7
assert any(s.get('reason')=='unsupported_supplement_format' for s in state['parents']['PMC6755842']['supplements'])
# Read source XML only from this ledger's approved files.
def tables(path):
    root=ET.parse(path).getroot()
    return {''.join(t.find('label').itertext()):t for t in root.findall('.//table-wrap') if t.find('label') is not None}
def rows(table):
    return [[' '.join(c.itertext()).strip() for c in tr if c.tag in ['td','th']] for tr in table.findall('.//tr')]
byid={e['id']:e for e in ledger['evidence']}
tw=tables(RUN/'literature/approved/23728f05bcc689d1e4d9549f25d163243c4dd6b3a174225f34a7758c1514eaa8.xml')
age=byid['E_TW_AGE_BY_BMI']['reported']
r5={r[0]:r for r in rows(tw['Table 5']) if r}
r2={r[0]:r for r in rows(tw['Table 2']) if r}
for j,label in enumerate(['30\u201340','40\u201350','51\u201360','61\u201370']):
    for k in range(4):
        assert int(r2[label][1+2*k])==age['n_age_by_bmi'][k][j]
        if j:
            assert float(r5[label][1+2*k].replace('\u2212','-'))==age['contrasts_mg_dl_by_bmi'][k][j]
            actual=r5[label][2+2*k].replace(' ','')
            expected=age['p_values_by_bmi'][k][j]
            if isinstance(expected,str):assert actual==expected
            else:assert float(actual)==expected
assert np.array_equal(np.sum(age['n_age_by_bmi'],axis=1),age['n_bmi'])
tur=tables(RUN/'literature/approved/765766b336a0dee9b8ed92251cc725b827fe94184396f59032703d216a5f1c38.xml')
tr=byid['E_TUR_OBESITY_CLASSES']['reported']
tur_rows={r[0]:r for r in rows(tur['Table 1']) if r}
for k,label in enumerate(['Obese class I','Obese class II','Obese class III']):
    rr=tur_rows[label]
    for column,var in [(1,'age'),(2,'bmi'),(5,'hdl_mg_dl')]:
        match=re.match(r'\s*([0-9.]+)\s*\u00b1\s*([0-9.]+)',rr[column])
        assert match and [float(x) for x in match.groups()]==[tr['mean_'+var][k],tr['sd_'+var][k]]
assert 'Data are shown as means' in ''.join(tur['Table 1'].itertext())
# Read and static-check before importing frozen code; static checker is not a sandbox.
static=lc.source_check(FINAL/'generator.py');lc.source_check(RUN/'initial/generator.py')
rng=np.random.get_state()
def module(path,name):
    ms=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(ms);ms.loader.exec_module(m);return m
g=module(FINAL/'generator.py','gap2_final_review');oldg=module(RUN/'initial/generator.py','gap2_initial_review')
assert lc.rng_equal(rng,np.random.get_state())
contract=read(ROOT/'runner_contract.json')
fake=pd.DataFrame([(f'final_art_{i}',b,a,s) for i,(b,a,s) in enumerate(( (b,a,s) for s in [1,2] for b in [13,17.5,25.5,30,36.92,45.77,81] for a in [20,35,50,65.5,79]))],columns=contract['observed_columns'],index=np.arange(70)*5+11)
fake0=fake.copy(deep=True);spec0=copy.deepcopy(spec)
for seed in [176,355]:
    out=g.generate(fake,spec,seed);oldout=oldg.generate(fake,spec,seed)
    pd.testing.assert_frame_equal(out,oldout,check_exact=True)
    pd.testing.assert_frame_equal(out,g.generate(fake,spec,seed),check_exact=True)
    lc.output_check(fake,out,contract)
assert not g.generate(fake,spec,176).hdl.equals(g.generate(fake,spec,355).hdl)
pd.testing.assert_frame_equal(fake,fake0,check_exact=True)
assert spec==spec0 and lc.rng_equal(rng,np.random.get_state())
p=spec['parameters'];pooled=np.array(p['age_effect_mg_dl']);w=np.array([4112,4087,4141,2197],float);w/=w.sum();center=w@pooled
age_var=float(w@((pooled-center)**2));assert abs(age_var-checks['variance_accounting']['between_age_variance'])<1e-14
for cell in checks['variance_accounting']['cells']:
    assert abs(np.sqrt(cell['reported_cell_SD_proxy']**2+age_var)-cell['model_marginal_SD_under_same_assumed_mixture'])<1e-12
for k,record in enumerate(checks['age_modifier_sensitivity']):
    np.testing.assert_allclose(np.array(age['contrasts_mg_dl_by_bmi'][k])-pooled,record['stratified_minus_pooled_mg_dl'],rtol=0,atol=1e-12)
source_contrast=tr['mean_hdl_mg_dl'][2]-tr['mean_hdl_mg_dl'][0]
assert abs(source_contrast-checks['turkish_obesity_contrast']['published_classIII_minus_I_mg_dl'])<1e-12
for sex in [1,2]:
    toy=pd.DataFrame({'row_id':['a','b','c'],'bmi':tr['mean_bmi'],'age':tr['mean_age'],'sex':[sex]*3})
    means,_=g.conditional_moments(toy,spec)
    record=checks['turkish_obesity_contrast']['plugin_model_comparisons'][sex-1]
    np.testing.assert_allclose(means,record['selected_plugin_means'],rtol=0,atol=1e-12)
    alt=copy.deepcopy(spec);alt['parameters']['tail_asymptote_by_sex']={s:p['mean_hdl_by_sex'][s][-1] for s in ['1','2']}
    flat,_=g.conditional_moments(toy,alt)
    assert abs((flat[2]-flat[0])-record['flat_classIII_minus_I'])<1e-12
result={'status':'passed','scope':'Only own initial/final candidates, own approved source artifacts/audit and invented inputs; no participant rows, target outcomes or external retrieval.','static_check':static,'initial_and_final_candidate_commitments_verified':commitments,'prior_review_commitment_verified':True,'gateway_audit_prefixes_verified':True,'exact_noop':noop,'all_initial_sources_and_evidence_retained_unchanged':True,'registered_source_action_links':len(refs),'all_final_gap_dispositions_and_revision_actions_valid':True,'usage':{'queries':8,'downloads':7},'mexican_supplement_unavailable_verified':True,'source_extractions_verified':'Taiwan all 12 nonreference age contrasts/p-values and 16 age-by-BMI counts; Turkish all obesity-class age/BMI/HDL means and SDs; Turkish n and sample restrictions, Mexican sample/measurement read from approved maintext','invented_rows':70,'invented_check_seeds':[176,355],'initial_final_outputs_exactly_equal':True,'contract_no_mutation_and_local_rng_checks':'passed','age_mixture_variance':age_var,'turkish_class_III_minus_I_mg_dl':source_contrast,'all_recorded_age_variance_and_obesity_plugin_calculations_reproduced':True}
(RUN/'final_review_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

