"""Offline integration checks: no API, real generator execution or target reads."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import tools_runtime as runtime
import api_loop
import pandas as pd


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class RevisionRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.plan=read(ROOT/'PLAN.json')
        self.ep=self.plan['episodes'][0]
        self.task=read(ROOT/self.ep['task_path'])
        self.package=ROOT/self.ep['imported_package_path']
        self.limits=self.plan['limits']

    def engine(self,policy='structured',directory='reviewer',limits=None,executor=None):
        return runtime.ToolRuntime(self.root/directory,self.task,limits or self.limits,
               bootstrap_package=self.package,review_policy=policy,
               analysis_ids=self.ep['requested_analysis_ids'],analysis_requirements=self.ep['analysis_requirements'],
               gateway_factory=lambda *a:(_ for _ in ()).throw(AssertionError('Network forbidden in test')),
               executor=executor or self.fake_execute)

    def fake_execute(self,candidate,task,seed,run,limits):
        run.mkdir(parents=True,exist_ok=False);(run/'output').mkdir();(run/'input').mkdir()
        for name in ['generator.py','model_spec.json']:(run/'input'/name).write_bytes((candidate/name).read_bytes())
        runtime.write_new(run/'input/task.json',task);runtime.write_new(run/'input/request.json',{'seed':seed})
        runtime.write_new(run/'input_bindings.json',{p.name:sha(p) for p in (run/'input').iterdir()})
        data={}
        for col in task['columns']:
            if col['name']==task['row_id']:data[col['name']]=list(range(task['n_rows']))
            elif col['kind']=='category':data[col['name']]=[col['categories'][0]]*task['n_rows']
            else:data[col['name']]=[float(col.get('minimum',1))]*task['n_rows']
        frame=pd.DataFrame(data);csv=run/'output/generated.csv';frame.to_csv(csv,index=False)
        receipt={'status':'success','candidate_id':candidate.name,'seed':seed,'generated_sha256':sha(csv),'target_reference_read':False,
                 'statistics':{'fixture_only':True,'target_reference_read':False}}
        runtime.write_new(run/'execution.json',receipt)
        return {'status':'success','candidate_id':candidate.name,'execution_receipt_sha256':sha(run/'execution.json')}

    def contract(self):
        return {'schema_version':1,'mathematical_review':[
            {'variable':c['name'],'support':'Unresolved; inspect declared code support.',
             'moment_assessment':'unresolved','justification':'No mathematical proof asserted in this test.',
             'code_locator':'generate','source_ids':[]}
            for c in self.task['columns'] if c['name']!=self.task['row_id'] and c['kind'] in ['number','integer']],
            'physiological_review':'No applicable physiological invariant asserted in this mechanical fixture.',
            'physiological_rules':[],
            'joint_analyses':[dict(analysis_id=a['analysis_id'],variables=a['variables'],adjustment=a['adjustment'],operator=a['operator'],
               dependencies=[{'parameter':'unidentified joint distribution','basis':'unresolved','source_ids':[],
                 'source_operator':'unreported','source_adjustment':[],'support':'not identified',
                 'uncertainty':'unresolved','code_locator':'generate'}]) for a in self.ep['analysis_requirements']]}

    def test_fresh_runtime_import_with_dataclass(self):
        self.assertIsNotNone(runtime.checks.REVIEW_CONTRACT_SCHEMA)

    def test_import_preserves_bytes_and_is_free(self):
        e=self.engine();folder,_=e._candidate('v000')
        for name in ['generator.py','model_spec.json','notes.json']:
            self.assertEqual((folder/name).read_bytes(),(self.package.parent/name).read_bytes())
        self.assertEqual(e.usage['candidates_submitted'],0)
        self.assertEqual(e.usage['actions'],0)

    def test_import_resume_preserves_binding(self):
        e=self.engine();e2=self.engine();self.assertEqual(e.state['import_binding'],e2.state['import_binding'])

    def test_resume_changed_policy_rejected(self):
        self.engine();self.assertRaises(ValueError,self.engine,'generic')

    def test_static_inspection_does_not_run(self):
        e=self.engine();out=e.dispatch('inspect_law',{'candidate_id':'v000'})
        self.assertEqual(out['status'],'static_only');self.assertEqual(e.usage['executions'],0)
        self.assertFalse(out['science_certified'])

    def test_schema_matches_requested_analysis_semantics(self):
        e=self.engine();out=e.dispatch('review_schema',{})
        self.assertEqual(out['analysis_requirements'],self.ep['analysis_requirements'])

    def test_structured_requires_selected_law_review(self):
        e=self.engine();out=e.dispatch('finalize',{'candidate_id':'v000','reason':'retain'})
        self.assertEqual(out['status'],'error');self.assertFalse(e.finalized)

    def test_generic_can_explicitly_retain(self):
        e=self.engine('generic');out=e.dispatch('finalize',{'candidate_id':'v000','reason':'retain'})
        self.assertEqual(out['status'],'finalized');self.assertEqual(e.selected_candidate,'v000')

    def test_structured_can_explicitly_report_inability(self):
        e=self.engine();out=e.dispatch('finalize',{'unable_reason':'No support for safe revision'})
        self.assertEqual(out['status'],'finalized');self.assertIsNone(e.selected_candidate)

    def test_empty_declarations_do_not_satisfy_gate(self):
        e=self.engine();c=self.contract();c['mathematical_review']=[];c['joint_analyses']=[]
        out=e.dispatch('inspect_law',{'candidate_id':'v000','review_contract':c})
        self.assertTrue(out['contract_validation']['valid'])
        self.assertFalse(next(iter(e.state['review_receipts'].values()))['complete_declarations'])
        self.assertEqual(e.dispatch('finalize',{'candidate_id':'v000','reason':'retain'})['status'],'error')

    def test_empty_dependencies_do_not_satisfy_gate(self):
        e=self.engine();c=self.contract();c['joint_analyses'][0]['dependencies']=[]
        e.dispatch('inspect_law',{'candidate_id':'v000','review_contract':c})
        self.assertFalse(next(iter(e.state['review_receipts'].values()))['complete_declarations'])

    def test_honest_unresolved_complete_contract_can_retain(self):
        e=self.engine();out=e.dispatch('inspect_law',{'candidate_id':'v000','review_contract':self.contract()})
        self.assertEqual(out['trial_review']['status'],'checked')
        self.assertEqual(out['trial_review']['physiology']['status'],'not_assessed')
        self.assertEqual(e.dispatch('finalize',{'candidate_id':'v000','reason':'retain with uncertainty'})['status'],'finalized')

    def test_duplicate_inspection_reuses_existing_trial(self):
        e=self.engine();c=self.contract()
        for _ in range(2):self.assertEqual(e.dispatch('inspect_law',{'candidate_id':'v000','review_contract':c})['status'],'reviewed')
        self.assertEqual(e.usage['executions'],1)

    def test_budget_zero_trial_explicitly_unavailable(self):
        limits=dict(self.limits,max_runs=0,max_executions=0)
        e=self.engine(limits=limits);out=e.dispatch('inspect_law',{'candidate_id':'v000','review_contract':self.contract()})
        self.assertEqual(out['trial_review']['status'],'unavailable');self.assertEqual(e.usage['executions'],0)

    def test_trial_hash_tampering_rejected(self):
        e=self.engine();e.dispatch('run_candidate',{'candidate_id':'v000'})
        (e.root/'executions/trial_001/output/generated.csv').write_text('bad',encoding='utf-8')
        self.assertEqual(e.dispatch('inspect_law',{'candidate_id':'v000','review_contract':self.contract()})['status'],'error')

    def test_trial_staged_inputs_tampering_rejected(self):
        e=self.engine();e.dispatch('run_candidate',{'candidate_id':'v000'})
        (e.root/'executions/trial_001/input/model_spec.json').write_text('{}',encoding='utf-8')
        self.assertEqual(e.dispatch('inspect_law',{'candidate_id':'v000','review_contract':self.contract()})['status'],'error')

    def test_trial_bindings_tampering_rejected(self):
        e=self.engine();e.dispatch('run_candidate',{'candidate_id':'v000'})
        (e.root/'executions/trial_001/input_bindings.json').write_text('{}',encoding='utf-8')
        self.assertEqual(e.dispatch('inspect_law',{'candidate_id':'v000','review_contract':self.contract()})['status'],'error')

    def test_generated_only_statistics_returned(self):
        e=self.engine();out=e.dispatch('inspect_law',{'candidate_id':'v000','review_contract':self.contract()})
        self.assertEqual(out['generated_only_statistics'],{'fixture_only':True,'target_reference_read':False})

    def test_imported_artifact_tampering_rejected(self):
        e=self.engine();(e.root/'candidates/v000/generator.py').write_text('bad',encoding='utf-8')
        self.assertEqual(e.dispatch('inspect_law',{'candidate_id':'v000'})['status'],'error')

    def test_mismatched_analysis_operator_invalid(self):
        e=self.engine();c=self.contract();c['joint_analyses'][0]['operator']='wrong'
        out=e.dispatch('inspect_law',{'candidate_id':'v000','review_contract':c})
        self.assertEqual(out['status'],'invalid_contract');self.assertEqual(e.usage['executions'],0)

    def test_mismatched_adjustment_invalid(self):
        e=self.engine();c=self.contract();c['joint_analyses'][0]['adjustment']=[]
        self.assertEqual(e.dispatch('inspect_law',{'candidate_id':'v000','review_contract':c})['status'],'invalid_contract')

    def test_unknown_source_not_certified(self):
        e=self.engine();c=self.contract();c['joint_analyses'][0]['dependencies'][0]['source_ids']=['PMC999999999']
        out=e.dispatch('inspect_law',{'candidate_id':'v000','review_contract':c})
        self.assertEqual(out['source_bindings']['PMC999999999']['status'],'unavailable_unregistered_source')

    def test_source_versions_remain_ambiguous(self):
        e=self.engine();sid=next(iter(e.imported_sources));m=e.imported_sources[sid]
        e.state['sources'][sid]=dict(m,version=m['version']+1,xml_sha256='other')
        c=self.contract();c['mathematical_review'][0]['source_ids']=[sid]
        out=e._source_bindings(c)[sid]
        self.assertTrue(out['version_ambiguous']);self.assertIsNone(out['selected_evidence_version']);self.assertEqual(len(out['registered_versions']),2)

    def test_imported_source_read_no_network(self):
        e=self.engine();sid=next(iter(e.imported_sources))
        out=e.dispatch('read_source',{'source_id':sid,'section':'index'})
        self.assertEqual(out['status'],'ok');self.assertFalse(out['network_used'])

    def test_invalid_source_version_bool_rejected(self):
        e=self.engine();sid=next(iter(e.imported_sources))
        self.assertEqual(e.dispatch('read_source',{'source_id':sid,'version':True})['status'],'error')

    def test_three_new_submissions_in_addition_to_import(self):
        e=self.engine();c=(self.package.parent/'generator.py').read_text();s=read(self.package.parent/'model_spec.json')
        for n in range(1,4):self.assertEqual(e.dispatch('submit_candidate',{'generator_py':c,'model_spec':s})['candidate_id'],f'v{n:03d}')
        self.assertEqual(e.dispatch('submit_candidate',{'generator_py':c,'model_spec':s})['status'],'error')
        self.assertEqual(e.usage['candidates_submitted'],3)

    def test_old_review_cannot_certify_new_candidate(self):
        e=self.engine();e.dispatch('inspect_law',{'candidate_id':'v000','review_contract':self.contract()})
        c=(self.package.parent/'generator.py').read_text();s=read(self.package.parent/'model_spec.json')
        e.dispatch('submit_candidate',{'generator_py':c,'model_spec':s})
        self.assertEqual(e.dispatch('finalize',{'candidate_id':'v001','reason':'changed'})['status'],'error')

    def test_paired_inputs_are_byte_equivalent(self):
        for n in range(1,13):
            a=api_loop.config(ROOT,f'R{n:02d}_GENERIC');b=api_loop.config(ROOT,f'R{n:02d}_STRUCTURED')
            self.assertEqual(a[4],b[4]);self.assertEqual(a[2],b[2]);self.assertNotEqual(a[3],b[3])

    def test_all_24_registered_no_other_session(self):
        self.assertEqual(len(api_loop.EPISODE_IDS),24)
        self.assertRaises(api_loop.IntegrityError,api_loop.config,ROOT,'R13_GENERIC')

    def test_not_finalized_cannot_generate_evaluation(self):
        e=self.engine();self.assertRaises(ValueError,e.generate_for_evaluation,'v000',54001,'seed_54001')

    def controller_fixture(self):
        r=self.root/'controller';r.mkdir()
        for name in ['PLAN.json']:(r/name).write_bytes((ROOT/name).read_bytes())
        for name in ['imports','tasks','requests','policies']:shutil.copytree(ROOT/name,r/name)
        return r

    def fake_post_sequence(self,calls):
        queue=list(calls)
        class Response:
            status_code=200
            headers={'x-request-id':'offline-fixture'}
            def __init__(self,body):self.body=body
            def iter_content(self,size):yield json.dumps(self.body).encode('utf-8')
            def close(self):pass
        def post(url,**kwargs):
            self.assertEqual(url,api_loop.ENDPOINT)
            self.assertNotIn('Authorization',kwargs['headers'])
            name,args=queue.pop(0)
            return Response({'id':'offline'+str(len(queue)),'status':'completed','model':api_loop.MODEL,
              'usage':{'input_tokens':100,'output_tokens':100,'input_tokens_details':{'cached_tokens':0}},
              'output':[{'type':'function_call','id':'f'+str(len(queue)),'call_id':'c'+str(len(queue)),
                         'name':name,'arguments':json.dumps(args),'status':'completed'}]})
        return post,queue

    def test_mock_controller_generic_retention_complete(self):
        r=self.controller_fixture()
        post,q=self.fake_post_sequence([('finalize',{'candidate_id':'v000','reason':'explicit retention'})])
        def factory(directory,task,limits):return runtime.ToolRuntime(directory,task,limits,
             bootstrap_package=r/self.ep['imported_package_path'],review_policy='generic',
             analysis_ids=self.ep['requested_analysis_ids'],analysis_requirements=self.ep['analysis_requirements'],executor=self.fake_execute)
        out=api_loop.run_episode('R01_GENERIC',root=r,http_post=post,runtime_factory=factory,tools=runtime.TOOL_DEFINITIONS,test_mode=True)
        self.assertEqual(out['status'],'finalized');self.assertEqual(out['selected_candidate'],'v000');self.assertFalse(q)

    def test_mock_controller_structured_check_then_retention(self):
        r=self.controller_fixture()
        post,q=self.fake_post_sequence([('inspect_law',{'candidate_id':'v000','review_contract':self.contract()}),
                                       ('finalize',{'candidate_id':'v000','reason':'explicit unresolved retention'})])
        def factory(directory,task,limits):return runtime.ToolRuntime(directory,task,limits,
             bootstrap_package=r/self.ep['imported_package_path'],review_policy='structured',
             analysis_ids=self.ep['requested_analysis_ids'],analysis_requirements=self.ep['analysis_requirements'],executor=self.fake_execute)
        out=api_loop.run_episode('R01_STRUCTURED',root=r,http_post=post,runtime_factory=factory,tools=runtime.TOOL_DEFINITIONS,test_mode=True)
        self.assertEqual(out['status'],'finalized');self.assertEqual(out['selected_candidate'],'v000');self.assertFalse(q)
        request=read(r/'episodes/R01_STRUCTURED/calls/0002/request.json')
        self.assertTrue(any(x.get('type')=='function_call_output' and 'generated_only_statistics' in x['output'] for x in request['input']))

if __name__=='__main__':unittest.main(verbosity=2)
