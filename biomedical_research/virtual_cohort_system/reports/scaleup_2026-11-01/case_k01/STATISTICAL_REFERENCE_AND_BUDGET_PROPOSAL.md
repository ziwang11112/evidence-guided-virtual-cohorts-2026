# K01 statistical reference and finite source budget

2 November 2026. **Scientific proposal; no case/global release, actual evidence fit or clinical sampling.** Root and independent reviewer accepted the formulas in principle before implementation. This document and its JSON are the concrete specification for review. Existing K02 and historical files remain unchanged.

## Decision and same-information scope

S01 is a transparent **independent-marginal completion reference**. It fits a small number of source marginal quantities analytically, states the unreported joint law and transports it by an explicit convention. It is not an optimized statistical competitor, causal model or claim that the evidence implies independence. All five Agents and S01 receive the same exact candidate packet: the seven selected MIND items and eleven Ayele covariate items, plus consistently labelled contextual evidence. No arm receives target rows, moments, composition, effects, desired signs, another constructor's results or extra private evidence. Agents choose their own joint structure and transport assumptions; S01's independence is not prescribed to them.

The candidate bindings are `evidence/MIND_REUSE_CANDIDATE.json` SHA256 `818382e977c429fbdb557c8554d0ad42ef4eb08192bb0d158fff46c5d8090b70` and `evidence/CANDIDATE_EVIDENCE.json` SHA256 `70d0a2c0d7b06d020699b2fa7db22dac9882ddf76ebc2b6b8f86a596834190db`. Exact selected IDs appear in the JSON. These are reviewed candidate inputs, not a live harness admission. A shared packet alteration requires a common pre-outcome version decision, not an extra private attempt.

Composite-diabetes ORs, abstract-only prevalence, other Bahendeka records and unrelated HbA1c evidence remain context-only. Neither a binary OR nor a marginal moment identifies the three continuous-glucose projections. Uncertainty about an estimate is not individual dispersion. The MIND SDs are reported individual SDs; their divisor and analytic weighting are unknown. S01 treats their squares as population marginal variances of an equal-weight approximation, not as verified population variances or conditional residual variances.

## Fixed S01 law and analytic derivation

The delivered schema is exactly `id, age, sex, bmi, glucose`, with string IDs, sex `F`/`M`, and units year, kg/m² and mmol/L. The scientific law has independent age, sex, BMI and glucose **within each source/donor context**. The same distribution forms and the same glucose law are used throughout; reviewed context-specific covariate margins and age selection vary. No separate outcome relationship is fitted for each source.

For a bounded age variable with source mean `a`, individual SD `s` and declared support `[L,U]`, set:

```text
m = (a-L)/(U-L)
v = (s/(U-L))²
k = m(1-m)/v - 1
alpha = m*k; beta = (1-m)*k
age = L + (U-L)*Beta(alpha,beta)
```

Require finite inputs, `L<a<U`, `s>0` and `0<v<m(1-m)`, yielding finite positive shapes. Otherwise stop; do not change the SD, bounds or family. This is a continuous-age approximation, not an asserted reconstruction of integer census-age recording or source imputation. MIND uses `[61,80]`; Ayele uses the methods `[25,64]` scenario while preserving the table-caption 25–65 inconsistency. Ayele's four printed age-category proportions are not fitted.

For MIND BMI and glucose, use independent lognormal marginals with reported arithmetic mean `x>0` and SD `s>0`:

```text
sigma² = log1p((s/x)²)
mu = log(x) - sigma²/2
X = exp(mu + sigma*Z), Z standard normal
```

This matches the theoretical mean/SD of the chosen lognormal scenario, not every finite sample, the original imputation process or assay. The positive shape is assumed; no mean/CI-to-SD conversion or target-informed tail fitting occurs.

For Ayele BMI, use **count-derived** probabilities `pL=65/872` and `pU=340/872`, with thresholds 18.5 and 25 kg/m²:

```text
zL = Phi_inverse(pL); zU = Phi_inverse(1-pU)
sigma = (log(25)-log(18.5))/(zU-zL)
mu = log(18.5)-sigma*zL
```

Require both probabilities strictly inside `(0,1)`, `pL<1-pU`, ordered positive thresholds, and finite positive sigma. The fitted outer events are `<18.5` and `>=25` for a continuous lognormal. **Do not fit rounded 7.5%/39.0% in place of these ratios.** Preserve printed percentages and the middle count `467/872` as source metadata. The printed middle interval `18.5–24.9` remains an unfitted literal diagnostic; the model's interval `[18.5,25)` is not silently claimed to be that source interval. No gap-closing or source-data correction is performed.

