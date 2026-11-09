# Whole-cohort source replay v1 implementation validation

9 November 2026. These are invented-data software checks, not clinical generator
results or scientific validation. No old scientific candidates, target outputs,
or target-reference values were read to implement the adapter. The approved
`work/conditional_evidence_2026-11-09/FOLLOW_ON_SPEC.md`, skill interface, source
code, interface documentation and invented fixture/test code supplied context.

## Test record

1. Initial adapter suite: `17 passed in 8.71s`, using existing Python 3.12 and
   `--basetemp D:/evcSrcAdapterTest01`. This included a real existing
   WSL/bubblewrap invented-program execution, plus mocked boundary tests. The
   real program read `/input/task.json`, emitted ten source rows and an extra
   raw predictor column against an eight-row parent task, and preserved exact
   generator/specification/evidence bytes. Mocked tests explicitly label their
   backend and are not claims of actual isolation.
2. Independent code review identified that strict nonidentity bindings skip
   source/task unit equality. The first implementation could therefore compute
   an assumed projection in inconsistent numeric outcome units. This was fixed
   in the new adapter, without changing `semantic_feedback_v1`: assumed
   projections require a specified source operator, matching numerical operand
   units and dimensional coefficient units. The complete strict result retains
   its original unavailable/nonidentity status. Additional checks require
   standardized predictor identities on every source-operator-selected row.
3. After those guards: `67 passed in 12.69s` across the new adapter suite and the
   existing semantic suite, using `--basetemp D:/evcSrcAdapterTest02`.
4. Final implementation also rejects nonidentity assumed projections without
   an explicitly checked zscore OLS coefficient term. Final command:

   ```text
   python -m pytest tests/test_whole_cohort_source_replay_v1.py tests/test_semantic_feedback_v1.py -q --basetemp D:/evcSrcAdapterTest03
   ```

   Result: **68 passed in 11.33s**: 22 new adapter cases and 46 existing semantic
   cases. The real WSL/bubblewrap smoke passed again. Engine SHA256:
   `ffeb32852e3aa1211a56ed7ec243ab94ea73bfb8449fc85f6f80fcb958b5ea6a`.
   Test SHA256:
   `2b6c4c476ac93b100144c528c704ff5fb8690044f3c31ef339c473a431e368fc`.

## Tested invariants and limits

- Separate source population, row count and nuisance/output columns reach the
  existing worker through the child task; code/spec/evidence bytes remain equal.
- Parent frozen candidate bytes stay unchanged. Its target-only canonical
  recipe cannot replace the source-specific recipe or strict semantic sidecar.
- Source-standardized OLS with nonidentity scaling and unknown source weighting
  is unavailable in strict feedback. Its explicitly named parallel projection
  computes only with assumption-dependent labels.
- Known wrong coefficient/adjustment definitions, inconsistent outcome units,
  unsupported source definitions and unchecked transforms reject before
  execution or arithmetic. Bad zscore identities and partial coverage fail
  before either numerical feedback lane.
- No parent execution table is an adapter input. Metadata preflight does not
  read individual tables or execute a generator.
- Frozen schedule identity, seeds, row counts, shared revision budget,
  append-only reservations, failed execution, interrupted construction, and
  failed predictor checks retain their actual scope and consume slots.
- Modified output, child specification, source recipe, replay calculation or
  extra replay artifacts fail verification.

The adapter does not enforce the separately authorized optimizer/analytic
objective-call ceiling inside arbitrary generator code, establish source-law
truth, recover unpublished standardization, implement weighted regression, or
prove source-to-target transport. The controller must freeze and review those
declarations and meter objective calls separately. No new packages, HPC jobs,
API calls, or clinical source retrieval were used.
