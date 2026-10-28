# Outcome-blinded implementation audit

27 October 2026. Independent read-only review of the comparison protocol,
feedback export, commitments, evaluator, submitted programs and decision records.
No real target outcome CSV, historical result file or new target accuracy result
was read. The reviewer saw the four authorized development summaries in submitted
decision records; these are permitted inputs, not hidden evaluation results.
No generator, input packet, lock or model artifact was edited. This report is the
only file written by this audit.

The protocol and earlier submissions were reviewed before target evaluation.
The final exercise structured review concluded after all-model commitment while
the coordinator independently ran evaluation. The reviewer did not read those
evaluation results. This is not a claim that every final review preceded the
coordinator's first outcome calculation.

## Status and scope

No unresolved severe numerical or fairness defect was found in the reviewed
artifacts. This is an implementation review, not evidence that either policy
generates accurate target populations.

| Component | Review status |
|---|---|
| PROTOCOL.md; common, ordinary and structured requests | Reviewed |
| prepare_revision.py; lock_models.py; evaluation/evaluate.py | Reviewed; two minor findings corrected before feedback export/model locking |
| Both FIT initial generators | Reviewed |
| FIT ordinary updated generator and decision | Reviewed after commitment |
| Exercise ordinary updated generator and decision | Reviewed after commitment |
| FIT structured updated generator and decision | Reviewed after commitment |
| Exercise structured updated generator and decision | Reviewed after commitment |

All four final submissions are covered. Do not extend this sign-off to future
file changes. No post-submission model repair is requested by this audit.

## Protocol and information handling

- Both policies receive the same evidence, output contracts, source/baseline
  checks, sample budgets and one scheduled revision. Ordinary iteration remains
  free to redesign, calibrate, decompose and test its model. The contrast is the
  whole prescribed policy, not access to correct statistics or essential checks.
- The marginal exporter requires all four initial commitments, then selects the
  frozen eligible development members before parsing outcome fields. Its outputs
  are exactly the pooled means and sample SDs (ddof=1) of signed percentage weight
  change and waist change in cm, with denominator and definitions. It does not
  compute check, subgroup or joint outcome statistics. Revised evidence hashes
  must match across policies.
- All eight submissions and evaluator code must be committed before evaluation.
  Valid generated targets are not excluded merely for failing source checks;
  missing/invalid outputs remain recorded failures. The absence of extra repairs
  applies equally to both policies.
- Source checks, declared invariants and numerical evidence probes establish
  particular implementation behavior. They do not establish transport validity,
  causal influence or full joint-distribution accuracy. A self-selected probe
  showing that an input changes an output does not establish the right effect.
- The workflow boundary is instructional, not an adversarial filesystem sandbox.
  No filesystem/network or real-outcome access was found in the reviewed generators.

Two minor findings were fixed before feedback export/model locking: the feedback
estimand now distinguishes six months from 24 weeks, and the evaluator verifies
the recorded revision-preparation lock hash. Frozen protocol text was preserved;
these were implementation/provenance clarifications, not outcome-informed changes.

## Numerical review

### Evaluation

The four response cells are coded consistently as neither, weight only, waist
only and both, with inclusive -5 percentage-point and -5 cm cutoffs. Marginal
response probabilities use the corresponding cells. TV is half the absolute
probability difference sum; exercise arms receive equal weights. Equal-budget
seed records are pooled before conditioning on arms, as documented.

Bootstrap resampling uses the same real-participant draw for all policies/stages,
within each check stratum and at its original size. Final and difference-in-change
contrasts use the correct model ordering and sign. An isolated in-memory toy test
returned the expected +0.75 for both contrasts under both case structures. It
opened no actual outcome or generated CSV. Undefined regression quantities are
reported explicitly. The bootstrap describes finite-target-sample uncertainty
conditional on fixed generators, not Agent or source-study uncertainty.

### FIT ordinary revision

