"""Bind reviewed source, candidate, controller and evaluator before six draws."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

UNIT = Path(__file__).resolve().parent
sys.path.insert(0, str(UNIT.parents[1]))
from cohort_harness.lifecycle import freeze_candidate, verify_candidate
from cohort_harness.execution import DEFAULT_RUNTIME

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    destination = UNIT / 'RELEASE.json'
    assert not destination.exists(), 'Do not rewrite a frozen release'
    state = read(UNIT / 'STATE.json')
    assert state['final_attempts_spent'] == 0 and not state['execution_released']
    assert not (UNIT / 'attempts').exists() and not (UNIT / 'results').exists()
    controller = read(UNIT / 'evaluation/CONTROLLER_REVIEW_v3.json')
    assert controller['controller_sha256'] == sha(UNIT / 'run_experiment.py')
    assert controller['status'].startswith('pass')
    agent_review = read(UNIT / 'AGENT_IMPLEMENTATION_REVIEW.json')
    assert agent_review['status'].startswith('pass')
    for name, expected in agent_review['candidate_sha256'].items():
        assert sha(UNIT / 'bundle/candidates/agent' / name) == expected
    fixture = read(UNIT / 'INVENTED_EXECUTION_REVIEW.json')
    assert fixture['passed'] and fixture['formal_attempts_spent'] == 0
    for row in fixture['results']:
        assert sha(UNIT / 'bundle/candidates' / row['arm'] / 'generator.py') == row['program_sha256']
    evaluator = read(UNIT / 'evaluation/EVALUATOR_MANIFEST.json')
    for file in evaluator['files']:
        assert sha(UNIT / file['path']) == file['sha256'], 'Evaluator manifest stale: ' + file['path']
    assert evaluator['invented_checks']['native']=='pass' and evaluator['invented_checks']['GLS']=='pass'
    for arm in ['native','agent']:
        path = UNIT / 'bundle/candidates' / arm
        freeze_candidate(UNIT / 'bundle', 'candidates/' + arm)
        verify_candidate(UNIT / 'bundle', 'candidates/' + arm)
    fixed = [
        'PROTOCOL.md','prepare_release.py','run_experiment.py','summarize.py',
        'SOURCE_REGISTRATION_REVIEW.json','PAPER_REFERENCE_ADMISSION.json',
        'ROOT_IMPLEMENTATION_REVIEW.json','AGENT_IMPLEMENTATION_REVIEW.json',
        'INVENTED_EXECUTION_REVIEW.json','check_invented_execution.py',
        'sources/SOURCE_MANIFEST.json','sources/HRS_SOURCE_EVIDENCE.json','sources/HRS_PUBLISHED_REFERENCES.json',
        'evaluation/EVALUATOR_MANIFEST.json','evaluation/CONTROLLER_REVIEW_v3.json',
        'evaluation/runtime/RUNTIME.json','evaluation/runtime/DEPENDENCY_DOWNLOADS.json',
        'evaluation/INVENTED_NATIVE_BOBYQA_CHECK.json','evaluation/INVENTED_BOBYQA_GLS_CHECK.json',
        'bundle/task.json','bundle/registry.json','bundle/AUTHOR_TASK.md','bundle/SOURCE_METADATA.json',
        '../../cohort_harness/contracts.py','../../cohort_harness/lifecycle.py',
        '../../cohort_harness/execution.py','../../cohort_harness/_worker.py'
    ] + [item['path'] for item in evaluator['files']]
    for arm in ['native','agent']:
        candidate = UNIT / 'bundle/candidates' / arm
        fixed.extend(str(p.relative_to(UNIT)).replace('\\','/') for p in candidate.iterdir() if p.is_file())
    for row in read(UNIT / 'bundle/registry.json')['artifacts']:
        fixed.append('bundle/' + row['path'])
    release = {'created_utc': datetime.now(timezone.utc).isoformat(),
        'execution_released':True,'arms':['native','agent'],'seeds':[6101,6102,6103],
        'generation_attempts_allowed':6, 'subjects_per_table':11509, 'visits_per_table':46036,
        'generator_runtime':DEFAULT_RUNTIME,
        'files':{relative:sha(UNIT/relative) for relative in sorted(set(fixed))},
        'scope':'One source-model reconstruction example with shared published parameters. Independent scientific Agent chooses own implementation; native comparator follows published rounded law. No new source patient data.',
        'preparation_execution':'Two entirely invented 48-row isolated interface fixtures only. No HRS-configured table sampled before freeze.',
        'final_output_policy':'All six physical generation attempts close before any scientific evaluation. No post-result regeneration, model adjustment or seed replacement.'}
    with destination.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(release, stream, indent=2)
        stream.write('\n')
    state.update(phase='released',execution_released=True,release_sha256=sha(destination))
    (UNIT / 'STATE.json').write_text(json.dumps(state, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'phase':'released','bound_files':len(release['files']),'final_attempts_spent':0}))

if __name__=='__main__':
    main()
