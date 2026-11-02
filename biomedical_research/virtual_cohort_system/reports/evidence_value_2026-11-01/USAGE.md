# Custodian artifacts and evaluation entrypoint

This unit is an invented mechanism pilot. The custodian created metadata, exact population summaries and deterministic quadrature references; it created no individual rows and executed no candidate generator.

`CUSTODY_COMMITMENT.json` is the readiness manifest. It binds 23 builder-visible files and four private custodian files by SHA-256. The four neutral bundles are `bundles/A`, `bundles/B`, `bundles/C` and `bundles/D`. Each contains its own task, evidence, registry, evidence note and identical `BUILDER_BRIEF.md`; admitted notes are under its `sources/` directory where applicable. Evidence-item counts are 0, 9, 19 and 19. Empty candidate directories are reserved for constructors. Existing task, evidence and registry contract checks passed. These checks establish metadata validity, not generator performance.

The independent reviewer must admit the final commitment file and all its bound files before constructor dispatch. Root should include that file's own hash, its `commitments` mapping, and the independent admission in the campaign freeze. `private/LAW.json`, `private/REFERENCE.json`, `private/make_fixture.py` and `private/evaluate.py` remain closed to constructors and root until release. Hashing their bytes is permitted. This is role-based custody in a shared workspace, not an access-controlled enclave.

Do not rerun `make_fixture.py`: the prepared metadata are already committed, and its exclusive writes intentionally refuse replacement. Do not import or invoke the evaluator early. All four candidates must be frozen before any output, and all twelve scheduled output or failure records must exist before release. Each failure retains its slot; no extra rows, retries, repair or post-reveal tuning are authorized.

After the complete campaign and an explicit custody release, run from the `virtual_cohort_system` project directory with the existing Python environment containing NumPy and pandas:

```text
python -B work/evidence_value_2026-11-01/private/evaluate.py
```

The evaluator takes **no arguments**, invokes no generator, and reads only the prepared metadata, existing harness verification interfaces and twelve campaign slots. Its gate verifies the custodian commitments, frozen engine and candidate hashes, campaign manifest, and every slot's saved attempt/result receipt. Successful slots additionally require valid execution receipts and output hashes before their fictional generated tables are analyzed. Failed slots remain in the report.

Expected outputs, created once under `evaluation/`:

- `REQUEST.json`: evaluation reservation and input/evaluator hashes.
- `REPORT.json`: all twelve statuses, per-output aggregate statistics, signed and absolute differences for each compatible world, source-population recombination checks, counterfactual responsiveness and the now-revealed artificial reference.
- `FAILURE.json`: written instead of a complete report if an error occurs after reservation. Preserve it and stop for review; do not silently retry or remove the reservation.

Standard output contains only completion metadata and the report path. The primary statistic is pooled unweighted `y ~ 1 + x`, without group adjustment. Source compliance uses fixed equal-group recombination of generated conditional moments, not raw target moments. The tail endpoint is `P(x > 1, y > 2) - P(x < -1, y > 2)`. Neither source sampling uncertainty nor clinically calibrated uncertainty is implied. Simulation-seed variation is conditional on each frozen program; common numeric seeds do not guarantee common innovations across programs. Compatible worlds are reported separately without invented probability weights or a global score.

The actual commitment digest and reviewer disposition belong in admission. Any pre-admission correction must be explicitly rehashed and reviewed; no source or evaluator changes are allowed after the campaign freeze.
