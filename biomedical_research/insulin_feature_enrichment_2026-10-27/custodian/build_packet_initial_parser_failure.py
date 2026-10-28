"""Freeze a blinded whole-feature enrichment packet without outcome analyses.

Allowed target operations: finite/positive and documented detection-code checks,
selection, exact copying, file integrity hashing. No target distribution summaries,
correlations, regressions, or generation model are performed here.
"""
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

BASE = Path(__file__).resolve().parent
SHARED = BASE.parent / "shared"
LOCKED = BASE / "locked"
PROTOCOL = BASE / "eligibility_frozen.json"
SOURCE_MANIFEST = BASE / "source_manifest.json"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def main():
    if (LOCKED / "freeze_manifest.json").exists():
        raise RuntimeError("Frozen packet already exists. Do not regenerate or overwrite it.")
    LOCKED.mkdir(exist_ok=True)
    SHARED.mkdir(exist_ok=True)
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    approval = {"frozen_utc": datetime.now(timezone.utc).isoformat(),
                "eligibility_sha256": sha(PROTOCOL),
                "build_script_sha256": sha(Path(__file__)),
                "target_data_read_before_this_freeze": False,
                "outcome_summaries_calculated": False}
    save_json(LOCKED / "pre_read_freeze.json", approval)
    os.chmod(PROTOCOL, stat.S_IREAD)
    source_manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    for source in source_manifest["sources"]:
        path = BASE / source["file"]
        if sha(path) != source["sha256"]:
            raise RuntimeError(f"Source checksum mismatch: {path.name}")
    requested = {
        "DEMO_J": ["SEQN", "RIDAGEYR", "RIAGENDR", "RIDEXPRG", "SDMVSTRA", "SDMVPSU"],
        "BMX_J": ["SEQN", "BMXBMI"],
        "INS_J": ["SEQN", "WTSAF2YR", "LBXIN", "LBDINLC"],
        "DIQ_J": ["SEQN", "DIQ010", "DIQ050"],
    }
    frames = {}
    raw_row_counts = {}
    for name, columns in requested.items():
        frame = pd.read_sas(BASE / "raw" / (name + ".xpt"), format="xport")
        assert frame.SEQN.notna().all() and frame.SEQN.is_unique
        raw_row_counts[name] = len(frame)
        frames[name] = frame[columns].copy()
    merged = frames["DEMO_J"]
    for name in ["BMX_J", "INS_J", "DIQ_J"]:
        merged = merged.merge(frames[name], on="SEQN", how="left", validate="one_to_one")
    flow = [{"step": "DEMO_J records", "remaining": len(merged), "excluded_at_step": 0}]
    keep = pd.Series(True, index=merged.index)
    checks = {}
    def add_step(name, condition):
        nonlocal keep
        condition = condition.fillna(False)
        before = int(keep.sum())
        keep = keep & condition
        checks[name] = condition
        flow.append({"step": name, "remaining": int(keep.sum()), "excluded_at_step": before-int(keep.sum())})

    positive_weight = np.isfinite(merged.WTSAF2YR) & (merged.WTSAF2YR > 0)
    add_step("Positive finite fasting subsample weight", positive_weight)
    add_step("Age 20-79 inclusive", merged.RIDAGEYR.between(20, 79))
    add_step("Sex coded 1 or 2", merged.RIAGENDR.isin([1, 2]))
    add_step("Positive finite BMI", np.isfinite(merged.BMXBMI) & (merged.BMXBMI > 0))
    female_reproductive_age = merged.RIAGENDR.eq(2) & merged.RIDAGEYR.between(20, 44)
    other_female = merged.RIAGENDR.eq(2) & ~merged.RIDAGEYR.between(20, 44)
    pregnancy_pass = (~female_reproductive_age | merged.RIDEXPRG.eq(2)) & (~other_female | ~merged.RIDEXPRG.eq(1))
    add_step("Available pregnancy ascertainment rule", pregnancy_pass)
    add_step("DIQ010 in 2 or 3", merged.DIQ010.isin([2, 3]))
    add_step("No reported current insulin use: DIQ050 != 1", ~merged.DIQ050.eq(1))
    add_step("Positive finite measured insulin", np.isfinite(merged.LBXIN) & (merged.LBXIN > 0))
    if not merged.loc[keep, "LBDINLC"].isin([0, 1]).all():
        raise RuntimeError("Unexpected insulin detection flag; stop before creating packet.")
    if not np.isfinite(merged.loc[positive_weight, ["SDMVSTRA", "SDMVPSU"]]).all().all():
        raise RuntimeError("Positive-weight design spine has missing design variables.")

    # Fresh nonsemantic identifiers and shuffled row order; no SEQN-derived IDs.
    target = merged.loc[keep].copy()
    target["row_id"] = ["r_" + uuid.uuid4().hex for _ in range(len(target))]
    permutation = list(range(len(target)))
    secrets.SystemRandom().shuffle(permutation)
    target = target.iloc[permutation].reset_index(drop=True)
    observed = target[["row_id", "BMXBMI", "RIDAGEYR", "RIAGENDR"]].rename(columns={"BMXBMI": "bmi", "RIDAGEYR": "age", "RIAGENDR": "sex"})
    observed[["age", "sex"]] = observed[["age", "sex"]].astype(int)
    assert list(observed.columns) == protocol["generator_columns"]
    assert observed.row_id.is_unique and observed.notna().all().all()
    observed.to_csv(SHARED / "observed.csv", index=False)

    reference = observed.copy()
    reference["insulin_uU_mL"] = target.LBXIN.to_numpy()
    reference["insulin_below_lod"] = target.LBDINLC.astype(int).to_numpy()
    reference.to_csv(LOCKED / "reference.csv", index=False)
    id_by_seqn = dict(zip(target.SEQN, target.row_id))
    spine = merged.loc[positive_weight, ["SEQN", "WTSAF2YR", "SDMVSTRA", "SDMVPSU"]].copy()
    spine["design_id"] = ["d_" + uuid.uuid4().hex for _ in range(len(spine))]
    spine["row_id"] = spine.SEQN.map(id_by_seqn)
    spine["in_target_domain"] = spine.SEQN.isin(id_by_seqn).astype(int)
    linkage = spine[["SEQN", "design_id", "row_id", "in_target_domain"]].copy()
    linkage.SEQN = linkage.SEQN.astype(int)
    linkage.to_csv(LOCKED / "linkage_private.csv", index=False)
    spine = spine[["design_id", "row_id", "in_target_domain", "WTSAF2YR", "SDMVSTRA", "SDMVPSU"]].rename(columns={"WTSAF2YR": "fasting_weight", "SDMVSTRA": "stratum", "SDMVPSU": "psu"})
    spine[["stratum", "psu"]] = spine[["stratum", "psu"]].astype(int)
    spine.to_csv(LOCKED / "design_spine.csv", index=False)

    schema = {
        "version": "1.0", "file": "observed.csv", "row_count": len(observed),
        "columns": {
            "row_id": {"type": "string", "meaning": "Fresh random pseudonymous row key; contains no original record identifier"},
            "bmi": {"type": "number", "unit": "kg/m^2", "meaning": "Body mass index from measured height and weight"},
            "age": {"type": "integer", "unit": "years", "meaning": "Age at screening, 20 through 79 inclusive"},
            "sex": {"type": "integer", "coding": {"1": "male", "2": "female"}, "meaning": "Source demographic sex coding"}
        },
        "feature_to_generate": {"name": "insulin_uU_mL", "unit": "uU/mL (microIU/mL)", "meaning": "Fasting serum insulin concentration", "entire_column_hidden": True},
        "required_output_key": "row_id", "missing_observed_values": False,
        "generation_scope": "Use only these observed covariates and independently obtained external aggregate literature. Do not identify participants or retrieve hidden source microdata."
    }
    save_json(SHARED / "schema.json", schema)
    target_description = """# Blinded fasting-insulin feature enrichment packet

This packet contains adults from a U.S. national health-examination probability sample collected in 2017-2018. Each row has measured BMI, screening age, and the source's sex coding. The fasting-serum-insulin column is entirely withheld. Generate it in uU/mL (microIU/mL), retaining each random row_id.

Eligibility was fixed before inspecting outcome distributions: age 20-79; positive fasting-subsample weight (the source's 8 to less than 24 hour fasting criterion); finite positive BMI and a reserved valid insulin measurement; male/female source code; no self-reported diagnosed diabetes (borderline status retained); and no reported current insulin use. Women aged 20-44 must have documented nonpregnancy at examination. Other women have identified pregnancy excluded, but public pregnancy ascertainment outside ages 20-44 is limited. No exclusion based on reported diabetic pills was applied.

The serum assay used a Tosoh AIA two-site immunoenzymometric method. Concentration is expressed in uU/mL; the reported detection limit is 1.0 uU/mL. The reference preserves the source's released handling of results below detection. These are assay facts, not summaries of this target cohort.

Use the observed.csv and schema.json files plus your independently retrieved external aggregate literature. Original record identifiers, hidden outcome data, target outcome summaries, and survey design variables are unavailable for generation. Do not search for participant matches, retrieve source individual-level insulin data, inspect custodian files, or infer record identity from covariates. This blinding is enforced by task instructions; a shared local filesystem is not a technical access sandbox.

This is a paired complete-case pilot of scientific-analysis utility. The source weights do not automatically repair remaining item nonresponse. Do not interpret the packet alone as an unconditional population estimate or use unobserved disease states as known covariates.
"""
    (SHARED / "target_description.md").write_text(target_description, encoding="utf-8")
    selection = {"created_utc": datetime.now(timezone.utc).isoformat(), "raw_row_counts": raw_row_counts,
                 "sequential_flow": flow, "final_target_rows": len(target), "positive_weight_design_rows": len(spine),
                 "target_rows_with_DIQ050_missing": int(target.DIQ050.isna().sum()),
                 "target_rows_with_DIQ050_unknown_or_refused": int(target.DIQ050.isin([7, 9]).sum()),
                 "insulin_values_disclosed": False, "outcome_distribution_statistics_computed": False,
                 "pills_metadata_inspected": False, "historical_local_2017_insulin_analyses_used": False}
    save_json(LOCKED / "selection_flow.json", selection)
    private_schema = {
        "reference.csv": {"columns": list(reference.columns), "rows": len(reference), "purpose": "Reserved true outcome and observed rows; never generator-visible"},
        "design_spine.csv": {"columns": list(spine.columns), "rows": len(spine), "purpose": "All positive-weight fasting-subsample design records; retain out-of-domain records in Taylor variance estimation. row_id is populated only in domain."},
        "linkage_private.csv": {"columns": list(linkage.columns), "rows": len(linkage), "purpose": "Custodian-only identity linkage, unnecessary for evaluator scientific analysis"},
        "survey_guidance": {"weight": "fasting_weight = WTSAF2YR", "stratum": "stratum = SDMVSTRA", "psu": "psu = SDMVPSU nested in stratum", "domain": "in_target_domain", "method": "Use a survey-aware domain estimator, preserving the complete positive-weight design spine. No weight rescaling for a single two-year cycle."},
        "blinding": "Parent receives counts and integrity hashes only until evaluation is authorized. Generator receives shared files only. Evaluator may receive reference and design spine after generation/evaluation protocol freeze."
    }
    save_json(LOCKED / "private_schema.json", private_schema)
    frozen_paths = [PROTOCOL, SOURCE_MANIFEST, Path(__file__), BASE / "acquire_sources.py"] + sorted(LOCKED.glob("*")) + [SHARED / name for name in ["observed.csv", "schema.json", "target_description.md"]]
    frozen_paths += sorted((BASE / "raw").glob("*.xpt"))
    manifest = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "protocol_version": "1.0", "files": [],
                "lock_meaning": "SHA256 integrity freeze and read-only filesystem attributes; procedural role blinding, not an adversarial OS access control boundary.",
                "target_outcome_statistics_computed": False,
                "rows": {"target": len(target), "design_spine": len(spine)},
                "runtime": {"python": __import__("sys").version.split()[0], "pandas": pd.__version__, "numpy": np.__version__}}
    for path in frozen_paths:
        manifest["files"].append({"path_relative_to_pilot": str(path.relative_to(BASE.parent)).replace("\\", "/"), "bytes": path.stat().st_size, "sha256": sha(path)})
        os.chmod(path, stat.S_IREAD)
    save_json(LOCKED / "freeze_manifest.json", manifest)
    os.chmod(LOCKED / "freeze_manifest.json", stat.S_IREAD)
    print(json.dumps({"selection": selection, "shared_schema": schema, "freeze_manifest_sha256": sha(LOCKED / "freeze_manifest.json"), "frozen_files": manifest["files"]}, indent=2))

if __name__ == "__main__":
    main()
