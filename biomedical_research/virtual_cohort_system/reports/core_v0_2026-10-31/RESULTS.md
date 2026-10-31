# Core v0 implementation freeze and source-feedback replay

31 October 2026. **F1 is ready for the documented reference profile:** externally orchestrated Agent construction of a whole-cohort program, verified identity-measurement source feedback, and a bounded retention/revision decision. This is an implementation freeze, not a scientific accuracy, novelty or publication-readiness result. A new real case is not yet admitted.

The [compact specification](CORE_METHOD_V0.md) defines the broader research objective, available interfaces and their limitations. The reference integration uses existing library modules; no new statistical model class, estimator, loss or library module was added. The unit controller connects existing calls and includes explicit fixture-specific guards. It is not a general autonomous scientific service. The [English working manuscript](../../manuscript/DRAFT_v0.md) now contains the problem, method, validation design and scoped development results.

## What actually happened

1. Admitted only the original bytes of an explicitly invented aggregate source; no old model, generated rows or real-target answers were copied.
2. Specified a complete fictional 768-row population: 256 generated records in each x=0,1,2 stratum, group=0. These quotas are task design, not inferred prevalence. There were no individual inputs.
3. A fresh-context scientific Agent extracted six source moments and chose Gamma distributions. Shape 4 and scales 0.5, 0.75 and 1 u follow from its chosen family and the source mean/individual-SD pairs. Tail form, independence, absence of a zero point mass and use of plug-in moments are explicit assumptions.
4. Independently reviewed source semantics, parameters, code and all six statistical recipes. Bound the specification, task prompts, source, native code and initial candidate before execution.
5. Executed the initial candidate in WSL/bubblewrap; collected and verified all six source diagnostics from that exact output.
6. The Agent reviewed all feedback and chose **retain**, citing no evidenced defect requiring a change. It copied and hash-bound the authentic report into the new candidate. Program, specification, evidence and recipe remained byte-identical.
7. Froze the parent-linked final candidate and performed the second and last execution with the same fixed seed, 26301. Its output was byte-identical to the initial output. This is **two executions of one unique 768-row draw**, not two independent cohorts or a quality improvement.
8. Independently recomputed both stages, verified execution/source/decision linkage and closed the unit. No scientific rerun, calibration, target fitting or new data download occurred.

## Complete source feedback

The same numbers occur at both stages because the Agent retained the scientific model and the seed was fixed. These differences remain recorded; no post hoc fit threshold was introduced.

| Stratum | Quantity | Source | Generated | Generated minus source |
|---|---|---:|---:|---:|
| x=0 | Mean y | 2.000000 | 2.075434 | +0.075434 |
| x=0 | Individual SD y | 1.000000 | 1.039611 | +0.039611 |
| x=1 | Mean y | 3.000000 | 2.935889 | -0.064111 |
| x=1 | Individual SD y | 1.500000 | 1.420805 | -0.079195 |
| x=2 | Mean y | 4.000000 | 4.031367 | +0.031367 |
| x=2 | Individual SD y | 2.000000 | 1.952424 | -0.047576 |

All values use unit u. Each check used 256 records with no missing values. The generated SD estimator uses n-1; the source's SD convention and estimation uncertainty are not reported. Approximation assumptions remain explicit. The Gamma family analytically matches the supplied process moments but its tails and distribution-sensitive analyses are not identified by these six moments.

## Independent verification and implementation findings

The [independent closeout](review/postrun/F1_INDEPENDENT_CLOSEOUT.md) concludes `F1_REFERENCE_PROFILE_READY`. Independent CSV and `math.fsum` arithmetic matches all six estimates in both stages, with maximum discrepancy 4.44e-16. Quotas, identifiers, group membership and nonnegative y pass. Native candidate, execution and feedback verifiers pass; the exact initial feedback is bound to the final candidate, whose revision index is one with the correct initial parent. All 46 assembly-bound files and eight explicitly selected historical anchors remain unchanged. This is not a whole-history audit.

Interface review identified controls to make explicit: whole-cohort recipe semantics require a separate preflight; a valid auxiliary hash alone does not authenticate feedback; retention alone does not force evidence/recipe identity; and generator-call limits are controller policy. The integration controller checks these conditions before the applicable execution. Two controller review findings—exact operator schemas and final-run linkage checks—were corrected before the assembly freeze. A preliminary wrong-module-name import failed before action and was corrected. No scientific execution failed or was replaced.

Actual worker records: Python 3.12.3, NumPy 2.4.5, pandas 3.0.3, Ubuntu-24.04 WSL/bubblewrap. Receipt elapsed times are 2.953 and 3.031 seconds, totaling **5.984 seconds of execution time**. This excludes Agent construction, review and coordination. Model identifier, temperature, tokens and total monetary cost are not exposed/metered. No training, paid API, HPC or recurring task was started. Only generator processes are OS-isolated; Agent tool restrictions are procedural.

## Freeze scope and next scientific step

F1 now binds a compact method specification and an exercised reference sequence. It does not demonstrate numeric revision efficacy, automatic retrieval quality, whole-cohort reconstruction of multiple study populations, calibrated uncertainty, all information regimes, general conversational requests, or real-population transfer. Whole-cohort identity feedback evaluates the actual generated population; mismatched sources cannot be relabelled as exact source-population replay.

Retain the same minimal core and move to [real-case admission](NEXT_CASE_ADMISSION.md): at most three candidate dataset families and six new primary studies, chosen from metadata, source applicability and access before target-effect inspection. Freeze one case and approximately three meaningful analyses before disclosure. Dynamic extension remains optional; no new platform or toy expansion is a prerequisite. If evidence or accessible independent data cannot support a case, close admission with the limitation.

The manuscript's primary outcome remains useful virtual data for scientific analysis. F1 implementation completion permits that scientific evaluation; it does not predetermine whether its result will be positive, mixed, null or unresolved. F2 and the final result/claim lock remain pending.
