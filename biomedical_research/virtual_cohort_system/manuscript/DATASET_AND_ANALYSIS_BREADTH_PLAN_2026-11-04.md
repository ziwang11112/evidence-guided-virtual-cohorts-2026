# Dataset and scientific-analysis coverage

4 November 2026. This review responds to the request to broaden the evidence for the final virtual data. It uses existing acquisition, exposure and experiment records, plus three original method papers. The completed units and the proposed extensions below have different statuses.

## What the current manuscript establishes

| Evidence setting | Reference | Generated variables | Scientific use |
|---|---|---|---|
| Main external-evidence study and latest open retrieval | CHNS, 6,631 selected people | Age, sex, BMI, glucose, HbA1c | Three HbA1c regression analyses |
| Main external-evidence study and latest open retrieval | ENSANUT, 6,931 selected people | Age, sex, BMI, glucose, HbA1c | Three HbA1c regression analyses, including additional adjustment |
| Summary-assisted reconstruction | The same CHNS reference | The same five variables | Three regressions and two glucose–HbA1c correlations |
| Longitudinal source-model reconstruction | Published HRS analysis material | Demographics, HbA1c, memory and follow-up structure | Sixteen fixed effects, including two highlighted interactions |

The current participant-reference evidence concentrates on two populations and one main outcome, HbA1c. The HRS case adds longitudinal structure and memory analysis using published coefficients. The current study has substantial repeated construction and numerical checking, but limited breadth of biological outcomes and real longitudinal reference uses.

The latest batch's 366 values comprise 36 primary estimates and 330 diagnostic estimates. CHNS has three primary definitions and 27 diagnostics, ENSANUT three and 28. Each has two constructions and three draws, giving (30 + 31) × 6 values. Most diagnostics are marginal means, SDs and quantiles. This accounting measures execution coverage.

Historical completed work already includes HAALSI glucose, Turkana TC/HDL, NHANES insulin, urate and DXA body fat, and PNS HbA1c. At least six participant-reference families occur in these later records. Earlier projects also contain NAGALA and DIETFITS. Their information conditions and method versions must accompany any use in the paper. The [data inventory](../reports/existing_data_benchmark_2026-11-02/DATA_INVENTORY.md), [evidence ledger](INTEGRATED_EVIDENCE_LEDGER_v07_2026-11-03.md) and [exposure registry](../docs/DATASET_EXPOSURE_REGISTRY.md) establish their roles.

## Selected expansion sequence

The first expansion should add a measured-lipid task under the current Agent workflow. The second should add paired, real-follow-up analysis. This would bring the main coverage to four participant-reference families if both are executed, alongside the HRS source-model case. Four is a practical scope for this project, not a publication rule.

| Order and status | Existing resource | Intended generated data | Proposed scientific questions | Preparation needed |
|---|---|---|---|---|
| 1 — selected for protocol preparation | Turkana, 397 previously evaluated lipid complete cases | Age, sex, BMI, TC and HDL | Age/sex-adjusted HDL–BMI association, adjusted TC–BMI association, and TC–HDL residual dependence after the declared covariates | Qualify the retrieved numerical source operators. The current Greiner packet supports geometric means and proportions, while some slope scales remain unresolved. |
| 2 — selected for protocol preparation | DIETFITS, 609 released participants and 464 previously analysed six-month pairs | A paired baseline/follow-up table for weight, waist, fasting glucose and insulin, with sex and diet arm. TG can enter if source and target measurement checks support it. | Arm-specific weight change, waist change, and the association of adiposity change with insulin-resistance change | Confirm exact visit definitions, paired eligibility and units. Assemble published source statistics. Earlier WLM/STRRIDE packets were calculated from source individual records. |
| Conditional second lipid reference | HAALSI baseline | Age, sex, BMI, TC and HDL | Repeat a fixed lipid analysis in another population | Verify populated lipid fields, valid ranges/censoring, eligibility and source applicability. The 4,394-person glucose sample size cannot supply a lipid sample size. |

The lipid and follow-up tasks would add TC, HDL and insulin, with weight/waist changes and potentially TG. HOMA-IR, if used, is calculated from glucose and insulin in specified units. It is a derived analysis quantity. IDs, visits, transformations, BMI and derived lipid quantities should be identified separately from independently measured biomarkers when reporting dimensionality.

