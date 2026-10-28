"""Independent initial review: own evidence and invented inputs only."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import math
import sys
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

RUN = Path(__file__).resolve().parent
ROOT = RUN.parent.parent
sys.path.insert(0, str(ROOT))
import loop_control as control

candidate = RUN / 'initial'
spec = json.loads((candidate / 'model_spec.json').read_text())
ledger = json.loads((candidate / 'evidence.json').read_text())
p = spec['parameters']
tests = []

def record(name, detail):
    tests.append({'name': name, 'passed': True, 'detail': detail})

static = control.source_check(candidate / 'generator.py')
record('controller_static_check_before_import', static)
_, ids = control.validate_ledger(ledger)
control.validate_spec(spec, ids)
record('ledger_and_parameter_provenance_validation', {'parameters': len(p), 'evidence': len(ids)})

# Restrict verification to this version's candidate/evidence commitment,
# never the broader run commitment that contains the observed CSV.
freeze = json.loads((candidate / 'freeze.json').read_text())
for name, expected in freeze['commitment'].items():
    path = Path(name)
    assert path.is_relative_to(RUN)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
events = [json.loads(line) for line in (RUN / 'literature' / 'audit.jsonl').read_text().splitlines()]
registered = {(e['artifact']['session_relative_path'], e['artifact']['sha256']) for e in events
              if e.get('type') == 'artifact_approved' and e.get('status') == 'accepted'}
for source in ledger['sources']:
    for artifact in source['approved_artifacts']:
        relative = artifact['path'].removeprefix('literature/')
        assert (relative, artifact['sha256']) in registered
record('frozen_candidate_and_approved_artifact_hashes', {'candidate_commitments_verified': len(freeze['commitment']), 'registered_ledger_artifacts': sum(len(s['approved_artifacts']) for s in ledger['sources'])})

xml_file = RUN / 'literature' / 'approved' / '23728f05bcc689d1e4d9549f25d163243c4dd6b3a174225f34a7758c1514eaa8.xml'
root = ET.fromstring(xml_file.read_bytes())
def rows(table_id):
    table = root.find(".//table-wrap[@id='" + table_id + "']")
    return [[''.join(cell.itertext()).strip() for cell in row if cell.tag in ('td', 'th')] for row in table.findall('.//tr')]
t2 = rows('genes-10-00440-t002')
for source_label, model_label in [('Men', 'male'), ('Women', 'female')]:
    row = next(row for row in t2 if row[0] == source_label)
    assert [int(row[i]) for i in (1, 3, 5, 7)] == p['source_cell_counts'][model_label]
    pairs = [[float(x.strip()) for x in row[i].split('\u00b1')] for i in (2, 4, 6, 8)]
    assert [pair[0] for pair in pairs] == p['source_hdl_means'][model_label]
    assert [pair[1] for pair in pairs] == p['source_mean_standard_errors'][model_label]
age_rows = [next(row for row in t2 if row[0] == label) for label in ['30\u201340', '40\u201350', '51\u201360', '61\u201370']]
assert [[int(row[i]) for row in age_rows] for i in (1, 3, 5, 7)] == p['source_age_counts_by_bmi']
t3 = rows('genes-10-00440-t003')
assert [0] + [float(next(row for row in t3 if row[0] == label)[1]) for label in ['40\u201350', '51\u201360', '61\u201370']] == p['age_contrasts']
assert sum(p['source_cell_counts']['male']) == 6184
assert sum(p['source_cell_counts']['female']) == 8353
assert np.array_equal(np.array(p['source_age_counts_by_bmi']).sum(axis=1), np.array(p['source_cell_counts']['male']) + p['source_cell_counts']['female'])
record('direct_XML_source_extraction_and_margins', {'tables': ['G2019 Table 2 sex and age rows', 'G2019 Table 3 age rows'], 'all_exact': True})

state = np.random.get_state()
module_spec = importlib.util.spec_from_file_location('reviewed_ordinary_1_initial', candidate / 'generator.py')
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)
assert control.rng_equal(state, np.random.get_state())
contract = json.loads((ROOT / 'runner_contract.json').read_text())
base = pd.DataFrame({'row_id': ['z', 'a', 'x', 'c', 'q', 'b'], 'bmi': [13.0, 17.0, 25.5, 30.5, 50.0, 80.0],
                     'age': [20, 35, 46, 55, 65, 79], 'sex': [2, 1, 2, 1, 1, 2]}, index=[40, 4, 9, 8, 1, 12])
old = base.copy(deep=True)
settings = copy.deepcopy(spec)
out = module.generate(base, settings, 80317)
control.output_check(base.reset_index(drop=True), out.reset_index(drop=True), contract)
pd.testing.assert_frame_equal(base, old, check_exact=True)
assert out.index.equals(base.index)
assert settings == spec
assert control.rng_equal(state, np.random.get_state())
pd.testing.assert_frame_equal(out, module.generate(base, spec, 80317), check_exact=True)
assert not np.array_equal(out.hdl, module.generate(base, spec, 80318).hdl)
record('contract_mutation_index_and_rng_checks', {'invented_rows': 6, 'seeds': [80317, 80318], 'input_spec_and_global_rng_unchanged': True, 'same_seed_exact': True})

empty = base.iloc[0:0].copy()
assert list(module.generate(empty, spec, 80317).columns) == ['row_id', 'bmi', 'age', 'sex', 'hdl']
for column, value in [('bmi', 0), ('bmi', float('nan')), ('age', float('inf')), ('sex', 3)]:
    bad = base.copy(deep=True)
    if column in ('bmi', 'age'):
        bad[column] = bad[column].astype(float)
    bad.loc[bad.index[0], column] = value
    try:
        module.generate(bad, spec, 1)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid input not rejected: ' + column)
record('empty_and_invalid_input_cases', {'empty_passes': True, 'rejected': ['zero BMI', 'NaN BMI', 'infinite age', 'sex 3']})

def lerp(value, knots, vals):
    if value <= knots[0]:
        return vals[0]
    for j in range(1, len(knots)):
        if value <= knots[j]:
            return vals[j-1] + (vals[j]-vals[j-1]) * (value-knots[j-1]) / (knots[j]-knots[j-1])
    return vals[-1]

def reference(bmi, age, sex):
    label = 'male' if sex == 1 else 'female'
    centers = [sum(n*a for n, a in zip(counts, p['age_contrasts'])) / sum(counts) for counts in p['source_age_counts_by_bmi']]
    means = [m-c for m,c in zip(p['source_hdl_means'][label], centers)]
    mu = lerp(bmi, p['bmi_knots'], means) + lerp(age, p['age_knots'], p['age_contrasts'])
    mu *= math.exp(p['tail_log_slopes'][label] * max(0, bmi-p['bmi_knots'][-1]))
    variances = [math.log(1 + se*se*n/(mean*mean)) for se,n,mean in zip(p['source_mean_standard_errors'][label], p['source_cell_counts'][label], p['source_hdl_means'][label])]
    lv = lerp(bmi, p['bmi_knots'], variances)
    return mu, lv

grid_rows = [(b, a, s) for b in [13,17,18.5,21.25,24,25.5,27,30.5,45,80] for a in [20,35,45,55.5,65.5,79] for s in [1,2]]
grid = pd.DataFrame(grid_rows, columns=['bmi','age','sex'])
grid.insert(0, 'row_id', ['invented_'+str(i) for i in range(len(grid))])
grid_out = module.generate(grid, spec, 80319)
z = np.random.default_rng(80319).standard_normal(len(grid))
expected = np.array([math.exp(math.log(reference(b,a,s)[0])-reference(b,a,s)[1]/2 + math.sqrt(reference(b,a,s)[1])*zz) for (b,a,s),zz in zip(grid_rows,z)])
np.testing.assert_allclose(grid_out.hdl, expected, rtol=3e-14, atol=0)
control.output_check(grid, grid_out, contract)
record('independent_scalar_reference_on_invented_grid', {'rows': len(grid), 'bmi_range': [13,80], 'age_range': [20,79], 'max_relative_error': float(np.max(abs(grid_out.hdl/expected-1)))})

moments=[]
for index,(b,a,s) in enumerate([(17,35,1),(21.25,45,2),(25.5,55.5,1),(30.5,65.5,2),(45,20,1),(80,79,2)]):
    n = 120000
    sample = pd.DataFrame({'row_id': np.arange(n).astype(str), 'bmi': float(b), 'age': float(a), 'sex': s})
    y=module.generate(sample,spec,91000+index).hdl.to_numpy()
    mu,lv=reference(b,a,s)
    sd=mu*math.sqrt(math.expm1(lv))
    standardized_mean=(float(y.mean())-mu)/(sd/math.sqrt(n))
    sd_relative_error=float(y.std(ddof=1))/sd-1
    assert abs(standardized_mean)<6
    assert abs(sd_relative_error)<0.025
    moments.append({'bmi':b,'age':a,'sex':s,'n':n,'mean_MC_SE':standardized_mean,'SD_relative_error':sd_relative_error})
record('conditional_arithmetic_moments_on_replicated_invented_inputs', {'tolerances': 'Mean within 6 MC standard errors; SD within 2.5%; distribution arithmetic only', 'cells': moments})

derived={label:[se*math.sqrt(n) for se,n in zip(p['source_mean_standard_errors'][label],p['source_cell_counts'][label])] for label in ['male','female']}
max_center_error=0.0
for sex,label in [(1,'male'),(2,'female')]:
    for j,b in enumerate(p['bmi_knots']):
        counts=p['source_age_counts_by_bmi'][j]
        integrated=sum(n*reference(b,a,sex)[0] for n,a in zip(counts,p['age_knots']))/sum(counts)
        max_center_error=max(max_center_error,abs(integrated-p['source_hdl_means'][label][j]))
assert max_center_error<1e-12
record('SEM_to_SD_and_declared_discrete_age_centering', {'source_broad_cell_SD':derived,'max_source_anchor_identity_error':max_center_error,'qualification':'Identity holds for assumed common discrete source age representatives; not evidence of exact conditional means or SDs.'})

tail={label:math.exp(p['tail_log_slopes'][label]*(80-30.5)) for label in ['male','female']}
record('quantified_invented_tail_vs_flat_sensitivity', {'BMI':80,'selected_mean_divided_by_flat_mean':tail,'qualification':'This checks consequences of the submitted tail bridge; no preferred target value or slope is asserted.'})
assert control.rng_equal(state, np.random.get_state())

report={'scope':'Own approved evidence and invented inputs only; no observed participant CSVs or outcomes, other runs, target results or external retrieval.',
        'all_passed':True,'tests':tests}
(RUN/'initial_review_checks.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps(report,indent=2,allow_nan=False))
