"""Prepare text-only, reviewed main-study artifacts; never participant row files."""
from pathlib import Path
import json
import re
import sys
UNIT=Path(__file__).resolve().parents[1]
PROJECT=UNIT.parents[1]
sys.path.insert(0,str(UNIT/'implementation'))
import main_session_v1 as c
BASE='biomedical_research/virtual_cohort_system/'
DEST=BASE+'reports/main_study_freeze_2026-11-03/'
TEXT={'.json','.md','.py','.txt'}

def prepare():
    release=c.READ(UNIT/'RELEASE.json');c.require_campaign_closed(release)
    audit=c.READ(UNIT/'independent_audit/RESULTS.json')
    assert audit['status']=='matched'
    assert audit['result_sha256']==c.SHA(UNIT/'final_evaluation/RESULTS.json')
    for required in [UNIT/'RESULTS.md',UNIT/'CLAIM_LOCK.json',UNIT/'publication/RESULT_INTERPRETATION.json',UNIT/'publication/FINAL_REPORT_REVIEW.json',UNIT/'publication/FIGURE_VISUAL_QA.json',UNIT/'publication/README_PUBLIC.md',PROJECT/'manuscript/DRAFT_v0_4.md']:
        assert required.is_file(), required
    assert c.READ(UNIT/'publication/FINAL_REPORT_REVIEW.json')['status']=='ready'
    files={}
    def add(path,destination):
        path=Path(path)
        assert path.is_file() and '__pycache__' not in path.parts
        assert path.suffix in TEXT or path.name in {'ALL_ENDPOINTS.csv','main_scientific_uses.svg'}
        assert path.stat().st_size<6_000_000
        content=path.read_text(encoding='utf-8')
        assert not re.search(r'-----BEGIN [A-Z ]*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{30,}',content)
        assert destination not in files or files[destination]['sha256']==c.SHA(path)
        files[destination]={'source':str(path),'sha256':c.SHA(path),'content':content}
    for item in release['constructions']:
        s=c.Session(item['session_root']);selection=s.selected('science_closed')
        if selection:
            chosen=selection[0]
            for source in sorted((s.bundle/chosen['candidate']).rglob('*')):
                if source.is_file() and source.suffix in TEXT and '__pycache__' not in source.parts:
                    relative=source.relative_to(s.bundle/chosen['candidate']).as_posix()
                    add(source,DEST+'constructions/'+item['id']+'/selected/'+relative)
            for key in ['decision','review']:
                c.verify_bound(chosen[key]);source=Path(chosen[key]['path'])
                add(source,DEST+'constructions/'+item['id']+'/'+source.name)
        # Metadata receipts only, without output rows or execution-directory copying.
        for source in sorted((s.folder/'events').glob('*.json')):
            add(source,DEST+'constructions/'+item['id']+'/events/'+source.name)
        for event in s.selected('result'):
            if event.get('receipt'):
                c.verify_bound(event['receipt']);source=Path(event['receipt']['path'])
                add(source,DEST+'constructions/'+item['id']+'/execution_receipts/'+event['run_id']+'.json')
                runtime=source.with_name('runtime_manifest.json')
                if runtime.exists():
                    assert c.SHA(runtime)==c.READ(source)['files']['runtime_manifest.json']
                    add(runtime,DEST+'runtime_manifests/'+c.SHA(runtime)+'.json')
    for directory in [UNIT/'independent_audit',UNIT/'first_pair_review',UNIT/'author_followups',UNIT/'final_evaluation',*sorted(UNIT.glob('group*_review'))]:
        if not directory.exists():continue
        for source in directory.rglob('*'):
            if source.is_file() and '__pycache__' not in source.parts and (source.suffix in TEXT or source.name=='ALL_ENDPOINTS.csv'):
                add(source,DEST+source.relative_to(UNIT).as_posix())
    for filename in ['STATE.json','CONTINUATION.json','ANALYSIS_RUNTIME.json','campaign_ops.py','INPUT_CACHE_NOTE.json','ALL_AUTHOR_DECISIONS_SUBMITTED.json','GENERATION_COMPLETED.json','RESULTS.md','CLAIM_LOCK.json']:
        source=UNIT/filename
        if source.exists():add(source,DEST+filename)
    for filename in ['plot_main.py','uptake_inventory.py','prepare_export.py','finalize_report.py','build_result_interpretation.py','UPTAKE_INVENTORY.json','COST_FINAL.json','METHODS_REVIEW.md','METHODS_REVIEW.json','METHODS_REVIEW_RESPONSE.json','RESULT_INTERPRETATION.md','RESULT_INTERPRETATION.json','FIGURE_VISUAL_QA.json','FINAL_REPORT_REVIEW.md','FINAL_REPORT_REVIEW.json','FINAL_REPORT_REVIEW_RESPONSE.json','DRAFT_REVIEW_RESPONSE_1.json','DRAFT_REVIEW_RESPONSE_2.json']:
        source=UNIT/'publication'/filename
        if source.exists():add(source,DEST+'publication/'+filename)
    for source in (UNIT/'publication/figures').glob('*'):
        if source.suffix=='.json' or source.name=='main_scientific_uses.svg':add(source,DEST+'publication/figures/'+source.name)
    for filename in ['MAIN_STUDY_METHODS_2026-11-03.md','DRAFT_v0_4.md']:
        source=PROJECT/'manuscript'/filename
        if source.exists():add(source,BASE+'manuscript/'+filename)
    readme=UNIT/'publication/README_PUBLIC.md'
    if readme.exists():add(readme,'README.md')
    out=UNIT/'publication/final_export';out.mkdir(exist_ok=False)
    entries=[{'path':path,'mode':'100644','type':'blob','content':item['content']} for path,item in sorted(files.items())]
    batches=[];current=[];size=0
    for entry in entries:
        width=len(json.dumps(entry,ensure_ascii=False).encode('utf-8'))
        if current and (size+width>350_000 or len(current)>=35):batches.append(current);current=[];size=0
        current.append(entry);size+=width
    if current:batches.append(current)
    for i,batch in enumerate(batches):c.WRITE(out/f'batch_{i:02d}.json',batch)
    c.WRITE(out/'MANIFEST.json',{'files':len(files),'batches':len(batches),'created_utc':c.now(),'row_files_included':False,
      'scope':'Reviewed selected candidate code and original scientific records, metadata execution receipts, audited aggregate analyses, figures and manuscript; no patient/generated row tables, original third-party papers/codebooks or credentials. Absolute paths preserve original audit metadata, not cross-host portability guarantees.',
      'artifacts':[{'destination':path,'source':item['source'],'sha256':item['sha256']} for path,item in sorted(files.items())]})
    return {'files':len(files),'batches':len(batches)}

if __name__=='__main__':print(json.dumps(prepare()))
