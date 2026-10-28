# Fresh construction request: evidence-guided fasting-insulin enrichment

Read only this file, the experiment's `shared/`, your own `agent_clean/` files, and screened records under `literature/approved/`. You may execute the literature_gateway.py CLI from the experiment root but must not open other root files. Do not read `agent/`, `custodian/`, `review/`, `results/`, other experiments, other Agents' logs, or any hidden outcome. There was a stopped earlier literature-search attempt; its content is intentionally not supplied to this fresh context.

## Your task

Preserve observed BMI, age and sex for all supplied people and generate an entirely missing fasting-insulin variable. This is virtual feature enrichment for scientific analysis, not individual medical diagnosis. Decide the model and all scientific assumptions yourself from applicable external primary literature. The coordinator supplies no biological slope, correlation, subgroup effect, residual variance, or desired scientific conclusion.

Input is `shared/observed.csv`, exactly `row_id,bmi,age,sex`. Read `shared/schema.json` and `shared/target_description.md` for population and measurement facts. The target is the NHANES 2017–2018 eligible adult fasting subsample, age20–79, with no self-reported diagnosed diabetes (borderline retained), excluding reported insulin use and pregnancy as documented. The source is disclosed solely to enforce evidence exclusions; never retrieve any NHANES outcome data, summaries, participant matches, or NHANES-based papers from ANY cycle.

**Output interface naming:** the schema's descriptive feature name `insulin_uU_mL` is mapped to the required output CSV/program column **`insulin`**, measured in µU/mL. This is only an interface alias, not a unit conversion.

## Literature discovery is your responsibility

Choose your own search queries and evidence. Use ONLY the screening gateway for all literature access; do not use general web search, a browser, raw requests, or alternate routes that display unscreened snippets. From the experiment root:

```
python literature_gateway.py search --query "your scientific query" --limit 10
python literature_gateway.py fetch --pmcid PMC1234567
python literature_gateway.py fetch --pmid 12345678
```

The gateway uses public bibliographic services, screens metadata/abstract/fulltext before display, and stores approved content with hashes. Rejected sources are unavailable. If the gateway rejects a primary paper because it mentions prohibited studies in its references, choose another source or record the limitation; do not bypass it. You may inspect the gateway implementation only if needed to understand its interface, never its rejected response contents. Procedural blinding and screening are not claims of perfect absence of pretrained knowledge.

Normally obtain 3–6 applicable primary studies with up to 12 substantive search queries initially. Record unsuccessful searches and reasons for stopping. Need more searches to resolve a concrete evidence gap? Send the gap and proposed bounded extension; do not silently widen the task. Do not invent quantitative parameters where only qualitative statements are reported: explicitly distinguish source estimates, justified transformations, and your modeling assumptions. Pay attention to fasting conditions, target population, assay units, adjustment, conditional variation, source overlap and applicability. Odds ratios for a derived binary diagnosis are not automatically continuous insulin slopes.

Write `agent_clean/EVIDENCE_LEDGER.json` and `SEARCH_LOG.md`, with query log, screened identifiers/DOIs/URLs, relevant section/table, extracted quantities, source uncertainty when available, source population, application to the generator, exclusions and unverified assumptions. Short necessary quotations only; do not copy whole papers into the report. Approved fulltexts remain separate local research inputs.

## Implement actual generation

Choose an Agent-authored program or direct-record route. If using a program, create `agent_clean/initial/generator.py` exposing:

`generate(observed: pandas.DataFrame, evidence: dict, seed: int) -> pandas.DataFrame`

The `evidence` argument is your JSON `agent_clean/initial/model_spec.json`. Return exactly `row_id,bmi,age,sex,insulin`, preserving every observed value and order. Insulin must be finite and positive. Do not apply target-informed clipping or make each virtual value a deterministic function solely to force a desired conclusion. Use explicit conditional variation and disclose limitations of uncertainty.

The generation function may use numpy/pandas/scipy and standard mathematical libraries. No file/network reads, subprocess calls, or target-data access inside generation; no input mutation or global RNG mutation. Use a local seed-controlled random generator. All scientific constants must link to sources or explicit assumptions. The execution controller will run 20 draws with seeds270101–270120, without target feedback. These are not twenty independent Agent constructions.

For direct records, notify the coordinator early to agree the transport interface; the same observed-preservation and source rules apply. Do not claim direct record generation if a numerical program actually produces them. No model training is required.

Write `agent_clean/INITIAL_DECISION.md` describing the selected route, evidence-to-model mapping, conditional variation, assumptions and intended/unsupported uses. Give concise auditable decisions, not private reasoning traces. You may run source-only or artificial-input checks; do not seek or compute evaluation answers.

Initial files will be frozen and independently reviewed against sources and code. If defects or evidence issues are found, revise into a NEW directory using only that feedback, preserving the initial model and decisions. No real target outcome or analysis result will be provided. A justified no-op is allowed. All scheduled initial and revised outputs will be retained; no hidden-score selection.
