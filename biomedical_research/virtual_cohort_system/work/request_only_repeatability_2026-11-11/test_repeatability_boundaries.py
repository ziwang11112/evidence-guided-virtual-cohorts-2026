"""Focused delta tests: matrix, economic gates, dispatch and global closure.

All API responses and scientific outputs are artificial test fixtures. No
credentials, network requests, patient data or candidate executions are used.
"""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

UNIT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('repeatability_loop_test', UNIT / 'api_loop.py')
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)
sys.path.insert(0, str(UNIT))
import evaluate_pilot as evaluator


def put(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding='utf-8')


@pytest.fixture
def pilot(tmp_path):
    plan = loop.read(UNIT / 'PLAN.json')
    put(tmp_path / 'PLAN.json', plan)
    for name in {plan['common_instructions_path']} | {
        e[k] for e in plan['episodes'] for k in ['task_path', 'request_path', 'policy_path']
    }:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((UNIT / name).read_bytes())
    return tmp_path


def sized_body(size):
    body = {'input': 'x' * (size - len(loop.encoded({'input': ''})))}
    assert len(loop.encoded(body)) == size
    return body


def test_all_twelve_registered_and_input_equivalent(pilot):
    plan = loop.read(pilot / 'PLAN.json')
    assert len(loop.EPISODE_IDS) == 12
    assert plan['max_final_tables'] == 36
    assert plan['limits']['total_usd_cap'] == 48
    for eid in loop.EPISODE_IDS:
        _, ep, _, instructions, initial, _ = loop.config(pilot, eid)
        assert ep['block'] == ep['constructor_repeat'] == int(eid[-1])
        original = next(e for e in loop.read(UNIT.parent / 'request_only_agent_capacity_2026-11-10/PLAN.json')['episodes']
                        if e['episode_id'] == eid.rsplit('_R', 1)[0])
        old = UNIT.parent / 'request_only_agent_capacity_2026-11-10'
        assert instructions == (old / plan['common_instructions_path']).read_text(encoding='utf-8') + '\n\n' + (old / original['policy_path']).read_text(encoding='utf-8')
        assert initial[0]['content'][0]['text'] == (old / original['request_path']).read_text(encoding='utf-8')
        assert initial[0]['content'][1]['text'].endswith((old / original['task_path']).read_text(encoding='utf-8'))


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'wrong_arm', 'wrong_block'])
def test_bad_matrix_rejected(pilot, mutation):
    plan = loop.read(pilot / 'PLAN.json')
    if mutation == 'missing': plan['episodes'].pop()
    elif mutation == 'duplicate': plan['episodes'][-1] = plan['episodes'][0]
    elif mutation == 'wrong_arm': plan['episodes'][0]['arm'] = 'workflow'
    else: plan['episodes'][0]['block'] = 2
    put(pilot / 'PLAN.json', plan)
    with pytest.raises(loop.IntegrityError): loop.config(pilot, 'PNS_BASE_R1')


@pytest.mark.parametrize('key,value', [('total_usd_cap', 48.01), ('episode_usd_cap', 4.01),
                                     ('max_calls', 49), ('max_input_bytes', 750001)])
def test_limits_not_expanded(pilot, key, value):
    plan = loop.read(pilot / 'PLAN.json'); plan['limits'][key] = value
    put(pilot / 'PLAN.json', plan)
    with pytest.raises(loop.IntegrityError): loop.config(pilot, 'PNS_BASE_R1')


@pytest.mark.parametrize('tokens,factors', [(272000, (1, 1)), (272001, (2, 1.5))])
def test_actual_tariff_threshold(tokens, factors):
    usage = {'input_tokens': tokens, 'output_tokens': 100,
             'input_tokens_details': {'cached_tokens': 1000, 'cache_write_tokens': 500}}
    expected = (((tokens - 1500) * 2 + 1000 * .1 + 500 * 2.5) * factors[0] + 100 * 10 * factors[1]) / 1e6
    assert loop.tariff(usage, loop.DEFAULT_RATES) == pytest.approx(expected)


@pytest.mark.parametrize('size,expected_factor', [(267904, 1), (267905, 2)])
def test_reservation_threshold_and_unknown_usage(pilot, size, expected_factor):
    limits = loop.read(pilot / 'PLAN.json')['limits']
    folder, reason = loop.reserve(pilot, 'PNS_BASE_R1', 1, sized_body(size), limits, loop.DEFAULT_RATES)
    assert reason is None
    reservation = loop.read(folder / 'reservation.json')
    assert reservation['input_rate_multiplier'] == expected_factor
    assert reservation['input_token_allowance'] == size + 4096
    assert loop.accounted(pilot) == pytest.approx(reservation['reserved_usd'])
    assert not (folder / 'receipt.json').exists()


