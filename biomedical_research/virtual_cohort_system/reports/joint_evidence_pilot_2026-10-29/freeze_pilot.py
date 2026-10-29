"""Record controller review and freeze the reviewed scientific candidates."""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,sys

E=Path(__file__).resolve().parent;P=E.parents[1];B=E/'agent_bundle'
sys.path.insert(0,str(P))
from cohort_harness.lifecycle import read_json,sha256
from cohort_harness.__main__ import validate_bundle

audit=read_json(E/'review/CANDIDATE_AUDIT.json')
assert audit['verdict'].startswith('PASS') and not audit['blockers']
for row in audit['reviewed_files']:
    assert sha256(E/row['path'])==row['sha256'],row['path']
cp=B/'candidates/joint_evidence'
checks=read_json(cp/'static_validation.json')
for rel,h in checks['input_sha256'].items():
    assert sha256(cp/rel)==h,rel
assert not (B/'source_replays').exists() and not (B/'executions').exists()
intent=read_json(E/'pilot_intent.json')
validation={name:validate_bundle(B,B/'candidates'/name) for name in intent['variants']}
receipt={'created_utc':datetime.now(timezone.utc).isoformat(),
    'decision':'proceed_with_exploratory_frozen_source_and_target_schedule',
    'static_candidate_audit_sha256':sha256(E/'review/CANDIDATE_AUDIT.json'),
    'candidate_contracts':validation,
    'root_evaluator_tests':{'command':'python -B -m unittest discover -s work/joint-evidence-pilot-2026-10-29/evaluation -p test_evaluator.py -v',
        'passed':9,'scope':'invented fixtures; nonmutating independent rerun'},
    'evaluation_amendment_sha256':sha256(E/'evaluation/protocol_amendment.json'),
    'source_extraction_independently_verified':True,
    'candidate_generator_or_target_evaluation_previously_run':False,
    'controller_review':'Same declared variants/seeds, isolated execution only, successful source execution linkage before target generation, complete output grid before target release, candidate/runtime/core/custody/evaluator hashes and chronology bound. No parameter-fitting step.',
    'limitations':['Source-to-target transfer is a hypothesis, not a validated calibration.',
        'Source joint adjusted-ratio replay is not available; old-source diagnostics are retained.',
        'Outer Agents procedurally restricted, not OS isolated; evaluator historical aggregate exposure disclosed separately.']}
with (E/'pre_execution_review.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2)
for name in intent['variants']:
    args=[sys.executable,'-B','-m','cohort_harness','freeze','--bundle',str(B),'--candidate',name]
    if name=='joint_evidence':args+=['--parent','baseline','--revision',str(cp/'revision.json')]
    result=subprocess.run(args,cwd=P,capture_output=True,text=True,encoding='utf-8',errors='replace')
    log=E/'controller_logs'/f'freeze_{name}.json';log.parent.mkdir(exist_ok=True)
    with log.open('x',encoding='utf-8') as f:json.dump({'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr},f,indent=2)
    if result.returncode:raise RuntimeError(result.stderr)
    print(name+' frozen',flush=True)
subprocess.run([sys.executable,'-B',str(E/'controller.py'),'freeze_protocol'],cwd=P,check=True)
