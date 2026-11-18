# Manuscript integration supplement to frozen v0.29

This is new, evidence-bound text for the next revision, not a replacement of the frozen v0.29 file. It contains no new simulation or target refit. The complete experiment is [reported here](RESULTS.md).

## Story and placement

Retain the application: research requests and published evidence become executable joint generators and analyzable virtual cohorts. Present three linked capabilities: autonomous evidence-to-data construction; measured usefulness for specified scientific analyses; inspectable source, transformation and modeling assumptions. Avoid claiming that a workflow must outperform ordinary Agent to make the application useful. However, the specialized workflow's incremental benefit remains unestablished and should be stated directly.

Place the new six-panel primary-analysis figure immediately after the end-to-end construction example. Retain older evidence-information contrasts as complementary experiments, not pooled replicates. Put delivery/resource details, full constructor diagnostics, exposure notes and mathematical-tail review in the supplement, with the tail defect also acknowledged in the main Results. Use a compact provenance case to show an actual source-to-operator-to-code decision. Feedback remains an available action rather than the visual or argumentative center.

## Methods insertion: repeated construction from research requests

We evaluated repeated autonomous construction on two previously used biomedical contexts: Brazilian adult blood pressure and Turkana-context adult lipids. Each context was assigned to an ordinary Agent and an evidence-organized scientific workflow, with three fresh constructor sessions per policy. Both policies used the same GPT model configuration, research request, retrieval and execution tools, and resource ceilings. Neither received a prepared scientific source packet, target individual records or target analysis estimates. The ordinary Agent could search, inspect evidence, design and execute programs, check outputs and revise; it was not restricted to one-shot generation. The workflow supplied reusable organizational procedures rather than case-specific scientific values.

The twelve selected generators were frozen before final evaluation. Each produced three cohorts of 3,000 fictional records using prescribed seeds. Six primary analyses comprised age- and sex-adjusted BMI associations with SBP, DBP, TC and HDL, and covariate-adjusted residual correlations within each outcome pair. All delivered, failed and unavailable slots were retained. Constructor-level profiles, nested seed estimates, reference uncertainty, marginal dispersion and physiological consistency were reported separately. No composite quality score or post hoc equivalence threshold was introduced. One blood-pressure generator sampled shared parameters per seed; its repeat variation therefore included encoded scenario uncertainty in addition to participant sampling.

Model requests, tool actions, retrieved source versions, candidate programs, terminal decisions and token costs were recorded. Clinical references had previously been exposed at project level, so this is a developmental repeatability study. One search preview exposed a target-family ideal-cardiovascular-health prevalence result; it was recorded and retained. An independent numerical reviewer recomputed saved-table analyses, verified execution and accounting, and checked reported comparisons against the pinned references. A separate source/code reviewer examined provenance without reading the current clinical comparison.

## Results insertion: reliable delivery, analysis-specific usefulness

All twelve sessions selected a generator and all 36 final cohorts were delivered, totaling 108,000 fictional records. The sessions used 331 model calls at an estimated token cost of USD3.985, with no unknown-usage calls. There were 127 provider queries and 54 episode-level full-text downloads, corresponding to 36 distinct PMC identifiers. Every selected program was the first submitted candidate; the batch provides no evidence of a gain from scientific revision. Independent recomputation of all final tables agreed to a maximum numerical difference of 9.06 × 10^−14.

Blood-pressure results varied across constructors. BMI–SBP coefficients ranged from 3.293 to 5.597 mmHg per five BMI units across the six constructor means, compared with the existing sample estimate of 3.524; BMI–DBP ranged from 2.424 to 3.704 against 2.260. Residual correlations ranged from 0.611 to 0.783 against 0.717. The workflow was descriptively closer on residual dependence and marginal dispersion, while ordinary Agent was closer on the two primary BMI coefficients when comparing mean absolute differences across constructor means. These comparisons do not identify a task-general policy advantage.

The lipid task exposed a more consistent limitation. All six constructor means underestimated the reference residual correlation (0.146–0.423 versus 0.512) and HDL dispersion (SD 11.38–13.18 versus 20.18 mg/dL). BMI–HDL associations ranged from −2.312 to −0.012 mg/dL per five BMI units, compared with −4.623. The workflow was descriptively closer on the TC association, while ordinary Agent was closer on HDL association and residual dependence. Reference estimates have sampling uncertainty; in particular, the saved TC coefficient interval includes zero. These differences are not proof of known population bias. One workflow-generated record had HDL above TC; it was retained.

