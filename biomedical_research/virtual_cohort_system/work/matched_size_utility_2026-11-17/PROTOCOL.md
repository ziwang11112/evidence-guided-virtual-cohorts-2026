# Matched-size scientific-use diagnostic: implementation binding

17 November 2026. This unit implements the existing 16 November `MINIMAL_VALIDATION_PROTOCOL.md` without changing its scientific design. The user authorized this execution on 17 November.

The frozen source inputs are the closed lifestyle inventory, original analysis operator/adapter, the real source and all six final saved tables. No generator is imported or executed. No API, source search, download, new virtual cohort, training or source/target-informed model revision occurs.

For each trait separately, use positive finite outcomes from adults older than 18 with valid age/sex/lifestyle. Expected real n: BMI 1,189; total cholesterol 400; HDL cholesterol 405. The six virtual tables each contain 1,226 complete rows. Keep six group-by-sex stratum counts equal to the real available-case counts for that trait. Do not match age or outcomes. Real and virtual samples are drawn with replacement within their own empirical pools.

Use 500 replicates, root seed 16161, explicit NumPy PCG64 and SeedSequence spawn keys `(trait_index, replicate_index, stream_index)`. Stream order is real A, real B and six virtual tables in dataset-ID order. Each comparison shares its replicate's real B. Save all 12,000 stream definitions before any real or virtual resampling.

Each sample is passed to the original `analyze_frame` via a thin trait-selection wrapper; unused traits become NaN, and only pooled contrasts and the analyzed trait's sample SD are extracted. Bootstrap copies receive temporary unique IDs. No interaction-based selection, multiplicity selection, trimming, or reranking of generated tables is performed.

Primary descriptive outputs are all nine raw-unit pooled group contrasts, with `real A − real B` and each `virtual − real B` difference. Record signed/absolute mean, median, and 2.5%, 25%, 75%, 97.5% empirical quantiles (NumPy linear). Report all three SD diagnostics and retain original unmatched point estimates. No resampled individual rows or row-selection arrays are persisted.

Execution is capped at one hour and 12,000 bootstrap trait-sample evaluations. Original-table equivalence checks and prespecified independent replays are validation overhead, separately counted. Failure slots stay in the inventory; they are not replaced. A partial run stays partial and cannot be silently restarted or expanded. Progress checkpoints preserve the completed ledger.

Implementation review before execution: invented fixture checks for schema, raw-unit conversion, immutable inputs, stratum matching, deterministic and distinct streams, missing-cell failure, constant/singular fits and ineligible observations; inspect frozen input hashes and all six slots. Freeze runner, wrapper, summarizer, independent-review script, this protocol, source design, input inventory, preflight report, test receipt and stream map.

Independent numeric review: use a separately written centered-age, raw-outcome QR regression for every original table/trait and for replicates 0, 249 and 499 of each trait and all eight streams (72 prespecified bootstrap replays). Verify every saved difference and aggregate summary from saved per-sample estimates. This is root-authored independent numerical implementation, not external expert review.

Interpretation: these empirical resamples condition on the same available-case pools and group/sex composition. They are not independent cohorts, survey/cluster-valid population intervals, clinical-equivalence margins or source/model/transport uncertainty. Matching changes composition as well as sample size, so effects cannot be attributed to sample size alone. The original source-rich, previously exposed-reference setting remains explicit. Retain the full profile and close with a bounded scientific-use judgment.
