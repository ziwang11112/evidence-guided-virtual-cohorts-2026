# K02 prospective scientific-use decisions

2 November 2026. Coordinator decision based on the [independent scientific-use advisory](SCIENTIFIC_USE_REVIEW_2026-11-02.md). No target clinical value, effect or sign was used to make these choices. This is a versioned analysis proposal, **not a scientific release or final case admission**; the original campaign and its frozen inventory are unchanged.

## Proceed with partial evidence

Do not require all joint correlations or conditional residual variances to have been published. The hypothesis is precisely that an Agent can construct a useful joint law from incomplete external evidence. Unambiguous summaries can constrain construction; other relationships, distributional choices and population/assay transport remain explicit assumptions. No coordinator-specified target relationship is added to the generator.

The independent source review must distinguish three things: accurate transcription, an executable statistic, and suitability for transfer. Correct arithmetic establishes only the second. A source-context simulation is not established merely by renaming a target table. Where weighting or source selection is unresolved, diagnostics must remain labelled approximate/descriptive rather than exact source replay. That limitation need not ban Agent use of the published evidence as context.

## Primary analyses to carry into case admission

Use one common complete-case analytic subset for age, documented sex, BMI, measured total cholesterol (TC) and HDL. Whole-cohort constructors generate all five variables without receiving target individual covariates.

1. **K02-HDL-BMI:** HDL ~ age + sex + BMI, reporting the BMI contrast per 5 kg/m² in mg/dL.
2. **K02-TC-BMI:** TC ~ age + sex + BMI, with the same contrast and units.
3. **K02-LIPID-RESIDUAL:** Pearson correlation of TC and HDL residuals from those two models.

These are descriptive scientific associations, not causal or individual-recovery claims. The third tests reusable joint structure beyond two fitted effects. No expected direction is prescribed. Related external HDL/BMI and HDL/non-HDL results may be supplied as contextual evidence; the exact target projections and residual correlation are not calibration targets.

Prospectively use the released measured adult subset as the empirical comparison population, not a national population. Resolve sex coding, age boundary and invalid-value handling from metadata before release. The schema availability count of 397 is not a fixed final sample size. Existing lifestyle and generic residual-correlation exposure requires an independent scoped-admissibility decision; changing model adjustment does not erase it.

## Working analytical-resolution rule adopted for the proposal

The intended early use is exploratory association analysis, not clinical interchangeability. Adopt the advisory's **0.10 working resolution**, with the complete fixed grid 0.05, 0.10, 0.20, 0.30 reported. For each BMI contrast, scale the absolute virtual-versus-reference effect discrepancy by the same reference outcome SD. For the residual association, use absolute correlation discrepancy. Reference SDs are evaluation-only and never provided to builders.

This threshold is an author-chosen feasibility criterion, not a validated biomedical equivalence margin, a 10% relative-error guarantee or a population-truth statement. Report raw effect discrepancies, directions, reference uncertainty, all constructors and all grid results alongside it. Do not select a more favourable grid point after disclosure. Synthetic-row p-values do not define scientific success.

A constructor satisfies the proposed bundle only if all three analyses satisfy the working margin on all three preassigned seeds. A case-level reliability result requires at least four of all five constructors, including failed attempts in the denominator. These are construction-level operational criteria, not five independent cohorts or a precise estimate of general success probability. The single fixed statistical reference is evaluated identically; superiority over it is not required for the feasibility claim.

Report the zero-association anchor for each endpoint. If all three zero anchors already fall inside the working margins, the case is insufficiently discriminating for joint-signal recovery and does not alone release Wave B. Keep weak/null agreement as a result instead of retroactively changing the questions. Initial-to-final retention remains zero improvement.

For the empirical comparison, point discrepancies describe this sample. Regression HC3 intervals may be included as an assumption-conditional sensitivity; unavailable clusters prevent a design-based population inference. Residual-correlation population uncertainty remains unresolved and must not be replaced with virtual-row precision. Final uncertainty implementation and computational budget must be fixed in the release contract.

## Remaining concrete release work

- Independent source-packet and operator review, then an explicit adapter that uses semantic_feedback_v1 for supported checks and labels the additive geometric diagnostic accurately.
- Target code/measurement eligibility and scoped exposure review; approve or decline the three exact analyses without seeing their effects.
- A shared source/context interface for initial and revised generators, and a deterministic, same-information statistical reference specification.
- Other admitted cases and the global freeze required by the larger campaign. No first-wave target disclosure until all relevant outputs have closed.

These gaps are implementation/admission work, not a demand for a new architecture, a new training objective, fully identified joint evidence or additional unbounded experiments.
