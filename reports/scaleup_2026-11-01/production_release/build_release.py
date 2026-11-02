"""Prepare a concrete reviewable release; never approve it or start construction."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
SCALE=HERE.parent
PROJECT=SCALE.parents[1]
WORKSPACE=PROJECT.parents[1]
INTEGRATION=SCALE/'production_integration'
for folder in (PROJECT,INTEGRATION,INTEGRATION/'campaign_control',HERE/'evaluation',HERE/'runtime'):
    sys.path.insert(0,str(folder))
import bundle_assembly as assembly
import campaign_control as control
import evaluate_campaign as evaluation
import runtime_check

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write_new(path,obj):
    with Path(path).open('x',encoding='utf-8',newline='\n') as handle:
        json.dump(obj,handle,indent=2,ensure_ascii=False,allow_nan=False);handle.write('\n')

def build():
    runtime_check.verify()
    for case in ('K01','K02'):
        assembly.verify_design(case)
    files=set()
    def add(path,expected=None):
        path=Path(path).resolve()
        if path.suffix.lower() not in {'.py','.json','.md','.txt'} or any(p.lower() in {'private_data','private_sources','private_documents'} for p in path.parts):
            raise ValueError('Forbidden release artifact: '+str(path))
        if expected is not None and sha(path)!=expected:
            raise ValueError('Frozen artifact differs: '+str(path))
        if not path.is_file():raise FileNotFoundError(path)
        files.add(path)
    for case,name in (('case_k01','REVIEWED_DESIGN_COMMITMENT.json'),('case_k02','REVIEWED_DESIGN_SNAPSHOT.json')):
        artifact=SCALE/case/name
        add(artifact)
        document=read(artifact)
        for name,expected in document['files'].items():add(SCALE/case/name,expected)
        for name,expected in document.get('read_only_dependencies',{}).items():add(PROJECT/name,expected)
    committed=INTEGRATION/'K02_SCIENTIFIC_COMMITMENT.json'
    add(committed)
    for name,expected in read(committed)['files_relative_to_scaleup'].items():add(SCALE/name,expected)
    integration=INTEGRATION/'INTEGRATION_COMMITMENT.json'
    add(integration)
    # Enumerate the actual trusted production import closure, not submitted scientific code.
    for path in (PROJECT/'cohort_harness').glob('*.py'):add(path)
    for directory in ('operators','bridge','bridge_units','production_integration','production_integration/k01_sources','production_integration/campaign_control'):
        for path in (SCALE/directory).glob('*.py'):
            if not path.name.startswith(('test_','export_','prepare_execution','prepare_inputs')):add(path)
    for name in ('INLINE_DERIVATION_ADDENDUM.md','INDEPENDENT_REVIEW.md','EXECUTION_INPUT_LOCATIONS.json'):
        add(INTEGRATION/name)
    for name in ('evaluation/evaluate_campaign.py','evaluation/EVALUATION_MANIFEST.json',
                 'submission/submission.py','runtime/runtime_check.py','runtime/RUNTIME_IDENTITY.json',
                 'runtime/DOWNLOAD_RECEIPT.json','runtime/SCIPY_INSTALL_REPORT.json','build_release.py',
                 'run_stage.py','INDEPENDENT_REVIEW.md'):
        add(HERE/name)
    for name in evaluation.DEPENDENCIES:add(SCALE/name)
    em=read(HERE/'evaluation/EVALUATION_MANIFEST.json')
    if em!=evaluation.prepare_evaluation_manifest(em['output_directory']):raise ValueError('Evaluation metadata changed')
    cases={}
    for case in ('K01','K02'):
        root=SCALE/('case_'+case.lower())
        paths={'scientific_commitment_sha256':root/'REVIEWED_DESIGN_COMMITMENT.json' if case=='K01' else INTEGRATION/'K02_SCIENTIFIC_COMMITMENT.json',
               'constructor_packet_sha256':root/'request'/('packet_manifest.json' if case=='K01' else 'manifest.json'),
               'task_template_sha256':root/'request/task_template.json',
               'budget_contract_sha256':root/'statistical_reference_and_budget_proposal.json'}
        for path in paths.values():add(path)
        cases[case]={name:sha(path) for name,path in paths.items()}
    evaluator=(HERE/'evaluation/evaluate_campaign.py').resolve()
    result={'schema_version':1,'kind':'wave_a_global_clinical_release',
        'campaign_id':'biomedical_scaleup_2026-11-01_wave_a','status':'released',
        'released_utc':datetime.now(timezone.utc).isoformat(),
        'ledger_directory':str((WORKSPACE/'evcA/ledger').resolve()),
        'designated_evaluator':{'path':str(evaluator),'sha256':sha(evaluator)},
        'schedule_sha256':control.digest(control.fixed_schedule()),'cases':cases,
        'artifacts':[{'path':str(path),'sha256':sha(path)} for path in sorted(files)]}
    write_new(HERE/'RELEASE_FOR_REVIEW.json',result)
    print(json.dumps({'status':'awaiting_independent_release_review','artifacts':len(files),
        'approved_sha256_required':control.release_digest(result),'ledger_created':False}))
    return result

if __name__=='__main__':build()
