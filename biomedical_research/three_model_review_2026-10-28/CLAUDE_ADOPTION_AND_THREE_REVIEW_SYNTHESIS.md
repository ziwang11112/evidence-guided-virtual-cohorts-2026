# Claude review and synthesis of the three independent model reviews

28 October 2026. This is a research decision record, not a new experimental result. No frozen generator, protocol, evaluation rule or reported result was changed. No new participant analysis was performed for this synthesis.

## 1. Provenance and limits of inspection

The complete Claude response was supplied by the user and preserved in `CLAUDE_REVIEW_USER_SUPPLIED.md` (33,298 bytes; SHA256 `8da64cb08b397f5a8332245ca9c60f70a0ceba793998285dc3634e5d3a68f20f`). It reports reading the brief and all 13 appendix files, inability to access the private repository, and no execution of project code. Its numerical table checks are arithmetic on supplied results, not an independent rerun. Gemini likewise reviewed the supplied packet without full repository access. ChatGPT reports additional targeted repository inspection; none of these provider reviews reran the complete experiments.

Supporting records are `CLAUDE_COMPLETE_CLAIM_CHECKS.md`, `CLAUDE_PRIMARY_SOURCE_CHECKS.md`, `GEMINI_COMPLETE_CLAIM_CHECKS.md`, `GEMINI_ADOPTION_DECISIONS.md`, `REVIEW_CLAIM_CHECKS.md` and `PRIMARY_SOURCE_CHECKS.md`. Three agreeing reviews are a useful cross-check of reasoning, not three independent empirical validations.

## 2. The main research objective remains data generation

**Agent integration of cross-study evidence should produce reusable virtual data for biomedical analyses. We need to determine which analyses remain useful and whether the workflow improves analytical quality or reduces measured manual modeling effort.**

The project retains three uses: whole-cohort synthesis, adding never-measured variables, and completing partially observed data. Entire-column enrichment is a useful first-paper test because its information boundary is clear. It does not make all statistical alternatives impossible, nor does it permanently exclude the other uses.

Ordinary capable Agent generation can be the main method. Extra agents, mandatory gap files and multiple scenarios are optional design choices. The completed record does not demonstrate that the tested additions help consistently. It also does not establish their universal uselessness.

Provisional title: **Evidence-Guided Virtual Cohort Enrichment for Biomedical Analysis**. A second framing, if heterogeneous results are the main finding, is **Which Analyses Survive? Evaluating Agent-Generated Biomedical Variables Across Studies**. Neither title asserts verified novelty or reliable general deployment.

## 3. What Claude adds usefully

### A. An information ladder for diagnosis

Compare a model using general prior knowledge, a literature-grounded Agent, a statistical construction using equivalent evidence, and a donor-data model with richer individual-level information. This can show whether retrieval improves the tested setup and whether richer information closes an important gap.

However, this ladder is not an error decomposition by itself. Donor populations differ in sample size, measurements, covariates, selection and time. If an external donor also misses a target relationship, transport is one possible explanation, not an isolated cause. Separate fair same-information comparisons from richer-information references.

### B. Can the system flag vulnerable analyses before seeing their answers?

This is an attractive extension. For example, an analysis depending on an unsupported BMI tail shape should carry that dependence into its result. Start with transparent evidence/assumption labels and source checks; evaluate whether they predict errors on reserved tasks.

Do not equate ensemble variance with lack of support. A wrong assumption fixed in every model has zero ensemble variance. Shared wrong sources also make independent Agent builds agree. Variance attribution depends on parameterization, correlated parameters and nonlinear interactions. AUROC assesses ranking of failures; it does not establish calibration of a claimed failure probability. A support system should also report the error rate among analyses it accepts and the fraction it accepts, with task-level uncertainty.

### C. A later measurement-value experiment

Compare a literature-informed generator updated with k real measurements against a model using those k measurements alone. At the same held-out analytical performance and error control, estimate the difference in required measurements. Repeat subsampling and allow negative benefit or no crossing of the learning curves.

This would give a concrete use beyond visual plausibility. It is a separate claim to test, not a prerequisite for the first generation pilot. An in-silico difference is not yet a reduction in recruited patients, clinical costs or real assay costs. It is not a universal prior effective sample size.

