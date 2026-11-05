"""Focused controller review with synthetic state only.

No generator, patient table, reference artifact or old run is opened. The only
prepared inputs read are this unit's protocol/endpoint metadata and new tasks.
"""
from contextlib import nullcontext
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import runner as r
import evaluator as ev
import controller_evidence_use as use
import lipid_provider as lipid
from cohort_harness.contracts import ContractError


def protocol():
    return {
        'authors': {name: {'bundle': str(ROOT / ('fake_' + name)),
                          'case_id': 'ENSANUT2018' if name[0] == 'H' else 'Turkana'}
                    for name in ('H01', 'H02', 'H03', 'L01', 'L02', 'L03')},
        'trial_seeds': {'initial': 9100, 'revision': 9110},
        'final_seeds': [9101, 9102, 9103],
        'max_physical_executions': 30, 'max_feedback_revisions': 1,
        'feedback_adapter': 'semantic_feedback_v1', 'evidence_use_adapter': 'evidence_use_v1',
        'limits': {'timeout_seconds': 30, 'memory_mb': 1536,
                   'output_bytes': 20000000, 'log_bytes': 100000},
    }


def fake_session(tmp_path, events=()):
    s = object.__new__(r.Session)
    s.p = protocol()
    s.author = 'H01'
    s.bundle = tmp_path / 'bundle'
    s.bundle.mkdir(exist_ok=True)
    s.folder = tmp_path / 'session'
    s.folder.mkdir(exist_ok=True)
    s.spec = {'analysis_ids': ['a'], 'case_id': 'ENSANUT2018'}
    s.contract = {'external_author_id': 'fresh-author'}
    ledger = deepcopy(list(events))
    s.events = lambda: ledger
    s.lock = lambda: nullcontext()
    def add(kind, **data):
        record = {'index': len(ledger) + 1, 'kind': kind, **data}
        ledger.append(record)
        return record
    s.add = add
    return s


def test_fixed_protocol_counts_seeds_and_adapters(monkeypatch):
    p = protocol()
    monkeypatch.setattr(r, 'READ', lambda _: p)
    assert r.protocol() is p
    for change in (
        lambda q: q['authors'].pop('H03'),
        lambda q: q['authors']['H03'].update(case_id='Turkana'),
        lambda q: q['trial_seeds'].update(initial=9200),
        lambda q: q.update(final_seeds=[9103, 9102, 9101]),
        lambda q: q.update(max_physical_executions=31),
        lambda q: q.update(feedback_adapter='legacy'),
    ):
        altered = deepcopy(p)
        change(altered)
        monkeypatch.setattr(r, 'READ', lambda _, q=altered: q)
        with pytest.raises(ContractError):
            r.protocol()


@pytest.mark.parametrize('queries,downloads,new_sources', [(5, 0, 0), (0, 3, 0), (0, 0, 3)])
def test_acquisition_caps_before_commit(tmp_path, monkeypatch, queries, downloads, new_sources):
    monkeypatch.setattr(r, 'ROOT', tmp_path)
    bundle = tmp_path / 'bundle'
    bundle.mkdir()
    (bundle / 'SEARCH_LEDGER.json').write_text('{}')
    p = protocol()
    p['authors']['H01'].update(bundle=str(bundle), curated_source_ids=['c1', 'c2', 'c3', 'c4'])
    monkeypatch.setattr(r, 'ensure_control', lambda: p)
    monkeypatch.setattr(r.lifecycle, '_bundle', Path)
    monkeypatch.setattr(r.lifecycle, '_registry', lambda _: None)
    monkeypatch.setattr(r, 'validate_task', lambda _: None)
    contents = {
        'task.json': {'mode': 'whole_cohort', 'n_rows': 3000,
                      'budget': {'source_queries': 4, 'source_downloads': 2, 'revisions': 1}},
        'registry.json': {'artifacts': [{'source_id': x} for x in
                         ['c1', 'c2', 'c3', 'c4'] + [f'n{i}' for i in range(new_sources)]]},
        'state.json': {'usage': {'queries': queries, 'downloads': downloads}},
    }
    monkeypatch.setattr(r, 'READ', lambda path: contents[Path(path).name])
    with pytest.raises(ContractError, match='cap|budget'):
        r.initialize('H01', 'fresh-author')
    assert not (tmp_path / 'sessions').exists()


