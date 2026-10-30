"""M11 custody-only preparation. Never print target values or summaries."""
from __future__ import annotations

import datetime
import hashlib
import hmac
import json
from pathlib import Path
import platform
import secrets
import urllib.request

import numpy as np
import pandas as pd
import pandas.io.sas.sas_xport as xport_reader

HERE = Path(__file__).resolve().parent
PRIVATE = HERE / "private"
VISIBLE = HERE / "visible"
BASE = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def xport_exact_zero(path: Path) -> pd.DataFrame:
    """Decode only IBM all-zero encodings correctly; preserve pandas otherwise."""
    original = xport_reader._parse_float_vec

    def corrected(vec):
        result = original(vec)
        raw_zero = np.ascontiguousarray(vec).view(">u8").reshape(-1) == 0
        result[raw_zero] = 0.0
        return result

    probe = np.array([bytes.fromhex(h) for h in [
        "0000000000000000", "4110000000000000", "4120000000000000", "c110000000000000"
    ]], dtype="S8")
    assert np.array_equal(corrected(probe), np.array([0.0, 1.0, 2.0, -1.0]))
    assert np.array_equal(corrected(probe)[1:], original(probe)[1:])
    xport_reader._parse_float_vec = corrected
    try:
        return pd.read_sas(path, format="xport", encoding="utf-8")
    finally:
        xport_reader._parse_float_vec = original


