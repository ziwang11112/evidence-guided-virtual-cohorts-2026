"""Bind the author's actual decision and all source receipts before target generation."""
from pathlib import Path
import datetime, json
import act

HERE = Path(__file__).resolve().parent

def main():
    bundle = Path(act.read(HERE / 'PROTOCOL.json')['bundle'])
    decision_path = bundle / 'author_final_decision.json'
    decision = act.read(decision_path)
    status = act.session.verify_session(bundle)
    if status['status'] != 'active' or status['usage']['executions'] != 0:
        raise ValueError('Author decision must precede any target execution')
    candidates = status['candidates']
    if decision['decision'] not in ('retain', 'revise') or decision['final_candidate'] not in candidates:
        raise ValueError('Invalid author decision')
    reports = sorted((bundle / act.source.FOLDER).glob('*/replay.json'))
    inventory = {p.relative_to(bundle).as_posix(): act.sha(p) for p in reports}
    if decision['source_feedback'] != inventory:
        raise ValueError('Author did not bind the complete source feedback inventory')
    for name in candidates:
        stage_plan = act.read(bundle / name / act.source.PLAN)
        expected = {e['replay_id'] for e in stage_plan['schedule'] if e['candidate'] == name}
        actual = {act.read(p)['replay_id'] for p in reports if act.read(p)['parent']['candidate'] == name}
        if expected != actual:
            raise ValueError('Incomplete scheduled source stage; inspect failures explicitly')
    seal = {'schema_version': 1, 'sealed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'decision': decision['decision'], 'final_candidate': decision['final_candidate'],
            'author_decision': {'path': decision_path.relative_to(bundle).as_posix(), 'sha256': act.sha(decision_path)},
            'candidate_freezes': {name: act.sha(bundle / name / 'freeze.json') for name in candidates},
            'source_feedback': inventory,
            'target_executions_before_seal': 0, 'clinical_reference_access': False}
    act.write(HERE / 'AUTHOR_SEALED.json', seal)
    act.verify_author_seal(bundle)
    print(json.dumps({'decision': seal['decision'], 'final_candidate': seal['final_candidate'],
                      'source_reports': len(inventory), 'target_executions_before_seal': 0}))

if __name__ == '__main__': main()
