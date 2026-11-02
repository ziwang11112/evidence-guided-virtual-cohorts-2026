# K01 scientific design commitment and execution boundary

2 November 2026. The coordinator accepts K01 for prospective scientific case admission following independent review and fixes its scientific design and necessary pure components. The independent review and hash commitment identify the exact accepted artifacts. Scientific admission is distinct from execution readiness: this decision does not release clinical construction, source fitting, target data access or the global campaign. Previous frozen cases and K02 commitments remain unchanged.

## Fixed scientific scope

The task is full generation of `id, age, sex, bmi, glucose`, with 5,000 rows and no observed individuals. The target is the HAALSI baseline pooled released-cleaned capillary POC measurement context, with census age at least 40, no upper age restriction, F/M sex, and positive finite BMI/glucose. A generated measurement is a model-based value. No individual recovery, true-population mean, universal fasting or assay-equivalence claim is made.

The same output supports three fixed OLS contrasts: BMI per 5 kg/m² and age per 10 years from the additive age/sex/BMI model, and the Female-minus-Male BMI contrast difference from its sex-by-BMI extension. Both designs require full rank, both sex levels and more than five common eligible records. The exact [analysis specification](analysis/K01_ANALYSIS_SPEC_v1.json) fixes missingness, malformed data, degenerate fits, intervals, normalization, failure and continuation rules before any target effect is read.

The measured reference uses the cleaned released numbers. No documented finite numerical nonmeasurement sentinel was identified in the reviewed metadata, so the explicit sentinel list is empty with that limitation retained. Native/tagged missing remains excluded. There is no flag, range, fasting, treatment or outlier trimming. Source age bounds are distinct from target eligibility and do not impose a target upper limit.

## Fixed evidence and scientific freedom

The common [request packet](request/README.md) contains 34 preserved source records. Eighteen marginal records can be used for explicitly approximate source-context descriptions: seven MIND and eleven Ayele. Six Ayele binary-diabetes ORs and ten abstract-only Bahendeka records remain contextual. All three target projections are still joint-assumption dependent. Record counts are not independent evidence counts.

The [descriptive plan](request/descriptive_diagnostic_plan.json) fixes four means, four individual SDs and ten count-derived fractions. Original printed percentages and integer operands remain distinguishable. Ayele age bins have an explicit completed-year half-open interpretation; the BMI middle bin retains the printed 24.9 endpoint and gap before 25. Every fraction uses all validated source rows as its denominator. Equal weighting, SD divisor n−1, post-imputation source-population representation and measurement transport remain assumptions. Strict source-estimator replay stays unavailable under unknown original weights/conventions.

The scientific Agent chooses the joint structure, parameters and shared versus context-varying assumptions. The coordinator supplies no desired signs or target means/slopes. A common generator must explain population and measurement changes; matching code hashes alone is not evidence of scientific transport. The source marginal facts do not identify the joint relations, and absence of a reported relation is not evidence that it is zero.

## Fixed reference and attempt budget

The [statistical reference](STATISTICAL_REFERENCE_AND_BUDGET_PROPOSAL.md) uses an explicit independent-marginal completion. It analytically matches selected source moments/count ratios, borrows MIND glucose where no continuous marginal is supplied, and transports an equal donor mixture using within-donor age conditioning. Its zero population glucose effects follow from its independence assumption, not published proof or a prescription to the Agents. It is a transparent limited reference; it is not the strongest possible statistical method.

Five fresh Agent constructors and S01 receive identical scientific evidence. Each gets an initial stage and at most one source-feedback decision. Target seeds remain 2101–2103, with 5,000 rows each. There are 36 reserved target slots, at most 33 new attempts when all five Agents revise and S01 retains. Two source contexts at 5,000 rows each use seeds 3101/3102: 24 reserved slots, at most 22 new attempts. Failures consume attempts. Retained finals alias initial outputs, and reservations cannot be transferred to retries. There are no extra simulation-calibration calls. S01 retains its scientific law regardless of finite-sample source mismatch when integrity is valid.

Final delivery is primary. A constructor passes the working criterion only when all three analyses on all three seeds have absolute effect discrepancies at most 0.10 reference glucose SD. The complete 0.05/0.10/0.20/0.30 grid remains mandatory. At least four of all five Agent constructors are needed for the case criterion. Reference SD is evaluation-only; these margins are research resolutions, not clinical equivalence. When all three zero anchors already satisfy the working margin, the case cannot support positive Wave B for joint-signal recovery. K02 alone cannot unlock Wave B.

## Implemented and verified at this checkpoint

- Exact source/target context mapping and a whole-frame generated-output guard, with no filtering, repair, silent upper-age cutoff or cross-context substitution.
- Pure three-estimand analysis, including reference-only descriptive HC3 intervals and SD normalization inputs.
- Fixed eighteen-source-statistic arithmetic using the existing operators, with full-row event denominators and explicit approximation labels.
- Pure statistical reference derivation/sampling and a provenance-bound source input view, separately reviewed without fitting actual source values.
- Independent invented-input composition and static packet/provenance checks, as recorded in [the independent review](CONTRACT_INDEPENDENT_REVIEW.md).

Software checks use invented data only. One initial analysis test failed because its independent statsmodels oracle reused a subsequently mutated design frame; the test was repaired without changing the analysis implementation, and the affected test passed. The failure remains recorded. No old passed suite was rerun. Source transcription, software arithmetic, scientific usefulness and clinical validation remain different claims.

## Remaining production work, with no design expansion

The [design commitment](REVIEWED_DESIGN_COMMITMENT.json) fixes the reviewed bytes. Before clinical runs, the controller must bind those bytes to actual candidate bundles and admitted source registrations, verified execution/child-task contexts, semantic-v1 feedback followed by the separately reviewed descriptive reports, and the finite cross-version ledger. The reserved evaluator must enforce the complete final inventory and use the frozen target mapping only after all Wave A constructions close. K02's existing bindings must be completed under the same global freeze.

These are production integration requirements. They do not require another outcome, new original-study search, additional Agent role, new loss, or further general framework. Necessary repairs discovered during integration must preserve the scientific choices or receive an explicit pre-outcome versioned amendment; they cannot tune known target results. Until that integration/global release is verified, the prepared request retains its non-executing status and none of its source checks is activated.
