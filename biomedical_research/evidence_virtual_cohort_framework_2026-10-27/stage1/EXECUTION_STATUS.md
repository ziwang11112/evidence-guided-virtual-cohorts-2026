# Stage 1 execution status

The frozen `stage1_v3` generation and evaluation are complete. This status page is operational metadata, outside the immutable scientific protocol and candidate artifacts.

- All nine fresh initial builders completed and passed the controller's mandatory source-only checks.
- All eighteen paired revision contexts were staged from their common initial parents.
- The three fixed statistical arms completed: 60/60 cohorts saved.
- All eighteen revision builders completed in fresh, source-restricted contexts. Candidates were frozen, reviewed and executed separately; diagnostic failures are retained. All 360 Agent cohorts were saved.
- The exact 21-arm, 420-cohort inventory gate passed before opening reserved real-data evaluation. Evaluation completed with 7,700 records, all with status `ok`; model-fit warnings remain reported and retained.
- This is an A0 target-summary-conditioned development experiment, not an independent cross-study transfer result.

The local sanitized GitHub export is `../github_virtual_cohort_2026-10-27` relative to the project parent. Its private remote is https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026. Source patient tables, completion tables, full synthetic cohort tables and custodian reference inputs are excluded. The first audited export was pushed; Stage 1 aggregate results are synchronized after execution and review, with commit and content-audit records retained in the export.

The current machine has 16 logical processors and approximately 31.6 GiB RAM. Numerical generation is inexpensive at this scale. Independent model construction and review dominated elapsed effort; an HPC allocation was not needed for this bounded run. The expansion decision is documented in [DECISION.md](DECISION.md).
