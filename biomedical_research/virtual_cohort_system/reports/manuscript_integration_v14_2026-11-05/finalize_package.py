"""Bind reviews, package the locally compiled reading copy and update navigation."""
from pathlib import Path
import hashlib,json,re,zipfile
import fitz

R=Path(__file__).resolve().parent;P=R.parents[1];M=P/'manuscript'
B=M/'conference_draft_v14_2026-11-05';UNIT=R.name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,t:p.write_text(t,encoding='utf-8',newline='\n')
old=M/'DRAFT_v0_13_1.md';new=M/'DRAFT_v0_14.md'
oldtext=old.read_text(encoding='utf-8');text=new.read_text(encoding='utf-8')
for number in (2,3):
    pat=rf'\*\*Table {number}\.([\s\S]*?)(?=\n\n!\[)'
    assert re.search(pat,oldtext).group()==re.search(pat,text).group()
review=json.loads((R/'INDEPENDENT_DRAFT_REVIEW.json').read_text())
assert review.get('status')=='PASS',review.get('status')
assert review['artifact']['sha256']==sha(new)
visual=json.loads((R/'FINAL_PDF_REVIEW.json').read_text())
assert visual.get('decision')=='PASS_FOR_READING_COPY',visual.get('decision')
assert visual['pdf']['sha256']==sha(B/'paper.pdf')
assert visual['tex']['sha256']==sha(B/'paper.tex')
build=json.loads((B/'BUILD_INPUTS.json').read_text())
assert build['source_sha256']==sha(new) and build['source_tex_sha256']==sha(B/'paper.tex')
doc=fitz.open(B/'paper.pdf');pages=len(doc)
page_map=[{'page':i+1,'characters':len(pg.get_text()),
           'figures':[s for s in pg.get_text().splitlines() if s.startswith('Figure ')],
           'tables':[s for s in pg.get_text().splitlines() if s.startswith('Table ')]} for i,pg in enumerate(doc)]
