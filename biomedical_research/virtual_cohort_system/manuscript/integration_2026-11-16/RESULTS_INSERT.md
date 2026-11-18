# Proposed core manuscript insert

This is an integration draft for the next manuscript, not an alteration of frozen v0.31 or an additional experimental result. Numbers below come from the closed experimental reports named in the evidence map. The lipid follow-up closed at source admission without new generation; its limitations are recorded separately.

## Contribution and scientific use

We study whether a scientific Agent can convert a biomedical research request and distributed published evidence into virtual records that support familiar downstream analyses. The data product may be a complete virtual cohort without individual-level inputs, an additional unmeasured variable, or completed missing measurements. Our current evidence emphasizes complete-cohort construction and the scientific uses that its joint model supports. The Agent selects scientific structures and parameters and authors executable generation code; a shared harness records evidence and assumptions, isolates execution, freezes artifacts, and applies prespecified analyses. Source-admission decisions in the experiments reported here also include manual original-text checking.

The key distinction is between producing plausible rows and producing a joint distribution useful for a particular analysis. A cohort can reproduce individual-variable summaries while leaving a regression, interaction or residual relationship largely determined by an unreported assumption. We therefore evaluate the same generated records with multiple scientific analyses and distinguish directly reported, derived and assumed modeling quantities. These records make scientific choices inspectable; they are not calibrated probability-of-correctness labels.

### Virtual data in a recognizable biomedical analysis

The lifestyle application illustrates the intended use: real and virtual records enter the same Methods-guided analysis, while the analytical specification is retained. For example, the urban-minus-pastoralist BMI contrast is 1.882 kg/m² in the existing real-data reference and 1.700–2.251 across six generated draws. Published group findings were available to the Agent, so this example demonstrates source-informed analytical reproduction rather than independent transport. All nine primary contrasts, including weaker lipid magnitudes and an HDL interaction exception, must accompany this illustration. Our implementation follows the paper's reported methods; it is not presented as unchanged software supplied by the original authors.

### Complementary evidence can identify analyses that separate summaries cannot

We next separated evidence-composition capability from clinical transport with two artificial tasks. Twenty-four fresh constructions received neither, one, or both of two complementary statistical records. The full-information condition identified an adjusted correlation of 0.21875 and, in a repeated-measurement task, a change-score correlation of −0.6. Generated constructor means were 0.2211–0.2230 and −0.6013 to −0.5991, respectively. All 90 identified primary and secondary estimates met the numerical tolerances frozen before construction.

This experiment demonstrates that the Agent can combine complementary information into a working joint generator. It does not establish validity for a real patient population. Conditions lacking identifying information were not counted as failures simply for differing from one possible completion. The 72 generated tables were repeated draws within 24 constructions, not independent scientific replications. Independent numerical recomputation agreed to a maximum absolute difference of 1.17 × 10⁻¹⁵ across 216 checked estimates.

### Finding joint evidence improved a specific biomedical analysis

We then returned to the existing PNS blood-pressure case, selected because paired dependence after age, sex and BMI adjustment was already an explicit evidence gap. An API-based research Agent searched for missing joint or conditional information and inspected original methods and tables. It found two partial sources: a same-study correlation matrix permitting adjustment for age and BMI in Burkina Faso, and joint multilevel blood-pressure components in a Ghanaian study. Neither identified the target operator exactly. A third source was withheld because its reporting did not clearly distinguish raw and residual correlation. Source admission and the algebraic derivation were manually checked before generation.

Three fresh constructions used the original external packet and three used that packet plus the qualified joint evidence. The economic GPT model, requested analyses, output format and execution environment were shared. Every constructor independently chose its scientific structure and parameters. All six programs closed before three prespecified draws of 3,000 virtual people per program; no target measurements or target feedback were supplied. The existing PNS sample reference was used after all outputs closed.

| Analysis | Real-sample reference | Original evidence, mean | Added joint evidence, mean | Mean absolute reference difference, original → added |
|---|---:|---:|---:|---:|
| SBP–DBP residual correlation | 0.7172 | 0.5376 | 0.7046 | 0.17962 → 0.01277 |
| BMI–SBP, mmHg per 5 kg/m² | 3.5240 | 3.8280 | 4.0001 | 0.31944 → 0.47613 |
| BMI–DBP, mmHg per 5 kg/m² | 2.2599 | 3.0951 | 2.9795 | 0.83516 → 0.71955 |
| SBP SD, mmHg | 18.1916 | 18.1816 | 18.8729 | 0.32525 → 0.71631 |
| DBP SD, mmHg | 11.0941 | 10.5107 | 11.1757 | 0.58344 → 0.36284 |

Seeds were first averaged within constructor, with constructors weighted equally. Absolute differences were computed before averaging. The displayed means and their distances from the reference therefore need not equal the mean absolute differences.

For paired residual dependence, the reference discrepancy decreased descriptively by 92.89%; every augmented constructor was closer than every original-packet constructor. The augmented Agents chose working residual correlations of 0.70, 0.72 and 0.70 and explicitly labeled their target choices as assumptions. The root supplied neither those values nor a required direction. The original constructors chose 0.55, 0.50 and 0.55. Thus the result is consistent with qualified joint evidence changing the Agents' scientific choices in a useful way. It does not turn those choices into identified transport estimates.

The benefit was specific. BMI–DBP and DBP spread became closer, whereas BMI–SBP and SBP spread became less close. The positive BMI associations were retained. These trade-offs preclude describing the experiment as comprehensive population recovery or a uniform increase in generation quality. Because additional evidence could change both model structure and parameters, the comparison does not isolate a single numerical mechanism. A same-source marginal-versus-joint control would isolate the evidence increment more specifically. The subsequent lipid source-admission attempt did not complete a usable packet and did not run that comparison; it supplies no replication result.

All 18 final tables executed successfully. They had distinct output hashes, no nonpositive BMI or blood-pressure values, and no SBP below DBP. Code inspection supported finite relevant moments for the six chosen laws. Independent QR-based analysis reproduced all 108 scientific and diagnostic values, with maximum absolute difference 5.23 × 10⁻¹³. Search and construction totaled USD1.0560 at the recorded tariff; this excludes human source checking, local compute and wider project costs. No feedback revisions occurred in this experiment.

## Interpretation for the paper

Taken together, these results support a focused contribution: an inspectable workflow for building biomedical virtual data, an explicit test of statistical evidence composition, and a real-case example in which filling a joint-evidence gap improved a useful downstream analysis. The data product and its scientific use remain the mainline. More rows, more review calls or more elaborate orchestration are not assumed to add information by themselves.

PNS and the other historical references were already exposed to the project. Keeping their values out of fresh author contexts preserves the local information boundary but does not create a new independent cohort. Real-data reference estimates also have sampling uncertainty and differ in measurement and population context. We report reference discrepancies alongside those qualifications, without treating every deviation as known population bias or disregarding large mismatches because the reference is uncertain.

The next manuscript should distinguish this bounded contribution from stronger claims: general workflow superiority, guaranteed correctness of unreported relationships, calibrated transport uncertainty, clinical replacement of measurements, and fully automatic source admission are not established. Existing negative, failed and unchanged outputs remain part of the empirical record.

## Figure placement

Use the existing scientific-use example first, followed by the controlled-composition figure and the three-panel PNS figure. In the PNS figure, retain both BMI analyses beside the residual-dependence improvement; show every constructor and the nested draws. A reference line denotes the real-sample estimate. Within-constructor seed ranges are Monte Carlo ranges, not confidence intervals or independent-replication uncertainty. Any additional lipid panel must be based on the complete closed comparison, not a selected favorable endpoint.
