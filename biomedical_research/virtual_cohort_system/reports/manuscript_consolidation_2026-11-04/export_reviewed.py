"""Allowlisted manuscript/figure export; never includes participant-like records."""
from pathlib import Path
import hashlib
import json
import posixpath
import re
import subprocess

R = Path(__file__).resolve().parent
P = R.parents[1]
E = P.parent / 'github_virtual_cohort_2026-10-27'
PREFIX = 'biomedical_research/virtual_cohort_system/'
DEST = PREFIX + 'reports/manuscript_consolidation_2026-11-04/'
HEAD = 'da1f915618921f2a886e8661fc07952ea9f808a9'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=E)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

assert git('rev-parse', 'HEAD').decode().strip() == HEAD
assert not git('status', '--porcelain', '--untracked-files=all').strip()
assert json.loads((R/'STATE.json').read_text(encoding='utf-8'))['status'] == 'complete_independently_reviewed'

report_files = ['CONSOLIDATION_DECISION.md', 'METHOD_AND_RERUN_AUDIT.md',
    'SUPPORT_AND_FIGURE_AUDIT.md', 'DRAFT_REVISION_NOTES.md', 'REVIEW_v09.md',
    'REVIEW_v09.json', 'STATE.json', 'PUBLIC_SCOPE.md', 'export_reviewed.py']
mapping = {DEST+name: R/name for name in report_files}
for name in ['README.md', 'manuscript/README.md', 'manuscript/DRAFT_v0_9.md',
             'docs/CURRENT_RESEARCH_FOCUS.md']:
    mapping[PREFIX+name] = P/name
F = 'manuscript/integrated_figures_v09_2026-11-04/'
for name in ['figure5_agent_scientific_utility.svg', 'supplement_real_real_context.svg',
             'figure5_input_and_value_bindings.json', 'figure5_public_input_and_value_bindings.json',
             'PUBLIC_RENDER_VERIFICATION.json', 'render_figure5.py', 'FIGURE5_CAPTIONS.md']:
    mapping[PREFIX+F+name] = P/F/name
mapping['README.md'] = R/'ROOT_README.md'

tracked = set(git('ls-files').decode().splitlines())
entries, manifest, rewrites, local_only = [], [], [], []
checked = 0
for target, source in mapping.items():
    assert source.suffix in {'.md', '.json', '.py', '.svg'}
    raw = source.read_bytes()
    content = raw.decode('utf-8-sig')
    assert not re.search(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9]{30,})\b', content)
    if source.suffix == '.json':
        content = json.dumps(json.loads(content), ensure_ascii=False, separators=(',', ':')) + '\n'
    if source.suffix == '.md':
        def link(match):
            global checked
            label, original = match.groups()
            if re.match(r'https?://|mailto:|#', original):
                return match.group(0)
            checked += 1
            changed = original.replace('../work/', '../reports/')
            if changed.startswith('work/'):
                changed = 'reports/' + changed[5:]
            base, _, fragment = changed.partition('#')
            dest = posixpath.normpath(posixpath.join(posixpath.dirname(target), base))
            if original == 'ROOT_README.md' and target.startswith(DEST):
                dest = 'README.md'
            if dest not in tracked and dest not in mapping and '/reports/' in '/'+dest:
                suffix = ('/'+dest).split('/reports/', 1)[1]
                found = [x for x in tracked if x.endswith('/reports/'+suffix)]
                if len(found) == 1:
                    dest = found[0]
            if dest not in tracked and dest not in mapping:
                local_only.append({'file': target, 'local_reference': original})
                return label + ' (local-only historical artifact; not included in this export)'
            new = posixpath.relpath(dest, posixpath.dirname(target))
            if fragment:
                new += '#'+fragment
            if new != original:
                rewrites.append({'file': target, 'old': original, 'new': new})
            return '['+label+']('+new+')'
        content = re.sub(r'\[([^\]]*)\]\(([^)]+)\)', link, content)
    public = content.encode('utf-8')
    entries.append({'path': target, 'mode': '100644', 'type': 'blob', 'content': content})
    manifest.append({'path': target, 'bytes': len(public), 'sha256': sha(public),
                     'local_source_sha256': sha(raw)})

record = {'parent': HEAD,
          'scope': 'Versioned manuscript, two aggregate-only figures, independent review and rerun decisions.',
          'individual_records_included': False, 'third_party_originals_included': False,
          'files': manifest.copy(), 'links_checked': checked,
          'navigation_rewrites': rewrites, 'local_only_links_rendered_as_plain_text': local_only,
          'json_export': 'Whitespace compacted; semantic values unchanged. Frozen local byte hashes stay local identities.'}
payload = json.dumps(record, indent=2, ensure_ascii=False)+'\n'
dest = DEST+'PUBLIC_EXPORT_MANIFEST.json'
entries.append({'path': dest, 'mode': '100644', 'type': 'blob', 'content': payload})
manifest.append({'path': dest, 'bytes': len(payload.encode()), 'sha256': sha(payload.encode())})
parts, current, size = [], [], 0
for entry in entries:
    count = len(json.dumps(entry, ensure_ascii=False).encode())
    if current and size+count > 220000:
        parts.append(current)
        current, size = [], 0
    current.append(entry)
    size += count
if current:
    parts.append(current)
for i, part in enumerate(parts):
    (R/f'PUBLIC_PAYLOAD_PART_{i}.json').write_text(json.dumps({'tree': part}, ensure_ascii=False), encoding='utf-8')
(R/'PUBLIC_MANIFEST.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'files': len(entries), 'bytes': sum(x['bytes'] for x in manifest),
                  'parts': len(parts), 'links_checked': checked, 'local_only_links': local_only,
                  'part_chars': [len((R/f'PUBLIC_PAYLOAD_PART_{i}.json').read_text(encoding='utf-8')) for i in range(len(parts))]}, ensure_ascii=False))
