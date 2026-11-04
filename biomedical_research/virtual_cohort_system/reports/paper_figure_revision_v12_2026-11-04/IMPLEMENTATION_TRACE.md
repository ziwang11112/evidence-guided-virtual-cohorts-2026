# Concrete implementation trace for the v12 framework figure

Independent read-only audit, 4 November 2026. **Pass for this factual trace with the scope below.** This follows the latest reviewed-evidence sex-stratified copula construction only. It does not combine it with the older CHNS E1 A01 projection example. No participant or generated row was opened, no generator was executed, and no fit or parameter revision was performed. Machine-readable pointers, exact evidence records and SHA256 bindings are in `IMPLEMENTATION_TRACE.json`.

## One real chain to depict

1. **Visible research request:** generate 3,000 entirely virtual Chinese adults aged 35–74 for `hba1c ~ 1 + bmi + glucose + age + female`, also `hba1c ~ 1 + bmi + age + female`. No individual observations, target distributions or expected signs enter. The target is a selected analytical population, not national representation. The actual source is `evcBuild01/request.json`.
2. **Acquire and qualify:** the preceding fresh acquisition Agent, `evcGap01`, used 10 combined queries and selected five original studies without a preset bibliography. Its actual interface is `cohort_harness.literature`, plus permitted primary-publisher web access. `evcGap01/reports/SEARCH_LOG.json` and `EVIDENCE_CANDIDATES.json` record acquisition; the independently reviewed packet is copied and admitted by `evcBuild01/SOURCE_ADMISSION.json`. Four originals are gateway artifacts; LifeLines is a separately admitted partial publisher rendering. The new constructor uses that closed packet and has **zero new retrieval queries**, not a pretend online search inside the sampler.
3. **Author scientific objects:** the fresh constructor writes `candidates/initial/evidence.json`, `model_spec.json`, `generator.py`, `source_semantics_v1.json`, `whole_cohort_feedback.json` and its decision/check records. It chooses a sex-stratified Gaussian copula, bounded integer age and positive lognormal/shifted-lognormal margins. Actual mathematical assembly is in `drafts/assemble_initial.py`, especially `pos_law`, `group_law`, `age_cov`, `continuous_cov` and `pooled_projection`. The controller did not supply the law or target coefficients.
4. **Execute and check:** `run_session.freeze()` calls `semantic_feedback_v1.preflight()` and the lifecycle freeze/verification. `run_session.run()` invokes `execution.run_candidate(...)`, verifies the receipt, then calls `semantic_feedback_v1.collect_feedback(bundle, relative, run_id, feedback_id)` and `diagnostics.diagnose_csv(table, key)`. These deterministic tools execute and measure an authored model; they are not the scientific author. WSL/bubblewrap isolates the generator process, not all Agent tools.
5. **Review and retain:** four actual executions (trial 7400; delivery 7401–7403), each with 34 source-check records: **11 approximate comparisons and 23 unavailable**. `FINAL_DECISION.json` records `retain`, zero revisions and the unchanged candidate. Three final slots alias the three initial deliveries. There is no extra final draw and no demonstrated revision gain.
6. **Analyze data:** each delivered CSV has six columns: identifier, age, female, BMI, HbA1c and glucose. Standard regressions use it after closure; the external reference comparison reads pinned, already exposed CHNS aggregate results, not new participants. This is one developmental workflow case, not an untouched confirmation or controlled estimate of search benefit.

## Concrete source → parameter → sampler example

Evidence object `Hainan_male_HG_spearman` identifies Li et al., PMC7960723 / DOI 10.1038/s41598-021-85581-z, Results Fig. 1A prose and Methods. It stores variables HbA1c and glucose; **unadjusted, within-male Spearman rho = 0.44**; unit 1; adjustment set empty; sampling CI/SE not reported; source population and measurement qualifications. Female rho is 0.50. These are neither raw Pearson correlations nor adjusted regression coefficients.

The Agent-authored `group_law()` implements this exact line (assembler line 125):

```python
gh=2*math.sin(math.pi*d['rho']/6)
```

