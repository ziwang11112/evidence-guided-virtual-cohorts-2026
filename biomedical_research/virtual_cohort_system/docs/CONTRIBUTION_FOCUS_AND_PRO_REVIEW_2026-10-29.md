# Contribution focus and PRO review brief

Prepared 29 October 2026, local workspace time, after M10 (completed 30 October UTC). This is a research decision document, not a preregistration, a new experiment, or an external model review. No new target outcomes were inspected for this document. The review prompt below has not been sent to PRO in this turn.

## Decision in one paragraph

Keep evidence-guided biomedical data generation as the project. Concentrate the next stage on one question: **can study-specific external evidence be translated into a target-population generator whose frozen output supports several subsequent scientific analyses?** Entirely unmeasured-variable enrichment is the clearest first setting. The most informative next mechanism to investigate is how additional compatible joint evidence changes the generator and its downstream analytical usefulness. Evidence coverage and limitations should accompany the generated data; they should not replace the project with a standalone quality classifier. An ordinary capable Agent is an acceptable implementation. A claim of superiority over another Agent is optional and requires its own evidence.

Working title: **Evidence-Guided Virtual Variable Enrichment for Biomedical Analysis**. This is a scope label, not a claim of established novelty.

## 1. What the project delivers

Input: observed target covariates, a description of an entirely unmeasured biomarker, and external published evidence with population, measurement, transformation, adjustment and timing information.

Operation: an Agent interprets compatible evidence, records unsupported assumptions, constructs an executable stochastic generator, and checks its implications under source-study conditions. Any scientific revision must use permitted evidence rather than reserved target answers.

Output: enriched virtual tables, a reusable generation recipe, evidence-to-assumption records, and a description of which analyses are supported or assumption-dependent. The latter descriptions are provisional unless validated prospectively.

Use: exploratory regression, subgroup and response-shape analysis, and conditional study planning when the target variable was not measured. A generated individual value is a possible value under the evidence and assumptions, not a recovered laboratory result. Synthetic analyses are not independent observations proving the relationships used to construct them.

Whole-cohort synthesis and missing-cell completion remain extensions. M10 does not establish them anew.

## 2. What we have actually learned

The authoritative local record is [M10 results](../MILESTONE_10_RESULTS.md). The private review repository is [evidence-guided-virtual-cohorts-2026](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026), archived at commit `d33d0cbad4c199fe5b450688fe8050d72afd9861`. A reviewer must explicitly state whether that private repository was accessible. Its URL alone is not an inspection packet.

M10 used two public-data targets: 1,961 NHANES 2015–2016 participants with fasting insulin hidden, and 7,979 PNS laboratory-cohort participants with HbA1c hidden. Two independent Agent constructions per case each produced three residual draws, for four scientific constructions and twelve tables. These are not twelve independent cohort replications.

| Reserved analysis | Real estimate | Construction A median | Construction B median | Interpretation |
|---|---:|---:|---:|---|
| Insulin: adjusted age / 10 years | −0.0117 | −0.0088 | +0.0017 | Reference 95% CI includes zero; do not label one point-sign reversal a biological contradiction |
| Insulin: adjusted BMI / 5 kg/m² | +0.2959 | +0.2379 | +0.2517 | Positive direction in all six draws; magnitudes attenuated |
| Insulin: quadratic BMI contrast | −0.0517 | −0.0206 | −0.0391 | Negative direction in all six draws; assumed functional forms contribute |
| Insulin: female-minus-male BMI slope | −0.1193 | −0.0081 | −0.0051 | Strong attenuation; not successful interaction recovery |
| HbA1c: adjusted age / 10 years | +0.1470 | +0.1589 | +0.1563 | Positive direction in all six draws |
| HbA1c: adjusted BMI / 5 kg/m² | +0.1610 | +0.0906 | +0.1043 | Positive direction in all six draws; magnitudes attenuated |
| HbA1c: quadratic BMI contrast | +0.0409 | −0.0060 | +0.0116 | A wrong in 3/3 draws; B positive in 2/3, hence unstable |
| HbA1c: female-minus-male BMI slope | +0.0219 | +0.0121 | +0.0194 | Each construction changes sign across draws |

Insulin outcomes use log insulin; HbA1c uses percentage points. Medians are across three dependent residual draws. No clinical equivalence margin was prespecified. NHANES uses survey-domain reference uncertainty; the PNS package lacks PSU/stratum fields, so PNS has provided-weight participant estimates and unweighted sensitivity, not manufactured survey confidence intervals. PNS baseline covariates and later laboratory measures have a timing difference.

The useful observation is **within-table variation in analytical usefulness**: some main relationships survive while a nonlinear or subgroup relationship fails. This is a concrete motivation for a method investigation, not itself proof of a new scientific phenomenon.

Other implementation facts that must remain visible:

