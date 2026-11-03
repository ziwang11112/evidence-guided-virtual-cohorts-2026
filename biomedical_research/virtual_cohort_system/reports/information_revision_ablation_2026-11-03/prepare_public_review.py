"""Curate original code, evidence summaries and aggregates; never export rows."""
from pathlib import Path
import hashlib,json
U=Path(__file__).resolve().parent;W=U.parents[3];ROOT=W/'evcIA';OUT=ROOT/'publish';E=W/'biomedical_research/github_virtual_cohort_2026-10-27'
PREFIX='biomedical_research/virtual_cohort_system/reports/information_revision_ablation_2026-11-03'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 assert (U/'FINAL_INDEPENDENT_REVIEW.md').is_file()
 assert all(load(ROOT/k/'FINAL_AUTHOR_DECISION.json')['kind']=='retain' for k in ('L01','R01','R02','L02','L03','R03'))
 OUT.mkdir(exist_ok=False);entries=[];manifest=[]
 def add(p,relative):
  assert p.suffix.lower() in {'.json','.md','.py','.svg'}
  entries.append({'path':PREFIX+'/'+relative,'mode':'100644','type':'blob','content':p.read_text(encoding='utf-8-sig')})
  manifest.append({'source':str(p),'export':relative,'original_sha256':sha(p),'original_bytes':p.stat().st_size})
 for p in sorted(U.iterdir()):
  if p.is_file() and p.suffix in {'.json','.md','.py','.svg'} and p.name!='prepare_public_review.py':add(p,p.name)
 add(U/'prepare_public_review.py','prepare_public_review.py')
 for p in sorted((U/'implementation').glob('*')):
  if p.is_file() and p.suffix in {'.json','.md','.py'}:add(p,'implementation/'+p.name)
 for key in ('L01','R01','R02','L02','L03','R03'):
  root=ROOT/key;events=[load(p) for p in sorted((root/'session/events').glob('*.json'))]
  publicbase='constructors/'+key
  for name in ('AUTHOR_TASK.md','profile.json','FINAL_AUTHOR_DECISION.json','CLOSURE_VERIFICATION.json'):add(root/name,publicbase+'/'+name)
  for name in ('task.json','registry.json'):add(root/'b'/name,publicbase+'/b/'+name)
  for p in sorted((root/'b/input').glob('*')):
   if p.is_file():add(p,publicbase+'/b/input/'+p.name)
  # Sources here are original evidence summaries/audits, not full papers.
  for p in sorted((root/'b/sources').glob('*')):add(p,publicbase+'/b/sources/'+p.name)
  add(root/'session/contract.json',publicbase+'/session_contract.json')
  entries.append({'path':PREFIX+'/'+publicbase+'/events.json','mode':'100644','type':'blob','content':json.dumps(events,indent=2)+'\n'})
  fs=[e for e in events if e['kind']=='freeze'];candidate_manifest=[]
  for event in fs:
   c=root/'b'/event['candidate'];stage=event['stage'];dst=publicbase+'/candidates/'+stage
   for p in sorted(c.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(c).as_posix();candidate_manifest.append({'stage':stage,'original_candidate':event['candidate'],'path':rel,'sha256':sha(p),'bytes':p.stat().st_size})
    # Large feedback copies already represented by complete central numeric report.
    if p.suffix.lower() not in {'.json','.md','.py'} or 'feedback' in p.name.lower() or p.name in {'evidence.json','whole_cohort_feedback.json','source_semantics_v1.json'}:continue
    add(p,dst+'/'+rel)
  entries.append({'path':PREFIX+'/'+publicbase+'/CANDIDATE_FILE_MANIFEST.json','mode':'100644','type':'blob','content':json.dumps(candidate_manifest,indent=2)+'\n'})
 readme='''# Review package: information provision and additional revision

Read [scientific interpretation](SCIENTIFIC_DECISION.md), [complete results](RESULTS.md), [independent audit](FINAL_INDEPENDENT_REVIEW.md), and [the figure](analysis_use_profile.png).

This package contains original protocols, implementation and independent audit code, source-evidence summaries, all30 aggregate measurements for all42 executions, and selected candidate artifacts. Six authors, one exposed CHNS case,24distinct tables; all six retained and all18paired deliveries were unchanged. No individual real or generated table, full third-party paper, credential or participant identifier is exported.

The per-constructor candidate manifest retains original local file hashes. Repeated evidence/semantic templates and large copied feedback artifacts are intentionally omitted from candidate folders; admitted inputs and the complete numeric report remain available for inspection. Frozen originals and all execution receipts stay local. This is a selected review package, not a complete portable frozen bundle. Text transfer may normalize line endings, so exported copies must not be represented as the byte-identical original frozen artifacts. Producer scripts retain their original local path conventions and are evidence for review; adapt a separately copied workspace before reproducing.

Scientific quantities and information regimes are explicit. Reference-assisted results assess consistency with supplied summaries; they do not establish unseen-analysis transfer or clinical equivalence. Three seeds are conditional generation variation, not clinical replication. Source extraction and applicability are not certified by arithmetic validation.
'''
 entries.append({'path':PREFIX+'/README.md','mode':'100644','type':'blob','content':readme})
 summary='**Completed information × revision experiment — 3 November 2026:** [scientific decision]('+PREFIX+'/SCIENTIFIC_DECISION.md), [all results]('+PREFIX+'/RESULTS.md), [independent audit]('+PREFIX+'/FINAL_INDEPENDENT_REVIEW.md), and [figure]('+PREFIX+'/analysis_use_profile.png). Six fresh whole-cohort constructions compared external literature with literature plus all CHNS reference summaries. All42executions succeeded (36delivery,6trial), yielding24distinct tables. All six retained, so every revision contrast is zero. Reference-assisted construction means were closer for the requested relations; literature-only outputs retained directions but had important magnitude/joint discrepancies. This is one exposed development case and reference consistency, not independent validation or method superiority. Individual tables remain local.\n\n'
 original=(E/'README.md').read_text(encoding='utf-8-sig');entries.append({'path':'README.md','mode':'100644','type':'blob','content':original.replace('# Evidence-guided virtual cohorts\n','# Evidence-guided virtual cohorts\n\n'+summary,1)})
 entries.append({'path':PREFIX+'/PUBLIC_PACKAGE_MANIFEST.json','mode':'100644','type':'blob','content':json.dumps({'scope':'selected text originals; original local hashes, not exported-text hash attestation','files':manifest},indent=2)+'\n'})
 chunks=[];chunk=[];size=0
 for e in entries:
  n=len(json.dumps(e,ensure_ascii=False))
  if chunk and size+n>150000:chunks.append(chunk);chunk=[];size=0
  chunk.append(e);size+=n
 if chunk:chunks.append(chunk)
 for i,c in enumerate(chunks):(OUT/f'batch_{i:03d}.json').write_text(json.dumps(c,ensure_ascii=False),encoding='utf-8')
 (OUT/'metadata.json').write_text(json.dumps({'prefix':PREFIX,'text_files':len(entries),'batches':len(chunks),'binary_plot':str(U/'analysis_use_profile.png'),'text_content_bytes':sum(len(e['content'].encode('utf-8')) for e in entries)},indent=2),encoding='utf-8')
 print((OUT/'metadata.json').read_text())
if __name__=='__main__':main()