There is relevant prior art: [AutoElicit, ICML 2025](https://proceedings.mlr.press/v267/capstick25a.html) elicits LLM priors and evaluates label efficiency. Statistical work also explicitly allows harmful prior information to have a negative effective contribution: [Reimherr, Meng and Nicolae](https://arxiv.org/abs/1406.5958). Thus measuring literature value is useful, but not by itself a new concept.

## 4. Internal claims: correct arithmetic, qualified interpretation

Claude's HDL arithmetic checks out against the retained aggregate results:

- Excluding the unresolved sex-by-BMI interaction, all 28 construction–endpoint signs agree with their reference estimates.
- Four of those 28 point estimates lie within the corresponding reference 95% interval.
- None of the four primary adjusted BMI point estimates is inside its reference interval.
- The range over four constructions includes six of eight reference point estimates, missing age and curvature.

These counts quantify descriptive agreement. They do not test equality, establish calibrated coverage or prove that every value outside a reference interval gives an unusable scientific conclusion. Reference estimates have sampling uncertainty; the analyses share participants; the construction range is not a probability interval. Our user-facing utility criterion should concern prespecified interpretation and practically important differences, with numerical diagnostics retained.

The core limitation is supported: each generator fixes its scientific parameters while residual seeds vary. But Claude's phrase “no uncertainty is reported” is too strong. Conditional intervals and across-seed variation are reported; source, structure and transport uncertainty are missing.

The source and code observations about age clamping, assumed tails and marginal-to-conditional bridges are useful. Their exact contributions to target errors have not been isolated. In particular, adjustment-set mismatch is a plausible explanation, not a proven causal diagnosis.

The implementation isolation concern is real. The static checker is not a sandbox, and in-process execution shares a filesystem with reference material. No misuse was found in the representative generators. Future confirmation should place builders where reference files are not available, including through mounted paths and credentials. This is a procedural improvement; it does not retroactively prove leakage or invalidate the audited arithmetic.

## 5. Statistical proposals requiring changes

### Summary likelihoods require a joint evidence model

Claude proposes multiplying Normal densities for reported statistics using a variance of SE squared plus a bridge variance. This is a possible modeling starting point, not a ready-made posterior. Summaries from the same participants, overlapping studies or multiple adjusted models are correlated. Treating them as independent double-counts evidence. Importance weighting additionally needs the target prior and proposal distribution to be specified; a likelihood alone is not a universal particle weight.

Population mismatch, measurement bias and an altered adjustment set do not necessarily act as zero-centered variance inflation. Some change the expected statistic. A large bridge variance cannot identify a missing joint distribution or make incompatible estimands interchangeable. The provenance location of a result—main text versus author response—is a reason to inspect context, not an automatic numerical variance multiplier.

Source-context replay remains useful: simulate under a source's conditions, reapply its analysis, and compare its report. If needed source covariate distributions are absent, use an explicit approximation or sensitivity analysis. A fitted source statistic is a consistency check. Holding out a source adds evidence only if shared data and publication overlap are considered and the omission was not chosen after results were seen.

### Ensembles need defined meanings

An outer shared evidence/model draw followed by individual residual draws is sensible. Independent parameter Normals and equal weights over plausible structures do not automatically constitute a calibrated posterior. Distinguish probability models supported by an inferential argument from unweighted or judgment-weighted sensitivity scenarios.

Shared model uncertainty can remain as inner Monte Carlo size grows, but only in estimand directions affected by that uncertainty. Increasing synthetic rows cannot remedy a common structural error. Holding generated n equal to real target n is a useful reporting convention, not a general solution to inferential validity.

Claude's instruction never to report within-dataset standard errors is too broad. Those quantities can be conditional diagnostics or components of a correctly derived combining rule; they should not be presented as all-source uncertainty. The target sample provides information about its observed covariate distribution and marginal targets, even though observing X alone does not identify an arbitrary missing Y|X law.

### Interval scores and calibration answer different questions

[Bracher et al.](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008618) describes WIS as a proper score for probabilistic interval forecasts, balancing interval width and misses. We must first specify what is forecast: a finite target-table analysis, a population parameter, or a future estimator. Scoring a parameter interval against one noisy survey estimate does not automatically establish population-parameter coverage.

WIS is useful alongside calibration, not proof of calibration. An 80% interval covering 60% of selected correlated endpoints can be an exploratory development screen, but not a successful 80% calibration result. Known-truth repeated worlds or an appropriately defined sampling experiment are needed for a calibration claim. Cases, study families, constructions and residual draws are different replication levels.

Failure defined by whether p crosses .05 is also unstable near the threshold and depends on sample size. Prefer prespecified scientific interpretation categories and effect tolerances where justified, with the original interval and effect estimates visible. The review's ratios, AUROC threshold and cohort counts are suggested design choices, not methodological or editorial standards.

## 6. Prior work and novelty: narrower, still testable

Generic literature-to-code, LLM simulation construction, summary-driven cohort generation, model ensembles and prior elicitation all have direct precedents. The no-target-outcome regime is an important boundary to define, not enough on its own for a first-ever claim.

Claude's ModelSMC status is outdated: it has [official ICML 2026 proceedings](https://proceedings.mlr.press/v306/wahl26a.html), not only an arXiv version. Its statistical SynDI lead is relevant, but the published method has observed internal outcomes. It is not a plug-in required baseline when the target outcome column is entirely hidden; any adaptation must disclose how the information regime changes. See the separate primary-source checks for these and other predecessors.

A paper needs a demonstrated contribution, but not necessarily all of Claude's proposed contributions simultaneously. Possibilities include useful analytical performance under a clear evidence regime, a tested improvement in source-statistic translation, reliable support assessment, or comparable analytical utility with measured reduction in expert work. These are candidate contributions, not results already established.

“A generator cannot discover biology missing from the literature” is too absolute. Combining evidence can generate new, testable predictions. Synthetic analyses are not independent biological confirmation; confirmation must come from suitable real measurements, intervention or independent data.

## 7. Agreement and differences among the three reviews

| Topic | Shared or strongest advice | Decision |
|---|---|---|
| Ordinary Agent | All allow it to be the main method if specified and empirically useful | Keep; no mandatory multi-Agent contribution |
| First paper | All favor absent-column enrichment | Use as first evaluation focus; retain wider project scope |
| Existing results | Feasibility with important failures; no established superiority | Preserve positive and negative findings unchanged |
| Evidence translation | Source population, measurement and analysis matter | First mechanism to test separately |
| Uncertainty | Scientific parameters fixed across seeds | Separate shared uncertainty from residual variation; validate inference independently |
| No-retrieval | Claude makes a win a central continuation condition | Use as retrieval ablation; a tie does not invalidate generation or prove contamination |
| Statistical comparison | All request a competent comparator | Same evidence for fair comparisons; richer donors labeled separately |
| Workflow value | ChatGPT explicitly allows equal accuracy plus measured manual-time savings | Keep as a valid potential contribution |
| Support labels | Claude gives the most developed evaluation proposal | Start simple; ranking, calibration and acceptance risk are distinct |
| Measurement savings | Claude makes it central; others treat prospective work as optional | Later use-case test, not required for the first pilot |
| Pooling formula | Gemini prescribes Rubin plus an effective-size cap | Do not adopt as a universal guarantee |
| Journal ambitions | All condition high-impact prospects on much stronger evidence | No promised venue; task counts are not journal requirements |

## 8. Minimal next milestone

1. **Make source-statistic checking executable on exposed development cases.** The Agent must represent the evidence's population, units, adjustment set and computation. Let source checks drive its revision; do not fit known target HDL or insulin answers.
2. **Test the mechanism with separated components.** Compare ordinary Agent, ordinary Agent plus source checks, and a capable statistical generator using equivalent evidence. Use controlled known-truth examples to verify category-mean translation without importing a real hidden answer. Add uncertainty as a separately interpretable test rather than an inseparable bundle.
3. **Confirm in fresh eligible public cases.** Audit access, variables, measurements and overlap before selection. Lock target outcomes and analyses. Include reserved relations and at least one distribution-sensitive task, while preserving the scientific analysis workflow the data are intended to support. Record independent constructions, human corrections, compute cost and failures.
4. **Use diagnostic additions selectively.** A no-retrieval ablation helps assess retrieval. A richer donor helps assess what more information can buy. Neither substitutes for the main generation utility evaluation, nor should either be the sole project-wide stop rule.

Proceed to a larger study if a repeatable improvement or measured workflow benefit appears on reserved analyses without unwarranted confidence. If gains only reproduce supplied summaries, narrow the claim to that demonstrated capability. If generated data repeatedly give unsupported, definite new relationships, repair the representation or restrict its supported analyses before scaling. If several fresh tests show no useful analytical or workflow value, reconsider the direction.

No 16–24 task campaign, model training, HPC job or new wet-lab work is triggered by this review. The next authorized execution plan should specify a small discriminating pilot. Public-data candidates and assay budgets remain subject to eligibility and feasibility checks.
