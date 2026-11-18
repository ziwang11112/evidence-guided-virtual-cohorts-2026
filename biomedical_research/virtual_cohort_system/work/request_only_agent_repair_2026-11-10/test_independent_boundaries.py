"""Independent integration fixtures: no live HTTP, credentials, or generator execution."""
import importlib.util
import json
from pathlib import Path
import shutil

import pytest

UNIT = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


loop = module('independent_request_loop', UNIT / 'api_loop.py')
runtime = module('independent_request_tools', UNIT / 'tools_runtime.py')


@pytest.fixture
def pilot(tmp_path):
    shutil.copy2(UNIT / 'PLAN.json', tmp_path / 'PLAN.json')
    for folder in ('tasks', 'policies', 'requests'):
        shutil.copytree(UNIT / folder, tmp_path / folder)
    return tmp_path


def test_actual_case_inputs_are_equal_before_policy(pilot):
    for case in ('PNS', 'LIPID'):
        a = loop.config(pilot, case + '_BASE')
        b = loop.config(pilot, case + '_WORKFLOW')
        assert a[2] == b[2] and a[4] == b[4] and a[5] == b[5]
        common = (pilot / 'policies/common.txt').read_text(encoding='utf-8')
        assert a[3] == common + '\n\n' + (pilot / 'policies/ordinary.txt').read_text(encoding='utf-8')
        assert b[3] == common + '\n\n' + (pilot / 'policies/workflow.txt').read_text(encoding='utf-8')
        serialized = json.dumps(a[4])
        for forbidden in ('evidence.json', 'REFERENCE_SNAPSHOT', 'reference_weighted', 'model_spec.json', '54001', '54003', '54007'):
            assert forbidden not in serialized


class Response:
    status_code = 200
    headers = {'x-request-id': 'offline-integration-fixture'}

    def __init__(self, output, number):
        self.raw = loop.encoded({'id': 'response_fixture_' + str(number), 'model': loop.MODEL,
            'status': 'completed', 'output': output,
            'usage': {'input_tokens': 1000, 'output_tokens': 100,
                'input_tokens_details': {'cached_tokens': 100, 'cache_write_tokens': 200},
                'output_tokens_details': {'reasoning_tokens': 75}}})

    def iter_content(self, _):
        yield self.raw

    def close(self):
        pass


def test_actual_loop_and_runtime_select_exact_version_after_failed_trial(pilot, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Live network, credential helper, or generator process is forbidden in fixture')

    monkeypatch.setattr(loop, 'load_module', forbidden)
    monkeypatch.setattr(runtime.gateway, 'http_get', forbidden)
    monkeypatch.setattr(runtime.execution, '_capture', forbidden)
    calls = []
    runs = []
    program = 'def generate(observed, spec, seed):\n    return None\n'
    actions = [
        ('submit_candidate', {'generator_py': program, 'model_spec': {'fixture_version': 1}}),
        ('run_candidate', {'candidate_id': 'v001'}),
        ('submit_candidate', {'generator_py': program, 'model_spec': {'fixture_version': 2}}),
        ('finalize', {'candidate_id': 'v001', 'reason': 'Explicitly select earlier version'})]

    def fake_execution(candidate, task, seed, run, limits):
        runs.append((candidate.name, seed))
        return {'status': 'failed', 'candidate_id': candidate.name, 'seed': seed,
            'statistics': None, 'error': {'type': 'FixtureFailure'}, 'target_reference_read': False}

    def factory(folder, task, limits):
        return runtime.ToolRuntime(folder, task, limits, executor=fake_execution)

    def post(url, **kwargs):
        assert url == loop.ENDPOINT and kwargs['allow_redirects'] is False
        assert 'Authorization' not in kwargs['headers']
        body = json.loads(kwargs['data'])
        number = len(calls) + 1
        calls.append(body)
        reservation = pilot / 'episodes/PNS_BASE/calls' / f'{number:04d}' / 'reservation.json'
        assert reservation.exists() and loop.read(reservation)['request_sha256'] == loop.sha_bytes(kwargs['data'])
        name, arguments = actions[number - 1]
        return Response([{'type': 'reasoning', 'id': f'rs_{number}', 'summary': [],
                'encrypted_content': f'opaque_fixture_{number}'},
            {'type': 'function_call', 'id': f'fc_{number}', 'call_id': f'call_{number}',
                'name': name, 'arguments': json.dumps(arguments)}], number)

    outcome = loop.run_episode('PNS_BASE', root=pilot, http_post=post,
        runtime_factory=factory, tools=runtime.TOOL_DEFINITIONS, test_mode=True)
    assert outcome['status'] == 'finalized' and outcome['selected_candidate'] == 'v001'
    assert outcome['calls_reserved'] == 4 and outcome['tool_usage']['candidates'] == 2
    assert runs == [('v001', 53001)]
    assert outcome['accounted_usd'] == pytest.approx(4 * (700 * 2 + 100 * .1 + 200 * 2.5 + 100 * 10) / 1e6)
    assert len(calls[-1]['input']) == 10  # initial user + three full reasoning/call/result triplets
    engine = factory(pilot / 'episodes/PNS_BASE', loop.config(pilot, 'PNS_BASE')[2], loop.read(pilot / 'PLAN.json')['limits'])
    assert engine.state['sources'] == engine.state['searches'] == {}
    assert engine.selected_candidate == 'v001'
    assert loop.run_episode('PNS_BASE', root=pilot, http_post=forbidden,
        runtime_factory=factory, tools=runtime.TOOL_DEFINITIONS, test_mode=True) == outcome


def test_exclusion_screen_blocks_decoded_text_and_host_urls(pilot):
    task = loop.config(pilot, 'PNS_BASE')[2]
    screen = runtime.gateway.Screen({'exclusions': {
        'compact_aliases': task['information_policy']['excluded_cohorts'], 'regexes': []}})
    for text in ('<article><body>P<span>N</span>S target text</body></article>',
                 '<article><body>P%4eS target text</body></article>'):
        with pytest.raises(runtime.gateway.GatewayError, match='excluded_study_alias'):
            runtime.gateway.parse_xml(text.encode(), screen)
    for url in ('file:///D:/.env', 'http://127.0.0.1/', 'https://www.ebi.ac.uk/private',
                'https://pmc-oa-opendata.s3.amazonaws.com/PMC1.1/../secret'):
        assert runtime.gateway.allowed_url(url) is False


def test_tool_schema_has_no_reference_or_arbitrary_file_capability():
    assert {t['name'] for t in runtime.TOOL_DEFINITIONS} == {
        'literature_search', 'read_source', 'list_sources', 'submit_candidate', 'run_candidate', 'finalize'}
    assert all(t['type'] == 'function' for t in runtime.TOOL_DEFINITIONS)
    assert 'generate_for_evaluation' not in runtime.NAMES
