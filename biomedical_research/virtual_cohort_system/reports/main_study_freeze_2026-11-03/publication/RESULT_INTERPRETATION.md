# Main-study result interpretation and claim audit

**Status: independent arithmetic matched.** Descriptive scientific interpretation only.

The independent audit reports 22713 checks, 2196 numeric comparisons and maximum numerical difference 4.263256414560601e-14, with zero errors and zero unavailable slots. Its result hash matches the current result (`1fbc32d2f982d31c649d9217e644a34c02b81e08c093380fba8f3aaec9e4c2cb`). This verifies retained-output arithmetic and frozen aggregate mapping, not clinical validity or a new patient-level reanalysis.

All 24 constructions and all 72 scheduled final slots are represented: 72 successful executions, 72 complete analyses and 72 distinct successful table contents. Only aggregate outputs and frozen metadata were used. No row table was inspected and no new experiment, hypothesis test, model fitting, revision or selection was performed.

## Prespecified information contrasts

For each endpoint, E1 minus E0 compares arm means of each constructor's mean absolute discrepancy over three fixed final seeds. Each Agent arm contains five constructors, all complete. A negative difference indicates a smaller discrepancy from the sample-reference point estimate. It does not establish equivalence, clinical interchangeability, significance or causal mechanism. Information-condition E1 and CHNS endpoint E1 are distinct labels.

| Case / endpoint | Coefficient | Unit | E0 discrepancy | E1 discrepancy | E1 − E0 |
|---|---|---|---:|---:|---:|
| CHNS2009 / E1 | BMI, adjusted for age and sex | %/(kg/m^2) | 0.02037954115369707 | 0.03155742004126274 | 0.011177878887565669 |
| CHNS2009 / E2 | Glucose, adjusted for age and sex | %/(mmol/L) | 0.13401851811577342 | 0.024079198100703313 | -0.1099393200150701 |
| CHNS2009 / E3 | Age, adjusted for sex, BMI and glucose | %/year | 0.007280703148418075 | 0.004854465203797137 | -0.0024262379446209383 |
| ENSANUT2018 / Q1_age10 | Age, adjusted for sex, BMI and glucose | %/10years | 0.06394421717668655 | 0.024670383036047308 | -0.039273834140639244 |
| ENSANUT2018 / Q2_bmi5 | BMI, adjusted for age and sex | %/5kg/m^2 | 0.05688301554340984 | 0.023732008836695483 | -0.03315100670671436 |
| ENSANUT2018 / Q3_bmi5 | BMI, adjusted for age, sex and glucose | %/5kg/m^2 | 0.04879666583854892 | 0.025649331631140568 | -0.023147334207408353 |

Five of six contrasts favored E1 descriptively. CHNS BMI is the counterexample among the prespecified endpoints: discrepancy increased by 0.011177878887565669 percentage points per kg/m². Unlike coefficients are not pooled; five of six is not an independence claim or a hypothesis test. Distinct authors and their completion/transport assumptions contribute to the information conditions, so this comparison does not isolate an algorithmic component.

## Sample references and uncertainty

| Case / endpoint | Reference coefficient | Reference lower | Reference upper | Unit |
|---|---:|---:|---:|---|
| CHNS2009 / E1 | 0.05494608227224506 | 0.04572624759489867 | 0.06416591694959145 | %/(kg/m^2) |
| CHNS2009 / E2 | 0.4020933879135471 | 0.37128635859620074 | 0.43290041723089345 | %/(mmol/L) |
| CHNS2009 / E3 | 0.008107035072072662 | 0.006387035326816245 | 0.00982703481732908 | %/year |
| ENSANUT2018 / Q1_age10 | 0.07513235976455014 | 0.06712403846043223 | 0.08218524233916669 | %/10years |
| ENSANUT2018 / Q2_bmi5 | 0.08364283892711358 | 0.07037325983526749 | 0.09521350127811261 | %/5kg/m^2 |
| ENSANUT2018 / Q3_bmi5 | 0.05663753525952589 | 0.043900521557340054 | 0.06800596410272369 | %/5kg/m^2 |

CHNS intervals are 95% community-cluster CR1-t intervals for the selected, unweighted age-35–74 analytical sample. ENSANUT bands come from the prespecified 399-attempt cluster-resampling stability procedure for the age-25–79 equal-cell analytical standard; they are not national confidence intervals. All six reference intervals are positive, but remain uncertain sample estimates. They are neither population constants nor equivalence/acceptance bounds.

