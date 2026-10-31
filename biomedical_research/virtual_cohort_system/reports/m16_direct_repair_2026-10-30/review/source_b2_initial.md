# Independent source/specification review — b2 initial

**PASS for pre-authoring commitment.** No blocking factual, arithmetic or technical mapping error was found. This is permission to proceed to the scheduled commitment step, not evidence that the scientific construction or future table is valid. No coefficient direction or target answer was proposed.

## Scope and integrity

Reviewed only b2's initial evidence.json, model_spec.json, audit/construction.json and audit/revision_plan.json; b2 task/registry metadata; registered originals and Yun supplement; and the controller's Korean-source admission record. All registered artifact hashes verified. There was no generated.csv at review completion. No private target outcomes, raw target files, other builders, other candidate data or past target results were accessed. No candidate artifact was edited and no outcome rows were generated.

The 176 evidence items comprise 172 numeric items and four contextual items. Independent XML table parsing compared 166 reported numeric estimates and all corresponding mean-associated SDs with the original tables: Yun Tables 1–2, Sun Tables 1–2, Bonaccorsi Tables 1–2, and Lee Table 1. All matched. The six remaining numerical items were checked directly against Yun Figure 2/text, Supplement Table S3, and the cross-lagged results text/Figure 1. All matched. This distinguishes source transcription verification from the scientific transfer assumptions.

## Source meaning and adopted construction

Yun adult race/sex means and SDs, age/BMI centers, sample sizes and standardized mediation coefficients are transcribed consistently. The central BMI guide is explicitly a derived working quantity, not a directly reported raw coefficient: independent pooling with within- and between-group terms and the n−1 denominator reproduced N=3402, SD(urate)=1.5980016361448122, SD(BMI)=7.393740265856269, and 0.322 × SD(urate)/SD(BMI)=0.06959353565810426, subsequently rounded by the builder to 0.07. The assumption states that the exact standardized-path convention and transport to a different covariate distribution are unresolved. No reverse-regression reciprocity is used.

The four longitudinal descriptive secants independently recompute to 0.00555556, 0.02168224, 0.01930693 and 0.04150442 mg/dL/year after the builder's stated BMI subtraction. They are explicitly distinguished from adjusted cross-sectional age effects, causal aging effects, and the chosen age-guide coefficients. Lee's mixed-sex age-band means are correctly treated as marginal population context, not as an adjusted age coefficient or target calibration. Korean recruitment, medication selection, age support, different covariate composition, and unspecified assay are disclosed.

The .94 scale multiplier is explicitly heuristic. Multiplying it by the four source marginal urate SDs reproduces all four declared scale-guide values. The file does not claim that these are estimated residual SDs or a valid adjusted-model variance decomposition. The working_guides interpretation, unknown tails/within-group heteroscedasticity, age hinges and BMI hinge assumptions remain explicit. Bonaccorsi's Pearson correlations retain the reported menopausal grouping and original concentration units; they are not converted into universal age-specific effects.

Embedded construction exactly equals audit/construction.json. Independent scalar evaluation at the four source mean age/BMI anchors reproduced the declared locations and scale values. Every adopted numerical centering/lookup/guide constant is accounted for by source evidence or a named assumption. The summary formula, hinge values and expression agree. Task, evidence, model and expression validators passed without reading target rows.

## All 23 planned checks

| Planned checks | Count | Review |
| --- | ---: | --- |
| Yun race/sex urate means and SDs | 8 | Correct original groups, variables and mg/dL units; all approximate target-shaped comparisons, with transport/assay assumptions. |
| Sun BMI-on-urate age-adjusted slopes | 4 | Correct regression direction, outcome BMI, urate term, age adjustment, stratum filters and kg/m² per mg/dL units. BMI is not added as its own predictor; the Table 2 dagger footnote is respected. Intercept use is disclosed as conventional. |
| Yun adjusted standardized paths | 5 | Not computable; omitted smoking/alcohol and exact standardization are not silently replaced by a reduced model. |
| Bonaccorsi menopausal Pearson correlations | 2 | Not computable; chronological age is not substituted for measured menopausal state. |
| Lee age-band urate means and SDs | 4 | Correct original marginal values/SDs, mg/dL units and age predicates. Source <40 versus target 20–39, and source 40–59 versus target 40–56, are explicitly approximate comparisons. |

All 16 executable planned comparisons are approximate and name existing assumptions; all seven not-computable items have null operators. Exact selected variables, outcome direction, units, categories and age predicates match their declared source mapping. No scientific equality tolerance or required sign is introduced. Actual numerical source checks remain deferred until authored rows are frozen.

## Admission and overlap

The Korean original is present in b2's registry with hashes matching source_admission/b2/ADMISSION_REVIEW.json. It is an independently recruited KAHP/HIRA study, not an NHANES sample; incidental NHANES citations are disclosed and no cited NHANES numerical result is among the adopted items. The admission ledger records three cumulative acquisition attempts and one newly admitted original. Yun/Sun overlap is disclosed, and the source count does not treat those papers or repeated subsets as independent cohorts.

## Bound candidate bytes

- evidence.json: `e309b9b9aaef0f9a47113da2727c85e3b9a00fccc80ad8be8a783657736d9998`
- model_spec.json: `a355315f8c83c98cd587c82d2847804820939e0298f0cc6bc6347a5fa3eb0323`
- audit/construction.json: `f62b54747f4e4d53eb5f8c0eecd12ac236fdf1e45a15732ca26ab7235ee885cb`
- audit/revision_plan.json: `66f8f3acb650c4d4096f7a0a0b4a3e7c5439574f8171b76e25ea48d33ae216b3`

Target release remains locked. This review does not establish literal authorship, final preservation, realized source fit, or target utility; those remain later scheduled checks.
