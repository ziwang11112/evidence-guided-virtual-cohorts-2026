# Independent critical review  
**28 October 2026**

## 1. Recommendation, scope and central question

**Continue the project, with entire-column enrichment as the first paper’s central task and the capable ordinary Agent as the main method.** The present record establishes a functioning, auditable workflow and limited analytical feasibility. It does not yet establish reliable prediction of unsupplied relationships, calibrated uncertainty, or an advantage over an evidence-matched statistical generator. The negative gap-policy pilot does not invalidate the broader approach.

I read REVIEW_BRIEF.txt[REVIEW_BRIEF.txt](REVIEW_BRIEF.txt) and IMPLEMENTATION_APPENDIX.txt[IMPLEMENTATION_APPENDIX.txt](IMPLEMENTATION_APPENDIX.txt) in full, including all 13 implementation excerpts. **The private repository was accessible.** At the [specified snapshot](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/commit/51d19b6a8fab07f774d0bd6032a2bb9a379595d8), I additionally checked `README.md`, `CURRENT_RESEARCH_SCOPE.md`, the HDL `RESULTS.md`, `review/postrun/AUDIT.md`, and `docs/REPRODUCTION.md`. This was targeted source inspection, not an executable end-to-end audit: I did not inspect participant records or rerun the reported analyses. No repository changes were made.

The most defensible research question is:

> **When target outcomes are unavailable, can a reproducible Agent translate heterogeneous external evidence into enrichment models that support useful, prespecified target-population analyses, and accurately characterize which conclusions remain assumption-dependent?**

Two plausible titles are:

1. **Evidence-Guided Enrichment of Biomedical Cohorts: Validating Analyses Beyond Supplied Relationships** — my recommendation.
2. **From Published Evidence to Virtual Cohorts: A Reproducible Agent Workflow for Biomedical Analysis**

The appropriate first-paper type is an **empirical methods paper with a substantial evaluation component**. A benchmark/resource paper becomes plausible if reproducible tasks and comparisons are the strongest contribution. The supplied results do not support a biomedical discovery paper.

The ordinary Agent can be the method. Its contribution must be a specified, repeatable procedure with demonstrated analytical or workflow value beyond case-by-case coding assistance. Mandatory gap maps, multiple agents, and scenario enumeration are separate interventions whose benefits remain unproved.

## 2. What the completed work establishes

The following are **reported findings**, supported by the supplied record; they are not independently rerun results.

| Completed work | Defensible conclusion | Remaining limitation |
|---|---|---|
| Retrospective completion | The implementation preserved selected analyses and observed cells. | Missing-only also retained 18/18 evidence states. The 16/18 discrepancy advantage over that MICE implementation is confounded by specifications and retrospective exposure. |
| Stage 1 scenarios | The tested scenario policy did not consistently improve reserved analyses. Some scenarios produced unwarranted confidence. | Three exposed development cases cannot establish general effectiveness or failure of evidence-guided synthesis. An unresolved reference interval is not a true null. |
| Insulin enrichment | External literature supported an executable generator for a completely hidden column. | The adjusted ratio was 1.230 versus reference 1.346; curvature and sex-slope differences were missed. One construction and no statistical comparator establish feasibility only. |
| HDL comparison | Four constructions preserved several broad associations; retrieval could change executable modeling decisions. | Three revisions were numerical no-ops; Ordinary1’s revision had mixed effects. Age and curvature remained problematic, and no workflow consistently won. |

The reported HDL audit—164 fits and 328 endpoints—supports numerical consistency and provenance. It cannot validate transport assumptions. Forty scheduled files, including 25 distinct contents, still represent four constructions in one cohort. These distinctions are correctly retained in the [post-run audit](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/51d19b6a8fab07f774d0bd6032a2bb9a379595d8/biomedical_research/evidence_gap_loop_2026-10-28/review/postrun/AUDIT.md).

### Implementation findings and their implications

Paths here refer to `biomedical_research/evidence_gap_loop_2026-10-28/` and the supplied appendix.