ENSANUT scales age per 10 years, BMI per 5 kg/m² and glucose per 10 mg/dL where applicable. CHNS uses raw age/BMI scales and glucose in mmol/L. Selection and measurement rules also differ; cross-case effects must not be pooled.

## Direction, magnitude and author variability

| Case / endpoint | Arm | Range of five constructor means | Range of five constructor mean absolute discrepancies | Positive / negative seed coefficients |
|---|---|---|---|---|
| CHNS2009 / E1 | E0 | -0.0005579316816458658 to 0.073973454479348 | 0.006273494752704912 to 0.05550401395389092 | 13 / 2 of 15 |
| CHNS2009 / E2 | E0 | 0.0038568410324386396 to 0.4623941604146956 | 0.0366644392064717 to 0.39823654688110843 | 14 / 1 of 15 |
| CHNS2009 / E3 | E0 | -0.0010122399978529516 to 0.004744076954921871 | 0.003362958117150792 to 0.009119275069925614 | 7 / 8 of 15 |
| CHNS2009 / E1 | E1 | 0.012399970129407514 to 0.04575656720989321 | 0.009189515062351848 to 0.042546112142837544 | 15 / 0 of 15 |
| CHNS2009 / E2 | E1 | 0.36336253385170453 to 0.41418940890722056 | 0.012096020993673443 to 0.03873085406184259 | 15 / 0 of 15 |
| CHNS2009 / E3 | E1 | -0.00050934048274624 to 0.007393436157991897 | 0.0014577553186925418 to 0.008616375554818902 | 13 / 2 of 15 |
| ENSANUT2018 / Q1_age10 | E0 | -0.0014744271306858746 to 0.03202137690049773 | 0.04311098286405241 to 0.07660678689523602 | 11 / 4 of 15 |
| ENSANUT2018 / Q2_bmi5 | E0 | -0.000915586219038753 to 0.07568791696368164 | 0.00795492196343194 to 0.08455842514615233 | 10 / 5 of 15 |
| ENSANUT2018 / Q3_bmi5 | E0 | -0.0008962349300190906 to 0.0220191860952011 | 0.03461834916432479 to 0.05753377018954498 | 10 / 5 of 15 |
| ENSANUT2018 / Q1_age10 | E1 | 0.0977687165339455 to 0.1024516279586996 | 0.022636356769395367 to 0.027319268194149458 | 15 / 0 of 15 |
| ENSANUT2018 / Q2_bmi5 | E1 | 0.05645919759096775 to 0.06251504411793557 | 0.021127794809178008 to 0.027183641336145828 | 15 / 0 of 15 |
| ENSANUT2018 / Q3_bmi5 | E1 | 0.02499659222497035 to 0.04209058466452136 | 0.014546950595004526 to 0.031640943034555544 | 15 / 0 of 15 |

These ranges include all five authors; 15 final seeds per arm are conditional simulations, not clinical replications. Ranges are not confidence intervals and do not propagate source-estimation, structural or transport uncertainty. Author labels reused across arms do not define a paired comparison.

CHNS E1 BMI means were 0.012399970129407514–0.04575656720989321, all below the reference 0.05494608227224506. Every E1 BMI seed was positive, so direction agreement did not prevent worse aggregate magnitude discrepancy. E1 glucose means varied from 0.36336253385170453 to 0.41418940890722056 against 0.4020933879135471, despite the smaller arm discrepancy.

CHNS E1 conditional-age means ranged from −0.00050934048274624 to 0.007393436157991897 against 0.008107035072072662. A03 retained a negative mean and two negative final seeds. The arm-average decrease in discrepancy therefore did not imply uniform directional recovery. The CHNS packet did not supply this conditional age relationship; Pani was absent from both conditions. Each modeled age value remains an assumption-dependent consequence.

All ENSANUT E1 Agent final-seed focal coefficients were positive. E1 age means were 0.0977687165339455–0.1024516279586996 against 0.07513235976455014; every final age seed exceeded the reference-band upper bound 0.08218524233916669. BMI means were 0.05645919759096775–0.06251504411793557 before glucose adjustment and 0.02499659222497035–0.04209058466452136 after adjustment, against 0.08364283892711358 and 0.05663753525952589. All five constructor means for each BMI endpoint were below its reference-band lower bound. Interval position describes mismatch and does not define a pass/fail rule or test the arm contrast.

