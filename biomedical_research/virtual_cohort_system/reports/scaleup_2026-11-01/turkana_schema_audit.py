"""Bounded header/key/missingness audit. Never emit clinical values or effects.

Acquisition is a separate Chrome action. This script accepts explicit local paths;
it never downloads, searches patient directories, selects outcomes, or fits models.
The report is a schema/availability artifact, not scientific admission.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

EXPECTED = [
    "Individual ID", "Waist circumference", "Systolic BP", "Diastolic BP",
    "Blood glucose", "Body fat", "Total cholesterol", "HDL cholesterol",
    "Triglycerides", "LDL cholesterol", "Sex", "Age", "BMI", "Lifestyle category",
]
EXPECTED_HASH = "7508097bd6578307a55aef793c15b4c26d2346e2d8e60e55ba8bf9d5254037f9"


def audit(path):
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_HASH:
        raise ValueError("Unexpected release bytes; resolve identity before auditing")
    keys = Counter()
    missing = Counter({name: 0 for name in EXPECTED})
    complete_lipid_panel = 0
    required = ["Age", "Sex", "BMI", "Total cholesterol", "HDL cholesterol"]
    row_count = 0
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, delimiter="\t")
        if next(reader) != EXPECTED:
            raise ValueError("Header mismatch")
        for row in reader:
            if len(row) != len(EXPECTED):
                raise ValueError("Row width mismatch; no row contents emitted")
            item = dict(zip(EXPECTED, row))
            row_count += 1
            for name, value in item.items():
                if value.strip() in {"", "NA"}:
                    missing[name] += 1
            if item["Individual ID"].strip() not in {"", "NA"}:
                keys[item["Individual ID"]] += 1
            if all(item[name].strip() not in {"", "NA"} for name in required):
                complete_lipid_panel += 1
    return {
        "audit_type": "header_keys_and_missingness_only",
        "sha256": digest, "bytes": len(payload), "columns": EXPECTED,
        "columns_including_id": len(EXPECTED), "rows_in_deposit": row_count,
        "distinct_nonmissing_ids": len(keys),
        "duplicate_nonmissing_id_groups": sum(count > 1 for count in keys.values()),
        "duplicate_nonmissing_id_extra_rows": sum(count - 1 for count in keys.values()),
        "missing_counts": dict(missing),
        "candidate_TC_HDL_covariate_availability": {
            "required_fields": required, "nonmissing_rows": complete_lipid_panel,
            "note": "Availability only; not a frozen eligibility or analysis population",
        },
        "not_computed": ["clinical_values_output", "means", "ranges", "quantiles",
                         "covariances", "correlations", "regression", "target_signs",
                         "clinical_endpoint_selection"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = audit(args.input)
    with args.output.open("xb") as stream:
        stream.write((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(result, indent=2))
