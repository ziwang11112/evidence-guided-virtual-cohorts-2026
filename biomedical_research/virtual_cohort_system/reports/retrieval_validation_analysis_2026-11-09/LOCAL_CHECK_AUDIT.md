# Local audit of the 34 unavailable source checks

2026-11-09 — independent read-only audit by `/root/rubric_reuse_audit`.

**The 34 records do not mean 34 statistics cannot be calculated, nor that the Agent must keep collecting papers.** They mean the frozen recipes were not accepted for numerical feedback under a strict declared-estimator metadata contract. This gate does not itself establish source-population equivalence even when a check passes. The run's source limitations, implementation limitations and unresolved target relationships need separate treatment.

This audit read the frozen initial evidence/recipe/sidecar, the identical stage-2 evidence/recipe/sidecar, current v1 and core operator code, gateway usage and finish-action metadata. It did not read real-reference payloads or generated clinical tables, run experiments, change frozen artifacts or alter code. Only this new document was written.

## What the 34 records actually contain

All 34 were **declared `not_computable` in the recipe, with null operators**, before any numerical source-check calculation. The unavailable count is therefore principally a declaration/gating result, not 34 failed estimations on generated data.

| Disjoint family | Count | Why strict v1 withheld a number | What can still be computed honestly |
|---|---:|---|---|
| Greiner geometric means | 6 | No geometric-mean operator; weighting unreported; sidecar also marks nonidentity transform | On positive generated values, calculate `exp(mean(log(x)))` within the declared sex group, under an explicit equal-weight convention. This requires a small operator addition or a separately retained calculation, not another paper merely to define the formula. |
| Greiner age quartiles/medians | 6 | Source interpolation convention and weighting are not established | Calculate the specified quantile probabilities using a named conventional method; examine convention sensitivity if relevant. Keep source-method verification unresolved. |
| Agongo arithmetic means/individual SDs | 10 | Generic “weighting/missingness or statistical definition unreported” binding; all marked definition-not-reported | Arithmetic means and sample SDs are already supported. State equal weighting, selected rows, completeness and ddof=1. A mean is clearly identified as arithmetic in the admitted evidence; the unknown fields do not make its ordinary descriptive analogue meaningless. |
| Ashanti rural/urban Spearman correlations | 6 | Weighting, ties and pair-specific missingness not fully reported | The existing operator ranks complete pairs using average ties and correlates their ranks. That is a valid named descriptive calculation; it is not verified reproduction of the source's exact conventions or a target adjusted Pearson correlation. |
| East African HDL BMI/age category contrasts | 6 | Exact categorical design/source strata and additional adjustment variables are unavailable; current core API has no factor/derived-column recipe | A standard dummy-variable regression or category summary can describe generated data under an explicitly chosen adjustment set. It cannot be relabeled as replication of the published hierarchical regression when source strata/covariates are absent. |

Thus **28 claim records have straightforward descriptive-statistic analogues**, subject to suitable nonempty/nondegenerate rows; 22 already have underlying core operators, and six geometric means expose a simple operator gap. The remaining six also permit useful category-based diagnostics, but not the exact published adjusted contrast from the current six-column target table.

These are counts of *claim records*, not independent pieces of evidence or independent computed quantities. The six Ashanti records are two communities' versions of three pairwise associations; without community labels, comparing one generated cohort with both triples reuses the same three generated correlations. Agongo pooled and sex-specific BMI summaries overlap; its means and SDs describe the same sample. Greiner's sex-specific summaries share source populations. The six East African contrasts come from one study and related models. There are four distinct publications, not 34 independent validations.

## Overlapping causes, without double counting

The actual sidecar flags are:

- 28/34 have weighting `not_reported`; six have explicitly unweighted regression.
- 22/34 have definition `not_reported`; 12/34 have definition `unsupported`.
- 6/34 have transform `nonidentity`, all six geometric means.
- 34/34 have null source operators and recipe status `not_computable`.

These sets overlap and must not be summed as separate failures. The six nonidentity flags largely duplicate the geometric-mean representation issue: a geometric mean is returned in the original concentration unit and does not inherently require a measurement or assay conversion. A proper geometric-mean operator can work on unchanged positive concentrations.

Unknown source sample size or missing estimator precision is **not itself a v1 blocking condition**: the code accepts `source_n.status="not_reported"` and missing source uncertainty. Do not attribute the count to absent SEs or insist that every descriptive comparison requires a source CI. Conversely, a reported CI is estimator uncertainty, not individual dispersion or a tolerance that generated means must fall inside.

Source–target non-equivalence affects the interpretation of all 34 comparisons, but it is not an extra independent count of numerical failures. The adapter calculates on the task-population output; it does not reconstruct the source population, weights, health selection, residence, fasting conditions or assay. A sex/age subset cannot recreate missing source selection variables.

## Where the gate is useful, and where its use was too restrictive

Strict checking usefully prevents false identity: geometric versus arithmetic mean, rank versus Pearson correlation, marginal versus adjusted association, categorical contrast versus a continuous BMI slope, and different units or denominators. Those distinctions must remain.

It becomes overly restrictive **if its unavailable label is treated as a ban on descriptive scientific checking**. All 22 definition-not-reported records share a generic reason although several central definitions are known. Unknown weighting and conventions should remain visible, but an analyst can still calculate an assumption-labelled unweighted mean, sample SD, conventional quantile or Spearman correlation. On a complete generated table, alternative missing-row rules often produce the same numerical calculation; that does not resolve source selection, but it need not prevent computation.

