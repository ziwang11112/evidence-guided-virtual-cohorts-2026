"""Stage only the original v15 editorial package for public review."""
from pathlib import Path
import hashlib,json,re,posixpath,subprocess
from urllib.parse import unquote,urlsplit

R=Path(__file__).resolve().parent; P=R.parents[1]; W=P.parents[1]
PREFIX='biomedical_research/virtual_cohort_system/'
MIRROR=W/'biomedical_research/github_virtual_cohort_2026-10-27'
HEAD='0b41c907da1fc391aa81e547c676d9e3d13166bf'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=MIRROR,text=True).strip()==HEAD
sha=lambda b:hashlib.sha256(b).hexdigest()
mapping={}
def add(dest,source):
 assert source.is_file(),source
 assert dest not in mapping
 mapping[dest]=source
for rel in ['README.md','manuscript/README.md','docs/CURRENT_RESEARCH_FOCUS.md','manuscript/DRAFT_v0_15.md']:
 add(PREFIX+rel,P/rel)
add('README.md',R/'ROOT_README.md')
fd='manuscript/paper_figures_v15_2026-11-05/'
stems=['fig1-agent-framework.drawio','fig2-evidence-results','fig3-cross-task','fig4-summary-results',
 'figS1-open-retrieval','figS2-longitudinal-use','figS3-dispersion','figS4-analysis-use']
for n in [s+e for s in stems for e in ('.pdf','.svg','.png')]+[
 'render_results.py','NUMERIC_BINDINGS_RESULTS.json','CAPTIONS_RESULTS.md','FIGURE_QA_RESULTS.json','SHA256SUMS_RESULTS.txt','README.md']:
 add(PREFIX+fd+n,P/fd/n)
for f in sorted((P/fd/'qa').glob('*.png')):add(PREFIX+fd+'qa/'+f.name,f)
bd='manuscript/conference_draft_v15_2026-11-05/'
for n in ['paper.tex','paper.pdf','build_reading_copy.py','BUILD_INPUTS.json','README.md','OVERLEAF_README.md','overleaf_v15.zip']+['figures/'+s+'.pdf' for s in stems]:
 add(PREFIX+bd+n,P/bd/n)
reports=['EDITORIAL_DECISIONS_ZH.md','FIGURE_REUSE.json','STORY_REDESIGN.md','VENUE_AND_STORY_AUDIT.md',
 'INDEPENDENT_CONTENT_REVIEW.md','INDEPENDENT_CONTENT_REVIEW.json','FINAL_PDF_REVIEW.md','FINAL_PDF_REVIEW.json',
 'PDF_PAGE_MAP.json','PACKAGE_INVENTORY.json','STATE.json','PUBLIC_SCOPE.md',
 'prepare_reading_package.py','finalize_package.py','prepare_export.py']
for n in reports:add(PREFIX+'reports/'+R.name+'/'+n,R/n)
tree=subprocess.check_output(['git','ls-tree','-r',HEAD],cwd=MIRROR,text=True)
remote={line.split('\t')[1]:line.split('\t')[0].split()[2] for line in tree.splitlines()}
available=set(remote)|set(mapping)
by_source={str(s.resolve()).lower():d for d,s in mapping.items()}
stage=R/'public_transport';stage.mkdir(exist_ok=True)
records=[];errors=[];rewrites=[]
link=re.compile(r'(!?\[[^\]]*\])\(([^)]+)\)')
secret=re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9]{30,})\b|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----')
for dest,src in mapping.items():
 raw=src.read_bytes(); original=sha(raw); binary=src.suffix.lower() in ('.pdf','.png','.zip')
 if not binary:
  text=raw.decode('utf-8');assert not secret.search(text),dest
  if src.suffix.lower()=='.md':
   def fix(m):
    label,href=m.groups();href=href.strip('<>');u=urlsplit(href)
    if u.scheme in ('http','https','mailto') or href.startswith('#'):return m.group(0)
    local=(src.parent/unquote(u.path)).resolve();resolved=by_source.get(str(local).lower())
    if src==R/'ROOT_README.md':resolved=re.sub(r'(^|/)work/',r'\1reports/',unquote(u.path))
    if not resolved:
     try:resolved=PREFIX+re.sub(r'^work/','reports/',local.relative_to(P).as_posix())
     except ValueError:pass
    if resolved not in available and resolved and '/reports/' in resolved:
     suffix=resolved.split('/reports/',1)[1]
     matches=[p for p in available if p.endswith('/reports/'+suffix) or p=='reports/'+suffix]
     if len(matches)==1:resolved=matches[0]
    # Existing image-review directories are valid GitHub directory links.
    exists=resolved in available or (resolved and any(p.startswith(resolved.rstrip('/')+'/') for p in available))
    if not exists:
     errors.append(dict(file=dest,href=href,local=str(local),resolved=resolved));return m.group(0)
    target=posixpath.relpath(resolved,posixpath.dirname(dest))
    if u.fragment:target+='#'+u.fragment
    if u.query:target+='?'+u.query
    if ' ' in target:target='<'+target+'>'
    if target!=href:rewrites.append(dict(file=dest,old=href,new=target))
    return label+'('+target+')'
   raw=link.sub(fix,text).encode('utf-8')
 gs=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();(stage/gs).write_bytes(raw)
 records.append(dict(path=dest,source=str(src),local_sha256=original,public_sha256=sha(raw),bytes=len(raw),git_blob_sha=gs,
  transport_file=gs,binary=binary,same_as_remote=remote.get(dest)==gs,existing_remote_blob=gs in set(remote.values())))
manifest=dict(status='NEEDS_LINK_REVIEW' if errors else 'STAGED_FOR_INDEPENDENT_PUBLIC_REVIEW',base_head=HEAD,
 files=records,link_errors=errors,markdown_link_rewrites=rewrites,patient_rows=False,third_party_originals=False,new_scientific_runs=0)
(R/'PUBLIC_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(files=len(records),bytes=sum(r['bytes'] for r in records),changed=sum(not r['same_as_remote'] for r in records),link_errors=errors)))
if errors:raise SystemExit(2)