def test_max_body_blocked_by_four_dollar_cap_not_silently_increased(pilot):
    limits = loop.read(pilot / 'PLAN.json')['limits']
    folder, reason = loop.reserve(pilot, 'PNS_BASE_R1', 1, sized_body(750000), limits, loop.DEFAULT_RATES)
    assert folder is None and reason == 'budget_limit'
    assert not (pilot / 'episodes').exists()
    folder, reason = loop.reserve(pilot, 'PNS_BASE_R1', 1, sized_body(750001), limits, loop.DEFAULT_RATES)
    assert folder is None and reason == 'input_byte_limit'


def test_global_cap_counts_all_twelve_reservations(pilot):
    plan = loop.read(pilot / 'PLAN.json')
    # Artificial durable reservations test accounting without model calls.
    for eid in loop.EPISODE_IDS:
        put(pilot / 'episodes' / eid / 'calls/0001/reservation.json',
            {'episode_id': eid, 'reserved_usd': 3.99})
    assert loop.accounted(pilot) == pytest.approx(47.88)
    limits = dict(plan['limits']); limits['episode_usd_cap'] = 10  # isolate the global-gate assertion only
    folder, reason = loop.reserve(pilot, 'PNS_BASE_R1', 2, sized_body(20), limits, loop.DEFAULT_RATES)
    assert folder is None and reason == 'budget_limit'
    assert loop.accounted(pilot) == pytest.approx(47.88)


def operational_gate(pilot, statuses=None):
    plan = loop.read(pilot / 'PLAN.json'); put(pilot / 'LAUNCH_FREEZE.json', {'test': True})
    first = [e for e in plan['episodes'] if e['block'] == 1]
    for index, ep in enumerate(first):
        put(pilot / 'episodes' / ep['episode_id'] / 'OUTCOME.json',
            {'episode_id': ep['episode_id'], 'status': (statuses or ['finalized'] * 4)[index]})
    gate = {'status': 'pass', 'target_comparisons_inspected': False,
            'plan_sha256': loop.sha(pilot / 'PLAN.json'), 'launch_freeze_sha256': loop.sha(pilot / 'LAUNCH_FREEZE.json'),
            'outcome_sha256': {e['episode_id']: loop.sha(pilot / 'episodes' / e['episode_id'] / 'OUTCOME.json') for e in first}}
    put(pilot / 'OPERATIONAL_BLOCK1_REVIEW.json', gate)
    return plan, gate


def test_first_block_can_start_without_gate(pilot):
    plan = loop.read(pilot / 'PLAN.json')
    loop.verify_dispatch_gate(pilot, plan, plan['episodes'][0])


def test_later_block_rejects_absent_gate(pilot):
    plan = loop.read(pilot / 'PLAN.json')
    with pytest.raises(loop.IntegrityError): loop.verify_dispatch_gate(pilot, plan, plan['episodes'][4])


def test_routine_exhaustion_not_reason_to_stop_remaining_matrix(pilot):
    plan, _ = operational_gate(pilot, ['call_limit', 'budget_limit', 'output_token_limit', 'model_stopped_without_finalize'])
    loop.verify_dispatch_gate(pilot, plan, plan['episodes'][4])


@pytest.mark.parametrize('change', ['reference_seen', 'hash_mismatch', 'failed_interface'])
def test_gate_rejects_invalid_operational_review(pilot, change):
    plan, gate = operational_gate(pilot)
    if change == 'reference_seen': gate['target_comparisons_inspected'] = True
    elif change == 'hash_mismatch': gate['plan_sha256'] = 'bad'
    else: put(pilot / 'episodes' / plan['episodes'][0]['episode_id'] / 'OUTCOME.json', {'status': 'uncertain_tool_dispatch'})
    put(pilot / 'OPERATIONAL_BLOCK1_REVIEW.json', gate)
    with pytest.raises(loop.IntegrityError): loop.verify_dispatch_gate(pilot, plan, plan['episodes'][4])


def test_block_three_waits_for_all_block_two_outcomes(pilot):
    plan, _ = operational_gate(pilot)
    with pytest.raises(loop.IntegrityError): loop.verify_dispatch_gate(pilot, plan, plan['episodes'][8])
    for ep in plan['episodes'][4:8]: put(pilot / 'episodes' / ep['episode_id'] / 'OUTCOME.json', {'status': 'call_limit'})
    loop.verify_dispatch_gate(pilot, plan, plan['episodes'][8])


def test_pending_first_block_cell_halts_after_nonroutine_prior_failure(pilot):
    plan = loop.read(pilot / 'PLAN.json')
    put(pilot / 'episodes' / plan['episodes'][0]['episode_id'] / 'OUTCOME.json', {'status': 'runtime_initialization_error'})
    with pytest.raises(loop.IntegrityError): loop.verify_dispatch_gate(pilot, plan, plan['episodes'][2])


