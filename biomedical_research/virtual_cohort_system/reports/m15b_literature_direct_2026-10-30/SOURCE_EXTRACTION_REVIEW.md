# Independent source extraction and comparator review

30 October 2026. **Stage 1 snapshot: numerical extraction and the proposed native source-check subset pass. Final scientific handoff remains pending decisions on two requested additional source-access actions and any resulting specification changes.** No generated row table was inspected, and no source feedback or target evaluation was run.

## Reviewed snapshot

| File | SHA-256 |
|---|---|
| `visible/bundle/candidates/initial/evidence.json` | `f3a2eec2f3dcd7aaa323e91ff7cce763b6e4cc6439e6ccf444e1d550fa9a0a96` |
| `visible/bundle/candidates/initial/model_spec.json` | `e774581f4b16c6467e9af2b273dfc18d90e15305179a2d7cf61d5e19bc9a7dc9` |
| `visible/research/evidence_gap_and_search.md` | `9fdd1cd7f1dc2790924df8bf31278b0852c4f837c06b7603b0a69fcd42799f1b` |
| `visible/research/source_check_plan.json` | `780471c24dc76a55dfa147ce53145510c2769221999cd0c7c1ca7530eed27cb7` |

Also read the two registered original JATS sources, relevant source admission notes and gateway state/audit records. Original source hashes remain the registered Yun `f3f4c658fe8ef90fb92ebc283f0dc4ddf87d0af81c10b127b734e2ce10f608a3` and Sun `26ce9cb66838e047d8c9c161668cd56ba8d87826a4c4950208699000612f3bcc`.

The builder's research note includes covariate-only summaries. They are not urate outcome information; this review did not recompute them or inspect the actual observed table. Private reference data, raw XPT outcomes and old target analysis outputs were not opened. No additional literature search was made by this reviewer.

## Extraction findings

The Yun adult group means/participant SDs for age, BMI and urate match Table 2. The adult cohort size, age range, nondiabetic selection and Olympus Au-5000 uricase measurement description match the Methods. The four urate means 6.1/4.5/6.2/4.6 and SDs 1.3/1.2/1.5/1.7 are openly supplied evidence rather than held-out tests.

Sun Table 2 gives **BMI as the dependent variable**, with urate as predictor. Its caption says age and BMI adjusted, but the BMI-row footnote removes BMI as its own covariate; the Results independently clarify that BMI was added for the other metabolic outcomes. The adopted group coefficients 1.38/2.59/1.29/2.14 `(kg/m²)/(mg/dL)` and age adjustment are correct. The proposal neither reciprocates them nor interprets their standardized counterparts as correlations. A linear age term and intercept are reasonable reconstructions of the described analysis, not recovered source code.

Yun Figure 2's adult 0.322 is a standardized contemporaneous urate-on-BMI path with age, race, sex, smoking and alcohol adjustment. It is not the longitudinal 0.068 path or a raw coefficient. The extracted item labels these distinctions. The precise standardization implementation and relevant omitted covariates remain unresolved.

The studies overlap in Bogalusa and cannot supply two independent replication samples or pooled precision. Their disease/treatment/fasting selections and survey periods differ. The builder retains the differing Black-female urate SDs rather than averaging them as independent studies. Sun's incidental pediatric NHANES comparison is disclosed and not represented as an adopted source constraint.

## Independently checked derivation

Using the published Yun group counts and rounded means/SDs, the builder's pooled sample-variance formula correctly includes within-group variation and between-group mean differences. Independent arithmetic gives:

- pooled urate mean 5.250058788947678 mg/dL and SD **1.5980016361448122**;
- pooled BMI mean 28.880011757789532 kg/m² and SD **7.393740265856269**;
- `0.322 × SD(urate) / SD(BMI)` = **0.06959353565810426**.

This verifies arithmetic only. The numerical result is an **assumption-dependent scale guide**, not an identified slope for the reduced target model. Even under the usual standardization convention, the conversion would give a raw coefficient conditional on smoking/alcohol as well as the other covariates. Removing smoking/alcohol requires a further assumption about their joint distribution and contribution given the available predictors. A numeric conversion alone cannot justify that marginalization. The final specification should make this omitted-covariate/transport assumption explicit if it retains the 0.07 working guide; otherwise it can keep 0.322 as a qualitative clue. This review supplies no alternative desired numeric coefficient.

## Construction assumptions to retain in interpretation

