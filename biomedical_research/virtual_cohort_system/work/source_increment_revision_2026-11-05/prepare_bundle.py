"""Prepare a new read-only-source bundle only after scientific proposal review."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
WORKSPACE = PROJECT.parent.parent
OLD = WORKSPACE / 'evcRepE01'
NEW = WORKSPACE / 'evcIncE01'
PROBE = PROJECT / 'work/supplement_probe_2026-11-05'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    proposal = json.loads((ROOT / 'PROPOSAL.json').read_text(encoding='utf-8'))
    # Reviewer uses an explicit separate root gate; this script chooses no science.
    gate = json.loads((ROOT / 'IMPLEMENTATION_GATE.json').read_text(encoding='utf-8'))
    assert gate['decision'] == 'implement_source_only_reviewed_proposal'
    assert gate['proposal_sha256'] == sha(ROOT / 'PROPOSAL.json')
    assert gate['review_sha256'] == sha(ROOT / 'REVIEW.json')
    assert not NEW.exists(), 'New bundle already exists; inspect it, do not reset.'
    manifest = json.loads((ROOT / 'INPUT_MANIFEST.json').read_text(encoding='utf-8'))
    for path, h in manifest['files'].items():
        assert sha(Path(path)) == h, 'Admitted input changed'
    NEW.mkdir()
    registry = json.loads((OLD / 'registry.json').read_text(encoding='utf-8'))
    for entry in registry['artifacts']:
        src, dst = OLD / entry['path'], NEW / entry['path']
        assert sha(src) == entry['sha256']
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    supplement_map = {}
    for name in ['VISIBLE_TEXT.txt', 'TABLES.json', 'PDF_TEXT.txt']:
        src = PROBE / 'local_converted' / name
        h = sha(src)
        rel = 'sources/supplement/' + h + src.suffix
        dst = NEW / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        registry['artifacts'].append({'source_id':'PMC6458679', 'path':rel, 'sha256':h,
                                     'origin':'curator','screening':'approved'})
        supplement_map[name] = {'path':rel,'sha256':h}
    task = json.loads((OLD / 'task.json').read_text(encoding='utf-8'))
    task['task_id'] = 'source-increment-development-2026-11-05-E01'
    # Administrative immutable repair lineage only; protocol still permits one scientific law.
    task['budget'] = {'source_queries':0,'source_downloads':0,'revisions':2}
    task['information_policy']['allowed_tools'] = ['admitted_source_read','contract_validation',
                                                  'controller_source_feedback','retained_analytic_calculation']
    (NEW / 'task.json').write_text(json.dumps(task,indent=2)+'\n',encoding='utf-8')
    (NEW / 'registry.json').write_text(json.dumps(registry,indent=2)+'\n',encoding='utf-8')
    shutil.copyfile(OLD/'request.json',NEW/'request.json')
    (NEW/'candidates/source_increment').mkdir(parents=True)
    admission = {'source_map':supplement_map,'scope':'Same scientific request; new development bundle. No old source-session reset.',
                 'original_registry_sha256':sha(OLD/'registry.json'),
                 'source_probe_receipts':{name:sha(PROBE/name) for name in ['ACQUISITION_RECEIPT.json','CONVERSION_RECEIPT.json','EXTRACTION.json']},
                 'working_assumptions':'Admitted printed values are not certified target statistics; unlabelled units and applicability gaps remain.',
                 'task_sha256':sha(NEW/'task.json'),'registry_sha256':sha(NEW/'registry.json'),
                 'proposal_sha256':gate['proposal_sha256'],'review_sha256':gate['review_sha256']}
    (NEW/'SOURCE_INCREMENT_ADMISSION.json').write_text(json.dumps(admission,indent=2)+'\n',encoding='utf-8')
    (ROOT/'NEW_BUNDLE.json').write_text(json.dumps({'bundle':str(NEW),'candidate':'source_increment',**admission},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'bundle':str(NEW),'registered_artifacts':len(registry['artifacts']),'candidate_created_empty':True}))

if __name__ == '__main__':
    main()
