"""Controller metadata review only; no generation or reference-table access."""
import datetime
import hashlib
import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent
P = R.parent.parent
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import verify_candidate


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    expected = {
        'b1': ('357cba8fce214024106dcf0028e69d3ab97f0aa0e1fce29d55230d0776752bfb',
               'ea24ce1e90cb01746889561791642ec7bee5f119a62f7e8f48955ce9eb11d210'),
        'b2': ('1737da8304906e833f7c89f4b4e0ca86116caed2d735b87c3254d72f1cbbbfec',
               '3e6e433f1eb2c474a7eeb8714ead8c69098db1d7b7b7bde3468faaedb1a0e7cb'),
    }
    records, seconds = [], 0.0
    for index, (bundle, hashes) in enumerate(expected.items(), 1):
        states = {stage: verify_candidate(R / bundle, 'candidates/' + stage)
                  for stage in ('initial', 'final')}
        for stage, digest in zip(('initial', 'final'), hashes):
            assert sha(R / bundle / f'candidates/{stage}/freeze.json') == digest
        assert states['final']['revision']['kind'] == 'retain'
        initial, final = [R / bundle / 'candidates' / stage for stage in ('initial', 'final')]
        names = ['generator.py', 'model_spec.json', 'evidence.json', 'source_context_plan.json']
        names += [f'source_contexts/{context}/{name}' for context in ('lifelines', 'pani')
                  for name in ('task.json', 'whole_cohort_feedback.json')]
        for name in names:
            assert (initial / name).read_bytes() == (final / name).read_bytes(), name
        handoff = R / bundle / 'controller_feedback/initial'
        manifest = json.loads((handoff / 'FEEDBACK_MANIFEST.json').read_bytes())
        assert manifest['candidate_freeze_sha256'] == hashes[0]
        assert manifest['source_seed'] == 18101 and manifest['target_results_included'] is False
        final_hashes = {v for k, v in states['final']['commitments'].items()
                        if k.startswith('candidates/final/')}
        assert sha(handoff / 'FEEDBACK_MANIFEST.json') in final_hashes
        for name, digest in manifest['files'].items():
            assert sha(handoff / name) == digest and digest in final_hashes
        source = R / f's{index}i'
        report = json.loads((source / 'report.json').read_bytes())
        assert sha(source / 'report.json') == manifest['files']['source_context_report.json']
        assert report['status'] == 'success'
        assert {c['id'] for c in report['contexts']} == {'lifelines', 'pani'}
        for context in report['contexts']:
            receipt_path = source / f"contexts/{context['id']}/bundle/executions/source/execution.json"
            receipt = json.loads(receipt_path.read_bytes())
            assert sha(receipt_path) == context['execution_sha256']
            assert receipt['status'] == 'success' and receipt['limits']['seed'] == 18101
            assert len(context['feedback']['checks']) == {'lifelines': 11, 'pani': 9}[context['id']]
            assert context['generation_link_verified'] and context['feedback']['output_link_verified']
            seconds += receipt['elapsed_seconds']
        records.append({
            'id': f'construction_{index}', 'bundle': bundle,
            'initial_candidate': 'candidates/initial', 'initial_freeze_sha256': hashes[0],
            'final_candidate': 'candidates/final', 'final_freeze_sha256': hashes[1],
            'decision': 'retain', 'source_bridge_report': f's{index}i/report.json',
            'source_bridge_sha256': sha(source / 'report.json'),
            'feedback_handoff_sha256': sha(handoff / 'FEEDBACK_MANIFEST.json'),
        })
    release = {
        'schema': 'cycle2_target_execution_release_v1', 'issuer': 'root', 'status': 'approved',
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'protocol_sha256': sha(R / 'PROTOCOL_v2.md'),
        'construction_release_sha256': sha(R / 'CONSTRUCTION_RELEASE.json'),
        'initial_scientific_review_sha256': sha(R / 'review/INITIAL_SCIENTIFIC_REVIEW.md'),
        'evaluation_guard_review_sha256': sha(R / 'review/EVALUATION_CONTROLLER_REVIEW.md'),
        'controller_script_sha256': sha(Path(__file__)), 'builders': records,
        'unique_runs': [{'bundle': bundle, 'candidate': 'candidates/initial',
                         'run_id': f'target-initial-{seed}', 'seed': seed}
                        for bundle in expected for seed in (18203, 18211, 18223)],
        'retention_policy': 'Final stages reuse exact initial same-seed outputs; no final redraws.',
        'source_execution_seconds': seconds, 'target_effects_authorized': False,
        'purpose': 'Generate and structurally validate the complete fixed six-run schedule. '
                   'Both final freezes complete. No real target effect fitting before separate release.',
    }
    with (R / 'EXECUTION_RELEASE.json').open('x', encoding='utf-8') as stream:
        json.dump(release, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status': 'approved', 'unique_runs': 6,
                      'release_sha256': sha(R / 'EXECUTION_RELEASE.json'),
                      'source_execution_seconds': seconds, 'target_effects_seen': False}))


if __name__ == '__main__':
    main()
