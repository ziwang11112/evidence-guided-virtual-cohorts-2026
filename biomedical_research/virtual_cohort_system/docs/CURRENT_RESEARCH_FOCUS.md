# Current research focus: contribution-led virtual biomedical data generation

Updated 1 November 2026, America/Chicago, following the user's explicit direction: keep experimental purposes clear, concentrate on the paper's contributions and innovation, improve the essential method, and place unresolved peripheral capabilities in limitations. This is the current prospective scope policy. It supersedes broader proposed expansions in earlier planning documents, without changing frozen protocols, historical results, or exposure records.

## The contribution we are trying to deliver

**An Agent turns published biomedical evidence, a target-population description and optional observed measurements into a reusable virtual dataset that can support specified scientific analyses.**

Complete-cohort generation with no individual input remains central. Variable enrichment and missing-cell completion remain within the overall method; this paper does not need to newly validate every regime. The output is data and its generation recipe, with evidence and assumptions documented. A checklist, reliability classifier, simulator benchmark or Agent orchestration framework must not replace that output as the project objective.

Working title: **From Published Evidence to Virtual Cohorts for Scientific Analysis**.

Following the user's subsequent clarification on 1 November, contribution is evaluated as a **biomedical data-generation method that addresses unavailable joint measurements and has demonstrated analytical uses**. A new loss, model family or Agent architecture is not a prerequisite. The value lies in turning available study evidence into useful joint data with an explicit construction and real-reference evaluation. This positive contribution is distinct from claims of firstness, quantitative replacement or comparative algorithmic superiority, which require their own support. The data product stays central; semantic checking is a supporting operation rather than the paper's replacement objective.

## Three contribution slots and their current evidence

| Contribution slot | What the paper should explain and demonstrate | Supported scope and remaining gap |
|---|---|---|
| Evidence-based data generation when individual measurements are unavailable | How a population request and partial published findings become a complete joint generator; preserve the optional-observation setting | Whole-cohort execution and selected analytical feasibility have real-reference evidence. Defining this setting is not itself proof of firstness or algorithmic novelty. |
| Study-conditioned evidence-to-generator construction | How population, measurement, adjustment and uncertainty change the use of a source result; trace scientific structure and parameters to reported values, derivations or assumptions | Evidence records, Agent-authored models and supported deterministic checks exist. General multi-study population replay and reliable autonomous repair are not established. The potential methodological distinction must be grounded in a concrete implemented operation relative to close prior methods. |
| Reusable scientific analysis from one virtual release | Apply several declared analyses to the same frozen data and report supported uses, discrepancies and unresolved assumptions | CHNS provides a whole-cohort example with directional agreement and substantial magnitude/variability discrepancies. The controlled pilot illustrates conditional-evidence translation, with unresolved tail behavior. These do not establish unrestricted fidelity. |

The organizing innovation candidate is **operationalizing heterogeneous published evidence as a scientifically usable joint-data generator under explicit study conditions**. The generic generate/check/revise loop, conditional sampling, provenance logs and multiple Agent roles are not claimed to be new. More components, cases or statistical tests do not establish novelty. A claim of an improved translation mechanism needs an actual distinguishable operation and evidence that it matters; the present record does not settle that claim.

## What “make the core as good as possible” means

1. **Faithful evidence use.** Correct source statistics, units, population conditions and adjustment sets; genuinely derived coefficients distinguished from assumptions. Scientific issues that affect the selected uses take priority over adding features.
2. **A coherent reusable generator.** Agent scientific decisions are real and inspectable; the program or direct-table route produces data usable by ordinary analysis tools. The same release supports the declared uses without endpoint-specific regeneration.
3. **Persuasive analytical evidence.** Evaluate scientific conclusions, relevant effect scales and functional relations, with necessary distribution diagnostics and reference uncertainty. Exact patient-row recovery and universal numerical matching are not required. Agreement of signs alone cannot substantiate a stronger claim of quantitative interchangeability.

One scientific Agent and deterministic tools are sufficient. Multi-Agent superiority, training, a new loss, a conversational front end and superiority to a direct-analysis Agent are not required. Comparison with a capable same-information generator is necessary only if the paper claims an advantage over existing generation methods; it cannot be replaced by comparing different input information and calling the difference algorithmic superiority.

## Completed work: use it without opening more branches

