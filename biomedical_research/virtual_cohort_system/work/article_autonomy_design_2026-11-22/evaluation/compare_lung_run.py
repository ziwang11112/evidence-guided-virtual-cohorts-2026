"""Apply the independent lung estimators to all frozen d02 outputs."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lung import evaluate


def load(path):
    return json.loads(path.read_text(encoding="utf8"))


def compare(manifest, mapping):
    tables = []
    values = {}
    for run in manifest["runs"]:
        row = {key: run[key] for key in ("scenario", "seed", "status")}
        tables.append(row)
        if row["status"] != "success":
            row["error"] = run.get("public_error")
            continue
        path = Path(run["table"])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != run["sha256"]:
            raise ValueError("Frozen table hash mismatch")
        table = pd.read_csv(path, float_precision="round_trip")
        sex = mapping["sex"]
        canonical = pd.DataFrame({"sex":table[sex["column"]].map(
            {float(code):label for code,label in sex["codes"].items()})})
        for name, definition in mapping["volumes"].items():
            canonical[name] = table[definition["column"]] * definition["litre_factor"]
        row["table_sha256"] = digest
        row["independent"] = stats = evaluate(canonical)
        row["authored_estimands"] = {}
        if stats["status"] != "computed":
            continue
        for key, field in mapping["estimands"].items():
            diagnostic = table["diagnostic_" + field["name"]]
            if diagnostic.nunique(dropna=False) != 1:
                raise ValueError("Authored scalar was not constant on its table")
            estimate = float(diagnostic.iat[0]) * field["to_percent"]
            row["authored_estimands"][key] = {"authored_pct":estimate, "independent_pct":stats[key],
                                              "abs_difference_pp":abs(estimate - stats[key])}
        values[(row["seed"], row["scenario"])] = (
            stats, [np.sort(canonical.loc[canonical.sex == sex, ["fev1_l","fvc_l"]].to_numpy(),
                            axis=0) for sex in ("F", "M")])

    contrasts = []
    for seed in sorted({k[0] for k in values}):
        names = [name for s, name in values if seed == s]
        for a, b in itertools.combinations(names, 2):
            one, x = values[seed, a]
            two, y = values[seed, b]
            contrasts.append({"seed":seed, "first":a, "second":b,
                              "threshold_change_pp":two["equal_sex_threshold_pct"] - one["equal_sex_threshold_pct"],
                              "ratio_change_pp":two["equal_sex_ratio_of_means_pct"] - one["equal_sex_ratio_of_means_pct"],
                              "sex_specific_sorted_columns_identical":all(np.array_equal(u,v) for u,v in zip(x,y)),
                              "both_pass_16_unadjusted_source_checks":all(s["source_replay_inside_count"] == 16 for s in (one,two))})
    return {"status":manifest["status"], "candidate_sha256":manifest["candidate_sha256"],
            "tables":tables,"within_seed_scenario_contrasts":contrasts}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("manifest", "mapping", "output"):
        p.add_argument(key, type=Path)
    args = p.parse_args()
    result = compare(load(args.manifest), load(args.mapping))
    with args.output.open("x", encoding="utf8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
