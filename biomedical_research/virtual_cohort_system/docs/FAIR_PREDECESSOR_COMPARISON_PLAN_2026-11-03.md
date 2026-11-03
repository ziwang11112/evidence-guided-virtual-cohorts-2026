# Fair comparison with summary-based biomedical synthesis

Prepared 3 November 2026. This is a design and interpretation note, not a new experiment or an amendment of the frozen study. It uses manuscript text, specifications, source records, code read as text, and retained aggregate results. No participant or generated rows were read; no generator, fitter or evaluator was imported or executed. No frozen artifact was edited.

**Recommendation:** the smallest informative next comparison is a conventional, explicitly adapted sequential statistical construction using the **same existing CHNS rich-summary packet** as the historical reference-assisted Agents, evaluated against their retained aggregate results. It asks whether the documented calibration consistency needs Agent model authorship or is also attainable by a prescribed statistical procedure. This is an optional, separate development comparison, not required to finish the frozen main paper. Execution would be new scientific work even though the data and summaries already exist; this note does not execute or authorize it. A direct SynthIPD experiment is not suitable for the present cross-sectional cases.

## 1. What is already implemented

The current statistical reference is accurately named **a prescribed source-wise Gaussian-copula moment-completion construction**. It is not the original Filshtein method and must not be relabelled as its replication.

Inspection of `work/main_study_freeze_2026-11-03/comparator/SPEC.md`, `build_spec.py`, `moment_reference.py`, `generator.py`, and the retained S01 model specifications establishes:

- Positive marginal families are fitted to admitted individual means/SDs or quantiles. Native IFCC HbA1c is transformed affinely; selected-source glucose support is represented by a truncated distribution. Age and independent binary sex have explicit approximations.
- Adjusted coefficients are evaluated as the appropriate component of a covariance-based population projection, with each original adjustment set. Separate BMI and glucose projections are not copied into one joint outcome regression. Pearson and law-specific continuous Spearman operators are distinct.
- A local constrained optimizer completes unspecified latent correlations by minimizing negative log determinant. It uses separate source contexts, a fixed starting rule and a bounded solve; it does not certify a global optimum. E0 is independent within source components, not necessarily independent after mixing components.
- CHNS transports an assumed equal-probability Jansen/Bao/MIND mixture with the requested age support. E1 constrains both Jansen projections, Bao Pearson and MIND Spearman. The MIND rank operation is a continuous approximation, not reproduction of its original mean-filling/tie process.
- ENSANUT transports Jansen biomarkers into the requested eight equal age/sex cells. Its E1 construction constrains both Jansen projections but leaves the Pani age coefficient and eight means contextual because the source age law, individual dispersion and survey-weighting completion are not bound.
- Generation is numerical sampling from the frozen law, without individual construction records, target fitting, post-generation moment forcing or redraw repair. Source-estimate, structure and transport uncertainty are not propagated.

This is a substantive conventional comparator, not a marginal-only straw man. Its restrictive family, donor rule, independent sex and incomplete Pani uptake nevertheless prevent calling it the strongest possible statistical method. Five independent Agent laws versus one prescribed law per case/arm is a descriptive comparison, not equal model-search replication. The frozen E1 statistical law is closer than every corresponding Agent for CHNS glucose and ENSANUT conditional BMI; those counterexamples remain part of the paper.

## 2. The predecessor identity and input contract

Filshtein et al. predefine a DAG and estimand, then collaborating analysts estimate source-specific conditional generating rules from original individual data. Shared rules include regression quantities and residual distributions. Simulated complete cohorts are checked against source distributions and associations, then pooled with treatment of structurally missing covariates. Our packet does not contain that comprehensive collection of source-fitted conditional rules. Substituting article summaries and assumed missing conditional laws creates an **adaptation inspired by sequential synthesis**, not a faithful replication or a test of the published implementation. Its original information regime can also be examined as a rich-summary reference scenario, provided the added information is explicitly identified. [Filshtein et al., Methods Steps 1–5 and Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC8338788/).

