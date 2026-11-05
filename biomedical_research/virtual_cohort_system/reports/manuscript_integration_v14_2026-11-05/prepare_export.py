"""Stage an explicit reviewed public export. No GitHub mutation or scientific run.

Original non-Markdown bytes are preserved. Only known Markdown navigation targets
are remapped to their public locations. Missing links stop preparation for review.
"""
from pathlib import Path
import hashlib,json,re,posixpath,subprocess,base64
from urllib.parse import unquote,urlsplit

R=Path(__file__).resolve().parent
P=R.parents[1]; W=P.parents[1]
M=P/'manuscript'; UNIT=R.name; PREFIX='biomedical_research/virtual_cohort_system/'
MIRROR=W/'biomedical_research/github_virtual_cohort_2026-10-27'
HEAD='3ceafd0d8b4755e662cc9d524dd73286629a24b6'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=MIRROR,text=True).strip()==HEAD
sha=lambda raw:hashlib.sha256(raw).hexdigest()
candidate=json.loads((R/'SAFE_EXPORT_CANDIDATES.json').read_text())
mapping={x['public_path']:Path(x['source']) for x in candidate['files']}
for x in candidate['files']:
    assert sha(Path(x['source']).read_bytes())==x['local_sha256'],x['source']

def add(dest,src):
    assert dest not in mapping or mapping[dest]==src,dest
    mapping[dest]=src

for rel in ['README.md','manuscript/README.md','docs/CURRENT_RESEARCH_FOCUS.md',
            'docs/DATASET_EXPOSURE_REGISTRY.md','manuscript/DRAFT_v0_14.md',
            'manuscript/KEY_EXPERIMENT_GAPS_v14_2026-11-05.md']:
    add(PREFIX+rel,P/rel)
add('README.md',R/'ROOT_README.md')
for rel in ['work/core_highlight_2026-11-02/TARGET_ACCESS_SCREEN.md',
            'work/core_highlight_2026-11-02/DESIGN.md',
            'work/core_highlight_2026-11-02/EVIDENCE_REUSE_MATRIX.md',
            'work/core_highlight_2026-11-02/STATE.json',
            'work/autonomous_research_cycle2_2026-10-31/admission/ANSUR_METADATA.md']:
    add(PREFIX+rel.replace('work/','reports/',1),P/rel)
stems=['fig1-agent-framework.drawio','fig2-evidence-results','fig3-summary-results',
       'fig4-longitudinal-use','fig5-open-retrieval','fig6-cross-task','fig7-dispersion','figS1-analysis-use']
fdir='manuscript/paper_figures_v14_2026-11-05/'
for name in ['README.md','render_cross_task_aggregates.py']+[s+e for s in stems for e in ['.svg','.pdf','.png']]:
    add(PREFIX+fdir+name,P/fdir/name)
bdir='manuscript/conference_draft_v14_2026-11-05/'
for name in ['paper.tex','paper.pdf','build_reading_copy.py','BUILD_INPUTS.json','README.md','OVERLEAF_README.md','overleaf_v14.zip']+['figures/'+s+'.pdf' for s in stems]:
    add(PREFIX+bdir+name,P/bdir/name)
reports=['STORY_AND_FIGURE_PLAN.md','FIGURE_REUSE_MANIFEST.json','AGGREGATE_FIGURE_REPRODUCTION.json',
         'DRAFT_INTEGRATION_AUDIT.json','INDEPENDENT_DRAFT_REVIEW.md','INDEPENDENT_DRAFT_REVIEW.json',
         'FINAL_PDF_REVIEW.md','FINAL_PDF_REVIEW.json','PDF_PAGE_MAP.json','PACKAGE_INVENTORY.json',
         'STATE.json','PUBLIC_SCOPE.md','prepare_package.py','prepare_export.py','finalize_package.py',
         'audit_manuscript_aggregate_consistency.py']
