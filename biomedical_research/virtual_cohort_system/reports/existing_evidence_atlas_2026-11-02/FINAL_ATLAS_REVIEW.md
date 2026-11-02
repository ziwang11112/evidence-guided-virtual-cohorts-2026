# Independent atlas review

2 November 2026. Scope: the existing-evidence atlas and its frozen aggregate/protocol sources. No participant tables, generated table rows, new scientific analysis, source search, generator execution or old-file modification was used in this review. The builder was read but neither imported nor executed as the verification oracle.

**Disposition: numerical extraction, coverage, retention metadata and reference-band semantics pass.** No numerical or scientific-analysis blocker was found. The small presentation corrections below should accompany publication of the standalone figures. Full rendered-image layout QA remains the coordinator's separate check.

## Independent verification

A separate inline Python check read the three original aggregate reports and the CHNS inventory, selected identities directly from their native fields, and compared every atlas CSV/JSON record. It also cross-checked the ENSANUT entries against the earlier `results_report/all_31_endpoints.csv`, rather than relying only on the atlas builder's choice of JSON source.

| Case | Included frozen quantities | Generated estimates | Unique stored table hashes | Seeds |
|---|---:|---:|---:|---|
| M17-B | All 8 locked endpoints | 48 | 6 | 17111, 17112, 17113 |
| ENSANUT cycle 2 | All 3 primary questions and the prespecified Q2-minus-Q3 companion | 24 | 6 | 18203, 18211, 18223 |
| CHNS F2 | All 3 primary estimands | 18 | 6 | 1701, 1702, 1703 |

All 90 records agree exactly between CSV and JSON after parsing numeric fields. Every generated coefficient, reference coefficient, reference lower/upper bound, reference N, generated N, construction identity, seed and stored table hash agrees with its original report. All 24 ENSANUT generated coefficients and all four reference values/bounds also agree exactly with the older all-31 CSV. No rounding or unit conversion was applied to the extracted numbers.

The records contain 15 case-specific quantities and 18 distinct table hashes. Each construction/seed's initial and retained final/revised entries have equal stored hashes and equal analysis results; all associated statuses are successful. Thus the 36 scheduled labels correctly reduce to 18 unique tables. This verifies retention using the frozen reports/inventory; it does not independently rehash generated table files, which were deliberately not opened.

The reported totals are simple inventory arithmetic: 6×320 + 6×2,000 + 6×3,000 = 31,920 fictional rows, and 320 + 6,931 + 6,631 = 13,882 case observations. The latter is not a pooled analysis population. Neither 90 estimates nor repeated seeds constitute independent scientific replications.

## Definitions, units and uncertainty

- **M17-B:** all eight frozen definitions agree with `docs/M17B_WHOLE_COHORT_PROTOCOL.md`. The curvature quantity is already the fixed second difference, twice the fitted quadratic coefficient; the atlas does not multiply it again. The interaction is the female-minus-male BMI slope difference. Reference bands are the existing normal HC3 95% intervals conditional on the selected unweighted quota sample, not NHANES survey inference or transport uncertainty. The curvature and interaction bands correctly retain their zero crossings.
- **ENSANUT:** the protocol requires Q1, Q2, Q3 and Q2-minus-Q3. The companion is a descriptive coefficient change after glucose adjustment, not mediation. The reference-stability metadata records 399 attempted and 399 valid replicates, linear 2.5th/97.5th percentile bands and no confidence-coverage claim. The plot legend correctly calls these stability bands rather than confidence intervals. HbA1c percentage points per decade and per five BMI units remain on their original scales.
- **CHNS:** E1/E2/E3 match the frozen equations in `f2/analysis_plan.json`. Percent-valued HbA1c coefficients are correctly labelled percentage-point changes without rescaling. Per-year age and per-one-unit BMI scales remain distinct from ENSANUT. The report records available CR1/t 95% intervals with 218 communities and 217 degrees of freedom, conditional on the selected complete-case reference. No generated inferential intervals are invented.

The source review's ENSANUT loader recommendation named the older CSV; the implementation uses its original aggregate JSON instead. The exact independent cross-check above resolves that substitution for the four displayed quantities. The full all-31 diagnostic table remains relevant supporting evidence.

## Presentation corrections and publication conditions

