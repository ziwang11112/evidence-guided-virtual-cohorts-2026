"""Intercepted HTTP/runtime tests. No credentials, provider calls or generators."""
import importlib.util
import json
from pathlib import Path

import pytest

SPEC=importlib.util.spec_from_file_location('tested_request_loop',Path(__file__).with_name('api_loop.py'))
loop=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(loop)

TOOLS=[{'type':'function','name':name,'parameters':{'type':'object'},'strict':False}
       for name in ['inspect','finalize']]


class FakeRuntime:
    actions=[]
    interrupted=False

    def __init__(self,directory,task,limits):
        self.directory=directory
        self.task=task
        self.limits=limits
        self.state_path=directory/'fake_runtime.json'
        self.state=json.loads(self.state_path.read_text()) if self.state_path.exists() else {'finalized':False,'selected_candidate':None,'unable_reason':None,'actions':0}

    @property
    def finalized(self):return self.state['finalized']
    @property
    def selected_candidate(self):return self.state['selected_candidate']
    @property
    def selected_candidate_path(self):return None
    @property
    def unable_reason(self):return self.state['unable_reason']
    @property
    def usage(self):return {'actions':self.state['actions']}

    def dispatch(self,name,args):
        self.actions.append((self.directory.name,name,args))
        self.state['actions']+=1
        if name=='finalize':
            self.state.update(finalized=True,selected_candidate=args.get('candidate_id'),unable_reason=args.get('unable_reason'))
        self.state_path.write_text(json.dumps(self.state))
        if self.interrupted:
            raise KeyboardInterrupt('simulated process interruption')
        return {'ok':True,'episode':self.directory.name,'name':name,'args':args}


class Response:
    def __init__(self,data,status=200):
        self.raw=loop.encoded(data) if not isinstance(data,bytes) else data
        self.status_code=status
        self.headers={'x-request-id':'request-test'}
        self.closed=False
    def iter_content(self,size):
        yield self.raw
    def close(self):self.closed=True


class HTTP:
    def __init__(self,responses):self.responses=list(responses);self.requests=[]
    def __call__(self,url,**kwargs):
        assert url==loop.ENDPOINT
        assert kwargs['allow_redirects'] is False
        assert 'Authorization' not in kwargs['headers']
        self.requests.append(json.loads(kwargs['data']))
        item=self.responses.pop(0)
        if isinstance(item,BaseException):raise item
        return item


def function(name='inspect',args=None,call_id='call_1'):
    return {'type':'function_call','id':'fc_'+call_id,'call_id':call_id,
            'name':name,'arguments':json.dumps(args or {})}


def reply(output,usage=True,**overrides):
    obj={'id':'resp_test','model':loop.MODEL,'status':'completed','output':output,
         'usage':{'input_tokens':100,'output_tokens':50,'input_tokens_details':{'cached_tokens':20,'cache_write_tokens':10},'output_tokens_details':{'reasoning_tokens':30}} if usage else None}
    obj.update(overrides)
    return Response(obj)


@pytest.fixture
def pilot(tmp_path):
    FakeRuntime.actions=[];FakeRuntime.interrupted=False
    (tmp_path/'tasks').mkdir();(tmp_path/'requests').mkdir();(tmp_path/'policies').mkdir()
    for case in ['PNS','LIPID']:
        (tmp_path/f'tasks/{case}.json').write_text(json.dumps({'case_id':case,'n_rows':3000}))
        (tmp_path/f'requests/{case}.txt').write_text('Request only for '+case)
    for name in ['ordinary','workflow','common']:
        (tmp_path/f'policies/{name}.txt').write_text(name+' instructions')
    plan={'model':{'id':loop.MODEL,'reasoning_effort':'high','service_tier':'default',**loop.DEFAULT_RATES},
          'limits':{'max_calls':24,'max_output_tokens':16384,'max_input_bytes':250000,
                    'episode_usd_cap':4,'total_usd_cap':16,'max_actions':60},
          'episodes':[],'common_instructions_path':'policies/common.txt'}
    for name in sorted(loop.EPISODE_IDS):
        case=name.split('_')[0];arm='ordinary' if name.endswith('BASE') else 'workflow'
        plan['episodes'].append({'episode_id':name,'case_id':case,'arm':arm,'task_path':f'tasks/{case}.json',
                                'request_path':f'requests/{case}.txt','policy_path':f'policies/{arm}.txt'})
    (tmp_path/'PLAN.json').write_text(json.dumps(plan))
    return tmp_path


