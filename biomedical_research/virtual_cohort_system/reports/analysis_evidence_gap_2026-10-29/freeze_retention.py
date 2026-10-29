"""Freeze the reviewed no-op; no generator or target evaluator is invoked."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys

E = Path(__file__).resolve().parent
P = E.parents[1]
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import read_json, sha256, freeze_candidate, verify_candidate
from cohort_harness.analysis_evidence import summarize_analysis_evidence


def main():
    b = E / 'agent_bundle'
    stage = read_json(E / 'stage_decision.json')
    if stage['generator_execution_authorized'] or stage['authorization_target_evaluation']:
        raise ValueError('Wrong milestone scope')
    audit = E / 'review/RETENTION_AUDIT.md'
    if not audit.is_file():
        raise ValueError('Independent retention review is missing')
    review = read_json(E / 'review/RETENTION_AUDIT_CHECKS.json')
    if review['disposition'] != 'pass_for_retention_freeze_only' or review['target_evaluation_authorized']:
        raise ValueError('Review does not authorize a retention freeze')
    for name, files in review['reviewed_candidate_hashes'].items():
        for relative, digest in files.items():
            if sha256(b / 'candidates' / name / relative) != digest:
                raise ValueError('Reviewed candidate changed: ' + name + '/' + relative)
    for path in (b / 'executions', b / 'source_replays', E / 'custodian/evaluation'):
        if path.exists():
            raise ValueError('Unexpected scientific execution')
    before, after = b / 'candidates/baseline', b / 'candidates/evidence_augmented'
    imported = read_json(E / 'baseline_import.json')
    for file in ('generator.py', 'model_spec.json'):
        if not sha256(before / file) == sha256(after / file) == imported['files'][file]:
            raise ValueError('Scientific artifact changed: ' + file)
    if read_json(after / 'revision.json')['kind'] != 'retain':
        raise ValueError('Expected retention revision')
    freeze_candidate(b, before)
    freeze_candidate(b, after, parent_receipt=before / 'freeze.json', revision=read_json(after / 'revision.json'))
    summaries = {}
    for name in ('baseline', 'evidence_augmented'):
        cp = b / 'candidates' / name
        verify_candidate(b, cp)
        summaries[name] = summarize_analysis_evidence(read_json(cp / 'analysis_evidence.json'),
            read_json(b / 'task.json'), read_json(cp / 'evidence.json'), read_json(cp / 'model_spec.json'))
    record = {'created_utc': datetime.now(timezone.utc).isoformat(), 'status': 'passed',
        'kind': 'reviewed_scientific_retention', 'generator_executed': False, 'target_evaluated': False,
        'generator_sha256': sha256(before / 'generator.py'), 'model_spec_sha256': sha256(before / 'model_spec.json'),
        'scientific_bytes_unchanged': True,
        'candidate_freezes': {name: sha256(b / 'candidates' / name / 'freeze.json')
                              for name in ('baseline', 'evidence_augmented')},
        'stage_decision_sha256': sha256(E / 'stage_decision.json'),
        'retention_audit_sha256': sha256(audit), 'custodian_lock_sha256': sha256(E / 'custodian/custodian_lock.json'),
        'map_summaries': summaries,
        'code_sha256': {f.relative_to(p).as_posix(): sha256(f) for p in [P]
                        for d in ['cohort_harness', 'tests'] for f in sorted((p / d).glob('*.py'))}}
    with (E / 'retention_freeze.json').open('x', encoding='utf-8') as stream:
        json.dump(record, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': 'passed', 'scientific_bytes_unchanged': True,
                      'candidate_freezes': record['candidate_freezes']}))


if __name__ == '__main__':
    main()
