"""Controller-only, aggregate-only package assembler; never executes a candidate.

Use the configured Python environment and --harness-project PROJECT (or an
already configured import path). Use
--check-only for a read-only preflight. Creation requires a new destination and
an explicit SHA256 of the separately reviewed root admission receipt.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys


ADMISSION_STATUS = "approved_for_bounded_scientific_construction_with_restrictions"
PUBLIC_INPUTS = ("task.json", "SOURCE_PANEL_SPEC.json", "BUILDER_BRIEF.md")
REVIEW_INPUTS = (*PUBLIC_INPUTS, "prepare_bundles.py")
PANEL_IDS = {
    "lifelines": [
        "J_T1_age_mean_task", "J_T1_age_sd_task", "J_T1_bmi_mean_task",
        "J_T1_bmi_sd_task", "J_T1_glucose_mean_mg_dL_derived",
        "J_T1_glucose_sd_mg_dL_derived", "J_T1_hba1c_mean_pct",
        "J_T1_hba1c_sd_pct", "J_T1_female_proportion_derived",
        "J_T2_bmi_slope_task_derived", "J_T2_glucose_slope_task_derived",
    ],
    "pani": [
        "P_NHANES_age_slope", "P_NHANES_hba1c_age_lt40_mean",
        "P_NHANES_hba1c_age_40_44_mean", "P_NHANES_hba1c_age_45_49_mean",
        "P_NHANES_hba1c_age_50_54_mean", "P_NHANES_hba1c_age_55_59_mean",
        "P_NHANES_hba1c_age_60_64_mean", "P_NHANES_hba1c_age_65_69_mean",
        "P_NHANES_hba1c_age_ge70_mean",
    ],
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def safe_file(root, relative):
    require(isinstance(relative, str) and relative and "\\" not in relative
            and ":" not in relative, "Expected portable relative file path")
    parts = PurePosixPath(relative).parts
    require(not PurePosixPath(relative).is_absolute()
            and all(x not in {"", ".", ".."} for x in parts), "Unsafe relative path")
    current = root
    for part in parts:
        current = current / part
        require(not current.is_symlink() and not current.is_junction(), "Linked input rejected")
    require(current.resolve().is_relative_to(root) and current.is_file(), "Input file missing or escapes root")
    return current


def expected_operator(item):
    eid = item["id"]
    operator = {"kind": item["kind"], "unit": item["unit"],
                "selection": [], "missing_policy": "error"}
    if item["kind"] in {"mean", "sd"}:
        operator["column"] = item["variables"][0]
    elif item["kind"] == "proportion":
        operator["event"] = {"column": "female", "op": "eq", "value": 1}
    else:
        outcome, term = item["variables"]
        operator.update(outcome=outcome, predictors=[term, *item["adjustment"]],
                        term=term, include_intercept=True)
    bands = {
        "lt40": [{"column": "age", "op": "ge", "value": 25},
                 {"column": "age", "op": "lt", "value": 40}],
        "ge70": [{"column": "age", "op": "ge", "value": 70}],
    }
    for lo, hi in ((40, 44), (45, 49), (50, 54), (55, 59), (60, 64), (65, 69)):
        bands[f"{lo}_{hi}"] = [{"column": "age", "op": "ge", "value": lo},
                                {"column": "age", "op": "le", "value": hi}]
    for label, filters in bands.items():
        if eid == f"P_NHANES_hba1c_age_{label}_mean":
            operator["selection"] = filters
    return operator


def check_inputs(packet, admission, admission_sha256, public):
    # Imports perform trusted schema checks only; candidate code is never loaded.
    from cohort_harness.contracts import validate_evidence, validate_task
    from cohort_harness.source_replay import _check_metadata

    source, pub, receipt_path = Path(packet).resolve(), Path(public).resolve(), Path(admission).resolve()
    require(re.fullmatch(r"[a-f0-9]{64}", admission_sha256) is not None, "Explicit admission SHA256 required")
    require(digest(receipt_path) == admission_sha256, "Root admission receipt changed")
    receipt = read(receipt_path)
    require(receipt["status"] == ADMISSION_STATUS and receipt["curator"] == "root", "No suitable root admission")
    require(receipt["raw_or_generated_patient_data_admitted"] is False, "Patient data not allowed")
    require(receipt["target_family_excluded"] == "ENSANUT", "Admission boundary changed")
    manifest_path = safe_file(source, "MANIFEST.json")
    require(digest(manifest_path) == receipt["packet_manifest_sha256"], "Packet manifest changed")
    manifest = read(manifest_path)
    files = manifest["files"]
    names = [x["path"] for x in files]
    require(len(names) == len(set(x.casefold() for x in names)), "Duplicate packet paths")
    require(set(names) == set(receipt["verified_files"]), "Manifest/admission file set differs")
    actual = {x.relative_to(source).as_posix() for x in source.rglob("*") if x.is_file()}
    require(actual == set(names) | {"MANIFEST.json"}, "Unexpected packet files")
    for entry in files:
        path = safe_file(source, entry["path"])
        require(digest(path) == entry["sha256"] and path.stat().st_size == entry["bytes"],
                "Approved packet artifact changed: " + entry["path"])
    require(digest(source / "evidence_template.json") == receipt["evidence_template_sha256"], "Evidence template changed")

    review = read(safe_file(pub, "PACKAGE_REVIEW.json"))
    require(review["status"] == "mechanically_checked_preparation_only", "Public package review unavailable")
    require(review["source_admission_sha256"] == admission_sha256, "Review/admission binding differs")
    for name in REVIEW_INPUTS:
        require(digest(safe_file(pub, name)) == review["public_file_sha256"][name], "Reviewed public file changed: " + name)
    ast.parse((pub / "prepare_bundles.py").read_text(encoding="utf-8"))
    task, panel, evidence = read(pub / "task.json"), read(pub / "SOURCE_PANEL_SPEC.json"), read(source / "evidence_template.json")
    validate_task(task)
    validate_evidence(evidence, task)
    require(task["mode"] == "whole_cohort" and task["n_rows"] == 2000, "Wrong task mode or row count")
    require([x["name"] for x in task["columns"]] == ["row_id", "age", "female", "bmi", "glucose", "hba1c"], "Wrong columns")
    require(panel["evidence_template_sha256"] == receipt["evidence_template_sha256"], "Panel evidence binding differs")
    require(panel["source_seed"] == 18101 and panel["source_n_rows"] == 6000, "Source schedule changed")
    items = {x["id"]: x for x in evidence["items"]}
    require(len(items) == 32, "Expected 32 admitted evidence items")
    require([x["id"] for x in panel["contexts"]] == ["lifelines", "pani"], "Source context IDs changed")
    for context in panel["contexts"]:
        checks = context["checks"]
        require([x["evidence_id"] for x in checks] == PANEL_IDS[context["id"]], "Fixed source panel differs")
        for check in checks:
            item = items[check["evidence_id"]]
            require(check["evidence_metadata"] == item, "Panel item metadata changed")
            require(check["operator"] == expected_operator(item), "Exact source operator changed")
            _check_metadata({"id": check["id"], "evidence_id": item["id"], "status": "approximate",
                             "operator": check["operator"], "assumption_ids": [],
                             "reason": "Mechanical metadata check only."},
                            items, {"A_mechanical_placeholder"}, ["A_mechanical_placeholder"])
    normalized = read(source / "normalized_quantities.json")
    require(panel["evidence_grouping"] == normalized["records"], "Original/derived grouping changed")
    require({x["item_id"] for x in panel["evidence_grouping"]} == set(items), "Incomplete evidence grouping")
    registry = []
    for study in evidence["sources"]:
        for artifact in study["artifacts"]:
            require(artifact["path"] in names, "Evidence source not admitted")
            require(artifact["path"].startswith("sources/"), "Unexpected source artifact location")
            require(digest(safe_file(source, artifact["path"])) == artifact["sha256"], "Evidence source hash differs")
            registry.append({"source_id": study["id"], "path": artifact["path"],
                             "sha256": artifact["sha256"], "origin": "curator", "screening": "approved"})
    require(len(registry) == 4, "Expected four admitted source artifacts")
    return {"source": source, "public": pub, "admission": receipt_path,
            "receipt": receipt, "manifest": manifest, "registry": registry,
            "admission_sha256": admission_sha256, "review": review}


def prepare(destination, checked):
    root = Path(destination).absolute()
    require(not root.exists() and not root.is_symlink() and not root.is_junction(), "Destination must be new")
    # Reject linked parents and resolve the final path before any writes.
    for parent in root.parents:
        require(not parent.is_symlink() and not parent.is_junction(), "Linked destination parent rejected")
    root = root.resolve()
    require(not root.is_relative_to(checked["source"]) and not root.is_relative_to(checked["public"]),
            "Destination must be outside approved packet and public package")
    copies = []
    for entry in checked["manifest"]["files"]:
        name = entry["path"]
        copies.append((checked["source"] / name, "source_packet/" + name, entry["sha256"]))
    copies.append((checked["source"] / "MANIFEST.json", "source_packet/MANIFEST.json", checked["receipt"]["packet_manifest_sha256"]))
    copies.append((checked["source"] / "evidence_template.json", "evidence_template.json", checked["receipt"]["evidence_template_sha256"]))
    copies.extend((checked["source"] / x["path"], x["path"], x["sha256"]) for x in checked["registry"])
    copies.extend((checked["public"] / name, name, checked["review"]["public_file_sha256"][name]) for name in PUBLIC_INPUTS)
    copies.append((checked["admission"], "SOURCE_PACKET_ADMISSION.json", checked["admission_sha256"]))
    for original, relative, expected in copies:
        require(digest(original) == expected, "Input changed after preflight: " + relative)
    root.mkdir(parents=True, exist_ok=False)
    (root / "candidates").mkdir()
    for original, relative, expected in copies:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with original.open("rb") as src, target.open("xb") as dst:
            shutil.copyfileobj(src, dst)
        require(digest(target) == expected, "Copy verification failed: " + relative)
    write(root / "registry.json", {"artifacts": checked["registry"]})
    receipt = {"schema_version": 1, "kind": "aggregate_only_builder_package",
               "created_utc": datetime.now(timezone.utc).isoformat(),
               "source_admission_sha256": checked["admission_sha256"],
               "packet_manifest_sha256": checked["receipt"]["packet_manifest_sha256"],
               "evidence_template_sha256": checked["receipt"]["evidence_template_sha256"],
               "task_sha256": digest(root / "task.json"),
               "source_panel_sha256": digest(root / "SOURCE_PANEL_SPEC.json"),
               "assembler_sha256": digest(checked["public"] / "prepare_bundles.py"),
               "package_review_sha256": digest(checked["public"] / "PACKAGE_REVIEW.json"),
               "copied_file_sha256": {relative: digest(root / relative) for _, relative, _ in copies},
               "registry_sha256": digest(root / "registry.json"),
               "individual_records_supplied": 0, "scientific_model_supplied": False,
               "candidate_created": False, "candidate_code_executed": False,
               "historical_pending_labels": "Preserved source-packet bytes; separate root admission is authoritative."}
    write(root / "INPUT_ADMISSION.json", receipt)
    # No code, model specification, patient table or candidate is created.
    require(not list((root / "candidates").iterdir()), "Candidates directory must stay empty")
    require(not list(root.rglob("*.csv")), "No individual tables are allowed")
    return root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", required=True)
    parser.add_argument("--admission", required=True)
    parser.add_argument("--admission-sha256", required=True)
    parser.add_argument("--public", default=str(Path(__file__).resolve().parent))
    parser.add_argument("--harness-project", help="Trusted project containing cohort_harness; used only for schema imports")
    parser.add_argument("--destination")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    require(args.check_only != bool(args.destination), "Choose exactly one of --check-only or --destination")
    if args.harness_project:
        project = Path(args.harness_project).resolve()
        require((project / "cohort_harness" / "contracts.py").is_file(), "Harness project is missing")
        sys.path.insert(0, str(project))
    checked = check_inputs(args.packet, args.admission, args.admission_sha256, args.public)
    if args.check_only:
        print(json.dumps({"status": "valid_preparation_inputs", "source_checks": 20,
                          "evidence_items": 32, "registry_artifacts": 4,
                          "files_written": 0, "candidate_executed": False}))
    else:
        print(json.dumps({"status": "prepared", "destination": str(prepare(args.destination, checked)),
                          "candidate_created": False, "candidate_executed": False}))


if __name__ == "__main__":
    main()
