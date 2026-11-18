"""Focused capacity-only tests; no providers, credentials or generator execution."""
import importlib.util
import json
from pathlib import Path

import pytest

UNIT=Path(__file__).resolve().parent
PREVIOUS=UNIT.parent/'request_only_agent_repair_2026-11-10'
spec=importlib.util.spec_from_file_location('capacity_boundary_loop',UNIT/'api_loop.py')
loop=importlib.util.module_from_spec(spec);spec.loader.exec_module(loop)


@pytest.fixture
def pilot(tmp_path):
    plan=json.loads((UNIT/'PLAN.json').read_text(encoding='utf-8'))
    (tmp_path/'PLAN.json').write_text(json.dumps(plan),encoding='utf-8')
    for path in {plan['common_instructions_path']} | {row[k] for row in plan['episodes'] for k in ['task_path','request_path','policy_path']}:
        target=tmp_path/path;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text('{}' if target.suffix=='.json' else 'Capacity boundary fixture only',encoding='utf-8')
    return tmp_path


def body_of_size(size):
    body={'input':'x'*(size-len(loop.encoded({'input':''})))}
    assert len(loop.encoded(body))==size
    return body


def test_only_two_validator_numeric_ceilings_change():
    before=(PREVIOUS/'api_loop.py').read_bytes()
    old=b"maxima = {'max_calls':24, 'max_output_tokens':16384, 'max_input_bytes':250000,"
    new=b"maxima = {'max_calls':48, 'max_output_tokens':16384, 'max_input_bytes':750000,"
    assert before.count(old)==1
    assert (UNIT/'api_loop.py').read_bytes()==before.replace(old,new)


def test_exact_new_limits_accepted_and_other_caps_retained(pilot):
    plan,*_=loop.config(pilot,'PNS_BASE')
    assert plan['limits']['max_calls']==48
    assert plan['limits']['max_input_bytes']==750000
    assert plan['limits']['episode_usd_cap']==4
    assert plan['limits']['total_usd_cap']==pytest.approx(14.3229868)
    assert plan['limits']['max_actions']==60 and plan['limits']['max_output_tokens']==16384


@pytest.mark.parametrize('key,value',[('max_calls',49),('max_input_bytes',750001),
                                     ('episode_usd_cap',4.01),('total_usd_cap',16.01)])
def test_beyond_changed_and_unchanged_ceilings_rejected(pilot,key,value):
    plan=json.loads((pilot/'PLAN.json').read_text());plan['limits'][key]=value
    (pilot/'PLAN.json').write_text(json.dumps(plan))
    with pytest.raises(loop.IntegrityError,match='Invalid limit'):
        loop.config(pilot,'PNS_BASE')


def test_exact_serialized_byte_boundary_and_unknown_reservation(pilot):
    plan,*_=loop.config(pilot,'PNS_BASE');limits=plan['limits']
    folder,status=loop.reserve(pilot,'PNS_BASE',1,body_of_size(750000),limits,loop.DEFAULT_RATES)
    assert status is None
    reservation=loop.read(folder/'reservation.json')
    assert reservation['input_bytes']==750000 and reservation['input_token_allowance']==754096
    assert reservation['reserved_usd']==pytest.approx(2.04908)
    worst_usage={'input_tokens':754096,'output_tokens':16384,
                 'input_tokens_details':{'cache_write_tokens':754096,'cached_tokens':0}}
    assert loop.tariff(worst_usage,loop.DEFAULT_RATES)==pytest.approx(reservation['reserved_usd'])
    assert loop.accounted(pilot,'PNS_BASE')==reservation['reserved_usd']  # No receipt: reserve retained.
    again,status=loop.reserve(pilot,'PNS_BASE',2,body_of_size(750000),limits,loop.DEFAULT_RATES)
    assert again is None and status=='budget_limit'  # Two unknown maximum requests exceed $4.
    too_big,status=loop.reserve(pilot,'LIPID_BASE',1,body_of_size(750001),limits,loop.DEFAULT_RATES)
    assert too_big is None and status=='input_byte_limit'


def test_remaining_global_cap_durable_across_episodes(pilot):
    plan,*_=loop.config(pilot,'PNS_BASE');limits=plan['limits']
    for eid in sorted(loop.EPISODE_IDS):
        for n in [1,2]:
            folder,status=loop.reserve(pilot,eid,n,body_of_size(630000),limits,loop.DEFAULT_RATES)
            assert folder is not None and status is None
    assert loop.accounted(pilot)==pytest.approx(13.99264)
    assert loop.accounted(pilot,'PNS_BASE')+.42408<4
    folder,status=loop.reserve(pilot,'PNS_BASE',3,body_of_size(100000),limits,loop.DEFAULT_RATES)
    assert folder is None and status=='budget_limit'  # $14.3229868 cap, although this episode remains below $4.
    assert loop.accounted(pilot)==pytest.approx(13.99264)


def test_mock_loop_stops_at_48_and_real_usage_replaces_reserve(pilot):
    class Runtime:
        finalized=False;selected_candidate=None;selected_candidate_path=None;unable_reason=None;usage={}
        def __init__(self,*args):self.actions=0
        def dispatch(self,name,args):self.actions+=1;return {'ok':True}
    class Response:
        status_code=200;headers={}
        def __init__(self,n):
            self.data={'id':f'resp_{n}','model':loop.MODEL,'status':'completed',
              'output':[{'type':'function_call','call_id':f'call_{n}','name':'inspect','arguments':'{}'}],
              'usage':{'input_tokens':100,'output_tokens':50,
                       'input_tokens_details':{'cached_tokens':20,'cache_write_tokens':10}}}
        def iter_content(self,*args):yield loop.encoded(self.data)
        def close(self):pass
    sent=[]
    def post(url,**kwargs):
        assert 'Authorization' not in kwargs['headers']
        n=len(sent)+1;folder=pilot/f'episodes/PNS_BASE/calls/{n:04d}'
        assert (folder/'reservation.json').is_file()
        assert (folder/'request.json').read_bytes()==kwargs['data']
        sent.append(n);return Response(n)
    kwargs=dict(root=pilot,http_post=post,runtime_factory=Runtime,
                tools=[{'type':'function','name':'inspect','parameters':{'type':'object'}}],test_mode=True)
    result=loop.run_episode('PNS_BASE',**kwargs)
    assert sent==list(range(1,49)) and result['status']=='call_limit'
    assert result['calls_reserved']==48 and result['requested_tool_actions']==48
    actual=(70*2+20*.1+10*2.5+50*10)/1e6
    assert result['known_tariff_cost_usd']==pytest.approx(48*actual)
    assert result['accounted_usd']==pytest.approx(48*actual) and result['unknown_usage_calls']==0
    assert loop.run_episode('PNS_BASE',**kwargs)==result and len(sent)==48