def run(root,http,episode='PNS_BASE',**kwargs):
    return loop.run_episode(episode,root=root,http_post=http,runtime_factory=FakeRuntime,
                            tools=TOOLS,test_mode=True,**kwargs)


def adjust(root,**values):
    p=root/'PLAN.json';plan=json.loads(p.read_text());plan['limits'].update(values);p.write_text(json.dumps(plan))


def test_encrypted_all_output_replayed_and_finalize_explicit(pilot):
    reasoning={'type':'reasoning','id':'rs_1','summary':[],'encrypted_content':'PRIVATE_OPAQUE_TOKEN'}
    message={'type':'message','id':'msg_1','role':'assistant','content':[{'type':'output_text','text':'I will inspect.'}]}
    fc=function(args={'x':1})
    http=HTTP([reply([reasoning,message,fc]),reply([function('finalize',{'candidate_id':'candidate_1'},'call_2')])])
    result=run(pilot,http)
    assert result['selected_candidate']=='candidate_1' and result['status']=='finalized'
    body=http.requests[1]
    assert body['input'][1:4]==[reasoning,message,fc]
    assert body['input'][4]['call_id']=='call_1' and body['input'][4]['type']=='function_call_output'
    assert body['store'] is False and body['include']==['reasoning.encrypted_content']
    assert body['reasoning']=={'effort':'high'} and body['service_tier']=='default'
    assert 'PRIVATE_OPAQUE_TOKEN' not in json.dumps(result)
    assert result['known_tariff_cost_usd']==pytest.approx(2*((70*2+20*.1+10*2.5+50*10)/1e6))
    folder=pilot/'episodes/PNS_BASE/calls/0001'
    assert json.loads((folder/'reservation.json').read_text())['request_sha256']==loop.sha(folder/'request.json')
    assert run(pilot,HTTP([]))==result  # completed resume never resends


def test_reservation_exists_before_http_and_exact_body(pilot):
    def post(url,**kwargs):
        folder=pilot/'episodes/PNS_BASE/calls/0001'
        assert (folder/'reservation.json').is_file()
        assert (folder/'request.json').read_bytes()==kwargs['data']
        return reply([function('finalize',{'unable_reason':'no basis'})])
    result=run(pilot,post)
    assert result['selected_candidate'] is None and result['unable_reason']=='no basis'


def test_malformed_arguments_and_unknown_tools_return_mechanical_outputs(pilot):
    malformed=function();malformed['arguments']='{"x":'
    unknown=function('unregistered',{},'call_2')
    duplicate_keys=function('inspect',{},'call_3');duplicate_keys['arguments']='{"x":1,"x":2}'
    http=HTTP([reply([malformed,unknown,duplicate_keys]),reply([function('finalize',{'unable_reason':'done'},'call_4')])])
    result=run(pilot,http)
    outputs=[x for x in http.requests[1]['input'] if x.get('type')=='function_call_output']
    assert [json.loads(x['output'])['error']['code'] for x in outputs]==['malformed_function_arguments','unknown_tool','malformed_function_arguments']
    assert result['requested_tool_actions']==4
    assert [a[1] for a in FakeRuntime.actions]==['finalize']


