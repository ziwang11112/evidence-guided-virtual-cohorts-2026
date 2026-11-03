# Scientific-utility figure captions

These are new display derivatives of retained aggregate reports. No individual clinical records or generated-row files were read. The two experiments remain separate; matching colors do not make their conditions interchangeable.

## Figure 1. Scientific analyses of evidence-generated cohorts

All six prespecified HbA1c regression coefficients in the main developmental experiment are shown: CHNS 2009 BMI adjusted for age/sex, glucose adjusted for age/sex, and age adjusted for sex/BMI/glucose (A–C); ENSANUT 2018 age adjusted for sex/BMI/glucose, BMI adjusted for age/sex, and BMI additionally adjusted for glucose (D–F). Axes retain each predictor's original scale and cannot be compared as a common accuracy scale. E0 supplies marginal/basic external evidence; E1 adds qualified relational evidence. Every A01–A05 construction is displayed within each condition. Author labels across E0 and E1 are unpaired and are not connected. S01 denotes the original prescribed statistical construction for each condition, not the later purpose-built R30 statistical supplement.

Small dots show the three final seeds per construction; vertical marks show Agent construction means, diamonds show statistical construction means, and horizontal segments span each construction's three-seed minimum and maximum. These ranges are conditional simulation variation, **not confidence intervals**. All 24 constructions and 72 final tables are represented across their three analyses (216 seed-level coefficients); each table contains 3,000 synthetic rows. The solid line is the previously exposed sample-reference estimate. CHNS shading is its selected-sample community-cluster CR1-t 95% interval. ENSANUT shading is an empirical cluster-resampling stability band for its equal eight age/sex-cell analytical standard, not a national survey interval. Neither band is an equivalence margin or acceptance region. The two populations, eligibility rules and estimators remain distinct; no pooled inference or overall ranking is implied. All effects, including negative and attenuated results, are retained.

Files: `figures/figure1_main_scientific_utility.svg` and `.png`.

## Figure 2. Scientific use with and without target summaries

Final results from the separate historical CHNS information experiment are shown for all six Agent constructions: L01–L03 received external literature, while R01–R03 additionally received 30 explicitly supplied target summaries. Panels A–C show the same three CHNS regression definitions stated above; D–E show glucose–HbA1c Pearson and Spearman correlations. All five displayed statistics were among the target summaries provided to R. Their agreement therefore evaluates **supplied-summary calibration**, not withheld-outcome prediction or new independent validation. The L/R experiment uses different authors and a different historical protocol from the main E0/E1 experiment; differences between figures are not treated as a controlled causal contrast.

Small dots, vertical means and horizontal ranges represent the three final seeds per author, with 3,000 rows per table. All 18 final tables contribute to the five panels (90 seed-level statistics). Author identifiers in L and R are unpaired. Seed ranges are not confidence intervals. Solid lines mark the exposed CHNS selected-sample reference. Shading in A–C retains the community-cluster CR1-t 95% reference intervals; correlation reference intervals were unavailable and are not fabricated. The repeated use of these tables for several analyses does not create independent clinical replicates. Only final-stage records are plotted; the retained historical study records initial stages and no-change decisions separately. The new custom statistical supplement remains in its own supplemental report rather than becoming the organizing comparison here.

Files: `figures/figure2_chns_information_conditions.svg` and `.png`.

## Numeric provenance and rebuild

Run `python build_utility_figures.py` from any working directory. The script locates hash-bound aggregate files under the local `work` or public `reports` layout, verifies their existing independent-audit bindings, and checks stored means/ranges against their three seed values. It does not import an evaluator or a generator.

`AGGREGATE_SOURCE.json` records all plotted values and exact JSON pointers. `NUMERIC_MANIFEST.json` binds the source reports, source audits, plot script, captions, data payload and final PNG/SVG files. Graphical resizing does not change the underlying statistical values. Neither figure introduces new scientific calculations, fit selection, equivalence thresholds or significance tests.
