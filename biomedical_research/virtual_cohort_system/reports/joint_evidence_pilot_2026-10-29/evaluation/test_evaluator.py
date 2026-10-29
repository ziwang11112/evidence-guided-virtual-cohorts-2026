"""M8 pre-release checks: invented inputs only, with participant-file IO blocked."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime, timezone

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ORIGINAL = HERE.parents[1] / 'analysis-evidence-gap-2026-10-29' / 'custodian'

def deny_participant_files(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, pathlib.Path)):
        path = pathlib.Path(args[0].decode() if isinstance(args[0], bytes) else args[0])
        if path.suffix.lower() in {'.csv', '.xpt', '.sas7bdat'}:
            raise RuntimeError('Participant-table file IO is forbidden in invented tests')

sys.addaudithook(deny_participant_files)
import numpy as np
import pandas as pd
import survey_analysis as amended
import evaluate_committed as evaluator

def deny_csv(*args, **kwargs):
    raise RuntimeError('CSV parsing is forbidden in invented tests')

pd.read_csv = deny_csv
spec = importlib.util.spec_from_file_location('frozen_m7_survey_analysis', ORIGINAL / 'survey_analysis.py')
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)

def invented_fixture(two_ages=False):
    rows = []
    for age in [45, 65]:
        for sex in [1, 2]:
            for bmi in [22, 27, 33]:
                for stratum in [1, 2, 3]:
                    for psu in [1, 2]:
                        for replicate in [0, 1]:
                            rows.append(dict(record_id=f'invented-{len(rows)}',
                                RIDAGEYR=age if two_ages else age + replicate,
                                RIAGENDR=sex, BMXBMI=bmi + .2 * replicate,
                                SDMVSTRA=stratum, SDMVPSU=psu,
                                WTSAF2YR=float(1 + stratum + replicate), eligible=1))
    full = pd.DataFrame(rows)
    values = pd.Series((100 + full.RIDAGEYR * .2 + full.BMXBMI * .6 +
                        full.RIAGENDR * 2 + full.SDMVPSU * 3).to_numpy(), index=full.record_id)
    return full, values

class EvaluatorTests(unittest.TestCase):
    def test_valid_inference_exactly_matches_frozen_evaluator(self):
        full, values = invented_fixture()
        for reference in [True, False]:
            expected = frozen.evaluate(full, values, reference=reference)
            actual = amended.evaluate(full, values, reference=reference)
            self.assertEqual(actual, expected)
            self.assertEqual(len(actual), 67)
            self.assertEqual(sum(key.endswith('_tg_ge150') for key in actual), 12)
            self.assertTrue(all('estimate' in stats for stats in actual.values()))
            if not reference:
                self.assertTrue(all('se' not in stats and 'ci_low' not in stats for stats in actual.values()))
        self.assertEqual(amended.validate_invented()['status'], 'passed')

    def test_partial_rank_failure_preserves_unaffected_models_and_cells(self):
        full, values = invented_fixture(two_ages=True)
        with self.assertRaisesRegex(ValueError, 'Rank-deficient'):
            frozen.evaluate(full, values)
        for reference in [True, False]:
            actual = amended.evaluate(full, values, reference=reference)
            self.assertEqual(len(actual), 67)
            failed = {key for key, stats in actual.items() if stats.get('status') == 'nonestimable'}
            self.assertEqual(failed, {'age_curvature_second_difference', 'raw_age_curvature_second_difference'})
            for key in failed:
                self.assertEqual(actual[key]['reason'], 'Rank-deficient domain design')
                self.assertNotIn('estimate', actual[key])
                self.assertEqual(actual[key]['n'], len(full))
            self.assertIn('estimate', actual['adjusted_age_per10'])
            self.assertIn('estimate', actual['bmi_curvature_second_difference'])
            self.assertIn('estimate', actual['cell_age40_59_sex1_bmi0_arithmetic'])

    def test_constant_age_keeps_all_declared_endpoints(self):
        full, values = invented_fixture()
        full['RIDAGEYR'] = 45
        actual = amended.evaluate(full, values)
        self.assertEqual(len(actual), 67)
        for key in ['adjusted_age_per10', 'adjusted_bmi_per5', 'adjusted_female_vs_male',
                    'age_curvature_second_difference', 'bmi_curvature_second_difference',
                    'raw_age_curvature_second_difference', 'raw_bmi_curvature_second_difference']:
            self.assertEqual(actual[key]['status'], 'nonestimable')
            self.assertEqual(actual[key]['reason'], 'Rank-deficient domain design')
        self.assertIn('estimate', actual['cell_age40_59_sex1_bmi0_arithmetic'])

    def test_empty_and_zero_df_domains_are_explicit(self):
        full, values = invented_fixture()
        for selection, reason in [(np.zeros(len(full), dtype=bool), 'Empty analysis domain'),
                                  ((full.SDMVSTRA == 1) & (full.SDMVPSU == 1),
                                   'No occupied-domain design degrees of freedom')]:
            reduced = full.copy()
            reduced['eligible'] = np.asarray(selection, dtype=int)
            actual = amended.evaluate(reduced, values)
            self.assertEqual(len(actual), 67)
            self.assertTrue(all(stats.get('status') == 'nonestimable' for stats in actual.values()))
            self.assertTrue(all(stats['reason'] == reason for stats in actual.values()))

    def test_invalid_design_is_not_silently_marked_nonestimable(self):
        full, values = invented_fixture(two_ages=True)
        full['SDMVPSU'] = 1
        with self.assertRaisesRegex(ValueError, 'Singleton full-design stratum'):
            amended.evaluate(full, values)

    def test_invalid_outcome_remains_error(self):
        full, values = invented_fixture()
        values.iloc[0] = 0
        with self.assertRaisesRegex(ValueError, 'nonpositive target'):
            amended.evaluate(full, values)

    def test_authorization_denial_and_missing_amendment_prevent_release(self):
        with tempfile.TemporaryDirectory(prefix='invented_gate_') as directory:
            path = pathlib.Path(directory) / 'commitment.json'
            path.write_text(json.dumps({'authorize_target_evaluation': False}), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'authorization'):
                evaluator.verify_preload(path)
            path.write_text(json.dumps({'authorize_target_evaluation': True,
                                        'all_candidates_and_seeds_committed': True}), encoding='utf-8')
            with self.assertRaises(KeyError) as caught:
                evaluator.verify_preload(path)
            self.assertEqual(caught.exception.args[0], 'evaluation_amendment')

    def test_amendment_binds_copied_evaluator_before_custody_access(self):
        with tempfile.TemporaryDirectory(prefix='invented_amendment_') as directory:
            folder = pathlib.Path(directory)
            names = ['analysis_protocol.json', 'survey_analysis.py', 'evaluate_committed.py', 'test_evaluator.py']
            for name in names:
                (folder / name).write_text('invented anchor only\n', encoding='utf-8')
            path = folder / 'protocol_amendment.json'
            path.write_text(json.dumps({'amended_files': {name: evaluator.digest(folder / name) for name in names},
                                        'original_files': []}), encoding='utf-8')
            commitment = {'evaluation_amendment': {'path': str(path), 'sha256': evaluator.digest(path)}}
            with patch.object(evaluator, 'HERE', folder):
                self.assertEqual(evaluator.verify_amendment(commitment)['sha256'], evaluator.digest(path))
                (folder / 'survey_analysis.py').write_text('changed invented anchor\n', encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'Amended evaluator file changed: survey_analysis.py'):
                    evaluator.verify_amendment(commitment)

    def test_frozen_protocol_endpoint_and_inference_definitions_unchanged(self):
        original = json.loads((ORIGINAL / 'analysis_protocol.json').read_text(encoding='utf-8-sig'))
        current = json.loads((HERE / 'analysis_protocol.json').read_text(encoding='utf-8-sig'))
        for key in ['selection', 'visible', 'transforms', 'models', 'endpoints', 'hypotheses',
                    'estimation', 'boundary', 'comparison', 'official_documentation', 'ordered_bmi_contrasts']:
            self.assertEqual(current[key], original[key], key)
        for key, value in original['joint_subgroups'].items():
            if key != 'estimands':
                self.assertEqual(current['joint_subgroups'][key], value, key)
        self.assertEqual(current['joint_subgroups']['estimands'][:2], original['joint_subgroups']['estimands'][:2])

def main():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(EvaluatorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = {'validated_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'passed' if result.wasSuccessful() else 'failed', 'tests_run': result.testsRun,
        'scope': 'invented_fixtures_and_code_protocol_metadata_only',
        'patient_file_io_blocked': True, 'participant_rows_read': False,
        'target_outcomes_analyzed': False, 'scientific_campaign_run': False,
        'frozen_source_sha256': hashlib.sha256((ORIGINAL / 'survey_analysis.py').read_bytes()).hexdigest(),
        'checks': unittest.defaultTestLoader.getTestCaseNames(EvaluatorTests),
        'independent_survey_package_validation': False}
    (HERE / 'invented_validation.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)

if __name__ == '__main__':
    main()