@pytest.mark.parametrize('calls',[
    [function(call_id='same'),function(call_id='same')],
    [{'type':'function_call','name':'inspect','arguments':'{}'}],
])
def test_bad_call_correspondence_never_dispatches(pilot,calls):
    result=run(pilot,HTTP([reply(calls)]))
    assert result['status']=='invalid_function_call_correspondence'
    assert FakeRuntime.actions==[]


def test_prior_call_id_cannot_dispatch_twice(pilot):
    http=HTTP([reply([function()]),reply([function()])])
    result=run(pilot,http)
    assert result['status']=='invalid_function_call_correspondence'
    assert len(FakeRuntime.actions)==1


def test_model_silence_does_not_select_latest(pilot):
    result=run(pilot,HTTP([reply([{'type':'message','role':'assistant','content':[{'type':'output_text','text':'Use candidate_99.'}]}])]))
    assert result['status']=='model_stopped_without_finalize' and result['selected_candidate'] is None


def test_budget_prevents_send(pilot):
    adjust(pilot,episode_usd_cap=.001)
    http=HTTP([]);result=run(pilot,http)
    assert result['status']=='budget_limit' and result['calls_reserved']==0 and not http.requests


def test_input_ceiling_no_truncation_or_send(pilot):
    adjust(pilot,max_input_bytes=1)
    result=run(pilot,HTTP([]))
    assert result['status']=='input_byte_limit' and result['calls_reserved']==0


def test_call_limit(pilot):
    adjust(pilot,max_calls=1)
    result=run(pilot,HTTP([reply([function()])]))
    assert result['status']=='call_limit' and result['calls_reserved']==1


def test_action_cap_denies_excess_calls_without_dispatch(pilot):
    adjust(pilot,max_actions=1)
    result=run(pilot,HTTP([reply([function(),function(call_id='call_2')])]))
    assert result['status']=='action_limit'
    assert len(FakeRuntime.actions)==1
    r=json.loads((pilot/'episodes/PNS_BASE/calls/0001/tool_002.result.json').read_text())
    assert json.loads(r['output'])['error']['code']=='action_budget_exhausted'


def test_unknown_usage_keeps_reservation(pilot):
    result=run(pilot,HTTP([reply([function('finalize',{'unable_reason':'done'})],usage=False)]))
    reserve=json.loads((pilot/'episodes/PNS_BASE/calls/0001/reservation.json').read_text())
    assert result['accounted_usd']==reserve['reserved_usd']
    assert result['unknown_usage_calls']==1 and result['known_tariff_cost_usd']==0


@pytest.mark.parametrize('error',[TimeoutError('timeout'),ConnectionError('broken')])
def test_transport_error_no_retry(pilot,error):
    http=HTTP([error]);result=run(pilot,http)
    assert len(http.requests)==1 and result['status']=='transport_or_capture_error'
    assert result['unknown_usage_calls']==1
    run(pilot,HTTP([]))


def test_interrupted_http_never_double_sends_on_resume(pilot):
    with pytest.raises(KeyboardInterrupt):run(pilot,HTTP([KeyboardInterrupt()]))
    result=run(pilot,HTTP([]))
    assert result['status']=='interrupted_http_dispatch' and result['unknown_usage_calls']==1


def test_interrupted_tool_never_double_dispatches_on_resume(pilot):
    FakeRuntime.interrupted=True
    with pytest.raises(KeyboardInterrupt):run(pilot,HTTP([reply([function()])]))
    FakeRuntime.interrupted=False
    result=run(pilot,HTTP([]))
    assert result['status']=='interrupted_tool_dispatch' and len(FakeRuntime.actions)==1