Source-analogous CHNS BMI/glucose and ENSANUT age/BMI projections were available under E1, with target values withheld. ENSANUT conditional BMI (Q3) was not supplied or algebraically identified by the packet. Its smaller E1 discrepancy is not discovery of a relationship or evidence of mediation: completion and transport assumptions determine the joint conditional projection.

## Statistical references and asymmetric comparison

Every statistical construction and focal endpoint is shown below. Statistical values are over three seeds; Agent values are arm means over five constructors. One fixed statistical specification per case/condition versus five independently authored Agent models is a descriptive, asymmetric comparison, not a general superiority experiment.

| Statistical constructor / endpoint | Statistical mean coefficient | Statistical discrepancy | Agent arm discrepancy |
|---|---:|---:|---:|
| CHNS2009_E0_S01 / E1 | -0.0029312482302423747 | 0.05787733050248743 | 0.02037954115369707 |
| CHNS2009_E0_S01 / E2 | 0.017343813162206942 | 0.3847495747513402 | 0.13401851811577342 |
| CHNS2009_E0_S01 / E3 | 0.00012132871330528218 | 0.007985706358767379 | 0.007280703148418075 |
| CHNS2009_E1_S01 / E1 | 0.002390644112047728 | 0.05255543816019734 | 0.03155742004126274 |
| CHNS2009_E1_S01 / E2 | 0.39256990103927847 | 0.012021417276057619 | 0.024079198100703313 |
| CHNS2009_E1_S01 / E3 | 0.00022894200975668124 | 0.007878093062315981 | 0.004854465203797137 |
| ENSANUT2018_E0_S01 / Q1_age10 | -0.0016641741364342322 | 0.07679653390098437 | 0.06394421717668655 |
| ENSANUT2018_E0_S01 / Q2_bmi5 | -0.001735577023325579 | 0.08537841595043916 | 0.05688301554340984 |
| ENSANUT2018_E0_S01 / Q3_bmi5 | -0.0017076167779998656 | 0.05834515203752576 | 0.04879666583854892 |
| ENSANUT2018_E1_S01 / Q1_age10 | -0.0015477637884946105 | 0.07668012355304475 | 0.024670383036047308 |
| ENSANUT2018_E1_S01 / Q2_bmi5 | 0.05744114373983842 | 0.02620169518727516 | 0.023732008836695483 |
| ENSANUT2018_E1_S01 / Q3_bmi5 | 0.04869757513774934 | 0.007939960121776552 | 0.025649331631140568 |

Under E1, statistical CHNS glucose discrepancy was 0.012021417276057619, below every corresponding Agent discrepancy (arm mean 0.024079198100703313). Statistical ENSANUT conditional-BMI discrepancy was 0.007939960121776552, also below every corresponding Agent discrepancy (arm mean 0.025649331631140568). Conversely, statistical ENSANUT E1 age had mean −0.0015477637884946105 and discrepancy 0.07668012355304475, larger than every corresponding Agent discrepancy (arm mean 0.024670383036047308). These are endpoint-specific orderings for the delivered constructions.

Numerical uptake also differed: ENSANUT E1 Agents constrained two Jansen projections and the Pani age projection; the statistical specification constrained only the two Jansen projections, keeping the Pani age slope and eight age-band quantities as context because source individual dispersion, source age law and original survey weighting were unbound. This describes different evidence-use decisions; it does not identify the cause of performance differences.

## Evidence use and absence of scientific revision

All E0 constructions had zero admitted relational operations. E1 operation counts are declared, reviewed uses, not independent evidence counts or weights. An analytic check need not match its source value, and a constraint remains qualified by the assumed source-context law.

