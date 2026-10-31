# M17-A: complete-cohort execution linked to source feedback

31 October 2026. **Completed engineering unit.** No biomedical or Agent-quality experiment was performed.

The system now collects and independently verifies source-statistic feedback from an already executed complete-cohort candidate. An actual isolated run generated 128 artificial rows with all three substantive variables (`x`, `group`, `y`) and no observed individual table. Five diagnostics matched an independent standard-library calculation; all ten pre-execution input bindings remained unchanged.

This prepares the evidence-only whole-cohort branch requested by the user. The generator in this check was a deliberately specified engineering fixture, not a scientific Agent's model inferred from papers. The result establishes execution and feedback linkage, not biological accuracy, independent target validity or a new method advantage.

## What changed

- Added [whole-cohort feedback collection and verification](cohort_harness/whole_cohort_feedback.py), without modifying the older enrichment replay adapters.
- Feedback reads the output of a successful verified execution belonging to the frozen candidate. It does not accept an unrelated comparison CSV.
- A frozen recipe defines permitted evidence-linked operators, units, adjustments and assumptions. The output report remains outside the frozen candidate.
- Verification repeats the statistics and checks candidate, recipe, task, evidence, execution and output bindings.
- Undefined checks remain explicit; direct tables and executed programs have distinct provenance flags. The adapter does not certify source-population applicability or perform measurement conversion.

See [interface documentation](docs/WHOLE_COHORT_FEEDBACK.md), [implementation review](docs/M17A_FEEDBACK_IMPLEMENTATION_REVIEW.md), [initial plan](docs/M17A_WHOLE_COHORT_PLAN.md) and [readiness audit](docs/M17A_WHOLE_COHORT_READINESS.md).

## What actually ran

| Item | Actual outcome |
|---|---|
| Focused interface tests | 33 passed; artificial fixtures and mocked program execution/direct-table cases |
| Initial test correction | One test expected the wrong error-message wording; rejection worked and the assertion was corrected before the passing rerun |
| Actual program execution | Successful in the existing WSL/bubblewrap generator-only runtime; no host execution fallback |
| Fixture input | Aggregate-only invented source brief, task metadata and a trusted seeded test program; zero individual records supplied |
| Output | 128 rows; both continuous variables and the categorical variable generated; seed 17001 |
| Recorded execution time | 2.922 seconds for this local engineering run; not a scientific cost comparison |
| Computed feedback | Mean x, sample SD x, group proportion, mean y and adjusted x coefficient in y ~ 1 + x + group |
| Independent arithmetic | All five matched; maximum absolute statistic difference 2.220446049250313e-16 |
| Immutable inputs | All ten pre-execution file bindings preserved |

The independent [checker](examples/m17a_independent_check.py) uses CSV reading, Python statistics and centered cross-products for the adjusted regression. It does not call the harness statistical operators. The [preparation script](examples/m17a_whole_cohort.py) creates metadata and program text only; execution is a separate explicit command.

The implementation review preceded actual execution. Its statement that runtime checking was pending describes that review time; the actual run and arithmetic reported here are subsequent checks.

## Preserved source diagnostics

These are invented population expectations and one finite artificial draw. The discrepancies are not Agent-performance results and were not used to tune the fixture.

| Diagnostic | Invented source expectation | Generated statistic | Difference |
|---|---:|---:|---:|
| Mean x | 0 | -0.1530897903464567 | -0.1530897903464567 |
| Sample SD x | 1 | 0.9465933636385772 | -0.05340663636142284 |
| P(group = 1) | 0.5 | 0.5078125 | 0.0078125 |
| Mean y | 1.3 | 1.1066844816693364 | -0.19331551833066363 |
| Adjusted x coefficient | 0.75 | 0.7543038812620151 | 0.004303881262015086 |

The aggregate [engineering result](reports/m17a_whole_cohort_2026-10-31/ENGINEERING_RESULT.json) and [independent arithmetic record](reports/m17a_whole_cohort_2026-10-31/INDEPENDENT_ARITHMETIC.json) retain hashes and exact values. The generated table is not needed in the GitHub export; it can be recreated from the artificial preparation script and seed using the documented runtime.

## Scope and next scientific step

This adapter evaluates the complete cohort produced by the selected generator. It does not yet generate separate source populations, convert assays, infer transport uncertainty or automatically calibrate across incompatible studies. The existing whole-cohort contracts prohibit the canonical observed table; this alone does not semantically certify every source document or isolate every general-purpose Agent tool.

The next scientific unit should ask an Agent to choose its own generator from an admitted aggregate-evidence packet, with all target individual records withheld. Freeze the candidate before evaluating unprovided analyses. Keep any observed-covariate arm separately labeled. A controlled reference can first distinguish information insufficiency from faulty evidence use, followed by fresh public biomedical validation where justified.

M13-B, M15-B and M16 remain closed to tuning and fresh confirmation. No new patient dataset, paid API, training job or HPC job was used for M17-A. No automatic follow-on experiment or recurring job was launched by this result.
