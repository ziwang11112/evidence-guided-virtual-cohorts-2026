# PRO system-design review after M11

30 October 2026. Review and proposed implementation decisions only. No new generator, calibration session or target analysis was run for this review. Historical freezes and results are unchanged.

## Inspection boundary

Read all 681 lines of the supplied [PRO response](reviews/pro_system_design_2026-10-30.txt), archived byte-for-byte. SHA256: `0c1d71f2190bd913c5d21643cc1927fde0d22e4b9d621c356a2a2fb6965b3a6c`.

The response refers to a separate `literature_biomedical_agent_system_design.md` through a ChatGPT sandbox link. That specification was unavailable during the first review. The user subsequently supplied it; all 933 lines are now covered by the [full-specification follow-up review](PRO_FULL_SPEC_REVIEW_2026-10-30.md). The response cites repository commit `d33d0cbad4c199fe5b450688fe8050d72afd9861` and M10. Current exported HEAD before this review was `74f5c0d4d5388677501a505b665490e127a7a22c`, containing M11. Review conclusions below use the current local code and [M11 results](../MILESTONE_11_RESULTS.md).

## Decision

Adopt the scientific division of labour: one capable scientific Agent interprets evidence and chooses structures; deterministic tools execute statistical definitions and bounded numerical fitting; the controller manages admissible information, execution, versions and release. A second review call can address a concrete concern. More Agent roles are not the research contribution.

Preserve the main deliverable: virtual biomedical tables and a reusable generator that support specified scientific analyses when measurements are unavailable. Whole-cohort generation, entirely unmeasured-variable enrichment and missing-cell completion remain within the broader scope; the next demonstration should use one continuous unmeasured variable.

The immediate improvement is to make evidence interpretation executable and source-to-target assumptions explicit. A lower source loss must not be treated as proof that a target table is more useful.

## What M11 changes

PRO's recommendation is based on M10, where the selected constructions did not change scientifically. M11 did implement a source-feedback-driven parameter revision. It improved the fitted source medians and worsened target levels. It did not revise model structure.

| M11 target statistic | Family A initial → primary calibration | Family B initial → primary calibration |
|---|---:|---:|
| Sex-median mean absolute error | 0.1769 → 0.2525 | 0.1417 → 0.2261 |
| Age–sex cell-mean mean absolute error | 0.3714 → 0.4469 | 0.3174 → 0.4019 |

Units are HbA1c percentage points; entries summarize three dependent residual draws. Preserved age/BMI slopes were expected under sex-specific additive shifts and are not evidence that the revision learned those relationships. This is one bounded negative mechanism result, not a universal impossibility result or a newly discovered statistical principle.

Therefore, implementation has to distinguish:

1. whether the published statistic was interpreted correctly;
2. whether the generator fits that statistic under a declared source approximation;
3. whether the conditional relationships and absolute levels have grounds to transfer;
4. which target analyses actually work in independent evaluation.

These are separate questions. Fixing the first two is useful but cannot identify an unknown target baseline by itself. A reference-source assumption or several transport scenarios are legitimate declared choices; neither creates missing evidence. Unrestricted study intercepts do not resolve this.

## Verified implementation gaps