def test_escaped_tool_exception_is_terminal_and_does_not_confirm_selection(pilot):
    class UncertainRuntime(FakeRuntime):
        def dispatch(self,name,args):
            super().dispatch(name,args)
            raise OSError('state result failed after side effect')
    http=HTTP([reply([function('finalize',{'candidate_id':'candidate_1'}),function(call_id='call_2')])])
    result=loop.run_episode('PNS_BASE',root=pilot,http_post=http,runtime_factory=UncertainRuntime,
                            tools=TOOLS,test_mode=True)
    assert result['status']=='uncertain_tool_dispatch' and len(http.requests)==1
    assert result['runtime_finalized'] and not result['finalized'] and result['selected_candidate'] is None
    assert len(FakeRuntime.actions)==1


def test_secret_redacted_before_exception_truncation(pilot):
    body=loop.request_body('instructions',[],TOOLS,json.loads((pilot/'PLAN.json').read_text())['limits'])
    limits=json.loads((pilot/'PLAN.json').read_text())['limits']
    folder,_=loop.reserve(pilot,'PNS_BASE',1,body,limits,loop.DEFAULT_RATES)
    secret='DO_NOT_PERSIST_THIS_SECRET'
    def post(*args,**kwargs):raise RuntimeError('x'*990+secret+'tail')
    receipt,_=loop.send_once(folder,post,{},[secret],loop.DEFAULT_RATES)
    assert 'DO_NOT' not in receipt['error'] and '[REDACTED]' in receipt['error']


def test_resume_completed_turn_without_resending_or_redispatch(pilot,monkeypatch):
    real=loop.reserve
    def interrupt(root,eid,n,*args):
        if n==2:raise KeyboardInterrupt()
        return real(root,eid,n,*args)
    monkeypatch.setattr(loop,'reserve',interrupt)
    with pytest.raises(KeyboardInterrupt):run(pilot,HTTP([reply([function()])]))
    monkeypatch.setattr(loop,'reserve',real)
    http=HTTP([reply([function('finalize',{'candidate_id':'candidate_1'},'call_2')])])
    result=run(pilot,http)
    assert result['calls_reserved']==2 and len(http.requests)==1 and len(FakeRuntime.actions)==2


def test_resume_input_change_rejected(pilot):
    with pytest.raises(KeyboardInterrupt):run(pilot,HTTP([KeyboardInterrupt()]))
    (pilot/'requests/PNS.txt').write_text('Different context')
    with pytest.raises(loop.IntegrityError,match='inputs changed'):run(pilot,HTTP([]))


def test_no_cross_episode_context(pilot):
    first=HTTP([reply([function('finalize',{'candidate_id':'SECRET_PNS_CANDIDATE'})])])
    run(pilot,first)
    second=HTTP([reply([function('finalize',{'unable_reason':'done'})])])
    run(pilot,second,'LIPID_WORKFLOW')
    body=json.dumps(second.requests)
    assert 'SECRET_PNS_CANDIDATE' not in body and 'Request only for PNS' not in body
    assert 'workflow instructions' in body and 'ordinary instructions' not in body


def test_total_budget_across_episode_reservations(pilot):
    adjust(pilot,total_usd_cap=.2)
    # Unknown first call retains ~0.18; second episode cannot reserve another.
    run(pilot,HTTP([reply([function('finalize',{'unable_reason':'done'})],usage=False)]))
    second=HTTP([]);result=run(pilot,second,'LIPID_BASE')
    assert result['status']=='budget_limit' and second.requests==[]


def test_two_global_episode_slots_and_same_episode_lock(pilot):
    with loop.episode_slot(pilot,'PNS_BASE'):
        with pytest.raises(loop.BusyError):
            with loop.episode_slot(pilot,'PNS_BASE'):pass
        with loop.episode_slot(pilot,'LIPID_BASE'):
            with pytest.raises(loop.BusyError):
                with loop.episode_slot(pilot,'PNS_WORKFLOW'):pass


def test_test_mode_requires_all_mocks(pilot):
    with pytest.raises(loop.IntegrityError,match='all intercepted'):
        loop.run_episode('PNS_BASE',root=pilot,test_mode=True)


