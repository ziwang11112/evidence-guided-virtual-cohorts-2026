# Stage 1 decision: complete the benchmark; do not scale an unproven accuracy policy

This decision follows the advance/stop rules written before the bounded Stage 1 run. It is not a new success criterion selected after looking at results.

## What was completed

- Three previously exposed development cases: Ross (75 participants, five visits), Travers (12 paired adults), and He (44 paired pediatric completers, 43 glucose/triglyceride pairs).
- Nine fresh initial Agent constructions, with ordinary and multiple-scenario revisions branching from identical parent inputs in separate fresh contexts.
- Eighteen Agent branches with twenty final cohorts each, plus three fixed statistical arms with twenty each: **420/420 generated**.
- A locked 55-term analysis registry, applied with the same analysis implementation to real and synthetic data: **7,700 retained synthetic-analysis records** and 55 reference records.
- Frozen inputs, auditable source decisions, successful and failed diagnostic logs, independent verification, and private GitHub synchronization of code and aggregate outputs.

The current experiment is A0 target-summary reconstruction. It contains neither newly sourced cross-study joint evidence nor an independently untouched validation cohort. Its generation success is not a replacement for the separate partial-record-completion experiments.

## What the results support

The framework constructs executable generators, preserves source constraints, documents assumptions, and exposes sensitivity of scientific analyses to relationships absent from the evidence. An Agent can make an inspectable measurement-level correction: Ross build_01 ordinary changed PFS to a 15-item aggregate lattice. These are useful implementation and research-rehearsal capabilities.

The tested scenario policy does **not** demonstrate consistent improvement in unprovided relationships relative to ordinary revision. Some individual scenarios perform better on some terms; other source-compatible scenarios make the results worse. Selecting the better scenario using the reserved answer would invalidate the intended procedure, so all scenarios remain reported.

Matching a paper's qualitative direction can coexist with large uncertainty errors. For example, the ordinary adult body-mass median standard-error ratios across the three builders are approximately 3.33, 1.91 and 7.57 relative to the observed reference; the pediatric ratios are approximately 4.72, 4.07 and 5.13. The source marginal means constrain the mean change, while the unprovided paired covariance determines its uncertainty. This is a reason to evaluate the complete analysis, not only the direction or marginal distribution.

The adult and pediatric reference intervals for all twelve reserved change correlations overlap zero. High agreement with that unresolved state is not evidence that those population correlations are zero. Conversely, confident synthetic correlations where the observed reference is unresolved are evidence discrepancies, not proven population false positives.

## Advance/stop disposition

**Complete and retain the software, benchmark, tables, figures and failure record. Do not launch the planned 1,100-cohort Stage 2 expansion of this unchanged scenario policy, and do not claim analytical superiority, calibrated confidence coverage or avoided patient recruitment.** The bounded development comparison has not met the original condition of recurrent, decision-useful benefit.

No HPC allocation is warranted for the completed workload. Numerical generation and evaluation fit on the current 16-logical-processor, approximately 31.6-GiB machine. Independent model construction/review dominated elapsed effort; no model/token-cost benchmark was available.

The overall evidence-guided virtual-cohort idea remains open. A further experiment would need a discriminating information source rather than more repetitions of an unidentified joint model. A concrete candidate is a prospectively frozen, small joint-evidence acquisition task: the Agent identifies an analysis-relevant missing covariance/conditional summary, obtains an admissible external summary under a bounded budget, revises the generator, and is tested on separate unqueried analyses. Applicability, cohort overlap and the evidence budget must be audited before opening new answers. The current results may motivate that new protocol; they cannot validate it.

## Manuscript readiness

Methods, implementation, source-quality controls, complete benchmark results and limitations can now be drafted. A paper claiming a superior cross-study generator or validated study-planning benefit still lacks the corresponding independent evidence. A benchmark/resource or a new joint-evidence mechanism is a different paper claim; it must be stated explicitly rather than relabeling this mixed result as an accuracy success.

See [RESULTS.md](RESULTS.md), the [pre-evaluation construction observations](../stage1_review/CONSTRUCTION_OBSERVATIONS.md), and the independent audit in [stage1_review/postrun](../stage1_review/postrun/).
