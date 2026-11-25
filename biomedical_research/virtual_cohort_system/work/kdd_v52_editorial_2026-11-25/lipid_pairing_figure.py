"""Rebuild the lipid overview from verified simulation outputs or the saved aggregate.

Run with --rebuild-aggregate where the original frozen simulation files are present.
The default plots the public, aggregate-only input and requires only numpy/matplotlib.
No patient measurements, individual synthetic values, or new generator runs are used.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
STUDY = HERE.parent / "kdd_v40_pairing_review_2026-11-20"
SOURCE = HERE.parent / "nonhdl_external_2026-11-20" / "SOURCE.json"
AGGREGATE = HERE / "lipid_pairing_figure_data.json"
OUT = PROJECT / "manuscript" / "kdd_draft_v52_2026-11-25" / "figures"
THRESHOLD = 160
SEEDS = (40937, 40949, 40961)
BINS = 64
AUTHOR = "author2"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def summarize():
    study = read(STUDY / "SENSITIVITY.json")["authors"]
    selected = study[AUTHOR]
    require(selected["both_pass"] and selected["gap_pp"] == min(v["gap_pp"] for v in study.values()),
            "Selected author is not the minimum-gap admissible example.")
    src = read(SOURCE)
    threshold_grid = np.arange(60, 261, 1)
    data = {"source": src["article"], "source_mean_ratio": src["mean_individual_ratio"]["estimate"],
            "author": AUTHOR, "seeds": list(SEEDS), "bins": BINS,
            "screening_cutoff_mg_dl": THRESHOLD, "curve_thresholds_mg_dl": threshold_grid.tolist(),
            "scenarios": {}}
    ref_tc = ref_hdl = None
    for label in ("a", "b"):
        counts = np.zeros((BINS, BINS), dtype=np.int64)
        survival = np.zeros(threshold_grid.size, dtype=np.int64)
        total_n = above = 0
        sum_ratio = sum_diff = 0.
        records = selected["runs"][label]
        require(tuple(r["seed"] for r in records) == SEEDS, "Unexpected frozen seeds.")
        for rec in records:
            run = STUDY / "private" / "draws" / AUTHOR / label / str(rec["seed"])
            permutation_path = run / "perm.npy"
            require(hashlib.sha256(permutation_path.read_bytes()).hexdigest() == rec["permutation_hash"],
                    "Frozen permutation checksum mismatch.")
            permutation = np.load(permutation_path, allow_pickle=False)
            spec = read(run / "candidate" / "model_spec.json")
            tc = np.asarray(spec["tc_mg_dl"])
            hdl = np.asarray(spec["hdl_mg_dl"])
            n = len(tc)
            require(spec["scenario"] == label and n == rec["score"]["n"] == len(hdl)
                    and n % BINS == 0 and np.all(np.diff(tc) > 0) and np.all(np.diff(hdl) > 0)
                    and np.issubdtype(permutation.dtype, np.integer)
                    and np.array_equal(np.sort(permutation), np.arange(n)),
                    "Invalid or incorrectly identified marginal arrays and permutation.")
            if ref_tc is None:
                ref_tc, ref_hdl = tc, hdl
            require(np.array_equal(tc, ref_tc) and np.array_equal(hdl, ref_hdl),
                    "Marginal grids differ between frozen arms.")
            ranks = np.arange(n) * BINS // n
            counts += np.bincount(ranks * BINS + ranks[permutation], minlength=BINS ** 2).reshape(BINS, BINS)
            paired_hdl = hdl[permutation]
            diff = tc - paired_hdl
            require(np.min(diff) >= 0, "Biomarker ordering violated.")
            above_now = int(np.count_nonzero(diff >= THRESHOLD))
            ratio_now = np.mean(tc / paired_hdl)
            require(above_now == rec["score"]["tail_count"]
                    and np.isclose(ratio_now, rec["score"]["mean_ratio"], rtol=0, atol=1e-10)
                    and np.isclose(diff.mean(), rec["score"]["mean"], rtol=0, atol=1e-10),
                    "Independent native-unit estimates differ from frozen receipt.")
            sorted_diff = np.sort(diff)
            survival += n - np.searchsorted(sorted_diff, threshold_grid, side="left")
            total_n += n
            above += above_now
            sum_ratio += ratio_now * n
            sum_diff += diff.sum()
        share = 100 * above / total_n
        avg = sum_diff / total_n
        require(np.all(counts.sum(axis=0) == total_n // BINS) and
                np.all(counts.sum(axis=1) == total_n // BINS) and
                above == survival[threshold_grid.tolist().index(THRESHOLD)] and
                np.isclose(share, selected["scenarios"][label]["percent"], rtol=0, atol=1e-10),
                "Binned marginal or survival checksum mismatch.")
        data["scenarios"][label] = {"n": total_n, "above": above, "above_percent": share,
                                     "mean_nonhdl_mg_dl": avg, "mean_individual_ratio": sum_ratio / total_n,
                                     "occupied_cells": [[int(i), int(j), int(counts[i, j])]
                                                        for i, j in zip(*np.nonzero(counts))],
                                     "survival_counts": survival.tolist()}
    pct = 100 * (np.arange(len(ref_tc)) + .5) / len(ref_tc)
    # Draw the cutoff in rank coordinates using the fixed marginal quantile functions.
    # Include its intersections with the frame before clipping the curve there.
    cut_x = np.unique(np.r_[np.linspace(0, 100, 401),
                            np.interp([ref_hdl.min()+THRESHOLD, ref_hdl.max()+THRESHOLD], ref_tc, pct)])
    tc_at_x = np.interp(cut_x, pct, ref_tc)
    cut_y = np.interp(tc_at_x - THRESHOLD, ref_hdl, pct, left=0, right=100)
    data["cutoff_rank_curve"] = np.column_stack([cut_x, cut_y]).round(8).tolist()
    return data


INK = "#20354b"
BLUE = "#214d82"
RUST = "#aa482d"
PALE = "#fbede6"
MUTED = "#4c5d6e"
RULE = "#bdc7d0"


def plot(data):
    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.0, "pdf.fonttype": 42,
                         "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": RULE,
                         "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": .5,
                         "axes.spines.right": False, "axes.spines.top": False})
    fig = plt.figure(figsize=(7, 2.24), facecolor="white")
    data_axes = [fig.add_axes(box) for box in ((.071,.242,.192,.535),(.312,.242,.192,.535),
                                                (.619,.242,.342,.535))]
    edge = np.asarray(data["cutoff_rank_curve"])
    size = 100 / data["bins"]
    maximum = max(cell[2] for v in data["scenarios"].values() for cell in v["occupied_cells"])
    for i, (ax, key) in enumerate(zip(data_axes[:2], ("a", "b"))):
        rec = data["scenarios"][key]
        ax.fill_between(edge[:, 0], 0, edge[:, 1], color=PALE, linewidth=0)
        patches, colors = [], []
        for x, y, count in rec["occupied_cells"]:
            patches.append(Rectangle((x*size, y*size), size, size))
            colors.append(to_rgba(BLUE, .24 + .76 * (count / maximum)**.5))
        ax.add_collection(PatchCollection(patches, facecolors=colors, edgecolors="none"))
        in_range = (edge[:, 1] > 0) & (edge[:, 1] < 100)
        ax.plot(edge[in_range, 0], edge[in_range, 1], color=RUST, lw=.85)
        ax.set(xlim=(0,100), ylim=(0,100), xticks=(0,50,100), yticks=(0,50,100))
        ax.set_xlabel("Total cholesterol percentile", fontsize=6.9, labelpad=3)
        if i == 0:
            ax.set_ylabel("HDL percentile", fontsize=7.2, labelpad=2)
        ax.tick_params(length=2, width=.5, pad=2, labelsize=6.5)
        ax.set_axisbelow(True)
    ax = data_axes[2]
    threshold = data["screening_cutoff_mg_dl"]
    ax.grid(axis="y", color="#dce2e8", lw=.45)
    ax.axvline(threshold, color=MUTED, ls=(0, (2, 2)), lw=.8)
    x = np.asarray(data["curve_thresholds_mg_dl"])
    for key, color, ls, delta in (("a",BLUE,"-",-5),("b",RUST,"--",6)):
        rec = data["scenarios"][key]
        y = 100*np.asarray(rec["survival_counts"])/rec["n"]
        ax.plot(x, y, color=color, lw=1.5, ls=ls)
        val = rec["above_percent"]
        ax.plot(threshold, val, "o", ms=4, mfc="white", mec=color, mew=1.15, zorder=4)
        ax.annotate(f"{key.upper()}  {val:.2f}%", xy=(threshold,val),
                    xytext=(threshold+26,val+delta), ha="left", va="center",
                    fontsize=7.3, fontweight="bold", color=color,
                    arrowprops={"arrowstyle":"-","color":color,"lw":.65,"shrinkA":1,"shrinkB":3},
                    bbox={"facecolor":"white","edgecolor":"none","pad":.6})
    ax.set(xlim=(60,260), ylim=(-3,103), xticks=(80,120,160,200,240), yticks=(0,25,50,75,100))
    ax.set_ylabel("At or above cutoff (%)", fontsize=7.0, labelpad=2)
    ax.set_xlabel("Non-HDL cutoff (mg/dL)", fontsize=7.1, labelpad=3)
    ax.tick_params(length=2, pad=2, width=.5, labelsize=6.5)
    ax.set_axisbelow(True)
    for x0, letter, title in ((.071,"A","Forward rank cycle"),(.312,"B","Reverse rank cycle"),
                              (.619,"C","Non-HDL screening")):
        fig.text(x0,.847,letter,weight="bold",fontsize=9.7,color=BLUE)
        fig.text(x0+.027,.847,title,weight="bold",fontsize=8.0)
    fig.text(.071,.96,"Mwanza lipid study",fontsize=7.5,weight="bold",va="center")
    fig.text(.258,.96,"One agent pairs the same cholesterol measurements in two ways",
             fontsize=7.25,va="center")
    fig.add_artist(plt.Line2D([.071,.961],[.917,.917],transform=fig.transFigure,color=RULE,lw=.58))
    fig.add_artist(Rectangle((.071,.029),.017,.031,transform=fig.transFigure,
                             facecolor=PALE,edgecolor=RUST,linewidth=.6))
    fig.text(.094,.043,"Non-HDL ≥ 160 mg/dL",fontsize=6.65,va="center")
    mean = data["scenarios"]["a"]["mean_nonhdl_mg_dl"]
    fig.text(.619,.043,f"Mean non-HDL in both: {mean:.2f} mg/dL",
             fontsize=6.9,va="center",weight="bold")
    fig.text(.312,.043,f"Both match mean TC/HDL = {data['source_mean_ratio']:.2f}",
             fontsize=6.65,va="center")
    OUT.mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT/"lipid-pairing-overview.pdf", metadata={"Title":"Lipid pairing and non-HDL screening",
                "Author":"", "Creator":"Matplotlib", "CreationDate":None,"ModDate":None})
    fig.savefig(HERE/"lipid-pairing-overview-preview.png",dpi=165,facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild-aggregate", action="store_true")
    args = parser.parse_args()
    if args.rebuild_aggregate:
        AGGREGATE.write_text(json.dumps(summarize(), separators=(",", ":"), allow_nan=False)
                             + "\n", encoding="utf-8")
    plot(read(AGGREGATE))
