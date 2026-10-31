# M16 export verification: invented-data software tests

31 October 2026 UTC. **PASS: 96 tests passed in 13.60 seconds; exit code 0.** This checks software behavior on explicitly invented fixtures, not the biomedical experiment or generated-data accuracy. No real-study evaluation was rerun.

| Test module | Passed |
|---|---:|
| `tests.test_self_consistency` | 56 |
| `work.m16_direct_repair_2026-10-30.evaluation_code.test_evaluator` | 18 |
| `work.m16_direct_repair_2026-10-30.independent_target_audit.test_recompute` | 22 |

## Executed command and boundary

Working directory: `biomedical_research/virtual_cohort_system` in the local research workspace. The exact local orchestration command was:

```powershell
python -B work/m16_direct_repair_2026-10-30/review_exports/run_invented_export_tests.py
```

The helper set `PYTHONDONTWRITEBYTECODE=1`, `sys.dont_write_bytecode=True`, and `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`; disabled pytest cache; created a fresh short scratch directory; recorded pre/post hashes; and called `pytest.main` with the following effective argument list. The project pytest configuration supplied `-ra`. The helper and JUnit file are local verification artifacts, not required scientific inputs.

```json
[
  "-ra",
  "tests/test_self_consistency.py",
  "work/m16_direct_repair_2026-10-30/evaluation_code/test_evaluator.py",
  "work/m16_direct_repair_2026-10-30/independent_target_audit/test_recompute.py",
  "-q",
  "-p",
  "no:cacheprovider",
  "--basetemp",
  "D:\\AIR-014_ECRC_Paper_Clean_2026-08-16\\.m16_xt_2afc2cd5",
  "--junitxml",
  "D:\\AIR-014_ECRC_Paper_Clean_2026-08-16\\biomedical_research\\virtual_cohort_system\\work\\m16_direct_repair_2026-10-30\\review_exports\\invented_test_junit.xml"
]
```

The fresh scratch directory was `.m16_xt_2afc2cd5` at the workspace root. It contains invented fixture outputs and is excluded from the export. A repeat must use another fresh scratch directory; no cleanup or deletion was attempted in this verification.

The published test modules were read before running. All rows are constructed algebraically in those modules and written beneath pytest `tmp_path`. The canonical wrapper tests exercise real lifecycle machinery only on invented bundles. The independent wrapper imports its pinned arithmetic code and verifies the older audit code hash; it does not open the older study data. No real observed, reference or generated participant table, raw XPT, source article, gateway response or private working-data file was read. No acquisition, real controller flow or real evaluation CLI was executed.

An additional Python audit hook rejected any CSV/XPT file open outside the fresh invented-data scratch tree. There were **zero outside-scratch row-file access attempts** and 2,410 permitted invented row-file opens, including repeated reads/writes. This is a scoped verification guard, not a general security sandbox or scientific information-boundary proof.

## Scope and limitations

The 56 checker tests cover known arithmetic, declared groups and joint groups, safe expression validation, table/text preservation, undefined diagnostics, hash binding, deterministic reports and exclusive creation. The 18 canonical-wrapper tests cover all six invented stage outputs, fixed estimands, genuine fixture lifecycle freezes, gate ordering, metadata handling, failure retention and aggregate serialization. The 22 independent-wrapper tests cover numerical comparison, deliberate corruption, complete endpoint/deletion accounting, null/rank failures, CSV integrity, failed/retained builders and refusal before reference access.

There were no failed tests, collection errors, reruns, skipped tests or scientific-code changes. Fourteen watched implementation/test/document files had identical SHA-256 hashes before and after this run. Tests were run in the source workspace; the exact export still requires its separate source-to-export hash and content checks.

## Environment

Python `3.12.10` on Windows. Test interval: `2026-10-31T05:14:19.831874+00:00` to `2026-10-31T05:14:33.528296+00:00`.

- numpy: `2.4.5`
- pandas: `3.0.3`
- scipy: `1.17.1`
- statsmodels: `0.15.0`
- pytest: `9.0.3`

## Unchanged file bindings

| Project-relative file | SHA-256 |
|---|---|
| `cohort_harness/self_consistency.py` | `60f8f8c398104df3c017e96f5d6c659953e6f634a6caa17c5de8711f646e97f7` |
| `cohort_harness/contracts.py` | `1587f974472a515182293972acd7470a01e423c912abd780280529c543560390` |
| `cohort_harness/lifecycle.py` | `01688ffce3972053bab631c19e1f7a7bb941c53af1a5a658dfff0ecad401fee4` |
| `tests/test_self_consistency.py` | `67cc1eaf409a3ecd4fa8e6136ccc1a4ae4df4fa5de4179babc28a01340e8249b` |
| `docs/SELF_CONSISTENCY.md` | `7b3526dd19caa458bc6b7a01a532b7f48feea8d789049399c9186ccebe0c448b` |
| `work/m16_direct_repair_2026-10-30/evaluation_code/evaluator.py` | `a63c3aecf9718ee9be1bd462bd0df3d40765d1228efd158fae69d18deda15483` |
| `work/m16_direct_repair_2026-10-30/evaluation_code/frozen_m15b_estimands.py` | `4181cfbd8ae37df58699558196ca241f2bd60e4d895b9a18de40a42cbaffce12` |
| `work/m16_direct_repair_2026-10-30/evaluation_code/test_evaluator.py` | `a57b7a89f4873c26e78a528da13ad5c4fad3e5ccdc1c04c858af855abb2bb8ed` |
| `work/m16_direct_repair_2026-10-30/evaluation_code/README.md` | `a4ae63bd41f1f45738220d904e98fb2affae3e32b126b7e2ba9b31bd3042681a` |
| `work/m16_direct_repair_2026-10-30/independent_target_audit/recompute.py` | `c969c2141de94e7d31762ff86dca41a802f7e7deb800b79f7ba499cdb52d1f29` |
| `work/m16_direct_repair_2026-10-30/independent_target_audit/frozen_independent.py` | `e2cd4b3cc7720c3d2bc42f5e67dae9c67595534091f1fe0631683f16fc1398da` |
| `work/m16_direct_repair_2026-10-30/independent_target_audit/test_recompute.py` | `470e94e9b6743aca80dfb6af5aba15e0bbe174783bcb596df541448a51c7efd7` |
| `work/m16_direct_repair_2026-10-30/independent_target_audit/README.md` | `42be20b02d05437a70c5f7ddff91b0f2217e46d0565195b40135a55bc7dcbde6` |
| `work/m15b_literature_direct_2026-10-30/independent_target_audit/audit.py` | `e2cd4b3cc7720c3d2bc42f5e67dae9c67595534091f1fe0631683f16fc1398da` |

The separate source/export manifest records any reviewed relocation or documentary link transformation. These hashes identify the code and documentation tested here, not a claim that omitted real inputs are available in the repository.
