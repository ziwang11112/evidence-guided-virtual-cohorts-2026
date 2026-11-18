# Delivery under the frozen reasoning and output budget

10 November 2026. This is a new explanatory report, outside the launch-frozen configuration. It authorizes no additional call, retry, continuation, parameter change, or scientific repair.

**The observed token-limit stops are delivery failures under this interface and budget configuration. They do not establish that a delivered scientific model was incorrect.** A construction without a complete accepted artifact remains in the original twenty-construction denominator; its downstream scientific adequacy is unavailable, rather than measured as a scientific error. Comparisons must report both construction delivery and scientific results among evaluable constructions.

## Current observations and their provenance

The root controller supplied the following observations while the batch was still running, using recorded stop reasons and public usage metadata. This note does not independently certify the entire batch; the closed-call audit will do that. No hidden reasoning text was opened or reproduced.

| Captured observation | Stop reason | Total output tokens | Thinking tokens | Nonthinking remainder | Interpretation |
|---|---|---:|---:|---:|---|
| Gemini 4 Carbon, each of the first two returned calls | `MAX_TOKENS` | 32,768 | 32,765 | 3 candidate tokens | Thinking consumed 99.9908% of the joint output budget; no complete scientific artifact was delivered. |
| Claude Fable 5.2, first PNS call | `max_tokens` | 32,768 | 30,166 | 2,602 | Output-cap truncation; thinking consumed approximately 92.06% of billed output. Scientific correctness is not assessable from the incomplete delivery. |
| Claude Fable 5.2, first LIPID call | `end_turn` | 32,724 | 20,233 | 12,491 | Complete returned artifact reported by the controller, despite high token use; executable and scientific adequacy still require the frozen downstream checks. |

For Claude, the thinking count comes from `usage.output_tokens_details.thinking_tokens`; total output remains the inclusive billing quantity. The remainder is arithmetic subtraction, not an independent tokenization of visible text. The frozen client preserves this field in `usage_raw`, although its generic normalized `reasoning` field is null. A postrun report can extract the public usage breakdown without changing any frozen file.

## What the official documentation establishes

Gemini's output cap includes thought tokens and is an infrastructure cutoff; it does not cause the model to reduce its chosen thinking allocation. Reaching it during reasoning can return `MAX_TOKENS` with empty or truncated text, while generated thinking tokens remain billable. `includeThoughts=false` controls the exposure of thought summaries; it does not disable thinking or reserve tokens for the answer. The current Developer API guide documents 32,768 tokens per nonstreaming `generateContent` segment and 65,536 per streaming segment. [Gemini GenerateContent thinking guide](https://aistudio.google.com/docs/thinking?generate-content=true&hl=en)

Google recommends `medium` as Carbon's default thinking level and notes that Carbon may devote more of the output limit to thinking than earlier models. Its guidance separates lowering thinking effort from raising the overall output allowance. Larger generations can use streaming or explicitly managed continuation, but that changes transport, call accounting, latency and cost. [What's new in Gemini 4 Carbon](https://aistudio.google.com/docs/whats-new-gemini-4-carbon)

Claude's `max_tokens` also caps thinking and response text together. Effort is a soft control, not a promised number of thought tokens. Anthropic explicitly identifies high effort as more likely to exhaust the budget and describes either lowering effort or increasing the cap as possible remedies. Its public usage breakdown exposes billed thinking tokens without requiring the thinking text. [Claude thinking steering and cost](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost)

Current Google documentation differs across services on the legacy `thinkingBudget` parameter: the Developer API page describes mapping a standalone value to a thinking level with a warning, while the Enterprise guide describes rejection. Both favor `thinkingLevel` for Gemini 4. Therefore a future protocol should not assume that a numeric `thinkingBudget` supplies an independent hard reasoning allowance. [Developer API thinking guide](https://aistudio.google.com/docs/thinking?generate-content=true&hl=en), [Enterprise Carbon guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/guides/gemini-4-carbon)

## Model identity and metadata

The controller reports an authenticated catalog entry with `outputTokenLimit=32768` and `version=3.0`, while the actual returned model ID is `gemini-4-carbon`. Preserve all three fields as returned. The output-limit number is compatible with the documented nonstreaming segment cap, but that does not explain or authenticate the catalog's version label. Its cause is unresolved. Do not silently correct the catalog, identify the call as a different model, or claim an unavailable immutable model snapshot.

## A separately registered next round

The current twenty constructions retain their original settings and outcomes. No truncated call is resent or continued in this unit.

A future engineering comparison could preregister Carbon `MEDIUM` with the current 32,768-token allowance as the first delivery configuration to assess. A distinct higher-compute configuration could assess `HIGH` with a 65,536-token streaming allowance or explicitly budgeted continuation. These are new configurations, not equivalent replacements for missing current results. If continuation is used, every segment must have an explicit reservation and call receipt; an SDK must not silently introduce uncounted continuation requests.

Assess complete-artifact delivery rate, public thinking/answer token allocation, elapsed time, and cost per delivered construction before making scientific-quality comparisons. Retain the same source-only evidence boundary and count all scheduled failures. Lowering effort may change the authored scientific law and is not guaranteed to preserve quality; that tradeoff requires the new comparison rather than inference from the present truncations.

Documentation was publicly fetched without credentials on 10 November 2026. Gemini GenerateContent thinking-page SHA256: `9d123e021546d5e91d26ec160de5c416b0bafc0ca20081886d3cf594b2b59e97`; Carbon release-guidance SHA256: `2a5898f508792d615a1f40f20ab34c6aa0737d3b2c124abd64a916068825a511`. These identify the fetched documentation text, not a provider model snapshot.

## Closed-batch audit addendum

The independent closed-call audit subsequently confirmed 20 initial calls, no repairs, fourteen accepted complete artifacts and six output-budget delivery failures. All four Gemini calls had the same 32,765 thinking / three candidate / 32,768 total token allocation. Both PNS Claude calls hit 32,768 total tokens, with thinking counts 30,166 and 27,935. Both LIPID Claude calls completed: thinking/total counts were 20,233/32,724 and 17,795/27,190. All actual requested and returned model IDs matched. These findings now come from the captured receipt/usage audit rather than only the earlier controller notification. The interpretation above is unchanged; no call was resent and no frozen configuration was modified.