There is a concrete implementation distinction: the core quantile checker permits an explicitly approximate convention when the source method is unreported, whereas v1 independently makes that source-method uncertainty unavailable. The current pilot deliberately chose the stricter contract. This audit does not retrospectively change its results or recommend a fallback that disguises a failed strict check as verified.

A prospective interface should expose three separate judgments:

1. **Calculation:** computed / cannot compute, with formula, subset, conventions and code.
2. **Source-definition match:** verified from source / assumed convention / known mismatch.
3. **Scientific applicability:** matched source context / explicit transfer assumption / unsupported target claim.

Keep the old strict result unchanged and add a separately labelled descriptive result where justified. This is more informative than forcing the Agent either to certify every rare implementation detail or to return no number. It does not lower the evidence requirement for claiming source replication or target usefulness.

## Which scientific gaps remain real

Ordinary estimator assumptions do not supply the missing joint law. Means, SDs, sex summaries and marginal ranks do not generally determine the requested age/sex-adjusted raw BMI coefficients, residual variation or adjusted TC–HDL Pearson correlation. Translating them through a Gaussian copula/lognormal law remains a model assumption, not an extracted fact.

PMC6897412 is a useful counterexample to the idea that every unknown is “unreported weights”: its methods explicitly say the regressions were unweighted, while Table 2 margins were survey-weighted. The six chosen HDL effects are categorical contrasts, with source strata/additional adjustment unavailable and the full reported age-row adjustment set not fully explicit. More primary-text interpretation may clarify the model, but no amount of renaming makes missing stratum/covariates exist in the current delivered table. A simpler generated regression may be useful; it estimates a different contrast.

The source's positive female HDL coefficient versus opposite narrative wording remains a real inconsistency. It was retained and unused, not resolved by choosing the preferred sign. Assay transport and target demographic/lifestyle mixture also remain substantive unknowns. Standard tie handling or a quantile convention cannot solve those problems.

## Retrieval was not stopped by the cap

Actual gateway state records **3 of 6 query units** and **2 of 3 downloads** used: three query units and one download remained. Five literature actions were reserved (two fetch attempts and three search attempts); action counts are not interchangeable with gateway query accounting. Fetch metadata and rejected requests have their own accounting.

The session reserved 28 of 48 controller actions and two of three candidate stages. Finish action `a28` explicitly retained the initial scenario, kept the dependence-source sensitivity, and stated that further revision was not justified by current evidence. It did not report budget exhaustion. That is an Agent stopping judgment, not proof that further retrieval could not help.

A fixed paper count is an engineering budget, not a scientific sufficiency criterion. More focused retrieval can be worthwhile for the missing conditional relations, source design, individual/residual variation or measurement bridge. More papers will not repair an absent geometric-mean operator, and endlessly searching for an unreported software default may be lower value than declaring a standard convention and testing its consequence.

A better prospective stopping rule is question-based: identify the unresolved quantity, state how new evidence could change the construction or conclusion, search while a plausible evidence path remains, then retain/restrict/stop when additional retrieval is unlikely to resolve the consequential uncertainty. Keep a cost/time/action ceiling and an explicit extension decision; do not declare sufficient evidence merely because a paper quota was reached. This audit cannot determine that another search would have found the missing joint evidence.

## Hospital/official knowledge and task-specific utility

Hospital aggregates, study data dictionaries, laboratory documentation and official clinical guidance can help establish measurement definitions, assay limits, eligibility, plausible constraints or context-specific distributions. They should be admitted with their population and measurement scope. Hospital patients are not automatically representative of community adults. A reference interval is not a population SD, a residual covariance matrix or an adjusted effect; clinical authority alone does not identify the needed joint distribution.

Applying **the same prespecified analysis to synthetic and untouched real data is a direct test of task-specific utility**. Align eligibility, units, covariates, contrasts and missingness; retain all requested endpoints and relevant joint/conditional, subgroup and tail diagnostics. Agreement then supports those analyses in that evaluated population and setting. It does not prove the whole joint distribution is correct, validate every possible clinical use, or demonstrate that the literature-based transfer assumptions are true.

Keep reference data outside adaptation. If real-result discrepancies guide model selection or revision, they become calibration feedback and independent evaluation needs a different held-out reference. Repeated synthetic seeds measure finite-draw variation, not additional clinical evidence or clinical confidence intervals. Simple baselines, clinically meaningful prospective error criteria, and independent populations/tasks strengthen a utility claim; merely obtaining computable coefficients does not.

## Local audit anchors

- [Frozen source sidecar](../adaptive_case_loop_2026-11-09/candidates/initial/source_semantics_v1.json), SHA-256 `95077da1679d983606f30e4c01d32a2ff08ff8d346d13d3d07cfe6029b3caf5e`; identical in stage 2.
- [Frozen recipe](../adaptive_case_loop_2026-11-09/candidates/initial/whole_cohort_feedback.json), SHA-256 `f41b3944ff7f1bca87efc29d1eeb6065a3dedf4703856fdd12ae41960fa9a820`; identical in stage 2.
- [v1 gating implementation](../../cohort_harness/semantic_feedback_v1.py#L199), especially definition/weight/transform gates at lines 238–257.
- [Core statistical operators](../../cohort_harness/source_checks.py#L103) and [quantile convention handling](../../cohort_harness/source_checks.py#L46).
- [v1 interface scope](../../docs/SEMANTIC_FEEDBACK_V1.md); [public acquisition summary (local state not redistributed)](../adaptive_case_loop_2026-11-09/ACTION_SUMMARY.json); finish-action metadata in the session event ledger.



Public link note: the acquisition-summary link is a public projection; the original local gateway state is not redistributed.
