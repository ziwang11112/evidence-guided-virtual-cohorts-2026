"""Package the reviewed v15 reading copy; no scientific execution."""
from pathlib import Path
import hashlib,json,re,zipfile
import fitz

R=Path(__file__).resolve().parent; P=R.parents[1]; M=P/'manuscript'
B=M/'conference_draft_v15_2026-11-05'; F=M/'paper_figures_v15_2026-11-05'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,t:p.write_text(t,encoding='utf-8',newline='\n')
new=M/'DRAFT_v0_15.md'; old=M/'DRAFT_v0_14.md'
review=json.loads((R/'INDEPENDENT_CONTENT_REVIEW.json').read_text(encoding='utf-8'))
visual=json.loads((R/'FINAL_PDF_REVIEW.json').read_text(encoding='utf-8'))
assert review['status']=='PASS'
assert review['draft_sha256']==sha(new)
assert visual['decision']=='PASS_FOR_READING_COPY'
assert visual['pdf']['sha256']==sha(B/'paper.pdf')
assert visual['tex']['sha256']==sha(B/'paper.tex')
build=json.loads((B/'BUILD_INPUTS.json').read_text(encoding='utf-8'))
assert build['source_sha256']==sha(new)
assert build['source_tex_sha256']==sha(B/'paper.tex')
doc=fitz.open(B/'paper.pdf'); pages=len(doc)
page_map=[{'page':i+1,'characters':len(pg.get_text()),
 'figures':[x for x in pg.get_text().splitlines() if x.startswith('Figure ')],
 'tables':[x for x in pg.get_text().splitlines() if x.startswith('Table ')]} for i,pg in enumerate(doc)]
