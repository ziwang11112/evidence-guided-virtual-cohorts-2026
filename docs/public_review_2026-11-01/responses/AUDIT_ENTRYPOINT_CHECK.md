# Audit entrypoint applicability check — 1 November 2026

**Confirmed: the README's `python -B sync/audit_export.py` command is a historical export verifier through M10, not a current whole-repository verifier.** This is a documentation/reproducibility issue, distinct from the independently completed publication-content audit. The check used only static source inspection and Git-object inventory at `7f4b38c0c0dfa8da4bbd8df3d5ee754399600562`; no repository audit, biomedical test or generator was executed, and no export files were changed.

The pinned README presents that command under general independent checks (`README.md:72`) and again after a broad refresh (`README.md:82–83`). The audit reads `sync/EXPORT_MANIFEST.json`, unions its destinations with hardcoded `LOCAL_FILES`, then scans the entire checkout and flags every other file as `not_allowlisted` ([`sync/audit_export.py:75–95`](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/sync/audit_export.py#L75)). Its historical chain ends with M10, with no dispatch to later unit audits (`:231–278`).

| Static inventory at the pinned snapshot | Count |
|---|---:|
| Tracked files | 6,109 |
| Legacy manifest source records | 1,639 |
| Hardcoded local files | 54 |
| Union of permitted legacy paths | 1,693 |
| Tracked paths outside that union | **4,416** |
| Legacy permitted paths absent from the snapshot | 0 |
| Current Git blobs differing from legacy source-record hashes | **4** |

The 4,416 out-of-scope paths comprise 4,372 under `biomedical_research`, 12 under `docs` and 32 under `sync`. The four legacy hash mismatches are project-relative `README.md`, `skills/evidence-cohort-generation/references/harness-interface.md`, `docs/SOURCE_CHECKS.md` and `docs/SCIENTIFIC_ANALYSIS_UTILITY_PLAN.md`, all under `biomedical_research/virtual_cohort_system/`. These counts establish incompatibility with the old contract; they do **not** establish unauthorized changes, corrupted science or sensitive data. The legacy manifest last changed at M10 commit `d33d0cbad4c199fe5b450688fe8050d72afd9861`.

The saved `sync/EXPORT_AUDIT.json` says PASS for **1,691 audited files / 1,639 sources**. Its two generated audit outputs are excluded from self-hashing, explaining 1,691 versus 1,693. That historical PASS cannot certify all 6,109 current files. Running the old script now would accumulate scope failures and, if it reaches its output stage, overwrite `sync/FILE_INVENTORY.tsv` and `sync/EXPORT_AUDIT.json` before returning failure ([`audit_export.py:279–314`](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/sync/audit_export.py#L279)). A disposable checkout was unnecessary to establish this statically.

**Later unit auditors do not provide a drop-in replacement command.** For example, `audit_m17b_export_2026-10-31.py:60–73,91–94` requires the original source workspace and checks the exact delta against its recorded prior commit. `audit_cycle2_case_export_phase2_2026-10-31.py:51–79,102–105` additionally requires HEAD to equal its prior staging commit; `:192` writes its receipt. These are export-time checks with historical prerequisites, not generic clean-clone verification commands. No current aggregate dispatcher was identified in `sync/`.

This distinction is already documented elsewhere: [`docs/RESEARCH_DIRECTION_EXPORT_2026-10-31.md:13`](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/docs/RESEARCH_DIRECTION_EXPORT_2026-10-31.md#L13) calls the M10 allowlist/manifests historical. `docs/CYCLE2_COMPLETED_CASE_EXPORT_2026-10-31.md:23` explicitly warns against rerunning an earlier delta audit against the expanded checkout.

**Recommended narrow correction:** remove the legacy command from current generic checks, label the broad sync/audit instructions as historical through M10, and preserve frozen receipts. Do not imply that replaying every unit auditor on latest HEAD is supported. A future current-snapshot verifier would need explicit unit/version composition and read-only output handling; no such implementation is claimed or performed here. The active audit script remains identical to the pinned version. Detailed path/count working records remain local; the counts and pinned implementation links above are the public audit record.
