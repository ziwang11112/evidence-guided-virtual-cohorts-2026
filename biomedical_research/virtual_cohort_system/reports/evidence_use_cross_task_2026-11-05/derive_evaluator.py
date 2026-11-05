"""Additive evaluator derivative; reference parsing remains behind full closure."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parent
source=ROOT.parent/'core_workflow_replication_2026-11-04/evaluator_v2.py'
raw=source.read_bytes()
text=raw.decode('utf-8-sig').replace('\r\n','\n')
adapter='''def load_references(protocol, schema):
    """Called only after full author closure. Never load participant records."""
    refs = {}
    for case, spec in protocol['references'].items():
        runner.verify_bound(spec)
        record = runner.READ(spec['path'])
        for key in spec['selector']: record = record[key]
        if case == 'ENSANUT2018':
            refs[case] = record
            continue
        out = {}
        for endpoint in schema[case]['analyses']:
            value = record['estimands'][endpoint['id']]
            runner.require(value['unit'] == endpoint['unit'], 'Lipid reference unit mismatch')
            out[endpoint['id']] = {'unit':value['unit'], 'value':value['estimate'],
                'status':value['status'], 'interval':value['interval'],
                'scope':'Existing exposed selected sample; identical K02 estimator'}
        for endpoint in schema[case]['diagnostics']:
            value = None
            for col in ('total_cholesterol', 'hdl_cholesterol'):
                if endpoint['id'] == col+'.sd_sample':
                    value = record['metric_denominators'][col]['sample_sd']
            out[endpoint['id']] = {'unit':endpoint['unit'], 'value':value,
                'status':'computed' if finite(value) else 'unavailable',
                'scope':'Existing sample ddof=1 SD' if finite(value) else 'Not present in pinned aggregate; generated diagnostic only'}
        refs[case] = out
    return refs

'''
changes=[
('all-four closure gate','all-six closure gate'),
('    correction=runner.READ(ROOT/\'EVALUATOR_V2_CORRECTION.json\')\n    for artifact in correction[\'bindings\']:runner.verify_bound(artifact)\n',''),
("    refinfo=protocol['reference']\n    runner.verify_bound(refinfo)\n    refs=runner.READ(refinfo['path'])['references']\n    schema=runner.READ(ROOT/'ENDPOINT_CONTRACT.json')['cases']",
 "    schema=runner.READ(ROOT/'ENDPOINT_CONTRACT.json')['cases']\n    refs=load_references(protocol,schema)\n    refhashes={case:r['sha256'] for case,r in protocol['references'].items()}"),
("dest=ROOT/'evaluation_v2'", "dest=ROOT/'evaluation'"),
("'reference_sha256':refinfo['sha256']", "'reference_sha256':refhashes"),
("runner.closure_gate();runner.verify_bound(refinfo)", "runner.closure_gate()\n        for refinfo in protocol['references'].values(): runner.verify_bound(refinfo)"),
("'schema_version':'core_workflow_replication_results_v2_numeric_scalar_correction','correction_manifest_sha256':runner.SHA(ROOT/'EVALUATOR_V2_CORRECTION.json')", "'schema_version':'evidence_use_cross_task_results_v1'"),
("'scheduled_authors':4", "'scheduled_authors':6"),
("'scheduled_final_slots':12", "'scheduled_final_slots':18"),
('Open author-selected PMC/EuropePMC evidence under fixed budgets;',
 'Curated external evidence plus optional gap-directed PMC/EuropePMC acquisition; six fresh constructions and eighteen scheduled delivery slots;')
]
for before,after in changes:
    count=text.count(before)
    if count < 1 or (count > 1 and before != "'reference_sha256':refinfo['sha256']"):
        raise RuntimeError('Unexpected replacement count: '+before)
    text=text.replace(before,after)
text=text.replace('def evaluate():', adapter+'def evaluate():')
with (ROOT/'evaluator.py').open('x',encoding='utf-8',newline='\n') as f:f.write(text)
with (ROOT/'EVALUATOR_DERIVATION.json').open('x',encoding='utf-8') as f:
    json.dump({'source':str(source),'source_sha256':hashlib.sha256(raw).hexdigest(),
        'destination_sha256':hashlib.sha256((ROOT/'evaluator.py').read_bytes()).hexdigest(),
        'changes':changes,'new_adapter':adapter},f,indent=2)
