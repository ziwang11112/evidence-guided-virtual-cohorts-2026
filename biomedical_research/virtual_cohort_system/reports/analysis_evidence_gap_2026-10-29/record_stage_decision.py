"""Record an evidence-insufficiency stop without opening target outcomes."""
from pathlib import Path
from datetime import datetime, timezone
import json
import sys

E = Path(__file__).resolve().parent
P = E.parents[1]
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import sha256


def main():
    # These are deliberately existence-only checks, not outcome-table reads.
    for path in (E / 'custodian/evaluation', E / 'agent_bundle/executions',
                 E / 'agent_bundle/source_replays', E / 'evaluation_commitment.json'):
        if path.exists():
            raise ValueError('Unexpected execution/release artifact')
    decision = {'created_utc': datetime.now(timezone.utc).isoformat(),
        'decision': 'retain_scientific_generator_and_keep_target_evaluation_locked',
        'authorization_target_evaluation': False, 'generator_execution_authorized': False,
        'reason': 'New evidence motivates age-by-BMI structure, but the direct joint-ratio '
                  'supplement was not obtained. Other extracted coefficients use unresolved '
                  'BMI standardization in longitudinal adjusted models. No calibrated update '
                  'to the current cross-sectional generator was justified by the source-only builder.',
        'not_a_negative_finding': 'This does not show the source studies or idea fail. '
                                  'The bounded retrieval did find relevant joint evidence.',
        'next_discriminating_action': 'Obtain an exact joint-statistic table or compatible '
                                     'conditional estimates with the required scaling/adjustment context; '
                                     'then freeze a justified generator revision before target release.',
        'input_commitments': {rel: sha256(E / rel) for rel in [
            'research/evidence_gap_map.md', 'research/candidate_evidence.json',
            'research/retrieval_log.md', 'source_admission.json',
            'custodian/custodian_lock.json', 'review/FULL_HARNESS_TESTS.json']},
        'scope': 'Source admission, structural evidence-map checks and retained-model freeze only. '
                 'No source replay, generator sampling or new target analysis in M7.'}
    with (E / 'stage_decision.json').open('x', encoding='utf-8') as stream:
        json.dump(decision, stream, indent=2, allow_nan=False)
        stream.write('\n')


if __name__ == '__main__':
    main()
