# Candidate 3: LARS / Efron diabetes data

31 October 2026. Metadata-only admission check. No data file, model fit or original paper result table was opened. Decision: **do not admit for the current biomedical transfer case**.

## Verified documentation

- [NCSU source description](https://www4.stat.ncsu.edu/~boos/var.select/diabetes.html) links the original LARS data and distinguishes it from standardized R-package data. It describes 442 patients, ten baseline variables and a one-year disease-progression response. Named variables include age, sex, BMI, average blood pressure and six serum measures.
- [Official scikit-learn description](https://scikit-learn.org/stable/datasets/toy_dataset.html#diabetes-dataset) describes the centered/scaled implementation and identifies the serum variables. It explicitly leaves the triglyceride transform uncertain ("possibly log").

These pages establish a readily available statistical example, but the checked documentation does not adequately specify clinical recruitment, geography, eligibility, medication, assays, original units or sex coding needed to transport external biomedical evidence. An unscaled file is not automatically a fully documented clinical cohort. This decision is based on insufficient contextual metadata, not a measured unfavorable effect or an assertion that the data are artificial.

## Exposure and source boundaries

A broad metadata search returned third-party teaching snippets with example patient rows and variable summaries before the official pages were opened. Those incidental snippets are not used as evidence or generation inputs. No patient file was downloaded and no candidate-data analysis was performed. The candidate is rejected for the current cycle and must not later be described as completely unseen. The misleading third-party expansion of some serum abbreviations was not adopted; official documentation controls interpretation.

The documentation cites Efron et al. 2004, but its original research paper was not opened or counted as a newly read primary study. This check consumed one of the three candidate-source slots and zero primary-paper slots. Downloads saved to the workspace: zero.
