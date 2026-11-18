"""Finalize the reviewed package and current-project entry points."""
from pathlib import Path
import hashlib,json,shutil,zipfile

I=Path(__file__).resolve().parent;P=I.parents[1]
O=P/'deliverables/Biomedical_Use_Review_v31_2026-11-11';Z=O.with_suffix('.zip')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dump=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
q=json.loads((I/'PACKET_QA.json').read_text());assert q['status']=='PASS_ROOT_PACKET_AUDIT'
assert sha(O/'01_REVIEW_BRIEF.pdf')==q['pdf_sha256']
visual={'status':'PASS_ROOT_VISUAL_REVIEW','pages':4,'scope':'All four final PNG pages inspected; clean page breaks, readable figures and tables, no visible clipping or overlap',
        'pdf_sha256':sha(O/'01_REVIEW_BRIEF.pdf'),'rendered_pages':{p.name:sha(p) for p in (I/'qa').glob('page-*.png')}}
dump(I/'VISUAL_REVIEW.json',visual)
m=json.loads((O/'PACKAGE_MANIFEST.json').read_text())
m['status']='review_ready';m['checks']=q['checks'];m['visual_review']='Four pages inspected; original full manuscript is an unchanged optional attachment.'
m['review_scope']='Root-led artifact/numerical review; historical independent scientific audits already recorded; no human domain verdict collected.'
dump(O/'PACKAGE_MANIFEST.json',m)
with zipfile.ZipFile(Z,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for f in sorted(O.rglob('*')):
        if f.is_file():z.write(f,O.name+'/'+f.relative_to(O).as_posix())

back=I/'previous_docs';back.mkdir(exist_ok=True)
for file in [P/'docs/CURRENT_RESEARCH_FOCUS.md',P/'manuscript/README.md']:
    dst=back/file.name
    if not dst.exists():shutil.copyfile(file,dst)
focus=P/'docs/CURRENT_RESEARCH_FOCUS.md'
s=focus.read_text(encoding='utf-8');title,rest=s.split('\n',1)
note='''

## Current follow-up: biomedical use review packet v0.31 — 11 November 2026

The [updated collaborator ZIP](../deliverables/Biomedical_Use_Review_v31_2026-11-11.zip) and [four-page brief](../deliverables/Biomedical_Use_Review_v31_2026-11-11/01_REVIEW_BRIEF.pdf) now include the completed lifestyle application, all nine primary contrasts, all sample/scale/interaction diagnostics, and selected parameter origins. The [blank review form](../deliverables/Biomedical_Use_Review_v31_2026-11-11/02_REVIEW_FORM.md) asks which scientific uses are useful, which assumptions change that judgment and which one addition is necessary. Earlier glycemia/lipid profiles and the unchanged full v0.31 draft are optional attachments. Individual patient/generated rows and third-party full papers are excluded.

The [root scientific-use review](../work/biomedical_review_v31_2026-11-11/ROOT_SCIENTIFIC_USE_REVIEW.md) identifies the key distinction: BMI group means have published descriptive anchors, while much lipid conditional/joint information remains assumed or extended from a source subgroup. These origins support targeted interpretation, not a validated confidence ranking or causal attribution of errors. Lifestyle categories combine geography, subsistence and diet; generated p-values are not extra clinical evidence.

The packet passed 1,013 root-led consistency/package checks and visual inspection of all four pages. Prior frozen candidate and source/code audits were inspected; no new model call, generation, patient fit, data acquisition, external contact or public synchronization occurred. No human review has been collected. Manuscript v0.31 remains unchanged. Use focused domain feedback to decide a specific next experiment rather than expanding by default.
'''
assert 'Current follow-up: biomedical use review packet v0.31' not in s
focus.write_text(title+note+rest,encoding='utf-8')
readme=P/'manuscript/README.md';s=readme.read_text(encoding='utf-8')
anchor='**Integrated methods working draft v0.31, 11 November 2026.**'
add='''

**Current biomedical-review packet:** [four-page brief](../deliverables/Biomedical_Use_Review_v31_2026-11-11/01_REVIEW_BRIEF.pdf), [review-friendly ZIP](../deliverables/Biomedical_Use_Review_v31_2026-11-11.zip) and [blank feedback form](../deliverables/Biomedical_Use_Review_v31_2026-11-11/02_REVIEW_FORM.md). Includes the lifestyle application, complete selected aggregates, source/assumption mappings and optional earlier cases. No human response has yet been collected; the manuscript itself remains unchanged.
'''
assert s.count(anchor)==1;s=s.replace(anchor,anchor+add,1);readme.write_text(s,encoding='utf-8')
results='''# Biomedical-use review package v0.31 — completed

Prepared a four-page English brief and reviewer-friendly ZIP around the completed
lifestyle application. The packet includes a blank use-focused response form,
source/method context, parameter-origin guide, 63 primary per-dataset estimates,
21 sample/scale/interaction rows and all 189 pooled/sex-specific contrasts.
The optional folder holds the unchanged v0.31 manuscript and earlier complete
glycemia/lipid review materials.

The root review checked exact modeling commitments and recorded evidence:
published BMI descriptive anchors; assumed TC magnitude/joint effects; subgroup
HDL spread extended across groups; observational composite lifestyle categories;
unequal measured sample sizes and conditional synthetic uncertainty. These make
the research-use questions concrete. They do not establish a new causal failure
mechanism, confidence score or external clinical validity.

QA: 1,013 root-led aggregate, rounded-table, file-integrity, package and text-bound
checks passed. All four final pages were visually inspected. The first QA attempt
mistakenly expected four free-text response lines; the form correctly has five.
The validator expectation was corrected without altering results or the form.
This is not a new independent scientific review. Historical independent experiment
recomputation remains separately attributed. No human responses have been collected.

No API calls, generators, patient-level refits, new downloads, external messages or
GitHub synchronization occurred. Frozen experiments, source audits and manuscript
files are unchanged. Only the current README/research-focus entry points were
updated, with previous versions preserved locally. No new paid run is queued.

Next: obtain qualitative biomedical judgment using the blank form. A response can
justify clarification, a narrower use, better evidence, a specific implementation
fix or a separately planned experiment. Do not retune this disclosed case by default.
'''
(I/'RESULTS.md').write_text(results,encoding='utf-8')
state={'status':'complete_review_package_ready','new_api_calls':0,'new_generated_tables':0,'new_patient_fits':0,'public_sync':False,'human_review_collected':False,
 'main_draft_unchanged':True,'checks':q['checks'],'pdf_pages':4,'zip_bytes':Z.stat().st_size,
 'pdf_sha256':sha(O/'01_REVIEW_BRIEF.pdf'),'zip_sha256':sha(Z),'next':'Qualitative biomedical use review; no automatic expansion.',
 'protected_inputs':len(json.loads((I/'INPUT_BINDINGS.json').read_text())['hashes'])}
dump(I/'STATE.json',state)
print(json.dumps(state))