**The controller is a substantive strength.** `loop_control.py` verifies registered evidence artifacts, parameter references, commitments, observed-cell preservation, and seed reproducibility. `custodian/evaluate.py` validates the release before reading outcomes. These controls support reproducibility, while the documents appropriately acknowledge procedural rather than OS-enforced isolation.

**The main weaknesses are statistical bridges, not an obvious lognormal arithmetic error.** Both supplied generators correctly convert arithmetic moments to lognormal parameters and apply the mean correction. However:

- `runs/ordinary_1/final/generator.py` treats sex-by-BMI category means as values at assumed BMI anchors, interpolates them, and adds adjusted age contrasts. Category averages do not identify pointwise conditional means.
- Its `source_se * np.sqrt(source_n)` conversion estimates broad-cell SD under stated assumptions. Using that as conditional spread can retain variability that the explicit predictor effects subsequently add again.
- Ordinary1’s exponential tail reproduces the external slope only locally at the anchor. Gap2’s asymptotes of 30/38 mg/dL and decay of 0.04 are explicitly assumed.
- Both supplied models impose a small common age pattern with endpoint clamping. Their near-flat target age associations therefore have a structural explanation.
- Both specifications fix scientific parameters across draws. Additional seeds explore residual randomness, not uncertainty about evidence, model structure, measurement or transport.

**A further evaluation limitation follows directly from the code.** All eight HDL endpoints are coefficient contrasts from raw-HDL weighted linear regressions in `custodian/evaluate.py::matrices()`. With predictors and weights fixed, expected coefficients depend on the generator’s conditional mean. Matched-mean gamma and lognormal generators therefore have identical expected coefficients. These endpoints barely test whether distributional assumptions support threshold, tail or richer joint analyses.

My strongest reviewer objection is consequently:

> **The method currently turns limited aggregate constraints into a much more specific conditional distribution, without showing that its unsupported detail is predictively useful or that uncertainty protects users when it is wrong.**

This is joined by insufficient independent replication, absent evidence-matched statistical baselines, and substantial overlap with existing methods.

## 3. Closest verified precedents and novelty boundary

This was a focused primary-source search, not a systematic novelty review. It does not justify a “first” claim.

