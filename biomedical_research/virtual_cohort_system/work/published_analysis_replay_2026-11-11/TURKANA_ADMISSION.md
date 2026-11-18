# Turkana published-analysis reuse: source and schema audit

11 November 2026. Reviewer: `/root/published_case_admission`.

**Decision:** a bounded Methods-guided reuse of the paper's age/sex-adjusted biomarker-correlation operator is feasible on existing BMI, TC and HDL fields. This is not an unchanged original-code rerun, the complete original correlation matrix, or reproduction of the paper's lifestyle/mediation findings. Freeze investigator-resolved details before any new reference computation. All six current frozen lipid constructions and their three fixed draws should be retained, without regeneration or output repair.

## What the original study actually specifies

Lea et al., Science Advances 2020, DOI [10.1126/sciadv.abb1430](https://pmc.ncbi.nlm.nih.gov/articles/PMC7577730/), Methods, "Experimental design and sampling overview" and "Data filtering and processing": recruitment was healthy adults strictly older than 18. Exclusions include pregnancy, extreme biomarker outliers, missing subsistence/interview information and missing age/sex. Biomarkers are centered and scaled by their SD; no log transform is specified for this operator. The original outlier threshold is not defined in the inspected passages.

The [original supplement](https://gurven.anth.ucsb.edu/sites/default/files/sitefiles/papers/lea%20et%20al.%202020%20supplement.pdf), PDF page 7 (zero-based page 6), "Correlations between measures," describes Pearson correlations after regressing out age and sex and summarizes squared correlation. It does not specify common versus pairwise complete cases, sex reference coding, a named correlation figure/table, or implementation code. The original biomarker set is larger than our three-field subset.

The main paper's availability statement links [Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.2z34tmpjk). The page lists one text data file, not an analysis script. A small targeted code search did not locate the authors' analysis code; this is not proof that no code exists elsewhere.

## Existing material and exact availability

- Patient file, not decoded by this review: `work/scaleup_2026-11-01/private_data/22Jul20_for_Dryad_noIDs.txt`. Actual current SHA256 rechecked: `7508097bd6578307a55aef793c15b4c26d2346e2d8e60e55ba8bf9d5254037f9`.
- Existing metadata: `work/scaleup_2026-11-01/TURKANA_SCHEMA_AUDIT.json`. Fourteen columns, including age, F/M sex, BMI, TC, HDL and lifestyle. The historical five-field nonmissing count is 397; it is not a new count under a strict age >18 rule.
- Canonical mapping: `Age -> age`, `Sex -> sex`, `BMI -> bmi`, `Total cholesterol -> total_cholesterol`, `HDL cholesterol -> hdl_cholesterol`. Reference lipids are mg/dL. Current generated lipids are mmol/L and their existing documented map is multiplication by 38.67.
- Current immutable generators: `work/request_only_repeatability_2026-11-11/episodes/LIPID_{BASE,WORKFLOW}_R{1,2,3}/candidates/v001/generator.py` and their final selections/evaluation outputs. All delivered schemas contain only id, age, sex, BMI, TC and HDL. Some programs contain latent lifestyle mixtures, but they do not deliver a measured or validated lifestyle column. Do not expose or relabel these hidden groups as the original three lifestyle categories.

## Proposed minimal executable reuse, not yet an analysis release

Evaluate all three pairs: BMI–TC, BMI–HDL and TC–HDL. Regress each biomarker on an intercept, continuous age and a binary sex indicator on the chosen rows, then compute Pearson correlation between the two residual vectors. Report signed r and r squared. Do not additionally adjust for BMI in the TC–HDL pair: that would revert to our older project estimand rather than this source operator. No log transform, no invented lifestyle label, no target-based exclusion and no generated-value correction.

For a compact three-by-three matrix, one common complete-case subset is a reasonable **investigator choice**, provided explicitly frozen and applied identically to real and generated tables. Pairwise deletion is also possible but would answer a different selected-sample question. The original passage does not resolve this choice. Centering/scaling each outcome before an intercept-containing OLS fit does not change the signed residual Pearson correlation; an implementation should verify this algebraic invariance. Sex reference choice also leaves the projection/residual unchanged when the same two groups and intercept are used.

Apply strict age >18 if intending to follow the paper's recruitment rule. Existing K02 used age >=18, so new counts may differ. Pregnancy/interview/fasting fields are unavailable in the released schema; their original filtering cannot be independently reconstructed. Do not claim that omission means everyone passed those exclusions. Extreme-outlier filtering cannot be reproduced without a threshold. A declared reuse of the available processed deposit without further outlier trimming is defensible as a partial reanalysis, not an exact original-sample reconstruction.

The supplementary paragraph does not supply these three individual pair-specific reference values. Compare new analysis results from the public processed real file with the same frozen operator on existing synthetic files; do not pretend that our new numerical values were published. No three-pair multiple-testing claim can reproduce the paper's whole-biomarker FDR family. Inference based on independent rows adds assumptions because the deposit lacks site/household identifiers; use point estimates and explicitly descriptive uncertainty if needed.

## Why the main original application cannot simply accept current virtual tables

The main lifestyle models require `Lifestyle category`, which is absent from generated outputs. Later dietary mediation and early-life models require further fields absent even from the released patient table. Supporting those applications would require a new, scientifically specified data-generation task, not merely a schema adapter. This audit does not authorize or recommend adding that task to the current unit.

## Activity and exposure

Only source text, existing metadata and generator code were inspected. A file hash read bytes without parsing participant values. No target correlation, mean, regression or new result was computed or read. No generator/API run, participant row decoding, new data download, external contact or old-file edit occurred. Browser source traffic was unmetered. Original-paper methods retrieval exposed adjacent qualitative results and generic correlation summaries already documented in historical admission; the paper and family remain exposed development, not a fresh confirmation. Search results also returned unrelated articles; none was admitted or used.
