"""Invented deterministic audit fixtures; no clinical or generated-output files."""
import copy
import itertools
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
import recompute_v2 as r


def fixture():
    bindings = {'cases': {}}
    references = {}
    identities, ledger, calculations, slots, summaries = [], [], {}, [], []
    for case, ids, unit, diag in [
        ('CHNS2009',['E1','E2','E3'],'%', 'age_q10'),
        ('ENSANUT2018',['Q1_age10','Q2_bmi5','Q3_bmi5'],'%', 'age.q10')]:
        bindings['cases'][case] = {'analyses':[{'id':x,'unit':unit} for x in ids], 'diagnostics':[{'id':diag,'unit':'year'}]}
        references[case] = {x:0.0 for x in [*ids,diag]}
        for arm in ['E0','E1']:
            for i in range(1,7):
                kind = 'agent' if i<=5 else 'statistical'
                cid=f'{case}_{arm}_{i}'
                identity={'constructor_id':cid,'case_id':case,'information_condition':arm,'constructor_kind':kind}
                identities.append(identity)
                base=float(i+(10 if arm=='E1' else 0))
                for j,seed in enumerate([5101,5102,5103]):
                    entry={**identity,'seed':seed,'scheduled':True,'closure_status':'all_final_slots_consumed',
                        'candidate':'candidates/initial','run_id':f'final_{seed}','execution_status':'success','output_sha256':cid+str(seed),'expected_error':None}
                    ledger.append(entry)
                    values={ident:base+j+k/10 for k,ident in enumerate([*ids,diag])}
                    calculations[(cid,seed)]={'values':values,'error':None}
                    slot={k:v for k,v in entry.items() if k!='expected_error'}
                    slot.update(analysis_status='complete',error=None,quality={},n=3000)
                    for category in ['analyses','diagnostics']:
                        slot[category]=[{'id':d['id'],'value':values[d['id']],'unit':d['unit'],'status':'computed','reason':None,
                            'reference_value':0.0,'generated_direction':'positive','reference_direction':'zero',
                            'signed_discrepancy':values[d['id']],'absolute_discrepancy':values[d['id']],'comparison_status':'computed'} for d in bindings['cases'][case][category]]
                    slots.append(slot)
                endpoints=[]
                for k,ident in enumerate(ids):
                    endpoints.append({'id':ident,'unit':unit,'scheduled_seeds':3,'available_values':3,'available_discrepancies':3,
                        'complete':True,'mean_absolute_discrepancy':base+1+k/10,'available_value_mean_absolute_discrepancy':base+1+k/10,
                        'mean_effect':base+1+k/10,'seed_effect_range':[base+k/10,base+2+k/10],
                        'seed_directions':['positive']*3,'summary_status':'complete'})
                summaries.append({**identity,'scheduled_final_slots':3,'successful_executions':3,'complete_analysis_slots':3,'endpoints':endpoints})
    summaries.sort(key=lambda x:x['constructor_id'])
    contrasts=[]
    for case,spec in bindings['cases'].items():
        for j,definition in enumerate(spec['analyses']):
            arms={}
            for arm in ['E0','E1']:
                mean=4.0+j/10+(10 if arm=='E1' else 0)
                arms[arm]={'scheduled_constructors':5,'represented_constructors':5,'constructors_with_complete_endpoint':5,
                    'constructors_with_any_discrepancy':5,'complete':True,'mean_constructor_mean_absolute_discrepancy':mean,
                    'incomplete_available_value_mean':None,'available_value_mean':mean}
            contrasts.append({'case_id':case,'endpoint':definition['id'],'unit':definition['unit'],'arms':arms,
                'status':'complete_descriptive_comparison','E1_minus_E0_mean_absolute_discrepancy':10.0,
                'incomplete_available_value_contrast':None,'complete_arm_comparison_available':True,
                'interpretation':'Added supplied-information descriptive contrast; no equivalence or isolated algorithmic superiority inference.'})
    report={'all_scheduled_slots':slots,'construction_summaries':summaries,'agent_information_contrasts':contrasts,
        'statistical_references':copy.deepcopy([x for x in summaries if x['constructor_kind']=='statistical']),
        'planned_constructions':24,'scheduled_final_slots':72,'successful_executions':72,'complete_analysis_slots':72,'unique_successful_table_contents':72}
    return report,identities,ledger,calculations,references,bindings


