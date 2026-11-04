"""Prepare a fixed, reviewed v0.12 public payload; never export rows or push.

Run only after the coordinating author has completed STATE and the package.
Text entries use content; PDF/PNG/ZIP entries use content_base64, which the caller
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
UNIT = 'paper_figure_revision_v12_2026-11-04'
DEST = PREFIX + 'reports/' + UNIT + '/'
FIGDIR = 'manuscript/paper_figures_v12_2026-11-04/'
PAPERDIR = 'manuscript/conference_draft_v12_2026-11-04/'
HEAD = '2bf466071c304cb0ce972f64f2fe20385db4701f'
FIGURES = ['fig1-agent-framework.drawio', 'fig2-evidence-results',
           'fig3-summary-results', 'fig4-longitudinal-use', 'fig5-analysis-use']
REPORT_FILES = [
    'IMPLEMENTATION_TRACE.md', 'IMPLEMENTATION_TRACE.json',
    'FIGURES_2_5_NUMERICAL_REVIEW.json',
    'FIGURES_AND_GUIDE_REVIEW.md', 'FIGURES_AND_GUIDE_REVIEW.json',
    'FINAL_PDF_REVIEW.md', 'FINAL_PDF_REVIEW.json',
    'DRAFT_CHANGE_AUDIT.json', 'STATE.json',
    'GSIM_SPADA_RESULT_READING.md', 'LLMSYNTHOR_FIGURES_AND_RESULT_READING.md',
    'FIG23_READING_GUIDE_ZH.md', 'PUBLIC_SCOPE.md',
    'export_reviewed.py', 'repair_drawio.mjs']
OPTIONAL_REPORT_FILES = ['prepare_manuscript.py']
FIGURE_FILES = [
    'build_framework.py', 'render_evidence_results.py', 'render_scientific_use.py',
    'NUMERIC_BINDINGS_23.json', 'NUMERIC_BINDINGS_45.json',
    'CAPTIONS_23.md', 'CAPTIONS_45.md', 'README.md', 'READING_GUIDE_ZH.md']
PAPER_FILES = ['paper.tex', 'paper.pdf', 'README.md', 'OVERLEAF_README.md', 'BUILD_INPUTS.json',
               'build_reading_copy.py', 'overleaf_v12.zip']
SECRET = re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9]{30,})\b')
MD_LINK = re.compile(r'(!?\[[^\]]*\])\(([^)]+)\)')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def mapping():
    files = {DEST+name: R/name for name in REPORT_FILES}
    for name in OPTIONAL_REPORT_FILES:
        if (R/name).is_file(): files[DEST+name] = R/name
    for name in ['README.md', 'manuscript/README.md', 'docs/CURRENT_RESEARCH_FOCUS.md',
                 'manuscript/DRAFT_v0_12.md']:
        files[PREFIX+name] = P/name
    for name in FIGURE_FILES + [s+ext for s in FIGURES for ext in ('.svg', '.png', '.pdf')]:
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
            package_file = P/PAPERDIR/('OVERLEAF_README.md' if name == 'README.md' else name)
            if not package_file.is_file() or package_file.read_bytes() != data:
                raise ValueError('ZIP member differs from the reviewed package file: '+name)
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


def verify_review_gates():
    """Bind independent approvals to current bytes, not merely report filenames."""
    def read(name):
        return json.loads((R/name).read_text(encoding='utf-8-sig'))
    statuses = {
        'IMPLEMENTATION_TRACE.json': 'PASS_FOR_FIGURE_TRACE_WITH_STATED_SCOPE',
        'FIGURES_2_5_NUMERICAL_REVIEW.json': 'PASS',
        'FIGURES_AND_GUIDE_REVIEW.json': 'PASS',
        'FINAL_PDF_REVIEW.json': 'PASS'}
    reports = {}
    for name, expected in statuses.items():
        report = read(name)
        if report.get('status') != expected:
            raise RuntimeError('Required independent review is not complete: '+name)
        reports[name] = report
    fig_names = {s+ext for s in FIGURES for ext in ('.svg', '.png', '.pdf')}
    figure_review = reports['FIGURES_AND_GUIDE_REVIEW.json']
    if set(figure_review['figure_output_hashes']) != fig_names:
        raise ValueError('Figure review must bind all 15 final figure exports.')
    for name, expected in figure_review['figure_output_hashes'].items():
        if sha((P/FIGDIR/name).read_bytes()) != expected:
            raise ValueError('Figure changed after independent review: '+name)
    for name, expected in reports['FIGURES_2_5_NUMERICAL_REVIEW.json']['output_hashes'].items():
        if name not in fig_names or sha((P/FIGDIR/name).read_bytes()) != expected:
            raise ValueError('Numerically reviewed figure changed: '+name)
    for file_name, key in [('READING_GUIDE_ZH.md','guide_sha256'),
                           ('build_framework.py','build_framework_sha256')]:
        if sha((P/FIGDIR/file_name).read_bytes()) != figure_review[key]:
            raise ValueError('Figure guide/builder changed after review: '+file_name)
    if set(figure_review['binding_hashes']) != {'NUMERIC_BINDINGS_23.json', 'NUMERIC_BINDINGS_45.json'}:
        raise ValueError('Independent review must bind both numeric manifests.')
    for name, expected in figure_review['binding_hashes'].items():
        if sha((P/FIGDIR/name).read_bytes()) != expected:
            raise ValueError('Numeric binding changed after independent review: '+name)
    draft = P/'manuscript/DRAFT_v0_12.md'
    pdf_review = reports['FINAL_PDF_REVIEW.json']
    for path, key in [(P/PAPERDIR/'paper.pdf','pdf_sha256'),
                       (P/PAPERDIR/'paper.tex','tex_sha256'),(draft,'draft_sha256')]:
        if sha(path.read_bytes()) != pdf_review[key]:
            raise ValueError('Reading package changed after final PDF review: '+key)
    audit = read('DRAFT_CHANGE_AUDIT.json')
    if not audit.get('scientific_body_identical') or not audit.get('tables_and_references_identical'):
        raise ValueError('Draft change scope has not passed.')
    if audit.get('new_experiments') is not False or audit.get('new_patient_analysis') is not False:
        raise ValueError('Unexpected new empirical work in this presentation export.')
    if audit['new_sha256'] != sha(draft.read_bytes()):
        raise ValueError('Draft change audit is stale: new manuscript bytes.')
    if audit['old_sha256'] != sha((P/'manuscript/DRAFT_v0_11.md').read_bytes()):
        raise ValueError('The preceding draft changed or its hash was not raw bytes.')
    build = json.loads((P/PAPERDIR/'BUILD_INPUTS.json').read_text(encoding='utf-8-sig'))
    if build['source_sha256'] != sha(draft.read_bytes()) or build['source_tex_sha256'] != sha((P/PAPERDIR/'paper.tex').read_bytes()):
        raise ValueError('Reading-copy build inputs do not match current manuscript/TeX.')
    if {f['name'] for f in build['figures']} != {s+'.pdf' for s in FIGURES}:
        raise ValueError('Build input figure inventory differs from the five reviewed figures.')
    for f in build['figures']:
        original = (P/FIGDIR/f['name']).read_bytes()
        copied = (P/PAPERDIR/'figures'/f['name']).read_bytes()
        if original != copied or sha(original) != f['sha256']:
            raise ValueError('Copied reading-package figure differs from reviewed source: '+f['name'])
    return {'independent_review_statuses': statuses, 'figure_exports_bound': len(fig_names),
            'draft_pdf_tex_hashes_bound': True, 'copied_figure_pdfs_match': True}


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
    review_binding = verify_review_gates()
    available = set(git('ls-files').decode().splitlines()) | set(files)
    entries, manifests, rewrites, checked, zip_members = [], [], [], [], []
    for target, source in files.items():
        raw = source.read_bytes()
        suffix = source.suffix.lower()
        entry = {'path': target, 'mode': '100644', 'type': 'blob'}
        if suffix in ('.pdf', '.png', '.zip'):
            if suffix == '.pdf' and not raw.startswith(b'%PDF-'):
                raise ValueError('Invalid original PDF: '+str(source))
            if suffix == '.png' and not raw.startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError('Invalid original PNG: '+str(source))
            if suffix == '.zip': zip_members = verify_zip(raw)
            public = raw
            entry['content_base64'] = base64.b64encode(raw).decode('ascii')
        else:
            if suffix not in {'.md', '.json', '.py', '.svg', '.tex', '.mjs'}:
                raise ValueError('Unapproved text extension: '+str(source))
            text = raw.decode('utf-8-sig')
            if SECRET.search(text): raise ValueError('Credential-pattern check failed: '+str(source))
            if suffix == '.json': json.loads(text)  # Do not compact or change scientific byte identities.
            if suffix == '.md': text = rewrite_links(text, target, available, rewrites, checked)
            public = text.encode('utf-8')
            entry['content'] = text
        entries.append(entry)
        manifests.append({'path': target, 'bytes': len(public), 'sha256': sha(public),
            'local_source_sha256': sha(raw), 'payload_field': 'content_base64' if suffix in ('.pdf', '.png', '.zip') else 'content'})
    record = {'parent': HEAD, 'status': 'reviewed_payload_prepared_not_pushed',
        'scope': 'Versioned v0.12 native-unit paper figures, implementation-grounded framework, interpretation guides, reading/Overleaf package and independent reviews.',
        'individual_records_included': False, 'third_party_originals_included': False,
        'review_bindings': review_binding, 'html_gallery_included': False,
        'files': manifests.copy(), 'links_checked': len(checked), 'navigation_rewrites': rewrites,
        'unresolved_links': [], 'references_removed': 0, 'overleaf_zip_members': zip_members,
        'hash_semantics': 'Existing frozen hashes and work/ paths inside scientific bindings identify the original local artifacts. Export hashes below identify public bytes; JSON values/whitespace are preserved.',
        'binary_transport': 'PDF, PNG and ZIP entries contain content_base64 locally. Create each Git blob with base64 encoding, then replace content_base64 by the returned sha before tree creation.'}
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


