"""Finalize manuscript navigation and verify presentation artifacts only."""
from pathlib import Path
import hashlib
import json
import re

M=Path(__file__).resolve().parent
P=M.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
draft=M/'DRAFT_v0_7.md'
review=M/'REVIEW_v0_7_2026-11-03.json'
assert review.is_file(), 'Independent review must finish first'
assert sha(draft)=='63a3f705f86a93e0b07a3b8da08687bb0652822300e1169c29ce84b16721baf6'

(M/'README.md').write_text('''# Manuscript

**Current full manuscript: [v0.7](DRAFT_v0_7.md), 3 November 2026.** It integrates the completed CHNS/ENSANUT external-evidence study, the separate CHNS summary-assisted experiment and the HRS longitudinal public-model example. The central contribution is Agent construction of useful biomedical virtual data from qualified evidence and an intended scientific analysis. The three information settings retain separate protocols and interpretation.

- [Story, contributions and draft checklist](STORY_AND_CONTRIBUTIONS_v07_2026-11-03.md)
- [Four main figures, Figure S1 and numeric provenance](integrated_figures_v07_2026-11-03/FIGURE_PLAN.md)
- [Complete figure captions](integrated_figures_v07_2026-11-03/CAPTIONS.md)
- [Key experiment gaps](KEY_EXPERIMENT_GAPS_v07_2026-11-03.md): one prospective transfer case is the priority optional scientific extension; an extraction audit is needed only for an autonomy claim. Neither launches a new campaign.
- [Integrated evidence ledger](INTEGRATED_EVIDENCE_LEDGER_v07_2026-11-03.md): principal studies, historical enrichment/direct-output uses and retained failures, with distinct denominators.
- [Independent manuscript review](REVIEW_v0_7_2026-11-03.md) and [presentation/link check](PACKAGE_REVIEW_v07_2026-11-03.json)

The HRS example is now integrated, rather than pending. It supplies six valid comparison tables from one Agent-authored and one reconstructed published-law model; its three invalid initial comparator attempts and technical recovery remain disclosed. It tests source-model reconstruction, not new-patient validation. Historical references remain exposed and closed.

## Supporting records

- [Source-to-generator trace and assumptions](SUPPLEMENT_SOURCE_AND_ASSUMPTIONS_v05.md)
- [Historical developmental results](SUPPLEMENT_HISTORICAL_RESULTS_v05.md)
- [HRS detailed addendum](SUPPLEMENT_HRS_PUBLIC_EXAMPLE_2026-11-03.md)
- [Completed main-study results](../work/main_study_freeze_2026-11-03/RESULTS.md)
- [Completed information-provision results](../work/information_revision_ablation_2026-11-03/RESULTS.md)
- [Completed statistical supplement](../work/summary_comparator_2026-11-03/RESULTS.md)
- [Completed HRS results](../work/hrs_public_example_2026-11-03/RESULTS.md)
- [Existing primary-literature positioning](CORE_CONTRIBUTION_POSITIONING_2026-11-03.md): predecessor method facts remain relevant; its then-proposed HRS comparison is superseded by the completed record.

## Version and submission status

[v0.6](DRAFT_v0_6.md), [v0.5](DRAFT_v0_5.md) and earlier drafts remain unchanged. This revision adds writing and presentation artifacts only: no new generation, target fitting, reference analysis or scientific parameters. No universal statistical-superiority claim is required.

The manuscript is ready for substantive author review, not submission-certified. Remaining preparation includes a clean reproduction entry point, author/funding/access/ethics/AI-use declarations, final article-type formatting and inspection at the actual journal layout. Competitive publication depends on the substantive contribution; a completed draft and successful audits do not guarantee acceptance.
''',encoding='utf-8')