def with_failure(args, *, provider=True):
    report,ids,ledger,calcs,refs,bindings=args
    cid='CHNS2009_E0_1'
    slot=next(x for x in report['all_scheduled_slots'] if x['constructor_id']==cid and x['seed']==5101)
    slot.update(analysis_status='provider_error' if provider else 'unavailable',error={'type':'FixtureError','message':'invented failure'},quality=None,n=None)
    if not provider:
        slot['execution_status']='failed'
        slot['output_sha256']=None
        expected=next(x for x in ledger if x['constructor_id']==cid and x['seed']==5101)
        expected.update(execution_status='failed',output_sha256=None,expected_error=copy.deepcopy(slot['error']))
        calcs.pop((cid,5101))
        report['successful_executions']-=1
        report['unique_successful_table_contents']-=1
    for category in ['analyses','diagnostics']:
        for row in slot[category]:
            row.update(value=None,status='unavailable',reason='invented failure',generated_direction=None,signed_discrepancy=None,absolute_discrepancy=None,comparison_status='unavailable')
    summary=next(x for x in report['construction_summaries'] if x['constructor_id']==cid)
    summary['complete_analysis_slots']=2
    if not provider:
        summary['successful_executions']=2
    for j,e in enumerate(summary['endpoints']):
        e.update(available_values=2,available_discrepancies=2,complete=False,mean_absolute_discrepancy=None,
            available_value_mean_absolute_discrepancy=2.5+j/10,mean_effect=2.5+j/10,
            seed_effect_range=[2+j/10,3+j/10],seed_directions=[None,'positive','positive'],summary_status='incomplete_available_values_only')
    for j,c in enumerate(x for x in report['agent_information_contrasts'] if x['case_id']=='CHNS2009'):
        c['arms']['E0'].update(constructors_with_complete_endpoint=4,complete=False,
            mean_constructor_mean_absolute_discrepancy=None,incomplete_available_value_mean=4.1+j/10,available_value_mean=4.1+j/10)
        c.update(status='incomplete_no_complete_arm_advantage_claim',E1_minus_E0_mean_absolute_discrepancy=None,
            incomplete_available_value_contrast=9.9,complete_arm_comparison_available=False)
    report['complete_analysis_slots']-=1
    return args


class AuditV2Tests(unittest.TestCase):
    def test_complete_fixture_and_constructor_first_arithmetic(self):
        result=r.review_report(*fixture())
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['status'],'matched')
        self.assertTrue(result['complete_numerical_validation'])

    def test_provider_failure_preserved_and_incomplete_contrast(self):
        args=with_failure(fixture())
        result=r.review_report(*args)
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['status'],'matched_with_preserved_provider_failures')
        self.assertFalse(result['complete_numerical_validation'])
        self.assertTrue(result['provider_failures'][0]['independently_computable'])
        self.assertFalse(result['provider_failures'][0]['primary_values_validated'])
        args[0]['agent_information_contrasts'][0]['incomplete_available_value_contrast']=10.0
        self.assertEqual(r.review_report(*args)['status'],'mismatch')

    def test_execution_failure_preserved_and_checked_against_ledger(self):
        args=with_failure(fixture(),provider=False)
        result=r.review_report(*args)
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['status'],'matched_with_unavailable_slots')
        self.assertFalse(result['complete_numerical_validation'])
        args[0]['all_scheduled_slots'][0]['error']['message']='changed'
        self.assertEqual(r.review_report(*args)['status'],'mismatch')

    def test_reject_missing_contrast_duplicate_endpoint_or_wrong_seed(self):
        for field in ['contrast','endpoint','seed']:
            args=fixture()
            if field=='contrast':
                args[0]['agent_information_contrasts'].pop()
            elif field=='endpoint':
                args[0]['all_scheduled_slots'][0]['analyses'][1]=copy.deepcopy(args[0]['all_scheduled_slots'][0]['analyses'][0])
            else:
                args[0]['all_scheduled_slots'][0]['seed']=9999
            self.assertEqual(r.review_report(*args)['status'],'mismatch',field)

    def test_summary_mutation_and_exact_quantile_comparison(self):
        args=fixture()
        args[0]['construction_summaries'][0]['endpoints'][0]['mean_effect']+=1
        self.assertEqual(r.review_report(*args)['status'],'mismatch')
        args=fixture()
        row=args[0]['all_scheduled_slots'][0]['diagnostics'][0]
        row['value']=float(np.nextafter(row['value'],np.inf))
        result=r.review_report(*args)
        self.assertEqual(result['status'],'mismatch')
        self.assertTrue(any(x['kind']=='value' and x['location'].endswith('/value') for x in result['errors']))

    def test_invented_projections_and_rank_gate(self):
        rows=list(itertools.product([30,45,60,75],[0,1],[22.,28.],[90.,110.]))
        frame=pd.DataFrame(rows,columns=['age','female','bmi','glucose'])
        frame['hba1c']=4+.1*(frame.age-50)/10+.2*frame.female+.3*(frame.bmi-25)/5+.4*(frame.glucose-100)/10
        result=r.calculate(frame,'ENSANUT2018',enforce_task=False)
        for key,value in {'Q1_age10':.1,'Q2_bmi5':.3,'Q3_bmi5':.3,'Q2_minus_Q3_bmi5':0.,'glucose10_age_sex':.4}.items():
            self.assertAlmostEqual(result[key],value,places=12)
        self.assertIsNone(r.qr_fit(np.ones((8,2)),np.arange(8.),np.ones(8))[0])

    def test_barrier_before_results_reference_or_manifest(self):
        with patch.object(r.control,'READ',return_value={}) as read,patch.object(r.control,'require_campaign_closed',side_effect=ValueError('still open')):
            with self.assertRaisesRegex(ValueError,'still open'):
                r.audit('release','results','never_created')
            read.assert_called_once_with('release')


if __name__=='__main__':
    unittest.main()
