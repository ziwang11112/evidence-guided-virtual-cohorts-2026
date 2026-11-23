"""Measure d03 and d04 on identical seeds using the independent paper-based scorer."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from d03_secondary import D03, HERE, read, sha
from lung import evaluate


D04 = HERE / "private/replay_v2/d04"
AUDIT = HERE / "evidence_replay/BOUND_REVIEW_SCIENCE_AUDIT.json"


def score_tables(manifest, spec):
    units = {d["name"]:d["unit"] for d in spec["columns"]}
    assert units["fvc"] == units["fev1"] == "L" and units["sex"] == "1"
    assert "0=female" in spec["coding"]["sex"] and "1=male" in spec["coding"]["sex"]
    rows = []
    for item in manifest["runs"]:
        row = {k:item[k] for k in ("scenario","seed","status")}
        rows.append(row)
        if row["status"] != "success":
            continue
        path = Path(item["table"])
        assert sha(path) == item["sha256"]
        frame = pd.read_csv(path,float_precision="round_trip")
        canon = pd.DataFrame({"sex":frame["sex"].map({0:"F",1:"M"}),"fev1_l":frame.fev1,"fvc_l":frame.fvc})
        stat = evaluate(canon)
        row.update(table_sha256=item["sha256"],total_source_stats=16,
                   source_stats_replayed=stat["source_replay_inside_count"],
                   source_stats_missed=stat["source_replay_outside_or_undefined"],
                   two_unselected_r_squared_pct={s:stat["sex"][s]["source_replay"]["r_squared_pct"]["rows"]
                                                 for s in ("F","M")},
                   n=len(frame), n_unique_profiles=canon.drop_duplicates().shape[0],
                   impossible_volumes=stat["nonphysical_rows_fev1_exceeding_fvc"],
                   standardized_threshold_pct=stat["equal_sex_threshold_pct"],
                   standardized_ratio_of_means_pct=stat["equal_sex_ratio_of_means_pct"])
        for name, metric in (("below_070_pct","standardized_threshold_pct"),
                             ("ratio_of_means_pct","standardized_ratio_of_means_pct")):
            actual = frame["diagnostic_" + name]
            assert actual.nunique(dropna=False) == 1 and np.isclose(actual.iat[0],row[metric],rtol=0,atol=1e-9)
    return rows


def main():
    initial = read(D03 / "build.json")
    assert initial == read(D04 / "build.json")
    assert read(D03 / "design.json") == read(D04 / "design_as_authored.json")
    assert read(D03 / "trial_public.json") == read(D04 / "trial_public.json")
    trial = score_tables(read(D03/"trial_manifest.json"),initial["model_spec"])
    assert trial == score_tables(read(D04/"trial_manifest.json"),initial["model_spec"])
    feedback = read(D04 / "source_feedback_sent.json")
    request = read(D04 / "episodes/development/calls/0003/request.json")
    assert json.dumps(feedback) in request["input"]
    review = read(D04 / "review.json")
    old_final = score_tables(read(D03 / "final_manifest.json"),initial["model_spec"])
    candidate = review.get("candidate", initial) if review["action"] == "revise" else initial
    new_final = score_tables(read(D04 / "final_manifest.json"),candidate["model_spec"])
    paired = []
    for row in new_final:
        prior = next((r for r in old_final if (r["seed"],r["scenario"])==(row["seed"],row["scenario"])),None)
        if prior and prior["status"] == row["status"] == "success":
            paired.append({"scenario":row["scenario"],"seed":row["seed"],
                           "same_table_hash":row["table_sha256"] == prior["table_sha256"],
                           "inside_printed_intervals_before_and_after":[prior["source_stats_replayed"],row["source_stats_replayed"]],
                           "threshold_change_pp":row["standardized_threshold_pct"] - prior["standardized_threshold_pct"],
                           "ratio_of_means_change_pp":row["standardized_ratio_of_means_pct"] - prior["standardized_ratio_of_means_pct"]})
    report = {"case":"Polish lung development, project-exposed paper; one fixed-initial fork",
              "article_doi":"10.1186/1465-9921-13-57","total_source_stats":16,
              "retained_raw_design_build_and_trial_tables":True,"feedback_present_in_review_request":True,
              "actual_trial_feedback_counts":[r["counts"] for r in feedback["runs"]],
              "review_action":review["action"],"common_trial":trial,"original_final_same_seeds":old_final,
              "fork_final":new_final,"paired_seed_comparison":paired,
              "unobserved_target":"The paper does not supply a tabulated measured cutoff prevalence."}
    with AUDIT.open("x",encoding="utf8") as f:
        json.dump(report,f,indent=2,allow_nan=False)


if __name__ == "__main__":
    main()
