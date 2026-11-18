"""Publish local manuscript pointers after content, build and visual checks."""
from pathlib import Path
import hashlib, json, shutil

I=Path(__file__).resolve().parent
P=I.parents[1]; M=P/'manuscript'; B=M/'methods_draft_v31_2026-11-11'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
qa=json.loads((B/'BUILD_QA.json').read_text())
audit=json.loads((I/'CONTENT_AUDIT.json').read_text())
assert qa['status']=='PASS_PACKAGE_AND_STANDALONE_BUILD'
assert qa['visual_review'].startswith('Root-led visual inspection completed')
assert audit['status']=='PASS_ROOT_EDITORIAL_AUDIT'
assert sha(M/'DRAFT_v0_31.md')==audit['source_markdown_sha256']==qa['markdown_sha256']
assert sha(B/'paper.pdf')==qa['pdf_sha256'] and sha(B/'overleaf_v31.zip')==qa['zip_sha256']
prior=I/'previous_docs';prior.mkdir(exist_ok=True)
for p in [M/'README.md',P/'docs/CURRENT_RESEARCH_FOCUS.md']:
    target=prior/p.name
    if not target.exists():shutil.copyfile(p,target)
old=(M/'README.md').read_text(encoding='utf-8')
history=old.split('## Preserved history',1)[1]
head=f'''# Manuscript

**Integrated methods working draft v0.31, 11 November 2026.**

[Reading PDF](methods_draft_v31_2026-11-11/paper.pdf) · [Overleaf ZIP](methods_draft_v31_2026-11-11/overleaf_v31.zip) · [Editable manuscript](DRAFT_v0_31.md) · [Build QA](methods_draft_v31_2026-11-11/BUILD_QA.json)

The central question is whether a scientific Agent can turn published evidence and a research request into useful virtual biomedical data. The first result now applies the same lifestyle analysis to real and Agent-generated records. Figure 3 shows all nine adjusted BMI/TC/HDL group contrasts in raw units; Figure S8 shows standardized effects. Two fresh authors generated six complete cohorts. Urban-minus-pastoralist BMI is 1.882 kg/m² in the real sample and 1.700-2.251 across virtual draws. Rural lipid contrasts, lower dispersion and one interaction exception remain explicit.

This lifestyle study permits the original paper and its reported findings. It is source-rich reconstruction, not a new independent target. The separate request-only comparison still starts without prepared papers and includes twelve fresh constructors. Its 24 later review sessions are dependent reviews, not 24 more initial authors. S25 applies a common correlation analysis to 24 existing tables without new generation. These experiments and their different information conditions are not pooled into a success rate.

The Agent chooses sources, structures, numerical assumptions and checks; the worker samples its program. The paper's main evidence supports autonomous construction, analysis-specific scientific uses and inspectable modeling choices. Neither feedback gains nor superiority over an ordinary capable Agent are required claims, and neither is demonstrated generally.

The reading edition has {qa['main_pages']} main pages and {qa['total_pages']} total pages, 19 figures, 32 tables and 25 supplementary sections. Its complete ZIP compiled separately with matching page text and external links. New tables/figure values passed {audit['checks']} root-led editorial checks against previously independently reviewed aggregates; {audit['old_files_unchanged']} protected old files are unchanged. All rendered pages were contact-reviewed, with detailed inspection of changed pages. No new independent scientific review is claimed for this editorial revision.

[Story, evidence map and remaining decisions](../work/manuscript_integration_v31_2026-11-11/STORY_AND_GAP_DECISION.md) · [Integration record](../work/manuscript_integration_v31_2026-11-11/RESULTS.md) · [Numerical/content audit](../work/manuscript_integration_v31_2026-11-11/CONTENT_AUDIT.json)

[Lifestyle application report](../work/lifestyle_application_2026-11-11/report/index.html) · [Existing-table reuse report](../work/published_analysis_replay_2026-11-11/index.html) · [System/results HTML](../docs/research-report.html)

The earlier [biomedical collaborator brief](../deliverables/Biomedical_Use_Review_v30_2026-11-11/01_REVIEW_BRIEF.pdf) and [aggregate-only ZIP](../deliverables/Biomedical_Use_Review_v30_2026-11-11.zip) remain available but predate the lifestyle addition. No human response has been collected. Author details, declarations, biomedical interpretation and venue formatting remain open. This is an expanded local working draft, not a submitted manuscript or an online Overleaf project.

This editorial integration ran no API calls, generators, patient analyses or new data acquisition and made no public synchronization. No new paid batch or data campaign is queued.

## Preserved history

- [v0.30](DRAFT_v0_30.md), [reading PDF](methods_draft_v30_2026-11-11/paper.pdf) and [Overleaf ZIP](methods_draft_v30_2026-11-11/overleaf_v30.zip). Superseded reading edition; frozen content unchanged.
'''
(M/'README.md').write_text(head+history,encoding='utf-8')
focus=P/'docs/CURRENT_RESEARCH_FOCUS.md'
s=focus.read_text(encoding='utf-8')
title,rest=s.split('\n',1)
new='''

## Current manuscript integration v0.31 — 11 November 2026

The [new reading PDF](../manuscript/methods_draft_v31_2026-11-11/paper.pdf), [Overleaf ZIP](../manuscript/methods_draft_v31_2026-11-11/overleaf_v31.zip) and [editable draft](../manuscript/DRAFT_v0_31.md) integrate the completed lifestyle generation and analysis-only reuse studies. The first main result holds a scientific analysis fixed and changes its data. Figure 3 shows all nine lifestyle contrasts in raw units; S24 retains standardized results, sample/scale diagnostics and the HDL interaction exception. S25 preserves all old-table correlation results. The expanded edition is 78 pages including supporting material, with 19 figures and 32 tables.

The mainline remains useful, inspectable Agent-generated biomedical data. Source-rich reconstruction, request-only autonomous construction and analysis-only reuse are clearly separated. The useful urban BMI pattern does not imply full joint-distribution fidelity. Ordinary Agent implementations remain valid. Feedback revision is a quality-control capability, not the required source of improvement.

The [story and gap decision](../work/manuscript_integration_v31_2026-11-11/STORY_AND_GAP_DECISION.md) ties any further experiment to a stronger desired claim. No automatic provider expansion, new clinical family, mechanism pilot or parameter tuning is launched. First complete biomedical interpretation and ordinary submission preparation. A new-population claim would require a separately planned independent target; repeated seeds and exposed cases cannot supply it.

The new edition passed 517 root-led editorial checks, a separately compiled archive comparison and rendered-page inspection. The earlier experiments already have their recorded independent recomputation; this manuscript pass is not a new independent scientific review. Ninety-seven protected old files remain unchanged. No new model calls, generation, patient fits, data acquisition or public synchronization occurred. Earlier entries below describe historical unit status; v0.31 is now the current local manuscript.
'''
focus.write_text(title+new+rest,encoding='utf-8')
result=f'''# Manuscript integration v0.31 — completed

11 November 2026. This unit integrates completed, already reviewed results; it does not run another scientific experiment.

## Delivered

- `manuscript/DRAFT_v0_31.md`: revised abstract, introduction, information boundaries, Methods 4.4-4.5, new first result, discussion and limitations; Supplements S24-S25.
- `manuscript/methods_draft_v31_2026-11-11/paper.pdf`: {qa['main_pages']} main pages, {qa['total_pages']} total; 19 figures, 32 tables and 25 supplementary sections.
- `manuscript/methods_draft_v31_2026-11-11/overleaf_v31.zip`: complete editable LuaLaTeX package, compiled from its extracted files with matching page text and links.
- Two new publication-size vector figures: raw-unit main Figure 3 and standardized Figure S8. Tables S22-S25 retain all selected contrasts, diagnostics and correlation profiles.
- `STORY_AND_GAP_DECISION.md`: claim/evidence map and conditional next-experiment decisions.
- Current local manuscript README and research-focus pointers updated; their previous versions are saved under `previous_docs`.

## Scientific story

Lead with the data product: the same lifestyle analysis operates on measured or generated records. Urban BMI differences are useful in this application; the lower raw TC magnitude, rural lipid discrepancies, lower lipid dispersion and one HDL interaction exception remain visible. The original paper was legal input, so this result is source-rich reconstruction. Request-only construction and prior failures retain their separate interpretation. The research remains about scientific-use virtual data rather than a newly invented confidence score or failure benchmark.

## Verification

- {audit['checks']} root-led editorial checks bind the new tables and 126 plotted records to saved aggregates, verify complete coverage and preserve {audit['old_files_unchanged']} old input files.
- Complete ZIP/standalone compilation: exact packaged file bytes, matching text on all pages, matching {qa['clickable_external_links']} clickable external links; no overfull boxes, missing characters or oversized floats.
- All 78 rendered pages inspected in contact sheets; changed abstract, Methods, primary result, figures, discussion and tables inspected individually. Stranded heading and short-table page-break defects were corrected.
- Prior lifestyle experiment: 189 contrasts and 21 interaction tests, independently recomputed before this turn. These are not new fits or checks of clinical validity.
- No additional independent Agent or biomedical reviewer was invoked in this editorial unit. Existing independent experiment reviews are cited as historical evidence, not relabeled as manuscript review.

## Cost, exposure and decision

New API calls: 0. New generated tables: 0. New patient analyses: 0. New downloads: 0. Public synchronization: no. No frozen scientific artifact was changed. All individual records, full papers, credentials and raw API logs remain outside the Overleaf package.

The integrated draft is ready for focused content discussion and biomedical interpretation. It is not venue-formatted or submission-ready: author/affiliation details and declarations remain incomplete. Additional replication or independent-target testing is conditional on a stronger desired claim, not automatically queued. Do not retune disclosed cases.
'''
(I/'RESULTS.md').write_text(result,encoding='utf-8')
outputs=[M/'DRAFT_v0_31.md',B/'paper.pdf',B/'overleaf_v31.zip',B/'BUILD_QA.json',I/'CONTENT_AUDIT.json',I/'STORY_AND_GAP_DECISION.md',I/'RESULTS.md',M/'README.md',focus]
state={'status':'completed_editorial_integration','version':'0.31','new_api_calls':0,'new_generated_tables':0,'new_patient_analyses':0,'new_downloads':0,'public_sync':False,
       'root_editorial_checks':audit['checks'],'independent_experimental_review':'Previously completed; no new independent manuscript reviewer',
       'protected_old_files':audit['old_files_unchanged'],'total_pages':qa['total_pages'],'main_pages':qa['main_pages'],
       'outputs':{p.relative_to(P).as_posix():sha(p) for p in outputs},
       'next':'Biomedical interpretation and submission preparation; no automatic scientific expansion.'}
(I/'STATE.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':state['status'],'pages':state['total_pages'],'outputs':len(outputs)}))
