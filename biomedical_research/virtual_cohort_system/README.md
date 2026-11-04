# Evidence-guided virtual biomedical data

**Current manuscript: [v0.8](manuscript/DRAFT_v0_8.md), 3 November 2026.**

A scientific Agent turns qualified biomedical evidence, a population description, optional observations and a requested analysis into virtual data. The Agent chooses the joint model and parameters; numerical tools sample and inspect it. Complete-cohort generation without participant inputs is central.

## Paper and evidence

- [Full manuscript](manuscript/DRAFT_v0_8.md), [story and contributions](manuscript/STORY_AND_CONTRIBUTIONS_v07_2026-11-03.md), and [complete evidence ledger](manuscript/INTEGRATED_EVIDENCE_LEDGER_v07_2026-11-03.md).
- [Four main figures and Figure S1](manuscript/integrated_figures_v07_2026-11-03/FIGURE_PLAN.md), with [captions](manuscript/integrated_figures_v07_2026-11-03/CAPTIONS.md).
- [Aggregate reproduction guide](docs/REPRODUCING_MANUSCRIPT_v07.md).
- [Current focus](docs/CURRENT_RESEARCH_FOCUS.md), [focused experiment gaps](manuscript/KEY_EXPERIMENT_GAPS_v07_2026-11-03.md), and [existing-reference feasibility audit](manuscript/EXISTING_REFERENCE_FEASIBILITY_v07_2026-11-03.md).

- [v0.8 independent writing review](manuscript/REVIEW_v0_8_2026-11-03.md), [venue preparation](manuscript/VENUE_AND_SUBMISSION_PLAN_v08_2026-11-03.md), and [Author Summary / submission text](manuscript/SUBMISSION_TEXT_v08_2026-11-03.md).

## Completed experiments

| Setting | Executed work | Interpretation |
|---|---|---|
| External evidence: CHNS and ENSANUT | 20 Agent and four statistical constructions; 72 final 3,000-row tables; six focal regression endpoints | Added relationship evidence lowered five discrepancies and increased CHNS BMI discrepancy. Exposed developmental references. |
| Target-summary access: separate CHNS L/R | Six Agent constructions; 42 executions, 24 distinct tables overall and 18 distinct delivery tables | Closer reconstruction of several supplied summaries. Initial/final deliveries identical; no additional-stage revision gain. |
| Published longitudinal model: HRS | One Agent and one reconstructed published-law model; six valid tables, each 11,509 virtual subjects at four visits; nine physical generations include three invalid initial comparator attempts | Native longitudinal analysis and source-model reconstruction. Weak upper-threshold interaction and upper-HbA1c spread remain imperfect. No HRS participant records used. |

These are separate information settings. Virtual rows, seed draws, authors and clinical references are different units. The evidence ledger retains historical enrichment/direct-output uses and failed studies. Revealed targets remain closed to tuning and renewed confirmation.

## Method and implementation

1. Define the scientific use, population and allowed information.
2. Preserve study population, measurement, operator, estimate, uncertainty and provenance.
3. Let the Agent choose the generator and declare joint/transfer assumptions.
4. Execute versioned candidates and supply permitted source feedback; record revision or retention.
5. Apply the scientific analyses and interpret agreement according to the information supplied.

Different requests may receive different generators. Multiple Agents, model training and universal superiority over a customized statistical generator are not requirements. Principal experiments use curated evidence and Agent-authored programs. Historical direct table authorship is reported separately; general autonomous extraction and missing-cell completion are not established by these principal studies.

Implementation references: [generation skill](skills/evidence-cohort-generation/SKILL.md), [execution adapter](docs/EXECUTION_ADAPTER.md), and [source replay](docs/SOURCE_REPLAY.md). Individual records identify their actual interface versions. Source-statistic consistency does not certify extraction, transport or analytical usefulness.

## Reproduction and access

The [public reproduction entry point](docs/REPRODUCING_MANUSCRIPT_v07.md) verifies pinned aggregate inputs, reconstructs numerical tables, redraws Figures 2-4/S1 and copies Figure 1 as a schematic. It does not run an LLM, generate participant-like records or refit clinical data.

Participant-level real/generated files, third-party full articles/codebooks and credentials are excluded from the public export. Clinical reruns require lawful dataset access and the case-specific environment. Repository availability does not replace those conditions.

## Status and history

The empirical versions and v0.7 source draft remain unchanged. v0.8 revises the scientific framing and interpretation, with identical tables, Results, captions and bibliography. Its independent review links those unchanged displays to the versioned v0.7 reproduction package. The metadata-only audit admits no new independent reference; no extra clinical experiment is launched. Author/funding/access/ethics/AI-use declarations, article-type selection and publication-layout inspection remain. The optional prospective extension is not a prerequisite for the bounded construction/reconstruction claim.

Earlier implementation/progress notes remain in the [previous README](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/bec2041d1816432dd744cf875c649e9ea6142e67/biomedical_research/virtual_cohort_system/README.md). They describe their original dates. Frozen protocols, adverse results and disclosure history remain in the [exposure registry](docs/DATASET_EXPOSURE_REGISTRY.md) and linked records.