def test_failed_adapter_consumes_trial_and_blocks_retry(tmp_path, monkeypatch):
    s = fake_session(tmp_path, [{'kind': 'freeze', 'stage': 'initial', 'candidate': 'candidates/initial'}])
    monkeypatch.setattr(r.lifecycle, 'verify_candidate', lambda *_: {})
    calls = []
    def fail(*args, **kwargs):
        calls.append(args)
        raise RuntimeError('synthetic backend failure')
    monkeypatch.setattr(r.execution, 'run_candidate', fail)
    result = s._run('candidates/initial', 'trial', 'initial', 9100)
    assert result['status'] == 'adapter_error'
    assert s.selected('attempt')[0]['charged'] is True
    with pytest.raises(ContractError, match='Slot consumed'):
        s._run('candidates/initial', 'trial', 'initial', 9100)
    assert len(calls) == 1


def decision_state(tmp_path, monkeypatch, selected='candidates/initial', initial_ok=True):
    events = [
        {'kind': 'freeze', 'stage': 'initial', 'candidate': 'candidates/initial', 'freeze_sha256': 'fi'},
        {'kind': 'freeze', 'stage': 'revision', 'candidate': 'candidates/revision', 'freeze_sha256': 'fr'},
        {'kind': 'attempt', 'index': 3, 'purpose': 'trial', 'stage': 'initial', 'candidate': 'candidates/initial', 'run_id': 'i'},
        {'kind': 'result', 'attempt_index': 3, 'status': 'success' if initial_ok else 'adapter_error',
         'receipt': {'sha256': 'receipt'} if initial_ok else None, 'table': {'sha256': 'table'} if initial_ok else None},
        {'kind': 'attempt', 'index': 5, 'purpose': 'trial', 'stage': 'revision', 'candidate': 'candidates/revision', 'run_id': 'v'},
        {'kind': 'result', 'attempt_index': 5, 'status': 'adapter_error', 'receipt': None, 'table': None},
    ]
    if initial_ok:
        events.append({'kind': 'feedback', 'run_id': 'i', 'feedback': {'sha256': 'feedback-i'}})
    s = fake_session(tmp_path, events)
    decision = {'author_id': 'H01', 'candidate': selected, 'reason': 'Documented trial finding',
                'action': 'retain' if selected.endswith('initial') else 'revise',
                'feedback_hashes': {'i': 'feedback-i'} if initial_ok else {}}
    review = {'approved': True, 'scientific_code_spec_consistency': True,
              'finite_moments_supported': True, 'source_semantics_reviewed': True,
              'target_results_used': False, 'reviewer_id': 'independent-reviewer',
              'candidate_freeze_sha256': 'fi' if selected.endswith('initial') else 'fr',
              'decision_sha256': 'decision-hash'}
    monkeypatch.setattr(r, 'READ', lambda path: decision if Path(path).name == 'decision.json' else review)
    monkeypatch.setattr(r, 'SHA', lambda _: 'decision-hash')
    monkeypatch.setattr(r, 'bound', lambda path: {'path': str(path), 'sha256': 'decision-hash'})
    return s, decision


@pytest.mark.parametrize('selected,initial_ok', [('candidates/revision', True), ('candidates/initial', False)])
def test_failed_candidate_cannot_be_final(tmp_path, monkeypatch, selected, initial_ok):
    s, _ = decision_state(tmp_path, monkeypatch, selected, initial_ok)
    with pytest.raises(ContractError, match='successful verified trial'):
        s.decide(tmp_path / 'decision.json', tmp_path / 'review.json')
    assert not s.selected('decision')


