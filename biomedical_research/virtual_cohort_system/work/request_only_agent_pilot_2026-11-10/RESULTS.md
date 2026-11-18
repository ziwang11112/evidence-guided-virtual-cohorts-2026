# From research requests to virtual cohorts: first API/retrieval pilot

Completed 10 November 2026, America/Chicago (API calls 03:47:39–03:54:26 UTC on 11 November). The user requested that both a capable ordinary Agent and our workflow begin with a research need and independently find their evidence. This is the first live comparison under that information boundary.

**The complete tool loop ran, and both lipid Agents delivered analyzable cohorts after repairing their own programs. Scientific agreement was mixed; the workflow was not consistently closer to the stored clinical reference. Both blood-pressure sessions stopped at a shared input-size limit before submitting a generator.** Those failures remain in the four-session denominator. No replacement sessions were launched.

## What was actually implemented

Both arms used `gpt-6.1-sol`, high reasoning effort, the same case request, the same packages and search/read/submit/run/finalize tools, and the same limits. Neither received prepared papers, source coefficients, an old generator or target analysis answers. Every session started with an empty source collection and its own API context.

The ordinary Agent chose its own research and coding strategy. The workflow Agent additionally received a reusable scientific procedure: connect requested analyses to missing evidence; preserve study conditions and statistical definitions; distinguish reported, derived and assumed quantities; build a joint model; inspect generated data; decide whether to search, repair, revise or retain. This pilot's treatment is that procedure on a common tool runtime. It is not a comparison of multiple specialists, a learned optimizer or an automatic calibration solver.

Agents searched Europe PMC and read available PMC article texts and embedded tables. Access was not unrestricted web browsing. The shared gateway screened target-family/project aliases before showing text; this is a conservative screen, not proof against all overlap or pretrained knowledge. Each source, query, response, candidate and tool result is recorded locally. Candidate code ran only in the existing WSL/bubblewrap sandbox, without reference files, credentials or network access. The host never selected scientific parameters or edited a submitted generator.

All four terminal outcomes were closed before final sampling and reference comparison. Selected laws produced three 3,000-row tables at seeds 54001/54003/54007. Previously exposed aggregate reference estimates were reused; there was no new patient-data access or target refitting. These are developmental comparisons, not new prospective clinical validation.

## Delivery and resources

| Case / arm | API calls | Queries / full-text downloads | Candidate versions / trial executions | Final delivery | Estimated API cost |
|---|---:|---:|---:|---|---:|
| Blood pressure / ordinary | 19 | 11 / 2 | 0 / 0 | Input-byte limit; no candidate | $0.1830744 |
| Blood pressure / workflow | 20 | 12 / 2 | 0 / 0 | Input-byte limit; no candidate | $0.1880455 |
| Lipids / ordinary | 21 | 8 / 2 | 2 / 2 | Selected v002; 3/3 final tables | $0.2447480 |
| Lipids / workflow | 18 | 3 / 3 | 2 / 2 | Selected v002; 3/3 final tables | $0.2508103 |

Total: **four fresh Agent sessions, 78 receipted API calls, two delivered scientific generators, six successful final tables containing 18,000 fictional rows, and six unavailable scheduled table slots**. Seeds are within-generator simulation repetitions, not additional constructors or independent populations. Both initial lipid trials failed; both repaired trials succeeded. Final execution itself had zero failures.

Usage-based cost was **$0.8666782**, with no unresolved usage reservations, against the $16 ceiling. This is a tariff estimate, not an invoice. Receipts contain 2,157,824 cumulative input tokens and 17,570 output tokens, including repeated/cached context. API/retrieval construction wall time was about 6 minutes 47 seconds; implementation, preflight review and final analysis time are separate. No recruitment-cost reduction is estimated.

## What analyses did the final data support?

All three prespecified lipid analyses are shown. Slopes adjust for age and sex and are expressed as mg/dL per five BMI units; residual correlation additionally removes BMI. Values are means over the three final sampling seeds, with their min–max range.

| Analysis | Ordinary Agent | Workflow | Existing reference sample |
|---|---:|---:|---:|
| BMI–HDL slope | −1.759 [−1.985, −1.423] | +0.709 [+0.418, +1.078] | −4.623 |
| BMI–total cholesterol slope | +12.131 [10.820, 13.522] | +7.488 [5.927, 8.971] | +5.683 |
| TC–HDL residual Pearson correlation | 0.349 [0.338, 0.364] | 0.208 [0.199, 0.222] | 0.512 |

The workflow was closer on the TC slope; the ordinary Agent was closer on the HDL slope and residual dependence. Both retained positive residual dependence but below the reference estimate. The workflow's HDL slope had the opposite sign to this reference sample. This cannot be presented as an overall workflow gain or universal data validity. Conversely, the blood-pressure non-delivery is an engineering failure and supplies no scientific-quality estimate.

Reference estimates are not known population truths. The stored conditional HC3 sensitivity intervals are [−8.392, −0.854] for HDL and [−3.754, 15.120] for TC. Their overlap with a generated estimate does not establish equivalence. A reference residual-correlation interval is unavailable. Generated seed ranges quantify sampling variation conditional on one law, not source, transport or model uncertainty.

