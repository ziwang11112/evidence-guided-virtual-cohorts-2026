# Recomputing the evidence the agent chose

Use [the source-replay entry point](../run_with_evidence_replay.py) for new runs. It accepts an article and a UTF-8 research request. The development cases can also be selected by their existing request key. The previous iron and lung runs retain their original loader and receipts.

~~~text
python run_with_evidence_replay.py --article path/to/article.txt --request-file path/to/request.txt --run study01
~~~

## What the agent sees

1. **Design.** The agent reads the article, sets the scientific task and declares its own evidence inventory. Each source quantity has an identifier, a location in the article, a population, a reported or derived value and unit, and either an operation on virtual measurements or an explanation of why it cannot be checked. Subgroups, conditioning, the direction of a regression, variable units and printed precision are recorded before generation. An assumption can be recorded without being scored as a source fact.
2. **Trial.** The agent writes a sampler and analysis. An isolated process generates the trial rows. The controller reads the hash-verified table and independently computes the registered statistics. For each scenario it reports the source reference, trial estimate, signed difference in source units, row count and status. A match to printed precision means only that the computation lies within the source's rounding interval. Estimates with no corresponding printed precision receive a descriptive difference.
3. **Review.** The agent receives those summaries with its original source and its own trial diagnostics. It can keep the model, revise it, abstain or qualify the intended use. The controller records whether the review addressed each discrepancy or unresolved item. Missing explanations and unknown IDs remain visible in the final reconciliation.
4. **Final execution.** The initial inventory is applied to the selected candidate on all final seeds and scenarios. This includes previously missing or mismatched items. The final table outputs and independent evaluation data are unavailable to the author during its review. A successful program exit denotes execution success. Source agreement and review completeness have separate fields.

## Reading a result

New private runs are under `private/replay_v2/<run>/`, relative to the article-authoring work directory. The v1 capture is retained at its original path. The v2 agent declares numeric column names and units during design. `design_as_authored.json` preserves the original response, and `unit_bindings.json` records exactly where each operation's units came from. Missing or conflicting declarations are flagged. `source_inventory.json` is the resulting pre-generation selection. `trial_source_replay.json` contains the computations and table hashes. `source_feedback_sent.json` is the aggregate payload used for review, and `review_coverage.json` lists unacknowledged items. `final_source_replay.json` binds the selected candidate, inventory, review reconciliation and final numerical results. A zero-length inventory with a declared reason has zero numerical coverage.

To replay a captured v1 design and generator through v2, supply a new run name and `--reuse-initial-run <v1-run>`; use the same arguments on resume. The adapter verifies both original API responses and requires identical initial candidate and trial table hashes and identical trial diagnostics before the review request. A fresh run uses three author calls. A retained initial design and generator require only the new review call. A final independent audit can verify that the itemized payload actually occurs in that call's captured input.

Reference values, printed precision and source interpretations are chosen by the agent. An independent source reader is still needed to detect a missing table, mistranscribed value, wrong sex coding, or a materially inapplicable study. Printed rounding precision does not measure sampling or population-transfer uncertainty. Unweighted simple OLS, correlations, moments and raw contingency statistics have explicit unit and variable checks. Adjusted analyses, unsupported weights and unrepresented measurement conversions must be left unresolved. Raw source counts require comparable sample sizes. Generation can continue when such an item cannot be evaluated. The program records the reason.

## Validation

Run the following commands from the project root. The historical test uses evaluator-transcribed fixtures and the original virtual rows. Its material stays outside the live constructor. The offline flow tests include both a retained disagreement and a revision that removes it. They also test that a favourable diagnostic returned by the agent cannot substitute for the value computed on its rows.

~~~text
python -B -m unittest discover -s work/article_autonomy_design_2026-11-22/evidence_replay -p "test_*.py" -v
python -B work/article_autonomy_design_2026-11-22/evidence_replay/fixtures/run_acceptance.py
~~~

[Historical source definitions and expected outcomes](fixtures/README.md)

[Integration results and independent scientific reanalysis](INTEGRATION_RESULTS.md)
