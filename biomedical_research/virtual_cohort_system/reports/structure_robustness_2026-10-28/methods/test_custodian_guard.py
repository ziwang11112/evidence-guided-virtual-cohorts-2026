"""Gate tests use invented files only; no target files are parsed or fitted."""
import copy,hashlib,importlib.util,json,pathlib,tempfile,unittest
from unittest import mock
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('custodian_eval_test',HERE/'evaluate_committed.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
def write(p,obj): p.write_text(json.dumps(obj),encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=HERE,prefix='invented_guard_')
        self.home=pathlib.Path(self.tmp.name); self.visible=self.home/'visible'; self.visible.mkdir()
        (self.visible/'observed.csv').write_text('record_id,age,sex,bmi\nx,35,1,25\ny,50,2,30\n')
        write(self.visible/'input_hashes.json',{'files':{'observed.csv':sha(self.visible/'observed.csv')}})
        (self.home/'design_with_hidden_outcome.csv').write_text('invented sentinel bytes; never parse this file')
        (self.home/'fake_method.py').write_text('invented = True\n')
        write(self.home/'methods_freeze.json',{'files':{'fake_method.py':sha(self.home/'fake_method.py')}})
        write(self.home/'custodian_lock.json',{'files':{'methods_freeze.json':sha(self.home/'methods_freeze.json')},'hidden_table_sha256':sha(self.home/'design_with_hidden_outcome.csv'),'visible_input_hashes_sha256':sha(self.visible/'input_hashes.json')})
        (self.home/'guard.py').write_text("def verify_release(path):\n    return {'status':'passed','scope':'invented_guard_fixture'}\n")
        (self.home/'builder.csv').write_text('record_id,age,sex,bmi,tg_assay\nx,35,1,25,unblanked_2021_2023\ny,50,2,30,unblanked_2021_2023\n')
        self.c={'authorize_target_evaluation':True,'all_structures_and_seeds_committed':True,'custodian_lock_sha256':sha(self.home/'custodian_lock.json'),'structures':['a','b'],'seeds':[1,2],'candidate_commitments':[],'outputs':[],'builder_observed':{'path':str(self.home/'builder.csv'),'sha256':sha(self.home/'builder.csv')},'controller_guard':{'path':str(self.home/'guard.py'),'sha256':sha(self.home/'guard.py'),'function':'verify_release'}}
        for structure in self.c['structures']:
            for stage in ['initial','final']:
                p=self.home/f'{structure}_{stage}.json'; write(p,{'invented':True})
                self.c['candidate_commitments'].append({'structure':structure,'stage':stage,'path':str(p),'sha256':sha(p)})
            for seed in self.c['seeds']:
                p=self.home/f'{structure}_{seed}.csv'
                p.write_text('record_id,age,sex,bmi,tg_assay,tg_mg_dl\nx,35,1,25,unblanked_2021_2023,100\ny,50,2,30,unblanked_2021_2023,120\n')
                self.c['outputs'].append({'structure':structure,'seed':seed,'path':str(p),'sha256':sha(p)})
        self.commit=self.home/'commitment.json'; write(self.commit,self.c)
        self.patch1=mock.patch.object(module,'HERE',self.home); self.patch2=mock.patch.object(module,'VISIBLE',self.visible)
        self.patch1.start(); self.patch2.start()
    def tearDown(self):
        self.patch1.stop(); self.patch2.stop(); self.tmp.cleanup()
    def gate(self,c=None):
        write(self.commit,self.c if c is None else c)
        with mock.patch.object(module.pd,'read_csv',side_effect=AssertionError('No table should be parsed in preload gate')):
            return module.verify_preload(self.commit)
    def test_valid_preload_no_table_parse(self): self.assertEqual(self.gate()[1]['status'],'passed')
    def test_authorization_required(self):
        c=copy.deepcopy(self.c); c['authorize_target_evaluation']=False
        with self.assertRaises(ValueError): self.gate(c)
    def test_all_outputs_required(self):
        c=copy.deepcopy(self.c); c['outputs'].pop()
        with self.assertRaises(ValueError): self.gate(c)
    def test_duplicate_grid_rejected(self):
        c=copy.deepcopy(self.c); c['outputs'][-1]=c['outputs'][0]
        with self.assertRaises(ValueError): self.gate(c)
    def test_candidate_tamper_rejected(self):
        pathlib.Path(self.c['candidate_commitments'][0]['path']).write_text('changed')
        with self.assertRaises(ValueError): self.gate()
    def test_output_tamper_rejected(self):
        pathlib.Path(self.c['outputs'][0]['path']).write_text('changed')
        with self.assertRaises(ValueError): self.gate()
    def test_controller_guard_refusal_rejected(self):
        p=self.home/'guard.py'; p.write_text("def verify_release(path):\n    return {'status':'rejected'}\n")
        self.c['controller_guard']['sha256']=sha(p)
        with self.assertRaises(ValueError): self.gate()
    def test_visible_anchor_tamper_rejected(self):
        (self.visible/'observed.csv').write_text('changed')
        with self.assertRaises(ValueError): self.gate()
    def test_all_generated_inputs_preserved(self):
        self.gate(); self.assertEqual(len(module.prepare_outputs(self.c)),4)
    def test_builder_covariate_mapping_rejected(self):
        p=self.home/'builder.csv'; p.write_text(p.read_text().replace('x,35,','x,36,'))
        self.c['builder_observed']['sha256']=sha(p)
        self.gate()
        with self.assertRaises(AssertionError): module.prepare_outputs(self.c)
    def test_raw_interval_identity_scale(self): self.assertEqual(module.validate_invented()['status'],'passed')

if __name__=='__main__': unittest.main()
