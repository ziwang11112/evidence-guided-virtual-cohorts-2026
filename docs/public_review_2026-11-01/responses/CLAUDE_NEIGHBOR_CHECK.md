# Focused primary-source check after receiving the Claude PDF

Checked on 1 November 2026. This is a bounded check of four decisive neighbors and a linked correction, not an exhaustive novelty review or numerical reproduction. No paper files or third-party code were exported.

## Jones et al.: the review understates the evaluation

The [PLOS ONE article](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0341704) describes whole household populations generated from aggregate descriptors without model fine-tuning. Contrary to the review's story-ranking shorthand that it only assesses target macro-statistic fit, Section 5.3 and Figure 8 explicitly examine household age relationships not provided as inputs. Section 5.5 also compares against iterative proportional updating. Consequently, checking unprovided relationships in generated populations is not by itself our novelty. The narrower biomedical challenge concerns heterogeneous study estimands, transport assumptions, and reusable analysis in an independent target. That gap still requires comparison, not a priority declaration. The [August correction](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0356492) replaces Figure 10, whose original image showed a preliminary experiment rather than the repeated Newcastle runs; it does not withdraw the paper's held-out Figure 8 analysis.

## SynthIPD: update the version and recognize analytical reuse

The [arXiv record](https://arxiv.org/abs/2509.16466) shows v1 on 19 September 2025 and v2 on 24 July 2026. Claude cited v1 and a different September date. The [v2 full text](https://arxiv.org/html/2509.16466v2) describes reconstruction from published survival curves and subgroup summaries, with covariates, a real-IPD comparison, pooled trial analysis, and simulations. Its six-trial application already uses synthetic data for downstream scientific analysis. It is therefore stronger prior art than a generic marginal-matching tool. Its survival/trial-specific structure differs from general biomedical cohorts assembled across heterogeneous studies. We did not reproduce its numerical claims or certify code availability.

## Chen et al.: useful validation precedent, scoped to the evaluated version

The [2019 Synthea validation](https://link.springer.com/article/10.1186/s12911-019-0793-0) evaluates clinical quality measures, including substantial failures in outcome measures despite plausible service/demographic behavior. This supports analyzing downstream uses rather than only source fit. It is not proof about every later Synthea version, nor a universal impossibility result for synthetic data.

## LLMSynthor: current version and visible code-release boundary

The [v4 arXiv record](https://arxiv.org/abs/2505.14752v4) confirms the June 2026 revision and the macro-aligned micro-record objective. The [official repository](https://github.com/YihongT/LLMSynthor) currently exposes a README/resources listing and a pending-code-release notice. An implementation reconstructed from the paper must not be described as a run of released official generation code. This check does not audit all branches or prove that no implementation exists elsewhere.

## Consequence for our paper

Do not claim first evidence-only population synthesis, first feedback loop, first held-out relationship test, or first downstream analysis with synthetic data. A defensible candidate contribution is an operational method and independent evaluation for translating heterogeneous biomedical evidence into reusable data, with explicit per-analysis support and transport limitations. Whether this is enough for a methods paper depends on implemented behavior and new results. The close predecessors make the intended contribution more specific; they do not establish that our scientific use case is worthless.
