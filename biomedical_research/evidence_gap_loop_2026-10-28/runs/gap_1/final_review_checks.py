"""Independent final check; no builder script execution or participant reads."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import math
import re
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from scipy.integrate import quad

RUN = Path(__file__).resolve().parent
ROOT = RUN.parent.parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

initial, final = RUN / 'initial', RUN / 'final'
initial_receipt, final_receipt = read(initial/'freeze.json'), read(final/'freeze.json')
verified = {}
for stage, receipt in [('initial', initial_receipt), ('final', final_receipt)]:
    verified[stage] = []
    for name, digest in receipt['commitment'].items():
        path = Path(name)
        assert path.is_relative_to(RUN)
        assert sha(path) == digest
        verified[stage].append(str(path.relative_to(RUN)))
assert initial_receipt['run_commitment'] == final_receipt['run_commitment']
assert initial_receipt['run_sha256'] == final_receipt['run_sha256']
common_checked = []
receipt_only = []
for name, digest in final_receipt['run_commitment'].items():
    path = Path(name)
    if path.name in ['observed.csv', 'protocol.json']:
        receipt_only.append(str(path.relative_to(ROOT)))
        continue
    assert sha(path) == digest
    common_checked.append(str(path.relative_to(ROOT)))
assert not (ROOT/'revise_gap1.py').exists()
assert (RUN/'revise_gap1.py').exists()
for name in ['generator.py', 'model_spec.json']:
    assert (initial/name).read_bytes() == (final/name).read_bytes()
initial_review = read(RUN/'initial_review.json')
for field, name in [('generator_sha256','generator.py'),('model_spec_sha256','model_spec.json'),('evidence_sha256','evidence.json'),('candidate_freeze_sha256','freeze.json')]:
    assert sha(initial/name) == initial_review[field]

control = module('gap1_final_review_controller', ROOT/'loop_control.py')
static = control.source_check(final/'generator.py')
gen = module('gap1_final_review_generator', final/'generator.py')
oldgen = module('gap1_final_review_initial_generator', initial/'generator.py')
spec, ledger = read(final/'model_spec.json'), read(final/'evidence.json')
oldledger = read(initial/'evidence.json')
assert ledger['sources'] == oldledger['sources']
assert ledger['evidence'][:-1] == oldledger['evidence']
assert ledger['evidence'][-1]['id'] == 'E_US_CELL_MOMENTS'
_, eids = control.validate_ledger(ledger)
control.validate_spec(spec, eids)
gaps, actions = read(final/'gaps.json'), read(final/'actions.json')
control.validate_gaps(gaps, final=True)
control.validate_actions(actions, gaps, final=True)
assert len(gaps) == 9 and len(actions) == 12
assert sum(g['status'] == 'unresolved' for g in gaps) == 8
assert next(g for g in gaps if g['id'] == 'G_AUDIT')['status'] == 'resolved'
audit = (RUN/'literature/audit.jsonl').read_bytes()
registry = set()
for line in audit.splitlines():
    event = json.loads(line)
    if event.get('type') == 'artifact_approved' and event.get('status') == 'accepted':
        a = event['artifact']
        registry.add(('literature/'+a['session_relative_path'], a['sha256']))
for a in [a for s in ledger['sources'] for a in s['approved_artifacts']] + [a for x in actions for a in x['evidence_artifacts']]:
    assert (a['path'],a['sha256']) in registry and sha(RUN/a['path']) == a['sha256']
assert (initial/'gateway_snapshot.json').read_bytes() == (final/'gateway_snapshot.json').read_bytes()
snapshot = read(final/'gateway_snapshot.json')
assert len(audit) == snapshot['audit_bytes']
assert hashlib.sha256(audit).hexdigest() == snapshot['audit_prefix_sha256']
assert snapshot['usage']['queries'] == 6 and snapshot['usage']['downloads'] == 3

# Check new extraction directly against the registered JATS table's columns.
source = next(s for s in ledger['sources'] if s['id'] == 'S_US')
xml_art = next(a for a in source['approved_artifacts'] if a['path'].endswith('.xml'))
xml = ET.parse(RUN/xml_art['path']).getroot()
table = next(t for t in xml.iter('table-wrap') if t.get('id') == 'Tab2')
rows = {}
for tr in table.iter('tr'):
    values = [''.join(c.itertext()).strip() for c in tr if c.tag in ('td','th')]
    if values and values[0] in ['n', 'Age (yrs.)', 'BMI (kg/m2)', 'HDL-C (mg/dL)']:
        rows[values[0]] = [values[i] for i in [1,2,4,5,7,8,10,11]]
new = ledger['evidence'][-1]['reported']['cells']
cells = new['male'] + new['female']
for i, cell in enumerate(cells):
    assert int(rows['n'][i]) == cell['n']
    for label, prefix in [('Age (yrs.)','age'),('BMI (kg/m2)','bmi'),('HDL-C (mg/dL)','hdl')]:
        numbers = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', rows[label][i])]
        assert numbers == [cell[prefix+'_mean'],cell[prefix+'_sd']]

diagnostics = read(RUN/'revision_diagnostics.json')
checks = read(final/'artificial_checks.json')
assert diagnostics == checks['revision_diagnostics']
assert checks['retained_initial_checks']['results'] == read(initial/'artificial_checks.json')
assert diagnostics['source_cell_reextraction']['cells'] == new
toy = pd.DataFrame({'row_id':['invented_z','invented_q','invented_n'], 'bmi':[19.2,33.7,82.0], 'age':[20,55,79], 'sex':[2,1,2]},index=[7,7,-3])
before = toy.copy(deep=True)
y = gen.generate(toy,spec,901357)
assert y.equals(oldgen.generate(toy,spec,901357))
assert toy.equals(before) and y.iloc[:,:4].equals(toy)
assert np.isfinite(y.hdl).all() and (y.hdl>0).all()

p0 = spec['parameters']
source_moments = next(e for e in ledger['evidence'] if e['id']=='E_US_MOMENTS')['reported']
gx, gw = np.polynomial.hermite.hermgauss(80)
gz, gw = np.sqrt(2)*gx, gw/np.sqrt(np.pi)

def g(age, p, factor):
    return factor * (np.interp(age,p['age_knots_years'],np.log(p['age_relative_means'])) - np.interp(p['age_reference'],p['age_knots_years'],np.log(p['age_relative_means'])))

def cell_multipliers(c, sex, p, rho, family, factor):
    # Adaptive outer integration split at transformed age knots. Independent
    # inner normal expectation for lognormal BMI; all inputs are aggregate.
    result=[]
    beta=p['bmi_log_slopes_by_sex'][sex]
    bounds=[-10] + [(a-c['age_mean'])/c['age_sd'] for a in p['age_knots_years']] + [10]
    for power in [1,2]:
        def integrand(z):
            age=c['age_mean']+c['age_sd']*z
            if family=='normal':
                eb=math.exp(power*beta*(c['bmi_mean']+rho*c['bmi_sd']*z-p['bmi_reference']) + 0.5*(power*beta*c['bmi_sd'])**2*(1-rho*rho))
            else:
                ls=math.sqrt(math.log1p((c['bmi_sd']/c['bmi_mean'])**2))
                lm=math.log(c['bmi_mean'])-ls*ls/2
                bmi=np.exp(lm+ls*(rho*z+math.sqrt(1-rho*rho)*gz))
                eb=float(np.dot(gw,np.exp(power*beta*(bmi-p['bmi_reference']))))
            return math.exp(power*g(age,p,factor)-z*z/2)/math.sqrt(2*math.pi)*eb
        result.append(sum(quad(integrand,l,h,epsabs=1e-10,epsrel=1e-10)[0] for l,h in zip(bounds[:-1],bounds[1:])))
    return result

def independent(p, rho=0, family='normal', factor=1, reanchor=True):
    result={}
    for sex in ['male','female']:
        group=new[sex]
        weights=np.array([c['n'] for c in group],float)
        weights/=weights.sum()
        ms=np.array([cell_multipliers(c,sex,p,rho,family,factor) for c in group])
        m1,m2=weights@ms
        base=p['conditional_means_at_reference_by_sex'][sex]
        sigma2=p['residual_log_sd_by_sex'][sex]**2
        if reanchor:
            base=source_moments[sex]['mean']/m1
            sigma2=math.log((source_moments[sex]['sd']**2+source_moments[sex]['mean']**2)/(base*base*m2))
        assert sigma2>0
        cell_mean=base*ms[:,0]
        cell_sd=np.sqrt(base*base*math.exp(sigma2)*ms[:,1]-cell_mean**2)
        total_var=base*base*(math.exp(sigma2)*m2-m1*m1)
        mean_var=base*base*(m2-m1*m1)
        residual=base*base*m2*math.expm1(sigma2)
        assert abs(mean_var+residual-total_var)<1e-9
        result[sex]={'base':base,'sigma':math.sqrt(sigma2),'mean':base*m1,'sd':math.sqrt(total_var),'cell_mean':cell_mean,'cell_sd':cell_sd,'mean_variance':mean_var,'residual':residual}
    return result

comparisons=[]
baseline=independent(p0,reanchor=False)
for scenario in diagnostics['closure_sensitivity']['cases']:
    result=independent(p0,scenario['dependence'],scenario['bmi_marginal'])
    max_error=0
    for sex,r in result.items():
        stored=scenario['results'][sex]
        max_error=max(max_error,float(np.max(np.abs(r['cell_mean']-[c['closure_mean'] for c in stored['cells']]))),float(np.max(np.abs(r['cell_sd']-[c['closure_sd'] for c in stored['cells']]))))
        assert abs(r['mean']-source_moments[sex]['mean'])<1e-10 and abs(r['sd']-source_moments[sex]['sd'])<1e-10
    assert max_error<0.015
    comparisons.append({'kind':'closure','family':scenario['bmi_marginal'],'dependence':scenario['dependence'],'max_cell_mean_or_sd_absolute_difference':max_error})
for kind,key in [('age','estimand_bridge_sensitivity'),('bmi','representative_bmi_sensitivity')]:
    for scenario in diagnostics[key]['cases']:
        p=copy.deepcopy(p0)
        factor=scenario['age_log_effect_multiplier'] if kind=='age' else 1
        if kind=='bmi':
            for sex in ['male','female']:
                ratio=(43.25/51.92) if sex=='male' else (51.06/60.72)
                p['bmi_log_slopes_by_sex'][sex]=math.log(ratio)/(scenario['obese_representative']-scenario['normal_representative'])
                assert abs(p['bmi_log_slopes_by_sex'][sex]-scenario['bmi_log_slopes_by_sex'][sex])<1e-15
        result=independent(p,factor=factor)
        max_error=0
        for profile in scenario['profiles']:
            sex=profile['sex']
            for axis,expected in profile['mean_by_age' if kind=='age' else 'mean_by_bmi'].items():
                bmi,age=(profile['bmi'],float(axis)) if kind=='age' else (float(axis),profile['age'])
                actual=result[sex]['base']*math.exp(p['bmi_log_slopes_by_sex'][sex]*(bmi-p['bmi_reference'])+g(age,p,factor))
                max_error=max(max_error,abs(actual-expected))
            assert abs(result[sex]['mean']-source_moments[sex]['mean'])<1e-10 and abs(result[sex]['sd']-source_moments[sex]['sd'])<1e-10
        assert max_error<0.015
        comparisons.append({'kind':kind,'scenario':factor if kind=='age' else scenario['obese_representative'],'max_profile_mean_absolute_difference':max_error})
for summary in diagnostics['source_rounding_checks']:
    group=new[summary['sex']]
    n=np.array([c['n'] for c in group])
    means=np.array([c['hdl_mean'] for c in group])
    sd=np.array([c['hdl_sd'] for c in group])
    mean=np.dot(n,means)/n.sum()
    pooled_sd=math.sqrt(np.sum((n-1)*sd**2+n*(means-mean)**2)/(n.sum()-1))
    assert abs(mean-summary['pooled_rounded_table2_mean'])<1e-12
    assert abs(pooled_sd-summary['pooled_rounded_table2_sample_sd'])<1e-12

output={'scope':'Own initial/final files, registered sources, permitted common inputs and invented profiles only. No observed rows, target data, other runs, or external retrieval. Builder revision script was read but not executed.',
        'static_check':static,'generator_and_spec_byte_identical':True,'additional_evidence_record':'E_US_CELL_MOMENTS',
        'eight_source_cells_verified_against_jats':True,'all_committed_initial_and_final_artifacts_match':verified,
        'current_common_inputs_hash_checked':common_checked,'same_run_commitment_receipts_but_not_read':receipt_only,
        'root_revision_script_absent':True,'nine_gap_dispositions_and_twelve_actions_valid':True,'registered_artifact_links_and_hashes_valid':True,
        'literature_audit_and_usage_unchanged':True,'final_invented_draws_identical_to_initial':True,
        'independent_adaptive_integration_comparisons':comparisons,'rounded_cell_pooled_moments_reproduced':True,
        'scope_note':'Current permitted common/frozen bytes match. The temporal order of the disclosed transient root-script write/move is not independently reconstructable from final files; no root revise_gap1.py remains. Observed.csv and protocol.json were not opened or hashed.',
        'hashes':{'generator_sha256':sha(final/'generator.py'),'model_spec_sha256':sha(final/'model_spec.json'),'evidence_sha256':sha(final/'evidence.json'),'candidate_freeze_sha256':sha(final/'freeze.json')}}
(RUN/'final_review_checks.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps(output,indent=2,allow_nan=False))
