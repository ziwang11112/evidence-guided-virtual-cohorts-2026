"""Transparent adapter for released aggregates only; no individual rows or fits.

Written after explicit controller release, using output fields, never original
evaluator implementation. No estimands or numerical formulas are modified.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


KEY_MAP = {f"global_{name}": f"global.{name}" for name in ("bmi", "age", "curvature", "interaction")}
KEY_MAP.update({f"{stat}_{race}_{sex}": f"group.{race}.{sex}.{stat}"
                for race in ("White", "Black") for sex in ("male", "female")
                for stat in ("reverse", "mean", "sd", "median", "q90")})


def mapped_estimate(estimate):
    return {"estimand": KEY_MAP[estimate["estimand"]], "value": estimate["value"],
            "n": estimate["n"], "complete_n": estimate["n_complete"],
            "matrix_rank": estimate["rank"], "status": estimate["status"],
            "units": estimate["units"], "reason": estimate["reason"] or None,
            "rank_kind": estimate["rank_definition"]}


def check_csv_export(released, csv_path):
    with Path(csv_path).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    expected = {(tuple(candidate["labels"]), item["estimand"]): item
                for candidate in released["candidate_comparisons"] for item in candidate["estimands"]}
    if len(rows) != len(expected):
        raise ValueError("Released CSV endpoint count differs from released JSON.")
    seen = set()
    checked_fields = 0
    for row in rows:
        key = (tuple(row["candidate_labels"].split(";")), row["estimand"])
        if key in seen or key not in expected:
            raise ValueError("Released CSV has missing, duplicate, or unexpected endpoint/label pairs.")
        seen.add(key)
        source = expected[key]
        for field in ("family", "race", "sex", "model", "coefficient", "units"):
            if row[field] != source[field]:
                raise ValueError(f"Released CSV metadata differs: {key}, {field}.")
            checked_fields += 1
        for prefix in ("measured", "generated"):
            for field in ("value", "n", "n_complete", "rank", "n_parameters"):
                number = None if row[f"{prefix}_{field}"] == "" else float(row[f"{prefix}_{field}"])
                if number != source[prefix][field]:
                    raise ValueError(f"Released CSV number differs: {key}, {prefix}, {field}.")
                checked_fields += 1
            for field in ("status", "reason", "sign"):
                if row[f"{prefix}_{field}"] != ("" if source[prefix][field] is None else str(source[prefix][field])):
                    raise ValueError(f"Released CSV status differs: {key}, {prefix}, {field}.")
                checked_fields += 1
        delta = None if not row["difference_generated_minus_measured"] else float(row["difference_generated_minus_measured"])
        same_sign = None if row["same_sign"] == "" else row["same_sign"] == "True"
        if delta != source["difference_generated_minus_measured"] or same_sign != source["same_sign"]:
            raise ValueError(f"Released CSV comparison differs: {key}.")
        checked_fields += 2
    return {"endpoint_rows": len(rows), "checked_fields": checked_fields,
            "all_checked_json_csv_fields_exactly_agree": True}


def map_output(released):
    if released["estimand_count"] != 24:
        raise ValueError("Released output changed the endpoint count.")
    estimates = {"reference": {}, "initial": {}, "final": {}}
    for candidate in released["candidate_comparisons"]:
        if set(item["estimand"] for item in candidate["estimands"]) != set(KEY_MAP) or len(candidate["estimands"]) != 24:
            raise ValueError("Released candidate omits, duplicates, or adds estimands.")
        for item in candidate["estimands"]:
            key = KEY_MAP[item["estimand"]]
            measured = mapped_estimate(item["measured"])
            generated = mapped_estimate(item["generated"])
            if key in estimates["reference"] and estimates["reference"][key] != measured:
                raise ValueError("Repeated reference estimates disagree in released aggregate.")
            estimates["reference"][key] = measured
            for label in candidate["labels"]:
                if label not in ("initial", "final") or key in estimates[label]:
                    raise ValueError("Invalid or duplicate candidate labels.")
                estimates[label][key] = generated.copy()
    if any(len(table) != 24 for table in estimates.values()):
        raise ValueError("Both initial and final labels must retain all 24 estimands.")
    ranges, deletions = {}, {}
    summaries = released["reference_sensitivity"]["summaries"]
    if {summary["estimand"] for summary in summaries} != {key for key in KEY_MAP if key.startswith("global_")} or len(summaries) != 4:
        raise ValueError("PSU sensitivity must contain exactly four global endpoints.")
    for summary in summaries:
        key = KEY_MAP[summary["estimand"]]
        ranges[key] = {"full": mapped_estimate(summary["full_estimate"]),
                       "minimum": summary["range_min"], "maximum": summary["range_max"],
                       "omitted_psu_groups": summary["omitted_psu_group_count"],
                       "finite_deletions": summary["finite_deletion_count"],
                       "failed_deletions": summary["failed_deletion_count"],
                       "rank_failed_deletions": summary["rank_failure_count"],
                       "finite_deletion_sign_stable_with_full": summary["finite_deletion_sign_stable_with_full"],
                       "all_deletions_sign_stable_with_full": summary["all_deletions_sign_stable_with_full"]}
        if summary["n_full"] != summary["full_estimate"]["n"] or len(summary["deletions"]) != summary["omitted_psu_group_count"]:
            raise ValueError("Released PSU sensitivity counts are inconsistent.")
        for deletion in summary["deletions"]:
            joint = (deletion["omitted_stratum"], deletion["omitted_psu"])
            record = deletions.setdefault(joint, {"stratum": joint[0], "psu": joint[1],
                                                 "omitted_n": deletion["n_omitted"],
                                                 "remaining_n": deletion["n_retained"], "estimates": {}})
            if record["omitted_n"] != deletion["n_omitted"] or record["remaining_n"] != deletion["n_retained"] or key in record["estimates"]:
                raise ValueError("Released deletion identity/counts are inconsistent or duplicated.")
            record["estimates"][key] = mapped_estimate(deletion)
    if any(len(record["estimates"]) != 4 for record in deletions.values()):
        raise ValueError("A deletion omits one or more fixed global coefficients.")
    return {"estimates": estimates, "reference_psu_sensitivity": {
                "ranges": ranges, "deletions": [deletions[key] for key in sorted(deletions)]},
            "preservation": {"changed_urate_rows": released["changed_urate_rows_initial_to_final"]},
            "unique_candidate_value_tables": released["unique_candidate_tables"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--released-json", required=True)
    parser.add_argument("--released-csv", required=True)
    parser.add_argument("--release-manifest", required=True)
    parser.add_argument("--expected-release-sha256", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise ValueError("Refusing overwrite of mapped aggregate.")
    manifest_hash = digest(args.release_manifest)
    if manifest_hash != args.expected_release_sha256:
        raise ValueError("Controller-provided release hash mismatch.")
    release = json.loads(Path(args.release_manifest).read_text(encoding="utf-8-sig"))
    released = json.loads(Path(args.released_json).read_text(encoding="utf-8-sig"))
    if released["release_manifest_sha256"] != manifest_hash or released["evaluator_sha256"] != release["evaluator_sha256"]:
        raise ValueError("Released aggregate binds to a different manifest or evaluator.")
    mapped = map_output(released)
    mapped["mapping_provenance"] = {"release_manifest_sha256": manifest_hash,
            "released_json_sha256": digest(args.released_json), "released_csv_sha256": digest(args.released_csv),
            "adapter_sha256": digest(__file__), "estimand_key_map": KEY_MAP,
            "json_csv_consistency": check_csv_export(released, args.released_csv),
            "method": "Field renaming and transpose of per-endpoint deletion lists into joint-group records; numerical values copied exactly. Both labels map to the single released table when grouped together."}
    output.write_text(json.dumps(mapped, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"fixed_estimands_per_label": 24, "labels": list(mapped["estimates"]),
                      "joint_psu_groups": len(mapped["reference_psu_sensitivity"]["deletions"]),
                      "csv_check": mapped["mapping_provenance"]["json_csv_consistency"]}))


if __name__ == "__main__":
    main()
