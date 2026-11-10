"""Prepare a finite, reviewable export; no tables or third-party full texts."""
from pathlib import Path
import hashlib,json,posixpath,re,subprocess
from urllib.parse import urlsplit,unquote,urlunsplit

U=Path(__file__).resolve().parent
P=U.parents[1]
MIRROR=P.parent/'github_virtual_cohort_2026-10-27'
PREFIX='biomedical_research/virtual_cohort_system/'
BASE='58e7f2ba09bed99252c828202a0f84de21ddd721'
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(MIRROR),*args])
def destination(rel):return posixpath.normpath(PREFIX+(rel.replace('work/','reports/',1) if rel.startswith('work/') else rel))
def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE and not git('status','--porcelain').strip()
    review=json.loads((U/'INDEPENDENT_RESULTS_REVIEW.json').read_text(encoding='utf-8'))
    assert review['status']=='PASS_INDEPENDENT_RESULTS_RECOMPUTATION' and not review['remaining_blockers']
    assert review['results_sha256']==sha((U/'RESULTS.json').read_bytes())
    tree={}
    for row in git('ls-tree','-rz','HEAD').split(b'\0'):
        if row:
            meta,name=row.split(b'\t',1);tree[name.decode()]=meta.split()[2].decode()
    paths=['README.md','docs/CURRENT_RESEARCH_FOCUS.md','docs/DATASET_EXPOSURE_REGISTRY.md']
    unit=U.relative_to(P).as_posix()+'/'
    names=['PLAN.md','PROTOCOL.md','ADMISSION_DECISION.md','MEASUREMENT_AND_EXPOSURE.md',
        'READINESS.json','SELECTION_LOCK.json','SOURCE_PACKET_REVIEW.json','SOURCE_FAMILIES.json',
        'EXTERNAL_EVIDENCE_AUDIT.md','AUTHOR_SAFE_EVIDENCE_PACKET.md','AUTHOR_SAFE_EVIDENCE_PACKET.json',
        'FULL_IMPLEMENTATION_REVIEW.md','FULL_IMPLEMENTATION_REVIEW.json',
        'PARTIAL_AUTHOR_AUDIT.md','PARTIAL_AUTHOR_AUDIT.json','PAPER_INTEGRATION_PLAN.md',
        'RESULTS.json','RESULTS.md','INTERPRETATION_ZH.md','MANUSCRIPT_INSERT.md',
        'ANALYSIS_COMPARISONS.csv','RUN_ACCOUNTING.json','PUBLIC_PACKAGE_NOTE.md',
        'INDEPENDENT_RESULTS_REVIEW.json','INDEPENDENT_RESULTS_REVIEW.md','STATE.json','prepare_public.py']
    paths += [unit+x for x in names]
    frozen=json.loads((U/'runtime/METHOD_FREEZE.json').read_text(encoding='utf-8'))
    paths+=list(frozen['files'])
    paths+=[unit+'runtime/'+x for x in ['METHOD_FREEZE.json','BATCH_SEAL.json','report_accounting.py','report_results.py','plot_results.py','independent_results_recompute.py']]
    for author in ['A01','A02','A03','A04','A05']:
        paths += [unit+f'runtime/sessions/{author}/'+x for x in ['AUTHOR_SEAL.json','final_decision.json']]
        paths += [p.relative_to(P).as_posix() for p in (U/'runtime/sessions'/author/'candidates').glob('*/*')
            if p.is_file() and p.name in {'generator.py','model_spec.json','evidence.json','decision.md','checks.json','static_checks.json','whole_cohort_feedback.json','source_semantics_v1.json','descriptive_feedback_v1.json','freeze.json'}]
        paths += [p.relative_to(P).as_posix() for p in (U/'runtime/reviews').glob(author+'*.json')]
        paths.append(unit+f'runtime/dispatch/{author}.json')
    paths += [unit+'figures/'+stem+'.'+ext for stem in ['pns_bp_analysis_utility','pns_bp_dispersion'] for ext in ['png','pdf','svg']]
    paths=list(dict.fromkeys(paths))
    mapping=[(rel,destination(rel)) for rel in paths]+[('README.md','README.md')]
    assert len({d for _,d in mapping})==len(mapping)
    available=set(tree)|{d for _,d in mapping}; missing=[];checked=[]
    link=re.compile(r'(!?\[[^\]]*\])\((<[^>]+>|[^)]+)\)')
    def rewrite(raw,rel,dest):
        text=raw.decode('utf-8-sig')
        def fix(m):
            label,href=m.groups();href=href.strip('<>');url=urlsplit(href)
            if url.scheme in ('http','https','mailto') or href.startswith('#'):return m[0]
            if href.startswith(P.as_posix()+'/'):local=href[len(P.as_posix())+1:]
            elif url.scheme:
                missing.append({'file':dest,'target':href});return label.removeprefix('!')+' (local artifact)'
            else:local=posixpath.normpath(posixpath.join(posixpath.dirname(rel),unquote(url.path)))
            target=destination(local)
            if target not in available and '/reports/' in target:
                legacy='reports/'+target.split('/reports/',1)[1]
                if legacy in available:target=legacy
            if target not in available and not any(v.startswith(target.rstrip('/')+'/') for v in available):
                missing.append({'file':dest,'target':target});return label.removeprefix('!')+' (local artifact)'
            checked.append({'file':dest,'target':target})
            return label+'('+urlunsplit(('','',posixpath.relpath(target,posixpath.dirname(dest) or '.'),url.query,url.fragment))+')'
        return link.sub(fix,text).encode('utf-8')
    transport=U/'_local_only/public_transport';transport.mkdir(parents=True,exist_ok=True)
    records=[]
    for rel,dest in mapping:
        assert '/sources/' not in rel and '/outputs/' not in rel and '/custodian/' not in rel
        src=P/rel;raw=src.read_bytes();data=rewrite(raw,rel,dest) if src.suffix=='.md' else raw
        if src.suffix in {'.md','.json','.csv','.py','.txt'}:
            text=data.decode('utf-8-sig')
            for base,replacement in [(P,'PROJECT'),(P.parent,'BIOMEDICAL_RESEARCH')]:
                for form in [str(base),str(base).replace('\\','\\\\'),base.as_posix()]:text=text.replace(form,replacement)
            data=text.encode('utf-8')
            assert not re.search(rb'(?i)(?:sk-[A-Za-z0-9]{24,}|gh[pousr]_[A-Za-z0-9]{20,})',data)
        oid=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        (transport/oid).write_bytes(data)
        records.append({'path':dest,'source':rel,'local_sha256':sha(raw),'public_sha256':sha(data),'git_blob_sha':oid,'bytes':len(data),'same_as_base':tree.get(dest)==oid,'transport_file':'_local_only/public_transport/'+oid})
    manifest={'base':BASE,'scope':'Original protocol/code, evidence metadata, audited generator specifications and aggregate results only. No individual tables/full source documents.','files':records,'links_checked':len(checked),'local_only_link_labels':missing}
    (U/'PUBLIC_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(records),'new_or_changed':sum(not x['same_as_base'] for x in records),'bytes':sum(x['bytes'] for x in records),'links_checked':len(checked),'local_only_links':len(missing)}))
if __name__=='__main__':main()
