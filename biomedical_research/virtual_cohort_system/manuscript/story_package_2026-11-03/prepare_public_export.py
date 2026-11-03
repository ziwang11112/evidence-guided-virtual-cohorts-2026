"""Prepare a byte-preserving, explicit manuscript export; never publish by itself."""
from pathlib import Path
import base64,hashlib,json,re

HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
E=P.parent/'github_virtual_cohort_2026-10-27'
OUT=P/'work/paper_story_export_2026-11-03'
OUT.mkdir(parents=True,exist_ok=True)
prefix='biomedical_research/virtual_cohort_system/'
names=['DRAFT_v0_5.md','SUPPLEMENT_HISTORICAL_RESULTS_v05.md','SUPPLEMENT_SOURCE_AND_ASSUMPTIONS_v05.md','CONTRIBUTION_EVIDENCE_MAP_2026-11-03.md','CORE_CONTRIBUTION_POSITIONING_2026-11-03.md','JOURNAL_FIT_2026-11-03.md','STORY_AND_FIGURE_AUDIT_2026-11-03.md']
selected=[P/'manuscript'/x for x in names]
selected+=sorted(f for f in HERE.rglob('*') if f.is_file() and '__pycache__' not in f.parts)
assert (HERE/'INDEPENDENT_PACKAGE_REVIEW.json').exists(), 'Wait for final independent review'
review=json.loads((HERE/'INDEPENDENT_PACKAGE_REVIEW.json').read_text(encoding='utf-8-sig'))
entries=[]; manifest=[]
def add(path,data,source):
 sha=hashlib.sha256(data).hexdigest()
 git=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 entries.append({'path':path,'content':base64.b64encode(data).decode(),'encoding':'base64','sha':git})
 manifest.append({'path':path,'source':source,'bytes':len(data),'sha256':sha,'git_blob_sha1':git})
for f in selected:
 assert f.suffix.lower() in {'.md','.json','.py','.js','.csv','.drawio','.svg','.png','.pdf'}
 add(prefix+f.relative_to(P).as_posix(),f.read_bytes(),str(f))

readme=(E/'README.md').read_bytes().decode('utf-8')
title='# Evidence-guided virtual cohorts'
assert readme.startswith(title)
addition='''

**Manuscript story and venue assessment — 3 November 2026:** [working manuscript v0.5](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_5.md), [method and complete-results figures](biomedical_research/virtual_cohort_system/manuscript/story_package_2026-11-03/README.md), [worked source-to-law trace](biomedical_research/virtual_cohort_system/manuscript/SUPPLEMENT_SOURCE_AND_ASSUMPTIONS_v05.md), [contribution assessment](biomedical_research/virtual_cohort_system/manuscript/CORE_CONTRIBUTION_POSITIONING_2026-11-03.md), and [journal fit](biomedical_research/virtual_cohort_system/manuscript/JOURNAL_FIT_2026-11-03.md). The paper centers on complete virtual biomedical cohorts from qualified published evidence, without individual-level construction inputs, evaluated for declared scientific analyses. All six outcomes, all constructors, statistical comparisons and historical failures remain visible. This is a presentation and interpretation update, with no new experiment or target tuning. PLOS Digital Health is the first preparation target; scope fit does not establish submission readiness or acceptance. See the [independent package review](biomedical_research/virtual_cohort_system/manuscript/story_package_2026-11-03/INDEPENDENT_PACKAGE_REVIEW.md).
'''
add('README.md',(title+addition+readme[len(title):]).encode('utf-8'),'derived public index; preceding content preserved')
assert len({x['path'] for x in entries})==len(entries)
public={'purpose':'Reviewed manuscript, figures, source trace and venue assessment; no new scientific experiment.','base_commit':'26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3','boundary':'Only original documents/code, aggregate estimates and figures; no individual real/generated rows, full third-party papers/codebooks or credentials.','artifacts':[{k:v for k,v in x.items() if k!='source'} for x in manifest]}
data=(json.dumps(public,indent=2)+'\n').encode('utf-8')
add('docs/PAPER_STORY_EXPORT_2026-11-03.json',data,'derived export manifest')
(OUT/'PAYLOAD.json').write_text(json.dumps(entries,separators=(',',':')),encoding='utf-8')
(OUT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
payload=(OUT/'PAYLOAD.json').read_text(encoding='utf-8')
for i in range(0,len(payload),50000):
 (OUT/f'chunk_{i//50000:03d}.json').write_text(json.dumps(payload[i:i+50000]),encoding='utf-8')
print(json.dumps({'files':len(entries),'raw_bytes':sum(x['bytes'] for x in manifest),'chunks':(len(payload)+49999)//50000,'output':str(OUT)}))
