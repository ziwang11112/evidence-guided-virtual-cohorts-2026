"""Allowlisted public export of original code and complete aggregate results."""
from pathlib import Path
import hashlib, json, posixpath, re, subprocess

R = Path(__file__).resolve().parent
P = R.parents[1]
E = P.parent / 'github_virtual_cohort_2026-10-27'
PREFIX = 'biomedical_research/virtual_cohort_system/'
DEST = PREFIX + 'reports/real_real_calibration_2026-11-04/'
HEAD = 'b8f1fc29404c8cfa365e9e81d5a368cc0f451f02'

def git(*args): return subprocess.check_output(['git', *args], cwd=E)
def sha(b): return hashlib.sha256(b).hexdigest()

assert git('rev-parse', 'HEAD').decode().strip() == HEAD
assert not git('status', '--porcelain', '--untracked-files=all').strip()
assert json.loads((R/'STATE.json').read_text(encoding='utf-8'))['status'] == 'complete_independently_reviewed'
files = ['RESULTS.md','PLAN.md','PROTOCOL.json','DESIGN_REVIEW.md','IMPLEMENTATION.md',
         'IMPLEMENTATION_REVIEW.md','FREEZE.json','STATE.json','calibration.py','test_calibration.py',
         'READ_RECEIPT.json','REPORT.json','independent_review.py','INDEPENDENT_READ_RECEIPT.json',
         'INDEPENDENT_REVIEW.json','INDEPENDENT_REVIEW.md','independent_review_continue.py',
         'INDEPENDENT_REVIEW_FAILURE.json','INDEPENDENT_REVIEW_CONTINUATION_FAILURE.json',
         'render_results.py','REAL_REAL_CONTEXT.svg',
         'COMPLETE_METRIC_TABLE.md','PUBLIC_SCOPE.md','export_reviewed.py']
mapping = {DEST+n: R/n for n in files}
for n in ['CURRENT_RESEARCH_FOCUS.md','DATASET_EXPOSURE_REGISTRY.md']:
    mapping[PREFIX+'docs/'+n] = P/'docs'/n
tracked = set(git('ls-files').decode().splitlines())
local_only = {'../work/core_highlight_2026-11-02/TARGET_ACCESS_SCREEN.md','../work/core_highlight_2026-11-02/STATE.json',
              '../work/autonomous_research_cycle2_2026-10-31/admission/ANSUR_METADATA.md',
              '../work/scaleup_2026-11-01/production_release/RESULTS.md'}
entries, manifest, rewrites = [], [], []
checked = 0
for target, path in mapping.items():
    assert path.suffix in {'.md','.json','.py','.svg'}
    raw = path.read_bytes()
    content = raw.decode('utf-8-sig')
    assert not re.search(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9]{30,})\b', content)
    if path.suffix == '.json':
        content = json.dumps(json.loads(content), separators=(',',':'), ensure_ascii=False) + '\n'
    if path.suffix == '.md':
        def link(match):
            global checked
            label, url = match.groups()
            if re.match(r'https?://|mailto:', url): return match.group(0)
            checked += 1
            if url in local_only:
                rewrites.append({'file':target,'old':url,'new':'local-only historical record'})
                return label + ' (local-only historical record; not part of this public export)'
            base, _, fragment = url.replace('../work/', '../reports/').partition('#')
            dest = posixpath.normpath(posixpath.join(posixpath.dirname(target), base))
            if dest not in tracked and dest not in mapping and '/reports/' in '/'+dest:
                suffix = ('/'+dest).split('/reports/',1)[1]
                found = [p for p in tracked if p.endswith('/reports/'+suffix)]
                if len(found) == 1: dest = found[0]
            assert dest in tracked or dest in mapping, (target,url,dest)
            new = posixpath.relpath(dest, posixpath.dirname(target))
            if fragment: new += '#'+fragment
            if new != url: rewrites.append({'file':target,'old':url,'new':new})
            return '['+label+']('+new+')'
        content = re.sub(r'\[([^\]]*)\]\(([^)]+)\)', link, content)
    data = content.encode('utf-8')
    entries.append({'path':target,'mode':'100644','type':'blob','content':content})
    manifest.append({'path':target,'bytes':len(data),'sha256':sha(data),'local_source_sha256':sha(raw)})
record = {'parent':HEAD,'scope':'Complete aggregate real-real evaluation; no individual real/generated tables or original papers.',
          'files':manifest.copy(),'links_checked':checked,'navigation_rewrites':rewrites,
          'json_export':'Whitespace compacted without semantic changes; local-source and public-byte hashes both retained.',
          'original_documents_included':False,'individual_tables_included':False}
text = json.dumps(record, indent=2)+'\n'
dest = DEST+'PUBLIC_EXPORT_MANIFEST.json'
entries.append({'path':dest,'mode':'100644','type':'blob','content':text})
manifest.append({'path':dest,'bytes':len(text.encode()),'sha256':sha(text.encode())})
parts, current, size = [], [], 0
for entry in entries:
    amount = len(json.dumps(entry, ensure_ascii=False).encode())
    if current and size+amount > 220000:
        parts.append(current); current=[]; size=0
    current.append(entry); size += amount
if current: parts.append(current)
for i, part in enumerate(parts):
    (R/f'PUBLIC_PAYLOAD_PART_{i}.json').write_text(json.dumps({'tree':part},ensure_ascii=False),encoding='utf-8')
(R/'PUBLIC_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(entries),'bytes':sum(x['bytes'] for x in manifest),'parts':len(parts),'links_checked':checked,
                  'part_bytes':[(R/f'PUBLIC_PAYLOAD_PART_{i}.json').stat().st_size for i in range(len(parts))]}))
