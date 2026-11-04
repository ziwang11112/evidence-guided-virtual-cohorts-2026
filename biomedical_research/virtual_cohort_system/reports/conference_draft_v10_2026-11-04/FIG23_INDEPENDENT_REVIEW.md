# Independent review of Figures 2 and 3

**PASS.** The reviewer independently loaded the original frozen main-study and historical-information reports, rather than calling the author's verification function. All **306 seed statistics, 102 constructor-by-analysis means, 102 observed seed ranges, 11 reference estimates and 9 available reference intervals** match their source pointers. The two historical correlation references correctly have no interval. Units retain the distinction between CHNS per-unit predictors and ENSANUT per-10-year/per-5-BMI predictors.

The six Figure 2 panels retain 24 constructions and 72 final tables. The five Figure 3 panels retain six constructions and 18 distinct delivered tables; 42 executions and 24 unique contents including trials remain explicitly distinguished in the caption. Independently inspected PNGs display unfavorable estimates as well as favorable ones, do not clip negative values, and use group offsets only to separate authors and seeds. The source renderer loops over every bound series; no best-seed selection or cross-condition pairing is introduced.

The captions correctly distinguish seed ranges from confidence intervals; CHNS CR1-t reference intervals from ENSANUT resampling stability bands; and supplied-summary reconstruction from held-out prediction. All constructor, seed, reference, and source-file hashes checked successfully. The manuscript's individual figures can therefore be used with these captions.

This check audits aggregate values and presentation only. It does not rerun or recertify the clinical analyses, source extraction or transport assumptions. No patient/generated row was read and no old file changed.

Reproducible review: `check_fig23_independently.py`. Machine-readable result: `FIG23_INDEPENDENT_REVIEW.json`. Separate figure-author review should remain in the package.
