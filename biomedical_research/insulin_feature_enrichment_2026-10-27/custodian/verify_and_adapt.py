"""Independent byte-decoder integrity checks and evaluator-only schema adapter."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
import stat

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
PILOT = BASE.parent
LOCKED = BASE / "locked"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def decode_ibm(raw):
    """Independent scalar arithmetic decoder; no pandas float conversion used."""
    raw = raw.ljust(8, b"\x00")
    if raw[0] in list(range(0x41, 0x5B)) + [0x5F, 0x2E] and raw[1:] == b"\x00" * 7:
        return math.nan
    bits = int.from_bytes(raw, "big")
    fraction = bits & ((1 << 56) - 1)
    if fraction == 0:
        return 0.0
    sign = -1.0 if (bits >> 63) else 1.0
    exponent = ((bits >> 56) & 0x7F) - 64
    return sign * math.ldexp(float(fraction), 4 * exponent - 56)

def independent_read(path, columns):
    # Pandas supplies transport schema/record boundaries only. The numeric data
    # conversion below is independent of its IBM-to-IEEE vector conversion.
    with pd.read_sas(path, format="xport", iterator=True) as reader:
        start, length, count = reader.record_start, reader.record_length, reader.nobs
        fields = {f["name"].decode("ascii"): f for f in reader.fields}
    data = path.read_bytes()
    decoded = {}
    for name in columns:
        field = fields[name]
        assert field["ntype"] == "numeric"
        offset, width = field["npos"], field["field_length"]
        decoded[name] = [decode_ibm(data[start+i*length+offset:start+i*length+offset+width]) for i in range(count)]
    return pd.DataFrame(decoded)

def main():
    assert decode_ibm(bytes(8)) == 0.0
    assert decode_ibm(bytes.fromhex("4110000000000000")) == 1.0
    assert decode_ibm(bytes.fromhex("c110000000000000")) == -1.0
    assert math.isnan(decode_ibm(bytes.fromhex("2e00000000000000")))
    frozen = json.loads((LOCKED / "freeze_manifest.json").read_text(encoding="utf-8"))
    for record in frozen["files"]:
        assert sha(PILOT / record["path_relative_to_pilot"]) == record["sha256"]
    spec = importlib.util.spec_from_file_location("custodian_build", BASE / "build_packet.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    columns = {
        "DEMO_J": ["SEQN", "RIDAGEYR", "RIAGENDR", "RIDEXPRG", "SDMVSTRA", "SDMVPSU"],
        "BMX_J": ["SEQN", "BMXBMI"],
        "INS_J": ["SEQN", "WTSAF2YR", "LBXIN", "LBDINLC"],
        "DIQ_J": ["SEQN", "DIQ010", "DIQ050"],
    }
    independent = {}
    for name, selected in columns.items():
        path = BASE / "raw" / (name + ".xpt")
        independent[name] = independent_read(path, selected)
        corrected = pd.read_sas(path, format="xport")[selected]
        assert np.array_equal(independent[name].to_numpy(), corrected.to_numpy(), equal_nan=True), name
    ins = independent["INS_J"]
    assert int(ins.WTSAF2YR.eq(0).sum()) == 325
    assert int(ins.WTSAF2YR.gt(0).sum()) == 2711
    assert set(ins.LBDINLC.dropna().unique()) == {0.0, 1.0}

    observed = pd.read_csv(PILOT / "shared" / "observed.csv")
    reference = pd.read_csv(LOCKED / "reference.csv")
    spine = pd.read_csv(LOCKED / "design_spine.csv")
    linkage = pd.read_csv(LOCKED / "linkage_private.csv")
    assert list(observed.columns) == ["row_id", "bmi", "age", "sex"]
    pd.testing.assert_frame_equal(observed, reference[list(observed.columns)], check_exact=True)
    assert reference.row_id.is_unique and observed.row_id.is_unique
    target_links = linkage[linkage.in_target_domain.eq(1)]
    ref_source = reference[["row_id", "insulin_uU_mL", "insulin_below_lod"]].merge(target_links[["row_id", "SEQN"]], on="row_id", validate="one_to_one").merge(ins[["SEQN", "LBXIN", "LBDINLC"]], on="SEQN", validate="one_to_one")
    # CSV decimal round trips can differ by floating-point ulps; compare against
    # the source's exact shortest decimal text, not a scientific error metric.
    assert np.allclose(ref_source.insulin_uU_mL, ref_source.LBXIN, rtol=1e-14, atol=0)
    assert np.array_equal(ref_source.insulin_below_lod, ref_source.LBDINLC)
    evaluator_reference = reference[["row_id", "insulin_uU_mL"]].merge(spine.loc[spine.in_target_domain.eq(1), ["row_id", "fasting_weight", "stratum", "psu"]], on="row_id", validate="one_to_one").rename(columns={"insulin_uU_mL": "insulin", "fasting_weight": "weight"})
    evaluator_spine = spine.copy()
    evaluator_spine["row_id"] = evaluator_spine.row_id.fillna(evaluator_spine.design_id)
    evaluator_spine = evaluator_spine[["row_id", "fasting_weight", "stratum", "psu"]].rename(columns={"fasting_weight": "weight"})
    assert evaluator_spine.row_id.is_unique and evaluator_spine.row_id.notna().all()
    assert set(evaluator_reference.row_id).issubset(set(evaluator_spine.row_id))
    assert len(evaluator_spine) == 2711 and len(evaluator_reference) == 1700
    assert evaluator_spine.weight.gt(0).all()
    for name, frame in [("evaluator_reference.csv", evaluator_reference), ("evaluator_design_spine.csv", evaluator_spine)]:
        assert not (LOCKED / name).exists(), "Do not replace a frozen evaluator packet"
        frame.to_csv(LOCKED / name, index=False)
        os.chmod(LOCKED / name, stat.S_IREAD)
    validation = {
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "original_freeze_manifest_sha256": sha(LOCKED / "freeze_manifest.json"),
        "frozen_original_hashes_all_match": True,
        "independent_scalar_ibm_decoder_matches_corrected_pandas": True,
        "decoder_scope": "Exact numeric-array comparison of selected source columns in all four component files; pandas used only for transport record metadata in the independent decoder",
        "synthetic_ibm_zero_one_negative_one_missing_checks_pass": True,
        "official_INS_J_zero_weight_count": 325,
        "downloaded_INS_J_zero_weight_count": 325,
        "official_INS_J_positive_weight_count": 2711,
        "downloaded_INS_J_positive_weight_count": 2711,
        "reference_preserves_source_values": True,
        "observed_contains_only_requested_columns": True,
        "target_rows": 1700,
        "design_rows": 2711,
        "target_outcome_statistics_computed": False,
        "evaluator_files": {
            "evaluator_reference.csv": {"columns": list(evaluator_reference.columns), "purpose": "Reserved target truth and design; insulin in uU/mL"},
            "evaluator_design_spine.csv": {"columns": list(evaluator_spine.columns), "purpose": "ALL positive-weight records. Target-domain membership = row_id in evaluator_reference.csv. Out-of-domain row IDs use independently random design IDs."}
        },
        "files": []
    }
    for path in [LOCKED / "evaluator_reference.csv", LOCKED / "evaluator_design_spine.csv", Path(__file__)]:
        validation["files"].append({"path_relative_to_pilot": str(path.relative_to(PILOT)).replace("\\", "/"), "bytes": path.stat().st_size, "sha256": sha(path)})
        os.chmod(path, stat.S_IREAD)
    path = LOCKED / "evaluator_adapter_manifest.json"
    path.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    os.chmod(path, stat.S_IREAD)
    print(json.dumps(validation, indent=2))
    print("evaluator_adapter_manifest_sha256=" + sha(path))

if __name__ == "__main__":
    main()