write(R/'PDF_PAGE_MAP.json',json.dumps(page_map,indent=2)+'\n')
members={n:B/n for n in ['paper.tex','paper.pdf','BUILD_INPUTS.json','build_reading_copy.py']}
members['README.md']=B/'OVERLEAF_README.md'
members.update({'figures/'+f.name:f for f in sorted((B/'figures').glob('*.pdf'))})
assert len(members)==13
with zipfile.ZipFile(B/'overleaf_v14.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
    for name,path in members.items():
        item=zipfile.ZipInfo(name,date_time=(2026,11,5,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(item,path.read_bytes())
with zipfile.ZipFile(B/'overleaf_v14.zip') as z:
    assert set(z.namelist())==set(members)
    assert all(z.read(n)==p.read_bytes() for n,p in members.items())
write(R/'PACKAGE_INVENTORY.json',json.dumps(dict(zip_sha256=sha(B/'overleaf_v14.zip'),
    members=[dict(path=n,sha256=sha(p),bytes=p.stat().st_size) for n,p in members.items()],verified=True),indent=2)+'\n')
write(R/'DRAFT_INTEGRATION_AUDIT.json',json.dumps(dict(input_draft_sha256=sha(old),new_draft_sha256=sha(new),
    original_tables_2_3_identical=True,figure_exports_preserved=24,new_generations=0,new_patient_reads_or_fits=0,
    frozen_experiments_modified=False,figures=8,tables=7,references=28,pages=pages,
    evidence_results_sha256=sha(P/'work/evidence_use_cross_task_2026-11-05/evaluation/RESULTS.json')),indent=2)+'\n')
navigation=f'''# Evidence-guided virtual biomedical data

**Current manuscript: [v0.14](manuscript/DRAFT_v0_14.md), 5 November 2026.**

**Evidence-Guided Agents for Analyzable Virtual Biomedical Cohorts**

[Reading PDF](manuscript/conference_draft_v14_2026-11-05/paper.pdf) · [Overleaf-ready ZIP](manuscript/conference_draft_v14_2026-11-05/overleaf_v14.zip) · [Figures](manuscript/paper_figures_v14_2026-11-05/README.md) · [Draft checklist](manuscript/KEY_EXPERIMENT_GAPS_v14_2026-11-05.md)

A scientific Agent turns published biomedical evidence, a population description, optional observations and intended analyses into a joint generating model and virtual data. Whole-cohort generation without individual construction records is central. The Agent chooses substantive structure and numerical evidence use; deterministic tools sample, inspect and analyze the result. Different research requests can receive different models.

## Completed scientific story

The paper combines an external-evidence information contrast, supplied-summary reconstruction, a published longitudinal model, repeated open retrieval, and a new glycemic/lipid cross-task study. These settings have different inputs and references and retain separate denominators. The contribution is an inspectable evidence-to-data workflow and demonstrated analysis-specific uses, not a new statistical family or universal superiority claim.

The [new cross-task experiment](work/evidence_use_cross_task_2026-11-05/RESULTS.md) contains six fresh Agent constructions, two requests and 18 final tables of 3,000 fictional rows. All 54 primary point directions agreed with the corresponding sample estimates, but effect magnitudes, residual dependence and dispersion differed. The TC slope reference interval crosses zero. All 513 aggregate outputs were independently recomputed; 324 matched cached references and 189 were generated-only diagnostics. These references were already exposed in development.

All six authors retained their initial laws. The 132 source checks were unavailable under their declared definitions, so numerical source-replay or feedback-driven improvement is not established. The data support transparent, assumption-dependent relationship exploration and analysis-workflow inspection; quantitative replacement of a measured target cohort remains unsupported. All six constructions and unfavorable results remain visible.

## Read, inspect and reproduce

- [Manuscript history and reviews](manuscript/README.md)
- [Story and figure roles](work/{UNIT}/STORY_AND_FIGURE_PLAN.md)
- [New Figure 6: scientific analyses](manuscript/paper_figures_v14_2026-11-05/fig6-cross-task.svg) and [Figure 7: dispersion](manuscript/paper_figures_v14_2026-11-05/fig7-dispersion.svg)
- [Evidence-use implementation](cohort_harness/evidence_use_v1.py) and [design](docs/EVIDENCE_USE_V1.md)
- [Portable aggregate plotting](manuscript/paper_figures_v14_2026-11-05/render_cross_task_aggregates.py): both new PNGs were reproduced pixel-for-pixel without participant or generated-row access.
- [Exposure registry](docs/DATASET_EXPOSURE_REGISTRY.md) and [public release scope](work/{UNIT}/PUBLIC_SCOPE.md)

The {pages}-page generic reading copy contains seven main figures, one supplementary figure, three main tables, four supplementary tables and 28 references. Scientific author review, venue/length selection and author declarations remain. The ZIP is a local LaTeX package, not an uploaded Overleaf project or a submission.

Patient-level real/generated tables, third-party originals/codebooks and credentials remain local. Public plotting is portable; the historical construction controllers retain documented local layout/runtime/source-access requirements. This release did not rerun a generator, read participant rows, refit a clinical reference or retune an exposed target. [Current focus](docs/CURRENT_RESEARCH_FOCUS.md).
'''
write(P/'README.md',navigation)
write(R/'ROOT_README.md',re.sub(r'\]\((?!https?://)([^)]+)\)',lambda m:'](biomedical_research/virtual_cohort_system/'+m.group(1)+')',navigation))
write(M/'README.md',f'''# Manuscript

**Current edition: [v0.14](DRAFT_v0_14.md), 5 November 2026.**

[Reading PDF](conference_draft_v14_2026-11-05/paper.pdf) · [Overleaf-ready ZIP](conference_draft_v14_2026-11-05/overleaf_v14.zip) · [Figures](paper_figures_v14_2026-11-05/README.md) · [Draft checklist](KEY_EXPERIMENT_GAPS_v14_2026-11-05.md)

The paper centers on Agent-controlled translation of heterogeneous published evidence into joint generating laws and virtual data for scientific analysis. The new Q5 study extends the workflow to glycemic and lipid requests. Figures 6–7 and Tables S3–S4 retain all six constructions, all final draws and the mixed quantitative results. Historical numerical Tables 2–3 and original figure exports are preserved.

The {pages}-page generic reading copy contains seven main figures, one supplementary figure, three main tables, four supplementary tables and 28 references. The [independent content review](../work/{UNIT}/INDEPENDENT_DRAFT_REVIEW.md) and [actual PDF review](../work/{UNIT}/FINAL_PDF_REVIEW.md) bind this edition. The [story plan](../work/{UNIT}/STORY_AND_FIGURE_PLAN.md) explains each display's role. No experiment was rerun for integration.

The current evidence supports analysis-specific, assumption-dependent uses. This is a draft for scientific author review, not a claim of universal quantitative accuracy, revision benefit or fresh clinical confirmation. Venue-specific length/format and authorship, affiliations, funding, conflicts, ethics/access, AI-use and software licensing remain to be completed. The ZIP is locally packaged for LuaLaTeX/Overleaf; no online project or submission has been created.

## Preserved history

- [v0.13.1](DRAFT_v0_13_1.md) and its [reading copy](conference_draft_v13_1_2026-11-04/paper.pdf)
- [v0.13](DRAFT_v0_13.md), [v0.12](DRAFT_v0_12.md) and [historical findings](SUPPLEMENT_HISTORICAL_RESULTS_v05.md)
- [New complete experiment](../work/evidence_use_cross_task_2026-11-05/RESULTS.md) and [public scope](../work/{UNIT}/PUBLIC_SCOPE.md)
''')
write(P/'docs/CURRENT_RESEARCH_FOCUS.md',f'''# Current focus — evidence-guided virtual biomedical data

Updated 5 November 2026. **The six-constructor cross-task study is closed and integrated into [manuscript v0.14](../manuscript/DRAFT_v0_14.md).**

The core remains an Agent converting published evidence, a target-population description, optional observations and intended analyses into useful virtual data. Whole-cohort generation without individual inputs is included; ordinary Agents and task-specific generating laws are valid implementations.

The completed cross-task study produced 18 final tables for HbA1c and measured TC/HDL requests. All 54 primary point directions matched existing sample estimates. Quantitative effects, dispersion and lipid residual dependence remained mixed. All six laws were retained; source checks were unavailable, so no numerical feedback/revision gain is claimed. The 513 outputs were independently recomputed. Existing references stay developmental and exposed. No candidate is selected retrospectively as an overall winner.

The [reading PDF](../manuscript/conference_draft_v14_2026-11-05/paper.pdf) and [LaTeX package](../manuscript/conference_draft_v14_2026-11-05/overleaf_v14.zip) integrate these results with prior information-contrast, summary-reconstruction, longitudinal and retrieval experiments. Distinct information settings and denominators remain separate. The [draft checklist](../manuscript/KEY_EXPERIMENT_GAPS_v14_2026-11-05.md) states the claim-specific remaining evidence gaps.

## Next decision

Proceed with scientific author review of the integrated contribution, then select venue and edit length/format and declarations. A stronger quantitative new-population claim requires a new prospective protocol; a component-level mechanism claim needs a controlled contrast. Neither is launched automatically by this writing unit. Do not retune exposed references, multiply seeds to imply clinical replication or revive old pending experiments from historical plans.

[Content review](../work/{UNIT}/INDEPENDENT_DRAFT_REVIEW.md) · [PDF review](../work/{UNIT}/FINAL_PDF_REVIEW.md) · [Public scope](../work/{UNIT}/PUBLIC_SCOPE.md) · [Exposure registry](DATASET_EXPOSURE_REGISTRY.md).

No patient-level real/generated records or full third-party originals are public. GitHub synchronization is verified separately in this integration unit's local PUBLIC_SYNC_RECEIPT.json; an old experiment completion receipt is not edited to claim a later publication.
''')
scope=(R/'PUBLIC_SCOPE_DRAFT.md').read_text(encoding='utf-8')
scope=scope.replace('# Draft public scope for manuscript v0.14 and the completed cross-task experiment','# Public release scope: manuscript v0.14 and the completed cross-task experiment')
scope='''This release includes all 380 exact experiment/interface/code/provenance candidates, including complete optional session-chain and aggregate-feedback groups, plus the reviewed v0.14 manuscript package and navigation. It excludes all individual records and third-party originals. The final staged manifest and independent release review bind public bytes; this document alone is not a remote sync receipt.

'''+scope
write(R/'PUBLIC_SCOPE.md',scope)
state=dict(status='complete_manuscript_integration',date='2026-11-05',draft_sha256=sha(new),pdf_sha256=sha(B/'paper.pdf'),pages=pages,
           figures=8,tables=7,references=28,new_generations=0,new_patient_reads_or_fits=0,frozen_experiments_modified=False,
           decision='Proceed to scientific author review and venue-specific editing; retain analysis-specific empirical scope.',
           public_sync='Recorded separately after verified remote update in PUBLIC_SYNC_RECEIPT.json')
write(R/'STATE.json',json.dumps(state,indent=2)+'\n')
print(json.dumps(dict(status='PACKAGED',pages=pages,zip_members=len(members),pdf_sha256=sha(B/'paper.pdf'))))
