"""Publish local navigation after independent content, figure and visual review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
BUILD = PROJECT / 'manuscript/methods_draft_v30_2026-11-11'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    qa = json.loads((BUILD / 'BUILD_QA.json').read_text(encoding='utf8'))
    assert qa['status'] == 'PASS_PACKAGE_AND_STANDALONE_BUILD'
    assert qa['visual_review'].startswith('PASS'), 'Final visual review is pending.'
    facts = json.loads((HERE / 'REVISION_FACTS.json').read_text(encoding='utf8'))
    for path, expected in facts['preserved_inputs'].items():
        assert sha(PROJECT / path) == expected, path
    for name in ('EDITORIAL_CHANGES.md', 'CLAIM_EVIDENCE_MAP.md', 'KEY_EXPERIMENT_GAPS.md',
                 'VISUAL_REVIEW.md'):
        assert (HERE / name).is_file(), name
    assert (HERE / 'review/FINAL_CONTENT_REVIEW.md').is_file(), 'Independent content review missing.'
    content_review = json.loads((HERE / 'review/FINAL_CONTENT_REVIEW.json').read_text(encoding='utf8'))
    assert content_review['status'] == 'pass', 'Independent content review did not pass.'
    readme_path = PROJECT / 'manuscript/README.md'
    focus_path = PROJECT / 'docs/CURRENT_RESEARCH_FOCUS.md'
    for name, path in [('README_before_v30.md', readme_path), ('CURRENT_FOCUS_before_v30.md', focus_path)]:
        snapshot = HERE / name
        if not snapshot.exists():
            snapshot.write_bytes(path.read_bytes())
    old_readme = (HERE / 'README_before_v30.md').read_text(encoding='utf8')
    history = old_readme.split('## Preserved history', 1)[1]
    readme = '''# Manuscript

**Integrated methods working draft v0.30, 11 November 2026.**

[Reading PDF](methods_draft_v30_2026-11-11/paper.pdf) · [Overleaf ZIP](methods_draft_v30_2026-11-11/overleaf_v30.zip) · [Editable manuscript](DRAFT_v0_30.md) · [Build QA](methods_draft_v30_2026-11-11/BUILD_QA.json)

The paper remains about a scientific Agent turning research needs and incomplete published evidence into virtual biomedical data for specified analyses. The latest integration foregrounds the twelve fresh autonomous constructions, then reports the separate quality-assurance review of those same laws. Evidence applicability is part of the source-use audit, not a new paper topic or launched experiment.

The repeated study has twelve initial constructors and 36 final tables in two contexts. The later study has 24 dependent review sessions and 72 final tables; these are not 24 additional independent constructors. Ordinary and workflow Agents both generated analyzable records. Analytical agreement varies by endpoint, and the completed checks repaired specific defects without establishing a general quality gain. All unfavorable profiles and unchanged outputs remain included.

Figure 5 now shows every repeated constructor and all six primary analyses using blue/purple policies and an orange sample reference. Figures S6-S7 show the complete paired-review profiles and changes. Other historical figures and results are retained. Table S16 corrects one DBP SD transcription to 11.094; original calculations and v0.29 are unchanged.

The reading edition has 29 main pages and 69 total pages, 17 figures, 28 tables and 23 supplementary sections. Its standalone Overleaf package was independently compiled and checked for matching text and links; figures and affected numerical tables were independently reviewed, and all pages were contact-reviewed with detailed inspection of changed pages. It is an expanded working draft, not a venue-formatted submission or an online Overleaf project.

[Editorial changes](../work/manuscript_integration_v30_2026-11-11/EDITORIAL_CHANGES.md) · [Contribution/evidence map](../work/manuscript_integration_v30_2026-11-11/CLAIM_EVIDENCE_MAP.md) · [Remaining experiment decisions](../work/manuscript_integration_v30_2026-11-11/KEY_EXPERIMENT_GAPS.md) · [Independent review](../work/manuscript_integration_v30_2026-11-11/review/FINAL_CONTENT_REVIEW.md)

No new model calls, data generation or patient-reference fits were made for this integration. Recent artifacts have not been publicly synchronized in this unit. Author details, biomedical interpretation and venue-specific formatting remain to complete. No mechanism pilot, new dataset campaign or provider expansion is launched by this revision.

## Preserved history

- [v0.29](DRAFT_v0_29.md), [reading PDF](methods_draft_v29_2026-11-11/paper.pdf) and [Overleaf ZIP](methods_draft_v29_2026-11-11/overleaf_v29.zip). Superseded reading edition; its frozen content is unchanged.
'''+history
    readme_path.write_text(readme, encoding='utf8')
    old_focus = (HERE / 'CURRENT_FOCUS_before_v30.md').read_text(encoding='utf8')
    _, remainder = old_focus.split('\n', 1)
    remainder = remainder.replace(
        'Manuscript v0.29 remains preserved; the new text is not yet in its PDF or Overleaf archive.',
        'These results are now integrated into v0.30. The earlier v0.29 edition remains preserved.')
    remainder = remainder.replace(
        'Next priority is result integration and a bounded generic scientific-law audit design; no new paid sessions, model expansion, candidate repair or target acquisition starts automatically.',
        'The subsequent scientific-law audit and v0.30 integration are complete. No new paid expansion is launched by that integration.')
    focus = '''# Current focus — from published evidence to analyzable biomedical cohorts

## Current decision and completed integration v0.30 — 11 November 2026

The user reaffirmed the application mainline after the evidence-indirectness review: scientific Agents should construct useful virtual biomedical data from research requests, published evidence and optional observations. Do not pivot to an indirectness benchmark, presume its causal mechanism, or start the proposed 24/384-session studies. Applicability, mathematical and physiological checks serve the generation task. Ordinary Agent implementations remain valid; no blanket workflow-superiority claim is required.

The [v0.30 reading draft](../manuscript/methods_draft_v30_2026-11-11/paper.pdf), [editable source](../manuscript/DRAFT_v0_30.md) and [Overleaf package](../manuscript/methods_draft_v30_2026-11-11/overleaf_v30.zip) now integrate the completed twelve-constructor autonomous study and its 24 dependent scientific-review sessions. Figure 5 displays all primary construction results; S22-S23 retain complete profiles and review outcomes. Main story: research request → Agent-selected evidence and joint model → analyzable virtual records → inspectable scientific uses and assumptions. The new reading edition is 69 pages including supporting material, with independently checked numbers, standalone build and visual review.

The record supports autonomous construction and analysis-specific utility. Checks repaired one mathematical tail law and one rounding edge case; 66/72 paired-review outputs were unchanged, and changed scientific estimates were mixed. Those facts support quality-control tools, not a claimed universal review benefit. Final data and their scientific uses remain primary. Previously exposed references remain developmental.

Next use the integrated [claim/evidence map](../work/manuscript_integration_v30_2026-11-11/CLAIM_EVIDENCE_MAP.md) and [short gap decision](../work/manuscript_integration_v30_2026-11-11/KEY_EXPERIMENT_GAPS.md) to review biological interpretation and submission scope. Add an experiment only for a specific unresolved core claim. This unit ran no API calls, generators, patient fits or new data acquisition and did not synchronize public GitHub. The frozen experiments and old editions are unchanged.

## Earlier completed-unit records

The records below describe prior stages; the current decision above supersedes their now-completed integration tasks.
'''+remainder
    focus_path.write_text(focus, encoding='utf8')
    state = {
        'status': 'completed_independently_reviewed', 'updated_utc': datetime.now(timezone.utc).isoformat(),
        'manuscript_version': '0.30', 'mainline': 'Agent-generated biomedical data for scientific analyses',
        'new_api_calls': 0, 'new_generated_tables': 0, 'new_patient_analyses': 0, 'public_sync': False,
        'evidence_indirectness_pilot_launched': False,
        'main_pages': qa['main_pages'], 'total_pages': qa['total_pages'],
        'preserved_inputs_verified': len(facts['preserved_inputs']),
        'pdf_sha256': sha(BUILD / 'paper.pdf'), 'zip_sha256': sha(BUILD / 'overleaf_v30.zip'),
        'source_sha256': sha(PROJECT / 'manuscript/DRAFT_v0_30.md'),
        'independent_content_review': 'review/FINAL_CONTENT_REVIEW.md', 'visual_review': 'VISUAL_REVIEW.md',
        'next': 'Review biomedical interpretation and manuscript scope against the short gap decision; no automatic experiment expansion.'}
    (HERE / 'STATE.json').write_text(json.dumps(state, indent=2) + '\n', encoding='utf8')
    (HERE / 'RESULTS.md').write_text('''# Completed application-focused manuscript integration v0.30

Integrated existing studies into an editable manuscript, compiled reading PDF and independently compiled Overleaf ZIP. The new primary figure retains all twelve autonomous constructors and six requested analyses. A separate quality-assurance section retains all 24 dependent reviews, unchanged outputs and mixed scientific changes. Prior v0.29 assets and frozen experiment files were hash-verified unchanged.

No new model call, generation, patient analysis, data acquisition or public synchronization was performed. This is a completed editorial/reporting unit, not a new scientific experiment. The evidence-indirectness proposal was not launched or promoted to the main contribution.

See the editorial changes, claim/evidence map, short gap decision, independent content review and full visual review in this directory. Current files are linked from manuscript/README.md and docs/CURRENT_RESEARCH_FOCUS.md. Author metadata, biological interpretation and venue formatting remain pending.
''', encoding='utf8')
    print(json.dumps(state, indent=2))

if __name__ == '__main__':
    main()
