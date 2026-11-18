"""Publish local manuscript pointers after numerical, build and visual review."""
from pathlib import Path
import hashlib,json,datetime
W=Path(__file__).resolve().parent;P=W.parents[1];M=P/'manuscript';B=M/'methods_draft_v33_2026-11-17'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
qa=json.loads((B/'BUILD_QA.json').read_text());assert qa['passed'] and not qa['protected_changed']
visual=json.loads((W/'VISUAL_REVIEW.json').read_text());assert visual['passed'] and visual['pdf_sha256']==sha(B/'paper.pdf')
pages=qa['pages']
summary=f'''# v0.33 manuscript integration — completed

17 November 2026. No new API experiment, generation, patient refit or public sync.

## Deliverables

- {pages}-page reading PDF: `manuscript/methods_draft_v33_2026-11-17/paper.pdf`.
- Editable text: `manuscript/DRAFT_v0_33.md`.
- Independently compiled Overleaf archive: `manuscript/methods_draft_v33_2026-11-17/overleaf_v33.zip`.
- Five main figures and one supplementary figure; three main tables and six supplementary tables.
- Native draw.io overview and embedded editable SVG; vector PDF/SVG/PNG result figures.
- Claim/evidence/figure map: `CLAIM_EVIDENCE_MAP.md`.

## What changed

The title, abstract, contributions and method now center on an Agent turning a request and fragmented evidence into an executable joint model and analyzable records. Agent scientific choices are distinguished from numerical execution. The method preserves whole-cohort generation without target individual input and allows different models for different requests.

New PNS and iron three-condition experiments are integrated with the lifestyle application and controlled composition tasks. PNS residual-correlation discrepancy falls 78.6% relative to SUMMARY; iron absolute log-OR discrepancy falls 46.8%. All other endpoints remain visible, including worsened slopes, joint prevalence and continuous iron dependence. These are exposed developmental comparisons, not new independent populations or a general workflow advantage.

The earlier favorable two-arm pressure search is retained in Figure S1/Table S5. Its 92.89% comparison is not substituted for the new three-arm result. Previous ordinary-Agent comparisons, mathematical repairs and failed source admission remain summarized in Table S6 with original records preserved.

## Validation

- {qa['plotted_rows']} plotted records reconciled to closed aggregate inputs.
- {qa['checks']} editorial/numerical/build checks passed; this is not a scientific sample count.
- {qa['protected_files']} protected inputs unchanged, including frozen experiments and v0.32 artifacts.
- Independent extraction and two-pass compilation of the Overleaf ZIP; identical page text and page count.
- No TeX overflow, missing-glyph or unresolved-reference warnings in the final builds.
- All final pages inspected on contact sheets, with detailed inspection of the figures/tables and changed page boundaries; visual receipt records the scope.

## Remaining evidence, not new work launched

The next claim-driven work is a domain-defined usefulness tolerance, a second-model replication of the same controlled task, and a genuinely unused evaluation boundary if transport is to be claimed. A compatible published-method reproduction remains a separate comparison. No extra agent components or additional cohorts were launched by this editorial task.
'''
(W/'RESULTS.md').write_text(summary,encoding='utf-8')
indexpaths=[P/'README.md',P/'docs/CURRENT_RESEARCH_FOCUS.md',M/'README.md']
oldhash={x.relative_to(P).as_posix():sha(x) for x in indexpaths}
if not (W/'INDEX_PREEDIT_HASHES.json').exists():(W/'INDEX_PREEDIT_HASHES.json').write_text(json.dumps(oldhash,indent=2)+'\n')
for path in indexpaths:
 old=path.read_text(encoding='utf-8')
 if 'Current reading edition: v0.33' in old:continue
 rel='../' if path.parent.name=='docs' else ''
 if path.parent==M:
  paper='methods_draft_v33_2026-11-17/paper.pdf';draft='DRAFT_v0_33.md';zipf='methods_draft_v33_2026-11-17/overleaf_v33.zip';result='../work/manuscript_integration_v33_2026-11-17/RESULTS.md'
 else:
  paper=rel+'manuscript/methods_draft_v33_2026-11-17/paper.pdf';draft=rel+'manuscript/DRAFT_v0_33.md';zipf=rel+'manuscript/methods_draft_v33_2026-11-17/overleaf_v33.zip';result=rel+'work/manuscript_integration_v33_2026-11-17/RESULTS.md'
 block=f'''## Current reading edition: v0.33 — 17 November 2026

[Reading PDF]({paper}) · [Editable text]({draft}) · [Overleaf ZIP]({zipf}) · [Integration and audit]({result}).

**From Fragmented Evidence to Analyzable Biomedical Cohorts with Scientific Agents.** The {pages}-page edition integrates both new content-control experiments with the lifestyle scientific-use example and controlled composition study. Five main figures and one supplement figure show actual Agent choices and complete scientific profiles. PNS residual-correlation discrepancy falls 78.6% and iron absolute log-OR discrepancy 46.8% versus marginal summaries; other analyses include unchanged and worse results. These are exposed developmental references, not new target confirmations.

All 698 plotted records are reconciled; 919 editorial/build checks and standalone compilation pass. The 3,650 protected inputs and v0.32 are unchanged. This integration performed no new Agent calls, cohort generation or patient fits. Earlier entries below are historical snapshots; their then-current version labels do not supersede v0.33.

'''
 first,rest=old.split('\n',1)
 path.write_text(first+'\n\n'+block+rest.lstrip('\n'),encoding='utf-8')
artifacts=[M/'DRAFT_v0_33.md',B/'paper.pdf',B/'paper.tex',B/'overleaf_v33.zip',B/'BUILD_QA.json',W/'PLOTTED_VALUES.csv',W/'CLAIM_EVIDENCE_MAP.md',W/'RESULTS.md',W/'VISUAL_REVIEW.json']
artifacts+=list((M/'paper_figures_v33_2026-11-17').glob('*'))
(W/'DELIVERY_MANIFEST.json').write_text(json.dumps({'files':{p.relative_to(P).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in artifacts}},indent=2)+'\n')
state={'status':'complete','version':'v0.33','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pages':pages,'main_figures':5,'supplement_figures':1,'tables':9,'new_experiments':False,'api_calls':0,'protected_inputs_unchanged':True,'independent_overleaf_compile':True,'next':'Domain review and frozen, claim-specific replication; no new experiment started.'}
(W/'STATE.json').write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps(state))
