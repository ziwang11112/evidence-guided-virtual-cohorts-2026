"""Prepare masked records. Allowed outcome operations: validity, copying, hashing."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import secrets
import stat
import uuid
import numpy as np
import pandas as pd
import pandas.io.sas.sas_xport as sas_xport

BASE = Path(__file__).resolve().parent
SHARED = BASE.parent / "shared"
LOCKED = BASE / "locked"

ORIGINAL_PARSE_FLOAT = sas_xport._parse_float_vec
def zero_guard(vec):
    result = ORIGINAL_PARSE_FLOAT(vec)
    words = vec.view(dtype=np.dtype(">u4,>u4"))
    result[((words["f0"] & 0x00FFFFFF) == 0) & (words["f1"] == 0)] = 0.0
    return result

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+"\n", encoding="utf-8")

def main():
    LOCKED.mkdir(exist_ok=True)
    SHARED.mkdir(exist_ok=True)
    if (LOCKED / "freeze_manifest.json").exists():
        raise RuntimeError("Packet already frozen; never regenerate")
    files_before_read = [BASE / x for x in ["eligibility_frozen.json", "analysis_spec.json", "evaluate.py", "build_packet.py", "acquire_sources.py"]]
    freeze = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "target_data_parsed_before_freeze": False,
              "authorized_by": "Parent agent explicit message, 2026-10-28; all model outputs must freeze before evaluation",
              "files": {p.name: sha(p) for p in files_before_read}}
    freeze_path = LOCKED / "pre_read_freeze.json"
    if freeze_path.exists():
        assert json.loads(freeze_path.read_text())["files"] == freeze["files"]
    else:
        save(freeze_path, freeze)
    for path in files_before_read + [freeze_path]:
        os.chmod(path, stat.S_IREAD)
    source_manifest = json.loads((BASE / "source_manifest.json").read_text())
    for source in source_manifest["sources"]:
        assert sha(BASE / source["file"]) == source["sha256"]
    synthetic = np.frombuffer(bytes.fromhex("00000000000000004110000000000000c1100000000000004120000000000000"), dtype="S8")
    assert np.array_equal(zero_guard(synthetic), [0, 1, -1, 2])
    sas_xport._parse_float_vec = zero_guard
    requests = {
        "DEMO_H": ["SEQN", "RIDAGEYR", "RIAGENDR", "RIDEXPRG", "WTMEC2YR", "SDMVSTRA", "SDMVPSU"],
        "BMX_H": ["SEQN", "BMXBMI"], "HDL_H": ["SEQN", "LBDHDD"]}
    frames, raw_counts = {}, {}
    for name, columns in requests.items():
        f = pd.read_sas(BASE / "raw" / (name+".xpt"), format="xport")
        assert f.SEQN.notna().all() and f.SEQN.is_unique
        raw_counts[name] = len(f)
        frames[name] = f[columns].copy()
    merged = frames["DEMO_H"].merge(frames["BMX_H"], on="SEQN", how="left", validate="one_to_one").merge(frames["HDL_H"], on="SEQN", how="left", validate="one_to_one")
    keep = pd.Series(True, index=merged.index)
    flow = [{"step": "DEMO_H records", "remaining": len(merged), "excluded_at_step": 0}]
    def select(name, condition):
        nonlocal keep
        before = int(keep.sum())
        keep &= condition.fillna(False)
        flow.append({"step": name, "remaining": int(keep.sum()), "excluded_at_step": before-int(keep.sum())})
    positive_weight = np.isfinite(merged.WTMEC2YR) & (merged.WTMEC2YR > 0)
    select("Positive finite MEC examination weight", positive_weight)
    select("Age 20-79 inclusive", merged.RIDAGEYR.between(20, 79))
    select("Sex code 1 or 2", merged.RIAGENDR.isin([1, 2]))
    select("Positive finite BMI", np.isfinite(merged.BMXBMI) & (merged.BMXBMI > 0))
    female_20_44 = merged.RIAGENDR.eq(2) & merged.RIDAGEYR.between(20, 44)
    other_female = merged.RIAGENDR.eq(2) & ~merged.RIDAGEYR.between(20, 44)
    select("Available pregnancy ascertainment rule", (~female_20_44 | merged.RIDEXPRG.eq(2)) & (~other_female | ~merged.RIDEXPRG.eq(1)))
    select("Positive finite reserved HDL measurement", np.isfinite(merged.LBDHDD) & (merged.LBDHDD > 0))
    assert np.isfinite(merged.loc[positive_weight, ["SDMVSTRA", "SDMVPSU"]]).all().all()
    target = merged.loc[keep].copy()
    target["row_id"] = ["r_"+uuid.uuid4().hex for _ in range(len(target))]
    order = list(range(len(target)))
    secrets.SystemRandom().shuffle(order)
    target = target.iloc[order].reset_index(drop=True)
    observed = target[["row_id", "BMXBMI", "RIDAGEYR", "RIAGENDR"]].rename(columns={"BMXBMI": "bmi", "RIDAGEYR": "age", "RIAGENDR": "sex"})
    observed[["age", "sex"]] = observed[["age", "sex"]].astype(int)
    observed.to_csv(SHARED / "observed.csv", index=False)
    reference = observed.copy()
    reference["hdl"] = target.LBDHDD.to_numpy()
    reference.to_csv(LOCKED / "reference.csv", index=False)
    id_by_seqn = dict(zip(target.SEQN, target.row_id))
    spine = merged.loc[positive_weight, ["SEQN", "WTMEC2YR", "SDMVSTRA", "SDMVPSU"]].copy()
    spine["design_id"] = ["d_"+uuid.uuid4().hex for _ in range(len(spine))]
    spine["row_id"] = spine.SEQN.map(id_by_seqn)
    spine["in_target_domain"] = spine.SEQN.isin(id_by_seqn).astype(int)
    linkage = spine[["SEQN", "design_id", "row_id", "in_target_domain"]].copy()
    linkage.SEQN = linkage.SEQN.astype(int)
    linkage.to_csv(LOCKED / "linkage_private.csv", index=False)
    spine = spine.drop(columns="SEQN").rename(columns={"WTMEC2YR": "weight", "SDMVSTRA": "stratum", "SDMVPSU": "psu"})
    spine[["stratum", "psu"]] = spine[["stratum", "psu"]].astype(int)
    spine.to_csv(LOCKED / "design_spine.csv", index=False)
    schema = {
        "version": "1.0", "file": "observed.csv", "row_count": len(observed),
        "observed_columns": ["row_id", "bmi", "age", "sex"], "outcome_column": "hdl",
        "allowed_output_columns": ["row_id", "bmi", "age", "sex", "hdl"],
        "columns": {
            "row_id": {"type": "string", "meaning": "Random nonsemantic key; no source ID"},
            "bmi": {"type": "number", "unit": "kg/m^2", "meaning": "BMI from measured weight and height"},
            "age": {"type": "integer", "unit": "years", "meaning": "Age at screening, 20-79"},
            "sex": {"type": "integer", "coding": {"1": "male", "2": "female"}}
        },
        "feature_to_generate": {"name": "hdl", "unit": "mg/dL", "meaning": "Serum direct HDL cholesterol", "entire_column_hidden": True},
        "output_contract": "Exactly one row per input row_id; preserve all observed numeric values exactly, permit reordered rows; finite positive hdl; no additional columns",
        "missing_observed_values": False,
        "evidence_scope": "Observed covariates and independently retrieved external aggregate literature only; no source individual-level data or participant matching"
    }
    save(SHARED / "schema.json", schema)
    target_description = """# Masked HDL cholesterol enrichment packet