def test_valid_initial_fallback_binds_feedback_and_closes_science(tmp_path, monkeypatch):
    s, decision = decision_state(tmp_path, monkeypatch)
    decision['feedback_hashes'] = {}
    with pytest.raises(ContractError, match='every actual feedback'):
        s.decide(tmp_path / 'decision.json', tmp_path / 'review.json')
    decision['feedback_hashes'] = {'i': 'feedback-i'}
    assert s.decide(tmp_path / 'decision.json', tmp_path / 'review.json')['action'] == 'retain'
    with pytest.raises(ContractError, match='phase closed'):
        s.open_science()


def test_three_final_slots_never_retry_or_modify_after_delivery(tmp_path, monkeypatch):
    s = fake_session(tmp_path, [{'kind': 'decision', 'candidate': 'candidates/initial'}])
    monkeypatch.setattr(r.lifecycle, 'verify_candidate', lambda *_: {})
    calls = []
    def fail(*args, **kwargs):
        calls.append(args[3])
        raise RuntimeError('synthetic execution failure')
    monkeypatch.setattr(r.execution, 'run_candidate', fail)
    assert s.deliver()['kind'] == 'closed'
    assert calls == [9101, 9102, 9103]
    assert len(s.selected('attempt')) == 3
    with pytest.raises(ContractError, match='terminally closed'):
        s.deliver()
    with pytest.raises(ContractError, match='phase closed'):
        s.open_science()


def test_prefreeze_gates_precede_freeze_and_enforce_program_route(tmp_path, monkeypatch):
    s = fake_session(tmp_path)
    candidate = s.bundle / 'candidates/initial'
    candidate.mkdir(parents=True)
    (candidate / 'generator.py').write_text('# synthetic inert bytes; never imported')
    calls = []
    monkeypatch.setattr(r.lifecycle, '_candidate', lambda *_: (candidate, 'candidates/initial'))
    monkeypatch.setattr(r.lifecycle, '_files', lambda _: [])
    monkeypatch.setattr(r, 'READ', lambda _: {'candidate': 'candidates/initial', 'candidate_files': {}})
    s._review_flags = lambda _: None
    monkeypatch.setattr(r, 'validate_candidate_use', lambda *a, **k: calls.append('evidence_use') or {})
    monkeypatch.setattr(r.semantic, 'preflight', lambda *_: calls.append('semantic') or {})
    monkeypatch.setattr(r.lifecycle, 'freeze_candidate', lambda *a, **k: calls.append('freeze') or {'revision_index': 0, 'route': 'generator.py'})
    monkeypatch.setattr(r, 'SHA', lambda _: 'synthetic')
    monkeypatch.setattr(r, 'bound', lambda _: {})
    s.freeze('initial', review=tmp_path / 'review.json')
    assert calls == ['evidence_use', 'semantic', 'freeze']
    (candidate / 'generated.csv').write_text('inert artifact, no patient rows')
    with pytest.raises(ContractError, match='program route'):
        s.freeze('initial', review=tmp_path / 'review.json')


def test_verify_rechecks_both_gates(tmp_path, monkeypatch):
    s = fake_session(tmp_path, [{'kind': 'freeze', 'stage': 'initial', 'candidate': 'candidates/initial',
        'freeze_sha256': 'synthetic', 'evidence_use_report': {'gate': 'use'},
        'semantic_preflight': {'gate': 'semantic'}, 'output_route': 'generator.py'}])
    s.contract.update(control_sha256='synthetic', inputs_sha256='synthetic')
    monkeypatch.setattr(r, 'ensure_control', lambda: s.p)
    monkeypatch.setattr(r, 'SHA', lambda _: 'synthetic')
    monkeypatch.setattr(r, 'READ', lambda _: {'root_files': [], 'protected_trees': [], 'files': {}})
    monkeypatch.setattr(r.lifecycle, 'verify_candidate', lambda *_: {'route': 'generator.py', 'revision_index': 0, 'parent': None})
    calls = []
    monkeypatch.setattr(r, 'validate_candidate_use', lambda *a, **k: calls.append('use') or {'gate': 'use'})
    monkeypatch.setattr(r.semantic, 'preflight', lambda *_: calls.append('semantic') or {'gate': 'semantic'})
    assert s.verify() is True
    assert calls == ['use', 'semantic']
    monkeypatch.setattr(r.semantic, 'preflight', lambda *_: {'gate': 'changed'})
    with pytest.raises(ContractError, match='Semantic preflight report changed'):
        s.verify()