for name in reports: add(PREFIX+'reports/'+UNIT+'/'+name,R/name)

tree=subprocess.check_output(['git','ls-tree','-r',HEAD],cwd=MIRROR,text=True)
remote={}
for line in tree.splitlines():
    bits,path=line.split('\t');mode,kind,gsha=bits.split();remote[path]=gsha
available=set(remote)|set(mapping)
by_source={str(src.resolve()).lower():dst for dst,src in mapping.items()}
for name,target in [('primary_analyses','fig6-cross-task'),('dispersion','fig7-dispersion')]:
    original=P/'work/evidence_use_cross_task_2026-11-05/figures'/f'{name}.pdf'
    copied=P/fdir/f'{target}.pdf'
    assert original.read_bytes()==copied.read_bytes()
    by_source[str(original.resolve()).lower()]=PREFIX+fdir+f'{target}.pdf'
staging=R/'public_transport';staging.mkdir(exist_ok=True)
records=[];errors=[];rewrites=[]
link=re.compile(r'(!?\[[^\]]*\])\(([^)]+)\)')
secret=re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9]{30,})\b|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----')
for dest,src in mapping.items():
    raw=src.read_bytes();original=sha(raw)
    if src.suffix.lower() not in ('.pdf','.png','.zip'):
        text=raw.decode('utf-8')
        assert not secret.search(text),dest
        if src.suffix.lower()=='.md':
            def fix(m):
                label,href=m.groups();href=href.strip('<>');u=urlsplit(href)
                if u.scheme in ('http','https','mailto') or href.startswith('#'):return m.group(0)
                local=(src.parent/unquote(u.path)).resolve()
                resolved=by_source.get(str(local).lower())
                if src==R/'ROOT_README.md':
                    resolved=re.sub(r'(^|/)work/',r'\1reports/',unquote(u.path))
                if not resolved:
                    try:
                        rel=local.relative_to(P).as_posix()
                        rel=re.sub(r'^work/','reports/',rel)
                        resolved=PREFIX+rel
                    except ValueError:
                        try:resolved=local.relative_to(W).as_posix()
                        except ValueError:pass
                if resolved not in available and resolved and '/reports/' in resolved:
                    suffix=resolved.split('/reports/',1)[1]
                    matches=[p for p in available if p.endswith('/reports/'+suffix) or p=='reports/'+suffix]
                    if len(matches)==1:resolved=matches[0]
                if resolved not in available:
                    errors.append(dict(file=dest,href=href,local=str(local),resolved=resolved));return m.group(0)
                target=posixpath.relpath(resolved,posixpath.dirname(dest))
                if u.fragment:target+='#'+u.fragment
                if u.query:target+='?'+u.query
                if ' ' in target:target='<'+target+'>'
                if target!=href:rewrites.append(dict(file=dest,old=href,new=target))
                return label+'('+target+')'
            text=link.sub(fix,text);raw=text.encode('utf-8')
    gitsha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    target=staging/gitsha;target.write_bytes(raw)
    records.append(dict(path=dest,source=str(src),local_sha256=original,public_sha256=sha(raw),
                        bytes=len(raw),git_blob_sha=gitsha,transport_file=gitsha,binary=src.suffix.lower() in ('.pdf','.png','.zip'),
                        same_as_remote=remote.get(dest)==gitsha,existing_remote_blob=gitsha in set(remote.values())))
manifest=dict(status='NEEDS_LINK_REVIEW' if errors else 'STAGED_FOR_INDEPENDENT_PUBLIC_REVIEW',base_head=HEAD,
              files=records,link_errors=errors,markdown_link_rewrites=rewrites,patient_rows=False,
              third_party_originals=False,new_scientific_runs=0)
(R/'PUBLIC_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(files=len(records),bytes=sum(x['bytes'] for x in records),link_errors=errors,
                     changed=sum(not x['same_as_remote'] for x in records),rewrites=len(rewrites))))
if errors:raise SystemExit(2)