SynthIPD v2 reconstructs survival data from published Kaplan–Meier graphics and risk/censoring information and assigns covariates using subgroup summaries. Its inputs must describe the same population; multivariate categorical reconstruction requires joint-stratum information. CHNS/ENSANUT contain neither survival endpoints nor the corresponding graphic/risk inputs. Therefore the published method is **outside this task's input domain**, not an empirical failure. A cross-sectional constrained-summary analogue would be a separately named adaptation. A genuine survival comparison would require a different task and adequate inputs, so it is unnecessary for the proposed first comparison. [SynthIPD v2, §§3.2–3.2.3](https://arxiv.org/html/2509.16466v2).

## 3. Separate information from construction method

Treat information availability and construction procedure as different factors. A richer packet can improve either procedure. Comparing an article-only Agent to a statistical method given source-fitted regressions would confound those factors; the reverse comparison would do so as well.

| Scenario | Information given to both procedures | Question it can answer | Interpretation boundary |
|---|---|---|---|
| Equal sparse information | Exactly the admitted E0 or E1 packet, task definitions and permitted diagnostics | What can each declared procedure deliver from the same evidence? | Different uptake and completion choices remain part of the procedure; unavailable quantities cannot be silently supplied. |
| Sparse information with additional assumptions | Same empirical packet plus a common, labelled completion specification, or explicitly different assumption sets | Are differences due to model family, uptake, completion or transport? | Assumptions are not extra observations. Shared assumptions answer a narrower question than free model authorship. |
| Equal rich summaries | Same existing target/source summary packet, including requested coefficients if openly supplied | How well can each procedure reproduce supplied statistical information in a coherent table? | Calibration consistency is legitimate utility. It is not evidence of recovering unprovided relations or transport. |
| Source-analyst or oracle rich-summary reference | Conditional coefficients, joint covariance, residual distributions or sufficient statistics unavailable in the sparse packet | What is attainable when dependence information is much more complete? | Report separately as an information-rich reference, not as a matched-input win. Rich information is not a guaranteed mathematical upper bound on every quality measure. |

The historical CHNS experiment already demonstrates useful supplied-summary consistency: reference-assisted author means for BMI were 0.052821–0.055789 against the supplied 0.054946; glucose means were 0.396941–0.413715 against 0.402093; conditional age means were 0.007569–0.007947 against 0.008107. These are observed descriptive ranges, not predicted outcomes of the proposed comparison. All thirty reference statistics were legitimate inputs in that experiment. Its strong calibration should be retained alongside its limits, rather than discounted because the analysis request or target quantities were visible. See `manuscript/SUPPLEMENT_HISTORICAL_RESULTS_v05.md` and the original information-and-revision protocol/results.

A full crossed information-by-method study could estimate changes within each method and compare those changes. The present main and historical experiments do not form such a controlled factorial study: their protocols, authors and model versions differ. Do not calculate a causal method-by-information interaction by pooling them. Neither hidden questions nor hidden statistics are prerequisites for a useful synthesis task; they define different claims.

## 4. A credible same-information sequential adaptation

A strong adaptation should have a transparent factorization such as

`p(age, sex) × p(BMI | age, sex) × p(glucose | age, sex, BMI) × p(HbA1c | age, sex, BMI, glucose)`.

This order is a generating factorization, not a claim that the arrows are causal. Conditional distributions can be represented by standard latent-copula regressions with positive marginal transforms and explicit residual laws. A covariance completion can be converted to a sequential representation by modified Cholesky regression; merely changing this representation does not create a new statistical law or a meaningful new comparator.

To improve on the current reference substantively, an adaptation must change an identified limitation, for example its admitted constraints, marginal flexibility, missing-dependence completion or transport rule. It should:

1. Use every admitted relationship either as a declared constraint, a check or an explicit nonuse. Match original adjustment sets and survey/source operators; never interpret a conditional coefficient as a marginal correlation or an SE as individual variability.
2. Solve constraints against the statistics of the actual completed law. For non-Gaussian margins, transformed latent coefficients are not automatically the required observed-scale regression coefficients. Retain infeasibility and approximation residuals.
3. Prespecify support, residual distributions, regularization of unidentified dependence, solver limits and information-dependent rules before execution. Use conventional numeric optimization, without access to records. Do not select among model families by closeness to a supposedly withheld result.
4. Distinguish source completion from target transport. For sparse E1, fit the Jansen projections in their Jansen scenario; using Bao, MIND or Pani does not turn their populations into the target population.
5. Provide the same allowed feedback and opportunity to use summaries. An optimizer can calibrate supplied quantities; those optimizer evaluations are construction work and should be counted separately from final row draws.

