"""Frozen M15B target preparation. No outcome summaries or analyses.

Reads only task-required columns; LBXSUA is used solely as a valid-availability
mask and copied into the private reference. Public output is covariates only.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests
from pandas.io.sas.sas_xport import XportReader


CUSTODIAN = Path(__file__).resolve().parent
RUN = CUSTODIAN.parent.parent
ADMISSION = RUN.parent / "m15b_admission_2026-10-30"
RAW = CUSTODIAN / "raw"
VISIBLE = RUN / "visible"
SALT = "M15B-20261030-v1|"
BASE = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/"
INPUTS = {
    "BIOPRO_L": {"size": 2425520, "columns": ["SEQN", "LBXSUA", "WTPH2YR"]},
    "DEMO_L": {"size": 2582160, "columns": ["SEQN", "RIDAGEYR", "RIDSTATR", "RIAGENDR", "RIDRETH3", "SDMVSTRA", "SDMVPSU"]},
    "BMX_L": {"size": 1563200, "columns": ["SEQN", "BMXBMI"]},
    "DIQ_L": {"size": 847600, "columns": ["SEQN", "DIQ010"]},
}
GROUPS = [("Black", "female"), ("Black", "male"), ("White", "female"), ("White", "male")]


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def log_access(value):
    with (CUSTODIAN / "acquisition.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")


def download(component, expected_size):
    """Explicit complete range; accept only expected-size XPT, never HTML."""
    url = BASE + component + ".xpt"
    destination = RAW / (component + ".xpt")
    if destination.exists():
        raise RuntimeError("Refusing to replace a downloaded component")
    request_range = f"bytes=0-{expected_size - 1}"
    started = utc()
    with requests.get(url, headers={"Range": request_range}, stream=True, timeout=(20, 90)) as response:
        receipt = {
            "started_utc": started, "operation": "GET", "url": url,
            "request_range": request_range, "final_url": response.url,
            "status": response.status_code,
            "headers": {k: v for k, v in response.headers.items() if k.lower() in
                        ["content-length", "content-range", "content-type", "last-modified", "etag"]},
        }
        log_access({**receipt, "stage": "response_headers"})
        if response.status_code not in (200, 206):
            raise RuntimeError("Official component download status not accepted")
        if response.status_code == 206:
            expected_range = f"bytes 0-{expected_size - 1}/{expected_size}"
            if response.headers.get("Content-Range") != expected_range:
                raise RuntimeError("Component Content-Range differs from frozen header verification")
        total = 0
        with destination.open("xb") as target:
            for chunk in response.iter_content(chunk_size=65536):
                total += len(chunk)
                if total > expected_size:
                    raise RuntimeError("Component exceeds verified file-size bound")
                target.write(chunk)
    with destination.open("rb") as stream:
        header = stream.read(80)
    valid_header = header == b"HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!000000000000000000000000000000  "
    if total != expected_size or not valid_header:
        raise RuntimeError("Component size/header verification failed")
    receipt.update({"stage": "complete", "finished_utc": utc(), "bytes": total,
                    "sha256": sha(destination), "sas_header_verified": valid_header})
    log_access(receipt)
    return destination, receipt


def decode_ibm(raw):
    """Byte-specific IBM/SAS numeric decoder; no small-number threshold."""
    eight = raw.ljust(8, b"\x00")
    if eight[0] in b"._ABCDEFGHIJKLMNOPQRSTUVWXYZ" and eight[1:] == b"\x00" * 7:
        return float("nan")
    fraction = int.from_bytes(eight[1:], "big")
    if fraction == 0:
        return 0.0
    sign = -1.0 if eight[0] & 0x80 else 1.0
    exponent = (eight[0] & 0x7F) - 64
    return sign * math.ldexp(float(fraction), 4 * exponent - 56)


def read_columns_and_verify(path, columns):
    """pyreadstat usecols plus independent raw-byte numeric checks.

    pandas is used only to parse XPT schema/record boundaries, never its numeric
    conversion (which lacks a dedicated IBM zero-mantissa branch). No monkeypatch.
    """
    frame, _metadata = pyreadstat.read_xport(path, usecols=columns,
                                          disable_datetime_conversion=True)
    if set(frame.columns) != set(columns):
        raise RuntimeError("Required column names differ")
    with XportReader(path) as reader:
        fields = {field["name"].decode(): field for field in reader.fields}
        record_start = reader.record_start
        record_length = reader.record_length
        record_count = reader.nobs
    if record_count != len(frame):
        raise RuntimeError("Independent reader row counts differ")
    with path.open("rb") as stream:
        stream.seek(record_start)
        data = stream.read(record_count * record_length)
    zero_verified = True
    for column in columns:
        field = fields[column]
        if field["ntype"] != "numeric":
            raise RuntimeError("Expected numeric field")
        width = field["field_length"]
        offset = field["npos"]
        raw_values = [data[i * record_length + offset:i * record_length + offset + width]
                      for i in range(record_count)]
        decoded = np.array([decode_ibm(value) for value in raw_values], dtype=float)
        actual = frame[column].to_numpy(dtype=float)
        if not np.allclose(actual, decoded, rtol=1e-13, atol=0.0, equal_nan=True):
            raise RuntimeError("Independent byte decoder disagrees with required input column")
        exact_zero_mask = np.array([value == b"\x00" * width for value in raw_values])
        if not np.all(actual[exact_zero_mask] == 0.0):
            zero_verified = False
            raise RuntimeError("Byte-encoded zero verification failed")
    identifiers = frame["SEQN"].to_numpy(dtype=float)
    if not np.all(np.isfinite(identifiers) & (identifiers > 0) & (identifiers == np.floor(identifiers))):
        raise RuntimeError("Invalid participant identifier")
    frame["SEQN"] = frame["SEQN"].astype("int64")
    if not frame["SEQN"].is_unique:
        raise RuntimeError("Input participant identifiers are not unique")
    return frame[columns].copy(), {
        "rows": len(frame), "columns_read": columns, "unique_identifiers": True,
        "reader": "pyreadstat.read_xport(usecols=...) + independent IBM-byte decoder",
        "independent_byte_check_passed": True, "exact_byte_zero_check_passed": zero_verified,
        "numeric_pandas_decoder_used": False, "numeric_monkeypatch_used": False,
    }


def main():
    RAW.mkdir(exist_ok=True)
    VISIBLE.mkdir(exist_ok=True)
    for destination in [VISIBLE / "observed.csv", CUSTODIAN / "reference.csv", RUN / "prep_report.json"]:
        if destination.exists():
            raise RuntimeError("Preparation output already exists")
    rule_path = CUSTODIAN / "selection_frozen.json"
    rule = json.loads(rule_path.read_text(encoding="utf-8"))
    if rule["version"] != "M15B-20261030-v1" or rule["selected_n"] != 200 or rule["per_group_n"] != 50:
        raise RuntimeError("Frozen selection rule mismatch")
    write_json_new(CUSTODIAN / "pre_download_commitment.json", {
        "utc": utc(), "selection_sha256": sha(rule_path), "script_sha256": sha(__file__),
        "full_download_has_started": False, "selection_frozen_before_download": True,
    })
    for name in ["target_access.json", "target_metadata.md"]:
        target = CUSTODIAN / ("admission_snapshot_" + name)
        if target.exists():
            raise RuntimeError("Admission snapshot already exists")
        shutil.copyfile(ADMISSION / name, target)
    assert decode_ibm(b"\x00" * 8) == 0.0
    assert decode_ibm(bytes.fromhex("4110000000000000")) == 1.0
    assert decode_ibm(bytes.fromhex("C110000000000000")) == -1.0
    assert math.isnan(decode_ibm(b"." + b"\x00" * 7))
    assert decode_ibm(bytes.fromhex("0010000000000000")) > 0.0
    frames, sources = {}, {}
    for component, specification in INPUTS.items():
        path, acquisition = download(component, specification["size"])
        frame, checks = read_columns_and_verify(path, specification["columns"])
        frames[component] = frame
        sources[component] = {"url": acquisition["url"], "bytes": acquisition["bytes"],
                              "sha256": acquisition["sha256"], "checks": checks}
    merged = frames["DEMO_L"]
    join_counts = {"DEMO_L": len(merged)}
    for component in ["BMX_L", "DIQ_L", "BIOPRO_L"]:
        merged = merged.merge(frames[component], on="SEQN", how="inner", validate="one_to_one")
        join_counts["after_" + component] = len(merged)
    strata = merged["SDMVSTRA"].to_numpy(dtype=float)
    eligible = (
        merged["RIDAGEYR"].between(20, 56, inclusive="both") &
        merged["RIDSTATR"].eq(2) & merged["RIAGENDR"].isin([1, 2]) &
        merged["RIDRETH3"].isin([3, 4]) & merged["DIQ010"].eq(2) &
        np.isfinite(merged["BMXBMI"]) & merged["BMXBMI"].gt(0) &
        np.isfinite(merged["WTPH2YR"]) & merged["WTPH2YR"].gt(0) &
        np.isfinite(strata) & (strata > 0) & (strata == np.floor(strata)) &
        merged["SDMVPSU"].isin([1, 2]) &
        np.isfinite(merged["LBXSUA"]) & merged["LBXSUA"].ge(0)
    )
    eligible_rows = merged.loc[eligible].copy()
    eligible_rows["race"] = eligible_rows["RIDRETH3"].map({3: "White", 4: "Black"})
    eligible_rows["sex"] = eligible_rows["RIAGENDR"].map({1: "male", 2: "female"})
    eligible_rows["selection_hash"] = eligible_rows["SEQN"].map(
        lambda seqn: hashlib.sha256((SALT + str(int(seqn))).encode("utf-8")).hexdigest())
    group_counts = []
    selected_parts = []
    enough = True
    for race, sex in GROUPS:
        group = eligible_rows.loc[eligible_rows["race"].eq(race) & eligible_rows["sex"].eq(sex)]
        group_counts.append({"race": race, "sex": sex, "eligible_n": len(group),
                             "selected_n": 50 if len(group) >= 50 else 0})
        enough = enough and len(group) >= 50
        selected_parts.append(group.sort_values("selection_hash", kind="stable").head(50))
    if not enough:
        report = {"status": "insufficient_eligible_group", "group_counts": group_counts,
                  "selection_scope_expanded": False, "outcomes_exposed": False,
                  "inputs": sources, "selection_sha256": sha(rule_path)}
        write_json_new(RUN / "prep_report.json", report)
        print(json.dumps({"status": report["status"], "group_counts": group_counts}))
        return 2
    selected = pd.concat(selected_parts, ignore_index=True)
    if len(selected) != 200 or not selected["SEQN"].is_unique or not selected["selection_hash"].is_unique:
        raise RuntimeError("Selected count/uniqueness verification failed")
    selected.insert(0, "sample_id", [f"m15b{i:04d}" for i in range(1, 201)])
    observed = selected[["sample_id", "race", "sex", "RIDAGEYR", "BMXBMI"]].rename(
        columns={"RIDAGEYR": "age", "BMXBMI": "bmi"})
    observed["age"] = observed["age"].astype("int64")
    observed_path = VISIBLE / "observed.csv"
    observed.to_csv(observed_path, index=False, mode="x", lineterminator="\n")
    reference = observed.copy()
    reference["urate"] = selected["LBXSUA"].to_numpy()
    for private_column in ["SDMVSTRA", "SDMVPSU", "SEQN", "WTPH2YR"]:
        reference[private_column] = selected[private_column].to_numpy()
    reference_path = CUSTODIAN / "reference.csv"
    reference.to_csv(reference_path, index=False, mode="x", lineterminator="\n")
    mapping_path = CUSTODIAN / "selection_mapping.csv"
    selected[["sample_id", "SEQN", "race", "sex", "selection_hash"]].to_csv(
        mapping_path, index=False, mode="x", lineterminator="\n")
    readback = pd.read_csv(observed_path)
    if list(readback.columns) != ["sample_id", "race", "sex", "age", "bmi"] or len(readback) != 200:
        raise RuntimeError("Visible output schema check failed")
    if readback.isna().any().any() or not readback["sample_id"].is_unique:
        raise RuntimeError("Visible output completeness/uniqueness check failed")
    pd.testing.assert_frame_equal(observed.reset_index(drop=True), readback,
                                  check_dtype=False, check_exact=False, rtol=1e-13, atol=0.0)
    private_receipt = {"utc": utc(), "reference_sha256": sha(reference_path),
                       "selection_mapping_sha256": sha(mapping_path),
                       "observed_sha256": sha(observed_path), "selection_sha256": sha(rule_path),
                       "script_sha256": sha(__file__), "acquisition_log_sha256": sha(CUSTODIAN / "acquisition.jsonl"),
                       "private_reference_columns": list(reference.columns),
                       "outcome_analysis_performed": False, "selected_rows": 200}
    write_json_new(CUSTODIAN / "private_receipt.json", private_receipt)
    report = {
        "status": "ready", "created_utc": utc(), "mode": "enrichment", "selected_n": 200,
        "group_counts": group_counts, "join_row_counts": join_counts,
        "selection": rule, "selection_sha256": sha(rule_path), "preparation_script_sha256": sha(__file__),
        "visible_path": str(observed_path), "visible_columns": list(observed.columns),
        "visible_sha256": sha(observed_path), "inputs": sources,
        "checks": {"selection_frozen_before_download": True, "one_to_one_joins": True,
                   "selected_identifier_uniqueness": True, "exactly_50_per_race_sex": True,
                   "hash_order_selection": True, "visible_schema_exact": True,
                   "visible_csv_roundtrip": True, "outcome_values_in_visible": False,
                   "outcome_summaries_computed": False, "prior_target_results_read": False},
        "assay": {"outcome": "serum urate", "source_variable": "LBXSUA", "unit": "mg/dL",
                  "platform": "Roche Cobas 8000", "method": "uricase/peroxidase colorimetric endpoint",
                  "survey_weight": "WTPH2YR", "design_variables": ["SDMVSTRA", "SDMVPSU"]},
        "limitations": ["DIQ010=2 is no self-reported professional diagnosis, not laboratory-defined nondiabetes.",
                        "No additional BMI cutoff, fasting, medication or pregnancy selection was imposed.",
                        "Source-population fasting, treatment and pregnancy restrictions may differ.",
                        "Same NHANES cycle as prior HbA1c experiment: new outcome, not wholly new participants.",
                        "Equal race/sex quotas are a deliberately balanced analysis set; raw NHANES weights are retained privately and do not by themselves undo quota selection."],
        "evaluation_status": "Not performed; requires explicit root follow-up after generator freeze.",
        "analysis_population": "Finite equal-quota benchmark; downstream estimates are unweighted descriptive quantities, not national population estimates.",
    }
    write_json_new(RUN / "prep_report.json", report)
    print(json.dumps({"status": "ready", "selected_n": 200, "group_counts": group_counts,
                      "visible_path": str(observed_path), "visible_sha256": sha(observed_path),
                      "prep_report_path": str(RUN / "prep_report.json")}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        log_access({"utc": utc(), "stage": "failed", "exception_type": type(exc).__name__,
                    "message": str(exc), "outcome_values_printed": False})
        print(json.dumps({"status": "failed", "exception_type": type(exc).__name__,
                          "private_log": str(CUSTODIAN / "acquisition.jsonl")}))
        sys.exit(1)