| Constructor | Model constraints | Analytic checks | Context only | Declined classification | Decision |
|---|---:|---:|---:|---:|---|
| CHNS2009_E1_A01 | 2 | 1 | 1 | 0 | retain |
| CHNS2009_E1_A02 | 2 | 1 | 1 | 0 | retain |
| CHNS2009_E1_A03 | 1 | 3 | 0 | 0 | initial_final |
| CHNS2009_E1_A04 | 2 | 1 | 1 | 0 | initial_final |
| CHNS2009_E1_A05 | 2 | 2 | 0 | 0 | initial_final |
| CHNS2009_E1_S01 | 4 | 0 | 0 | 0 | initial_final |
| ENSANUT2018_E1_A01 | 3 | 0 | 8 | 0 | retain |
| ENSANUT2018_E1_A02 | 3 | 8 | 0 | 0 | initial_final |
| ENSANUT2018_E1_A03 | 3 | 8 | 0 | 0 | initial_final |
| ENSANUT2018_E1_A04 | 3 | 0 | 8 | 0 | initial_final |
| ENSANUT2018_E1_A05 | 3 | 8 | 0 | 0 | initial_final |
| ENSANUT2018_E1_S01 | 2 | 0 | 9 | 0 | initial_final |

CHNS A01/A02/A04 constrained both Jansen projections, checked Bao Pearson and retained MIND Spearman as context. A03 constrained MIND Spearman and checked both Jansen projections plus Bao Pearson. A05 constrained Jansen BMI and MIND Spearman, checking Jansen glucose and Bao Pearson. The statistical specification constrained all four. ENSANUT Agents constrained three projections each; A02/A03/A05 checked all eight Pani age-band means, while A01/A04 kept all eight as context. No record used the explicit `declined` classification, although context-only records can explain declining numerical use.

Across all 24 constructions, seven Agent decisions were `retain`, thirteen Agent decisions were `initial_final`, and four statistical decisions were `initial_final`. Every selected candidate was the initial candidate. No feedback-driven scientific revision occurred. Retention after feedback cannot substantiate revision gains, and unexecuted analytic drafting is not a feedback-to-revision experiment.

The cases share Jansen/Lifelines evidence and measurement guidance. Within-source margins, projections and converted units are not independent replications; Pani age slope and bands share one study. Source estimator uncertainty is not individual dispersion, and unit conversion adds no independent evidence. Source-to-target selection, assays, serum/plasma, ancestry and distributional assumptions remain unresolved. Target-table source replay was unavailable.

## Claim audit and recommended manuscript framing

| Claim | Assessment |
|---|---|
| All 24 constructions and all 72 scheduled final slots completed; all 72 successful table contents were distinct. | supported_descriptive: Operational completion and arithmetic agreement do not establish clinical validity, source reconstruction or transport. |
| E1 had smaller constructor-averaged absolute discrepancy for five of six prespecified endpoints; CHNS BMI discrepancy increased. | supported_descriptive: Unlike endpoints are not pooled or independent confirmations. No significance test, universal benefit or causal evidence-use mechanism is established. |
| Direction agreement coexisted with magnitude mismatch: ENSANUT E1 age means were above and BMI means below their sample references. | supported_descriptive: Reference intervals provide uncertainty context, not acceptance margins. Seed variation is conditional on fixed laws. |
| CHNS E1 conditional-age results varied across authors, including a negative mean and two negative seeds for A03. | supported_descriptive: This relationship was not directly supplied by the CHNS packet; the arm-average decrease in discrepancy does not establish uniform recovery. |
| Statistical and Agent constructions had endpoint-specific ordering; statistical E1 CHNS glucose and ENSANUT conditional BMI had smaller discrepancies than every corresponding Agent. | supported_descriptive: One fixed statistical specification per arm versus five Agent contexts, with different uptake, cannot establish broad method superiority. |
| Seven Agent retain, thirteen Agent initial_final and four statistical initial_final decisions occurred; no feedback-driven scientific revision occurred. | supported_process: Retention after feedback is not a revision gain; analytic drafting without executed feedback is not a correction-loop experiment. |
| E1 authors documented constraints, analytic checks or contextual use for all admitted relational operations. | supported_process: Operation counts are not independent evidence counts. Checks and constraints use assumed source contexts and do not establish source replay or transport. |
| The virtual cohorts are equivalent to or clinically interchangeable with the references. | unsupported: No equivalence design or margin exists, the references are uncertain, and discrepancy or interval position does not define clinical acceptance. |
| The Agent discovered a causal biological mechanism, or extra evidence causally produced the discrepancy changes. | unsupported: Regressions and assumption-completed laws are not causal identification; the arms contain distinct authored models and uptake decisions. |
| These are untouched external confirmations or independent clinical replications. | unsupported: Both target families were researcher-exposed, source evidence overlaps, and repeated generated tables are fixed-law simulations. |
| The Agent generally outperforms statistical synthesis or E1 improves every author and endpoint. | unsupported: Comparison is asymmetric and endpoint ordering is mixed; CHNS BMI and conditional age supply explicit counterexamples. |
| Exploratory feedback demonstrated a beneficial scientific model revision. | unsupported: No construction made a feedback-to-scientific-revision decision. |

