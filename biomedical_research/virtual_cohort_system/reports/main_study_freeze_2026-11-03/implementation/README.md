# Main-study adapter boundary

`main_session_v1.py` is a new orchestration adapter. It does not modify earlier frozen experiment modules and does not launch an LLM. The calling conversation must record actual external author dispatches.

Implemented boundaries:

- independently reviewed campaign release before session activation/author dispatch;
- one fixed constructor identity, initial/revised immutable candidates, explicit final selection;
- two exploratory attempts total, three final attempts, 3,000 rows; reservations precede isolated execution;
- fixed trial seeds 5201/5202 and final seeds 5101/5102/5103;
- failed/interrupted attempts stay spent, and incomplete final delivery resumes only unused slots;
- explicit `semantic_feedback_v1` preflight and collection, no legacy fallback;
- only generated-table diagnostics returned during construction; source checks on target rows unavailable;
- separately reviewed analytic source operations, not a new source-population replay engine;
- all 24 scheduled constructions close, including failures, before common reference evaluation.

The campaign remains disabled until case cards, source-operation bindings, same-information statistical reference, generated-only providers, final evaluator, source-uptake review requirements, all 24 session contracts, and independent prerelease review are bound. The controller's hash chain detects accidental or stale modification; it is not a signature or security boundary against the host. Fresh author instructions do not sandbox the author's general tools. A compiled/procedurally valid generator is not automatically biologically valid.

Unit tests use temporary ledger fixtures and mocked executor failures only. No patient records, scientific generator, or case-level final table is used. The first test attempt had one test-fixture error: the tamper test called the production append-only writer on an existing file. The fixture was corrected to make an explicit tamper write; production behavior was unchanged. The corrected 12-test suite passed. Two subsequently added tests cover actual orchestration-ID versus constructor-ID distinction and mandatory uptake/moment artifacts; both passed after correcting the fixture's expected wrapped exception and misplaced test lines. The affected release-binding test also passed. Thus 14 distinct tests have passed, with only changed tests repeated. Independent implementation review remains necessary before campaign release.
