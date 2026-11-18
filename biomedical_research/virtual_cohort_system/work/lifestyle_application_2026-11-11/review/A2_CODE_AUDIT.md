# LIFESTYLE_A2: independent frozen-candidate code audit

Decision: no implementation blocker to the planned frozen final draws. This is a static code/provenance and already-run generated-trial audit, not an assessment against real participant measurements.

## What the Agent actually did

- 15 receipted Responses calls; tariff cost USD0.1682289; zero unknown usage calls.
- 2 literature searches and 10 source-read actions; the primary article was allowed evidence, not a hidden target answer.
- One submitted candidate v001; one successful isolated trial at seed63001; retained v001 after inspecting feedback. No revision.
- The submit payload exactly matches generator.py and model_spec.json. The scientific law and numerical choices came from this Agent submission, not a root rewrite.

## Law and mathematical inspection

A2 allocates fixed demographic strata and uniform ages, builds affine conditional arithmetic means for BMI/HDL/TC, then generates positive BMI, HDL and non-HDL=TC-minus-HDL means using correlated lognormal innovations. It fixes residual SD by group, rather than a constant multiplicative coefficient of variation. Generated TC is the sum of HDL and non-HDL.

For BMI and HDL, pastoral residual variance equals reported pastoral marginal variance minus the analytic variance of the assumed age/sex conditional mean. These residual variances are 4.4077107 and212.9669009, both positive. positive_draw uses sigma^2=log(1+(sd/mu)^2), hence E(Y|X)=mu and Var(Y|X)=sd^2. Total cholesterol inherits covariance through the two positive components; TC marginal SD was not identified by source evidence.

Independent algebra confirms positive conditional means over the bounded full age/sex support, positive residual scales, and a positive-definite latent correlation matrix. All first and second moments exist for these current parameters. Positive HDL and positive non-HDL imply TC>HDL. There is no nested exponential-of-lognormal tail construction.

All cases are complete fictional records. This does not validate clinical tail frequencies or emulate CardioChek measurement error. No code was imported or executed during this independent audit.

## Source and parameter provenance

External source PMC6435188 version2 was actually searched and read after a version-selection response; population, measurement and Table1 were available. Table1 Maasai female/male HDL1.2/1.1mmol/L and BMI22.5/21.0 were verified in cached text. 0.1mmol/L*38.67=3.867mg/dL supports the numerical origin of the proposed3.87 female HDL difference, but using that raw external difference as a conditional coefficient remains an acknowledged assumption, not a transport validation.

The primary paper's BMI and HDL pastoralist mean/SD anchors and BMI descriptive percentages were checked against cached read_source text. Those descriptive percentages are treated approximately as marginal mean ratios; they are not newly measured adjusted regression coefficients. TC levels/effect sizes, joint correlations, most variance components and interaction magnitudes remain explicitly assumed.

Rural BMI mean is20.2222869132 rather than declared quotient20.2222918012; difference -0.000004888. This tiny arithmetic discrepancy is preserved. No mathematical mechanism defect was found from the current specification.

## What the existing check establishes

The recorded WSL/bubblewrap trial succeeded with1226 age-eligible rows, no missing/nonpositive/nonfinite biomarkers, zero HDL-above-TC rows,27 computed contrasts and3 interaction tests. It used lifestyle_main_three_traits_v1 and recorded target_reference_read=false. The final-selection prose agrees with these generated-only diagnostics.

Retention is not evidence of a successful revision, nor is one trial a target validation.

## Limits that must remain visible

- Source-rich analysis reconstruction: the same paper provides qualitative findings and numeric anchors. Later agreement measures reconstruction utility; it is not an unseen-source claim.
- Complete1226-person synthetic lipid measurement differs from406 source measured lipid records (BMI1198). Standard errors and detection rates can differ even for plausible laws.
- The declared conditional dependencies and many effect magnitudes are assumptions. External raw differences or variability ratios do not identify Turkana adjusted coefficients.
- The source Table1 total1360 is proportionally rescaled to1226; age70/top-age definitions are explicit assumptions.
- Draw seeds represent individual sampling under fixed parameters; neither source uncertainty nor model uncertainty is propagated. Classical OLS intervals have that conditional interpretation.
- The two constructors share one GPT family and supplied evidence. Their agreement does not constitute independent scientific confirmation.

Machine-readable detail, file hashes, exact action references, support bounds and scale algebra are in A2_CODE_AUDIT.json. No frozen inputs, candidate files, source files or reference data were changed.