- Evidence packets were curated; this was not autonomous evidence retrieval.
- Source checks used approximated source covariates, not source-study individual records.
- One insulin construction used Taiwan and MACAD information; both HbA1c constructions principally used one compatible SHIP-Trend source cohort. Comprehensive cross-study synthesis was not established.
- All four scientific generators remained unchanged after their initial construction. Source-only retention and schema repair are not evidence that scientific revision improved generation.
- No target outcome was supplied for generator selection. All constructions were frozen and retained before reference evaluation.
- Residual seeds measure conditional sampling variation, not source, model or transport uncertainty. Agreement between generators can still reflect a shared wrong assumption.
- Exact model-backend and token-cost accounting were unavailable. Do not invent them or claim measured cost savings.

## 3. Contribution hierarchy

| Level | Candidate statement | Present status | Evidence needed |
|---|---|---|---|
| Application | External evidence can enable useful analysis of virtual, entirely unmeasured target variables | Partially supported in two cases | More independent tasks and prespecified analytical interpretation, including failures |
| Main method candidate | Preserving study conditions while translating joint evidence improves a reusable target generator | Plausible, not demonstrated as an incremental mechanism | Trace evidence to a changed scientific decision; demonstrate benefit on an unprovided target analysis; separate extra information from a better translation method |
| Supporting contribution | The method reports which analyses depend on unsupported assumptions | Records exist; prospective reliability not established | Pre-release declarations evaluated against later analyses; shared-model bias and weak/null effects tested |
| Research asset | Reproducible cases connect evidence, frozen generators and downstream scientific analyses | An audited pilot package exists | Broader independent tasks and reusable evaluation documentation if a resource paper is pursued |

Do not claim a novel loss, latent model, superior multi-Agent architecture, automatic mechanism discovery, calibrated reliability classifier, full causal identification or replacement of patient measurement from these results.

The preferred paper spine is **data-generation method + downstream scientific utility + transparent boundaries**. The main method candidate earns its place only if its operation and benefit can be distinguished from existing evidence synthesis and simulator construction.

## 4. Closest-work constraints on novelty

These are overlap checks, not an exhaustive novelty search.

