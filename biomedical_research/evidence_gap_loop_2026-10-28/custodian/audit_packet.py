"""Metadata and exact-copy audit only; never calculate target summaries/relations."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import pandas.io.sas.sas_xport as sas_xport
from build_packet import zero_guard, sha, save
from evaluate import read_csv, valid_observed, match_generated, number

BASE = Path(__file__).resolve().parent
PILOT = BASE.parent

def main():
    manifest = json.loads((BASE/"locked/freeze_manifest.json").read_text())
    for item in manifest["files"]:
        assert sha(PILOT/item["path"]) == item["sha256"]
    observed = read_csv(PILOT/"shared/observed.csv")
    valid_observed(observed)
    reference = read_csv(BASE/"locked/reference.csv")
    match_generated(observed, reference)
    linkage = pd.read_csv(BASE/"locked/linkage_private.csv")
    spine = pd.read_csv(BASE/"locked/design_spine.csv", float_precision="round_trip")
    assert linkage.design_id.is_unique and spine.design_id.is_unique
    assert set(linkage.design_id) == set(spine.design_id)
    assert set(linkage.loc[linkage.in_target_domain == 1, "row_id"]) == set(observed.row_id)
    assert spine.loc[spine.in_target_domain == 0, "row_id"].isna().all()
    sas_xport._parse_float_vec = zero_guard
    d = pd.read_sas(BASE/"raw/DEMO_H.xpt", format="xport")
    b = pd.read_sas(BASE/"raw/BMX_H.xpt", format="xport")
    h = pd.read_sas(BASE/"raw/HDL_H.xpt", format="xport")
    f = d.merge(b[["SEQN", "BMXBMI"]], on="SEQN", how="left", validate="one_to_one").merge(h[["SEQN", "LBDHDD"]], on="SEQN", how="left", validate="one_to_one")
    wt = np.isfinite(f.WTMEC2YR) & (f.WTMEC2YR > 0)
    female = f.RIAGENDR == 2
    reproductive = f.RIDAGEYR.between(20, 44)
    pregnancy = (~(female & reproductive) | (f.RIDEXPRG == 2)) & (~(female & ~reproductive) | (f.RIDEXPRG != 1))
    eligible = wt & f.RIDAGEYR.between(20, 79) & f.RIAGENDR.isin([1, 2]) & np.isfinite(f.BMXBMI) & (f.BMXBMI > 0) & pregnancy & np.isfinite(f.LBDHDD) & (f.LBDHDD > 0)
    assert set(f.loc[eligible, "SEQN"]) == set(linkage.loc[linkage.in_target_domain == 1, "SEQN"])
    assert set(f.loc[wt, "SEQN"]) == set(linkage.SEQN)
    target_map = linkage[linkage.in_target_domain == 1].set_index("row_id").loc[observed.row_id]
    raw_aligned = f.set_index("SEQN").loc[target_map.SEQN]
    ref_aligned = reference.set_index("row_id").loc[observed.row_id]
    for column, raw_column in [("hdl", "LBDHDD"), ("bmi", "BMXBMI"), ("age", "RIDAGEYR"), ("sex", "RIAGENDR")]:
        np.testing.assert_array_equal(number(ref_aligned, column), raw_aligned[raw_column].to_numpy())
    all_aligned = f.set_index("SEQN").loc[linkage.SEQN]
    spine_aligned = spine.set_index("design_id").loc[linkage.design_id]
    for column, raw_column in [("weight", "WTMEC2YR"), ("stratum", "SDMVSTRA"), ("psu", "SDMVPSU")]:
        np.testing.assert_array_equal(spine_aligned[column].to_numpy(), all_aligned[raw_column].to_numpy())
    shared_files = sorted(p.name for p in (PILOT/"shared").iterdir() if p.is_file())
    report = {"passed": True, "target_rows": len(observed), "full_design_rows": len(spine),
              "checks": ["All frozen hashes unchanged", "Observed strict allowlist", "Exact source-to-reference numeric preservation",
                         "All and only prespecified eligible rows", "Complete positive-weight examination design spine",
                         "Original source IDs absent from observed packet", "Random row IDs match exactly across observed/reference/design", "Survey weights and design codes preserved exactly"],
              "target_distribution_summaries_computed": False, "target_associations_computed": False,
              "shared_files_at_audit": shared_files}
    save(BASE/"packet_audit_report.json", report)
    save(BASE/"evaluation_release_contract.json", {
        "all_four_constructions_frozen": False, "root_authorized_evaluation": False, "no_builder_access_to_target": False,
        "analysis_spec_sha256": sha(BASE/"analysis_spec.json"), "evaluator_sha256": sha(BASE/"evaluate.py"),
        "artifacts": {}, "artifacts_schema": "Pilot-relative-path to SHA256 map binding controller, protocol, all run inputs including contract/observed/gateway, and each run.json, initial/final freeze, gateway snapshots, reviews/receipt, execution.json",
        "outputs": [], "output_entry_schema": {"construction": "ordinary_1, ordinary_2, gap_1, or gap_2", "arm": "ordinary or gap_policy",
            "stage": "initial or final", "draw": "integer 1..5", "seed": "corresponding protocol seed 281001..281005", "file": "relative to pilot root", "sha256": "hash of frozen generated CSV"},
        "requirement": "40 distinct canonical output paths and construction/stage/draw slots, bound to actual execution receipts; four distinct run paths and fixed policy; all candidate/run/review/controller/gateway hashes and seed schedule verified before hidden reference read",
        "execution_after_root_authorization_only": "python custodian/evaluate.py --release custodian/evaluation_release.json"})
    print(json.dumps(report))

if __name__ == "__main__":
    main()