Recommended Results/Discussion wording:

In two researcher-exposed development families, the frozen evidence-guided whole-cohort procedure completed all 24 constructions and all 72 fixed final slots. Additional available relational information was associated with smaller constructor-averaged absolute discrepancy for five of six prespecified regression coefficients, while the CHNS BMI projection showed a larger discrepancy. These were descriptive comparisons against uncertain selected-sample references.

The results support a feasibility and limitations account of explicit evidence use and assumption-dependent joint-law construction. Author variability, systematic coefficient shifts and conditional-regression counterexamples limit claims of reliable target recovery. They do not support clinical interchangeability, universal improvement, causal mechanism discovery or general Agent superiority.

The four statistical constructions provide fixed, asymmetric comparisons. Endpoint-specific results and different numerical uptake must remain visible; no favorable author, seed, endpoint or case is selected for a general performance claim.

There was no feedback-driven scientific revision: seven Agent constructions retained their original model after feedback, thirteen finalized their initial model without exploratory feedback, and all four statistical constructions finalized their initial model. This allocation therefore evaluates completed constructions and information conditions, not gains from an iterative correction loop.

Retain all six contrasts, every constructor, all four statistical references, the CHNS BMI/age counterexamples and ENSANUT direction/magnitude mismatch. The 27 CHNS and 28 ENSANUT diagnostics remain in the common aggregate evaluation; focal contrasts do not establish whole-distribution recovery. Both target families were previously exposed to researchers; fresh author contexts do not restore untouched validation. Arithmetic agreement is separate from scientific and clinical validation.

## Complete constructor ledger

Each entry is copied from the frozen summaries: mean coefficient, actual range over seeds 5101/5102/5103, mean absolute discrepancy, and seed signs in that order. Ranges are not confidence intervals. No favorable author or seed is selected. The companion JSON retains full numeric precision and operation classifications.

### CHNS2009

