# Qualified-plan author metadata preflight

This additive author utility catches metadata errors before freeze. It reads only `task.json`, `evidence.json`, `model_spec.json` and `qualified_plan_v1.json`, visits every declared context when those metadata indexes are readable, and reports the original file path, JSON pointer, context/check ID and metadata remediation hint for each failure. It never changes a candidate. The CLI writes JSON to stdout and exits 0 for the checked metadata passing, 1 for findings, or 2 for unreadable input.

The check reuses the released `_alias_contract`, `_mapping_contract` and `_operator_contract` in `work/evidence_revision_v1_2026-11-02/implementation/qualified_relationships_v1.py`, plus its pure operand checks. Authored `bindings` must equal `{}`. Declaration shape and source-context labels are checked. A bad context does not stop later contexts; invalid aliases block dependent operators. Fingerprints cover all four read inputs and the five directly used validator/code files. No released module is edited.

Run from this directory:

```powershell
python -B qualified_author_preflight.py --bundle D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcDP/A01 --candidate initial_interface
python -B -m pytest -q -p no:cacheprovider test_preflight.py
python -B record_regression.py
```

The final command writes only `regression_results.json` beside this utility. Tests use in-memory invented metadata; no temporary directories, bytecode or pytest cache are required. The tests include read-only regression against the three expressly permitted retained candidates and trap forbidden lifecycle/numerical calls. The 68 older tests were not rerun.

The final focused suite passed **27 tests in 0.51 seconds**, including rejection of an empty context object. `test_result.json` records that invocation and the earlier 26-test run before this focused robustness addition. `regression_results.json` separately reproduces 3 retained submissions, 9 visited contexts and 12 visited checks, with **9 findings**: A01 `initial` has three nonempty authored binding objects and two J mapping failures; A01 and A02 `initial_interface` each have two J mapping failures. All 11 distinct input files retained their hashes. Both corrected submissions' J mappings use `hba1c`, while the retained `U_NGSP_SCALE` item names `HbA1c_percent` and `HbA1c_IFCC`.

Two copied in-memory hypothetical plans add the native alias `HbA1c_percent <- hba1c` using existing measurement assumptions and use that alias as both J mapping inputs. Each passes all four checked operators. Tests also confirm that the released pure mapping helper rejects the original inputs and accepts the copied metadata correction. This demonstrates interface behavior only; it is not a scientific correction, submission, review or experiment. No modified candidate or approval was written.

Passing is limited to the named metadata checks. It does not establish source correctness, faithful extraction, source-population reconstruction, support, moments, transport or full lifecycle approval. It does not validate bridge/evidence-use consistency, source coverage, strict semantic status, relation review, evidence admission or frozen/run bindings. These remain the released workflow's responsibilities. Missing operators can pass metadata while remaining noncomputable. The utility does not read source/target output tables, reference or patient files, import a submitted generator, sample data, create a bridge, freeze anything or fabricate independent approval. The closed developmental pilot and its execution budget remain unchanged.
