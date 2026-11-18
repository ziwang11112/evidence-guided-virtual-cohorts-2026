# Model selection and API-budget amendment

10 November 2026. **Planning amendment; no provider call has been made.** The user now reports about USD 200 of monthly OpenAI API credit and permits broader model use. This supersedes the earlier browser-only assumption for OpenAI and proposes expanding the unlaunched 12-slot pilot to 20 slots. It does not alter any frozen clinical experiment, claim that API credentials are configured, or authorize purchasing access to other providers. The user's actual remaining balance and billing-cycle expiry have not been inspected.

## Scientific purpose and model allocation

Keep the core question: can an Agent construct virtual biomedical data supporting requested analyses from fragmented published evidence? Cross-model choice behavior and cost explain the scope of this capability; they do not replace it with a generic model leaderboard.

| Configuration | Proposed role | Selection status |
|---|---|---|
| OpenAI GPT-6 Astra | High-capability OpenAI member of the four-provider comparison | Official model ID `gpt-6-astra` verified; account availability, returned identity, settings and snapshot not yet verified |
| OpenAI GPT-6.1 Sol | Within-OpenAI capability/cost comparison and possible repeated-run workhorse | Official model ID `gpt-6.1-sol` verified; account availability and exact runtime not yet verified |
| DeepSeek | One independent provider configuration | Official catalog has V4 Pro and V4.1 Flash; choose one available configuration before any pilot responses |
| Claude | One independent provider configuration | Official current catalog verified; choose one available configuration before responses, not after judging pilot outputs |
| Gemini | One independent provider configuration | Official model catalog retrieved; exact available account model remains to be frozen |

Do not call these five independent model families: there are four provider families, and one additional OpenAI configuration. With one principal model per provider, provider, model and configuration remain confounded. Their performance on this biomedical task is unknown until evaluated. More repeats from OpenAI cannot substitute for independent provider coverage.

## Two distinct comparisons

1. **Provider-balanced primary block:** PNS and lipids × one selected model from each of four providers × two fresh contexts = 16 constructions.
2. **OpenAI configuration block:** the same two cases × GPT-6.1 Sol × two fresh contexts = 4 further constructions. Compare with the primary OpenAI configuration, without overweighting OpenAI in the four-provider summary.

Total first-stage ceiling: **20 constructions**. Identical case packets, no desired target numbers, same scientific freedom, complete initial response retention, all failures counted, and at most one mechanical repair per slot remain in force. The previous pilot's schema-only execution and no-clinical-reference-feedback boundaries also remain. Numerical residual/latent/rank correlations must not be pooled unless they are genuinely the same operator on the same scale and conditioning set.

Before launch, stage and independently inspect the two case payloads, freeze their hashes, verify actual provider access and capture model/configuration/request/response/usage metadata. Prefer comparable API execution for a quantitative cross-model study. If other providers are available only through existing wang Chrome web accounts, preserve those as a separately labelled interface exploration: API versus web interfaces differ in hidden prompts, tools and compute. Do not present a mixed-interface result as an isolated model effect. No credentials belong in chat, prompts, public GitHub or result artifacts.

## Budget

User-reported OpenAI monthly allowance: **USD 200**, not a checked account balance. Proposed project ceilings: **USD 20 for the first-stage OpenAI calls**, and **USD 100 cumulative for a later expanded study**, leaving headroom for other work and unexpected context/reasoning usage. These are controller limits to implement, not assertions of an existing platform hard cap. Before each request reserve its conservative maximum cost, including accumulated input, billed output/reasoning, tool charges and any permitted repair. Stop before dispatch when it would exceed the remaining project allowance. Record incurred failures and retries as costs. Do not enable auto-recharge.

Official standard short-context text rates checked today, per million tokens:

| OpenAI model | Input USD | Output USD |
|---|---:|---:|
| GPT-6 Astra | 10 | 50 |
| GPT-6.1 Sol | 2 | 10 |

Illustration only: if one complete construction consumes 100,000 total uncached input tokens and 20,000 billed output tokens, the corresponding text costs are USD 2.00 and USD 0.40. These are not measured run costs or per-construction guarantees. Do not ignore reasoning tokens, repeated context, tools, tier changes or longer-context pricing. Eight OpenAI pilot constructions at those hypothetical totals cost USD 9.60 before such extras. Measure actual usage before increasing the run count.

The OpenAI credit cannot pay DeepSeek, Anthropic or Google bills. Existing authorized access may be used; a separate metered budget must be established if paid non-OpenAI APIs are needed. No such new paid-provider commitment is made here.

Official OpenAI documentation currently lists USD 200 monthly credits for eligible Pro USD 200 subscriptions, after activation and organization linkage. Credits expire at the billing-cycle end. The benefit covers eligible API Platform usage and does not cover Codex use through API keys; use the scientific experiment's API client rather than assuming that a Codex CLI run spends this grant.

## What justifies more runs

The first stage tests complete artifact capture, traceable scientific decisions and execution. An operational expansion criterion is at least 17/20 complete traceable executable submissions and at least one success in every case-by-configuration cell, together with a coding process that can distinguish compatible and incompatible parameter meanings. This is not an accuracy or convergence threshold. Disagreement between models is as informative as agreement; do not expand only when results look favorable.

A possible larger design is three existing tasks × five configurations × five fresh contexts = **75 cumulative constructions**, not 75 extra. The third task should be selected and its packet frozen before inspecting pilot outcomes if the initial 20 are to be included unchanged. Iron status is a candidate because it contributes joint threshold evidence rather than another adjusted linear regression; its packet is not staged or admitted by this document. If prompts, models or execution rules change after the pilot, treat the later version separately rather than silently pooling results.

The larger scientific evaluation must freeze requested analysis estimands, diagnostics, references, exposure status and output seeds before generation. Report scientific effect sizes and uncertainty alongside feasibility, selected assumptions and billed cost. Multiple draws from one frozen law are nested Monte Carlo repetitions, not independent authors or new clinical cohorts. Existing exposed references support developmental comparisons; no new independent clinical validation is created by adding models. An analysis-support card remains an unvalidated proposal.

## Immediate next work

Implement a small provider adapter with exact prompt/response and usage capture for the OpenAI path, using an existing securely configured API key if available. Validate the adapter on offline fixtures before spending credits. Stage the two blinded evidence packets, verify the four providers' actual access, then freeze the execution manifest and first-stage budget. No new agent collaboration layer, training or extra dataset search is needed for this step.

The current v0.28 manuscript remains unchanged; none of these prospective comparisons is a reported result. The old 12-slot files remain as superseded protocol history. Independent read-only design review recommended the 16+4 split and separate provider/configuration interpretations.

## Verified official sources

- [OpenAI model catalog](https://developers.openai.com/api/docs/models)
- [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)
- [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
- [OpenAI pricing](https://developers.openai.com/api/docs/pricing)
- [API credits for ChatGPT subscribers](https://developers.openai.com/api/docs/guides/chatgpt-api-credits)
- [DeepSeek models and pricing](https://api-docs.deepseek.com/quick_start/pricing/)
- [Claude current models](https://platform.claude.com/docs/en/models/overview)
- [Gemini model catalog](https://ai.google.dev/gemini-api/docs/models) (redirected to AI Studio; direct HTML retrieval was used after the web reader failed)