- [CHNS F2](../reports/chns_admission_2026-11-01/f2/CASE_RESULTS.md): two Agent constructions; twelve slots, six unique tables; 6,631 complete-case participants as the measured reference. All three selected association directions reproduce. BMI effect magnitudes are approximately 30–39% of the reference estimate; other effect scales and variability also differ. Both Agents retained their initial models. This is selected analytical feasibility, with no revision gain.
- [Conditional-evidence pilot](../reports/evidence_value_2026-11-01/RESULTS.md): four constructions, twelve artificial tables. Conditional evidence supports the expected target projection under stipulated transport. The primary quantity is algebraically implied by the inputs; compatible tail laws remain unidentified. Use this as a concise mechanism illustration or supplement, not a new research branch or evidence of biological discovery.
- Earlier pilots can support a clearly labelled development appendix or separately justified information regime. Do not pool different method versions or multiply repeated seeds into independent biomedical validations.

All revealed targets remain closed to tuning. No new experiment, target family, literature quota, download, API, training run, HPC job or schedule is launched by this scope update. The existing CHNS automation stays paused.

## Experimental admission: a short decision, not another infrastructure project

Before any proposed new experiment, write five concrete items: **the manuscript claim it tests; the unresolved gap; the minimal discriminating experiment; the decision its result would change; and the fixed stopping rule.** If an item cannot be stated clearly, do not run the experiment. Prefer reusing existing verified results when they already answer the question. This rule needs no new controller, audit subsystem or benchmark.

Current writing checkpoint: [manuscript v0.2](../manuscript/DRAFT_v0_2.md) consolidates the complete results and centers the biomedical method contribution; the [G-Sim/LLMSynthor positioning](../manuscript/POSITIONING_GSIM_LLMSYNTHOR_2026-11-01.md) is complete within its stated scope. Do not repeatedly rewrite the framing as a substitute for progress. Remaining manuscript work is the broader statistical-predecessor context, source bibliography, author/access/ethics declarations and submission-specific reproduction/format preparation. The current results support selected analytical feasibility; stronger quantitative usefulness or comparative improvement remains a separate evidence question. There is no automatic requirement for another cohort or toy experiment before drafting.

Only if an incremental biomedical-validity claim remains central should one focused prospective comparison be designed. It must isolate the proposed mechanism with matched information when claiming a method advantage, and test scientific analyses from the same frozen virtual release on a genuinely fresh reference. A different evidence packet can test information value, but does not alone isolate an algorithmic advantage. Its budget and informative stopping decision must be fixed before execution. Do not repeatedly add cases or components to obtain a positive result; if the promised gain is not demonstrated, simplify the method and narrow the claim.

## What belongs in limitations, and what must change the main claim

| Issue | Treatment |
|---|---|
| Restricted variables, selected populations, sparse extreme observations, uncertain transport, limited regimes or direct-row validation | State the tested scope and limitations. No automatic extension experiment. |
| No calibrated source/model/transport uncertainty | State that limitation and remove calibrated-coverage or confirmatory-inference claims. Simulation seed spread is not a substitute. |
| No feedback-driven improvement, full autonomous retrieval or general source-population replay | Describe the actual implemented workflow and remove unsupported benefit/autonomy claims. No requirement to add these capabilities for the bounded paper. |
| Imperfect recovery of some primary scientific relationships or their magnitudes | Report in main Results and narrow the supported analytical uses. Further repair is justified only if essential to the retained contribution, not because every discrepancy must disappear. |
| Leakage, wrong units/statistic, invalid calculations, or an implementation that contradicts its declared model | Repair and independently check, or withdraw the affected evidence. These cannot be dismissed as ordinary limitations. |
| Unidentified tails, individual true values, arbitrary requested biomarkers, causal effects or cost savings not validated here | Keep outside the paper's supported claims; explain the boundary where relevant. Do not promise them to make the paper sound broader. |

## Manuscript consolidation and completion condition

Prepare a contribution-to-evidence table, one accurate method description, the complete real-case analytical results, the bounded mechanism illustration, and a candid limitations section. Update the working draft's obsolete “real case not yet evaluated” statements by creating a dated revision; preserve the old draft and distinguish the later CHNS implementation from the original core-v0 reference replay.

The next manuscript iteration is complete when each contribution has supporting results and a stated scope, every retained method component serves that contribution, and important failures appear where they alter interpretation. It need not demonstrate every optional capability. Submission strength and venue remain judgments to make from that complete record; a limited result must not be relabelled as an established algorithmic innovation.

This policy keeps the broader data-generation idea intact while concentrating work on the scientific value the paper can actually demonstrate.
