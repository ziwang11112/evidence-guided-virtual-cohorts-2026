"""Finite reviewed manuscript/audit allowlist; never exports participant records."""
from pathlib import Path
import base64,hashlib,json,posixpath,re,subprocess
from urllib.parse import urlsplit,unquote,urlunsplit

HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
MIRROR=P.parent/'github_virtual_cohort_2026-10-27'
PREFIX='biomedical_research/virtual_cohort_system/'
BASE='0d51c9b98a62a63357abf4ffb4121d73cd19295b'
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(MIRROR),*args])
assert git('rev-parse','HEAD').decode().strip()==BASE and not git('status','--porcelain').strip()
tree={}
for x in git('ls-tree','-rz','HEAD').split(b'\0'):
    if x:
        meta,name=x.split(b'\t',1);tree[name.decode()]=meta.split()[2].decode()
build='manuscript/methods_draft_v26_2026-11-09/'
fig='manuscript/paper_figures_v26_2026-11-09/'
qa=json.loads((P/build/'BUILD_QA.json').read_text())
review=json.loads((HERE/'MANUSCRIPT_REVIEW.json').read_text())
assert qa['zip_independent_build_text_matches'] and not any(qa['layout_errors'].values())
assert 'visually inspected' in qa['visual_review']
assert review['status']=='PASS'
assert sha((P/'manuscript/DRAFT_v0_26.md').read_bytes())==qa['markdown_sha256']==review['snapshot']['reviewed_v26_sha256']
for k,f in [('pdf_sha256','paper.pdf'),('zip_sha256','overleaf_v26.zip')]:assert sha((P/build/f).read_bytes())==qa[k]

paths=['README.md','manuscript/README.md','docs/CURRENT_RESEARCH_FOCUS.md','manuscript/DRAFT_v0_26.md']
paths += [fig+x for x in ['fig3-analysis-utility.png','fig3-analysis-utility.svg','fig3-analysis-utility.pdf','FIGURE_DATA.csv','FIGURE_QA.json','render_analysis_utility.py']]
paths += [build+x for x in ['paper.tex','paper.pdf','overleaf_v26.zip','OVERLEAF_README.md','BUILD_INPUTS.json','BUILD_QA.json','build_review_copy.py','compile_review.py','verify_review_copy.py']]
inputs=json.loads((P/build/'BUILD_INPUTS.json').read_text())
paths += [build+'figures/'+f['file'] for f in inputs['figures']]
unit='work/manuscript_focus_v26_2026-11-09/'
paths += [unit+x for x in ['RESULTS.md','CLAIM_FIGURE_MAP.md','METHOD_COVERAGE.md','METHOD_COVERAGE.json','MANUSCRIPT_REVIEW.md','MANUSCRIPT_REVIEW.json','FIGURE_CAPTION.md','REVISION_FACTS.json','prepare_draft.py','prepare_build.py','prepare_public.py']]
strength='work/strengths_synthesis_2026-11-09/'
paths += [strength+x for x in ['PLAN.md','RESULTS_AND_FOCUS.md','ALL_UNIT_INDEX.csv','INDEX_MANIFEST.json','HISTORY_AUDIT.md','HISTORY_AUDIT.json','PRIMARY_AUDIT.md','PRIMARY_AUDIT.json','RECENT_AUDIT.md','RECENT_AUDIT.json','MAIN_COMPARISONS.csv','DERIVED_HIGHLIGHTS.json','DERIVATION_REVIEW.md','SYNTHESIS_REVIEW.md','derive_highlights.py','build_index.py']]
paths += ['../obesity_temporal_prediction_2026-10-25/RESULTS.md','../obesity_temporal_prediction_2026-10-25/results/compact_comparison.csv']
def destination(rel):return posixpath.normpath(PREFIX+(rel.replace('work/','reports/',1) if rel.startswith('work/') else rel))
mapping=[(rel,destination(rel)) for rel in paths]+[('README.md','README.md')]
assert len({d for _,d in mapping})==len(mapping)
available=set(tree)|{d for _,d in mapping}
missing=[];rewrites=[];checked=[]
link=re.compile(r'(!?\[[^\]]*\])\((<[^>]+>|[^)]+)\)')
def rewrite_md(raw,rel,dest):
    text=raw.decode('utf-8-sig')
    def resolve(m):
        label,href=m.groups();href=href.strip('<>');url=urlsplit(href)
        if url.scheme in ('http','https','mailto') or href.startswith('#'):return m[0]
        if href.startswith(P.as_posix()+'/'):local=href[len(P.as_posix())+1:]
        elif url.scheme:
            missing.append({'file':dest,'target':href,'reason':'local-only absolute artifact'})
            return label.removeprefix('!')+' (local audit artifact)'
        else:local=posixpath.normpath(posixpath.join(posixpath.dirname(rel),unquote(url.path)))
        target=destination(local)
        if target not in available and '/reports/' in target:
            legacy='reports/'+target.split('/reports/',1)[1]
            if legacy in available:target=legacy
        if target not in available and not any(p.startswith(target.rstrip('/')+'/') for p in available):
            missing.append({'file':dest,'target':target,'reason':'not part of reviewed public allowlist'})
            return label.removeprefix('!')+' (local audit artifact)'
        updated=posixpath.relpath(target,posixpath.dirname(dest) or '.')
        checked.append({'file':dest,'target':target})
        updated=urlunsplit(('','',updated,url.query,url.fragment))
        if updated!=href:rewrites.append({'file':dest,'old':href,'new':updated})
        return label+'('+updated+')'
    return link.sub(resolve,text).encode('utf-8')
def clean_text(raw):
    text=raw.decode('utf-8-sig')
    for path,sub in [(P,'PROJECT'),(P.parent,'BIOMEDICAL_RESEARCH')]:
        for form in (str(path),str(path).replace('\\','\\\\'),path.as_posix()):text=text.replace(form,sub)
    return text.encode('utf-8')

transport=HERE/'_local_only/public_transport';transport.mkdir(parents=True,exist_ok=True)
records=[]
for rel,dest in mapping:
    src=P/rel;raw=src.read_bytes()
    data=rewrite_md(raw,rel,dest) if src.suffix=='.md' else raw
    if src.suffix in ('.md','.json','.csv','.py','.txt','.tex'):
        data=clean_text(data)
        assert not re.search(rb'(?i)(?:sk-[A-Za-z0-9]{24,}|gh[pousr]_[A-Za-z0-9]{20,})',data),rel
    oid=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    (transport/oid).write_bytes(data)
    records.append({'path':dest,'source':rel,'local_sha256':sha(raw),'public_sha256':sha(data),'git_blob_sha':oid,'bytes':len(data),'same_as_base':tree.get(dest)==oid,'transport_file':'_local_only/public_transport/'+oid})
manifest={'base':BASE,'scope':'Reviewed original manuscript/code, metadata and aggregate reports only; no real/generated participant rows or third-party source documents.','files':records,'relative_links_checked':len(checked),'rewrites':rewrites,'local_only_link_labels':missing}
(HERE/'PUBLIC_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
report={'status':'PASS_REVIEWED_ALLOWLIST','files':len(records),'new_or_changed':sum(not r['same_as_base'] for r in records),'bytes':sum(r['bytes'] for r in records),'relative_links_checked':len(checked),'local_only_link_labels':len(missing),'manifest_sha256':sha((HERE/'PUBLIC_MANIFEST.json').read_bytes()),'policy':'Unreleased local audit links are labelled as such rather than uploading their targets or leaving broken hyperlinks.'}
(HERE/'PUBLIC_EXPORT_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