| Verified work and publication status | Relevance to this project |
|---|---|
| [Kramer et al., *Leveraging generative AI to enhance Synthea model development*](https://doi.org/10.1093/jamiaopen/ooaf123), **JAMIA Open, 2026**, published 6 January | A particularly close predecessor: authoritative medical sources → LLM extraction → executable Synthea model → validation and revision. Evidence-to-code plus review is already established. Your stronger potential distinction is quantitative cross-study translation evaluated on reserved target analyses. [PubMed](https://pubmed.ncbi.nlm.nih.gov/41502536/) |
| [G-Sim](https://proceedings.mlr.press/v267/holt25b.html), **ICML 2025** | LLM simulator construction combined with empirical parameter calibration, including simulation-based inference. Neither executable simulation nor “LLM structure plus statistical calibration” is sufficient novelty. [proceedings.mlr.press](https://proceedings.mlr.press/v267/holt25b.html) |
| [DALL-M: Context-aware clinical data augmentation with large language models](https://doi.org/10.1016/j.compbiomed.2025.110022), **Computers in Biology and Medicine, 2025** | Direct precedent for adding clinical features using patient context and external knowledge. Its predictive-model evaluation differs from validating absent-variable biomedical estimands. [ScienceDirect](https://doi.org/10.1016/j.compbiomed.2025.110022) |
| [SynthCraft](https://doi.org/10.1371/journal.pdig.0001290), **PLOS Digital Health, 9 March 2026** | An auditable Agent workflow for generation, evaluation and augmentation. It uses observed datasets and evaluates regression relationships, so analytical validation and provenance alone are also insufficient novelty. [PLOS Digital Health](https://journals.plos.org/digitalhealth/article?id=10.1371%2Fjournal.pdig.0001290\) |
| [SPADA: *Doubling Your Data in Minutes…*](https://aclanthology.org/2025.emnlp-main.525/), **EMNLP 2025** | LLM-selected dependency graphs followed by numerical conditional sampling. Its fitted-data regime differs from an entirely absent target column; it requires adaptation for a fair comparison here. [ACL Anthology](https://aclanthology.org/2025.emnlp-main.525/) |
| [ModelSMC: *A Probabilistic Framework for LLM-Based Model Discovery*](https://proceedings.mlr.press/v306/wahl26a.html), **ICML 2026** | The briefing’s lead is now a published conference paper. It treats alternative LLM-generated models probabilistically, reinforcing why arbitrary scenario enumeration is not calibrated uncertainty. It does not make SMC necessary here. [proceedings.mlr.press](https://proceedings.mlr.press/v306/wahl26a.html) |
| [Synthea](https://doi.org/10.1093/jamia/ocx079), **JAMIA 2018**, and [SASC](https://doi.org/10.1016/j.patter.2022.100453), **Patterns 2022** | Whole-patient simulation predates current Agents; SASC specifically generates cohorts from grouped summary statistics and correlations. These are closer conceptual precedents than target-trained GANs alone. [Oxford Academic](https://academic.oup.com/jamia/article/25/3/230/4098271) |

Three statistical traditions are essential. [Indirect inference](https://doi.org/10.1002/jae.3950080507), published in 1993, already fits simulators through auxiliary statistics. [ML-NMR](https://doi.org/10.1111/rssa.12579), published in 2020, integrates individual-level models over study-specific covariate distributions to connect aggregate evidence and target populations. Your proposed source-statistic operators belong in this lineage. [stat.cmu.edu](https://www.stat.cmu.edu/~cshalizi/462/readings/Indirect%20Inference%20%28Gourieroux%2C%20Monfort%20and%20Renault%29.pdf)

[Statistical matching/data fusion](https://www.ajs.or.at/index.php/ajs/article/view/vol33%2C%20no1%262%20-%209/380) directly addresses relationships between variables never jointly observed. Common predictors generally do not identify their residual association. [ajs.or.at](https://www.ajs.or.at/index.php/ajs/article/view/vol33%2C%20no1%262%20-%209/380)

Finally, the [NCHS synthetic linked-data programme](https://www.cdc.gov/nchs/linked-data/synthetic/index.html) already provides verification of synthetic analyses against originals. This supports the use case, not novelty or validity of evidence-only enrichment. [CDC](https://www.cdc.gov/nchs/linked-data/synthetic/index.html)

**The defensible candidate contribution is the combination of an absent-outcome information regime, reliable quantitative evidence translation, and prospective analytical validation. That contribution remains to be demonstrated.**

## 4. Two highest-value method improvements

### Improvement 1: Constrain generators using the statistics sources actually report

Keep one capable ordinary Agent. Add a small set of source-statistic templates for group means, SDs, regression coefficients and measurement transformations.

For each important estimate, specify source selection, measurement conditions, covariate distribution, adjustment set, and the analysis applied to simulated source data. Fit or check the generator against that statistic before transporting it to the target. Conventional summary likelihoods, constrained estimation or simulated moments suffice; no new loss is required.

For example, a reported BMI-bin mean should constrain an **average over that bin’s predictor distribution**, not automatically become a value at its midpoint. A coefficient adjusted for waist–hip ratio and lifestyle cannot silently become an age effect in a model omitting those variables.

When source context is unavailable, retain an explicitly approximate constraint or sensitivity parameter. Simulating an assumed source population and matching it is not empirical source validation. Account for cohort overlap and correlated summaries rather than treating every extracted number as independent evidence.

**Discriminating test:** Compare ordinary construction and source-operator construction on the same packet, using omitted source statistics and fresh target analyses. Better fit only to fitted constraints is insufficient.

### Improvement 2: Separate shared uncertainty from individual variability

Use an outer layer for uncertain source parameters, measurement shifts and defensible structural alternatives, with individual residual draws inside each outer realization. Study-level uncertainty must be shared across rows; independently adding it to each person’s noise allows it to average away incorrectly.

Where probability distributions are defensible, propagate them. Where they are not, report sensitivity ranges and analysis-specific robustness. Do not label hand-picked, equally weighted scenarios a posterior distribution.

Missing-data and synthetic-data combining rules depend on what was observed, estimated and synthesized. Rubin’s rules should not be applied automatically across all three project regimes; this distinction is established in [Reiter and Raghunathan’s 2007 analysis](https://doi.org/10.1198/016214507000000932). [scholars.duke.edu](https://scholars.duke.edu/publication/742204)

**Discriminating test:** Assess coverage and informativeness in known-truth experiments. Increasing synthetic rows should reduce Monte Carlo error while leaving uncertainty from unchanged empirical evidence substantially intact.

These changes address demonstrated failure mechanisms. A universal operator compiler or multi-agent architecture would be premature.

## 5. Prioritized experiment matrix

Effort estimates below are **researcher-days**, assuming the existing infrastructure and part-time statistical review; access delays are excluded. They are planning estimates.

| Priority/task and allowed information | Comparison | Held-out analysis | Replication, success/failure criterion and effort |
|---|---|---|---|
| **1. Fresh entire-column enrichment.** Hide HbA1c or triglycerides; provide predictors, population/assay metadata and an identical screened evidence packet. | Ordinary Agent; expert-authored summary-constrained regression/spline generator; same Agent without retrieval. Add the operator-aware version only if ready before freezing. | Adjusted BMI contrast, BMI-35 versus BMI-25 slope contrast, sex modification, and threshold prevalence. | Two tasks, three independent builds per Agent condition, five inner draws. Seek evidence-related improvement on unsupplied endpoint classes and competitiveness with the statistical baseline. Failure: only supplied relationships improve. **6–10 days.** |
| **2. Uncertainty and nonidentification stress test.** Known-truth worlds with sparse, conflicting or overlapping source summaries; include different truths compatible with identical packets. | Fixed parameters versus uncertainty propagation; competent statistical uncertainty baseline. | Coverage, interval score, width, confident errors; repeat with 1×/10×/100× synthetic size. | 200 independent source/target worlds per setting using frozen inference code. Proposed screen: 90% interval coverage approximately 85–95%, with useful width; failure if precision grows solely with synthetic size. This tests inference, not 200 Agent builds. **3–5 days.** |
| **3. Retrieval and cross-study transfer.** New study populations; only target predictors and metadata. | Frozen ordinary workflow and statistical generator; crossed curated versus Agent-retrieved evidence packets to separate retrieval from modeling. | Target curvature, subgroup effects and prevalence; source-held-out checks. | Expand toward 6–8 tasks across ≥3 study families, with builds nested within tasks. Success: useful transport predictions and uncertainty that reflects failures; failure: systematic unacknowledged transport bias. **10–20 days after access.** |
| **4. Joint new-variable enrichment.** Hide two biomarkers; initially supply separate conditional evidence, then add an independent joint constraint. | Ordinary Agent/joint copula generator versus conditional independence. | Residual biomarker association and a prespecified multivariable analysis. | Replicate across cohort–variable pairs, not seeds. Success: joint evidence improves the reserved relationship; absent that evidence, the method exposes nonidentification. **5–8 days.** |
| **5. Missing-cell extension.** Reveal some target outcomes; impose 20%/50% MCAR and MAR masks, plus an MNAR sensitivity condition. | Ordinary Agent, properly configured MICE–PMM and Bayesian joint modeling with identical predictors. | Affected adjusted/nonlinear analyses and uncertainty, excluding unchanged-column controls. | Several cohorts, ten masks nested within each. Success: acceptable bias/coverage or measured effort advantage; failure: apparent gain depends on weaker comparator specifications. **5–8 days.** |
| **6. Whole-cohort extension.** Target definition and summaries only. | Ordinary Agent versus summary-constrained parametric/copula or maximum-entropy generation. | Reserved joint contrasts and distribution-dependent analyses. | Three fresh cohorts with repeated constructions. Success requires useful implications beyond supplied moments; marginal matching alone fails. **5–10 days.** |

For all rows, prespecify analytical tolerances with a biomedical collaborator. Report continuous error and interval scores alongside them. The proposed coverage screen and study counts are **operational choices, not clinical standards or journal requirements**. Reference estimates also have sampling uncertainty.

Target-trained CTGAN, diffusion models or MICE cannot be the sole opponents when the entire target outcome is absent. Source-microdata transfer is a valuable **separate information regime**, provided every comparator receives equivalent access.

A no-generation Agent belongs in an ancillary utility experiment: give it the same evidence and ask it to solve a finite planning or analytical task directly. Compare decision quality, analyst effort and reuse across follow-up questions. It is not a mandatory generic generation baseline. The no-retrieval ablation also retains pretrained knowledge and should not be called “no knowledge.”

### Concrete public-data candidates

The official [NHANES 2021–2023 catalogue](https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component=Laboratory&Cycle=2021-2023) lists HbA1c and triglycerides. They are feasible candidate tasks if a custodian confirms they remain unexposed to this project. Multiple biomarkers and cycles still belong to one study family. [Continuous NHANES](https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component=Laboratory\&Cycle=2021-2023\)

A distinct-population candidate is the open [Turkana cardiometabolic Dryad deposit](https://doi.org/10.5061/dryad.2z34tmpjk), which documents BMI, age, sex, HDL, triglycerides and glucose. It could provide a demanding transport test. I verified the deposit metadata, not participant-level completeness, assay compatibility or suitability; those remain selection gates. [datadryad.org](https://datadryad.org/dataset/doi%3A10.5061/dryad.2z34tmpjk)

## 6. What would justify analytical claims beyond reproducing inputs?

Separate three levels in the results:

1. **Evidence consistency:** reproduce a supplied statistic under its source conditions.
2. **Reserved prediction:** predict an unsupplied target functional, including its practically relevant magnitude or shape.
3. **Assumption-dominated exploration:** generate a result whose essential dependence is unsupported.

The second level can support a methods contribution without identifying the complete joint distribution. The third requires explicit qualification and empirical testing where possible.

For example, adding \(Y\) from \(p(Y\mid X)\) to records containing \(X,Z\), without conditioning on \(Z\), imposes \(Y\perp Z\mid X\). A resulting marginal \(Y\)–\(Z\) association can arise through shared predictors. It is not evidence that residual dependence was recovered. Test this using a jointly measured reference and deliberately contrasting plausible residual-dependence assumptions.

A convincing paper should show useful prediction across at least two unsupplied endpoint classes, performance competitive with strong statistical construction, and uncertainty that distinguishes supported from weakly supported analyses. Equal accuracy with substantially lower **measured** expert effort could instead support an automation contribution.

Present four main figures: the evidence-to-model process; all fresh analytical results; uncertainty calibration and confident failures; and transport or practical utility. Keep the negative scenario/gap findings visible.

## 7. Leakage, circularity and artificial precision

The existing freezing discipline is valuable. Strengthen it for the next study:

- Freeze eligibility, sources, analyses and tolerances before outcome inspection. Insulin and HDL are now development cases.
- Remove outcome-derived ratios, calculated variables and identifiers that could reveal hidden outcomes. Track overlap between publications and cohorts.
- Separate source consistency from reserved prediction. A withheld coefficient already determined by supplied constraints is not an independent discovery.
- Freeze every build before release; retain failures and avoid selecting the best construction after evaluation.
- Record available model identifiers, prompts, actual tool use and effort. Equal caps do not establish equal compute.
- Use filesystem separation for the custodian where practicable. Public availability and fresh contexts cannot prove absence of pretrained exposure.

Synthetic-only regression intervals must remain labeled as conditional on the generator. Neither retaining the original row count nor using survey covariance repairs omitted model uncertainty. Never treat appended synthetic rows as additional observed participants.

## 8. Public-data-only and optional measurement routes

**Public-data-only route:** fresh masked-column tasks, distinct-study transport, known-truth uncertainty tests and a concrete reuse task can support a methods paper. New wet-lab work is not inherently required.

**Optional paired-assay study:** measuring matched stored specimens on two assays could estimate a measurement bridge and its uncertainty. It validates assay translation, not the entire joint distribution or population transport.

**Optional prospective subset:** freeze the generator, then measure a target subset sampled across informative predictor strata. Choose sample size from the precision required for one or two prespecified group-level estimands. Keep calibration and final evaluation subsets separate. This provides prospective target validation; a small subset is unlikely to validate subtle interactions or extreme tails.

**Optional measurement-selection experiment:** compare Agent-selected measurements with random or expert selection at the same actual budget. Evaluate improvement in a prespecified decision or reduction in uncertainty. Recruitment or measurement savings require such observed comparisons; synthetic row counts cannot establish them.

HPC should follow a demonstrated computational bottleneck, not define the project.

## 9. Realistic venue positioning

**First methods target: Journal of Biomedical Informatics.** Its stated emphasis includes generalizable methods, comparison with existing approaches and substantive methodological lessons. A reproducible evidence-translation method with fresh analytical validation fits that remit. The present pilot alone is insufficient. [Official scope](https://amia.org/news-publications/journals/journal-biomedical-informatics). [AMIA - American Medical Informatics Association](https://amia.org/news-publications/journals/journal-biomedical-informatics)

**More attainable methodological alternative: BMC Medical Research Methodology.** A rigorous study of when evidence-guided enrichment succeeds, fails or requires additional information could fit even without universal superiority. Its scope explicitly includes methodological evaluation and emphasizes scientific validity. [Official scope](https://link.springer.com/journal/12874/aims-and-scope). [Springer Nature Link](https://bmcmedresmethodol.biomedcentral.com/submission-guidelines/aims-and-scope)

**Selective alternative: PLOS Computational Biology.** This would require substantial methodological or biological insight and broader usefulness. Its official policy explicitly states that experimental validation is not required; reproducibility and convincing validation still matter. [Journal criteria](https://journals.plos.org/ploscompbiol/s/journal-information). [journals.plos.org](https://journals.plos.org/ploscompbiol/s/journal-information)

**Nature Communications: conditional stretch target.** Its criteria concern significant advances and conceptual or methodological importance. I would consider an attempt only after demonstrating a clear capability beyond predecessors: useful reserved analyses across independent populations, strong comparisons, informative uncertainty, and a compelling scientific use case. These are my assessment criteria, not invented journal minimums. More cases of familiar sign preservation or additional Agent machinery would not suffice. [Scope](https://www.nature.com/ncomms/aims) and [editorial criteria](https://www.nature.com/ncomms/submit/editorial-process). [Nature Communications](https://www.nature.com/ncomms/aims)

## 10. Two-week milestone and ranked decision

**The highest-information immediate experiment is the fresh, identical-evidence enrichment comparison in row 1.** It separates evidence usefulness, Agent translation and statistical modeling quality.

For **28 October–10 November**:

- **Days 1–3:** Select two new tasks using metadata; lock evidence packets, analyses, tolerances, comparator specifications and the reveal gate.
- **Days 4–7:** Build the competent statistical comparator; run three ordinary-Agent constructions per task and the retrieval ablation. Use exposed cases for implementation development.
- **Days 8–10:** Complete source checks and a small uncertainty stress test; freeze all candidates and record actual effort.
- **Days 11–14:** Reveal every reserved endpoint and issue a claim-by-claim report, including all failures.

**Go to expansion** if evidence helps on at least two unsupplied analytical classes, performance is competitive with statistical construction, and uncertainty avoids systematic false confidence. This is a pilot decision, not a superiority test.

**Conditional go** if accuracy is similar but the Agent measurably reduces expert work while preserving reproducibility. Pursue an automation-focused methods paper.

**No-go for the broad analytical-validity claim** if benefits remain confined to supplied relationships, results depend on favorable-build selection, or unsupported relationships remain confidently wrong. A systematic limitations or benchmark paper may still be worthwhile.

My ranking is: **first, run the discriminating comparison; second, improve source-statistic translation and uncertainty; third, test independent transport; only then extend all three use cases.** Stop expanding the unchanged gap policy, counting additional draws as evidence, repeatedly refining exposed HDL/insulin cases as confirmation, and scaling compute without a scientific reason.

What would change my assessment is a reproducible pattern of useful reserved predictions, competitive statistical performance, and uncertainty that remains informative while acknowledging failure. The supplied project has enough implementation discipline to test that proposition. It has not yet supplied the evidence to claim it.