"""Publish local reading pointers only after hash-bound review and build QA."""
from pathlib import Path
import hashlib
import json

U = Path(__file__).resolve().parent
P = U.parents[1]
B = P / 'manuscript/methods_draft_v28_2026-11-10'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
qa = json.loads((B / 'BUILD_QA.json').read_text(encoding='utf-8'))
review = json.loads((U / 'INDEPENDENT_REVIEW.json').read_text(encoding='utf-8'))
draft_sha = sha(P / 'manuscript/DRAFT_v0_28.md')
assert qa['status'] == 'PASS_PACKAGE_AND_STANDALONE_BUILD'
assert 'visually inspected' in qa['visual_review'].lower()
assert review['status'] == 'content_pass' and not review['mandatory_fixes']
assert draft_sha == qa['markdown_sha256'] == review['audited_draft_sha256']

manuscript_readme = P / 'manuscript/README.md'
old = manuscript_readme.read_text(encoding='utf-8')
history = old.split('## Preserved history', 1)[1]
current = '''# Manuscript

**Methods draft [v0.28](DRAFT_v0_28.md), 10 November 2026.**

[Reading PDF](methods_draft_v28_2026-11-10/paper.pdf) · [Overleaf ZIP](methods_draft_v28_2026-11-10/overleaf_v28.zip) · [Editable manuscript](DRAFT_v0_28.md) · [Build QA](methods_draft_v28_2026-11-10/BUILD_QA.json) · [Independent content review](../work/manuscript_revision_v28_2026-11-10/INDEPENDENT_REVIEW.md)

The paper asks whether a scientific Agent can turn fragmented biomedical evidence and a research request into an executable joint model and analyzable virtual records. v0.28 integrates the completed PNS blood-pressure task and a retrospective audit of thirty constructions. The audit distinguishes published statistics, adopted parameters, complete-model implications, finite generated estimates and measured references. It explains selected model choices without asserting a calibrated provenance-to-accuracy rule. All unfavorable comparisons and exposure qualifications remain.

| Main figure | What it shows |
|---|---|
| 1. Scientific Agent workflow | The author chooses a model; tools execute and inspect it; final data go to analysis. The loop is a capability, not a demonstrated quality benefit. |
| 2. One concrete construction | Iron evidence becomes paired hemoglobin/ferritin records with explicit assumptions. |
| 3. Complete-cohort analytical utility | All six requested glycemia analyses from four authors and twelve tables, including magnitude mismatches. |
| 4. Relationship evidence | Five of six information contrasts improve; all statistical comparator results remain. |
| 5. Iron-status analyses | Threshold and continuous uses differ on the same records. |
| 6. Glycemia and lipids | Complete cross-task results and unresolved joint relationships. |
| 7. Attribution | Model choices explain selected generated odds ratios and residual dependence; reference agreement remains analysis-specific. |
| 8. Paired blood pressure | All five authors and fifteen draws: SBP slopes are closer to the sample reference, while DBP slopes are higher and residual dependence lower. |

The reading PDF has 20 main pages and 48 total pages, with 13 figures and 16 tables. The ZIP compiles independently with matching text and links; final visual inspection is recorded in Build QA. The original 11 figures, 38 references and 15 table blocks are preserved, with PNS rows added to Tables 4 and 5. S18 adds complete PNS details and S19 the attribution scope. This is a local editable reading/development package, not an online Overleaf project or a submission-format certification.

[Revision results](../work/manuscript_revision_v28_2026-11-10/RESULTS.md) · [Attribution master](../work/parameter_attribution_2026-11-10/ATTRIBUTION_MASTER.md) · [Cross-provider pilot protocol](../work/manuscript_revision_v28_2026-11-10/CROSS_MODEL_PILOT.md). The twelve-slot pilot has not launched. This revision did not generate new clinical tables or refit revealed targets. Author details, biomedical applicability review and venue-specific formatting remain pending.

The [method coverage](../work/manuscript_focus_v26_2026-11-09/METHOD_COVERAGE.md) and [reproducibility guide](../work/manuscript_revision_v27_2026-11-09/REPRODUCIBILITY_GUIDE.md) retain the distinctions between historical controllers, executable-program replay and original Agent-session reproduction.

## Preserved history

- [v0.27](DRAFT_v0_27.md), [reading PDF](methods_draft_v27_2026-11-09/paper.pdf), [Overleaf ZIP](methods_draft_v27_2026-11-09/overleaf_v27.zip) and [review response](../work/manuscript_revision_v27_2026-11-09/REVIEW_RESPONSE.md).
'''
if '[v0.27](DRAFT_v0_27.md)' in history:
    history = history.split('\n', 2)[-1] if history.startswith('\n\n- [v0.27]') else history
