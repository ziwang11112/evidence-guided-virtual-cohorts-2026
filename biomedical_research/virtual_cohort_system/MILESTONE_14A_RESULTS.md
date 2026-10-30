# M14-A: external evidence audit and bounded decision

30 October 2026. **One externally specified conditional-mean alternative is worth retaining as a future sensitivity test. No supported scanner correction, conditional residual repair or transport-uncertainty distribution was found.** The audit is complete; no new target was acquired and no generator was run. The exposed M13-B body-fat target remains closed to calibration and independent revalidation.

This is a conditional go for a revision **specification**, not a positive validation result. The six-paper budget is exhausted. Further searching or outcome-driven adjustment within this branch is not scheduled.

## Why this audit was needed

[M13-B](MILESTONE_13B_RESULTS.md) completed one real-target screen: 842 participants, 16 generated/reference tables and 62 scheduled analyses. Source-statistic feedback improved source fit without consistently improving the target analyses. Primary means were low, BMI associations too strong, spread changes differed by sex and generated male-age intervals omitted important uncertainty. Those discrepancies motivate the audit, but do not identify their biological or technical cause and cannot supply new parameter values.

The method's objective remains evidence-guided virtual data that can support scientific analyses. The important next question is whether independent published information supports a specific, testable change. More optimization, Agents or synthetic rows cannot provide evidence that the sources do not contain.

## What was examined

Two researchers independently retrieved relationship and measurement evidence, and a third checked the central extractions and decision. Exactly six additional primary studies were examined. Five supplied full relevant text/tables; the Gomez-Ambrosi main text was accessible, but image-only tables and supplementary material remained unavailable. This limitation is retained. Official CDC documents were used only for technical measurement definitions. No NHANES-derived biological quantities were admitted as generator constraints.

