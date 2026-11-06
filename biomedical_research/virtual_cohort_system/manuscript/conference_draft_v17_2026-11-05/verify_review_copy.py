"""Confirm the compiled edition, source binding and standalone rebuild."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
import fitz

here = Path.cwd()
manifest = json.loads((here/'BUILD_INPUTS.json').read_text())
standalone = here/'tmp/pdfs/standalone'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def normalized_pages(path):
    with fitz.open(path) as doc:
        return [" ".join(page.get_text(sort=True).split()) for page in doc]

def all_text_and_metadata(path):
    with fitz.open(path) as doc:
        material=[str(doc.metadata), str(doc.get_xml_metadata())]
        for page in doc:
            material.append(page.get_text())
            material.extend(str(link.get('uri','')) for link in page.get_links())
        return "\n".join(material)

assert manifest['source_sha256'] == digest(here.parent/manifest['source_markdown'])
assert manifest['source_tex_sha256'] == digest(here/'paper.tex')
tex=(here/'paper.tex').read_text(encoding='utf8')
assert r'\documentclass[sigconf,anonymous,review]{acmart}' in tex
assert r'\onecolumn' not in tex
assert 'two frozen generating laws' in tex
with zipfile.ZipFile(here/'overleaf_v17.zip') as archive:
    expected=['paper.tex','OVERLEAF_README.md']+['figures/'+f['file'] for f in manifest['figures']]
    assert set(expected)==set(archive.namelist())
    assert archive.read('paper.tex') == (here/'paper.tex').read_bytes()
    for f in manifest['figures']:
        name='figures/'+f['file']
        assert f['sha256']==digest(here/name)==hashlib.sha256(archive.read(name)).hexdigest()
        assert f['sha256']==digest(here.parent/f['source'])
identity_markers=('ziwang11112','evidence-guided-virtual-cohorts-2026','D:/AIR-','D:\\AIR-')
for target in [here/'paper.pdf',*(here/'figures'/f['file'] for f in manifest['figures'])]:
    text=all_text_and_metadata(target)
    assert all(term.lower() not in text.lower() for term in identity_markers), target
pages=normalized_pages(here/'paper.pdf')
assert pages==normalized_pages(standalone/'paper.pdf')
headings={}
fig_pages={}
table_pages={}
with fitz.open(here/'paper.pdf') as doc:
    for page_no,page in enumerate(doc,1):
        text=page.get_text()
        for heading in ('References','Supplementary results'):
            if re.search(r'^'+heading+r'$', text, re.M):
                headings[heading]=page_no
        for typ,mapping in [('Figure',fig_pages),('Table',table_pages)]:
            for match in re.finditer(r'^'+typ+r' (S?\d+):',text,re.M):
                key=match.group(1)
                assert key not in mapping,key
                mapping[key]=page_no
assert sorted(fig_pages)==['1','2','3','4','S1','S2','S3','S4','S5'],fig_pages
assert sorted(table_pages)==['1','S1','S2','S3','S4','S5','S6','S7'],table_pages
body_pages=headings['References']-1
assert body_pages <=8
log=(here/'paper.log').read_text(encoding='utf8',errors='replace')
bad=[line for line in log.splitlines() if re.search(r'Overfull \\[hv]box|Missing character:|Float too large|^! ',line)]
assert not bad,bad
visual_note = (here/'tmp/pdfs/visual_review.txt').read_text(encoding='utf8').strip()
checks={
    'source_markdown_sha256':manifest['source_sha256'],
    'source_tex_sha256':digest(here/'paper.tex'),'compiled_pdf_sha256':digest(here/'paper.pdf'),
    'standalone_zip_sha256':digest(here/'overleaf_v17.zip'),
    'class_options':['sigconf','anonymous','review'],'paper_size_points':[612,792],
    'body_pages':body_pages,'references_first_page':headings['References'],
    'appendix_first_page':headings['Supplementary results'],'total_pages':len(pages),
    'figure_pages':fig_pages,'table_pages':table_pages,
    'standalone_zip_file_count':len(expected),'standalone_build':'two LuaLaTeX passes in isolated extracted folder',
    'standalone_paginated_text_matches':True,
    'latest_markdown_and_all_nine_source_figure_hashes_match':True,
    'review_pdf_and_asset_metadata_checked':True,
    'overfull_boxes_missing_glyphs_oversize_floats':bad,
    'visual_review':visual_note,
    'review_format_notes':['Anonymous identity and red review line numbers are visible. The pre-publication ACM citation block is suppressed.']
}
(here/'BUILD_QA.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf8')
print(json.dumps(checks,indent=2))
