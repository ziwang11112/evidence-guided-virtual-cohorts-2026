# Independent source numerical audit

The single final audit completed with exit code **0**. All **54 successful source allocations**, across all six constructor/version combinations, were retained. All **72 qualified comparisons** were independently computable and agreed with the recorded collector calculations. There were **zero numerical mismatches, audit errors, failed slots, or unavailable comparisons**.

Maximum absolute difference in the calculated statistic: **3.3306690738754696e-16**. Maximum absolute difference in calculated-minus-reported-source-point discrepancy: **3.3306690738754696e-16**. The audit used absolute and relative tolerances of 1e-10 solely to check numerical implementation agreement.

Exact command:

```powershell
python -B 'D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system/work/developmental_continuation_v1_2026-11-03/source_audit/independent_source_audit.py' --output SOURCE_AUDIT.json
```

The script checked the release approval, ledger hash chain through scientific-freeze event `000030.json`, complete source allocation accounting, feedback-packet and declaration/review commitments, successful execution identities and seeds, receipt inventories, candidate freeze commitments, qualified metadata bindings, source-table hashes, and unchanged strict-replay unavailability. It read only generated source J/B/M tables and source/administrative metadata; it did not open target tables or reference contents. It imported no harness, source-check, qualified-collector, controller, or generator code. No generator execution, replacement draw, additional test run, or method-selection experiment occurred.

The arithmetic used the aliases, measurement mappings, operators and source evidence declared in authenticated qualified feedback. J comparisons used separate intercept-including least-squares projections of mapped native IFCC HbA1c on age, declared binary gender, and either BMI or FPG, solved with NumPy `lstsq`. B used an independent centered Pearson dot product with `math.fsum`. M used manually assigned average ranks for exact ties followed by the same Pearson calculation. All source records were retained without filtering or imputation.

The full comparison vectors and bindings are in `SOURCE_AUDIT.json`. Controller support-eligibility findings are preserved as metadata and were not independently reestimated by this focused numerical audit. This result establishes numerical agreement of the available source statistics; it makes no claim that source fit is scientifically adequate, that source participants were reconstructed, or that transport or target validity has been demonstrated.

- Script SHA-256: `8b203f88e199239ac309644b00759d364c76b06c6f1696215de4ccc69e02c627`
- Full report SHA-256: `571444654f1bf60de1d128e95b484394e0b75b804d2c38520019844158716877`
- Final inspected ledger event SHA-256: `9d59d7b4eb852c8599de24632d5438dd79d5f596e8edd25eaf67635f255ee1c5`