| Study | Relevant evidence | Admission and limitation |
|---|---|---|
| [Deurenberg et al., 1991](https://doi.org/10.1079/BJN19910073) | Adult age/BMI/sex body-fat equation and validation errors | Densitometry/Siri endpoint; a conditional relation in its own setting, not a DXA conversion or conditional residual law |
| [Pasco et al., 2012](https://doi.org/10.1371/journal.pone.0029580) | Adult DXA quadratic BMI model with sex interactions, age terms, coefficient CIs and pooled regression error | Most relevant structural alternative. Almost entirely White Australian cohort, mixed Lunar devices and unknown software. Model 3 uses available predictors; higher models require lean/bone measurements |
| [Gomez-Ambrosi et al., 2012](https://doi.org/10.2337/dc11-1334) | CUN-BAE formula, separate same-center validation and aggregate prediction errors | Air-displacement plethysmography/Siri endpoint. No identified DXA bridge or joint coefficient uncertainty; inaccessible tables/supplement are not inferred |
| [Diessel et al., 2000](https://doi.org/10.1152/jappl.2000.89.2.599) | Same-person DPX-IQ to QDR-4500 percent-fat comparison, distinct from phantom results | Real instrument-specific relation, but missing the later target hardware/software step and quantitative coefficient uncertainty |
| [Hull et al., 2009](https://doi.org/10.1016/j.jocd.2008.09.004) | Sex-specific component-mass cross-calibration among DPXL, Prodigy and iDXA | Requires fat, lean and bone masses in kg; cannot be applied directly to a percent-fat equation. Version and residual-covariance links unavailable |
| [Shepherd et al., 2012](https://doi.org/10.1002/jbmr.1654) | Prodigy/enCORE14 to Hologic Discovery/Delphi Apex3 percent-fat standardization | Internal calibration evidence, not exact Discovery A/Apex4/NHANES-BCA validation. All adult participants Chinese; lean/component labeling is ambiguous |

Jackson2002 was screened but not fully read: failed access and a pre-read change to the more directly relevant DXA Pasco study are logged. It is not a seventh included study. No unfavorable full-read result was replaced. Sources sharing authors or institutions were not assumed to have independent participants; overlap checks remain explicit where participant linkage is unavailable.

## Evidence-to-analysis decisions

| Evidence or proposed change | Classification | What it can affect | What it does not establish |
|---|---|---|---|
| Pasco Model 3 printed coefficients, centering and sex coding | Usable reported constraint in the source context | Conditional mean, BMI shape, sex contrasts and age association | That the equation transfers to another population/device or improves M13-B |
| Derivatives and contrasts of that exact equation | Defensible derived constraint | Check implementation and describe source-implied shape | New target regression estimates or a novel biological discovery |
| Pooled regression S or SEE from any selected relation | Reported descriptor; conditional law unresolved | A possible explicitly assumed sensitivity scale | Sex/age/BMI-specific residual SD, individual truth or source/transport uncertainty |
| Diessel human, Hull component and Shepherd PFAT equations | Usable reported constraints on their stated instruments | Instrument-conditioned location/scale or component harmonization | A complete chain to the target measurement pipeline |
| BCA as a universal +5 pp shift | Incompatible | None as justified here | A Lunar-to-Hologic correction. CDC describes reallocation of a fraction of lean mass |
| Derive change in fat percentage from lean-mass reallocation | Defensible conditional algebra | Identify the units and required components | The correct source-to-target bridge or the exact unreported software convention |
| Coefficient CIs without covariance | Unresolved joint uncertainty | Inspect marginal estimation precision | Independent coefficient draws, calibrated model weights or full inferential intervals |
| Cross-study measurement, selection and population differences | Unresolved transport assumptions | Define applicability and required validation | A license to fit target-specific intercepts, slopes or sex SDs |

The detailed extracts, exact bridge orientations, source locators and retained numerical inconsistencies are in the [audit packet](reports/m14_evidence_portability_2026-10-30/README.md). The inconsistencies include participant-count arithmetic and, in Shepherd, manufacturer-specific lean/component labeling. They are not silently corrected and do not establish which interpretation is true.

## The single retained revision

Use the whole published Pasco Model 3 conditional mean as one alternative, without fitting its coefficients to the exposed target. Keep one incumbent residual mechanism unchanged so a later comparison isolates the mean structure. Pasco's pooled regression error is **not** substituted as a newly established target residual law. The [complete specification](reports/m14_evidence_portability_2026-10-30/revision_specification.md) records its parent, exact formula, unchanged assumptions, prohibited adjustments and future target requirements.

This is an opportunity to test a source-supported structure, not evidence it will win. For example, its source-centered local BMI slopes remain substantial; no target prediction or evaluation was used to claim that the earlier excessive slope is repaired. Age/curvature terms supplied by this paper would be assessed as transport, not as previously unreported findings.

The six studies do not complete the measurement bridge to the prior target. A name such as Lunar, Hologic or DXA is not enough to compose conversions across software versions and component conventions. No constant BCA offset, reverse regression, phantom variance or component-mass SEE is promoted into a percent-fat generator parameter.

## What is closed, and what would be needed later

- **Closed:** further scalar tuning of the old body-fat target, target-derived residual repair, and an unsupported exact scanner correction. Preserve the negative and mixed M13-B results.
- **Retained, not executed:** one source-mean substitution specification. It is a sensitivity candidate with inherited residual assumptions, not a validated new data release.
- **Required for a new experiment:** a separately admitted real cohort with an unexposed measured endpoint, documented measurement pipeline, permitted covariates and a protocol frozen before outcome access. No such cohort was downloaded, selected by outcomes or admitted in this audit.
- **Method claim:** evidence translation and honest analytical applicability remain the focus. Copying a published regression equation is not itself a novel method, and this audit demonstrates neither Agent superiority nor publication readiness.

The bounded follow-up ends here. It does not automatically start a new cohort search, calibration or generation run. Ordinary local documentation and the approved private GitHub summary export are the only completion operations.

## Verification boundary

The independent reviewer checked the central equations against original tables/text and reviewed the proposed specification. Root separately inspected Pasco Table 4 and its measurement/selection methods. Artifact integrity checks cover the historical M13-B freeze, unchanged harness modules and unchanged aggregate results; no biomedical reanalysis was performed. Source documents remain local, and the distributed packet contains extracts and citations, not patient rows or full copyrighted source copies.
