"""Verify the new manuscript package and standalone Overleaf compilation."""
from pathlib import Path
import hashlib,json,re,zipfile
import fitz

HERE=Path(__file__).resolve().parent
STANDALONE=HERE/'tmp/pdfs/standalone'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((HERE/'BUILD_INPUTS.json').read_text(encoding='utf-8'))
assert sha(HERE.parent/manifest['source_markdown'])==manifest['source_sha256']
assert sha(HERE/'paper.tex')==manifest['source_tex_sha256']
members={'paper.tex','OVERLEAF_README.md'}|{'figures/'+f['file'] for f in manifest['figures']}
with zipfile.ZipFile(HERE/'overleaf_v26.zip') as archive:
    assert set(archive.namelist())==members and len(archive.namelist())==len(members)
    for name in members:
        assert archive.read(name)==(HERE/name).read_bytes()==(STANDALONE/name).read_bytes(),name
for f in manifest['figures']:
    assert sha(HERE.parent/f['source'])==sha(HERE/'figures'/f['file'])==f['sha256']

def inspect(path):
    with fitz.open(path) as doc:
        pages=[' '.join(p.get_text(sort=True).split()) for p in doc]
        links=sorted((p.number+1,x['uri']) for p in doc for x in p.get_links() if x['kind']==fitz.LINK_URI and x.get('uri'))
        headings={}; figures={}; tables={}
        for number,p in enumerate(doc,1):
            txt=p.get_text()
            for heading in ('References','Supplementary results'):
                if re.search('^'+heading+'$',txt,re.M):headings[heading]=number
            for kind,index in [('Figure',figures),('Table',tables)]:
                for m in re.finditer('^'+kind+r'\s+(S?\d+)[.:]',txt,re.M):
                    assert m.group(1) not in index,(kind,m.group(1))
                    index[m.group(1)]=number
        return pages,links,headings,figures,tables
pages,links,headings,figures,tables=inspect(HERE/'paper.pdf')
other=inspect(STANDALONE/'paper.pdf')
assert pages==other[0] and links==other[1] and links
assert set(figures)=={str(i) for i in range(1,7)}|{'S'+str(i) for i in range(1,6)}
assert set(tables)=={'1','2','3'}|{'S'+str(i) for i in range(1,9)}
assert max(figures[str(i)] for i in range(1,7))<headings['References']
errors={}
for folder in (HERE,STANDALONE):
    errors[folder.name]=[s for s in (folder/'paper.log').read_text(encoding='utf-8',errors='replace').splitlines()
                          if re.search(r'Overfull \\[hv]box|Missing character:|Float too large|^! ',s)]
assert not any(errors.values()),errors
# The previously frozen manuscript is unchanged, not silently rewritten.
facts=json.loads((HERE.parents[1]/'work/manuscript_focus_v26_2026-11-09/REVISION_FACTS.json').read_text())
assert sha(HERE.parent/'DRAFT_v0_25.md')==facts['input_sha256']
assert sha(HERE.parent/'DRAFT_v0_26.md')==facts['output_sha256']
review=HERE/'tmp/pdfs/visual_review.txt'
report={'status':'PASS_PACKAGE_AND_STANDALONE_BUILD','main_pages':headings['References']-1,'total_pages':len(pages),'page_limit':None,
        'figure_pages':figures,'table_pages':tables,'headings':headings,'layout_errors':errors,
        'markdown_sha256':manifest['source_sha256'],'source_tex_sha256':manifest['source_tex_sha256'],
        'pdf_sha256':sha(HERE/'paper.pdf'),'zip_sha256':sha(HERE/'overleaf_v26.zip'),
        'zip_independent_build_text_matches':True,'standalone_external_links_match':True,
        'clickable_external_links':len(links),'zip_members':sorted(members),
        'old_manuscript_unchanged':True,'new_clinical_evaluation':False,
        'visual_review':review.read_text(encoding='utf-8').strip() if review.exists() else 'Pending final visual inspection'}
(HERE/'BUILD_QA.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','main_pages','total_pages','layout_errors','visual_review']}))
