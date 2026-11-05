# Cross-task evidence-use capability: manuscript insertion package

This is an additive, reviewed-results insertion for the working manuscript. It does not modify the archived v0.13.1 draft or its historical comparison arms. The new study is a developmental capability experiment, not a randomized workflow ablation or new independent clinical confirmation.

## Proposed results text

We evaluated the common evidence-use workflow on two biomedical requests without providing participant-level inputs: age- and BMI-related HbA1c analyses and BMI-related total/HDL cholesterol analyses. Three fresh Agent contexts independently constructed a generator for each request using external published evidence and target-context metadata. Scientific source interpretation, model/specification consistency and finite moments were reviewed before isolated execution. Each constructor could retain its initial model or revise once after a scheduled trial and source/generated diagnostics. All six retained their initial construction. Three fixed final seeds per model yielded 18 distinct 3,000-row tables, with no failed final executions or replacement draws.

All 54 primary point estimates matched the direction of the corresponding existing-sample estimate, but quantitative fidelity differed by analysis and construction. HbA1c age effects averaged 0.09954–0.10091 percentage points per decade versus 0.07513 in the reference. BMI effects after age/sex adjustment averaged 0.04892–0.06030 versus 0.08364 per five BMI units. With glucose additionally adjusted, H03 averaged 0.05098 versus 0.05664, whereas H01/H02 averaged 0.03047/0.01936. H03 nevertheless had lower HbA1c marginal and conditional dispersion than the reference, showing that agreement on a focal effect did not imply broader distributional agreement.

For the lipid request, HDL BMI effects averaged -2.1865 to -1.9868 mg/dL per five BMI units versus -4.6230 in the reference; TC effects averaged 10.0151–11.2609 versus 5.6831. The reference TC sensitivity interval crossed zero, so positive point-direction agreement does not establish replication of a definite positive population effect. Adjusted residual TC–HDL correlations averaged 0.10828–0.14134 versus 0.51207. L02's TC SD was close to the reference (43.6778 versus 42.8466 mg/dL), while its residual association remained weak. No construction uniformly dominated the others across focal analyses, joint dependence and dispersion.

All 513 prespecified generated estimates/diagnostics were independently reconstructed; the maximum numerical difference was 5.33e-14. All matched reference mappings and comparison arithmetic were verified. The reference cohorts had been exposed earlier in development, and the seeded outputs are not independent clinical replications. The 132 source-check entries remained unavailable under the implemented semantic rules because essential definitions were incomplete, weighted, or unsupported. Thus, this experiment demonstrates reviewed evidence-to-generator construction and analysis-specific descriptive utility, not numerical source-replay or feedback-driven improvement.

## Contribution wording

The Agent chooses how heterogeneous published evidence enters a task-specific generative law, while the common harness records those uses and evaluates the final data with scientific analyses. The demonstrated contribution is a reusable workflow with inspectable numerical evidence use and a cross-task empirical assessment. The laws use established statistical families; neither a new universal sampler nor universal superiority over statistical generation is claimed. Whole-cohort generation remains part of the general method, alongside enrichment and completion. These two requests test the former directly.

## Figures and captions

**New cross-task figure:** [primary_analyses.pdf](paper_figures_v14_2026-11-05/fig6-cross-task.pdf). All constructors and three final draws appear in native units. Circles denote individual tables, open diamonds their mean, and dark diamonds the existing sample estimates. Grey bands are empirical cluster-resampling stability bands for HbA1c and HC3 assumption-conditional sensitivity intervals for lipid slopes; no interval is available for residual correlation. These bands are neither equivalence margins nor pass/fail thresholds. The TC slope reference band crosses zero.

**Companion dispersion figure:** [dispersion.pdf](paper_figures_v14_2026-11-05/fig7-dispersion.pdf). Marginal HbA1c, TC and HDL dispersion and HbA1c full-model residual dispersion are shown for every construction. Seed ranges describe Monte Carlo variation conditional on the frozen model, not uncertainty about evidence, structure or transport. Joint and marginal fidelity must be assessed separately.

## Editorial placement and next decision

Add this after the current open-retrieval capability results, with its own task/input/version label. Keep prior E0/E1 comparisons and reconstruction settings distinct. Put the full 18 author–endpoint summaries and source/unavailable-check inventory in supplementary tables, retaining all outcomes. Do not showcase H03 without its dispersion trade-off or interpret 54/54 point directions as an overall accuracy rate.

The current batch is closed. Its empirical claim is simplified to documented, assumption-dependent analytical use. Continue manuscript integration; further quantitative transfer claims require a separate prospective protocol, not retuning these exposed references. Full records and independent reviews: [RESULTS.md](../reports/evidence_use_cross_task_2026-11-05/RESULTS.md).
