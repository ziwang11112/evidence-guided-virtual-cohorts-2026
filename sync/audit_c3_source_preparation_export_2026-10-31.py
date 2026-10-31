"""Verify this exact C3 preparation export using file/metadata checks only."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

MANIFEST = 'sync/C3_SOURCE_PREPARATION_EXPORT_MANIFEST_2026-10-31.json'
AUDIT = 'sync/C3_SOURCE_PREPARATION_EXPORT_AUDIT_2026-10-31.json'
CASE = 'biomedical_research/virtual_cohort_system/reports/c3s'
SECRET_PATTERNS = {
    'github_token': r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,})',
    'provider_key': r'\bsk-[A-Za-z0-9_-]{20,}',
    'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'aws_access_key': r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b',
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical_sha(obj, ensure_ascii=True):
    return sha(json.dumps(obj, sort_keys=True, ensure_ascii=ensure_ascii,
                          separators=(',', ':'), allow_nan=False).encode())

def safe(root, name):
    p = root / name
    assert not Path(name).is_absolute() and '..' not in Path(name).parts
    assert not p.is_symlink() and p.resolve().is_relative_to(root)
    return p

def possible_individual_records(obj):
    if isinstance(obj, dict):
        matches = [v for k, v in obj.items() if str(k).lower() in
                   {'age', 'female', 'bmi', 'fpg', 'hba1c', 'glucose', 'weight', 'height'}]
        if len(matches) >= 4 and all(not isinstance(v, (dict, list)) for v in matches):
            return True
        return any(possible_individual_records(v) for v in obj.values())
    if isinstance(obj, list):
        return any(possible_individual_records(v) for v in obj)
    return False

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--export', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--local-receipt', type=Path)
    args = parser.parse_args()
    root, workspace = args.export.resolve(strict=True), args.workspace.resolve(strict=True)
    raw_manifest = safe(root, MANIFEST).read_bytes()
    manifest = json.loads(raw_manifest)
    findings, retained_local_references, path_references = [], [], []
    counters = {'json': 0, 'python': 0, 'markdown': 0, 'log': 0, 'links': 0, 'bindings': 0}

    def flag(rule, **detail):
        findings.append({'rule': rule, **detail})

    def git(*values):
        return subprocess.check_output(['git', *values], cwd=root)

    before = manifest['prior_head']
    if git('rev-parse', 'HEAD').decode().strip() != before:
        flag('head_changed_during_preparation')
    records = manifest['files']
    expected = {x['destination'] for x in records} | {MANIFEST, AUDIT}
    if len(records) != len({x['destination'] for x in records}) or expected != set(manifest['expected_delta']):
        flag('manifest_delta_inconsistent')
    changed = set(git('diff', '--name-only', before).decode().splitlines())
    changed.update(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    changed.add(AUDIT)  # The first audit creates this one planned receipt.
    if changed != expected:
        flag('unexpected_delta', missing=sorted(expected-changed), unexpected=sorted(changed-expected))
    old_names, old_count = set(), 0
    for entry in git('ls-tree', '-rz', before).split(b'\0'):
        if not entry:
            continue
        metadata, encoded_name = entry.split(b'\t', 1)
        _, kind, object_id = metadata.decode().split()
        name = encoded_name.decode()
        old_names.add(name)
        if kind != 'blob':
            flag('unexpected_nonblob', file=name)
            continue
        path = safe(root, name)
        if os.name == 'nt':
            path = Path('\\\\?\\' + str(path))
        if not path.is_file():
            flag('historical_file_missing', file=name)
            continue
        raw = path.read_bytes()
        if hashlib.sha1(('blob ' + str(len(raw)) + '\0').encode() + raw).hexdigest() != object_id:
            flag('historical_bytes_changed', file=name)
        old_count += 1
    if old_names & expected:
        flag('tracked_file_overwrite', files=sorted(old_names & expected))

    source_summaries = {}
    for record in records:
        name = record['destination']
        path = safe(root, name)
        raw, original = path.read_bytes(), safe(workspace, record['source']).read_bytes()
        if sha(raw) != record['export_sha256'] or len(raw) != record['export_bytes']:
            flag('export_hash_or_size_mismatch', file=name)
        if sha(original) != record['source_sha256'] or len(original) != record['source_bytes']:
            flag('source_changed_since_selection', file=name)
        transformed = original
        for old, new in record['transformations']:
            transformed = transformed.replace(old.encode(), new.encode())
        if transformed != raw:
            flag('unrecorded_transformation', file=name)
        if path.suffix in {'.json', '.py'} and raw != original:
            flag('code_or_json_not_byte_preserved', file=name)
        forbidden = {'source_calibration', 'executions', 'history', '__pycache__', 'raw', 'downloads', 'outputs'}
        if forbidden & set(Path(name).parts) or path.name in {'STATE.json', 'STATE_HISTORY.jsonl', 'calibration_budget.json'}:
            flag('forbidden_payload_path', file=name)
        if path.suffix not in {'.py', '.json', '.md', '.log'}:
            flag('unapproved_extension', file=name)
        if path.suffix == '.log' and name != CASE + '/method/test_results_final.log':
            flag('unapproved_log', file=name)
        text = raw.decode('utf-8-sig')
        for rule, pattern in SECRET_PATTERNS.items():
            if re.search(pattern, text):
                flag(rule, file=name)
        if re.search(r'\bDESKTOP-[A-Za-z0-9]+\b|hostname\s*=\s*["\'][^"\']+["\']', text):
            flag('machine_hostname', file=name)
        if re.search(r'[A-Za-z]:[\\/]+(?:Users|AIR-|Codex)|/(?:home|Users)/', text):
            path_references.append(name)
        if path.suffix == '.json':
            counters['json'] += 1
            if possible_individual_records(json.loads(text)):
                flag('possible_individual_measurement_records', file=name)
        elif path.suffix == '.py':
            counters['python'] += 1
            ast.parse(text)  # Syntax only: never import or execute the submitted source.
        elif path.suffix == '.log':
            counters['log'] += 1
            if not re.fullmatch(r'\.+\s+\[100%\]\s+22 passed in 39\.82s\s*', text):
                flag('unexpected_mock_summary_content', file=name)
        elif path.suffix == '.md':
            counters['markdown'] += 1
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
                target = target.strip('<>')
                if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', target) or target.startswith('#'):
                    continue
                target = unquote(target.split('#', 1)[0])
                if target:
                    counters['links'] += 1
                    resolved = (path.parent / target).resolve()
                    if not resolved.is_relative_to(root) or (not resolved.exists() and resolved != root/AUDIT):
                        retained_local_references.append({'file': name, 'target': target})
        if record['classification'] == 'short_authored_source_summary':
            source_summaries[name] = len(raw)
            if path.name != 'source_summary.md' or len(raw) > 2000:
                flag('non_summary_source_payload', file=name)
    if len(source_summaries) != 12:
        flag('source_summary_count', count=len(source_summaries))

    case = root / CASE
    def read(path):
        return json.loads(path.read_bytes())
    def binding(path, digest, label):
        counters['bindings'] += 1
        if not path.is_file() or sha(path.read_bytes()) != digest:
            flag('provenance_binding_mismatch', binding=label)
    def value_binding(value, digest, label, ensure_ascii=True):
        counters['bindings'] += 1
        if canonical_sha(value, ensure_ascii) != digest:
            flag('canonical_provenance_binding_mismatch', binding=label)

    for name, digest in read(case/'INPUT_MANIFEST.json')['files'].items():
        binding(case/'inputs'/name, digest, 'input:'+name)
    omitted = []
    for name, digest in read(case/'review/PREEXECUTION_REVIEW_BINDINGS.json')['files'].items():
        if name == 'method/test_results_final.xml':
            omitted.append({'binding': name, 'sha256': digest, 'reason': 'Local hostname; intentionally excluded'})
        else:
            binding(case/name, digest, 'review:'+name)
    release_set = read(case/'ROOT_RELEASE_SET.json')
    for name, digest in release_set['bindings'].items():
        binding(case/name, digest, 'root:'+name)
    for structure in ['linear', 'alternative']:
        bundle = case/structure
        release_meta = release_set['structures'][structure]
        binding(case/release_meta['release'], release_meta['release_sha256'], structure+':release')
        for key, name in [('initial_freeze_sha256', 'candidates/initial/freeze.json'),
                          ('plan_sha256', 'calibration_plan.json'), ('criteria_sha256', 'scientific_criteria.json')]:
            binding(bundle/name, release_meta[key], structure+':'+key)
        frozen = read(bundle/'candidates/initial/freeze.json')
        for name, digest in frozen['commitments'].items():
            binding(bundle/name, digest, structure+':freeze:'+name)
        snapshot = frozen['registry_snapshot']
        value_binding(read(bundle/snapshot['path'])['artifacts'][:snapshot['artifact_count']],
                      snapshot['sha256'], structure+':registry_snapshot', ensure_ascii=False)
        available = {x.relative_to(bundle).as_posix() for x in (bundle/'candidates/initial').rglob('*')
                     if x.is_file() and x.name != 'freeze.json'}
        if available != set(frozen['candidate_files']):
            flag('incomplete_frozen_initial_candidate', structure=structure)
        release = read(case/(structure+'_RELEASE.json'))
        validation = read(case/(structure+'_VALIDATION.json'))
        if release['binding'] != validation['binding']:
            flag('release_validation_binding_disagrees', structure=structure)
        b = release['binding']
        for name, key in [('task.json', 'task_sha256'), ('candidates/initial/freeze.json', 'parent_freeze_sha256')]:
            binding(bundle/name, b[key], structure+':validated:'+key)
        binding(case/'method/run_source_calibration.py', b['adapter_sha256'], structure+':adapter')
        value_binding(read(bundle/'calibration_plan.json'), b['plan_sha256'], structure+':canonical_plan')
        value_binding(read(bundle/'scientific_criteria.json'), b['criteria_sha256'], structure+':canonical_criteria')
    controller = (case/'controller_run.py').read_text(encoding='utf-8-sig')
    expected_root_hash = re.search(r"assert sha\(gate_path\) == '([0-9a-f]{64})'", controller)
    if not expected_root_hash:
        flag('controller_root_release_binding_missing')
    else:
        binding(case/'ROOT_RELEASE_SET.json', expected_root_hash.group(1), 'controller:release_set')

    audit = {'status': 'PASS' if not findings else 'FAIL',
        'scope': 'Exact initial C3 source export; filesystem, syntax and metadata checks only.',
        'prior_head': before, 'manifest_sha256': sha(raw_manifest),
        'source_project_file_count': manifest['source_project_file_count'], 'expected_new_file_count': len(expected),
        'historical_tracked_blobs_byte_verified': old_count,
        'historical_tracked_edits': 0 if not old_names & expected and not any(x['rule'].startswith('historical_') for x in findings) else None,
        'files_checked': counters, 'short_source_summaries': source_summaries,
        'omitted_bound_artifacts': omitted, 'retained_local_navigation_references': retained_local_references,
        'machine_specific_path_references': path_references,
        'privacy_scope': 'Exact authored-file allowlist, forbidden payload paths/extensions, recognizable credential and individual-record patterns, short source-summary limit; no claim of automated proof against every possible privacy issue.',
        'code_and_json_byte_preserved': not any(x['rule'] == 'code_or_json_not_byte_preserved' for x in findings),
        'scientific_tests_rerun': False, 'scientific_execution_performed': False,
        'generated_table_or_calibration_result_contents_read': False, 'commit_or_push_performed': False,
        'original_engine_runtime_environment_reconstructed': False,
        'findings': findings, 'expected_delta': sorted(expected)}
    raw_audit = (json.dumps(audit, indent=2, ensure_ascii=False) + '\n').encode()
    safe(root, AUDIT).write_bytes(raw_audit)
    if args.local_receipt:
        args.local_receipt.write_bytes(raw_audit)
    print(json.dumps({k: audit[k] for k in ['status', 'source_project_file_count', 'expected_new_file_count',
        'historical_tracked_blobs_byte_verified', 'files_checked', 'retained_local_navigation_references',
        'machine_specific_path_references', 'findings']}, indent=2))
    raise SystemExit(bool(findings))

if __name__ == '__main__':
    main()
