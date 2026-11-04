"""Prepare a fixed, reviewed v0.10 public payload; never export rows or push.

Run only after the coordinating author has completed STATE and the package.
Text entries use content; PDF/ZIP entries use content_base64, which the caller
must convert through Git create_blob before creating a tree. Outputs stay here.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import io
import json
import posixpath
import re
import subprocess
from urllib.parse import unquote, urlsplit
import zipfile

R = Path(__file__).resolve().parent
P = R.parents[1]
PREFIX = 'biomedical_research/virtual_cohort_system/'
UNIT = 'conference_draft_v10_2026-11-04'
DEST = PREFIX + 'reports/' + UNIT + '/'
FIGDIR = 'manuscript/conference_figures_v10_2026-11-04/'
PAPERDIR = 'manuscript/' + UNIT + '/'
HEAD = 'a21b08629aa30b3e5b530f3b36565d224147df2d'
FIGURES = ['fig1-method.drawio', 'fig2-relational-evidence',
           'fig3-summary-reconstruction', 'fig4-longitudinal', 'fig5-scientific-use']
REPORT_FILES = [
    'GSIM_STORY_AND_FIGURES.md', 'LLMSYNTHOR_STORY_AND_FIGURES.md',
    'DRAFT_REVISION_NOTES.md', 'STORY_AND_VISUAL_DESIGN.md', 'FIG1_REVIEW.md',
    'FIG23_INDEPENDENT_REVIEW.md', 'FIG23_INDEPENDENT_REVIEW.json',
    'check_fig23_independently.py', 'FIG45_EXPORT_CHECK.json',
    'INDEPENDENT_DRAFT_REVIEW.md', 'INDEPENDENT_DRAFT_REVIEW.json',
    'PDF_REVIEW.md', 'PDF_REVIEW.json',
    'STATE.json', 'PUBLIC_SCOPE.md', 'export_reviewed.py']
FIGURE_FILES = [
    'build_overview.py', 'render_quantitative.py',
    'render_use_cases.py', 'FIG23_CAPTIONS.md', 'FIG23_NUMERIC_BINDINGS.json',
    'FIG23_PUBLIC_RENDER_CHECK.json', 'FIG45_CAPTIONS.md', 'FIG45_NUMERIC_BINDINGS.json']
PAPER_FILES = ['paper.tex', 'paper.pdf', 'README.md', 'BUILD_INPUTS.json',
               'build_reading_copy.py', 'overleaf_v10.zip']
SECRET = re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9]{30,})\b')
MD_LINK = re.compile(r'(!?\[[^\]]*\])\(([^)]+)\)')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def mapping():
    files = {DEST+name: R/name for name in REPORT_FILES}
    for name in ['README.md', 'manuscript/README.md', 'docs/CURRENT_RESEARCH_FOCUS.md',
                 'manuscript/DRAFT_v0_10.md']:
        files[PREFIX+name] = P/name
    for name in FIGURE_FILES + [s+ext for s in FIGURES for ext in ('.svg', '.pdf')]:
        files[PREFIX+FIGDIR+name] = P/FIGDIR/name
    for name in PAPER_FILES + ['figures/'+s+'.pdf' for s in FIGURES]:
        files[PREFIX+PAPERDIR+name] = P/PAPERDIR/name
    files['README.md'] = R/'ROOT_README.md'
    return files


def verify_zip(raw):
    required = {'paper.tex', 'README.md'} | {'figures/'+s+'.pdf' for s in FIGURES}
    allowed = required | {'paper.pdf', 'BUILD_INPUTS.json', 'build_reading_copy.py'}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or not required.issubset(names) or set(names)-allowed:
            raise ValueError('Unexpected or missing Overleaf ZIP members: '+repr(names))
        for name in names:
            if name.startswith('/') or '..' in name.split('/') or '\\' in name:
                raise ValueError('Unsafe ZIP path: '+name)
            data = archive.read(name)
            if name.endswith('.pdf'):
                if not data.startswith(b'%PDF-'): raise ValueError('Invalid packaged PDF: '+name)
            elif SECRET.search(data.decode('utf-8-sig')):
                raise ValueError('Credential-pattern check failed in packaged text: '+name)
    return names


def rewrite_links(content, target, available, rewrites, checked):
    def replace(match):
        label, original = match.groups()
        value = original[1:-1] if original.startswith('<') and original.endswith('>') else original
        parsed = urlsplit(value)
        if parsed.scheme in ('http', 'https', 'mailto') or value.startswith('#'):
            return match.group(0)
        if parsed.scheme or parsed.netloc or value.startswith('/'):
            raise ValueError(f'Nonportable link in {target}: {original}')
        path = unquote(parsed.path)
        path = re.sub(r'(^|/)work/', r'\1reports/', path)
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(target), path))
        if target.startswith(DEST) and path == 'ROOT_README.md':
            resolved = 'README.md'
        if resolved not in available and '/reports/' in '/'+resolved:
            suffix = ('/'+resolved).split('/reports/', 1)[1]
            matches = [name for name in available if name.endswith('/reports/'+suffix)]
            if len(matches) == 1: resolved = matches[0]
        if resolved not in available:
            raise FileNotFoundError(f'Unresolved public link; no reference will be dropped: {target}: {original} -> {resolved}')
        new = posixpath.relpath(resolved, posixpath.dirname(target))
        if parsed.query: new += '?'+parsed.query
        if parsed.fragment: new += '#'+parsed.fragment
        if ' ' in new: new = '<'+new+'>'
        checked.append({'file': target, 'original': original, 'resolved': resolved})
        if new != original: rewrites.append({'file': target, 'old': original, 'new': new})
        return label+'('+new+')'
    return MD_LINK.sub(replace, content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkout', type=Path, default=P.parent/'github_virtual_cohort_2026-10-27')
    args = parser.parse_args()
    def git(*values):
        return subprocess.check_output(['git', *values], cwd=args.checkout)
    if git('rev-parse', 'HEAD').decode().strip() != HEAD:
        raise RuntimeError('Unexpected review-checkout HEAD; re-review the export parent.')
    if git('status', '--porcelain', '--untracked-files=all').strip():
        raise RuntimeError('Review checkout must be clean; exporter never alters it.')
    files = mapping()
    missing = [str(path) for path in files.values() if not path.is_file()]
    if missing: raise FileNotFoundError('Required reviewed artifacts are missing:\n'+'\n'.join(missing))
    if json.loads((R/'STATE.json').read_text(encoding='utf-8-sig'))['status'] != 'complete_independently_reviewed':
        raise RuntimeError('STATE is not complete_independently_reviewed.')
    available = set(git('ls-files').decode().splitlines()) | set(files)
    entries, manifests, rewrites, checked, zip_members = [], [], [], [], []
    for target, source in files.items():
        raw = source.read_bytes()
        suffix = source.suffix.lower()
        entry = {'path': target, 'mode': '100644', 'type': 'blob'}
        if suffix in ('.pdf', '.zip'):
            if suffix == '.pdf' and not raw.startswith(b'%PDF-'):
                raise ValueError('Invalid original PDF: '+str(source))
            if suffix == '.zip': zip_members = verify_zip(raw)
            public = raw
            entry['content_base64'] = base64.b64encode(raw).decode('ascii')
        else:
            if suffix not in {'.md', '.json', '.py', '.svg', '.tex', '.drawio'}:
                raise ValueError('Unapproved text extension: '+str(source))
            text = raw.decode('utf-8-sig')
            if SECRET.search(text): raise ValueError('Credential-pattern check failed: '+str(source))
            if suffix == '.json': json.loads(text)  # Do not compact or change scientific byte identities.
            if suffix == '.md': text = rewrite_links(text, target, available, rewrites, checked)
            public = text.encode('utf-8')
            entry['content'] = text
        entries.append(entry)
        manifests.append({'path': target, 'bytes': len(public), 'sha256': sha(public),
            'local_source_sha256': sha(raw), 'payload_field': 'content_base64' if suffix in ('.pdf', '.zip') else 'content'})
    record = {'parent': HEAD, 'status': 'reviewed_payload_prepared_not_pushed',
        'scope': 'Question-led v0.10 draft, five original figures, reading/Overleaf package and independent aggregate reviews.',
        'individual_records_included': False, 'third_party_originals_included': False,
        'files': manifests.copy(), 'links_checked': len(checked), 'navigation_rewrites': rewrites,
        'unresolved_links': [], 'references_removed': 0, 'overleaf_zip_members': zip_members,
        'hash_semantics': 'Existing frozen hashes and work/ paths inside scientific bindings identify the original local artifacts. Export hashes below identify public bytes; JSON values/whitespace are preserved.',
        'binary_transport': 'PDF and ZIP entries contain content_base64 locally. Create each Git blob with base64 encoding, then replace content_base64 by the returned sha before tree creation.'}
    body = json.dumps(record, ensure_ascii=False, indent=2)+'\n'
    dest = DEST+'PUBLIC_EXPORT_MANIFEST.json'
    entries.append({'path': dest, 'mode': '100644', 'type': 'blob', 'content': body})
    manifests.append({'path': dest, 'bytes': len(body.encode()), 'sha256': sha(body.encode()), 'payload_field': 'content'})
    parts, part, size = [], [], 0
    for entry in entries:
        count = len(json.dumps(entry, ensure_ascii=False).encode())
        if part and size+count > 220000: parts.append(part); part, size = [], 0
        part.append(entry); size += count
    if part: parts.append(part)
    sizes = []
    for i, part in enumerate(parts):
        serialized = json.dumps({'tree': part}, ensure_ascii=False)
        (R/f'PUBLIC_PAYLOAD_PART_{i}.json').write_text(serialized, encoding='utf-8')
        sizes.append({'part':i,'bytes':len(serialized.encode()),'characters':len(serialized),
                      'entries':len(part),'binary_entries':sum('content_base64' in e for e in part)})
    (R/'PUBLIC_MANIFEST.json').write_text(json.dumps(manifests, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'files':len(entries),'parts':len(parts),'bytes':sum(x['bytes'] for x in manifests),
        'links_checked':len(checked),'references_removed':0,'binary_entries':sum('content_base64' in e for e in entries),
        'part_sizes':sizes,
        'note':'Only current part count is authoritative; no checkout mutation, Git blob creation or push performed.'}))


if __name__ == '__main__':
    main()
