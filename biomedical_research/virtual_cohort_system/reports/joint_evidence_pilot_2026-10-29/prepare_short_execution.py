"""Retain failed long-path copy and relocate identical frozen inputs for execution."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,sys

E=Path(__file__).resolve().parent;P=E.parents[1]
OLD=E/'agent_bundle';NEW=Path('${EXECUTION_BUNDLE}')
sys.path.insert(0,str(P))
from cohort_harness.lifecycle import read_json,sha256,verify_candidate

assert not NEW.exists(), 'Never overwrite an execution workspace'
old_anchor=read_json(E/'protocol_commitment.json')
prior=E/'attempt1';prior.mkdir(exist_ok=False)
shutil.copyfile(E/'protocol_commitment.json',prior/'protocol_commitment.json')
# Recover the two pre-amendment files by reversing the exact location edits and
# require byte hashes to match the already frozen old commitments before saving.
old_controller=(E/'controller.py').read_text(encoding='utf-8').replace(
    "B = Path(json.loads((E / 'execution_location.json').read_text())['bundle'])", "B = E / 'agent_bundle'").replace(
    "log = E / 'controller_logs' / ('attempt2_' + label + '.json')", "log = E / 'controller_logs' / (label + '.json')").encode('utf-8')
old_guard=(E/'release_guard.py').read_text(encoding='utf-8').replace(
    "e=Path(__file__).resolve().parent;p=e.parents[1]\n    b=Path(read_json(e/'execution_location.json')['bundle'])",
    "e=Path(__file__).resolve().parent;p=e.parents[1];b=e/'agent_bundle'").encode('utf-8')
for name,data in [('controller.py',old_controller),('release_guard.py',old_guard)]:
    assert hashlib.sha256(data).hexdigest()==old_anchor['files'][name],name
    (prior/name).write_bytes(data)
# Scientific frozen inputs are copied byte-for-byte; partial failed replay is not.
NEW.mkdir()
for name in ['task.json','registry.json','observed.csv']:
    shutil.copyfile(OLD/name,NEW/name)
for name in ['sources','candidates']:
    shutil.copytree(OLD/name,NEW/name)
bindings={}
for src in sorted(NEW.rglob('*')):
    if src.is_file():
        rel=src.relative_to(NEW).as_posix()
        assert sha256(src)==sha256(OLD/rel),rel
        bindings[rel]=sha256(src)
for name in ['baseline','joint_evidence']:verify_candidate(NEW,NEW/'candidates'/name)
location={'bundle':str(NEW),'original_frozen_bundle':str(OLD),
          'reason':'Windows long path in derived replay candidate copy failed before generator execution.',
          'candidate_bytes_unchanged':True,'participant_rows_remain_local':True}
(E/'execution_location.json').write_text(json.dumps(location,indent=2)+'\n',encoding='utf-8')
amendment={'created_utc':datetime.now(timezone.utc).isoformat(),
    'prior_protocol_sha256':sha256(prior/'protocol_commitment.json'),
    'failure_log_sha256':sha256(E/'controller_logs/baseline_80201.json'),
    'prior_controller_sha256':old_anchor['files']['controller.py'],
    'prior_guard_sha256':old_anchor['files']['release_guard.py'],
    'changed_controller_sha256':sha256(E/'controller.py'),
    'changed_guard_sha256':sha256(E/'release_guard.py'),
    'copied_inputs':bindings,'fresh_execution_directory':str(NEW),
    'scientific_parameters_seeds_and_endpoints_changed':False,
    'generator_executed_in_failed_attempt':False,
    'failed_replay_preserved_at':'agent_bundle/source_replays/baseline_80201',
    'scope':'Execution-location and controller-log namespace amendment only, before any scientific output.'}
(E/'execution_path_amendment.json').write_text(json.dumps(amendment,indent=2)+'\n',encoding='utf-8')
new_anchor=dict(old_anchor);new_anchor['created_utc']=datetime.now(timezone.utc).isoformat()
new_anchor['files']={r:sha256(E/r) for r in old_anchor['files']}
for r in ['execution_location.json','execution_path_amendment.json','prepare_short_execution.py']:
    new_anchor['files'][r]=sha256(E/r)
new_anchor['scope']='Attempt2 identical frozen scientific inputs in short physical directory; same seed/evaluation schedule. Prior failed preparation retained.'
(E/'protocol_commitment.json').write_text(json.dumps(new_anchor,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'identical_inputs_verified','copied_files':len(bindings),
    'candidate_freezes':new_anchor['candidate_freezes'],'new_bundle':str(NEW)}))
