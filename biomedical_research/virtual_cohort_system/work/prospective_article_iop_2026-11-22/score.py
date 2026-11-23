"""Apply the registered tolerances to each final table and the sealed reference."""
import argparse
from itertools import combinations
from pathlib import Path
import json

import numpy as np
import pandas as pd

from evaluate import evaluate
from seal import HERE, EPISODE, ROOT, sha


def source_checks(o):
    limits = {"pascal_mean_mmhg":16.89, "goldmann_mean_mmhg":15.06,
              "pascal_sd_mmhg":2.49, "goldmann_sd_mmhg":2.71}
    passed = {k: abs(o[k] - target) <= .10 + 1e-12 for k, target in limits.items()}
    r = o["pearson_r"]
    passed["pearson_r"] = r is not None and min(abs(r - x) for x in (.5969,.597,.598)) <= .025
    passed["abs_ge_4_pct"] = abs(o["abs_ge_4_pct"] - 19) <= 2 + 1e-12
    passed["positive_majority_among_extreme"] = (o["among_abs_ge_4_pascal_higher_n"]
                                                  > o["among_abs_ge_4_goldmann_higher_n"])
    passed["positive_complete"] = (o["positive_pressure_check"]["either_nonpositive_n"] == 0
                                   and o["n_incomplete"] == 0)
    return passed


def compare(p_col, g_col, measured):
    seal = json.loads((HERE/"PREREVEAL.json").read_text(encoding="utf8"))
    for name, checksum in seal["files"].items():
        path = ROOT / name
        if path == HERE / "PREREVEAL_READING.md":
            # The formal note contained a typo in a digest in its footer. Verify
            # the preserved original bytes against the seal; the edited copy is commentary.
            path = HERE / "PREREVEAL_READING.as_sealed.md"
        if sha(path) != checksum:
            raise ValueError("Preregistered file changed: " + name)
    manifest = json.loads((EPISODE/"final_manifest.json").read_text(encoding="utf8"))
    observed = evaluate(measured, "pascal", "goldmann", measured=True, id_column="subject")
    report = {"measured":observed, "measured_source_checks":source_checks(observed), "runs":[]}
    groups = {}
    for run in manifest["runs"]:
        entry = {k:run[k] for k in ("scenario","seed","status")}
        report["runs"].append(entry)
        groups.setdefault(run["scenario"], {})[run["seed"]] = entry
        if run["status"] != "success":
            continue
        path = Path(run["table"])
        if sha(path) != run["sha256"]:
            raise ValueError("Unverified table")
        frame = pd.read_csv(path, float_precision="round_trip")
        o = evaluate(frame, p_col, g_col, id_column="row_id")
        checks = source_checks(o)
        entry.update(outcomes=o, checks=checks, source_eligible=all(checks.values()),
                     mean_use_agreement=abs(o["mean_difference_mmhg"] - 1.83) <= .10 + 1e-12,
                     measured_discrepancies={k:o[k]-observed[k]
                         for k in ("mean_difference_mmhg","signed_gt_3_pct")})
    scenarios = {}
    seeds = {823031,823039,823043}
    for name, group in groups.items():
        complete = set(group) == seeds and all(x["status"]=="success" for x in group.values())
        row = {"complete":complete, "all_seeds_source_eligible":complete and all(
               x["source_eligible"] for x in group.values()), "all_means_acceptable":complete and all(
               x["mean_use_agreement"] for x in group.values())}
        if complete:
            for k in ("mean_difference_mmhg","signed_gt_3_pct","abs_ge_4_pct"):
                vals = [x["outcomes"][k] for x in group.values()]
                row[k] = {"min":min(vals),"max":max(vals),"average":float(np.mean(vals))}
        scenarios[name] = row
    pairs = []
    for a,b in combinations(groups,2):
        row = {"scenarios":[a,b],"qualifies":False}
        if scenarios[a]["complete"] and scenarios[b]["complete"]:
            diff = [groups[b][s]["outcomes"]["signed_gt_3_pct"] -
                    groups[a][s]["outcomes"]["signed_gt_3_pct"] for s in sorted(seeds)]
            row.update(seed_differences_pp=diff, qualifies=bool(
                all(scenarios[q]["all_seeds_source_eligible"] and scenarios[q]["all_means_acceptable"]
                    for q in (a,b)) and abs(np.mean(diff)) >= 5 and (min(diff) > 0 or max(diff) < 0)))
        pairs.append(row)
    vals = [r["outcomes"]["signed_gt_3_pct"] for r in report["runs"] if r["status"]=="success"]
    report.update(scenarios=scenarios, pairs=pairs, measured_in_full_descriptive_span=(
                  min(vals) <= observed["signed_gt_3_pct"] <= max(vals) if vals else None))
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--virtual-columns", nargs=2, required=True)
    args = p.parse_args()
    sealed = json.loads((HERE / "PREREVEAL.json").read_text(encoding="utf8"))
    workbook = HERE / "private/sealed.xlsx"
    if sha(workbook) != sealed["files"][workbook.relative_to(ROOT).as_posix()]:
        raise ValueError("The measured workbook differs from the sealed bytes")
    frame = pd.read_excel(workbook, sheet_name="Sheet1", usecols=["Avg DCT OS","Avg GAT OS"])
    frame = frame.rename(columns={"Avg DCT OS":"pascal","Avg GAT OS":"goldmann"})
    # The original bilateral worksheet has one subject per row and no subject ID.
    frame["subject"] = np.arange(len(frame)) + 2
    result = compare(*args.virtual_columns, frame)
    result["measured_extraction"] = {"sheet":"Sheet1", "pascal":"Avg DCT OS",
                "goldmann":"Avg GAT OS", "record_key":"worksheet row; no subject ID released",
                "supplement_sha256":sha(workbook)}
    output = HERE/"ANALYSIS.json"
    data = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
    if output.exists() and output.read_text(encoding="utf8") != data:
        raise ValueError("Aggregate result changed")
    output.write_text(data, encoding="utf8")
