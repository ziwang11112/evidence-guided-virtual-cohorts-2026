# Focused primary-source check of new reviewer leads

Checked 1 November 2026. This is a bounded verification of three high-impact leads from the ChatGPT review, not a new systematic literature review or reproduction. No biomedical records or generators were run. Reviewer opinions and asserted performance remain distinguishable from independently reproduced findings.

## KMGen

The [official MLHC 2026 proceedings page](https://proceedings.mlr.press/v340/jiang26a.html) confirms **KMGen: A Skill-based Approach for Synthetic Individual Patient Data Generation**, by Jalen Jiang and colleagues, PMLR 340:755–814. Its abstract describes agentic Kaplan–Meier extraction, LLM extraction of arm-level information from trial records, and mechanistic sampling of patient trajectories. It reports three held-out oncology trials with 30 regenerations each. The linked [author repository](https://github.com/chufangao/kmgen) is public and contains implementation/skill files; it was not executed here.

This establishes a close predecessor for published-information-to-program-to-patient-data generation. It does not by itself establish heterogeneous external-study transfer into a new target population. The abstract supports the broad reviewer summary; the stronger statement about exact access to measured patient records in its evaluation was not independently verified in this bounded check. The proceedings PDF link returned an unsupported content-type in the web tool; no exhaustive full-paper or code audit is claimed.

## ISPOR case study

The [official ISPOR 2026 abstract](https://www.ispor.org/conferences-education/conferences/past-conferences/ispor-2026/program/program/presentation/ispor-2026/poster-session-1-4/generative-ai-secures-synthetic-datasets-of-nsclc-trial-cohorts-for-rwd-analysis-a-privacy-preserving-case-study) confirms Manuel Cossio and Ramiro Eugenio Gilardino's CHRYSALIS-2 case study. One Agent extracts published trial characteristics; another writes Python synthesis scripts. Evaluation compares outputs with reported source characteristics, and fabricated low-frequency mutations persist after refinement. This is a conference abstract/poster, not evidence of independent cross-population transfer or a general privacy guarantee. No executable repository was verified. It is a legitimate direct precedent for the broad workflow, not proof that the present scoped research question is already resolved.

## Statistical synthesis predecessor

[Bonofiglio, Schumacher and Binder (2020)](https://onlinelibrary.wiley.com/doi/full/10.1002/sim.8470), Statistics in Medicine 39:1183–1198, uses marginal moments and correlations from data-holding centers to generate Gaussian-copula pseudo-data and recover multivariable inferences. Its input regime includes same-source joint summaries. A comparator for our external-evidence regime must not receive an unavailable target correlation matrix. The publisher page confirms the methodological overlap and links the [authors' application code](https://github.com/bonorico/gcipdr-application-to-multi-center-IST-data); performance was not independently reproduced.

## Decision

Add these verified leads to the next related-work assessment. Do not claim that Agent-authored data generation itself is new. Preserve the distinction between same-source reconstruction and external-study transport. Neither these papers nor agreement among model reviewers establishes our proposed improvement or publication readiness. All venue suggestions remain conditional opinions, not acceptance forecasts.
