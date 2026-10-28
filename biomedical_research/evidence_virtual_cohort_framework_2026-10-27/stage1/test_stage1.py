"""Meaningful contract/regime tests; toy values only, no reserved targets opened."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
import runner
import source_checks as checks
import fixed_generator

class Stage1Contracts(unittest.TestCase):
    def test_allocations_are_total_budget_not_per_scenario(self):
        self.assertEqual(checks.allocation(['a']),{'a':20})
        self.assertEqual(checks.allocation(['a','b']),{'a':10,'b':10})
        self.assertEqual(checks.allocation(['a','b','c']),{'a':7,'b':7,'c':6})
        for ids in [[],['a','a'],['a','b','c','d']]:
            with self.assertRaises(ValueError): checks.allocation(ids)

    def test_registry_inventory_and_reconstruction_roles(self):
        rows=runner.analysis_registry()
        self.assertEqual([sum(r['case_id']==c for r in rows) for c in runner.CASE_IDS],[35,10,10])
        self.assertEqual(len({(r['case_id'],r['analysis'],r['term']) for r in rows}),55)
        self.assertTrue(all(r['validation_role']=='given/reconstruction' for r in rows if r['analysis']=='paired_change'))
        self.assertTrue(all(r['validation_role']=='reserved' for r in rows if r['analysis']=='change_pearson'))

    def test_fixed_sampler_source_support_counts_reproducibility(self):
        for case in runner.CASE_IDS:
            schema=checks.read(runner.ROOT/'packets'/case/'schema.json'); evidence=checks.read(runner.ROOT/'packets'/case/'evidence.json')
            for scenario in ['rho_0','rho_04','rho_08']:
                a=checks.call_checked(fixed_generator,schema,copy.deepcopy(evidence),810101,scenario)
                b=checks.call_checked(fixed_generator,schema,copy.deepcopy(evidence),810101,scenario)
                self.assertTrue(a.equals(b))
                self.assertFalse(a.equals(checks.call_checked(fixed_generator,schema,copy.deepcopy(evidence),810102,scenario)))

    def test_paired_formula_known_toy_and_pairwise_missingness(self):
        data={'participant_id':['a','b','c','d','e']}
        for i,e in enumerate(['leptin','body_mass','glucose','triglycerides']):
            data[e+'_pre']=np.arange(5.)+10+i
            data[e+'_post']=data[e+'_pre']+np.arange(5.)*(i+1)-1
        df=pd.DataFrame(data); df.loc[4,['glucose_pre','glucose_post']]=np.nan
        result=runner.paired_analysis(df,'case_b')
        self.assertEqual(len(result),10)
        a=result[0]
        self.assertEqual(a['estimate'],1)
        self.assertAlmostEqual(a['se'],np.std([-1,0,1,2,3],ddof=1)/np.sqrt(5))
        corr=next(r for r in result if r['term']=='leptin__glucose')
        self.assertEqual(corr['n_persons'],4)
        self.assertAlmostEqual(corr['estimate'],1)

    def test_enrollment_weight_bound_applies_only_at_baseline(self):
        schema=checks.read(runner.ROOT/'packets/case_a/schema.json'); evidence=checks.read(runner.ROOT/'packets/case_a/evidence.json')
        df=fixed_generator.generate(75,810101,evidence)
        df.loc[df.index[1],'weight_kg']=181.
        self.assertTrue(checks.validate_frame(df,schema,evidence,75))
        df.loc[df.index[0],'weight_kg']=181.
        with self.assertRaisesRegex(ValueError,'Baseline weight'):
            checks.validate_frame(df,schema,evidence,75)

    def test_loader_rejects_io_and_global_seed(self):
        with tempfile.TemporaryDirectory(dir=runner.ROOT) as tmp:
            path=Path(tmp)/'candidate.py'
            for text in ['import os\ndef generate(n, seed, evidence, context="target"): pass','import numpy as np\ndef generate(n, seed, evidence, context="target"):\n np.random.seed(seed)','def generate(n, seed, evidence, context="target"):\n open("secret")']:
                path.write_text(text)
                with self.assertRaises(ValueError): checks.load_generator(path)

    def test_evidence_mutation_rejected(self):
        class Bad:
            @staticmethod
            def generate(n,seed,evidence,context='target'):
                evidence['bad']=True
                return pd.DataFrame()
        with self.assertRaisesRegex(ValueError,'mutated evidence'):
            checks.call_checked(Bad,{'n_persons':12},{'a':1},1,'target')

    def test_incomplete_inventory_blocks_before_reference_open(self):
        with tempfile.TemporaryDirectory(dir=runner.ROOT) as tmp:
            with patch.object(runner,'ROOT',Path(tmp)), patch.object(runner,'verify_freeze',return_value={}), patch.object(runner.pd,'read_csv') as reader:
                with self.assertRaisesRegex(ValueError,'exactly one final'):
                    runner.evaluate()
                reader.assert_not_called()

    def test_equal_source_budget_records_rejected_ordinary_candidates(self):
        evidence=checks.read(runner.ROOT/'packets/case_b/evidence.json')
        task=dict(run_id='toy',lineage_id='toy',branch='ordinary')
        d=runner.decision_template(task,evidence)
        d['calibration_log']['examined_structures'] += [dict(id=f'rejected_{i}',source_seeds_evaluated=[810101,810102,810103],disposition='rejected',reason='Toy alternative') for i in [1,2]]
        self.assertEqual(checks.validate_decision(d,task,evidence),{'target':20})
        d['calibration_log']['examined_structures'].append(dict(id='fourth',source_seeds_evaluated=[],disposition='rejected',reason='Too many'))
        with self.assertRaisesRegex(ValueError,'structure budget'):
            checks.validate_decision(d,task,evidence)

    def test_toy_controller_immutable_execution_and_no_mi(self):
        actual=runner.ROOT
        with tempfile.TemporaryDirectory(dir=actual,prefix='toy_smoke_') as tmp:
            root=Path(tmp)
            for name in ['protocol.json','source_checks.py','fixed_generator.py']:
                shutil.copyfile(actual/name,root/name)
            shutil.copytree(actual/'packets',root/'packets')
            # Toy controller reuses allowed packets only; no custodian/reference data.
            runner.write(root/'protocol_freeze.json',{'files':{p:runner.sha(root/p) for p in ['protocol.json','source_checks.py','fixed_generator.py']}})
            with patch.object(runner,'ROOT',root):
                run=Path(runner.stage('case_b',0,'statistical'))
                self.assertEqual(runner.check_candidate(run)['status'],'valid')
                output=runner.execute_final(run)
                self.assertEqual(output['saved'],20)
                manifest=checks.read(run/'final/manifest.json')
                self.assertEqual(manifest['scenario_allocation'],{'rho_0':7,'rho_04':7,'rho_08':6})
                self.assertEqual(len({r['sha256'] for r in manifest['records']}),20)
                self.assertEqual(checks.read(run/'task.json')['regime'],'whole_cohort')
                with self.assertRaises(FileExistsError): runner.execute_final(run)
                with self.assertRaises(FileExistsError): runner.check_candidate(run)
                # Persist compact non-patient smoke audit outside the temporary workspace.
                audit={'status':'passed','requested':20,'saved':20,'allocation':manifest['scenario_allocation'],'unique_tables':20,'immutable_reexecution_rejected':True,'whole_cohort_only':True,'reference_data_opened':False}
            if not (actual/'toy_smoke_audit.json').exists(): runner.write(actual/'toy_smoke_audit.json',audit)

if __name__=='__main__': unittest.main(verbosity=2)
