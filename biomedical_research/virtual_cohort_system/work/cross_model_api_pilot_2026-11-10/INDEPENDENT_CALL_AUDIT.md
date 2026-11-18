# Independent audit of the closed API batch

**PASS. No blocking capture, identity, budget, or candidate-binding issue was found.** The twenty construction outcomes can be sealed for the separately gated scientific execution. This pass does not assess scientific validity of the generated laws.

There were exactly **20 initial calls, zero repair calls, 14 complete accepted artifacts and six incomplete deliveries**. All scheduled constructions remain in the denominator. The six incomplete calls hit their combined output budget: all four Gemini calls and both PNS Claude calls. They are delivery failures with scientific correctness unavailable; they are not observed scientific-model errors.

| Configuration | Complete artifacts / scheduled constructions | Independently recomputed tariff estimate, USD |
|---|---:|---:|
| GPT-6 Astra | 4 / 4 | 3.25879200 |
| GPT-6.1 Sol | 4 / 4 | 0.57784120 |
| DeepSeek V4 Pro | 4 / 4 | 0.45008392 |
| Claude Fable 5.2 | 2 / 4 | 5.52179200 |
| Gemini 4 Carbon | 0 / 4 | 1.39848800 |
| **Total** | **14 / 20** | **11.20699712** |

Every call supplied usage sufficient for the frozen tariff computation; no unknown-usage reservation remains. Recomputed input, cached-read, cache-write and inclusive output costs agree with the receipts and construction ledger. Each predispatch reservation also agrees with an independent calculation. Provider totals remain below their respective ceilings. These figures are tariff estimates, not invoices; DeepSeek deliberately uses the conservative peak tariff.

The audit checked every actual request body, endpoint, requested model, native reasoning setting, output allowance and common system instruction against the frozen plan. Every returned model ID exactly matched its requested ID. The actual UTF-8 scientific prompt in every request body exactly matches its frozen case packet. No request adds tools, prior-response state or conversation context.

All twenty persisted `calls/.../prompt.txt` files use Windows newline encoding and therefore have different raw hashes from the LF packet files. Their receipt hashes correctly identify those persisted bytes. After newline decoding, they exactly match the submitted text. The machine-readable audit separately records the actual submitted-string SHA256; it is this hash that matches the frozen packet. This is a storage representation difference, not an input change or contamination.

For all fourteen accepted candidates, the generator bytes, scientific model specification, task wrapper, decision record and capture binding exactly match the selected API artifact. All captured file hashes checked against their receipts. Raw response bodies were hashed only; no hidden reasoning was interpreted or reproduced. The review did not load credentials, make provider calls, or execute any generated program.

The public usage fields show all four Gemini calls consumed 32,765 thinking tokens and three candidate tokens within a total cap of 32,768. PNS Claude thinking counts were 30,166 and 27,935, each within 32,768 total output tokens and both ending at `max_tokens`. The two completed LIPID Claude outputs used 20,233/32,724 and 17,795/27,190 thinking/total tokens. These fields establish allocation and stopping behavior; they do not reveal or prove the quality of the unreturned scientific construction. See [delivery budget interpretation](DELIVERY_BUDGET_NOTE.md).

The frozen Gemini catalog reports `version="3.0"`, `outputTokenLimit=32768` and model name `models/gemini-4-carbon`; all four actual responses identify `gemini-4-carbon`. The unexplained version label remains recorded without correction or substitution. Matching returned IDs do not establish an unavailable immutable internal model snapshot.

Machine-readable evidence: `INDEPENDENT_CALL_AUDIT.json`, SHA256 `6c3120178185d764a63cdc0c8276299bf5636d04421c7dff57b021439c93c3ae`. The report binds its auditor, run plan and construction-outcome hashes and retains every call, token allocation, cost and newline observation. Execution and scientific evaluation remain subject to their independent all-construction and all-execution closure gates.
