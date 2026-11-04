# LLMSynthor: story and figure lessons for our v0.10 draft

2026-11-04. This is a writing and presentation audit, not a new scientific experiment. It uses the PDF skill for visual reading. No patient/generated rows, model construction, analysis rerun or historical artifact modification occurred. Only this original note was written.

## Verified access and reading

- Current arXiv version is **v4, 8 June 2026**, according to its [version history](https://arxiv.org/abs/2505.14752). The [full HTML](https://arxiv.org/html/2505.14752v4) identifies the KDD 2026 proceedings and DOI [10.1145/3770855.3818965](https://doi.org/10.1145/3770855.3818965). The DOI endpoint itself was unavailable through the web reader; that is an access limitation, not a contradictory publication finding.
- The title appears in the official [KDD 2026 paper list](https://kdd2026.kdd.org/papers/), recovered by domain-restricted search. The direct static page extract exposes only its search controls, so the exact conference track is not needed for this recommendation.
- Read the v4 Introduction, Related Work, Methodology, Algorithm 1, all three experimental subsections, Discussion and Limitations in the primary HTML. This is not abstract-only reading.
- The web PDF reader rejected the large file. The [v4 PDF](https://arxiv.org/pdf/2505.14752v4) was subsequently read and rendered in memory: **12 pages; 18,843,425 bytes; SHA-256 `06bf4fe23f26c0410e38cdbe56762d81b1845499f3349ced553e2b4b18da7b03`**. Visually inspected PDF pages **2, 3, 4, 7, 8 and 9**, including Figures 1, 2, 6, 7 and 8 and Tables 1–6. Existing local v3 pages 7–8 were first inspected, but the style conclusions below were checked against v4. No new persistent PDF or third-party image copy was created.

## Concise primary-paper interpretation

LLMSynthor starts with an inaccessible-records problem and an available-aggregates opportunity. It identifies a tension between plausible individual records and global statistical alignment, then assigns the LLM a dependency-selection and proposal-planning role. A numerical sampler executes proposals; discrepancy feedback informs subsequent batches. Its experiments follow three questions: practical synthesis from limited summaries, quantitative fidelity, and variable-length population records. Figure 1 establishes the problem position; Figure 2 explains two method components. Later figures show application patterns, distributions, downstream performance and iteration behavior, with compact comparison tables. Pages 7–9 use restrained blue/purple fills, aligned small panels and short figure titles; the captions carry interpretation. The paper is therefore a useful model for question-driven evidence organization, rather than a reason to copy its superiority or iteration claims. These observations derive from the [v4 primary paper](https://arxiv.org/html/2505.14752v4).

## Our recommended story: one question, three technical responsibilities, four empirical questions

Our own central question should be stated before implementation details:

> Can an Agent turn fragmented biomedical evidence into virtual data that can actually be used for a specified scientific analysis, when construction records are unavailable?

The existing v0.9 already supports a concrete technical answer. Organize the method into three responsibilities, each demonstrated later:

1. **Preserve the meaning of evidence.** Population, measurement, units, adjustment and uncertainty accompany a statistic. This is why the same nominal relationship does not automatically have the same numerical use.
2. **Construct a joint model that makes the requested analysis possible.** The Agent chooses its law and uses evidence numerically, declaring the unreported dependence it supplies. The main-study separately adjusted projection example and latest copula conversion are actual worked examples.
3. **Produce and inspect an analyzable data product.** Numerical tools execute the law, expose the implied analyses and provide permitted feedback. Retain is a valid decision; the manuscript must not require revision improvement to explain a useful output.

The main text should answer four questions, using already completed results rather than starting four new experiments:

| Proposed empirical question | Existing evidence | Result to lead with | Evidence that stays alongside it |
|---|---|---|---|
| Q1. Can external evidence support requested biomedical analyses? | CHNS/ENSANUT main study | Complete data products; five of six information contrasts improve | All six endpoints, all authors/seeds and the CHNS BMI deterioration |
| Q2. What changes when more informative summaries are available? | Separate CHNS L/R study | Quantitative summary-assisted reconstruction | Provided target information, statistical supplement and unchanged additional-review stage |
| Q3. Can the procedure deliver a different data/analysis structure? | HRS public-model reconstruction | Complete longitudinal records analyzed with the original mixed model | Source-rich input identity, both interactions, all 16 effects and high-HbA1c spread |
| Q4. Can actual acquisition reach generation, and which analyses depend on missing evidence? | Open search → latest complete-cohort model, sensitivity and real-real context | One completed acquisition-to-data example; useful secondary BMI/age behavior | All seven terms, unsupported conditional dependence and remaining discrepancies |

This order gives each experiment a scientific purpose. The historical live integration can be shortened into the Q4 implementation context. Earlier enrichment, direct-output, tail failures and deployment details belong in the supplement with precise links. They should remain available without interrupting the main argument every few paragraphs.

## Changes to the actual draft

- **Introduction:** use roughly six connected paragraphs: biomedical data need; why published evidence cannot simply be concatenated; existing synthesis routes; our scientific model-author responsibility; concise contributions; preview of the four empirical questions. Keep complete-cohort generation central and optional observations visible.
- **Method:** define the input as a research request, target specification, qualified evidence and optional observations; define the output as a sampled data product plus model/evidence assumptions. Describe three responsibilities above. Put the two concrete transformations in a worked-example box. A short algorithm can show the actual procedure without implying automatic standalone deployment.
- **Experiments:** use a compact information/mode/reference table once, then the four question-led subsections. Avoid repeating the entire freeze/history narrative in each section. State developmental versus reconstruction status where it changes interpretation.
- **Results prose:** lead each paragraph with what the generated data enabled, then the relevant complete numerical evidence. Move detailed audit counts and artifact receipts to reproducibility material. These audit counts validate implementation; they are not the scientific novelty.
- **Discussion:** explain when this approach is useful, why a joint law provides reusable data, and which remaining dependence/transport assumptions matter. Consolidate limitations in one section rather than repeating every qualification in every caption and result paragraph.

The current contribution can be presented positively and specifically. It does not need a claim of first literature-to-data generation, a universal quality score, or superior performance against every statistical method. The word “Agent” should be substantiated by the observed scientific decisions and tool use.

## Figure recommendations for our own original artwork

These are proposed designs for our data, not reproductions of another paper's artwork.

| Our figure | Question it should answer | Concrete design |
|---|---|---|
| 1. Problem and scientific method | What input is missing, and what scientific work does the Agent perform? | Show an example request with optional observations, qualified paper evidence, a compact evidence-to-parameter example, the chosen joint law and the resulting analysis-ready table. Label actual Agent decisions and numerical execution. Use one optional inspect/retain/revise branch; do not advertise an unproved improving loop. |
| 2. External-evidence utility | What relationships survive synthesis, and how does relational information help? | Keep all six panels, native units, all constructors and seed summaries. Use the same semantic colors for E0, E1 and statistical references; do not color an entire panel as success/failure. |
| 3. Summary-assisted utility | What can accessible aggregate information support? | Keep the five prescribed analysis displays and separate L/R from the later statistical supplement. Mark supplied-summary reconstruction in a compact subtitle, not in repeated paragraph-sized banners. |
| 4. Longitudinal capability | Can generated records run a materially different scientific analysis? | Show both interactions with native labels; keep the complete 16-term display in the supplement. An inset may define the four-visit structure but must not fabricate trajectories. |
| 5. Acquisition and analysis dependence | What did actual retrieval enable, and where does a missing relation matter? | Preserve all seven new coefficients and the two genuine analytical sensitivity points. A short panel heading can state the missing BMI–glucose dependence. Put long uncertainty definitions in the caption; the real-real panel remains supplemental if the main figure becomes crowded. |

For a conference-style reading draft, standardize the five original figures to a shared column/full-width grid, font family, axis sizes, panel letters and evidence-role palette. Use short noun-phrase panel titles, a shared legend and minimal repeated explanatory text inside panels. Retain units and interval identities. Reduce decorative title banners and empty title space before shrinking data labels. At final size, an ordinary reader should be able to read the smallest tick label without zooming. These are our design targets; they are not measurements of the reference paper's exact typography.

Do not add iteration curves because a neighbor has them: our completed constructions mostly retained their laws. Do not add artificial pointwise predictions or raw scatterplots from summary-only examples. The relevant attractive result is the existing full scientific-analysis panel, not a fabricated visual of richer data.

## Important positioning boundary

LLMSynthor is a close LLM-guided synthesis neighbor, and programmatic sampling does not make its LLM incidental. Our implementation also validly uses Agent-authored models plus numerical execution. Our current strongest distinction should be explained through the **biomedical evidence contract and requested-analysis use**, supported by the demonstrated transformations and datasets. Whether that complete combination is sufficiently novel for a particular top conference remains a research and review question; the writing style cannot settle it.

The v0.10 revision should preserve all original results and main-table values. This note recommends restructuring and original redrawing only; it does not release a new experiment, stronger generalization claim or outcome-based case selection.