Generate the wholly withheld serum HDL cholesterol feature, `hdl`, in mg/dL for each random `row_id`. The observed inputs are BMI measured in kg/m^2, age at screening in years, and source sex code (1 male; 2 female). Preserve observed numeric values exactly; return only row_id, bmi, age, sex and hdl.

The case is a U.S. national health-examination probability sample collected in 2013-2014. Eligibility was fixed from metadata: ages 20-79; positive examination weight; valid sex code; finite positive BMI and an available valid HDL result. Women aged 20-44 require documented nonpregnancy; reported pregnancy is excluded for other women, but public ascertainment outside ages 20-44 is limited. There are no disease, smoking, alcohol, lipid-therapy, or fasting exclusions. This is a paired complete-case benchmark; remaining item nonresponse is not automatically corrected by source weights.

The source documents a direct serum HDL enzymatic assay with magnesium/dextran sulfate and PEG-modified enzymes; Roche Modular P and Cobas 6000 instruments were used in this cycle. The reported lower detection limit is 3 mg/dL. These are measurement facts, not target cohort summaries.

Original survey IDs, the full HDL column, all target-outcome summaries, survey weights and design variables are withheld. Use only this packet and independently obtained external aggregate evidence. Do not retrieve the source individual-level data, match participants, inspect custodian files, or infer record identity from covariates. Role instructions enforce this blinding; the shared filesystem is not an access-control sandbox.

No synthetic value is an observed patient measurement. The comparison concerns scientific analysis utility in a small prospective pilot, not individual outcome recovery or unconditional national population estimation.
"""
    (SHARED / "target_description.md").write_text(target_description, encoding="utf-8")
    report = {"created_utc": datetime.now(timezone.utc).isoformat(), "raw_row_counts": raw_counts,
              "sequential_flow": flow, "final_target_rows": len(target), "full_design_rows": len(spine),
              "source_outcome_summaries_computed": False, "source_associations_evaluated": False,
              "data_preparation_operations_on_outcome": ["finite/positive validity", "row selection", "exact copying", "integrity hash"],
              "parser": "pandas SAS XPORT with audited raw IBM-float mantissa-zero guard; toy encodings 0,1,-1,2 validated"}
    save(LOCKED / "selection_flow.json", report)
    save(SHARED / "preparation_report.json", report)
    save(LOCKED / "private_schema.json", {
        "reference": "reference.csv: row_id, bmi, age, sex, hdl; target values private until release",
        "design_spine": "design_spine.csv: all positive WTMEC2YR records, weight/stratum/psu; row_id only for target domain; no weight rescaling",
        "linkage": "linkage_private.csv: source SEQN mapping; never supplied to builders or needed by evaluator",
        "evaluation_gate": "Requires an explicit all-output-freeze release manifest created after root authorization"})
    paths = files_before_read + [BASE / "source_manifest.json"] + list(LOCKED.glob("*.json")) + list(LOCKED.glob("*.csv"))
    paths += [SHARED / x for x in ["observed.csv", "schema.json", "target_description.md", "preparation_report.json"]]
    paths += sorted((BASE / "raw").glob("*.xpt"))
    manifest = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "target_statistics_computed": False,
                "lock_meaning": "SHA256 + read-only attributes; procedural role blinding, not an OS sandbox", "files": []}
    for path in paths:
        manifest["files"].append({"path": path.relative_to(BASE.parent).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size})
        os.chmod(path, stat.S_IREAD)
    save(LOCKED / "freeze_manifest.json", manifest)
    os.chmod(LOCKED / "freeze_manifest.json", stat.S_IREAD)
    print(json.dumps({"target_rows": len(target), "full_design_rows": len(spine), "freeze_manifest_sha256": sha(LOCKED / "freeze_manifest.json"), "outcome_statistics_computed": False}))

if __name__ == "__main__":
    main()