Target percentage weight and cm-waist margins use their delivered individual SDs.
Under the transported Han slope, residual variance is correctly computed as
`waist_variance - slope^2 * weight_percent_variance`; the intercept matches target
means. Source FIT paths and baseline random-number ordering are retained.
Positivity floors and the slope feasibility cap are declared safeguards, rather
than undocumented source estimates. The submitted program contains no target
outcome access.

The Han reference context uses a modeled predictor distribution and approximate
source ratio-of-means level, not the former fixed reference grid or recovered
source participants. Source SEE is used approximately as individual residual SD;
coefficient uncertainty is not substituted for individual variation.

### Exercise ordinary revision

Pooled target calibration is performed in percent-weight/cm-waist coordinates.
Each generated weight response is subsequently converted to kg using its own
baseline weight. DREW's modeled pooled dependence is evaluated in kg/cm after
the same conversion, with conditional-mean covariance separated from residual
covariance. Source individual SDs remain individual noise. `SD^2/n` appears only
in the declared uncertainty calculation for a source mean-dose contrast.

The Fisher-z blending weight and its 0.60 prior dependence centre are assumptions.
The latter must not be described as a measured pooled correlation of the initial
generated population. This is a reporting limitation, not a numerical defect.
Source and baseline invariance claims agree with the inspected code paths.

### FIT structured revision

The analytic source log-weight-ratio variance correctly uses both occasion
variances and the separately assumed temporal persistence. The log-moment
calibration solves for a global scale and offset so the mixture's weight ratio
matches the authorized mean and SD, without sample recentering. Source observation
and target baseline paths are retained.

The target waist path uses the same Han slope accessor as the reference path and
the correct residual-variance identity. Its residual draws are independent of
the first innovation driving weight response; reusing the second independent
normal is consistent with the stated conditional model. Native source waist
rounding is retained, and Han reference rounding is explicit. No unit, sign,
SD-versus-SE or unintended source-change error was found. The chosen source
mixture shape, persistence, baseline-rank dependence and slope transport remain
unverified scientific assumptions, not implementation discoveries.

### Exercise structured revision

The kg-affine calibration correctly observes percentage change through baseline
weight. Within each arm-sex stratum it integrates E[1/W0] and E[1/W0^2], then solves
the mean constraint and the resulting quadratic variance equation for a common
positive kg scale and intercept. This is consistent with its explicitly assumed
conditional independence of absolute kg response and baseline weight. A percentage
SD is not used as a kg SD. Waist calibration correctly includes within-arm variance
and between-arm mean variation.

The female dependence calculation separates pooled mean covariance from residual
covariance and solves the pooled physical-unit Pearson equation. It is valid to
perform this calculation using source-shaped moments before the target calibration:
the same positive affine transformation for each outcome applies across all female
arms, so the pooled physical-unit Pearson correlation is unchanged. The derived
residual coefficient is therefore not simply copied from the reported pooled r.
Male and native-source residual assumptions remain unchanged. Baseline and source
random-stream preservation agree with the implementation and decision record.

No numerical, sign, unit, SD-versus-SE, unintended source-change or outcome-access
defect was found in this final submission. Interpreting DREW as pooled Pearson,
transferring its value to target women, retaining conditional kg-response structure
and leaving male residual dependence at zero are explicit unverified assumptions.
The constructed female pooled correlation is a fitted implication of those
assumptions, not validation against target joint data.

## Limits on interpretation

One builder per case/policy does not estimate Agent variability. The same generation
seeds are Monte Carlo repetitions, not independent Agent runs. Actual preparation
compute and tokens are unmeasured. Different initial models prevent attributing
the final contrast specifically to revision alone. Both targets are historically
exposed retrospective development, with transductive baseline information and
predeclared limited development feedback. The selected FIT packet is incomplete
relative to all published information.

Passing this audit and the source/baseline observers is not a finding of better
target prediction, reusable scientific utility, novelty or equivalence to patient
data collection. Preserve all model failures and adverse outcomes when the frozen
evaluation is eventually run.
