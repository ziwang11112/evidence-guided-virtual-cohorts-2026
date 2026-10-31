# Storyline and paper-design notes: G-Sim, LLMSynthor, and our direction

> Export note: this is an original reading/audit note. Downloaded papers and third-party implementation snapshots remain in the local research archive. Later scope decisions, including evidence-only full-cohort generation as a core intended capability, are recorded in the current paper-direction document.

2026-10-31. Primary-text narrative analysis and proposed design; no experiment, new result or priority claim.

## 1. What makes each paper coherent

### G-Sim

**Author framing.** Simulators enable experimentation and decisions, but learned predictors do not automatically provide editable, plausible simulation components. Desired properties precede the method: system-wide experimentation, plausible generalization, empirical alignment and preserving data forms (P0–P3, pp. 1–2).

**Mapping.** LLM proposals serve plausible structure; calibration serves empirical alignment; diagnostics connect them. The problem definition separates structure from parameters. Figure 1 depicts the loop and its generated artifact: executable code.

**Evidence.** Known simulators enable fidelity tests and ablations. Intervention and policy examples show what editability enables. Three environments broaden the claim.

**Interpretation.** The contribution is an automated simulator builder, bounded by the known-simulator and oracle-feedback conditions documented in our audit.

Primary source: [G-Sim, Introduction, §§2–3, §§5–6 and Figure 1](https://proceedings.mlr.press/v267/holt25b.html).

### LLMSynthor

**Author framing.** Applications need micro-records but have aggregates. Figure 1 contrasts plausible individual records with population-level agreement; efficiency adds another requirement.

**Mapping.** Dependency grouping connects variables; discrepancy feedback controls alignment; proposal sampling enables bulk production. Definitions formalize records, aggregation and the objective. The title names the capability.

**Actual section order:** mobility/RQ1 demonstrates source composition; e-commerce/RQ2 provides controlled fidelity and utility comparisons; ACS/RQ3 tests complex records and policy queries. Efficiency/backbone comparisons support engineering claims. This order differs from our proposed controlled-first development sequence below.

**Interpretation.** The paper transforms available information into a useful data object. Downstream analysis is already substantive. Avoid copying overbroad claims that all classical methods require microdata or treating scenarios as validated predictions.

Primary source: [LLMSynthor v3, Introduction, §3, §4 and Figure 1](https://arxiv.org/html/2505.14752v3).

## 2. The broad direction that fits our project

**Proposed theme:** turn published biomedical evidence into reusable virtual data for scientific analysis.

**Working title:** *From Published Evidence to Virtual Cohorts for Scientific Analysis*.

This covers cohort generation, missing measurements and new variables. Entirely unmeasured biomarker enrichment can anchor the first paper without defining the direction as one BMI–urate correction.

Publications report results under specific populations, measurements and adjustments. These constrain but generally do not determine the target joint distribution. Generation must interpret conditions and expose unresolved assumptions.

The technical hinge is study-conditioned evidence execution: an Agent proposes generators/source analyses; tools calibrate; diagnostics support revision or retention. Value and novelty require comparison with competent statistical and generative alternatives.

## 3. A paper spine: question → mechanism → evidence → use

| Part | Reader's question | What our paper should supply |
|---|---|---|
| Introduction | Why does this data gap matter? | Concrete missing-biomarker example and the available published evidence |
| Problem definition | What may the method see, and what must it output? | Source evidence, observed target covariates, virtual columns/cohorts, and permitted feedback |
| Method | How does evidence change the generator? | Explicit proposal, source-condition operators, calibration and diagnostic revision |
| Controlled validation | Can the mechanism work, and when is the problem identifiable? | Compatible versus heterogeneous sources; hidden analyses; deliberately ambiguous relationships |
| Real-data validation | Are the outputs useful outside a toy model? | Frozen generation compared with the same analyses on independent complete references |
| Mechanistic analysis | What accounts for success or failure? | Evidence coverage, source shift, feedback attribution, generation representation, costs |
| Demonstration | What can a researcher do with the data? | Several analyses of one frozen dataset, with qualified conclusions |

This maps claims to evidence. Test counts and provenance support reproducibility; main results must establish usefulness.

## 4. Proposed contributions, with evidence obligations

1. **A clearly specified evidence-to-data setting.** Show why external study results differ from available target joint tables. Release evidence/input/evaluation definitions that make the task reproducible. A new setting alone does not prove a new method.
2. **A concrete mechanism for using heterogeneous evidence.** Demonstrate how preserving population, measurement and analysis conditions affects generation. Pooled-versus-conditioned handling is an ablation; an Agent-specific superiority claim would additionally need a competent condition-aware statistical comparator.
3. **Demonstrated scientific reuse and its boundaries.** Evaluate adjustment-sensitive effects, nonlinear shapes and subgroup relationships that were not all explicit calibration targets. Use multiple independent cases and report negative results. Direction alone is insufficient; effect size, stability and uncertainty matter.

These proposed contributions require quantitative evidence. Simple methods working well are useful findings.

## 5. Figure and writing plan

- **Figure 1: the scientific opportunity.** Fragmented papers plus observed target covariates become a reusable virtual dataset, then support several analyses. Show the specific missing-variable example; do not start with a crowded multi-agent diagram.
- **Figure 2: the operative mechanism.** Follow one reported result through extraction, source-conditioned analysis, generator constraint, diagnostic and revision. Distinguish source evidence from assumptions and reserved target answers.
- **Figure 3: primary utility.** Show the same prespecified analysis panel across real-data cases, with effects and uncertainty rather than only a global similarity score.
- **Figure 4: why it works or fails.** Controlled source heterogeneity and evidence-coverage experiments; connect gains to the changed mechanism.
- **Figure 5, if justified: reuse and limits.** One frozen dataset supports several scientific questions; display conclusions that are stable and those unsupported by available evidence. Costs and scaling can be a compact panel or appendix.

An introduction can follow five connected paragraphs: practical data gap; current substitutes and their actual information requirements; why study-conditioned statistics are difficult to combine; the proposed generative insight; the exact validated contributions. An abstract can mirror that sequence, ending with quantitative results once available. Avoid future-tense results, claims of recovering individual truth, and guarantees of replacing patient collection.

## 6. Scope decision

First establish one mechanism result, then expand to two or three distinct biomedical cases. Different survey cycles are not automatically different domains. Whole-cohort generation and partial missingness remain extensions, not mandatory parallel projects.

A methods paper can center biomedical usefulness. A discovery paper additionally needs an important biological finding and validation. Develop the former; let results determine venue and claims. These examples are not universal conference templates or acceptance guarantees.
