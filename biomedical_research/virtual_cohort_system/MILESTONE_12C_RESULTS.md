# M12-C — Actual Agent construction, source review and candidate promotion

Completed 30 October 2026. The minimum source-only Agent integration gate is met: one actual externally launched LLM constructed a generator, received verified statistical feedback, made a recorded scientific decision, and had its selected model preserved in a formal development candidate. This is not a biomedical validation, autonomous literature-discovery result or performance comparison with other Agents.

## What the Agent did

The construction Agent began with two invented study summaries, their covariate-only source populations, a target covariate table without y, and interface/experiment contracts. It did not receive a generator formula, a previous experiment's generator, individual source y records or target outcomes. The task preparation code contains no preferred scientific structure or generator program.

Study A has category proportions 80:40; study B has 40:80. Both report a mean, sample standard deviation and x coefficient adjusted for z. The Agent chose an additive conditional mean with independent symmetric triangular residuals. Under its explicitly shared-source assumption, it derived an intercept of 3 and category contrast approximately 2 from the two means and compositions, adopted the reported adjusted x coefficient of 2, and derived a starting residual SD of 1.0041928905 using expected sample-variance decomposition.

The common source equation, linearity, absence of interactions/source effects, residual law and target interpolation were all recorded as assumptions. The Agent also identified alternative study-specific shifts and the lack of interior-x/curvature evidence. These are substantive choices in the actual generated program and specification, not a controller-written biomarker formula.

## Actual execution and review

The controller checked the admitted input hashes and fixed experiment settings, froze the initial candidate and invoked the existing numerical tool. The initial vector already met the previously declared engineering tolerance, so no parameter-search step was needed.

| Quantity | Observed result |
|---|---:|
| Invented source studies / scheduled statistics | 2 / 6 |
| Evaluated parameter vectors | 1, the initial vector |
| Numerical parameter changes | 0 |
| Actual isolated source executions | 8: 2 contexts × 4 seeds |
| Fit mean squared scaled discrepancy | 0.0040170478 |
| Separately scheduled replay discrepancy | 0.0020033815 |
| Predetermined engineering stopping tolerance | 0.04 |
| Actual scientific decision | retain_structure |
| Formal promoted development candidates | 1 |

The review request was recorded before the same Agent received feedback. It inspected all six constraints and the scheduled seeds, chose retention and explicitly stated that neither parameter improvement nor structural revision had occurred. It also noticed that reuse of seeds across equal-sized source populations correlates Monte Carlo errors. The smaller replay loss is fresh-draw variation, not evidence of optimization or new empirical validation.

## Controller implementation

Added `cohort_harness/scientific_loop.py`. The new adapter records exact requests, external decisions, fixed review/promotion budgets and pending states; verifies calibration and evidence references; reserves a promotion before creating files; and copies the selected generator/specification bytes into `candidates/source_reviewed` with lineage and actual feedback.

The output is explicitly a **source-checked development candidate**, not a target release. The scientific choice was `retain_structure`. The old lifecycle flag is `revise` because calibrated provenance changes specification bytes; it must not be interpreted as a model change or improved generated data.

The externally launched initial construction is separately logged. The controller budget counts subsequent review requests and promotions, not every Agent tool call or token. Revision, evidence-request and stop decisions are supported as records; automated retrieval and structural editing are not implemented by this adapter. The real demonstration exercised retention and promotion only. Agent tool access remains procedurally restricted; only generator execution is isolated.

## Verification

- 21 new controller tests passed; complete suite **502 passed, 2 skipped** for unavailable Windows symbolic-link privileges.
- Independent arithmetic review recomputed all eight actual generated tables using direct sums, sample variance and regression normal equations. Maximum statistic difference was **2.44 × 10⁻¹⁵**; recomputed losses agreed within **5 × 10⁻¹⁷**.
- Original numeric parameters, observed cells, source inputs, source operators and fixed controls were preserved.
- Request/decision/promotion order, exact selected program/specification bytes, parent lineage, revision annotation and feedback bindings passed independent verification.
- Existing engine files and previous curated experiment artifacts remain unchanged; the curated preservation record enumerates them.

The Agent initially used an unsupported CLI candidate-path form, recorded the rejection, and corrected that invocation before freezing. Schema review also added explicit checks for decision-derived revision annotations and UTF-8 event sizes before mutation. No generated code ran on the host and no biomedical outcome was accessed in this milestone.

## Interpretation and next step

This demonstrates actual LLM participation in generator design and a source-informed retention decision through reproducible tools. It does not show that feedback caused a useful correction, that the framework beats an ordinary Agent, that the source model is uniquely identified, or that generated values support uncalibrated analyses in a real population.

The next priority is **admitting one real evidence case**, followed by a frozen real-data analysis schedule. Use the current tool chain to construct from external evidence, document population/measurement compatibility and unresolved assumptions, and keep target outcomes withheld until generation is complete. Assess scientific associations and analysis reuse against reserved real measurements. Additional controller features are not required before starting that admission work.

See [the curated run and actual Agent records](reports/m12c_2026-10-30/README.md), [interface and boundaries](docs/SCIENTIFIC_AGENT_LOOP.md), and the [active roadmap](docs/IMPLEMENTATION_ROADMAP_2026-10-30.md). Latest biomedical findings remain M10/M11.