focus=P/'docs/CURRENT_RESEARCH_FOCUS.md'
text=focus.read_text(encoding='utf-8-sig')
notice='''**Current writing checkpoint — v0.7, 3 November 2026:** the [integrated manuscript](../manuscript/DRAFT_v0_7.md) now presents external-evidence developmental results, CHNS summary-assisted reconstruction and the completed HRS longitudinal public-model example as three distinct studies. Four main figures and one supplementary figure retain their original numeric sources. The [story and checklist](../manuscript/STORY_AND_CONTRIBUTIONS_v07_2026-11-03.md), [full evidence ledger](../manuscript/INTEGRATED_EVIDENCE_LEDGER_v07_2026-11-03.md) and [key-gap review](../manuscript/KEY_EXPERIMENT_GAPS_v07_2026-11-03.md) govern the next writing work. Existing results support a bounded construction/reconstruction paper; a prospective unexposed transfer case would strengthen external usefulness, and an extraction audit is relevant only to an autonomy claim. Neither is released here. Current effort is manuscript review, reproduction packaging and author/submission preparation; no revealed-target tuning or unrelated expansion. Earlier pending-HRS and manuscript-version statements below are historical.

'''
if notice not in text:
    heading,rest=text.split('\n',1)
    focus.write_text(heading+'\n\n'+notice+rest.lstrip(),encoding='utf-8')

archive=P/'work/research_focus_2026-11-01/CURRENT_RESEARCH_FOCUS_before_v07.md'
if not archive.exists():archive.write_bytes(focus.read_bytes())
focus.write_text('''# Current research focus: useful evidence-guided virtual biomedical data

3 November 2026. The current full draft is [manuscript v0.7](../manuscript/DRAFT_v0_7.md). Its [story and checklist](../manuscript/STORY_AND_CONTRIBUTIONS_v07_2026-11-03.md), [evidence ledger](../manuscript/INTEGRATED_EVIDENCE_LEDGER_v07_2026-11-03.md), [figure plan](../manuscript/integrated_figures_v07_2026-11-03/FIGURE_PLAN.md) and [focused experiment gaps](../manuscript/KEY_EXPERIMENT_GAPS_v07_2026-11-03.md) are the active writing references.

The core purpose is to turn published biomedical evidence, a population description, optional observed variables and an intended analysis into virtual data with useful scientific properties. The Agent chooses scientific structure and numerical parameters; programmatic sampling and directly authored tables are permitted implementations. Complete-cohort generation remains central, with historical enrichment results reported separately. Ordinary Agents are valid; training, multiple Agents and universal superiority over a bespoke statistical generator are not requirements.

## Completed evidence

- [External-evidence main study](../work/main_study_freeze_2026-11-03/RESULTS.md): two exposed development references, 20 Agent plus four statistical constructions, 72 final tables; five of six discrepancy contrasts improved and CHNS BMI worsened.
- [CHNS information-provision study](../work/information_revision_ablation_2026-11-03/RESULTS.md): six Agents; accessible target summaries support closer reconstruction; no additional-stage revision gain. Different protocol and source packet from the main study.
- [Statistical calibration supplement](../work/summary_comparator_2026-11-03/RESULTS.md): three final tables from one purpose-built family, retained as a descriptive reference.
- [HRS public-model reconstruction](../work/hrs_public_example_2026-11-03/RESULTS.md): six valid longitudinal tables from two constructions; nine physical generations include three invalid initial comparator tables and a separately reviewed parser repair. Source coefficients were provided; no HRS participant records were accessed. This resolves the earlier pending public-method-example task.

All these units are closed. The integrated ledger also retains earlier enrichment, direct-output, failed transport, infinite-moment and revision-trade-off results. Synthetic rows, seed draws, authors and clinical references are different units and are not pooled as a single validation count.

## Current next actions

1. Complete substantive manuscript review, reproducible entry points and author/access/ethics/AI-use declarations.
2. Select the article type and inspect the manuscript and figures at the actual publication layout.
3. If strengthening the empirical claim is necessary, prioritize one prospectively selected project-unexposed reference from already accessible data, under a new bounded protocol. An original-document extraction audit is relevant only for an autonomous evidence-processing claim. Neither study is released by this writing checkpoint.

The HRS example supports reconstruction; CHNS/ENSANUT support developmental, analysis-specific comparisons. Current support for a bounded method paper does not guarantee competitive publication. Known targets may not be retuned or renamed as new confirmation. No new cohort search, generation, fitting, training, HPC or paid API call is authorized by this consolidation.

## Historical record

Earlier prospective and completed checkpoints remain in their original documents and experiment records. The prior long-form focus note is preserved in [repository history at b24bd8e](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/b24bd8e87b57bb0f41741690cdf14b372bfaae47/biomedical_research/virtual_cohort_system/docs/CURRENT_RESEARCH_FOCUS.md). Its pending/zero-execution statements describe their original dates, not the current state. No frozen protocol, result, exposure record or receipt was changed by this current-state summary.
''',encoding='utf-8')
probe=P/'work/research_focus_2026-11-01/v07_export_probe/EXPORT_LAYOUT_PROBE.json'
assert json.loads(probe.read_text())['status']=='pass'
(M/'FIGURE_EXPORT_LAYOUT_REVIEW_v07_2026-11-03.json').write_bytes(probe.read_bytes())