| Constructor / endpoint | Mean coefficient | Final-seed range | Mean absolute discrepancy | Seed directions |
|---|---:|---|---:|---|
| CHNS2009_E0_A01 / E1 | -0.0005579316816458658 | -0.0017985997785323882 to 0.00020023824321677679 | 0.05550401395389092 | -, +, - |
| CHNS2009_E0_A01 / E2 | 0.0038568410324386396 | -0.018183663850455445 to 0.01669486106519057 | 0.39823654688110843 | +, +, - |
| CHNS2009_E0_A01 / E3 | -0.0010122399978529516 | -0.0018409429991152403 to -0.00026148522099471043 | 0.009119275069925614 | -, -, - |
| CHNS2009_E0_A02 / E1 | 0.05748084517472536 | 0.04933798449690814 to 0.061652113919652335 | 0.006273494752704912 | +, +, + |
| CHNS2009_E0_A02 / E2 | 0.2909221176512029 | 0.2826299941693574 to 0.29576794360604386 | 0.1111712702623442 | +, +, + |
| CHNS2009_E0_A02 / E3 | 2.847198527919981e-05 | -0.0004320041266376718 to 0.0008384795165768307 | 0.008078563086793462 | +, -, - |
| CHNS2009_E0_A03 / E1 | 0.0683160743605338 | 0.06478627929360414 to 0.07476842251158335 | 0.013369992088288736 | +, +, + |
| CHNS2009_E0_A03 / E2 | 0.4623941604146956 | 0.46152898383445723 to 0.46406099769371967 | 0.060300772501148514 | +, +, + |
| CHNS2009_E0_A03 / E3 | 0.0005073842429892688 | -0.00044964639298190423 to 0.0019147079962810996 | 0.007599650829083393 | -, +, + |
| CHNS2009_E0_A04 / E1 | 0.062142535287078145 | 0.05415651264474792 to 0.0664815410736449 | 0.007722832766497846 | +, +, + |
| CHNS2009_E0_A04 / E2 | 0.3383738261857528 | 0.32712756642991453 to 0.3443525203740251 | 0.0637195617277943 | +, +, + |
| CHNS2009_E0_A04 / E3 | -0.00013603356706445288 | -0.000652486986480171 to 0.000522646155219786 | 0.008243068639137116 | +, -, - |
| CHNS2009_E0_A05 / E1 | 0.073973454479348 | 0.07042163086833275 to 0.07716376897603641 | 0.019027372207102936 | +, +, + |
| CHNS2009_E0_A05 / E2 | 0.3654289487070754 | 0.3599503737869895 to 0.37363661368169576 | 0.0366644392064717 | +, +, + |
| CHNS2009_E0_A05 / E3 | 0.004744076954921871 | 0.004026612934624493 to 0.005207327017051867 | 0.003362958117150792 | +, +, + |
| CHNS2009_E0_S01 / E1 | -0.0029312482302423747 | -0.005023813001390542 to -0.0017383182359066612 | 0.05787733050248743 | -, -, - |
| CHNS2009_E0_S01 / E2 | 0.017343813162206942 | 0.008032522160290899 to 0.03238215358080434 | 0.3847495747513402 | +, +, + |
| CHNS2009_E0_S01 / E3 | 0.00012132871330528218 | -0.0019860434011363852 to 0.0017421221603028962 | 0.007985706358767379 | +, +, - |
| CHNS2009_E1_A01 / E1 | 0.012399970129407514 | 0.009901388432612603 to 0.015192010796320349 | 0.042546112142837544 | +, +, + |
| CHNS2009_E1_A01 / E2 | 0.41418940890722056 | 0.4022027117548283 to 0.4264367097722286 | 0.012096020993673443 | +, +, + |
| CHNS2009_E1_A01 / E3 | 0.003459351186453364 | 0.003229629086269833 to 0.0038096926542900344 | 0.004647683885619299 | +, +, + |
| CHNS2009_E1_A02 / E1 | 0.012656546911713978 | 0.0067863114897842676 to 0.01824444773673399 | 0.04228953536053108 | +, +, + |
| CHNS2009_E1_A02 / E2 | 0.36336253385170453 | 0.3603056060705957 to 0.367384510770623 | 0.03873085406184259 | +, +, + |
| CHNS2009_E1_A02 / E3 | 0.002413190534485321 | 0.0021144727816853996 to 0.0027274842455474327 | 0.005693844537587341 | +, +, + |
| CHNS2009_E1_A03 / E1 | 0.030979149350999262 | 0.025287178246990064 to 0.03392382430037622 | 0.023966932921245798 | +, +, + |
| CHNS2009_E1_A03 / E2 | 0.37406960673072415 | 0.36250024254169955 to 0.38015503389440736 | 0.028023781182822966 | +, +, + |
| CHNS2009_E1_A03 / E3 | -0.00050934048274624 | -0.0012232354473141257 to 0.00044719147892052834 | 0.008616375554818902 | +, -, - |
| CHNS2009_E1_A04 / E1 | 0.015151077552897648 | 0.01158103454480832 to 0.022256062434753567 | 0.03979500471934741 | +, +, + |
| CHNS2009_E1_A04 / E2 | 0.3865853349847897 | 0.38028344959790605 to 0.3985250026552191 | 0.015508052928757418 | +, +, + |
| CHNS2009_E1_A04 / E3 | 0.00425036834980506 | 0.0030684071088186975 to 0.004884878615039315 | 0.0038566667222676024 | +, +, + |
| CHNS2009_E1_A05 / E1 | 0.04575656720989321 | 0.045460113412840515 to 0.04612351905530039 | 0.009189515062351848 | +, +, + |
| CHNS2009_E1_A05 / E2 | 0.37605610657712696 | 0.36839288098078443 to 0.3902466701291573 | 0.026037281336420155 | +, +, + |
| CHNS2009_E1_A05 / E3 | 0.007393436157991897 | 0.005765061040502542 to 0.009223269678990327 | 0.0014577553186925418 | +, +, + |
| CHNS2009_E1_S01 / E1 | 0.002390644112047728 | -0.00024723683781167617 to 0.004382829263841199 | 0.05255543816019734 | +, +, - |
| CHNS2009_E1_S01 / E2 | 0.39256990103927847 | 0.3778269069337928 to 0.4058402835162306 | 0.012021417276057619 | +, +, + |
| CHNS2009_E1_S01 / E3 | 0.00022894200975668124 | -0.0014203911638713397 to 0.001515570842651874 | 0.007878093062315981 | +, +, - |

