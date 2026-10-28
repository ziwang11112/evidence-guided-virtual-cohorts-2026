# Independently Agent-authored specimen

These four files are byte-for-byte copies of the independently authored `agent_initial` candidate from the invented M2 execution fixture. They are supplied for inspection, not a new candidate or a biomedical generator recommendation. No patient records are included.

- `generator.py`: the Agent's gamma sampling program.
- `model_spec.json`: parameters, evidence links and assumptions.
- `evidence.json`: the two explicitly artificial sources in their original units.
- `decision.md`: the Agent's original pre-execution handoff, including what it had not tested.

The controller subsequently executed the frozen original three times. See `MILESTONE_2_PROGRESS.md` and `m2_validation.json` for outcomes and output hashes. The decision record is deliberately not rewritten to claim the Agent performed those later checks.

`examples/prepare_execution_fixture.py` recreates the allowed inputs and fictional sources in a new directory without supplying a generator. This review specimen omits the original local freeze/check/execution directories, so it is not a drop-in frozen bundle. A new run must create genuine check records, validate and freeze a new candidate before using the configured isolated runner. Do not import or execute this program as a host-side shortcut.

The paper fetched during the separate gateway smoke check was not used as evidence for this model. Moments alone do not identify the gamma family or target-population validity.
