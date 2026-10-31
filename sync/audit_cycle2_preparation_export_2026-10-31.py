"""Audit the exact cycle-2 preparation checkpoint; never run scientific code or push."""
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

MANIFEST = 'sync/CYCLE2_PREPARATION_EXPORT_MANIFEST_2026-10-31.json'
AUDIT = 'sync/CYCLE2_PREPARATION_EXPORT_AUDIT_2026-10-31.json'
CASE = 'biomedical_research/virtual_cohort_system/reports/autonomous_research_cycle2_2026-10-31'
SECRETS = {
    'github_token': r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,})',
    'provider_key': r'\bsk-[A-Za-z0-9_-]{20,}',
    'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'aws_access_key': r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def safe(root, name):
    p = root / name
    if Path(name).is_absolute() or '..' in Path(name).parts or p.is_symlink() or not p.resolve().is_relative_to(root):
        raise ValueError(f'Unsafe path: {name}')
    return p


def individual_records(obj):
    if isinstance(obj, dict):
        fields = {str(k).lower() for k in obj}
        measurements = fields & {'age', 'female', 'bmi', 'fpg', 'hba1c', 'glucose', 'weight', 'height'}
        if len(measurements) >= 4 and all(not isinstance(obj[k], (dict, list)) for k in obj if str(k).lower() in measurements):
            return True
        return any(individual_records(v) for v in obj.values())
    if isinstance(obj, list):
        return any(individual_records(v) for v in obj)
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--export', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--stage-output', type=Path)
    args = parser.parse_args()
    root, workspace = args.export.resolve(strict=True), args.workspace.resolve(strict=True)
    manifest_raw = safe(root, MANIFEST).read_bytes()
    manifest = json.loads(manifest_raw)
    findings = []

    def git(*values):
        return subprocess.check_output(['git', *values], cwd=root)

    def flag(rule, **detail):
        findings.append({'rule': rule, **detail})

    records = manifest['files']
    selected = {x['destination'] for x in records}
    expected = selected | {MANIFEST, AUDIT}
    if len(records) != len(selected) or expected != set(manifest['expected_delta']):
        flag('manifest_delta_inconsistent')
    before = manifest['prior_head']
    if git('rev-parse', 'HEAD').decode().strip() != before:
        flag('head_changed_during_preparation')
    if manifest['initial_status'] != '':
        flag('baseline_was_not_clean')
    actual = set(git('diff', '--name-only', before).decode().splitlines())
    actual.update(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    # Audit is written at the end; include its fixed planned path on the first run.
    actual.add(AUDIT)
    if actual != expected:
        flag('unexpected_delta', missing=sorted(expected-actual), unexpected=sorted(actual-expected))
    old_tree = git('ls-tree', '-rz', before)
    old_names = set()
    old_count = 0
    for entry in old_tree.split(b'\0'):
        if not entry:
            continue
        metadata, encoded_name = entry.split(b'\t', 1)
        mode, kind, object_id = metadata.decode('ascii').split()
        name = encoded_name.decode('utf-8')
        old_names.add(name)
        if kind != 'blob':
            flag('unexpected_historical_nonblob', file=name)
            continue
        path = safe(root, name)
        if os.name == 'nt':
            path = Path('\\\\?\\' + str(path))
        raw = path.read_bytes()
        digest = hashlib.sha1(('blob ' + str(len(raw)) + '\0').encode() + raw).hexdigest()
        old_count += 1
        if digest != object_id:
            flag('historical_bytes_changed', file=name)
    if old_names & expected:
        flag('checkpoint_overwrites_tracked_paths', files=sorted(old_names & expected))

    json_count = code_count = links = 0
    summary_sizes = {}
    for record in records:
        name = record['destination']
        path = safe(root, name)
        raw = path.read_bytes()
        source_raw = safe(workspace, record['source']).read_bytes()
        if sha(raw) != record['export_sha256'] or len(raw) != record['export_bytes']:
            flag('export_binding_mismatch', file=name)
        if sha(source_raw) != record['source_sha256'] or len(source_raw) != record['source_bytes']:
            flag('source_changed_since_selection', file=name)
        if path.suffix not in {'.py', '.md', '.json'}:
            flag('unapproved_file_type', file=name)
        forbidden = {'private', 'b1', 'b2', 'history', 'results', 'outputs', 'executions', '__pycache__', 'downloads', 'raw'}
        if forbidden.intersection(Path(name).parts) or path.name in {'STATE.json', 'STATE_HISTORY.jsonl', 'DOWNLOAD_LEDGER.json'}:
            flag('forbidden_payload_path', file=name)
        text = raw.decode('utf-8-sig')
        for rule, pattern in SECRETS.items():
            if re.search(pattern, text):
                flag(rule, file=name)
        if re.search(r'[A-Za-z]:[\\/]+(?:Users|AIR-|Codex)|/(?:home|Users)/', text):
            flag('machine_specific_path', file=name)
        if path.suffix in {'.json', '.py'} and raw != source_raw:
            flag('code_or_metadata_not_byte_preserved', file=name)
        if path.suffix == '.json':
            json_count += 1
            if individual_records(json.loads(text)):
                flag('possible_individual_measurement_records', file=name)
        elif path.suffix == '.py':
            code_count += 1
            ast.parse(text)  # Parse only; do not import or execute checkpoint code.
        elif path.suffix == '.md':
            if record['transformations']:
                changed = source_raw
                for old, new in manifest['markdown_navigation_replacements']:
                    changed = changed.replace(old.encode(), new.encode())
                if changed != raw:
                    flag('unrecorded_markdown_change', file=name)
            elif raw != source_raw:
                flag('unrecorded_document_change', file=name)
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
                target = target.strip('<>')
                if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', target) or target.startswith('#'):
                    continue
                target = unquote(target.split('#', 1)[0])
                if target:
                    links += 1
                    resolved = (path.parent / target).resolve()
                    if not resolved.is_relative_to(root) or (not resolved.exists() and resolved != root / AUDIT):
                        flag('broken_local_link', file=name, target=target)
        if '/evidence/packet/sources/' in name:
            summary_sizes[name] = len(raw)
            if path.name != 'source_summary.md' or len(raw) > 2000:
                flag('non_summary_source_payload', file=name)
    if len(summary_sizes) != 4:
        flag('source_summary_count', count=len(summary_sizes))

    case = root / CASE
    packet = case / 'evidence/packet'
    evidence_manifest = json.loads((packet / 'MANIFEST.json').read_bytes())
    internal_checks = 0

    def verify(path, expected_hash, label):
        nonlocal internal_checks
        internal_checks += 1
        if not path.is_file() or sha(path.read_bytes()) != expected_hash:
            flag('internal_provenance_binding', binding=label)

    for item in evidence_manifest['files'] + evidence_manifest['audit_inputs'] + [evidence_manifest['preparation_script']]:
        verify(packet / item['path'], item['sha256'], 'packet:' + item['path'])
    admission = json.loads((case / 'admission/SOURCE_PACKET_ADMISSION.json').read_bytes())
    verify(packet / 'MANIFEST.json', admission['packet_manifest_sha256'], 'admission:manifest')
    verify(packet / 'evidence_template.json', admission['evidence_template_sha256'], 'admission:evidence')
    if set(admission['verified_files']) != {x['path'] for x in evidence_manifest['files']}:
        flag('admission_verified_file_set_changed')
    for item in admission['source_audits']:
        verify(packet / item['path'], item['sha256'], 'admission:' + item['path'])
    proposal = json.loads((packet / 'registry_proposal_PENDING.json').read_bytes())
    for item in proposal['proposed_artifacts']:
        verify(packet / item['path'], item['sha256'], 'registry_proposal:' + item['path'])
    public = case / 'public_v2'
    package = json.loads((public / 'PACKAGE_REVIEW.json').read_bytes())
    for name, digest in package['public_file_sha256'].items():
        verify(public / name, digest, 'public:' + name)
    for key, path in {
        'protocol_sha256': case / 'PROTOCOL_v2.md',
        'source_admission_sha256': case / 'admission/SOURCE_PACKET_ADMISSION.json',
        'packet_manifest_sha256': packet / 'MANIFEST.json',
        'evidence_template_sha256': packet / 'evidence_template.json',
    }.items():
        verify(path, package[key], 'public:' + key)
    schema_receipt = json.loads((packet / 'schema_check_receipt.json').read_bytes())
    verify(case / 'evidence/prepare_packet.py', schema_receipt['script_sha256'], 'schema_receipt:script')
    existing_contract = root / 'biomedical_research/virtual_cohort_system/cohort_harness/contracts.py'
    historical_contract_match = existing_contract.is_file() and sha(existing_contract.read_bytes()) == schema_receipt['contracts_sha256']

    result = {
        'status': 'PASS' if not findings else 'FAIL',
        'scope': 'Exact preparation/implementation export delta only; no scientific code/tests/data processing executed.',
        'prior_head': before,
        'manifest_sha256': sha(manifest_raw),
        'source_bindings_checked': len(records),
        'source_project_file_count': manifest['source_project_file_count'],
        'expected_new_file_count': len(expected),
        'historical_tracked_blobs_byte_verified': old_count,
        'historical_tracked_edits': 0 if not old_names & actual and not any(x['rule']=='historical_bytes_changed' for x in findings) else None,
        'json_files_byte_preserved': json_count,
        'python_files_byte_preserved_and_syntax_parsed': code_count,
        'internal_provenance_bindings_verified': internal_checks,
        'historical_harness_contract_matches_packet_receipt': historical_contract_match,
        'local_navigation_links_checked': links,
        'source_summary_bytes': summary_sizes,
        'privacy_scope': 'Explicit MD/JSON/Python allowlist, forbidden paths/extensions, recognizable individual records, credential patterns and machine paths; authored synthetic test literals are source code, not exported cohort files.',
        'omitted_dependencies': manifest['omitted_dependencies'],
        'scientific_tests_rerun': False,
        'scientific_execution_performed': False,
        'commit_or_push_performed': False,
        'findings': findings,
        'changed_paths': sorted(expected),
    }
    out = json.dumps(result, indent=2) + '\n'
    safe(root, AUDIT).write_bytes(out.encode())
    if args.stage_output:
        args.stage_output.write_bytes(out.encode())
    print(json.dumps({k: result[k] for k in ('status', 'source_bindings_checked', 'expected_new_file_count', 'historical_tracked_blobs_byte_verified', 'internal_provenance_bindings_verified', 'local_navigation_links_checked', 'findings')}, indent=2))
    raise SystemExit(bool(findings))


if __name__ == '__main__':
    main()
