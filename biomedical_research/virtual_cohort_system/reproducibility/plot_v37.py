"""Draw the two v0.37 result figures from archived aggregates. No participant rows."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.ticker import FixedLocator, ScalarFormatter
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
OUT = ROOT / "manuscript/kdd_draft_v37_2026-11-19/figures"
CHNS = WORK / "chns_iron_conditional_holdout_2026-11-19"
IRON = WORK / "original_paper_iron_sensitivity_2026-11-19"
BP = WORK / "prospective_bp_freetown_2026-11-18"
INK = "#222d3d"
BLUE = "#265d9b"
ORANGE = "#bd521e"
GUIDE = "#dce1e8"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "axes.labelsize": 8,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "text.color": INK, "axes.unicode_minus": True, "pdf.fonttype": 42,
})


def read(folder, stem):
    return json.loads((folder / (stem + ".json")).read_text(encoding="utf-8"))


def save(fig, filename):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for label in fig.findobj(Text):
        if label.get_visible() and label.get_text():
            box = label.get_window_extent(renderer)
            corners = [(box.x0, box.y0), (box.x1, box.y1)]
            if any(not fig.bbox.contains(x, y) for x, y in corners):
                raise ValueError(f"Text extends beyond {filename}: {label.get_text()}")
    fig.savefig(OUT / filename, metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def panel(ax, title):
    ax.set_title(title, loc="left", fontsize=9.2, fontweight="bold", pad=6)
    ax.spines[["left", "right", "top"]].set_visible(False)
    ax.spines["bottom"].set_color("#9ba7b7")
    ax.tick_params(axis="both", labelsize=7.4)
    ax.tick_params(axis="y", length=0, pad=4)
    ax.tick_params(axis="x", length=2.5)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color=GUIDE, linewidth=.5)


def show_results(ax, y, virtual, observed, interval):
    # Vertical separation reveals overlapping models. It has no numerical meaning.
    offsets = np.linspace(-.10, .10, len(virtual)) if len(virtual) > 1 else [0]
    ax.scatter(virtual, y + .16 + np.array(offsets), s=19, color=BLUE,
               linewidth=.45, edgecolor="white", zorder=3)
    if observed is None:
        ax.text(.025, y - .20, "No low-ferritin cases", transform=ax.get_yaxis_transform(),
                fontsize=6.7, color=ORANGE, va="center")
        return
    lo, hi = interval
    ax.plot([lo, hi], [y - .18] * 2, color=ORANGE, solid_capstyle="round", lw=1.45)
    ax.scatter(observed, y - .18, s=22, color=ORANGE, marker="D",
               edgecolor="white", linewidth=.5, zorder=4)


def overview():
    with (WORK / "original_paper_capability_2026-11-17/analysis/author_results.csv").open() as fp:
        authors = list(csv.DictReader(fp))
    def original(key):
        return [float(r["seed_mean"]) for r in authors if r["estimand"] == key]
    pns = read(WORK / "pns_evidence_content_control_2026-11-16/analysis", "REFERENCE_USED")["PNS"]
    nhanes = read(WORK / "iron_evidence_content_control_2026-11-16/analysis", "REFERENCE_USED")["original_aggregate"]["estimands"]
    freetown = read(BP, "AGGREGATES")["target"]
    pressure = read(BP, "MODEL_AUDIT")["population"]
    burkina = read(IRON, "REVEAL")["result"]
    iron_laws = [v for k, v in read(IRON, "SCIENTIFIC_RESULTS")["laws"].items() if k != "statistical"]
    chns = read(CHNS, "RESULTS")
    augmented = [pair["estimates"]["evidence"] for pair in chns["pairs"].values()]
    fig, axs = plt.subplots(2, 2, figsize=(7.03, 3.43),
                            gridspec_kw={"height_ratios": [1, 1.38]})
    fig.subplots_adjust(left=.107, right=.985, top=.86, bottom=.134, wspace=.45, hspace=.82)
    slopes, rates, odds, ranks = axs.ravel()
    panel(slopes, "A   Brazil · BMI and blood pressure")
    for y, key in [(1, "bmi_sbp"), (0, "bmi_dbp")]:
        item = pns[key]
        show_results(slopes, y, original(key), item["value"],
                     [item["uncertainty"][k] for k in ["lower", "upper"]])
    slopes.set(yticks=[1, 0], yticklabels=["Systolic", "Diastolic"], ylim=(-.5, 1.5),
               xlim=(1.6, 4.45), xticks=[2, 3, 4], xlabel="Adjusted slope (mmHg per 5 kg/m² BMI)")
    panel(rates, "B   Freetown · joint screening")
    show_results(rates, 0, [100 * pressure[k]["Q2"] for k in ("primary", "alternative")],
                 100 * freetown["estimates"]["Q2"], 100 * np.array(freetown["within_zone_intervals"]["Q2"]))
    rates.set(yticks=[0], yticklabels=["Both high"], ylim=(-.53, .54), xlim=(0, 50),
              xticks=[0, 10, 20, 30, 40, 50], xlabel="SBP ≥140 and DBP ≥90 mmHg (%)")
    for ax, key, ck, target_i in [(odds, "odds_ratio", "odds_ratio", 0), (ranks, "spearman", "rank", 1)]:
        item = nhanes[key]
        show_results(ax, 2, original(key), item["estimate"], item["ci95"])
        show_results(ax, 1, [v[key] for v in iron_laws], burkina["weighted"][target_i],
                     burkina["weighted_cluster_bootstrap"][target_i]["percentile95"])
        interval_key = "odds_interval" if key == "odds_ratio" else "rank_interval"
        show_results(ax, 0, [v[ck] for v in augmented], chns["reference"][ck],
                     chns["reference"][interval_key])
        ax.set(yticks=[2, 1, 0], yticklabels=["US", "Burkina Faso", "CHNS B"], ylim=(-.50, 2.5))
    panel(odds, "C   Iron status · threshold association")
    odds.set(xscale="log", xlim=(1.85, 40), xlabel="Crude odds ratio (log scale)")
    odds.xaxis.set_major_locator(FixedLocator([2, 4, 8, 16, 32]))
    odds.xaxis.set_major_formatter(ScalarFormatter())
    odds.minorticks_off()
    panel(ranks, "D   Iron status · continuous ranks")
    ranks.set(xlim=(-.36, .52), xticks=[-.2, 0, .2, .4], xlabel="Hb–ferritin Spearman correlation")
    handles = [Line2D([], [], marker="o", ls="", color=BLUE, markersize=4.8, label="Agent-authored law"),
               Line2D([], [], marker="D", lw=1.4, color=ORANGE, markersize=4, label="Measured sample and 95% interval")]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.5,1.015), ncol=2, frameon=False,
               handlelength=1.9, columnspacing=2.2, fontsize=8.1)
    save(fig, "analysis-support.pdf")


def chns_revision():
    pairs = read(CHNS, "RESULTS")["pairs"]
    components = read(CHNS, "RANK_COMPONENTS")["paired_descriptions"]
    fig, axs = plt.subplots(1, 2, figsize=(7.03, 2.20), sharey=True)
    fig.subplots_adjust(left=.125, right=.982, top=.77, bottom=.24, wspace=.25)
    for i, name in enumerate(pairs):
        y = len(pairs) - 1 - i
        c, e = (pairs[name]["estimates"][branch] for branch in ["control", "evidence"])
        b = components[name]
        for ax, x1, x2 in [(axs[0], c["rank_error"], e["rank_error"]),
                           (axs[1], b["control_mid_component_error"], b["evidence_mid_component_error"])]:
            ax.plot([x1, x2], [y, y], color="#64718a", lw=1.1)
            ax.scatter(x1, y, facecolors="white", edgecolors=INK, s=23, linewidth=.9, zorder=3)
            ax.scatter(x2, y, facecolors=BLUE, edgecolors="white", s=21, linewidth=.45, zorder=4)
    for ax, title in zip(axs, ["A   Prespecified · global rank",
                               "B   Exploratory · middle Hb band"]):
        panel(ax, title)
        ax.axhline(2.5, color=GUIDE, lw=.65, zorder=0)
        ax.set(xlim=(-.001, .026), xticks=[0, .01, .02], ylim=(-.45, 5.55),
               xlabel="Absolute error against held-out communities")
        ax.set_xticklabels(["0", "0.01", "0.02"])
    axs[0].set(yticks=range(5, -1, -1),
               yticklabels=[s.replace("ordinary", "Ordinary ").replace("workflow", "Guided ") for s in pairs])
    handles = [Line2D([], [], marker="o", ls="", color=INK, markerfacecolor="white",
                      markersize=4.9, label="Revision with original evidence"),
               Line2D([], [], marker="o", ls="", color=BLUE, markersize=4.9, label="Revision with additional A contrast")]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.51,1.01), ncol=2, frameon=False,
               fontsize=8.1, columnspacing=2)
    save(fig, "chns-revision.pdf")


if __name__ == "__main__":
    overview()
    chns_revision()