manuscript_readme.write_text(current + history, encoding='utf-8')

for path, prefix in [(P / 'README.md', ''), (P / 'docs/CURRENT_RESEARCH_FOCUS.md', '../')]:
    text = path.read_text(encoding='utf-8')
    title, rest = text.split('\n', 1)
    end_anchor = '**Scientific-use development, 9 November' if path.name == 'README.md' else 'The core remains evidence-guided'
    assert end_anchor in rest
    rest = rest[rest.index(end_anchor):]
    intro = f'''

**Methods paper v0.28, 10 November 2026.** [Reading PDF]({prefix}manuscript/methods_draft_v28_2026-11-10/paper.pdf) · [Editable manuscript]({prefix}manuscript/DRAFT_v0_28.md) · [Overleaf ZIP]({prefix}manuscript/methods_draft_v28_2026-11-10/overleaf_v28.zip) · [Content review]({prefix}work/manuscript_revision_v28_2026-11-10/INDEPENDENT_REVIEW.md).

The revision integrates the completed paired blood-pressure validation and retrospective model-to-analysis attribution. It retains the core scientific-agent construction task, selected analysis agreements and all adverse outcomes. Five PNS authors generated fifteen sealed cohorts before the three reference analyses were revealed; the release family was already exposed. SBP slopes were 3.081-4.276 versus 3.524 mmHg per 5 kg/m², DBP slopes 2.886-3.691 versus 2.260, and adjusted residual correlations 0.466-0.646 versus 0.717. These are sample-reference comparisons, not known population truths.

The [attribution audit]({prefix}work/parameter_attribution_2026-11-10/ATTRIBUTION_MASTER.md) covers thirty constructions and 96 records, comprising 90 requested analyses and six dispersion diagnostics. Numerical full-model implications are available for seven requested analyses and six diagnostics; 83 requested implications remain uncomputed. Provenance is descriptive, not a validated accuracy ranking. The new two figures separate modeled consequences from clinical-reference agreement. Existing titles, frozen models, results and negative findings are retained.

The final PDF has 20 main pages and 48 total, with 13 figures and 16 tables. Independent content checks, standalone ZIP compilation and visual review passed within their stated scope. [Build QA]({prefix}manuscript/methods_draft_v28_2026-11-10/BUILD_QA.json) · [Revision results]({prefix}work/manuscript_revision_v28_2026-11-10/RESULTS.md) · [Preserved versions]({prefix}manuscript/README.md).

**Next bounded experiment: protocol only.** A [cross-provider pilot]({prefix}work/manuscript_revision_v28_2026-11-10/CROSS_MODEL_PILOT.md) specifies two existing evidence packets, three distinct model-provider families and two fresh contexts per cell (12 constructions). It will characterize choices for unreported relationships; it is not a new clinical confirmation. Exact available models, blinded delivery payloads and launch records must be verified before execution. No pilot model calls or new clinical experiments were performed for v0.28.

'''
    path.write_text(title + intro + rest, encoding='utf-8')