1. The M17 `bmi_sex_interaction` unit currently reads `Urate slope difference per 5 kg/m²`. Add the missing outcome unit, for example `Urate: mg/dL per 5 kg/m², female − male`. The numeric values are correct.
2. The plotted markers are labelled `Draw 1/2/3`, while the machine-readable table correctly records actual seeds. Add the case-specific seed mapping to the legend or accompanying caption to satisfy the read-only review's identity requirement.
3. Accompany standalone plots with the already-required version and diagnostic context: M17/ENSANUT are historical supporting implementations, CHNS is the current-system case; link the complete original diagnostics. The current plot titles identify cases/releases but do not themselves state that implementation distinction. Preserve the existing warnings against pooled accuracy, equivalence from band membership, successful repair, or biological discovery claims.
4. In the subtitle or caption, make `No individual input` explicitly refer to **generation**. Reference estimates were originally computed from measured participant cohorts, whereas this atlas only rereads frozen aggregates. The distinction is needed when the figure is viewed without the surrounding report.

These are bounded presentation corrections, not requests for more experiments, revised generators or a larger evaluation framework. A figure's claim that the same table supports several analyses should mean that it can be reused for those calculations, not that every resulting association agrees adequately with the measured reference.

## Code and artifact integrity

Source inspection found no regression fitting, resampling, new scientific statistic, target-row access, favourable endpoint selection or composite accuracy calculation. The builder opens exactly four hardcoded aggregate/inventory JSON inputs, checks their hashes before and after extraction, and writes descriptive records/plots. It does not follow embedded participant paths. This review's independent check verified all four input hashes, all eight output hashes and the script hash against the manifest. The check was not a rerun of the original scientific analyses.

Reviewed SHA256 identities:

| Artifact | SHA256 |
|---|---|
| `build_atlas.py` | `5e48f7fa6d30dcf0d013692c90cd56d6ee943f021d3d883faf1fa798d9128f23` |
| `analytical_reuse_points.json` | `a6ee125b4747bebc634db48a0ce5d051a52595ef3a01f7aabae0b0eda1e29631` |
| `analytical_reuse_points.csv` | `64b87a73f249dbfc1091560139aa26f58d0d2f55ce0f9793bbbb4f3dcae4aeef` |
| `ATLAS_MANIFEST.json` | `e38ca6a32201a5312dc264b87f260df3fe8ac6ac7cc1cfe6e6d9de6815622ccd` |
| `READ_ONLY_ATLAS_REVIEW.md` | `04a7d8756734b9f0eca117eefe302ed3496fc658ef7d640517e15781b60ab605` |

The eight reviewed CSV/JSON/PNG/SVG hashes are recorded in that exact manifest. This report wrote only `FINAL_ATLAS_REVIEW.md`; the results, code, figures, protocols and source reports were unchanged by this reviewer.

## Addendum: reviewed presentation repairs and public replot route

The coordinator subsequently corrected the explicit mg/dL interaction unit, replaced draw numbers with actual case-specific seed labels, labelled M17/ENSANUT historical implementations and CHNS semantic-feedback v1, and changed the footer to state that the same table **was used** for all displayed analyses. These repairs close items 1 and 2 and the plot-title portion of item 3 above. Full diagnostic links and limitations remain the accompanying README's responsibility; that README was not yet present at this check. Item 4 can be resolved there or in a figure subtitle/caption.

An independent post-repair comparison again found all 90 generated/reference/band tuples exactly equal to their original frozen reports, CSV/JSON field parity, 18 unique stored table hashes, and matching four-input/eight-output/script manifest hashes. The unit text change did not alter scientific numbers.

The added `--replot` branch reads only the adjacent `ATLAS_MANIFEST.json` and `analytical_reuse_points.json`, verifies the aggregate-point hash, checks 90 rows/18 hashes, renders into a separate directory, and returns before `load_inputs()` is reached. Source inspection therefore supports its no-original-workspace/no-participant-read boundary. It performs no scientific fit or recomputation of intervals. This is a display-reproduction route for the released aggregate snapshot, not an independent validation of that snapshot's scientific correctness. Its actual exported execution and new image-layout QA remain the coordinator's checks; this reviewer did not redundantly run them.

**Updated disposition: approved for the bounded retrospective aggregate atlas, with the already-stated diagnostic and generation-input context in the accompanying publication text. No new numerical blocker.** This does not approve broader pipeline, superiority, transport, equivalence or biological-validation claims.

Updated reviewed identities (superseding the earlier script/points/manifest identities above):

| Artifact | SHA256 |
|---|---|
| `build_atlas.py` | `791eeb7a719948e0f124214057a6c51ceb9cb14bb45efc5c3c0c5fa20b409c40` |
| `analytical_reuse_points.json` | `25716b87dc6558951c7724e928f8e9c56fa6ea0ee9ab40734af3b91d218b1321` |
| `analytical_reuse_points.csv` | `b0c3337b0f00ff5c85ee6aa78d36822b5d4c27c57d88dad6792e14c84ceef323` |
| `ATLAS_MANIFEST.json` | `f1597c2563415fadd6ecc2f4fd35d38c9389829616dcf1c837cf936a25a829bd` |
