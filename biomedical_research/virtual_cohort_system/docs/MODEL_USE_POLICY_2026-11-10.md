# Model-use policy after the first API pilot

The user's latest preference is to concentrate expensive model use on GPT and reduce routine cross-provider spending. Adopt **GPT-6.1 Sol for repeated development, GPT-6 Astra for a small high-capability reference subset, and DeepSeek V4 Pro for inexpensive external comparison**. Fable 5.2 and the current Carbon HIGH configuration leave the default future roster. Cheaper Claude/Gemini configurations can be selected later; no replacement model or paid call is introduced by this amendment.

The completed first twenty calls and their frozen files remain unchanged. Their scientific outcomes and failures remain part of the record. This is a prospective resource decision, not retrospective removal of unfavorable results or a claim of general model superiority.

## Empirical basis

Usage-derived published-tariff estimates from the completed pilot:

| Model | Mean cost per initial call | Cost per delivered construction, including failed-call spending | Delivered |
|---|---:|---:|---:|
| GPT-6.1 Sol | USD0.1444603 | USD0.1444603 | 4/4 |
| GPT-6 Astra | USD0.814698 | USD0.814698 | 4/4 |
| DeepSeek V4 Pro | USD0.11252098 | USD0.11252098 | 4/4 |
| Claude Fable 5.2 | USD1.380448 | USD2.760896 | 2/4 |
| Gemini 4 Carbon | USD0.349622 | unavailable | 0/4 |

Fable accounted for 49.27% of the USD11.20699712 pilot estimate. Sol cost 82.27% less per attempt than Astra in this small run. These are task/configuration-dependent observations, not guaranteed future prices, equivalent computation, or scientific rankings. The source is [the captured cost ledger](../work/cross_model_api_pilot_2026-11-10/PILOT_COSTS.json), independently recomputed in [the call audit](../work/cross_model_api_pilot_2026-11-10/INDEPENDENT_CALL_AUDIT.md).

The [official OpenAI comparison](https://developers.openai.com/api/docs/models/compare?model=gpt-6-astra&model=gpt-6.1-sol), fetched 10 November 2026, also lists lower standard short-context rates for Sol: USD2 input/USD10 output per million tokens, versus Astra's USD10/USD50. Actual request estimates additionally account for billed reasoning and cache behavior. The user's reported monthly OpenAI credit remains an account resource to verify at billing, not a guarantee of free or unlimited calls.

## Bounded next-run option

One small development option is twelve constructions: eight Sol, two Astra, and two DeepSeek, split as4/1/1 across each of two cases. Using the prior observed means gives about USD3.01 before changed context, effort, caching or repairs. A proposed USD10 batch ceiling would be enforced by the next launcher before each dispatch. **No such batch is frozen or started here.** Its scientific question must be specified first; an unequal allocation must not be presented as a balanced provider comparison.

For a future formal model comparison, use a shared, prospectively selected subset with equal replication, and keep additional Sol development repeats separate. Do not allocate further authors after seeing favorable target results. Neither two GPT configurations nor two fresh conversations count as independent model-training families.

Generating additional predefined draws from an already frozen program requires local statistical sampling, not another language-model call. Reuse that separation to conserve API budget without confusing extra synthetic rows with extra scientific evidence. Future launches must explicitly consume the [machine-readable policy](MODEL_USE_POLICY_2026-11-10.json); the completed pilot launcher is historical and is not altered into a new runner.
