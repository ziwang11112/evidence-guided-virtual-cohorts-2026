"""Independent verification of the conditional permutation expectation from saved draws."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr


HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "chns_iron_conditional_holdout_2026-11-19"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def expected(h, f):
    x, y = rankdata(h), rankdata(f)
    x, y = x - x.mean(), y - y.mean()
    masks = [h < 12, (h >= 12) & (h < 14), h >= 14]
    mean_y_given_band = np.empty_like(y)
    for group in masks:
        mean_y_given_band[group] = y[group].mean()
    return float(np.dot(x, mean_y_given_band) / (np.linalg.norm(x) * np.linalg.norm(y)))


def cells(h, f):
    return np.bincount((h < 12).astype(int) * 2 + (f < 15).astype(int), minlength=4)


def exhaustive_example():
    h = np.array([10.,11.,12.,13.,14.,15.])
    f = np.array([6.,16.,15.,15.,10.,30.])
    ranks = []
    for idx in itertools.product(*(itertools.permutations(pair) for pair in [(0,1),(2,3),(4,5)])):
        g = f[np.array(idx).ravel()]
        np.testing.assert_array_equal(cells(h,g), cells(h,f))
        ranks.append(spearmanr(h,g).statistic)
    np.testing.assert_allclose(expected(h,f), np.mean(ranks), atol=1e-12, rtol=0)
    return len(ranks)


def saved_draws():
    laws = read(OLD / "SOURCE_CLOSURE.json")["models"]
    results = read(HERE / "RESULTS.json")["results"]
    rows = []
    for p in results["pairs"]:
        name = p["parent"] + "_control"
        pieces = []
        for run in laws[name]["runs"]:
            path = OLD / "private/runs" / name / str(run["seed"]) / "output/generated.csv"
            assert hashlib.sha256(path.read_bytes()).hexdigest() == run["hash"]
            pieces.append(pd.read_csv(path, usecols=["hb_g_dl","ferritin_ug_l"]))
        data = pd.concat(pieces, ignore_index=True)
        h, f = data["hb_g_dl"].to_numpy(), data["ferritin_ug_l"].to_numpy()
        perm_rank = expected(h,f)
        orig_rank = spearmanr(h,f).statistic
        np.testing.assert_allclose([perm_rank,orig_rank], [p["repairing_expectation"]["rank"],p["agent"]["rank"]], atol=1e-12,rtol=0)
        reverse = f.copy()
        for mask in (h < 12, (h >= 12) & (h < 14), h >= 14):
            reverse[mask] = f[mask][::-1]
        np.testing.assert_array_equal(cells(h,reverse), cells(h,f))
        a,b,c,d = [int(x) for x in cells(h,f)]
        np.testing.assert_allclose(a*d/(b*c), p["agent"]["odds_ratio"], rtol=1e-12)
        rows.append({"parent":p["parent"],"input_draw_hashes_matched":len(pieces),
                     "pooled_rows":len(data),"authored_and_expected_ranks_verified":True,
                     "four_threshold_cells_preserved":True})
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-local-draws",action="store_true")
    parser.add_argument("--receipt",type=Path)
    args = parser.parse_args()
    outcome = {"exhaustive_tied_rank_permutations":exhaustive_example()}
    if args.check_local_draws:
        outcome["original_controls"] = saved_draws()
    if args.receipt:
        with args.receipt.open("x",encoding="utf-8",newline="\n") as handle:
            json.dump(outcome,handle,indent=2)
            handle.write("\n")
    print(json.dumps(outcome))
