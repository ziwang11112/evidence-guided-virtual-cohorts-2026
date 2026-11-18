# Information provision and feedback-revision experiment

Design proposal following the user's 3 November question about ablations. No experiment is launched, no trial budget is reset, and no frozen result is changed. The product remains useful generated biomedical data under the adaptive scope in `ADAPTIVE_DATA_GENERATION_SCOPE_2026-11-03.md`.

## Separate the experimental factor from the evaluation

The three previously discussed reference roles are not three mutually exclusive algorithms. Agreement with provided references evaluates fit; agreement with unused comparable references can evaluate external utility; agreement after every reference has informed revision remains an exposed-reference assessment. An experiment must specify what changes between arms and apply a common evaluation to their outputs.

Two useful factors are explicit provision of additional real-reference information and an additional feedback-revision stage. Information provision tests the value of supplied information, not superiority of the underlying algorithm.

## Minimal four-cell design

| Arm | Inputs explicitly supplied | Evaluated delivery |
|---|---|---|
| L0 | Research request, population description, external literature | Initial delivery |
| L1 | Same inputs as L0 | Delivery after one additional recorded source-feedback revision |
| R0 | Same base inputs plus a specified development/reference summary package | Initial delivery |
| R1 | Same inputs as R0 | Delivery after one additional recorded source/development-feedback revision |

The summary package's population, measurements and contents must be specified before constructing candidates. It may contain distributions and associations. Separating marginal summaries from joint summaries would be a later information-factor experiment, not an additional required arm now.

All arms know the intended analyses and can perform scoped retrieval, choose structures, use available tools and conduct ordinary authoring trials. Initial delivery does not mean an artificially static-only Agent. L1 and R1 test the increment from a defined post-delivery feedback stage. Each revised candidate descends from its own retained initial candidate within that information condition; do not compare a newly authored unrelated model as though it were a paired revision.

With open retrieval, L0 is not guaranteed ignorant of facts contained in the supplied reference package. The factor is **explicit provision**, not guaranteed absence of knowledge. Record actual retrieval and overlap. If an arm independently retrieves equivalent summaries, retain that outcome and interpret the contrast accordingly; do not silently exclude it or prohibit routine search to manufacture an information gap.

Feedback must respect the arm's declared information sources. In particular, L1 must not receive new unpublished development-reference statistics that only R0/R1 are supposed to receive. If such feedback is intentionally allowed, the comparison becomes a comparison of complete workflows with different cumulative information, not separable information and revision effects.

## Questions and claim limits

- R0 minus L0: effect of explicitly supplying the specified reference package under the common authoring procedure. This is an information/access-value comparison.
- L1 minus L0 and R1 minus R0: paired effect of the additional feedback-revision stage, including its additional computation. Report improvement, deterioration, no change and cost.
- Difference between these paired changes: exploratory evidence that revision benefit depends on the information condition. It requires adequate independent constructions/tasks; repeated synthetic seeds alone do not establish it.

The initial/revised contrast does not isolate feedback content from extra reasoning or compute. A matched-budget self-review comparator is optional if a stronger mechanism claim becomes important; it is not compulsory for demonstrating that the data-generation workflow is useful. No direct-analysis-Agent superiority, training or multi-Agent architecture is required.

## Shared evaluation and practical start

Use the same declared research purpose, model service, ordinary authoring budget, output-size policy and evaluation definitions within a comparison. Generators may differ scientifically across tasks and information conditions. Evaluate distributions relevant to the intended use, needed joint/conditional relationships, and downstream analysis results with reference uncertainty. Exact equality with a real sample is not the success criterion.

Report fit to inputs separately from performance on any unused comparator. A reference used for revision cannot simultaneously establish independent utility of that revised version. Different datasets require population, measurement and selection comparability; multiple datasets do not guarantee independence. If all available references are exposed, run a useful developmental fit comparison and label its scope. Existing CHNS remains developmental even if new author contexts do not see its result values. No new cohort acquisition is required by this design.

Preserve the initial and revised versions, record all consequential attempts and use final deliveries for their declared comparisons. A retained law with identical output is a no-change result, not a new independent construction. Independent scientific construction/task is the relevant replication unit; generated rows and repeated seeds measure different variability. Specify the actual bounded allocation and success/stop interpretation in the execution unit before running it; this design note creates no new execution allowance.

For the lowest-cost start, use one clearly stated information condition and its paired initial/revised deliveries. If that exposes a useful question about information availability, expand to the four cells above within a separately stated allocation. Broad information sweeps and every possible component ablation are unnecessary.
