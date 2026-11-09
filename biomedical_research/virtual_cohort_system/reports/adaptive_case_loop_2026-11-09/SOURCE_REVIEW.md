# Initial candidate source review

**No blocking selected-source extraction or unit error identified.** Review was outcome-blind: no target payloads, generated clinical results or old candidate results were read, and no generator was executed. Scientific model choices remain with the author.

The audit matched **34 numerical claims**: 12 Greiner geometric-mean/age summaries, 10 Agongo arithmetic mean/SD claims, six Ashanti Spearman correlations, and six newly retrieved East African HDL category contrasts. Reported CI endpoints were checked where present. One additional contextual item records the source's sex-association inconsistency. No numerical or CI mismatch was found.

| Source | Version reviewed | Primary or curator artifact SHA-256 |
|---|---|---|
| PMC4457529 / DOI 10.1371/journal.pone.0129494 | Retrieved PMC version 1; Table 7 and methods | `e17360ed956a02bd96e22d832cbda3356d2f755f6038543cbf98953095519cf8` |
| PMC6897412 / DOI 10.1371/journal.pone.0223189 | Retrieved PMC version 1; Table 4 and methods | `416aa5fbea8f3b2c79a409230f55310d9bdbe072b8bcd9d11710bd89e834830e` |
| greiner_2021 / DOI 10.1136/bmjgh-2021-005222 | Admitted curator extraction; primary full-text version unspecified | `dd111f6d64daf9e7fad86f20b6a5a54142c3af1709b95ebab265344b0ee50ba5` |
| agongo_2018_navrongo / DOI 10.1371/journal.pone.0206326 | Admitted curator extraction; primary full-text version unspecified | `e783bdc1a4d05800f5393636aff57dd58e161388a56286087d43888388b15851` |

The earlier Obirikorang curator extraction was also checked against the retrieved primary table. It is the same publication as PMC4457529, not another independent study. [SOURCE_REVIEW.json](SOURCE_REVIEW.json) records all source XML/text/metadata hashes, that curator hash, and the nine-file initial-candidate inventory.

All **34 source-semantic checks remain not computable**: six unsupported geometric means, 22 statistics with unresolved definitions/weighting, and six adjusted categorical contrasts requiring unavailable source design/covariates. Evidence/recipe hashes in the sidecar match the current files. These statuses do not prevent separate, properly labeled own-law or generated-only diagnostics; they do prevent claiming a computed v1 discrepancy or source-population replay.

The new East African source explicitly distinguishes survey-weighted marginal summaries from unweighted regressions. Its selected HDL BMI effects are category contrasts, not continuous BMI slopes. Nonfasting serum collection is confirmed. Its Table 4 female HDL coefficient is +0.08 mmol/L (95% CI 0.05–0.11), while the prose states lower HDL for females. The candidate records the conflict and does not use it as a sex coefficient.

The reviewer requested one wording qualification: stratum and sex are the known minimum adjustment for the reported age contrasts, while the full reported age-row adjustment set remains unresolved. The author added that qualification, and it is present in the current bound evidence. The review did not prescribe model values. The assumed-law TC slope and residual-correlation derivations were independently reproduced to floating-point precision; that checks bookkeeping, not transfer validity.

Remaining assumptions include population and assay transport; demographic composition and age tails; conditional use of marginal rank relationships; cross-source CV transfer; and reuse of total variation as conditional residual variation. Source confidence intervals remain estimate uncertainty. No matched source population, validated target relationship or clinical precision is established.

This receipt captures the now-frozen initial state after the wording qualification: evidence hash `e8ba39379bd724e8b4e9f93220468ff9794e8437551f3223e16fd37a47136e61`, freeze hash `08ec4395b2e680792957bd20d7aad822f988170d0885d4438e8623b74e5947c7`. No earlier prequalification draft hash is inferred. The JSON distinguishes content-reviewed files from other inventory bindings. Later source-claim changes are outside this receipt.

