# Published-example longitudinal reconstruction: manuscript addendum

This addendum supplies a completed longitudinal capability example for the v0.6 manuscript. It does not change the earlier CHNS/ENSANUT studies, their exposure status or their frozen outputs. Complete records are in the [HRS result report](../reports/hrs_public_example_2026-11-03/RESULTS.md).

## Suggested Methods text

We evaluated whole-cohort generation on the public HRS recipient-stage example of Filshtein et al. The admitted material comprised published aggregate model exports and original method definitions at a pinned repository version. A fresh scientific Agent received these materials, the requested variables, visit schedule and intended analysis. It selected a sequential conditional model and implemented a generator with parameter-level provenance. An independently implemented comparator reconstructed the published generating law. Each construction delivered three fixed-seed datasets of 11,509 synthetic subjects, with visits at 0, 2, 4 and 6 years (46,036 rows per dataset). No HRS participant records were accessed.

Evaluation used the published longitudinal mixed-model specification, including a two-branch HbA1c spline, age interactions and correlated subject intercepts/slopes. All 16 coefficients and their model-based SEs were retained, together with 27 baseline distribution metrics. All final tables were generated before evaluation. A separate Python computation verified coefficients and SEs conditional on the fitted variance components. Source statistics were available during construction; this example evaluates reconstruction and analysis preservation, rather than unreported-relation discovery or new-population validation.

## Suggested Results text

All three Agent datasets supported the specified longitudinal model. The mean below-threshold HbA1c-by-age coefficient was −0.044635 (three-seed range −0.051059 to −0.038247), compared with the exported source estimate −0.046837. The corrected published-law reconstruction yielded −0.040500 on average. The above-threshold interaction was less stable: Agent estimates averaged 0.026485 versus a source estimate of 0.012867; one Agent dataset produced a model-based interval excluding zero, whereas the source interval included zero. Corrected comparator estimates for this interaction were negative across the three draws and had intervals including zero. These results do not establish an accuracy ranking.

The Agent-generated overall HbA1c mean and SD averaged 5.8725 and 0.9676, respectively, compared with published original values 5.9 and 1.0. However, the subgroup at or above 6.5% had mean 7.1515 and SD 0.5630, approaching the paper's synthetic values 7.2 and 0.6 while differing from its original values 7.7 and 1.4. The example therefore demonstrates useful source-model reconstruction alongside inherited distributional limitations. The six retained comparison fits passed independent conditional-GLS verification.

## Implementation incident and accounting

Nine physical generation attempts were made: the original six-attempt allocation and a separately documented three-attempt comparator recovery. The initial comparator parser crossed model boundaries because of CRLF line endings and silently overwrote seven HbA1c coefficient/SE pairs. Its three outputs were invalid comparator deliveries. The original preparation assessment was overturned; all failures and original freezes remain retained. The repair recovered those exact pairs and locators from the original source, without changing generator code, the other model parameters, the scientific family or the Agent outputs. Independent source-specific verification and malformed-input checks preceded the recovery release. This technical failure is not counted as a weakness of the published method.

## Contribution supported by this example

The new evidence concerns a concrete extension of the data product: a task-driven Agent can turn sufficiently detailed published material into an entire longitudinal cohort containing conditional variables, repeated observations, piecewise associations, interactions and individual effects, suitable for the corresponding analysis workflow. The example broadens the implemented task scope beyond cross-sectional generation and enrichment. It does not introduce a new simulation family: the Agent selected the source's established structure. It also does not establish autonomous literature retrieval, lower human effort, calibrated model uncertainty, superior accuracy or equivalence to unobserved individual measurements.

The manuscript should distinguish three evidence types: external-evidence developmental analysis, summary-assisted consistency, and this public-model reconstruction. They answer different questions and should not be pooled into an undifferentiated success rate. The valid comparison contains six tables from two constructions in one example, not six independent real cohorts. No further tuning of this case is proposed.

## Figures and tables

- [All 16 fixed effects](../reports/hrs_public_example_2026-11-03/figures/all_16_fixed_effects.png): points show all three fixed seeds, diamonds show their means, segments show their ranges, and dashed lines show exported source coefficients. Ranges are not confidence intervals.
- [Two prespecified longitudinal relationships](../reports/hrs_public_example_2026-11-03/figures/focal_longitudinal_relationships.png): all final estimates and model-conditional 95% Wald intervals; source estimates and their reported SEs are displayed separately. Synthetic intervals do not imply added clinical sample information.
- [Complete coefficient table](../reports/hrs_public_example_2026-11-03/summary/fixed_effects_all_seeds.csv) and [complete baseline diagnostic table](../reports/hrs_public_example_2026-11-03/summary/distributions_all_seeds.csv), with every seed retained.
- [Technical correction record](../reports/hrs_public_example_2026-11-03/recovery_v1/INCIDENT_AND_CORRECTION.md) and [independent result review](../reports/hrs_public_example_2026-11-03/FINAL_RESULT_REVIEW.md).

Reference: Filshtein TJ et al. *Proof of concept example for use of simulation to allow data pooling despite privacy restrictions*. Epidemiology. 2021;32:638–647. [Primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC8338788/); [pinned public method](https://github.com/powerepilab/Sim_for_data_pooling/tree/6708e43d5e342fa76d57b31d5a6d0bfcc2979539).