story=M/'STORY_AND_CONTRIBUTIONS_v07_2026-11-03.md'
s=story.read_text();s=s.replace('- [ ] Resolve the independent v0.7 writing/figure checks against the delivered files.','- [x] Resolve the independent v0.7 writing/figure checks against the delivered files (native-size figure review; journal-layout check remains).')
story.write_text(s,encoding='utf-8')

files=[draft,M/'README.md',story,M/'KEY_EXPERIMENT_GAPS_v07_2026-11-03.md',M/'INTEGRATED_EVIDENCE_LEDGER_v07_2026-11-03.md',M/'REVIEW_v0_7_2026-11-03.md',M/'integrated_figures_v07_2026-11-03/FIGURE_PLAN.md',M/'integrated_figures_v07_2026-11-03/CAPTIONS.md']
checked=[];missing=[]
for path in files:
    for match in re.finditer(r'!?\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8-sig')):
        target=match.group(1).split('#')[0]
        if not target or re.match(r'https?://|mailto:',target): continue
        dest=(path.parent/target).resolve()
        if dest.name=='PACKAGE_REVIEW_v07_2026-11-03.json': continue
        checked.append({'file':path.name,'target':target,'exists':dest.is_file()})
        if not dest.is_file():missing.append(checked[-1])
assert not missing,missing
fm=json.loads((M/'integrated_figures_v07_2026-11-03/NUMERIC_MANIFEST.json').read_text())
for rel,binding in fm['outputs'].items():
    f=M/'integrated_figures_v07_2026-11-03'/rel
    assert sha(f)==binding['sha256'],rel
payload={'status':'pass','scope':'Writing, existing-asset integrity, local navigation and native-size visual check; no scientific reruns.',
 'draft_sha256':sha(draft),'independent_review_sha256':sha(review),'numeric_manifest_sha256':sha(M/'integrated_figures_v07_2026-11-03/NUMERIC_MANIFEST.json'),
 'local_links_checked':len(checked),'broken_links':missing,'main_figures':4,'supplementary_figures':1,'main_tables':4,
 'figure_export_layout_probe_sha256':sha(probe),'public_figure_rebuild':'pass; 10 figures and 5 aggregate payloads match local bytes; two exact reversible CRLF/LF export mappings documented',
 'root_visual_inspection':{'files':['fig1_method.png','fig2_external_evidence.png','fig3_summary_assisted.png','fig4_longitudinal.png','figS1_longitudinal_all_effects.png'],'native_size':'labels and panels present; no visible clipping','journal_layout':'not yet selected or rendered'},
 'preserved':'All original studies, failed experiments, target exposure and frozen numerical outputs unchanged.',
 'new_generations':0,'new_fits':0,'patient_rows_read':0,'new_experiment_release':False,
 'remaining':['Clean reproduction entry point','Author/funding/access/ethics/AI-use declarations','Article-type format and final rendered-layout check'],
 'links':checked}
(M/'PACKAGE_REVIEW_v07_2026-11-03.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in payload.items() if k!='links'},indent=2))
