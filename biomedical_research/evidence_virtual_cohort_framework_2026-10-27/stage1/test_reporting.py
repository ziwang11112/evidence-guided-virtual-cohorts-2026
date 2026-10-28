"""Full 21-arm evaluator contract test using artificial one-row fixtures only."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
import runner

class ReportingContract(unittest.TestCase):
    def test_inventory_and_all_reports_without_patient_references(self):
        actual=runner.ROOT
        with tempfile.TemporaryDirectory(dir=actual,prefix='reporting_toy_') as tmp:
            root=Path(tmp); (root/'custodian').mkdir()
            shutil.copyfile(actual/'protocol.json',root/'protocol.json')
            shutil.copyfile(actual/'analysis_registry.json',root/'analysis_registry.json')
            runner.write(root/'protocol_freeze.json',{'files':{}})
            protocol=runner.read(root/'protocol.json'); registry=runner.read(root/'analysis_registry.json')
            for case in runner.CASE_IDS:
                pd.DataFrame({'toy':[1]}).to_csv(root/'custodian'/f'{case}_reference.csv',index=False)
                arms=[(b,p) for b in [1,2,3] for p in ['ordinary','proposed']]+[(0,'statistical')]
                for build,branch in arms:
                    run=root/('statistical' if branch=='statistical' else 'runs')/case/('fixed' if branch=='statistical' else f'build_{build:02d}')/(branch+'_v1')
                    run.mkdir(parents=True)
                    task=dict(case_id=case,lineage_id=f'{case}_build_{build:02d}',run_id=f'{case}_{build}_{branch}',branch=branch,regime='whole_cohort',parent={'common_parent_hash':'toy'})
                    runner.write(run/'task.json',task)
                    runner.write(run/'candidate_manifest.json',{'files':{'task.json':runner.sha(run/'task.json')}})
                    final=run/'final';final.mkdir()
                    scenarios={'target':20} if branch=='ordinary' else ({'low':10,'high':10} if branch=='proposed' else {'rho_0':7,'rho_04':7,'rho_08':6})
                    records=[];cursor=0
                    for scenario,count in scenarios.items():
                        for _ in range(count):
                            cursor+=1; name=f'cohort_{cursor:02d}.csv'
                            pd.DataFrame({'toy':[cursor]}).to_csv(final/name,index=False)
                            records.append(dict(draw=cursor,seed=protocol['final_seeds'][case][cursor-1],scenario=scenario,status='ok',path=name,sha256=runner.sha(final/name)))
                    runner.write(final/'manifest.json',dict(task=task,candidate_manifest_sha256=runner.sha(run/'candidate_manifest.json'),records=records,files=runner.files_manifest(final),cohorts_requested=20,cohorts_saved=20,scenario_allocation=scenarios))
            def fake_analysis(df,case):
                return [dict(analysis=r['analysis'],term=r['term'],estimate=float(df.toy.iloc[0]),se=1.,ci_low=-1.,ci_high=21.,p=.5,status='ok',n_persons=1,n_rows=1) for r in registry if r['case_id']==case]
            with patch.object(runner,'ROOT',root),patch.object(runner,'analyze',side_effect=fake_analysis):
                result=runner.evaluate('toy_evaluation')
                self.assertEqual(result['cohorts'],420)
                self.assertEqual(result['analysis_records'],7700)
                out=root/'custodian/toy_evaluation'
                summaries=runner.read(out/'scenario_summaries.json')
                self.assertTrue(all(all(k in r for k in ['analysis','term','multiplicity_family']) for r in summaries))
                paired=runner.read(out/'paired_lineage_comparisons.json')
                self.assertEqual(len(paired),165)
                self.assertTrue(all(set(r['arms'])=={'ordinary','proposed'} for r in paired))
                self.assertTrue(all(len(r['arms']['ordinary'])==1 and len(r['arms']['proposed'])==2 for r in paired))
                states=runner.read(out/'scenario_sensitivity.json')
                self.assertTrue(all(not r['between_scenario_modal_evidence_state_disagreement'] for r in states))
                rows=runner.read(out/'analysis_records.json')
                self.assertTrue(all(r['direction_agreement'] is None for r in rows))
                # A duplicate repaired final must be refused before target analysis.
                src=root/'runs/case_b/build_01/ordinary_v1'; dst=root/'runs/case_b/build_01/ordinary_v2'
                shutil.copytree(src,dst)
                with self.assertRaisesRegex(ValueError,'exactly one final'):
                    runner.final_inventory()
            audit=dict(status='passed',fixture='artificial one-row toy inputs; all analysis calls replaced by declared fixture statistics',final_arms=21,requested=420,analysis_records=7700,paired_term_comparisons=165,raw_unit_cross_term_aggregation=False,unresolved_reference_direction_not_scored=True,duplicate_repair_rejected=True,patient_reference_files_opened=False)
        if not (actual/'reporting_toy_audit.json').exists(): runner.write(actual/'reporting_toy_audit.json',audit)

if __name__=='__main__': unittest.main(verbosity=2)