| PRO recommendation | Current implementation | Decision |
|---|---|---|
| Separate source and target contracts | `cohort_harness/source_replay.py:61–90` validates covariate-only input, deep-copies the target task and changes only population text and row count. Column bounds remain inherited. | Real functional limitation. Add a validated, versioned source-context contract, leaving target eligibility unchanged. Separately declare the generator's computational domain. |
| Executable analysis operators | `source_checks.py:103–119` already implements means, SDs, quantiles, correlations, OLS coefficients and proportions with selection and missingness rules. | Extend the existing implementation, not a parallel statistics engine. Current operator fields do not implement general transformations, survey-weighted regression or flexible formulas. Unit text is not unit conversion. |
| Measurement mappings | `source_replay.py:116–118` accepts identity mapping only. | Add only explicit, justified transformations needed by admitted evidence. Unit conversion, assay bridging and population transport must remain distinct. |
| Independent calibration session | `lifecycle.py` binds parameter/specification bytes when freezing and increments a child revision index; `execution.py` executes verified frozen candidates. M11 used a case-specific analytic offset. The revision limit is lineage depth, not a global count of sibling trials. | A native general bounded session is missing; fitting is not technically impossible today. Add immutable internal parameter trials under one session with a total evaluation budget, then materialize a final scientific candidate. Never weaken existing freeze verification to permit in-place parameter changes. |
| Four parameter origins | `contracts.py:318–341` requires evidence/assumption IDs and derivation text, but has no enforced `reported/derived/calibrated/assumed` category. | Add validated provenance metadata. Some parameters use mixed inputs; retain their complete derivation, not just a single label. |
| Agent action loop | Literature access, candidate generation, replay and freezing exist; milestone orchestration still includes case-specific scripts and human/controller decisions. | Add a small finite action interface after the tools are sound. Do not describe current execution as fully autonomous literature-to-data generation. |
| Multiple hypotheses and uncertainty | M11 has two inherited structures, source-context scenarios and residual seeds. | Label these dimensions explicitly. Arbitrary scenarios are sensitivity analyses, not posterior samples or calibrated confidence intervals. |

M11 openly approximated the source's open-ended older-age bin within the inherited 20–79 range. The contract issue helps explain why this limitation needs attention; repairing it is not evidence that M11 target accuracy would improve. Historical results should remain frozen.

An independent read-only code review by the M11 custodian confirmed these findings. The current range check rejects out-of-domain data rather than silently clipping it; observed and generated column bounds are both inherited. Existing `source_portfolio.py` already supports verified seed portfolios and should be reused. Historical replay verification checks exact engine hashes (`source_replay.py:266`), so a new implementation must preserve a versioned historical engine for verification, not replace it in place and claim old receipts still verify under the new engine.

## A concrete evidence-admission finding

PRO's uric-acid example is a reasonable candidate, but the proposed evidence packet is not yet calibration-ready.

