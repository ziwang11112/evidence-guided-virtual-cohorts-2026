"""Verify visible preparation and source bindings without loading hidden data."""
from pathlib import Path
import hashlib
import json
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parents[1]))
from cohort_harness.contracts import validate_task,validate_input,validate_evidence
from cohort_harness.lifecycle import _registry
from analytical_points import normalize_visible


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    findings=[]; cases=[]
    for case in ['nhanes_insulin','pns_hba1c']:
        bundle=ROOT/'bundles'/case
        task=json.loads((bundle/'task.json').read_text(encoding='utf-8'))
        evidence=json.loads((bundle/'admitted_evidence.json').read_text(encoding='utf-8'))
        observed=pd.read_csv(bundle/'observed.csv',dtype={task['row_id']:'string'})
        validate_task(task);validate_input(observed,task);validate_evidence(evidence,task)
        normalized=normalize_visible(observed,case)
        assert len(normalized)==task['n_rows']
        assert sha(bundle/'observed.csv')==sha(ROOT/case/'visible/observed.csv')
        assert sha(bundle/'task.json')==sha(ROOT/case/'task.json')
        manifest=json.loads((bundle/'input_manifest.json').read_text(encoding='utf-8'))
        assert {p.relative_to(bundle).as_posix() for p in bundle.rglob('*') if p.is_file()}==set(manifest['files'])|{'input_manifest.json'}
        for name,h in manifest['files'].items(): assert sha(bundle/name)==h,name
        _registry(bundle)
        forbidden_parts={'custodian','raw','reference.csv','design_weights.csv','id_mapping.csv'}
        assert not any(set(p.relative_to(bundle).parts)&forbidden_parts for p in bundle.rglob('*'))
        cases.append({'case':case,'n_rows':task['n_rows'],'visible_schema_pass':True,'source_registry_pass':True,
                      'source_items':len(evidence['items']),'no_reference_files_in_bundle':True,
                      'input_manifest_sha256':sha(bundle/'input_manifest.json')})
    files={}
    for subdir in ['methods','protocols','prompts']:
        for p in sorted((ROOT/subdir).glob('*')):
            if p.is_file() and p.suffix in {'.py','.json','.md'}:files[p.relative_to(ROOT).as_posix()]=sha(p)
    report={'status':'preparation_verified_not_generation_validated','cases':cases,'findings':findings,
            'target_reference_rows_loaded':False,'scientific_generator_executed':False,'target_analysis_executed':False,
            'prototype_point_estimator':'invented-fixture validation only; survey inference is a separate pending adapter',
            'snapshot_files':files,
            'remaining_before_campaign':['predeclare conventional generator family from admitted evidence',
                 'bind model identity and feasible resource accounting', 'bind isolated execution runtime',
                 'review NHANES full-design variance adapter before any reference inference'],
            'boundary':'Procedural Agent custody; generator sandbox only, no OS isolation of all LLM tools'}
    (ROOT/'preparation_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['status','cases','findings','target_analysis_executed']}))


if __name__=='__main__':main()
