"""Prepare aggregate-only plotting inputs from the sealed Akwa Ibom and Turkana results."""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

OUT = Path(__file__).resolve().parent
WORK = OUT.parent
IRON = WORK / "prospective_iron_dependence_2026-11-20"
LIFESTYLE = WORK / "matched_size_utility_2026-11-17"


def load(folder, name):
    return json.loads((folder / name).read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def profile(values, expected):
    h, f = values.T
    rank = float(spearmanr(h, f).statistic)
    cells = [int(np.sum(((h < 12) == a) & ((f < 15) == b)))
             for a, b in ((True, True), (True, False), (False, True), (False, False))]
    a, b, c, d = cells
    odds = a * d / (b * c)
    np.testing.assert_allclose([rank, odds], [expected["rank"], expected["odds_ratio"]], rtol=0, atol=1e-12)
    n = len(h)
    def quartile(x):
        return np.floor(4*(rankdata(x, method="average")-.5)/n).astype(int)
    qh, qf = quartile(h), quartile(f)
    grid, _, _ = np.histogram2d(qh, qf, bins=(np.arange(5), np.arange(5)))
    grid = grid.astype(int)
    assert grid.sum() == n
    np.testing.assert_array_equal(grid.sum(axis=1), np.bincount(qh, minlength=4))
    return {"n": n, "grid_hb_by_fe": grid.tolist(), "rank": rank, "odds": odds}


def iron():
    result, sealed, admission = (load(IRON, n) for n in ("RESULTS.json","DRAW_CLOSURE.json","ADMISSION.json"))
    src = IRON / "private/biochem.dta"
    assert sha(src) == admission["files"]["biochem.dta"]["sha256"]
    frame = pd.read_stata(src, convert_categoricals=False,
                          columns=["Group","SEX","AGE_MOTHER","HGB","FER_ug_L"])
    okay = (frame.Group.str.strip().eq("M") & frame.SEX.eq(2) & frame.AGE_MOTHER.between(18,49)
            & frame.HGB.gt(0) & frame.FER_ug_L.gt(0) & np.isfinite(frame.HGB) & np.isfinite(frame.FER_ug_L))
    observed = profile(frame.loc[okay,["HGB","FER_ug_L"]].to_numpy(), result["reference"])
    assert observed["n"] == result["reference"]["n"] == 603
    # Every reported measured cell is an aggregate of at least thirty participants.
    assert np.min(observed["grid_hb_by_fe"]) >= 30
    profiles = {}
    for name in ["statistical"]+[f"author{i}" for i in range(1,7)]:
        draws = []
        for rec in sealed["models"][name]["runs"]:
            f = IRON / "private/cohorts" / name / (str(rec["seed"])+".npy")
            assert sha(f) == rec["npy_sha256"]
            draws.append(np.load(f, allow_pickle=False))
        profiles[name] = profile(np.vstack(draws), result["by_law"][name])
    assert all(p["n"]==36000 for p in profiles.values())
    reference = np.array(profiles["author1"]["grid_hb_by_fe"])
    diff = max(np.abs(np.array(profiles[f"author{i}"]["grid_hb_by_fe"])-reference).max() for i in range(1,7))
    return {"measured": observed, "agent": profiles["author1"], "statistical": profiles["statistical"],
            "agent_slot_choice":"First pre-numbered author; no selection by target score",
            "max_bin_count_difference_from_author1_among_six": int(diff),
            "measured_cluster_intervals": {k:result["paired_bootstrap"][k]["percentile95"]
                                            for k in ("reference_rank","reference_odds_ratio")},
            "frozen_results_sha256": sha(IRON/"RESULTS.json")}


def lifestyle():
    source = LIFESTYLE / "DIFFERENCES.csv"
    df = pd.read_csv(source)
    summary = pd.read_csv(LIFESTYLE / "CONTRAST_SUMMARIES.csv")
    assert len(df)==31_500 and df.status.eq("computed").all()
    assert not df.duplicated(["trait","contrast","stream","replicate"]).any()
    all_curves = {}
    # All facets within a trait use identical physical boundaries; they include all saved replicates.
    for trait, limit in [("bmi", 2.0), ("total_cholesterol", 45.0), ("hdl_cholesterol", 25.0)]:
        xs = np.linspace(-limit,limit,241)
        sub = df[df.trait==trait]
        assert len(sub)==10_500 and sub.difference.abs().max() < limit
        facets = {}
        for contrast, group in sub.groupby("contrast", sort=True):
            differences = {}
            absolute = {}
            for stream, sample in group.groupby("stream", sort=True):
                values = np.sort(sample.difference.to_numpy())
                assert len(values)==500 and sample.replicate.nunique()==500
                saved = summary[(summary.trait==trait)&(summary.contrast==contrast)&(summary.stream==stream)].squeeze()
                np.testing.assert_allclose([values.mean(),np.abs(values).mean()],
                                           [saved.signed_mean,saved.absolute_mean],atol=1e-12,rtol=0)
                differences[stream]=np.searchsorted(values,xs,side="right")
                absolute[stream]=float(np.abs(values).mean())
            real = differences.pop("R_A")
            real_abs = absolute.pop("R_A")
            assert len(differences)==len(absolute)==6
            curves = np.asarray(list(differences.values()))
            facets[contrast] = {
                "real_ecdf_n":real.tolist(),"virtual_min_ecdf_n":curves.min(axis=0).tolist(),
                "virtual_max_ecdf_n":curves.max(axis=0).tolist(),
                "virtual_median_ecdf_n":np.median(curves,axis=0).tolist(),
                "absolute_gap_real_real":real_abs,
                "absolute_gap_virtual_real_range":[min(absolute.values()),max(absolute.values())]}
        assert len(facets)==3
        all_curves[trait]={"x_grid":np.round(xs,7).tolist(),"facets":facets}
    return {"n_per_stream":500,"constructor_count":2,"tables_per_constructor":3,"traits":all_curves,
            "differences_sha256":sha(source),"published_summary_sha256":sha(LIFESTYLE/"CONTRAST_SUMMARIES.csv")}


if __name__=="__main__":
    data={"iron":iron(),"lifestyle":lifestyle()}
    (OUT/"plot_inputs.json").write_text(json.dumps(data,separators=(",",":"),allow_nan=False)+"\n",
                                        encoding="utf-8",newline="\n")
    print("Checked measured sample, all 21 sealed virtual draws, 9 contrasts, 63 saved summaries and 31,500 resampling differences.")
