"""Curate M12-A invented engineering artifacts and verify historical byte preservation."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[2]
EXPORT = PROJECT.parent / 'github_virtual_cohort_2026-10-27/biomedical_research/virtual_cohort_system'
REPORT = PROJECT / 'reports/source_context_engineering_2026-10-30'
sys.path.insert(0, str(PROJECT))
from cohort_harness.source_replay_v2 import verify_source_replay


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n', encoding='utf-8')


baseline = '74f5c0d4d5388677501a505b665490e127a7a22c'
git_root = PROJECT.parent / 'github_virtual_cohort_2026-10-27'
prefix = 'biomedical_research/virtual_cohort_system/'
paths = subprocess.check_output(['git', '-C', str(git_root), 'ls-tree', '-r', '--name-only', baseline,
    prefix + 'cohort_harness/'], text=True).splitlines()
old_engines = {name.removeprefix(prefix): hashlib.sha256(subprocess.check_output(
    ['git', '-C', str(git_root), 'show', baseline + ':' + name])).hexdigest()
    for name in paths if name.endswith('.py')}
engine_mismatches = [name for name, expected in old_engines.items() if sha(PROJECT / name) != expected]
assert not engine_mismatches, engine_mismatches
historical = PROJECT / 'reports/source_location_transfer_2026-10-30'
old_manifest = json.loads((historical / 'file_manifest.json').read_text(encoding='utf-8-sig'))['files']
history_mismatches = [name for name, expected in old_manifest.items() if sha(historical / name) != expected]
assert not history_mismatches, history_mismatches
write(REPORT / 'historical_compatibility.json', {
    'scope': 'Byte checks, not a new target analysis',
    'baseline_export_commit': '74f5c0d4d5388677501a505b665490e127a7a22c',
    'old_engine_files_unchanged': len(old_engines), 'old_engine_hashes': old_engines,
    'm11_curated_artifacts_unchanged': len(old_manifest), 'mismatches': []})

fixture = REPORT / 'invented_fixture'
original_fixture = PROJECT / 'work/m12a-smoke-02'
if fixture.exists():
    original_files = {p.relative_to(original_fixture).as_posix(): sha(p) for p in original_fixture.rglob('*') if p.is_file()}
    copied_files = {p.relative_to(fixture).as_posix(): sha(p) for p in fixture.rglob('*') if p.is_file()}
    assert copied_files == original_files, 'Existing fixture differs; do not overwrite'
else:
    shutil.copytree(original_fixture, fixture)
verified = verify_source_replay(fixture, 'independent_source', candidate='candidates/initial')
assert verified['status'] == 'success'
write(REPORT / 'curated_verification.json', {
    'scope': 'Copied invented fixture verified by unchanged execution/statistic engines and v2 adapter',
    'status': verified['status'], 'source_contexts': len(verified['contexts']),
    'generator_process_isolated': True, 'agent_tool_isolation_provided': False,
    'contains_participant_data': False, 'new_biomedical_results': False})
write(REPORT / 'development_checks.json', {
    'full_suite': {'passed': 384, 'skipped': 1,
        'skip_reason': 'Windows user cannot create the symlink fixture'},
    'new_targeted_tests': 82,
    'intermediate_findings': [
        'Malformed source operators were initially checked after launch; preflight added.',
        'CSV category dtype initially came from target; source schema now controls parsing.',
        'Case-insensitive context ID collisions now fail before launching.',
        'Empty-frame preflight missed string/numeric ordering; typed scalar validation added.'],
    'intermediate_environment_failures': [
        'Long pytest scratch path exceeded nested Windows path limit: 6 failures, 67 passed.',
        'First shortened scratch attempt had a missing parent: 16 setup errors, 57 passed.',
        'Fresh short scratch parent resolved both environment failures.',
        'Initial curation verifier call used shorthand initial; corrected to candidates/initial and verified the unchanged copy.'],
    'preliminary_smoke': 'work/m12a-smoke-01 passed before the additional filter preflight fix; superseded by smoke-02.',
    'final_smoke': 'Actual WSL/bubblewrap run; source mean 18; slope 1.9999999999999996; target and parent unchanged'})
if Path(__file__).resolve() != (REPORT / 'curation_script.py').resolve():
    shutil.copyfile(__file__, REPORT / 'curation_script.py')
files = {p.relative_to(REPORT).as_posix(): sha(p) for p in REPORT.rglob('*')
         if p.is_file() and p.name != 'file_manifest.json'}
write(REPORT / 'file_manifest.json', {'scope': 'Invented engineering fixture and tests only; no participant data',
                                    'files': files})
print(json.dumps({'old_engines': len(old_engines), 'm11_files': len(old_manifest),
                  'curated_fixture_verified': True, 'curated_files': len(files)}, indent=2))