For the ENSANUT sparse-E1 alternative, a conventional procedure can include Pani by explicitly completing a source distribution under which its adjusted slope is defined, then declaring which conditional quantity is transported. The missing age distribution, weights and individual dispersion must be assumptions or supplied evidence, not inferred from age-band SEs or target quotas. An adjusted mean slope alone does not always require every individual variance to be known; a linear conditional-mean specification can impose it under named residual/design assumptions. Thus the current nonuse is a limitation of this particular fixed specification, not a general impossibility theorem. A separate assumption-matched sensitivity analysis could compare this choice with contextual nonuse. It is not the recommended first execution and is not performed here.

## 5. Quality should follow scientific use

Maintain three parallel quality tracks. Do not combine them into one heterogeneous accuracy score.

| Track | Relevant measures | Available now / limitation |
|---|---|---|
| Supplied-summary consistency | Signed and absolute residual for each supplied coefficient, mean, SD, quantile, Pearson/rank association; support/feasibility failures; source-qualified analytic residuals | Existing source calculations and target aggregate outputs support this. Exact constraints demonstrate calibration, not independent validation. |
| Requested analysis utility | All prespecified regression coefficients in native units; sign, magnitude, adjustment meaning and constructor/seed variation; fit availability | The six main endpoints and historical CHNS endpoints already exist. Avoid relative errors near zero and avoid declaring clinical acceptance from an arbitrary aggregate score. |
| Unprovided implications and robustness | How requested but unprovided projections change over reasonable completion/transport assumptions; whether conclusions reverse; which quantities are unidentifiable | Current specs disclose assumptions, but no calibrated robustness envelope is established. New sensitivity fits would be new scientific work. |

Also retain marginal tails, dispersion and joint diagnostics: plausible central moments alone can hide an unusable regression. When evaluating future subgroup effects, risk prediction, calibration or survival analyses, define their estimands and required held-out/supplied information explicitly. They cannot be claimed from today's six coefficients. Synthetic training/testing against original patient rows is outside the current access and analysis scope.

Report each constructor's fixed-seed results, then its mean discrepancy, then the arm summary. A01 labels are not pairs of independently authored E0/E1 models. The number of synthetic rows or seeds does not multiply the number of independent biomedical cases. A fixed statistical procedure needs no artificial set of five identical copies; its stochastic variability and the Agents' between-construction variability are distinct quantities. A family-level ranking would need a separately designed comparison of construction policies and budgets.

## 6. Uncertainty and the real-versus-real noise reference

Four uncertainties must remain separate: finite generated sampling; source-estimate uncertainty; model/completion/transport uncertainty; and uncertainty in the selected real reference estimate. Three seeds cover only the first, conditional on a fixed law. More generated rows can reduce that first component without adding biological information. Source and structural uncertainty do not shrink merely because a large table was emitted.

The retained CHNS community-cluster CR1-t intervals and ENSANUT cluster-resampling stability bands provide real-reference context. They are not equivalence margins or proof of the correct population coefficient. Interval overlap is descriptive, not evidence that two procedures are interchangeable. A synthetic p-value does not represent clinical evidence gathered from 3,000 new people.

A real-versus-real comparison would quantify how much the same statistic changes between comparable real samples under the same eligibility, weighting and cluster design. It is useful for interpreting attainable agreement, especially if changes at n=3,000 are substantial. It must not be fabricated by treating reference CI width as the error between two independent samples. Even the usual variance-addition approximation requires assumptions about independence, sample size and design; supplied-summary calibration is correlated with its real reference by construction.

If retained cluster-resampling **aggregate replicates** and valid design metadata exist, a later aggregate-only analysis can summarize their variation without opening rows. A band alone cannot reconstruct the replicate distribution or cross-statistic covariance. No matched n=3,000 real-versus-real distribution has been verified in this review. Producing fresh splits, bootstraps, sufficient statistics or conditional regression rules from real records would require a separate custodian analysis/access epoch; it is not “already done” merely because the cohort exists. Do not make that extra task a prerequisite for reporting the present calibration findings.

## 7. Unidentifiable relations need a declared answer

