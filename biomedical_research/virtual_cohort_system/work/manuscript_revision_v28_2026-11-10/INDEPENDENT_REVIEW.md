# Independent content review of manuscript v0.28

**Content review passed; no mandatory correction remains.**

Audited draft SHA256: `721bbc4d58b01c0bbbb2b9c2129628a58072653ecf55117da919bf6233802aca`. Initial reviewed version: `8ba1700d0bd242f2553a4c53fdcd79d16eb8f268673eb4190a07e85e4dc5cd5f`. The reviewer is independent of the editorial agent but authored the prior PNS attribution audit; this is not a second independent primary-source or patient-level validation.

## Required clarification

The Q2 endpoint has been made explicit. No mandatory correction remains.

## Verified findings

| Area | Result |
|---|---|
| Existing material | All11 old image paths retained. Of15 old table blocks,13 are identical; Tables4/5 preserve every old row and add only one PNS row each. All38 old reference lines remain identical. |
| Numbering | Figures1–8 and S1–S5; Tables1–5 and S1–S11; references1–41. No duplicate figure/table labels. |
| Audit scope | 30 constructions,90 requested-analysis records+6 SD records;7 requested+6 diagnostic numerical implications and83 uncomputed requested implications. No inflation into independent clinical replications. |
| PNS results | All15-draw ranges,5author medians, weighted/unweighted references and TableS11 interval endpoints match original RESULTS at displayed precision. |
| Dispersion and feedback | All marginal/residual SD ranges and BPmean ranges match. All generated means are below the weighted reference. Source-check counts108/75/27 match RUN_ACCOUNTING. |
| Prior independent recomputation | The receipt supports306 numerical comparisons and maximum difference1.81899e−12; the manuscript correctly avoids claiming that bootstrap quantiles were independently refitted. |
| Statistical definitions | PNS medians versus other-case means, per5BMI units, innovation rho versus requested residual Pearson, rank versus raw/conditional measures, shared reference and nested draws remain distinct. A02 rho is0.65. |
| Attribution examples | L03 theoretical/mean/range values and iron OR/rank summaries match the master. Iron reweighting/redraw consequences are distinguished from an unexplained population difference. |
| Inference limits | The manuscript does not claim causal attribution of all error, a validated provenance score, feedback benefit, universal author convergence or reliable new-population inference. Cards and the cross-provider pilot remain future work. |

The abstract's SBP-versus-DBP comparison is supported descriptively: across15draws, mean absolute discrepancy is0.34610 versus0.83513mmHg per5kg/m². All DBP estimates exceed the weighted reference, while all residual correlations fall below it. This does not imply full joint-distribution adequacy. The text retains the failed iron primary comparison and earlier prospective criteria.

New reference39 matches the local INTERSALT packet's DOI and journal/year/pages. TableII p322 had been directly inspected in the earlier PNS audit; it was not newly reopened here. Reference40 matches the bibliographic citation in local PMC9278591.txt. Both official URLs in reference41 match the retained PNS source/download manifests, whose archive/member hash strings match the frozen RESULTS binding. No internet lookup or target archive access was needed.

prepare_draft.py was read and parsed, not executed. It guards v27 by SHA256, performs explicit replacement assertions, reads story inserts, writes v28/REVISION_FACTS and rechecks v27. It imports no scientific generator or evaluator. Its new numbers are editorial literals, so this numerical cross-check provides the required integration verification.

## Resolved precision improvements and remaining review boundary

The root applied all three requested clarifications and they were confirmed in the audited final hash: Q2 before glucose adjustment; Table5’s **conditional reference resampling interval**; and Discussion’s comparison with the **measured target reference**. These corrections preserve the numerical findings and avoid treating the reference as population truth.

This review covers content and artifact consistency. New Figure7/Figure8 files exist, but their rendered panels and the final PDF were not visually inspected here; figure/layout review remains separate. No patient or generated record table was read, no scientific run repeated, and no manuscript or old artifact edited. Exact hashes and structured checks are in INDEPENDENT_REVIEW.json.
