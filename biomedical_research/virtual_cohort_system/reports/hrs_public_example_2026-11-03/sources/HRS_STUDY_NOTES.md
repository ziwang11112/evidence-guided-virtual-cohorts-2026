# HRS measurement and study scope

The original analytic sample comprises 11,509 HRS participants aged 50 or older with valid HbA1c from 2006/2008 blood collection, after the paper's exclusions. HbA1c is measured in percent. Memory is delayed recall of a 10-word list, transformed using the cohort-specific mean and SD among participants aged 50–65 at HbA1c measurement. The exported memory model already uses this standardized scale; the adapter does not re-standardize its synthetic outcome. CSES is a continuous childhood socioeconomic composite. These definitions are reported in [the primary paper's Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC8338788/).

The source code supplies additional generation choices: sex/race/age cells, continuous uniform age within bins, conditional parametric families, and four balanced visits. Actual age increases by elapsed years; the analysis age covariate is centered at 60 and divided by 10. Baseline HbA1c and other covariates stay fixed. The original 43,500 longitudinal observations and synthetic 46,036 balanced observations differ.

These public aggregates and source modeling choices define this recipient-stage example. They support exposed-summary consistency assessment, not reconstruction of individual records or independent verification of causal assumptions. Paper Tables 2/3 remain rounded, author-reported reference quantities.
