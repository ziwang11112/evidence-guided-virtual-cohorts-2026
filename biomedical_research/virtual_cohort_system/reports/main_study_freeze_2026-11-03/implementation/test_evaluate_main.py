"""Artificial endpoint lists and mocked lifecycle only; no clinical evaluation."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import copy
import json
import unittest

import evaluate_main as ev

SEEDS=(5101,5102,5103)


def metadata():
    # Only coordinator path/schema metadata, never any referenced report.
    return json.loads(ev.DEFAULT_BINDINGS.read_text(encoding='utf-8'))


def references(bindings):
    return {case:{item['id']:{'value':10.,'unit':item['unit'],'status':'available',
          'interval':ev.interval_record({'lower':8.,'upper':12.},'invented test interval')}
          for category in ('analyses','diagnostics') for item in spec[category]}
          for case,spec in bindings['cases'].items()}


def scheduled(bindings):
    records=[]
    refs=references(bindings)
    for case,spec in bindings['cases'].items():
        for condition in ('E0','E1'):
            for index in range(6):
                kind='agent' if index<5 else 'statistical'
                identity=f'{case}_{condition}_{kind}_{index}'
                for offset,seed in zip((-.1,0.,.1),SEEDS):
                    error=(index+1)*(1. if condition=='E0' else .5)+offset
                    payload={category:[{'id':item['id'],'unit':item['unit'],'status':'computed','value':10.+error}
                       for item in spec[category]] for category in ('analyses','diagnostics')}
                    records.append({'constructor_id':identity,'case_id':case,'information_condition':condition,
                      'constructor_kind':kind,'seed':seed,'execution_status':'success','analysis_status':'complete',
                      **ev.add_reference(payload,refs[case])})
    return records


class FinalEvaluationTests(unittest.TestCase):
    def test_constructor_then_arm_mean_contrast_and_units(self):
        bindings=metadata()
        report=ev.summarize(scheduled(bindings),bindings,seeds=SEEDS)
        self.assertEqual(len(report['construction_summaries']),24)
        self.assertEqual(len(report['statistical_references']),4)
        self.assertEqual(len(report['agent_information_contrasts']),6)
        for contrast in report['agent_information_contrasts']:
            self.assertTrue(contrast['complete_arm_comparison_available'])
            self.assertAlmostEqual(contrast['E1_minus_E0_mean_absolute_discrepancy'],-1.5)
        units={c['unit'] for c in report['agent_information_contrasts']}
        self.assertIn('%/(mmol/L)',units)
        self.assertIn('%/5kg/m^2',units)

    def test_missing_seed_preserved_and_complete_contrast_withheld(self):
        bindings=metadata(); slots=scheduled(bindings)
        bad=next(r for r in slots if r['case_id']=='CHNS2009' and r['information_condition']=='E1' and r['constructor_id'].endswith('agent_0') and r['seed']==5102)
        bad['analysis_status']='incomplete'
        row=bad['analyses'][0]
        row.update(value=None,status='unavailable',absolute_discrepancy=None,signed_discrepancy=None,generated_direction=None)
        report=ev.summarize(slots,bindings,seeds=SEEDS)
        contrast=next(c for c in report['agent_information_contrasts'] if c['case_id']=='CHNS2009' and c['endpoint']=='E1')
        self.assertFalse(contrast['complete_arm_comparison_available'])
        self.assertIsNone(contrast['E1_minus_E0_mean_absolute_discrepancy'])
        self.assertIsNotNone(contrast['incomplete_available_value_contrast'])
        self.assertEqual(contrast['arms']['E1']['represented_constructors'],5)
        self.assertEqual(contrast['arms']['E1']['constructors_with_complete_endpoint'],4)
        self.assertEqual(len(slots),72)

    def test_abandoned_constructor_retained_in_denominator(self):
        bindings=metadata(); slots=scheduled(bindings)
        identity='ENSANUT2018_E0_agent_0'
        refs=references(bindings)
        for row in slots:
            if row['constructor_id']==identity:
                row.update(execution_status='not_attempted',analysis_status='unavailable')
                row.update(ev.add_reference(ev.missing_payload(bindings['cases']['ENSANUT2018'],'abandoned'),refs['ENSANUT2018']))
        summary=ev.summarize(slots,bindings,seeds=SEEDS)
        entry=next(c for c in summary['construction_summaries'] if c['constructor_id']==identity)
        self.assertEqual(entry['scheduled_final_slots'],3)
        self.assertEqual(entry['successful_executions'],0)
        self.assertTrue(all(x['available_values']==0 and not x['complete'] for x in entry['endpoints']))
        self.assertEqual(len(summary['construction_summaries']),24)

    def test_barrier_failure_prevents_reference_or_binding_load(self):
        with patch.object(ev.session,'READ',return_value={'fake':'release'}) as read, \
             patch.object(ev.session,'require_campaign_closed',side_effect=ValueError('not all closed')) as gate, \
             patch.object(ev,'load_references') as loader, \
             patch.object(ev,'_require_bound_release_file') as bindings:
            with self.assertRaisesRegex(ValueError,'not all closed'):
                ev.evaluate(Path('invented_release.json'),Path('must_not_create_results'))
            read.assert_called_once()
            gate.assert_called_once()
            loader.assert_not_called()
            bindings.assert_not_called()

    def test_payload_failure_coverage_unit_and_interval(self):
        bindings=metadata()
        for case,spec in bindings['cases'].items():
            payload=ev.missing_payload(spec,'invented failure')
            ev.validate_payload(payload,spec)
            self.assertEqual(len(payload['diagnostics']),27 if case=='CHNS2009' else 28)
            malformed=copy.deepcopy(payload); malformed['diagnostics'].pop()
            with self.assertRaises(Exception):ev.validate_payload(malformed,spec)
            malformed=copy.deepcopy(payload); malformed['analyses'][0]['unit']='wrong_unit'
            with self.assertRaises(Exception):ev.validate_payload(malformed,spec)
        self.assertEqual(ev.interval_record({'lower':-1.,'upper':1.},'toy')['direction'],'includes_zero')
        self.assertFalse(ev.interval_record(None,'toy')['equivalence_margin'])

    def test_slot_collector_keeps_all_72_with_one_abandonment_and_failure(self):
        bindings=metadata(); refs=references(bindings)
        records=scheduled(bindings)
        ids=sorted({r['constructor_id'] for r in records})
        abandoned=ids[0]; failed=ids[1]; bad_provider=ids[2]
        lookup={identity:next(r for r in records if r['constructor_id']==identity) for identity in ids}

        class FakeSession:
            def __init__(self,root):
                self.identity=str(root); row=lookup[self.identity]
                self.bundle=Path('artificial_bundle')
                self.contract={'case_id':row['case_id'],'information_condition':row['information_condition'],
                 'constructor_kind':row['constructor_kind'],'provider':'invented_provider.py','profile':'invented_profile.json'}
            def selected(self,kind):
                if kind=='closed':return [{'status':'construction_failed' if self.identity==abandoned else 'all_final_slots_consumed','reason':'invented test'}]
                if self.identity==abandoned:return []
                if kind=='attempt':return [{'index':i,'purpose':'final','seed':s,'run_id':str(s),'candidate':'candidates/final'} for i,s in enumerate(SEEDS)]
                if kind=='result':return [{'attempt_index':i,'status':'failed' if self.identity==failed and i==1 else 'success','error':None} for i in range(3)]
                return []

        def fake_spec(name,path):
            identity=name.removeprefix('main_final_provider_'); case=lookup[identity]['case_id']
            def populate(module):
                def generated(*args):
                    if identity==bad_provider:raise ValueError('invented provider failure after successful generation')
                    return {category:[{'id':i['id'],'unit':i['unit'],'status':'computed','value':9.} for i in bindings['cases'][case][category]] for category in ('analyses','diagnostics')}
                module.evaluate_generated=generated
            return SimpleNamespace(loader=SimpleNamespace(exec_module=populate))

        release={'constructions':[{'id':i,'session_root':i} for i in ids]}
        with patch.object(ev.session,'Session',FakeSession), \
             patch.object(ev.session,'SHA',return_value='a'*64), \
             patch.object(ev.importlib.util,'spec_from_file_location',side_effect=fake_spec), \
             patch.object(ev.importlib.util,'module_from_spec',side_effect=lambda spec:SimpleNamespace()):
            out=ev.collect_slots(release,bindings,refs)
        self.assertEqual(len(out),72)
        self.assertEqual(sum(r['execution_status']=='not_attempted' for r in out),3)
        self.assertEqual(sum(r['execution_status']=='failed' for r in out),1)
        for row in out:
            self.assertEqual(len(row['analyses']),3)
            self.assertEqual(len(row['diagnostics']),27 if row['case_id']=='CHNS2009' else 28)
        self.assertEqual(sum(r['analysis_status']=='complete' for r in out),65)
        self.assertEqual(sum(r['analysis_status']=='provider_error' for r in out),3)
        self.assertEqual(sum(r['output_sha256'] is not None for r in out),68)


if __name__=='__main__':
    unittest.main()