def test_live_gate_before_credentials(pilot,monkeypatch):
    def forbidden(*args):raise AssertionError('Must not import credentials before gate')
    monkeypatch.setattr(loop,'load_module',forbidden)
    with pytest.raises(loop.IntegrityError):loop.run_episode('PNS_BASE',root=pilot)


def test_freeze_cannot_bless_code_different_from_review(pilot,monkeypatch):
    for name in ['api_loop.py','tools_runtime.py','PROTOCOL.md']:
        (pilot/name).write_text('reviewed bytes')
    helper=pilot/'helper.py';helper.write_text('# no secrets')
    monkeypatch.setattr(loop,'KEY_HELPER',helper)
    files={p.relative_to(pilot).as_posix():loop.sha(p) for p in pilot.rglob('*') if p.is_file()}
    review={'status':'PASS','reviewed_files':files,'credential_helper_sha256':loop.sha(helper)}
    (pilot/'PREFLIGHT_REVIEW.json').write_text(json.dumps(review))
    files=dict(files);files['PREFLIGHT_REVIEW.json']=loop.sha(pilot/'PREFLIGHT_REVIEW.json')
    freeze={'files':files,'credential_helper_sha256':loop.sha(helper)}
    (pilot/'LAUNCH_FREEZE.json').write_text(json.dumps(freeze))
    plan=json.loads((pilot/'PLAN.json').read_text())
    loop.verify_live_gate(pilot,plan)
    (pilot/'api_loop.py').write_text('changed after review')
    freeze['files']['api_loop.py']=loop.sha(pilot/'api_loop.py')
    (pilot/'LAUNCH_FREEZE.json').write_text(json.dumps(freeze))
    with pytest.raises(loop.IntegrityError,match='Reviewed bytes differ'):
        loop.verify_live_gate(pilot,plan)


@pytest.mark.parametrize('response,status',[
    (reply([],status='incomplete'), 'incomplete_response'),
    (reply([],model='different-model'), 'model_mismatch'),
    (Response({'error':{'message':'not authorized'}},401), 'http_error'),
])
def test_noncompleted_api_responses_stop_without_tool_dispatch(pilot,response,status):
    http=HTTP([response]);result=run(pilot,http)
    assert result['status']==status and len(http.requests)==1 and not FakeRuntime.actions


def test_only_registered_function_tools(pilot):
    with pytest.raises(loop.IntegrityError,match='Only dispatched'):
        loop.run_episode('PNS_BASE',root=pilot,http_post=HTTP([]),runtime_factory=FakeRuntime,
                         tools=[{'type':'web_search'}],test_mode=True)


def test_actual_runtime_finalize_unable_integration_without_external_actions(pilot):
    unit=Path(__file__).resolve().parent
    runtime_module=loop.load_module('request_only_runtime_integration',unit/'tools_runtime.py')
    (pilot/'tasks/PNS.json').write_bytes((unit/'tasks/PNS.json').read_bytes())
    def forbidden(*args,**kwargs):raise AssertionError('No external source or generator operation is authorized in this test')
    def factory(directory,task,limits):
        return runtime_module.ToolRuntime(directory,task,limits,gateway_factory=forbidden,executor=forbidden)
    http=HTTP([reply([function('finalize',{'unable_reason':'Offline interface check only'})])])
    result=loop.run_episode('PNS_BASE',root=pilot,http_post=http,runtime_factory=factory,
                            tools=runtime_module.TOOL_DEFINITIONS,test_mode=True)
    assert result['status']=='finalized' and result['selected_candidate'] is None
    assert result['unable_reason']=='Offline interface check only'
    assert result['tool_usage']['actions']==1


def test_bad_usage_not_zero_charge():
    assert loop.tariff({'input_tokens':3,'output_tokens':5,'input_tokens_details':{'cached_tokens':4}},loop.DEFAULT_RATES) is None
    assert loop.tariff(None,loop.DEFAULT_RATES) is None
