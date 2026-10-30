# Custody preparation validation

2026-10-30. Pre-access, invented fixtures only. No target XPT acquired or read.

`python -m pytest work/m13b/custodian/test_prep.py -q --basetemp work/m13b/custodian/_pytest_temp_run1`

Result: **17 passed in 0.70 seconds**. An earlier default-temp invocation completed 13 transformation checks but hit two setup errors because the preexisting Windows pytest temp directory was inaccessible; the successful run used a fresh directory under custody. No scientific or eligibility changes were needed for that environment issue.

The invented temporary fixtures remain in `_pytest_temp_run1/` because automatic execution policy rejected their recursive cleanup. They include fake gate manifests/authorizations, not actual authorization or target data. Exclude `_pytest_temp_run1/` and `__pycache__/` from the scientific freeze and delivery. No deletion-policy workaround was attempted.

`python work/m13b/custodian/prep.py show-required-rules`

Result: success; exact frame/generator schemas and frozen domain bounds printed. This command neither requests nor reads target data.

The fixture checks include a valid freeze/authorization gate, rejection after a frozen file changes, rejection without explicit authorization, rejection before any network call when the manifest hash mismatches, exact output whitelist, endpoint boundaries and integrity, valid-scan exclusion, one-to-one left merges, duplicate/orphan rejection, arbitrary opaque IDs, consistent row order, full-frame/zero-domain PSU retention, and weighted/unweighted completeness.

Actual acquisition and outcome evaluation remain unperformed at this handoff. Root must freeze the final audited bytes, create an authorization tied to that freeze, and explicitly direct acquisition. Frozen scientific candidates and generator parameters were not edited.
