# LIFESTYLE_A1: independent frozen-candidate code audit

Decision: no implementation blocker to the planned frozen final draws. This is a static code/provenance and already-run generated-trial audit, not an assessment against real participant measurements.

## What the Agent actually did

- 16 receipted Responses calls; tariff cost USD0.2063786; zero unknown usage calls.
- 2 literature searches and 11 source-read actions; the primary article was allowed evidence, not a hidden target answer.
- One submitted candidate v001; one successful isolated trial at seed63001; retained v001 after inspecting feedback. No revision.
- The submit payload exactly matches generator.py and model_spec.json. The scientific law and numerical choices came from this Agent submission, not a root rewrite.

## Law and mathematical inspection

A1 allocates fixed demographic strata, uses uniform age except a triangular oldest stratum, and generates BMI, HDL and non-HDL with bounded affine conditional arithmetic means and correlated multiplicative lognormal innovations. Its lognormal scale is solved from each group marginal variance after integrating assumed age/sex variation. TC is HDL plus non-HDL.

For a group, v=Var(mu), m=E(mu). With mean-one multiplicative lognormal noise, Var(Y)=v+(m^2+v)*(exp(sigma^2)-1). The implemented sigma^2=log(1+(s^2-v)/(m^2+v)) is algebraically correct; every current s^2-v is positive. It does not rescale a realized sample.

Independent algebra confirms positive conditional means over the bounded full age/sex support, positive residual scales, and a positive-definite latent correlation matrix. All first and second moments exist for these current parameters. Positive HDL and positive non-HDL imply TC>HDL. There is no nested exponential-of-lognormal tail construction.

All cases are complete fictional records. This does not validate clinical tail frequencies or emulate CardioChek measurement error. No code was imported or executed during this independent audit.

## Source and parameter provenance

External source PMC7347104 was actually searched and read (population, exclusions, source-of-variation section containing Table3, and Table4). TC age SDR0.41 and HDL age0/sex0.33 were observed in cached source text; these are variability ratios, not signed regression slopes. The Agent explicitly retains numerical age/sex slopes and interactions as assumptions. Its reference to the Beckman-Coulter assay was not independently verified in the specific cached sections inspected here.

The primary paper's BMI and HDL pastoralist mean/SD anchors and BMI descriptive percentages were checked against cached read_source text. Those descriptive percentages are treated approximately as marginal mean ratios; they are not newly measured adjusted regression coefficients. TC levels/effect sizes, joint correlations, most variance components and interaction magnitudes remain explicitly assumed.

Rural BMI mean is 20.2228367610 rather than the declared 19.99*1.0969/1.0843=20.2222918012; difference +0.000544960. This is immaterial relative to rounded source percentages but is a real arithmetic/provenance discrepancy, preserved without editing.

## What the existing check establishes

The recorded WSL/bubblewrap trial succeeded with1226 age-eligible rows, no missing/nonpositive/nonfinite biomarkers, zero HDL-above-TC rows,27 computed contrasts and3 interaction tests. It used lifestyle_main_three_traits_v1 and recorded target_reference_read=false. The final-selection prose agrees with these generated-only diagnostics.

A1 includes its own diagnostic helper; the official returned feedback remains the host's frozen analysis operator. Retention is not evidence of a successful revision, nor is one trial a target validation.

## Limits that must remain visible

- Source-rich analysis reconstruction: the same paper provides qualitative findings and numeric anchors. Later agreement measures reconstruction utility; it is not an unseen-source claim.
- Complete1226-person synthetic lipid measurement differs from406 source measured lipid records (BMI1198). Standard errors and detection rates can differ even for plausible laws.
- The declared conditional dependencies and many effect magnitudes are assumptions. External raw differences or variability ratios do not identify Turkana adjusted coefficients.
- The source Table1 total1360 is proportionally rescaled to1226; age70/top-age definitions are explicit assumptions.
- Draw seeds represent individual sampling under fixed parameters; neither source uncertainty nor model uncertainty is propagated. Classical OLS intervals have that conditional interpretation.
- The two constructors share one GPT family and supplied evidence. Their agreement does not constitute independent scientific confirmation.

Machine-readable detail, file hashes, exact action references, support bounds and scale algebra are in A1_CODE_AUDIT.json. No frozen inputs, candidate files, source files or reference data were changed.
