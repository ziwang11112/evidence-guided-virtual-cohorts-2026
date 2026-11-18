# The contribution and the scientific story

## Proposed central question

Can a scientific Agent turn a biomedical research request and partial published evidence into an inspectable joint generator whose virtual records support the requested analyses, without target individual-level training records?

The product is still virtual data. The executable law and its evidence/assumption record make those data interpretable and reusable. A provenance dashboard alone is not the research contribution, and an Agent label alone does not distinguish the method from existing LLM simulators.

## Three contributions, with their present evidential status

| Contribution | What is implemented or observed | What would be stronger than the evidence |
|---|---|---|
| Research-request-driven scientific construction | The current API Agent selects search queries, reads papers, chooses numerical evidence and assumptions, writes a joint stochastic program, requests a trial, and selects its output. Ordinary and workflow arms start from the same request and shared tools. | An unprecedented general Agent architecture, fully automatic clinical validation, or a universal advantage over ordinary Agents. |
| Virtual records evaluated for scientific analyses | Earlier glycemia evidence contrasts and repeated constructions, plus iron, lipid and BP analyses, distinguish conditional slopes, co-occurrence and residual dependence. The latest four constructions deliver all six prespecified primary analyses, with mixed magnitude agreement. | Every generated variable is clinically valid, new-patient measurements are recovered, or more sampled rows create additional biological evidence. |
| Auditable scientific construction | Source statistic, adopted quantity, transformation, scientific assumption, executable choice and downstream analysis can be inspected separately. The fixed-packet audit and latest source audit provide worked examples. | Provenance automatically predicts target error, inferred model reasoning is faithful to hidden cognition, or a cited source proves transport to the target population. |

These contributions form an application/methods study with a concrete scientific Agent capability. The current evidence does not establish a new optimization algorithm or a dominant general-purpose generation method. Whether the combination is competitive for a selective venue depends on the strength of the empirical contribution and comparisons, not on attaching an Agent name.

## A story that uses the favorable and unfavorable findings together

1. Researchers can obtain published summaries while lacking the individual records needed for their intended multivariable analysis. The missing work is choosing a joint construction from heterogeneous evidence.
2. An Agent can perform that work: recover numerical relationships, distinguish measurements and adjustment sets, and author a sampler. Numerical execution makes its choices reproducible.
3. Useful analyses are possible, but the same records can support one analysis better than another. The earlier relationship-evidence contrast improves five of six coefficients; the worsening coefficient remains part of the result.
4. The latest request-only experiment demonstrates actual autonomous retrieval and construction. Both arms recover BP residual dependence numerically near the reference, while BMI–BP magnitudes and lipid dispersion/dependence remain different.
5. Tracing sources and assumptions explains which scientific bridge must be examined. It does not turn agreement into proof or automatically assign a trustworthy score.
6. The reusable result is a virtual dataset plus an inspectable account of how it was constructed and which analyses were evaluated. That is a more specific contribution than a generate–check–revise loop.

The fixed-packet pilots' residual-dependence shortfall in all twenty delivered initial constructions remains a valid observation within those two tasks. The later open-retrieval BP results prevent a universal claim that Agents necessarily underestimate dependence. Comparing those phases generates a hypothesis about evidence and construction choices; it does not isolate their causal effect.

## Explainability that can actually be evaluated

Use **scientific traceability** or **inspectable generation** as the main terms. A practical explanation answers: which source quantity influenced this code, what was changed, which assumptions were added, and which requested analyses depend on them. Do not ask for private chain-of-thought. Preserve short submitted decision records and verifiable artifacts.

There are three distinct tests:

| Test | Unit and output | Current position |
|---|---|---|
| Provenance correctness | Independently check a claimed source locator, value, operator, unit and code link against the archived source and program. | Existing audits support worked examples; comprehensive coverage needs a denominator that includes missing links. |
| Scientific consequence | Derive a requested model-law functional when possible, or declare a prespecified sensitivity analysis; compare it to calculations on generated data. | Available for selected constructions. A raw parameter cannot substitute for a post-selection/nonlinear estimand. |
| Audit usefulness | Compare the same programs/sources with and without the provenance map; measure reviewer accuracy, unsupported claims and time. | Designed next, not yet tested. It can show an efficiency or interpretability benefit without claiming better generated data. |

Calling a source-reported parameter high-confidence and an assumption low-confidence is insufficient: a faithfully copied source parameter can transfer poorly, while an assumption can happen to be close. A predictive analysis-risk score would require a separate prospective validation.

## Closest work and a defensible distinction

This is a bounded update to the existing related-work audit, not an exhaustive novelty search. Primary pages were checked on 11 November 2026 UTC.

| Work | Relevant overlap | What to emphasize here |
|---|---|---|
| G-Sim, ICML 2025 | LLM-designed simulator structure, numerical parameter calibration and iterative refinement. | Biomedical study-qualified evidence and requested conditional analyses; do not claim the generic simulator loop as new. [Primary paper](https://proceedings.mlr.press/v267/holt25b.html). |
| LLMSynthor, KDD 2026 | Generation from target macro-statistics, inferred dependencies and discrepancy-guided proposals. | Our external study statistics have different populations, adjustment sets and measurement operators; these must be interpreted before authoring a joint law. We have not demonstrated superiority to its own algorithm or efficiency. [Version 3](https://arxiv.org/html/2505.14752v3), [DOI](https://doi.org/10.1145/3770855.3818965). |
| SynthIPD | Training-free survival-record/covariate reconstruction from published materials. | Different requested scientific task and information boundary; not the first publication-to-patient-data method. [Version 2](https://arxiv.org/html/2509.16466v2). |
| KMGen, MLHC 2026 | Agentic extraction, clinical priors and a mechanistic sampler for survival and adverse-event records. | The current Agent chooses the joint biomarker program for each request rather than only populating a fixed oncology sampler. Both involve assumptions and statistical sampling; neither distinction proves broader accuracy. [Primary proceedings](https://proceedings.mlr.press/v340/jiang26a.html). |
| PROV-AGENT | Captures Agent/model/tool interactions and decisions within workflow provenance. | Analysis-specific statistical meaning and source-to-law dependencies, rather than generic log collection alone. Provenance itself is established work. [Primary manuscript](https://arxiv.org/html/2508.02866v1). |

The comparison is about documented inputs, delegated decisions, outputs and evaluated uses. Do not call predecessors non-agentic, entirely hard-coded, unable to scale, or non-biomedical without evidence. Our lower target-data requirement is a declared setting; measured cost savings and comparative scalability remain separate experiments.

## Manuscript hierarchy

Figure 1 explains the actual request-to-data implementation. Core scientific-use/evidence-contrast figures show what the records can analyze. The complete request-only result figure adds autonomous retrieval and ordinary-Agent comparison. A worked provenance figure connects a published statistic to a scientific choice and its evaluated consequence. Complete failures, author profiles and model configurations remain in the supplement.

Do not make a framework diagram's feedback arrow larger than its evidential role: all four latest constructors retained v001. Put the final data and scientific analyses at the end of the visual flow. Explainability should illuminate those results, not replace them.

The focused next-experiment design is in [EXPERIMENT_EXTENSION_PLAN.md](EXPERIMENT_EXTENSION_PLAN.md). No model call, patient analysis, generator modification or new scientific experiment was executed for this revision.
