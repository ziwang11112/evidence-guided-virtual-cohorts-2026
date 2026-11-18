"""Small offline probe review. Never calls download() or any HTTP transport."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'probe.py'
spec = importlib.util.spec_from_file_location('reviewed_probe', SOURCE)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def production_reservation_only(directory):
    """Compile only existing pre-network statements, under another function name.

    Stop before the time.monotonic assignment and the network try block. This
    checks the real persistent reservation primitive without invoking download.
    """
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'download')
    preflight = []
    for statement in fn.body:
        if isinstance(statement, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == 'start' for t in statement.targets):
            break
        preflight.append(copy.deepcopy(statement))
    assert len(preflight) == 4 and isinstance(preflight[-1], ast.With)
    fn = ast.FunctionDef(name='reserve_only', args=copy.deepcopy(fn.args),
                         body=preflight, decorator_list=[])
    isolated = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    namespace = dict(probe.__dict__)
    namespace.update(ROOT=directory, verify_parent=lambda: {'offline_fixture': 'unchanged'})
    exec(compile(isolated, '<production-reservation-only>', 'exec'), namespace)
    return namespace['reserve_only']


class OfflineAccessReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen_before = probe.frozen_hashes()
        cls.network_guard = patch.object(socket.socket, 'connect', side_effect=AssertionError('Network prohibited in review'))
        cls.network_guard.start()

    @classmethod
    def tearDownClass(cls):
        cls.network_guard.stop()
        if probe.frozen_hashes() != cls.frozen_before:
            raise AssertionError('Original source/task/config/session bytes changed during review')

    def test_original_parent_provenance_read_only(self):
        self.assertEqual(probe.verify_parent(), self.frozen_before)

    def test_known_container_magic(self):
        self.assertEqual(probe.detect_format(bytes.fromhex('d0cf11e0a1b11ae1') + b'fixture'), 'OLE_compound_document')
        self.assertEqual(probe.detect_format(b'  {\\rtf1 fixture}'), 'RTF')
        self.assertEqual(probe.detect_format(b'PK\x03\x04fixture'), 'ZIP_container_requires_inspection')

    def test_unknown_container_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unrecognized document magic'):
            probe.detect_format(b'<html>fixture</html>')

    def test_fixture_payload_accepted_with_matching_checksum(self):
        raw = b'{\\rtf1 offline fixture}'
        with patch.object(probe, 'MD5', hashlib.md5(raw).hexdigest()):
            self.assertEqual(probe.check_payload(raw, 'application/msword', str(len(raw))), 'RTF')

    def test_official_binary_mime_accepted_with_matching_checksum(self):
        raw = b'{\\rtf1 offline fixture}'
        with patch.object(probe, 'MD5', hashlib.md5(raw).hexdigest()):
            self.assertEqual(probe.check_payload(raw, 'binary/octet-stream', str(len(raw))), 'RTF')

    def test_fixture_checksum_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Manifest checksum failed'):
            probe.check_payload(b'{\\rtf1 wrong bytes}', 'application/msword', None)

    def test_fixture_response_size_and_truncation_rejected(self):
        for raw, length, message in [(b'', None, 'Response size limit'),
                                     (b'12345', None, 'Response size limit'),
                                     (b'1234', '5', 'Incomplete response')]:
            with self.subTest(message=message, raw_length=len(raw)):
                with patch.object(probe, 'LIMIT', 4), self.assertRaisesRegex(ValueError, message):
                    probe.check_payload(raw, 'application/msword', length)

    def test_fixture_html_content_type_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unexpected response content type'):
            probe.check_payload(b'{\\rtf1 fixture}', 'text/html', None)

    def test_redirect_rejected_without_network(self):
        with self.assertRaisesRegex(ValueError, 'Redirect prohibited'):
            probe.NoRedirect().redirect_request(None, None, 302, 'Moved', {}, 'https://example.invalid/')

    def test_original_screen_accepts_benign_fixture(self):
        self.assertIsNone(probe.screen_text('Review fixture: body and table text only.'))

    def test_original_screen_handles_encoded_table_aliases(self):
        config_path = probe.BUNDLE / 'gateway/config.json'
        fixture_config = json.dumps({'exclusions': {
            'compact_aliases': ['ReviewExcludedCohort'],
            'regexes': [r'\bHiddenFixture\b']}})
        original_read_text = Path.read_text

        def fixture_read_text(path, *args, **kwargs):
            if path == config_path:
                return fixture_config
            return original_read_text(path, *args, **kwargs)

        variants = ['Table header\nReviewExcludedCohort\tcoefficient',
                    'Review<b>Excluded</b>Cohort', 'Review%45xcludedCohort',
                    'Review&#69;xcludedCohort', 'Review\u200bExcludedCohort']
        with patch.object(Path, 'read_text', fixture_read_text):
            for text in variants:
                with self.subTest(encoding_case=variants.index(text)):
                    with self.assertRaisesRegex(Exception, 'excluded_study_alias'):
                        probe.screen_text(text)
            with self.assertRaisesRegex(Exception, 'excluded_configured_pattern'):
                probe.screen_text('Metadata field: HiddenFixture')

    def test_persistent_second_reservation_rejected(self):
        with tempfile.TemporaryDirectory(prefix='review_fixture_', dir=HERE) as temp:
            directory = Path(temp)
            production_reservation_only(directory)()
            receipt = directory / 'ACQUISITION_RECEIPT.json'
            first_bytes = receipt.read_bytes()
            first = json.loads(first_bytes)
            self.assertEqual(first['status'], 'attempt_reserved')
            self.assertEqual(first['http_attempts'], 1)
            self.assertEqual(first['attempt_limit'], 1)
            # A fresh compiled function sees the same persistent reservation.
            with self.assertRaises(FileExistsError):
                production_reservation_only(directory)()
            self.assertEqual(receipt.read_bytes(), first_bytes)


if __name__ == '__main__':
    print('Reviewed probe.py SHA256:', hashlib.sha256(SOURCE.read_bytes()).hexdigest())
    unittest.main(verbosity=2)
