# Scaling the original-article experiments

22 November 2026. The matched lipid experiment is complete. All 12 blocks had admissible pairs in both arms. Eleven targeted searches and zero ordinary second models crossed the registered materiality threshold. The result qualified the study for testing a second publication. The other three articles below are candidates. [Results and complete denominators](RESULTS.md)

## Research question and unit of evidence

An investigator has paper summaries but lacks the paired measurements needed for an intended scientific analysis. Several models can match those summaries. The useful data product is a virtual cohort that enables the analysis, together with a second admissible construction showing when the result depends on a modeling assumption. Observed patient samples provide a separate check on transfer. A difference between two constructed prevalence estimates is a demonstration of sensitivity. An accuracy claim requires the matching target-population analysis.

The paired experiment starts each follow-up condition with the same article and the same first submission. The comparison asks whether explicitly requesting an alternative changes the probability of producing a scientifically material, source-compatible pair. More draws from one program improve numerical precision. More separately authored programs measure repeatability on one paper. More eligible publications test how broadly the procedure works.

## Article portfolio under consideration

| Published source | Values supplied by the article | Intended pair of analyses to check at admission |
|---|---|---|
| Mwanza lipid survey, current experiment | Municipal cholesterol means, two single-marker frequencies and the mean individual ratio | Mean non-HDL and the fraction reaching 160 mg/dL. The first is invariant under re-pairing. [Original article](https://doi.org/10.1371/journal.pone.0223189) |
| Polish lung-function survey | Sex-specific volume means and SDs, association and regression information on paired measurements | Ratio of the group means and the fraction with individual FEV1/FVC below 0.70. Overlapping source constraints must be checked at their printed precisions. [Original article](https://doi.org/10.1186/1465-9921-13-57) |
| Zhu iron-status study | Published joint counts across hemoglobin and ferritin categories | Crude threshold odds ratio and continuous rank correlation. Decide before authoring which continuous marginal assumptions the evaluator supplies and which the paper can check. [Original article](https://doi.org/10.1024/0300-9831/a000014) |
| Australian handgrip study | Measurements for the two hands by age and sex | Average bilateral strength and the mean absolute difference between hands. The second is sensitive to the within-person assignment. Check all available joint statements in the original before freezing. [Original article](https://doi.org/10.1186/1756-0500-4-127) |

These are four existing source-study families with different constraint structures. Reusing these sources measures performance on known problems. A new patient dataset or a held-out publication would be necessary for a fresh generalization claim. Each source needs a predeclared extraction rubric, biologically relevant constraints, one invariant or well-constrained comparison, one potentially sensitive use, and a use-specific tolerance. If an intended comparison is unsupported, publish the admission failure before considering a replacement.

## Call and cost envelope

* One source has 12 matched blocks, with one initial and two follow-ups per block, for at most 36 calls. Each available program receives three registered draws. There are 12 paired comparisons, regardless of the number of virtual rows.
* The four-source version would have 48 blocks and at most 144 API calls, including this pilot. The three candidate sources would add at most 108 calls. The intended study ceiling is USD 18 per source and USD 72 in total if each new article passes a fresh maximum-token budget check. The user's stated USD 400 monthly allowance gives room for replications. Neither the balance nor an invoice is available to this experiment.
* Use the same primary GPT, tool access, service tier, reasoning effort and per-call output allowance. Archive full prompts, replies, reported model, token details, tariff calculations, code and output hashes. Optional cross-model replication would use the same protocol and a separately reported spending ceiling. It is a second question.
* Apply the pilot's preregistered execution and sensitivity gate before adding papers. If a shared first candidate or a second candidate frequently fails the validator, separate extraction, execution and source-constraint failure before spending on repetition. Archive the original failures. Any change to feedback, tolerance or code is a separate version with a matched control.
* Prioritize lung function for the second article. A ratio below a threshold is a distinct scientific use, and the paper supplies joint information that can rule out some candidate assignments. Check the feasibility of the printed joint statistics with the marginal assumptions and register the use-specific tolerances before spending. Assess the other two publications in the same order of operations. The additional spending ceiling for all three is USD 54 if they pass admission.
* Compare successes and failures by paper and author block. Independent measurements can support absolute agreement for that estimand and population. Neither repeated API sessions nor multiple random seeds enlarge the number of independently measured populations.

[Public model price schedule](https://developers.openai.com/api/docs/pricing) · [Matched lipid protocol](PROTOCOL.md) · [Current paper and source-model examples](../../manuscript/kdd_draft_v49_2026-11-21/README.md)