Source sex is Bernoulli Female with MIND `2049/3547` and Ayele `586/872`; the Ayele Male complement is `286/872`. These are explicit count divisions, not weighted population proportions. Printed Ayele 67.2%/32.8% remain rounding metadata; checks distinguish the count ratio from the printed percentage. Two complementary sex records are not two independent facts.

Ayele reports no continuous glucose marginal. S01 therefore copies the entire MIND glucose marginal to Ayele and the target **as an unsupported transport convention**. It supplies no glucose constraint for the Ayele source check. Serum laboratory overnight-fasting glucose, a mixed-feeding three-day capillary average and pooled released cleaned HAALSI POC values are different measurement operators. Equal numerical laws in mmol/L are a reference assumption, not evidence of assay, feeding, handling, timing, selection or population equivalence. No calibration factor is invented.

## Target transport and sampling

For each target row draw a donor label MIND/Ayele with probabilities exactly `(1/2,1/2)`. Within the selected donor, draw age from that donor's bounded-beta law **conditioned on age at least 40**, sex and BMI from its source marginal, and glucose from the shared independent MIND law. For a donor CDF `F`, this conditional draw is:

```text
q = F(40), respecting the source support boundary
age = F_inverse(q + (1-q)*U_uniform)
```

Require positive retained mass and a valid finite inverse-CDF result. Use direct standard inverse-beta-CDF sampling; no fitted numerical optimization, clipping, rejection repair or redraw of an unfavorable cohort. Fail on invalid domains, failed numerics or nonfinite output. Ordinary RNG implementation internals are not scientific fitting calls.

The donor weights stay one half **after the within-donor age conditioning**. This is different from drawing the original pooled mixture and filtering everyone below 40, which would change donor weights. The equal mixture, the within-donor selection law, unmodified sex/BMI margins, and transport of the same glucose marginal are explicit assumptions. No target demographic or feeding proportions select them.

The reference's maximum age support is 80, inherited from its donor law; this is a model limitation, **not an upper-age target eligibility exclusion**. Target validation keeps `age>=40` without an upper bound; source validation uses the separate reviewed source bounds. Shared canonical columns/units do not impose one global population bound. The current bridge/task packaging must enforce these context-specific rules explicitly before release; this document does not claim that existing bridge v1 already does so.

Mixing donors can induce associations among age, sex and BMI. Because the glucose law is identical and independent in both donors, S01's population adjusted BMI/age contrasts and sex×BMI contrast are zero **by completion assumption**. No target coefficient is supplied or estimated, no finite cohort is forced to have zero coefficients, and no such constraint applies to the Agents. This is a deliberately transparent limited reference; its failure would not establish failure of richer statistical models.

## Every shared item has a disposition

| Shared source records | S01 use and possible diagnostic |
|---|---|
| MIND age/BMI/glucose means and SDs: six items | Fit the corresponding theoretical marginals. Generated arithmetic means and sample SDs are descriptive proxies; declare SD `ddof=1` for the proxy while retaining the source's unknown divisor. No exact survey/imputation reconstruction claim. |
| MIND Female ratio: one item | Fit the exact reported-count division; descriptive generated Female proportion. |
| Ayele age mean/SD: two items | Fit bounded-beta moments under the methods-bound scenario; same SD/divisor caveat. |
| Ayele Female/Male: two items | Fit the count-ratio pair, not rounded percentages. Retain both printed records and the explicit derivation. |
| Ayele underweight/overweight: two items | Fit the exact outer count ratios with the lognormal inverse-CDF rule. Printed percentages remain distinct comparison metadata. |
| Ayele middle BMI category: one item | Unfitted diagnostic with the printed 24.9 endpoint; count ratio and printed rounding distinguished. |
| Ayele age categories: four items | Unfitted diagnostics under the explicitly reviewed completed-year interpretation `[25,35)`, `[35,45)`, `[45,55)`, `[55,65)`. Preserve the printed 25–34/35–44/45–54/55–64 labels. This is a declared continuous-age approximation, not an exact reconstruction or silent source rewrite; source support remains 25–64. |
| Binary ORs, abstract prevalence and other unselected records | Context only; no four-column numerical constraint, invented discrepancy or fitted coefficient. |

