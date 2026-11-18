# Focused design review: economical same-parent review experiment

10 November 2026. **Design accepted with the boundaries below.** This review does not authorize changing any historical candidate, importing target results into author contexts, or expanding the proposed call/table limits. No API, credential, patient data or generated program was accessed for this review.

## The discriminating question

Given the same initial agent-authored generator and published evidence, does exposing the author to a small, deterministic check of its own generated data lead to a more internally coherent and usable final construction than an equally budgeted ordinary second look? Which problems can be repaired from that information, and which remain dependent on assumptions that the supplied evidence does not identify?

This is a development experiment with two paired parents, not a powered proof that feedback improves transport or that the overall system beats an ordinary agent. The earlier prompt already distinguished source statistics, parameters and requested estimands. Adding another generic checklist alone would provide little new evidence; the intervention here is concrete generated-only diagnostic information.

## Fixed calls and roles

For each of two existing cases, create four fresh initial constructions: Sol A, Sol B, Astra, and DeepSeek. Sol A is the paired parent, nominated before any output is seen. Sol B is a separately reported construction-variability reference; it cannot replace A if A fails or appears less favorable.

Fork each Sol A into two fresh API review contexts, both receiving the identical original packet and identical initial artifact:

1. **Ordinary second look:** review the original evidence and own initial program/specification/decision record, then retain or revise.
2. **Generated-check feedback:** the same review task and initial inputs, plus the deterministic diagnostic payload from that parent's three initial draws.

Both use the same model configuration, effort, output allowance and review objective. Actual input tokens will differ because the diagnostic is the treatment; record rather than claim equal realized compute. Neither branch sees the other branch, Sol B, Astra, DeepSeek, historical candidates, historical results or target-reference values. A retain, a reporting-only change and a substantive program/specification revision are distinct outcomes, all retained. No instruction requires a successful-looking change.

Total planned opportunities: **eight initial calls plus four review calls = twelve**, allocated as eight Sol, two Astra and two DeepSeek. Do not introduce an uncounted repair or expensive fallback. If a paired parent is not delivered, its branches remain unavailable with that reason; do not substitute B or construct a new parent to fill the cell.

## Generated-only feedback boundary

Run the same deterministic diagnostics on three predefined initial-diagnostic seeds for each Sol A, after sealing the initial artifact. The payload may contain:

- Execution/schema status, row count, finite-value checks and full-design rank.
- Duplicate measurement-row count and predefined component-constraint counts/fractions: SBP below DBP or HDL above TC, as applicable to the schema.
- Declared scientific-variable margins: mean, clearly labelled SD convention, minima/maxima and fixed quantiles; category counts for categorical variables. Identifier summaries have no scientific role.
- The same three requested adjusted analyses, their definitions, units and conditioning set, computed only on that parent's generated rows.
- Clearly defined generated residual scales, distinguishing residual RMS from degrees-of-freedom-adjusted residual SD if included.
- Descriptive mean/range over the three draws. Such ranges are Monte Carlo diagnostics, not confidence intervals or population truth.

The payload must not contain a target value, desired direction, reference discrepancy, target-derived tolerance, cross-author ranking, proposed coefficient, recommended correlation, favored distribution or part-whole recipe. In particular, do not insert the successful historical Claude structure or the prior DeepSeek rejection error as an instruction. A small finite-sample difference from an author's claimed population value is not automatically a mathematical error. Unresolved or incompatible operators are not numerically comparable merely because their labels contain "correlation" or "SD".

The ordinary branch receives no generated diagnostics. Common review instructions may ask both branches to inspect their own mathematics, definitions, provenance and practical usability. The only intentional arm difference is access to the generated-check payload; new audit advice must not be appended only to the feedback branch.

## Evaluation and implementation checks

Use six diagnostic tables in total: two Sol A parents times three diagnostic seeds. After **all four review outcomes are sealed**, evaluate every initial and final version on three different, predefined evaluation seeds: eight initial versions plus four review branches times three seeds gives 36 evaluation slots. **Maximum total is 42 table slots.** The new evaluation seeds avoid grading a feedback branch only on the exact draws it saw. Common seed integers across versions do not guarantee identical random-number coupling after a structural change.

Keep the full denominators and original versions. A retained program should produce the same rows as its initial version at the same evaluation seed if it uses the declared seed deterministically; check this without silently replacing inconsistent output. A reporting-only retraction of an unsupported exact-estimand claim is not a data-quality improvement.

The primary descriptive readouts should separate:

1. **Delivery and valid execution:** all scheduled calls and table slots, including failures.
2. **Actual data constraints:** component violations, duplicates, finite/eligible rows and unchanged predefined analyses. Do not repair or discard rows on the host.
3. **Claim and operator consistency:** exact requested-estimand claims supported by the actual post-transformation law; unsupported exact claims; disclosed assumptions; unavailable/not-derived claims. Report claim coverage alongside correctness so changing every number to null cannot masquerade as improved generation.
4. **Revision type and consequences:** retained, reporting-only, parameter, or structural changes, with artifact differences; initial versus both final branches on the same endpoint definitions.
5. **Developmental external comparisons:** the existing real-data aggregate estimates and their uncertainty, revealed only after all review outcomes are frozen. Report every requested analysis; neither point-estimate proximity nor interval overlap alone establishes equivalence.

Do not pool rank, latent, innovation, component-pair and raw adjusted residual correlations into one parameter column. The covariance/dispersion provenance audit must retain the conditioning set and scale. The supplied sources do not identify every requested joint relationship; a remaining discrepancy after an internal repair is not proof of a uniquely identified missing-evidence cause.

## What can change the next decision

- If feedback corrects verifiable internal defects or component violations without introducing new defects, retain this targeted check as a useful engineering mechanism and report the two paired cases descriptively.
- If ordinary second look does the same, prefer the simpler workflow; no feedback-superiority claim follows.
- If only explanations improve while generated analyses do not, report better accounting rather than better data.
- If neither branch improves or the initial parent has no relevant defect, keep that outcome. Do not expand cases, change thresholds, add components or select a new parent to create improvement.
- Cross-model initial references show construction variation and cost only. With one Astra and one DeepSeek construction per case, they do not support a model leaderboard.

The proposal's USD10 next-batch ceiling must be checked before each paid dispatch, including the cost reserved for the four review opportunities. The historical mean projection is not a guarantee: review prompts include the initial artifact and may cost more than a fresh initial request. Fixed historical outputs and manuscript results remain unchanged.

## Review basis

Read-only inspection of the prior pilot's `packets/common_prompt.txt`, `provenance_review/CORE_PROVENANCE_REVIEW.md`, `provenance_review/LIPID_CORE_REVIEW.md`, and the prospective `docs/MODEL_USE_POLICY_2026-11-10.json`, followed by root/execution-agent design coordination. This review supplied no scientific coefficient or target-derived modeling advice and performed no new data or literature collection.
