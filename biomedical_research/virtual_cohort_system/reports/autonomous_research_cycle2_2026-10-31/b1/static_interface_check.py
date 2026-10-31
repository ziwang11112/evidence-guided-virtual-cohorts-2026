"""Static contract validation only: no generator or bridge imports/execution."""
import copy
import hashlib
import json
import sys
from pathlib import Path

B=Path(__file__).resolve().parent
C=B/'candidates/initial'
PROJECT=Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system')
sys.path.insert(0,str(PROJECT))
from cohort_harness.contracts import validate_task,validate_evidence,validate_spec,exact_keys
from cohort_harness.source_replay import _check_metadata
from cohort_harness.source_replay_v2 import _operator_preflight

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

task=read(B/'task.json')
spec=read(C/'model_spec.json')
evidence=read(C/'evidence.json')
panel=read(B/'SOURCE_PANEL_SPEC.json')
plan=read(C/'source_context_plan.json')
validate_task(task)
validate_spec(spec,validate_evidence(evidence,task))
known={a['id'] for a in spec['assumptions']}
items={i['id']:i for i in evidence['items']}
domains=plan['model_domain']['columns']
domain_task=copy.deepcopy(task)
domain_task['columns']=domains
validate_task(domain_task)
assert set(plan['model_domain']['assumption_ids'])<=known
assert len(plan['contexts'])==2
check_count=0
for name,descriptor in spec['parameters']['contexts'].items():
    exact_keys(descriptor,{'population','n_rows','columns','inputs'},where='context descriptor')
    derived=copy.deepcopy(task)
    derived.update({key:descriptor[key] for key in ('population','n_rows','columns')})
    validate_task(derived)
    for col,parent_col,domain in zip(derived['columns'],task['columns'],domains):
        immutable=lambda x:{k:v for k,v in x.items() if k not in ('minimum','maximum')}
        assert immutable(col)==immutable(parent_col)==immutable(domain)
        for bound in ('minimum','maximum'):
            if bound in domain:
                assert bound in col
                assert col[bound]>=domain[bound] if bound=='minimum' else col[bound]<=domain[bound]
    if name=='target':
        assert derived==task
    else:
        assert derived==read(C/f'source_contexts/{name}/task.json')
        assert derived['n_rows']==6000
        recipe=read(C/f'source_contexts/{name}/whole_cohort_feedback.json')
        exact_keys(recipe,{'schema_version','population','measurement','assumption_ids','checks'},where='feedback')
        assert recipe['schema_version']==1 and recipe['population']==derived['population']
        assert recipe['measurement']['mode']=='identity'
        assert set(plan['model_domain']['assumption_ids'])<=set(recipe['assumption_ids'])<=known
        fixed=next(x for x in panel['contexts'] if x['id']==name)['checks']
        assert len(fixed)==len(recipe['checks'])
        for original,check in zip(fixed,recipe['checks']):
            assert (check['id'],check['evidence_id'],check['operator'])==(original['id'],original['evidence_id'],original['operator'])
            _check_metadata(check,items,known,recipe['assumption_ids'])
            _operator_preflight(check['operator'],derived)
            check_count+=1
assert check_count==20
receipt={'status':'pass','scope':'static contracts, source recipe metadata and operator syntax',
         'source_contexts':2,'exact_fixed_checks':check_count,'generator_imported':False,
         'generator_called':False,'bridge_imported_or_called':False,'individual_rows_generated':0,
         'checks':['parent task and model contracts','all context descriptors and common domain bounds',
                   'source tasks differ only by population/count/numeric bounds',
                   'all20 fixed metadata/operator identities','shared API metadata/operator preflight'],
         'scientific_validity':'not_assessed','numerical_source_validation':'not_performed'}
path=C/'static_interface_audit.json'
path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
checks=read(C/'checks.json')
checks['records'].append({'name':'source_context_static_interface','status':'pass',
                        'detail':'Actual static descriptor/domain/task invariants and shared source metadata/operator validation recorded in static_interface_audit.json; no bridge or generator execution.'})
checks['artifacts'].append({'path':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(C/'checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