state = {
    'date': '2026-11-10',
    'status': 'completed_local_manuscript_and_protocol',
    'scope': 'Integrate completed PNS and retrospective attribution; no new clinical experiment',
    'draft_sha256': draft_sha,
    'pdf_sha256': qa['pdf_sha256'],
    'zip_sha256': qa['zip_sha256'],
    'main_pages': qa['main_pages'], 'total_pages': qa['total_pages'],
    'main_figures': 8, 'supplement_figures': 5, 'tables': 16,
    'content_review': review['status'],
    'build_review': qa['status'], 'visual_review_complete': True,
    'new_generated_patient_tables': 0, 'new_target_fits': 0,
    'new_model_provider_calls': 0, 'new_dataset_downloads': 0,
    'pilot_status': 'protocol_only_not_launched',
    'pilot_planned_constructions': 12,
    'github_sync_this_unit': False,
    'next': 'Stage and independently inspect identical case payloads, verify actual provider/model access, then execute the bounded cross-provider pilot without target feedback.'
}
(U / 'STATE.json').write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
(U / 'RESULTS.md').write_text('''# v0.28 integration and bounded next experiment

Completed locally on 10 November 2026. This is an editorial/attribution integration, not a new clinical experiment.

## Delivered

- [Manuscript v0.28](../../manuscript/DRAFT_v0_28.md), [48-page reading PDF](../../manuscript/methods_draft_v28_2026-11-10/paper.pdf), and [independently compiled Overleaf ZIP](../../manuscript/methods_draft_v28_2026-11-10/overleaf_v28.zip).
- Completed PNS validation integrated in main results and S18, with all five authors, fifteen draws, reference uncertainty and exposure limits.
- Thirty-construction attribution integrated in Methods, Results and S19; 90 requested-analysis entries plus six dispersion entries are audit records, not 96 independent experiments.
- Two new vector figures: model implications versus sampled analyses; complete blood-pressure comparisons. All eleven older figure assets remain unchanged.
- [Twelve-slot cross-provider protocol](CROSS_MODEL_PILOT.md), not launched. It does not presume that fresh host contexts are different model families.

## What the integration supports

The Agent can author an executable joint model from incomplete published evidence and make the completion assumptions inspectable. Particular model operations can explain particular scientific results: the iron independent-redraw step changes the model odds ratio, and lipid L03's weak residual dependence is already implied by its joint law. Target agreement remains analysis-specific. The PNS task adds whole-cohort evidence and a clear coexistence of closer SBP slopes, higher DBP slopes and lower residual dependence.

The audit does not show that all errors are transport errors, all variances contract, or provenance categories predict accuracy. The Q2 ENSANUT counterexample concerns the age/sex-adjusted BMI coefficient before additional glucose adjustment. Unknown exact historical model identities remain unknown; same-host author consistency is not cross-provider confirmation. Source checks that could not execute are not counted as successful checks.

## Verification and corrections

[Independent content review](INDEPENDENT_REVIEW.md) checks aggregate values, estimands, original source records and preservation. All 38 existing references and eleven figures remain; thirteen old table blocks are byte-equivalent, while Tables 4 and 5 only receive PNS rows. One new table provides all PNS author medians. Three clarifications from review were applied and rechecked against the final source hash. Review independence is limited by the reviewer having contributed to the prior PNS attribution audit; this is not independent patient-level validation.

[Build QA](../../manuscript/methods_draft_v28_2026-11-10/BUILD_QA.json) verifies 13 figures, 16 tables, unchanged v0.27, matching standalone ZIP text/links, and no overfull or missing-character errors. Final visual checks covered all contact sheets and the new results pages. A one-line near-empty page was fixed by removing a forced supplement break. Final length is 20 main pages and 48 total. This is a reading edition; author/declaration details and target-venue formatting remain pending.

## Cost and next decision

No new patient-level or generated rows were read, no scientific generator executed, no target analysis refitted, no new data downloaded, and no paid API or model-provider session launched. Work consisted of existing-aggregate plotting, document integration, compilation and review.

The next bounded unit is to stage two identical fixed case payloads and verify actual provider/model identities and transcript capture, then run 12 fresh constructions under the protocol. These are historical exposed cases used for developmental comparison, not new independent clinical validation. No new agent architecture or large-scale campaign is justified by this manuscript revision alone. Public GitHub synchronization has not occurred in this unit.
''', encoding='utf-8')
print(json.dumps(state))
