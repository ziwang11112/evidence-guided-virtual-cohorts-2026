# Build or revise an evidence-driven population generator

Read only this run's case.json, evidence.json, task.json, and, when present,
evidence_delta.json and parent/{generator.py,decision.json,feedback.json}.
These are the delivered inputs. Do not inspect real target records, prior
target results, other experiment folders, staged future evidence, or external
literature. Separation is by workflow convention, not an OS sandbox.

Choose an executable statistical model appropriate to the evidence and target.
No model family, dependence parameter, source mixture or measurement correction
is imposed by the framework. Generate records with
`generate(n, seed, evidence, context="target")`. Return a pandas DataFrame or
dictionary satisfying the context-specific schema in case.json. Every context
receives the same delivered evidence object. Inputs and source checks describe
what was reported, not a universal target law. Do not put filesystem/network
reads, subprocesses or calls to other models in generator.py. Numpy, pandas,
scipy, math, json, typing, copy and dataclasses are available. Use reproducible
seeded sampling. Only supplied-input smoke tests are permitted before submission.

Create generator.py and decision.json in this run. Do not execute runner.py or
write report.json, samples/, feedback.json or manifest.json; the coordinator
executes the shared engine. Use a single candidate per request. Failed candidates
remain in the history. A justified no-op or a request for unavailable information
is an acceptable evidence decision. No clinical efficacy claim follows.

decision.json must contain:

- action: build, revise, or no_op; model_family: a short description.
- evidence_use: one item for every evidence ID in this stage, with id,
  action (use, qualify, defer), and reason. Distinguish the source's operator,
  population and measurement from the target assumptions.
- assumptions and open_questions: lists of concise explicit statements.
- component_map: list of {id, functions, evidence_ids, target_role}. Functions
  must exist in submitted code. Explain which code is shared by native-source
  and target sampling, and which mapping is a target-specific assumption.
- changes: list of {component, evidence_ids, reason, expected_effect}. Revisions
  must identify the evidence or diagnostic addressed, the changed component,
  its transport assumption and consequences beyond the fitted statistic.
- invariants: optional list of {context, columns}. The framework compares these
  with predecessor generated rows under common seeds and requires exact equality.
  Declare only genuine claimed invariants, not intended approximate similarities.
- influence_probes: optional list of {context, pointer, delta, columns, expect}.
  A pointer selects a numeric value in evidence.json, such as /sources/0/value;
  a small delta should leave the input scientifically interpretable. The engine
  perturbs that value and regenerates with the same seed. expect is changes or
  unchanged. This checks whether evidence reaches the actual generation path;
  it does not validate the transport assumption. Explain the probe's scope.

Use named model components so a change can be inspected. Different components
may be needed for individual variation, study differences, measurement,
population conditioning and dependencies; separate them when scientifically
appropriate, without forcing an arbitrary architecture. Unknown effects remain
assumptions or sensitivity scenarios. More generated rows do not resolve them.

For a revision, preserve the previous program in parent/ and address the delivered
diagnostics and evidence changes. Do not silently optimize a hidden outcome,
discard unfavorable subgroups, or replace individual SD with the uncertainty of
a mean. A source-only branch that fits a table is not by itself evidence that
the target generator uses that source mechanism correctly.