write(R/'PDF_PAGE_MAP.json',json.dumps(page_map,indent=2)+'\n')
members={n:B/n for n in ['paper.tex','paper.pdf','BUILD_INPUTS.json','build_reading_copy.py']}
members['README.md']=B/'OVERLEAF_README.md'
members.update({'figures/'+f.name:f for f in sorted((B/'figures').glob('*.pdf'))})
assert len(members)==13
with zipfile.ZipFile(B/'overleaf_v15.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,path in members.items():
  item=zipfile.ZipInfo(name,date_time=(2026,11,5,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(item,path.read_bytes())
with zipfile.ZipFile(B/'overleaf_v15.zip') as z:
 assert set(z.namelist())==set(members)
 assert all(z.read(n)==p.read_bytes() for n,p in members.items())
write(R/'PACKAGE_INVENTORY.json',json.dumps(dict(zip_sha256=sha(B/'overleaf_v15.zip'),
 members=[dict(path=n,sha256=sha(p),bytes=p.stat().st_size) for n,p in members.items()],verified=True),indent=2)+'\n')
navigation=f'''# Evidence-guided virtual biomedical data

**Current manuscript: [v0.15](manuscript/DRAFT_v0_15.md), 5 November 2026.**

**From Published Evidence to Analyzable Biomedical Cohorts with Scientific Agents**

[Reading PDF](manuscript/conference_draft_v15_2026-11-05/paper.pdf) · [Overleaf-ready ZIP](manuscript/conference_draft_v15_2026-11-05/overleaf_v15.zip) · [Figures](manuscript/paper_figures_v15_2026-11-05/README.md) · [Venue and story audit](work/{R.name}/VENUE_AND_STORY_AUDIT.md)

A scientific Agent translates heterogeneous published evidence, a population description, optional observations and intended analyses into a joint generating model and virtual data. Whole-cohort generation without individual construction records is central. The Agent chooses the scientific structure and numerical evidence use; deterministic tools execute sampling, inspection and analysis. Different requests can receive different laws.

## Current scientific argument

1. Study-qualified evidence becomes an executable model through explicit numerical derivations and completion assumptions.
2. Relational evidence improves five of six designated mean-discrepancy comparisons; all six results and statistical comparisons remain visible.
3. The workflow constructs complete glycemic and lipid data, with analysis-specific successes and quantitative limits. Supplied-summary reconstruction, open retrieval and longitudinal examples demonstrate different information settings.

The completed cross-task study contains six constructions and 18 final tables. All 54 primary point directions agree with corresponding cached sample estimates, but effect magnitudes, residual dependence and dispersion remain mixed. The TC reference interval crosses zero. All 513 aggregate outputs were independently recomputed; references were previously exposed. All six authors retained their initial laws, and runtime source checks were unavailable, so this study does not demonstrate numerical source-fit feedback or revision improvement.

## Reading package and next decision

The {pages}-page generic reading copy has four main figures, four supplementary figures, one main table, six supplementary tables and 28 references. Four plots have been redesigned from frozen aggregates; no experiment was rerun or retuned. The narrative follows the scientific argument rather than the chronology of project batches.

- [Manuscript history](manuscript/README.md) and [editorial explanation in Chinese](work/{R.name}/EDITORIAL_DECISIONS_ZH.md)
- [Independent content review](work/{R.name}/INDEPENDENT_CONTENT_REVIEW.md) and [actual PDF review](work/{R.name}/FINAL_PDF_REVIEW.md)
- [Completed cross-task study](work/evidence_use_cross_task_2026-11-05/RESULTS.md) and [evidence-use implementation](cohort_harness/evidence_use_v1.py)
- [Claim-specific experiment gaps](manuscript/KEY_EXPERIMENT_GAPS_v14_2026-11-05.md) and [exposure registry](docs/DATASET_EXPOSURE_REGISTRY.md)

The venue audit prioritizes MLHC for conference fit, a future AAMAS cycle for the Agent community, and PLOS Digital Health as a separate journal route. KDD Research/AI for Sciences are conditional ambitious options. Official 2027 rules and deadline availability are recorded in the audit; no acceptance probability is implied.

Scientific author review and venue-specific formatting/declarations remain. The ZIP is a local LuaLaTeX package, not an online Overleaf project or a submission. Patient-level real/generated data, third-party originals and credentials remain local. [Current focus](docs/CURRENT_RESEARCH_FOCUS.md).
'''
write(P/'README.md',navigation)
write(R/'ROOT_README.md',re.sub(r'\]\((?!https?://)([^)]+)\)',lambda m:'](biomedical_research/virtual_cohort_system/'+m.group(1)+')',navigation))
write(M/'README.md',f'''# Manuscript

**Current edition: [v0.15](DRAFT_v0_15.md), 5 November 2026.**

[Reading PDF](conference_draft_v15_2026-11-05/paper.pdf) · [Overleaf-ready ZIP](conference_draft_v15_2026-11-05/overleaf_v15.zip) · [Figures](paper_figures_v15_2026-11-05/README.md)

The narrative centers on Agent-controlled qualification, numerical translation and joint-law construction from published evidence. Four main figures show a worked construction, the six-analysis information contrast, cross-request scientific results, and supplied-summary reconstruction. Complete tables and retrieval, longitudinal, dispersion and dependence displays remain in the supplement. Historical experiments and all unfavorable results are retained.

This {pages}-page reading format is not an official venue template. [Content review](../work/{R.name}/INDEPENDENT_CONTENT_REVIEW.md), [PDF review](../work/{R.name}/FINAL_PDF_REVIEW.md), [story redesign](../work/{R.name}/STORY_REDESIGN.md) and [venue audit](../work/{R.name}/VENUE_AND_STORY_AUDIT.md) bind this edition. No scientific reruns or participant reads were used for this revision.

Scientific author review, final venue length/format, authorship, affiliations, funding, conflicts, ethics/access, AI assistance and software licensing remain to be completed. Stronger transport, component-benefit, uncertainty or efficiency claims require their corresponding evidence; they are not claimed here. See the [claim-specific gap checklist](KEY_EXPERIMENT_GAPS_v14_2026-11-05.md).

## Preserved history

- [v0.14](DRAFT_v0_14.md) and [reading copy](conference_draft_v14_2026-11-05/paper.pdf)
- [v0.13.1](DRAFT_v0_13_1.md), [v0.13](DRAFT_v0_13.md), [v0.12](DRAFT_v0_12.md)
- [Historical findings](SUPPLEMENT_HISTORICAL_RESULTS_v05.md)
''')
write(P/'docs/CURRENT_RESEARCH_FOCUS.md',f'''# Current focus — evidence-guided virtual biomedical data

Updated 5 November 2026. **The completed experiments are organized into [manuscript v0.15](../manuscript/DRAFT_v0_15.md).**

The core is an Agent converting study-qualified published evidence, target-population descriptions, optional observations and intended analyses into executable joint laws and useful virtual data. Whole-cohort generation without individual inputs remains central. Ordinary Agents and task-specific laws are valid implementations.

This editorial unit reorganized the paper into a scientific argument, redrew four result displays from frozen aggregates, retained complete numerical tables and obtained independent content/PDF review. It did not generate new tables, access patient rows, refit clinical references or modify frozen experiments.

The existing cross-task study produced six laws and 18 tables. Primary directions agreed with cached sample points while magnitudes, spread and residual dependence remained mixed. The TC sensitivity interval crosses zero. All six laws were retained and numerical source-check feedback was unavailable. These are developmental, previously exposed references; directions alone do not establish quantitative transport.

## Next decision

Proceed with scientific author review and venue selection. [The official-source venue audit](../work/{R.name}/VENUE_AND_STORY_AUDIT.md) prioritizes MLHC, a future AAMAS cycle and a separate PLOS Digital Health journal route; KDD options are conditional. Future conference dates/page rules are not assumed from earlier years. Existing claims can be drafted now. A stronger transport, component, uncertainty or efficiency claim requires its own evidence, not an automatic expansion of this study.

[Reading PDF](../manuscript/conference_draft_v15_2026-11-05/paper.pdf) · [LaTeX ZIP](../manuscript/conference_draft_v15_2026-11-05/overleaf_v15.zip) · [Editorial decisions](../work/{R.name}/EDITORIAL_DECISIONS_ZH.md) · [Exposure registry](DATASET_EXPOSURE_REGISTRY.md).

Public synchronization is recorded separately in this unit's PUBLIC_SYNC_RECEIPT.json after remote verification. Patient-level data, third-party originals and credentials remain local. Do not revive closed experimental plans or retune exposed references from old documents.
''')
state=dict(status='complete_editorial_refinement',date='2026-11-05',draft_sha256=sha(new),pdf_sha256=sha(B/'paper.pdf'),pages=pages,
 main_figures=4,supplementary_figures=4,main_tables=1,supplementary_tables=6,references=28,
 new_generations=0,new_patient_reads_or_fits=0,frozen_experiments_modified=False,
 decision='Proceed to scientific author review and venue-specific preparation; existing experiments remain frozen.',
 public_sync='Recorded separately after verified update in PUBLIC_SYNC_RECEIPT.json')
write(R/'STATE.json',json.dumps(state,indent=2)+'\n')
print(json.dumps(dict(status='PACKAGED',pages=pages,zip_members=len(members),pdf_sha256=sha(B/'paper.pdf'))))
