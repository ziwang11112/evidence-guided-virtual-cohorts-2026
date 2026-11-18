# Implementation review and decision — 2026-11-16

The bounded pilot completed successfully. The six authors with complete evidence constructed data that reproduce the two derived primary relations and the secondary analyses. All 24 authors distinguished identified analyses from chosen scenarios in their submitted decision records. This is positive evidence for composition capability under explicit, compatible statistical inputs.

## What was actually implemented

The new `pilot.py` connects the existing `provider_client.py` to the existing WSL/bubblewrap command adapter and trusted worker. It adds task-specific artifact interfaces, immutable input/program/call seals, a 24-call budget, and separate construction/execution/analysis closures. It does not replace the model with a host-written scientific generator. Each saved `generator.py` and model parameter object is byte/value matched to the corresponding API artifact.

The 24 author contexts receive only their frozen artificial records, the requested analyses and a generic executable-output schema. No expected partial correlation, change correlation, host witness covariance, hidden data or other author output is inserted into the prompt. Values derivable from the authorized evidence are legitimately available for the author to calculate. No model tools are attached; this is a controlled composition diagnostic, not an autonomous retrieval evaluation. There were no repair calls, scientific feedback messages, retries, hand-fixed parameters or extra authors.

The API client uses `gpt-6.1-sol`, high reasoning, standard/default service, with a 16,384 output-token ceiling. Every response returned the requested identifier. The API does not expose an additional immutable model snapshot here; the exact request/returned identifier, timestamp, request id, output and usage are recorded, without claiming unavailable backend reproducibility. Calls use separate contexts; cached input tokens do not represent shared author conversation state.

All 24 author artifacts were sealed before the first experimental generation. Every program runs only inside the existing Linux namespace: read-only code/spec/task, cleared environment, no mounted host drives/home, no network routes, limited memory/CPU/output/log sizes. All 72 worker receipts and staged hashes were verified. A sandbox-access restriction initially blocked the trusted runtime probe; using the authorized WSL access path resolved it before any API dispatch. No unrestricted execution fallback was used.

## What Agent code does

All 24 authors chose finite-moment Gaussian constructions. Six adjusted-family authors used a covariance matrix; the other six used equivalent latent-factor constructions. Longitudinal authors separated stable person components from visit deviations and sampled them independently under the supplied measurement-model assumptions. Every covariance law was positive definite. The author-declared analysis values agree with the separately reconstructed program-law values to at most 1.67e-16.

Full generator programs and requested-estimand records were inspected. There is no post-sampling covariance forcing, selected random seed, outcome-based rejection or positivity clipping in these programs. The host does not execute author code to inspect it; inspection uses source text/AST and independent algebra.

These choices are mathematically appropriate for this moment-based exercise. Gaussian shapes remain unverified assumptions; no claim about clinical tails, bounds or nonlinear biology is implied.

## Why the primary result matters

In the adjusted task, source A gives marginal X–Y correlation .5; source B supplies the two covariate relationships .6 and .6. Combining them identifies the residual correlation .21875. Each complete-evidence author independently chose the required covariance law, and generated-data author means range .2211–.2230. Mean absolute error across the nine final draws is .00731.

In the repeated-measure task, both supplied correlations are positive: stable-component correlation .8 and same-visit correlation .52. With stable variance 4 and visit-deviation variance 1, the implied correlation of changes is negative, -.6. All three complete-evidence authors derived this decomposition and implemented it. Generated-data author means range -.6013–-.5991; mean absolute error across nine draws is .01492. This example demonstrates composition rather than copying one input correlation into every analysis.

The incomplete conditions also satisfy their supplied constraints. Their primary relations remain assumptions, so their separation from the complete-evidence result is not scored as a mistaken recovery. For example, A-only longitudinal authors all chose a positive .3 deviation correlation. That choice is consistent with A-only information; it becomes incompatible when the additional same-visit evidence is supplied. Complete-evidence authors resolve it correctly.

All 90 identified primary/secondary analysis estimates fall within the preregistered .08 numerical tolerance. All 738 source diagnostics fall within their fixed numerical tolerances. These are repeated numerical checks, not 90 independent clinical conclusions or formal statistical coverage. All 72 identification labels are correct for these two tasks under the explicit identification instruction in the prompt.

## Audit limitations and provenance detail

The 72 saved outputs contain 57 distinct numeric tables after removing cosmetic person identifiers. Repeated authors sometimes chose the same law and implementation, and the common seed schedule then produced identical values. Results are therefore reported by 24 author constructions with three nested draws, not by 72 independent datasets. Even the 24 constructions do not establish population-wide performance: there are only two mathematical task templates and one model.

The covariance-based evaluator independently recomputed 216 table analyses, with maximum discrepancy 1.17e-15. This is an alternative implementation by the same root assistant, not a blinded human or independent external review. The code-level law reconstruction is a postrun diagnostic, not a new preregistered endpoint or proof that every possible distribution is supported.

All 200 provenance entries reference only visible record IDs. Their `REPORTED/DERIVED/ASSUMED` labels describe computational origin, not sufficient scientific support on their own. For example, `adjusted_bridge_only_1` marks marginal XY=.52 as DERIVED while correctly stating that it depends on an assumed residual correlation .25. `longitudinal_bridge_only_2` derives stable covariance 2.0 only after choosing deviation covariance .6. These are transparent conditional derivations, not evidence-only identification. The requested-estimand records correctly call them scenarios.

One future implementation rule follows directly: propagate assumption dependencies into each analysis-use label; never map all DERIVED parameters to evidence-supported analyses. A change to that metadata rule does not require changing today's frozen generators or rerunning these results.

## Cost and completeness

- 24 API calls, 24 completed sealed author programs, 72 successful final executions; zero failed or repaired authors.
- 29,640 input tokens, including 17,099 cached; 62,105 output tokens, including 24,315 reported reasoning tokens. No private reasoning transcript is requested or analyzed.
- Published-tariff estimate $0.6540764; no unresolved charged-call reservations. The $6 cap and worst-case schedule reservation $4.55022 were fixed before dispatch.
- Pricing verified against the [official model page](https://developers.openai.com/api/docs/models/gpt-6.1-sol). These are usage-derived estimates, not an invoice.
- Frozen inputs, model request, raw outputs, usage, costs, source provenance, executable code, isolated-run logs and all unfavorable/partial conditions are retained locally. No new patient-data download or real-patient refit occurred.

## Decision

Close this 24-construction unit. Retain the positive result as a controlled mechanism/capability result within the virtual-data mainline. It weakens a blanket interpretation that these Agents can only copy source numbers or cannot combine relationships. It does not explain all historical clinical discrepancies, establish superiority over another system, validate calibrated confidence scores or prove general clinical utility.

The focused next step should use one existing biomedical analysis task to specify the exact missing joint/conditional quantity, inspect whether compatible external evidence can supply it, and preserve the distinction between evidence-derived and assumption-derived relations. Only after that source-admission check should a new real-case generation comparison be frozen. Do not automatically expand models, new datasets or large reviewer-driven evidence-harm studies. The current positive controlled result is not a reason to tune exposed target data.