def test_revision_retains_actual_initial_feedback_bytes(tmp_path):
    s = fake_session(tmp_path, [
        {'kind': 'attempt', 'purpose': 'trial', 'stage': 'initial', 'run_id': 'i'},
        {'kind': 'attempt', 'purpose': 'trial', 'stage': 'revision', 'run_id': 'v'}])
    candidate = s.bundle / 'candidates/revision'
    candidate.mkdir(parents=True)
    report = candidate / 'initial_feedback.json'
    report.write_text('{"synthetic_feedback": true}')
    digest = r.SHA(report)
    s.add('feedback', run_id='i', feedback={'sha256': digest})
    s.add('feedback', run_id='v', feedback={'sha256': 'later-revision-feedback'})
    checks = candidate / 'checks.json'
    checks.write_text('{"artifacts": []}')
    with pytest.raises(ContractError, match='every actual initial feedback'):
        s._revision_feedback_artifacts(candidate)
    checks.write_text(json.dumps({'artifacts': [{'path': report.name, 'sha256': digest}]}))
    s._revision_feedback_artifacts(candidate)
    report.write_text('{"synthetic_feedback": false}')
    with pytest.raises(ContractError, match='artifact changed'):
        s._revision_feedback_artifacts(candidate)


def test_evidence_use_cannot_substitute_actual_task(tmp_path, monkeypatch):
    candidate = tmp_path / 'candidates/initial'
    candidate.mkdir(parents=True)
    manifest = {'bindings': {role: {'path': ('wrong-task.json' if role == 'task' else
                'candidates/initial/' + ('generator.py' if role == 'generator' else role + '.json'))}
                for role in ('task', 'evidence', 'model_spec', 'analysis_evidence', 'checks', 'generator')}}
    (candidate / 'evidence_use_v1.json').write_text(json.dumps(manifest))
    with pytest.raises(ContractError, match='different actual input: task'):
        use.validate_candidate_use(tmp_path, 'candidates/initial', ['a'])


def test_batch_requires_all_six_closed_and_preserves_30_attempt_bound(tmp_path, monkeypatch):
    p = protocol()
    monkeypatch.setattr(r, 'ensure_control', lambda: p)
    monkeypatch.setattr(r, 'SHA', lambda _: 'synthetic')
    sessions = {}
    for name in p['authors']:
        folder = tmp_path / name
        folder.mkdir()
        events = [{'kind': 'attempt'} for _ in range(5)] + [{'kind': 'closed'}]
        sessions[name] = SimpleNamespace(folder=folder, verify=lambda: True,
            selected=lambda kind, es=events: [x for x in es if x['kind'] == kind],
            events=lambda es=events: es, status=lambda: {'closed': True})
    monkeypatch.setattr(r, 'Session', lambda author: sessions[author])
    assert r.batch_state()['physical_attempts'] == 30
    sessions['L03'].events().pop()
    with pytest.raises(ContractError, match='All six authors'):
        r.batch_state()
    sessions['L03'].events().extend([{'kind': 'attempt'}, {'kind': 'closed'}])
    with pytest.raises(ContractError, match='Global physical attempt budget'):
        r.batch_state()


def test_reference_loading_requires_six_closures_before_any_read(monkeypatch):
    calls = []
    def blocked():
        calls.append('gate')
        raise ContractError('All six authors must terminally close')
    monkeypatch.setattr(r, 'closure_gate', blocked)
    monkeypatch.setattr(r, 'READ', lambda _: pytest.fail('Read before closure'))
    monkeypatch.setattr(r, 'verify_bound', lambda _: pytest.fail('Reference hash read before closure'))
    with pytest.raises(ContractError, match='six authors'):
        ev.evaluate()
    with pytest.raises(ContractError, match='six authors'):
        ev.load_references({}, {})
    assert calls == ['gate', 'gate']