| Primary source | Established overlap relevant to our positioning | What still needs investigation here |
|---|---|---|
| [G-Sim, ICML 2025](https://proceedings.mlr.press/v267/holt25b.html) | LLM proposes/refines simulator structure with empirical parameter calibration | The benefit of translating heterogeneous published study statistics to an entirely unmeasured target variable cannot be assumed from a different workflow name |
| [SynthCraft, PLOS Digital Health 2026](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0001290) | Agent orchestration of biomedical synthesis, tool-based evaluation, feedback and reproducible workflow; demonstrated using real source datasets | Our missing-target-variable and external-publication information conditions are a candidate distinction, not evidence of firstness |
| [STEAM, NeurIPS 2025](https://proceedings.nips.cc/paper_files/paper/2025/hash/2ba023061bca4e2d3cbe9ceaeef37e43-Abstract-Conference.html) | Synthesis and evaluation organized around downstream medical causal inference | Preserving scientific estimates is already a research objective; our present results concern descriptive associations, not causal effects |

These primary pages were checked for this decision; that is not a full reproduction or exhaustive method inspection. Prior local reviews also identify indirect inference, simulated method of moments, ML-NMR, AMSIPD, SynDI and SASC as important statistical precedents. Review their original methods and information requirements before choosing an actual comparator or asserting novelty. Some require internal individual outcomes and are not directly usable when the target outcome is completely absent. An adaptation must be made explicit rather than silently weakening a comparator.

Read the previous [three-review synthesis](../../three_model_review_2026-10-28/CLAUDE_ADOPTION_AND_THREE_REVIEW_SYNTHESIS.md) and [primary-source checks](../../three_model_review_2026-10-28/CLAUDE_PRIMARY_SOURCE_CHECKS.md) as a starting point. Those reviews predate M10. Agreement among three reviewers is not three empirical validations, and the previous Claude/Gemini reviews did not have full private-repository access.

## 5. One next experiment, before expansion

### Question

Does a compatible piece of cross-study joint evidence change the generator in a way that improves an unprovided target analysis while preserving an already useful basic relationship?

This is a mechanism screen. It tests the value and use of evidence; by itself it does not prove that our evidence-translation algorithm is new or better than existing methods.

### Before any generation

1. Audit one fresh public-data task against all previous project use. M10 outcomes are now development observations and cannot be relabeled untouched confirmation data.
2. Obtain a genuinely relevant external joint statistic with a traceable population, measurement, transformation, adjustment set and uncertainty. Exclude target-derived evidence and duplicated cohorts. If no such evidence exists, do not manufacture it; change the candidate task or record that the test is infeasible.
3. Freeze one primary downstream joint analysis and one basic relationship as a preservation check. Choose a scientifically interpretable success criterion before reference release. Direction is central; effect scale and shape are supporting checks against trivial or misleading sign matches. Weak or inconclusive reference effects must be reportable as inconclusive.
4. Fix intended use families, construction budget, source-check rules and reference analysis code. Exact reserved answers and target outcomes remain unavailable to builders.

### Minimal construction conditions

- A: the compatible basic evidence packet.
- B: the same packet plus the eligible joint evidence.

Use the same capable Agent, target covariates and construction budget. Two independent constructions per condition, each with three fixed residual seeds, are an economical diagnostic screen, not a statistically powered cohort-level superiority study. Keep every construction. Source-only selection must not use any hidden target result.

For each construction, record the chain **source statement → scientific interpretation → generator change → source implication → expected scope of use**. Explicitly retain no-change decisions and unresolved assumptions. Do not ask the Agent to reproduce a target coefficient direction.

Evaluate both conditions once against the sealed target. Compare the primary scientific analysis, the preservation check and all prespecified secondary analyses. Record whether improvements were caused by a scientific structural change, a scale change, or merely a different residual draw.

### Decision after the screen

- If B changes the relevant modeling decision and improves the unprovided analysis without losing the preservation check, continue to a second independent task. This supports a targeted evidence-use effect.
- If source fit improves but target analysis does not, record a transport or identifiability failure; do not claim the feedback loop solved the problem.
- If both conditions behave alike, investigate whether the extra evidence was redundant, incompatible or unused. Do not hand-tune the generator against the revealed target.
- If the primary claim becomes improved handling of study context, the following experiment must hold evidence constant and compare that handling with a credible simpler translation or an applicable existing method. A richer evidence packet alone cannot establish method superiority.
- If focused tests do not reveal a meaningful contribution, retain a transparent feasibility/resource direction or stop that method claim. Do not escalate to a large benchmark merely to obtain a favorable result.

No HPC is needed for this screening design. The unresolved work is evidence interpretation and experiment design, not large-scale generator computation.

## 6. What to send PRO

Send this document plus the full M10 report, not only a private GitHub link. For a code review also supply the frozen specifications and the relevant generator/evaluator files from the curated package. Do not include participant-level data or credentials. Ask the reviewer to identify exactly which materials were accessible; no repository access means no code-inspection claim.

Suggested prompt:

> Act as a critical biomedical methods and statistical synthesis reviewer. We want to decide the contribution of an evidence-guided virtual-data paper before expanding experiments. Read the attached contribution brief and full M10 report, including failures and access limitations. Our primary product is generated biomedical data, especially enrichment of an entirely unmeasured variable. A capable ordinary Agent is a legitimate implementation; we do not require a multi-Agent superiority claim. We care about downstream scientific conclusions, with effect scale and shape as checks, rather than making marginal-distribution similarity the sole objective.
>
> First state which supplied files and repository contents you actually accessed. Distinguish verified findings, source-based interpretations and your proposals. Please inspect the relevant primary methods of the strongest statistical and LLM-based predecessors, not only their abstracts; give precise citations and state inaccessible sources. Do not call the work novel simply because several existing components are combined.
>
> Deliver the following:
>
> 1. Choose one primary paper contribution and at most one supporting contribution. Explain the scientific use, the concrete input/operation/output, and why it matters. If the evidence supports only an application or resource paper, say so.
> 2. Provide a nearest-work comparison covering information available to the method, target-variable availability, treatment of study context, generator construction and downstream validation. Identify what, if anything, remains substantively different.
> 3. Explain what the M10 positive and negative results support. Do not count residual draws as independent replications, treat no-op retention as scientific revision, or label a weak real reference effect a biological contradiction.
> 4. Critique the proposed evidence-addition screen. Specify one minimal experiment that could change your assessment, its alternative explanation, a fair control if needed, its success criterion and its stop criterion. Separate benefit from extra information from benefit of a new method. Avoid a long undifferentiated experiment wishlist.
> 5. Explain when reusable generated rows provide practical scientific utility beyond reporting isolated source-derived coefficients, and what would demonstrate that utility. This is a use-case question, not a mandatory ordinary-Agent leaderboard.
> 6. Identify which implementation changes are essential, optional or unjustified. Keep the framework general; do not prescribe a manually fixed BMI/age relationship after inspecting target results.
> 7. Propose one title and a one-paragraph contribution statement with calibrated claims. Discuss plausible paper categories and journal fit conditionally on named results; do not predict acceptance or promise Nature Communications from the current pilot.
>
> End with a decision: proceed with the specific core above, revise to a clearly defined different core within virtual-data generation, pursue a transparent application/resource paper, or stop. Explain what evidence would reverse your decision.

## 7. Immediate work order

1. Review the contribution brief with PRO using the updated positive and negative evidence.
2. Translate the useful review into one chosen contribution, one mechanism experiment and an explicit stop rule. Keep a decision record; model agreement is advice, not validation.
3. Audit candidate joint evidence and task freshness before any new outcome release.
4. Run the small screen only after the above is concrete. Expand independent cases and draft the paper around supported claims afterward.

The existing [scientific analysis utility plan](SCIENTIFIC_ANALYSIS_UTILITY_PLAN.md) remains the broader plan. This document narrows the next decision; it does not retrospectively amend frozen protocols or change historical results.
