"""Audit how much iron rank correlation can change with the source checks fixed.

Default: replay the published statistical comparator in memory. With --archived,
read its three existing synthetic CSVs and check their original receipt hashes.
Both paths print aggregate results only. No target observations are used.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

IRON = Path(__file__).resolve().parents[1] / "original_paper_iron_sensitivity_2026-11-19"
sys.path.insert(0, str(IRON))
from neutral import generate
from scoring import assess


def read_json(name):
    return json.loads((IRON / name).read_text(encoding="utf-8-sig"))


def baseline(archived):
    plan = read_json("FREEZE.json")
    draws = read_json("INTERFACE_CLOSURE.json")["laws"]["statistical"]["draws"]
    assert [draw["seed"] for draw in draws] == plan["seeds"]["statistical"]
    frames = []
    for draw in draws:
        seed = draw["seed"]
        assert draw["status"] == "success"
        if archived:
            path = IRON / "private_runs" / "runs" / "statistical" / str(seed) / "output" / "generated.csv"
            assert hashlib.sha256(path.read_bytes()).hexdigest() == draw["sha256"]
            frame = pd.read_csv(path)
        else:
            frame = generate(None, {"task": plan["task"]}, seed)
        assert len(frame) == plan["task"]["n_rows"]
        frames.append(frame[["hb_g_dl", "ferritin_ug_l"]])
    return pd.concat(frames, ignore_index=True)


def pairings(frame, cells, original):
    hb = frame["hb_g_dl"].to_numpy()
    ferritin = frame["ferritin_ug_l"].to_numpy()
    hr, fr = rankdata(hb), rankdata(ferritin)
    hr -= hr.mean()
    fr -= fr.mean()
    denominator = np.linalg.norm(hr) * np.linalg.norm(fr)
    endpoints = {}
    for name, descending in [("minimum", True), ("maximum", False)]:
        values = np.empty_like(ferritin)
        numerator = 0.0
        for cell in np.unique(cells):
            indices = np.flatnonzero(cells == cell)
            hb_order = indices[np.argsort(hb[indices], kind="stable")]
            ordered_f = np.sort(ferritin[indices])
            ordered_ranks = np.sort(fr[indices])
            if descending:
                ordered_f = ordered_f[::-1]
                ordered_ranks = ordered_ranks[::-1]
            values[hb_order] = ordered_f
            # Rearrangement inequality on the globally centered ranks in this cell.
            numerator += np.dot(np.sort(hr[indices]), ordered_ranks)
        score = assess(frame.assign(ferritin_ug_l=values))
        np.testing.assert_allclose(score["spearman"], numerator / denominator, rtol=0, atol=1e-12)
        assert score["tier2"] and score["checks"].keys() == original["checks"].keys()
        for key, entry in original["checks"].items():
            np.testing.assert_allclose(score["checks"][key]["draw"], entry["draw"], rtol=0, atol=1e-12)
        assert score["odds_ratio"] == original["odds_ratio"]
        endpoints[name] = round(score["spearman"], 9)
    return endpoints


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archived", action="store_true", help="read the locally archived statistical comparator draws")
    args = parser.parse_args()
    frame = baseline(args.archived)
    original = assess(frame)
    published = read_json("SCIENTIFIC_RESULTS.json")["laws"]["statistical"]
    assert len(frame) == published["n"] and len(original["checks"]) == 16 and original["tier2"]
    for name in ["odds_ratio", "spearman"]:
        np.testing.assert_allclose(original[name], published[name], rtol=0, atol=1e-12)
    for key, entry in published["checks"].items():
        np.testing.assert_allclose(original["checks"][key]["draw"], entry["draw"], rtol=0, atol=1e-12)
    band = np.digitize(frame["hb_g_dl"], [10.0, 12.0])
    depleted = frame["ferritin_ug_l"].to_numpy() < 15.0
    result = {
        "statistical_comparator_rows": len(frame),
        "preserved_source_summaries": len(original["checks"]),
        "original_and_all_rearrangements_odds_ratio": round(original["odds_ratio"], 9),
        "original_spearman": round(original["spearman"], 9),
        "spearman_permuting_within_hb_band": pairings(frame, band, original),
        "spearman_permuting_within_hb_band_and_depletion_status": pairings(frame, 2 * band + depleted, original),
    }
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
