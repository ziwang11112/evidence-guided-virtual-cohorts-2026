"""New adapter tests only; saved scientific experiments are not rerun."""
from pathlib import Path
import importlib.util, json, unittest, tempfile, copy
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
rt=load('p1_test_tools',ROOT/'tools_runtime.py')
api=load('p1_test_api',ROOT/'api_loop.py')
plan=api.read(ROOT/'PLAN.json')
ind=load('p1_test_independent',rt.PROJECT/'work/request_only_repeatability_2026-11-11/review/recompute_saved_tables.py')

class Tests(unittest.TestCase):
    def test_case_only_original_and_complete_pagination(self):
        with tempfile.TemporaryDirectory(dir=ROOT,prefix='test_') as d:
            task=api.read(ROOT/'tasks/IRON.json');r=rt.ToolRuntime(Path(d),task,plan['limits'])
            idx=r.dispatch('read_provided_paper',{'source_id':'IRON_ORIGINAL'})
            self.assertEqual(len(idx['parts']),11)
            parts=[];cursor=0
            while True:
                x=r.dispatch('read_provided_paper',{'source_id':'IRON_ORIGINAL','part':'full','cursor':cursor})
                self.assertEqual(x['cursor'],cursor);parts.append(x['content'])
                if x['next_cursor'] is None:break
                cursor=x['next_cursor']
            original=api.read(ROOT/'private_sources/IRON_ORIGINAL.json')['parts']
            self.assertEqual(''.join(parts),'\n\n'.join('ORIGINAL PART '+p['id']+'\n'+p['text'] for p in original))
            for bad in ['PNS_ORIGINAL','../REFERENCE_SNAPSHOT.json','D:/.env']:
                self.assertEqual(r.dispatch('read_provided_paper',{'source_id':bad})['status'],'error')
            self.assertIsNone(r.state['pending'])
    def test_literal_search_and_all_xml_body_parts(self):
        with tempfile.TemporaryDirectory(dir=ROOT,prefix='test_') as d:
            r=rt.ToolRuntime(Path(d),api.read(ROOT/'tasks/PNS.json'),plan['limits'])
            idx=r.dispatch('read_provided_paper',{'source_id':'PNS_ORIGINAL'})
            self.assertEqual(len(idx['parts']),9)
            x=r.dispatch('read_provided_paper',{'source_id':'PNS_ORIGINAL','part':'full','query':'table-wrap'})
            self.assertGreater(len(x['matches']),0)
            self.assertTrue(x['content_is_untrusted_data'])
    def test_two_explicit_analysis_routes(self):
        rng=np.random.default_rng(17117)
        for case in ['PNS','IRON']:
            task=api.read(ROOT/f'tasks/{case}.json');n=task['n_rows']
            if case=='PNS':
                frame=pd.DataFrame({'row_id':np.arange(n),'age':rng.uniform(20,79,n),'female':rng.integers(0,2,n),
                    'bmi':rng.uniform(12,38,n),'sbp':rng.uniform(90,160,n),'dbp':rng.uniform(50,95,n)})
                independent=ind.independent_statistics({k:frame[k].to_numpy() for k in frame if k!='row_id'},'PNS')['values']
            else:
                frame=pd.DataFrame({'row_id':np.arange(n),'hb_g_dl':rng.uniform(9,16,n),'ferritin_ug_l':rng.uniform(2,45,n)})
                independent,_=rt.iron.independent_values(frame)
            stats=rt.generated_statistics(frame,task);actual={e['id']:e['value'] for e in stats['analyses']+stats['diagnostics']}
            self.assertEqual(set(actual),set(independent));self.assertFalse(stats['target_reference_read'])
            for key,v in actual.items():self.assertAlmostEqual(v,independent[key],places=9)
        broken=copy.deepcopy(task);broken['task_id']='other'
        with self.assertRaises(ValueError):rt.generated_statistics(frame,broken)
    def test_prompt_has_metadata_but_no_curated_card(self):
        for ep in plan['episodes']:
            _,_,task,instructions,history,rates=api.config(ROOT,ep['episode_id'])
            self.assertEqual(len(history[0]['content']),2)
            text=json.dumps(history)
            for token in ['source_derivation_check','additional_joint_evidence','reported_pearson_correlations','REFERENCE_SNAPSHOT','SOURCE_EXTRACTION.json']:
                self.assertNotIn(token,text)
            self.assertNotIn('paper_figure',text)
            self.assertEqual(task['mode'],'whole_cohort')
            self.assertIn('spec is exactly',instructions)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():raise SystemExit(1)