- The Korean source concerns ages 40–79 and excludes gout treatment. It can inform sex/age distributions within its study conditions; it does not by itself fix an American target baseline or justify extrapolation to younger participants. [Koo et al.](https://www.kjim.org/journal/view.php?number=170514&viewtype=pubreader)
- The Chinese source uses many adjustment variables beyond age, sex and BMI. Its online abstract and results also describe coefficients inconsistently as per-unit, per-SD and fold changes, with conflicting sign wording. Exact numerical use needs resolution against authoritative tables or supporting material; this review did not resolve the scale. Do not silently choose the interpretation that generates a convenient result. [Zhou et al.](https://link.springer.com/article/10.1186/s12967-019-02142-9)

The second finding is useful as a real semantic-review fixture. Detecting ambiguity is a valid outcome; inventing a repaired coefficient is not. One ambiguous article is not a benchmark or evidence that the entire approach outperforms another method.

The existence of a public assay variable is only one admission condition. Before committing the uric-acid case, a custodian must audit prior project exposure, aliases and derived fields, sample eligibility, weights and compatible measurements. This review did not download or inspect new participant-level uric-acid outcomes or certify a fresh target.

## Small next implementation milestone

The following is a proposed sequence, not a launched M12 experiment or frozen confirmation protocol.

### 1. Repair source-context independence

Preserve `generate(observed, spec, seed) -> DataFrame` and the three existing task modes. Add a versioned source-context object with its own variable schema, selection, measurement assumptions and covariate reconstruction. All sidecars require semantic validators and hash binding. Do not mutate old v1 bundles.

Acceptance checks should show that a source row outside target eligibility can still be replayed when inside the declared model domain; the same row still fails target eligibility. A row outside model support fails explicitly. A source-only covariate needs an explicit reconstruction/admission path, not silent dropping or a zero effect. Known source outcome columns remain forbidden in covariate-only contexts.

### 2. Add a minimal calibration session

Bind code structure, admitted evidence, source contexts, operators, parameter paths/bounds, objective scales, randomization and execution budget. Keep source covariate assumptions fixed during fitting. Evaluate immutable parameter snapshots through the same isolated runtime; allow no host-execution fallback. Store each trial, failure and selected result. Fit with common random numbers if useful, then replay with separate prespecified residual draws.

Use a simple bounded derivative-free optimizer only where needed; an analytic solution is acceptable when valid. An optimization step is not a scientific revision. Changing evidence, model structure, admissible parameter space or source reconstruction starts a new recorded scientific decision/session.

Do not reinterpret a summary loss as a likelihood. Source sampling uncertainty, reported rounding, Monte Carlo error and scientific tolerance are distinct. Correlated statistics from one cohort must not become fictitious independent observations. Final acceptance checks individual constraints, not only an aggregate score.

### 3. Let one Agent operate the tools

A minimal action vocabulary is enough: admit/defer evidence, specify source/operator, propose a generator, calibrate, inspect diagnostics, request targeted evidence, revise, retain, and release. Each scientific patch points to a specific evidence or diagnostic item and names the intended change. A justified no-op or unresolved evidence gap remains a valid outcome.

Templates may provide linear terms, low-dimensional smooth terms, interactions and residual families. They must not hard-code the expected sign, curvature or a biomarker-specific coefficient. The Agent's contribution is choosing and justifying an admissible construction; ordinary numerical optimization does not make the system non-agentic.

### 4. Admit one real case in parallel with engineering

Check whether available sources actually constrain at least one relevant relationship, a usable level/distribution, and a plausible transfer assumption. Separate source calibration statistics from unused source checks. If key evidence is ambiguous or adjustment conditions cannot be reconstructed, seek a better source or keep that relationship unassessed. Do not open successive target datasets while changing the evidence packet.

Uric acid remains a candidate, not a requirement. Avoid choosing a case only because literature announces an attractive nonlinear shape. Every new module should make a concrete scientific decision or analysis testable; defer infrastructure that does not do so.

### 5. Freeze and evaluate once the case is ready

Two independently constructed generators with three residual seeds each are a small engineering screen, not a powered study. If additional hypothesis or transport scenarios are justified, prerecord a bounded schedule and retain them all. No post-evaluation selection of the best structure or seed.

Apply identical analysis code to the generated tables and the reserved real measurements. Include one primary adjusted association, at least one uncalibrated analysis using the same frozen generator, and distribution checks relevant to those uses. Predeclare an analysis-specific usefulness criterion, magnitude/shape assessment, and reference uncertainty. Do not use nominal significance or sign agreement as the sole criterion. Reference survey uncertainty and synthetic/model uncertainty must be distinguished; multiplying synthetic rows does not increase biological evidence.

The evaluator's results inform the next development version, not revisions within the same confirmatory case. If feasible, leave an independent source study unused for fitting as an additional intermediate transport check; it does not replace target validation and is not mandatory if no appropriate study exists.

## Contribution and comparison policy

The basic empirical claim remains: external published evidence can produce virtual measurements that preserve specified scientific analyses in the evaluated settings. A successful ordinary Agent is a valid implementation. No unconditional Agent-versus-Agent superiority requirement is introduced.

For a method claim, test the particular additional mechanism with comparable information and adequate alternatives. A small reference calculation can distinguish semantic correctness from lucky output. If claiming better numerical calibration, compare to a competent statistical procedure with equivalent evidence. If claiming retrieval efficiency, compare the information gained and cost. If claiming automation, measure intervention count, completion, interpretive errors and failures rather than merely showing a diagram.

Existing work already covers LLM simulator design, parameter calibration and iterative revision ([G-Sim](https://proceedings.mlr.press/v267/holt25b.html)). Integrating individual models over source covariates to fit aggregate evidence has established statistical precedents ([ML-NMR](https://pmc.ncbi.nlm.nih.gov/articles/PMC7362893/)). Therefore the architecture alone is not a demonstrated innovation. The candidate contribution is reliable interpretation and use of heterogeneous published evidence for an entirely unavailable target measurement, validated through reusable downstream analyses. Its incremental benefit and scope still need experiments.

Keep positive feasibility results, M11's negative transfer and unresolved uses together. Do not declare clinical substitution, individual measurement recovery, general causal discovery, calibrated uncertainty or a publication tier from this review.
