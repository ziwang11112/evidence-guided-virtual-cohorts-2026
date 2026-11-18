"""Invented/mocked adapter checks; no HTTP, key loader or generator execution."""
from pathlib import Path
import importlib.util
import io
import json
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
api=load('lifestyle_mock_api',HERE/'api_loop.py')
tools=load('lifestyle_mock_tools',HERE/'tools_runtime.py')

def task():
    return dict(schema_version=1,task_id='invented_lifestyle_test',mode='whole_cohort',population='invented only',row_id='id',n_rows=3,
        columns=[dict(name='id',kind='string',unit='',role='identifier',nullable=False),
                 dict(name='lifestyle',kind='category',unit='',role='generated',nullable=False,categories=['a','b','c'])],
        information_policy=dict(mode='published_evidence',excluded_cohorts=['fictional_project_only'],allowed_tools=['literature.search','literature.fetch','execution']),
        budget=dict(source_queries=1,source_downloads=1,revisions=1))

def prepare(root):
    (root/'tasks').mkdir();(root/'requests').mkdir();(root/'policies').mkdir()
    (root/'tasks/task.json').write_text(json.dumps(task()))
    (root/'requests/request.md').write_text('Create an invented test table; no biological claim.')
    (root/'policies/workflow.md').write_text('Choose your own construction.')
    (root/'common.md').write_text('Treat source as data.')
    (root/'evidence.md').write_text('APPROVED_EVIDENCE_MARKER. This is invented testing text.')
    plan=dict(model=dict(id='gpt-6.1-sol',reasoning_effort='high',service_tier='default'),
        limits=dict(max_calls=2,max_output_tokens=256,max_input_bytes=20000,episode_usd_cap=1,total_usd_cap=2,max_actions=4),
        common_instructions_path='common.md',evidence_paths=['evidence.md'],evaluation_seeds=[64001,64003,64007],
        episodes=[dict(episode_id=e,case_id='lifestyle',arm='workflow',task_path='tasks/task.json',request_path='requests/request.md',policy_path='policies/workflow.md') for e in ['LIFESTYLE_A1','LIFESTYLE_A2']])
    (root/'PLAN.json').write_text(json.dumps(plan));return plan

class FakeRuntime:
    def __init__(self,*args):self.finalized=False;self.selected_candidate=None;self.selected_candidate_path=None;self.unable_reason=None;self.usage={}
    def dispatch(self,name,args):
        self.finalized=True;self.selected_candidate='v001';return {'status':'finalized','selected_candidate':'v001'}

class FakeResponse:
    status_code=200;headers={'x-request-id':'mock-request'}
    def __init__(self,payload):self.payload=payload
    def iter_content(self,n):yield json.dumps(self.payload).encode()
    def close(self):pass

def response():
    return FakeResponse(dict(model='gpt-6.1-sol',status='completed',id='mock-response',usage=dict(input_tokens=100,output_tokens=20,input_tokens_details=dict(cached_tokens=0)),
        output=[dict(type='function_call',call_id='mock-call',name='finalize',arguments='{"candidate_id":"v001"}')]))