Existing NHANES insulin enrichment supplies another immediately relevant historical example. A separately frozen whole-cohort insulin task is a narrower reserve option if the publication-only longitudinal evidence cannot support the proposed DIETFITS construction. Any such substitution must be recorded before generation and reference comparison. Selection should follow measurement and evidence availability.

Blood pressure and renal indicators remain later possibilities. Their current source/measurement preparation is weaker than the selected lipid task. The [alternate-outcome audit](EXISTING_REFERENCE_FEASIBILITY_v07_2026-11-03.md) records the specific HAALSI, CHNS urate and ENSANUT lipid issues.

## What to evaluate in the delivered data

| Evaluation layer | Measures and interpretation | Application |
|---|---|---|
| Scientific result | Direction and size of the specified adjusted effect, interaction or change estimate, with reference sampling uncertainty | Every case |
| Joint structure needed by the analysis | Residual association, conditional spread, or within-person dependence | Lipid pairing and longitudinal change |
| Distribution needed for the use | SD, quantiles and relevant threshold proportions alongside the location | Retain the existing diagnostics and add only task-relevant checks |
| Stability across constructions and sampling | Show every author and seed separately, with their different meanings | Each new frozen task |
| Data usability | Schema/units, positivity and algebraic identities, paired IDs/visits, missing-value policy, and successful execution of the requested analyses | Every delivered table |

A matching marginal mean alone cannot establish a conditional effect. Direction agreement is useful but should be accompanied by magnitude and the variability needed for the intended analysis. The existing within-CHNS real–real resplits provide context for that sample. Each new reference needs an uncertainty calculation appropriate to its design.

The first new plots should display native-unit scientific estimates and one joint or repeated-measures check per task. A coverage matrix should show which cohort, biomarker group, data structure and information condition each experiment supplies. This allows readers to assess breadth alongside performance without treating seeds as populations or combining incompatible effect units into one score.

## Bounded implementation sequence

1. Complete the Turkana task contract from the existing measurement/eligibility records and public source evidence. Specify final-table analyses before construction. Review the adapter's variable mapping and declared units.
2. Reuse the current Agent procedure for retrieval, source interpretation, model authorship, sampling and inspection. The Agent chooses the scientific law and parameters. Source checks must retain their actual operator and applicability.
3. Start with two fresh constructions and three final draws per construction, using the existing isolated execution approach. Allow one generated-only/source-feedback inspection and record the final model decision. These are proposed resource bounds for the new protocol.
4. After all constructions close, evaluate every frozen final table against the existing developmental reference and independently recompute the planned analyses. Record all attempts and outcomes.
5. Prepare the DIETFITS task using publication-derived evidence and the verified paired-data definitions. Freeze its exact endpoint formulas and information condition before execution.

The selected existing target families have historical exposure. Their new results can extend current-workflow and analysis coverage with that history disclosed. A previously unexposed population would answer an additional transfer question. Target cohort results must stay outside the external-literature generation input in the planned literature-only condition.

No new clinical read, generation, download or model fit was performed in this breadth review. The next executable unit is the lipid protocol and source/operator preparation. Readiness is assessed from measurements and admissible information, not from whether the old result was favorable.

## What the neighboring papers show

- G-Sim evaluates COVID SIR, supply-chain and hospital-bed simulators, including downstream interventions and out-of-distribution settings. These are three simulator environments. Its design illustrates coverage of different simulation and decision problems. [Original paper, Sections 5–6](https://arxiv.org/html/2506.09272#S5).
- LLMSynthor uses mobility, a controlled six-variable commerce example and hierarchical ACS household/person generation, including sixteen policy queries. These examples vary both data structure and downstream questions. [Original paper, Section 4](https://arxiv.org/html/2505.14752v3#S4).
- SynthIPD presents N9741 and six myeloma trials across two detailed examples, with subgroup survival curves, hazard ratios, median/fixed-time survival and restricted mean survival time. Its breadth comes partly from several scientific analyses of a focused data type. [Original paper](https://arxiv.org/html/2509.16466v2).

Our expansion sequence is a design judgment informed by these examples and by our existing resources. The current biological domain remains concentrated in metabolic phenotypes. Broad biomedical applicability would require evidence from additional domains.
