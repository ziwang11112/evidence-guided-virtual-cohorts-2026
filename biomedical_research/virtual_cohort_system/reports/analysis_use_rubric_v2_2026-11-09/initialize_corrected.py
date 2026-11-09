"""Preserve failed zero-action setup and prepare a new provenance-corrected setup.

No generator executions, statistical changes, target access, or network calls.
"""
from pathlib import Path
import hashlib
import json
import shutil
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORKSPACE = PROJECT.parents[1]
PREVIOUS = PROJECT / 'work/analysis_use_rubric_2026-11-09'
FAILED = WORKSPACE / 'evcUseR01'
NEW = WORKSPACE / 'evcUseR02'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write('\n')

def main():
    if NEW.exists(): raise ValueError('New bundle already exists; no reset')
    events = list((FAILED/'adaptive_session_v2/events').glob('*'))
    executions = list((FAILED/'executions').glob('*/execution.json'))
    freezes = list((FAILED/'candidates').glob('*/freeze.json'))
    if events or executions or freezes: raise ValueError('Not an unused setup')
    failure = {'status':'setup_failed_before_controller_actions', 'bundle':str(FAILED),
               'reason':'Inherited sources/web_evidence_v1 entries were incorrectly copied into a fresh web session without its bound approvals.',
               'actions':0, 'executions':0, 'freezes':0,
               'files':{p.relative_to(FAILED).as_posix():sha(p) for p in FAILED.rglob('*') if p.is_file()},
               'resolution':'Preserve failed bundle. Curate inherited web artifacts under a distinct namespace in a fresh setup; no invented retrievals or approvals; no scientific-law change.'}
    write(PREVIOUS/'SETUP_FAILURE.json', failure)
    for name in ('evaluate.py','close_author.py','independent_recompute.py','generated_analysis.py',
                 'analysis_use_adapter.py','test_evaluate.py','test_adapter_integration.py','RULE_BASIS.json','RULE_BASIS.md'):
        shutil.copyfile(PREVIOUS/name, HERE/name)
    code = (PREVIOUS/'prepare.py').read_text(encoding='utf8')
    code = code.replace("bundle = WORKSPACE/'evcUseR01'", "bundle = WORKSPACE/'evcUseR02'")
    code = code.replace("dest=bundle/item['path'];", "relative=item['path'].replace('sources/web_evidence_v1/','sources/curated/inherited_web_v1/')\n        dest=bundle/relative;")
    code = code.replace("registry.append({**item,'origin':'curator'})", "registry.append({**item,'path':relative,'origin':'curator'})")
    code = code.replace("'path':item['path'],'sha256':item['sha256'],'previous_origin'", "'path':relative,'original_path':item['path'],'sha256':item['sha256'],'previous_origin'")
    insertion = '''    original_baseline=dict(baseline)
    evidence_path=dest/'evidence.json'
    evidence=read(evidence_path)
    for source_item in evidence['sources']:
        for artifact in source_item['artifacts']:
            artifact['path']=artifact['path'].replace('sources/web_evidence_v1/','sources/curated/inherited_web_v1/')
    evidence_path.write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+'\\n',encoding='utf8')
    baseline['evidence.json']=sha(evidence_path)
    for name in ('source_semantics_v1.json','descriptive_feedback_v1.json'):
        declaration=read(dest/name)
        if declaration['evidence_sha256']!=original_baseline['evidence.json']:raise ValueError('Original binding mismatch')
        declaration['evidence_sha256']=baseline['evidence.json']
        (dest/name).write_text(json.dumps(declaration,indent=2,ensure_ascii=False)+'\\n',encoding='utf8')
        baseline[name]=sha(dest/name)
    write(bundle/'input/provenance_only_rebinding.json',{'original_files':original_baseline,'current_files':baseline,
        'path_mapping':{'sources/web_evidence_v1/':'sources/curated/inherited_web_v1/'},
        'changes':'evidence artifact locations and two evidence hash bindings only; scientific values, law and assumptions unchanged; source bytes unchanged; historical manifests remain original provenance, not new-session approvals.'})
'''
    needle="    write(bundle/'input/baseline_commitments.json'"
    code = code.replace(needle, insertion + needle)
    code = code.replace('Original scientific law and source declarations, no old outcomes or reference results.',
        'Original scientific law and source statistics, with provenance-only artifact-path and evidence-hash rebinding documented separately; no old outcomes or reference results.')
    (HERE/'prepare.py').write_text(code, encoding='utf8')
    sys.path.insert(0, str(HERE))
    import prepare
    prepare.main()
    task = (FAILED/'AUTHOR_TASK.md').read_text(encoding='utf8')
    task = task.replace('The nine copied files in candidates/baseline are committed',
        'The nine baseline files (six byte-identical to their source; evidence.json and two hash-bound declarations changed only for inherited-source paths/bindings, see input/provenance_only_rebinding.json) are committed')
    task = task.replace('Keep every copied file byte-for-byte unchanged.', 'Keep all nine current committed files byte-for-byte unchanged.')
    (NEW/'AUTHOR_TASK.md').write_text(task,encoding='utf8')
    config = read(PREVIOUS/'SESSION_CONFIG.json')
    def rebase(value):
        if isinstance(value,str): return value.replace(str(PREVIOUS),str(HERE)).replace(str(FAILED),str(NEW))
        if isinstance(value,list): return [rebase(x) for x in value]
        if isinstance(value,dict): return {rebase(k):rebase(v) for k,v in value.items()}
        return value
    write(HERE/'SESSION_CONFIG.json',rebase(config))
    write(HERE/'SETUP_CORRECTION.json',{'failed_setup':str(PREVIOUS),'failed_bundle':str(FAILED),
        'failure_receipt_sha256':sha(PREVIOUS/'SETUP_FAILURE.json'),'new_bundle':str(NEW),
        'new_experiment':False,'scientific_budget_reset':False,'previous_actions':0,'previous_executions':0,
        'source_bytes_changed':False,'generator_changed':False,'model_spec_changed':False,
        'reason':'Namespace denotes fresh web-session approved downloads; inherited sources must be honest curator inputs with separate historical provenance.',
        'engines_changed':False,'target_access':False})
    print(json.dumps({'prepared':str(NEW),'source_count':len(read(NEW/'registry.json')['artifacts'])}))

if __name__=='__main__':main()
