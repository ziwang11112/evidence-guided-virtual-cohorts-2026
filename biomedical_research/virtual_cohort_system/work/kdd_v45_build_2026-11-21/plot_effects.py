"""Native-unit effects from the same fitted lifestyle model in each dataset."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator


HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1] / "manuscript/kdd_draft_v45_2026-11-21"
INK = "#22364b"
BLUE = "#3c6395"
RUST = "#ae542d"
LIGHT = "#dae1e9"
PANELS = (("bmi", "A   Body mass index", "kg/m²", [-.46, 2.64]),
          ("total_cholesterol", "B   Total cholesterol", "mg/dL", [-6.4, 39.4]),
          ("hdl_cholesterol", "C   HDL cholesterol", "mg/dL", [-11.1, 11.3]))
GROUPS = ("rural_minus_pastoralist", "urban_minus_pastoralist", "urban_minus_rural")
GROUP_NAMES = ("Rural − pastoralist", "Urban − pastoralist", "Urban − rural")


def main():
    source = json.loads((HERE / "ANALYSIS_SUBSTITUTION.json").read_text(encoding="utf-8"))
    rows = {(r["trait"], r["contrast"]): r for r in source["results"]}
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.1, "text.color": INK,
                         "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                         "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.64))
    fig.subplots_adjust(left=.169, right=.991, top=.742, bottom=.223, wspace=.205)
    legend = [
        Line2D([], [], color=INK, marker="s", lw=1, ms=4, label="Measured cohort (95% interval)"),
        Line2D([], [], color=BLUE, marker="o", ls="", ms=4.6, label="Agent 1"),
        Line2D([], [], color=RUST, marker="D", ls="", mfc="white", ms=4.1, label="Agent 2"),
    ]
    fig.legend(handles=legend, loc="upper center", bbox_to_anchor=(.55, .994),
               ncol=3, frameon=False, columnspacing=1.7, fontsize=8.1)
    for j, (ax, (trait, title, unit, limits)) in enumerate(zip(axes, PANELS)):
        ax.set_title(title, loc="left", weight="bold", fontsize=9, pad=8)
        ax.axvline(0, color="#8794a1", linestyle=(0, (2, 2)), lw=.8, zorder=1)
        for y, contrast in zip((2, 1, 0), GROUPS):
            r = rows[trait, contrast]
            value = r["measured_raw"]
            lo, hi = r["measured_ols_interval"]
            ax.errorbar(value, y+.155, xerr=[[value-lo], [hi-value]], fmt="s",
                        ms=3.8, lw=1.05, capsize=2.1, color=INK, zorder=3)
            ax.scatter(r["authors"]["LIFESTYLE_A1"]["raw_mean"], y,
                       s=22, marker="o", color=BLUE, zorder=4)
            ax.scatter(r["authors"]["LIFESTYLE_A2"]["raw_mean"], y-.155,
                       s=21, marker="D", facecolor="white", edgecolor=RUST, lw=1.2, zorder=4)
        for band in (.5, 1.5):
            ax.axhline(band, color=LIGHT, lw=.6, zorder=0)
        ax.set(ylim=(-.40, 2.39), xlim=limits, yticks=[2, 1, 0])
        ax.set_yticklabels(GROUP_NAMES if j == 0 else [""] * 3)
        ax.tick_params(axis="y", length=0, pad=5, labelsize=7.55)
        ax.tick_params(axis="x", length=2.4, labelsize=7.4)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
        ax.set_xlabel(f"Adjusted difference ({unit})", fontsize=7.7, labelpad=3)
        for k in ("left", "right", "top"):
            ax.spines[k].set_visible(False)
        ax.spines["bottom"].set_color("#a4b0ba")
    fig.text(.008, .015, "Each agent symbol averages three saved tables. The measured cohort had 1,189 BMI, 400 total cholesterol and 405 HDL measurements.",
             fontsize=6.7, color="#445769")
    dest = PAPER / "figures/lifestyle-effects.pdf"
    fig.savefig(dest, metadata={"CreationDate": None, "ModDate": None, "Creator": "Matplotlib"})
    fig.savefig(HERE / "lifestyle-effects.png", dpi=200, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