Sparse marginals plus a few projections do not generally identify a full joint distribution. Two Jansen separate projections leave residual BMI–glucose dependence unspecified; additional choices can change fully adjusted coefficients. CHNS conditional age and ENSANUT conditional BMI therefore remain consequences of the completed law rather than new observations.

For each requested quantity, label it as supplied, algebraically implied within the adopted law, or dependent on unidentified assumptions. If several plausible completions give different values, report the disagreement instead of selecting the completion closest to the revealed reference. A future sensitivity interval must be called an assumption envelope unless a justified probability model supplies calibration. A valid outcome can be “this analysis cannot be supported by the supplied evidence.” This is a quality result, not a failed obligation to beat another Agent or statistical method.

## 8. One next discriminating comparison and stop rule

**Question:** using the already existing CHNS thirty-statistic packet, can a prescribed sequential statistical adaptation produce calibration consistency comparable to the retained reference-assisted Agent constructions, and where do its constraints conflict?

Use the exact historical R packet and analysis definitions, not the later main-study E1 packet. The manifest binds the existing reference summary to SHA-256 `7cda7cb9a3a1b337b92bc6f6664366fede1cd50dd1da9d255d20c346d5d25b02`; the locator is `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcIA/R01/b/input/reference_summary.json`. The same hash is listed for R02 and R03. Before any future execution, reconcile actual source additions/feedback visible to those historical authors. Any unmatched information must be disclosed; exact nominal packets do not guarantee identical actual information use.

The proposed single statistical construction uses a predeclared conditional/covariance completion with positive flexible margins, the same three projection constraints and both Pearson and rank targets. Its fixed family must be able to represent those operator types; if a simple Gaussian-copula restriction prevents their joint fit, record that restriction or review a fixed mixture extension **before** execution. Do not call a manifestly incapable family a strong baseline. Marginal quantile residuals and infeasible constraints remain visible. The target aggregates are explicitly calibration inputs, so optimizing their residuals is permitted. No source or target participant fitting is needed.

Compare the resulting three 3,000-row final seeds to the retained R01–R03 aggregates, without regenerating the historical Agent tables. Use the historical final-seed schedule (4101–4103) for a comparable draw count; identical seed labels do not imply common random numbers across distinct samplers. Show all three focal coefficients and the complete 27 diagnostics, and retain historical construction/feedback budgets. This first comparison is intentionally descriptive: one newly prescribed law versus three previously authored laws cannot estimate general superiority or eliminate temporal/model-selection asymmetry.

This choice directly addresses the gap between “the Agent can match supplied statistics” and “Agent authorship adds something conventional synthesis cannot achieve under those inputs.” It needs no new dataset, no new reference analyses and no new Agent run. It does require a separately frozen statistical construction and new scientific generation/evaluation if the user later chooses to execute it. The existing main-study claim lock remains closed.

**Practical stopping rule:** one reviewed construction specification, one fixed construction/solver budget, three final draw slots, one independent aggregate audit, then stop regardless of ordering. Freeze any permitted source-summary fitting and feasibility tolerances before the new draws; do not tune tolerances to make one method pass. A failed fit or failed draw stays in the report, without adding families, seeds, constructors or datasets. If the statistical method also matches the supplied quantities, conclude that this calibration ability is shared. If it does not, conclude only that this declared adaptation had the reported limitation. If residual differences are small or their scientific relevance is not established, leave the ranking unresolved. No outcome is a trigger for an automatic experiment escalation.

## Evidence consulted

- `manuscript/DRAFT_v0_5.md`, `SUPPLEMENT_SOURCE_AND_ASSUMPTIONS_v05.md`, `SUPPLEMENT_HISTORICAL_RESULTS_v05.md`, and `CORE_CONTRIBUTION_POSITIONING_2026-11-03.md`.
- `work/main_study_freeze_2026-11-03/CLAIM_LOCK.json`, `RESULTS.md`, the comparator specification/code, `implementation/reference_bindings.json`, CHNS evaluation definitions, ENSANUT Pani scoped source extract, and statistical construction/review receipts. S01 `model_spec.json` files were read from their receipt-listed `evcMS` locations.
- `work/information_revision_ablation_2026-11-03/PROTOCOL.md` and `INPUT_MANIFEST.json`; historical numerical results above come from the manuscript supplement, not a fresh calculation.
- Primary predecessor full texts linked above, inspected on 3 November 2026. No result for a new adapted comparator is claimed.