### ENSANUT2018

| Constructor / endpoint | Mean coefficient | Final-seed range | Mean absolute discrepancy | Seed directions |
|---|---:|---|---:|---|
| ENSANUT2018_E0_A01 / Q1_age10 | 0.03202137690049773 | 0.028626543555124756 to 0.03511321814530158 | 0.04311098286405241 | +, +, + |
| ENSANUT2018_E0_A01 / Q2_bmi5 | 0.05693149229694355 | 0.055929739066081424 to 0.05845197799180775 | 0.026711346630170028 | +, +, + |
| ENSANUT2018_E0_A01 / Q3_bmi5 | 0.0220191860952011 | 0.020592862112119317 to 0.024071438359429508 | 0.03461834916432479 | +, +, + |
| ENSANUT2018_E0_A02 / Q1_age10 | 0.002215978931479686 | 0.00010519925901001682 to 0.0044577415968311785 | 0.07291638083307045 | +, +, + |
| ENSANUT2018_E0_A02 / Q2_bmi5 | 0.0015740502763664063 | -0.0026277251797673113 to 0.009399191982223143 | 0.08206878865074717 | -, +, - |
| ENSANUT2018_E0_A02 / Q3_bmi5 | 0.0016039057316467467 | -0.002672838259059589 to 0.009411669545425829 | 0.055033629527879144 | -, +, - |
| ENSANUT2018_E0_A03 / Q1_age10 | -0.0014744271306858746 | -0.002528177651351493 to -0.00010504915014013499 | 0.07660678689523602 | -, -, - |
| ENSANUT2018_E0_A03 / Q2_bmi5 | -0.000915586219038753 | -0.0040409839002997034 to 0.003120038211868396 | 0.08455842514615233 | -, -, + |
| ENSANUT2018_E0_A03 / Q3_bmi5 | -0.0008962349300190906 | -0.004052627731058223 to 0.0031668085163593248 | 0.05753377018954498 | -, -, + |
| ENSANUT2018_E0_A04 / Q1_age10 | -0.00034546476937163533 | -0.00519688298079539 to 0.0023154491715166956 | 0.07547782453392178 | -, +, + |
| ENSANUT2018_E0_A04 / Q2_bmi5 | 0.0005212436005658544 | -0.0015249717418755972 to 0.0020369052097060107 | 0.08312159532654773 | +, +, - |
| ENSANUT2018_E0_A04 / Q3_bmi5 | 0.00044665209996645614 | -0.0016814268007073626 to 0.0020323182230934443 | 0.05619088315955943 | +, +, - |
| ENSANUT2018_E0_A05 / Q1_age10 | 0.02352324900739805 | 0.02192242009839321 to 0.026079262371185005 | 0.05160911075715209 | +, +, + |
| ENSANUT2018_E0_A05 / Q2_bmi5 | 0.07568791696368164 | 0.07131416416151257 to 0.07888279737077089 | 0.00795492196343194 | +, +, + |
| ENSANUT2018_E0_A05 / Q3_bmi5 | 0.016030838108089647 | 0.011684470289204333 to 0.018968969804226743 | 0.04060669715143624 | +, +, + |
| ENSANUT2018_E0_S01 / Q1_age10 | -0.0016641741364342322 | -0.006627480302026135 to 0.002183641817866712 | 0.07679653390098437 | +, -, - |
| ENSANUT2018_E0_S01 / Q2_bmi5 | -0.001735577023325579 | -0.005978818161556417 to 0.001243483809184136 | 0.08537841595043916 | -, -, + |
| ENSANUT2018_E0_S01 / Q3_bmi5 | -0.0017076167779998656 | -0.005748512397496124 to 0.0012753061310607561 | 0.05834515203752576 | -, -, + |
| ENSANUT2018_E1_A01 / Q1_age10 | 0.09778383818841187 | 0.09376162017599898 to 0.10514763695807028 | 0.022651478423861723 | +, +, + |
| ENSANUT2018_E1_A01 / Q2_bmi5 | 0.05645919759096775 | 0.03673004776540839 to 0.06703696504593137 | 0.027183641336145828 | +, +, + |
| ENSANUT2018_E1_A01 / Q3_bmi5 | 0.02715684763163791 | 0.011859076906753897 to 0.03533388257498474 | 0.02948068762788798 | +, +, + |
| ENSANUT2018_E1_A02 / Q1_age10 | 0.0977687165339455 | 0.09266418631928719 to 0.1059396474159851 | 0.022636356769395367 | +, +, + |
| ENSANUT2018_E1_A02 / Q2_bmi5 | 0.06064409382962459 | 0.05506571537809548 to 0.06421519607150049 | 0.022998745097488994 | +, +, + |
| ENSANUT2018_E1_A02 / Q3_bmi5 | 0.032404912978472714 | 0.02777935255152431 to 0.03680415900137915 | 0.024232622281053173 | +, +, + |
| ENSANUT2018_E1_A03 / Q1_age10 | 0.1024516279586996 | 0.09688616425420044 to 0.10878890697921223 | 0.027319268194149458 | +, +, + |
| ENSANUT2018_E1_A03 / Q2_bmi5 | 0.06251504411793557 | 0.049528571336535404 to 0.07243194352410717 | 0.021127794809178008 | +, +, + |
| ENSANUT2018_E1_A03 / Q3_bmi5 | 0.028292080642324274 | 0.01693214621710395 to 0.03484502165989459 | 0.028345454617201615 | +, +, + |
| ENSANUT2018_E1_A04 / Q1_age10 | 0.09904731638424955 | 0.09560783788706564 to 0.1041052952891029 | 0.023914956619699404 | +, +, + |
| ENSANUT2018_E1_A04 / Q2_bmi5 | 0.059385787284558886 | 0.05110217516342224 to 0.06622240766771571 | 0.024257051642554688 | +, +, + |
| ENSANUT2018_E1_A04 / Q3_bmi5 | 0.04209058466452136 | 0.03274972078528111 to 0.05052941821478627 | 0.014546950595004526 | +, +, + |
| ENSANUT2018_E1_A05 / Q1_age10 | 0.10196221493768072 | 0.10020748953717389 to 0.10479053473891108 | 0.026829855173130582 | +, +, + |
| ENSANUT2018_E1_A05 / Q2_bmi5 | 0.06055002762900369 | 0.055702243777564664 to 0.06382020527394845 | 0.023092811298109892 | +, +, + |
| ENSANUT2018_E1_A05 / Q3_bmi5 | 0.02499659222497035 | 0.02042776021222147 to 0.028078219008628388 | 0.031640943034555544 | +, +, + |
| ENSANUT2018_E1_S01 / Q1_age10 | -0.0015477637884946105 | -0.006023234432974034 to 0.0020392276535596 | 0.07668012355304475 | +, -, - |
| ENSANUT2018_E1_S01 / Q2_bmi5 | 0.05744114373983842 | 0.05155187068809058 to 0.06155735052970992 | 0.02620169518727516 | +, +, + |
| ENSANUT2018_E1_S01 / Q3_bmi5 | 0.04869757513774934 | 0.045119777419773154 to 0.05135795352820809 | 0.007939960121776552 | +, +, + |

## Provenance

Frozen release SHA-256: `796fb50db7fc49c0b0195e596182a3550816938f5d8e1d28e859bf267ee78aad`. Result SHA-256: `1fbc32d2f982d31c649d9217e644a34c02b81e08c093380fba8f3aaec9e4c2cb`. Independent audit code SHA-256: `d225b591b6c3d3f6e54ff9b0fc41f9437b6bfdd8f18f367d52a79db85538e8b4`. The companion JSON records source hashes, copies all six contrasts/all 24 summaries, and binds the audit status.

Inputs: `final_evaluation/RESULTS.json`; `independent_audit/RESULTS.json`; `publication/UPTAKE_INVENTORY.json`; frozen case cards and operator metadata; `manuscript/MAIN_STUDY_METHODS_2026-11-03.md`. No source acquisition or patient-level analysis was performed.
