# M13-B evaluator: pre-access specification

This evaluator implements the frozen pilot panel for NHANES 2017–2018 `DXDTOPF`, in percentage points. Development and validation used invented fixtures only. It neither imports nor executes submitted generator code. Input rows stay private; the only persisted evaluation outputs are aggregate JSON and CSV. The target result title explicitly names the complete-covariate, valid-scan domain.

## Files and command

```powershell
python work/m13b/evaluator/bodyfat_evaluator.py --full-frame PRIVATE_FULL_FRAME.csv --manifest work/m13b/generated_manifest.json --output-dir NEW_AGGREGATE_DIRECTORY
```

`generated_manifest.json`, `protocol.json`, and `preaccess_freeze.json` must share a directory. The output directory must not already contain `aggregate.json` or `aggregate.csv`. Successful CLI stdout contains completion status and table/panel counts only. Failure messages use fixed categories without row identifiers, values, paths or tracebacks.

## Exact input schemas

CSV column names **and order** are enforced. IDs are unique nonempty strings with no leading/trailing whitespace. Missing private numeric values are empty CSV fields; textual sentinels, infinities, duplicate keys, duplicate columns and malformed row widths are rejected.

Private full-frame columns:

```text
id,SEQN,WTMEC2YR,SDMVSTRA,SDMVPSU,RIDAGEYR,RIAGENDR,RIDRETH3,BMXBMI,DXAEXSTS,DXDTOPF
```

The custodian supplies all DEMO records with finite positive MEC weights and complete design fields, with components joined one-to-one on SEQN. Every full-frame row has an opaque ID. SEQN, stratum and PSU must be finite integers. Missing age, BMI, scan status or body-fat outcome does not delete a row from the design frame. Any finite body-fat value outside `[0,100]` fails integrity validation. A singleton full-frame stratum fails, without a lonely-PSU adjustment. The evaluator can validate the supplied frame's integrity but cannot prove acquisition completeness without the custodian's source receipts.

Generator observed columns:

```text
id,age,bmi,male,asian,inv_bmi,male_inv_bmi,asian_inv_bmi,male_age,asian_age
```

Generated columns are exactly those ten columns followed by `bodyfat`. The observed IDs must exactly equal the union of the primary and extension domain IDs; generated IDs must exactly equal observed IDs. Row order may differ and is aligned by opaque ID. Every preserved covariate is checked against custody and every generated covariate against observed input with only a floating-point CSV serialization tolerance (`rtol=atol=1e-12`). `male` is 1 for RIAGENDR=1, otherwise 0 for RIAGENDR=2. `asian` and its interactions are zero in the admitted White/Black domain. Reciprocal BMI and interactions are recomputed from age, BMI and male. Race remains evaluator-only through RIDRETH3. Extra DXA-family, design or other columns fail whitelist validation.

Manifest schema is the controller's single strict version, integer `schema_version: 1`, with top-level `observed_path`, `preaccess_sha256`, and `tables`. Each table has exactly `table_id`, `kind`, `builder`, `candidate`, `seed`, `path`, `status`, plus:

- Agent: `execution_receipt_path`, `execution_status`; complete tables additionally have `sha256`.
- Reference: `reference_receipt_path`; complete tables additionally have `sha256`.

Failed tables have null `path` and no SHA256. All complete tables require a verified SHA256 before they are read. Receipt paths are metadata; the controller, not this evaluator, verifies generator execution receipts. The evaluator checks the pre-access freeze digest, its own code hash and the protocol hash, then requires the manifest roster to equal the protocol roster exactly. It additionally enforces the fixed 16 identities: `build01`/`build02` × `initial`/`source_reviewed` × seeds 33101, 33102, 33103; `gallagher_mean`; and `gallagher_normal_33101`, `_33102`, `_33103`. Complete reference formula construction is the controller's responsibility.

## Fixed scientific computation

Eligibility requires age 20–59, RIAGENDR 1/2, RIDRETH3 3/4, finite BMI, DXAEXSTS exactly 1 and a finite body-fat endpoint. Primary BMI is `[18.5,30)`; extension BMI is `[30,35]`. The design frame remains intact for every calculation. There are 62 endpoints per table:

- Primary, each sex: weighted mean; age/race-adjusted BMI slope per 5 kg/m²; BMI/race-adjusted age slope per 10 years; quadratic BMI second difference `1.28 * beta_B2`.
- Extension, each sex: weighted mean and the same two linear slopes; no curvature.
- Twelve sex × age (20–39/40–59) × BMI (`[18.5,25)`, `[25,30)`, `[30,35]`) cells: quartiles and IQR.

Linear design is `[1, (BMI-24)/5, (age-40)/10, Black]`; curvature adds squared centered/scaled BMI. Means use an intercept-only fit. The full-frame sandwich uses nested `(stratum, PSU)` score totals, explicit zeros for excluded rows/PSUs and stratum factor `m/(m-1)`. Inferential df is contributing-domain PSUs minus contributing-domain strata. Two-sided pointwise 95% intervals use Student t with this df. There is no finite-population correction or log/ratio transformation.

Each projection or cell requires n≥30, Kish n≥20, ≥8 contributing PSUs and domain df≥4. Projection designs additionally require full rank and n greater than their parameter count. Every failed endpoint remains scheduled with counts and failed gates; no bin merging, rank-driven formula substitution, or relaxed thresholds occurs.

Quantiles aggregate tied values and select the first observed value whose cumulative weight reaches the specified probability, with no interpolation. **Quartile and IQR intervals, Woodruff intervals and measured-reference inclusion indicators are deliberately omitted in this pilot.** All distribution discrepancies are points only. For linear estimands, signed errors are generated minus measured and intervals come from the paired response difference on the identical full frame. Generated and paired intervals condition on the frozen model and realized draw.

Aggregate JSON includes deterministic exclusion flow, weighted/unweighted completeness, measured and all 16 table panels, failed tables, and separate arithmetic mean/min/max over all three draws per builder/candidate/reference group. If any draw is unavailable, the group summary remains incomplete and its summary values are null. No pooled builder result, combined interval, Rubin combination, overall success score or effect tolerance is introduced. Aggregate CSV contains the measured panel and 16 table panels (1,054 rows), with gates and paired intervals; JSON is authoritative for seed summaries and metadata.

## Actual checks and limitations

`python -m unittest test_invented -v` ran **22 tests, all passed**, after controller-manifest integration. Tests include exact rational mean/variance with an empty-domain PSU; hand-calculated WLS covariance; coefficient agreement with statsmodels WLS; nested PSU handling; domain df and t critical value; weight scaling; row permutation; off-domain NaNs; paired differences; curvature multiplier; quantile ties and boundaries; all domain/scan/support limits; sparse/rank gates; whitelist/key/covariate failures; strict roster and hashes; failure-slot retention; and a full 16-table CLI run using only freshly invented CSVs and freshly invented protocol/freeze fixtures.

The independent audit agent separately checks the scientific kernel and formula implementation in `../audits/`; that audit is a distinct record. No R `survey` cross-validation was available or claimed. WLS coefficient agreement does not validate this variance implementation; hand-calculated fixtures and independent formula review provide the variance checks. Tests do not establish coverage, transport validity, clinical equivalence, source-parameter uncertainty or individual predictive accuracy.