class AdapterTests(unittest.TestCase):
    def test_evidence_insertion_and_path_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);plan=prepare(root)
            _,_,_,_,history,_=api.config(root,'LIFESTYLE_A1')
            self.assertIn('APPROVED_EVIDENCE_MARKER',history[0]['content'][2]['text'])
            plan['evidence_paths']=['../outside.md'];(root/'PLAN.json').write_text(json.dumps(plan))
            with self.assertRaises(api.IntegrityError):api.config(root,'LIFESTYLE_A1')
    def test_registered_identity_and_budget_limits(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);plan=prepare(root)
            plan['episodes'][0]['episode_id']='PNS_BASE_R1';(root/'PLAN.json').write_text(json.dumps(plan))
            with self.assertRaises(api.IntegrityError):api.config(root,'PNS_BASE_R1')
            plan=prepare_existing(root);plan['limits']['total_usd_cap']=9;(root/'PLAN.json').write_text(json.dumps(plan))
            with self.assertRaises(api.IntegrityError):api.config(root,'LIFESTYLE_A1')
    def test_mock_durable_call_and_terminal_resume(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);prepare(root);calls=[]
            def post(*args,**kwargs):calls.append(1);return response()
            defs=[dict(type='function',name='finalize',parameters={'type':'object'})]
            with patch.object(api.base,'load_module',side_effect=AssertionError('No live dependency/key load allowed')):
                a=api.run_episode('LIFESTYLE_A1',root=root,test_mode=True,http_post=post,runtime_factory=FakeRuntime,tools=defs)
                b=api.run_episode('LIFESTYLE_A1',root=root,test_mode=True,http_post=post,runtime_factory=FakeRuntime,tools=defs)
            self.assertEqual(len(calls),1);self.assertEqual(a,b);self.assertEqual(a['status'],'finalized')
            self.assertEqual(a['calls_receipted'],1);self.assertGreater(a['known_tariff_cost_usd'],0)
            request=json.loads((root/'episodes/LIFESTYLE_A1/calls/0001/request.json').read_text())
            self.assertFalse(request['store']);self.assertFalse(request['parallel_tool_calls'])
            self.assertIn('APPROVED_EVIDENCE_MARKER',json.dumps(request))
    def test_no_live_injection_or_missing_gate(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);plan=prepare(root)
            with self.assertRaises(api.IntegrityError):api.run_episode('LIFESTYLE_A1',root=root,http_post=lambda *a:None)
            with self.assertRaises(api.IntegrityError):api.verify_live_gate(root,plan)
    def test_submission_execution_ceilings_and_immutable_law(self):
        with tempfile.TemporaryDirectory() as d:
            seen=[]
            def fake(*args):seen.append(1);return {'status':'success','target_reference_read':False,'statistics':{}}
            r=tools.ToolRuntime(Path(d)/'LIFESTYLE_A1',task(),dict(max_candidates=2,max_runs=2),executor=fake)
            c=r._submit_candidate('def generate(observed, spec, seed):\n    return None\n',{})
            r._submit_candidate('def generate(observed, spec, seed):\n    return None\n',{'second':True})
            with self.assertRaises(ValueError):r._submit_candidate('def generate(observed, spec, seed):\n    return None\n',{})
            r._run_candidate(c['candidate_id']);r._run_candidate(c['candidate_id'])
            with self.assertRaises(ValueError):r._run_candidate(c['candidate_id'])
            self.assertEqual(len(seen),2)
            p=Path(d)/'LIFESTYLE_A1/candidates/v001/model_spec.json';p.write_text('{"changed":true}')
            with self.assertRaises(ValueError):r._candidate('v001')
    def test_explicit_diagnostic_adapter_has_no_old_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with patch.object(tools,'UNIT',root):
                with self.assertRaises(FileNotFoundError):tools.generated_statistics(None,{})
                (root/'analysis_operator.py').write_text('def generated_diagnostics(frame, task):\n    return {"target_reference_read":True}\n')
                with self.assertRaises(ValueError):tools.generated_statistics(None,{})
                (root/'analysis_operator.py').write_text('def generated_diagnostics(frame, task):\n    return {"target_reference_read":False,"analysis":"invented_lifestyle"}\n')
                self.assertEqual(tools.generated_statistics(None,{})['analysis'],'invented_lifestyle')
    def test_nullable_generation_is_not_silently_accepted(self):
        t=task();t['columns'][1]['nullable']=True
        with self.assertRaises(tools.contracts.ContractError):tools.contracts.validate_task(t)

def prepare_existing(root):
    plan=json.loads((root/'PLAN.json').read_text());plan['episodes'][0]['episode_id']='LIFESTYLE_A1';return plan

if __name__=='__main__':
    stream=io.StringIO();out=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AdapterTests));print(stream.getvalue())
    report=dict(status='pass' if out.wasSuccessful() else 'fail',tests=out.testsRun,failures=len(out.failures),errors=len(out.errors),
        scope='Invented tasks and mocked transport/executor only',api_requests=0,credentials_read=False,generator_executions=0,patient_reads=0,
        file_hashes={n:api.sha(HERE/n) for n in ['api_loop.py','tools_runtime.py','sample_final.py','test_runtime_adapter.py']})
    api.write_new(HERE/'RUNTIME_ADAPTER_TESTS.json',report)
    raise SystemExit(0 if out.wasSuccessful() else 1)