@pytest.mark.parametrize('reason,expected', [('max_output_tokens', 'output_token_limit'), ('unknown', 'incomplete_response')])
def test_explicit_output_limit_is_classified_without_retry(pilot, reason, expected):
    limits = loop.read(pilot / 'PLAN.json')['limits']
    folder, _ = loop.reserve(pilot, 'PNS_BASE_R1', 1, {'input': []}, limits, loop.DEFAULT_RATES)
    class Response:
        status_code = 200; headers = {}
        def iter_content(self, *args):
            yield loop.encoded({'model': loop.MODEL, 'status': 'incomplete', 'incomplete_details': {'reason': reason},
                                'output': [], 'usage': {'input_tokens': 1, 'output_tokens': 2}})
        def close(self): pass
    receipt, _ = loop.send_once(folder, lambda *a, **kw: Response(), {}, [], loop.DEFAULT_RATES)
    assert receipt['status'] == expected
    assert loop.accounted(pilot) == pytest.approx(.000022)


def evaluation_fixture(pilot, monkeypatch, n=12):
    monkeypatch.setattr(evaluator, 'ROOT', pilot)
    plan = loop.read(pilot / 'PLAN.json')
    for ep in plan['episodes'][:n]:
        put(pilot / 'episodes' / ep['episode_id'] / 'OUTCOME.json',
            {'episode_id': ep['episode_id'], 'selected_candidate': None, 'status': 'call_limit',
             'calls_reserved': 2, 'known_tariff_cost_usd': .2, 'accounted_usd': .3})
    return plan


def test_closure_cannot_ignore_twelfth_constructor(pilot, monkeypatch):
    evaluation_fixture(pilot, monkeypatch, n=11)
    with pytest.raises(FileNotFoundError): evaluator.close()
    assert not (pilot / 'CONSTRUCTION_CLOSURE.json').exists()


def test_twelve_failed_constructors_preserve_thirtysix_slots(pilot, monkeypatch):
    plan = evaluation_fixture(pilot, monkeypatch)
    evaluator.close()
    def forbidden(*args, **kwargs): raise RuntimeError('No failed runtime or real patient read allowed')
    monkeypatch.setattr(evaluator.runtime, 'ToolRuntime', forbidden)
    slots = evaluator.draw()
    assert len(slots) == 36 and all(s['status'] == 'unavailable' for s in slots)
    snapshot = pilot / '_host/synthetic_reference.json'
    put(snapshot, {'references': {case: {'fixture': {'unit': 'fictional', 'value': 123}} for case in ['PNS', 'lipids']}})
    monkeypatch.setattr(evaluator, 'SNAPSHOT', snapshot); monkeypatch.setattr(evaluator, 'SNAPSHOT_SHA', evaluator.sha(snapshot))
    result = evaluator.evaluate()
    assert result['counts']['episodes'] == 12 and result['counts']['final_slots'] == 36
    assert result['counts']['unavailable_tables'] == 36 and result['counts']['model_calls'] == 24
    assert result['costs']['accounted_usd'] == pytest.approx(3.6)
    assert all(s['mean'] is None for s in evaluator.read(pilot / 'EVALUATION.json')['summaries'])


def test_scientific_runtime_and_inputs_byte_identical():
    unchanged = loop.read(UNIT / 'UNCHANGED_SCIENTIFIC_INPUTS.json')
    for name, digest in unchanged['shared_files'].items():
        assert loop.sha(UNIT / name) == digest
        assert (UNIT / name).read_bytes() == (Path(unchanged['predecessor']) / name).read_bytes()


def test_cli_preserves_unstarted_cells_without_fabricating_author_outcomes(pilot, monkeypatch):
    plan = loop.read(pilot / 'PLAN.json')
    monkeypatch.setattr(loop, 'ROOT', pilot)
    monkeypatch.setattr(sys, 'argv', ['api_loop.py', '--block', '1'])
    def stop_before_dispatch(eid):
        raise loop.IntegrityError('Fixture nonroutine failure; no HTTP')
    monkeypatch.setattr(loop, 'run_episode', stop_before_dispatch)
    with pytest.raises(SystemExit) as stopped: loop.main()
    assert stopped.value.code == 2
    receipt = loop.read(pilot / 'DISPATCH_BLOCK_1.json')
    assert len(receipt['episodes']) == 4
    assert all(r['dispatch_status'] == 'not_started_due_protocol_stop' and r['calls_reserved'] == 0 for r in receipt['episodes'])
    assert not (pilot / 'episodes').exists()
    with pytest.raises(loop.IntegrityError, match='already has a dispatch receipt'): loop.main()
