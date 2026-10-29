"""Freeze the one permitted final round; no generator/source execution."""
from pathlib import Path
import hashlib
import json
import sys

P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[2]))
from cohort_harness.lifecycle import freeze_candidate,verify_candidate
from cohort_harness.source_replay import _plan
from cohort_harness.__main__ import validate_bundle

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,obj): Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')

review={'scope':'independent_final_static_audit','blocking_findings':[],
 'checks':['s1 pooled-slope algebra and residual CV values independently verified.','Mean-one lognormal centering preserves conditional arithmetic mean.','Observed row copy, sex indexing and assay routing are correct.','s2/s3 code and specification bytes equal their initial parents.','Common evidence/replay/contexts/shared source assumptions unchanged across all six candidates.','All bound check hashes match and copied feedback bytes equal admitted originals.'],
 'generator_executed':False,'source_replay_executed':False,
 'limits':'Positive-mean regularization and approximate source covariates limit exact source moment preservation; numerical compatibility and transport are not established.'}
for sid in ['s1','s2','s3']:
    c=P/'candidates'/(sid+'_final')
    assert not (c/'freeze.json').exists()
    write(c/'reviewf.json',review)
    checks=read(c/'checks.json')
    checks['records'].append({'name':'independent_final_static_audit','status':'pass','detail':'Source-only static audit found no blocking issue; exact s1 variance/slope algebra and all binding/preservation statements verified without generator execution.'})
    checks['artifacts'].append({'path':'reviewf.json','sha256':sha(c/'reviewf.json')})
    write(c/'checks.json',checks)
    assert validate_bundle(P,c)['generator_executed'] is False

ready={'kind':'final_source_only_freeze_readiness','revision_plan_sha256':sha(P/'REVISION_PLAN.json'),
       'initial_structure_plan_sha256':sha(P/'STRUCTURE_PLAN.json'),'generator_executed_by_builder':False,
       'source_replay_executed_by_builder':False,'target_feedback_available_to_builder':False,
       'decisions':{'s1':'revise','s2':'retain_with_unresolved_source_mismatch','s3':'retain_source_challenged_sensitivity'},'candidates':{}}
for sid in ['s1','s2','s3']:
    c=P/'candidates'/(sid+'_final')
    parent=P/'candidates'/(sid+'_initial')
    frozen=freeze_candidate(P,c,parent_receipt=parent/'freeze.json',revision=read(c/'revision.json'))
    assert frozen==verify_candidate(P,c)
    assert frozen['revision_index']==1
    _,contexts,_,_=_plan(P,c,20_000_000)
    ready['candidates'][sid+'_final']={'freeze_sha256':sha(c/'freeze.json'),'parent_freeze_sha256':sha(parent/'freeze.json'),
         'generator_sha256':sha(c/'generator.py'),'model_spec_sha256':sha(c/'model_spec.json'),
         'evidence_sha256':sha(c/'evidence.json'),'source_replay_sha256':sha(c/'source_replay.json'),
         'static_replay_context_count':len(contexts),'revision_index':frozen['revision_index'],'acceptance':frozen['acceptance']}
write(P/'FINAL_READY.json',ready)
print(json.dumps(ready,indent=2))
