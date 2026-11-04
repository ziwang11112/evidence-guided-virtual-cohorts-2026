"""Separate, transparent three-slot technical recovery release."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import shutil
import sys

R=Path(__file__).resolve().parent; U=R.parent
sys.path.insert(0,str(U.parents[1]))
from cohort_harness.lifecycle import freeze_candidate,verify_candidate

def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not (R/'RELEASE.json').exists()
    review=load(R/'INDEPENDENT_REVIEW.json');assert review['status']=='pass'
    for item in review['bindings']:
        assert sha(U/item['path'])==item['sha256'],item['path']
    repair=load(R/'REPAIR_AUDIT.json');assert repair['status']=='pass'
    old=U/'bundle/candidates/native';new=R/'native_candidate'
    verify_candidate(U/'bundle','candidates/native');verify_candidate(U/'bundle','candidates/agent')
    assert sha(old/'generator.py')==sha(new/'generator.py')
    old_p=load(old/'model_spec.json')['parameters'];new_p=load(new/'model_spec.json')['parameters']
    assert {k:v for k,v in old_p.items() if k!='hba1c'}=={k:v for k,v in new_p.items() if k!='hba1c'}
    assert old_p['hba1c']['dispersion']==new_p['hba1c']['dispersion']
    # Third reading: take only the first GLM call block, then read numeric rows.
    raw=(U/'sources/original/HRSmodels_20200902_fullDemoTable.txt').read_text(encoding='cp1252')
    block=raw.split('glm(formula = hba1c',1)[1].split('Call:',1)[0]
    expected={}
    for line in block.splitlines():
        bits=line.split()
        if bits and bits[0] in new_p['hba1c']['coefficients']:
            assert bits[0] not in expected
            expected[bits[0]]=(float(bits[1]),float(bits[2]))
    assert len(expected)==7
    for term,(estimate,se) in expected.items():
        actual=new_p['hba1c']['coefficients'][term]
        assert (actual['estimate'],actual['standard_error'])==(estimate,se)
        assert 42<=actual['source']['line_start']<=48
    (R/'ROOT_REPAIR_REVIEW.json').write_text(json.dumps({'status':'pass',
        'scope':'Independent original GLM-block reading,7 coefficient/SE pairs plus locator range; no correction parser imported.',
        'other_parameter_groups_unchanged':True,'generator_identical':True,
        'original_root_preflight':'Overturned for native source-parameter fidelity; earlier review failed to detect cross-model coefficient overwrite.',
        'model_spec_sha256':sha(new/'model_spec.json'),'generation_executed':False},indent=2)+'\n',encoding='utf-8')
    bundle=R/'bundle';candidate=bundle/'candidates/native_corrected'
    candidate.mkdir(parents=True,exist_ok=False)
    for p in new.iterdir():
        if p.is_file():shutil.copyfile(p,candidate/p.name)
    for name in ['task.json','registry.json','AUTHOR_TASK.md','SOURCE_METADATA.json']:
        shutil.copyfile(U/'bundle'/name,bundle/name)
    for item in load(bundle/'registry.json')['artifacts']:
        dest=bundle/item['path'];dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(U/'bundle'/item['path'],dest)
    freeze_candidate(bundle,'candidates/native_corrected')
    files=['PROTOCOL.md','run_recovery.py','release_recovery.py','REPAIR_AUDIT.json',
           'INDEPENDENT_REVIEW.json','ROOT_REPAIR_REVIEW.json','parse_source_corrected.py',
           'independent_source_audit.py','PARSED_SOURCE_MODELS.json',
           '../RELEASE.json','../bundle/candidates/agent/freeze.json',
           '../evaluation/native_evaluate.R','../evaluation/run_r.py','../evaluation/independent_gls.py',
           '../evaluation/runtime/RUNTIME.json','../evaluation/runtime/DEPENDENCY_DOWNLOADS.json',
           '../assemble_recovered_results.py','../summarize.py']
    files.extend(str(p.relative_to(R)).replace('\\','/') for p in bundle.rglob('*') if p.is_file())
    release={'created_utc':datetime.now(timezone.utc).isoformat(),'execution_released':True,
       'additional_attempts_allowed':3,'initial_attempts_spent':6,'maximum_total_attempts':9,
       'seeds':[6101,6102,6103],'original_release_sha256':sha(U/'RELEASE.json'),
       'correction_scope':'Only7 source-Gamma coefficient/SE pairs and source locators; no new law or Agent model revision.',
       'files':{p:sha(R/p) for p in sorted(set(files))},
       'no_further_recovery':True}
    with (R/'RELEASE.json').open('x',encoding='utf-8') as f:json.dump(release,f,indent=2);f.write('\n')
    state=load(U/'STATE.json');state.update(phase='technical_recovery_released',
       original_final_attempts_spent=6,additional_technical_attempts_allowed=3,
       original_comparator_status='invalid_source_extraction; retained',agent_status='three_frozen_successful_outputs_retained')
    (U/'STATE.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'recovery_released':True,'additional_attempts':3,'original_attempts_spent':6}))

if __name__=='__main__':main()
