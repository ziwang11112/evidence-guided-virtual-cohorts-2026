"""Record the completed editorial delivery; no scientific computation or dispatch."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
W=Path(__file__).resolve().parent
P=W.parents[1]
B=P/'manuscript/methods_draft_v32_2026-11-16'
now=datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
qa=json.loads((B/'BUILD_QA.json').read_text(encoding='utf8'))
assert qa['status']=='passed' and qa['pages']==18
for rel,h in json.loads((W/'INPUT_BINDINGS.json').read_text(encoding='utf8'))['files'].items():
    assert sha(P/rel)==h,rel
visual={'status':'reviewed','reviewed_at_utc':now,'pdf_sha256':sha(B/'paper.pdf'),
        'all_page_contact_review':list(range(1,19)),
        'individual_page_review':[3,7,8,9,16,17,18],
        'review_method':'Rendered PNG inspection by root assistant; not independent personnel review.',
        'findings':'Final pages have no observed clipping, overlap or orphaned table rows. Figures retain readable point/range/interval distinctions. Table S3 is together on page 17.',
        'resolved':['Long monospaced paths','Table S3 lone continued row','Supplementary hyperlink anchor collisions','PDF inclusion version mismatch','Figure 4 range direction caption'],
        'remaining':'Single-column working draft; final venue typesetting and author/declaration metadata remain.'}
(W/'VISUAL_REVIEW.json').write_text(json.dumps(visual,indent=2),encoding='utf8')
qa['visual_review_completed']=True
qa['visual_review_pages']=18
qa['final_pdf_sha256']=sha(B/'paper.pdf')
(B/'BUILD_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf8')
outputs=[P/'manuscript/DRAFT_v0_32.md', B/'paper.pdf',B/'paper.tex',B/'overleaf_v32.zip',B/'BUILD_INPUTS.json',B/'BUILD_QA.json',B/'OVERLEAF_README.md',
         *sorted((P/'manuscript/paper_figures_v32_2026-11-16').glob('*.*')),
         W/'PLOTTED_VALUES.csv',W/'CONTENT_AUDIT.json',W/'VISUAL_REVIEW.json',W/'RESULTS.md',W/'NEXT_DECISION.md']
manifest={'created_utc':now,'delivery_scope':'Original manuscript, figure assets and aggregates; no patient-level records or third-party papers.',
          'files':[{'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in outputs]}
(W/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
state={'status':'completed','completed_utc':now,'unit':'manuscript_integration_v32','manuscript':'manuscript/DRAFT_v0_32.md',
       'pages':18,'main_figures':4,'tables':6,'api_calls':0,'new_tables':0,'patient_data_read':False,'new_patient_fits':0,
       'protected_prior_inputs_unchanged':24,'plotted_values_verified':304,'editorial_checks':785,
       'standalone_package_verified':True,'visual_review_completed':True,'public_sync_performed':False,
       'automation_changed':False,'new_experiment_queued':False,
       'next_decision':'Use NEXT_DECISION.md to resolve a specific scientific-use/submission gap; no automatic source or provider expansion.'}
(W/'STATE.json').write_text(json.dumps(state,indent=2),encoding='utf8')
print(json.dumps({'status':state['status'],'pages':18,'delivered_files':len(outputs),'pdf_bytes':(B/'paper.pdf').stat().st_size,'zip_bytes':(B/'overleaf_v32.zip').stat().st_size}))
