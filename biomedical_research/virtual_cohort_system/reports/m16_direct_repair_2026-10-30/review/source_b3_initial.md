# B3 initial source and construction review

**Decision: PASS for preauthoring commitment and subsequent literal authorship.** This is an extraction, provenance, and implementation review, not evidence that the proposed construction will reproduce the hidden target. Reviewed on 2026-10-30 by the independent protocol reviewer. No observed participant rows, generated rows, hidden reference rows, or previous target results were read for this review. No scientific parameter modification is requested.

## Bound artifacts

Relative to `visible/b3/bundle/candidates/initial`:

| Artifact | SHA-256 |
|---|---|
| `evidence.json` | `3a67b0b4197235b694928190c21edbebd9de06af73a207aa3cc2c06410e74eb9` |
| `model_spec.json` | `605509750b7ea241db829bb7d9b0e6f88a1a0d0fd1854006f80aea1cb94e06e9` |
| `audit/construction.json` | `f2c57059eb5658f0b5d02b0194b14866f27f9f9b6a723ac5a61f58e52dd5f479` |
| `audit/revision_plan.json` | `735429de2edef8ffde762de49e8ff8a3f1fc1b0b0eb6de51d28ed67cad18001a` |

`check_source_b3_initial.py` and its JSON result provide the numerical audit. They checked all **203 numerical items among 205 evidence items**, all **27 source-check mappings**, all cited artifact hashes, the contract and source registry, and **96 independent formula comparisons on invented predictor values**. The 48 numerical age-band items were independently parsed from the original Ohyama DOCX rather than the builder's text extraction. Other numerical expectations were transcribed from the independently inspected original main tables and Yun supplement.

## Original-source verification

- **Yun, PMC8236402:** Adult Table 2 group means, SDs, counts and units match. The cohort I adult follow-up and cohort II baseline/follow-up descriptions match Table 1, with longitudinal summaries retained as longitudinal context. The adult standardized BMI-to-urate path is 0.322, adjusted for age, race, sex, smoking and alcohol. The supplement subgroup coefficients 0.337/0.302/0.332/0.407 are correctly retained; they do not identify four raw conditional slopes. Shared Bogalusa recruitment and within-study overlap are acknowledged.
- **Sun, PMC4208749:** All adult descriptive items and Table 2 coefficients match. The regression direction remains **BMI on urate**, adjusted for age within race/sex; it is not inverted. Reported standardized coefficients and lack of coefficient SE/CI are correctly represented. The overlap with Yun and different age, fasting, treatment and recruitment restrictions are recorded.
- **Bonaccorsi, PMC6941025:** Premenopausal/postmenopausal mean/SD and BMI correlations match Tables 1 and 2. Original urate values remain in micromol/L; the separate mg/dL items are labeled derived and correctly divide by 59.48. Menopause is not replaced by an age threshold. No adjusted urate-age coefficient is claimed.
- **Ohyama, PMC7803020:** Original main XML and the controller-admitted `mmc2.docx` were independently inspected. Gunma recruitment, exclusion of baseline hypertension/CVD, n=12,029, male n=7,112 and female n=4,917 match. Sex-specific urate means/SD are 5.9/1.2 and 4.3/0.9 mg/dL. The source's abstract female percentage differs from its counts/Table 1; the builder correctly uses the latter and records the discrepancy. Serum urate assay details are unavailable and are not invented. Diabetes and urate-lowering treatment restrictions cannot be equated to the target.
- **Ohyama age bands:** At source mean ages 36, 44, 54, 64, male urate means are 6.0, 6.0, 5.8, 5.7 and female means are 4.2, 4.1, 4.4, 4.6 mg/dL. All associated age/BMI/urate SDs agree with the original DOCX. The supplement's ambiguous `40–50` label is retained and distinguished from main-text bands. These are **marginal descriptions**, not within-person trajectories or BMI-adjusted effects. The construction explicitly acknowledges this limitation.

The four articles represent three recruitment populations: Yun and Sun are not independent evidence units. No NHANES numerical results are adopted. Incidental NHANES citations in supplied originals are disclosed.

## Construction audit

The expression in `audit/construction.json` exactly equals the declaration inside `model_spec.json`. An independent recursive expression interpreter reproduces the separately written formula for all four race/sex groups at invented ages 20/40/45/56 and BMI 18/40/50, including both knots and centering.

- Group location anchors and BMI/age centers come from Yun Table 2.
- The pooled marginal SD calculation reproduces 1.598001636 for urate and 7.393740266 for BMI; `0.322 * SD_urate / SD_BMI = 0.069593536`. Using this to motivate a local slope of 0.07 is correctly labeled an approximation, because the needed conditional scaling/standardization details are not fully identified. The Sun reverse-slope variance-ratio calculations are also explicitly approximate; no reciprocal slope is used.
- The BMI knot at 40 and slope 0.03 above it are declared extrapolation assumptions, not findings from a paper.
- Male flat-then-negative and female small-negative-then-positive age guides are declared assumptions informed by independent marginal context. Breakpoints 40/45 and coefficients are not reported as estimated conditional effects or proof of menopause. Source age differences are confounded with other cohort differences and cannot determine these coefficients uniquely.
- Working scales 1.2/1.1/1.4/1.5 are explicitly assumed conditional guides, not source marginal SDs or inferential SEs. The retained larger SD in one longitudinal subgroup is not suppressed.
- Literal authorship remains prospective. The plan prohibits forced exact source means, mirrored deviations, zero residual moments and a false known sampling-law claim. The reviewer did not construct or select any outcome rows.

## Feedback mapping and interpretation

There are **24 approximate checks**: 16 Yun/Sun group means/SDs, four Sun BMI-on-urate age-adjusted slopes, and four Ohyama sex means/SDs. Units, variables, group selection, intercept and adjustment direction are correct. Three checks are **not computable**: the fully adjusted standardized Yun effect and the two true-menopause Bonaccorsi correlations. Their operators remain null; no reduced substitute is silently introduced.

All computable checks apply source statistical operators to a target-shaped table. They are not a replay of the source populations: age support, race composition, disease selection, fasting, medication and assay context differ. This approximation is explicit in the plan. In particular, no age-band or Japanese-source discrepancy should automatically trigger a forced parameter change. A residual-age diagnostic measures adherence to the Agent's declared guide, not an externally established age truth.

## Remaining scientific limitations

No source uniquely identifies target conditional age effects, extreme-BMI curvature, interactions, conditional variance or tails. Marginal-to-conditional translation and population transfer remain hypotheses to be tested, even though their provenance is honest. Four approximate external descriptive comparisons are not independent validated constraints. This PASS does not authorize a target release or establish a gain from revision; the ordinary controller commitment, freeze, feedback, and eventual global release checks remain required.
