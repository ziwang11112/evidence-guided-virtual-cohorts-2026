"""Allowlist the experimental skill, fictional check and original design records."""
import base64
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

UNIT = Path(__file__).resolve().parent
PROJECT = UNIT.parents[1]
MIRROR = PROJECT.parent / 'github_virtual_cohort_2026-10-27'
PREFIX = 'biomedical_research/virtual_cohort_system/'
BASE = '91ac161db7ebab5012894af84d81bf915dc6136f'
REL = UNIT.relative_to(PROJECT).as_posix()
SKILL = 'experimental_skills/analysis-guided-cohort'
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('public_helpers', PROJECT / 'work/manuscript_v16_2026-11-05/prepare_public_v16.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    head, tree = h.read_tree(MIRROR)
    assert head == BASE and not h.git(MIRROR, 'status', '--porcelain').strip()
    assert h.git(MIRROR, 'ls-remote', 'origin', 'refs/heads/main').decode().split()[0] == head
    archive = json.loads((UNIT / 'TESTED_VERSION_ARCHIVE.json').read_bytes())
    lock = json.loads((UNIT / 'DESIGN_LOCK.json').read_bytes())
    archive_lookup = {row['original']: row for row in archive['files']}
    for rel, digest in lock['files'].items():
        source = archive_lookup[rel]['tested_archive'] if rel in archive_lookup else rel
        assert sha((PROJECT / source).read_bytes()) == digest, rel
    review = json.loads((UNIT / 'DESIGN_REVIEW.json').read_bytes())
    assert review['status'] == 'PASS_AFTER_NARROW_CALIBRATION_WORDING_CORRECTION'
    for rel, digest in review['bindings'].items():
        assert sha((PROJECT / rel).read_bytes()) == digest, rel
    state = json.loads((UNIT / 'STATE.json').read_bytes())
    for rel, digest in state['current_skill_files'].items():
        assert sha((PROJECT / rel).read_bytes()) == digest, rel
    paths = ['docs/METHOD_REFINEMENT_PROPOSAL_2026-11-08.md', 'docs/RUBRIC_SKILL_METHOD_DESIGN_2026-11-09.md']
    paths += [SKILL + '/' + n for n in ['SKILL.md', 'references/rubric.md', 'references/procedures.md']]
    names = ['PROTOCOL.md', 'RESULTS.md', 'STATE.json', 'DESIGN_LOCK.json', 'ADJUDICATION.json',
        'DESIGN_REVIEW.json', 'TESTED_VERSION_ARCHIVE.json', 'fixture/SOURCE_PACKET.json',
        'forward_test/RESPONSE.md', 'forward_test/calculate.py', 'forward_test/calculations.json',
        'tested_skill/SKILL.md', 'tested_skill/references/rubric.md', 'tested_skill/references/procedures.md', 'prepare_public.py']
    paths += [REL + '/' + n for n in names]
    def dest(rel):
        return PREFIX + (rel.replace('work/', 'reports/', 1) if rel.startswith('work/') else rel)
    index_dest = dest(REL + '/PUBLIC_EXPORT_INDEX.json')
    available = set(tree) | {dest(x) for x in paths} | {index_dest}
    rows, checked, rewrites, payload = [], [], [], {}
    for rel in paths:
        raw = (PROJECT / rel).read_bytes()
        data = h.rewrite_markdown(raw, rel, dest(rel), available, rewrites, checked) if rel.endswith('.md') else raw
        assert not re.search(rb'(?<![A-Za-z])[A-Za-z]:[\\/]', data), rel
        assert not re.search(rb'(?i)(?:sk-[A-Za-z0-9]{24,}|gh[pousr]_[A-Za-z0-9]{20,})', data), rel
        oid = h.git_blob(data)
        h.atomic_write(UNIT / 'public_transport' / oid, data)
        payload[oid] = data
        rows.append({'path': dest(rel), 'local': rel, 'local_sha256': sha(raw), 'public_sha256': sha(data),
            'git_blob_sha': oid, 'bytes': len(data), 'transport_file': 'public_transport/' + oid, 'same_as_base': tree.get(dest(rel)) == oid})
    index = {'scope': 'Original experimental skill and fictional planning check. No participant tables, third-party originals, credentials or global installation.',
        'hash_scope': 'Scientific and design bindings retain local-original hashes; this index maps public Markdown link derivatives. The tested skill is archived separately from the later calibration wording correction.',
        'base_head': head, 'files': [{k: r[k] for k in ['path', 'local', 'local_sha256', 'public_sha256', 'bytes']} for r in rows]}
    data = (json.dumps(index, indent=2) + '\n').encode()
    h.atomic_write(UNIT / 'PUBLIC_EXPORT_INDEX.json', data)
    oid = h.git_blob(data); payload[oid] = data
    h.atomic_write(UNIT / 'public_transport' / oid, data)
    rows.append({'path': index_dest, 'local': REL + '/PUBLIC_EXPORT_INDEX.json', 'local_sha256': sha(data), 'public_sha256': sha(data),
        'git_blob_sha': oid, 'bytes': len(data), 'transport_file': 'public_transport/' + oid, 'same_as_base': tree.get(index_dest) == oid})
    manifest = {'base_head': head, 'files': rows, 'relative_links_checked': len(checked), 'rewrites': rewrites}
    h.atomic_write(UNIT / 'PUBLIC_MANIFEST.json', (json.dumps(manifest, indent=2) + '\n').encode())
    entries, blobs = [], {}
    for row in rows:
        if row['same_as_base']:
            continue
        oid = row['git_blob_sha']
        entries.append({'path': row['path'], 'mode': '100644', 'type': 'blob', 'sha': oid})
        if oid in blobs or oid in set(tree.values()):
            continue
        data = payload[oid]; chunks = []
        for i, offset in enumerate(range(0, len(data), 7200)):
            name = f'{oid}-{i:03d}.txt'
            h.atomic_write(UNIT / 'transport_chunks' / name, base64.b64encode(data[offset:offset + 7200]))
            chunks.append(name)
        blobs[oid] = {'chunks': chunks, 'encoded_length': 4 * ((len(data) + 2) // 3)}
    transport = {'base': head, 'tree': h.git(MIRROR, 'rev-parse', 'HEAD^{tree}').decode().strip(), 'entries': entries, 'blobs': blobs}
    h.atomic_write(UNIT / 'TRANSPORT.json', json.dumps(transport).encode())
    receipt = {'status': 'PASS_PUBLIC_PLAN', 'files': len(rows), 'bytes': sum(r['bytes'] for r in rows),
        'new_objects': len(blobs), 'links_checked': len(checked), 'participant_tables': 0,
        'manifest_sha256': sha((UNIT / 'PUBLIC_MANIFEST.json').read_bytes())}
    h.atomic_write(UNIT / 'PUBLIC_EXPORT_QA.json', (json.dumps(receipt, indent=2) + '\n').encode())
    print(json.dumps(receipt))

if __name__ == '__main__':
    main()
