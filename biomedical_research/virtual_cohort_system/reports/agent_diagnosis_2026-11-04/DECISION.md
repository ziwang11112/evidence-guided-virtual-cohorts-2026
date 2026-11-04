# Diagnose the evidence and joint model before adding a module

4 November 2026. This decision follows the user's challenge to treating source/target-population simulation as necessary, and their agreement to first inspect missed evidence, actual contradictions and genuinely missing information. It supersedes the prospective source-context implementation priority in the previous live-run result and state. The completed experiment, frozen candidates, results and receipts remain unchanged.

## Finding

There is no basis to require source-population replay for every use of evidence-guided virtual biomedical data. The live run's unavailable replay checks identify limitations of the submitted checking setup and available source-context information; they do not prove that lack of replay caused the unfavorable adjusted BMI result. The narrower review found two actionable issues: incomplete extraction of joint/subgroup evidence and a joint-model implication that should be understood before interpreting a requested conditional analysis.

### Evidence that was missed or not used quantitatively

The [original-source review](EVIDENCE_GAPS.md) distinguishes quantities missing from the ledgers from quantities present but only used as context. Wang Results 3.4 reports a serum-glucose–HbA1c Spearman correlation of 0.743 among 425 participants with a known diabetes history. That subgroup association is absent from both evidence ledgers; B includes the total-sample correlation of 0.529. Other subgroup composition and joint threshold profiles are not represented quantitatively.

These are useful leads, not ready-made target parameters. Known-history diabetes is not the same group as the source's full diabetes category or the generator's latent elevated-glycaemia component. A subgroup Spearman coefficient is not a conditional Gaussian correlation, and none of these numbers supplies the requested BMI coefficient adjusted for glucose, age and sex. The finding warrants more complete extraction and an applicability decision, not copying 0.743 into B's copula.

The protocol restricted the live demonstration to three previously used original studies. The general tool supports search, but unused query/download counts did not authorize searching outside that scope. Thus the absence of broader gap-driven retrieval must be attributed partly to the coordinator's experiment design, not automatically to an Agent's failure to use available calls. Jansen was available only as an abstract in the supplied route; no full-text coefficient should be treated as known.

### No demonstrated transcription or implementation contradiction

The earlier independent audit found source anchors correctly transcribed, mean/median and Pearson/Spearman distinctions preserved, and the final programs consistent with their declared specifications. The pre-execution B moment defect was corrected and preserved in history. No additional numerical coding defect has been established in this review.

Both authors nevertheless selected substantial assumptions: conditional slopes, demographic composition, latent prevalence and dependence. B also introduced a 15% meal-affected scenario with no source estimate for that fraction. Disclosure makes those assumptions inspectable; it does not establish their accuracy. Unknown fasting adherence alone does not estimate a contamination rate.

### A positive model pathway does not fix an adjusted regression sign

The [structure diagnosis](STRUCTURE_DIAGNOSIS.md) derives the requested regression's dependence on residual covariances. It also inspects a tractable conditional part of the submitted B model, without generating records or refitting any data.

Let X denote BMI, G0 pre-meal glucose and H HbA1c. Within one latent component and fixed age/sex, the submitted lognormal model gives:

`d log E[H | G0, X, age, sex, component] / dX = 0.002/f_H(X) − k × 0.012/f_G(X)`

Here `f_H(X)=1+0.002(X−24.5)`, `f_G(X)=1+0.012(X−24.5)`, and `k=rho*sigma_H/sigma_G` uses the component's log-scale SDs. At the chosen BMI center, the derivative is approximately −0.001336 in the lower component and −0.002949 in the elevated component. The coordinator independently recalculated these two values from the saved specification.

This demonstrates a compatible negative conditional association in a specific part of the submitted joint model, despite its positive direct BMI mean multipliers. It is not an attribution of the full observed OLS reversal: the evaluated regression marginalizes the latent component, uses glucose after the assumed meal increment, and adjusts age/sex linearly. Those differences matter. The stored report lacks the full residual covariance matrix needed to decompose the complete result; no new rows or fits were accessed to manufacture an explanation.

The finding justifies asking the author to explain the analysis implied by its joint law. It does not justify forcing a positive coefficient, deleting the meal assumption to obtain a favorable result, or claiming that a source-replay module would fix the issue.

## Minimal prospective improvement

Use a concise analysis-oriented review in the existing scientific author workflow, rather than first building another mandatory controller:

1. State the requested analysis and the available population, era and measurement description. The last task omitted explicit geography/era, even though the coordinator knew the intended comparison. Providing this metadata need not reveal outcome statistics.
2. Ask the Agent to map relevant joint and conditional evidence to the requested analysis, distinguishing direct numerical evidence, contextual evidence and assumptions. Cover important subgroups and source adjustment sets; do not demand a particular sign.
3. If the requested dependency is missing, let a future, separately bounded search target that gap instead of limiting every search to preset DOI lookups. Use appropriate lawful original-source routes; absence from PMC alone is not a universal full-text-access conclusion. This review does not itself open new searches or restore closed budgets.
4. Ask the Agent to inspect what its proposed joint law implies for the requested analysis. A short analytic explanation or ordinary generated-data diagnostic may suffice. If a finding conflicts with applicable evidence or the stated model, correct that specific issue. An unanticipated coefficient is not automatically an error.
5. Keep source-population simulation, soft statistical constraints, direct data generation, programmatic generation and alternative-assumption scenarios as options. Choose only the machinery justified by the available evidence and intended use. If evidence cannot resolve a relation, report that dependency and its assumptions without claiming it has been recovered.

Success remains useful scientific analysis of the generated data under the declared information setting. Exact individual matching and universal superiority to bespoke statistical methods are not requirements. A reconstruction using supplied reference summaries and an evaluation against an unused reference answer different questions; neither source replay nor a particular Agent architecture defines the method.

## Scope and decision

This was an audit of existing originals, code and aggregate results, plus exact algebra/arithmetic on already saved constants. It produced no new clinical analysis, generated table, model fit, source search or patient download. The two old candidates remain closed. Evidence found in this post-result audit must not be mislabeled as a prospective discovery or an independent confirmation.

**Decision:** continue the core Agent data-generation direction through better evidence coverage and analysis-aware model review. Do not require source/target-population replay, add unrelated experiments, or claim the cause of the previous outcome is fully identified. The next scientific run requires a fresh explicit specification; none was started here.