It gives male latent correlation **0.45670174022131144** and female **0.5176380902050415**, exactly matching `model_spec.parameters.sex_models.<sex>.latent_correlation[2][3]`. The vector order is `[age, bmi, glucose, hba1c]`. The mapping is an established identity **under the selected continuous Gaussian copula**. Its use for the requested population remains a transport assumption; source fasting plasma and target central serum are treated as an explicitly unverified identity scenario. Source n is a stratum count, not a verified pairwise complete-case count.

The actual `generate(observed, spec, seed)` interface rejects non-None observations. Its contiguous sampling excerpt is:

```python
R = np.asarray(model["latent_correlation"], dtype=float)
# A Cholesky failure is an error, never repaired by changing the model.
z = rng.standard_normal((len(indices), 4)) @ np.linalg.cholesky(R).T
```

Its contiguous marginal-transform excerpt is:

```python
for k, out, column in ((1, bmi, "bmi"), (2, glucose, "glucose"), (3, hba1c, "hba1c")):
    law = model[column]
    out[indices] = law["floor"] + np.exp(law["log_mu"] + law["log_sd"] * z[:, k])
```

Use either exact excerpt with omission markers, or label a shortened form as pseudocode. Do not show noncontiguous lines as one literal contiguous source extract. The specification supplies all scientific parameters. The chosen glucose floor 2.0 mmol/L and HbA1c floor 3.5% are family regularization assumptions, **not** reported physiological hard limits. Hainan moments fix glycaemic margins conditional on the chosen families; JDPP supplies BMI margins and a Pearson link. Three other latent links (age–BMI 0.10, age–glucose 0.20, BMI–glucose 0.25) are declared completions. The conditional-age construction uses transported Pani evidence and deterministic moment equations; it is distinct from A01.

## What the concrete feedback does

For delivery 7401, source object `Hainan_male_HG_spearman` maps to a `spearman_correlation` check with `female == 0`, no weights and identity transform. The existing feedback calculates **0.44681338820017125** versus source **0.44**, raw difference **+0.006813388200171244**. Female comparison is 0.49220202821884956 versus 0.50. These values come from the existing feedback JSON, not a new table read. Both statuses are `approximate`; the feedback explicitly states `scientific_validity: not_assessed` and `source_context_validity: not_certified`. They compare target-output summaries against source reports and are not source-population replay.

The Agent reviewed all 136 records across the four runs and retained the model. The figure may show a potential revise-or-retain loop, but the highlighted realized branch must be **retain**. No check establishes biological truth, target transfer or patient-level recovery. The receipt's `agent_authorship_verified: false` means this deterministic adapter does not attest the identity of the scientific author; host dispatch and the saved assignment/author artifacts establish the procedural authoring record, not a new isolation guarantee.

## Output bindings and allowed visual roles

- Actual run: `evcBuild01/executions/b_initial_delivery_7401/execution.json`.
- Actual local data path (not opened here, not for public export): `evcBuild01/executions/b_initial_delivery_7401/output/generated.csv`.
- Data hash from receipt: `9c8f8322768a5b4f014faa3f62c75c0e53c858f162fa3e9a4257d0166882b026`.
- Source feedback: `evcBuild01/semantic_feedback_v1/b_initial_delivery_7401_source/feedback.json`.
- Scientific decision: `evcBuild01/FINAL_DECISION.json`.
- Final aliases: `work/evidence_to_generation_2026-11-04/sessions/B/final_delivery_aliases.json`.
- Analysis aggregates: `work/evidence_to_generation_2026-11-04/evaluation/REPORT.json`.

A figure can show request → selected source records → explicit source-to-latent conversion → numerical specification and code → tool execution → synthetic table schema → standard analysis, with actual feedback returning to the author. Show a small **source-qualified / derived / assumed** visual distinction at the conversion. The dependence graph is a statistical model, not a causal graph. The full-cohort route is primary; optional enrichment/completion can be a peripheral capability label but did not occur in this trace. A synthetic table should show header/placeholder cells, not actual participants or invented quantitative examples masquerading as execution output.

## Review boundary

No new literature or scientific validation was conducted here. This audit confirms consistency of the existing implementation trace and exact arithmetic against the frozen specification. The older A01 derivation remains valid in the manuscript as its own worked example; it must not be inserted into this newer executed copula chain. The companion JSON hashes all read trace artifacts without reading or hashing the generated CSV itself.