The BMI hinge at 40 with half-slope above it, sex-specific age slopes 0.005/0.020, common initial BMI slope and residual-scale guides 1.20/1.10/1.40/1.55 are disclosed Agent choices. The inspected original evidence does not establish those numeric values. A source mean used at source mean covariates is a location-centering approximation, especially with a nonlinear hinge and omitted predictors. Smaller residual-scale guides do not constitute an empirically estimated variance decomposition.

These choices can be evaluated as a candidate; insufficient identification need not prevent an honest experiment. But age/curvature/interaction outputs are **assumption-sensitive reuse analyses**, not discoveries that were unconstrained in construction. In particular, the hinge imposes a shape prior even without a quadratic coefficient target, and a common initial slope is an interaction assumption. No expected sign or value is supplied by this reviewer, and no change is based on target outcomes.

Several mean evidence items encode participant SD using `uncertainty.kind=sd`. The surrounding prose and separate urate-SD entries identify these as participant dispersion. Keep that distinction explicit throughout the final artifacts: they must not be used as standard errors, estimate uncertainty or inverse-variance weights for the means. The current source-check subset does not use those fields to weight a fit.

## Source-check comparability

The proposed native subset contains 13 entries:

- Four subgroup arithmetic urate means.
- Four subgroup n-1 urate SDs.
- Four subgroup `BMI ~ intercept + urate + age` coefficients, restricted to observed ages 20–54.
- One explicitly not-computable exact Yun standardized-path check.

The 12 numeric operators align with their evidence types, units and variable orientation. They are correctly marked **approximate transport diagnostics**. The actual table is target-shaped; it does not recreate the original population or its fasting/treatment restrictions. The Sun selection lacks age 19 and the source covariate distribution, while target ages 55–56 are excluded for that diagnostic. Matching a native source regression is useful checking but is not exact source reproduction or independent target validation.

The additional proposed reduced-adjustment standardized model, combined descriptive quadratic/interaction model, residual descriptions and extra quantiles do not have admitted numeric source targets. They are not part of the 13-entry source-check subset currently intended for the controller. Do not claim these were computed, calibrated or scientifically validated merely because the proposal lists them. If later used as generated-table diagnostics, label them separately; their formulas do not replace the frozen target-evaluation formulas. The original target protocol's separate curvature and interaction models remain unchanged.

## Retrieval evidence and pending access

Gateway state at this snapshot records six queries, two downloads and four auxiliary requests, with 17 queries/seven downloads remaining in the initialized session. The research note's usage agrees. The successful Yun fetch is another version/acquisition of an existing study, not independent evidence. Its different artifact hash is acknowledged, and adopted extraction cites the original supplied XML.

The PMC6941025 full-text fetch was rejected by the alias screen; the builder does not claim to have read it. Yun supplement discovery reports an unsupported DOCX, likewise not read by the builder. The request for controller-assisted provenance/access review is legitimate and does not justify silently bypassing the gateway or resetting budgets. Full-content approval, exposure and usage should be recorded before any new material enters construction. Final review should rehash the completed handoff after those admission decisions and any resulting builder amendments.

## Status

No fabricated extraction, incorrect native regression orientation or target-outcome feedback was found in this stage 1 snapshot. The central remaining issue is how strongly to interpret the assumption-derived working forward model, not a transcription error. Final handoff approval is pending the requested source-access decisions and the final artifact hashes. No builder file was edited by this reviewer.

## Stage 2 source-admission and extraction addendum

30 October 2026, reviewed while literal authorship was still in progress. **The updated source extraction and model specification pass material scientific review at this snapshot.** Final handoff hashes and any source-check-plan amendments remain to be bound after builder completion. The earlier stage 1 text records the earlier state; its pending source-access decisions have now been resolved by the controller.

| Updated artifact | SHA-256 at this review |
|---|---|
| `visible/bundle/candidates/initial/evidence.json` | `8956bfd491b9c9a9e9f39c90e276a6e647c1393c289e0a9307f062a9f0f8c69c` |
| `visible/bundle/candidates/initial/model_spec.json` | `22be42657b3603e533c05489932ce14c880cbfe4c01a9fc57a7c816d09478a44` |

The controller's `SUPPLEMENTAL_SOURCE_ACCESS.md` and `visible/research/controller_source_admission.json` document two charged acquisition attempts and explicit admission of seven artifacts. Independently hashed all seven admitted files; each matches both its admission entry and the visible registry:

| Artifact under `visible/bundle/sources/controller/` | Verified SHA-256 |
|---|---|
| `PMC6941025.xml` | `e3a9523f20628c54800933f1dec18239c8793703fc10a2e48e6ed7e8f2b0b679` |
| `PMC6941025.txt` | `3ff4cd40ef0ff94f3abddd3d5d27581d10a2dcd2ea3b07f596e45a427db5b99c` |
| `PMC8236402.supplement.docx` | `417a28f721b2f07f78a5beb2680bdc7c0cf765aebcf207871de52af99cd9c790` |
| `PMC8236402.supplement.txt` | `1a5566cdf608f379cbcc625517cb9e7076d4b8c79bce2e114769199f9b12a400` |
| `PMC8236402.supplement.image1.png` | `8b2591ffafd67735c767c7d1b782418e68fc9109451ab493c1b5abf57d8fe997` |
| `PMC8236402.supplement.image2.png` | `815f25957e2134b87e4e0b0882aa87b435dd59af70309611f5ea7862a752c5e2` |
| `PMC8236402.supplement.image3.png` | `b813cbc03b9ad1c18a30cd0b5de8be1bf03360f2b76e65dce03a1790acd9c47e` |

Read the Ferrara original XML body and all three original tables, and independently decoded the authoritative Yun DOCX's `word/document.xml` to inspect all three supplemental tables. DOCX ZIP CRC checking passed. Numerical extraction below is verified against the original XML/DOCX tables, not merely against the controller's prose or the derivative text. Embedded figure files were hash-verified, not visually transcribed; no new adopted value depends on those figure pixels.

**Ferrara original.** The source describes 358 apparently healthy Caucasian women in Ferrara, Italy, including 124 premenopausal and 234 postmenopausal women, recruited from the university's densitometry clinic and employees. Menopause is defined by menstrual history, not an age threshold. Table 1 reports age 35±10 versus 55±4 years, BMI 23±4 versus 25±3 kg/m², and urate 225±76 versus 239±76 µmol/L. Results 2.1 explicitly state no significant urate mean difference. Table 2's unadjusted BMI–urate Pearson correlations are −0.013 and 0.345; the latter bears the p<0.001 marker. The asterisk next to −0.013 identifies the correlation coefficient, not statistical significance. The builder preserves source units and does not convert these to US subgroup anchors, adjusted age effects or menopause labels for individuals.

Ferrara Table 3's adjusted coefficient 0.220 concerns **total-hip BMD as outcome**, not urate as outcome; the BMI-added model gives 0.119. The source has an inconsistent final-column heading, but its model footnote and narrative identify the outcome. The builder does not misuse these coefficients. The original's incidental discussion of NHANES is admitted and recorded as exposure; it is not adopted as a numerical construction constraint. Ferrara provides a distinct recruitment source, whereas Yun, its supplement and Sun remain overlapping Bogalusa evidence.

**Yun supplement.** Table S3's adult BMI→urate paths are standardized: men 0.332 (n=1521) and women 0.407 (n=1881); the reported between-sex p value is 0.675. The builder labels them dimensionless and does not interpret nonsignificance as proof of equal effects. Parent Methods supply the adjustment context; the exact stratified design matrix and standardization implementation are not recovered. Supplemental adult longitudinal paths 0.064/0.069 are not substituted for contemporaneous relationships.

Independent source-only arithmetic, pooling the original Table 2 counts and moments separately within sex, gives:

| Derivation | Men | Women |
|---|---:|---:|
| Pooled source urate SD | 1.3705014066046708 | 1.3996635679443556 |
| Pooled source BMI SD | 6.46455448081726 | 8.053382566189569 |
| Standardized effect × SD(urate)/SD(BMI) | 0.07038481435076838 | 0.07073587619504916 |

These exactly match the updated specification's arithmetic. Their interpretation remains conditional on the stated standardization and omitted-covariate assumptions; neither number is a published raw reduced-model coefficient. The new `A_omitted_covariate_transport` explicitly addresses the stage 1 concern. Participant SDs remain dispersion measures and are not used as SEs or inverse-variance precision.

**Remaining construction choices are explicit.** The female working age guide changed from 0.020 to 0.010 mg/dL/year before literal authorship. The change is disclosed as an Agent modeling judgment informed by the weak Ferrara group comparison. A nonsignificant, unadjusted between-group difference does not quantitatively identify that slope or justify halving a conditional age effect; the current specification correctly makes neither claim. Male age guide 0.005, the BMI-40 hinge/half-slope, common working BMI slope and residual-scale guides remain explicit assumptions. These are permissible experimental choices, with no target-informed numbers supplied by this reviewer. Any favorable target age, curvature or interaction result must still be interpreted as assumption-sensitive transfer/reuse, not identification of an unconstrained relationship.

