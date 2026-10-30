# M15-B1 final release review

30 October 2026. **PASS: release the two frozen, byte-identical candidates to the single planned target-analysis pass.** This is a release/provenance decision, not a finding that the generated data are scientifically accurate. The final decision is retention after one source-feedback pass; it makes no improvement claim.

## Review boundary

Reviewed final decision, checks, revision record, both freeze receipts, actual source-feedback receipt and copied feedback, audit bindings, initial direct-validation receipt, prelaunch commitments and unchanged evaluator/controller hashes. Reused the completed source extraction and evaluator audits; no test suite was rerun. Generated CSV files were accessed only as bytes for identity/hash checks, without parsing, printing or inspecting row values. No real-reference file, raw measured outcomes or target-analysis results were opened, hashed or calculated by this reviewer.

## Completed checks

| Check | Result |
|---|---|
| Initial freeze receipt hash | Matches the expected frozen initial receipt |
| Final freeze receipt hash | Matches the expected frozen final receipt |
| Initial frozen commitments | All 33 file hashes match |
| Final frozen commitments | All 37 file hashes match |
| Frozen candidate file sets | Both exactly match their receipt lists; no extra candidate file found |
| Registry snapshots | Both match the canonical JSON hash of the committed 19-entry prefix |
| Prelaunch inputs | All 13 file hashes match, including protocol, observed covariates, task, gateway configuration and original seeds |
| Original source-registry prefix | Initial four admitted artifacts remain unchanged |
| Final artifact references | All nine `checks.json` artifact bindings match actual audit files |
| Scientific retention | `generated.csv`, `model_spec.json`, `evidence.json`, `source_checks.json` are byte-identical between initial and final |
| Ancestry | Final names the exact initial freeze as parent; revision index 1 and `kind=retain`; embedded revision equals `revision_record.json` |
| Actual feedback provenance | Final copied feedback is byte-identical to `visible/feedback/initial_feedback.json` |
| Feedback bindings | Parent freeze, generated table, prelaunch receipt and all three scientific input hashes match the current frozen files |
| Feedback scope/count | One reserved/completed source-only pass, slot 1; 12 approximate numeric diagnostics plus one not-computable comparison |
| Direct authorship validation receipt | Success, `generated.csv` route, `direct_rows_validation` backend, `generator_executed=false`; all seven execution-file hashes match |
| Audited implementation | Controller, source-statistic engine and target evaluator hashes remain unchanged |

The registry snapshot uses the lifecycle's documented canonical serialization of the artifact prefix, rather than the raw `registry.json` file bytes. An initial raw-file comparison was therefore not the applicable check; independently recomputing the canonical prefix gives the expected hash for both freezes. There is no remaining registry discrepancy.

Observed-covariate preservation remains bound through the unchanged prelaunch observed hash, previously audited structural receipt, initial direct-validation inputs and zero-change retention. This release audit did not reread individual covariates or outcomes to repeat that check.

## Scientific interpretation of retention

The final decision accurately reports the actual source feedback. It retains the noticeably larger native Sun BMI-on-urate slopes in three groups rather than declaring those discrepancies resolved. Population composition, selection and residual assumptions are possible explanations, not demonstrated quantitative explanations. No new fit threshold, synthetic source population, reciprocal regression conversion or source-swapping rule was introduced.

The marginal source comparisons are not independent validation. Age guides, the BMI hinge, sex-slope assumption and conditional residual scales remain disclosed construction choices. The exact adjusted standardized comparison and menopause-defined comparisons remain unavailable. Consequently, neither reasonable-looking marginal moments nor the retained positive source relationships establish correctness of those untested features.

There were **zero changed outcome cells, zero changed scientific assumptions and zero newly adopted sources after feedback**. Initial and final are the same scientific candidate, so any target analysis must produce identical point estimates under the same analysis code. It cannot demonstrate feedback-driven improvement, collaboration benefit or a successful corrective revision. It can provide one evaluation of the literature-enabled direct-enrichment candidate against the locked real-reference analyses. Source discrepancies and any target failures must remain reportable.

## Final bindings

| Object | SHA-256 |
|---|---|
| Initial freeze | `558effb25a1ede3ef7b514a5e0c028b4185881a80466451c4dd0a441a5499a1b` |
| Final freeze | `1cd0da713677689509cbdcd8bc8c44bf12bb69a2eaf3c081c66f9cf1f7e24a4e` |
| Generated CSV, initial and final | `69b01e7ec84cef431da50d394040edfe661413c5541130b8960490c541607b42` |
| Model specification, initial and final | `40e6cf9be459c5b2092b1895a9c337d2c55b46aa6eeed31bf04d8551b93b7344` |
| Evidence, initial and final | `8956bfd491b9c9a9e9f39c90e276a6e647c1393c289e0a9307f062a9f0f8c69c` |
| Native source recipe, initial and final | `e07f838008dac6405fb9325beb236d4a5ee14b5aadf44e9aff15bab504cb6aa3` |
| Actual source feedback and copied feedback | `ecbec8ea6c1a3befde336021fca843c65c2117c4c70dcfe23c28028e50090e64` |
| Final decision | `259c066e4383ada6b721677dc91bcc9c299ba077692b3fada37ce2ac3297e746` |
| Final checks | `8f26e696b8814d5e1f6d986ab773d8f0b432056b11367c2677ae9ead4db69f98` |
| Final revision record | `025eb8971141aae160709450cd1a1d131fc6b9916f235dab6890ec532b660ee3` |
| Prelaunch commitment | `c0f7a7fb0396187f246d03b262243deccd5e708adff1102cbf8ac0b94f2089da` |
| Target evaluator | `4181cfbd8ae37df58699558196ca241f2bd60e4d895b9a18de40a42cbaffce12` |

The target-reference hash already committed before builder research is `0151191d1cf76c7096ca598687b7eb569a18f789627bee1e5676f92a35187ba3`. The existing evaluator release manifest must retain this value; its gate performs the actual reference-byte check before reading measured values. This review authorizes the already planned bounded evaluation, without changing its 24 estimands, finite-cohort interpretation or PSU sensitivity analysis. No further candidate revision is authorized by seeing those results, and no extra source search, parameter adjustment or analysis selection was performed in this review.

**Release status: PASS. No unresolved blocking issue.**
