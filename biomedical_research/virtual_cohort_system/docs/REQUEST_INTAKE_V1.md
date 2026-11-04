# Research-request intake v1

3 November 2026. Implemented in [request_intake.py](../cohort_harness/request_intake.py).
This is a request-to-author handoff, not a natural-language parser or autonomous model launcher.

## What it does

The calling Agent translates the user's research purpose, population, variables,
units and analyses into a structured request. The intake validates that request,
keeps scientific questions visible, and creates a fresh bundle understood by the
existing harness. It does not choose scientific relationships or parameters.

A request has four fields:

- schema_version: 1.
- purpose: the research purpose.
- analyses: a nonempty list of requested analyses, without expected answers.
- task: the existing exact task-v1 object defined in cohort_harness/contracts.py.

The scientific author receives the request and decides how to retrieve evidence,
interpret it, construct the generator and use the available numerical tools.
Three task modes are accepted: whole_cohort, enrichment and completion. The last
two require an explicitly supplied observed CSV, validated and copied byte-for-byte.
Whole-cohort requests reject individual input.

## Run the entry

From the project directory, using the configured Python environment:

```powershell
python -m cohort_harness.request_intake --request examples/research_requests_v1/adult_bmi.json --destination /path/to/new-bundle
```

The destination's parent must exist; the destination itself must not exist.
For enrichment/completion add --observed /path/to/permitted-observed.csv.
Keep participant files and generated tables local under the project data policy.

Created files are request.json, task.json, an empty registry.json, AUTHOR_TASK.md,
adapters.json, intake_receipt.json and, where required, observed.csv. The sources/
and candidates/ directories start empty. No paper, model specification, generator,
generated table or successful diagnostic is fabricated.

The receipt records performed intake operations and explicit unperformed stages.
It describes intake-time hashes; later legitimate source registrations may append.

## Adapter routing and limits

- Literature actions use cohort_harness.literature and the literal task permissions.
  An empty registry is a valid starting point for its existing registration process.
  The entry does not search the network or confirm that a particular paper is available.
- Candidate validation/freezing uses the existing cohort_harness interface.
- Generator execution requires an explicitly supplied verified runtime and frozen
  candidate. Preparing an invocation is not execution, and there is no local fallback.
- Whole-cohort source feedback points to cohort_harness.semantic_feedback_v1.
  Source declarations, candidate artifacts and a valid execution must be supplied
  at the appropriate stage. Intake does not run or certify that feedback.
- For enrichment/completion, a suitable source-feedback route remains to be selected;
  the whole-cohort adapter is not falsely advertised for every mode.
- The calling environment launches the scientific LLM. This module does not.
  Its status is ready_for_external_author, not generation_completed.

The existing task-v1 contract does not contain the purpose/analysis fields, so
they remain in request.json and the author packet. No frozen contract or controller
was changed to introduce this entry.

## Actual validation

Two metadata-only CLI demonstrations succeeded:

1. Adult BMI/HbA1c analysis adjusted for age and sex.
2. The same request with fasting glucose added and included in adjustment.

Both examples used the same entry unchanged. They produced different task and
author packets, with zero patient-like rows, model calls or retrievals. Their
1,000-row task sizes are requested future output sizes, not executed generation.

An independent agent wrote and ran [the new tests](../tests/test_request_intake.py):
19 parameterized cases passed. They cover request preservation, input validation,
observed byte preservation in enrichment/completion, safe refusal to overwrite a
bundle, permissions, actual local literature-session initialization with HTTP
forbidden, and the explicit v1 feedback descriptor. The first run failed before
test execution because global temporary-directory access was denied; rerunning
with a checked fresh project temporary directory passed. No old scientific test
or clinical experiment was rerun.

These are interface results. They do not demonstrate autonomous evidence
interpretation, scientific adaptation, quality gains or reduced human work.

## Next integration step

Use the accepted [system-contribution plan](AGENT_SYSTEM_CONTRIBUTION_AND_EVALUATION_2026-11-03.md).
Connect a newly launched author to one fresh request, actual permitted evidence
access and the existing execution/feedback tools, recording what is performed by
the author and by the coordinator. Select the scientific task and allowed evidence
before that run. Existing exposed references remain development references.

A universal dispatcher, reliable original-paper extraction, feedback coverage for
all modes and validated data delivery remain unfinished. The optional 24-table
evidence-selection study is not a prerequisite for completing this workflow.
