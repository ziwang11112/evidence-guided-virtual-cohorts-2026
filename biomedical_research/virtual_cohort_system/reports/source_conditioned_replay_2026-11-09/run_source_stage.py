"""Execute an already reviewed author stage using its unchanged frozen schedule."""
from pathlib import Path
import json, sys
import act

HERE = Path(__file__).resolve().parent

def main():
    stage = sys.argv[1]
    if stage not in ('initial', 'revised'):
        raise ValueError('Unknown stage')
    review_name = 'SCIENTIFIC_CANDIDATE_REVIEW.json' if stage == 'initial' else 'REVISED_CANDIDATE_REVIEW.json'
    review = act.read(HERE / review_name)
    if review['remaining_blockers']:
        raise ValueError('Scientific review has blockers')
    for path, expected in review['reviewed_candidate_files'].items():
        if act.sha(Path(path)) != expected:
            raise ValueError('Reviewed scientific artifact changed: ' + path)
    protocol = act.read(HERE / 'PROTOCOL.json')
    bundle = Path(protocol['bundle'])
    candidate = 'candidates/' + stage
    action = {'kind': 'submit', 'candidate': candidate}
    if stage == 'revised':
        action.update(parent='candidates/initial', revision=act.read(bundle / candidate / 'revision_declaration.json'))
    result = act.dispatch(stage + '_submit', action)
    if result['status'] != 'success':
        raise ValueError('Submission failed; see retained receipt')
    plan = act.read(bundle / candidate / 'whole_cohort_source_replay_v1.json')
    schedule = [entry for entry in plan['schedule'] if entry['candidate'] == candidate]
    for entry in schedule:
        result = act.dispatch(entry['replay_id'], {
            'kind': 'source_replay', 'candidate': candidate,
            'replay_id': entry['replay_id'], 'context_id': entry['context_id'], 'seed': entry['seed']})
        print(json.dumps({'replay_id': entry['replay_id'], 'status': result['status'],
                          'computed': sum(x['status'] == 'computed' for x in result['context']['assumed_diagnostics'])}), flush=True)
    print(json.dumps({'stage': stage, 'scheduled_attempts': len(schedule), 'target_rows_read': False}), flush=True)

if __name__ == '__main__':
    main()
