"""Independent offline review of the new matrix, tariff and dispatch boundaries.

No provider requests, credentials, source downloads, patient data, target values
or candidate execution. All mutation probes use a temporary directory.
"""
from __future__ import annotations

import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
UNIT = Path(__file__).resolve().parents[1]
OLD = UNIT.parent / 'request_only_agent_capacity_2026-11-10'


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value), encoding='utf-8')


def main():
    loop = load('independent_repeatability_loop', UNIT / 'api_loop.py')
    checks = []

    def check(name, value):
        assert value, name
        checks.append(name)

    def rejects(name, fn):
        try:
            fn()
        except (loop.IntegrityError, AssertionError, FileNotFoundError):
            checks.append(name)
        else:
            raise AssertionError(name)

    plan = read(UNIT / 'PLAN.json')
    check('twelve unique registered authors', len(plan['episodes']) == 12 and
          len({e['episode_id'] for e in plan['episodes']}) == 12)
    check('balanced three constructors per case/policy',
          Counter((e['case_id'], e['arm']) for e in plan['episodes']) ==
          Counter({('PNS', 'ordinary'): 3, ('PNS', 'workflow'): 3,
                   ('lipids', 'ordinary'): 3, ('lipids', 'workflow'): 3}))
    check('three complete four-cell blocks', all(
          len({(e['case_id'], e['arm']) for e in plan['episodes'] if e['block'] == b}) == 4
          for b in [1, 2, 3]))
    check('final denominator and fixed seeds', plan['max_final_tables'] == 36 and
          plan['evaluation_seeds'] == [54001, 54003, 54007] and plan['final_rows_per_table'] == 3000)
    check('monetary ceilings', plan['limits']['episode_usd_cap'] == 4 and
          plan['limits']['total_usd_cap'] == 48)
    same = ['tools_runtime.py', 'policies/common.txt', 'policies/ordinary.txt',
            'policies/workflow.txt', 'tasks/PNS.json', 'tasks/LIPID.json',
            'requests/PNS.txt', 'requests/LIPID.txt']
    for name in same:
        check('unchanged scientific input/runtime: ' + name,
              (UNIT / name).read_bytes() == (OLD / name).read_bytes())
    inputs = {}
    for ep in plan['episodes']:
        _, _, _, instructions, initial, rates = loop.config(UNIT, ep['episode_id'])
        key = (ep['case_id'], ep['arm'])
        value = (instructions, initial)
        if key in inputs:
            check('same fresh-context input: ' + ep['episode_id'], inputs[key] == value)
        else:
            inputs[key] = value
    for case in ['PNS', 'lipids']:
        check('ordinary/workflow request equality: ' + case,
              inputs[(case, 'ordinary')][1] == inputs[(case, 'workflow')][1])

    for n in [272000, 272001]:
        usage = {'input_tokens': n, 'output_tokens': 100,
                 'input_tokens_details': {'cached_tokens': 1000, 'cache_write_tokens': 2000}}
        factor_i, factor_o = (1, 1) if n == 272000 else (2, 1.5)
        expected = ((n - 3000) * 2 + 1000 * .1 + 2000 * 2.5) * factor_i / 1e6 + 100 * 10 * factor_o / 1e6
        check('actual-use tariff boundary: ' + str(n), abs(loop.tariff(usage, rates) - expected) < 1e-12)

    with tempfile.TemporaryDirectory(prefix='repeatability_launch_gate_') as temp:
        root = Path(temp)
        required = {'PLAN.json', 'api_loop.py', 'tools_runtime.py', 'evaluate_pilot.py',
                    'PROTOCOL.md', 'TARIFF_VERIFICATION.json', 'MODEL_AVAILABILITY.json',
                    'ANALYSIS_INTERPRETATION_PLAN.md', plan['common_instructions_path']}
        required |= {e[k] for e in plan['episodes'] for k in ['task_path', 'request_path', 'policy_path']}
        for name in required:
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(UNIT / name, root / name)
        hashes = {name: sha(root / name) for name in required}
        helper_hash = sha(loop.KEY_HELPER)
        write(root / 'PREFLIGHT_REVIEW.json', {'status': 'pass', 'reviewed_files': hashes,
              'credential_helper_sha256': helper_hash, 'reviewed_external_files': {}})
        frozen = dict(hashes, **{'PREFLIGHT_REVIEW.json': sha(root / 'PREFLIGHT_REVIEW.json')})
        write(root / 'LAUNCH_FREEZE.json', {'files': frozen, 'credential_helper_sha256': helper_hash, 'external_files': {}})
        rejects('root approval absent blocks live gate', lambda: loop.verify_live_gate(root, plan))
        approval = {'status': 'approved', 'launch_freeze_sha256': sha(root / 'LAUNCH_FREEZE.json'),
                    'plan_sha256': sha(root / 'PLAN.json'), 'episodes': sorted(loop.EPISODE_IDS), 'files': frozen}
        write(root / 'ROOT_EXECUTION_APPROVAL.json', approval)
        loop.verify_live_gate(root, plan)
        checks.append('valid root approval binds all12 and exact launch bytes')
        approval['episodes'] = approval['episodes'][:-1]
        write(root / 'ROOT_EXECUTION_APPROVAL.json', approval)
        rejects('partial root approval rejected', lambda: loop.verify_live_gate(root, plan))
        approval['episodes'] = sorted(loop.EPISODE_IDS)
        approval['launch_freeze_sha256'] = 'changed'
        write(root / 'ROOT_EXECUTION_APPROVAL.json', approval)
        rejects('root approval of different freeze rejected', lambda: loop.verify_live_gate(root, plan))

    def body_at(size):
        body = {'input': 'x' * (size - len(loop.encoded({'input': ''})))}
        assert len(loop.encoded(body)) == size
        return body

    with tempfile.TemporaryDirectory(prefix='repeatability_independent_') as temp:
        root = Path(temp)
        write(root / 'PLAN.json', plan)
        for path in {plan['common_instructions_path']} | {e[k] for e in plan['episodes']
                for k in ['task_path', 'request_path', 'policy_path']}:
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(UNIT / path, root / path)
        eid = plan['episodes'][0]['episode_id']
        for n, allowance in enumerate([272000, 272001], 1):
            folder, reason = loop.reserve(root, eid, n, body_at(allowance - 4096), plan['limits'], rates)
            check('reservation accepted at threshold: ' + str(allowance), reason is None)
            reservation = read(folder / 'reservation.json')
            expected = (allowance * 2.5 * (1 if allowance == 272000 else 2) +
                        16384 * 10 * (1 if allowance == 272000 else 1.5)) / 1e6
            check('conservative reservation boundary: ' + str(allowance),
                  abs(reservation['reserved_usd'] - expected) < 1e-12)
        total_unknown = loop.accounted(root, eid)
        check('unknown usage stays reserved', abs(total_unknown -
              sum(read(p)['reserved_usd'] for p in (root / 'episodes' / eid).glob('calls/*/reservation.json'))) < 1e-12)
        folder, reason = loop.reserve(root, plan['episodes'][1]['episode_id'], 1,
                                      body_at(750000), plan['limits'], rates)
        check('maximum request exceeds four-dollar conservative reservation',
              folder is None and reason == 'budget_limit')
        folder, reason = loop.reserve(root, plan['episodes'][1]['episode_id'], 1,
                                      body_at(750001), plan['limits'], rates)
        check('byte ceiling independently enforced', folder is None and reason == 'input_byte_limit')
        first = root / 'episodes' / eid / 'calls' / '0001'
        write(first / 'receipt.json', {'reservation_sha256': sha(first / 'reservation.json'), 'tariff_cost_usd': .01})
        check('known usage replaces only its own reservation', abs(loop.accounted(root, eid) -
              (total_unknown - read(first / 'reservation.json')['reserved_usd'] + .01)) < 1e-12)

        for malformed in [dict(plan, episodes=plan['episodes'][:-1]),
                          dict(plan, episodes=plan['episodes'] + [plan['episodes'][0]])]:
            write(root / 'PLAN.json', malformed)
            rejects('missing/duplicate matrix cell rejected', lambda: loop.config(root, eid))
        write(root / 'PLAN.json', plan)
        write(root / 'LAUNCH_FREEZE.json', {'fixture': True})
        block2 = next(e for e in plan['episodes'] if e['block'] == 2)
        rejects('block2 blocked before operational approval', lambda: loop.verify_dispatch_gate(root, plan, block2))
        outcomes = {}
        for ep in [e for e in plan['episodes'] if e['block'] == 1]:
            op = root / 'episodes' / ep['episode_id'] / 'OUTCOME.json'
            write(op, {'episode_id': ep['episode_id'], 'status': 'call_limit'})
            outcomes[ep['episode_id']] = sha(op)
        gate = {'status': 'pass', 'target_comparisons_inspected': False,
                'plan_sha256': sha(root / 'PLAN.json'), 'launch_freeze_sha256': sha(root / 'LAUNCH_FREEZE.json'),
                'outcome_sha256': outcomes}
        write(root / 'OPERATIONAL_BLOCK1_REVIEW.json', gate)
        loop.verify_dispatch_gate(root, plan, block2)
        checks.append('complete routine-exhaustion block may proceed after operational review')
        gate['target_comparisons_inspected'] = True
        write(root / 'OPERATIONAL_BLOCK1_REVIEW.json', gate)
        rejects('target-aware operational gate rejected', lambda: loop.verify_dispatch_gate(root, plan, block2))
        gate['target_comparisons_inspected'] = False
        write(root / 'OPERATIONAL_BLOCK1_REVIEW.json', gate)
        block3 = next(e for e in plan['episodes'] if e['block'] == 3)
        rejects('block3 cannot skip unfinished block2', lambda: loop.verify_dispatch_gate(root, plan, block3))
        for ep in [e for e in plan['episodes'] if e['block'] == 2]:
            write(root / 'episodes' / ep['episode_id'] / 'OUTCOME.json',
                  {'episode_id': ep['episode_id'], 'status': 'budget_limit'})
        loop.verify_dispatch_gate(root, plan, block3)
        checks.append('block3 admits complete routine block2')
        write(root / 'episodes' / block2['episode_id'] / 'OUTCOME.json',
              {'episode_id': block2['episode_id'], 'status': 'model_mismatch'})
        rejects('protocol failure stops all fresh dispatch', lambda: loop.verify_dispatch_gate(root, plan, block3))

    # Exercise the twelve-author closure and all36 slots using no-candidate
    # outcomes and an explicitly artificial reference, never the clinical file.
    old_path = list(sys.path)
    old_runtime = sys.modules.get('tools_runtime')
    try:
        sys.path.insert(0, str(UNIT))
        sys.modules.pop('tools_runtime', None)
        evaluator = load('independent_repeatability_evaluator', UNIT / 'evaluate_pilot.py')
    finally:
        sys.path[:] = old_path
        if old_runtime is None:
            sys.modules.pop('tools_runtime', None)
        else:
            sys.modules['tools_runtime'] = old_runtime
    with tempfile.TemporaryDirectory(prefix='repeatability_closure_') as temp:
        root = Path(temp)
        evaluator.ROOT = root
        write(root / 'PLAN.json', plan)
        evaluator.SNAPSHOT = root / 'ARTIFICIAL_REFERENCE.json'
        write(evaluator.SNAPSHOT, {'references': {
            'PNS': {'fixture_analysis': {'value': 0, 'unit': 'fixture'}},
            'lipids': {'fixture_analysis': {'value': 0, 'unit': 'fixture'}}}})
        evaluator.SNAPSHOT_SHA = sha(evaluator.SNAPSHOT)
        for ep in plan['episodes'][:-1]:
            write(root / 'episodes' / ep['episode_id'] / 'OUTCOME.json',
                  {'episode_id': ep['episode_id'], 'status': 'call_limit',
                   'selected_candidate': None, 'calls_reserved': 0,
                   'known_tariff_cost_usd': 0, 'accounted_usd': 0})
        rejects('eleven terminal authors cannot create construction closure', evaluator.close)
        check('failed partial closure leaves no closure artifact', not (root / 'CONSTRUCTION_CLOSURE.json').exists())
        ep = plan['episodes'][-1]
        write(root / 'episodes' / ep['episode_id'] / 'OUTCOME.json',
              {'episode_id': ep['episode_id'], 'status': 'call_limit',
               'selected_candidate': None, 'calls_reserved': 0,
               'known_tariff_cost_usd': 0, 'accounted_usd': 0})
        closure = evaluator.close()
        check('twelve distinct suffixed authors preserved in closure',
              {e['episode_id'] for e in closure['episodes']} == loop.EPISODE_IDS)
        slots = evaluator.draw()
        check('all36 unavailable planned slots preserved without execution', len(slots) == 36 and
              all(s['status'] == 'unavailable' for s in slots) and
              len({(s['episode_id'], s['seed']) for s in slots}) == 36)
        result = evaluator.evaluate()
        check('evaluation reports twelve constructors and36 slots',
              result['counts']['episodes'] == 12 and result['counts']['final_slots'] == 36 and
              result['counts']['unavailable_tables'] == 36)
        output = read(root / 'EVALUATION.json')
        check('summary retains suffixed constructor IDs and assigned case/policy',
              {(s['episode_id'], s['case_id'], s['arm']) for s in output['summaries']} ==
              {(e['episode_id'], e['case_id'], e['arm']) for e in plan['episodes']})

    # Verify unchanged function bodies outside the declared operational changes.
    def functions(path):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        return {n.name: ast.dump(n, include_attributes=False) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    before, after = functions(OLD / 'api_loop.py'), functions(UNIT / 'api_loop.py')
    permitted = {'config', 'verify_live_gate', 'tariff', 'reserve', 'run_episode', 'main', 'send_once'}
    for name in before:
        if name not in permitted:
            check('unchanged operational primitive: ' + name, before[name] == after[name])
    payload = {'status': 'pass', 'created_utc': datetime.now(timezone.utc).isoformat(),
               'passed': len(checks), 'checks': checks,
               'reviewed_files': {n: sha(UNIT / n) for n in ['PLAN.json', 'api_loop.py', 'evaluate_pilot.py', 'tools_runtime.py']},
               'paid_calls': 0, 'credentials_read': False, 'target_values_read': False,
               'patient_rows_read': False, 'generated_candidates_executed': 0}
    (UNIT / 'review' / 'INDEPENDENT_OFFLINE_CHECKS.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(json.dumps({'status': payload['status'], 'passed': len(checks)}))


if __name__ == '__main__':
    main()
