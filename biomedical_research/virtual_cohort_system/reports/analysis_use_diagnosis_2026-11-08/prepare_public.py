"""Prepare an allowlisted public derivative without changing scientific originals."""
import base64
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

UNIT = Path(__file__).resolve().parent
PROJECT = UNIT.parents[1]
WORKSPACE = PROJECT.parents[1]
MIRROR = PROJECT.parent / 'github_virtual_cohort_2026-10-27'
PREFIX = 'biomedical_research/virtual_cohort_system/'
BASE = 'efbb7dcd4349f07d316ed42a399fcb1b8a762a5e'
REL = UNIT.relative_to(PROJECT).as_posix()
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('public_helpers', PROJECT / 'work/manuscript_v16_2026-11-05/prepare_public_v16.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def sanitize_string(text):
    for root, alias in [(PROJECT, 'project'), (WORKSPACE, 'local_archive')]:
        for value in [root.as_posix(), str(root).replace('/', '\\')]:
            text = re.sub(re.escape(value), lambda _: alias, text, flags=re.I)
    # Only normalize archive identifiers, not arbitrary prose or regex escapes.
    return re.sub(r'(?:project|local_archive)\\[^\s\"\n]+', lambda m: m.group().replace('\\', '/'), text)

def sanitize_json(obj):
    if isinstance(obj, dict):
        return {sanitize_string(k): sanitize_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_json(v) for v in obj]
    return sanitize_string(obj) if isinstance(obj, str) else obj

def main():
    head, tree = helpers.read_tree(MIRROR)
    require(head == BASE and not helpers.git(MIRROR, 'status', '--porcelain').strip(), 'Mirror is not the expected clean base')
    require(helpers.git(MIRROR, 'ls-remote', 'origin', 'refs/heads/main').decode().split()[0] == head, 'Remote head changed')
    for name in ['CROSS_REVIEW.json', 'FINAL_USE_REVIEW.json']:
        review = json.loads((UNIT / name).read_bytes())
        records = review['provenance']
        for row in records:
            if Path(row['path']).name == 'READOUT.md':
                require(sha((UNIT / 'READOUT.md').read_bytes()) == row['sha256'], 'Readout differs from review')
        require(any(Path(x['path']).name == 'READOUT.md' for x in records), 'Missing review binding')
    final = json.loads((UNIT / 'FINAL_USE_REVIEW.json').read_bytes())
    require(final['status'] == 'PASS_SCIENTIFIC_CONTENT_AND_BOUNDARY', 'Scientific review incomplete')
    indep = json.loads((UNIT / 'INDEPENDENT_CHECK.json').read_bytes())
    require(indep['status'] == 'PASS_INDEPENDENT_ALGEBRA_CHECKS', 'Algebra checks incomplete')
    names = ['README.md', 'PROTOCOL.md', 'READOUT.md', 'STATE.json', 'USE_MAP.json', 'USE_MAP.csv',
        'GLYCEMIA_AUDIT.json', 'GLYCEMIA_VARIANCE_DIAGNOSTIC.py', 'IRON_LIPID_AUDIT.json',
        'RECONSTRUCTION_PROSPECTIVE_AUDIT.json', 'hrs_deterministic_audit.py', 'HRS_DETERMINISTIC_AUDIT.json',
        'source_only_age_profile.py', 'AGE_PROFILE_SENSITIVITY.json', 'independent_check.py',
        'INDEPENDENT_CHECK.json', 'CROSS_REVIEW.json', 'FINAL_USE_REVIEW.json', 'assemble.py', 'prepare_public.py']
    paths = ['README.md', 'docs/CURRENT_RESEARCH_FOCUS.md'] + [REL + '/' + n for n in names]
    def destination(rel):
        return PREFIX + (rel.replace('work/', 'reports/', 1) if rel.startswith('work/') else rel)
    index_dest = destination(REL + '/PUBLIC_EXPORT_INDEX.json')
    available = set(tree) | {destination(x) for x in paths} | {'README.md', index_dest}
    rows, rewrites, checked, payload = [], [], [], {}
    for rel, dest in [(x, destination(x)) for x in paths] + [('README.md', 'README.md')]:
        src = PROJECT / rel
        raw = src.read_bytes()
        if src.suffix == '.json':
            data = (json.dumps(sanitize_json(json.loads(raw)), ensure_ascii=False, indent=2) + '\n').encode()
        else:
            data = sanitize_string(raw.decode('utf-8')).encode()
        if src.suffix == '.md':
            data = helpers.rewrite_markdown(data, rel, dest, available, rewrites, checked)
        require(not re.search(rb'(?<![A-Za-z])[A-Za-z]:[\\/]', data), 'Unmapped absolute path: ' + rel)
        require(not re.search(rb'(?i)(?:sk-[A-Za-z0-9]{24,}|gh[pousr]_[A-Za-z0-9]{20,})', data), 'Credential-like string: ' + rel)
        require(not rel.endswith(('generated.csv', 'participants.csv')) and '/private_runs/' not in rel, 'Row data not permitted')
        oid = helpers.git_blob(data)
        helpers.atomic_write(UNIT / 'public_transport' / oid, data)
        payload[oid] = data
        rows.append({'path': dest, 'local': rel, 'local_sha256': sha(raw), 'public_sha256': sha(data),
            'git_blob_sha': oid, 'bytes': len(data), 'transport_file': 'public_transport/' + oid, 'same_as_base': tree.get(dest) == oid})
    index = {'date': '2026-11-08', 'base_head': head,
        'scope': 'Original code, aggregate results and original reviews only; no participant tables or third-party originals.',
        'transformations': ['Absolute project and workspace prefixes become archive identifiers.', 'Markdown links are rewritten for public reports layout.', 'JSON is reserialized; numeric values and scientific conclusions are preserved.'],
        'hash_scope': 'Review and provenance hashes refer to local originals. This index maps each released derivative to its reviewed local original.',
        'files': [{k: r[k] for k in ['path', 'local', 'local_sha256', 'public_sha256', 'bytes']} for r in rows]}
    data = (json.dumps(index, indent=2) + '\n').encode()
    helpers.atomic_write(UNIT / 'PUBLIC_EXPORT_INDEX.json', data)
    oid = helpers.git_blob(data)
    helpers.atomic_write(UNIT / 'public_transport' / oid, data)
    payload[oid] = data
    rows.append({'path': index_dest, 'local': REL + '/PUBLIC_EXPORT_INDEX.json', 'local_sha256': sha(data), 'public_sha256': sha(data),
        'git_blob_sha': oid, 'bytes': len(data), 'transport_file': 'public_transport/' + oid, 'same_as_base': tree.get(index_dest) == oid})
    manifest = {'base_head': head, 'files': rows, 'relative_links_checked': len(checked), 'rewrites': rewrites}
    helpers.atomic_write(UNIT / 'PUBLIC_MANIFEST.json', (json.dumps(manifest, indent=2) + '\n').encode())
    blobs, entries = {}, []
    known = set(tree.values())
    for row in rows:
        if row['same_as_base']:
            continue
        oid = row['git_blob_sha']
        entries.append({'path': row['path'], 'mode': '100644', 'type': 'blob', 'sha': oid})
        if oid in known or oid in blobs:
            continue
        data = payload[oid]
        chunks = []
        for i, offset in enumerate(range(0, len(data), 7200)):
            chunk = f'{oid}-{i:03d}.txt'
            helpers.atomic_write(UNIT / 'transport_chunks' / chunk, base64.b64encode(data[offset:offset + 7200]))
            chunks.append(chunk)
        blobs[oid] = {'chunks': chunks, 'encoded_length': 4 * ((len(data) + 2) // 3)}
    transport = {'base': head, 'tree': helpers.git(MIRROR, 'rev-parse', 'HEAD^{tree}').decode().strip(), 'entries': entries, 'blobs': blobs}
    helpers.atomic_write(UNIT / 'TRANSPORT.json', json.dumps(transport).encode())
    receipt = {'status': 'PASS_PUBLIC_PLAN', 'files': len(rows), 'new_objects': len(blobs), 'links_checked': len(checked),
        'total_bytes': sum(r['bytes'] for r in rows), 'new_clinical_tables': 0, 'patient_level_rows': 0, 'third_party_originals': 0,
        'manifest_sha256': sha((UNIT / 'PUBLIC_MANIFEST.json').read_bytes())}
    helpers.atomic_write(UNIT / 'PUBLIC_EXPORT_QA.json', (json.dumps(receipt, indent=2) + '\n').encode())
    print(json.dumps(receipt))

if __name__ == '__main__':
    main()