def test_reference_selector_mapping_with_synthetic_aggregates(monkeypatch):
    schema = {'ENSANUT2018': {'analyses': [{'id': 'h', 'unit': '%'}], 'diagnostics': []},
              'Turkana': {'analyses': [{'id': 'l', 'unit': 'mg/dL per 5 kg/m^2'}],
                         'diagnostics': [{'id': 'total_cholesterol.sd_sample', 'unit': 'mg/dL'},
                                         {'id': 'hdl_cholesterol.sd_sample', 'unit': 'mg/dL'},
                                         {'id': 'age.mean', 'unit': 'year'}]}}
    fixtures = {'fake-h': {'references': {'ENSANUT2018': {'h': {'value': 2., 'unit': '%'}}}},
                'fake-l': {'references': {'K02': {
                    'estimands': {'l': {'estimate': 7., 'unit': 'mg/dL per 5 kg/m^2',
                                       'status': 'computed', 'interval': {'status': 'unavailable'}}},
                    'metric_denominators': {'total_cholesterol': {'sample_sd': 4.},
                                            'hdl_cholesterol': {'sample_sd': 3.}}}}}}
    p = {'references': {'ENSANUT2018': {'path': 'fake-h', 'selector': ['references', 'ENSANUT2018']},
                        'Turkana': {'path': 'fake-l', 'selector': ['references', 'K02']}}}
    monkeypatch.setattr(r, 'closure_gate', lambda: {})
    monkeypatch.setattr(r, 'verify_bound', lambda _: None)
    monkeypatch.setattr(r, 'READ', lambda path: fixtures[path])
    refs = ev.load_references(p, schema)
    assert refs['ENSANUT2018']['h']['value'] == 2.
    assert refs['Turkana']['l']['value'] == 7.
    assert refs['Turkana']['total_cholesterol.sd_sample']['value'] == 4.
    assert refs['Turkana']['hdl_cholesterol.sd_sample']['value'] == 3.
    assert refs['Turkana']['age.mean']['status'] == 'unavailable'
    assert refs['Turkana']['age.mean']['value'] is None


def test_prepared_metadata_endpoint_inventory_and_dependencies(monkeypatch):
    # Actual new metadata is allowed; never open either referenced aggregate.
    p = json.loads((ROOT / 'PROTOCOL.json').read_text(encoding='utf-8-sig'))
    schema = json.loads((ROOT / 'ENDPOINT_CONTRACT.json').read_text(encoding='utf-8-sig'))['cases']
    files = set(r.control_files(p))
    assert ROOT / 'ENDPOINT_CONTRACT.json' in files
    assert ROOT / 'controller_evidence_use.py' in files
    assert ROOT / 'lipid_provider.py' in files
    for path in p['dependencies']:
        assert Path(path).resolve() in files
    for author in p['authors'].values():
        task = json.loads((Path(author['bundle']) / 'task.json').read_text(encoding='utf-8-sig'))
        assert task['mode'] == 'whole_cohort' and task['n_rows'] == 3000
        assert task['budget'] == {'source_queries': 4, 'source_downloads': 2, 'revisions': 1}
        assert set(author['analysis_ids']) == {x['id'] for x in schema[author['case_id']]['analyses']}
        assert not (Path(author['bundle']) / 'observed.csv').exists()
    # Tiny explicitly artificial input checks provider/contract spelling; no generator runs.
    frame = pd.DataFrame({'id': ['a', 'b', 'c', 'd'], 'age': [20., 30., 40., 60.],
                          'sex': ['F', 'M', 'F', 'M'], 'bmi': [20., 23., 24., 22.],
                          'total_cholesterol': [3., 4., 5., 6.], 'hdl_cholesterol': [1., 2., 1., 2.]})
    estimates = {x['id']: {'estimate': 0., 'unit': x['unit']} for x in schema['Turkana']['analyses']}
    monkeypatch.setattr(lipid, '_module', lambda: SimpleNamespace(analyze_frame=lambda *a, **k:
                       {'selection': {'eligible_rows': 4}, 'estimands': estimates}))
    payload = lipid.generated_statistics(frame, expected_rows=4)
    ev.validate(payload, schema['Turkana'])

