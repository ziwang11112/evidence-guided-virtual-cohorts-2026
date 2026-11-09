"""New-controller integration on invented rows; no clinical reference access."""
from copy import deepcopy
import json

import pytest

from cohort_harness import adaptive_session_v2 as session
from cohort_harness import descriptive_feedback_v1 as descriptive
from cohort_harness import web_evidence_v1 as web
from cohort_harness.lifecycle import read_json, sha256
from test_adaptive_session_v1 import fixture as old_fixture
from test_whole_cohort_feedback import write


def fixture(tmp_path):
    root, candidate, config = old_fixture(tmp_path, seeds=(11, 12))
    task = read_json(root / 'task.json')
    task['information_policy']['allowed_tools'].append('web.fetch')
    write(root / 'task.json', task)
    request = read_json(root / 'request.json'); request['task'] = task
    write(root / 'request.json', request)
    config.update(schema_version=2, web_evidence={'http_requests': 4})
    binding = read_json(candidate / 'source_semantics_v1.json')['bindings'][0]
    operator = deepcopy(binding['source_operator'])
    check = {
        'id': 'descriptive_mean', 'evidence_id': binding['evidence_id'],
        'source_locator': binding['source_locator'], 'operator': operator,
        'conventions': {'weighting': 'equal', 'sd_ddof': None,
                        'quantile_method': None, 'spearman_ties': None},
        'source_definition': {'definition_status': 'not_reported', 'source_operator': None,
             'weights': 'not_reported', 'transform': 'identity', 'source_variable_units': {},
             'reason': 'Invented source conventions unresolved.'},
        'assumption_ids': ['A_fixture'],
        'applicability': {'status': 'explicit_transfer_assumption', 'reason': 'Invented contexts.'},
        'reason': 'Calculate a conventional descriptive analogue.'}
    write(candidate / descriptive.FILE, {'schema_version': 1,
          'evidence_sha256': sha256(candidate / 'evidence.json'), 'checks': [check]})
    return root, candidate, config


def act(root, key, kind, **kwargs):
    return session.dispatch(root, key, {'kind': kind, **kwargs})


def test_both_feedback_layers_and_complete_seed_schedule(tmp_path):
    root, candidate, config = fixture(tmp_path)
    assert session.create_session(root, config)['status'] == 'active'
    assert act(root, 'submit', 'submit', candidate='initial')['status'] == 'success'
    for seed in (11, 12):
        run = 'r' + str(seed)
        assert act(root, run, 'execute', candidate='initial', run_id=run, seed=seed)['status'] == 'success'
        reply = act(root, run+'f', 'feedback', candidate='initial', run_id=run, feedback_id=run+'f')
        assert reply['status'] == 'success', reply
        assert reply['result']['strict']['n_computable'] == 5
        check = reply['result']['descriptive']['checks'][0]
        assert check['calculation']['value'] == pytest.approx(0)
        assert check['source_definition_match']['status'] == 'assumed_convention'
        assert (root / 'semantic_feedback_v1' / (run+'f') / 'feedback.json').exists()
        assert (root / 'descriptive_feedback_v1' / (run+'f') / 'feedback.json').exists()
        assert act(root, run+'a', 'analysis', candidate='initial', run_id=run,
                   adapter='generated', analysis_id=run+'a')['status'] == 'success'
        if seed == 11:
            with pytest.raises(ValueError, match='scheduled seed'):
                act(root, 'early', 'finish', final_candidate='initial', reason='Incomplete')
    assert act(root, 'finish', 'finish', final_candidate='initial', reason='Inspect all outputs')['session_status'] == 'completed'
    assert session.verify_session(root)['status'] == 'completed'


def test_new_plan_is_required_before_freezing(tmp_path):
    root, candidate, config = fixture(tmp_path)
    (candidate / descriptive.FILE).unlink()
    session.create_session(root, config)
    result = act(root, 'bad', 'preflight', candidate='initial')
    assert result['status'] == 'error' and result['session_status'] == 'active'
    assert not (candidate / 'freeze.json').exists()


def test_web_dispatch_binds_state_and_refuses_reset(tmp_path):
    root, _, config = fixture(tmp_path)
    session.create_session(root, config)
    # No request is sent for a loopback target. The rejected action is retained.
    result = act(root, 'blocked', 'web_evidence', url='https://127.0.0.1/a',
                 source_id='official', purpose='Invented metadata check', source_type='official_website')
    assert result['status'] == 'error'
    assert result['session_status'] == 'active', result
    assert session.verify_session(root)['usage']['actions'] == 1
    state = root / 'web_evidence_v1/state.json'
    state.write_bytes(state.read_bytes() + b'\n')
    with pytest.raises(ValueError, match='Gateway bytes changed'):
        session.verify_session(root)


def test_descriptive_feedback_tamper_is_detected(tmp_path):
    root, _, config = fixture(tmp_path)
    session.create_session(root, config)
    act(root, 's', 'submit', candidate='initial')
    act(root, 'r', 'execute', candidate='initial', run_id='r', seed=11)
    act(root, 'f', 'feedback', candidate='initial', run_id='r', feedback_id='f')
    report = root / 'descriptive_feedback_v1/f/feedback.json'
    data = read_json(report); data['checks'][0]['calculation']['value'] = 99
    write(report, data)
    with pytest.raises(ValueError, match='Action artifact changed'):
        session.verify_session(root)


@pytest.mark.parametrize('reason', ['task_or_provenance_violation', 'interrupted_command', 'local_or_parser_failure'])
def test_internal_web_failures_halt_instead_of_masquerading_as_search_failure(tmp_path, monkeypatch, reason):
    root, _, config = fixture(tmp_path)
    session.create_session(root, config)
    monkeypatch.setattr(web, 'fetch', lambda *a, **k: {'status': 'error', 'reason': reason})
    result = act(root, 'internal', 'web_evidence', url='https://example.org/a',
                 source_id='official', purpose='Invented check', source_type='official_website')
    assert result['session_status'] == 'halted'
    assert session.verify_session(root)['status'] == 'halted'


@pytest.mark.parametrize('reason', ['encrypted_pdf_unsupported', 'pdf_page_limit'])
def test_unavailable_pdf_allows_another_source(reason):
    assert session._outcome({'kind': 'web_evidence'}, {'status': 'error', 'reason': reason}) == ('error', 'active')