def acquire() -> list[dict]:
    manifest = []
    for stem in ["DEMO_L", "BMX_L", "GHB_L"]:
        for extension, folder in [("htm", "documentation"), ("xpt", "raw")]:
            url = BASE + stem + "." + extension
            path = PRIVATE / folder / (stem + "." + extension)
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                raise RuntimeError("Existing acquisition detected; preserve it and review before rerunning.")
            request = urllib.request.Request(url, headers={"User-Agent": "M11-research-custodian/1.0"})
            with urllib.request.urlopen(request, timeout=60) as response:
                content = response.read()
                item = {
                    "dataset": stem, "kind": "official_codebook" if extension == "htm" else "official_XPT",
                    "url": url, "final_url": response.url, "status": response.status,
                    "content_type": response.headers.get("Content-Type"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "retrieved_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "path": str(path.relative_to(HERE)).replace("\\", "/"),
                    "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()
                }
            if extension == "xpt":
                assert content.startswith(b"HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!"), "Invalid SAS transport header"
            path.write_bytes(content)
            manifest.append(item)
            dump(PRIVATE / "source_manifest.json", {"records": manifest})
    return manifest


def main() -> None:
    spec_path = HERE / "preparation_spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    PRIVATE.mkdir(parents=True, exist_ok=True)
    VISIBLE.mkdir(parents=True, exist_ok=True)
    freeze_path = PRIVATE / "pre_read_freeze_v2.json"
    if freeze_path.exists():
        raise RuntimeError("Preparation already started; do not overwrite frozen inputs or artifacts.")
    freeze = {
        "frozen_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "preparation_spec_sha256": sha(spec_path), "preparation_script_sha256": sha(Path(__file__)),
        "freshness_access_manifest_sha256": sha(HERE / "freshness_access_manifest.json"),
        "scope": "Technical parser repair frozen before first participant parse; raw files were acquired opaque under the original freeze. Selection rules are unchanged.",
        "prior_freeze_sha256": sha(PRIVATE / "pre_read_freeze.json"),
        "technical_repair_sha256": sha(HERE / "technical_repair.json"),
        "authorization": spec["authorization"]
    }
    dump(freeze_path, freeze)
    acquisition = json.loads((PRIVATE / "source_manifest.json").read_text(encoding="utf-8"))["records"]
    assert len(acquisition) == 6, "Incomplete opaque acquisition"
    for item in acquisition:
        assert sha(HERE / item["path"]) == item["sha256"], "Acquisition hash mismatch"
    original_freeze = json.loads((PRIVATE / "pre_read_freeze.json").read_text(encoding="utf-8"))
    assert sha(spec_path) == original_freeze["preparation_spec_sha256"], "Selection spec changed"
    assert sha(HERE / "prepare_target.py") == original_freeze["preparation_script_sha256"], "Historical script changed"
    need = {
        "DEMO_L": ["SEQN", "RIDAGEYR", "RIAGENDR", "SDMVSTRA", "SDMVPSU"],
        "BMX_L": ["SEQN", "BMXBMI"],
        "GHB_L": ["SEQN", "WTPH2YR", "LBXGH"]
    }
    frames = {}
    for stem, columns in need.items():
        data = xport_exact_zero(PRIVATE / "raw" / (stem + ".xpt"))
        assert set(columns).issubset(data.columns), "Required source metadata field missing"
        assert data.SEQN.notna().all() and data.SEQN.is_unique, "Source ID integrity failure"
        frames[stem] = data[columns].copy()
    joined = frames["DEMO_L"].merge(frames["BMX_L"], on="SEQN", how="left", validate="one_to_one")
    joined = joined.merge(frames["GHB_L"], on="SEQN", how="left", validate="one_to_one")
    covariate_eligible = (
        joined.RIDAGEYR.between(*spec["age_inclusive"])
        & joined.RIAGENDR.isin(spec["sex_codes"])
        & np.isfinite(joined.BMXBMI) & joined.BMXBMI.gt(0)
        & np.isfinite(joined.WTPH2YR) & joined.WTPH2YR.gt(0)
    )
    base = joined.loc[covariate_eligible].copy()
    assert not base.LBXGH.eq(0).any(), "Official no-lab-result zero code requires an availability-rule clarification; no values released."
    available = np.isfinite(base.LBXGH)
    # Availability alone establishes the paired evaluation set. No target magnitudes
    # are examined for selection, fitted, summarized, or transmitted to the builder.
    selected = base.loc[available].copy()
    assert len(selected) > 0, "No paired eligible rows"
    assert np.isfinite(selected.SDMVSTRA).all() and np.isfinite(selected.SDMVPSU).all(), "Design fields unavailable"
    key = secrets.token_bytes(32)
    (PRIVATE / "row_id_key.bin").write_bytes(key)
    selected["row_id"] = ["row_" + hmac.new(key, str(int(v)).encode("ascii"), hashlib.sha256).hexdigest()[:24] for v in selected.SEQN]
    selected = selected.sort_values("row_id", kind="stable").reset_index(drop=True)
    assert selected.row_id.is_unique, "Opaque ID collision"
    observed = pd.DataFrame({
        "row_id": selected.row_id, "age_years": selected.RIDAGEYR.astype(int),
        "sex": selected.RIAGENDR.map({1: "male", 2: "female"}), "bmi_kg_m2": selected.BMXBMI
    })
    design = pd.DataFrame({
        "row_id": selected.row_id, "weight": selected.WTPH2YR,
        "stratum": selected.SDMVSTRA.astype(int), "psu": selected.SDMVPSU.astype(int)
    })
    reference = pd.DataFrame({"row_id": selected.row_id, "hba1c_pct": selected.LBXGH})
    mapping = selected[["row_id", "SEQN"]].copy()
    assert observed.columns.tolist() == spec["visible_columns"]
    assert design.columns.tolist() == spec["controller_design_columns"]
    assert reference.columns.tolist() == spec["private_reference_columns"]
    artifacts = {
        "observed": (VISIBLE / "observed.csv", observed),
        "design_weights": (PRIVATE / "design_weights.csv", design),
        "reference": (PRIVATE / "reference.csv", reference),
        "id_mapping": (PRIVATE / "id_mapping.csv", mapping)
    }
    artifact_manifest = {}
    for name, (path, frame) in artifacts.items():
        frame.to_csv(path, index=False, lineterminator="\n", float_format="%.17g")
        roundtrip = pd.read_csv(path, float_precision="round_trip")
        assert roundtrip.columns.tolist() == frame.columns.tolist(), "Serialized schema failure"
        assert roundtrip.row_id.equals(observed.row_id), "Serialized alignment failure"
        for col in frame.select_dtypes(include="number").columns:
            assert np.array_equal(roundtrip[col].to_numpy(), frame[col].to_numpy()), "Numeric round-trip failure"
        artifact_manifest[name] = {"path": str(path.relative_to(HERE)).replace("\\", "/"), "sha256": sha(path), "bytes": path.stat().st_size, "rows": len(frame)}
    # Eligibility counts are recorded in custody. They are not target distribution statistics.
    private_manifest = {
        "schema_version": 1, "task_id": spec["task_id"],
        "prepared_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "pre_read_freeze": freeze, "official_acquisition": acquisition,
        "selection_spec": spec,
        "eligibility": {"covariate_and_weight_eligible_rows": len(base), "paired_observable_rows": len(selected), "omitted_for_nonfinite_target_availability": int((~available).sum())},
        "artifacts": artifact_manifest,
        "versions": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
        "validation": {"unique_source_ids": True, "one_to_one_joins": True, "unique_opaque_ids": True, "exact_numeric_serialization": True, "observed_design_reference_row_alignment": True, "positive_phlebotomy_weights": True, "complete_design_fields": True, "no_scientific_model_fit": True, "no_target_statistics_computed": True},
        "exposure": {"public_codebook_frequency_sections_seen_by_custodian": True, "participant_values_in_tool_outputs": False, "new_hba1c_endpoint_not_new_survey_or_guaranteed_new_participants": True}
    }
    dump(PRIVATE / "preparation_manifest.json", private_manifest)
    safe = {
        "schema_version": 1, "task_id": spec["task_id"], "n_rows": len(observed),
        "source_survey": "NHANES August 2021-August 2023",
        "visible_columns": spec["visible_columns"], "hidden_target": "hba1c_pct", "hidden_target_unit": "percent",
        "observed_sha256": artifact_manifest["observed"]["sha256"],
        "eligibility": "Adults aged 20-79, sex codes 1/2, finite positive measured BMI and phlebotomy weight; finite measured HbA1c establishes paired evaluation availability only. No pregnancy, diagnosis, or target-magnitude exclusions.",
        "age_definition": "Age at screening; age-80 topcode avoided by prespecified upper age 79.",
        "sex_mapping": {"1": "male", "2": "female"},
        "design": "WTPH2YR, SDMVSTRA and SDMVPSU retained separately in controller custody; primary metrics are descriptive weighted point estimates.",
        "freshness_limit": "New project HbA1c endpoint under bounded audit; the NHANES cycle and potentially participant covariates were previously used for TG.",
        "exposure_limit": "Preparation custodian saw public CDC codebook frequency/range sections; no target values or target summaries are included in the builder package. Public-data pretraining exposure cannot be excluded.",
        "information_boundary": spec["information_boundary"],
        "scientific_model_fit": False
    }
    dump(VISIBLE / "task_safe_manifest.json", safe)
    receipt = {"task_id": spec["task_id"], "n_rows": len(observed), "artifacts": artifact_manifest,
               "task_safe_manifest_sha256": sha(VISIBLE / "task_safe_manifest.json"),
               "private_preparation_manifest_sha256": sha(PRIVATE / "preparation_manifest.json"),
               "pre_read_freeze_sha256": sha(freeze_path),
               "no_target_values_or_statistics_in_receipt": True}
    dump(HERE / "preparation_receipt.json", receipt)
    print(json.dumps({"prepared": True, "n_rows": len(observed), "receipt": str(HERE / "preparation_receipt.json"), "visible_observed_sha256": artifact_manifest["observed"]["sha256"]}))


if __name__ == "__main__":
    main()