Necessary secondary checks also remain visible:

| Diagnostic | Ordinary | Workflow | Reference |
|---|---:|---:|---:|
| TC sample SD, mg/dL | 39.303 | 47.518 | 42.847 |
| HDL sample SD, mg/dL | 13.632 | 14.208 | 20.176 |
| HDL greater than TC | 0/9,000 rows | 23/9,000 rows | Not supplied |

All delivered rows were retained. No post hoc clipping, filtering or matching to the reference was performed. The component-order violations need attention in any application; the current outputs were not silently repaired.

## What did the Agents do themselves?

The workflow independently located a Ghana study with a full reported correlation matrix and sex-specific summaries, reconstructed an approximate covariance matrix, solved the joint regression normal equations and derived residual covariance. It then combined those conditional relationships with Tanzania marginal anchors and a Uganda demographic proxy, documenting substantial transfer and mixture assumptions. Independent static algebra gives a source-derived residual correlation of approximately 0.1864 and structural BMI slopes of +6.8042 (TC) and +0.2186 (HDL), before the additional population mixture. These structural quantities are not identical to the final evaluator's marginal-over-mixture estimands.

The ordinary Agent independently used Tanzania/Uganda and Maasai material, interpolated categorical BMI evidence into continuous slopes and explicitly assumed a conditional lipid correlation of 0.35. Its notes acknowledged that the requested residual correlation was not reported by the retrieved sources. Its closer residual result therefore does not establish a better-supported correlation estimate.

This is a substantive construction capability: the workflow used retrieved joint statistics numerically rather than merely attaching citations. It also demonstrates a boundary: a more explicit derivation does not guarantee that those relationships transfer to the requested population. Provenance quality and target agreement must be assessed separately.

The source audit also found limitations that a citation alone does not resolve: the Ghana paper contains inconsistent female sample-size labels across two tables, which the Agent did not flag; conditional lipid SDs were assumed reductions of marginal SDs; longitudinal migration changes were used as cross-sectional scenario offsets. These remain assumptions or source-quality caveats, not validated constraints.

Both lipid revisions repaired parameter-wrapper access (`KeyError` on `age_beta` or `ghana`). The ordinary Agent unwrapped its declared model; the workflow embedded the same declared constants in its submitted program. Static review found unchanged scientific laws. **Do not call this a scientific feedback improvement:** it is autonomous software repair enabling delivery.

## Implementation finding and next decision

The blood-pressure failures identify a shared retrieval-interface problem. Last transmitted request sizes were 239,346 and 246,269 bytes, close to the 250,000-byte ceiling. Tool outputs accounted for about 87% and 83%; encrypted continuation accounted for only about 6% and 9%. Both sessions spent roughly 130,000 returned characters on raw search metadata. Author/affiliation fields often preceded complete titles and PMCIDs. The search did find studies, but its presentation made them unnecessarily expensive to inspect.

**Decision: retain the current scientific question and free Agent choices; repair the shared search presentation before scaling.** The next mechanical change should return compact complete hit cards, explicit abstract previews and record-level pagination, with full hash-linked source metadata still accessible. Offline replay of the existing cached search results can check this without new API spending. A subsequent rerun must be separately versioned, disclose this failed first round and preserve equal access for both arms. No HDL sign, covariance, source coefficient or desired target answer should be inserted to repair these scientific discrepancies.

The common submission contract also needs a clearer single-level model object and a mechanical shape check, so an Agent does not need to spend a trial discovering the wrapper convention. This should be the same interface repair for both arms, without interpreting or modifying scientific values.

The first round is complete. No paid replacement, new case, additional seed, method component or manuscript claim was added after seeing outcomes. One constructor per arm in one successfully delivered case is insufficient for a superiority claim or a definitive explanation of arm differences.

## Audit and artifacts

- [Frozen protocol](PROTOCOL.md), [preflight review](PREFLIGHT_REVIEW.md) and [launch freeze](LAUNCH_FREEZE.json).
- [All analysis summaries](ANALYSIS_RESULTS.csv) and [machine-readable evaluation](EVALUATION.json).
- [Interactive local results page](figures/SCIENTIFIC_AGGREGATES.html), [primary figure](figures/PRIMARY_ENDPOINTS.png) and [secondary figure](figures/SECONDARY_DIAGNOSTICS.png), with SVG/PDF versions alongside.
- [Independent saved-table recomputation](review/INDEPENDENT_RECOMPUTATION.md): 755 checks passed, maximum numerical difference 5.33×10⁻¹⁴; all 12 scheduled slots, unit conversions, hashes and no-row-deletion verified.
- [Source/tool/cost audit](review/TOOL_SOURCE_COST_AUDIT.md), [independent scientific provenance audit](review/SCIENTIFIC_PROVENANCE_AUDIT.md) and [retrieval repair proposal](review/RETRIEVAL_INTERFACE_REPAIR_PROPOSAL.md).

Original frozen experiments and manuscript v0.28 remain unchanged. API payloads, downloaded articles and individual generated records remain local. This unit has not been exported to the public repository.