No material extraction, unit, orientation, overlap or undisclosed numerical-assumption error was found in this updated evidence/spec snapshot. The source-check plan was still its stage 1 version during this review, so its old “unread/rejected” entries require final-state reconciliation rather than being treated as the final access record. No generated table, private reference outcome or old target output was opened; no row was produced or repaired, and no source diagnostic or target analysis was executed by this reviewer.

## Final initial-candidate handoff: PASS

30 October 2026, after builder completion and native-recipe packaging. **PASS for source extraction, declared construction assumptions, exposure accounting and source-check comparability/binding. The initial candidate may proceed to the controller's freeze and permitted source-only feedback step.** This approval establishes neither source agreement nor target validity; neither was evaluated by this reviewer.

The final evidence file is unchanged from the audited stage 2 snapshot. Final model-specification changes record completion/provenance; the reviewed scientific numerical choices are retained. The research ledger preserves chronological stage 1 history and then explicitly records Ferrara/supplement admission, incidental NHANES discussion exposures, three unique original papers from two recruitment populations, literal authorship and no source-statistic execution. Its final source-check plan now resolves the earlier unread/rejected-source entries. The decision document and checks distinguish approximate transport diagnostics from exact source replay, participant SD from mean precision, and assumptions from extracted effects. No new material scientific issue was found.

Independently compared the native `source_checks.json` against the reviewed plan as structured objects. **All 13 entries match** in evidence ID, status/comparability, operator, selection, reason and assumption references. The 12 computable entries retain four means, four sample SDs and four native BMI-on-urate age-adjusted regressions. All 12 point to `generated.csv` with the single controller-confirmed hash below and `agent_supplied_simulation` origin. The exact Yun path retains null table/operator and `not_computable` status. All referenced evidence kinds/units and assumption IDs agree; no additional coefficient, target-value constraint or diagnostic was introduced while packaging. All six artifact hashes referenced by final `checks.json` match the actual audit files. No mismatches were found.

Final artifact bindings, paths relative to `visible/bundle/candidates/initial/`:

| Artifact | SHA-256 |
|---|---|
| `evidence.json` | `8956bfd491b9c9a9e9f39c90e276a6e647c1393c289e0a9307f062a9f0f8c69c` |
| `model_spec.json` | `40e6cf9be459c5b2092b1895a9c337d2c55b46aa6eeed31bf04d8551b93b7344` |
| `source_checks.json` | `e07f838008dac6405fb9325beb236d4a5ee14b5aadf44e9aff15bab504cb6aa3` |
| `checks.json` | `9966f50a250828b25b0062c01ffb42331518408daba538e408f37dbbe5582472` |
| `decision.md` | `05ae9383f2bfed627ba07daaf15394ed6120615020a9fa21e81148010f9b8d0b` |
| `audit/evidence_gap_and_search.md` | `817f73822818ea3705a43ba64f658b14e2c1d668b4103ba0fb4aee91e8390e6d` |
| `audit/source_check_plan.json` | `7dbfcdd8c93355a1bab77670e36c8d9b749bbb402e9916d721dc65d711ca29a6` |
| `audit/controller_source_admission.json` | `ebfce65074830d6d195b97ae2c03d775dbd7a9a2d7d5725deb3d5d8f14c0f7d0` |
| `audit/controller_access_budget.json` | `7301df78003538d9d4f0be7cfde41bb77575fc41bd546b1042782285a48c121d` |
| `audit/source_check_recipe_binding.json` | `70408e2bafe3be20c977aa1b1468ebf924aa17bd94ff34aed9c311293fd2f54a` |
| `audit/structural_preservation.json` | `ced098f10cffc2a9e3e09fba3fc4794b9a8aaa4fcaf2e9446a0d1be02a9e202a` |

The recipe, metadata receipts and root controller consistently identify generated-table SHA-256 `69b01e7ec84cef431da50d394040edfe661413c5541130b8960490c541607b42`. This reviewer checked that binding without opening or independently rehashing the generated CSV. Root separately reported successful structural preservation and direct-route validation. The recipe-binding audit records express controller authorization for the builder's narrow interface-only read of `cohort_harness/source_checks.py`; this supplied an envelope, not outcome information or scientific parameter values.

The final review has not opened generated row values, the private reference, raw target outcomes or old target results; has not executed source/target statistics; and has not modified the candidate, protocol or generation choices. It closes the source-audit gate only. Any future candidate revision requires its own provenance and new binding, while the disclosed nonidentification/transport limitations remain applicable.
