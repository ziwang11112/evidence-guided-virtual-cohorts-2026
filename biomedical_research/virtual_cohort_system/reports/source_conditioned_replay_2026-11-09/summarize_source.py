"""Source-only aggregate feedback. No target-execution or reference reads."""
from pathlib import Path
import collections, hashlib, json, sys
import act

HERE = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    stage = sys.argv[1]
    if stage not in ('initial', 'revised'): raise ValueError('Unknown stage')
    bundle = Path(read(HERE / 'PROTOCOL.json')['bundle'])
    plan = read(bundle / 'candidates' / stage / act.source.PLAN)
    planned = {e['replay_id'] for e in plan['schedule'] if e['candidate'] == 'candidates/' + stage}
    attempted = {p.parent.name for p in (bundle / act.source.FOLDER).glob(stage + '_*/request.json')}
    records, failures, reports = [], [], {}
    strict_status = collections.Counter()
    for path in sorted((bundle / 'whole_cohort_source_replays_v1').glob(stage + '_*/replay.json')):
        report = act.source.verify_source_replay(bundle, path.parent.name, candidate='candidates/' + stage)
        reports[path.relative_to(bundle).as_posix()] = sha(path)
        context = report['context']
        if report['status'] != 'success':
            failures.append({'replay_id': report['replay_id'], 'status': report['status'], 'error': context['error']})
        for check in (context.get('strict_feedback') or {}).get('checks', []):
            strict_status[check['semantic_status']] += 1
        for check in context['assumed_diagnostics']:
            records.append({'replay_id': report['replay_id'], 'context_id': context['context_id'],
                'check_id': check['check_id'], 'evidence_id': check['evidence_id'],
                'status': check['status'], 'reported': check['reported_value'],
                'reported_uncertainty': check['reported_uncertainty'],
                'generated': (check['calculation'] or {}).get('value'), 'difference': check['difference'],
                'assumptions': check['assumption_ids'], 'strict_reason': check['strict_unavailable_reason'],
                'unavailable_reason': check['unavailable_reason']})
    result = {'stage': stage, 'scope': 'source_only_assumption_dependent_projection',
              'source_reports': reports, 'source_attempts_with_report': len(reports),
              'planned_replay_ids': sorted(planned), 'attempted_replay_ids': sorted(attempted),
              'unattempted_replay_ids': sorted(planned - attempted),
              'attempts_without_report': sorted(attempted - {Path(p).parent.name for p in reports}),
              'strict_semantic_counts': dict(strict_status), 'records': records, 'failures': failures,
              'target_outputs_or_references_read': False,
              'interpretation': 'Source reported CIs are not residual variability or acceptance thresholds; seeds are numerical repeats, not clinical studies.'}
    destination = HERE / (stage.upper() + '_SOURCE_FEEDBACK.json')
    with destination.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, allow_nan=False); f.write('\n')
    print(json.dumps({'file': str(destination), 'reports': len(reports), 'computed': sum(x['status']=='computed' for x in records), 'failures':len(failures)}))

if __name__ == '__main__': main()
