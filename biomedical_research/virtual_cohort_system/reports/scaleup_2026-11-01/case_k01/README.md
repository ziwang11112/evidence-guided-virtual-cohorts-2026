# K01: whole-cohort glucose generation for scientific analyses

2 November 2026. **K01 now has prospective scientific admission and a fixed reviewed design; clinical execution remains unreleased.** The [decision](CONTRACT_DECISION_2026-11-02.md), [independent contract review](CONTRACT_INDEPENDENT_REVIEW.md) and [byte commitment](REVIEWED_DESIGN_COMMITMENT.json) supersede the earlier preparation-only status. The task is whole-cohort generation without target participant inputs. Necessary pure components passed invented-input verification; actual Agent scientific models, clinical source fitting, generation and target-effect evaluation have not run.

The evidence discussion below records the preceding source-review checkpoint. Its scientific limitations remain; its call for completing the case design has now been resolved by the linked contract.

## The scientific question

Can one Agent-authored joint generator, informed by external study summaries and an explicit target measurement/population description, produce a whole virtual cohort that supports three useful analyses of measured glycemia? The proposed release contains age, sex, BMI and protocol-relative point-of-care glucose. The same table must support the age/sex-adjusted BMI contrast, the BMI/sex-adjusted age contrast, and the Female-minus-Male difference in the BMI contrast. See the [scientific-use proposal](SCIENTIFIC_USE_PROPOSAL.md).

This tests an actual data gap: there are no individual target inputs. It does not test recovery of individual measurements, identify a causal mechanism, or establish that synthetic patients replace measured evidence. The reference will be a prospectively defined subset of released cleaned measurements, not known population truth.

## What the source review changed

The [two-study review](evidence/SOURCE_REVIEW_2026-11-02.md) produced [27 candidate records](evidence/CANDIDATE_EVIDENCE.json). Ayele supplies covariate margins and categorical composite-diabetes odds ratios. Bahendeka remains abstract-only, with weighted prevalence and age summaries. Neither verified source supplies the continuous-glucose scale or the three adjusted coefficients. The diabetes odds ratios cannot be converted into continuous-glucose slopes.

An existing, audited MIND-China source supplies age, BMI and fasting-serum-glucose mean/individual-SD pairs plus a female count. Its [new K01 reuse view](evidence/MIND_REUSE.md) preserves those facts while replacing the old CHNS applicability discussion. Fasting serum and pooled HAALSI capillary POC measurements are different. Shared mmol/L units do not remove the measurement and population transport assumptions.

The [independent design review](INDEPENDENT_DESIGN_REVIEW.md) supports a bounded assumption-labelled test. All three proposed target relationships remain joint-assumption dependent, even with MIND. This is a limitation to test, not a reason to prescribe zero effects or supply the expected target signs.

## Coordinator decision at this checkpoint

Continue K01 preparation using this finite evidence basis. Do not open another original study merely to seek the missing target-like slopes. MIND is a candidate continuous-scale source context; Ayele's covariate margins are candidate additional source-context information. Composite-diabetes ORs, abstract-only prevalence and unrelated HbA1c quantities are not executable checks for this four-variable request. No item is activated by this decision.

Keep evidence-role and applicability labels separate: a mean can be directly reported for its source while its use for HAALSI still depends on an unvalidated transport assumption. Individual SD is neither estimator SE nor conditional residual SD. Multiple summaries from one study are not independent clinical replications. A common generation model must declare shared structure and context changes; unrelated source-specific models hidden behind one file would not demonstrate transfer.

The next work is a complete, outcome-blind case contract, using existing reviewed machinery:

1. Fix the exact source items, source populations, descriptive diagnostic operators and any explicit approximation permissions. Preserve unavailable checks and source uncertainty.
2. Fix the target recorded-value eligibility and documented sentinel policy, without range trimming or selection based on unseen clinical values.
3. Specify one transparent same-information statistical reference and a finite source-attempt schedule. The five fresh Agent constructors own their scientific structure and transport assumptions; the coordinator supplies no desired effects.
4. Bind the three estimators, failure rules, discrepancy-resolution grid and all-use/all-seed continuation rule. Independently review and freeze the complete Wave A contract before clinical execution or any reference disclosure.

Keep the existing campaign ceiling: five Agent constructors plus one statistical reference, initial and at most one source-feedback decision, three target seeds and 5,000 rows per new table, at most 36 target slots for K01. Retained finals alias initial artifacts. K02 remains a qualified context-exposed case; only independently admitted K01 success under the fixed rule can support positive Wave B continuation. No additional clinical run is authorized by this preparation note.

## Review and resource boundaries

Ayele's source extraction used the full rendered primary article. The independent reviewer checked the retained primary excerpts because its own browser reopening was gated; this is not a second independently authenticated retrieval. Bahendeka is abstract-only. MIND reuses previous local source audits; no new MIND original-read slot is consumed. Full third-party text, codebooks, participant tables and contact details remain local.

This unit consumes two new original-study review slots, bringing campaign use to five of twelve. Target-family use remains four of six. A failed 1,817-byte HTML response is recorded once, despite two local copies. No new clinical table, target-effect estimate, generator, software test or scheduled execution is counted. The [preparation verification](PREPARATION_VERIFICATION.json) binds the reviewed artifacts and checks that 29 protected K02 files and five historical MIND input files remain unchanged.
