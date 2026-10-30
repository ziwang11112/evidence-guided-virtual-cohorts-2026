# M10 controller evaluation freeze interface

`evaluate.py --manifest ABSOLUTE_JSON --output ABSOLUTE_NEW_DIRECTORY` is the only target-reading entry point. `--verify-only` verifies a complete freeze without parsing reserved target outcomes. No construction agent may invoke target evaluation. All paths below are absolute; `selected_candidate` is an absolute candidate directory. Hash values are lowercase SHA-256 hex strings. The manifest is integrity custody, not cryptographic isolation.

Required manifest shape:

```json
{
  "schema_version": "m10-campaign-freeze-1",
  "status": "frozen_before_target_analysis",
  "target_outcomes_inspected": false,
  "frozen_utc": "ISO-8601 timestamp",
  "residual_seeds": [92101, 92102, 92103],
  "bindings": [{"path": "ABSOLUTE_PATH", "sha256": "64 hex characters"}],
  "cases": {
    "nhanes_insulin": {
      "observed_path": "S/nhanes_insulin/visible/observed.csv",
      "reference_path": "S/nhanes_insulin/custodian/reference.csv",
      "prepare_reader_path": "S/nhanes_insulin/prepare.py",
      "demo_path": "S/nhanes_insulin/custodian/raw/DEMO_I.xpt",
      "fasting_design_path": "S/nhanes_insulin/custodian/raw/GLU_I.xpt"
    },
    "pns_hba1c": {
      "observed_path": "S/pns_hba1c/visible/observed.csv",
      "reference_path": "S/pns_hba1c/custodian/reference.csv",
      "weights_path": "S/pns_hba1c/custodian/design_weights.csv",
      "id_mapping_path": "S/pns_hba1c/custodian/id_mapping.csv"
    }
  },
  "constructions": [{
    "construction_id": "ia",
    "case_id": "nhanes_insulin",
    "bundle_path": "ABSOLUTE_BUNDLE_DIRECTORY",
    "initial_candidate": "ABSOLUTE_INITIAL_CANDIDATE_DIRECTORY",
    "selected_candidate": "ABSOLUTE_FINAL_CANDIDATE_DIRECTORY",
    "final_selection_path": "ABSOLUTE_FINAL_SELECTION_JSON",
    "outputs": [{
      "path": "ABSOLUTE_BUNDLE/executions/UNIQUE_RUN/output/generated.csv",
      "sha256": "64 hex characters",
      "seed": 92101,
      "receipt_path": "ABSOLUTE_BUNDLE/executions/UNIQUE_RUN/execution.json",
      "receipt_sha256": "64 hex characters",
      "run_id": "UNIQUE_RUN"
    }]
  }]
}
```

Replace `S/...` examples with absolute paths. Exactly four constructions are required: `ia`, `ib` for NHANES; `ha`, `hb` for PNS. Each requires exactly the three frozen residual seeds, twelve distinct output paths and twelve distinct `(bundle_path, run_id)` pairs. Run IDs are scoped to a bundle and may recur across independent bundles. Identical content hashes are permitted because deterministic generators may ignore a seed; this is reported, never mistaken for independent evidence. Both initial and selected candidates are verified recursively using the existing harness. Every selected output must have a successful, verified execution receipt matching its candidate, seed, path, run ID and recorded output hash. Candidate source replays remain bound through the final selection document and candidate lineage; the controller records their admission review before making this manifest.

The binding list must include all case paths above; each bundle's `observed.csv`, `task.json`, initial/selected `freeze.json`, and `final_selection_path`; every evaluator `.py` file, this interface and `INFERENCE.md`; the frozen `methods/analytical_points.py`; both original case protocols, `endpoint_evidence_map.json`, `campaign_feasibility_v2.json`; and the active protocol/campaign/shared-input manifests. These last controller artifacts are explicitly supplied as nonempty `controller_binding_paths` (array of absolute file paths) and must occur in `bindings`. The evaluator requires every listed binding's bytes unchanged. Reserved references are hashed as opaque bytes during gate verification and are parsed only after all gates pass.

NHANES reference header (inspected without values): `row_id,SEQN,fasting_insulin_uU_ml,LBDINSI,LBDINLC,SDMVSTRA,SDMVPSU,WTSAF2YR,WTSAF2YR_GLU,WTMEC2YR,WTINT2YR,RIDSTATR,PHDSESN,PHAFSTHR,PHAFSTMN,fasting_hours,RIDEXPRG,DIQ010,DIQ050,LBDGLUSI`. No separate NHANES ID-map or design CSV exists: mapping/design for eligible rows are in the reference. Full-design rows are built from only DEMO SEQN/SDMVSTRA/SDMVPSU and GLU SEQN/WTSAF2YR, retaining every finite positive fasting-weight record before domain selection. The existing preparation reader handles XPORT exact zero decoding. PNS reference header is `row_id,age_years,sex,bmi_kg_m2,hba1c_pct`; weights header `row_id,peso_lab`; mapping header `row_id,source_archive_sha256,source_member,source_sheet,source_excel_row`.

Builder final-selection JSON must contain `selected_candidate` as the candidate name, bundle-relative path or same absolute path, and `target_outcomes_read: false`. If `target_feedback_used` is present it must also be false. Preserve the builder's original decision record. This gate checks actual evidence bindings and harness receipts; it does not accept a bare Boolean claim that candidates or execution were verified.
