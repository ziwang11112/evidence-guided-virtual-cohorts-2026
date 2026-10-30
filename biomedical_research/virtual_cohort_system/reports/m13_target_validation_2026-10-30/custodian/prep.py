"""M13-B local custody: freeze/auth gates, official acquisition, exact input whitelist.

Importing this module does not acquire or read target data. The only acquisition
entry point is ``acquire`` after verify_gate succeeds. No generator is run here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
METADATA = HERE / "metadata_sources.json"
FRAME_COLUMNS = ["id", "SEQN", "WTMEC2YR", "SDMVSTRA", "SDMVPSU", "RIDAGEYR",
                 "RIAGENDR", "RIDRETH3", "BMXBMI", "DXAEXSTS", "DXDTOPF"]
GENERATOR_COLUMNS = ["id", "age", "bmi", "male", "asian", "inv_bmi", "male_inv_bmi",
                     "asian_inv_bmi", "male_age", "asian_age"]
TARGET_RULES = {
    "cycle": "2017-2018", "endpoint": "DXDTOPF", "primary_bmi": [18.5, 30],
    "extension_bmi": [30, 35], "generator_columns": GENERATOR_COLUMNS,
    "frame_columns": FRAME_COLUMNS,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def require(ok, message: str) -> None:
    if not ok:
        raise ValueError(message)


def utc_time(value: str) -> datetime:
    t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(t.tzinfo is not None, "Gate timestamps must specify timezone")
    return t.astimezone(timezone.utc)


def verify_gate(manifest_path: Path, expected_hash: str, authorization_path: Path) -> dict:
    """Read only frozen source/code/contract files, never raw target files."""
    require(len(expected_hash) == 64, "An explicit freeze manifest SHA256 is required")
    require(sha256(manifest_path) == expected_hash, "Freeze manifest SHA256 mismatch")
    m, a = load_json(manifest_path), load_json(authorization_path)
    require(m.get("schema_version") == 1 and m.get("phase") == "before_target_acquisition", "Wrong freeze schema/phase")
    require(m.get("scientific_revision_allowed") is False, "Freeze must forbid scientific revision")
    require(a.get("schema_version") == "m13b_target_access_authorization_v1", "Wrong authorization schema")
    require(a.get("freeze_manifest_sha256") == expected_hash, "Authorization bound to another freeze")
    require(a.get("authorized_by") == "root" and a.get("target_access_authorized") is True,
            "Explicit root target-access authorization is required")
    frozen = utc_time(m["created_utc"])
    authorized = utc_time(a["authorized_at_utc"])
    require(frozen <= authorized <= datetime.now(timezone.utc), "Invalid freeze/authorization chronology")
    require(isinstance(m.get("files"), dict) and len(m["files"]) > 0, "Frozen file map is required")
    root = manifest_path.resolve().parent
    seen = set()
    for relative, expected in m["files"].items():
        p = (root / relative).resolve()
        require(p.is_relative_to(root), "Frozen file escapes M13-B directory")
        require(p not in seen, "Duplicate frozen file")
        require(p.is_file() and sha256(p) == expected, "Frozen file missing or changed: " + relative)
        seen.add(p)
    require(Path(__file__).resolve() in seen and METADATA.resolve() in seen,
            "Freeze must bind this custody script and metadata sources")
    require(root / "protocol.json" in seen and root / "PROTOCOL.md" in seen, "Frozen protocol files missing")
    protocol = load_json(root / "protocol.json")
    require(protocol.get("target") == "NHANES2017-18_DXDTOPF" and
            protocol.get("observed_columns") == GENERATOR_COLUMNS and
            protocol.get("primary_bmi") == [18.5, 30] and protocol.get("primary_upper_inclusive") is False and
            protocol.get("extension_bmi") == [30, 35], "Frozen protocol disagrees with custody rules")
    return {"freeze_manifest_sha256": expected_hash, "authorization_sha256": sha256(authorization_path),
            "frozen_file_count": len(seen), "verified_at_utc": now()}


def finite(series: pd.Series) -> np.ndarray:
    return np.isfinite(series.to_numpy(dtype=float))


def validate_component(df: pd.DataFrame, columns: list[str], component: str) -> pd.DataFrame:
    require(set(columns) <= set(df.columns), component + " required columns missing")
    out = df.loc[:, columns].copy()
    for c in columns:
        out[c] = pd.to_numeric(out[c], errors="raise")
    seq = out["SEQN"].to_numpy(dtype=float)
    require(np.isfinite(seq).all() and (seq == np.floor(seq)).all(), component + " invalid SEQN")
    require(out["SEQN"].is_unique, component + " duplicate SEQN")
    out["SEQN"] = out["SEQN"].astype("int64")
    return out


def aggregate(mask, weights) -> dict:
    mask = np.asarray(mask, dtype=bool)
    return {"n": int(mask.sum()), "weight_sum": float(np.asarray(weights)[mask].sum())}


def completeness(base, checks: dict, weights) -> dict:
    base = np.asarray(base, dtype=bool)
    total = aggregate(base, weights)
    fields = {}
    for key, mask in checks.items():
        item = aggregate(base & np.asarray(mask, dtype=bool), weights)
        item["unweighted_fraction"] = item["n"] / total["n"] if total["n"] else None
        item["weighted_fraction"] = item["weight_sum"] / total["weight_sum"] if total["weight_sum"] else None
        fields[key] = item
    return {"denominator": total, "complete": fields}


def build_frames(demo: pd.DataFrame, bmx: pd.DataFrame, dxx: pd.DataFrame) -> tuple:
    """Pure transformation, usable with invented fixtures without target access."""
    metadata = load_json(METADATA)
    demo = validate_component(demo, metadata["components"]["DEMO_J"]["variables"], "DEMO_J")
    bmx = validate_component(bmx, metadata["components"]["BMX_J"]["variables"], "BMX_J")
    dxx = validate_component(dxx, metadata["components"]["DXX_J"]["variables"], "DXX_J")
    for label, child in [("BMX_J", bmx), ("DXX_J", dxx)]:
        require(child.SEQN.isin(demo.SEQN).all(), label + " SEQN absent from DEMO_J")
    y = dxx.DXDTOPF.to_numpy(dtype=float)
    require(not np.isinf(y).any(), "DXDTOPF infinite value: custody integrity failure; no trimming")
    require(not ((y < 0) | (y > 100)).any(), "DXDTOPF outside [0,100]: custody integrity failure; no trimming")
    valid_weight = finite(demo.WTMEC2YR) & (demo.WTMEC2YR > 0)
    valid_design = finite(demo.SDMVSTRA) & finite(demo.SDMVPSU)
    selected = demo.loc[valid_weight & valid_design].copy()
    require(len(selected) > 0, "Empty positive-weight survey-design frame")
    for col in ["SDMVSTRA", "SDMVPSU"]:
        require((selected[col] == np.floor(selected[col])).all(), "Noninteger survey-design identifier")
    frame = selected.merge(bmx, on="SEQN", how="left", validate="one_to_one").merge(
        dxx, on="SEQN", how="left", validate="one_to_one").sort_values("SEQN", kind="stable").reset_index(drop=True)
    require(len(frame) == len(selected), "Full design frame changed during merge")
    frame.insert(0, "id", ["m13b_" + secrets.token_hex(16) for _ in range(len(frame))])
    require(frame.id.is_unique, "Opaque ID collision")
    frame = frame.loc[:, FRAME_COLUMNS]
    psus_per_stratum = frame.groupby("SDMVSTRA")["SDMVPSU"].nunique()
    require((psus_per_stratum >= 2).all(), "Full survey-design singleton stratum: stop, no correction")
    age = finite(frame.RIDAGEYR) & frame.RIDAGEYR.between(20, 59)
    race = frame.RIDRETH3.isin([3, 4])
    sex = frame.RIAGENDR.isin([1, 2])
    bmi = finite(frame.BMXBMI)
    primary_bmi = bmi & (frame.BMXBMI >= 18.5) & (frame.BMXBMI < 30)
    extension_bmi = bmi & frame.BMXBMI.between(30, 35)
    scan = frame.DXAEXSTS.eq(1)
    endpoint = finite(frame.DXDTOPF)
    eligible = age & race & sex & bmi & scan & endpoint
    primary = eligible & primary_bmi
    extension = eligible & extension_bmi
    included = primary | extension
    f = frame.loc[included]
    observed = pd.DataFrame({"id": f.id, "age": f.RIDAGEYR, "bmi": f.BMXBMI,
                             "male": f.RIAGENDR.eq(1).astype(int), "asian": 0}).reset_index(drop=True)
    observed["inv_bmi"] = 1.0 / observed.bmi
    observed["male_inv_bmi"] = observed.male * observed.inv_bmi
    observed["asian_inv_bmi"] = 0.0
    observed["male_age"] = observed.male * observed.age
    observed["asian_age"] = 0.0
    observed = observed.loc[:, GENERATOR_COLUMNS]
    require(finite(observed.iloc[:, 1:].stack()).all(), "Nonfinite permitted generator covariate")
    require(observed.id.tolist() == frame.loc[included, "id"].tolist(), "Row key/order mismatch")
    weight = frame.WTMEC2YR.to_numpy(dtype=float)
    # Sequential exclusions have a fixed order. At pre-design stages weights
    # summarize only finite positive MEC weights, explicitly labelled below.
    demo_weight = np.where(valid_weight, demo.WTMEC2YR, 0.0)
    flow = [dict(stage="all_DEMO_J", **aggregate(np.ones(len(demo), bool), demo_weight)),
            dict(stage="positive_finite_MEC_weight", **aggregate(valid_weight, demo_weight)),
            dict(stage="full_design_frame", **aggregate(valid_weight & valid_design, demo_weight))]
    running = np.ones(len(frame), dtype=bool)
    for name, rule in [("age_20_59", age), ("race_White_Black", race), ("sex_1_2", sex),
                       ("BMI_finite", bmi), ("BMI_18.5_35", primary_bmi | extension_bmi),
                       ("DXAEXSTS_1", scan), ("DXDTOPF_finite", endpoint)]:
        prior = aggregate(running, weight)
        running &= np.asarray(rule)
        row = dict(stage=name, **aggregate(running, weight))
        row["excluded_n"] = prior["n"] - row["n"]
        row["excluded_weight_sum"] = prior["weight_sum"] - row["weight_sum"]
        flow.append(row)
    checks = {"sex_valid": sex, "BMI_finite": bmi, "DXA_status_present": finite(frame.DXAEXSTS),
              "scan_complete_valid": scan, "endpoint_finite": endpoint,
              "all_covariates_and_valid_endpoint": sex & bmi & scan & endpoint}
    completeness_report = {
        "age_race_frame_before_BMI_selection": completeness(age & race, checks, weight),
        "primary_age_race_BMI_frame": completeness(age & race & primary_bmi, checks, weight),
        "extension_age_race_BMI_frame": completeness(age & race & extension_bmi, checks, weight),
    }
    full_psus = set(zip(frame.SDMVSTRA, frame.SDMVPSU))
    included_psus = set(zip(frame.loc[included, "SDMVSTRA"], frame.loc[included, "SDMVPSU"]))
    report = {
        "schema_version": "m13b_custody_quality_v1", "exclusion_flow": flow,
        "flow_weight_definition": "Sum of finite positive WTMEC2YR only, including pre-design stages.",
        "domains": {"primary": aggregate(primary, weight), "extension": aggregate(extension, weight)},
        "completeness": completeness_report,
        "design": {"strata": len(psus_per_stratum), "nested_psus": len(full_psus),
                   "zero_domain_psus_retained": len(full_psus - included_psus)},
        "endpoint_integrity": "All available endpoints in DXX_J checked against [0,100]; no trimming.",
        "row_order": "Ascending SEQN internally; identical order for opaque IDs in generator inputs.",
        "missingness_policy": "No imputation, nonresponse reweighting or extra clinical exclusions.",
    }
    return frame, observed, report


def download_component(name: str, url: str, destination: Path) -> dict:
    require(urlparse(url).scheme == "https" and urlparse(url).hostname == "wwwn.cdc.gov", "Non-CDC XPT URL")
    request = urllib.request.Request(url, headers={"User-Agent": "M13B-NHANES-custody/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        actual = response.geturl()
        parsed = urlparse(actual)
        require(parsed.scheme == "https" and parsed.hostname == "wwwn.cdc.gov" and
                parsed.path.lower().endswith("/" + name.lower() + ".xpt"), "Unexpected XPT redirect")
        body = response.read()
        content_type = response.headers.get("Content-Type")
    require(body.startswith(b"HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!"), "Response is not SAS XPORT")
    destination.write_bytes(body)
    return {"component": name, "requested_url": url, "actual_used_url": actual,
            "sha256": sha256(destination), "bytes": len(body), "content_type": content_type,
            "downloaded_at_utc": now()}


def acquire(args) -> dict:
    gate = verify_gate(args.freeze_manifest.resolve(), args.freeze_sha256, args.authorization.resolve())
    output = args.output.resolve()
    require(output.is_relative_to(HERE) and output != HERE, "Acquisition output must be a new child of custody directory")
    require(not output.exists(), "Acquisition output already exists; no overwrite/retry in place")
    output.mkdir(parents=True)
    # All participant-level outputs, including covariates, remain local only.
    (output / ".gitignore").write_text("*\n", encoding="utf-8")
    raw = output / "private" / "raw"
    raw.mkdir(parents=True)
    inputs = output / "generator_input"
    inputs.mkdir()
    receipt = {"schema_version": "m13b_acquisition_receipt_v1", "started_at_utc": now(),
               "status": "started", "gate": gate, "downloads": []}
    receipt_path = output / "private" / "acquisition_receipt.json"
    write_json(receipt_path, receipt)
    try:
        components = load_json(METADATA)["components"]
        for name in ["DEMO_J", "BMX_J", "DXX_J"]:
            receipt["downloads"].append(download_component(name, components[name]["planned_xpt_url"], raw / (name + ".xpt")))
            write_json(receipt_path, receipt)
        tables = [pd.read_sas(raw / (name + ".xpt"), format="xport", encoding="utf-8")
                  for name in ["DEMO_J", "BMX_J", "DXX_J"]]
        frame, observed, quality = build_frames(*tables)
        frame_path = output / "private" / "full_frame.csv"
        observed_path = inputs / "observed.csv"
        frame.to_csv(frame_path, index=False)
        observed.to_csv(observed_path, index=False)
        mapping_path = output / "private" / "id_mapping.csv"
        frame[["id", "SEQN"]].to_csv(mapping_path, index=False)
        write_json(output / "private" / "quality_report.json", quality)
        receipt["outputs"] = {"full_frame": {"path": str(frame_path), "sha256": sha256(frame_path)},
                              "generator_input": {"path": str(observed_path), "sha256": sha256(observed_path)},
                              "id_mapping": {"path": str(mapping_path), "sha256": sha256(mapping_path)}}
        receipt["status"] = "complete"
        receipt["completed_at_utc"] = now()
        write_json(receipt_path, receipt)
    except Exception as exc:
        receipt["status"] = "failed"
        receipt["error"] = str(exc)
        receipt["failed_at_utc"] = now()
        write_json(receipt_path, receipt)
        raise
    return {"status": "complete", "receipt": str(receipt_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("show-required-rules", help="Print metadata-only contract fragment; no target access")
    for name in ["check-gate", "acquire"]:
        p = sub.add_parser(name)
        p.add_argument("--freeze-manifest", type=Path, required=True)
        p.add_argument("--freeze-sha256", required=True)
        p.add_argument("--authorization", type=Path, required=True)
        if name == "acquire":
            p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "show-required-rules":
        result = TARGET_RULES
    elif args.command == "check-gate":
        result = verify_gate(args.freeze_manifest.resolve(), args.freeze_sha256, args.authorization.resolve())
    else:
        result = acquire(args)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("M13-B custody stopped: " + str(error), file=sys.stderr)
        sys.exit(1)
