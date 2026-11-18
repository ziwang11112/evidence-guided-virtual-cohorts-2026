"""New mechanical-boundary fixtures only; no network, models or generators."""
from pathlib import Path
import hashlib
import importlib.util
import json

UNIT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('independent_repaired_runtime', UNIT / 'tools_runtime.py')
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


def engine(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Network or author execution forbidden')
    monkeypatch.setattr(runtime.gateway, 'http_get', forbidden)
    monkeypatch.setattr(runtime.execution, '_capture', forbidden)
    task = json.loads((UNIT / 'tasks/PNS.json').read_text(encoding='utf-8'))
    limits = json.loads((UNIT / 'PLAN.json').read_text(encoding='utf-8'))['limits']
    return runtime.ToolRuntime(tmp_path, task, limits)


def cache(e, record):
    path = e.root / 'sources/search_0001.json'
    runtime.write_new(path, record)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    e.state['searches']['search_0001'] = {'path': 'sources/search_0001.json', 'sha256': digest}
    e._save()
    return digest


def read_all(e, source_id, section):
    cursor, parts = 0, []
    while True:
        page = e.dispatch('read_source', {'source_id': source_id, 'section': section, 'cursor': cursor})
        assert page['status'] == 'ok' and page.get('network_used') is False
        parts.append(page['content'])
        if page['next_cursor'] is None:
            return ''.join(parts), page
        assert page['next_cursor'] > cursor
        cursor = page['next_cursor']


def test_compact_cards_recover_every_original_record_without_http(tmp_path, monkeypatch):
    e = engine(tmp_path, monkeypatch)
    records = [{'title': 'Complete title ' + str(i), 'pmcid': 'PMC' + str(100 + i),
                'pubYear': '2021', 'source': 'MED', 'id': str(1000 + i),
                'abstractText': 'Multilingual é α evidence. ' * 100,
                'authorList': ['large unprojected metadata ' * 100]} for i in range(10)]
    records[3]['title'] = 'An exceptionally long but fully recoverable title ' * 1000
    record = {'accepted': records, 'next_cursor': 'provider_cursor_2',
              'total_hit_count': 12345, 'retrieved_count': 10, 'rejected_count': 0}
    digest = cache(e, record)
    cursor, cards = 0, []
    while True:
        page = e.dispatch('read_source', {'source_id': 'search_0001', 'cursor': cursor})
        assert page['status'] == 'ok'
        assert page['cache_sha256'] == digest and page['next_query_cursor'] == 'provider_cursor_2'
        assert len(json.dumps(page, ensure_ascii=False, separators=(',', ':')).encode()) <= e.limits['page_chars']
        cards.extend(page['hits'])
        if page['next_cursor'] is None:
            break
        assert page['next_cursor'] > cursor
        cursor = page['next_cursor']
    assert [c['hit_id'] for c in cards] == [f'hit_0001_{i:03d}' for i in range(1, 11)]
    assert cards[3]['identity_complete'] is False
    for card, original in zip(cards, records):
        text, metadata = read_all(e, card['hit_id'], 'metadata')
        assert json.loads(text) == original
        assert hashlib.sha256(text.encode()).hexdigest() == card['record_sha256'] == metadata['record_sha256']
        assert metadata['cache_sha256'] == digest
        if card['identity_complete']:
            assert card['title'] == original['title']
            assert card['abstract_complete'] is False
            assert original['abstractText'].startswith(card['abstract_preview'])
    assert e.state['gateway_usage'] == {}


def test_full_abstract_and_identity_are_recoverable_not_scientifically_summarized(tmp_path, monkeypatch):
    e = engine(tmp_path, monkeypatch)
    abstract = 'Exact printed expression <i>r</i>=0.123; no host interpretation. ' * 250
    title = 'A complete title ' * 1500
    original = {'title': title, 'abstractText': abstract, 'doi': '10.1234/example', 'source': 'MED', 'id': '123456'}
    cache(e, {'accepted': [original], 'next_cursor': None, 'total_hit_count': 1, 'retrieved_count': 1, 'rejected_count': 0})
    recovered, _ = read_all(e, 'hit_0001_001', 'abstract')
    identity, _ = read_all(e, 'hit_0001_001', 'identity')
    assert recovered == abstract and json.loads(identity)['title'] == title


def test_spec_with_task_and_model_keys_is_neither_wrapped_nor_unwrapped(tmp_path, monkeypatch):
    e = engine(tmp_path, monkeypatch)
    submitted = {'model': {'nested': {'value': 3.25}}, 'task': {'author_metadata': True},
                 'unrelated': [None, False, {'text': 'é'}]}
    result = e.dispatch('submit_candidate', {'generator_py': 'def generate(observed, spec, seed):\n    return None\n',
        'model_spec': submitted})
    assert result['status'] == 'stored' and result['executed'] is False
    path = e.root / 'candidates/v001/model_spec.json'
    assert json.loads(path.read_text(encoding='utf-8')) == submitted
    assert hashlib.sha256(path.read_bytes()).hexdigest() == result['model_spec_sha256']
    assert e.usage['executions'] == 0