All 18 numerical candidate records are dispositioned; redundancy does not create 18 independent constraints. Strict source-estimator equality remains unavailable because weights, imputation effects, selection and some operator conventions are unverified. Report generated descriptive statistics separately. Numerical equal-weight proxy differences require the reviewed scenario/semantic mapping, including the explicit completed-year age bins and literal closed BMI middle interval. An unsupported declared operator is marked unavailable; this proposal does not authorize inventing an operator or modifying frozen semantic feedback to force a check. Unavailable checks do not trigger extra runs.

## Source schedule, feedback and finite computation

| Context | Seed per executed stage | Rows | Population bound |
|---|---:|---:|---|
| `source_mind_china_2019` | 3101 | 5,000 | 61–80 scenario, with source selection/timing caveats |
| `source_ayele_dire_dawa_2017` | 3102 | 5,000 | Methods 25–64 scenario; caption discrepancy retained |

Use those same fixed seeds for each constructor and a changed final stage. The target context is `target_haalsi_pooled_poc`, with 5,000 rows for each unchanged campaign seed **2101, 2102, 2103**. Per constructor/stage this is two source trials and three target trials. Source slots are additional, separately bounded executions, not hidden inside the target allocation.

| Accounting | Source | Target |
|---|---:|---:|
| Six constructors, initial | 12 slots / 60,000 rows | 18 slots / 90,000 rows |
| Initial plus final reservation | **24 slots / 120,000 rows** | **36 slots / 180,000 rows** |
| Maximum new attempts when all five Agents revise and S01 retains | **22 / 110,000 scheduled rows** | **33 / 165,000 scheduled rows** |
| All six retain | 12 / 60,000 scheduled rows | 18 / 90,000 scheduled rows |

These follow the K02 convention: retained final slots alias exact initial candidate/output identities, not new samples. S01's two final source and three final target reservations are nontransferable aliases. Failures, prelaunch errors, timeouts and interruptions consume their attempted slot and full scheduled-row allocation; actual produced rows can be fewer. No retry, replacement seed, warm-up cohort, hidden calibration or automatic partial resumption is permitted.

Each constructor receives **one initial source-feedback packet** containing both scheduled source reports, including failed/unavailable checks. It may revise once, retain or stop. Freeze a changed final before its one scheduled source/target pass. Final diagnostics are saved for reporting, never delivered for another revision; target scientific summaries are never feedback. Final delivery is primary; initial/final comparisons remain paired secondary analyses.

**S01 precommits retention:** if execution/contract integrity is valid, retain identical scientific bytes and alias initial outputs regardless of source Monte Carlo mismatch. Otherwise stop with failed/unrun slots retained. No recalibration, moment rescaling, family switching, seed selection or repair-and-retry scientific candidate follows source feedback.

Keep K02's common limits: each scheduled run at most 60 seconds, 1,024 MiB memory, 2,000,000 output bytes and 10,000 log bytes in the existing isolated executor. No host fallback or new scheduler. Each initial or changed-final construction permits at most one reviewed deterministic **analytic parameter-derivation job**, at most 120 seconds and 1,024 MiB. Reservation: 12 jobs; S01 retention reduces actual maximum to 11, with one for S01. Failure consumes the job. Preserve code/input/evidence/output hashes, finite-calculation description, elapsed time and status in the existing controller ledger.

No optimizer, model grid, quadrature, Monte Carlo fitting, generator call or pseudopatient row is allowed inside a derivation job. The standard CDF/inverse-CDF evaluations required by the declared formula/sampler are allowed; they are not permission for numerical fitting/search. Sampling occurs only in the frozen scheduled executions. No extra whole cohort may be drawn or discarded for favorable diagnostics, and no parameter or seed adapts inside a run. The common 40 design/feedback-turn ceiling and zero extra simulation-calibration calls remain unchanged.

## Implementation/release boundary

After root/reviewer agreement, a pure fit/draw component and narrowly meaningful **invented-input** tests may be implemented. That permission does not authorize fitting these actual source values, creating a clinical candidate, sampling a clinical table, or opening target data. Domain failures must be explicit and immutable, not repaired to make the evidence fit. This proposal has performed no source parameter fit or feasibility computation on actual values.

Case release still requires the same shared admitted packet, reviewed descriptive-proxy dispositions, a complete case/task contract, enforceable context eligibility, reviewed code and finite attempt ledger, independent review and the existing global pre-outcome freeze. No STATE, campaign inventory, source record or older frozen file is changed here. Basis: design v1; unchanged campaign budget; K02 reference/budget conventions; K01 scientific-use and independent design reviews; exact MIND/Ayele candidate views.
