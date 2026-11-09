"""Run all submitted stages after the author's source-only decision is sealed."""
from pathlib import Path
import json
import act

HERE = Path(__file__).resolve().parent

def main():
    protocol = act.read(HERE / 'PROTOCOL.json')
    bundle = Path(protocol['bundle'])
    seal = act.verify_author_seal(bundle)
    for candidate in sorted(seal['candidate_freezes']):
        stage = Path(candidate).name
        for seed in protocol['target_seeds']:
            run_id = stage + '_target_' + str(seed)
            result = act.dispatch(run_id, {'kind': 'execute', 'candidate': candidate, 'run_id': run_id, 'seed': seed})
            print(json.dumps({'run_id': run_id, 'execution': result['status']}), flush=True)
            if result['status'] != 'success':
                # No retry or silently dropped execution; the immutable session retains failure.
                continue
            feedback_id = run_id + '_feedback'
            response = act.dispatch(feedback_id, {'kind': 'feedback', 'candidate': candidate,
                                                  'run_id': run_id, 'feedback_id': feedback_id})
            if response['status'] != 'success': raise ValueError('Feedback action failed; see receipt')
            for adapter in ('generated', 'analysis_use'):
                analysis_id = run_id + '_' + adapter
                response = act.dispatch(analysis_id, {'kind': 'analysis', 'candidate': candidate,
                                                      'run_id': run_id, 'analysis_id': analysis_id, 'adapter': adapter})
                if response['status'] != 'success': raise ValueError('Analysis action failed; see receipt')
            print(json.dumps({'run_id': run_id, 'feedback_and_both_analyses': 'completed'}), flush=True)
    print(json.dumps({'status': 'outputs_complete', 'final_candidate': seal['final_candidate'],
                      'reference_access': 'none', 'finish_pending_independent_recalculation': True}), flush=True)

if __name__ == '__main__': main()
