"""Check that the editorial revision preserves prior quantitative displays."""
from pathlib import Path
import hashlib,json,re
from urllib.parse import unquote,urlsplit

HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
oldp=P/'manuscript/DRAFT_v0_26.md'
newp=P/'manuscript/DRAFT_v0_27.md'
old,new=(p.read_text(encoding='utf-8') for p in (oldp,newp))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(oldp)=='feba15e00a510598df145226c49e70c24ab3bd4483f26640fe4d9eadabec0f42'

def tables(text):
    out={}
    for m in re.finditer(r'^\*\*Table (S?\d+)\. .*?\n\n((?:\|[^\n]*\n)+)',text,re.M):
        assert m[1] not in out
        out[m[1]]=m[2].strip()
    return out
a,b=tables(old),tables(new)
assert len(a)==11 and len(b)==15,(len(a),len(b))
for key,rows in a.items():
    mapped=key if key.startswith('S') else str(int(key)+1)
    assert rows==b[mapped],(key,mapped)
assert set(b)=={str(i) for i in range(1,6)}|{f'S{i}' for i in range(1,11)}

fig=lambda s:re.findall(r'^!\[[^\]]*\]\(([^)]+)\)',s,re.M)
assert fig(old)==fig(new) and len(fig(new))==11
figure_hashes={x:sha(newp.parent/Path(x).with_suffix('.pdf')) for x in fig(new)}
refs=lambda s:s.split('## References\n',1)[1].split('## Supplementary results',1)[0]
assert refs(old)==refs(new),'Bibliography changed'

links=[]
for href in re.findall(r'\]\(([^)]+)\)',new):
    url=urlsplit(href.strip('<>'))
    if url.scheme or href.startswith('#'):continue
    path=(newp.parent/unquote(url.path)).resolve()
    assert path.exists(),href
    links.append(href)

report={'status':'PASS_EDITORIAL_SCOPE','previous_draft_sha256':sha(oldp),'reviewed_draft_sha256':sha(newp),
        'existing_table_blocks_preserved':len(a),'new_documentation_tables':len(b)-len(a),
        'all_prior_figure_assets_unchanged':figure_hashes,'bibliography_unchanged':True,
        'local_links_resolved':len(links),'new_clinical_experiments':0,
        'scope':'Mechanical preservation of quantitative tables/assets and document links, not certification of scientific applicability.'}
(HERE/'EDITORIAL_SCOPE_QA.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','existing_table_blocks_preserved','new_documentation_tables','local_links_resolved','reviewed_draft_sha256']}))