## Results insertion: traceable decisions reveal distinct failure mechanisms

Source/code inspection showed that Agents made substantive scientific decisions. One workflow derived blood-pressure covariance from SBP, DBP and pulse-pressure variances before subtracting an assumed covariate contribution. Lipid constructors converted standardized BMI effects using inferred or assumed BMI scales, and one transferred covariance components from a longitudinal joint model to a single-visit generator. Both third-repeat lipid authors independently used positive component models to enforce TC greater than HDL. These choices were inspectable, but their source populations, adjustment sets and statistical operators did not automatically identify the requested target analyses.

Uniform mathematical review distinguished missing information from generator defects. One ordinary lipid generator combined unbounded lognormal BMI with a positively exponential TC conditional mean, yielding an infinite raw TC mean under its continuous ideal law. Another ordinary generator used numerical caps and therefore retained finite actual moments; its uncapped counterfactual must not be conflated with the implemented law. Both produced finite successful tables. This demonstrates that executable output and empirical checks alone do not certify a scientifically coherent population model. All frozen outputs were retained; no post-evaluation repair was performed.

## Discussion insertion: what explainability means here

The implemented contribution is scientific inspectability: a reviewer can trace an analysis through selected literature, statistical definitions, transformations, adopted parameters and generator code, and distinguish reported evidence from derivations and assumptions. This does not require access to private model reasoning. It is not yet evidence that reviewers are faster, that provenance labels predict error, or that a documented assumption transports correctly. The new comparison supports autonomous construction in both Agent policies and demonstrates the usefulness of auditing analytical dependencies; it does not establish overall superiority of the organized workflow.

The repeated lipid shortfall motivates better joint evidence and explicit sensitivity to unidentified dependence, but it does not support a universal shrinkage law: blood-pressure dependence sometimes exceeded the sample reference. Likewise, the mathematical tail defect requires law-level checks rather than additional target-fitting. These mechanisms should remain distinct. Subsequent evaluation should test a small, versioned improvement with the same scientific freedom, while preserving complete unfavorable results and separating reused developmental references from new confirmation.

## Figure captions and supplementary material

Use [primary_analyses.pdf](figures/primary_analyses.pdf) for the complete six-panel scientific profile and [delivery_resources.pdf](figures/delivery_resources.pdf) for construction availability and cost. Full captions are in [FIGURE_CAPTIONS.md](FIGURE_CAPTIONS.md). Use [AGGREGATE_TABLES.md](AGGREGATE_TABLES.md) for complete constructor-level and diagnostic tables and [SCIENTIFIC_PROVENANCE_AUDIT.md](review/SCIENTIFIC_PROVENANCE_AUDIT.md) for the bounded 36-analysis mapping and exact mathematical-tail statement.

The old capacity-round traceability dossiers are a separate prepared reviewer resource. They contain curated postclosure interpretation, not an automated evaluation result. No human usability statistics may be added until actual responses and adjudication exist.

## Required correction to the next manuscript version

In the diagnostic table at frozen v0.29 line 878, change the reference DBP SD from **10.757 to 11.094**. This corrects a manuscript transcription error only. The pinned reference is 11.09413727799307; underlying capacity-round and repeatability evaluations were already correct. Cite [REFERENCE_VALUE_RECONCILIATION.json](review/REFERENCE_VALUE_RECONCILIATION.json) in the revision log and preserve the old manuscript receipt.

## Claims to retain and claims awaiting evidence

| Claim | Current support |
|---|---|
| Agent can autonomously retrieve and author a full-cohort generator from a research request | Demonstrated for all twelve sessions in these two contexts |
| Generated data can support specified scientific analyses | Analysis-specific developmental evidence; complete profiles and uncertainty required |
| Scientific choices are traceable to sources, derivations and assumptions | Source/code audit demonstrated on twelve laws; audit coverage is bounded |
| Workflow improves quality over ordinary Agent | Not established; descriptive results are mixed |
| Scientific feedback improves outputs | Not demonstrated in this batch; all v001 retained |
| Provenance improves review efficiency or predicts correctness | Not tested; review packets are preparation only |
| More models or more virtual rows establish broad generalization | Not supported; constructors, seeds, clinical contexts and model configurations remain separate units |

Keep the overall paper title descriptive. Do not replace it with a claim that Agents universally fail to transport evidence or universally outperform conventional construction. The new results sharpen the contribution and its boundary without erasing useful application evidence from earlier experiments.
