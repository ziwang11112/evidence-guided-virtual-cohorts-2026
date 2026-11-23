"""Independent, evaluator-side source and row audit of the frozen d03 lung run."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lung import evaluate, PRECISION, SOURCE


HERE = Path(__file__).resolve().parent.parent
D03 = HERE / "private/replay_v1/d03"
OUTPUT = HERE / "evidence_replay/LIVE_SCIENCE_AUDIT.json"


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class Definition:
    field: str
    kind: str
    y: str
    x: str = ""


DEFS = {
    "fvc_mean": Definition("fvc_mean_l", "mean", "fvc"),
    "fvc_sd": Definition("fvc_sd_l", "sd", "fvc"),
    "fev1_mean": Definition("fev1_mean_l", "mean", "fev1"),
    "fev1_sd": Definition("fev1_sd_l", "sd", "fev1"),
    "correlation": Definition("pearson_r", "pearson", "fev1", "fvc"),
    "regression_slope": Definition("ols_slope", "ols_slope", "fev1", "fvc"),
    "regression_intercept": Definition("ols_intercept_l", "ols_intercept", "fev1", "fvc"),
}


def inspect_inventory(items):
    audit = {}
    for sex, label, code in (("F","female",0),("M","male",1)):
        for suffix, expected in DEFS.items():
            key = f"{label}_{suffix}"
            item = next(r for r in items if r["id"] == key)
            ref, op = item["reference"], item["operator"]
            columns_ok = expected.y == op.get("y") and expected.x == op.get("x", "")
            if expected.kind == "pearson":
                columns_ok = {op.get("x"), op.get("y")} == {"fvc","fev1"}
            unit = "1" if suffix in {"correlation","regression_slope"} else "L"
            science_ok = (columns_ok and op["where"] == [dict(column="sex",cmp="eq",value=code)]
                          and op["kind"] == expected.kind and ref["unit"] == unit
                          and ref["value"] == SOURCE[sex][expected.field]
                          and np.isclose(10**-ref["decimals"],PRECISION[expected.field])
                          and (expected.kind != "sd" or op["ddof"] == 1))
            audit[key] = dict(agrees_with_printed_source_and_roles=bool(science_ok),
                              input_unit_map_present="units" in op)
    return audit


def independent_rows(manifest):
    tables = []
    for r in manifest["runs"]:
        obj = {k:r[k] for k in ("seed","scenario","status")}
        tables.append(obj)
        if r["status"] != "success":
            continue
        path = Path(r["table"])
        assert sha(path) == r["sha256"]
        frame = pd.read_csv(path, float_precision="round_trip")
        canonical = pd.DataFrame({"sex":frame["sex"].map({0:"F",1:"M"}),
                                  "fev1_l":frame["fev1"],"fvc_l":frame["fvc"]})
        outcome = evaluate(canonical)
        obj.update(table_sha256=r["sha256"], full_source_checks_inside=outcome["source_replay_inside_count"],
                   full_source_checks_outside=outcome["source_replay_outside_or_undefined"],
                   nonphysical=outcome["nonphysical_rows_fev1_exceeding_fvc"],
                   n=len(frame), standardized_threshold_pct=outcome["equal_sex_threshold_pct"],
                   standardized_ratio_of_means_pct=outcome["equal_sex_ratio_of_means_pct"],
                   n_distinct_sex_and_volume_pairs=canonical.drop_duplicates().shape[0])
    return tables


def main():
    inv = read(D03/"source_inventory.json")["evidence_checks"]
    checks = inspect_inventory(inv)
    feedback = read(D03/"source_feedback_sent.json")
    body = read(D03/"episodes/development/calls/0003/request.json")
    assert json.dumps(feedback) in body["input"]
    final = read(D03/"final_source_replay.json")
    report = dict(case="project-exposed Polish lung development case", doi="10.1186/1465-9921-13-57",
                  source_inventory_sha256=sha(D03/"source_inventory.json"), selected_total=len(inv),
                  independent_semantic_check=checks,
                  outside_inventory_published_joint_entries=["female_r_squared_pct","male_r_squared_pct"],
                  material_source_info_unavailable_to_this_audit="Tabulated participant threshold prevalence.",
                  trial_feedback_in_request=True,
                  trial_replay_counts=[r["counts"] for r in feedback["runs"]],
                  selected_missing_unit_maps=sum(not c["input_unit_map_present"] for c in checks.values()),
                  review_action=read(D03/"review.json")["action"],
                  final_replay_status_counts=[r["counts"] for r in final["runs"]],
                  final_rows=independent_rows(read(D03/"final_manifest.json")))
    with OUTPUT.open("x",encoding="utf8") as stream:
        json.dump(report,stream,indent=2,allow_nan=False)


if __name__ == "__main__":
    main()
