# Final report consistency review

Reviewed on 4 November 2026. Scope: root `RESULTS.md`, its closed aggregate `evaluation/REPORT.json`, the live-run additions to `docs/CURRENT_RESEARCH_FOCUS.md`, and consistency with the unchanged `SOURCE_AND_MODEL_AUDIT.md`. `STATE.json`, `LIVE_CLOSURE.json`, `evaluation/REFERENCE_READ_RECEIPT.json` and `evaluation/IMPLEMENTATION_REVIEW.md` were read to resolve status, alias and attribution claims. No real or generated individual rows were read, and no scientific experiment or estimator was rerun. Review calculations only selected and rounded existing aggregate values.

**Final verdict after correction:** numerical reporting, alias accounting and the final narrative pass this consistency review. The coordinator corrected the mutable state, reference-read attribution, and main utility wording; these changes were read back and verified. No outstanding correction to the reviewed scientific results is requested. No correction to the closed scientific artifacts or aggregate report is needed. The source/model audit was left unchanged.

**Resolved review findings:**

1. The status behind the `RESULTS.md:72` “current state” link was stale. `STATE.json` now says `complete_independently_reviewed_development_run`. This resolves the discrepancy without modifying the frozen reference-read or closure receipts.
2. `RESULTS.md:17` now explicitly says the evaluator read the CHNS participant reference only after both authors closed. This resolves the earlier ambiguous grammatical attribution. The reference-read receipt is timestamped after closure and binds that closure.
3. `RESULTS.md:3` now calls the outcome “selective descriptive agreement” and explicitly disclaims formal equivalence; line 50 calls the marginal correlation “numerically similar.” The current-focus phrase “useful agreement” remains attached to the specific A age and B glucose relationships, immediately contrasted with the B adjusted-BMI failure and developmental limitations. In that bounded context it is an interpretation of observed scale agreement, not a claim that a formal utility threshold was passed. No arbitrary success or equivalence criterion should be added after seeing results. B's adjusted BMI failure against this particular reference is well supported and need not be softened into success.
4. The root report now states that the run started on 3 November and completed on 4 November 2026, America/Chicago, preserving the run directory's start-date label while acknowledging completion after local midnight.

**Numeric check:** all seven displayed non-intercept reference coefficients, their interval endpoints, and three-delivery minimum/maximum ranges round correctly at the precision used in `RESULTS.md`. All displayed marginal and correlation summaries also round correctly. The following higher-precision extract records the checks without changing the source report.

| Term | Reference estimate [95% interval] | Final generated range |
|---|---:|---:|
| A BMI | 0.0549460823 [0.0457262476, 0.0641659169] | 0.0244523601 to 0.0389367064 |
| A age | 0.0153037055 [0.0132208357, 0.0173865753] | 0.0133701706 to 0.0148326345 |
| A female | −0.0452956548 [−0.0897136906, −0.000877618946] | −0.0478108100 to −0.00765492602 |
| B BMI | 0.0224642214 [0.0152595128, 0.0296689299] | −0.00949166872 to −0.000984996216 |
| B glucose | 0.392908861 [0.361753942, 0.424063781] | 0.391640491 to 0.438704044 |
| B age | 0.00810703507 [0.00638703533, 0.00982703482] | 0.00152424615 to 0.00275122514 |
| B female | 0.0259890256 [−0.00776094724, 0.0597389985] | −0.0490732529 to −0.0145744340 |

All A female delivery intervals include zero. For B BMI, one generated interval is negative and two include zero, while the reference interval is positive. B female has the opposite point direction from the reference, but the reference interval includes zero; the narrative explicitly preserves that uncertainty. A age and B glucose have similar positive scales, without an equivalence test. Intercepts remain in the report, so the seven-term display is not a hidden exclusion of regression terms.

The B glucose–HbA1c Pearson range 0.655351076–0.699952586 versus 0.660968287 rounds to 0.655–0.700 versus 0.661. Spearman 0.491880943–0.520727630 versus 0.361457319 rounds to 0.492–0.521 versus 0.361. B glucose mean 5.49483053–5.52522553 versus 5.48776761 rounds to 5.495–5.525 versus 5.488 mmol/L. A HbA1c mean 5.79646402–5.81722115 versus 5.67531292 and SD 0.917764618–0.966988920 versus 0.953571419 round as displayed. B BMI mean 24.8349354–24.9789912 versus 23.6998884 rounds to 24.835–24.979 versus 23.700 kg/m².

**Counts and aliases:** `REPORT.json` contains 12 initial/final slots, six unique run IDs and six unique table hashes. All six final slots have `aliased_initial=true`, and each table hash equals its matched initial slot. Each unique delivery has 3,000 rows. Inventory and state metadata record four physical executions per request, totaling eight: two trials plus six deliveries. Therefore neither 12 slots nor six final aliases constitute additional physical tables. The reference has 6,631 common complete cases and 218 communities. Per-session retrieval totals are four queries and four paper downloads across the two authors, representing two distinct full papers, plus the abstract-only third study. The narrative does not conflate downloaded copies with independent studies.

**Scientific claims:** the report agrees with the source audit that all nine A and eight B declared source checks were unavailable; none establishes successful evidence calibration. The pre-freeze B tail correction is correctly attributed to coordinator review followed by author choice and is not mislabelled post-feedback revision. Both authors retained their initial frozen candidates; no improvement or revision gain is claimed. Source, model and transport uncertainty remain excluded from synthetic intervals; CHNS uncertainty is selected-sample clustered uncertainty, not population truth. The source/target context proposal is clearly future work. The report acknowledges supplied DOI seeds, host dispatch, coordinator-managed execution, missing target geography/era details, shared variable family, and confounding of author with request. These boundaries are consistent with the audit's “small developmental implementation study” verdict.

The current-focus additions preserve the same counts and conclusions. Prior-study counts in that document were outside this follow-up review and were not re-audited. Public-export intent is appropriately limited to reviewed authored code/specifications, metadata and aggregates; this textual review is not an audit of an assembled export bundle.

**Reviewed snapshots (SHA-256):**

- `RESULTS.md`, corrected version: `8aa203c75a8fd9012bb84829135a26b449423c56b237078f7bb69ad3cbc6b3cc`
- `evaluation/REPORT.json`: `f5565a6fb54072462f278b2a6b6f0d7ff343d91bd6e166048e8da65bab1f1c10`
- `docs/CURRENT_RESEARCH_FOCUS.md`: `27f9d37236905e06c4625884128b0889c7d9436569c7b41b6c2f6be5c66bc9db`
- `SOURCE_AND_MODEL_AUDIT.md`: `389bdd2ef04dc5b6b77febf2f66198df3de64df07efe472261782e7afd841549`
- `STATE.json`, corrected version: `c81418d9dcf66fb8e305ba82a6f2cb0603fa8156231d9401b2cc1601734d777c`
