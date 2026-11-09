# Conditional evidence: useful additions, incomplete target identification

Completed source audit, 9 November 2026. This follows the closed analysis-use/coherence experiment. No new target measurements, candidates, patient datasets or generated tables were accessed or produced in this unit.

## What changed

We found useful numerical continuous-association and joint-relation evidence beyond the prior qualitative summaries. Original-table review and an independent source-only reviewer verified the strongest candidates. These additions justify a bounded source-replay exploration. They do not establish that the existing generated data improved, or that all requested relations are now identified.

The substantive distinction is between (a) an authentic statistic reported under its own study conditions, (b) an executable replay of that statistic, and (c) its applicability to another population's analysis. A paper can supply useful information without being an exact target answer. The framework should preserve that information and expose the assumptions needed to use it.

## Evidence-to-use map

| Existing requested use | Newly verified evidence | What it can support | What remains unresolved |
|---|---|---|---|
| HDL on continuous BMI, adjusted age/sex | Soares2019/2020 continuous HDL coefficients, stratified and extensively adjusted, per source BMI SD | Quantitative source-specific projection checks, beyond a qualitative negative-association cue | BMI standardization reference, differing covariates/selection, pooled raw-unit projection and transport |
| TC on continuous BMI, adjusted age/sex | Same MEIRU family, continuous TC coefficients under corresponding source models | Quantitative source-specific projection checks across sex/site strata | Same scaling/adjustment issues; the two publications are overlapping evidence, not independent replication |
| TC-HDL residual Pearson correlation after age/sex/BMI | Liu2023 provides three clinical-lipid/BMI partial correlations after age/sex/batch | An explicit source joint constraint; conditional algebra adds BMI adjustment | Batch remains; common records/design and uncertainty are incomplete; German source population is not the African target |

Sources: [Soares2019](https://doi.org/10.1136/bmjgh-2019-001542), [Soares2020](https://doi.org/10.1186/s12916-020-01648-0), [Liu2023](https://doi.org/10.1111/acel.13934). Full operator details, values, CIs and original locators are in the inventories and independent review. Paper bodies remain local.

Soares2019 is the primary follow-on association family because its adult sex/site coverage is broader than the selected urban age ranges in Soares2020. This choice is based on design and population coverage, without reading target effects. All eight Table3 TC/HDL coefficients are retained. Soares2020 contributes a related-source check, not extra independent sample size. Standardization and source-replay conventions must remain visible.

Greiner regression scales remain unresolved. Agongo supplements contain additional log-outcome associations, but log base/adjustment issues prevent an exact raw-slope label. Categorical and rank-based evidence remains available under its actual meaning. A coefficient CI is not individual-level residual variation; two lipid slopes do not determine their residual covariance.

## Verified aggregate calculation

Under a common source residual design, Liu's three rounded coefficients give an additional-BMI partial correlation of approximately **0.190**, still adjusted for age, sex and batch. Independent recursive and Schur-complement calculations agree exactly at machine precision. The nearest-0.01 rounding-only interval is approximately **0.182 to 0.198**. This is not a sampling confidence interval, a target estimate, or a clinical validation. Exact common n and batch processing remain unresolved.

See `verify_partial_relation.py` and `PARTIAL_RELATION_CHECK.json`. The calculation reads three published numbers, not individual rows. It does not fit or revise a generator.

## What the audit does and does not explain

- **Retrieval/extraction gap:** some useful published continuous statistics had not been incorporated. Reading original supplements can improve the evidence packet.
- **Implementation gap:** the next controller needs a declared source-specific replay and an explicit source-to-target model link. Calculating a target statistic and calling it a source replay would not test the paper's constraint.
- **Identification/transfer gap:** the retrieved summaries do not uniquely determine the requested target joint law or conditional variability. More generated rows cannot supply this missing information.
- **Measurement gap:** the evidence concerns measured assay outputs. Moving to error-free latent concentrations requires a separately declared observation model.

These are different issues. The audit alone cannot assign a numerical proportion of earlier generation error to each one. It also does not show that an unrestricted literature search would eliminate all gaps.

## Decision and bounded next step

**Continue with one source-consistency exploration, not another target-tuning run.** `FOLLOW_ON_SPEC.md` defines the implementation change and execution limits: one fresh scientific construction, at most one source-feedback revision and six final tables. Source-law evaluation has its own finite cap. The Agent chooses the model and transport assumptions; the host does not insert expected slopes or correlations. Freeze both versions before releasing requested target-use analyses. No old target is reused as fresh confirmation.

Assumption-dependent replay is allowed and labelled. We will not demand unavailable perfect source information as a precondition for all modelling, nor call a chosen convention verified. If no defensible replay can be constructed, stop that branch and preserve the failure. A later independent clinical-reference evaluation is separate.

The useful paper-facing implication is a sharper account of **which scientific analyses the evidence-guided data can support and which depend on unverified choices**. This unit provides evidence acquisition and mathematical-audit results, not new generation-performance claims. The recursive identity itself is standard mathematics, not a methodological novelty claim.

## Audit, cost and reproducibility

- Two source-discovery agents and one independent methods/source reviewer; root consolidated decisions.
- 18 conservatively counted successful discovery requests (root3, association7, joint8), plus one failed connector attempt. Below the24-request resource ceiling; no fixed paper-count requirement.
- Saved original-source/metadata transport: **5,838,353 bytes**. Known additional HTTP-response bodies: **174,990 bytes**. Web browsing and one unsized publisher response are unmetered and not claimed as zero. Rendered/extracted copies are not double-counted as downloads.
- No clinical or synthetic row-table download; no target reads; no new scientific generation; no changes to previous frozen artifacts or receipts.
- Original-file SHA-256 manifests, full query logs, source-specific exclusions and independent review are retained. Public exports contain original summaries, metadata and aggregate calculations only.

## Read together

1. `association_inventory.md` / `.json` — six association sources, including non-admitted and incomplete items.
2. `joint_inventory.md` / `.json` — joint-evidence candidates, incompatibilities and algebraic conditions.
3. `IDENTIFIABILITY.md` — sufficient summaries and what cannot be inferred.
4. `INDEPENDENT_EVIDENCE_REVIEW.md` / `.json` — independently checked original sources and limits.
5. `FOLLOW_ON_SPEC.md` and `FOLLOW_ON_REVIEW.md` — next construction contract and independent design review.
